# 2D Python Game Coding Environment

> Experimental / Smaller Projects portfolio project — independent open-source implementation.
> This is an original, from-scratch build. It is not affiliated with, and does not
> contain any code, prompts, data, or business logic from, any employer or client.

![status](https://img.shields.io/badge/status-in%20progress-yellow)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## 1. Problem

An educational tool where users write Python code to control a 2D game character, useful for teaching programming concepts interactively.

## 2. Architecture

```text
Code Editor -> Sandbox Executor -> Game Engine State Update -> Rendered Output + Terminal/Debugger
```

## 3. Technology Stack

- Django
- Python (sandboxed execution)
- Pygame or a custom 2D engine
- JavaScript (editor frontend)

## 4. Feature List

- In-browser code editor
- Restricted/sandboxed code execution
- Terminal output panel
- Debugger support
- Live game state visualization
- Django backend for session management

## 5. Implementation Plan

1. Phase 1: Sandboxed Python execution environment
2. Phase 2: Simple 2D game engine controllable via code API
3. Phase 3: Editor, terminal, and debugger UI integration

## 6. Repository Structure

```text
python-game-code-runner/
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── .env.example
├── docker/
├── docs/
│   ├── architecture.md
│   └── evaluation.md
├── src/
├── tests/
├── configs/
├── scripts/
├── notebooks/
├── examples/
├── assets/
└── .github/
    └── workflows/
```

## 7. Setup

```bash
git clone <this-repo-url>
cd python-game-code-runner
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # or: pip install -e .
cp .env.example .env              # fill in API keys / config
```

## 8. Dataset

Document which public dataset(s) or synthetic data generators are used here.
No proprietary, employer-owned, or client-identifiable data is used in this project.

## 9. Training / Execution

Document the commands used to run training, ingestion, or the main pipeline, e.g.:

```bash
# Phase 1: run a submission in the restricted executor
python -m src.main run --file examples/safe_moves.py
python -m src.main run --code "print(sum(range(10)))"
python -m src.main run --file examples/blocked_escape.py   # -> rejected
```

**Phase 1 scope:** the executor restricts builtins, enforces an import
allow-list, and rejects introspection-based escapes via an AST pre-pass. It
runs in-process and does **not** yet bound CPU time or memory — an infinite
loop will still hang the caller. Hard limits (subprocess + `resource` rlimits +
timeout) are Phase 1 issue #2.

## 10. Evaluation

Document evaluation metrics and how to reproduce them here (see `docs/evaluation.md`).

## 11. Results

_To be filled in as the implementation progresses — screenshots, metrics tables, and
sample outputs go here._

## 12. API

_If this project exposes an API, document the main endpoints here (or link to
auto-generated OpenAPI docs, e.g. `/docs` for FastAPI)._

## 13. Docker

```bash
docker build -t python-game-code-runner .
docker run -p 8000:8000 python-game-code-runner
```

## 14. Tests

```bash
pytest tests/
```

## 15. Limitations

- This is a from-scratch, independent recreation built for portfolio purposes.
- Performance numbers, once added, are based on public datasets and are not
  representative of any production system's real-world results.

## 16. Future Work

- Expand evaluation coverage and add CI-based regression checks.
- Add more configuration presets and deployment targets.
- Track open items as GitHub Issues.

## 17. Disclosure

This repository is an **independent open-source recreation inspired by the kind of
production systems I have worked on professionally**. It contains no employer or
client source code, prompts, datasets, credentials, architecture diagrams, or
business logic. All code, data, and documentation here are original or built on
publicly available datasets and open-source tools.

---
_Last updated: 2026-08-18_
