import os
from google import genai
from dotenv import load_dotenv

import src.prompts as prompts

load_dotenv()


class Config:
    NANO_BANANA_PROMPT = prompts.NANO_BANANA_PROMPT
    JSON_PROMPT = prompts.JSON_PROMPT
    SYSTEM_PROMPT = prompts.SYSTEM_PROMPT

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def get_client(self):
        return self.client


config = Config()
