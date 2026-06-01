# Workspace RAG — AI Agent Guide

> **Operational instructions for AI agents** (orchestrators, sub-agents, Cursor agents).  
> Read this before querying the index or advising humans on RAG usage.

---

## Purpose (one paragraph)

Workspace RAG is Gnomad Studio’s **semantic retrieval layer** over the ORGANIZATION workspace. It answers: *“What does this organization already know about X?”* by returning ranked text passages with source paths. It does **not** replace project maps, direct file reads, or code search. Query RAG **before** broad filesystem crawls or reinventing documented solutions.

Human-facing context: [HUMAN_GUIDE.md](./HUMAN_GUIDE.md)

---

## Decision tree: RAG vs other tools

```
User / task needs context
        │
        ├─ Know exact file path? ──────────────────► Read file directly
        │
        ├─ Need to find which project/folder? ─────► WORKSPACE.md / ROOT_MAP / GUIDE_FILESYSTEM_MAP
        │
        ├─ Need code symbols / imports / grep? ────► rg / targeted search in project subfolder ONLY
        │
        ├─ Need org knowledge (SOP, skill, ADR,
        │  brief, prior decision, workflow)? ─────► RAG SEARCH (this system)
        │
        └─ Need secrets / credentials? ────────────► VAULT (never RAG — not indexed)
```

**Default for orchestrator agents:** Map lookup → **RAG query** → narrow file read in returned `source_path` → execute in isolated subfolder.

---

## When to use RAG

| Scenario | Example query |
|----------|---------------|
| Cross-project prior art | `"how we implemented Firebase App Check"` |
| Agency SOPs & workflows | `"nonprofit website build process"` |
| Agent directives & autonomy | `"chronicler session memory protocol"` |
| Architecture decisions | `"Firestore vs Supabase decision"` |
| Client/commercial context | `"brand guide typography rules"` |
| Skill library patterns | `"Playwright E2E testing skill"` |
| Onboarding unfamiliar domain | `"deployment branch for Firebase hosting"` |

---

## When NOT to use RAG

| Scenario | Use instead |
|----------|-------------|
| Exact file known | `Read` tool on path |
| Editing source code | Read/grep within project directory |
| Live session state | `.agents/LOGS/SESSION_STATE.md` |
| Secrets, API keys, `.env` | `03_admin_finance/VAULT/` (never indexed) |
| Legacy archived content | `06_archive/` (excluded) |
| Binary assets, JSON configs, lockfiles | Direct file access |
| “What changed in the last 5 minutes?” | Git diff, session logs |

---

## How to query

### CLI (preferred for agents with shell)

**Wrapper scripts (from ORGANIZATION root or repo root):**

```bash
02_ai_engineering/workspace-rag/scripts/rag-search.sh "your natural language question"
02_ai_engineering/workspace-rag/scripts/rag-status.sh
02_ai_engineering/workspace-rag/scripts/rag-index.sh    # full reindex — hours
```

`RAG_MODE=local` by default. Future swarm: `RAG_MODE=remote` — see [DEPLOYMENT.md](./DEPLOYMENT.md).

Working directory (direct CLI): `02_ai_engineering/workspace-rag`

```bash
python internal/cli.py search "your natural language question"
python internal/cli.py search "HIPAA compliance" --domain 01_web_design
python internal/cli.py search "agent directives" --type agent_directive
python internal/cli.py search "swarm setup" --project gnomad-swarm-core
python internal/cli.py search "query" --limit 5 --threshold 0.75
python internal/cli.py status
```

### Python import (in-process)

```python
from internal.query import search, search_by_domain, search_by_type, search_by_project

results = search("Firebase deployment checklist", limit=5)
results = search_by_domain("02_ai_engineering", "RAG pipeline architecture")
results = search_by_type("sop", "index rebuild procedure")
```

Each `SearchResult` exposes: `content`, `source_path`, `domain`, `project`, `doc_type`, `similarity`, `title`.

**After RAG returns paths:** Read the full source files for authoritative context. RAG chunks are excerpts — not substitutes for the complete document.

---

## Filters & metadata

### Domains (`--domain`)

| Value | Contents |
|-------|----------|
| `01_web_design` | Client sites, demos, live deployments |
| `02_ai_engineering` | Swarm core, RAG, trading agents, AI tools |
| `03_admin_finance` | Brand, corporate docs (not VAULT) |
| `04_business_ops` | SOPs, briefs, brand guides, agency ops |
| `05_apps_and_extensions` | Extensions, apps, desktop tools |
| `SKILL_LIBRARY` | Shared skill catalog (573+ skills) |

Apply domain filter when the user’s task clearly belongs to one area — reduces noise.

### Document types (`--type`)

| `doc_type` | Typical paths |
|------------|---------------|
| `agent_directive` | `directives/`, `AGENTS.md`, `AGENTS/*.md` |
| `chronicler` | `CHRONICLER.md`, `HANDOFF_*.md` |
| `sop` | `SOPS/`, `workflows/`, `PROJECT_SOP.md` |
| `skill` | `SKILLS/**/*.md` |
| `decision` | `DECISIONS/**/*.md` |
| `reference` | `references/`, `KNOWLEDGE_BASE/` |
| `client_brief` | `Clients/`, `brand-guides/` |
| `proposal` | `proposals/`, `MARKETING/`, `STRATEGIES/` |
| `project_doc` | `README.md`, `ROADMAP.md`, `TODO.md` |
| `autonomy` | `SELF_EVOLUTION.md`, `SWARM_AUTONOMY_FRAMEWORK.md` |
| `workspace_doc` | Root `WORKSPACE.md`, top-level manifests |
| `general` | Everything else matching index rules |

Use `--type sop` when looking for procedures; `--type decision` for ADRs; `--type skill` for reusable patterns.

### Project filter (`--project`)

Second path segment under domain, e.g. `gnomad-swarm-core` in `02_ai_engineering/gnomad-swarm-core/...`.

---

## Index scope (hard rules)

**Indexed extensions:** `.md`, `.txt` only.

**Indexed directories:** `01_web_design`, `02_ai_engineering`, `03_admin_finance`, `04_business_ops`, `05_apps_and_extensions`, `SKILL_LIBRARY`, plus root-level `*.md`.

**Excluded directory names (anywhere in path):**  
`node_modules`, `.next`, `.venv`, `__pycache__`, `dist`, `build`, `.firebase`, `.git`, **`VAULT`**, **`06_archive`**.

If RAG returns zero results, the content may be excluded, not yet indexed, below similarity threshold, or not written as markdown/text.

---

## Query craft (best practices)

1. **Write questions, not keywords.** `"What is our Firebase production security checklist?"` beats `"firebase security"`.
2. **Start broad, then filter.** First unfiltered search; if noisy, add `--domain` or `--type`.
3. **Lower threshold sparingly.** Default `0.7`. Try `0.6` only if genuinely sparse corpus; never below `0.5` without cause.
4. **Limit results.** Default 10; use `-n 5` for orchestrator context conservation.
5. **Follow sources.** Always open `source_path` relative to ORGANIZATION root for full context.
6. **Combine with map.** RAG finds *content*; `WORKSPACE.md` finds *location*.

### Anti-patterns

- ❌ Recursive grep across entire ORGANIZATION before trying RAG
- ❌ Treating RAG excerpts as complete authoritative docs without reading source
- ❌ Expecting RAG to return code implementations (index is prose-focused)
- ❌ Querying for vault secrets or archived legacy content
- ❌ Mass-indexing or indexing VAULT (violates project policy)

---

## Pipeline reference (for accurate explanations)

| Step | Module | Behavior |
|------|--------|----------|
| Discovery | `internal/discover.py` | Walk indexed domains; skip excluded paths |
| Classification | `internal/config.py` | Assign `doc_type` from path patterns |
| Chunking | `shared/chunking.py` | Markdown-header splits; ~500 tokens; 50 overlap |
| Embedding | `shared/embeddings.py` | Ollama `nomic-embed-text`, 768 dimensions |
| Storage | `shared/store/firestore.py` | Firestore `find_nearest`, cosine similarity |
| Search | `internal/query.py` | Embed query → KNN → filter by metadata |
| Re-index | `internal/indexer.py` | Delete chunks by `source_path`, upsert fresh |
| Watch | `internal/watcher.py` | Auto re-index on create/modify/delete |

**Collection:** `workspace_rag_internal` (configurable via `FIRESTORE_COLLECTION`).

**Similarity:** Firestore distance converted to `similarity = 1 - cosine_distance`; results below `--threshold` are dropped.

---

## Orchestrator workflow (mandatory sequence)

Per Gnomad Master Orchestrator policy:

1. **Route** — Locate project in `WORKSPACE.md` or domain `ROOT_MAP.md`.
2. **Retrieve** — `python internal/cli.py search "..."` with appropriate filters.
3. **Read** — Open top 1–3 `source_path` files in the relevant subfolder.
4. **Execute** — Restrict writes/tools to target project path (hub-and-spoke isolation).
5. **Update** — Record outcomes in project `CHRONICLER.md` / `SESSION_STATE.md` (not RAG-indexed live state).

---

## Troubleshooting (agent responses)

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| No results | Unindexed content, wrong filter, high threshold | Run `status`; relax threshold; remove filters |
| Stale content | Index not updated | Human runs `index` or `watch` |
| Firebase auth error | Missing credentials | Check `GOOGLE_APPLICATION_CREDENTIALS`, `FIREBASE_PROJECT_ID` |
| Ollama error | Model not running | `ollama serve` + `ollama pull nomic-embed-text` |
| Wrong domain in results | Missing filter | Add `--domain` |

Do not attempt to fix Firebase/Ollama infrastructure unless the user explicitly requests ops work — report the error and suggest [PROJECT_SOP.md](../.agents/PROJECT_SOP.md).

---

## External build (do not confuse)

`external/` is a **distributable product scaffold** — user-defined folders via `config.yaml`, collection `workspace_rag_external`. Orchestrator agents working on Gnomad ORGANIZATION should use **`internal/` only**.

---

## Quick reference card

```
TOOL:     scripts/rag-search.sh "<question>" [--domain D] [--type T] [--project P]
          (or: python internal/cli.py search "<question>" ...)
WHEN:     Org knowledge, SOPs, skills, decisions, briefs — before broad search
NOT FOR:  Code, secrets, exact paths, session state, archive
AFTER:    Read full source_path files; execute in isolated project folder
EXCLUDES: VAULT, 06_archive, node_modules, build dirs, non-.md/.txt
DEFAULTS: threshold=0.7, limit=10, model=nomic-embed-text, dims=768
DEPLOY:   local now — ROADMAP.md Phase 1–3 for vault/Ryzen migration
```

---

*Agents: prefer this guide over inferring RAG behavior from conversation memory.*
