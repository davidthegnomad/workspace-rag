# Tech Stack — Distribution & Scaling

## Current stack (v1)

| Component | Technology | Distribution fit | Scale notes |
|-----------|------------|------------------|-------------|
| Embeddings | Ollama (local) | Requires Ollama install per machine | CPU-bound; fine for personal/small team |
| Vector DB | Firestore | Firebase project per user or shared multi-tenant | GA vector search; 2048 dim max; 1000 results/query |
| Indexer | Python CLI | `pip install` or PyInstaller | Batch writes; 400 docs/batch delete |
| Watcher | watchdog | Internal only (external TBD) | Local filesystem only |
| Auth | Service account JSON | Standard Firebase pattern | Move to Cloud Functions for SaaS |

## Firebase vs Supabase (decision)

**Chosen: Firebase Firestore** for Gnomad because:
- Already used across client projects (App Hosting, Auth, Firestore)
- Managed vector indexes — no Postgres ops
- Scales horizontally; pay per read/write/storage
- Server-side SDK supports `find_nearest` with pre-filters

Supabase/pgvector remains archived for reference. Revisit only if you need SQL joins or self-hosted Postgres.

## Scaling paths

### Internal (Gnomad swarm)
1. **Now**: Local Ollama + Firestore on your Firebase project
2. **Next**: Background indexer on MSI worker via SSH for full reindex
3. **Later**: Cloud Function triggered by Storage/Firestore for auto-embed on doc upload

### External (product)
1. **Phase 1**: CLI + config.yaml (current)
2. **Phase 2**: Tauri desktop app; bundled Ollama optional
3. **Phase 3**: SaaS — Cloud Functions embed with Vertex AI; multi-tenant collections; API key auth

## Cost model (Firestore)

- Storage: ~1–2 KB per chunk + 768-float vector
- Reads: 1 per search (+ index reads)
- Writes: chunks × docs on full reindex
- For ~10k chunks: negligible on Spark plan; monitor at 100k+

## Security

- **Never index VAULT** (internal config excludes it)
- Service account keys in `.env` only — never commit
- External product: consider Firebase App Check + Cloud Functions proxy so users never hold service account keys

## Embedding model

`nomic-embed-text` (768 dimensions) — local, free, good for markdown/docs. Alternatives for external SaaS: Vertex `text-embedding-005` (cloud, higher quality, cost per token).
