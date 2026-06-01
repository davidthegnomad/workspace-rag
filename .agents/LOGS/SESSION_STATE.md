# Session State
> Last updated: 2026-06-01

## Status: OPERATIONAL (local MacBook mode)

- Search: working via `scripts/rag-search.sh`
- Index: background job may still be running — check `scripts/rag-status.sh`
- Deployment: **local** until Tailscale + vault (see ROADMAP.md Phase 1–2)

## New this session
- `docs/DEPLOYMENT.md` — local now, vault/Ryzen scheduled index later (no 24/7 watch)
- `ROADMAP.md` — orchestrator pickup target (phases 0–5)
- `scripts/rag-search.sh`, `rag-index.sh`, `rag-status.sh` — `RAG_MODE=local` default

## Orchestrator
- Query: `02_ai_engineering/workspace-rag/scripts/rag-search.sh "<question>"`
- Pickup: `02_ai_engineering/workspace-rag/ROADMAP.md`

## Next (human / infra gates)
- Phase 1: Tailscale mesh + vault ORGANIZATION mirror
- Phase 2–3: move index to vault, Ollama on Ryzen when powered on
