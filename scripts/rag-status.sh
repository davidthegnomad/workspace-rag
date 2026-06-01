#!/usr/bin/env bash
# Index statistics — chunk counts by domain.
#
# Usage: ./scripts/rag-status.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAG_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RAG_MODE="${RAG_MODE:-local}"
RAG_REMOTE_HOST="${RAG_REMOTE_HOST:-data-vault}"
RAG_REMOTE_PATH="${RAG_REMOTE_PATH:-/home/gnomad/workspace-rag}"

if [[ "$RAG_MODE" == "remote" ]]; then
  ssh -tt "$RAG_REMOTE_HOST" "cd $(printf '%q' "$RAG_REMOTE_PATH") && python3 internal/cli.py status"
else
  cd "$RAG_ROOT"
  python3 internal/cli.py status
  echo ""
  echo "Mode: local (see docs/DEPLOYMENT.md for swarm migration)"
  if [[ -f "$RAG_ROOT/.agents/LOGS/index-run.pid" ]] && ps -p "$(cat "$RAG_ROOT/.agents/LOGS/index-run.pid")" >/dev/null 2>&1; then
    echo "Background index: RUNNING (pid $(cat "$RAG_ROOT/.agents/LOGS/index-run.pid"))"
  fi
fi
