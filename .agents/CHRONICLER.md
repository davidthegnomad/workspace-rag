# CHRONICLER — Project Memory & Session Continuity

> **What**: The living memory of this project. Ensures no context is lost between sessions, agents, or conversations.
> **Who**: Not a separate model — the **acting agent** executes Chronicler duties when triggers fire.
> **Why**: AI agents lose context between sessions. The Chronicler system makes projects resumable by any agent at any time.

---

## Triggers — When to Update

Execute these **immediately in the same turn** (before moving on), unless the user says "skip chronicler."

| Trigger | User Says | Action |
|---------|-----------|--------|
| **A — Checkpoint** | "save session", "checkpoint", "sync state" | Rewrite `SESSION_STATE.md`. Append checkpoint to today's `HANDOFF_YYYY-MM-DD.md`. |
| **B — End of Day** | "done for the day", "wrap up", "end session" | Everything in A, plus fuller handoff: topics covered, what worked/failed, files changed, next session priorities. |
| **C — Git Push** | *(automatic after successful push)* | Update `SESSION_STATE.md` last git section (branch, SHA, remote). Append push record to today's handoff. |
| **D — Major Decision** | Agent makes architectural choice | Append entry to `DECISIONS/ADR_YYYY-MM-DD.md` with context, options considered, and rationale. |
| **E — Skill Learned** | Agent discovers better pattern | Append to `SKILLS/LEARNING_LOG.md` and update relevant skill file. See Self-Evolution Protocol. |

Match **intent**, not exact wording.

---

## File Structure

```
.agents/
├── CHRONICLER.md              # This file
├── LOGS/
│   ├── SESSION_STATE.md       # Hot state — read FIRST at session start
│   └── SESSIONS/
│       └── HANDOFF_YYYY-MM-DD.md  # Daily archive
├── DECISIONS/
│   └── ADR_YYYY-MM-DD.md     # Architecture Decision Records
└── SKILLS/
    ├── LEARNING_LOG.md        # Chronological record of discoveries
    └── (evolving skill files)
```

---

## SESSION_STATE.md Format

```markdown
# Session State
> Last updated: [timestamp]

## Current Focus
[What we're working on right now]

## Recent Changes
- [Bullet list of files added/modified/removed]

## Open TODOs
- [ ] [Active tasks]

## Last Git
- Branch: [branch]
- SHA: [short sha]
- Remote: [remote/branch]

## Blockers / Notes
[Anything the next agent needs to know]
```

---

## At Session Start (Every Agent, Every Time)

1. Read `.agents/LOGS/SESSION_STATE.md` top to bottom
2. If stale or missing, read the latest `.agents/LOGS/SESSIONS/HANDOFF_*.md`
3. Run `git log -3 --oneline` to verify state matches reality
4. If anything is out of sync, update SESSION_STATE before proceeding

---

## Architecture Decision Records (ADR)

When an agent makes a significant architectural choice (new dependency, structural change, deployment strategy shift), log it:

```markdown
## [Decision Title] — [Date]

**Context**: [Why this decision came up]
**Options Considered**:
1. [Option A] — [pros/cons]
2. [Option B] — [pros/cons]
**Decision**: [What was chosen and why]
**Consequences**: [What this means going forward]
```

---

## Principles

- **Accuracy over volume** — A wrong log is worse than a long log. Fix errors in addenda.
- **Zero-litter** — No ad-hoc notes.md in project root. Use `.agents/LOGS/`.
- **The "Why" over the "What"** — Always record context behind decisions, not just what changed.
- **Write for AI** — These logs are consumed by agents as much as humans. Be precise with paths and states.
- **Self-Enhancement** — If you discover a better logging pattern, update this CHRONICLER.md file directly.
