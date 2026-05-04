import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
MAX_HISTORY_ROUNDS = int(os.getenv("MAX_HISTORY_ROUNDS", "10"))


def require_api_key():
    if not API_KEY:
        raise ValueError("Missing OPENAI_API_KEY. Please create a .env file first.")
    return API_KEY


if __name__ == "__main__":
    api_key = require_api_key()
    print("API key:", api_key[:8] + "...")
    print("Base URL:", BASE_URL)
    print("Model:", MODEL)
    print("Temperature:", TEMPERATURE)
    print("Max tokens:", MAX_TOKENS)
