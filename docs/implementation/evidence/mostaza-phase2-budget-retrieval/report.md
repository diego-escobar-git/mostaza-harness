# Phase-2 preparation and historical diagnosis

Local preparation: READY. Phase-2 real evaluation: NOT_RUN. Separate GPU authorization is absent. No phase-2 outcomes or retrieval benefit are claimed.

## Historical observations

All six phase-1 sessions exhausted the 60-second budget. Each arm had PASS 0, FAIL 1, ERROR 2. Requests generated only reproduction scripts; their caught assertions and zero shell exits did not establish a fix. Official verification still failed. FastAPI/Rich had no patch. E1 used neither similarity nor graphs; E0 made one similarity attempt whose backend remains unproven. These observations justify a small matched three-minute/30-call pilot, not an efficacy conclusion.

Historical native sources, patch findings and detailed metric coverage are hash-bound in trace-diagnosis.json and comparison.json. Event gaps do not isolate model/tool wall time. Unknown telemetry remains null.

## Exact quota proposal (not authorized)

Six evaluations: E0-B180 and E1-B180, each on requests_7205, fastapi_15589, rich_3061 in that order. One private offline NVIDIA L4 x4 session; concurrency 1; zero retries. Each generation: 180 seconds, 3 minutes, 30 charged tools, 50 turns; verification: 300 seconds. Generation upper bound 18 minutes; verification upper bound 30 minutes. Total ceiling 120 wall-clock minutes from GPU allocation start, including cold start/loading/compiler/export: at most 8 GPU-device-hours and $0 paid purchases. Check the actual remaining platform quota and its accounting units before launch; quota units may differ from device-hours. Reserve 120 seconds task overhead and 300 seconds export; stop scheduling unless the full remaining per-task allowance fits.

## Technical launch blocker

No authenticated allocation-start clock and allocation-termination adapter verified for this offline Kaggle session. A Python timer or VllmServer.stop does not release the Kaggle GPU allocation.

The official Kaggle CLI exposes a run timeout, but verified coverage of allocation startup and reliable resource termination are unavailable for this prepared offline route. No allocation clock/quota was observed. The notebook launch guard therefore refuses even a manually set authorization flag. A verified external platform watchdog, remaining quota and allocation start/deadline/termination evidence are required before enabling execution. Generic GPU approval cannot waive this technical precondition. No remote notebook was pushed or started.

Official interfaces: [Kaggle kernels CLI](https://github.com/Kaggle/kaggle-cli/blob/main/skills/references/kernels.md), [Kaggle GPU quota](https://www.kaggle.com/docs/efficient-gpu-usage).

## Reproduce local preparation

```sh
/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/.tools/uv/bin/uv run --project /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness --frozen --no-sync python /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/scripts/prepare_phase2.py
/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/.tools/uv/bin/uv run --project /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness --frozen --no-sync python /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/scripts/check_phase2.py --check --cohort /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/experiments/cohort.json --evidence-dir /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/docs/implementation/evidence/mostaza-phase2-budget-retrieval
bash /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness/scripts/validate.sh
```

The preparation command writes only the generated notebook and declared readiness/comparison/report evidence. The checker is read-only: it replays authentic historical evidence, recompiles all five new closures twice and verifies exact notebook/source/payload bytes. It does not start Kaggle, install a model or infer outcomes.

B300 is proposed only if B180 is still time/tool constrained before implementation/verification. E1-R180 requires analyzed budget calibration and a new contemporaneous E0-B180 baseline. Each is a distinct later six-run batch with a separate 120-minute/8-device-hour/$0 authorization; none is launched automatically. Preserve failures; no success selection.

## Comparison limitations

- Six historical evaluations; no new inference or phase-2 outcomes.
- Event intervals are not pure model/tool wall time.
- Similarity invocation/scores do not establish vector execution.
- Partial/missing telemetry stays null with reasons; observations are not exhaustive execution totals.
- Small exploratory cohort; no significance or superiority claim.
- Patch/verification findings are host-only and never agent inputs.
- B180 readiness is not phase-2 real benchmark completion.
- B300 and E1-R180 are separate later six-run quota decisions.
- Native cost_usd=0 is not a quota measurement or unlimited allowance.
