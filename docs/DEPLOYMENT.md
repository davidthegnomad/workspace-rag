# Deployment — Local & Swarm

> **Current mode:** `local` (MacBook Air)  
> **Target mode:** scheduled indexing on vault/Ryzen over Tailscale (no 24/7 watch required)

---

## Operating modes

| Mode | Index host | Ollama | Search from Mac | Freshness |
|------|------------|--------|-----------------|-----------|
| **`local`** (now) | MacBook | Local `localhost:11434` | Same machine | Manual / cron on Mac |
| **`remote-index`** (future) | i7 Data Vault | Ryzen via `OLLAMA_HOST` | Mac → Firestore + local query embed | Scheduled reindex on vault |
| **`remote-all`** (future) | i7 Data Vault | Ryzen | `ssh data-vault rag-search` | Scheduled reindex on vault |

**24/7 `watch` is optional.** Scheduled batch `index` is the recommended model when Ryzen is not always on.

---

## Local deployment (current — MacBook)

Use this until Tailscale, vault, and Ryzen batch jobs are configured.

### Prerequisites

- Python 3.9+ (3.10+ recommended)
- Ollama running with `nomic-embed-text`
- `.env` at repo root (see `.env.example`)
- Firestore vector index on `workspace_rag_internal.embedding` (768d)

### One-time setup

```bash
cd 02_ai_engineering/workspace-rag
pip install -r requirements.txt
cp .env.example .env   # fill FIREBASE_PROJECT_ID + GOOGLE_APPLICATION_CREDENTIALS
ollama pull nomic-embed-text
```

Vector index: Firebase Console → Firestore → Indexes, or `./internal/firebase/setup-index.sh` (needs gcloud + IAM).

### Daily use (from ORGANIZATION root)

```bash
./02_ai_engineering/workspace-rag/scripts/rag-search.sh "Firebase deployment checklist"
./02_ai_engineering/workspace-rag/scripts/rag-status.sh
```

### Indexing (local)

```bash
# Full reindex (~8k docs, hours on Mac CPU)
./02_ai_engineering/workspace-rag/scripts/rag-index.sh

# Optional: schedule on Mac (launchd/cron) — e.g. weekly Sunday 3am
# crontab -e:
# 0 3 * * 0 cd /path/to/workspace-rag && python3 internal/cli.py index >> .agents/LOGS/cron-index.log 2>&1
```

### Stop background index on Mac before migrating

```bash
kill $(cat 02_ai_engineering/workspace-rag/.agents/LOGS/index-run.pid) 2>/dev/null || true
```

---

## Swarm deployment (future — see [ROADMAP.md](../ROADMAP.md))

### Design principles

1. **MacBook = controller only** — orchestrator + search; no heavy indexing.
2. **i7 Data Vault = index source** — `WORKSPACE_ROOT` points at aggregated ORGANIZATION backup (most complete corpus).
3. **Ryzen 9 = Ollama GPU** — embeddings during index runs; machine does **not** need to be 24/7.
4. **MSI = not RAG host** — incomplete project sync; keep for scrapers/`agy` workloads.
5. **Firestore = shared brain** — all machines query the same `workspace_rag_internal` collection.

### Target topology

```text
[i7 Vault: ORGANIZATION backup] ──index (cron)──► [Ryzen: Ollama embed] ──► Firestore
                                                                                    ▲
[MacBook: orchestrator] ── rag-search.sh ──────────────────────────────────────────┘
         (query embed: local Ollama OR Ryzen when up)
```

### Scheduled indexing (no 24/7 watch)

When Ryzen is on (manual schedule or boot script):

```bash
# On vault or Ryzen — WORKSPACE_ROOT = canonical ORGANIZATION path
export OLLAMA_HOST=http://ai-powerhouse:11434   # Tailscale hostname for Ryzen
python3 internal/cli.py index
```

Suggested schedules:

| Trigger | When |
|---------|------|
| Ryzen login / startup script | User turns on desktop for work |
| Vault cron (2am) | Only if Ryzen is scheduled on at that time |
| Manual | After large doc sessions: `scripts/rag-index.sh` |

**Staleness:** search results lag until the next index run completes. Acceptable for SOPs/skills; not for sub-minute freshness.

### Remote scripts (after Tailscale)

Edit env in `scripts/rag-search.sh` / `scripts/rag-index.sh`:

```bash
export RAG_MODE=remote
export RAG_REMOTE_HOST=data-vault          # Tailscale MagicDNS
export RAG_REMOTE_PATH=/home/gnomad/workspace-rag
export OLLAMA_HOST=http://ai-powerhouse:11434   # index jobs only
```

### Mac search when Ryzen is off

Keep **query embedding** on the Mac (small model, ~274MB):

```bash
ollama pull nomic-embed-text
# OLLAMA_HOST unset → localhost; Firestore reads still work
./scripts/rag-search.sh "your question"
```

Indexing stays on vault/Ryzen when those machines are available.

---

## Environment variables

| Variable | Local | Swarm |
|----------|-------|-------|
| `FIREBASE_PROJECT_ID` | `gnomad-studio-client` | same |
| `GOOGLE_APPLICATION_CREDENTIALS` | path to service account JSON | on index host |
| `FIRESTORE_COLLECTION` | `workspace_rag_internal` | same |
| `WORKSPACE_ROOT` | auto-detected on Mac | vault backup path |
| `OLLAMA_HOST` | `http://localhost:11434` | `http://ai-powerhouse:11434` during index |
| `RAG_MODE` | `local` | `remote` (scripts) |

---

## Orchestrator integration

From ORGANIZATION root, agents should use:

```bash
02_ai_engineering/workspace-rag/scripts/rag-search.sh "<natural language question>"
```

See [AI_AGENT_GUIDE.md](./AI_AGENT_GUIDE.md) and [ROADMAP.md](../ROADMAP.md) Phase 4 for `RAG_QUERY` skill in `gnomad-swarm-core`.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Search: missing vector index | Firebase Console → Indexes → enable 768d vector on `embedding` |
| Search: Ollama error | `ollama serve`; Mac can embed queries locally even if index runs elsewhere |
| Index: slow on Mac | Expected; migrate to Ryzen GPU per ROADMAP |
| Stale results | Run `rag-index.sh`; check last index time in `status` |
| Filtered search fails | Composite index needed for `--domain`/`--type` — use unfiltered search or create index in Console |

---

*Update this doc when `RAG_MODE=remote` is activated.*
