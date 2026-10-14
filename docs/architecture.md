# Architecture

Mostaza adds an exploration policy to the official Google ADK based competition
harness. A single LlmAgent follows Understand → Explore → Implement → Verify.
Kaggle owns model execution, tools, budgets and patch evaluation. Host-side
`mostaza` Python modules prepare experiments and analyze authentic results.
They are not submitted as an alternate agent runtime.

E0 is derived from verified official starter resources. E1 changes exploration
instructions while preserving model, sampling, global budget and repair policy.
The competition model is `gemma-4-31b-it-qat-w4a16-ct` for both arms.

Hybrid exploration begins with targeted lexical searches and existing symbols.
It uses bounded structural neighbors and symbol-based vector similarity when
appropriate, prioritizes error/test evidence, and stops when sufficient context
has been found. One graph hop is the default. Pilot limits of 10 neighbors and
vector k=5 are conservative starting values, not measured optima. No external
embedding, vector or graph service is introduced.

## Boundaries

`submission/` contains permitted declarative files only. Explicit arm manifests
select archive content. Authentic harness assets and official compiler dependencies
are isolated from the small local Python tooling environment; no optional GPU
runtime is installed by setup. Verify current official APIs before integrating.

Task inputs must exclude reference patches, solution fields and post-generation
verification material. Evaluation records bind task, arm, configuration, model,
source run and patch/test receipts. Paired analysis uses the same preselected tasks
and explicit missing telemetry. Bulky sources stay outside Git with hashes and
reproducible locators. Missing assets/evidence fail closed.

Local tests check host contracts. Official compiler checks verify declarations.
Actual Kaggle GPU execution establishes model behavior. These evidence levels
remain separate throughout documentation and reports.


## Phase-2 preparation boundaries

Budget-only variants overlay evaluation budgets in temporary packaging trees;
E1-R180 replaces only exploration. The new phase2 host module generates an exact
notebook payload allowlist; diagnostic/analysis modules, raw task metadata and
verification secrets are excluded. Only declarative config/prompt closures are
submitted. The notebook uses one native VllmServer and serial Evaluator tasks,
retaining native raw sources outside agent workspaces.

GPU startup defaults off and fails closed before bootstrap/install/model startup.
A verified allocation-start deadline and external resource termination mechanism
must cover cold start and failures. Stopping the vLLM process alone cannot prove
that Kaggle released the allocation. Local readiness and authentic historical
replay can complete while all six new outcomes remain NOT_RUN. See the
[phase-2 report](implementation/evidence/mostaza-phase2-budget-retrieval/report.md)
for the exact six-run proposal, provenance and pending execution prerequisites.
