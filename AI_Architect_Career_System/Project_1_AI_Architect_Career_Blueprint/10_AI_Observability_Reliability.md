# AI Observability & Reliability

## Four layers
1. Infrastructure: CPU, memory, network, GPU.
2. Application: latency, throughput, errors.
3. LLM/RAG: token usage, model latency, retrieval quality, groundedness.
4. Business: task success, user satisfaction, cost per successful task.

## Useful traces
request → retrieval → reranker → prompt → model → tool calls → validation → response.

The resume reports Prometheus, Grafana, Splunk and Dynatrace monitoring for AI pipelines. fileciteturn0file0L64-L69
