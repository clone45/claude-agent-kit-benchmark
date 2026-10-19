# claude-agent-kit vs plain Opus: experiment plan

Status: proposed 2026-10-18, awaiting approval. Nothing that costs money has run.

## 1. What the plugin does (read in full, commit c8dfca7, v1.0.0, one commit, MIT)

Files: 2 hook scripts, 7 agent definitions, orchestration rules, 2 skills, an installer, templates, tests.

Hooks (`hooks/hooks.json`), both `node` scripts, 10 s timeout, both fail open:

| Event | Matcher | Script | What it does |
|---|---|---|---|
| SessionStart | startup, resume, clear, compact | `agent-kit/hooks/session-start.js` | Reads `agents/*.md` names and `agent-kit/orchestration.md`; checks `~/.claude/CLAUDE.md`, `<project>/CLAUDE.md`, `<project>/.claude/CLAUDE.md` for a script-install marker; prints the orchestration rules (9,256 chars) as `additionalContext`. No writes, no network. |
| PreToolUse | Read, Bash | `agent-kit/hooks/shunt.js` | Parses the tool input. For `Read`, resolves the path and counts lines of the target file (reads the whole file into memory, up to 64 MB, binary sniff on first 8 KB). For `Bash`, tokenizes the command, detects `cat`, `bat`, `less`, `more`, `nl`, `tac`, `head`, `tail`, `sed`, `git show <rev>:<path>`, `rtk read`, and skips stages piped into a filter or redirected to a file. If more than 350 lines would reach the context, returns `permissionDecision: deny` with a reason that tells the model to use the `agent-kit:bulk-reader` agent or a ranged Read. Applies to the main session and to the `builder`, `refuter`, `debugger` subagents; exempt for every other agent type. `SHUNT_OFF=1` disables; `SHUNT_MIN_LINES` sets the threshold. No writes, no network, no exec. |

Agents (`agents/*.md`), all with `disallowedTools: Agent` so none can spawn agents:

| Agent | Model | Effort | Caps | Can edit |
|---|---|---|---|---|
| scout | haiku | medium | maxTurns 25 | no |
| bulk-reader | haiku | medium | maxTurns 20 | no |
| code-writer | haiku | medium | maxTurns 30 | yes, named target files only |
| researcher | sonnet | medium | | no |
| builder | sonnet | medium | | yes |
| refuter | opus | medium | | no |
| debugger | opus | high | | no (told not to implement) |

None sets `permissionMode`, so they inherit the session's mode. Builder and code-writer are told to run static checks only, never tests.

Skills: `/agent-kit:init` writes an "Agent contract" section into the project CLAUDE.md and adds `.claude/tmp/` to `.gitignore`; `/agent-kit:doctor` is read-only. Both are `disable-model-invocation: true` (user-invoked only).

Installer (`install.sh`): modifies `~/.claude/settings.json`, `CLAUDE.md`, `.gitignore`, copies agents; backs up first. README suggests `curl | bash`. We will not use it; `--plugin-dir` loads the plugin for one session with no writes.

Risk assessment: nothing phones home, nothing obfuscated, no destructive commands. Points worth knowing:
- `shunt.js` opens and fully reads any local file named in a Read or Bash call to count its lines, including files outside the repo. Local only.
- The Bash parsing is heuristic and easy to bypass (for example `python3 -c "print(open(f).read())"`); it is a nudge, not a guard.
- The deny reason is injected into the model's context and steers it toward the plugin's agents.
- Verified locally: `claude plugin validate --strict` passes; the plugin's own 71 hook test cases and 30 packaging checks pass with Node 22.

## 2. Verified facts (docs at code.claude.com, pricing at platform.claude.com, checked 2026-10-18)

- Headless run: `claude -p "<prompt>" --output-format json`; `stream-json` with `--verbose` emits one JSON event per line and ends with a `result` event.
- `result` fields (docs plus a real result from the 2026-10-02 runs): `total_cost_usd`, `usage` (input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens, `cache_creation.ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens`), `modelUsage` keyed by model id (inputTokens, outputTokens, thinkingTokens, cacheReadInputTokens, cacheCreationInputTokens, costUSD, contextWindow, maxOutputTokens, costBasis), `duration_ms`, `duration_api_ms`, `num_turns`, `session_id`, `is_error`, `subtype`, `result`, `permission_denials`, `subagent_stats` (spawned, by_type, completed, failed).
- Subagents: `total_cost_usd` and `modelUsage` include subagent requests; `usage` excludes them. Costs are client-side estimates at list price.
- Per-message `output_tokens` on streamed assistant events is a placeholder taken at message start; read output totals from `result`. Input and cache counts per message are accurate. In my check of a 2026-10-02 transcript, the on-disk main transcript's output tokens deduplicated by request id matched the session cost record exactly.
- Transcripts: `~/.claude/projects/<cwd-escaped>/<session-id>.jsonl`; subagents at `<session-id>/subagents/agent-<id>.jsonl` plus `.meta.json` with `agentType` and `model`. Assistant records carry `message.model` and `message.usage`. Format is documented as internal and unstable.
- Compaction is recorded as a `system` record with `subtype: compact_boundary` and `compactMetadata.preTokens` / `postTokens` / `trigger`.
- Opus 5.5 runs with a 1M context window by default in Claude Code (`contextWindow: 1000000` in a real result; docs: Opus 4.7 and later run 1M by default, auto-compact at about 967K).
- Aliases on the Anthropic API: `opus` = Opus 5.5, `sonnet` = Sonnet 5.5, `haiku` = Haiku 5.5. Opus 5.5 default effort is `medium` unless set.
- Claude Code's own helper calls use `claude-haiku-4-5-20251001` even with no subagents (seen in sessions with no subagent directory), so Haiku 5.5 usage can be attributed to the plugin and Haiku 4.5 to built-ins.
- Plugin install at project scope: `claude plugin marketplace add FlaviusBurghila/claude-agent-kit` then `claude plugin install agent-kit@agent-kit --scope project` writes `enabledPlugins` into `.claude/settings.json` (marketplace is declared in user settings); uninstall with `claude plugin uninstall agent-kit@agent-kit --scope project`. `--plugin-dir <path>` loads a plugin for one session and writes nothing to settings; plugin hooks run in subagents and in `-p` mode. Recommended for this test.
- Hook input carries `agent_id` and `agent_type`; SessionStart `additionalContext` is capped at 10,000 chars.
- This machine: Claude Code 2.1.303, Node 22.15, Python 3.13, logged in via claude.ai on a Max subscription. Runs draw plan quota, not dollars; all cost figures are list-price equivalents.

Prices, USD per million tokens (`prices.json`):

| Model | Input | 5m cache write | 1h cache write | Cache read | Output |
|---|---|---|---|---|---|
| Opus 5.5 | 4.00 | 5.00 | 8.00 | 0.20 | 20.00 |
| Sonnet 5.5 | 2.00 | 2.50 | 4.00 | 0.10 | 10.00 |
| Haiku 5.5 (prompt up to 100K) | 0.10 | 0.125 | 0.20 | 0.01 | 0.50 |
| Haiku 5.5 (prompt over 100K) | 0.50 | 0.625 | 1.00 | 0.05 | 2.50 |
| Haiku 4.5 (built-in helpers) | 1.00 | 1.25 | 2.00 | 0.10 | 5.00 |

## 3. Test design

### Repo

pallets/click at commit 2247b35 (2026-10-04). Python, 12,930 source lines, 59 test files, full suite in about 6 s, ruff and mypy configured and clean. Six source files exceed the plugin's 350-line threshold (core.py 4,038; types.py 1,437; termui.py 1,024), so the read-budget hook will actually fire.

Each task gets its own base: a single squashed commit of the click tree with the task's source-and-test changes reverse-applied, `CHANGES.md` removed (it describes the fixes), and a shared `CLAUDE.md` added. No history to mine. The venv lives outside the repo. Before every run: `git reset --hard <base> && git clean -fd`.

### Tasks (17)

Bug fixes, hidden tests from the real fix commit (B):

| Id | Commit | Area | Hidden tests |
|---|---|---|---|
| B1 | f67c2bb | short-help abbreviation (utils.py) | 6 |
| B2 | 6f85d26 | BytesWarning in Path type under python -bb (types.py) | 1 |
| B3 | f58ca3e | Sentinel copy/deepcopy/pickle (_utils.py) | 3 |
| B4 | f316d5c | progress bar final position (_termui_impl.py) | 6 |
| B5 | 047adef | help option names declaration order (core.py) | 4 |
| B6 | 762c97e | double-bracketed choices in synopsis (core.py) | 2 |

Small features, hidden tests from the real commit (F):

| Id | Commit | Area | Hidden tests |
|---|---|---|---|
| F1 | a1d8785 | pathlib.Path support in click.edit (termui.py, _termui_impl.py) | 1 |
| F2 | 22177f8 | path_type narrows the converted value's type (types.py) | 1 |

Refactors, full suite plus ruff and mypy must pass, blind diff grading (R):

| Id | Task |
|---|---|
| R1 | Extract color-code validation and lookup from `termui.style` (125 lines) into helpers; behavior unchanged |
| R2 | Convert percent-formatting and `.format()` in exceptions.py and types.py to f-strings where semantics are identical |
| R3 | Split `testing.CliRunner.isolation` (196 lines) into stream-setup and restore helpers; behavior unchanged |

Find-where questions, graded against an answer key (Q):

| Id | Question | Key |
|---|---|---|
| Q1 | Where does click decide whether to strip ANSI codes from echo output, and on what inputs? | utils.echo calling _compat.should_strip_ansi with resolve_color_default |
| Q2 | Where is help text width determined; what are the default and minimum? | formatting.HelpFormatter.__init__ (80 default, min 50), Context.terminal_width override |
| Q3 | Where does a Group with no arguments decide to show help instead of running its callback? | Command.parse_args no_args_is_help check; Group defaults from invoke_without_command |
| Q4 | Which code resolves a parameter's value from environment variables, and how does auto_envvar_prefix reach it? | Parameter/Option.resolve_envvar_value and Context.auto_envvar_prefix composition |

Long multi-step (L):

| Id | Task | Check |
|---|---|---|
| L1 | Add a `click.Duration` ParamType parsing strings like `90s`, `5m`, `1h30m` into `datetime.timedelta`, with `to_info_dict`, export from `click/__init__.py`, a docs entry, and tests | about 10 hidden acceptance tests written by me, plus full suite, ruff, mypy |
| L2 | Warn when an argument name collides with other parameters (commit 3495fba; touches core.py and 4 test files) | 13 hidden tests |

Task prompts describe the bug or feature in plain language (no commit references), state the test command, and say: work autonomously, do not ask questions, do not commit, finish by running the test suite.

### Conditions

| | A: plain | B: plugin |
|---|---|---|
| Model | `--model opus --effort high` | same |
| Plugin | none | `--plugin-dir <clone of c8dfca7>` |
| CLAUDE.md | shared text: project description, test and lint commands | shared text plus the plugin's "## Agent contract" section (Verify: ruff check, ruff format --check, mypy src; Tests: subagents run none; Exclude: .venv; Read threshold: 350) |
| Everything else | identical: `--setting-sources project,local --strict-mcp-config --permission-mode bypassPermissions --max-budget-usd 15 --output-format stream-json --verbose --forward-subagent-text`, same base commit, same prompt, Claude Code 2.1.303 | |

`--setting-sources project,local` keeps the user-level settings out of both conditions (content-filter hooks on every tool call, five enabled plugins, the fable model default). `--strict-mcp-config` drops the user-scope MCP servers (gmail, linear, playwright, chrome-devtools). `~/.claude/CLAUDE.md` still loads in both. The pilot verifies all of this from the `system/init` event.

### Repetitions

3 runs per task per condition: 17 x 2 x 3 = 102 runs. Sequential, about 8 to 12 hours of wall time, likely spread over more than one day because Max plan rate limits will pause the runner.

### Measurements per run

| Measure | Source |
|---|---|
| Input, output, cache read, cache write tokens by model | `result.modelUsage`; 5m/1h cache-write split from per-call `cache_creation` in the stream |
| Cost | tokens x `prices.json`; `total_cost_usd` kept beside it as a cross-check |
| Wall time | runner clock; `duration_ms` and `duration_api_ms` from `result` |
| Tests pass | hidden tests, full suite, ruff, mypy, run by the harness after the session ends |
| Rework (B only) | refuter transcripts whose verdict line says FAIL; builder spawns after a FAIL |
| Context at end, compaction | last main-session API call's input + cache_read + cache_creation over `contextWindow`; count of `compact_boundary` records |
| Subagent usage | `subagent_stats.by_type` and the subagent transcripts (model, call count) |
| Final diff | `git diff` saved as `blind/<uuid>.diff`; find-where answers as `blind/<uuid>.answer.md` |

Blind grading: the `blind/` folder holds only the artifact and the task prompt; `private/mapping.json` maps uuid to task, condition, run. You grade without the mapping.

### Scripts (all in /mnt/c/Code/routing_test)

- `make_tasks.py`: builds the per-task base commits in a scratch clone, writes `tasks.json`, hidden test manifests, and the answer key.
- `run.py`: loops tasks x conditions x reps (or a chosen subset), resets the repo, runs `claude -p`, saves `stream.jsonl`, `result.json`, stderr, the final diff, copies the main and subagent transcripts, runs the hidden tests and linters, writes `run.json`. Detects rate-limit errors and pauses.
- `summarize.py`: reads `results/`, prices tokens, and writes a per-task-type and overall table with mean, median, min, max and the spread between runs, plus a CSV.

## 4. Cost estimate (list-price equivalent)

| Scenario | Per run A | Per run B | Runs | Subtotal |
|---|---|---|---|---|
| Short tasks (15) | 1.00 to 2.50 | 1.50 to 3.50 | 90 | 110 to 270 |
| Long tasks (2) | 4 to 8 | 5 to 10 | 12 | 55 to 110 |
| Total | | | 102 | roughly 165 to 380 |

The uncertainty is about 2x in each direction until the pilot calibrates it. On the Max plan this is quota rather than dollars.

Pilot: B1 and Q1, one run each in both conditions, 4 runs, estimated 5 to 10 in list-price terms. After it I report the measured per-run cost, show the pilot results, confirm the init event shows the right plugins and hooks, and give a refined full-run estimate before continuing.

## 5. Open choices for approval

1. Repo: click as above, or one of yours.
2. Permission mode: bypassPermissions in a scratch clone with a 15 USD per-run budget cap, or acceptEdits plus an allowlist for pytest, ruff, mypy and git.
3. Repetitions: 3 per cell as proposed, or 5 on a subset.
4. Loading the plugin with `--plugin-dir` rather than a real project-scope install.
