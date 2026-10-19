# Agent Kit versus plain Opus: a measured comparison

A test harness and the complete results of an A/B comparison between a plain Claude Code session on Opus 5.5 and the same session with the [claude-agent-kit](https://github.com/FlaviusBurghila/claude-agent-kit) plugin loaded. The plugin's claim is that cheaper models can take over reading, searching, and routine implementation through subagents so that the main Opus session keeps its context small and spends its tokens on judgment. We wanted to measure that rather than assume it.

- `results/REPORT.md` is the write-up with every table.
- `results/report.html` is a one-page visual summary; `results/method.html` is a method note written for the plugin's authors.
- `results/summary.md`, `results2/summary.md`, and the `runs.csv` files are the machine-generated tables.

## Headline

170 headless runs across two codebases. The plugin cost 21 to 26 percent more per task than a plain session in fresh sessions and about the same in chained ones, with identical automatic quality in all but one task. The extra cost is the roughly 5,000 tokens of rules and agent descriptions it adds to every call. Its context-saving mechanisms almost never engaged: delegation in 6 of 85 plugin runs, one read blocked by its hook, no compaction anywhere, because these tasks never came close to filling Opus 5.5's 1M-token window. The test therefore says nothing about the larger codebases and smaller context windows the plugin was designed for. The limits are spelled out in `results/method.html`.

## What was compared

| | A: plain | B: with the plugin |
|---|---|---|
| Claude Code 2.1.303, `claude -p`, Opus 5.5, effort high, bypass-permissions mode | yes | yes |
| User-level settings, hooks, plugins, and MCP servers | excluded | excluded |
| Project CLAUDE.md with the test and check commands | yes | yes, plus the plugin's "Agent contract" section |
| The plugin, loaded for the session with `--plugin-dir` | no | commit c8dfca7 plus `plugin.patch` |
| Same base commit, same prompt, repository reset before every run, auto-memory cleared | yes | yes |

Phase 1 used pallets/click at commit 2247b35: 17 tasks, each in a fresh session, 3 runs per task and condition. Phase 2 used the Voxglitch VCV Rack plugin at commit d32b18f: 8 tasks, each run both in a fresh session and as one step of a continued session that carries all eight tasks in order, 2 runs per task, condition, and session shape.

Tasks were chosen so a script can judge them: bug fixes and small features built by reverting real upstream commits with their tests held back as hidden tests, refactors checked by the full suite or a compile check, find-where questions with an answer key, and longer multi-step tasks. Every diff is also saved under a random id for blind grading. Two deliberate deviations are documented in `docs/deviations.md`: the plugin's startup hook was extended to fire on forked sessions, and one Voxglitch task is a seeded regression.

## Layout

```
config.json, config2.json          per-phase configuration (paths, model, flags, conditions)
task_specs.json, task_specs2.json  the authored task lists (frozen ids, prompt files, checks)
tasks/, tasks2/                    prompts, CLAUDE.md variants, hidden test sources, the Voxglitch check script
prices.json                        Anthropic list prices used for cost, with the date checked
make_tasks.py, make_tasks2.py      build the task repositories and base branches; --verify proves hidden tests fail before the fix
run.py, run2.py                    run tasks headlessly (run2.py adds chained sessions and shell-command checks)
lib/metrics.py                     token, cost, context, and subagent accounting from the saved outputs
summarize.py, report.py            tables with means and spread; the HTML report
results/, results2/                every run: run.json, result.json, init.json, command.json, diff, check outputs
blind/, blind2/                    diffs, prompts, and find-where answers under random ids, with the grading sheets
docs/deviations.md                 the two deliberate changes
plugin.patch, get_plugin.sh        the one-line plugin change and the script that fetches the plugin at c8dfca7
```

Not included: `private/` (the id-to-condition map and the answer keys, so grading stays blind), `tasks*/hidden/` (generated), `plugin/` (fetched by the script), and the full session streams and transcripts (88 MB; available on request). Everything the tables are computed from is here.

## Reproducing it

Requirements: Claude Code 2.1.303 or close, logged in; Python 3.11+; Node 18+ for the plugin's hooks; g++ and the VCV Rack SDK headers for phase 2 (path in `tasks2/repo_files/scripts/vg_check.sh`).

```sh
bash get_plugin.sh                              # the plugin at c8dfca7 with plugin.patch
python3 make_tasks.py --rebuild --verify         # phase 1: click task trees; hidden tests must fail on each base
python3 run.py --reps 3                          # 102 runs; re-running fills gaps only
python3 summarize.py --config config.json
python3 make_tasks2.py --rebuild --verify        # phase 2: Voxglitch task trees and chain bases
python3 run2.py --config config2.json --modes fresh,chain --reps 2
python3 summarize.py --config config2.json
python3 report.py --config config.json --config config2.json
```

Edit `config*.json` for your paths. The runs here used a Claude Max subscription, so nothing was billed; costs are list-price estimates from token counts, and they match Claude Code's own `total_cost_usd` to the cent.

## Fairness

If you consider another setup the fair one, for example a different Agent contract, another main model, or tasks of the shape the plugin was built for, every prompt, command, and check is a file here, and a run is one command. We would rather be corrected by a better experiment than argue about this one.
