# AI Architecture Foundations

## Mental model
An enterprise AI system is a set of cooperating layers:

User/API → orchestration → retrieval/tools → model(s) → validation/guardrails → response

Cross-cutting: identity, security, observability, evaluation, cost, reliability and governance.

## Architect's checklist
- Functional requirements
- Non-functional requirements
- Data sources and ownership
- Latency/SLO
- Availability
- Scale/concurrency
- Security and tenancy
- Model strategy
- Retrieval/tool strategy
- Evaluation
- Observability
- Cost
- Failure modes
- Human-in-the-loop requirements

## Interview habit
Always state assumptions before choosing technologies.
