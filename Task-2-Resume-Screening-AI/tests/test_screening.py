"""
tests/test_screening.py
========================
Automated test suite for Resume Screening AI system.
Tests SkillExtractor, ResumeParser, and ResumeMatcher components.

Run with:  python tests/test_screening.py
"""

import os
import sys
import unittest

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from skill_extractor import SkillExtractor
from resume_parser import ResumeParser
from matcher import ResumeMatcher


class TestSkillExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = SkillExtractor()

    def test_exact_skill_extraction(self):
        text = "Experienced with Python, Machine Learning, and Docker in AWS cloud."
        skills = self.extractor.extract_skills(text)
        skills_lower = [s.lower() for s in skills]
        self.assertIn("python", skills_lower)
        self.assertIn("machine learning", skills_lower)
        self.assertIn("docker", skills_lower)
        self.assertIn("aws", skills_lower)

    def test_skill_boundary_matching(self):
        # 'c' or 'r' should not match inside words like 'cat' or 'rabbit'
        text = "The cat ran across the room."
        skills = self.extractor.extract_skills(text)
        skills_lower = [s.lower() for s in skills]
        self.assertNotIn("c", skills_lower)
        self.assertNotIn("r", skills_lower)

    def test_categorize_skills(self):
        skills = ["Python", "React", "PostgreSQL", "Docker", "Machine Learning"]
        categorized = self.extractor.categorize_skills(skills)
        self.assertIn("programming_languages", categorized)
        self.assertIn("ai_ml_technologies", categorized)


class TestResumeParser(unittest.TestCase):
    def setUp(self):
        self.parser = ResumeParser()

    def test_email_extraction(self):
        text = "Contact me at candidate.test@example.com for inquiries."
        email = self.parser.extract_email(text)
        self.assertEqual(email, "candidate.test@example.com")

    def test_phone_extraction(self):
        text = "Phone: +1 (555) 234-5678 or 9876543210"
        phone = self.parser.extract_phone(text)
        self.assertIsNotNone(phone)

    def test_education_extraction(self):
        text = "Education: Bachelor of Technology in Computer Science from IIT Delhi (2020)."
        edu = self.parser.extract_education(text)
        self.assertTrue(len(edu) > 0)


class TestResumeMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = ResumeMatcher()

    def test_scoring_weights(self):
        jd = "Looking for Senior Python Machine Learning Engineer with PyTorch, Docker, AWS and 3 years experience."
        resume = {
            "name": "Test Candidate",
            "email": "test@example.com",
            "phone": "555-1234",
            "raw_text": "Experienced Python Machine Learning developer with PyTorch, Scikit-Learn, Docker, and AWS.",
            "skills": ["Python", "Machine Learning", "PyTorch", "Docker", "AWS"],
            "education": ["Master of Science in Computer Science"],
            "experience_years": 4.0,
            "filename": "test_resume.pdf"
        }
        result = self.matcher.analyze(jd, [resume])
        candidates = result["candidates"]
        self.assertEqual(len(candidates), 1)
        self.assertTrue(candidates[0]["match_percentage"] > 50.0)
        self.assertIn("score_breakdown", candidates[0])

    def test_candidate_ranking_order(self):
        jd = "Senior Python Machine Learning Engineer requiring PyTorch, NLP, Docker, AWS with 4 years experience."
        resume_good = {
            "name": "Good Match",
            "email": "good@example.com",
            "phone": "555-0001",
            "raw_text": "Senior ML Engineer with extensive Python, PyTorch, NLP, Docker, and AWS experience.",
            "skills": ["Python", "PyTorch", "NLP", "Docker", "AWS", "Machine Learning"],
            "education": ["Master of Science in Artificial Intelligence"],
            "experience_years": 5.0,
            "filename": "good.pdf"
        }
        resume_poor = {
            "name": "Poor Match",
            "email": "poor@example.com",
            "phone": "555-0002",
            "raw_text": "Digital marketing executive specializing in SEO, Google Ads, and copywriting.",
            "skills": ["Digital Marketing", "SEO", "Copywriting"],
            "education": ["Bachelor of Arts in Communications"],
            "experience_years": 3.0,
            "filename": "poor.pdf"
        }
        result = self.matcher.analyze(jd, [resume_poor, resume_good])
        ranked = result["candidates"]
        self.assertEqual(ranked[0]["name"], "Good Match")
        self.assertEqual(ranked[1]["name"], "Poor Match")
        self.assertGreater(ranked[0]["match_percentage"], ranked[1]["match_percentage"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
