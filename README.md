# Mostaza Harness

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

## Layout and research

- `src/mostaza/`: host-side evaluation and research tools.
- `tests/unit/`, `tests/integration/`: local contracts and fixture checks.
- `submission/`: permitted declarative competition assets only.
- `experiments/`: explicit E0 baseline and E1 hybrid configurations and cohort.
- `scripts/`: reproducible setup, validation, packaging and experiment interfaces.
- `resources/`: ignored authentic downloads and compact provenance manifest.
- `results/`: ignored bulky local outputs; retain compact approved evidence only.
- `docs/`: architecture, proposal, experiment and Kaggle procedures.

See [architecture](docs/architecture.md), [research proposal](docs/research-proposal.md),
[specifications](docs/specs/README.md), [Kaggle setup](docs/kaggle-setup.md), and
[experiments](docs/experiments.md). Official downloads require a Kaggle account and
acceptance of competition rules. Missing official assets must be reported as a
prerequisite failure. Do not substitute invented APIs or simulated measurements.

Original code is licensed under [Apache-2.0](LICENSE). External resources retain
their own license and notices; no competition datasets or model weights are
redistributed here.
