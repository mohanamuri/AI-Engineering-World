# Model Context Protocol (MCP)

## Mental model
MCP standardizes how an AI application exposes/discovers tools and contextual resources to models/agents.

## Architecture
Agent/Host → MCP client → MCP server → enterprise API/service.

## Design checklist
Authentication, authorization, input schemas, output schemas, timeouts, auditability, least privilege, idempotency and error handling.

The resume describes custom MCP servers exposing Kubernetes, Dynatrace, Splunk and Jira APIs and using MCP for AI-powered infrastructure operations. fileciteturn0file0L41-L49
