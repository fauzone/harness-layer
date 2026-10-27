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
- **Phase 2 — Reference implementation (nanobot).** Write-before-compact
  hook, hierarchical L1 injection, L4 session log, `harness-layer check`
  CLI. Independent QA gate: nothing merges without review. *(±12–18 h)*
- **Phase 3 — Evaluation & calibration.** Run the acceptance battery
  (below) before vs. after; publish results as measured, including
  failures. A failed battery returns the work to Phase 1 — it is not
  declared done. *(±6–10 h)*
- **Phase 4 — Second adapter + migration drill.** One more adapter (Goose
  or Hermes), then the portability drill: a real job moved between two
  harnesses using only Layer files. *(±8–12 h)*

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
  suites actually guard fixes.
- **Module 3 — Cost & Context Discipline:** per-task cost metering,
  context-floor budgets, continuation on truncated output, compaction that
  trims tool output before summarising, one-shot session workflow.
- **Module 4 — Orchestration Patterns:** recipes, Plan/Act separation,
  loop event hooks, sub-agent isolation, QA gate, human decision gates.

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
