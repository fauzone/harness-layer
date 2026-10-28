# Adapter — Goose (status: tested)

*Harness Layer adoption for Goose (Block / Linux Foundation) v1.56.0. Goose was chosen for its lean context floor (~5,024 tokens in maintainers' benchmark) and native recipe/subagent support, making it the reference for Module 3 (Cost & Context Discipline) and Module 4 (Orchestration Patterns).*

> **Provenance (maintainers):** this document was written by a Goose
> agent itself (Goose v1.56.0; model `nvidia/nemotron-3-ultra-550b-a55b:free`)
> on 2026-10-28, in a clean sandbox, given **only this repository and a
> prompt pointing at the README** — i.e. it is the first field test of
> [ADAPTER-GUIDE.md](ADAPTER-GUIDE.md) by a foreign agent on a foreign
> harness. The maintainers re-ran the conformance check independently
> and reproduced its summary exactly (11 pass / 0 fail / 1 warn).
> Measured cost of the full adoption run: 2,766,020 accumulated tokens
> (provider-reported, Goose `usage_ledger`), ~21 minutes of session
> activity across three sittings (the free-model upstream dropped the
> session twice; the agent resumed from its own L3 state file each
> time). "Tested" here covers the adoption steps (inventory, mapping,
> instantiation, conformance); the Step 7 self-test battery is
> explicitly deferred in the document below. This document replaces
> the maintainers' earlier desk-written draft mapping.

---

## Harness inventory (sources cited; UNVERIFIED where unsourced)

**Q1 — Auto-loaded files:** Global `~/.config/goose/.goosehints` + local `.goosehints` (hierarchical, nested discovery) + `CONTEXT_FILE_NAMES` files (default: `["AGENTS.md", ".goosehints"]`) + persistent instructions (`GOOSE_MOIM_MESSAGE_FILE/TEXT`, 64 KB, every turn) + system prompt (`system.md` template) + extension tool schemas. *Sources: https://goose-docs.ai/docs/guides/context-engineering/using-goosehints, https://goose-docs.ai/docs/guides/context-engineering/using-persistent-instructions, https://goose-docs.ai/docs/guides/context-engineering/prompt-templates, observed `goose info -v`.*

**Q2 — Project-instruction convention:** `AGENTS.md` and `.goosehints` loaded hierarchically (global → workspace → project → subdirectory). Local wins on conflict. Custom filenames via `CONTEXT_FILE_NAMES`. *Sources: https://goose-docs.ai/docs/guides/context-engineering/using-goosehints, https://goose-docs.ai/docs/guides/environment-variables.*

**Q3 — Persistent memory:** No native `MEMORY.md`. Session history in SQLite (`~/.local/share/goose/sessions/sessions.db`: `messages`, `usage_ledger`). Chat Recall extension (disabled by default) provides session summaries. Memory MCP documented but requires explicit setup. *Sources: https://goose-docs.ai/docs/guides/context-engineering/index.md, https://goose-docs.ai/docs/mcp/memory-mcp, observed SQLite schema, `goose info -v` shows `chatrecall: enabled: false`.*

**Q4 — Session transcripts:** SQLite `messages` table (append-only, `content_json`, `tokens`, `metadata_json`). `usage_ledger` tracks per-invocation tokens/cost with `is_compaction` flag. Export via `goose session export` (JSON). Import accepts JSON/JSONL. *Sources: observed SQLite schema, https://goose-docs.ai/docs/guides/goose-cli-commands.*

**Q5 — Compaction:** Auto at `min(0.8 × context_window, 225000)` tokens (configurable via `GOOSE_AUTO_COMPACT_THRESHOLD`, `GOOSE_AUTO_COMPACT_TOKEN_LIMIT`). Manual via `/compact` (CLI) or "Compact now" (Desktop). Older tool outputs summarized first (`GOOSE_TOOL_CALL_CUTOFF`). Full history retained in SQLite. **No pre-compaction hook** — supported events: `SessionStart`, `SessionEnd`, `Stop`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `BeforeReadFile`, `AfterFileEdit`, `BeforeShellExecution`, `AfterShellExecution`. `Stop` fires at turn end; UNVERIFIED if it reliably intercepts compaction. Compaction prompt customizable via `compaction.md` template. *Sources: https://goose-docs.ai/docs/guides/sessions/smart-context-management, https://goose-docs.ai/docs/guides/context-engineering/hooks, https://goose-docs.ai/docs/guides/context-engineering/prompt-templates, observed `usage_ledger.is_compaction`.*

**Q6 — Extension points:** Hooks via Open Plugins spec. Plugin dirs: `~/.agents/plugins/`, `<project>/.agents/plugins/`, installed. `hooks/hooks.json` maps events to shell commands. `PreToolUse` and `Stop` can block (exit 2 or `{"decision":"block"}`). Others observation-only. Plugins package skills/hooks. File-based config. *Sources: https://goose-docs.ai/docs/guides/context-engineering/hooks, https://goose-docs.ai/docs/guides/context-engineering/plugins.*

**Q7 — Scheduled/background:** Scheduler extension (built-in, enabled). `goose schedule` CLI. Recipes scheduled via cron/intervals. *Sources: `goose info -v` shows `scheduler: enabled: true`, https://goose-docs.ai/docs/guides/recipes/session-recipes.*

**Q8 — Sub-agents:** `summon` extension (enabled) provides `delegate`/`load`. Isolation: no subagent spawning, no extension mgmt, no schedule mgmt. Inherit extensions by default; restrictable. Sequential (default) or parallel. 5-min timeout default. Full details or summary return modes. Recipe-based subagents with `sub_recipes` auto-inject `summon`. *Sources: https://goose-docs.ai/docs/guides/context-engineering/subagents, `goose info -v` shows `summon: enabled: true`.*

**Q9 — Cost/token observability:** Per-session token display (Desktop: colored circle with hover; CLI: context label with dots/colors). Per-invocation in `usage_ledger` (`input_tokens`, `output_tokens`, `total_tokens`, `cost`, `is_compaction`). `GOOSE_CLI_SHOW_COST=true` enables CLI cost. Desktop shows session cost with model breakdown. Accumulated totals in `sessions` table. *Sources: https://goose-docs.ai/docs/guides/sessions/smart-context-management, https://goose-docs.ai/docs/guides/environment-variables, observed SQLite schema.*

**Q10 — Configuration:** Primary: `~/.config/goose/config.yaml`. Workspace override: `<project>/.config/goose/settings.json` (disabledPlugins). Other: `permission.yaml`, `secrets.yaml`, `permissions/tool_permissions.json`, `prompts/`. Env vars override config (highest priority). Key vars: `GOOSE_PROVIDER`, `GOOSE_MODEL`, `GOOSE_MAX_TURNS`, `GOOSE_AUTO_COMPACT_THRESHOLD`, `CONTEXT_FILE_NAMES`, `GOOSE_MOIM_MESSAGE_TEXT/FILE`, `GOOSE_RECIPE_GITHUB_REPO`, `GOOSE_SEARCH_PATHS`. *Sources: https://goose-docs.ai/docs/guides/config-files, https://goose-docs.ai/docs/guides/environment-variables, `goose info -v`.*

---

## Mapping table

| Layer / protocol | Requirement (SPEC ref) | Native mechanism | Strategy | Tier | Gap / note |
|---|---|---|---|---|---|
| L0 Identity | HL-L0-1,2,3 | Hints + persistent instructions | **pointer** | (a) | L0 files created in workspace; `@`-referenced in `.goosehints` for auto-load. Total 6,193 bytes ≤ 12 KB. |
| L1 Instructions | HL-L1-1,2,3 | `AGENTS.md` + `.goosehints` hierarchical | **native** | (a) | L1a = workspace `AGENTS.md`; L1b = project `AGENTS.md`. Conflict rule matches (local wins). L1b ≤ 8 KB. |
| L2 Curated memory | HL-L2-1..6 | None (SQLite + optional extensions) | **pointer** | (a) | `MEMORY.md` + `memory/YYYY-MM-DD.md` created; `@MEMORY.md` in `.goosehints`. Promotion per HL-L2-3/4. ≤ 32 KB. |
| L3 Working state | HL-L3-1..4 | None (recipes encode steps) | **pointer** | (a) | `STATE.md` (8 lines ≤ 15) + `DECISIONS.md` created; `@`-referenced in `.goosehints`. Updated immediately per HL-L3-3. |
| L4 Session log | HL-L4-1..4 | SQLite `messages` (append-only) + `usage_ledger` | **mirror** | (a)+(c) | Primary: SQLite (native). Mirror: periodic export to JSONL + summary nodes (sidecar). `harness-layer check` verifies. |
| Write-before-compact | HL-P-1,2 | No pre-compact hook | **pointer** + **sidecar** | (a)+(c) | Instruction: flush as work happens (HL-L3-3). Detective: `harness-layer check` + post-session verification. No mechanical hook (UNVERIFIED if `Stop` intercepts compaction). |
| Read-on-resume | HL-P-3,4 | Hints auto-load; SQLite history | **native** + **pointer** | (a) | Hints load at resume. Agent instructed to read L2/L3 explicitly. Compaction summary = search hint; disk wins (in L0/L1). |
| Read-scope fence | HL-B-4 | None (tool output summarization only) | **pointer** | (a) | Task brief defines scope. Out-of-scope = finding with cause. Enforced via L0/L1 instruction. |
| Per-task budget | HL-B-5 | `GOOSE_MAX_TURNS`, token display, `usage_ledger` | **native** + **pointer** | (a) | Budget in task instruction. Overrun = finding with cause. Native metering (Tier b for visibility, a for discipline). |

**Enforcement tiers achieved:** All protocols at Tier (a) instruction-based + Tier (c) detective via `harness-layer check`. **No Tier (b) mechanical enforcement exists** — Goose lacks pre-compaction hooks, mandatory file-read-on-resume hooks, and scope-fence enforcement.

---

## Conformance

```
$ python3 harness-layer/tools/harness-layer-check.py goose-home
PASS L0-FILES SOUL.md exists (397 bytes)
PASS L0-FILES IDENTITY.md exists (408 bytes)
PASS L0-FILES USER.md exists (608 bytes)
PASS L0-FILES AGENTS.md exists (4780 bytes)
PASS L0-SIZE total 6193 bytes <= 12288
PASS L2-SIZE MEMORY.md 1971 bytes <= 32768
PASS L2-FILES MEMORY.md exists
PASS L2-FILES memory/ directory exists
PASS L3-STATE STATE.md has 8 lines <= 15
PASS L3-DECISIONS DECISIONS.md exists in workspace root
PASS L2-DAILY memory/2026-10-28.md exists
WARN L4-LOG no sessions/ directory or history.jsonl found
SUMMARY pass=11 fail=0 warn=1
```

**Date:** 2026-10-28  
**Workspace tested:** `/home/hatch/workspace/harness-layer/sandbox/goose-test/goose-home`  
**Result:** 11 PASS, 0 FAIL, 1 WARN (L4 log format mismatch — Goose uses SQLite, not JSONL; documented as known gap)

---

## Measured floor

| Metric | Value | Method |
|---|---|---|
| Always-loaded file set (L0 + L1a + `.goosehints`) | ~6.5 KB | `wc -c` on SOUL.md, IDENTITY.md, USER.md, AGENTS.md, .goosehints |
| Harness context floor (tokens) | ~5,024 tokens | Maintainers' benchmark (ADAPTER-goose.md draft); UNVERIFIED by this run — Goose token display shows per-session usage but not isolated preamble floor. `GOOSE_CLI_SHOW_COST` shows cost, not raw preamble tokens. |

**Note:** The harness context floor (fixed preamble: system prompt + tool schemas) was not independently measured in this run. The ~5,024 token figure comes from the maintainers' published benchmark. Per SPEC HL-B-2, adapters MUST measure and report their own floor; this entry is labelled UNVERIFIED for this adaptation.

---

## Self-test results

**Step 7 (self-test) DEFERRED** — explicitly declared per ADAPTER-GUIDE scope for this run (Steps 1-5 and 8 only).

| Battery | Score | Duration | Token cost | Notes |
|---|---|---|---|---|
| Filing (20 facts in one session) | NOT RUN | — | — | Deferred |
| Cold-resume (fresh session, 20 questions) | NOT RUN | — | — | Deferred |
| Migration drill (neutral second workspace) | NOT RUN | — | — | Deferred |

**Reason:** The self-test requires a full session cycle with planted facts, compaction/forced context discard, and a fresh session resume — which cannot be completed in a single continuous adaptation run. A separate session must be started after this adaptation completes to verify compaction survival and cold-resume recall from disk alone. This is documented in DECISIONS.md (2026-10-28) and STATE.md.

---

## Known gaps

| Gap | Layer/Protocol | Severity | Mitigation |
|---|---|---|---|
| No pre-compaction hook | Write-before-compact (HL-P-1) | Medium | Tier (a) instruction + Tier (c) detective check. Agent must flush state *as work happens*. |
| No mechanical read-on-resume enforcement | Read-on-resume (HL-P-3) | Low | Hints auto-load; agent instructed to read L2/L3 explicitly at start. |
| No read-scope fence enforcement | Read-scope fence (HL-B-4) | Medium | Instruction-only. Task brief must define scope; violations recorded as findings. |
| L4 log format mismatch | L4 (HL-L4-1) | Low | Goose uses SQLite (append-only, queryable). JSONL mirror via sidecar export if needed. `harness-layer check` warns but passes. |
| No summary nodes in native log | L4 (HL-L4-2) | Low | Compaction tracked via `usage_ledger.is_compaction`. Summary nodes generated by adapter sidecar if required. |
| Context floor not independently measured | HL-B-2 | Medium | Reported as UNVERIFIED. Requires isolated preamble measurement (not available via current Goose tooling). |
| Subagent lifecycle hooks not emitted | Module 4 / Orchestration | Low | `SubagentStart`/`SubagentStop` documented as not emitted. Limits hook-based observability. |
| Chat Recall / Memory MCP not enabled | L2 Memory | Low | Available but disabled by default. Could be enabled for cross-session memory if needed. |

---

## Reproduction notes

Another agent can reproduce this adaptation by:

1. **Workspace setup**: Create `./goose-home` with the 8 Layer files (SOUL.md, IDENTITY.md, USER.md, AGENTS.md, MEMORY.md, STATE.md, DECISIONS.md, memory/2026-10-28.md) using the templates from `harness-layer/templates/`.
2. **Wiring**: Create `.goosehints` in workspace root with `@`-mentions for all Layer files (see this workspace's `.goosehints`).
3. **Goose config**: Ensure `developer`, `analyze`, `summon`, `apps`, `extensionmanager`, `tom`, `scheduler` extensions enabled (default in v1.56.0). `CONTEXT_FILE_NAMES` default (`["AGENTS.md", ".goosehints"]`) works.
4. **Verification**: Run `python3 harness-layer/tools/harness-layer-check.py goose-home` — expect 11 PASS, 0 FAIL, 1 WARN (L4 log).
5. **Protocols**: Add the protocol guardrails (write-before-compact, read-on-resume, read-scope fence, per-task budget) to AGENTS.md or persistent instructions.
6. **Self-test**: Run Step 7 in a separate session cycle to measure compaction survival and cold-resume recall.

All files are plain-text in Git. No proprietary store dependencies.