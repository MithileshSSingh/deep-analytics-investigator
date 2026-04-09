# Deep Analytics Investigator Agent — Design Summary

## Product
An agentic analytics investigator that diagnoses metric changes, validates likely causes, and explains what matters.

## Core Routes
1. Revenue investigation
2. Payment failure investigation
3. Refund investigation
4. Funnel leak investigation

## Core Product Positioning
Traditional analytics tools tell you what changed. This system investigates why it changed.

## Architecture
- API/UI layer
- Supervisor workflow
- Route-specific investigation workflows
- Query builders + validators
- Analytics database
- Evidence-backed ranking
- Confidence-aware report generation

## Core Design Principles
- Investigation over retrieval
- Route-specific workflows instead of one giant generic chain
- Evidence-backed likely causes
- Explicit contracts for metrics, schema, routes, and query outputs
- Guarded SQL execution
- Confidence-aware reporting

## Key Contracts
### Schema Registry
Defines available tables, columns, dimensions, joins, and route eligibility.

### Metric Registry
Defines metric meaning, base table, supported dimensions, route ownership, and validation query families.

### Route Contracts
Define required tables, expected artifacts, supported dimensions, and output expectations for each route.

### Query Contracts
Every query builder should return:
- name
- purpose
- sql
- output_shape

## Workflow Pattern
For each route:
- baseline check
- segment analysis
- hypothesis generation
- validation
- ranking
- report generation

## Shared Report Shape
- summary
- what_changed
- top_findings
- likely_causes
- next_steps
- confidence

## MVP Roadmap
### Phase 1
Revenue route only:
- seeded dataset
- baseline + segment delta queries
- validation queries
- ranking
- readable report
- API endpoint

### Phase 2
Quality hardening:
- evidence formatting
- ranking improvements
- guardrails
- evaluation cases

### Phase 3
Payment route

### Phase 4
Funnel route

### Phase 5
History, follow-ups, product polish

### Phase 6
LLM structured parsing, richer hypothesis generation, charts

## Evaluation
Evaluate on:
- route correctness
- metric interpretation correctness
- main cause identification
- segment identification
- evidence quality
- communication quality

Include both seeded anomaly datasets and neutral/no-anomaly datasets.

## Recommended Initial Stack
- Python 3.11+
- LangGraph
- LangChain
- FastAPI
- DuckDB
- Pandas
- Pydantic

## Immediate Development Goal
Build the first full vertical slice for:
"Why did revenue drop yesterday?"
