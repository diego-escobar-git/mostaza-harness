"""Host-only ATIF observations; never submitted to or injected into an agent.

budget-retrieval-calibration:AC-3/4/5/10. Schema-1 records and historical
normalizer/report sources remain byte-exact. This separate diagnostic schema
reports observations, not exhaustive execution telemetry or timing attribution.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shlex
from pathlib import Path
from typing import Any

from mostaza.evaluation.contracts import canonical_json, nonempty, require, sha256
from mostaza.evaluation.import_results import (
    HOST_SOURCE_PATHS,
    retained_path,
    verify_native_evidence,
)

EXEMPT = {"get_status", "submit_patch"}
REJECTIONS = {"BudgetExceeded", "TimeoutExceeded"}
UNOBSERVABLE = {
    "localization_seconds": "No localization start/end operational definition",
    "pure_model_seconds": "No isolated model generation spans",
    "tool_execution_seconds": "Response latency includes scheduling/transport",
    "relevant_context_ratio": "No complete context/relevance mapping",
    "recall_at_k": "No separately defined post-run relevance denominator",
    "full_unique_files": "Commands and truncated reads do not enumerate all files",
    "repairs": "No complete operational repair-event contract",
}


def _number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def _elapsed(value: Any) -> float | None:
    if not isinstance(value, dict):
        return None
    extra = value.get("extra")
    elapsed = extra.get("elapsed_s") if isinstance(extra, dict) else None
    return (
        float(elapsed)
        if isinstance(elapsed, (int, float)) and _number(elapsed)
        else None
    )


def _response(observation: Any) -> dict[str, Any] | None:
    if not isinstance(observation, dict):
        return None
    content = observation.get("content")
    try:
        data = json.loads(content) if isinstance(content, str) else content
    except (ValueError, TypeError):
        return None
    return data if isinstance(data, dict) else None


def classify_command(command: Any) -> str:
    """Classify simple observed commands, never infer full search/read totals."""
    if not isinstance(command, str) or any(c in command for c in "|;&<>\n`$"):
        return "unknown"
    try:
        words = shlex.split(command)
    except ValueError:
        return "unknown"
    if not words:
        return "unknown"
    # No wrappers, aliases, script bodies or compound commands are interpreted.
    return "lexical" if words[0] in {"grep", "rg", "git-grep"} else "unknown"


def _metric(
    value: int | float | None,
    unit: str,
    source: list[str],
    denominator: int | None,
    scope: str,
    reason: str | None = None,
) -> dict[str, Any]:
    return {
        "value": value,
        "unit": unit,
        "numerator": value,
        "denominator": denominator,
        "source": source,
        "availability": "measured" if value is not None else "unavailable",
        "reason": reason if value is None else None,
        "coverage": {"scope": scope, "complete_execution": False},
    }


def diagnose_trace(
    trace_path: Path, result_path: Path, source_root: Path
) -> dict[str, Any]:
    """Extract reproducible compact observations from bounded retained paths.

    Source pointers identify exact JSON events; no raw issue/patch/verification
    contents are copied. Unknown/malformed telemetry is explicitly unavailable.
    ATIF step usage is counted once, never final_metrics or per-call extra.usage.
    """
    root = source_root.resolve()
    paths = [trace_path.absolute(), result_path.absolute()]
    for path in paths:
        require(path.is_relative_to(root), "Diagnostic source escapes root")
        retained_path(root, path.relative_to(root).as_posix())
    trace_bytes, result_bytes = (path.read_bytes() for path in paths)
    trace, result = json.loads(trace_bytes), json.loads(result_bytes)
    require(isinstance(result, dict), "Invalid native result")
    require(
        isinstance(trace, dict) and trace.get("schema_version") == "ATIF-v1.7",
        "Unsupported diagnostic trace schema",
    )
    instance = result.get("task_id")
    require(nonempty(instance), "Missing native task identity")
    require(trace_path.name == f"trace_{instance}.json", "Trace task identity mismatch")
    trace_ref = result.get("trace_path")
    require(
        isinstance(trace_ref, str) and Path(trace_ref).name == trace_path.name,
        "Native result trace identity mismatch",
    )
    trace_source = (
        f"{paths[0].relative_to(root).as_posix()}@sha256:{sha256(trace_bytes)}"
    )
    result_source = (
        f"{paths[1].relative_to(root).as_posix()}@sha256:{sha256(result_bytes)}"
    )
    steps = trace.get("steps")
    complete_structure = isinstance(steps, list) and bool(steps)
    steps = steps if isinstance(steps, list) else []
    issues: list[str] = []
    calls: list[dict[str, Any]] = []
    agent_times: list[tuple[str, float | None]] = []
    seen_steps: set[int] = set()
    seen_calls: set[str] = set()
    usage_total, usage_observed, agents = 0, 0, 0
    read_ranges: list[tuple[str, int, int]] = []
    explicit_read_attempts, known_read_responses = 0, 0
    counters = {
        "lexical_command_attempts": 0,
        "unknown_shell_attempts": 0,
        "similarity_attempts": 0,
        "graph_neighbor_attempts": 0,
        "graph_subgraph_attempts": 0,
        "exempt_attempts": 0,
    }
    for index, step in enumerate(steps):
        pointer = f"{trace_source}#/steps/{index}"
        if (
            not isinstance(step, dict)
            or type(step.get("step_id")) is not int
            or step["step_id"] in seen_steps
            or step.get("source") not in ("system", "user", "agent")
        ):
            complete_structure = False
            issues.append(pointer + ": malformed or duplicate step")
            continue
        seen_steps.add(step["step_id"])
        if step["source"] != "agent":
            continue
        agents += 1
        agent_times.append((pointer, _elapsed(step)))
        usage = step.get("metrics")
        if isinstance(usage, dict):
            total = usage.get("total_tokens")
            prompt, completion = (
                usage.get("prompt_tokens"),
                usage.get("completion_tokens"),
            )
            fields = [
                usage.get(n)
                for n in ("total_tokens", "prompt_tokens", "completion_tokens")
                if usage.get(n) is not None
            ]
            valid = all(type(v) is int and v >= 0 for v in fields)
            if valid and type(total) is int:
                if type(prompt) is int and type(completion) is int:
                    valid = total == prompt + completion
                if valid:
                    usage_total += total
                    usage_observed += 1
            elif valid and type(prompt) is int and type(completion) is int:
                usage_total += prompt + completion
                usage_observed += 1
        tool_calls = step.get("tool_calls")
        if not isinstance(tool_calls, list):
            complete_structure = False
            issues.append(pointer + ": missing/malformed tool_calls")
            continue
        observation = step.get("observation")
        for call_index, call in enumerate(tool_calls):
            call_pointer = pointer + f"/tool_calls/{call_index}"
            if (
                not isinstance(call, dict)
                or not nonempty(call.get("tool_call_id"))
                or call["tool_call_id"] in seen_calls
                or not nonempty(call.get("function_name"))
            ):
                complete_structure = False
                issues.append(call_pointer + ": malformed or duplicate call")
                continue
            seen_calls.add(call["tool_call_id"])
            name = call["function_name"]
            arguments = call.get("arguments")
            arguments = arguments if isinstance(arguments, dict) else {}
            # Single-call pairing uses native tool_name. Multi-call observations
            # require an explicit matching ID; never reuse a response for all calls.
            extra = (
                observation.get("extra", {}) if isinstance(observation, dict) else {}
            )
            matched = (
                isinstance(extra, dict)
                and extra.get("tool_name") == name
                and (
                    extra.get("tool_call_id") == call["tool_call_id"]
                    or len(tool_calls) == 1
                    and extra.get("tool_call_id") is None
                )
            )
            response = _response(observation) if matched else None
            obs_pointer = pointer + "/observation" if matched else None
            start = _elapsed(call)
            end = _elapsed(observation) if matched else None
            latency = (
                end - start
                if start is not None and end is not None and end >= start
                else None
            )
            rejected = None
            response_success = None
            if response is not None:
                status, error_type = response.get("status"), response.get("error_type")
                if status == "ok" and error_type is None:
                    rejected = False
                    response_success = True
                elif status == "error" and nonempty(error_type):
                    rejected = error_type in tuple(REJECTIONS)
                    response_success = False
            backend: str | None = None
            if (
                name == "search_similar_code"
                and response is not None
                and response.get("status") == "ok"
            ):
                # Only an explicit response backend establishes vector/fallback.
                # Scores and tool names do not establish execution of embeddings.
                backend = (
                    response.get("backend")
                    if response.get("backend") in ("vector", "lexical_fallback")
                    else None
                )
            graph_nodes: list[str] | None = None
            if (
                name in {"get_code_neighbors", "get_code_subgraph"}
                and response is not None
                and response.get("status") == "ok"
            ):
                nodes = response.get(
                    "neighbors" if name == "get_code_neighbors" else "nodes"
                )
                if isinstance(nodes, list) and all(isinstance(n, str) for n in nodes):
                    graph_nodes = nodes
            classification = (
                classify_command(arguments.get("command"))
                if name == "run_command"
                else None
            )
            if name == "run_command":
                counters[
                    "lexical_command_attempts"
                    if classification == "lexical"
                    else "unknown_shell_attempts"
                ] += 1
            for tool, metric in (
                ("search_similar_code", "similarity_attempts"),
                ("get_code_neighbors", "graph_neighbor_attempts"),
                ("get_code_subgraph", "graph_subgraph_attempts"),
            ):
                counters[metric] += int(name == tool)
            counters["exempt_attempts"] += int(name in EXEMPT)
            explicit_range = None
            if name == "read_file":
                filename, first, last = (
                    arguments.get(k) for k in ("filepath", "start_line", "end_line")
                )
                if (
                    isinstance(filename, str)
                    and type(first) is int
                    and type(last) is int
                    and 1 <= first <= last
                ):
                    explicit_read_attempts += 1
                    known_read_responses += int(response_success is not None)
                    if response_success is True:
                        explicit_range = (filename, first, last)
                        read_ranges.append(explicit_range)
            calls.append(
                {
                    "step_id": step["step_id"],
                    "tool_call_id": call["tool_call_id"],
                    "tool": name,
                    "source": call_pointer,
                    "response_source": obs_pointer,
                    "call_elapsed_seconds": start,
                    "response_elapsed_seconds": end,
                    "response_interval": _metric(
                        latency,
                        "seconds",
                        [call_pointer, obs_pointer] if obs_pointer else [call_pointer],
                        1,
                        "matched event latency; not attributable tool execution",
                        "Missing, ambiguous or reversed matched timestamps",
                    ),
                    "rejected": rejected,
                    "rejection_reason": None
                    if rejected is not None
                    else "Missing or unmatched native response status",
                    "exempt_by_official_policy": name in EXEMPT,
                    "shell_classification": classification,
                    "similarity_backend": backend,
                    "backend_reason": None
                    if backend
                    else "No backend receipt; scores/invocation are insufficient",
                    "returned_graph_nodes": graph_nodes,
                    "graph_nodes_reason": None
                    if graph_nodes is not None
                    else "No observable successful native graph node list",
                    "response_truncated": response.get("is_truncated")
                    if response and type(response.get("is_truncated")) is bool
                    else None,
                    "truncation_reason": None
                    if response and type(response.get("is_truncated")) is bool
                    else "No native truncation flag",
                    "explicit_read_range": list(explicit_range)
                    if explicit_range
                    else None,
                    "read_range_reason": None
                    if explicit_range
                    else "No successful explicit filepath/start/end request",
                    "zero_exit_with_failure_output": bool(
                        name == "run_command"
                        and response
                        and response.get("exit_code") == 0
                        and isinstance(response.get("stdout"), str)
                        and re.search(
                            r"(?:Test failed|AssertionError|Expected None)",
                            response["stdout"],
                        )
                    ),
                }
            )
    scope = "recorded ATIF attempts only; not exhaustive search/read/execution totals"
    reason = "Missing, malformed or duplicate recorded event coverage"
    metrics = {
        name: _metric(
            value if complete_structure else None,
            "count",
            [trace_source + "#/steps"],
            len(calls) if complete_structure else None,
            scope,
            reason,
        )
        for name, value in counters.items()
    }
    metrics["recorded_attempts"] = _metric(
        len(calls) if complete_structure else None,
        "count",
        [trace_source + "#/steps"],
        len(calls) if complete_structure else None,
        scope,
        reason,
    )
    rejected_known = complete_structure and all(
        c["rejected"] is not None for c in calls
    )
    metrics["rejected_attempts"] = _metric(
        sum(c["rejected"] is True for c in calls) if rejected_known else None,
        "count",
        [trace_source + "#/steps"],
        len(calls) if complete_structure else None,
        scope,
        "Incomplete matched rejection-response coverage",
    )
    charged = result.get("tool_calls")
    metrics["official_charged_calls"] = _metric(
        charged if type(charged) is int and charged >= 0 else None,
        "count",
        [result_source + "#/tool_calls"],
        1,
        "official native result counter; independent of observed attempts",
        "Missing or invalid official charged counter",
    )
    graph_calls = [
        c for c in calls if c["tool"] in {"get_code_neighbors", "get_code_subgraph"}
    ]
    nodes_complete = complete_structure and all(
        c["returned_graph_nodes"] is not None and c["response_truncated"] is False
        for c in graph_calls
    )
    metrics["returned_graph_nodes"] = _metric(
        sum(len(c["returned_graph_nodes"]) for c in graph_calls)
        if nodes_complete
        else None,
        "count",
        [trace_source + "#/steps"]
        + [c["response_source"] for c in graph_calls if c["response_source"]],
        len(graph_calls),
        "returned untruncated native node entries; not full graph size or unique nodes",
        "Missing, unsuccessful or truncated native graph response coverage",
    )
    metrics["tokens"] = _metric(
        usage_total
        if agents > 0 and usage_observed == agents and complete_structure
        else None,
        "tokens",
        [trace_source + "#/steps"],
        agents,
        "sum of agent-step aggregates once; excludes final_metrics/call extra usage",
        "Incomplete, inconsistent or missing agent-step token usage",
    )
    # Success is part of this metric's definition. A structurally valid call
    # with an unobserved result cannot be classified as either included or failed.
    read_membership_known = (
        complete_structure and known_read_responses == explicit_read_attempts
    )
    metrics["repeated_explicit_read_ranges"] = _metric(
        len(read_ranges) - len(set(read_ranges)) if read_membership_known else None,
        "count",
        [trace_source + "#/steps"]
        + [c["source"] for c in calls if c["explicit_read_range"]],
        len(read_ranges) if read_membership_known else None,
        "identical successful explicit filepath/start/end requests",
        reason
        if not complete_structure
        else "Incomplete matched successful-read response/status coverage",
    )
    metrics["repeated_explicit_read_ranges"]["coverage"].update(
        explicit_range_attempts=explicit_read_attempts,
        known_response_attempts=known_read_responses,
    )
    for name, why in UNOBSERVABLE.items():
        unit = (
            "seconds"
            if name.endswith("seconds")
            else "ratio"
            if name in {"recall_at_k", "relevant_context_ratio"}
            else "count"
        )
        metrics[name] = _metric(
            None, unit, [], None, "unobservable from this contract", why
        )
    intervals = []
    for (left_source, left), (right_source, right) in zip(
        agent_times, agent_times[1:], strict=False
    ):
        gap = (
            right - left
            if left is not None and right is not None and right >= left
            else None
        )
        intervals.append(
            _metric(
                gap,
                "seconds",
                [left_source + "/extra/elapsed_s", right_source + "/extra/elapsed_s"],
                1,
                "adjacent agent-event elapsed gap; not attributable model generation",
                "Missing or reversed adjacent event timestamps",
            )
        )
    patch = result.get("agent_patch")
    extension = result.get("_mostaza")
    effective = (
        extension.get("effective_agent_patch") if isinstance(extension, dict) else None
    )
    generated = _patch(patch, result_source + "#/agent_patch")
    applied = _patch(effective, result_source + "#/_mostaza/effective_agent_patch")
    error = result.get("error_message")
    timeout = (
        error
        if isinstance(error, str) and re.search("timeout|time budget", error, re.I)
        else None
    )
    return {
        "schema_version": 1,
        "instance_id": instance,
        "native_status": {
            "value": result.get("status")
            if isinstance(result.get("status"), str)
            else None,
            "source": result_source + "#/status",
            "reason": None
            if isinstance(result.get("status"), str)
            else "Native status absent",
        },
        "sources": {
            "trace": {
                "path": paths[0].relative_to(root).as_posix(),
                "sha256": sha256(trace_bytes),
            },
            "result": {
                "path": paths[1].relative_to(root).as_posix(),
                "sha256": sha256(result_bytes),
            },
        },
        "coverage": {
            "scope": scope,
            "structurally_complete_recorded_events": complete_structure,
            "agent_steps": agents,
            "usage_steps": usage_observed,
            "matched_responses": sum(c["response_source"] is not None for c in calls),
            "issues": issues,
            "complete_execution": False,
        },
        "metrics": metrics,
        "calls": calls,
        "adjacent_agent_intervals": intervals,
        "timeout": {
            "value": timeout,
            "source": result_source + "#/error_message",
            "reason": None if timeout else "No explicit native timeout reason",
        },
        "generated_patch": generated,
        "effective_patch": applied,
        "verification": _verification(result, result_source),
        "requests_postrun_finding": {
            "reproduction_only": (
                applied["changed_files"] in [["repro.py"], ["reproduce_issue.py"]]
            )
            if instance == "requests_7205" and applied["changed_files"] is not None
            else None,
            "reason": None
            if instance == "requests_7205" and applied["changed_files"] is not None
            else "Missing effective patch inventory or outside Requests diagnosis",
            "zero_exit_with_failure_events": [
                c["response_source"]
                for c in calls
                if c["zero_exit_with_failure_output"]
            ],
            "interpretation": (
                "A reproduction command exit does not establish resolution; "
                "only independent verification does."
            ),
            "source": [result_source + "#/_mostaza/effective_agent_patch"],
            "host_only": True,
        },
    }


def _patch(value: Any, source: str) -> dict[str, Any]:
    available = isinstance(value, str)
    files = (
        re.findall(r"^diff --git a/(\S+) b/(\S+)$", value, re.M) if available else []
    )
    return {
        "present": bool(value) if available else None,
        "sha256": sha256(value.encode()) if available else None,
        "changed_files": sorted({name for pair in files for name in pair})
        if available
        and (not value or files)
        and len(files) == len(re.findall(r"^diff --git .+$", value, re.M))
        else None,
        "source": source,
        "reason": "Generated/effective patch not retained"
        if not available
        else "Patch file inventory unavailable"
        if value
        and (
            not files or len(files) != len(re.findall(r"^diff --git .+$", value, re.M))
        )
        else None,
    }


def _verification(result: dict[str, Any], source: str) -> dict[str, Any]:
    output = result.get("test_output")
    summary = None
    if isinstance(output, str):
        matches = re.findall(r"(\d+) (passed|failed|skipped)(?: in |,|\s)", output)
        if matches:
            summary = {name: int(value) for value, name in matches}
    # Never export verifier text or test identities; these are post-run only.
    return {
        "resolved": result.get("resolved")
        if type(result.get("resolved")) is bool
        else None,
        "exit_code": result.get("test_exit_code")
        if type(result.get("test_exit_code")) is int
        else None,
        "summary": summary,
        "source": [
            source + "#/resolved",
            source + "#/test_exit_code",
            source + "#/test_output",
        ],
        "reason": None if summary else "No independently recorded test-count summary",
        "host_only": True,
    }


def diagnose_historical(project_root: Path) -> dict[str, Any]:
    """Recompute all six diagnoses, binding immutable receipts and original code."""
    root = project_root.resolve()
    evidence = root / "docs/implementation/evidence/mostaza-phase1-foundation"
    receipt = json.loads((evidence / "official-validation.json").read_text())
    # Historical normalizer sources are preserved, not re-labelled as new code.
    cohort = json.loads((root / "experiments/cohort.json").read_text())
    _, records, _ = verify_native_evidence(root, cohort, receipt)
    pins = receipt["host_postprocessing"]["sources"]
    require(set(pins) == set(HOST_SOURCE_PATHS), "Historical host source set mismatch")
    for name, expected in pins.items():
        require(
            sha256(retained_path(root, name).read_bytes()) == expected,
            "Historical host normalizer source changed",
        )
    native = retained_path(
        root, receipt["acquisition"]["retained_source_root"], directory=True
    )
    policy_source = "resources/official/swegemma-0.2.11-py3-none-any.whl"
    policy_hash = sha256(retained_path(root, policy_source).read_bytes())
    require(
        policy_hash == receipt["manifests"]["E0"]["resources"]["harness"]["sha256"],
        "Official tool policy source hash mismatch",
    )
    tasks = []
    for arm in ("E0", "E1"):
        for selected in receipt["manifests"][arm]["cohort"]:
            instance = selected["instance_id"]
            matches = []
            for path in (native / arm / "results").glob("official-result-*.json"):
                raw = json.loads(path.read_text())
                if raw.get("task_id") == instance:
                    matches.append(path)
            require(len(matches) == 1, "Missing/duplicate retained native result")
            row = diagnose_trace(
                native / arm / "results/traces" / f"trace_{instance}.json",
                matches[0],
                root,
            )
            row["arm"] = arm
            normalized = next(r for r in records[arm] if r["instance_id"] == instance)
            row["normalized_status"] = normalized["status"]
            row["patch_validity"] = normalized["patch"]
            row["verification"]["outcome"] = normalized["tests"]["outcome"]
            tasks.append(row)
    immutable = {
        path.relative_to(root).as_posix(): sha256(path.read_bytes())
        for path in sorted(evidence.iterdir())
        if path.is_file()
    }
    return {
        "schema_version": 1,
        "kind": "host_postrun_trace_diagnosis",
        "historical_evidence": immutable,
        "historical_normalizer_sources": pins,
        "official_tool_policy": {
            "source": policy_source,
            "sha256": policy_hash,
            "locators": [
                "swegemma/tools/base.py:budget_gated",
                "swegemma/context.py:check_budget",
                "swegemma/tools/graph.py:search_similar_code",
            ],
            "semantics": (
                "get_status/submit_patch exempt; rejection before increment; "
                "accepted tool errors may still be charged"
            ),
        },
        "executed_normalizer_sha256": receipt["host_postprocessing"][
            "executed_normalizer_sha256"
        ],
        "analyzer_sha256": sha256(Path(__file__).read_bytes()),
        "tasks": tasks,
        "limitations": [
            "Six historical evaluations; no new inference or phase-2 outcomes.",
            "Event intervals are not pure model/tool wall time.",
            "Similarity invocation/scores do not establish vector execution.",
            (
                "Partial/missing telemetry stays null with reasons; "
                "observations are not exhaustive execution totals."
            ),
            "Small exploratory cohort; no significance or superiority claim.",
            "Patch/verification findings are host-only and never agent inputs.",
        ],
    }


def check_diagnosis(project_root: Path, evidence_path: Path) -> dict[str, Any]:
    report = diagnose_historical(project_root)
    require(
        evidence_path.read_bytes() == canonical_json(report),
        "Trace diagnosis differs from retained source recomputation",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check_diagnosis(args.project, args.output)
    else:
        # Explicit output only; never implicitly regenerate old evidence.
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical_json(diagnose_historical(args.project)))


if __name__ == "__main__":
    main()
