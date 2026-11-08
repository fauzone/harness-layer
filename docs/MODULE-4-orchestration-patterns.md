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
- **OR-8 — Structured dispatch briefs.** A dispatch brief MUST open
  with locked field headers (sender, recipient, kind, task, plus the
  fields the task class needs) and MUST contain an explicit
  return-report instruction. Body prose is free; the header is not. A
  brief without the header is not dispatchable. *(Field report,
  maintainers' fleet, 2026-11: free-form briefs repeatedly lost the
  report-back requirement entirely; locking the header made the loss
  mechanically detectable.)*
- **OR-9 — Controlled-vocabulary completion status, mechanically
  enforced.** Every worker report MUST close with a status token from
  a controlled vocabulary (e.g. DONE / BLOCKED / FAILED; audit
  verdicts PASS / PASS WITH NOTES / FAIL). The dispatch wrapper's
  completion gate SHOULD reject a "done" that carries no valid status
  and record the violation. A status vocabulary that is only a
  convention decays; enforced at the gate, it becomes a protocol.
- **OR-10 — Structured completion reports.** Worker reports SHOULD
  follow a fixed shape — deliverables, check results, measured cost
  (Module 3, CC-1), remaining work — so the reviewer's synthesis is a
  summary, not an excavation (extends Module 2, SC-5 to delegated
  work).
- **OR-11 — Traceability labels.** Every work item in a brief and
  every deliverable in a report MUST carry its source label
  (requirement id, plan section, or workstream id). Unlabelled
  deliverables do not count toward completion or convergence
  (OR-13); they are out of scope until the orchestrator says
  otherwise.
- **OR-12 — Constitution check at plan open.** Every plan, plan
  amendment, or large brief MUST open with a short block naming the
  standing rules that bind it (drawn from the project's context
  capsule, Module 3 CC-9) and listing explicit deviations, if any. No
  block, no dispatch. Standing sections are referenced, never
  rewritten per phase.
- **OR-13 — Convergence pass before closure.** A phase or milestone
  MUST NOT be recorded complete until a convergence pass reconciles
  the plan against what actually shipped: every drift is resolved in
  writing in one direction or the other (fix the work, or amend the
  plan), and the verdict (Converged / Not converged: <drift>) is
  recorded in the state file. Progress percentages move only after
  convergence, never before.
- **OR-14 — Scope freeze for parallel work.** Briefs for parallel or
  pipelined dispatches MUST declare frozen areas (files, schemas,
  surfaces) that the dispatch may not touch. Only the orchestrator
  installs or removes a freeze, and removals are recorded in the
  state file. Work that edits a frozen area is invalid until the
  orchestrator inspects it.
- **OR-15 — Waiting requires a real trigger.** An orchestrator MUST
  NOT report work as "waiting for X" (a free worker seat, an external
  event, a state change) unless a mechanism that actually fires on X —
  a watcher, hook, or scheduled check — is installed in the same
  step. A blocked flag in a task list is not a trigger; passive
  waiting is indistinguishable from forgetting. *(Field report,
  maintainers' fleet, 2026-11: a build reported as "waiting for a
  free seat" sat idle through two seat openings because nothing was
  watching the seat ledger.)*
- **OR-16 — Venue failure is branch-scoped.** Where a venue (a
  machine, a host, an account) is reachable through independent
  branches, failure of one branch MUST NOT be reported as the venue
  being unavailable; the remaining branches are probed first.
  Environment frames ("venue X is down", "window closed at T") expire
  when the underlying facts change and MUST be re-derived, not
  inherited, at each planning step (compare Module 2, SC-6).

- **OR-17 — Completion-independent death detection.** Task tracking
  MUST NOT depend on the worker's voluntary end record alone. A
  session that has started and then produces neither an end record
  nor a progress heartbeat within a stated threshold MUST be
  surfaced automatically as a suspected silent death — carrying its
  identifier and last-seen timestamp — and re-surfaced on a stated
  interval until an end record or a fresh heartbeat clears it. A
  heartbeat is any progress pulse the runner or its adapter emits;
  where none exists, the start timestamp is the last-seen time.
  *(Field report, maintainers' fleet, 2026-11: a dispatched build
  died about ten minutes in with no error and no end record; the
  end-keyed tracker never fired and the death was found only when a
  human asked, more than two hours later.)*
- **OR-18 — Open interchange contracts; control-plane separation.**
  Cross-harness continuity SHOULD rest on published, file-based
  contracts rather than one vendor's runtime: an append-only ledger
  of start / heartbeat / end records carrying trace identifiers, a
  Markdown state file per workstream, a next-brief file that must
  exist before a chain can advance, and a launcher contract (any CLI
  that takes a prompt file and a working directory and writes the
  ledger). A shared monitor or registry — the control plane — MAY
  detect and emit events but MUST NOT dispatch, merge, or kill
  work; policy stays in the consuming harness. The monitor being
  down MUST NOT stop the work, only its visibility: the state lives
  in files the workers already write.
- **OR-19 — Portable configuration.** Shared tooling MUST NOT embed
  machine-absolute paths in code defaults. Locations are resolved
  configuration-first: explicit option, then environment, then a
  workspace-relative default — so identical code runs on any host
  or harness, and a deployment states its locations as configuration
  rather than as a code change. *(Field report, maintainers' fleet,
  2026-11: removing a hard-coded home path from a production watcher
  was completed by stating the deployment's ledger location as
  environment configuration in its service definition; behaviour
  verified identical after restart.)*
- **OR-20 — Graded adapters; conformance as proof.** Portability
  claims SHOULD be structured as graded adapter levels — level 0: a
  generic shell wrapper that records start and end around any
  command; level 1: a ledger adapter emitting contract records;
  level 2: continuity handlers reacting to detection events;
  level 3: a full harness pack (skills, handlers, configuration)
  adopting the whole orchestration discipline — and proven by a
  conformance suite that exercises the contracts themselves,
  including the same chain run through two different harnesses,
  rather than asserted in prose.

## Conformance

Percentage of delegated tasks with a recorded review before merge;
percentage of sensitive actions executed without a human gate (target:
zero); percentage of dead tasks detected by tracking rather than by a
human asking; percentage of dispatches carrying the OR-8 header and a
valid OR-9 closing status; percentage of phase closures with a
recorded OR-13 convergence verdict; percentage of silently dead
sessions detected automatically within the stated OR-17 threshold,
and median silent-death detection latency against the pre-adoption
baseline; number of machine-absolute paths in shared tooling defaults
(target: zero, OR-19).
