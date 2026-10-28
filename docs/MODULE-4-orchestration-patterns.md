# Module 4 — Orchestration Patterns (SPEC-lite, DRAFT)

*Distilled from Goose (recipes, MCP-first extensions), Cline
(Plan/Act), OpenCode (plan mode), DeepSeek Harness (the loop as an
interceptable protocol), and multi-agent production practice.*

## Problem

Single-agent, single-session work does not scale to organisations of
agents. Ad-hoc delegation loses track of who owes what, merges
unreviewed work, and lets agents make decisions that belong to humans.

## Requirements

- **OR-1 — Recipes / playbooks.** Recurring multi-step work SHOULD be
  captured as declarative, reusable playbooks (the Goose recipes
  pattern) instead of re-briefed from scratch each time.
- **OR-2 — Plan/Act separation.** For work that changes files or
  external state, a plan SHOULD be produced and approved before
  execution (the Cline pattern); execution then follows the plan, and
  deviations are reported, not improvised silently.
- **OR-3 — Loop event hooks.** Harnesses SHOULD expose interception
  points around steps and tool calls so logging, policy and
  guardrails attach to the loop without forking it (the DSH
  loop-as-plugin insight). Where no hooks exist, a wrapper around
  invocations is an acceptable substitute and MUST be labelled as such.
- **OR-4 — Isolated delegation with a QA gate.** Delegated workers run
  in their own workspaces/sessions. Their output is *input* to a
  reviewer, never a direct merge: nothing merges without independent
  review, and reviewers re-run the decisive checks themselves.
- **OR-5 — Human decision gates.** Sensitive classes — pricing,
  refunds, publishing, production deploys, payments, data migration —
  are decided by a human. Agents prepare; they do not execute these.
  Gates are part of the specification, not local custom.
- **OR-6 — Tracked tasks.** Delegated work MUST be tracked as tasks
  with an owner, a state, and a completion condition, so silent deaths
  are detectable (a task that stops reporting is flagged, not
  forgotten). Redispatch of a dead task MUST reuse its task identity
  so the record closes correctly.
- **OR-7 — One subtask per dispatch; two-failure stop.** A dispatch
  carries one subtask. A worker that fails the same problem twice with
  the same hypothesis MUST stop, commit its state, and report the
  failure verbatim (compare Module 2, SC-4).

## Conformance

Percentage of delegated tasks with a recorded review before merge;
percentage of sensitive actions executed without a human gate (target:
zero); percentage of dead tasks detected by tracking rather than by a
human asking.
