# Deviations from the upstream plugin (commit c8dfca7)

- 2026-10-19: `hooks/hooks.json` SessionStart matcher changed from `startup|resume|clear|compact` to
  `startup|resume|clear|compact|fork`, so the orchestration rules also load in sessions started with
  `--fork-session` (phase two forks existing sessions). Claude Code 2.1.214+ reports forks as `fork`,
  not `resume`. No effect on phase one, whose sessions all start fresh (`startup`).
