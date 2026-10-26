# External — a RAG for any folder

Point it at Markdown and text you already have. Embeddings run in Ollama. The index is a SQLite file next to those notes. Nothing is uploaded.

## Setup

```bash
cd workspace-rag
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-local.txt
ollama pull nomic-embed-text
```

## Commands

```bash
python external/cli.py index --root ~/Documents/my-notes
python external/cli.py search "deployment checklist" --root ~/Documents/my-notes
python external/cli.py status --root ~/Documents/my-notes
```

Or copy `config.example.yaml` to `config.yaml`, set `workspace_root`, and leave `--root` off.

## What it searches

- Meaning: cosine similarity on the Ollama embedding
- Exact words: SQLite FTS5 (BM25)
- The two lists are merged with reciprocal rank fusion, so a rare code or name is not dropped just because the vector missed it

Notes are split on Markdown headings, then on a token limit, with overlap so a sentence is not cut away from its heading.

## Firestore

Leave this off unless you already run Firebase. In `config.yaml`:

```yaml
store: firestore
firestore_collection: workspace_rag_external
```

Then install `requirements.txt` and set `FIREBASE_PROJECT_ID` and `GOOGLE_APPLICATION_CREDENTIALS` in `.env`.
