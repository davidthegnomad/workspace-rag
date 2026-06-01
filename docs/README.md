# Workspace RAG — Documentation

Semantic search over the Gnomad ORGANIZATION workspace (and future external product).

## Start here

| Document | Audience | Purpose |
|----------|----------|---------|
| **[Human Guide](./HUMAN_GUIDE.md)** | Executives, stakeholders, portfolio readers, technical leads | What RAG is, why it exists, business outcomes, stack, setup, security |
| **[AI Agent Guide](./AI_AGENT_GUIDE.md)** | Orchestrator agents, Cursor agents, swarm workers | When to query, filters, workflow, anti-patterns, CLI reference |

## Engineering reference

| Document | Purpose |
|----------|---------|
| [Deployment (local + swarm)](./DEPLOYMENT.md) | Where RAG runs; Mac now, vault/Ryzen later; scheduled vs watch |
| [Architecture](./ARCHITECTURE.md) | Repository layout, data flow, collection separation |
| [Stack & scaling](./STACK.md) | Firebase decision, cost model, product scaling paths |
| [Legacy Supabase schema](./legacy/supabase-migration.sql) | Archived pgvector migration (reference only) |

## Roadmap & operations

| Document | Purpose |
|----------|---------|
| [ROADMAP.md](../ROADMAP.md) | **Orchestrator pickup** — phases 0–5, swarm migration, checkboxes |
| [Project SOP](../.agents/PROJECT_SOP.md) | Environment setup, commands, troubleshooting |
| [AGENTS.md](../AGENTS.md) | Swarm roles (MORPHEOUS, CYPHER) |
| [scripts/](../scripts/) | `rag-search.sh`, `rag-index.sh`, `rag-status.sh` |
| [internal/README.md](../internal/README.md) | Internal build quick start |
| [external/README.md](../external/README.md) | External product scaffold |
| [external/ROADMAP.md](../external/ROADMAP.md) | Distributable product roadmap |

## Quick commands

```bash
scripts/rag-search.sh "your question"
scripts/rag-status.sh
scripts/rag-index.sh          # scheduled batch — not 24/7 watch
python internal/cli.py watch  # optional live reindex (local dev only)
```

Deployment: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) · Roadmap: [ROADMAP.md](ROADMAP.md)
