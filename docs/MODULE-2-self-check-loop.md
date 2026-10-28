# Module 2 — Self-Check Loop (SPEC-lite, DRAFT)

*Distilled primarily from Claude Code, whose most-praised user-visible
trait is loop persistence: it keeps working a problem — running its own
tests, reading failures, fixing — instead of declaring a plausible
partial result done.*

## Problem

Agents stop early. The most common failure shape across harnesses is
not a wrong answer; it is a *plausible partial result presented as
finished*: a refactor that covers most files, code that was never run,
a fix whose test suite would not catch a regression.

## Requirements

- **SC-1 — Explicit completion criteria.** Every build/fix task MUST
  carry checkable completion criteria (commands that must exit 0,
  behaviours that must be observable) before execution starts.
- **SC-2 — The loop.** The agent MUST iterate
  *investigate → change → run the checks → read failures → fix* until
  the criteria pass or a stop condition (SC-4) triggers. Ending a turn
  while a check the agent itself ran is still red is a violation.
- **SC-3 — Mutation check.** For a bug fix guarded by tests, the agent
  SHOULD prove the guard works: re-introduce the original bug (or an
  equivalent mutation) and confirm the test suite goes red, then
  restore the fix. A suite that stays green under the mutation does
  not guard anything.
- **SC-4 — Stop conditions.** The loop MUST stop and report when: the
  same failure survives two fix attempts with the same hypothesis
  (change hypothesis or escalate — no third attempt on the same idea);
  or a pre-set iteration/token budget (HL-B-5) is reached. The report
  states what was tried, verbatim errors, and what is still failing.
- **SC-5 — Evidence in the report.** A completion report MUST include
  the actual check commands run and their outcomes. "Tests pass"
  without the commands and outputs is a claim, not evidence.

## Conformance

Measured per task class: percentage of tasks whose first delivery
passes independent re-run of the stated checks; mutation-check
coverage on bug-fix tasks. Targets are set by the adopter; the module
requires that they be *measured*, not what they must be.

## Non-goals

This module does not prescribe a test framework, a CI system, or how
checks are written — only that the loop closes on evidence.
