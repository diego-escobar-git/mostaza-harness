# N-IMPORT-CPU-01 — notebook import integration validated on CPU

Status: CPU_GATE_PASS. Independent audit verdict is recorded in audit.json;
commit/push/update PR2 requires its PASS with zero findings. This is an ordinary
CPU follow-up; the original closed SDD continuity and its pre-existing dirty bytes
are preserved. No merge, GPU, Kaggle mutation or Discussion is authorized here.

## Implemented behavior

The fresh guarded GPU/network-disabled notebook integrates the common Requests
layout through the OFFICIAL snapshot resolver: unchanged standalone original
archives, base_snapshots input plus the exact requests -> src/requests symlink
patch, and untouched standalone FastAPI/Rich archives. E0-C8K-L1/E1-C8K-L1 are new
host identities referencing byte-identical original C8K agent ZIPs. Model, prompt,
sampling, budget, cohort, repair policy and native verifier remain unchanged.

A versioned host envelope distinguishes parent binding from actual derived inputs;
validate the actual view before Evaluator construction and each dispatch. The same
resolved tuple feeds pre-model setup and direct native verify_task. Reject resolver
fallbacks, unsafe aliases, extra/changed inputs, source/function drift and stale
witnesses. The host helper is outside agent closures. Own diagnostic tests and
retained replay patches never enter agent prompts/payloads.

The host source proof always runs standard tarfile.data_filter and preserves ONLY
safe trailing separators of tracked symbolic links whose spellings resolve to the
same in-root target. This avoids the documented Requests certificate-link
normalization that caused gate4, while retaining Git clean-index/worktree and exact
one-link-delta checks. No native extraction/filter/verification code was modified.
Original/derived tree, archive/component hashes and native source hashes are bound.

## Final complete gate

The separately approved attempt6 passed all twelve commands in 211.3903 wall
seconds, below1200 seconds. The receipt's duration includes counters/inventory up
to the final JSON write; export completion is separately checked against the same
1200-second limit. Its polled owned-artifact peak was556434407 bytes (about531MiB),
below1073741824 bytes. It includes retained prior CPU outputs and owned TMPDIR.

Validation included378unit tests,119integration tests, Ruff format/lint, strict
mypy on56source files, package build, official compiler validation and frozen
historical evidence checks. The ten historical commands passed, including their
11+9 native regressions. The new pipeline completed/assessed6native rows,6separate
setup probes and2stdlib Python3.12.8 transport probes. Total per gate:26native,
6setup,2stdlib, with no retries or auditor reruns.

| New input | Setup/verification workspace binding | Own diagnostic outcome |
| --- | --- | --- |
| Faulty generic L01 | Both accepted | Assertion failed; unresolved, exit1 |
| Correct generic L02 | Both accepted | Passed; resolved, exit0 |
| Wrong generic L03 | Both accepted | Assertion failed; unresolved, exit1 |
| Requests baseline R00 | Both accepted | Origin/missing/valid pass; empty machine/default fail, exit1 |
| Retained E0-B180 patch R01 | Both accepted | Four checks pass; missing-match TypeError, exit1 |
| Retained E1-B180 patch R02 | Both accepted | All five own checks pass, exit0 |

Requests witnesses identify actual snapshot workspace/src/requests sources in both
phases, with raw/canonical paths, module bytes, loaded-function fingerprint and
actual PID/runtime. Setup and pytest have separate fresh witnesses and coverage
labels. Native baseline commits contain the alias with no working delta leakage.
R01/R02 use the existing retained agent patches, not new model generations.
These own tests diagnose import binding and behavior; they are not official task
scores, hidden tests or proof of private scorer equivalence/hybrid effectiveness.

Python3.12.8 probes used -I -S and standard-library-only transport. They verified
layout and product hashes at relocated space/Unicode paths plus a dependency-free
generic import. Requests was NOT imported and native verify_task was NOT executed
in3.12. The native setup/verification matrix ran macOS/ARM/Python3.13.15/pytest9.1.1.
Host/cwd relocation includes spaces/Unicode; native sandbox paths are ASCII.

## Bounded supervision and repairs

Whole-gate work stops by1170s with30s cleanup reserve. Each new row includes
preparation, setup/verification, assessment, export and fixture cleanup within90s,
reserving30s for cleanup after at most60s process work. Native commands retain30s
limits. Cap/deadline checks run every0.2s between reads; process discovery is limited
to once per second per own controller. Reads use min(5s, remaining shared budget),
with no automatic retry. Frozen legacy inner scripts retain their2s reads.

Unavailable/malformed/late process snapshots fail rather than imply absence.
Cleanup still terminates its owned live Popen if discovery fails; child signals
require matching current PID/PGID/command identity, never stale tables or group0.
Use total1200/row90 cleanup deadlines separately from work deadlines. Preserve work,
cleanup and persistence errors plus partial receipts. Any unverifiable cleanup
blocks PASS. Exit verification covers observed owned groups, not a continuous
physical view of every process between samples.

Gate6 retained289 own-controller observations (235work/54cleanup); all were available,
maximum read duration0.145007s. This excludes frozen legacy inner-observer telemetry.
The1Hz policy was tested/recorded; actual empirical frequency is null because read
start timestamps were not retained. Every recorded process cleanup completed;
scoped temporary roots were removed. There were no observed signal/observation
errors. Original phase1 worktree,234frozen files,11external pins, historic runbook
prefix and prior raw outputs remain intact.

Preflight independent audit found AUD006–009 before the gate: initial receipt I/O
could bypass cleanup; full row/closeout deadlines omitted later export work; a
root PID could be reused during ps. Corrections include protected persistence,
conservative partial error evidence, post-read Popen revalidation and final deadline
checks including assessment/fixture cleanup/counts/export.120focused non-native
checks passed before the gate. The final gate exercised all current tests.

## Preserved attempt history and measurement limits

| Gate | Wall seconds | Outcome | Native starts/results | Setup | Stdlib |
| --- | ---: | --- | --- | ---: | ---: |
| 1 |253.4993|Commands1–9 passed; interruption10 PermissionError|20/19|0|0|
| 2 |171.2035|Commands1–10 passed; setup receipt assessment stopped11|21/21|1|0|
| 3 |6.9295|Command1 observed artifact cap exceeded|0/0|0|0|
| 4 |144.3997|Commands1–10+generic3 passed; host source proof stopped R00|23/23|3|0|
| 5 |215.9226|Commands1–10+generic3+R00 passed; outer ps2s timeout|24/24|4|0|
| 6 |211.3903|Complete twelve-command gate passed|26/26|6|2|

All six separate authorizations are consumed. Cumulative114native starts,
113retained native results,14setup,2stdlib and1003.3448gate wall seconds. These are
CPU diagnostic calls, including repeated regressions, not Kaggle evaluations or
process-CPU time. Each failed receipt is unchanged; no partial attempt is relabeled
PASS. Historical causes retain their uncertainty: gate1 PermissionError root cause
and gate5 OS delay remain unknown; gate3 genuinely exceeded1GiB. Earlier host-temp
coverage gaps and gate5 missing final summary/command cleanup receipt remain in
checkpointed reports with null/reasons. The snapshots themselves were not mutated.

Wall seconds and bytes are explicit units. Process CPU time and instantaneous
physical peak remain null with reasons; polled size cannot prove a physical peak.
Per-row worker duration spans setup+native verification, excludes host preparation/
fixture cleanup, and is distinguished from the separately enforced90s acceptance.
Raw JUnit is consumed/removed natively, explicitly null with reason.

## Reproduction and remaining boundary

Exact approved commands/limits are in supervision-gate-plan.md and approval pins
in supervision-gate-approval.json. The executed entry point was:

~~~sh
.venv/bin/python scripts/run_notebook_import_cpu_gate.py --check --attempt 6
~~~

The gate guard is bound to this APPROVED EXISTING WORKTREE, including the pinned
pre-existing dirty closed-plan bytes, which are deliberately excluded from this
commit. A clean clone does not reproduce that authorization snapshot automatically.
It also needs the separately acquired/pinned ignored resources and official runtime.
A new checkout/run requires fresh approved workspace inputs and output scope; do
not edit historical pins or copy unpublished plan changes merely to replay a gate.
The disabled notebook's host payload does not depend on that closed-plan file.

It is a consumed exclusive output path, NOT permission to rerun. New native runs
require fresh scope/budget approval; no automatic attempt7 exists. Reconstructing
and checking the disabled notebook alone is non-evaluating:

~~~sh
.venv/bin/python scripts/prepare_notebook_import_cpu.py --check
~~~

cpu-results.json stores outcomes/witnesses/coverage; gate-attempts.json preserves
all receipts; raw-inventory.json hashes ignored local raw files; source-inventory.json
pins current source. Gate6's own raw source inventory matches that code. Checkpoints
preserve earlier blocked evidence. audit.json records the independent final review.
User authorized commit/push/update existing PR2 toward develop after PASS, no merge;
the unrelated dirty closed plan must be excluded from staging.

This validates host notebook-payload preparation, native setup/import/verification
and bounded transport on CPU. The full notebook/model/agent loop has not executed.
Linux/native Python3.12, private scorer parity and a real Kaggle run of this new
candidate remain untested; readiness stays false, parity null with reason and
real_evaluations=NOT_RUN. No new GPU/model call, Kaggle session mutation/publication/
submission, Discussion, install/model download or Docker/Colima/service change.
Historical GPU outcomes and all original experiments remain unchanged.
