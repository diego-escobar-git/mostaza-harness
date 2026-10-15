# Observed B180 allocation: startup failure and confirmed closure

One authorized private NVIDIA L4×4 allocation ran on 2026-10-14. No task reached
agent execution: all six E0-B180/E1-B180 rows are **NOT_RUN**. Task tokens, tool
calls, patches and verification remain null with reasons. No comparison of
retrieval efficacy is available, and no replacement allocation is authorized.

[Private version 1](https://www.kaggle.com/code/diegofescobar/mostaza-b180-6526b0decc91474cb1bd3335d77d06a0?scriptVersionId=358356305) is bound to notebook
138681790 and opaque scriptVersionId 358356305. The original agent/input payloads
and paired B180 settings were preserved. The runtime candidate and the fresh
single-use launch adapter each received independent PASS before GPU use.

## Observed failure

The retained native log identifies **CUDA out of memory during sampler warm-up
with 256 dummy requests**, followed by `EngineCore failed to start`. One worker
reported trying to allocate 256 MiB with 31.06 MiB free on a 22.03 GiB device.
Weights had loaded; worker 0 reported 72.36 seconds for that operation. CUDA graph
capture preceded the sampler failure. The parent API process remained alive and
the official readiness loop continued waiting, so a live PID alone was not a
readiness or progress guarantee. No model-ready/task-start marker or task result
was acquired. This evidence establishes the new run's startup failure; the cause
of the prior uninstrumented aborted allocation remains unknown.

The new instrumentation persisted 117 observations and the full
85,871-byte native server log. Both native source
and retained-log downloads have identical hashes. Thirty-four output files
(504,399 bytes) were acquired through the official output API
only after browser/SDK terminal confirmation. The API notebook pull contains
submitted source with null execution counts; it is retained as saved source,
not an executed notebook. Official execution logs and native artifacts provide
the startup evidence independently.

## Timeline and quota

| Observation | Value |
| --- | --- |
| External prelaunch T0 | 2026-10-14 08:50:14.795 Bogotá / 13:50:14.795 UTC |
| First observer | +130.20 s; preceding queue/container/kernel work not separately observed |
| Offline package installation | 51.72 s |
| Torch import | 5.72 s |
| Bootstrap complete → preflight complete | 97.41 s, including cell transition |
| Server start requested | +227.80 s |
| Native OOM timestamp | 08:59:21 Bogotá / 13:59:21 UTC; one-second resolution |
| Exact-version browser Cancel clicked | +630.55 s, 09:00:45.345 Bogotá |
| First observed SDK CANCEL_ACKNOWLEDGED | +700.20 s, well before minute 105 |
| Browser version | Cancelled after 8 minutes and 38 seconds; platform runtime excludes part of external clock |
| Reported quota delta | 1017.237842 Kaggle quota seconds (about 16 min 57 s); not physical GPU-device seconds |
| Paid purchases / retries | $0 / 0 |

SDK CANCEL_ACKNOWLEDGED and exact-version browser cancellation agree. Active
Events showed the target Cancelled and 0 active events. Reported used quota was
stable at 4115.521071 seconds over reads separated by more than 30 seconds;
reserved zero is only corroboration. The physical release instant remains null.
Four devices multiplied by the external interval to the browser terminal
observation equals about 0.804
device-hours; this arithmetic is not a direct physical-use measurement or a
platform release guarantee. The 120-minute / eight-device-hour spending ceiling
was not approached in the observed operational interval.

## What can be concluded

Instrumentation exposed a concrete memory failure that the earlier acquisition
could not diagnose. Browser version supervision and cancellation worked for the
identified target. E0 and E1 produced no benchmark observations in this batch;
there is no evidence here for hybrid retrieval success, failure or superiority.
The completed phase-1 six-task results remain unchanged and cannot be combined
with these NOT_RUN rows as if generation budgets had been compared.

A source-level comparison with the executed phase-1 notebook found four explicit
startup environment assignments that the phase-2 submitted notebook does not
make: `VLLM_ENGINE_READY_TIMEOUT_S=1200`,
`VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=1`, `NCCL_DEBUG=WARN`, and
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. Both exact source hashes and
the comparison scope are retained in
[startup-environment-delta.json](startup-environment-delta.json). Effective
inherited subprocess values were not snapshotted; absent assignments do not prove
absent environment values or causal responsibility for the OOM.

The next independent local step is to review restoring that historically explicit
startup environment, then review the official vLLM warm-up capacity and memory
settings. The native exception recommends inspecting `max_num_seqs`
or `gpu_memory_utilization`; neither was changed or retried in this allocation.
Any runtime correction must preserve both arms' matched conditions, undergo
local checks/audit and receive a fresh concrete compute authorization before
another GPU allocation. Do not reuse this batch receipt or historical controller.

Provenance, units, coverage, source hashes and limitations are in
[acquisition.json](acquisition.json); all planned rows are in
[evaluation-records.json](evaluation-records.json). Bulky original files remain
in ignored `results/kaggle-phase2-observed-6526b0decc91474cb1bd3335d77d06a0`. The native pre-start inventory is a snapshot,
not a final hash inventory; `download-inventory.json` binds the acquired bytes.
