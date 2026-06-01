# Workspace RAG — Roadmap

> **For orchestrator agents:** This file is a pickup target when scanning ORGANIZATION subfolders for `ROADMAP.md` / `TODO.md`.  
> **Current deployment mode:** `local` (MacBook) — see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Phase 0 — Local MacBook (in progress)

MacBook runs index + search until swarm infra is ready. **No 24/7 watch required** — use scheduled or manual reindex.

- [x] Internal/external split + Firestore backend
- [x] `.env.example`, gitignore for secrets
- [x] Firebase vector index on `gnomad-studio-client`
- [x] Semantic search operational
- [x] Deployment docs + wrapper scripts (`scripts/rag-*.sh`)
- [ ] Complete first full index of ORGANIZATION (~8,790 docs)
- [ ] Stop Mac background index after migration plan confirmed
- [ ] Optional: weekly `cron`/`launchd` reindex on Mac until Phase 2
- [ ] Add composite Firestore indexes for `--domain` / `--type` filtered search (as needed)
- [ ] Create `RAG_QUERY` skill in `02_ai_engineering/gnomad-swarm-core/.agents/SKILLS/`

---

## Phase 1 — Tailscale & swarm prerequisites

Blocked on: all machines on Tailscale, MagicDNS hostnames stable.

- [ ] Verify hostnames in `SWARM_HARDWARE_MAP.md` (controller-mac, data-vault, ai-powerhouse, agent-base)
- [ ] SSH keys: Mac → vault, Mac → Ryzen, vault → Ryzen
- [ ] Confirm canonical ORGANIZATION path on each machine (see `scripts/copy-organization-to-mac.sh`)
- [ ] Decide index corpus source of truth:
  - [ ] **Option A:** i7 vault backup mirror (superset, may lag)
  - [ ] **Option B:** Ryzen `/mnt/SteamDrive/ORGANIZATION` (live, if primary edit surface)
- [ ] Document chosen path in `docs/DEPLOYMENT.md`

---

## Phase 2 — i7 Data Vault (index host)

Blocked on: Phase 1, vault ORGANIZATION mirror configured.

- [ ] Clone `workspace-rag` on vault
- [ ] Deploy `.env` + service account JSON (vault-local path, not in git)
- [ ] Set `WORKSPACE_ROOT` to vault ORGANIZATION backup path
- [ ] `pip install -r requirements.txt` on vault
- [ ] Smoke test: `python3 internal/cli.py status`
- [ ] First full index from vault corpus
- [ ] Schedule cron reindex (daily or weekly — **no watch required**)
- [ ] Remove indexing workload from MacBook

---

## Phase 3 — Ryzen 9 (Ollama + scheduled index)

Blocked on: Phase 1. Ryzen does **not** need to be 24/7.

- [ ] Ollama on Ryzen with `nomic-embed-text` (GPU pool per `SWARM_HARDWARE_MAP.md`)
- [ ] Tailscale: vault/Mac reach `http://ai-powerhouse:11434`
- [ ] Index jobs set `OLLAMA_HOST=http://ai-powerhouse:11434`
- [ ] Ryzen startup or scheduled script: run index when machine is on
- [ ] Mac keeps local Ollama **for query embedding only** (search works when Ryzen off)

---

## Phase 4 — Orchestrator integration (org-wide)

When user runs orchestrator over full ORGANIZATION to pickup roadmaps/todos:

- [ ] Orchestrator scans `**/ROADMAP.md` and `**/TODO.md` across domains 01–05
- [ ] Master `.cursorrules` RAG-first rule → use `scripts/rag-search.sh` (not raw grep)
- [ ] `RAG_QUERY` skill published in gnomad-swarm-core with CLI + filter reference
- [ ] `scripts/rag-search.sh`: switch `RAG_MODE=remote` when Phase 2 complete
- [ ] Session template for ORGANIZATION orchestrator (see `docs/AI_AGENT_GUIDE.md`)

---

## Phase 5 — External product (parallel track)

See [external/ROADMAP.md](external/ROADMAP.md) — distributable RAG for non-Gnomad users.

---

## Explicit non-goals

- **MSI as RAG host** — incomplete project sync; use for `agy`/scrapers only
- **24/7 `watch` on MacBook** — battery/thermal; use scheduled index instead
- **Indexing VAULT or `06_archive`** — policy exclusion, permanent

---

## Pickup metadata (orchestrator)

| Field | Value |
|-------|--------|
| Project | `02_ai_engineering/workspace-rag` |
| Owner agents | MORPHEOUS (retrieval), CYPHER (pipeline) |
| Escalation | `02_ai_engineering/gnomad-swarm-core/` |
| Active phase | **Phase 0** |
| Next human gate | Tailscale + vault ORGANIZATION mirror (Phase 1) |

---

*Update checkboxes as work completes. Orchestrator: prefer this file over conversation memory for RAG infra status.*
