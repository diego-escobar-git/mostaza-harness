# V-CPU-01 CPU implementation — blocked final gate

Status: BLOCKED_FINAL_GATE_BUDGET_EXHAUSTED. Not complete; no audit PASS, commit,
push or PR2 update. No GPU, Kaggle action, Discussion or verifier change.

## Implemented

New approved specification and host-only fixture driver call the actual pinned
swegemma0.2.11 verify_task with the real SubprocessManager. Eight owned controls
and three Requests cases are defined, with original snapshot/retained-agent-patch
pins, required nodes, native test protection/pytest/JUnit/cleanup, own test-body
module/function/process witnesses, CPU-only classification and descendant-aware
watchdog. No import-path repair, origin plugin or original Task solution/test_patch.
The runbook links the exact protocol and its limitations.

## Actual validation and partial evidence

- Attempt1: eight prior commands passed; ninth failed at V07 due to my classifier
  reading `error` instead of native serialization `error_message`. Seven native
  result files exist; six were accepted before the classifier crash.
- Attempt2: eight prior commands passed again (306 unit,43 integration,42 typed
  source files; build/compiler and old evidence checks included). Ninth failed
  during V05 cleanup because my disk meter stat'ed a temporary file after native
  deletion. Five native result files exist; four were accepted before interruption.
- Both failures are in the new host tooling. Native V07 correctly returned exit0,
  resolved=false and the missing-JUnit diagnostic. These are real CPU outputs,
  not simulated native outcomes. The directory inventories retain the failures.
- The partial controls show V01 faulty baseline FAIL; V02 generic correct patch
  PASS; V03 wrong patch FAIL; V04 src/root shadow rejected. Attempt1 also shows
  V05 skipped required test rejected and V06 no tests rejected. None establishes
  the complete new gate. V08 and R00/R01/R02 were never invoked.
- Total native result files:12 across the two interrupted attempts. This is not
  eleven completed/accepted cases in a single matrix. Historical summaries named
  accepted cases `invocations_completed`; the corrected controller now separates
  invocations_started, native_results_present and invocations_assessed.
- Original raw summaries/logs remain unchanged. No historical benchmark outcomes
  are reclassified. No new Requests semantics/import conclusion can be drawn.

Gate attempt wall time: 96.20s and
81.09s, each below the approved1200s ceiling.
Retained new raw evidence: 442274bytes. No sandbox directories
remain under either run. All recorded immutable-input pins were rechecked after
interruption and still match, including the pre-existing dirty closed SDD plan.

## Corrections and independent audit

Corrected native error alias, atomic V07 write, exact receipt multiplicity,
required runtime witnesses, separate native process-group supervision and the
cleanup-sensitive disk meter. The disk meter uses one lstat per entry, tolerates
only disappeared files/directories, avoids following links and propagates other
I/O errors. Focused checks after corrections: Ruff PASS, strict mypy on three new
source files PASS,23 targeted unit/integration tests PASS. No native rerun followed.
The independent auditor reproduced23 targeted tests and Ruff, reviewed the race
repair as sound, and returned BLOCKED_FINAL_GATE. See audit.json. This is not a
full gate PASS on the final corrected source.

## Exact pending action and budget decision

The approved proposal allows at most two complete gate attempts and states:
"if more are needed, report the blocker and seek a revised budget." Both attempts
have been consumed. A third native matrix or final full gate is currently
unauthorized. The implementation and corrected tooling are reviewable locally;
publication remains conditional on the originally approved full gate/audit PASS.

Request one additional attempt of the SAME nine commands in plan-for-approval.md,
maximum20min total,11 serial native invocations,30s native command/verification
timeout,90s per-case watchdog,1GiB additional local artifact ceiling, no automatic
retry. No scope expansion, GPU, model, network download, Kaggle action, Discussion,
verifier/setup/path change or merge. Stop and report if that attempt fails.
After full PASS, obtain final independent audit/corrections within existing scope
and only then commit/push/update PR2 toward develop under existing authorization.

Keep original pytest/Python/environment differences explicit. CPU PASS would only
certify local diagnostics; private scorer equality and GPU readiness stay unknown/
blocked. No new import/setup repair or GPU batch is authorized.
