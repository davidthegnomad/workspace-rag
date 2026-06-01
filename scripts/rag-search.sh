#!/usr/bin/env bash
# Semantic search over Gnomad ORGANIZATION (wrapper for orchestrator agents).
#
# Usage (from anywhere):
#   /path/to/workspace-rag/scripts/rag-search.sh "how do we deploy to Firebase"
#   /path/to/workspace-rag/scripts/rag-search.sh "HIPAA" --domain 01_web_design
#
# From ORGANIZATION root:
#   02_ai_engineering/workspace-rag/scripts/rag-search.sh "your question"
#
# Remote mode (after Tailscale + vault deploy — see docs/DEPLOYMENT.md):
#   export RAG_MODE=remote RAG_REMOTE_HOST=data-vault RAG_REMOTE_PATH=/path/to/workspace-rag
#   ./scripts/rag-search.sh "question"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAG_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RAG_MODE="${RAG_MODE:-local}"
RAG_REMOTE_HOST="${RAG_REMOTE_HOST:-data-vault}"
RAG_REMOTE_PATH="${RAG_REMOTE_PATH:-/home/gnomad/workspace-rag}"
RAG_LIMIT="${RAG_LIMIT:-10}"

if [[ $# -lt 1 ]]; then
  echo "Usage: rag-search.sh \"natural language question\" [--domain D] [--type T] [--project P]" >&2
  exit 1
fi

run_local() {
  cd "$RAG_ROOT"
  python3 internal/cli.py search "$@" -n "$RAG_LIMIT"
}

run_remote() {
  # Pass all args quoted for remote shell
  local query shell_args
  query=$(printf '%q ' "$@")
  ssh -tt "$RAG_REMOTE_HOST" "cd $(printf '%q' "$RAG_REMOTE_PATH") && python3 internal/cli.py search ${query} -n ${RAG_LIMIT}"
}

case "$RAG_MODE" in
  local)  run_local "$@" ;;
  remote) run_remote "$@" ;;
  *)
    echo "Unknown RAG_MODE=$RAG_MODE (use local or remote)" >&2
    exit 1
    ;;
esac
