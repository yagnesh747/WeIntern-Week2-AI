"""
skill_extractor.py - Transparent Keyword-Based Skill Extraction
===============================================================
Extracts technical skills from resume text and job descriptions
using a curated dictionary (skills.json), alias normalization,
and boundary-aware pattern matching. Avoids false positives from
common English words and academic terms (e.g. 'Spring 2023' semester).

Author  : WeIntern AI Internship Team
Task    : Week 2 - Task 2: Resume Screening AI
"""

import json
import os
import re
from typing import Dict, List, Set, Tuple


class SkillExtractor:
    """
    Extracts and categorises technical skills from text using
    transparent keyword matching and regex patterns.
    """

    def __init__(self, skills_path: str = "skills.json"):
        self.skills_path = skills_path
        self.categories: Dict[str, List[str]] = {}
        self.aliases: Dict[str, str] = {}
        self.display_map: Dict[str, str] = {}
        self.all_skills: List[str] = []
        self._compiled_patterns: List[Tuple[str, re.Pattern]] = []
        self._load_skills()

    def _load_skills(self) -> None:
        """Load skills database from JSON file and precompile regex patterns."""
        resolved_path = self.skills_path
        if not os.path.isabs(resolved_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            resolved_path = os.path.join(current_dir, self.skills_path)

        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"Skills dictionary not found at: {resolved_path}")

        with open(resolved_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.categories = data.get("categories", {})
        self.aliases = {k.lower(): v for k, v in data.get("aliases", {}).items()}
        self.display_map = {}

        unique_skills: Set[str] = set()
        for cat_skills in self.categories.values():
            for skill in cat_skills:
                s_clean = skill.strip()
                unique_skills.add(s_clean.lower())
                self.display_map[s_clean.lower()] = s_clean

        # Register aliases in display_map
        for alias_key, alias_val in self.aliases.items():
            unique_skills.add(alias_key.lower().strip())
            if alias_val.lower() in self.display_map:
                self.display_map[alias_key.lower()] = self.display_map[alias_val.lower()]
            else:
                self.display_map[alias_key.lower()] = alias_val

        # Sort longer skills first (e.g., 'spring boot' before 'spring')
        self.all_skills = sorted(list(unique_skills), key=len, reverse=True)
        self._precompile_patterns()

    def _precompile_patterns(self) -> None:
        """
        Precompile regex patterns with proper boundary handling.
        Prevents false positives on symbols and words with dual meanings.
        """
        self._compiled_patterns = []
        for skill in self.all_skills:
            escaped = re.escape(skill)

            # Special cases
            if skill in ("c++", "c#", ".net", ".net core"):
                pattern_str = r"(?<!\w)" + escaped + r"(?!\w)"
            elif skill == "c":
                # Strict boundary for single-letter C (avoid grades, middle initials, C-suite)
                pattern_str = r"(?<![\w\+\#\.\-])\bC\b(?![\w\+\#\.\-]|\s*(?:suite|level|grade|section))"
                pattern = re.compile(pattern_str)  # Case sensitive for standalone C
                self._compiled_patterns.append((skill, pattern))
                continue
            elif skill == "r":
                # Standalone R language (case sensitive, word boundary)
                pattern_str = r"(?<![\w])\bR\b(?![\w]|\s*(?:&\s*d|research))"
                pattern = re.compile(pattern_str)
                self._compiled_patterns.append((skill, pattern))
                continue
            elif skill == "go":
                # Avoid English verb 'go'
                pattern_str = r"\b(?:golang|go\s+(?:lang|language|programming|developer|backend))\b"
            elif skill == "spring":
                # Avoid 'Spring 2021/2022/2023/2024' semester
                pattern_str = r"\bspring(?!\s+(?:20\d{2}|19\d{2}|semester|term|break))\b"
            elif skill == "rest":
                pattern_str = r"\b(?:rest\s+api|restful\s+api|restful|rest\s+apis)\b"
            else:
                pattern_str = r"\b" + escaped + r"\b"

            pattern = re.compile(pattern_str, re.IGNORECASE)
            self._compiled_patterns.append((skill, pattern))

    def normalize_skill(self, skill: str) -> str:
        """Normalize skill string using alias mapping and canonical casing."""
        s = skill.lower().strip()
        if s in self.aliases:
            target = self.aliases[s]
            return self.display_map.get(target.lower(), target)
        return self.display_map.get(s, skill.title())

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract all recognized skills from arbitrary text.
        Returns a sorted list of unique normalized skill names.
        """
        if not text or not isinstance(text, str):
            return []

        found_normalized: Set[str] = set()

        for skill, pattern in self._compiled_patterns:
            if pattern.search(text):
                normalized = self.normalize_skill(skill)
                found_normalized.add(normalized)

        return sorted(list(found_normalized))

    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Group a list of skills by their predefined categories."""
        categorized: Dict[str, List[str]] = {cat: [] for cat in self.categories}
        categorized["other"] = []

        for skill in skills:
            placed = False
            s_lower = skill.lower()
            for cat, cat_skills in self.categories.items():
                if any(cs.lower() == s_lower for cs in cat_skills):
                    categorized[cat].append(skill)
                    placed = True
                    break
            if not placed:
                categorized["other"].append(skill)

        # Filter out empty categories
        return {cat: items for cat, items in categorized.items() if items}

    def compare_skills(self, jd_skills: List[str], resume_skills: List[str]) -> Dict:
        """
        Compare skills found in Job Description vs Candidate Resume.
        Returns matching, missing, additional, and match rate.
        """
        jd_set = set(jd_skills)
        res_set = set(resume_skills)

        matching = sorted(list(jd_set.intersection(res_set)))
        missing = sorted(list(jd_set - res_set))
        additional = sorted(list(res_set - jd_set))

        match_rate = len(matching) / len(jd_set) if jd_set else 0.0

        return {
            "matching_skills": matching,
            "missing_skills": missing,
            "additional_skills": additional,
            "match_rate": round(match_rate, 4),
            "jd_skills_count": len(jd_set),
            "resume_skills_count": len(res_set),
            "matching_count": len(matching),
            "missing_count": len(missing),
        }
