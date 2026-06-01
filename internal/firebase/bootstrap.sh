#!/usr/bin/env bash
# Automated bootstrap — no browser login required (uses service account from .env)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.homebrew/bin:${PATH}"

if [[ ! -f .env ]]; then
  echo "Missing .env — copy from .env.example first."
  exit 1
fi

# shellcheck disable=SC2046
export $(grep -v '^#' .env | grep -v '^$' | xargs)

CRED="${GOOGLE_APPLICATION_CREDENTIALS:?}"
PROJECT="${FIREBASE_PROJECT_ID:?}"

echo "==> Activating service account for ${PROJECT}"
gcloud auth activate-service-account --key-file="$CRED" --project="$PROJECT" --quiet
gcloud config set project "$PROJECT" --quiet

echo "==> Creating Firestore vector index (768d on ${FIRESTORE_COLLECTION:-workspace_rag_internal})"
if ! FIREBASE_PROJECT_ID="$PROJECT" ./internal/firebase/setup-index.sh; then
  echo ""
  echo "WARN: Index creation failed (service account may lack roles/datastore.indexAdmin)."
  echo "      Indexing still works; search needs the vector index."
  echo "      Fix: GCP Console → IAM → grant firebase-adminsdk Index Admin, or create index in Firestore → Indexes UI."
fi

echo "==> Starting full index (log: .agents/LOGS/index-run.log)"
nohup python3 internal/cli.py index >> .agents/LOGS/index-run.log 2>&1 &
echo $! > .agents/LOGS/index-run.pid
echo "PID: $(cat .agents/LOGS/index-run.pid)"
