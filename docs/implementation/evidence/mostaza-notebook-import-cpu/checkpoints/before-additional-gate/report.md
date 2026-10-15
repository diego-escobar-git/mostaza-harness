# N-IMPORT-CPU-01 — implementation prepared, gate blocked

Status: BLOCKED_CPU_GATE_BUDGET_EXHAUSTED. No complete gate PASS, no final
development completion, no commit/push/PR update for this follow-up.
PR2 remains at bcec689aadc9be0801de6b1c7e560d776e17299e toward develop.

## Implemented

A fresh mostaza-notebook-import-cpu.ipynb, GPU/network disabled and launch guard
unchanged, embeds the minimal host layout adapter and a pinned layout policy.
E0-C8K-L1/E1-C8K-L1 host experiment manifests reference unchanged C8K agent ZIPs.
The official resolver supplies a common base-plus-delta Requests input to both
agent preparation and verification. FastAPI/Rich retain standalone input policy.
No retrieval, model, sampling, budget, repair or cohort change is combined here.

The host envelope distinguishes parent_binding from actual_execution and validates
both source and derived component inventories before evaluator/dispatch. The old
runner and historical notebooks/manifests remain byte-identical. CPU diagnostics,
retained patches and behavioral expectations are excluded from production payloads.
The implementation and precise acceptance remain in the approved original plan.

## Executed evidence, without extrapolation

| Attempt | Gate wall seconds | Outcome | Native dispatches / results | Setup probes | Stdlib probes |
| --- | ---: | --- | --- | ---: | ---: |
|1|253.4993|Commands1–9 PASS; interrupted during10 with PermissionError|20 /19|0|0|
|2|171.2035|Commands1–10 PASS; command11 stopped assessing N-L01|21 /21|1|0|

Total:41 native dispatch boundaries,40 retained native results,1setup probe and
0stdlib transport probes. Total gate wall time424.7028s. No automatic case retries
and no native/auditor reruns outside these two gates. Both allowed attempts are
consumed even though neither completed all twelve commands. Raw attempts and
results are immutable; do not label them PASS after offline analysis.

Attempt2 included362 unit tests,59 integration tests, strict typing on56 source
files, lint/format, package build, official compiler and historical evidence checks.
Its unchanged eleven-case V-CPU and nine-case R-IMPORT matrices passed.
Those Requests regressions again establish the already known local alias remedy;
they do not establish that Requests ran through the NEW notebook pipeline.

The new N-L01 generic faulty-baseline row completed setup and direct unmodified
native verify_task. Its actual setup import and native pytest witnesses point at
the same expected source content in two distinct sandboxes. Native verification
reached the intended assertion (evaluate()==0 rather than1), exit1/resolved=false.
That is an owned negative control, not an official competition result.
The row was NOT accepted by the controller because of the assessment issue below.
N-L02/N-L03/N-R00/N-R01/N-R02 and both Python3.12 probes were NOT_RUN.
Do not claim full notebook portability, Requests notebook verification or3.12
runtime/import compatibility from this partial matrix.

## Failures and prepared repairs

1. Attempt1's outer controller reported PermissionError without preserving its
   originating traceback; the active regression controller was interrupted.
   /bin/ps is setuid root, consistent with a transient group-signaling race, but
   the actual cause is NOT conclusively established. The new own supervisor
   records signal failures, continues bounded cleanup and verifies every observed
   matching PID/PGID/command exited. Persistent survivors block PASS. It never
   rediscovers a finished Popen root. Simulated EPERM/survivor/PID-reuse tests pass.
   Attempt2 reports no signal errors or survivors. Native/frozen legacy code unchanged.

2. Setup uses python -c. Python legitimately places an empty first sys.path entry,
   meaning its current working directory. The inherited pytest binding predicate
   incorrectly rejected that actual receipt. See the
   [official sys.path documentation](https://docs.python.org/3.13/library/sys.html#sys.path).
   The post-gate correction interprets ONLY that first entry as the separately
   witnessed cwd in a validation COPY, preserving the raw list and process.
   All path/hash/loaded-function/process checks remain strict. Future setup receipts
   use actual_native_setup_import_cpu; the old copied pytest coverage wording was
   inaccurate for a plain setup probe and remains unchanged in historical evidence.
   No PYTHONPATH/sys.path/.pth/loader/native-environment repair was made.

3. Independent audit found the disk sampler missed host tempfile/mktemp directories.
   No actual overrun was established. Historical sampled maxima324568386bytes and
   293128318bytes cover only the declared scratch/results roots, NOT every temporary
   byte. They cannot establish the complete1GiB cap. The prepared supervisor now
   sets child TMPDIR to owned scratch/host-tmp; the matrix verifies that Python's
   tempfile resolves there. Build and history-validation temporaries then fall
   within sampling/cleanup. Native code and old protocols remain unchanged.

After those repairs:53 focused NON-NATIVE tests PASS, lint/format PASS and strict
typing on56 source files PASS. This is not a corrected full gate receipt.
No native/setup/stdlib probe ran after attempt2. The generated notebook and closures
remain reproducible. See audit.json for independent review and unresolved gate.

## Metrics and limits

Times above are wall seconds; process CPU time is null (not measured). File sizes
and sampled usage are bytes. Physical instantaneous peak is null (polling does not
establish it); complete historical artifact-cap coverage is null because of the
identified host-temp gap. Raw JUnit is null because native cleanup consumes/removes
it; retained native output and own actual-process witnesses delimit test coverage.
Attempt1 lost one result and its assessment summary; keep missing metrics null
with reasons in supplemental telemetry, never fabricate a completed result.

Coverage: owned generic setup/python process plus owned native pytest, macOS/ARM,
Python3.13.15/pytest9.1.1. Host payload/cwd use relocated space/Unicode paths;
native sandbox paths are ASCII. No native agent loop, full notebook, model,
Linux runtime or private Kaggle scorer was executed. Private scorer parity=null,
ready_for_gpu=false, real_evaluations=NOT_RUN. No new hybrid efficacy conclusion.

## Pending decision and closure

The [additional gate proposal](additional-gate-plan.md) requests ONE fresh full
attempt3, max26 native verifications,6setup and2stdlib probes,1200s total with30s
cleanup reserve,1GiB owned artifacts and no retries. It is NOT authorized or enabled.
Original attempts/counters remain intact. The proposed runner admission would
require separate approval tied to that proposal's SHA256.

Only after a complete corrected gate and independent audit PASS with zero findings
may commit/push/update PR2 proceed. No merge. Preserve the pre-existing dirty closed
plan and phase1 worktree. This follow-up performed no GPU/model inference, Kaggle
session/API/browser mutation, submission, Discussion, model download, installation
or Docker/Colima change.
