# Workspace RAG

**Semantic memory for Gnomad Studio** — search 7,000+ document passages across web design, AI engineering, finance, business ops, and a 573-skill library by meaning, not filename.

## Documentation

| Guide | Who it's for |
|-------|----------------|
| **[Human Guide](docs/HUMAN_GUIDE.md)** | Portfolio, executives, stakeholders — problem, outcomes, stack, setup |
| **[AI Agent Guide](docs/AI_AGENT_GUIDE.md)** | AI agents — when to query, filters, workflow, anti-patterns |
| **[Docs index](docs/README.md)** | Full documentation map |

## What it does

- Indexes `.md` / `.txt` across Gnomad ORGANIZATION domains `01`–`05` + `SKILL_LIBRARY`
- Embeds locally via Ollama (`nomic-embed-text`) — private, no cloud embedding API
- Stores vectors in Firebase Firestore — same stack as client projects
- Excludes `VAULT/`, `06_archive/`, and build artifacts by design

Agents and humans query before broad filesystem search: SOPs, skills, client briefs, decisions, and cross-project knowledge become searchable in seconds.

## Architecture (two builds, one core)

| Build | Path | Purpose |
|-------|------|---------|
| **Internal** | [`internal/`](internal/) | Gnomad ORGANIZATION — agent swarm memory |
| **External** | [`external/`](external/) | Distributable product — any user's document folder |
| **Shared** | [`shared/`](shared/) | Chunking, embeddings, Firestore vector store |

## Quick start (internal)

```bash
pip install -r requirements.txt
cp .env.example .env   # Firebase project + service account
ollama pull nomic-embed-text
export FIREBASE_PROJECT_ID=your-project
./internal/firebase/setup-index.sh

python internal/cli.py index
python internal/cli.py search "Firebase deployment"
python internal/cli.py status
```

See [docs/HUMAN_GUIDE.md](docs/HUMAN_GUIDE.md) for full setup and [internal/README.md](internal/README.md) for command reference.

## Stack

| Component | Technology |
|-----------|------------|
| Embeddings | Ollama `nomic-embed-text` (768d, local) |
| Vector store | Firebase Firestore native vector search |
| Indexer | Python + watchdog |
| CLI | Click + Rich |

Details: [docs/STACK.md](docs/STACK.md) · [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Legacy

Supabase/pgvector schema archived at [docs/legacy/supabase-migration.sql](docs/legacy/supabase-migration.sql).
