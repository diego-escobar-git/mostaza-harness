"""Host-only context/error coverage; never changes native outcomes or agent tools."""

from __future__ import annotations

import json
import re
from typing import Any


def context_fit(
    prompt_tokens: int | None, output_cap: int = 8192, *, lower_bound: bool = False
) -> dict[str, Any]:
    if type(output_cap) is not int or not 1 <= output_cap <= 32768:
        raise ValueError("Invalid output reservation")
    if prompt_tokens is not None and (
        type(prompt_tokens) is not int or prompt_tokens < 0
    ):
        raise ValueError("Invalid observed input count")
    total = None if prompt_tokens is None else prompt_tokens + output_cap
    status = "UNKNOWN" if total is None or lower_bound else "FITS_OBSERVED_REQUEST"
    if total is not None and total > 32768:
        status = "EXCEEDS_CONTEXT"
    return {
        "status": status,
        "prompt_tokens": prompt_tokens,
        "prompt_count_is_lower_bound": lower_bound,
        "requested_output_tokens": output_cap,
        "combined_tokens_or_lower_bound": total,
        "context_window_tokens": 32768,
        "future_fit_guaranteed": False,
    }


def error_category(error: str | None, *, verification_exit: int | None = None) -> str:
    text = (error or "").lower()
    if "contextwindow" in text or "maximum context length" in text:
        return "CONTEXT_REJECTION"
    if "timeout" in text or "time limit" in text:
        return "TIME_LIMIT"
    if "tool" in text and ("budget" in text or "limit" in text):
        return "TOOL_LIMIT"
    if verification_exit is not None and verification_exit != 0:
        return "VERIFICATION_FAILURE"
    return "OTHER_ERROR" if error else "NO_RECORDED_ERROR"


def read_action(
    arguments: dict[str, Any], response: dict[str, Any], *, duplicate: bool
) -> str:
    if duplicate:
        return "USE_BOUNDED_SHELL_READ"
    if set(arguments) - {"filepath", "start_line", "end_line"}:
        return "CHECK_ARGUMENT_KEYS"
    start = arguments.get("start_line", 1)
    if start is not None and str(response.get("start_line")) != str(start):
        return "CHECK_RETURNED_RANGE"
    return (
        "READ_ONLY_MISSING_RANGE"
        if response.get("is_truncated")
        else "USE_OBSERVED_RANGE"
    )


def trace_coverage(trace: dict[str, Any], output_cap: int = 8192) -> dict[str, Any]:
    reads, contexts, decisions = [], [], []
    seen: set[tuple[Any, ...]] = set()
    for step in trace.get("steps", []):
        if step.get("source") != "agent":
            continue
        usage = step.get("metrics", {})
        observed = usage.get("prompt_tokens")
        contexts.append(
            {
                "step_id": step["step_id"],
                "completion_tokens": usage.get("completion_tokens"),
                **context_fit(observed, output_cap),
            }
        )
        for line in step.get("message", "").splitlines():
            if re.match(r"^Retrieval decision:\s*\S", line):
                decisions.append({"step_id": step["step_id"], "observed_text": line})
        for call in step.get("tool_calls", []):
            if call.get("function_name") != "read_file":
                continue
            content = step.get("observation", {}).get("content")
            try:
                response = json.loads(content) if isinstance(content, str) else {}
            except (ValueError, TypeError):
                response = {}
            if not isinstance(response, dict):
                response = {}
            args = call.get("arguments", {})
            if not isinstance(args, dict):
                raise ValueError("Unsupported native tool argument representation")
            key = (
                args.get("filepath"),
                response.get("start_line"),
                response.get("end_line"),
                response.get("content"),
            )
            complete = (
                response.get("status") == "ok"
                and response.get("start_line") is not None
            )
            duplicate = complete and key in seen
            reads.append(
                {
                    "step_id": step["step_id"],
                    "unknown_argument_keys": sorted(
                        set(args) - {"filepath", "start_line", "end_line"}
                    ),
                    "duplicate_returned_range": duplicate if complete else None,
                    "returned_start_line": response.get("start_line"),
                    "returned_end_line": response.get("end_line"),
                    "is_truncated": response.get("is_truncated"),
                    "action": read_action(args, response, duplicate=duplicate),
                }
            )
            if complete:
                seen.add(key)
    return {
        "context_requests": contexts,
        "read_observations": reads,
        "retrieval_decisions": decisions or None,
        "retrieval_decisions_missing_reason": None
        if decisions
        else "No explicit native agent-text decision observed",
        "backend_execution": None,
        "backend_execution_missing_reason": (
            "A named invocation or decision is not a backend receipt"
        ),
        "native_outcome_modified": False,
    }
