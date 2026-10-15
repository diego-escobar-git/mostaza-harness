# N-IMPORT-CPU-01 — one additional corrected gate, pending approval

Status: PROPOSED, NOT AUTHORIZED. This does not replace the original plan/approval,
reopen SDD, reset either consumed attempt or authorize any execution.

The original [plan](plan-for-approval.md) permits at most two gate attempts.
Both have been consumed and retained. User approval is required for another.
No commit/push/PR update is permitted before a successful complete corrected gate
and final independent audit PASS with zero findings.

## Concrete correction prepared

The second gate passed commands1–10, then rejected the first owned generic setup
receipt because inherited pytest-only bound() required every sys.path entry to be
nonempty. The setup ran with python -c, whose first empty entry means its actual
current working directory. Its source/module/function witness and subsequent
negative native verification were present; this was an assessment error.

The new setup_binding() interprets ONLY the first empty -c entry as the separately
witnessed canonical cwd for checking. It preserves the raw ordered sys.path and
all native source/hash/function/process checks. It does not change sys.path,
PYTHONPATH, loader, command, source package, native verifier or environment.
Malformed/nonstring/misplaced empty entries and wrong source/code still reject.
The setup diagnostic now declares actual_native_setup_import_cpu, not the
historical reused pytest scope label. The old gate2 receipt remains byte-exact and
is not rewritten or retrospectively marked as passing.

The audit also identified incomplete temporary-file coverage of the disk cap.
The prepared supervisor sets child TMPDIR to its owned, sampled scratch root
and the matrix verifies tempfile resolves there. Native and frozen legacy files
remain unchanged. Historical sampled peaks do not cover those formerly external
temporaries; no observed overrun is asserted.

Prepared correction has53 focused NON-NATIVE tests passing; format/lint and strict
typing on56 source files pass. Independent review is recorded in audit.json.
No additional native verification/setup/stdlib transport probe has been launched.

## Requested additional allowance

Exactly ONE additional full gate (attempt3), with the same twelve commands and
acceptance criteria. Only commands11–12 output paths change to gate-3.
Before execution, an approved implementation would add choice3 to the runner only
behind a separately stored approval tied to this document's SHA256, require both
prior receipts and the prepared correction record, and retain maximum ordinary
attempts1–2 as historical facts. No reset, overwrite or automatic replay.
Focused non-native gate-admission checks must pass before this extra execution.

Exact entry point AFTER that approval and admission implementation:

~~~sh
.venv/bin/python scripts/run_notebook_import_cpu_gate.py --check --attempt 3
~~~

Exact commands, serial and once:

~~~sh
bash scripts/validate.sh
.venv/bin/python scripts/check_phase2.py --check --cohort experiments/cohort.json
.venv/bin/python scripts/prepare_startup_phase2.py --check
.tools/official/bin/python scripts/check_startup_configuration.py
.venv/bin/python docs/implementation/evidence/mostaza-phase2-startup-run/recompute.py --check
.venv/bin/python scripts/check_context_verification.py --check
.venv/bin/python scripts/check_pcv01.py --check
.venv/bin/python scripts/check_pcv01_scorer_contract.py --check
.tools/official/bin/python scripts/check_verify_task_cpu.py --check
.tools/official/bin/python scripts/check_requests_import_cpu.py --check
.tools/official/bin/python scripts/check_notebook_import_cpu.py --check --output results/notebook-import-cpu/gate-3/matrix
/Users/diego/.pyenv/versions/3.12.8/bin/python3.12 -I -S scripts/check_notebook_import_portability.py --check --receipt results/notebook-import-cpu/gate-3/matrix/summary.json --output results/notebook-import-cpu/gate-3/portability
~~~

Maximum26 native verify_task invocations (20regression+6new),6setup probes,
2stdlib-only portability probes, no case/command retries.1200s TOTAL including
cleanup; stop owned work by1170s, reserve30s;90s per row/probe,30s native commands/
verification;1GiB additional owned artifacts. Same strict descendant supervision,
source freezes, exclusive output paths and cleanup. No matrices outside the gate,
including auditor reruns. Failure ends the allowance; no further attempt implied.

The first two attempts used41 native dispatch boundaries,40 retained native
results,1setup probe and0stdlib probes over424.70s gate wall time. With this
additional allowance, cumulative maxima would be67 native calls,7setup probes,
2stdlib probes. This expressly exceeds the original two-attempt limit and its
52-call maximum; unused original headroom is not automatic authorization.

## Unchanged boundaries and closure

Preserve original evidence, the dirty closed plan and phase1 worktree. No new
Requests solution or original Task reference/test fields in agent payloads.
No GPU/model call, Kaggle mutation/publication/submission, Discussion, environment
installation, Docker/Colima start, Linux-runtime claim or verifier change.
The new notebook remains blocked, GPU/network disabled and readiness false.

After all twelve commands and independent final audit PASS with zero findings,
commit/push/update existing PR2 toward develop; no merge. If the gate fails,
preserve partial records, report the blocker and stop. Linux/native3.12/private
scorer parity and real Kaggle evaluation remain untested.
