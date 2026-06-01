# Self-Evolution Protocol — Agent Autonomy Framework

> Every agent in the Gnomad swarm is expected to **learn, adapt, and improve** without explicit instruction. This protocol defines how.

---

## Core Principle

Agents are not static config files. They are **living systems** that evolve through use. Every session should leave the project's agent infrastructure slightly better than it was found.

---

## What Agents Can Update Autonomously

| File | When | How |
|------|------|-----|
| `AGENTS.md` | Agent discovers its responsibilities are incomplete or stale | Append new responsibilities, update stack info, correct errors |
| `.agents/SKILLS/*.md` | Agent learns a new pattern, technique, or integration | Create new skill file or update existing one |
| `.agents/SKILLS/LEARNING_LOG.md` | Any significant discovery | Append timestamped entry |
| `.agents/CHRONICLER.md` | Better logging pattern discovered | Update triggers or file format |
| `.agents/PROJECT_SOP.md` | Build/deploy/test process changes | Update the relevant section |
| `.agents/DECISIONS/*.md` | Architectural decision made | Create new ADR entry |
| `.agents/LOGS/SESSION_STATE.md` | Every trigger event | Rewrite per Chronicler protocol |

## What Agents Must NOT Update Without User Approval

- Deleting files or directories
- Changing deployment targets or hosting config
- Modifying `.env` or secrets
- Pushing to remote repositories
- Changes that affect other projects

---

## Skill File Standard

When an agent learns something worth preserving, create or update a skill file:

```markdown
# [Skill Name]

> Learned: [date] | Agent: [who discovered it] | Project: [where]

## Context
[Why this skill was needed]

## The Pattern
[Code, config, or process that works]

## When to Use
[Conditions that make this skill relevant]

## Gotchas
[Things that can go wrong]

## Related
- [Links to other skills or external docs]
```

Save to `.agents/SKILLS/[DESCRIPTIVE_NAME].md`

---

## Learning Log Format

`.agents/SKILLS/LEARNING_LOG.md`:

```markdown
# Learning Log

## [YYYY-MM-DD] [Brief Title]
**Agent**: [Who]
**Discovery**: [What was learned]
**Applied**: [How it was used]
**Skill File**: [Path if a skill was created/updated, or "N/A"]
```

---

## Evolution Triggers

Agents should self-evolve when they encounter:

1. **Repeated friction** — Same problem solved twice = create a skill file
2. **Better pattern** — Found a cleaner approach than what's documented = update the skill
3. **New integration** — Connected a new tool/API = document the integration
4. **Process improvement** — Found a faster way to build/test/deploy = update PROJECT_SOP
5. **Knowledge gap** — Searched for something that should have been documented = create it
6. **Post-incident** — Something broke and was fixed = document the fix and prevention

---

## Cross-Project Learning

When a skill discovered in one project could benefit others:

1. Create the skill locally in `.agents/SKILLS/`
2. If it's broadly applicable, promote it to `02_ai_engineering/gnomad-swarm-core/.agents/SKILLS/`
3. Reference the swarm-core skill from the local project: `> See also: gnomad-swarm-core/.agents/SKILLS/[NAME].md`

---

## Autonomy Levels

| Level | Description | Authorization |
|-------|-------------|---------------|
| **Green** | Update logs, session state, learning log | Always autonomous |
| **Yellow** | Update skills, SOP, AGENTS.md | Autonomous, log the change |
| **Orange** | Create new files in .agents/ | Autonomous, notify user |
| **Red** | Changes outside .agents/ that affect behavior | Require user approval |
