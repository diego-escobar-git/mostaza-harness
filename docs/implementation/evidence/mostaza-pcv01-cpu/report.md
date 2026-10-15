# P-CV-01 CPU diagnostic implementation

The user separately approved P-CV-01 for implementation/validation in CPU, official
compatibility review, independent audit/corrections and update of PR2 toward
develop. This is an ordinary follow-up; the closed SDD plan is not resumed or
edited. No new Kaggle session, GPU allocation, model call or real verifier change
is part of this delivery. The historical proposal is retained as the earlier
unimplemented checkpoint; this report supersedes only its CPU implementation
status. Historical readiness stays PREPARED_BLOCKED_VERIFICATION_ORIGIN.

## Implemented boundary

`src/mostaza/evaluation/pytest_origin_receipt.py` is a passive, opt-in plugin.
The CPU fixture driver copies it into disposable native SubprocessManager venvs
as mostaza_origin_receipt.py beside its host-only reviewed JSON configuration.
There is no entry point/autoload hook or installation into .tools/official, agent
sandboxes, agent archives, notebooks or a real Kaggle verifier. No dependency or
lockfile changes. The exact diagnostic command delta is:

```text
python3 -s -m pytest <same options/targets>
python3 -s -m pytest -p mostaza_origin_receipt <same options/targets>
```

Both controls use the same installed files/configuration, cwd, environment,
PYTHONSAFEPATH/PYTHONNOUSERSITE, timeout/JUnit/options and synthetic inputs. The
plugin is inactive in the baseline; its unexpected autoload would fail the control.
No change to native verifier source, PYTHONPATH, setup or scoring is implemented.

The sole hook is tryfirst pytest_runtest_call with no item/config/test arguments.
It inspects named, already-loaded public sys.modules entries using their base
ModuleType namespace, avoiding dynamic accessors and product imports/reloads.
Configured files are reviewed, public, bounded and SHA-pinned; test/conftest paths
and module names are rejected. It does not examine tests, fixtures, expectations,
arguments, outcomes or exceptions. Receipts append to a bounded host-only regular
file outside workspace; diagnostic errors do not raise into pytest. The host
reports missing receipts as null with reasons.

## Units, coverage and limitations

One JSONL row is one reached call hook, not one score or tool invocation. PID,
interpreter/Python/pytest, epoch seconds, cwd/effective sys.path and plugin SHA256
identify its process/runtime. Each requested public module has resolved file and
SHA256, expected file/binding, optional function identity/code/source SHA256 and
explicit reasons for missing values. All hashes are hexadecimal SHA256 digests;
function identity is a process-local id, not a cross-run identifier.

The code hash covers marshal.dumps of the actual supported Python function's code
object, including filename/Python-version-sensitive metadata. It is not portable
across versions/paths and does not hash globals, closure state or later execution.
The source hash covers the AST function definition segment in the pinned public
module (not decorator source). Unsupported, unreviewed or test-origin functions
are not serialized. Reexports from another reviewed file retain a code hash but
have a null source hash/reason rather than attributing the importing file's bytes.
Module binding alone does not prove that an individual function was not replaced.

This is point-in-time call-hook evidence. Fixtures execute earlier; test code or
other hooks may change bindings afterward. Tests with setup errors never reach
this hook; logging/configuration failures yield unavailable receipts. Plugin load
can itself perturb import order, so synthetic parity is not general scorer
parity. No historical Requests binding, correct patch, model adherence, retrieval
effectiveness or Kaggle outcome is established by these controls.

## Official compatibility review

Official pytest documents explicit `-p` loading, the call-phase hook and hook
argument pruning/tryfirst ordering:
[plugin loading](https://docs.pytest.org/en/8.4.x/how-to/plugins.html),
[call hook](https://docs.pytest.org/en/8.4.x/reference/reference.html#pytest.hookspec.pytest_runtest_call),
[plugin hooks](https://docs.pytest.org/en/stable/how-to/writing_plugins.html).
Actual CPU controls test pytest8.4.2 (recorded Kaggle version) and9.1.1 (local
.tools/official version) on Python3.13.15. Python3.12 grammar is checked, but the
Kaggle Python3.12.13 runtime/setup has not been reproduced.

The pinned swegemma0.2.11 wheel and installed native config/verification bytes are
compared before validation. Its verifier constructs the fixed pytest command and
the inspected EvalConfig has no plugin activation parameter. compatibility.json
records native source/hook hashes and inspected config fields. This proves public
pytest API compatibility and a local diagnostic implementation, not an official
organizer-supported switch or approval for scorer instrumentation.

The previously authenticated organizer setup inventory returned403 and remains
unavailable. No bypass or repeated remote query was made here. Organizer
permission, setup/install provenance, real scorer parity and historical exact
process origin remain null/unknown. The existing sibling observer's fail-closed
readiness logic is byte-exact, and no CPU receipt can upgrade it. Real integration,
source-binding repair or remote diagnostic execution requires a separately
reviewed concrete protocol and authorization after obtaining authorized setup.

## CPU controls

Fourteen paired controls execute28 actual pytest processes through the native
SubprocessManager. Each version exercises positive and negative assertions,
installed-package shadowing, fixture function replacement, setup error, logging
failure and absent configuration. Both commands have identical exit codes and
JUnit passed/failure/error/skipped counts. These are synthetic control outcomes,
not benchmark results or simulated replacements for unavailable real runs.

Shadowing reports a binding mismatch. A fixture-replaced function is withheld as
outside reviewed public source. Successful receipts match the test's own PID and,
where supported, function identity before the test body mutates the function.
An unloaded sentinel module stays unloaded; a dynamic missing-function accessor
is never invoked. Synthetic expectation/test/fixture markers are absent from
receipts, and source/test/plugin bytes remain unchanged within each pair. Setup,
write and configuration failures retain null receipts/reasons. Elapsed seconds
are local observation timings, not an overhead benchmark or Kaggle cost estimate.

The checker also compares91 historical/protected files against eb04b1c, checks
all five new agent closures and the embedded notebook/archive payload, preserves
blocked readiness and checks Python3.12 plugin syntax. Historical evidence,
original experiments/notebooks, dependency files and the old worktree stay intact.

## Reproduction and gate

Use the existing pinned host and official environments. In addition, cache the
small official pytest8.4.2 wheel ONLY under ignored resources/official, verifying
SHA256 `872f880de3fc3a5bdc88a11b39c9710c3497a547cfa9320bc3c5e62fbf272e79`.
Its URL and [PyPI metadata](https://pypi.org/pypi/pytest/8.4.2/json) are recorded in
compatibility.json. It is365750bytes, not a model. The driver extracts it only
into its owned temporary CPU venv; .tools/official remains pytest9.1.1. Do not
install it over the working environment or change the historical resource manifest.

The seven-command gate extends the previously approved six CPU commands:

```sh
bash scripts/validate.sh
.venv/bin/python scripts/check_phase2.py --check --cohort experiments/cohort.json
.venv/bin/python scripts/prepare_startup_phase2.py --check
.tools/official/bin/python scripts/check_startup_configuration.py
.venv/bin/python docs/implementation/evidence/mostaza-phase2-startup-run/recompute.py --check
.venv/bin/python scripts/check_context_verification.py --check
.venv/bin/python scripts/check_pcv01.py --check
```

For retained raw receipts use a NEW directory, for example:

```sh
.venv/bin/python scripts/check_pcv01.py --check --raw-dir results/pcv01-cpu/new-controls
```

Without --raw-dir, temporary raw files are removed. The integration test executes
the native paired matrix; the unit suite covers public path/config rejection,
loaded/unloaded/dynamic modules, changed-source/reexport/replaced-function handling,
passive namespaces/environment and missing logging. validation.json records actual
gate exits/log hashes; cpu-controls.json and raw-inventory.json preserve compact
results and source/raw provenance. Audit status is recorded separately in audit.json.
No gate or audit PASS is a GPU launch authorization.

The seven-command CPU gate passed:269 unit tests,40 integration tests, strict
types on37 source/script files, format/lint/build, pinned official compilations
and historical recomputation. The28-process P-CV-01 matrix passed in both pytest
versions. See validation.json for the executed commands and raw log hashes.

Independent read-only audit returned PASS with zero findings and reran the
14 paired native CPU controls successfully. All6 source and158 raw evidence
pins matched. audit.json records the review boundary and explicit limitations.
