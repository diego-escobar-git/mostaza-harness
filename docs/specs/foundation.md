# foundation

Depends on: none

## Purpose

Provide a small reproducible development foundation and verified official dependencies.

## Requirements

REQ-1: Keep host-side development and research tools separate from competition submission contents.
REQ-2: Reuse Google ADK and the official harness; do not implement an alternative runtime.
REQ-3: Use reproducible dependencies and preserve the machine configuration.

## Rules and constraints

AC-1: A fresh macOS development environment installs the locked Python 3.13 tooling with uv; setup validates the interpreter and never installs GPU model weights or changes global Colima configuration. Kaggle GPU execution follows the official notebook environment separately.

AC-2: The repository has the requested source, tests, submission, experiments, scripts, results and documentation structure, Apache-2.0 license, and ignore rules excluding credentials, virtual environments, weights, datasets, archives and bulky run outputs.

AC-3: The resource inventory records official URLs, retrieval date, notebook and wheelhouse versions, wheel SHA-256 and Python requirements; HARNESS_README, sample submission and selected task resources are reviewed from official authenticated downloads before integration. Missing resources cause an explicit prerequisite failure, never invented API behavior.

AC-4: Local unit, integration, lint, formatting, type and package-build checks execute reproducibly; simulation, compiler-only validation and actual Gemma/Kaggle evaluation are distinguishable in documentation and results.

## Product decisions

PD-1 — Use Python 3.13 for local tooling, subject to actual dependency resolution; use the official Kaggle runtime for GPU execution (plan: mostaza-phase1-foundation, 2026-10-13).
PD-2 — Adopt Apache-2.0 for original project code, retaining third-party notices and avoiding redistribution of data/model weights (plan: mostaza-phase1-foundation, 2026-10-13).

## Interfaces and data contracts

Host tooling is a Python package mostaza. Official assets live in an ignored resources directory. A small JSON resource manifest contains provenance and hashes, never credentials.

## Out of scope

Fine-tuning, reinforcement learning, specialized multiagents, external embedding/vector/graph services, public APIs, dashboards, deployment and exhaustive hyperparameter tuning are outside Phase 1. No model downloads on the Mac.
