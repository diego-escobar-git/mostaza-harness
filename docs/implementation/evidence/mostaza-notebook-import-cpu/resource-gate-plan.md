# N-IMPORT-CPU-01 — host temporary retention and one gate, pending approval

Status: PROPOSED_NOT_AUTHORIZED. Ordinary CPU continuation, no SDD restart.
The gate3 allowance was consumed and ended on failure. It cannot be resumed,
overwritten or silently replayed even though no native calls began.

## Observed cause and prepared correction

Gate3 stopped in command1 after6.9295s. Sampled owned usage reached1405596992bytes,
exceeding1073741824bytes (1GiB). This is an OBSERVED cap failure; it is not merely
missing cap coverage. All owned scratch was removed; no native verification,
setup or3.12 transport probe began.

tests/unit/test_packaging.py:400–419 has five parametrized cases. Each copies all
resources (463659201bytes currently) to its own tmp_path. Default pytest retains
all those paths until session cleanup, so three concurrent retained copies alone
can exceed the cap. The assertions concern manifest rejection, not retaining data.
No frozen test or original resource was modified.

The installed pytest9.1.1 source _pytest/tmpdir.py:303–310 supports
tmp_path_retention_policy=failed. It deletes a passed test's tmp_path at that
fixture's teardown and retains failed-test data. The prepared helper adds exactly:

    PYTEST_ADDOPTS=-o tmp_path_retention_policy=failed

to a COPY of command1's environment ONLY. Commands2–12 receive the unchanged base
environment; no option is added to native verify_task's pytest command/environment.
Existing nonempty PYTEST_ADDOPTS blocks activation instead of silently combining
unknown test-selection flags. All test nodes, assertions, exit handling, compiler
checks and cap/cleanup checks remain mandatory. No plugin, conftest, dependency,
verifier, frozen validation script or old test is changed.

This helper is NOT yet wired into run(). CLI/admission still reject attempt4.
Two tiny own pytest suites proved that passed tmp data is removed and failed data
is retained; they used small text files, no real resources or native sandbox.
Four policy tests passed, with64 focused non-native tests passing in total,
lint/format and strict typing on56 source files passing. These checks do not prove
that the full suite now stays under cap. Deletion remains best-effort; the same
sampler and cleanup must fail the gate if it does not succeed.

## Requested implementation and one additional gate

Approval would authorize wiring host_test_environment(env, index) ONLY into the
outer controller's Popen of command1, with the applied override recorded in its
receipt. Add attempt4 admission only behind a separate approval pinned to this
proposal and all three prior receipts, preserving their statuses and counters.
Validate the admission and per-command wiring with non-native tests before launch.

Exactly ONE complete gate attempt4, serial, no retries and no native matrix outside
the runner (including audit). Entry point after approval/admission implementation:

~~~sh
.venv/bin/python scripts/run_notebook_import_cpu_gate.py --check --attempt 4
~~~

The exact twelve commands below are unchanged except output paths gate-4.
Only command1 gets the explicitly reviewed host retention environment above.

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
.tools/official/bin/python scripts/check_notebook_import_cpu.py --check --output results/notebook-import-cpu/gate-4/matrix
/Users/diego/.pyenv/versions/3.12.8/bin/python3.12 -I -S scripts/check_notebook_import_portability.py --check --receipt results/notebook-import-cpu/gate-4/matrix/summary.json --output results/notebook-import-cpu/gate-4/portability
~~~

Unchanged limits per gate:26 native verifications (11+9 regressions,6new),6setup
probes,2stdlib-only transport probes,1200s total including cleanup, stop work
by1170s/30s reserve,90s per row/probe,30s native commands/verification,1GiB owned
temporary/retained files sampled throughout. No cap increase, test exclusion,
automatic retry, original-file deletion or cleanup of unrelated paths.
A further failure ends this allowance; no additional execution is implied.

Current cumulative observations across gates1–3:41 native dispatch boundaries,
40 retained native results,1setup probe,0stdlib probes,431.6323s gate wall time.
Gate3 added0native calls. If approved, attempt4 would permit cumulative maxima of
67 native dispatches,7setup probes and2stdlib probes. Unused call headroom does not
extend the already consumed gate3 allowance.

## Acceptance and closure

Same approved acceptance: all twelve commands exit0, actual counts26/6/2 completed/
assessed, valid source/function witnesses in both phases, generic controls, both
transport probes, immutable originals, scoped cleanup and independent audit PASS
with zero findings. A local unit/control result is never a substituted real run.

Only after that PASS: commit/push/update PR2 toward develop, no merge.
No GPU/model call, Kaggle session/API/browser mutation, notebook publication,
submission, Discussion, Linux service start, download/install or verifier change.
Private scorer parity, full Linux/native3.12 execution and real Kaggle evaluation
remain untested; GPU readiness stays false. Preserve the dirty closed plan,
phase1 worktree, all prior evidence and the exact three failed receipts.
