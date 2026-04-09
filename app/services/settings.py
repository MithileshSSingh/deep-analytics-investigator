import os


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


LLM_ENABLED = env_flag("INVESTIGATOR_LLM_ENABLED", default=False)
LLM_MODEL = os.getenv("INVESTIGATOR_LLM_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
