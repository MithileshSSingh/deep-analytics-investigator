import json
from typing import Any, Dict, List


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, default=str)


def build_generate_report_prompt(
    question: str,
    baseline_results: Dict[str, Any],
    ranked_hypotheses: List[Dict[str, Any]],
    segment_results: List[Dict[str, Any]],
) -> str:
    compact_hypotheses = []
    for item in ranked_hypotheses[:3]:
        validated = item.get("validated_item") or {}
        compact_hypotheses.append(
            {
                "title": item.get("title"),
                "score": item.get("score"),
                "reasons": item.get("reasons", []),
                "evidence": validated.get("evidence", [])[:5],
                "status": validated.get("status"),
            }
        )

    compact_segments = []
    for block in segment_results:
        compact_segments.append(
            {
                "dimension": block.get("dimension"),
                "rows": (block.get("rows") or [])[:3],
            }
        )

    return f"""
You are generating a concise analytics investigation report.
Return JSON only. Do not wrap it in markdown.

Required JSON shape:
{{
  "summary": string,
  "what_changed": [string, string, string, string],
  "top_findings": [string],
  "likely_causes": [
    {{
      "cause": string,
      "confidence": "high" | "medium" | "low",
      "evidence": [string]
    }}
  ],
  "next_steps": [string],
  "confidence": "high" | "medium" | "low"
}}

Rules:
- Base everything only on the provided analytics data.
- Be specific and evidence-backed.
- Do not invent causes or evidence.
- Keep likely_causes to at most 3 items.
- Keep next_steps to 3 concise actions.
- If the metric increased or was flat, do not frame it as an incident.
- If strong evidence points to Razorpay + UPI + India + mobile, say that plainly.
- top_findings should be short bullet-style strings, not paragraphs.

Question:
{question}

Baseline results:
{_json(baseline_results)}

Top ranked hypotheses:
{_json(compact_hypotheses)}

Top segment breakdown rows:
{_json(compact_segments)}
""".strip()
