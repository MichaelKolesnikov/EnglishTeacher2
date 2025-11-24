from src.core.LLMConfig import LLMConfig
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm_config_from_env() -> LLMConfig:
    return LLMConfig(
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
        model=os.getenv("LLM_MODEL", "deepseek-chat")
    )
