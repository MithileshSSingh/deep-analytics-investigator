import json
from typing import Any, Dict

from app.services.settings import LLM_ENABLED, LLM_MODEL, OPENAI_API_KEY


class LLMUnavailableError(RuntimeError):
    pass


class LLMParseError(RuntimeError):
    pass


def llm_available() -> bool:
    return bool(LLM_ENABLED and OPENAI_API_KEY)


def invoke_json(prompt: str) -> Dict[str, Any]:
    if not llm_available():
        raise LLMUnavailableError("LLM is disabled or missing API key")

    try:
        from langchain_openai import ChatOpenAI
    except Exception as exc:
        raise LLMUnavailableError("langchain_openai is not installed") from exc

    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    response = llm.invoke(prompt)
    content = getattr(response, "content", response)

    if isinstance(content, list):
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)

    try:
        return json.loads(content)
    except Exception as exc:
        raise LLMParseError(f"Failed to parse LLM JSON output: {content}") from exc
