# Agentic AI

## Core mental model
Agent = model + instructions + tools + state + decision loop + stopping conditions.

## Patterns
- ReAct
- Plan-and-Execute
- Reflection
- Tool-calling
- Supervisor
- Human approval

## Architect's questions
What can the agent do? What can it not do? Which actions require approval? How is state persisted? How are loops bounded? How are tool failures handled? How are permissions enforced?

## Reliability controls
Timeouts, retries, idempotency, max iterations, tool allowlists, schema validation, human approval, audit logs and fallback models.
