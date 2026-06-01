# Session State
> Last updated: 2026-06-01

## Done this session
- Reorganized repo: `shared/`, `internal/`, `external/`, `docs/`
- Migrated vector store from Supabase → Firebase Firestore
- Internal: auto-detect WORKSPACE_ROOT, delete-before-upsert, Firebase CLI setup script
- External: config.yaml scaffold + ROADMAP for distributable product
- Legacy Supabase migration → `docs/legacy/supabase-migration.sql`

## Next session priorities
1. User fills `internal/.env` with Firebase credentials
2. Run `./internal/firebase/setup-index.sh` + `ollama pull nomic-embed-text`
3. First internal index + smoke test search
4. Build `RAG_QUERY` skill in gnomad-swarm-core

## Blockers
- Firebase service account + vector index must be created manually (one-time)
