# A/B Evaluation — With vs. Without Harness Layer (Pilot)

*Run 2026-10-28 under a protocol frozen before the first run. Harness:
Goose v1.56.0. Model (both arms, identical): `nvidia/nemotron-3-ultra-
550b-a55b:free`. n = 2 per cell — read every number below as a pilot
indication, not a proof. Tokens are read from Goose's own session
ledger (`usage_ledger`), never from agent self-reports.*

## Setup
- **Control arm:** plain Goose workspace, harness defaults only.
- **Layer arm:** the workspace produced by the tested Goose adoption
  (see `ADAPTER-goose.md`), job-specific leftovers reset, plus the
  identical task fixtures.
- Run order interleaved K-L-L-K per task; fresh sessions and isolated
  per-run state; scoring fully mechanical (answer keys, hidden tests).

## Results

### T1 — Cold-resume recall (20 fictional facts planted in session A, questioned in a brand-new session B)
| Arm | Score | Total tokens | Session-B tokens | Wall clock |
|---|---|---|---|---|
| Control | **0/20, 0/20** | 16,867 / 16,637 | 10,957 / 10,885 | 29.0s / 25.4s |
| Layer | **20/20, 20/20** | 101,468 / 67,286 | 9,980 / 18,697 | 154.5s / 69.0s |

Manually verified: the control session B answered, verbatim, that it
had no information and its working directory was empty — the control
agent wrote nothing in session A. The 0 is real, not a scoring
artefact. The Layer's cost sits almost entirely in session A (the
filing work: ~40–91K tokens); answering in session B costs about the
same in both arms (≈1.3× midpoints).

### T2 — Continued coding job (small CLI tool, 6 hidden checks)
| Arm | Score | Total tokens | Wall clock |
|---|---|---|---|
| Control | 6/6, 6/6 | 143,794 / 161,566 | 222s / 379s |
| Layer | 6/6, 6/6 | 380,037 / 339,195 | 242s / 325s |

Quality tied at the ceiling; Layer tokens ≈2.4× midpoints; wall clock
comparable.

### T3 — Short one-shot task (negative control; 6 constraints)
| Arm | Score | Total tokens | Wall clock |
|---|---|---|---|
| Control | 6/6, 6/6 | 29,228 / 29,129 | 59s / 152s |
| Layer | 6/6, 6/6 | 57,468 / 47,019 | 61s / 42s |

As pre-registered in the protocol: on a short task the Layer is pure
overhead (≈1.8× tokens) with no quality gain. No sign of treatment
leakage (the Layer did not "win" where it should not).

## Deviations from the frozen protocol (recorded, not hidden)
1. Cell T3-control-1 ran first as a pipeline smoke test and was kept
   as a valid cell (T3 order became K1 → L1 → L2 → K2).
2. **T2 did not test mid-work interruption as designed**: in all four
   cells the session-A agent finished the small job by itself before
   the 480s cut (104–290s), so session B verified/continued nearly
   finished work — explaining the 6/6 ceiling in both arms. Protocol
   v2 needs a larger job or a much shorter session-A cap (~120s).

## Verdict
1. **The core claim held, in pilot strength**: cross-session
   continuity 20/20 with the Layer vs. 0/20 without. Without it, a new
   session really does start from zero.
2. **This project's own acceptance criterion "cost non-regression
   (≤ +10% tokens per task)" is NOT met by the current adoption.**
   Measured overhead: ≈1.8× on short tasks to ≈5× on fact-planting
   tasks. The benefit is real but narrow (continuity); the cost is
   broad. The SPEC and roadmap now state this openly.
3. Wall-clock speed shows no consistent penalty.
4. The concrete improvement target for Module 3 (cost discipline):
   session-A filing overhead — the adopted agent spends most of its
   tokens exploring/inventorying before writing small files. The
   read-scope fence (HL-B-3/B-4) exists on paper; behaviour is still
   expensive. Protocol-v2 target: T1 Layer tokens ≤2× control at a
   held 20/20 score, n=3, T2 hardened per deviation 2.
