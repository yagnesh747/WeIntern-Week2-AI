"""
matcher.py - Transparent Multi-Factor Candidate Matcher & Ranker
================================================================
Calculates candidate match scores using the exact transparent formula:
- 50% TF-IDF / Text Similarity
- 35% Required Skill Match
- 10% Education Relevance
- 5% Experience Relevance

All components normalized to 0–100 before applying weights.
Every candidate dictionary guarantees the 'score_breakdown' structure:
{
  "semantic_similarity": ...,
  "skill_match": ...,
  "education_relevance": ...,
  "experience_relevance": ...,
  "final_score": ...
}

Author  : WeIntern AI Internship Team
Task    : Week 2 - Task 2: Resume Screening AI
"""

import re
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import SkillExtractor


class ResumeMatcher:
    """
    Evaluates candidate resumes against a target Job Description.
    Calculates multi-factor weighted match scores and ranks candidates.
    """

    WEIGHT_SEMANTIC = 0.50
    WEIGHT_SKILLS = 0.35
    WEIGHT_EDUCATION = 0.10
    WEIGHT_EXPERIENCE = 0.05

    def __init__(self, skill_extractor: Optional[SkillExtractor] = None):
        self.skill_extractor = skill_extractor or SkillExtractor()
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
            max_features=5000,
        )

    def clean_text(self, text: str) -> str:
        """
        Normalize text for TF-IDF vectorization:
        - Lowercase
        - Retain alphanumeric characters and programming symbols (+, #, ., -)
        """
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"[^\w\s\+\#\.\-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def extract_required_experience(self, jd_text: str) -> float:
        """
        Extract required years of experience from Job Description text.
        Default to 2.0 years if not explicitly mentioned.
        """
        match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:to|-|–)?\s*(\d+(?:\.\d+)?)?\s*(?:\+|\s*plus)?\s*(?:years?|yrs?)",
            jd_text,
            re.IGNORECASE
        )
        if match:
            try:
                min_exp = float(match.group(1))
                return min_exp
            except ValueError:
                pass
        return 2.0

    def evaluate_education(self, education_list: List[str]) -> float:
        """
        Calculate an education relevance score (0 - 100).
        - Master's / Ph.D. / M.Tech / M.S. / MCA in CS / IT / Tech: 100.0
        - Bachelor's in CS / Tech (B.Tech, B.E., B.S., BCA): 85.0
        - Other Bachelor's / Diploma: 60.0
        - No degree listed: 20.0
        """
        if not education_list:
            return 20.0

        edu_str = " ".join(education_list).lower()

        if any(deg in edu_str for deg in ["ph.d", "doctorate", "master", "m.tech", "m.s", "m.sc", "mca"]):
            return 100.0
        elif any(deg in edu_str for deg in ["b.tech", "b.e", "b.s", "b.sc", "bca", "bachelor"]):
            return 85.0
        elif any(deg in edu_str for deg in ["diploma", "associate", "mba", "bba"]):
            return 60.0

        return 40.0

    def evaluate_experience(self, candidate_years: float, required_years: float) -> float:
        """
        Calculate experience relevance score (0 - 100).
        - If candidate meets or exceeds required years: 100.0
        - If candidate has partial experience: proportional ratio
        - If fresher (0 years): realistic score based on requirement
        """
        if required_years <= 0.0:
            return 100.0

        if candidate_years >= required_years:
            return 100.0
        elif candidate_years > 0.0:
            ratio = candidate_years / required_years
            return round(min(100.0, ratio * 100.0), 2)
        else:
            # Fresher applying
            return 20.0 if required_years >= 3.0 else 50.0

    def analyze(self, job_description: str, parsed_resumes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare all parsed resumes against the job description using
        the transparent 4-factor scoring model.

        Parameters
        ----------
        job_description : str
            Target Job Description.
        parsed_resumes : list[dict]
            Parsed resume records from ResumeParser.
        """
        if not job_description or not job_description.strip():
            raise ValueError("Job Description cannot be empty.")

        if not parsed_resumes:
            raise ValueError("At least one resume must be provided for analysis.")

        # 1. Extract skills from Job Description
        jd_skills = self.skill_extractor.extract_skills(job_description)
        required_exp = self.extract_required_experience(job_description)

        # 2. Build corpus for TF-IDF
        cleaned_jd = self.clean_text(job_description)
        corpus = [cleaned_jd]

        for res in parsed_resumes:
            raw_text = res.get("raw_text", "")
            cleaned_res = self.clean_text(raw_text)
            corpus.append(cleaned_res if cleaned_res else "empty_resume_content")

        # 3. Compute TF-IDF matrix & Cosine Similarities
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        jd_vector = tfidf_matrix[0:1]
        resume_vectors = tfidf_matrix[1:]

        cosine_sims = cosine_similarity(jd_vector, resume_vectors).flatten()

        # 4. Compute transparent weighted score for each candidate
        scored_candidates: List[Dict[str, Any]] = []

        for i, res in enumerate(parsed_resumes):
            raw_cos = float(cosine_sims[i]) if i < len(cosine_sims) else 0.0
            semantic_similarity = round(min(100.0, max(0.0, raw_cos * 100.0)), 2)

            res_skills = res.get("skills", [])
            skill_comp = self.skill_extractor.compare_skills(jd_skills, res_skills)

            # Required skill match component (0-100)
            if jd_skills:
                skill_match = round(skill_comp["match_rate"] * 100.0, 2)
            else:
                skill_match = semantic_similarity

            # Education component (0-100)
            education_relevance = self.evaluate_education(res.get("education", []))

            # Experience component (0-100)
            cand_exp_yrs = float(res.get("experience_years", 0.0))
            experience_relevance = self.evaluate_experience(cand_exp_yrs, required_exp)

            # Exact 4-factor composite weighted match score
            final_score = (
                (self.WEIGHT_SEMANTIC * semantic_similarity) +
                (self.WEIGHT_SKILLS * skill_match) +
                (self.WEIGHT_EDUCATION * education_relevance) +
                (self.WEIGHT_EXPERIENCE * experience_relevance)
            )
            final_score = round(min(100.0, max(0.0, final_score)), 2)

            # Guaranteed score_breakdown dictionary
            score_breakdown = {
                "semantic_similarity": semantic_similarity,
                "skill_match": skill_match,
                "education_relevance": education_relevance,
                "experience_relevance": experience_relevance,
                "final_score": final_score,
            }

            candidate_card = {
                "name": res.get("name", "Name Not Detected"),
                "filename": res.get("filename", "Resume.pdf"),
                "email": res.get("email", "Not detected"),
                "phone": res.get("phone", "Not detected"),
                "education": res.get("education", []),
                "experience_years": cand_exp_yrs,
                "experience_summary": res.get("experience_summary", "Fresher / 0 years"),
                "match_percentage": final_score,
                "skill_match_percentage": skill_match,
                "score_breakdown": score_breakdown,
                "matching_skills": skill_comp["matching_skills"],
                "missing_skills": skill_comp["missing_skills"],
                "additional_skills": skill_comp["additional_skills"],
                "all_resume_skills": res_skills,
                "error": res.get("error"),
                "raw_text": res.get("raw_text", ""),
            }
            scored_candidates.append(candidate_card)

        # 5. Rank candidates by final weighted match_percentage descending
        scored_candidates.sort(
            key=lambda c: (
                c.get("match_percentage", 0.0),
                c.get("skill_match_percentage", 0.0),
                (c.get("score_breakdown") or {}).get("semantic_similarity", 0.0)
            ),
            reverse=True
        )

        for rank, cand in enumerate(scored_candidates, 1):
            cand["rank"] = rank

        # 6. Build clean DataFrame for leaderboard table and export
        df_rows = []
        for c in scored_candidates:
            df_rows.append({
                "Rank": c["rank"],
                "Candidate Name": c["name"],
                "Match %": f"{c['match_percentage']:.1f}%",
                "Skill Match %": f"{c['skill_match_percentage']:.1f}%",
                "Matching Skills": ", ".join(c["matching_skills"]) if c["matching_skills"] else "None",
                "Missing Skills": ", ".join(c["missing_skills"]) if c["missing_skills"] else "None",
                "Experience": c["experience_summary"],
                "Education": " | ".join(c["education"]),
                "Email": c["email"],
                "Phone": c["phone"],
                "File": c["filename"],
            })

        df = pd.DataFrame(df_rows)

        # 7. Aggregate summary metrics
        scores = [c["match_percentage"] for c in scored_candidates]
        high_matches = sum(1 for s in scores if s >= 70.0)
        mod_matches = sum(1 for s in scores if 50.0 <= s < 70.0)
        low_matches = sum(1 for s in scores if s < 50.0)

        missing_skill_freq: Dict[str, int] = {}
        for c in scored_candidates:
            for s in c["missing_skills"]:
                missing_skill_freq[s] = missing_skill_freq.get(s, 0) + 1

        top_missing_skills = sorted(
            missing_skill_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        summary = {
            "total_candidates": len(scored_candidates),
            "top_candidate": scored_candidates[0]["name"] if scored_candidates else "None",
            "top_score": scored_candidates[0]["match_percentage"] if scored_candidates else 0.0,
            "average_score": round(float(np.mean(scores)), 1) if scores else 0.0,
            "high_matches": high_matches,
            "moderate_matches": mod_matches,
            "low_matches": low_matches,
            "jd_skills_count": len(jd_skills),
            "jd_skills": jd_skills,
            "top_missing_skills": top_missing_skills,
        }

        return {
            "candidates": scored_candidates,
            "jd_skills": jd_skills,
            "summary": summary,
            "dataframe": df,
        }
