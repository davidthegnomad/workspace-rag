# Architecture

```
workspace-rag/
├── shared/                 # Shared library (both builds)
│   ├── chunking.py         # Markdown-aware token chunking
│   ├── embeddings.py       # Ollama embed calls
│   └── store/
│       └── firestore.py    # Firestore vector CRUD + KNN search
├── internal/               # Gnomad-only
│   ├── config.py           # ORGANIZATION paths, doc types, VAULT exclusions
│   ├── discover.py         # Domain-aware document discovery
│   ├── indexer.py
│   ├── query.py
│   ├── watcher.py
│   ├── cli.py
│   └── firebase/setup-index.sh
└── external/               # Distributable product
    ├── config.yaml         # User workspace + collection
    ├── discover.py         # Generic folder walk
    ├── indexer.py
    ├── cli.py
    └── ROADMAP.md
```

## Data flow

```mermaid
flowchart LR
    Docs[Markdown / TXT files] --> Discover
    Discover --> Chunk[shared/chunking]
    Chunk --> Embed[Ollama nomic-embed-text]
    Embed --> FS[(Firestore collection)]
    Query[Search query] --> Embed
    Embed --> KNN[find_nearest COSINE]
    KNN --> FS
    KNN --> Results[Ranked chunks]
```

## Collection separation

| Build | Default collection | Indexed scope |
|-------|-------------------|---------------|
| Internal | `workspace_rag_internal` | ORGANIZATION domains 01–05 + SKILL_LIBRARY |
| External | `workspace_rag_external` | User-defined folder via config.yaml |

Both can live in one Firebase project without collision.

## Agent integration (internal)

Swarm agents should follow [AI_AGENT_GUIDE.md](./AI_AGENT_GUIDE.md):

- CLI: `python internal/cli.py search "..."` with optional `--domain`, `--type`, `--project`
- Python: `from internal.query import search, search_by_domain, search_by_type`
- Planned: `RAG_QUERY` skill in gnomad-swarm-core

Human-facing overview: [HUMAN_GUIDE.md](./HUMAN_GUIDE.md)

## Re-index behavior

- **Per-file**: delete existing chunks by `source_path`, then upsert new chunks (no duplicates).
- **Full index**: same per-file logic; does not wipe unrelated files.
