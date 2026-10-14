# Approved A/B public setup access and static scorer-contract review

The user approved source provenance and static/CPU review, the exact eight-command
gate, independent audit/corrections and commit/push/update of PR2 toward develop.
Discussion publication is explicitly withheld. This is an ordinary follow-up,
not a resumed SDD plan. No GPU, model call, notebook/scorer execution, real
verifier modification, image build/download, new dependency or Colima change.

## Source acquisition and provenance

Three authentic participant-facing files were acquired through the authenticated
[competition Data UI](https://www.kaggle.com/competitions/gemma-4-developer-agent/data),
using individual Download controls:

| Source path | Bytes | SHA256 |
| --- | ---: | --- |
| sandbox/setup.py | 13883 | 0263995ade90f83c8efa0ab5c7c9b7629696f39bc75274d58fc27ab774568409 |
| docker/Dockerfile.sandbox | 773 | 2fef37c9275522eea4dc3371c60b54d9ba3cfa7871f89f1749aa92f34beff70a |
| docker/Dockerfile.public | 988 | c92dfd9cd9ce019c4910a5334d6ecac606b612ec736a933b4af36da9c6fdf06c |

Total15644bytes, within four-file/256KiB-per-file/1MiB limits. Sources remain under
ignored resources/official/pcv01-access-20261014; original Downloads files remain
intact. public-sources.json records URL/path/hash/date/method and null numeric
version with a reason: the reviewed UI exposed no such version. These are not
organizer-attested scorer bytes. No metric wrapper was supplied through the
reviewed public surface; it stays null with a reason. No private paths were tried.

The historical403 receipt is preserved: it concerned ListDatasetFiles on the
separate metric/gemma-4-developer-agent-metric-data dataset. The public competition
route succeeded without bypassing that denial or expanding authentication. Prior
reports' broad public-setup-unavailability interpretation is superseded by this
new evidence, while private scorer access/equivalence remain unknown. The prior
investigation and proposed plan remain unchanged historical checkpoints; approval
and implemented results are separate append-only records.

The [official CLI documentation](https://github.com/Kaggle/kaggle-cli/blob/main/docs/competitions.md)
also describes individual -f downloads. This delivery used the working browser;
no CLI installation, credential refresh, new terms or access expansion was needed.
No full dataset, model, wheel collection or container image was downloaded.

## Static source findings and interpretation correction

The checker pins swegemma0.2.11 and compares installed native config,
container_setup.py, verification.py and subprocess.py against the authentic wheel.
It parses their bytes as AST/data, without importing native setup or downloaded
code. The native subprocess guards must be the first executable statements and
return before installation/dependency work. The other path stages dependencies,
resolves a runtime-dependent setup source and may copy/execute --fast-path.

The earlier suppressed-install-failure discussion applies to that other code
path; it is not proof that editable installation ran/failed in the historical
subprocess notebook. The existing Mostaza runner requires subprocess. Reading a
public setup file cannot override those native early returns, repair historical
imports or explain a specific verification failure by itself.

The public script's main requests editable installation; its fast path adds the
workspace and child directories via workspace_paths.pth and configures pytest.ini
and conftest.py. Its editable/fallback operations use unchecked subprocess results.
These are static code facts, not an observed failed/successful install. The script
was never imported/executed here, and its settings were not applied anywhere.
The actual selected setup and effective import precedence remain unknown.

The native subprocess backend defaults to inherited site-packages and assigns
PYTHONPATH to workspace. Native verification uses the fixed Python safety flags,
pytest targets/options and JUnit validation. No command, environment, plugin,
path order, setup, hidden test, patch application or scoring behavior was changed.
Host process, agent sandbox and verifier sandbox identities are distinct; no
new historical exact-process observation was obtained.

Both Docker recipes declare python:3.13-slim and install pytest without a version
pin. Recipe text therefore cannot establish a Python patch version, pytest
runtime version or image digest. P-CV-01's existing pytest8.4.2/9.1.1 CPU matrix
is a declared local compatibility test, not a Docker/scorer reconstruction.

## Implemented acceptance and unchanged uncertainty

The host-only scorer_contract module and check_pcv01_scorer_contract.py verify:

- exact bounded source inventory/location/bytes/pins and explicit absent wrapper;
- native source identity, early-return ordering, public fast-path behavior,
  subprocess defaults/import-path assignment and fixed verifier invocation;
- static Docker tag/unpinned pytest facts without turning them into runtime versions;
- unchanged historical/verifier inputs and blocked verification-origin readiness;
- scorer/organizer fields remain null with reasons and no publication is authorized.

The current validator accepts absent/limited unverified response metadata only as
unknown; it rejects non-null scorer attestations (including false denial values)
and publication/promotion attempts. It implements no organizer verification or
response ingestion pipeline. Source inspection is not permission verification.
The approved A/B work leaves organizer-status.json with zero messages and no reply.
The saved question draft is untouched and unsent; no discussion/DM/support action
or background polling is performed.

The output reports PASS_CPU_STATIC_REVIEW for these local checks. Independent
claims remain scorer_backend_attested=null, scorer_source_equivalence_attested=null,
organizer_diagnostic_permission=null, supported_observation_route=null and
actual_scorer_runtime_parity=null, each with a missing-evidence reason.
GPU readiness remains explicitly false under the existing origin guard.

A real P-CV-01 activation would add -p and a plugin/config to the test environment;
it is outside this unchanged-verifier delivery. Even a future organizer permission
would not alone prove runtime parity. A supported existing official observation
route, effective source/runtime provenance and separately authorized evidence are
still needed before any real integration/readiness decision.

## Reproducible exact gate and limits

From the same worktree, with existing pinned dependencies and these ignored
public text artifacts present, run in order:

```sh
bash scripts/validate.sh
.venv/bin/python scripts/check_phase2.py --check --cohort experiments/cohort.json
.venv/bin/python scripts/prepare_startup_phase2.py --check
.tools/official/bin/python scripts/check_startup_configuration.py
.venv/bin/python docs/implementation/evidence/mostaza-phase2-startup-run/recompute.py --check
.venv/bin/python scripts/check_context_verification.py --check
.venv/bin/python scripts/check_pcv01.py --check
.venv/bin/python scripts/check_pcv01_scorer_contract.py --check
```

The static command has no network/model/scorer side effects. It reads the locally
cached source artifacts and native wheel, plus Git provenance. Tests cover actual
source drift, duplicate/unreviewed inventory entries, invented numeric versions,
unchecked/scoped metadata and setup-as-data without execution. Existing tests
rerun actual native synthetic pytest processes, maintaining parity/coverage.

Run commands serially with a20min total wall ceiling and1GiB additional artifact
cap, retaining logs/hash receipts. Existing historical/P-CV-01 source/evidence,
experiments/notebooks and original manifests/lockfiles are protected. The closed
plan's preexisting local edit stays byte-exact and outside the new commit. The
old phase1 worktree is not modified. Approval of A/B does not authorize stage C,
a real verifier change, task-result reinterpretation, GPU execution or merge.

Validation/audit results and inventories accompany this report. Their PASS is
limited to the approved CPU source review; scorer compatibility and historical
verification origin remain unconfirmed.

The unchanged earlier check_pcv01.py retains its original compatibility note about
the prior dataset403. That note is an earlier checkpoint, not the current public
access conclusion. The final source-contract command/public-sources.json and this
report supersede that access interpretation without rewriting old source/evidence.

The exact eight-command gate passed in 71.71 seconds, within the
1200-second gate ceiling. It passed287 unit tests,41 integration tests and strict
typing on39 source/script files, plus format/lint/build, official compiler checks
and historical recomputation. The unchanged native P-CV-01 matrix passed14 paired
controls/28 pytest processes. Raw gate files total157102bytes; public source
downloads total15644bytes. No budget limit was approached.

contract-review.json records the current static-source result and null scorer
claims. cpu-parity.json records the rerun matrix with explicit receipt coverage
and missing reasons; validation.json contains command exits/timings/log hashes.
Independent audit status is recorded separately after review.

Independent read-only audit returned PASS with zero findings and reproduced the
static contract command. It recomputed all3 public-source pins,7 source-inventory
pins and16 raw-inventory pins, and confirmed104 protected files unchanged. The
review explicitly preserves null scorer attestations and withheld publication.
Audit details are in audit.json. No implementation correction was required.
