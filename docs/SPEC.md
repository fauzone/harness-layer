# Harness Layer Specification v0.2 (DRAFT)

## Module 1: Memory on Disk

*Status: DRAFT. This specification is published as part of the repository
so it can be tested and challenged. The key words MUST, MUST NOT, SHOULD
and MAY are to be interpreted as in RFC 2119.*

*Changelog v0.2 (from the first sandbox adoption test, 2026-10-28): added
the read-scope fence (HL-B-4) and per-task token budgets (HL-B-5) after a
test in which the memory protocol scored 20/20 on cold-resume recall but
the agent sessions consumed ~10.4M tokens through out-of-scope
exploration; clarified enforcement tiers in HL-P-2.*

---

## 1. Purpose and scope

This specification defines how an agent harness stores memory on disk so
that it (a) survives context compaction, (b) can be resumed by a fresh
session without losing decisions and edge cases, and (c) stays portable
across harnesses because everything is a plain-text file in Git. v0.1
covers layer structure, formats, protocols, budgets and conformance
requirements.

## 2. The five layers

### L0 — Identity (always loaded)

- **HL-L0-1** An adopter workspace MUST contain: `SOUL.md` (persona),
  `IDENTITY.md` (compact identity: name, role, vibe, markers — template
  in `templates/IDENTITY.md`), `USER.md` (owner profile), and a core
  `AGENTS.md` (authority, hard limits, routing).
- **HL-L0-2** L0 content MUST be limited to what is classified as FIXED:
  identity, authority, hard constraints, escalation contracts.
  Procedures, doctrine and reference material MUST NOT live in L0; they
  belong in on-demand skills.
- **HL-L0-3** Total L0 file size (SOUL + IDENTITY + USER + core AGENTS)
  SHOULD be ≤ 12 KB per agent; exceeding it MUST be recorded as a
  deviation with a reason inside the file itself.

### L1 — Instructions

- **HL-L1-1** Two sub-layers are strictly distinguished: **L1a** = the
  agent's operating instructions at workspace level (`AGENTS.md` in the
  agent workspace); **L1b** = project instructions at project level
  (`AGENTS.md` in the project root; projects using another name map to
  this file).
- **HL-L1-2** Loading hierarchy: global → workspace (L1a) → project
  (L1b) → subdirectory. Conflict rule: the more specific layer wins; a
  material conflict MUST be recorded in the project's DECISIONS.md (L3),
  never silently resolved.
- **HL-L1-3** L1b SHOULD be ≤ 8 KB per project and contain only that
  project's working rules (conventions, prohibitions, gates).

### L2 — Long-term memory

- **HL-L2-1** Every workspace MUST have a curated `MEMORY.md` and a
  `memory/` folder of **Markdown daily notes named `YYYY-MM-DD.md`**.
  A raw session log (e.g. `history.jsonl`) is L4 and MUST NOT be used as
  a substitute for daily notes.
- **HL-L2-2** A daily note is written on the day the work happens
  (template in `templates/daily-note.md`): facts, decisions,
  commitments and outcomes — not a transcript.
- **HL-L2-3** *Promotion* from daily notes into MEMORY.md is allowed only
  for durable facts, preferences, decisions, commitments and verified
  outcomes that change the situation. Routine progress and transient
  technical detail MUST NOT be promoted.
- **HL-L2-4** Every MEMORY.md entry MUST follow `templates/MEMORY-entry.md`:
  dated, carrying provenance (who/source), and a correction MUST replace
  the claim it supersedes — the old claim must not remain active
  alongside the new one.
- **HL-L2-5** MEMORY.md SHOULD be ≤ 32 KB; overflow is handled by moving
  older sections to `memory/archive/` (still in Git), never by deleting.
- **HL-L2-6** Curation happens at the close of every substantial job and
  at every session pause at the latest; an agent MUST NOT defer facts
  that meet HL-L2-3.

### L3 — Working state

- **HL-L3-1** Every active job MUST have one STATE file following
  `templates/STATE.md`, **≤ 15 lines**, in the job's home directory.
  Contents: goal, status, next step, blockers, key file pointers — not
  narrative.
- **HL-L3-2** Every project MUST have a `DECISIONS.md`
  (`templates/DECISIONS-entry.md`): one entry per human or architecture
  decision — date, decision, one-line reason, decider.
- **HL-L3-3** *Write triggers* — STATE/DECISIONS MUST be updated
  **immediately** when: a decision is made, a milestone completes, a
  blocker appears or clears, the plan changes, or the session is about
  to pause or end. Deferring to "end of session" is a protocol
  violation.
- **HL-L3-4** A large multi-step job SHOULD have a `PLAN.md` in the same
  home; STATE points to PLAN instead of duplicating it.

### L4 — Append-only session log

- **HL-L4-1** The harness MUST keep an append-only session log (one
  line/entry per event) containing everything sent to the model: user
  messages, responses, tool calls, tool results, and per-turn token
  usage metadata. Reference format: JSONL.
- **HL-L4-2** The log MUST NOT be edited or deleted by compaction.
  Compaction produces a **summary node** (schema in
  `templates/summary-node.json`) appended to the log, pointing to the
  range it summarises (line or time range, plus a content hash).
- **HL-L4-3** Operations that MUST be supported over the log by the
  harness or its adapter: `resume` (continue a session from the log),
  `search` (find text in the log), `fork` (branch from any point),
  `replay` (re-run a range). In v0.1, `search` MAY be satisfied by plain
  text search over the file; `resume`/`fork`/`replay` are implementation
  requirements for adapters.
- **HL-L4-4** Internal compaction behaviour (what gets trimmed first)
  MUST be documented by each adapter as observed; claims without
  config/log evidence MUST NOT be stated as fact.

## 3. Protocols

### 3.1 Write-before-compact

- **HL-P-1** Before any compaction — automatic or manual — the agent
  MUST flush to disk: new decisions (L3/L2), new facts (L2), task status
  (L3), open edge cases (L3). Anything that exists only in conversation
  is treated as **not saved**.
- **HL-P-2** Enforcement is tiered: (a) the protocol as an instruction in
  a canonical skill auto-loaded by all agents, plus the write triggers
  of HL-L3-3; (b) a mechanical hook or wrapper in harnesses that support
  one; (c) detective control — periodic conformance checks across
  workspaces plus per-task meter review, which catches violations after
  the fact and feeds them back as corrections. Each adapter MUST state
  its tier explicitly and MUST NOT claim a higher tier than it runs.
  (A true pre-compact hook requires harness support; where the harness
  exposes none, tier (a)+(c) is the honest maximum.)

### 3.2 Read-on-resume

- **HL-P-3** A new or resumed session MUST read, before working: the
  workspace L0, the applicable L1, MEMORY.md (or its index), and the
  STATE of the job being continued.
- **HL-P-4** A compaction summary is a **search hint, not a source of
  truth**. When a summary and the disk disagree, **the disk wins**, and
  the material difference is recorded in that day's daily note.

### 3.3 Survival matrix

| Survives compaction (on disk) | Does not survive (conversation only) |
|---|---|
| Decisions recorded in DECISIONS.md / MEMORY.md | Decisions only spoken in chat |
| Facts & preferences promoted to L2 | Facts "discussed" but never written |
| Status & next step in STATE | Status held only in the session's head |
| Edge cases written to STATE / daily note | Verbal edge cases |
| The full raw session in L4 | Nuance, tone, unrecorded reasons for rejection |
| Tool output written to a file | Tool output shown only in the session |

Every newly discovered field loss MUST be added to this matrix as a new
row, together with its protocol fix.

## 4. Budgets

- **HL-B-1** The specification controls the **file component**: L0
  ≤ 12 KB (HL-L0-3), L1b ≤ 8 KB (HL-L1-3), MEMORY.md ≤ 32 KB (HL-L2-5),
  STATE ≤ 15 lines (HL-L3-1).
- **HL-B-2** Every adapter MUST **measure and report its harness floor**
  (fixed tokens per call before files load: system prompt + tool
  schemas), measured from session metadata, never guessed.
- **HL-B-3** L2/L3 MUST be loaded selectively (index/headings first,
  then the sections needed). Loading a large MEMORY.md in full into
  every session violates this clause.
- **HL-B-4 — Read-scope fence.** A task brief defines the read scope:
  the files it names plus what the current step demonstrably needs.
  Reading outside the scope MUST be justifiable in the task's report.
  Exploratory reading of unrelated trees is a protocol violation, not
  initiative. (Added in v0.2 after sandbox measurement: out-of-scope
  exploration, not file size, was the dominant token cost.)
- **HL-B-5 — Per-task token budget.** Organisations SHOULD set a token
  budget per task class, measured by the harness's per-invocation meter
  (see Module 3). Exceeding the budget is recorded as a finding in the
  task report — with the cause — not silently absorbed.

## 5. Self-learning guard

- **HL-G-1** Agent auto-writes to L1/L2 MUST NOT overwrite a human's
  manual edits without showing a diff and obtaining approval.
- **HL-G-2** Every auto-write MUST be recorded in L4 with the tag
  `provenance: agent-written` (and `human-written` for human edits,
  where recorded).
- **HL-G-3** Self-learning systems (the Hermes pattern) MAY write only
  to a staging area; promotion to L1/L2 follows HL-G-1.

## 6. Conformance — `harness-layer check`

The `harness-layer check` tool (in `tools/`) MUST verify, per adopter
workspace:

1. Required L0 files exist (SOUL, IDENTITY, USER, AGENTS) and L2 exists
   (MEMORY.md, `memory/` folder).
2. Size ceilings of HL-B-1.
3. A DECISIONS.md exists per active project and STATE files are
   ≤ 15 lines.
4. A daily note for today exists when there was session activity today.
5. The L4 log is append-only and its latest summary node (if any)
   points to a range that exists.

The check is **read-only**: it reports pass/fail per clause and changes
nothing.

**Evaluation battery (v1 targets):** compaction-survival test with
≥ 20 planted edge cases (target ≥ 95% answerable from disk alone);
cold-resume test (≤ 1 clarification question the files should have
answered); a migration drill between two harnesses using only Layer
files; and cost non-regression (≤ +10% tokens per task vs. baseline).

*Measured status (2026-10-28 pilot, Goose, n=2/cell — see
`EVALUATION-AB.md`): continuity and cold-resume targets met
(20/20 vs 0/20 control); cost non-regression **NOT met** — measured
overhead ≈1.8× (short tasks) to ≈5× (fact-planting). The ≤ +10%
figure remains the Module 3 target, not a current property.*

---

*End of SPEC v0.1 DRAFT.*
