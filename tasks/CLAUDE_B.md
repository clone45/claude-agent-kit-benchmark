# click

Working copy of the pallets/click command-line toolkit, used for an evaluation. Python 3.13. Source is in `src/click/`, tests in `tests/`, docs in `docs/`.

## Commands

- Full test suite (about 6 seconds): `.venv/bin/python -m pytest -q`
- One test file: `.venv/bin/python -m pytest tests/test_basic.py -q`
- Lint: `.venv/bin/ruff check src tests`
- Format check: `.venv/bin/ruff format --check src tests`
- Type check (strict; covers `src` and `tests/typing` as configured in `pyproject.toml`): `.venv/bin/mypy`

Warnings are errors in the test suite (`filterwarnings = error`).

## Rules

- Work autonomously. Nobody will answer questions; make reasonable decisions and finish the task.
- Do not commit, stash, or switch branches. Leave your changes in the working tree.
- Do not edit `pyproject.toml` and do not install packages.
- Do not fetch anything from the network. Everything you need is in this tree.

## Agent contract

- **Verify:** `.venv/bin/ruff check <files you touched>`; `.venv/bin/ruff format --check <files you touched>`; `.venv/bin/mypy`
- **Tests:** subagents run none; they name the test files and the Orchestrator runs them.
- **Exclude from searches:** `.venv/`, `__pycache__/`, `.claude/`
- **Formatting:** ruff format; no hook runs it.
- **Read threshold:** 350 lines. Scratch files go to `.claude/tmp/` (gitignored).
