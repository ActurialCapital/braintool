---
verified_at: 2026-08-07
status: removed
---

# gitingest-mcp

**removed** as of 2026-08-07.

## Decisions

| Date | Decision | Evidence | Reason |
|---|---|---|---|
| 2026-08-07 | **removed** | Failed to connect: `ModuleNotFoundError: mcp.server.fastmcp` | Upstream package stale against current MCP SDK (FastMCP graduated out of `mcp`). Re-evaluate pinned, project-scoped, when this repo needs repo-ingest. |

## Re-evaluate when

- the evidence above changes (invocations, health, churn)
- a sweep surfaces a replacement that scores higher on fit
- `verified_at` is more than 90 days old

<!-- generated above; hand-written notes below survive --force -->
