# Official resources and compiler checks

The official starter notebook version 3 and organizer wheelhouse version 31 were inspected on 2026-10-13. `resources/manifest.json` records the three pinned wheel SHA-256 values, Python requirements and actual retrieval provenance. Downloads stay in ignored `resources/official`; third-party data and model assets are not redistributed. Wheel metadata does not declare a license; inspect applicable Kaggle terms before redistribution. Original Mostaza code uses Apache-2.0.

## Authenticated resource review

On 2026-10-13 the enrolled user obtained individual authentic competition files through the official Data UI. The README, root agent, evaluation config, sampling config, system/analyzer prompts, analyzer config and task metadata now live in ignored `resources/official/`; original Downloads files remain intact. All hashes and review notes are recorded in `resources/manifest.json`. Its sample inventory was generated locally from these downloads and is explicitly not an organizer-supplied file. Numeric competition dataset version was not exposed by the individual downloads; the exact SHA-256 values identify the reviewed bytes without inventing a version.

The task metadata contains 129 unique instances: 67 FastAPI, 13 Requests, 48 Rich and 1 HTTPX. Only instance IDs, repository names and base commits were reviewed for inventory. Reference patch/test_patch bytes remain in ignored raw metadata and never enter agent inputs or submission archives. The selected snapshot, graph and embedding assets were acquired and hashed; the three-task cohort was frozen before outcomes and executed in both arms. Model weights remained in Kaggle.

The full official README and sample declarations were reviewed against the existing pinned wheels. The README permits four quantized competition models; Mostaza retains the specifically required 31B model. Its illustrative timeout of 300 seconds does not override the authentic sample's 60 seconds. The original delegated analyzer's `../` includes are removed with that agent; compiler security is unchanged. Native similarity supports stored symbol lookup and lexical fallback, without a live text encoder. No material incompatibility requiring a new specification was found.

## Minimal E0 derivation

`experiments/E0-baseline/manifest.json` binds each source and exact change. E0 preserves the original root name, 31B model, all nine native tools, generation parameters and source evaluation config. It removes `adapter: main_lora` and the delegated `code_analyzer` AgentTool, omitting the analyzer declaration/prompt and both dummy adapters from the submitted closure. Adapter weights were not needed or downloaded. The exact sampling mapping is inlined into the owned root YAML and the instruction include points to `prompts/baseline.md`.

The original system prompt remains a byte-exact prefix. The only added shared instruction is the documented `Shared Budget Checkpoints` suffix required by agent-retrieval:AC-4: call get_status before exploration, implementation and verification, preserving official time for patching, targeted verification and submission. Both arms use this same clause. E0's original retrieval, implementation, verification and repair text otherwise remains unchanged; no Graph-SDD exploration optimization was added to E0.

Source values used unchanged in the actual paired run are temperature 0.2, top_p 0.95, max_output_tokens 16384, thinking_budget 4096 and include_thoughts true. The exact evaluation file sets timeout_seconds 60, max_tool_calls 10, max_time_minutes 1 and max_turns 50. Phase 2 verification_timeout_seconds remains the pinned harness default 300; it is absent from the sample file. None of these values were tuned from outcomes.

E0 passed current official directory/schema/compiler validation and deterministic selected-closure archive reproduction locally. These are actual derived-config compiler checks with inert registry bindings, distinct from synthetic boundary tests. They perform no Gemma inference or benchmark task execution and do not establish actual evaluation compatibility. E1 receives the same frozen conditions and changes only the exploration instruction section.

## Reproduce public pins

From the repository root, after `sh scripts/setup.sh`:

```sh
uv run --frozen --no-sync python scripts/fetch_resources.py --resource swegemma --resource adk_submission --resource adk_eval_core
uv run --frozen --no-sync python scripts/fetch_resources.py --check --resource swegemma --resource adk_submission --resource adk_eval_core --resource notebook
```

The fetch command downloads one explicitly named small file at a time through official Kaggle endpoints, verifies the pin before atomic publication and refuses to overwrite conflicting files. It does not fetch authenticated competition assets or bulk datasets. All three per-wheel endpoints were re-downloaded independently and matched the approved hashes on 2026-10-13. Notebook API response metadata can change; the retained exact response hash identifies the bytes actually inspected.

## Isolated compiler environment

Local tooling uses Python 3.13; the official GPU notebook reports Python 3.12.13. Keep compiler dependencies out of the locked host environment and never install the GPU wheel stack on macOS:

```sh
uv venv --python .venv/bin/python .tools/official
uv pip install --python .tools/official/bin/python resources/official/adk_submission-0.2.13-py3-none-any.whl google-adk==1.36.1 pytest rich docker
uv pip install --python .tools/official/bin/python cachetools==5.5.2 networkx==3.4.2 numpy==2.2.6
uv pip install --no-deps --python .tools/official/bin/python resources/official/swegemma-0.2.11-py3-none-any.whl resources/official/adk_eval_core-0.1.0-py3-none-any.whl
```

The isolated environment supports compiler and native retrieval contract checks; it does not install all SWE evaluation dependencies. The native dependency pins were verified installed: cachetools 5.5.2, networkx 3.4.2 and numpy 2.2.6. They satisfy the inspected swegemma 0.2.11 wheel requirements cachetools>=5.0.0, networkx>=3.0 and numpy>=1.26.0. Native graph/embedding tests use local synthetic fixtures and perform no inference. Integration tests execute actual directory validation, the current restricted schema and compiler against synthetic declarations with inert tool/model registry values. They also exercise the actual native tool registry, get_status budget response and workspace path boundary. These tests perform no inference and do not establish real E0/E1 compatibility. Missing compiler modules are errors, not skipped tests.

## Package and validate

Both authentic E0 derivation and the E1 exploration treatment are available. Reproduce the existing archives and compiler checks with:

```sh
sh scripts/package.sh --experiment E0 --output /tmp/mostaza-e0-submission.zip
sh scripts/package.sh --experiment E1 --output /tmp/mostaza-e1-submission.zip
uv run --frozen --no-sync python scripts/check_official.py --check --experiments E0 E1
```

Packaging requires an experiment manifest with schema_version 1, status `ready`, ready_for_evaluation `true`, experiment_id `E0` or `E1`, a submission-relative prompt path (for example `prompts/hybrid-retrieval.md`) and baseline_source_sha256 matching the authenticated starter bytes. A pending/draft manifest remains ineligible even after resources are available. These markers accompany the actual prerequisite review and do not establish real evaluation compatibility.

Each archive has root agent.yaml, optional eval_config.yaml and only the selected prompt's transitive include closure. The host MVP accepts declarative config/prompt files, one LlmAgent, the fixed 31B model and the nine native tools verified in `swegemma/tools/__init__.py:create_tools`. Traversal, symlinks, unknown tools/models, executable features, forbidden files, missing/cyclic includes and existing output files fail. ZIP metadata and ordering are fixed for deterministic byte reproduction. Current official directory/schema/compiler checks execute before publication. Existing archive outputs must be moved by their owner before rerunning.

The approved official check also requires authenticated resource pins and builds the host package. It fails if any resource pin, derivation or ready experiment prerequisite is missing or changed. Archive creation and local synthetic compiler tests never satisfy actual Gemma execution requirements.

## Official execution route

Follow the inspected [starter notebook](https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent) in the Kaggle offline L4x4 environment. Its current demonstration selects 12B; Mostaza must explicitly retain `gemma-4-31b-it-qat-w4a16-ct`. The notebook mounts model revision 2, serves with VllmServer, uses `swegemma.models.load_tasks`, `swegemma.config.EvalConfig` and `swegemma.evaluate.Evaluator.evaluate_task`, then validates with `adk_submission.validate_directory`. The approved frozen cohort—requests_7205, fastapi_15589 and rich_3061—was executed in both arms in actual Kaggle notebook version 2, run 358139443, on four NVIDIA L4 GPUs. Each arm recorded PASS 0, FAIL 1, ERROR 2 and zero resolved tasks; all six sessions reached the unchanged one-minute budget. Requests produced applicable patches that failed official verification; FastAPI and Rich produced no patch, so verification did not run. E1 made no vector or graph tool call, and these results establish no retrieval benefit. Retained native files and the declared compact evidence document actual execution separately from local compiler tests.

For a future rerun, attach the same required task/snapshot/graph/embedding inputs, pinned wheelhouse, 31B model revision 2 and L4x4 GPU runtime, and freeze any new cohort before observing outcomes. These are prerequisites for another execution, not blockers of the completed six runs. Never substitute illustrative first tasks for the approved cohort or describe mocks as model results. See [experiments.md](experiments.md) for result import, source-integrity verification and deterministic report commands.
