# External — Distributable Workspace RAG

Semantic search product for **any** document folder. Uses the same `shared/` core as internal but with user-owned configuration.

## Setup

```bash
cd workspace-rag
pip install -r requirements.txt
cp external/config.example.yaml external/config.yaml
cp ../.env.example ../.env
# Edit config.yaml (workspace_root) and .env (Firebase credentials)
ollama pull nomic-embed-text
./internal/firebase/setup-index.sh   # set FIRESTORE_COLLECTION=workspace_rag_external
```

## Commands

```bash
python external/cli.py index
python external/cli.py search "deployment checklist"
python external/cli.py status
```

See [ROADMAP.md](./ROADMAP.md) for product phases.
