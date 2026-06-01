# Session State
> Last updated: 2026-06-01

## Done this session
- Installed `gcloud` CLI via Homebrew
- Service-account auth (no browser login)
- Hardened `.gitignore`, committed + pushed
- Smoke-tested Firestore writes (indexing works)
- **Full index running in background** — see `.agents/LOGS/index-run.log`

## In progress
- `python3 internal/cli.py index` — PID in `.agents/LOGS/index-run.pid`
- ~8790 documents; expect hours on local Ollama

## Blocked (needs one GCP IAM action)
- Firestore **vector index** creation failed: service account lacks `datastore.indexAdmin`
- Indexing works without it; **search will not work** until vector index exists
- Fix: GCP Console → IAM → `firebase-adminsdk-fbsvc@gnomad-studio-client.iam.gserviceaccount.com` → add role **Cloud Datastore Index Admin** (`roles/datastore.indexAdmin`), then re-run `./internal/firebase/setup-index.sh`
- Or: Firestore → Indexes → create vector index on `workspace_rag_internal.embedding` (768 dims)

## Commands
```bash
tail -f .agents/LOGS/index-run.log
python3 internal/cli.py status
kill $(cat .agents/LOGS/index-run.pid)   # stop index if needed
```
