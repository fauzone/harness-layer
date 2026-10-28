# Module 3 — Cost & Context Discipline (SPEC-lite, DRAFT)

*Distilled from Cline (per-task cost visibility), Goose and Pi
(context leanness), Claude Code (recovery behaviour), and the
maintainers' own production metering practice.*

## Problem

The same model can cost 3× more per task in one harness than another
at statistically indistinguishable quality. The drivers are mundane:
fat fixed preambles, whole-file reads, sessions that carry their entire
history into every call, and no meter anywhere a human can see it
while it matters.

## Requirements

- **CC-1 — Per-task metering.** Every invocation MUST be metered:
  input/output tokens, call count, and the measurement method
  (provider-reported vs. estimated), recorded durably per task.
  *Reference implementation: a wrapper that snapshots session-file
  metadata before/after each invocation and reads the provider's
  reported per-turn usage — in production use by the maintainers
  (ATC token meter v3).*
- **CC-2 — Context floor measurement.** The fixed per-call floor
  (system prompt + tool schemas + always-loaded files) MUST be
  measured per harness/agent and reported (HL-B-2). You cannot budget
  what you have not measured.
- **CC-3 — One-shot sessions, state-file continuity.** A subtask SHOULD
  run in a fresh session; continuity travels through L3 state files
  (Module 1), not through an ever-growing conversation. Measured
  motivation: a carried session in the maintainers' fleet reached
  ~20.8M tokens / 201 calls for work that a state-file workflow does
  in a fraction of that.
- **CC-4 — Scripted mechanical steps.** Recurring mechanical work
  (checks, transforms, data pulls) MUST be captured as saved scripts
  with compact output, not re-improvised as model turns.
- **CC-5 — Targeted reading.** Reads MUST be section-targeted where
  the brief can name the section (HL-B-3, HL-B-4). Whole-file reads of
  large documents require justification.
- **CC-6 — Continuation on truncation.** When a model's step is cut
  off mid-output, the harness SHOULD prompt it to continue rather than
  silently ending the step. (Honest note: in the Shandong harness
  study, transplanting this prompt alone showed no measurable score
  gain; its value is reducing silent work loss, not raising scores.)
- **CC-7 — Compaction trims tool output first.** Where the harness
  controls compaction order, bulky tool results SHOULD be trimmed
  before conversational history is summarised. Adapters MUST document
  observed behaviour (HL-L4-4) instead of claiming this by default.
- **CC-8 — Budgets with findings.** Per-task-class budgets (HL-B-5)
  SHOULD exist; an overrun produces a recorded finding with cause.

## Conformance

Tokens per completed task, per task class, trended over time; context
floor per agent; percentage of invocations with provider-reported
metering. A harness that cannot produce CC-1 numbers is not conformant
with this module regardless of its other merits.
