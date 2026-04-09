from app.graph.state import InvestigatorState
from app.graph.nodes.parse_question import parse_question as parse_question_deterministic
from app.prompts.parse_question_prompt import build_parse_question_prompt
from app.services.llm_client import invoke_json, LLMUnavailableError, LLMParseError
from app.services.settings import LLM_ENABLED


def parse_question_llm(state: InvestigatorState):
    question = state["question"]

    if not LLM_ENABLED:
        result = parse_question_deterministic(state)
        trace = result["trace"][:-1] + [{
            "node": "parse_question_llm",
            "message": "LLM parsing disabled; used deterministic parser",
        }] + [result["trace"][-1]]
        result["trace"] = trace
        return result

    prompt = build_parse_question_prompt(question)
    try:
        parsed = invoke_json(prompt)
        trace = state["trace"] + [{
            "node": "parse_question_llm",
            "message": f"Parsed question with LLM: {question}",
        }]
        return {"parsed_question": parsed, "trace": trace}
    except (LLMUnavailableError, LLMParseError, KeyError, TypeError, ValueError):
        result = parse_question_deterministic(state)
        trace = result["trace"][:-1] + [{
            "node": "parse_question_llm",
            "message": "LLM parse failed or unavailable; used deterministic fallback",
        }] + [result["trace"][-1]]
        result["trace"] = trace
        return result
