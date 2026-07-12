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


def mask_api_key(api_key):
    if not api_key:
        return "未配置"
    return api_key[:8] + "..."


def get_config_summary():
    return {
        "api_key": mask_api_key(API_KEY),
        "base_url": BASE_URL,
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "max_history_rounds": MAX_HISTORY_ROUNDS,
    }
