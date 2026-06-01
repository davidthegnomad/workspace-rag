#!/usr/bin/env bash
# Full workspace reindex (batch — run on schedule, not 24/7).
#
# Local (now):
#   ./scripts/rag-index.sh
#
# Requires: Ollama with nomic-embed-text, .env configured, Firestore credentials.
# Duration: hours on Mac CPU; faster on Ryzen GPU when Phase 3 is ready.
#
# Remote (future):
#   export RAG_MODE=remote RAG_REMOTE_HOST=data-vault RAG_REMOTE_PATH=/path/to/workspace-rag
#   export OLLAMA_HOST=http://ai-powerhouse:11434   # on remote host during index
#   ./scripts/rag-index.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAG_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$RAG_ROOT/.agents/LOGS"

RAG_MODE="${RAG_MODE:-local}"
RAG_REMOTE_HOST="${RAG_REMOTE_HOST:-data-vault}"
RAG_REMOTE_PATH="${RAG_REMOTE_PATH:-/home/gnomad/workspace-rag}"

mkdir -p "$LOG_DIR"

run_local() {
  cd "$RAG_ROOT"
  echo "Indexing (WORKSPACE_ROOT from .env or auto-detect)"
  echo "Log: $LOG_DIR/index-run.log"
  python3 internal/cli.py index 2>&1 | tee -a "$LOG_DIR/index-run.log"
}

run_remote() {
  ssh -tt "$RAG_REMOTE_HOST" "cd $(printf '%q' "$RAG_REMOTE_PATH") && python3 internal/cli.py index"
}

case "$RAG_MODE" in
  local)  run_local ;;
  remote) run_remote ;;
  *)
    echo "Unknown RAG_MODE=$RAG_MODE (use local or remote)" >&2
    exit 1
    ;;
esac
