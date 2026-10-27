# Harness Layer

**An open, harness-agnostic layer of best practices for AI agents — distilled from the best agent harnesses, specified as plain files, adoptable by any harness.**

> *Agent = Model + Harness.* The same model produces measurably different work in
> different harnesses: controlled studies that hold the model fixed find cost
> differences of up to 3× per task between harnesses, different failure modes,
> and different reliability — even when benchmark scores barely move. The
> harness is where most of that difference lives. Harness Layer collects the
> patterns that cause it, writes them down as an open specification, and makes
> them portable.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Status: Developer Preview](https://img.shields.io/badge/status-developer%20preview-orange)

---

## What this is

Harness Layer is **not another harness**. It is a layer *above* harnesses:

- A **specification** (conventions, protocols, schemas) written in open formats —
  Markdown with frontmatter, kept in Git — that any agent harness can implement.
- A **pattern library**: each pattern names the harness it was distilled from,
  the problem it solves, the evidence behind it, and how to adopt it.
- A **conformance test battery** so "we adopted it" is a measured claim,
  not a documentation claim.
- **Adapter guides** that map the same specification onto different harnesses.

Design rule zero: **an ecosystem must never depend on a single harness.** If a
harness disappears tomorrow, everything that matters — identity, memory,
skills, decisions, state — must already live in open files that the next
harness can pick up unchanged.

## Status

**Developer preview — specification v0.1 in development.** Module 1
(Memory on Disk) is being specified first; later modules are specified as
roadmap in [docs/ROADMAP.md](docs/ROADMAP.md). Features below are labelled:

- `SPEC` — defined in the v0.1 specification draft
- `GUIDE` — adapter guide in progress
- `ROADMAP` — designed, scheduled in a later module

Nothing in this repository claims production readiness yet. Evaluation
results will be published as they are measured, including negative ones.

## Features

### Module 1 — Memory on Disk `SPEC`

*Distilled primarily from Claude Code's disk-based memory (project instruction
files, plans and auto-memory that survive context compaction), hardened by
failure cases observed in other harnesses.*

**Five-layer memory architecture**

- **L0 — Identity layer.** Always-loaded, deliberately slim: persona, user
  profile, core instructions, hard limits and routing rules. Token-budgeted;
  content is classified as *fixed* (identity, authority, hard constraints) —
  everything else must live in a lower layer.
- **L1 — Project instruction layer.** One instruction file per project or
  repository (convention: `AGENTS.md`; harnesses that use another name map to
  the same file). Hierarchical merge — global → project → subdirectory — with
  explicit conflict rules: the more specific layer wins, and conflicts are
  recorded, never silently resolved.
- **L2 — Curated long-term memory.** A curated `MEMORY.md` of durable facts,
  preferences, decisions and commitments, backed by append-only daily logs
  (`memory/YYYY-MM-DD.md`). Promotion rules decide what may move from a daily
  log into curated memory; every curated entry carries a date and provenance;
  a correction *replaces* the claim it supersedes instead of piling up.
- **L3 — Working state.** A concise state file (≤ 15 lines) per active job,
  a plan file per large task, and a per-project decision log. State is written
  *as the work happens*, not at the end of a session — it is what makes
  disposable, one-shot sessions safe.
- **L4 — Append-only session log.** Everything that enters a model request
  must be reconstructible from the session log ("model-visible means logged",
  borrowed from DeepSeek Harness). The log supports resume, fork, search and
  replay. Compaction never deletes it: compaction produces a *summary node*
  that points back to the log range it summarises.

**Protocols**

- **Write-before-compact.** Before any compaction, automatic or manual, the
  agent must flush decisions, new facts, task status and open edge cases to
  disk. Anything that exists only in conversation is treated as *not saved*.
- **Read-on-resume.** A new or resumed session reads L0–L3 from disk before
  working. A compaction summary is a search hint, never a source of truth —
  **files beat summaries, always.**
- **Survival matrix.** An explicit table of what survives compaction (anything
  on disk) and what does not (conversational nuance, unrecorded reasons, tool
  output that was never written down). Every field loss becomes a new matrix
  entry and a protocol fix.
- **Per-layer token budgets.** Always-loaded layers (L0 + L1) have a measured
  size ceiling per harness; L2/L3 are loaded selectively (index first, then
  the sections needed), so better memory does not silently mean fatter context.
- **Self-learning guard.** Agent-written memory and skill updates (the pattern
  popularised by Hermes) must never overwrite a human's manual edits without a
  diff and approval. All agent-written entries are logged in L4 and tagged
  `agent-written` with provenance.
- **Git-native storage.** Every layer is a plain-text file in Git — diffable,
  reviewable, portable, and free of any vendor's proprietary store.
- **`harness-layer check` CLI.** Verifies an adopter workspace: required
  files exist, always-loaded layers are within budget, structure conforms.

### Module 2 — Self-Check Loop `ROADMAP`

*From Claude Code, whose most-praised user-visible trait is loop persistence.*

- Iterate **investigate → edit → run tests → fix from failures** until the
  completion criteria pass, instead of declaring a plausible partial result done.
- **Mutation check (bug re-insertion):** to prove a test suite actually guards
  a fix, re-introduce the original bug and confirm the tests catch it.
- Explicit completion criteria per task, checked mechanically where possible.

### Module 3 — Cost & Context Discipline `ROADMAP`

*From Cline (per-task cost visibility), Goose and Pi (context leanness),
Claude Code (recovery behaviour), measured across harnesses by independent studies.*

- **Per-task cost metering:** tokens and cost displayed per task and per
  invocation — the user sees the meter while it runs, not on a monthly invoice.
- **Context-floor discipline:** the fixed preamble (system prompt + tool
  schemas) is measured and budgeted; in one controlled comparison it ranged
  from 829 to 16,581 tokens across harnesses and set the bill.
- **Continuation on truncated output:** when a model's reasoning is cut off
  mid-step, the harness prompts it to continue instead of silently ending
  the step with nothing written.
- **Compaction that trims tool output first** before summarising history.
- **Token-saving workflow:** one-shot sessions per subtask with continuity via
  L3 state files, scripted mechanical steps instead of model turns, and
  targeted (section-level) file reading instead of whole-file loading.

### Module 4 — Orchestration Patterns `ROADMAP`

*From Goose (recipes, MCP-first extensions), Cline (Plan/Act), OpenCode
(plan mode), DeepSeek Harness (the loop as an interceptable protocol),
and multi-agent production practice.*

- **Recipes:** reusable, declarative task playbooks (YAML) instead of
  re-prompting from scratch.
- **Plan/Act separation:** a plan is produced and approved before file-changing
  execution begins; per-step approvals for sensitive operations.
- **Event hooks:** pre/post interception points around steps and tool calls,
  so policy, logging and guardrails attach to the loop without forking it.
- **Sub-agent isolation and a QA gate:** delegated workers run isolated; a
  reviewer must approve work before it merges; a human decides sensitive
  matters (pricing, publishing, payments, production changes).
- **Human decision gates** are part of the specification, not an afterthought.

### Cross-cutting

- **Harness-agnostic adapters** `GUIDE` — the same specification mapped onto
  different harnesses (initial targets: nanobot as reference implementation,
  plus Goose, Hermes, and Claude Code as comparison baseline).
- **Migration drill** — a defined exercise that moves a real job between two
  harnesses using *only* the Layer's files (L0–L4). Portability is claimed
  only after a drill passes.
- **Evaluation battery** (targets for v1, measured and published):
  - *Compaction survival:* ≥ 20 edge cases planted in conversation, context
    compacted by force — target ≥ 95% answerable from disk alone.
  - *Cold resume:* a fresh session continues a multi-step job from state +
    plan files with ≤ 1 clarification question that the files should have answered.
  - *Portability:* the migration drill completes with zero proprietary data
    moved from the source harness.
  - *Size discipline:* always-loaded layers within the specified token ceiling.
  - *Cost non-regression:* tokens per task on the battery rise ≤ 10% versus
    the pre-adoption baseline.

## Design principles

1. **Files are the truth; summaries are not evidence.**
2. **Always-loaded context stays slim; procedures live on-demand** as skills
   loaded only when a task needs them.
3. **Shared rules are installed generically at the layer level** — never
   copy-pasted into each agent one by one.
4. **Every pattern cites its source harness and its evidence.** Vendor claims
   are labelled as vendor claims.
5. **Adoption is a measurement, not a document.** A pattern counts as adopted
   only when its conformance test passes.

## Adopting Harness Layer (preview)

1. Create the five-layer file structure in your agent workspace (templates ship
   with the specification).
2. Move identity, project instructions and curated memory into L0–L2 as plain
   Markdown in Git.
3. Start every job with an L3 state file; make your agent update it as it works.
4. Turn on the write-before-compact and read-on-resume protocols in your
   harness's instructions.
5. Run `harness-layer check`, then the compaction-survival test, and publish
   your numbers.

## Repository layout

```
.
├── README.md          — this file
├── LICENSE            — MIT
├── docs/
│   ├── SPEC.md        — Module 1 specification v0.1 (draft)
│   └── ROADMAP.md     — module roadmap, phases and acceptance criteria
├── templates/         — file templates for every layer (L0–L4)
├── tools/             — the `harness-layer check` CLI
└── examples/          — a minimal conformant workspace + a broken fixture
```

The repository is built and tested as a standalone product first
(Phases 2–3 of the roadmap); adoption into a specific harness comes
after the tests pass (Phase 4).

## Why open source?

The patterns in this layer were learned from harnesses across the whole
spectrum — closed and open, provider-native and community-built. Keeping the
*layer* closed would repeat the lock-in problem it exists to solve. The
specification is MIT-licensed so any harness — including commercial ones —
can adopt it, and so the evaluation battery can be reproduced and challenged
by anyone.

## Contributing

Contributions are welcome: new patterns (with source harness + evidence),
adapter guides for additional harnesses, conformance-test cases, and —
especially — published evaluation results, including ones where a pattern
fails. Please open an issue describing the pattern and its evidence before
sending a large pull request.

## License

MIT — see [LICENSE](LICENSE).

---

*Ringkasan (Bahasa Indonesia): Harness Layer adalah lapisan best-practice
terbuka di atas harness AI mana pun — pola-pola terbaik dari Claude Code, Pi,
Goose, DeepSeek Harness, Hermes, Cline, dan lainnya, ditulis sebagai
spesifikasi file terbuka (Markdown + Git) agar bisa diadopsi harness lain
tanpa lock-in. Fokus v1: Memory on Disk — memori lima lapis yang selamat dari
compaction, dengan protokol write-before-compact dan read-on-resume.*
