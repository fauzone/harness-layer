# Harness Layer — Roadmap

*Living document. Estimates are in active agent-work hours and are
recalibrated from the actuals of the first completed phase.*

## Module 1 — Memory on Disk (v1)

- **Phase 0 — Inventory & gap audit.** Map existing practice (context
  continuity skills, curated-memory systems, state files, per-worker token
  metering) against the draft specification. Output: `GAP.md`, exact deltas
  only, no building yet. *(±4–6 h)*
- **Phase 1 — Specification v0.1.** `SPEC.md`: the five-layer architecture
  (L0 identity, L1 project instructions, L2 curated long-term memory, L3
  working state, L4 append-only session log) written as testable rules, plus
  file templates per layer. Human review gate before any build. *(±6–8 h)*
- **Phase 2 — Build the repository as a standalone product.** The
  public specification (`docs/SPEC.md`), per-layer templates
  (`templates/`), the `harness-layer check` CLI (`tools/`), a conformant
  example workspace (`examples/`) and its test suite. **No adoption into
  any harness happens in this phase.** Independent QA gate: nothing
  merges without review. *(±12–18 h)*
- **Phase 3 — Test the repository.** Internal tests first (the check CLI
  must pass the conformant example and fail a deliberately broken
  fixture), then the check is run read-only against real workspaces as
  test subjects for a conformance baseline, and the evaluation battery
  (below) is run as far as it can go without adoption. Results are
  published as measured, including failures. A failed battery returns
  the work to Phase 1/2 — it is not declared done. *(±6–10 h)*
- **Phase 4 — First adoption, second adapter, migration drill.** Only
  after Phase 3 passes: the Layer is adopted into a first harness
  (write-before-compact hook, hierarchical L1 injection, L4 operations),
  then a second adapter (Goose or Hermes), then the portability drill:
  a real job moved between two harnesses using only Layer files.
  *(±8–12 h)*

**Total v1 (Phases 0–4): ±36–54 active agent hours.**

### v1 acceptance criteria (measurable)

1. **Compaction survival:** ≥ 20 planted edge cases, forced compaction,
   ≥ 95% answerable from disk alone (pre-implementation baseline measured
   first).
2. **Cold resume:** a fresh session continues a multi-step job from STATE +
   plan files with ≤ 1 clarification question the files should have answered.
3. **Portability:** the Phase-4 migration drill completes without moving
   any proprietary data of the source harness.
4. **Size discipline:** always-loaded layers (L0 + L1) pass the token
   ceiling set in the specification; `harness-layer check` is green.
5. **No cost regression:** tokens per task on the battery rise ≤ 10%
   versus baseline — better memory must not be bought with silently
   fatter context.

## Later modules

- **Module 2 — Self-Check Loop:** test-iteration loop with explicit
  completion criteria; mutation check (bug re-insertion) to prove test
  suites actually guard fixes. *SPEC-lite published:
  [MODULE-2-self-check-loop.md](MODULE-2-self-check-loop.md).*
- **Module 3 — Cost & Context Discipline:** per-task cost metering,
  context-floor budgets, continuation on truncated output, compaction that
  trims tool output before summarising, one-shot session workflow.
  *SPEC-lite published:
  [MODULE-3-cost-context-discipline.md](MODULE-3-cost-context-discipline.md).*
- **Module 4 — Orchestration Patterns:** recipes, Plan/Act separation,
  loop event hooks, sub-agent isolation, QA gate, human decision gates.
  *SPEC-lite published:
  [MODULE-4-orchestration-patterns.md](MODULE-4-orchestration-patterns.md).*

Adapter guides: a generic, agent-executable adaptation procedure
([ADAPTER-GUIDE.md](ADAPTER-GUIDE.md)) — an agent on any harness
inventories its own harness, builds the layer mapping, instantiates
the files and self-tests, following the procedure end to end.
Worked examples: [ADAPTER-nanobot.md](ADAPTER-nanobot.md) (tested,
measured) and [ADAPTER-goose.md](ADAPTER-goose.md) (adoption tested
2026-10-28 by a Goose agent following the guide from the README alone;
Step 7 self-test deferred). Sequencing
note (maintainers, 2026-10-28): completing the modules and guides so
others can use them comes before deepening the implementation inside
the maintainers' own systems; per-module adoption into those systems
follows once each module is complete.

## Risks tracked openly

- **Over-engineering** (the failure mode of maximal-pluggability designs):
  v1 is exactly one module; every rule must have a test in the battery.
- **Duplication of existing practice:** Phase 0 maps first; Harness Layer
  consolidates and standardises — it does not silently replace what works.
- **Agent-written memory noise:** the self-learning guard (diff + approval
  before overwriting human edits; provenance tags) is part of the spec.
- **Unproven portability claims:** portability may be claimed only after
  the Phase-4 drill passes; before that the status is "designed to be
  portable".
