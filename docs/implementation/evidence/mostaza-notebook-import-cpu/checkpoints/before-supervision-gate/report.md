# N-IMPORT-CPU-01 — fifth gate consumed; bounded observer prepared

Status: BLOCKED_CPU_GATE_ALLOWANCE_EXHAUSTED. No complete gate PASS or final
completion. No commit/push/PR update. HEAD remains bcec689aadc9be0801de6b1c7e560d776e17299e.
Five immutable receipts and historical approvals are preserved. The original
closed SDD plan is not reopened; its pre-existing dirty bytes remain unchanged.

## Implemented notebook and source correction

The GPU/network-disabled candidate uses E0-C8K-L1/E1-C8K-L1 host identities,
unchanged C8K agent closures and an explicit parent-versus-actual input envelope.
The official resolver supplies the same base-plus-layout tuple to pre-model setup
and verification. The sole Requests layout delta is requests -> src/requests.
Original cohort, model, prompts, sampling, budgets and repair policy are preserved;
no native verifier, command, environment or official source archive is changed.

The source proof now always uses tarfile.data_filter and restores ONLY safe trailing
separators of tracked symlinks when both spellings resolve identically inside the
root. Other normalization is rejected; Git cleanliness/index and one-link delta
checks remain. gate4-source-diagnosis.json identifies the original tracked
certificate link and a host-only source proof. Gate5 reached actual Requests
setup and verification, so this correction now has baseline native coverage.

Historical blocked reports/records remain byte-exact in checkpoints/, including
before-source-filter-gate/. No historical result is retroactively reassessed.

## Actual execution and coverage

| Gate | Wall seconds | Outcome | Native starts/results | Setup | Stdlib3.12 |
| --- | ---: | --- | --- | ---: | ---: |
| 1 | 253.4993 | Commands1–9 PASS; interrupted10 PermissionError | 20/19 | 0 | 0 |
| 2 | 171.2035 | Commands1–10 PASS; first setup assessment stopped11 | 21/21 | 1 | 0 |
| 3 | 6.9295 | Command1 stopped by observed artifact cap | 0/0 | 0 | 0 |
| 4 | 144.3997 | Commands1–10 PASS; generic3 accepted; Requests host proof stopped | 23/23 | 3 | 0 |
| 5 | 215.9226 | Commands1–10 PASS; generic3+Requests baseline accepted; ps timeout | 24/24 | 4 | 0 |

Cumulative: 88 native starts, 87 retained native results, 8 setup, 0 stdlib probes,
791.9546 wall seconds. All five gate authorizations are consumed, regardless of
unused per-call headroom. No native/setup/stdlib run occurred after gate5.

Gate5 command1 passed 378 unit and 86 integration tests, lint/format, typing on
56 source files, package build, official compiler and historical evidence checks.
Host pytest retention remained confined to command1 and solved gate3's cap issue.
The frozen legacy matrices completed 11+9 native regressions. New L01/L02/L03/R00
have raw result and controller assessment markers; final matrix summary is absent
because the outer controller terminated command11. It is null with a reason, never
reconstructed as a successful runtime aggregate.

| New row | Setup source binding | Verification source binding | Own control outcome |
| --- | --- | --- | --- |
| N-L01 faulty generic | Accepted | Accepted | Expected assertion failure, unresolved |
| N-L02 correct generic | Accepted | Accepted | Passed, resolved |
| N-L03 wrong generic | Accepted | Accepted | Expected assertion failure, unresolved |
| N-R00 Requests baseline | Accepted | Accepted | Origin/missing/valid passed; empty machine/default failed, unresolved |

For R00, both module/function witnesses point into their respective snapshot
workspace/src/requests trees and have actual process/runtime fingerprints. These
are own diagnostics, not a Kaggle score. R01 preparation was dispatched but no
setup-started/native-started marker exists; R02 and both Python3.12 transport probes
were NOT_RUN. Older Requests alias regressions never substitute for these rows.

## Fifth-gate interruption and cleanup

The exact failure is TimeoutExpired in the OUTER controller's call to frozen
check_verify_task_cpu.process_table: full ps exceeded its 2-second limit. The cause
of the OS delay is unknown. No claim of memory pressure, tool leak or native test
failure is supported. Outer and inner controllers nominally query ps on every
0.2-second loop; actual sampling rate was not measured.

Gate5 sampled peak was 539910575 bytes (about 515 MiB), below the 1 GiB limit.
Owned scratch and observed legacy temporary roots were removed. A separate later
read-only ps found zero matching workers. Raw command11 process_cleanup is missing
because the exception receipt omitted it; preserve null with that reason rather
than claiming a recorded per-command cleanup PASS. Whole-run scratch cleanup is
recorded. No raw gate5 receipt or earlier evidence was edited.

## Prepared supervision correction — INACTIVE

OWN read_process_table limits a single /bin/ps read to min(5 seconds, remaining
shared deadline), records duration/error/availability, does not retry and rejects
empty/malformed/duplicate/late tables. Kernel PID0/PGID0 rows are accepted for
inventory. An unavailable count stays null with reason, never zero.

OWN stop_group_bounded clamps observation and waits to the applicable total
cleanup deadline. It still terminates the live Popen session owned by the
controller if discovery fails; child signals require current matching identity,
stale tables cannot authorize signals and group0 is never signaled. Any missing
cleanup observation blocks PASS and carries partial evidence via CleanupIncomplete.

These helpers are not wired into outer/inner/cleanup execution. CLI/admission still
reject attempt6. The proposed integration must persist both work and cleanup errors,
use work1170 versus total1200 correctly, keep each new row within90 seconds including
cleanup, and throttle working process discovery to at most1Hz while retaining cap/
deadline checks every0.2s between reads. Frozen legacy scripts keep their2s reader;
system delays remain a residual failure risk.

Current prepared sources passed 101 focused NON-NATIVE tests, lint and typing on
56 source files. Fourteen new supervision controls include one real, owned benign
sleep process terminated while observation is fault-injected unavailable; its
cleanup remains conservatively incomplete rather than a fabricated PASS. These
controls do not execute native setup, verify_task, matrix or3.12 transport probes.

## Boundaries and next action

Times are wall seconds, sizes bytes; CPU time and instantaneous physical peak
remain null with reasons. Polling cannot establish a physical maximum; earlier
host-temporary coverage gaps stay documented. Gate3 genuinely exceeded its cap.
Missing raw JUnit is explicitly attributed to native cleanup.

Coverage remains local macOS/ARM/Python3.13.15/pytest9.1.1 with spaces/Unicode in
host/cwd paths and ASCII native sandbox paths. Full notebook/model/agent loop,
Linux/native3.12 and private scorer are untested. real_evaluations=NOT_RUN,
GPU readiness=false, scorer parity=null with reason. No hybrid efficacy claim.

[supervision-gate-plan.md](supervision-gate-plan.md) proposes integration and one
separately authorized gate6 under the same 1200s/1GiB/26native+6setup+2stdlib limits.
No gate6 is active or authorized. Complete gate and independent audit PASS with
zero findings are required before commit/push/update PR2 toward develop, no merge.
No GPU/model inference, Kaggle mutation/publication/submission, Discussion,
installation, model download or Docker/Colima/service change occurred. Phase1,
234 frozen files,11 external pins and historical runbook prefix remain intact.
