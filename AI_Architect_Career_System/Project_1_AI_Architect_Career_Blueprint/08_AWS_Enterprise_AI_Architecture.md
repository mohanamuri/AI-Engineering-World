# AWS Enterprise AI Architecture

## Reference layers
API/edge → auth → application/orchestrator → retrieval/data → model serving/API → evaluation/observability → storage.

## Services to know conceptually
API Gateway, Lambda, ECS/EKS, S3, IAM, Secrets Manager, CloudWatch, OpenSearch/vector search options, SageMaker and networking primitives.

The goal is not memorizing service names; be able to justify managed service vs Kubernetes/self-hosted alternatives.

## Interview exercise
Design for 10M documents and 10K concurrent users. State assumptions, estimate load, choose retrieval/indexing strategy, define SLOs, identify bottlenecks and explain cost controls.
