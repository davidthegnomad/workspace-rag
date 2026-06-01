# Project SOP — Workspace RAG Pipeline

> Retrieval-Augmented Generation using Firestore vector search, Ollama local embeddings, and file watching.

---

## Environment Setup

```bash
cd 02_ai_engineering/workspace-rag
pip install -r requirements.txt
cp .env.example .env
# FIREBASE_PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS, FIRESTORE_COLLECTION
ollama pull nomic-embed-text
export FIREBASE_PROJECT_ID=your-project
./internal/firebase/setup-index.sh
```

## Development

```bash
# Internal (Gnomad)
python internal/cli.py index
python internal/cli.py search "query"
python internal/cli.py watch

# External (product)
python external/cli.py index
```

### Key Directories
| Directory | Purpose |
|-----------|---------|
| `shared/` | Chunking, embeddings, Firestore store |
| `internal/` | Gnomad ORGANIZATION indexer + watcher |
| `external/` | Distributable product scaffold |
| `docs/` | Architecture and stack decisions |

## Testing

```bash
python -c "from shared.store.firestore import FirestoreVectorStore; print('ok')"
python internal/cli.py --help
```

## Deployment

Local development tool only. No production deploy for internal. External product roadmap in `external/ROADMAP.md`.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Firebase auth error | Verify `GOOGLE_APPLICATION_CREDENTIALS` path and project ID |
| Vector index missing | Run `./internal/firebase/setup-index.sh` |
| Ollama not responding | `ollama serve` + `ollama pull nomic-embed-text` |
| Zero documents found | Check `WORKSPACE_ROOT` in internal/.env |

---

*Living document — update when processes change.*
