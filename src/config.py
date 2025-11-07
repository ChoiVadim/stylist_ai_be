import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


class Config:
    NANO_BANANA_PROMPT = """
    Choose the person from Image 1 and dress them in all the clothing and accessories from Image 2.
    Keep the person’s identity, face, and pose from Image 1 exactly the same.
    Apply the complete outfit and accessories from Image 2 naturally and realistically to match their body shape and movement.
    Capture the result as a realistic OOTD-style photos, taken outdoors in natural lighting.
    The shots should show full-body views, stylish street fashion aesthetics, and cohesive composition that highlights the outfit clearly.
    """
    JSON_PROMPT = """Analyze the person's color season and return ONLY a valid JSON object with the following exact structure (no markdown, no code blocks, just pure JSON):
    {
    "personal_color_type": "string (e.g., 'Deep Autumn', 'Light Spring', etc.)",
    "confidence": 0.0-1.0,
    "undertone": "warm or cool",
    "season": "spring, summer, autumn, or winter",
    "subtype": "string (e.g., 'deep', 'light', 'soft', 'bright', etc.)",
    "reasoning": "brief explanation of the analysis"
    }"""
    SYSTEM_PROMPT = "You are a color analyst. You are given an image of a person and you need to analyze the person's color season."

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def get_client(self):
        return self.client


config = Config()
