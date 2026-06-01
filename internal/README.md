# Internal — Gnomad Studio RAG

Semantic search across the **ORGANIZATION** workspace for agent swarm use. Indexes Gnomad domain folders, doc types, and excludes VAULT/archive.

## Setup

```bash
cd workspace-rag
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Firebase project + service account path
ollama pull nomic-embed-text

export FIREBASE_PROJECT_ID=your-project
./internal/firebase/setup-index.sh
```

## Commands

```bash
python internal/cli.py index
python internal/cli.py search "HIPAA compliance" --domain 01_web_design
python internal/cli.py search "agent directives" --type agent_directive
python internal/cli.py status
python internal/cli.py watch
```

## Firebase vs Supabase

Internal now uses **Firestore vector search** to align with your existing Firebase stack. Internal and external use separate collections (`workspace_rag_internal` / `workspace_rag_external`) in the same Firebase project.

Legacy Supabase schema: [../docs/legacy/supabase/migration.sql](../docs/legacy/supabase/migration.sql)
