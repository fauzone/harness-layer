# Adapter — nanobot (status: tested)

*nanobot is a small, MIT-licensed Python agent harness (~4k lines of
core) with a workspace-file model very close to this Layer's. It is the
maintainers' production harness and this Layer's reference
implementation: the first adoption, the sandbox test and the migration
drill were all run on it. Everything below was verified against the
installed source or measured in those tests (2026-10-28); anything not
verified is labelled `UNVERIFIED`.*

## Harness inventory

- **Q1 Auto-loaded files:** `AGENTS.md`, `SOUL.md`, `USER.md` — exactly
  these three (`agent/context.py`: `BOOTSTRAP_FILES`). `AGENTS.md` is
  read from the project root, `SOUL.md`/`USER.md` from the workspace.
  `MEMORY.md` is **not** in the bootstrap list; memory content reaches
  sessions through the memory subsystem (below), and `IDENTITY.md` is
  **not loaded at all** — see the pointer strategy in the mapping.
- **Q2 Project instructions:** `AGENTS.md` doubles as agent SOP and
  project instructions. There is no separate L1a/L1b split and no
  built-in hierarchy/conflict merge; the SPEC's split must be
  maintained by convention inside the file.
- **Q3 Persistent memory:** files in the workspace — `memory/MEMORY.md`
  plus `memory/history.jsonl` (`agent/memory.py`). A background
  consolidation process ("Dream") rewrites `SOUL.md`, `USER.md` and
  `memory/MEMORY.md`; the agent also writes memory during sessions.
  Because a background process can rewrite curated files, the SPEC's
  self-learning guard (HL-G) matters here in practice, not in theory.
- **Q4 Session transcripts:** one JSONL file per session under a
  `sessions/` directory located relative to the config file. Entries
  include a provider-reported usage record per turn (`_last_usage`).
- **Q5 Compaction:** an `AutoCompact` component (`agent/autocompact.py`)
  archives expired sessions (our deployment sets
  `idleCompactAfterMinutes: 15`), and a `ContextGovernor`
  (`agent/context_governance.py`) prepares/trims message lists before
  model calls. **No pre-compaction hook is exposed.** The internal
  order in which message content is trimmed is `UNVERIFIED`.
- **Q6 Extension points:** a real hook system exists (`agent/hook.py`,
  `AgentHook`: `before_run`, `after_run`, `before_iteration`,
  `before_execute_tools`, `before_execute_tool`, `after_execute_tool`,
  `on_execute_tool_error`, `after_iteration`, …) — but hooks are
  registered **programmatically in Python code**, not from workspace
  files, and none of them fire before compaction.
- **Q7 Scheduling:** yes — the harness ships cron-style scheduled jobs,
  used in production in this deployment.
- **Q8 Sub-agents:** multiple named workspaces/agents run under one
  installation. In this deployment, delegation goes through an
  external wrapper (a sidecar, see L4/budget rows) that records every
  invocation's tokens and status.
- **Q9 Cost observability:** per-turn provider-reported usage in the
  session JSONL; the deployment's wrapper aggregates it into a
  per-invocation meter (tokens in/out/total, call count, duration).
- **Q10 Configuration:** JSON config files; each agent has its own
  workspace directory and can run under a dedicated config (used to
  isolate the sandbox tests from production).

## Mapping table

| Layer / protocol | Native mechanism | Strategy | Tier | Gap / note |
|---|---|---|---|---|
| L0 Identity | `AGENTS.md` + `SOUL.md` + `USER.md` auto-loaded | native for those three; **pointer** for `IDENTITY.md` (an "identity file" section in `AGENTS.md` tells the agent to read it at session start) | (a) | `IDENTITY.md` is never auto-loaded by nanobot — the single most important finding of the gap audit |
| L1 Instructions | `AGENTS.md` | native, by convention split into SOP vs project sections | (a) | No hierarchy/merge support (HL-L1-2 manual) |
| L2 Memory | `memory/MEMORY.md` + daily notes `memory/YYYY-MM-DD.md` + `history.jsonl` | native files; promotion & provenance rules in the protocol section | (a) + (c) periodic check | Background consolidation can outpace curation; daily notes must be re-established as files, not only `history.jsonl` entries |
| L3 State | `STATE*.md`, `DECISIONS.md` per job home | native files (plain convention) | (a) | Nothing enforces the ≤15-line discipline except the checker (tier c) |
| L4 Session log | Session JSONL + `history.jsonl` | native | (a) | Summary nodes (HL-L4-2) are an adapter responsibility; resume/search are file-level, not product features |
| Write-before-compact | — | instruction protocol + write-as-you-go rule | (a) | No pre-compaction hook exists (Q5/Q6); mechanical tier awaits harness support |
| Read-on-resume | Protocol section in `AGENTS.md` (read L0–L3 at session start) | native (instruction) | (a) | Proven effective in the cold-resume test below |
| Read-scope fence (HL-B-4) | Stated in the protocol section | instruction | (a) | Proven to have teeth: a test session **refused** a dispatcher instruction to read outside its fenced workspace, citing this rule |
| Per-task budget (HL-B-5) | Wrapper meter (sidecar) records every invocation | sidecar | (b) recording / (c) review | The meter records and reports; it does not yet cut off an overrunning task |

## Conformance

- Sandbox clone of a production workspace, after adoption:
  **12 pass / 0 fail / 0 warn** (`harness-layer check`, 2026-10-28).
- All **11 production workspaces** after the additive promotion
  (identity file, decision log, protocol section; nothing overwritten):
  **fail = 0 on every workspace**. Remaining warnings are the expected
  kind (no daily note yet for today, no per-job state file yet).

## Measured floor

- Always-loaded file sets in the tested workspaces: **4,978–9,011
  bytes** (within the 12,288-byte L0 ceiling), measured by the checker.
- Harness context floor: **14,413 tokens** for an empty task, measured
  by the maintainers in a same-model comparison (2026-10-27; Goose
  5,024, Pi 10,397 in the same study) — nanobot's floor is the fattest
  of the three, which is exactly why HL-B-2 asks every adapter to
  publish this number.

## Self-test results (2026-10-28, fictional "KiosKita" fixture)

- **Filing:** 20/20 planted edge cases found on disk with correct
  values and correct filing (decisions → `DECISIONS.md`, facts → daily
  note + `MEMORY.md`, status → state file, 13 lines).
- **Cold resume:** a fresh session answered **20/20** from disk alone,
  0 clarifying questions (target ≥ 95%).
- **Migration drill:** the file pack moved to a neutral workspace with
  a foreign persona; a session there answered **20/20** and continued
  the job correctly (next-step entry written, state file updated
  within its line limit). An earlier drill attempt produced the fence
  finding above: the agent refused to read a brief placed *outside*
  its fenced workspace.
- **Costs, as measured by the wrapper meter:** filing session
  3,698,936 tokens / 63 calls; cold-resume 6,692,128 / 70; drill
  948,302 / 33. The first two numbers are the honest baseline that
  motivated HL-B-4/B-5: protocol-perfect, efficiency-poor.

## Known gaps

- No mechanical write-before-compact (tier a only) — pending harness
  support for a pre-compaction hook.
- `IDENTITY.md` requires the pointer strategy forever unless the
  bootstrap list grows.
- L1 hierarchy/conflict rules are manual.
- Compaction's internal trim order is `UNVERIFIED`.
- The budget meter records but does not enforce a cut-off.
