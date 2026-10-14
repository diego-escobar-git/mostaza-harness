# P-CV-01 — CPU-only actual-process import observation

Approved 2026-10-14 as an ordinary follow-up to the historical P-CV-01 proposal:
implementation, CPU validation, official compatibility review, independent audit,
corrections and commit/push/update of PR2 toward develop. No SDD resume, merge,
GPU, real Kaggle verifier change or new remote execution is authorized. Historical
proposal/readiness/evidence and the closed phase2 plan remain unchanged.

AC-P1: Provide an opt-in diagnostic pytest plugin, copied only into disposable
native CPU sandbox environments as mostaza_origin_receipt.py. Its sole activation
is adding `-p mostaza_origin_receipt` to the unchanged synthetic verifier command.
No entry point, autoload registration, conftest injection, product installation,
PYTHONPATH repair, official source patch or real harness configuration change.

AC-P2: At tryfirst pytest_runtest_call, observe ONLY already-loaded named public
product modules from sys.modules and supported module-level Python functions.
Accept no item/test arguments. Do not import/reload product, inspect test bodies,
names, arguments, fixtures or expectations; do not alter product namespaces,
imports, search paths, environment, test outcomes, exceptions or scoring.

AC-P3: Configuration is host-only, bounded and explicit: schema1, absolute receipt
outside workspace, reviewed module/symbol/expected file and at most five pinned
public files per target (at most20 targets). Exclude test/conftest paths and module
names. Bound file reads to2MiB and append only to a regular nonsymlink destination
(up to10MiB before append). Fail silently on diagnostic errors; the host marks
missing receipts unavailable with a reason. Never reinterpret missing as zero.

AC-P4: Receipts identify PID/interpreter/Python/pytest, timestamp, cwd/sys.path,
plugin hash and each requested public target's module origin/file hash, expected
binding and function code/source hashes. Nulls carry reasons. Read only reviewed
public files. Do not hash code from a replacement originating in test/fixture
files. A reexport from a different reviewed public file may have a code hash but
must not misattribute the importing module's source segment. Module binding does
not prove unchanged function semantics. No source text or code constants emitted.

AC-P5: Validate actual native SubprocessManager pytest processes with and without
the plugin using the same synthetic inputs, environment, options and targets.
Exercise positive/negative outcomes, installed-package shadowing, fixture function
replacement, setup error, logging failure and missing configuration, under both
pytest8.4.2 and9.1.1. Require exit/JUnit-count parity, same PID/function identity
at the call hook when supported, no dynamic product accessor/import, no fixture
expectation/name leakage and no source/test mutation. Code changed later in the
test is outside this point-in-time receipt's coverage.

AC-P6: Review official pytest APIs and pinned harness sources. Clearly separate
public API support from organizer authorization and real scorer parity, which
remain unknown without authorized setup provenance. The native fixed command is
not changed. Test both pytest versions on local Python3.13; Python3.12 grammar
validation is not Python3.12 runtime/Kaggle validation.

AC-P7: Keep plugin, raw synthetic tests/receipts and analyst diagnosis outside
all submitted closures/notebook payloads. Preserve original experiments, notebooks,
lock/dependencies and historical evidence byte-exact against eb04b1c. Preserve
blocked GPU readiness and the sibling observer's fail-closed behavior. No model,
GPU, remote sessions, competition submission, purchases or large model download.

Acceptance gate: run the six existing CPU correction commands in their recorded
order, followed by `.venv/bin/python scripts/check_pcv01.py --check` (optionally
retain raws in a NEW results directory). Tests, lint/types/build, official compiler,
historical evidence recomputation and native controls must actually pass. Record
command statuses/source hashes and obtain independent PASS with zero open findings
before commit/push/update PR2, without merge. The exact seven-command gate and
reproduction prerequisites are recorded in the new CPU evidence report. A local
PASS never unlocks GPU or proves historical Requests imports/task correctness.
