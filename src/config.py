import os
from google import genai
from dotenv import load_dotenv

import src.prompts as prompts

load_dotenv()


class Config:
    NANO_BANANA_PROMPT = prompts.NANO_BANANA_PROMPT
    JSON_PROMPT = prompts.JSON_PROMPT
    SYSTEM_PROMPT = prompts.SYSTEM_PROMPT
    FULL_OUTFIT_PROMPT = prompts.FULL_OUTFIT_PROMPT

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self._openai_key = os.getenv("OPENAI_API_KEY")
        self._anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self._database_url = os.getenv("DATABASE_URL")

    def get_client(self):
        return self.client
    
    def get_openai_key(self):
        if not self._openai_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return self._openai_key
    
    def get_anthropic_key(self):
        if not self._anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        return self._anthropic_key

    def get_database_url(self):
        if not self._database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        return self._database_url


config = Config()
