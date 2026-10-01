"""
tests/test_generator.py
========================
Automated test suite for AI Content Generator.
Tests prompt templates, tone instructions, and configuration handling.

Run with:  python tests/test_generator.py
"""

import os
import sys
import unittest

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prompts import build_prompt, CONTENT_PROMPTS, TONE_INSTRUCTIONS
from generator import ContentGenerator


class TestPrompts(unittest.TestCase):
    def test_content_types_exist(self):
        expected = ["Blog Post", "Social Media Caption", "Text Summary", "Email Newsletter", "Product Description"]
        for ct in expected:
            self.assertIn(ct, CONTENT_PROMPTS)

    def test_tones_exist(self):
        expected = ["Professional", "Casual", "Friendly", "Creative", "Formal"]
        for tone in expected:
            self.assertIn(tone, TONE_INSTRUCTIONS)

    def test_build_prompt_formatting(self):
        topic = "Artificial Intelligence in Modern Healthcare"
        prompt = build_prompt("Blog Post", topic, "Professional", "Medium")
        self.assertIn(topic, prompt)
        self.assertIn("Professional", prompt)
        self.assertIn("You are a professional content writer", prompt)


class TestGeneratorConfig(unittest.TestCase):
    def test_unconfigured_error_handling(self):
        gen = ContentGenerator()
        gen._configured = False
        gen.api_key = ""
        result = gen.generate("Test prompt")
        self.assertFalse(result["success"])
        self.assertTrue(len(result["error"]) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
