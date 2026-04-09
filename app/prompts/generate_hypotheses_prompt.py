import json
from typing import Any, Dict, List


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, default=str)


def build_generate_hypotheses_prompt(
    question: str,
    baseline_results: Dict[str, Any],
    segment_results: List[Dict[str, Any]],
) -> str:
    compact_segments = []
    for block in segment_results:
        compact_segments.append(
            {
                "dimension": block.get("dimension"),
                "rows": (block.get("rows") or [])[:5],
            }
        )

    return f"""
You are generating candidate analytics hypotheses for a revenue investigation.
Return JSON only. Do not wrap it in markdown.

Allowed hypothesis IDs:
- h1_payment_failure
- h2_mobile_segment
- h3_geo_specific_issue
- h0_general_decline

Return JSON with this shape:
{{
  "hypotheses": [
    {{
      "id": "h1_payment_failure|h2_mobile_segment|h3_geo_specific_issue|h0_general_decline",
      "title": string,
      "reason": string
    }}
  ]
}}

Rules:
- Use only the provided data.
- Prefer specific hypotheses over generic ones.
- Include h0_general_decline only when no strong specific explanation is visible.
- Return at most 4 hypotheses.
- Do not invent IDs outside the allowed set.
- If the overall metric did not decline, return an empty hypotheses list.

Question:
{question}

Baseline results:
{_json(baseline_results)}

Segment results:
{_json(compact_segments)}
""".strip()
