# Native verify_task CPU end-to-end — proposal V-CPU-01

Status: PROPOSED; implementation and execution await approval. Prepared 2026-10-14.
This is an ordinary follow-up to the closed SDD delivery, not an SDD restart.
Only this proposal and prerequisites.json are new. No verify_task invocation,
new test implementation, verifier change or remote compute was performed here.

## Objective and boundary

Exercise the complete pinned swegemma 0.2.11 verify_task path using the actual
SubprocessManager on CPU. Establish that our local diagnostic protocol credits
only passing, required tests against the intended workspace product, and diagnose
Requests using the retained agent-generated patches. Keep the native result,
import qualification and semantic test results separate.

This establishes local development-backend behavior. It does not establish
historical Kaggle imports, private scorer equivalence, benchmark task resolution,
future GPU-environment binding, P-CV-01 activation permission or hybrid retrieval
success. No organizer reply or Discussion publication is needed for this bounded
local experiment. These CPU results cannot clear real-evaluation readiness.

## Verified prerequisites and source identity

The worktree is /Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness,
branch sdd/mostaza-phase2-budget-retrieval, inspected HEAD
c54946237ee9921f5247be75eb888864da93333a. PR2 targets develop. The existing dirty
closed plan must remain byte-identical and unstaged; its SHA is in prerequisites.json.
The phase1 worktree is read-only and outside this change.

prerequisites.json pins the cached wheel, installed native sources, actual Requests
archive and two B180 agent_patch inputs. The archive has 193 members, 39,052,005
unpacked bytes and two links. Before native extraction, validate member paths,
link targets and types against an owned disposable extraction root; reject escapes,
devices and excess size. Do not rewrite the official archive to remove links.

Requests archive SHA256 is
42dc3d360f842a5c7a66d0008ac05447fcd807dc33ee8cc18d2f2d4876283106,
37,402,474 bytes. The older cohort SHA starts 4a293476 and is not the downloaded
archive identity. Existing B180 acquisition evidence already records this archive
and base-tree correspondence: exported HEAD 443f0b73558781b7dac0e304ad268a30ee35aaeb,
tree 683d44befe0d3519469011c35e46f332eebbc010, original base
1b40fdd004bfc8ba5301bcf8a6908264e9b6b877. Recheck the tree locally before testing;
never alter the cohort or pretend the compressed files have equal hashes.

The official local interpreter is Python 3.13.15, pytest 9.1.1, swegemma 0.2.11,
adk-submission 0.2.13. Requests 2.34.2 is installed in its site-packages, so a competing
installed distribution is plausible; metadata alone does not prove its selection.
Record effective interpreter, dependencies, platform and pytest per process.
Historical Kaggle host Python 3.12.13 / pytest 8.4.2 differ. Existing isolated
P-CV-01 pytest-version controls remain evidence only for their own protocol; this
new matrix does not claim full verify_task equivalence on those historical versions.
No dependency upgrade, extra interpreter, image, VM or network download is included.

## Proposed specification delta and files

After approval, add docs/specs/verify-task-cpu.md with the contract below and an
append-only clarification in the Kaggle runbook. Do not reopen the closed SDD plan.
Proposed implementation boundaries:

- scripts/verify_task_cpu_fixtures.py: disposable fixture/Task construction and
  direct native calls, independent test sources, raw CPU evidence collection.
- src/mostaza/evaluation/verify_task_cpu.py: bounded inputs, receipt validation,
  result classification and immutable-input checks; no alternate verifier.
- scripts/check_verify_task_cpu.py: exact --check entry point below. It executes
  the 11-case matrix, validates its evidence and writes a compact result summary.
- tests/unit/test_verify_task_cpu.py and tests/integration/test_verify_task_cpu_contract.py:
  meaningful receipt, classification, source-integrity and scope checks. They do
  not repeat the entire matrix; the dedicated gate command runs it once.
- docs/implementation/evidence/mostaza-verify-task-cpu/: approval, report, compact
  inventories, command receipts and independent audit. Large/raw outputs remain
  ignored under results/verify-task-cpu/<run-id>/ with hashes and retention paths.

No edits to experiments, manifests, original evidence, notebooks, native installed
files, wheel, setup, scorer, locks or agent prompts. Keep the existing
binding_readiness helper and its real-evaluation block intact. A new CPU-only
assessment must not reinterpret its editable-install requirement or unknown fields.

## Execution protocol

1. Fail closed on missing/changed pins, unavailable dependencies, unsafe archive,
   wrong Requests tree, missing agent patches or insufficient local resource budget.
   Use existing local caches; do not fetch replacements silently.
2. Build small owned fixture archives and actual 40-hex baseline Git commits. Create
   fresh Task objects explicitly: patch="", our own test_patch and required nodes.
   Avoid the native special-case repo test/mock_repo + base_commit 123456. Do not
   hydrate an original Task or read its solution/hidden-test fields. Historical
   result JSON is allowlisted to agent_patch and its provenance.
3. Call the imported, unmodified native verify_task with an actual SubprocessManager,
   sandbox="subprocess", default inherited-site-packages behavior, fast_path=True,
   concurrency one, verification timeout 30 seconds and command timeout 30 seconds.
   Set config.wheels_dir to an owned empty directory to prevent automatic bulk
   wheelhouse discovery/copying; inherited cached packages remain unchanged.
   No subclass, monkeypatch, fake manager or substituted helper. Pass a real monotonic
   start_time so returned durations are meaningful. No model server or agent runner.
4. Native code must perform extraction, bootstrap, baseline, protected-path handling,
   patch application, test reset/application, its fixed pytest command, JUnit
   validation and cleanup. Native subprocess setup intentionally skips editable
   installation/dependency setup. Do not compensate with pip install, a path shim,
   .pth injection, altered PYTHONPATH, conftest repair, plugin loading or changed
   command. Our own diagnostic test_patch is the only new pytest test content.
5. Ordinary diagnostic test bodies capture import witnesses in their actual pytest
   process, before behavioral assertions. Store them atomically in the run's owned
   host evidence directory outside the sandbox that native finally removes. Capture
   TaskResult/stdout through normal returned data; do not intercept native execution.
   Preserve collection/setup errors and missing-witness reasons. A receipt must be
   independently validated, not trusted simply because its JSON claims a match.
6. Check manager state and owned sandbox directories after each native cleanup.
   The local watchdog may terminate only this run's child process group, with a
   cleanup attempt and explicit incomplete status. Never touch Kaggle sessions.

## Exact CPU matrix: 11 native invocations, serial, no automatic retries

Each fixture has an independent diagnostic test_patch and explicit required test
nodes. A negative expected result is a successful control only when its intended
failure condition is evidenced; unrelated setup/import failure does not qualify.

| ID | Input/control | Required observation |
| --- | --- | --- |
| V01 | Small flat product, faulty baseline, no agent patch | Native resolved=false; genuine required assertion fails; witness binds to intended baseline workspace file. |
| V02 | Same product/tests, generic correct agent patch | Native resolved=true, exit 0, required tests pass under native JUnit checks; patched workspace and function identities match. |
| V03 | Same product/tests, deliberately incorrect agent patch | Native resolved=false because required behavior assertion fails; patched workspace binding verified. |
| V04 | Owned src-layout fixture with a root-level competing module; correct patch only to src product | Real pytest witness identifies the competing module; mandatory origin assertion fails even if its behavior would pass. Native resolved=false; CPU diagnostic never credits intended-patch success. No path/environment repair. |
| V05 | Required fixture test skipped | Native resolved=false; required node is skipped, not counted as passed. |
| V06 | Owned test file contains no collected tests and names a required node | Native resolved=false; no required passing tests. The missing-test-spec early return must not substitute for this invocation. |
| V07 | Owned required test exits its own pytest process with os._exit(0) before JUnit is finalized | Native resolved=false despite child exit 0; missing/incomplete JUnit cannot be credited. This destructive-to-own-child control is synthetic only. |
| V08 | Faulty flat baseline; agent patch attempts to alter protected diagnostic tests instead of product | Native protected-path handling prevents a false PASS; final independent required behavior test fails. |
| R00 | Official Requests snapshot, no agent patch | Actual complete-module import witness and five diagnostic test-node results; native outcome retained, not prescribed as benchmark truth. |
| R01 | Identical Requests snapshot/tests with exact retained E0-B180 agent_patch | Same receipts plus before/after expected source hash and patch identity; preserve whatever native outcome occurs. |
| R02 | Identical Requests snapshot/tests with exact retained E1-B180 agent_patch | Same receipts and comparison; do not require or manufacture an E1 PASS. |

Requests tests live in a new dedicated diagnostic test file outside the existing
tests/conftest.py hierarchy. Pytest receives that file through native Task.test_files
selection. Preserve existing snapshot files and native generated root config.
Import the complete requests.utils module normally; do not compile a function AST,
load the source by explicit filename or change search paths.

Use four independently authored behavioral tests derived from the public issue:
empty matching machine credentials, empty default credentials, missing matching
entry, and valid non-empty credentials. Use temporary local netrc files selected through Requests' supported NETRC
environment variable inside each owned test body, restoring it afterwards.
The native command/bootstrap environment is unchanged; NETRC is fixture input,
not an import-path repair. Use assertion-based expectations and no network. Add a
fifth mandatory origin test for workspace binding. These are our diagnostics,
not the original task tests, an official score or a reference solution. Keep their
content and forensic outcomes out of agent prompts, submissions and experiment
packaging. Do not add a new corrected Requests patch in this scope.

All three Requests cases use the same snapshot, interpreter, environment, five
tests, dependency state, timeout and verification command. Only agent_patch differs.
If imports select installed Requests, record its actual location/version/hash and
per-test semantic outputs, mark binding MISMATCH, and retain native failure due to
the origin assertion. Do not relabel that as evidence that the intended patch's
semantics failed. If collection prevents execution, the witness remains null with
a reason; classify the Requests stage BLOCKED rather than passing the gate silently.

## Evidence and acceptance

Per case retain inputs/hashes, native result/resolved/exit/error/stdout, wall-clock
seconds, expected required nodes, observed per-node statuses and witness presence.
The witness is inside our own diagnostic test, not the general P-CV-01 plugin or a
receipt for the historical hidden tests. Coverage is exactly
actual_pytest_owned_diagnostic_test_cpu. Required passing-node coverage is validated
using native results and diagnostic evidence, without replacing native JUnit logic.
Own test bodies record node start and assertion outcome before returning or
re-raising; these are labeled test-body observations, not complete hook/teardown
telemetry. Native TaskResult and its JUnit validation remain the final resolution
authority. Native JUnit bytes are not returned and are deleted at cleanup: record
raw_junit=null with that reason rather than inventing or intercepting a report.

The deliberate no-execution controls V05/V06 may have no test-body witness:
require the intended skip/no-collection evidence and explicit null reason instead.
V07 records its witness before exiting. All behavior/import controls and all three
Requests cases require valid witnesses.

Record PID/parent PID, sys.executable, Python/pytest, cwd and ordered sys.path;
loaded module __file__/resolved path/file SHA256; function __module__,
__code__.co_filename, source/code fingerprint with algorithm/version, and expected
workspace relative path and effective patched file/function fingerprints. Validate
loaded module and function together. Unknown runtime-generated/unavailable data
stays null with a reason, never zero. Fingerprints are comparable only with their
recorded algorithm/runtime. Hashing the file alone does not prove loaded code identity.

Each of R00/R01/R02 must reach all five required test nodes (pass/fail observations),
produce a valid in-process import receipt and either establish intended binding or
expose a concrete mismatch. Unexpected import/collection/setup failure blocks this
milestone and is reported, never fixed by modifying the verifier/environment.
A binding mismatch is an allowed diagnosis, not readiness: it yields
CPU_E2E_CONTROLS_PASS_REQUESTS_BINDING_MISMATCH if all eight controls pass and all
three Requests receipts are complete. Intended binding yields
CPU_E2E_CONTROLS_PASS_REQUESTS_OBSERVED, with behavior outcomes reported separately.
Neither label claims all Requests tests passed. Missing required/invalid receipts, unrelated
control failures, changed pins, incomplete cleanup or exhausted budget fail the gate.

All eight synthetic expectations must hold. R00/R01/R02 native resolved=false may
be expected diagnostic evidence; it never becomes an official resolved-task count.
Keep public_setup_acquired/source review separate from private scorer attestation.
All prior unknown scorer fields stay null with reasons, gpu_readiness stays false,
and existing blocked readiness cannot be promoted. No CPU PASS can authorize GPU.

## Exact gate after approval and implementation

Run from the worktree above, sequentially; require exit 0 for every command:

```sh
bash scripts/validate.sh
.venv/bin/python scripts/check_phase2.py --check --cohort experiments/cohort.json
.venv/bin/python scripts/prepare_startup_phase2.py --check
.tools/official/bin/python scripts/check_startup_configuration.py
.venv/bin/python docs/implementation/evidence/mostaza-phase2-startup-run/recompute.py --check
.venv/bin/python scripts/check_context_verification.py --check
.venv/bin/python scripts/check_pcv01.py --check
.venv/bin/python scripts/check_pcv01_scorer_contract.py --check
.tools/official/bin/python scripts/check_verify_task_cpu.py --check
```

The ninth command is proposed, not yet implemented or executed. It performs the
11 invocations once and verifies classifications, provenance, cleanup and immutable
inputs. It must also reject acceptance based on a synthetic/mock bypass, a changed
native source, missing actual pytest evidence, a forged binding claim, or an
unsupported readiness promotion. Unit tests exercise receipt/classifier negative
cases with owned data; they are not extra claims of native execution.

Existing eight commands preserve prior checks, historical evidence recomputation,
compiler validation and local P-CV-01 controls. Record versions, exact commands,
exit codes, durations and log hashes. A passing old gate does not substitute for
the new ninth command. No silent retries or conditional omissions of Requests.
After meaningful corrections rerun the affected checks and the full final gate;
if a scope/contract change is needed, return it for approval instead.

## Budget, audit and closure proposed for approval

CPU only; zero GPU hours, Kaggle sessions/mutations, model calls, purchases,
submissions, Discussion/posts/messages, network downloads or verifier changes.
Eleven invocations per matrix execution, serial; 30 seconds native pytest timeout,
30 seconds per native setup command, 90 seconds outer wall ceiling per case and
20 minutes total wall ceiling per full gate attempt. A watchdog must enforce the
outer limits and retain timeout evidence; command timeouts alone are insufficient.
At most two full gate attempts (initial and corrections); if more are needed,
report the blocker and seek a revised budget. No automatic retries of cases.

At most 1 GiB additional temporary plus retained local artifacts at any time;
preflight and check between cases, retain compact logs, clean only owned temporary
sandboxes. No bulk copying of wheelhouses/site-packages. If space/time/dependencies
prevent execution, report BLOCKED with the exact missing prerequisite, not success.

Approval covers the specification delta, bounded implementation, nine-command gate,
independent audit and corrections, then commit/push/update existing PR2 toward
develop after audit PASS with zero findings. No merge. Audit inspects the complete
relevant diff, native integrity, actual CPU results, leakage boundaries and exact
gate evidence. Preserve the pre-existing dirty closed-plan file without staging it.
This proposal itself requests no new Kaggle authorization. A future real batch,
any import/setup repair or real-verifier instrumentation requires a separate plan.
