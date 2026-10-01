"""
generator.py - Gemini API integration for AI Content Generator
Uses: google-genai >= 2.0 (new SDK, replaces deprecated google-generativeai)
"""
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class ContentGenerator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self._client = None
        self._configured = False

    def configure(self, api_key: str = None):
        """Configure the Gemini API with the provided or env key."""
        key = api_key or self.api_key
        if not key:
            raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")
        self._client = genai.Client(api_key=key)
        self._model = "gemini-flash-latest"
        self._configured = True

    def is_configured(self) -> bool:
        return self._configured

    def generate(self, prompt: str) -> dict:
        """
        Generate content from the given prompt.
        Returns dict: {success: bool, content: str, error: str}
        """
        if not self._configured:
            try:
                self.configure()
            except ValueError as e:
                return {"success": False, "content": "", "error": str(e)}

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            text = response.text.strip()
            return {"success": True, "content": text, "error": ""}
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
                return {"success": False, "content": "", "error": "Invalid API key. Please check your GEMINI_API_KEY."}
            elif "quota" in error_msg.lower() or "429" in error_msg:
                return {"success": False, "content": "", "error": "Rate limit exceeded. Please wait a moment and try again."}
            elif "blocked" in error_msg.lower() or "safety" in error_msg.lower():
                return {"success": False, "content": "", "error": "Content was blocked by safety filters. Please revise your topic."}
            else:
                return {"success": False, "content": "", "error": f"Generation failed: {error_msg}"}
