# Multi-Agent Systems

## Patterns
1. Sequential pipeline
2. Parallel fan-out/fan-in
3. Supervisor routing
4. Debate and Judge
5. Research team/shared memory

The resume explicitly documents these patterns and describes a Proponent/Opponent debate followed by a neutral Judge. fileciteturn0file0L33-L40

## When NOT to use multi-agent
If one model + tools solves the problem reliably, extra agents add latency, cost and coordination failure.

## Debate architecture
Problem → independent proposals → critique/opposition → additional rounds if needed → judge/synthesis → evidence-backed final answer.

## Evaluation
Compare single-agent baseline vs multi-agent system on accuracy, groundedness, latency, cost and failure rate.
