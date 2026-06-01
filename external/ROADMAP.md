# External Product Roadmap

Distributable semantic search over local markdown/text folders.

## Phase 1 — CLI MVP (current)
- [x] Shared core: chunking, Ollama embeddings, Firestore vector store
- [x] User-configurable `config.yaml` + `.env`
- [ ] File watcher for delta reindex
- [ ] Packaging: `pip install workspace-rag` or PyInstaller binary
- [ ] First-run wizard (`init` command)

## Phase 2 — Distribution
- [ ] Desktop app shell (Tauri or Electron) wrapping CLI
- [ ] Installer (macOS .dmg, Windows .exe)
- [ ] Hosted onboarding docs + Firebase project template
- [ ] License model decision (open source vs commercial)

## Phase 3 — Scale
- [ ] Cloud Functions for embedding on upload (optional — removes local Ollama requirement)
- [ ] Multi-tenant Firestore collections per user/org
- [ ] Hybrid search (BM25 + vector) for better recall
- [ ] Rate limiting + usage metering for SaaS tier

## Stack rationale
| Layer | Choice | Why |
|-------|--------|-----|
| Embeddings | Ollama (local) | Privacy-first default; no API costs |
| Vector DB | Firestore | Matches Gnomad stack; scales to millions of docs; managed indexes |
| CLI | Python + Click | Fast to ship; shared with internal build |
| Future UI | Tauri | Lightweight cross-platform; reuses web UI |
