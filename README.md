# Workspace RAG

Semantic search pipeline with two builds sharing a common core:

| Build | Path | Purpose |
|-------|------|---------|
| **Internal** | [`internal/`](internal/) | Gnomad ORGANIZATION workspace — agent swarm memory |
| **External** | [`external/`](external/) | Distributable product — any user's document folder |
| **Shared** | [`shared/`](shared/) | Chunking, embeddings, Firestore vector store |

## Stack

- **Embeddings**: Ollama `nomic-embed-text` (768d, local, private)
- **Vector store**: Firebase Firestore native vector search
- **Indexer**: Python + watchdog (internal watcher; external watcher TBD)
- **CLI**: Click + Rich

See [docs/STACK.md](docs/STACK.md) for distribution and scaling notes.

## Quick start (internal — Gnomad)

```bash
pip install -r requirements.txt
cp .env.example .env   # add Firebase project + service account
ollama pull nomic-embed-text
export FIREBASE_PROJECT_ID=your-project
./internal/firebase/setup-index.sh

python internal/cli.py index
python internal/cli.py search "Firebase deployment"
python internal/cli.py status
```

## Quick start (external — distributable)

```bash
cp external/config.example.yaml external/config.yaml
cp .env.example .env
python external/cli.py index
python external/cli.py search "onboarding checklist"
```

## Why Firebase?

Gnomad projects already run on Firebase. Firestore vector search (GA) supports 768-dim embeddings, pre-filters, and scales without running Postgres. Internal and external indexes use **separate collections** in the same project.

Legacy Supabase/pgvector schema archived at [docs/legacy/supabase-migration.sql](docs/legacy/supabase-migration.sql).

## Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/STACK.md](docs/STACK.md)
- [internal/README.md](internal/README.md)
- [external/README.md](external/README.md) + [external/ROADMAP.md](external/ROADMAP.md)
