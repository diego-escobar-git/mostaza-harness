# N-IMPORT-CPU-01 — process observation and one gate, pending approval

Status: PROPOSED_NOT_AUTHORIZED. Ordinary CPU continuation; do not reopen SDD.
All five gate allowances are consumed. CLI/admission still reject attempt6.

## Observations and prepared correction

Gate5 passed commands1–10 and assessed N-L01/N-L02/N-L03/N-R00, including separate
setup and native pytest workspace imports. R00's own origin check passed; two
empty-netrc behavior controls failed as expected for the baseline. R01 preparation
was dispatched but no setup/native-start marker exists; R02 and both3.12 transport
probes did not run. Counts:24native calls,4setup,0stdlib,215.9226wall seconds and
539910575polled bytes. Owned scratch cleanup completed and a later read-only ps
found0 matching workers. Raw command11 cleanup outcome is null: its exception
receipt omitted that field, so do not reconstruct it as an observed success.

The outer monitor raised TimeoutExpired from the frozen process_table's2s ps
query. The cause of the OS delay is unknown. Outer and inner controllers currently
query the full process table on every0.2s iteration (nominally10queries/s together;
actual rate not measured). No native/test/model timeout caused this interruption.

Prepared OWN read_process_table uses /bin/ps, timeout=min(5s, remaining shared
budget), no automatic retry, and records duration/error/availability. Empty,
malformed, duplicate or late tables fail; unavailable counts stay null with a
reason. PID0/PGID0 kernel rows are accepted for inventory, never signaled.

Prepared stop_group_bounded uses that reader, clamps waits to the supplied total
cleanup deadline, and still signals the live Popen session owned by the controller
if discovery fails. Child-group signals require current PID/PGID/command identity;
stale tables cannot authorize signals. It rediscovers descendants only from live
matching known identities. Any unavailable cleanup observation prevents PASS and
returns truthful partial evidence via CleanupIncomplete (survivors=null with a
reason). Fresh observations at cleanup phases are bounded checks, not case retries.
No mutation of native/frozen code or broader process ownership is permitted.

Both helpers remain INACTIVE: the outer gate, inner matrix and current stop_group
still use the frozen2s reader.101 focused NON-NATIVE tests, lint and typing56files
PASS. Tests include fault injection and terminating one own benign sleep process
while ps is unavailable, with incomplete exit proof retained as failure. No new
native/setup/stdlib transport evaluation ran after gate5.

## Implementation authorized by a future approval

1. Wire only the own outer gate and own new-matrix controller to the prepared
   reader. Working discovery is at most once per second per controller; artifact
   cap and deadline checks continue every0.2s between reads. A timeout/error aborts
   work immediately; no retry of ps or a case. Record all sampling durations,
   availability/errors and sampling policy. Do not claim a physical peak or exact
   process state between observations.
2. Reads consume the existing work budget: outer stops work by1170s. Each new row
   retains90s INCLUDING cleanup, reserving30s within it (work stops by60s).
   Matrix teardown must use the row total deadline and never exceed global1200s;
   outer cleanup uses the global1200s deadline, separately from1170s work stop.
   Reads/waits must always clamp to the applicable remaining deadline.
3. Use stop_group_bounded for own controllers, preserving termination of the owned
   Popen even on discovery error. Persist partial cleanup evidence in failed-step
   receipts before raising, including CleanupIncomplete.receipt and BOTH the original
   work error and cleanup error if both occur. Never infer absence/cleanup PASS
   from missing telemetry.
4. Leave all ten historical validation commands/scripts, native verifier, command,
   dependencies and native environments unchanged. Their frozen2s monitoring may
   still fail under system delays; document that residual risk. No guarantee of a
   successful gate or exact physical teardown time follows from a longer read cap.
5. Add attempt6 admission only behind a separate approval pinned to this proposal,
   supervision-repair.json and all five consumed receipts. Preserve all prior
   counters/paths. Validate wiring, throttling, deadlines, exception receipts and
   cleanup with mocked/own benign-process tests before launch; independent review.

## Exactly one proposed gate and limits

After approval/integration, the single entry point would be:

~~~sh
.venv/bin/python scripts/run_notebook_import_cpu_gate.py --check --attempt 6
~~~

Exactly the same twelve commands; only new output paths become gate-6:

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
.tools/official/bin/python scripts/check_notebook_import_cpu.py --check --output results/notebook-import-cpu/gate-6/matrix
/Users/diego/.pyenv/versions/3.12.8/bin/python3.12 -I -S scripts/check_notebook_import_portability.py --check --receipt results/notebook-import-cpu/gate-6/matrix/summary.json --output results/notebook-import-cpu/gate-6/portability
~~~

Host retention override remains exclusive to command1. Same caps:1200s total,
1170s work stop/30s cleanup reserve;1GiB polled owned temporary/retained artifacts
including previous results;26native verifications (11+9+6),6setup,2stdlib3.12 probes;
90s per new row/probe including cleanup,30s native commands/verification, serial,
no automatic retries. No extra native matrix by auditor or outside runner.
A failure consumes this allowance; it never authorizes attempt7.

Cumulative gates1–5:88native starts,87retained native results,8setup,0stdlib and
791.9546wall seconds. Gate6, if approved, allows cumulative maxima114native starts,
14setup and2stdlib probes. Unused gate5 headroom does not authorize another run.

Acceptance:12commands exit0;26/6/2started/completed/assessed; correct source and
function witnesses in both phases, generic controls, Requests rows and3.12 transport;
immutable originals, scoped verified cleanup, full provenance and independent audit
PASS with zero findings. Only then commit/push/update PR2 toward develop; no merge.
No GPU/model call, Kaggle mutation/publication/submission, Discussion, install,
service start or verifier change. Readiness remains false; no private scorer,
full Linux/native3.12 or hybrid-efficacy claim. Preserve phase1 and the dirty closed
plan. The notebook remains GPU/network disabled and no model/agent loop is run.
