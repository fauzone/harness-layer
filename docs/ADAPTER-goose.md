# Adapter Guide — Goose (DRAFT)

*How the Harness Layer maps onto Goose (Block / Linux Foundation).
Status: guide-level mapping written from the maintainers' harness
research; verify file conventions against your Goose version before
relying on them — Goose evolves quickly.*

## Why Goose

In the maintainers' same-model benchmark, Goose had the leanest
measured context floor (5,024 tokens, vs. Pi 10,397 and nanobot
14,413) — it is the reference for Module 3 discipline — and its
recipes are the reference pattern for Module 4 playbooks.

## Layer mapping

| Layer | Goose mapping |
|---|---|
| L0 Identity | A small always-loaded instruction set: keep the agent's persona/authority in the project instruction file (`.goosehints` / `AGENTS.md` where supported) and global hints; apply the ≤ 12 KB ceiling (HL-L0-3) — Goose's lean floor makes this easy to honour |
| L1 Instructions | Project hints file per repository = L1b; workspace/user-level hints = L1a. Apply the hierarchy & conflict rules of HL-L1-2 manually until the harness grows merge support |
| L2 Long-term memory | `MEMORY.md` + `memory/YYYY-MM-DD.md` in the project/workspace directory, in Git, exactly as Module 1 specifies — the Layer's formats are deliberately harness-neutral so nothing Goose-specific is needed |
| L3 Working state | `STATE*.md` / `DECISIONS.md` per job home, same templates. Goose **recipes** (YAML) can encode the recurring steps that produce and update state |
| L4 Session log | Goose keeps session history locally; export/retain it as the append-only record. Summary nodes (HL-L4-2) are an adapter responsibility until natively supported — label the tier honestly (HL-P-2) |

## Module notes

- **Module 3:** start from Goose's floor; keep extensions (MCP) few
  and purposeful — every extension's tool schemas add to the floor.
- **Module 4:** recipes are the native playbook mechanism (OR-1);
  run headless per task from a deterministic scheduler when the agent
  is a resident worker, so schedules and triggers belong to the
  system, not to the model's discretion.

## Conformance

Run `tools/harness-layer-check.py` against the workspace directory
the agent treats as home; report pass/fail per clause plus the
measured context floor (CC-2).
