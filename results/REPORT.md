# Agent Kit versus plain Opus: results

Written 2026-10-19 from the saved runs in `results/` (phase 1, click) and `results2/` (phase 2, Voxglitch). Every number comes from `summarize.py` over the `run.json` files; the executive report is `results/report.html` and the method note is `results/method.html`.

## Phase 1: pallets/click, 17 tasks, 3 runs per task and condition, 102 runs

All 102 runs completed and ended with a normal result. No rate-limit pauses.

| Measure | A: plain Opus (n=51) | B: with the plugin (n=51) |
|---|---|---|
| Cost per run, mean (min to max) | $0.23 ($0.06 to $0.53) | $0.29 ($0.05 to $0.73) |
| Cost per run excluding the first call's cache write | $0.22 | $0.26 |
| Wall time per run, mean | 63 s | 77 s |
| Context at the end of the run, mean | 27,400 tokens | 32,500 tokens |
| Largest context seen, share of the 1M window | 4.2% | 5.2% |
| Compactions | 0 | 0 |
| Runs passing every automatic check | 50 of 51 | 48 of 51 |
| Reads denied by the plugin's hook | not applicable | 0 in 51 runs |
| Runs in which the plugin delegated to a subagent | not applicable | 2 of 51 |

By task type, cost per run and checks passed:

| Type | Runs per condition | A cost | B cost | A pass | B pass |
|---|---|---|---|---|---|
| Bug fix (6 tasks) | 18 | $0.20 | $0.24 | 18 of 18 | 18 of 18 |
| Small feature (2) | 6 | $0.34 | $0.40 | 6 of 6 | 6 of 6 |
| Refactor (3) | 9 | $0.32 | $0.46 | 9 of 9 | 9 of 9 |
| Find where (4) | 12 | $0.09 | $0.10 | 12 of 12 | 12 of 12 |
| Long (2) | 6 | $0.37 | $0.49 | 5 of 6 | 3 of 6 |

Reading of phase 1:

- The plugin cost 26% more per run on average, six cents. The pooled run-to-run standard deviation of cost is 16 cents, so the difference is inside the spread and is not established by this sample, although it has the same sign in every task type.
- The extra cost is the context the plugin adds. Condition B carried about 5,000 more tokens on every call: the orchestration rules injected at session start and the seven agent descriptions. Its first call also wrote more to the cache.
- The plugin almost never acted. Its read-budget hook ran on every Read and Bash call and denied nothing in 51 runs, because the sessions read files in ranges and with grep on their own. It delegated in 2 of 51 runs: a refuter review in one refactor run and a builder in one long run, 8 subagent calls in total.
- Quality was the same except on one task. Every failure is on L2, the long task that changes how click stores its help option: 1 of 3 A runs and 3 of 3 B runs missed the same stated requirement, a warning when a parameter claims the reserved storage name. With three runs per cell this is a hint, not a finding.
- Time followed cost: B took 13 seconds longer per run on average, also inside the spread.

## Phase 2: Voxglitch, 8 tasks, fresh and chained sessions, 68 runs

All 68 runs completed normally and every one of them passed every automatic check, in both conditions and both session shapes. No rate-limit pauses, no compactions.

Fresh sessions, one task each (16 runs per condition, 2 per task):

| Measure | A: plain Opus | B: with the plugin |
|---|---|---|
| Cost per task, mean (min to max) | $0.39 ($0.10 to $1.41) | $0.47 ($0.13 to $1.83) |
| Cost excluding the first call's cache write | $0.35 | $0.39 |
| Wall time per task, mean | 100 s | 93 s |
| Context at the end, mean | 38,900 tokens | 40,800 tokens |
| Runs passing every check | 16 of 16 | 16 of 16 |
| Runs in which the plugin delegated | not applicable | 2 of 16 |
| Reads denied by the plugin's hook | not applicable | 1 in 16 runs |

Chained sessions, the eight tasks in order inside one session (18 runs per condition, from one two-step pilot chain and two full eight-step chains):

| Measure | A: plain Opus | B: with the plugin |
|---|---|---|
| Cost per task, mean (min to max) | $0.40 ($0.13 to $1.41) | $0.42 ($0.08 to $1.24) |
| Cost of a full eight-task chain | $2.53 and $3.84 | $3.96 and $2.39 |
| Wall time per task, mean | 89 s | 116 s |
| Context at the end of a full chain | 141,800 and 176,500 tokens | 161,500 and 131,600 tokens |
| Runs passing every check | 18 of 18 | 18 of 18 |
| Runs in which the plugin delegated | not applicable | 2 of 18 |
| Reads denied by the plugin's hook | not applicable | 0 |

By task type, fresh sessions, cost per task (all checks passed in every cell):

| Type | Runs per condition | A cost | B cost |
|---|---|---|---|
| Find where (3 tasks) | 6 | $0.14 | $0.18 |
| Bug fix (1) | 2 | $0.35 | $0.35 |
| Feature (2) | 4 | $0.48 | $0.61 |
| Refactor (1) | 2 | $0.34 | $0.41 |
| Long (1) | 2 | $1.05 | $1.22 |

Cost and context by step along the chain, mean of the two full chains (plus the pilot chain for steps 1 and 2):

| Step | Task | A cost | A context | B cost | B context |
|---|---|---|---|---|---|
| 1 | Q1 | $0.17 | 25,900 | $0.22 | 30,100 |
| 2 | Q2 | $0.35 | 45,000 | $0.40 | 47,300 |
| 3 | Q3 | $0.13 | 43,800 | $0.08 | 41,300 |
| 4 | B1 | $0.68 | 80,900 | $0.78 | 78,500 |
| 5 | F1 | $0.22 | 91,000 | $0.16 | 84,700 |
| 6 | F2 | $0.52 | 112,500 | $0.50 | 103,000 |
| 7 | R1 | $0.41 | 130,600 | $0.49 | 124,400 |
| 8 | L1 | $0.91 | 159,100 | $0.83 | 146,600 |

Reading of phase 2:

- In fresh sessions the plugin again cost more, 21% on average, with a standard deviation larger than the difference. Quality was identical: every run in both conditions passed every hidden test, standalone test, and compile check.
- In chained sessions the two conditions cost the same within a few percent, and the plugin's sessions ended two of the chains with less context than the plain sessions and one with more. This is the first setting where the plugin's extra context was offset by something, but with two full chains per condition the offset is not measurable, and neither condition came within a sixth of the 1M window, so compaction never entered the picture.
- The plugin acted more here than on click, but still rarely: it delegated in 4 of 34 B runs, always on the two engine feature tasks (a builder on 8 and 13 calls in the chains, a refuter review on 3 and 8 calls in fresh runs, both reviews returning PASS), and its hook denied one read in 34 runs. The 2,929-line and 2,384-line headers in the find-where tasks were handled by both conditions with grep and ranged reads, without the hook ever intervening.
- Wall time is mixed: B was faster on fresh tasks and slower on chained tasks, with no consistent direction.
- The refactor task shows what blind grading will have to decide: every run compiled and reduced GrooveBox::process from about 400 lines to 19 to 28 lines, but whether the extractions are good is a judgment the checks cannot make.

## Across both phases

The plugin never lowered cost in any task type or session shape, and never changed the automatic quality result except on one click task where it did worse in a sample of three. Its added context cost 5,000 tokens per call, which is what the measured cost difference amounts to, and the mechanisms meant to save context, delegation and the read-budget hook, fired in 6 of 85 plugin runs. On these tasks, with this model and its 1M window, there was nothing for them to save.

What this does not show: how the plugin behaves with a person answering its questions, on a codebase an order of magnitude larger, on a 200K-window model with five-minute caches, or on tasks hard enough that a review gate catches mistakes the tests do not. Those are the conditions its design targets, and this test did not reach them.

## Blind grading

Diffs and find-where answers are saved under random ids in `blind/` and `blind2/`, with the id-to-condition mapping in `private/`. Scores entered in the grading sheets are picked up by `summarize.py` and `report.py`.
