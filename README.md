# Mostaza Harness

## Run locally and package for Kaggle

Edit `submission/agent.yaml`, `submission/eval_config.yaml` and the prompt selected
by `instruction`. The local runner and Kaggle ZIP use this same directory.

```bash
# First setup only: copy .env.example to .env and configure the paths below.
bash scripts/setup_local.sh
bash scripts/harness.sh run --task requests_7205
bash scripts/harness.sh pack
```

`MOSTAZA_DATA_DIR` points to the official directory containing `tasks.jsonl` and
`snapshots/`. Reuse downloaded competition data. To reuse the installed official
environment, set `MOSTAZA_PYTHON` in `.env` to its absolute `bin/python` path;
setup validates its package versions without reinstalling or rebinding it.
Quote paths containing spaces: the shell entrypoints source `.env`.

In LM Studio, load the existing Gemma 4 12B model and enable its OpenAI-compatible
local server on `127.0.0.1:1234`. The requested `/gemma-4-12b` is exposed as
`google/gemma-4-12b`. The defaults are `MOSTAZA_MODEL=google/gemma-4-12b` and
`MOSTAZA_API_BASE=http://127.0.0.1:1234/v1`; configure these in `.env` or use
`--model` and `--endpoint`. Each run checks `/models` for that exact identifier
and fails explicitly if the server or model is unavailable. No model is downloaded.
If server authentication is enabled, set the actual local token in
`MOSTAZA_API_KEY`; keep it outside `submission/`. Otherwise leave it unset: the
official OpenAI adapter receives the neutral non-secret `local-no-auth` placeholder
because it requires a nonempty key. Catalog checks send no placeholder token.

The official `swegemma` evaluator runs one task with its subprocess backend;
concurrency is 1 and results appear under `results/local/`. The current agent
limits are 60 seconds per command, 20 tool calls, five session minutes and 50
turns, with 16384 output tokens, default reasoning and the official 300-second
verification timeout. Local agent commands and verification prioritize the
snapshot's Python sources; `requirements-local.txt` includes the Requests
`httpbin` fixtures. A task timeout or FAIL
does not demonstrate agent effectiveness; inspect its native results and traces
separately from connection or environment failures.

Historical E0/E1 experiments load their frozen agent, evaluation settings and
prompts from `experiments/historical-submission/`, retained from commit
`74b58bc`. Their manifests still validate the original conditions and prompt
hashes. Editing `submission/` changes local development and delivery packaging
without changing those historical experiments; context variants also derive from
the frozen inputs.
Regenerating the phase-2 preparation writes
`notebooks/mostaza-phase2-preparation.ipynb`; the original preparation, observed
and startup notebooks remain historical snapshots. Generated preparations keep
GPU and Internet disabled and require their existing execution authorization.

`pack` compiles the agent with the official compiler and writes
`dist/submission.zip` and `dist/submission.ipynb`, replacing the previous generated
files. Create a notebook from the competition page and import `submission.ipynb`.
Keep GPU and Internet disabled, then Save Version with Run All. The notebook
writes `/kaggle/working/submission.zip` for the competition submission workflow.
The ZIP contains only the agent, evaluation settings, included prompts and the
allowlisted search-code skill with its standalone script. Local endpoint/authentication settings and task data
stay outside it. Kaggle uses the competition model declared in `agent.yaml`;
LM Studio is the development backend. Packaging does not launch or submit to Kaggle,
and local validation does not establish Kaggle acceptance or score.

The active agent uses six native tools and the official search-code skill. Load
`search-code` and run its `scripts/search_code.py` bootstrap through
`run_skill_script` with an explicit absolute workspace root. Bootstrap returns a
quoted command for later `run_command` searches. The CLI supports `search`,
`neighbors`, `subgraph` and `status`; every call refreshes changed source files.
Lexical retrieval replaces vector similarity. Ambiguous or dynamic dependencies
remain unresolved. If indexing is unavailable, use bounded `grep -n -F` searches.
Results fit 4500 characters; default search returns eight entries, maximum twenty.
Graph expansion defaults to one hop and is capped at two. The cache stays outside
the workspace and submitted patch.

Skill discovery/load helpers consumed zero native calls in the deterministic
pinned-runtime witness; script bootstrap consumed one native call. Bootstrap and
cold indexing also consume the unchanged five-minute wall-clock budget. The
20-call limit is enforced by the official runtime for subsequent commands.

`scripts/check_search_code.py --check --source-assets ABSOLUTE_SOURCE_CHECKOUT
--official-python ABSOLUTE_OFFICIAL_PYTHON --python312 ABSOLUTE_PYTHON312
--evidence-dir docs/implementation/evidence/2026-10-20-search-code` runs all
repository checks and five source-only snapshot benchmarks without inference.
Set `PYTHONPATH` to this checkout's absolute `src` and
`MOSTAZA_HISTORICAL_PHASE2_ROOT` to the retained historical checkout. Cold, warm
and refresh limits are 45, 3 and 10 seconds; child RSS and SQLite limits are
256 MiB and 128 MiB. Reports preserve failed checks and missing prerequisites,
and the command exits nonzero until the full gate passes. Local CPU measurements
and source-reviewed Docker path mapping do not establish Kaggle repair efficacy.
The original phase-2 retained checkout and phase-1 raw packet are currently
missing; full historical validation requires their original pinned identities.
They must not be reconstructed or replaced with generated summaries.

The sections below retain the existing research and experiment procedures.

Mostaza studies whether adaptive hybrid code retrieval helps a small language
model solve software engineering issues with less exploration. Local Python code
supports development and analysis. Competition agents run through the official
Google ADK based Kaggle harness; Mostaza does not supply a replacement runtime.

## Local setup

Use macOS with Python 3.13. The interpreter is pinned to 3.13.15 in
`.python-version`; `uv.lock` fixes dependencies and hashes. No GPU, model weights,
Docker or Colima changes are needed for local checks.

Install pinned uv into the repository when an existing uv is unavailable:

```bash
python3 -m venv .tools/uv
.tools/uv/bin/python -m pip install uv==0.9.5
export PATH="$PWD/.tools/uv/bin:$PATH"
bash scripts/setup.sh
```

An existing uv can also run setup directly. Setup uses `uv sync --locked`,
validates Python 3.13 and imports the editable package. It fails if the lock needs
updating. uv may fetch the pinned Python interpreter into `.tools/python` if unavailable;
setup caches dependencies in `.tools/cache` and never downloads model weights. For raw commands or the SDD gate, put the scoped
uv directory on PATH as above. Shell entrypoints find it automatically.

```bash
uv run --frozen --no-sync pytest -q -p no:cacheprovider tests/unit/test_foundation.py
uv run --frozen --no-sync ruff format --check .
uv run --frozen --no-sync ruff check .
uv run --frozen --no-sync mypy src scripts
bash scripts/validate.sh
```

The complete validation script also builds the package in a temporary directory,
checks authentic official resources/configurations, and verifies real paired
Kaggle evidence. It fails when those prerequisites are missing. Local unit tests
and fixtures demonstrate tooling behavior; compiler-only validation demonstrates
configuration acceptance; only sourced Kaggle runs demonstrate actual Gemma task
execution. Passing the local checks does not complete the benchmark.

Integration checks marked `historical_evidence` require
`MOSTAZA_HISTORICAL_PHASE2_ROOT` to point to the retained, immutable evidence
checkout. They deliberately fail when that prerequisite is absent; current files
cannot substitute for historical evidence. To check the current integration
separately, run `pytest tests/integration -m 'not historical_evidence'`. The full
validation script continues to require the historical checks and real evidence.

## Layout and research

- `src/mostaza/`: host-side evaluation and research tools.
- `tests/unit/`, `tests/integration/`: local contracts and fixture checks.
- `submission/`: permitted declarative competition assets only.
- `experiments/`: explicit E0 baseline and E1 hybrid configurations and cohort.
- `scripts/`: reproducible setup, validation, packaging and experiment interfaces.
- `resources/`: ignored authentic downloads and compact provenance manifest.
- `results/`: ignored bulky local outputs; retain compact approved evidence only.
- `docs/`: architecture, proposal, experiment and Kaggle procedures.

See the reusable [Kaggle execution runbook](docs/runbooks/kaggle-execution.md)
for authentication, quota checks, exact-version supervision and evidence closure.

See [architecture](docs/architecture.md), [research proposal](docs/research-proposal.md),
[specifications](docs/specs/README.md), [Kaggle setup](docs/kaggle-setup.md), and
[experiments](docs/experiments.md). Official downloads require a Kaggle account and
acceptance of competition rules. Missing official assets must be reported as a
prerequisite failure. Do not substitute invented APIs or simulated measurements.

Original code is licensed under [Apache-2.0](LICENSE). External resources retain
their own license and notices; no competition datasets or model weights are
redistributed here.

## Phase 2 results and prepared variants

The authorized B180-startup-v3 batch completed all six real evaluations after the
startup/memory correction. Each arm produced PASS0 / FAIL2 / ERROR1; no similarity
or graph-tool call was recorded, so hybrid retrieval effectiveness remains
untested. The session ended normally around external minute25, with stable quota;
a retained67-second observation gap is documented as a supervision deviation.
See the [real batch report](docs/implementation/evidence/mostaza-phase2-startup-run/report.md)
for source hashes, the executed notebook, metrics/coverage and reproducible checks.

B300 and the separate E1-R180 treatment remain prepared and compiler-validated,
with no real results. All saved preparation notebooks default to GPU disabled.
Every consumed allocation is historical; another execution requires a fresh,
specific compute authorization and prelaunch controls. The original
[phase-2 readiness report](docs/implementation/evidence/mostaza-phase2-budget-retrieval/report.md)
is retained as the pre-acquisition checkpoint.

The [approved CPU corrections](docs/implementation/evidence/mostaza-context-verification/report.md)
prepare C8K, common Q1 verification and separate R1 recovery variants without new
GPU evaluations. Exact verifier import provenance is unavailable, so the fresh
notebook remains blocked for real execution. Use
`.venv/bin/python scripts/check_context_verification.py --check` for the dedicated
CPU gate; its PASS does not remove that blocker.

The separately approved [P-CV-01 CPU diagnostic](docs/implementation/evidence/mostaza-pcv01-cpu/report.md)
observes public-module origin in actual synthetic pytest processes. Its opt-in
plugin stays outside agent/notebook payloads and the real Kaggle verifier.
`.venv/bin/python scripts/check_pcv01.py --check` validates CPU parity/isolation;
organizer acceptance and historical verifier provenance remain unconfirmed.

The [public setup/scorer source review](docs/implementation/evidence/mostaza-pcv01-access/report.md)
records authorized individual source downloads and distinguishes subprocess setup
bypass from Docker bootstrap. Its offline command is
`.venv/bin/python scripts/check_pcv01_scorer_contract.py --check`. Public source
access preserves unknown scorer attestations and blocked GPU readiness; the
organizer question remains unsent.

## Iteration 2 integration status

See [the integration boundary](docs/integration/phase2-status.md) for the combined source tree, immutable historical reconciliation, and pending CPU/Kaggle research work. Integration does not establish GPU readiness or retrieval efficacy.
