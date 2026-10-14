# V-CPU-01 native end-to-end CPU diagnostics

Status: FINAL_GATE_PASS; independent audit PASS with zero findings. The native verifier
remains unchanged. No GPU, model inference, Kaggle session, Discussion or merge.

## Finding and limits

The complete approved CPU protocol ran with the real swegemma 0.2.11 verify_task
and SubprocessManager. All eight synthetic controls behaved as required. Requests
baseline, retained E0-B180 patch and retained E1-B180 patch each reached all five
independent diagnostic nodes in the actual pytest process. All three imported
requests.utils from the official local environment's site-packages, not the
extracted workspace/src/requests/utils.py. That environment has Requests 2.34.2.

Observed module SHA256:
657fd02343b2586bbd138a4ec0f03ceeb7610c2712f96ac54f28a708bf7d079c

Observed loaded-function fingerprint (cpu-code-json-v1, Python 3.13.15):
71939d2e8ce6aa05c5695427647a180a55036b2903d7bbae07a832a5ff5d1309

All three Requests runs failed the mandatory origin assertion and passed the four
own behavioral tests against that installed code. Native resolved=false/exit1
was preserved. These behavior passes do not validate either workspace patch;
they do not show that the two patches are equivalent, correct or incorrect.
The protocol status is CPU_E2E_CONTROLS_PASS_REQUESTS_BINDING_MISMATCH, an allowed
diagnostic outcome under the approved contract. It is not a benchmark PASS.

This directly establishes a local development-backend binding problem. It does
not retroactively establish historical Kaggle imports or the cause of every old
Requests failure, and does not attest the private scorer. Host macOS/Python 3.13.15/
pytest 9.1.1 differs from the historical Kaggle host Python 3.12.13/pytest 8.4.2.
GPU readiness remains false; actual_scorer_runtime_parity remains null with a
reason. Import/setup repair and any GPU batch require separate approval.

## Matrix and native acceptance

| Case | Native result | Intended observation |
| --- | --- | --- |
| V01 | false, exit1 | Faulty baseline assertion fails; workspace binding verified. |
| V02 | true, exit0 | Generic correct patch passes required tests and native JUnit validation. |
| V03 | false, exit1 | Incorrect patch assertion fails with verified binding. |
| V04 | false, exit1 | Competing root module rejected despite matching behavior. |
| V05 | false, exit0 | Required skipped test rejected by native JUnit checks. |
| V06 | false, exit5 | No collected tests rejected. |
| V07 | false, exit0 | Premature exit without JUnit rejected by native validator. |
| V08 | false, exit1 | Attempt to alter protected tests cannot credit a faulty product. |
| R00 | false, exit1 | Baseline: origin fails; four own behavioral tests pass on installed code. |
| R01 | false, exit1 | E0 retained patch: same measured origin failure. |
| R02 | false, exit1 | E1 retained patch: same measured origin failure. |

No reserved mock bypass, native monkeypatch, alternate verifier, import-path
repair, origin plugin, original Task.patch or original test_patch was used.
Own test bodies record module file, loaded-function fingerprint, PID/parent PID,
interpreter, Python/pytest, cwd and ordered sys.path before assertions. Their
coverage is actual_pytest_owned_diagnostic_test_cpu, not general pytest hooks or
teardown telemetry. V05/V06 intentionally have null body coverage with reasons.
Native JUnit XML is consumed internally and removed by native cleanup; its raw
bytes remain null with a reason. TaskResult is the final resolution authority.

## Implementation and reproducibility

The new spec is docs/specs/verify-task-cpu.md. Scripts verify_task_cpu_fixtures.py
and check_verify_task_cpu.py construct owned fixtures/Task inputs, enforce limits
and classify the returned native result plus independently validated witnesses.
The host module verifies archive safety, immutable input pins and binding.
Runbook guidance is appended in docs/runbooks/kaggle-execution.md.

Use the exact nine commands in plan-for-approval.md, sequentially from the phase2
worktree. The final command is:

```sh
.tools/official/bin/python scripts/check_verify_task_cpu.py --check
```

Execution consumes a CPU-matrix attempt and needs an available approved budget;
no further attempt is currently authorized. Original source/patch/archive pins are
in prerequisites.json; source files match corrected-source-inventory.json.
Requests compressed archive SHA starts 42dc3d36, as acquired and already documented
in B180 evidence; its base tree was rechecked. The original cohort's 4a293476
compressed hash was not rewritten or conflated with the acquired archive.

## Exact final gate evidence

All nine commands passed on the corrected source in gate attempt 3, separately
authorized by additional-attempt-approval.json. Total wall time:
98.87s, below 1200s. The final native matrix started,
produced results for and accepted exactly 11 serial invocations, no retries; its
wall time was 30.58s. The gate includes Ruff, strict mypy
on 42 source files, 306 unit tests, 45 integration tests, build, official compiler
validation, old source/evidence checks and the new native matrix.

Controller limits: 30s per native command/pytest, 90s per case, 1 GiB polled local
artifact cap. Actual peak space and CPU-process time were not recorded and stay
null with reasons; wall times and retained file bytes are recorded. All 11 native
cleanup flags are true and no sandbox directories remain. All immutable input
pins, including the pre-existing dirty closed SDD plan, were rechecked unchanged.

The first two authorized attempts remain historical failures: attempt 1 stopped
on my error/error_message classifier mistake after 7 native results (6 accepted);
attempt 2 stopped on my disk-meter/native-cleanup race after 5 native results
(4 accepted). Repairs and focused tests were independently reviewed before the
additional attempt. Neither failed run is relabeled PASS. Their reports/audit
checkpoint are retained under checkpoints/before-additional-attempt. There are
23 native result files across all three attempts; only the final 11 constitute
the accepted matrix. These counts are CPU diagnostics, not new Kaggle evaluations.

Compact cpu-results.json retains every case, process witness, outcome and input/
result hash; raw-inventory.json pins ignored native outputs/logs. gate-attempts.json
retains command exits/times/log hashes for all three attempts. Historical raw
outputs, original configurations, notebooks and earlier evidence remain unchanged.

## Closure and next boundary

The independent auditor verified the complete relevant delta, authorization,
source inventory and actual final matrix, returning PASS with zero findings.
See audit.json. Commit/push/update existing PR2 toward develop is authorized
following these checks. No merge. The unrelated closed-plan working-tree change
remains byte-identical and excluded from this commit.

Next scientific/engineering work is a separately specified, CPU-tested import
binding remedy consistent with the official backend and unchanged scorer policy.
Until then the measured local Requests patch binding is invalid. No new real
evaluation, hidden-test observation, P-CV-01 activation or organizer outreach is
implied. This result supplies no evidence of hybrid retrieval efficacy.
