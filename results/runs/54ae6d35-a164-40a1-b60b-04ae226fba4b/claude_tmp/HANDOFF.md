# HANDOFF
## Current: click.Duration param type
- [x] Builder: implement Duration in types.py, export, docs (parameter-types.md, api.md), tests
- [x] Review (Orchestrator read the diff directly; no Refuter spawned)
- [x] Orchestrator: run full test suite, ruff, mypy
Decisions: bool rejected (not treated as int); negative int rejected; OverflowError -> fail; ASCII digits only; no whitespace between number and unit.
