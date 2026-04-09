# Deep Analytics Investigator — V2 Architecture

## Goal

Build an agentic analytics investigator that can:

- understand a business question in natural language
- choose the right investigation route
- run evidence-backed analysis against structured data
- generate and validate likely causes
- explain findings clearly
- support follow-up investigative questions

Core principle:

> Deterministic systems find the facts. LLMs help decide what to inspect and how to explain it.

## V2 product philosophy

V2 should feel:
- more intelligent than the MVP
- more flexible than hardcoded routes
- still inspectable and trustworthy

It should not become:
- “LLM writes some SQL and vibes out a story”
- a black box that cannot justify its conclusions

## Core layers

### Interface layer
- FastAPI API
- future chat / UI interface
- request / response models
- investigation session handling

### Orchestration layer
- LangGraph workflow
- route-specific workflows
- planner / loop controller
- trace and audit state

### Intelligence layer
- LLM-assisted intent parsing
- route selection
- hypothesis generation
- narrative report generation
- follow-up planning

### Deterministic analytics layer
- metric registry
- schema registry
- query family registry
- SQL builders
- validation query library
- scoring / ranking engine

### Data layer
- DuckDB for local seeded demo
- future warehouse abstraction
- query execution / guardrails
- result normalization

### Evaluation + observability layer
- traces
- executed queries
- intermediate artifacts
- benchmark cases
- failure analysis

## Proposed V2 workflow

1. parse_question_llm
2. resolve_metric_and_route_candidates
3. select_route_llm
4. build_investigation_plan
5. run_baseline_queries
6. run_segment_queries
7. generate_hypotheses_llm
8. validate_hypotheses
9. rank_hypotheses
10. decide_next_step
11. optional evidence loop
12. generate_report_llm
13. return_response

## Route architecture

Each route should define:
- route name
- supported question intents
- required tables
- baseline query families
- segment query families
- validation families
- supported dimensions
- stop conditions
- expected report focus

## Core registries needed in V2

### Metric registry
Should define:
- canonical name
- business meaning
- calculation expression
- filters
- base table
- valid dimensions
- valid routes
- baseline strategies
- validation families

### Schema registry
Should define:
- tables
- columns
- types
- join paths
- route eligibility
- dimension availability
- time columns

### Query family registry
Instead of letting an LLM invent raw SQL, define reusable query families like:
- revenue_baseline
- segment_delta
- payment_success_rate
- error_code_cluster
- target_cluster_check
- checkout_to_payment_dropoff

Each family should have:
- parameters
- SQL template/builder
- expected output schema
- owning routes

### Route registry
Should define the route contract and eligible query families.

## State model for V2

Suggested state fields:

```python
{
  "question": str,
  "parsed_question": {...},
  "selected_route": {...},
  "metric_definition": {...},
  "plan": {...},
  "baseline_results": {...},
  "segment_results": [...],
  "evidence_artifacts": [...],
  "hypotheses": [...],
  "validated_hypotheses": [...],
  "ranked_hypotheses": [...],
  "final_report": {...},
  "executed_queries": [...],
  "trace": [...],
  "loop_count": int,
  "errors": [...]
}
```

## Confidence model

Confidence should be derived from:
- metric movement magnitude
- consistency across evidence
- direct validation support
- contradiction penalties
- sample-size sufficiency
- route relevance

## Recommended implementation order

1. Add registries properly:
   - route registry
   - query family registry
   - schema registry
2. Add an LLM parse node
3. Normalize evidence artifacts
4. Add LLM hypothesis generation
5. Add LLM report generation
6. Add route selection for multi-route support
7. Add decision/loop node for iterative investigation

## Recommended non-goals for V2

- arbitrary freeform SQL generation
- direct warehouse write-backs
- autonomous alerting/actions
- giant multi-agent system
- open-ended “ask anything about the business” promise

## Final stance

V2 should be:
- a deterministic evidence engine
- with an LLM reasoning shell

That balance gives trust, extensibility, and better UX without losing debuggability.
