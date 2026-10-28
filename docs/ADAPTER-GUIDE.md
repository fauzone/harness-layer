# Adapter Guide — Adapting Harness Layer to a New Harness

*This document is written for an AI agent. If you are an agent running
on some harness and you have been pointed at this repository — by your
user, your developer, or your own reading of the README — this guide is
your procedure for making Harness Layer work on **your** harness. It
assumes nothing about which harness you run on. Follow the steps in
order; each step produces an artifact the next step needs.*

*Worked example: [ADAPTER-nanobot.md](ADAPTER-nanobot.md) is a completed
run of this exact procedure on a real harness, with measured results.
A draft mapping for Goose is in [ADAPTER-goose.md](ADAPTER-goose.md).*

## Definition of done

You are done when all six exist:

1. A completed **harness inventory** (Step 1) with every answer sourced
   or labelled `UNVERIFIED`.
2. A **mapping table** (Step 2) covering L0–L4 and both protocols.
3. The Layer's **files instantiated** in your workspace and wired so
   your harness actually loads them (Step 3).
4. A **`harness-layer check` run** with its summary recorded (Step 5).
5. A **self-test result** (Step 7): planted facts recovered from disk
   by a fresh session, score reported as measured.
6. An **`ADAPTER-<your-harness>.md`** document (Step 8, template at the
   end of this guide) that another agent could follow to reproduce
   your adaptation.

## Ground rules (apply at every step)

- **Files beat summaries.** If this guide, the SPEC, or your harness's
  documentation disagrees with what you observe on disk or in source,
  trust the observation and record the discrepancy.
- **Never guess a mechanism.** If you cannot verify how your harness
  behaves (e.g. whether a file is auto-loaded, what compaction does),
  write `UNVERIFIED` next to that item and adapt conservatively.
  *Cautionary case: on nanobot, `IDENTITY.md` looks like a standard
  bootstrap file and the Layer requires it — but nanobot's bootstrap
  list does not include it, so for a long time the file existed and
  was silently never loaded. Existence is not loading. Verify loading.*
- **Claim only the enforcement tier you actually run** (HL-P-2):
  **(a) instruction** — the behaviour is written in instructions the
  agent is told to follow; **(b) mechanical** — a hook, wrapper or
  harness feature enforces it whether the agent remembers or not;
  **(c) detective** — a periodic external check detects violations
  after the fact. Most adaptations are mostly (a) with some (c).
  That is acceptable. Mislabeling (a) as (b) is not.
- **Write each artifact to disk as soon as it is drafted.** Never hold
  all deliverables for one final output: long generations get cut off
  (upstream timeouts, compaction, crashes), and only what is on disk
  survives. This is the Layer's own survival rule applied to the
  adaptation work itself — *(field evidence: the first Goose adoption
  run lost its ending to an upstream idle timeout mid-generation; the
  resumed run, writing incrementally, completed.)*
- **Keep the always-loaded set small.** L0 + L1 together have a size
  ceiling (SPEC: L0 ≤ 12 KB, L1 ≤ 8 KB per file set). If your harness
  auto-loads additional files, count them against the same budget and
  report the total — that total is your *context floor* contribution
  from files (HL-B-2 also asks you to measure the harness's own
  preamble floor if your tooling exposes it).

## Step 1 — Inventory your harness

Answer these ten questions about the harness you run on. Verify each
from the harness's documentation or source code, and record the source
(a doc page, a file path, or a command's output) next to the answer.

| # | Question |
|---|---|
| Q1 | Which files does the harness **auto-load** into every session (bootstrap/context files)? Exact names, load order, and size limits if any. |
| Q2 | What is the **project-instruction** convention (per-repo/per-directory instruction files)? How are nested instructions merged? |
| Q3 | Where does **persistent memory** live, if the harness has any (files, a database, a provider plugin)? Who writes it — the agent, a background process, both? |
| Q4 | Where are **session transcripts** stored, in what format, and are they append-only? |
| Q5 | How does **compaction / summarisation** work: trigger, what is kept, what is dropped, and is there any hook that runs *before* it? |
| Q6 | What **extension points** exist (hooks, plugins, middleware, wrappers)? Which loop events can they intercept? Are they configured by files or only by code? |
| Q7 | Does the harness support **scheduled/background** execution (cron, heartbeats)? |
| Q8 | Does it support **sub-agents / delegation**? With what isolation? |
| Q9 | What **cost/token observability** exists per session or per task (a meter, a log, a usage API)? |
| Q10 | Where do **configuration** files live, and can a workspace override them per-agent? |

Any answer you cannot source is `UNVERIFIED`. An inventory with honest
`UNVERIFIED` entries is a valid result; an inventory with invented
answers is worse than none.

## Step 2 — Build the mapping table

For each row, choose a strategy:

- **native** — the harness already does this; use its mechanism.
- **pointer** — the Layer file exists in the workspace and a file the
  harness *does* auto-load references it (use this for Layer files
  missing from the Q1 list — the IDENTITY.md pattern).
- **mirror** — keep the Layer file as the source of truth and sync it
  to/from the harness's own store on a schedule or at session edges.
- **sidecar** — an external tool (wrapper, cron job, checker) provides
  the behaviour the harness lacks.
- **unsupported** — the harness cannot do this today; record the gap
  plainly instead of simulating it.

| Layer / protocol | Requirement (SPEC ref) | Native mechanism (from Q1–Q10) | Strategy | Tier (a/b/c) | Gap / note |
|---|---|---|---|---|---|
| L0 Identity | HL-L0 | | | | |
| L1 Instructions (agent SOP + project) | HL-L1 | | | | |
| L2 Curated memory + daily notes | HL-L2 | | | | |
| L3 Working state + decisions | HL-L3 | | | | |
| L4 Append-only session log | HL-L4 | | | | |
| Write-before-compact | HL-P-1 | | | | |
| Read-on-resume | HL-P-1 | | | | |
| Read-scope fence | HL-B-4 | | | | |
| Per-task budget | HL-B-5 | | | | |

## Step 3 — Instantiate the files

1. Copy the templates from `templates/` into your workspace home:
   identity, user profile, agent instructions, `MEMORY.md`,
   `memory/YYYY-MM-DD.md` daily notes, the state-file template and
   `DECISIONS.md`.
2. For every file your harness does **not** auto-load (compare against
   Q1), add a short pointer section to a file it **does** load, naming
   the file and when the agent must read it (at minimum: session start).
3. Fill in L0 from facts you actually know about your user and your
   role. Do not copy the example workspaces' content — their facts are
   fictional fixtures.

## Step 4 — Wire the protocols

- **Read-on-resume:** arrange, at the highest tier available to you,
  for a new session to read L0–L3 before working. Instruction tier is
  a protocol section in your instructions file; mechanical tier is a
  session-start hook if Q6 says one exists.
- **Write-before-compact:** if Q5 found a pre-compaction hook, use it
  (tier b). If not, do not pretend: run the protocol at tier (a) —
  agents write state as work happens, not at session end — and add
  the detective control (tier c): a periodic `harness-layer check`
  plus a habit of verifying state files after any long session.
- **Read-scope fence & budgets (HL-B-4/B-5):** state the task's file
  scope and token budget in the task instruction itself; record any
  overrun as a finding with a cause, never silently.

## Step 5 — Run the conformance check

Run `tools/harness-layer-check.py <your-workspace>` and record the
summary line (pass/fail/warn counts). Fix every FAIL you legitimately
can; for any FAIL you cannot fix, the mapping table's gap column must
already explain why. A FAIL with an honest gap note is an acceptable
adaptation result; a PASS achieved by deleting requirements is not.

## Step 6 — Measure your floor

Report two numbers, with the method for each: (1) the total size of
the always-loaded file set (L0 + L1 + anything Q1 adds), and (2) your
harness's context floor in tokens for an empty task, if your tooling
exposes it (Q9). If (2) is not measurable on your harness, write
`UNVERIFIED` — do not estimate it from (1) and present it as measured.

## Step 7 — Self-test (minimum battery)

Portability and memory claims require evidence, so run this:

1. In one session, state 20 facts about a fictional project (invent
   one; never use your user's real business data for a destructive
   test): names, numbers, deadlines, and at least three explicit
   *decisions* attributed to your user.
2. Let the session file them following the Layer's rules, then verify
   by reading the files yourself: 20/20 present, correct values,
   correct filing (decisions in `DECISIONS.md`, facts in the daily
   note / `MEMORY.md`, status in the state file).
3. Start a **fresh session** with no access to the first session's
   context. Ask the 20 questions. Score answers against the files.
   Target: ≥ 95% correct with zero clarifying questions.
4. Optionally, move the file pack to a neutral second workspace and
   repeat step 3 there (the migration drill).
5. Report scores, durations and token costs **as measured**, including
   failures. A failed battery sends you back to Step 2 — it is not
   declared done by editing the target.

## Step 8 — Write your adapter document

Write `ADAPTER-<your-harness>.md` using the template below and, if you
can, contribute it back to this repository. Follow the worked example
([ADAPTER-nanobot.md](ADAPTER-nanobot.md)) for the level of concreteness
expected: real file paths, real measured numbers, real gaps.

---

## Appendix — Adapter document template

```markdown
# Adapter — <Harness name> (status: draft | tested)

*One line: what this harness is and why it is being adapted.*

## Harness inventory (sources cited; UNVERIFIED where unsourced)
Q1..Q10 answers, each with its source.

## Mapping table
The Step-2 table, completed.

## Conformance
`harness-layer check` summary line + date + workspace(s) tested.

## Measured floor
File-set bytes; harness context floor (method) or UNVERIFIED.

## Self-test results
Filing score, cold-resume score, drill score if run; durations and
token costs as measured.

## Known gaps
Everything unsupported or tier-(a)-only, stated plainly.
```
