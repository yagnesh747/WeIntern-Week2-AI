"""
resume_parser.py - Accurate PDF Resume Entity & Text Parser
===========================================================
Extracts clean text and key entities from candidate PDF resumes:
- Candidate Name: First valid personal-name line from top (supports Indian & international names, all-caps, title-case; strictly rejects headings & contact links).
- Education: Isolated strictly under the EDUCATION heading; never includes ABOUT ME or summary text.
- Experience: Strict professional employment extraction; ignores academic/college dates; accurately identifies freshers.
- Contact: Email & Phone.
- Skills: Extracted via SkillExtractor.

Author  : WeIntern AI Internship Team
Task    : Week 2 - Task 2: Resume Screening AI
"""

import io
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pypdf
except ImportError:
    try:
        import PyPDF2 as pypdf
    except ImportError:
        pypdf = None

from skill_extractor import SkillExtractor


class ResumeParser:
    """Parses PDF resumes and extracts candidate information and metadata."""

    EMAIL_PATTERN = re.compile(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        re.IGNORECASE
    )

    PHONE_PATTERN = re.compile(
        r"(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4})",
        re.IGNORECASE
    )

    # Common section headings to reject as names
    SECTION_HEADING_KEYWORDS = {
        "about", "about me", "summary", "professional summary", "executive summary",
        "career summary", "objective", "career objective", "profile", "personal profile",
        "education", "academic", "academics", "academic background", "qualifications",
        "skills", "technical skills", "key skills", "core competencies", "technologies",
        "experience", "work experience", "professional experience", "employment",
        "employment history", "work history", "internship", "internships",
        "projects", "academic projects", "personal projects", "key projects",
        "certifications", "certificates", "awards", "honors", "achievements",
        "publications", "languages", "interests", "hobbies", "activities",
        "extracurricular", "references", "declaration", "contact", "contact info",
        "contact details", "curriculum", "vitae", "resume", "cv", "page",
        "strengths", "roles", "responsibilities", "coursework"
    }

    # Contact & link indicators that disqualify a line from being a personal name
    CONTACT_INDICATORS = [
        "@", "http", "www", ".com", ".in", ".org", ".io", ".dev",
        "linkedin", "github", "leetcode", "geeksforgeeks", "hackerrank",
        "codechef", "codeforces", "portfolio", "email", "phone", "+91", "+1"
    ]

    # Non-name tokens (titles, student statuses)
    NON_NAME_TOKENS = {
        "developer", "engineer", "designer", "manager", "analyst", "consultant",
        "specialist", "architect", "programmer", "intern", "student", "fresher",
        "graduate", "candidate", "applicant", "officer", "executive", "lead",
        "associate", "director", "administrator", "scientist", "researcher",
        "undergraduate", "postgraduate", "department", "college", "university"
    }

    MONTH_MAP = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }

    DATE_RANGE_PATTERN = re.compile(
        r"\b(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*)?((?:19|20)\d{2})\s*(?:-|–|to)\s*(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*)?((?:19|20)\d{2}|present|current)\b",
        re.IGNORECASE
    )

    EXP_EXPLICIT_MENTION = re.compile(
        r"(\d+(?:\.\d+)?)\s*(?:\+|\s*plus)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:professional|work|industry|software|relevant)?\s*experience",
        re.IGNORECASE
    )

    def __init__(self, skill_extractor: Optional[SkillExtractor] = None):
        self.skill_extractor = skill_extractor or SkillExtractor()

    # ------------------------------------------------------------------
    # 1. Text Extraction
    # ------------------------------------------------------------------
    def extract_text_from_pdf(self, file_source: Union[str, bytes, io.BytesIO, Any]) -> Tuple[str, int, Optional[str]]:
        """Extract full text from PDF file."""
        text_content = []
        page_count = 0
        error = None

        stream = None
        if isinstance(file_source, str):
            if not os.path.exists(file_source):
                return "", 0, f"File not found: {file_source}"
            stream = open(file_source, "rb")
        elif isinstance(file_source, bytes):
            stream = io.BytesIO(file_source)
        elif hasattr(file_source, "read"):
            stream = file_source
            if hasattr(stream, "seek"):
                stream.seek(0)
        else:
            return "", 0, "Invalid file source provided."

        if pdfplumber is not None:
            try:
                if hasattr(stream, "seek"):
                    stream.seek(0)
                with pdfplumber.open(stream) as pdf:
                    page_count = len(pdf.pages)
                    for page in pdf.pages:
                        page_text = page.extract_text() or ""
                        if page_text.strip():
                            text_content.append(page_text)
            except Exception as exc:
                error = f"pdfplumber notice: {exc}"

        if not text_content and pypdf is not None:
            try:
                if hasattr(stream, "seek"):
                    stream.seek(0)
                reader = pypdf.PdfReader(stream)
                page_count = len(reader.pages)
                for page in reader.pages:
                    t = page.extract_text() or ""
                    if t.strip():
                        text_content.append(t)
                error = None
            except Exception as exc:
                error = f"Failed to extract PDF text: {exc}"

        if isinstance(file_source, str) and stream:
            stream.close()

        full_text = "\n\n".join(text_content).strip()
        if not full_text and not error:
            error = "PDF appears to be empty or contains scanned images without selectable text."

        return full_text, page_count, error

    # ------------------------------------------------------------------
    # 2. General, Reliable Name Extraction
    # ------------------------------------------------------------------
    def is_valid_name_line(self, line: str) -> bool:
        """
        Validates if a line strictly represents a candidate's personal name.
        - Supports standard First + Last, Middle names, Indian full names (e.g. 2-6 words).
        - Supports Title Case and All-Caps names.
        - Strictly rejects contact/link lines, digits, and section headings.
        """
        cleaned = line.strip()
        if not cleaned or len(cleaned) < 3 or len(cleaned) > 65:
            return False

        lower_line = cleaned.lower()

        # 1. Reject contact/link lines
        if any(ci in lower_line for ci in self.CONTACT_INDICATORS):
            return False

        # 2. Reject if line contains digits or forbidden symbols
        if any(ch.isdigit() for ch in cleaned):
            return False
        if any(ch in cleaned for ch in ["@", ":", ";", "/", "\\", "|", "=", "*", "(", ")", "[", "]", "{", "}"]):
            return False

        # 3. Reject if the line matches a section heading
        clean_text_only = re.sub(r"[^a-zA-Z\s]", "", lower_line).strip()
        if clean_text_only in self.SECTION_HEADING_KEYWORDS:
            return False
        if any(clean_text_only.startswith(h + " ") or clean_text_only == h for h in self.SECTION_HEADING_KEYWORDS):
            return False

        tokens = [t.strip(",.") for t in cleaned.split() if t.strip(",.")]
        # Accept names between 1 and 7 words
        if not (1 <= len(tokens) <= 7):
            return False

        # Reject lines with title or student status keywords
        for t in tokens:
            t_low = t.lower()
            if t_low in self.NON_NAME_TOKENS or t_low in self.SECTION_HEADING_KEYWORDS:
                return False
            # Token must be purely alphabetic (letters, periods for initials, hyphens/apostrophes)
            if not re.match(r"^[a-zA-Z\.\'\-]+$", t):
                return False

        return True

    def extract_name(self, text: str, filename: str = "") -> str:
        """
        Extract the first valid person-name line from the top portion of the resume.
        Never returns section headings like 'ABOUT ME', 'SUMMARY', etc.
        If uncertain, returns 'Name Not Detected'.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Scan the first 12 non-empty lines for the name
        for line in lines[:12]:
            if self.is_valid_name_line(line):
                # Clean multiple spaces and return
                return " ".join(line.split())

        # Fallback to filename if cleanly matches 'Firstname_Lastname.pdf'
        if filename:
            base = os.path.splitext(os.path.basename(filename))[0]
            clean_base = re.sub(r"[_\-]+", " ", base)
            clean_base = re.sub(r"\b(?:resume|cv|profile|v\d+|\d+)\b", "", clean_base, flags=re.IGNORECASE)
            tokens = [t.strip() for t in clean_base.split() if t.strip()]
            if 2 <= len(tokens) <= 6:
                if all(t.isalpha() and t.lower() not in self.SECTION_HEADING_KEYWORDS and t.lower() not in self.NON_NAME_TOKENS for t in tokens):
                    return " ".join(tokens).title()

        return "Name Not Detected"

    def extract_email(self, text: str) -> str:
        """Extract primary email address from text."""
        match = self.EMAIL_PATTERN.search(text)
        return match.group(0).lower() if match else "Not detected"

    def extract_phone(self, text: str) -> str:
        """Extract primary phone number from text."""
        match = self.PHONE_PATTERN.search(text)
        if match:
            phone = match.group(0).strip()
            digits = re.sub(r"\D", "", phone)
            if 7 <= len(digits) <= 15:
                return phone
        return "Not detected"

    # ------------------------------------------------------------------
    # 3. Section-Isolated Education Extractor
    # ------------------------------------------------------------------
    def extract_education(self, text: str) -> List[str]:
        """
        Extract education qualifications strictly starting from the EDUCATION heading.
        Never includes ABOUT ME, SUMMARY, OBJECTIVE, or previous sections.
        """
        edu_header_pattern = re.compile(
            r"^\s*(?:education|academic\s+background|academics|qualifications|academic\s+qualifications|educational\s+qualifications)\b",
            re.IGNORECASE
        )
        term_header_pattern = re.compile(
            r"^\s*(?:skills|technical\s+skills|key\s+skills|experience|work\s+experience|projects|academic\s+projects|certifications|certificates|achievements|awards|publications|languages|interests|activities|extracurricular)\b",
            re.IGNORECASE
        )

        lines = text.split("\n")
        in_edu = False
        edu_raw_lines: List[str] = []

        for line in lines:
            l_str = line.strip()
            if not l_str:
                continue

            # Start of EDUCATION section
            if edu_header_pattern.match(l_str) and len(l_str) < 40:
                in_edu = True
                continue

            if in_edu:
                # Terminate when the next section begins
                if term_header_pattern.match(l_str) and len(l_str) < 40:
                    in_edu = False
                    break
                edu_raw_lines.append(l_str)

        entries: List[str] = []

        # If EDUCATION section was explicitly found
        if edu_raw_lines:
            for l in edu_raw_lines:
                # Clean bullets and leading dashes
                clean_l = re.sub(r"^[•\-\*]\s*", "", l).strip()
                if not clean_l:
                    continue

                # Filter out lines that are purely standalone date ranges or CGPA scores
                if re.match(r"^(?:(?:19|20)\d{2}\s*(?:-|–|to)\s*(?:(?:19|20)\d{2}|present|current)|\d+(?:\.\d+)?\s*(?:%|cgpa|gpa|marks))\b", clean_l, re.IGNORECASE):
                    continue

                # Filter out lines that are purely numbers or short location fragments
                if len(clean_l) < 4:
                    continue

                # Truncate length if unusually long
                if len(clean_l) > 100:
                    clean_l = clean_l[:97] + "..."

                if clean_l not in entries:
                    entries.append(clean_l)

            if entries:
                return entries[:5]

        # Fallback only if no explicit EDUCATION heading was found:
        # Search lines containing degrees, strictly rejecting any line containing ABOUT ME / SUMMARY / OBJECTIVE
        for line in lines:
            l_clean = line.strip()
            if not l_clean:
                continue
            l_low = l_clean.lower()
            if any(w in l_low for w in ["about me", "summary", "objective", "profile"]):
                continue

            for pattern in [r"\b(?:b\.?tech|b\.?e|b\.?s|b\.?sc|m\.?tech|m\.?s|bachelor|master|intermediate|diploma|ph\.?d)\b"]:
                if re.search(pattern, l_clean, re.IGNORECASE):
                    entry = " ".join(l_clean.split())
                    if len(entry) > 100:
                        entry = entry[:97] + "..."
                    if entry not in entries:
                        entries.append(entry)
                    break

        return entries[:4] if entries else ["Education not explicitly listed"]

    # ------------------------------------------------------------------
    # 4. Accurate Experience Extractor
    # ------------------------------------------------------------------
    def extract_experience(self, text: str) -> Tuple[float, str]:
        """
        Accurately calculates professional employment experience.
        - Excludes college/graduation dates and academic projects.
        - For freshers or candidates without employment, returns 0.0, 'Fresher / 0 years'.
        """
        text_lower = text.lower()

        # Check for explicit fresher / student status
        is_fresher_explicit = any(
            phrase in text_lower for phrase in [
                "fresher", "fresh graduate", "recent graduate", "seeking an entry-level",
                "seeking an entry level", "entry level software", "student at",
                "undergraduate", "b.tech student", "pursuing b.tech", "currently studying",
                "engineering (ai) student", "engineering student", "computer science student"
            ]
        )

        # 1. Check for explicit professional experience statement
        explicit_match = self.EXP_EXPLICIT_MENTION.search(text)
        if explicit_match:
            try:
                yrs = float(explicit_match.group(1))
                if yrs > 0:
                    return yrs, f"~{yrs:g} years (explicitly stated)"
            except ValueError:
                pass

        # 2. Extract strictly within Work Experience / Employment section
        exp_header_pattern = re.compile(
            r"^\s*(?:work\s+experience|professional\s+experience|employment\s+history|work\s+history|experience)\b",
            re.IGNORECASE
        )
        term_header_pattern = re.compile(
            r"^\s*(?:education|academic|academics|projects|academic\s+projects|certifications|skills|technical\s+skills|achievements|awards|publications|languages)\b",
            re.IGNORECASE
        )

        lines = text.split("\n")
        in_experience_section = False
        experience_lines = []

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            if exp_header_pattern.match(line_stripped) and len(line_stripped) < 40:
                in_experience_section = True
                continue

            if in_experience_section:
                if term_header_pattern.match(line_stripped) and len(line_stripped) < 40:
                    in_experience_section = False
                    break

                line_lower = line_stripped.lower()
                if any(w in line_lower for w in ["degree", "university", "college", "school", "b.tech", "m.tech", "b.e.", "b.s.", "bca", "mca", "gpa", "cgpa", "coursework", "academic project"]):
                    continue

                experience_lines.append(line_stripped)

        total_months = 0
        current_year = datetime.now().year

        if experience_lines:
            exp_block = "\n".join(experience_lines)
            ranges_found = self.DATE_RANGE_PATTERN.findall(exp_block)

            for m_start, y_start, m_end, y_end in ranges_found:
                try:
                    start_yr = int(y_start)
                    if y_end.lower() in ("present", "current"):
                        end_yr = current_year
                        end_m = datetime.now().month
                    else:
                        end_yr = int(y_end)
                        end_m = self.MONTH_MAP.get(m_end.lower()[:3], 6) if m_end else 6

                    start_m = self.MONTH_MAP.get(m_start.lower()[:3], 1) if m_start else 1

                    if 1995 <= start_yr <= end_yr <= current_year + 1:
                        diff_months = (end_yr - start_yr) * 12 + (end_m - start_m)
                        if 0 < diff_months <= 360:
                            total_months += diff_months
                except ValueError:
                    continue

        if total_months >= 4:
            est_years = round(total_months / 12.0, 1)
            est_years = min(est_years, 25.0)
            return est_years, f"~{est_years:g} years (professional employment)"

        return 0.0, "Fresher / 0 years"

    # ------------------------------------------------------------------
    # 5. Parser Orchestrator
    # ------------------------------------------------------------------
    def parse(self, file_source: Union[str, bytes, io.BytesIO, Any], filename: str = "") -> Dict[str, Any]:
        """Parse PDF resume and return full structured dictionary."""
        if not filename and isinstance(file_source, str):
            filename = os.path.basename(file_source)
        elif hasattr(file_source, "name") and not filename:
            filename = file_source.name

        text, page_count, error = self.extract_text_from_pdf(file_source)

        if error and not text:
            return {
                "filename": filename or "Unknown.pdf",
                "name": "Name Not Detected",
                "email": "Not detected",
                "phone": "Not detected",
                "education": [],
                "experience_years": 0.0,
                "experience_summary": "Fresher / 0 years",
                "skills": [],
                "raw_text": "",
                "page_count": page_count,
                "error": error,
            }

        name = self.extract_name(text, filename)
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        education = self.extract_education(text)
        exp_years, exp_summary = self.extract_experience(text)
        skills = self.skill_extractor.extract_skills(text)

        return {
            "filename": filename or "Resume.pdf",
            "name": name,
            "email": email,
            "phone": phone,
            "education": education,
            "experience_years": exp_years,
            "experience_summary": exp_summary,
            "skills": skills,
            "raw_text": text,
            "page_count": page_count,
            "error": error,
        }
