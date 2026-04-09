# Deep Analytics Investigator

An evidence-backed analytics investigator that diagnoses metric changes, validates likely causes, and explains what matters.

## What it does

The current MVP supports one strong vertical slice:
- **Why did revenue drop yesterday?**

It takes a natural-language analytics question, runs a structured investigation workflow, validates likely causes with SQL, and returns a report with:
- summary
- what changed
- top findings
- likely causes
- next steps
- confidence

## Current status

This project is now beyond initial scaffold.

Implemented today:
- FastAPI API with `/investigate` endpoint
- LangGraph-based investigation workflow
- DuckDB seeded demo dataset
- revenue investigation vertical slice
- baseline + segment analysis
- validation queries for payment-failure hypotheses
- evidence-backed ranking
- normalized v2 scaffolding:
  - route registry
  - query family registry
  - schema registry
  - evidence artifacts
- first three LLM integration seams:
  - `parse_question_llm` node with deterministic fallback
  - `generate_hypotheses_llm` node with deterministic fallback
  - `generate_report_llm` node with deterministic fallback

Current test status:
- **19 passing tests**

## Current workflow

For a question like:
- `Why did revenue drop yesterday?`

The system currently does this:
1. parse the question
2. resolve the metric and route
3. run baseline revenue comparison
4. run segment breakdown queries
5. generate candidate hypotheses
6. validate hypotheses with targeted SQL
7. rank likely causes
8. generate a final report

## Tech stack

- Python 3.11+
- FastAPI
- LangGraph
- LangChain
- DuckDB
- Pandas
- Pydantic

## Project structure

```text
app/
  api/                # FastAPI routes and response schemas
  graph/              # LangGraph workflow and nodes
  models/             # shared typed models
  prompts/            # LLM prompt builders
  registries/         # route, query-family, and schema registries
  services/           # database, guardrails, evidence, settings, LLM client
  tools/              # metric registry and SQL executor

docs/
  design-summary.md
  v2-architecture.md

scripts/
  seed_data.py        # creates the demo DuckDB dataset

tests/
  ...
```

## How to run the application

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -e .
```

If editable install gives trouble, use:

```bash
pip install -r <(python - <<'PY'
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
for dep in data['project']['dependencies']:
    print(dep)
PY
)
```

### 3) Seed the demo database

This creates `data/demo.duckdb`.

```bash
python scripts/seed_data.py
```

### 4) Start the API server

```bash
uvicorn app.main:app --reload
```

By default, the app will be available at:
- `http://127.0.0.1:8000`

### 5) Check health

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### 6) Run an investigation

```bash
curl -X POST http://127.0.0.1:8000/investigate \
  -H "Content-Type: application/json" \
  -d '{"question":"Why did revenue drop yesterday?"}'
```

Example response shape:

```json
{
  "summary": "...",
  "what_changed": ["..."],
  "top_findings": ["..."],
  "likely_causes": [
    {
      "cause": "...",
      "confidence": "high",
      "evidence": ["..."]
    }
  ],
  "next_steps": ["..."],
  "confidence": "high",
  "trace": [
    {"node": "parse_question", "message": "..."}
  ]
}
```

## Running tests

```bash
pytest -q
```

## Optional LLM parsing setup

The project now includes the first LLM integration seam for question parsing.

Current behavior:
- if LLM is enabled and configured, the workflow can use:
  - `parse_question_llm`
  - `generate_hypotheses_llm`
  - `generate_report_llm`
- these LLM nodes validate and normalize returned JSON contracts before accepting model output
- if LLM is disabled, unavailable, or returns invalid output, it falls back to deterministic parsing/hypothesis generation/reporting

### Environment variables

```bash
export INVESTIGATOR_LLM_ENABLED=true
export INVESTIGATOR_LLM_MODEL=gpt-4o-mini
export OPENAI_API_KEY=your_key_here
```

If these are not set, the app still runs normally using fallback parsing.

## Current limitations

- only one main route is implemented end-to-end: revenue investigation
- LLM integration is only started, not fully rolled out
- hypothesis generation is still mostly deterministic
- reporting is mostly template-based
- demo data is local DuckDB, not a production warehouse

## Docs

- Design summary: `docs/design-summary.md`
- V2 architecture: `docs/v2-architecture.md`

## Next planned work

- dedupe evidence rows in final reports
- add `select_route_llm` with the same fallback/validation pattern
- expand route contracts beyond revenue
- improve evaluation coverage
