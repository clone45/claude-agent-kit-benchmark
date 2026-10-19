# Summary of 68 completed runs

### Overall, chain sessions

| Measure | Condition A (n=18) | Condition B (n=18) |
|---|---|---|
| Cost per run, mean (min to max) | $0.40 ($0.13 to $1.41) | $0.42 ($0.08 to $1.24) |
| Cost stdev | $0.34 | $0.35 |
| Cost excluding first-call cache write | $0.39 ($0.11 to $1.40) | $0.39 ($0.07 to $1.23) |
| First-call cache write, tokens (cold start) | 2362 (1368 to 5267) | 3042 (1222 to 9447) |
| Opus share of cost | 100% | 93% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.03 ($0.00 to $0.32) |
| Wall time, seconds | 89 (16 to 328) | 116 (17 to 538) |
| Main-session API calls | 8 (3 to 20) | 9 (3 to 24) |
| Subagent API calls | 0 (0 to 0) | 1 (0 to 13) |
| Context at end, tokens | 80469 (24891 to 176483) | 77177 (29190 to 161458) |
| Context at end, share of window | 8.0% (max 17.6%) | 7.7% (max 16.1%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 100% | 100% |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | 100% | 100% |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.01 | pooled stdev 0.34: difference is smaller than the run-to-run spread |
| B minus A, wall time | +27.19 | pooled stdev 117.31: difference is smaller than the run-to-run spread |

### Task type: bugfix, chain sessions

| Measure | Condition A (n=2) | Condition B (n=2) |
|---|---|---|
| Cost per run, mean (min to max) | $0.68 ($0.61 to $0.74) | $0.78 ($0.75 to $0.81) |
| Cost stdev | $0.09 | $0.04 |
| Cost excluding first-call cache write | $0.66 ($0.60 to $0.72) | $0.77 ($0.74 to $0.80) |
| First-call cache write, tokens (cold start) | 1560 (1368 to 1753) | 1362 (1330 to 1394) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 186 (122 to 250) | 362 (186 to 538) |
| Main-session API calls | 18 (17 to 20) | 24 (23 to 24) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 0) |
| Context at end, tokens | 80894 (79196 to 82591) | 78524 (75919 to 81129) |
| Context at end, share of window | 8.1% (max 8.3%) | 7.9% (max 8.1%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 100% | 100% |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.10 | pooled stdev 0.07: difference is larger than the run-to-run spread |
| B minus A, wall time | +176.35 | pooled stdev 187.73: difference is smaller than the run-to-run spread |

### Task type: feature, chain sessions

| Measure | Condition A (n=5) | Condition B (n=5) |
|---|---|---|
| Cost per run, mean (min to max) | $0.45 ($0.18 to $0.76) | $0.45 ($0.15 to $0.95) |
| Cost stdev | $0.26 | $0.38 |
| Cost excluding first-call cache write | $0.43 ($0.17 to $0.74) | $0.44 ($0.14 to $0.93) |
| First-call cache write, tokens (cold start) | 1878 (1649 to 2172) | 1924 (1222 to 2425) |
| Opus share of cost | 100% | 90% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.04 ($0.00 to $0.22) |
| Wall time, seconds | 99 (40 to 183) | 123 (42 to 305) |
| Main-session API calls | 8 (4 to 14) | 9 (3 to 17) |
| Subagent API calls | 0 (0 to 0) | 2 (0 to 8) |
| Context at end, tokens | 94064 (63286 to 117319) | 88725 (68132 to 110389) |
| Context at end, share of window | 9.4% (max 11.7%) | 8.9% (max 11.0%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 100% | 100% |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.01 | pooled stdev 0.33: difference is smaller than the run-to-run spread |
| B minus A, wall time | +23.70 | pooled stdev 94.12: difference is smaller than the run-to-run spread |

### Task type: refactor, chain sessions

| Measure | Condition A (n=2) | Condition B (n=2) |
|---|---|---|
| Cost per run, mean (min to max) | $0.41 ($0.32 to $0.49) | $0.49 ($0.37 to $0.61) |
| Cost stdev | $0.11 | $0.17 |
| Cost excluding first-call cache write | $0.39 ($0.31 to $0.47) | $0.48 ($0.35 to $0.60) |
| First-call cache write, tokens (cold start) | 1638 (1568 to 1707) | 1758 (1690 to 1825) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 81 (43 to 120) | 87 (57 to 117) |
| Main-session API calls | 6 (5 to 8) | 8 (7 to 10) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 0) |
| Context at end, tokens | 130614 (126717 to 134511) | 124356 (115506 to 133206) |
| Context at end, share of window | 13.1% (max 13.5%) | 12.4% (max 13.3%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | n/a | n/a |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.08 | pooled stdev 0.15: difference is smaller than the run-to-run spread |
| B minus A, wall time | +5.70 | pooled stdev 48.62: difference is smaller than the run-to-run spread |

### Task type: find, chain sessions

| Measure | Condition A (n=7) | Condition B (n=7) |
|---|---|---|
| Cost per run, mean (min to max) | $0.15 ($0.13 to $0.18) | $0.15 ($0.08 to $0.24) |
| Cost stdev | $0.02 | $0.07 |
| Cost excluding first-call cache write | $0.12 ($0.11 to $0.14) | $0.11 ($0.07 to $0.16) |
| First-call cache write, tokens (cold start) | 3281 (1494 to 5267) | 4989 (1425 to 9447) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 26 (16 to 37) | 28 (17 to 39) |
| Main-session API calls | 4 (3 to 5) | 4 (3 to 6) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 0) |
| Context at end, tokens | 33836 (24891 to 44249) | 35242 (29190 to 42040) |
| Context at end, share of window | 3.4% (max 4.4%) | 3.5% (max 4.2%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | n/a | n/a |
| Full suite / standalone tests pass | n/a | n/a |
| Lint, types, compile pass | n/a | n/a |
| No file changes (find tasks) | 100% | 100% |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.00 | pooled stdev 0.05: difference is smaller than the run-to-run spread |
| B minus A, wall time | +2.50 | pooled stdev 7.68: difference is smaller than the run-to-run spread |

### Task type: long, chain sessions

| Measure | Condition A (n=2) | Condition B (n=2) |
|---|---|---|
| Cost per run, mean (min to max) | $0.91 ($0.40 to $1.41) | $0.83 ($0.42 to $1.24) |
| Cost stdev | $0.71 | $0.58 |
| Cost excluding first-call cache write | $0.89 ($0.39 to $1.40) | $0.82 ($0.40 to $1.23) |
| First-call cache write, tokens (cold start) | 1884 (1872 to 1896) | 1992 (1868 to 2115) |
| Opus share of cost | 100% | 81% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.16 ($0.00 to $0.32) |
| Wall time, seconds | 195 (62 to 328) | 190 (72 to 308) |
| Main-session API calls | 13 (7 to 19) | 12 (8 to 15) |
| Subagent API calls | 0 (0 to 0) | 6 (0 to 13) |
| Context at end, tokens | 159129 (141775 to 176483) | 146550 (131642 to 161458) |
| Context at end, share of window | 15.9% (max 17.6%) | 14.7% (max 16.1%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 100% | 100% |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | -0.08 | pooled stdev 0.65: difference is smaller than the run-to-run spread |
| B minus A, wall time | -5.35 | pooled stdev 177.42: difference is smaller than the run-to-run spread |

### Overall, fresh sessions

| Measure | Condition A (n=16) | Condition B (n=16) |
|---|---|---|
| Cost per run, mean (min to max) | $0.39 ($0.10 to $1.41) | $0.47 ($0.13 to $1.83) |
| Cost stdev | $0.33 | $0.43 |
| Cost excluding first-call cache write | $0.35 ($0.06 to $1.36) | $0.39 ($0.05 to $1.75) |
| First-call cache write, tokens (cold start) | 5576 (5223 to 6060) | 9761 (9410 to 10247) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 100 (19 to 428) | 93 (19 to 310) |
| Main-session API calls | 8 (3 to 24) | 10 (3 to 27) |
| Subagent API calls | 0 (0 to 0) | 1 (0 to 8) |
| Context at end, tokens | 38895 (20163 to 84738) | 40838 (23315 to 88740) |
| Context at end, share of window | 3.9% (max 8.5%) | 4.1% (max 8.9%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.1 (0.0 to 1.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 100% | 100% |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | 100% | 100% |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.08 | pooled stdev 0.38: difference is smaller than the run-to-run spread |
| B minus A, wall time | -6.84 | pooled stdev 98.16: difference is smaller than the run-to-run spread |

### Task type: bugfix, fresh sessions

| Measure | Condition A (n=2) | Condition B (n=2) |
|---|---|---|
| Cost per run, mean (min to max) | $0.35 ($0.27 to $0.43) | $0.35 ($0.30 to $0.41) |
| Cost stdev | $0.11 | $0.08 |
| Cost excluding first-call cache write | $0.31 ($0.23 to $0.38) | $0.27 ($0.22 to $0.33) |
| First-call cache write, tokens (cold start) | 5541 (5533 to 5549) | 9725 (9717 to 9733) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 245 (62 to 428) | 79 (64 to 93) |
| Main-session API calls | 10 (6 to 14) | 10 (9 to 11) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 0) |
| Context at end, tokens | 39868 (37060 to 42677) | 39210 (35290 to 43130) |
| Context at end, share of window | 4.0% (max 4.3%) | 3.9% (max 4.3%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 100% | 100% |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.00 | pooled stdev 0.10: difference is smaller than the run-to-run spread |
| B minus A, wall time | -166.55 | pooled stdev 183.59: difference is smaller than the run-to-run spread |

### Task type: feature, fresh sessions

| Measure | Condition A (n=4) | Condition B (n=4) |
|---|---|---|
| Cost per run, mean (min to max) | $0.48 ($0.32 to $0.61) | $0.61 ($0.36 to $1.00) |
| Cost stdev | $0.13 | $0.29 |
| Cost excluding first-call cache write | $0.44 ($0.27 to $0.56) | $0.53 ($0.28 to $0.92) |
| First-call cache write, tokens (cold start) | 5926 (5902 to 5952) | 10112 (10086 to 10138) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 99 (53 to 136) | 138 (64 to 214) |
| Main-session API calls | 8 (7 to 11) | 13 (9 to 18) |
| Subagent API calls | 0 (0 to 0) | 1 (0 to 3) |
| Context at end, tokens | 44917 (38313 to 48535) | 47246 (40486 to 53279) |
| Context at end, share of window | 4.5% (max 4.9%) | 4.7% (max 5.3%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 100% | 100% |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.13 | pooled stdev 0.23: difference is smaller than the run-to-run spread |
| B minus A, wall time | +38.98 | pooled stdev 61.49: difference is smaller than the run-to-run spread |

### Task type: refactor, fresh sessions

| Measure | Condition A (n=2) | Condition B (n=2) |
|---|---|---|
| Cost per run, mean (min to max) | $0.34 ($0.27 to $0.41) | $0.41 ($0.39 to $0.43) |
| Cost stdev | $0.10 | $0.03 |
| Cost excluding first-call cache write | $0.29 ($0.22 to $0.37) | $0.33 ($0.32 to $0.35) |
| First-call cache write, tokens (cold start) | 5445 (5437 to 5453) | 9626 (9618 to 9635) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 73 (61 to 86) | 102 (98 to 106) |
| Main-session API calls | 8 (7 to 10) | 11 (11 to 11) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 0) |
| Context at end, tokens | 35406 (34488 to 36324) | 38418 (36659 to 40178) |
| Context at end, share of window | 3.5% (max 3.6%) | 3.8% (max 4.0%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.5 (0.0 to 1.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | n/a | n/a |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.07 | pooled stdev 0.07: difference is smaller than the run-to-run spread |
| B minus A, wall time | +28.60 | pooled stdev 12.81: difference is larger than the run-to-run spread |

### Task type: find, fresh sessions

| Measure | Condition A (n=6) | Condition B (n=6) |
|---|---|---|
| Cost per run, mean (min to max) | $0.14 ($0.10 to $0.18) | $0.18 ($0.13 to $0.20) |
| Cost stdev | $0.03 | $0.03 |
| Cost excluding first-call cache write | $0.10 ($0.06 to $0.13) | $0.10 ($0.05 to $0.13) |
| First-call cache write, tokens (cold start) | 5239 (5223 to 5256) | 9424 (9410 to 9439) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 26 (19 to 37) | 26 (19 to 30) |
| Main-session API calls | 4 (3 to 5) | 4 (3 to 5) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 0) |
| Context at end, tokens | 23178 (20163 to 25427) | 27046 (23315 to 29314) |
| Context at end, share of window | 2.3% (max 2.5%) | 2.7% (max 2.9%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | n/a | n/a |
| Full suite / standalone tests pass | n/a | n/a |
| Lint, types, compile pass | n/a | n/a |
| No file changes (find tasks) | 100% | 100% |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.04 | pooled stdev 0.03: difference is larger than the run-to-run spread |
| B minus A, wall time | +0.15 | pooled stdev 5.72: difference is smaller than the run-to-run spread |

### Task type: long, fresh sessions

| Measure | Condition A (n=2) | Condition B (n=2) |
|---|---|---|
| Cost per run, mean (min to max) | $1.05 ($0.69 to $1.41) | $1.22 ($0.60 to $1.83) |
| Cost stdev | $0.51 | $0.87 |
| Cost excluding first-call cache write | $1.00 ($0.64 to $1.36) | $1.14 ($0.52 to $1.75) |
| First-call cache write, tokens (cold start) | 6052 (6045 to 6060) | 10239 (10231 to 10247) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 204 (111 to 296) | 209 (107 to 310) |
| Main-session API calls | 18 (13 to 24) | 20 (12 to 27) |
| Subagent API calls | 0 (0 to 0) | 4 (0 to 8) |
| Context at end, tokens | 76522 (68305 to 84738) | 73444 (58148 to 88740) |
| Context at end, share of window | 7.7% (max 8.5%) | 7.3% (max 8.9%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 100% | 100% |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.17 | pooled stdev 0.71: difference is smaller than the run-to-run spread |
| B minus A, wall time | +4.80 | pooled stdev 137.33: difference is smaller than the run-to-run spread |

### Chained session, by step

| Step | Task | Cond | n | Cost mean | Context at end | Checks pass |
|---|---|---|---|---|---|---|
| 1 | Q1 | A | 3 | $0.17 | 25870 | 100% |
| 1 | Q1 | B | 3 | $0.22 | 30086 | 100% |
| 2 | Q2 | A | 3 | $0.35 | 44965 | 100% |
| 2 | Q2 | B | 3 | $0.40 | 47334 | 100% |
| 3 | Q3 | A | 2 | $0.13 | 43816 | 100% |
| 3 | Q3 | B | 2 | $0.08 | 41284 | 100% |
| 4 | B1 | A | 2 | $0.68 | 80894 | 100% |
| 4 | B1 | B | 2 | $0.78 | 78524 | 100% |
| 5 | F1 | A | 2 | $0.22 | 90994 | 100% |
| 5 | F1 | B | 2 | $0.16 | 84745 | 100% |
| 6 | F2 | A | 2 | $0.52 | 112523 | 100% |
| 6 | F2 | B | 2 | $0.50 | 103001 | 100% |
| 7 | R1 | A | 2 | $0.41 | 130614 | 100% |
| 7 | R1 | B | 2 | $0.49 | 124356 | 100% |
| 8 | L1 | A | 2 | $0.91 | 159129 | 100% |
| 8 | L1 | B | 2 | $0.83 | 146550 | 100% |

### Per task

| Task | Type | Mode | Cond | n | Cost mean | Cost min to max | Wall s | Context end | Checks pass | Hidden pass | Grade |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | bugfix | chain | A | 2 | $0.68 | $0.61 to $0.74 | 186 | 80894 | 100% | 100% | n/a |
| B1 | bugfix | chain | B | 2 | $0.78 | $0.75 to $0.81 | 362 | 78524 | 100% | 100% | n/a |
| B1 | bugfix | fresh | A | 2 | $0.35 | $0.27 to $0.43 | 245 | 39868 | 100% | 100% | n/a |
| B1 | bugfix | fresh | B | 2 | $0.35 | $0.30 to $0.41 | 79 | 39210 | 100% | 100% | n/a |
| F1 | feature | chain | A | 3 | $0.40 | $0.18 to $0.76 | 92 | 81758 | 100% | 100% | n/a |
| F1 | feature | chain | B | 3 | $0.42 | $0.15 to $0.95 | 130 | 79207 | 100% | 100% | n/a |
| F1 | feature | fresh | A | 2 | $0.45 | $0.32 to $0.58 | 95 | 42253 | 100% | 100% | n/a |
| F1 | feature | fresh | B | 2 | $0.71 | $0.41 to $1.00 | 147 | 49265 | 100% | 100% | n/a |
| F2 | feature | chain | A | 2 | $0.52 | $0.33 to $0.70 | 110 | 112523 | 100% | 100% | n/a |
| F2 | feature | chain | B | 2 | $0.50 | $0.22 to $0.78 | 112 | 103001 | 100% | 100% | n/a |
| F2 | feature | fresh | A | 2 | $0.52 | $0.43 to $0.61 | 103 | 47580 | 100% | 100% | n/a |
| F2 | feature | fresh | B | 2 | $0.52 | $0.36 to $0.67 | 129 | 45226 | 100% | 100% | n/a |
| L1 | long | chain | A | 2 | $0.91 | $0.40 to $1.41 | 195 | 159129 | 100% | 100% | n/a |
| L1 | long | chain | B | 2 | $0.83 | $0.42 to $1.24 | 190 | 146550 | 100% | 100% | n/a |
| L1 | long | fresh | A | 2 | $1.05 | $0.69 to $1.41 | 204 | 76522 | 100% | 100% | n/a |
| L1 | long | fresh | B | 2 | $1.22 | $0.60 to $1.83 | 209 | 73444 | 100% | 100% | n/a |
| Q1 | find | chain | A | 3 | $0.17 | $0.15 to $0.18 | 27 | 25870 | 100% | n/a | n/a |
| Q1 | find | chain | B | 3 | $0.22 | $0.21 to $0.24 | 35 | 30086 | 100% | n/a | n/a |
| Q1 | find | fresh | A | 2 | $0.17 | $0.16 to $0.18 | 32 | 25328 | 100% | n/a | n/a |
| Q1 | find | fresh | B | 2 | $0.20 | $0.20 to $0.20 | 29 | 28420 | 100% | n/a | n/a |
| Q2 | find | chain | A | 2 | $0.14 | $0.13 to $0.16 | 27 | 35805 | 100% | n/a | n/a |
| Q2 | find | chain | B | 2 | $0.12 | $0.11 to $0.13 | 27 | 36934 | 100% | n/a | n/a |
| Q2 | find | fresh | A | 2 | $0.15 | $0.14 to $0.15 | 24 | 23286 | 100% | n/a | n/a |
| Q2 | find | fresh | B | 2 | $0.19 | $0.18 to $0.20 | 29 | 28135 | 100% | n/a | n/a |
| Q3 | find | chain | A | 2 | $0.13 | $0.13 to $0.13 | 22 | 43816 | 100% | n/a | n/a |
| Q3 | find | chain | B | 2 | $0.08 | $0.08 to $0.08 | 18 | 41284 | 100% | n/a | n/a |
| Q3 | find | fresh | A | 2 | $0.11 | $0.10 to $0.12 | 21 | 20920 | 100% | n/a | n/a |
| Q3 | find | fresh | B | 2 | $0.14 | $0.13 to $0.16 | 20 | 24584 | 100% | n/a | n/a |
| R1 | refactor | chain | A | 2 | $0.41 | $0.32 to $0.49 | 81 | 130614 | 100% | n/a | n/a |
| R1 | refactor | chain | B | 2 | $0.49 | $0.37 to $0.61 | 87 | 124356 | 100% | n/a | n/a |
| R1 | refactor | fresh | A | 2 | $0.34 | $0.27 to $0.41 | 73 | 35406 | 100% | n/a | n/a |
| R1 | refactor | fresh | B | 2 | $0.41 | $0.39 to $0.43 | 102 | 38418 | 100% | n/a | n/a |

Blind grades recorded: 0 of 68 runs.