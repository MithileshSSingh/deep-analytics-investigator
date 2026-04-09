import json
from typing import Any, Dict


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, default=str)


def build_select_route_prompt(parsed_question: Dict[str, Any], route_registry: Dict[str, Any]) -> str:
    compact_routes = {}
    for route_name, route in route_registry.items():
        compact_routes[route_name] = {
            "description": route.get("description"),
            "supported_metrics": route.get("supported_metrics", []),
            "supported_investigation_types": route.get("supported_investigation_types", []),
            "supported_dimensions": route.get("supported_dimensions", []),
            "baseline_query_families": route.get("baseline_query_families", []),
            "segment_query_families": route.get("segment_query_families", []),
            "validation_query_families": route.get("validation_query_families", []),
        }

    return f"""
You are selecting the best analytics route for an investigation.
Return JSON only. Do not wrap it in markdown.

Return JSON with this shape:
{{
  "route_name": string,
  "reason": string,
  "confidence": "low" | "medium" | "high"
}}

Rules:
- Choose only from the provided route registry keys.
- Use the parsed question as the main source of truth.
- Pick the most specific compatible route.
- Do not invent route names.

Parsed question:
{_json(parsed_question)}

Available routes:
{_json(compact_routes)}
""".strip()
