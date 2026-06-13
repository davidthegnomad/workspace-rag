# Workspace RAG — Agent Swarm

> Tier 2 (Focused Team) | Escalation: `02_ai_engineering/gnomad-swarm-core/`

## Agent documentation (read first)

**All agents must read:** [docs/AI_AGENT_GUIDE.md](docs/AI_AGENT_GUIDE.md)

- When to query RAG vs maps vs direct file read
- CLI commands, filters (`--domain`, `--type`, `--project`)
- Orchestrator workflow and anti-patterns
- Index scope and exclusions (VAULT never indexed)

Human/portfolio overview: [docs/HUMAN_GUIDE.md](docs/HUMAN_GUIDE.md)

---

## MORPHEOUS: RAG Infrastructure Architect

**Stack**: Python, Ollama, Firebase Firestore vectors, watchdog  
**Location**: `02_ai_engineering/workspace-rag/internal/`

### Responsibilities
- Embedding model selection and optimization (currently nomic-embed-text)
- Chunking strategy tuning for optimal retrieval quality
- Firestore index management and query performance
- Query relevance evaluation and threshold calibration

### Conventions
- All embeddings generated locally via Ollama (never cloud) for internal
- VAULT content is never indexed
- Archive (06_archive) is excluded from indexing

## CYPHER: Data Pipeline Engineer

### Responsibilities
- Indexer reliability and error handling
- File watcher stability and delta reindex correctness
- CLI tool maintenance (`internal/cli.py`)
- Integration with agent swarm (RAG_QUERY skill in gnomad-swarm-core)

### Conventions
- Firestore vector indexes tracked via `internal/firebase/setup-index.sh`
- Shared core in `shared/`; Gnomad config in `internal/config.py`
- External product scaffold in `external/`

## Quick query (agents)

```bash
cd 02_ai_engineering/workspace-rag
python internal/cli.py search "your question" [--domain 02_ai_engineering] [--type sop]
python internal/cli.py status
```
