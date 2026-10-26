# Workspace RAG

Semantic search pipeline with two builds sharing a common core:

| Build | Path | Purpose |
|-------|------|---------|
| **Internal** | [`internal/`](internal/) | Gnomad ORGANIZATION workspace — agent swarm memory |
| **External** | [`external/`](external/) | Distributable product — any user's document folder |
| **Shared** | [`shared/`](shared/) | Chunking, embeddings, SQLite index, optional Firestore |

## Use it on your own files

The index stays on your machine. You do not need a Google account.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-local.txt
ollama pull nomic-embed-text

python external/cli.py index --root ~/Documents/my-notes
python external/cli.py search "onboarding checklist" --root ~/Documents/my-notes
```

That writes `~/Documents/my-notes/.workspace-rag/index.sqlite`. Search mixes meaning (the local embedding) with exact words (SQLite FTS5, which is BM25). A product code still matches even when the embedding does not.

`nomic-embed-text` is the default because it is small and runs in Ollama. Change `embedding_model` in `external/config.example.yaml` if you want a newer embedder, then index again.

Firestore is optional. Set `store: firestore` only if you already have a Firebase project. See [external/README.md](external/README.md).

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
