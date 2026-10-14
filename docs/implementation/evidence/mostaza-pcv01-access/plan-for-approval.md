# P-CV-01 official setup access and scorer compatibility — proposal

Status: PROPOSED, awaiting approval. Ordinary follow-up, not a new/resumed SDD
workflow. This records read-only investigation on2026-10-14 and proposes the next
bounded CPU/documentation work. It authorizes no compute allocation or verifier
integration. No implementation/specification/runtime/readiness/PR change was made
in this investigation; only this new proposal/evidence and an ignored source copy.

## Findings established now

1. The authenticated competition Data UI exposes sandbox/setup.py as an individual
   participant-facing file. Its Download action produced13883bytes; SHA256 is
   `0263995ade90f83c8efa0ab5c7c9b7629696f39bc75274d58fc27ab774568409`.
   The original remains in /Users/diego/Downloads/setup.py, with an ignored copy at
   resources/official/pcv01-access-20261014/sandbox/setup.py. It was parsed/read,
   never imported or executed. No numeric competition-file version was exposed;
   do not invent one. investigation.json records the exact provenance.
2. The historical403 was for ListDatasetFiles on the separate
   metric/gemma-4-developer-agent-metric-data dataset. It does not establish that
   participant-facing competition assets are inaccessible. The public competition
   route succeeded without retrying/bypassing that403, broader OAuth permissions,
   credential changes or new terms acceptance. Private dataset/scorer access
   remains unknown; possession of a public development setup does not establish it.
3. The public script's main calls editable installation; its fast path writes
   workspace_paths.pth including the workspace and child directories, and changes
   local pytest discovery configuration. Failed editable installation has a
   fallback whose status is also unchecked. These are static code findings, not
   observed execution/installation results or a proposed repair.
4. In the pinned swegemma0.2.11 wheel, install_editable_package and
   install_test_dependencies both return immediately for SubprocessManager or
   SubprocessSandbox. In the Docker path, test dependency installation may copy
   and execute the selected setup script with --fast-path. Installed native files
   match wheel bytes. Therefore the prior statement about suppressed install
   failures describes a code path; it is not proof that installation ran/failed in
   the subprocess notebook. The existing Mostaza runner requires subprocess.
5. The notebook's host Python version and the verifier sandbox Python version must
   be recorded separately. Published Data documentation describes Python3.13 for
   the Docker sandbox; this does not attest the actual private scorer image or
   the historical subprocess runtime. Neither public script nor CPU parity can
   establish the historical imported Requests module/function.
6. The official competition Discussion surface provides New Topic and identifies
   Elan Markowitz as Competition Host in the linked welcome topic. No message,
   comment, upload, publication, submission or remote compute action was made.

## Limits of the compatibility conclusion

Public pytest API support and the existing synthetic CPU controls are established
by the previous P-CV-01 delivery. This investigation adds accessible public setup
source and a backend-specific bootstrap distinction. Three other questions stay
separate: organizer permission for instrumentation, applicability of published
assets to the actual scorer, and behavior inside an actual scored pytest process.

P-CV-01 explicitly adds -p mostaza_origin_receipt and copies a module/config into
its diagnostic environment. Activating it in the real scorer would change that
process/environment. This proposal does NOT authorize that action. Without an
already supported organizer receipt or further authorized execution, actual
instrumented scorer parity remains unknown. Organizer approval alone would not
prove runtime parity. No CPU/documentation result can promote GPU readiness.

## Proposed specification/documentation delta

Add an append-only source-access/compatibility review to the existing P-CV-01
specification and runbook after approval. Preserve earlier reports as historical
checkpoints, while clearly superseding their broad public-setup-access limitation.
Document subprocess early returns separately from Docker installation failures.
Do not modify submission/experiments/notebooks, real verification code, original
manifest/lockfiles, old evidence or the closed SDD plan.

Acceptance records must keep these fields distinct, with null/reasons as needed:
public_setup_acquired, source_hash_verified, development_backend_reviewed,
scorer_backend_attested, scorer_source_equivalence_attested,
organizer_diagnostic_permission, supported_observation_route,
actual_scorer_runtime_parity and gpu_readiness. No missing response is a denial,
zero, compatibility approval or evidence of source equality.

## Stage A — complete authorized source provenance

Retain the acquired public setup with URL, account, relative file path, bytes,
SHA256, acquisition date/method and observed version (null if not exposed).
Download only Dockerfile.sandbox and Dockerfile.public from the same competition
Data UI, and a public/redacted metric bootstrap wrapper ONLY if an official source
or host explicitly supplies it. No guessed private paths or bulk dataset download.

An optional official CLI equivalent, not executed during this investigation, is:

```sh
kaggle competitions files gemma-4-developer-agent --page-size 200
kaggle competitions download gemma-4-developer-agent -f sandbox/setup.py -p NEW_IGNORED_DIR
```

The official CLI documents individual -f downloads; omitting -f downloads all and
is excluded. Prefer the already working authenticated browser. The runbook's
.tools/kaggle executable is not present at that path in this worktree; do not
install/re-authenticate or broaden scope merely to replace a working browser.
If the participant-facing route requires new terms, permissions or returns a
fresh access denial, record it and return the concrete decision; do not bypass.

Distinguish published development artifacts from the effective source selected by
resolve_sandbox_setup_script in a particular runtime. A public file hash does not
attest that selection. Ask for source/version/hash or a redacted bootstrap manifest
rather than requesting secret tasks, reference solutions or private test bodies.

## Stage B — source review and existing CPU controls, without verifier modification

Review pinned setup, container_setup.py, verification.py, subprocess backend and
public Docker recipes as data. Map setup selection, early returns, install status,
workspace_paths.pth, inherited site-packages, import paths, generated discovery
settings and the fixed pytest invocation. Separate host, agent sandbox and verifier
sandbox runtime identities. No setup import/execution, native monkeypatching,
plugin installation into .tools/official, image build/download, new Linux VM,
Colima change, dependency upgrade or grader invocation is included.

Implement a small host-only static contract checker,
scripts/check_pcv01_scorer_contract.py --check, only after approval. It verifies
source pins/AST facts, inventory boundaries and explicit unknowns. It must not
infer organizer permission from API support or a missing plugin switch. It must
not infer scorer equality from a public file name. It must retain blocked
readiness and reject any automatic real-verifier/plugin activation.

Rerun the existing synthetic CPU matrix with the same commands/conditions. New
static tests cover native subprocess early returns, public setup identification
and absent/limited organizer metadata. These checks validate local tooling and
source interpretation; they do not become real scorer evaluations. Inspect the
complete relevant delta and obtain independent audit PASS with zero findings.

## Stage C — obtain an authoritative organizer answer (separate send authorization)

The exact proposed public question is organizer-question-draft.md. Destination:
one new technical topic in the competition Discussion, under diegofescobar,
addressed to the competition hosts. The question contains only published source
identity and the generic diagnostic protocol; no raw traces, credentials, private
notebook IDs, task patches, tests, outcome expectations or file attachments.

No post/send is authorized by this proposal's existence. Publication needs explicit
user authorization for that draft and destination. Local Stage A/B approval can
be given independently. Do not submit forms, join Discord, send DMs or support
requests automatically. If the user prefers, they may post the draft themselves
and provide the official response link. No background polling/reminder is created.

Request confirmation of:

- authorized public/redacted scorer bootstrap/setup source and version/hash;
- actual scorer backend, container/runtime identity, Python/pytest and harness/
  metric wrapper versions, plus any known development-versus-scoring differences;
- whether an official existing hook/receipt can report already-loaded public
  module/function origin inside the actual pytest process without participant
  command/environment changes;
- whether the explicit -p diagnostic protocol has official support, and whether
  that support applies only to local diagnostics or also to scorer observation.
  This is a policy/API question, not a request to enable it in our scorer.

Record an official response URL, author/host badge, date, exact scope and public
source identifiers. A participant's suggestion is not organizer authorization.
If no supported unchanged-scorer route exists, retain LOCAL_DIAGNOSTIC_ONLY;
if no authoritative answer exists, retain PENDING_HOST_CONFIRMATION. Even with a
supported route, actual scorer runtime parity stays null until direct appropriate
evidence exists under separate authorization. No result here claims task success.

## Exact proposed local gate

After approval and implementation of the static checker, execute in order:

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

The final command is proposed and not yet implemented/executed. Record command
exits/log hashes and source/raw inventories; preserve actual source evidence and
null reasons. Local gate may PASS with host confirmation pending, but only as CPU
review status. No organizer/scorer/GPU readiness promotion follows from PASS.
Independent audit/corrections precede any approved commit/push/PR2 update.

## Proposed budgets, closure and approval

Zero Kaggle compute sessions, GPU hours, model calls, submissions, purchases or
verifier changes. No models, full datasets or container images downloaded. New
source downloads: at most four allowlisted text files,256KiB each,1MiB total;
already cached native wheels are read-only. Local validation: serial,20min total
wall-clock ceiling for commands,1GiB additional retained artifacts; stop/report
if a limit is reached. Organizer reply waiting is not polling or compute work.

Approval requested separately:

A/B: source provenance, bounded static/CPU review, the exact gate, independent
audit/corrections and commit/push/update PR2 toward develop after PASS, no merge.

C: publish exactly the accompanying draft once to the named competition Discussion
under the authenticated account, or leave it unsent for the user. No implicit send
authorization from an A/B approval. No attached files or further communications.

This does not authorize any activation of P-CV-01 in the real scorer, setup/path
repair, notebook execution or GPU batch. Such a proposal must be returned for a
separate decision if it becomes necessary.

## Primary sources

- https://www.kaggle.com/competitions/gemma-4-developer-agent/data — authenticated UI, sandbox/setup.py and development/Docker documentation.
- https://github.com/Kaggle/kaggle-cli/blob/main/docs/competitions.md — official files/download commands and individual-file flag.
- https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion — official competition discussion surface.
- https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743007 — observed Competition Host identity.
- resources/manifest.json — pinned official swegemma wheel provenance; its original bytes are not edited.
- investigation.json — new acquisition hash and native AST/source checks, not a scorer-parity receipt.
