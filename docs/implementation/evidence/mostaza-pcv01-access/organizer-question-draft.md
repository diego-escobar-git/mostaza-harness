# DRAFT — not sent

Proposed destination: one new technical topic in
https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion
under diegofescobar. Public audience: competition hosts and participants.
No attachments, private notebook references, task patches, tests or raw logs.
Sending requires separate explicit user authorization.

## Proposed title

Official scorer setup provenance and supported read-only import-origin diagnostics

## Proposed body

Hello competition hosts,

We are reviewing public-module import provenance without changing scoring,
submitting a competition entry or starting compute sessions.

The published competition Data page provides sandbox/setup.py (13,883 bytes,
SHA256 0263995ade90f83c8efa0ab5c7c9b7629696f39bc75274d58fc27ab774568409).
The released swegemma0.2.11 source returns early from editable/test-dependency
installation for SubprocessManager, while its Docker path may execute the setup
script. The public setup fast path writes workspace_paths.pth. Could you confirm
which public or redacted setup/bootstrap sources, versions/hashes and runtime
backend describe the actual scorer, including Python/pytest, container image and
harness/metric wrapper versions? Are there development-versus-scoring differences
we should account for?

Is there an existing organizer-supported way to obtain the already-loaded public
module/function file and code hash from inside the actual pytest process, without
participant changes to the verifier command or environment?

For local CPU diagnostics only, P-CV-01 is an explicit opt-in pytest plugin loaded
with `-p mostaza_origin_receipt`. A tryfirst pytest_runtest_call hook accepts no
test item; it reads only configured already-loaded public product modules and
reviewed public source/code hashes, writes a separate process-origin receipt,
and never imports/reloads the product, inspects test/fixture/expected-value data,
or alters outcomes. Loading a plugin can itself affect import order, so we do
not treat local parity as proof of scorer parity. Is any such observation protocol
officially supported, and is that support limited to local diagnostics or also
available through an organizer-controlled scorer observation mechanism?

We have not enabled this plugin in the real scorer. We are asking for source/API
provenance and the permitted diagnostic boundary, not for secret tests, reference
solutions or changes to scoring. If no unchanged-scorer observation route exists,
we will keep it as a local diagnostic and retain scorer provenance as unknown.

Thank you.
