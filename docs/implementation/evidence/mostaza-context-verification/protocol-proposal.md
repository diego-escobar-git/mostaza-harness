# P-CV-01 — proposed exact-process import observation (not implemented)

This is the concrete decision returned by stage A's approved blocked-readiness
branch. It is NOT part of the implemented CPU behavior or its authorization. GPU
permission remains absent. Existing FAIL/ERROR records are never replaced.

## First prerequisite

Obtain an authorized copy and source/version/hash of the organizer's sandbox/setup.py
and the effective editable-install result. The current official authenticated
dataset inventory request returned403; do not bypass this denial. If the organizer
exposes a documented observation hook that yields the actual pytest process's
public-module origin, prefer that hook and review its exact API before use.

## Explicit diagnostic protocol change if no supported hook exists

Request separate approval for a diagnostic-only pytest plugin and its installation
in the verifier sandbox, isolated from the agent sandbox and submitted archive.
The concrete invocation delta would be:

```text
Before: python3 -s -m pytest <unchanged official targets and options>
After:  python3 -s -m pytest -p mostaza_origin_receipt <same targets and options>
```

Keep cwd, PYTHONSAFEPATH, PYTHONNOUSERSITE, PYTHONPATH, targets, timeouts, JUnit
options, patch application, secret hydration and scoring exactly unchanged. Do
not patch the official package source. Installation of the diagnostic plugin is
itself an explicit verifier-environment change, never described as an untouched
official scorer or silently enabled by the current adapter.

Proposed plugin contract: in pytest_runtest_call, read ONLY already-loaded public
product modules from sys.modules, without importing/reloading the product. Emit
interpreter, cwd/sys.path, resolved module file/hash and the public target
function's code/source hash to a host-only receipt. Do not read/serialize test
bodies, fixtures, expected values or test arguments/names. Never modify imports,
module objects, tests, environment, hook outcomes or exceptions; a logging failure
is unavailable evidence. No assertions or pass/fail override in the plugin.

Before any real use, CPU validation must show that original and instrumented
commands have the same positive/negative control outcomes, that a deliberately
shadowed module is identified inside the actual pytest process, and that the
plugin remains outside every model-visible payload. Confirm organizer compatibility
and pin plugin/official sources. Because plugin loading can itself perturb import
order, even this observation has a disclosed instrumentation limitation and must
not retroactively establish historical source binding.

If a subsequent source-binding repair is needed (editable install or path order),
return the exact before/after setup commands as a further decision after authorized
setup inspection. Do not combine that repair with retrieval or output-cap effects.
An instrumented run is a distinct diagnostic protocol until official parity is
established; it must not be presented as unchanged official benchmark scoring.

## Requested boundary for a future decision

Approve only offline design/validation of P-CV-01 and organizer compatibility
review if desired. Any implementation, verifier installation/command change,
remote diagnostic execution or GPU allocation needs its own explicit decision.
No such action was performed in this CPU delivery.
