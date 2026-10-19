# Summary of 102 completed runs

### Overall

| Measure | Condition A (n=51) | Condition B (n=51) |
|---|---|---|
| Cost per run, mean (min to max) | $0.23 ($0.06 to $0.53) | $0.29 ($0.05 to $0.73) |
| Cost stdev | $0.13 | $0.18 |
| Cost excluding first-call cache write | $0.22 ($0.06 to $0.49) | $0.26 ($0.05 to $0.67) |
| First-call cache write, tokens (cold start) | 1962 (0 to 5664) | 3978 (0 to 21243) |
| Opus share of cost | 100% | 99% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.10) |
| Wall time, seconds | 63 (11 to 127) | 77 (15 to 192) |
| Main-session API calls | 8 (3 to 15) | 9 (3 to 23) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 4) |
| Context at end, tokens | 27378 (19481 to 42329) | 32532 (22924 to 51649) |
| Context at end, share of window | 2.7% (max 4.2%) | 3.3% (max 5.2%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 97% | 90% |
| Full suite / standalone tests pass | 97% | 92% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | 100% | 100% |
| All automatic checks pass | 98% | 94% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.06 | pooled stdev 0.16: difference is smaller than the run-to-run spread |
| B minus A, wall time | +13.24 | pooled stdev 40.84: difference is smaller than the run-to-run spread |

### Task type: bugfix

| Measure | Condition A (n=18) | Condition B (n=18) |
|---|---|---|
| Cost per run, mean (min to max) | $0.20 ($0.09 to $0.32) | $0.24 ($0.10 to $0.38) |
| Cost stdev | $0.06 | $0.08 |
| Cost excluding first-call cache write | $0.19 ($0.09 to $0.28) | $0.20 ($0.10 to $0.31) |
| First-call cache write, tokens (cold start) | 2080 (0 to 5584) | 4988 (0 to 21243) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 61 (28 to 82) | 63 (28 to 107) |
| Main-session API calls | 9 (6 to 12) | 9 (5 to 13) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 0) |
| Context at end, tokens | 25243 (20365 to 29584) | 29440 (25210 to 35347) |
| Context at end, share of window | 2.5% (max 3.0%) | 2.9% (max 3.5%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 100% | 100% |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.03 | pooled stdev 0.07: difference is smaller than the run-to-run spread |
| B minus A, wall time | +1.33 | pooled stdev 16.91: difference is smaller than the run-to-run spread |

### Task type: feature

| Measure | Condition A (n=6) | Condition B (n=6) |
|---|---|---|
| Cost per run, mean (min to max) | $0.34 ($0.22 to $0.53) | $0.40 ($0.27 to $0.58) |
| Cost stdev | $0.11 | $0.12 |
| Cost excluding first-call cache write | $0.32 ($0.22 to $0.49) | $0.37 ($0.23 to $0.50) |
| First-call cache write, tokens (cold start) | 1802 (0 to 5527) | 3204 (0 to 9731) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 92 (55 to 118) | 95 (73 to 123) |
| Main-session API calls | 10 (8 to 14) | 12 (8 to 17) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 0) |
| Context at end, tokens | 34107 (29127 to 42329) | 39415 (32176 to 44583) |
| Context at end, share of window | 3.4% (max 4.2%) | 3.9% (max 4.5%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 100% | 100% |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.06 | pooled stdev 0.12: difference is smaller than the run-to-run spread |
| B minus A, wall time | +3.12 | pooled stdev 22.07: difference is smaller than the run-to-run spread |

### Task type: refactor

| Measure | Condition A (n=9) | Condition B (n=9) |
|---|---|---|
| Cost per run, mean (min to max) | $0.32 ($0.19 to $0.52) | $0.46 ($0.20 to $0.72) |
| Cost stdev | $0.12 | $0.19 |
| Cost excluding first-call cache write | $0.31 ($0.18 to $0.48) | $0.44 ($0.20 to $0.67) |
| First-call cache write, tokens (cold start) | 1724 (0 to 5190) | 3125 (0 to 9393) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 90 (52 to 127) | 126 (60 to 175) |
| Main-session API calls | 7 (4 to 9) | 9 (7 to 11) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 4) |
| Context at end, tokens | 30555 (24250 to 38853) | 38240 (29081 to 48887) |
| Context at end, share of window | 3.1% (max 3.9%) | 3.8% (max 4.9%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | n/a | n/a |
| Full suite / standalone tests pass | 100% | 100% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.14 | pooled stdev 0.16: difference is smaller than the run-to-run spread |
| B minus A, wall time | +35.50 | pooled stdev 39.33: difference is smaller than the run-to-run spread |

### Task type: find

| Measure | Condition A (n=12) | Condition B (n=12) |
|---|---|---|
| Cost per run, mean (min to max) | $0.09 ($0.06 to $0.11) | $0.10 ($0.05 to $0.15) |
| Cost stdev | $0.02 | $0.04 |
| Cost excluding first-call cache write | $0.07 ($0.06 to $0.09) | $0.07 ($0.05 to $0.09) |
| First-call cache write, tokens (cold start) | 2083 (0 to 5023) | 3836 (0 to 9230) |
| Opus share of cost | 100% | 100% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.00 ($0.00 to $0.00) |
| Wall time, seconds | 18 (11 to 23) | 24 (15 to 47) |
| Main-session API calls | 4 (3 to 5) | 4 (3 to 5) |
| Subagent API calls | 0 (0 to 0) | 0 (0 to 0) |
| Context at end, tokens | 20462 (19481 to 22426) | 24347 (22924 to 26675) |
| Context at end, share of window | 2.0% (max 2.2%) | 2.4% (max 2.7%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | n/a | n/a |
| Full suite / standalone tests pass | n/a | n/a |
| Lint, types, compile pass | n/a | n/a |
| No file changes (find tasks) | 100% | 100% |
| All automatic checks pass | 100% | 100% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.02 | pooled stdev 0.03: difference is smaller than the run-to-run spread |
| B minus A, wall time | +6.02 | pooled stdev 7.31: difference is smaller than the run-to-run spread |

### Task type: long

| Measure | Condition A (n=6) | Condition B (n=6) |
|---|---|---|
| Cost per run, mean (min to max) | $0.37 ($0.29 to $0.46) | $0.49 ($0.39 to $0.73) |
| Cost stdev | $0.07 | $0.13 |
| Cost excluding first-call cache write | $0.36 ($0.29 to $0.41) | $0.46 ($0.39 to $0.65) |
| First-call cache write, tokens (cold start) | 1881 (0 to 5664) | 3282 (0 to 9869) |
| Opus share of cost | 100% | 96% |
| Sonnet + Haiku cost per run | $0.00 ($0.00 to $0.00) | $0.02 ($0.00 to $0.10) |
| Wall time, seconds | 92 (83 to 109) | 132 (89 to 192) |
| Main-session API calls | 11 (9 to 15) | 15 (11 to 23) |
| Subagent API calls | 0 (0 to 0) | 1 (0 to 4) |
| Context at end, tokens | 36124 (32348 to 38956) | 42734 (38985 to 51649) |
| Context at end, share of window | 3.6% (max 3.9%) | 4.3% (max 5.2%) |
| Compactions | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Read-budget denials (hook) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Refuter FAIL verdicts (rework) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| Hidden tests pass | 83% | 50% |
| Full suite / standalone tests pass | 83% | 50% |
| Lint, types, compile pass | 100% | 100% |
| No file changes (find tasks) | n/a | n/a |
| All automatic checks pass | 83% | 50% |
| Blind grade, mean 1 to 5 | n/a | n/a |
| B minus A, cost | +0.12 | pooled stdev 0.10: difference is larger than the run-to-run spread |
| B minus A, wall time | +40.13 | pooled stdev 25.22: difference is larger than the run-to-run spread |

### Per task

| Task | Type | Mode | Cond | n | Cost mean | Cost min to max | Wall s | Context end | Checks pass | Hidden pass | Grade |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | bugfix | fresh | A | 3 | $0.21 | $0.19 to $0.22 | 61 | 24398 | 100% | 100% | n/a |
| B1 | bugfix | fresh | B | 3 | $0.29 | $0.18 to $0.36 | 58 | 28464 | 100% | 100% | n/a |
| B2 | bugfix | fresh | A | 3 | $0.17 | $0.13 to $0.21 | 58 | 23993 | 100% | 100% | n/a |
| B2 | bugfix | fresh | B | 3 | $0.17 | $0.13 to $0.24 | 63 | 26315 | 100% | 100% | n/a |
| B3 | bugfix | fresh | A | 3 | $0.22 | $0.20 to $0.26 | 79 | 25331 | 100% | 100% | n/a |
| B3 | bugfix | fresh | B | 3 | $0.23 | $0.19 to $0.32 | 64 | 29120 | 100% | 100% | n/a |
| B4 | bugfix | fresh | A | 3 | $0.22 | $0.17 to $0.28 | 61 | 27223 | 100% | 100% | n/a |
| B4 | bugfix | fresh | B | 3 | $0.27 | $0.23 to $0.33 | 66 | 34482 | 100% | 100% | n/a |
| B5 | bugfix | fresh | A | 3 | $0.14 | $0.09 to $0.20 | 39 | 22000 | 100% | 100% | n/a |
| B5 | bugfix | fresh | B | 3 | $0.15 | $0.10 to $0.18 | 36 | 25961 | 100% | 100% | n/a |
| B6 | bugfix | fresh | A | 3 | $0.27 | $0.23 to $0.32 | 71 | 28511 | 100% | 100% | n/a |
| B6 | bugfix | fresh | B | 3 | $0.30 | $0.26 to $0.38 | 89 | 32299 | 100% | 100% | n/a |
| F1 | feature | fresh | A | 3 | $0.25 | $0.22 to $0.30 | 82 | 30558 | 100% | 100% | n/a |
| F1 | feature | fresh | B | 3 | $0.29 | $0.27 to $0.31 | 77 | 35040 | 100% | 100% | n/a |
| F2 | feature | fresh | A | 3 | $0.42 | $0.35 to $0.53 | 102 | 37656 | 100% | 100% | n/a |
| F2 | feature | fresh | B | 3 | $0.50 | $0.42 to $0.58 | 113 | 43789 | 100% | 100% | n/a |
| L1 | long | fresh | A | 3 | $0.34 | $0.29 to $0.42 | 83 | 34659 | 100% | 100% | n/a |
| L1 | long | fresh | B | 3 | $0.46 | $0.40 to $0.50 | 113 | 41222 | 100% | 100% | n/a |
| L2 | long | fresh | A | 3 | $0.41 | $0.36 to $0.46 | 100 | 37590 | 67% | 67% | n/a |
| L2 | long | fresh | B | 3 | $0.52 | $0.39 to $0.73 | 152 | 44246 | 0% | 0% | n/a |
| Q1 | find | fresh | A | 3 | $0.09 | $0.07 to $0.10 | 17 | 20161 | 100% | n/a | n/a |
| Q1 | find | fresh | B | 3 | $0.12 | $0.07 to $0.15 | 29 | 23822 | 100% | n/a | n/a |
| Q2 | find | fresh | A | 3 | $0.08 | $0.06 to $0.10 | 20 | 19586 | 100% | n/a | n/a |
| Q2 | find | fresh | B | 3 | $0.09 | $0.05 to $0.14 | 25 | 23516 | 100% | n/a | n/a |
| Q3 | find | fresh | A | 3 | $0.09 | $0.07 to $0.11 | 19 | 20175 | 100% | n/a | n/a |
| Q3 | find | fresh | B | 3 | $0.10 | $0.07 to $0.15 | 24 | 23934 | 100% | n/a | n/a |
| Q4 | find | fresh | A | 3 | $0.09 | $0.07 to $0.11 | 16 | 21925 | 100% | n/a | n/a |
| Q4 | find | fresh | B | 3 | $0.11 | $0.08 to $0.15 | 18 | 26118 | 100% | n/a | n/a |
| R1 | refactor | fresh | A | 3 | $0.20 | $0.19 to $0.22 | 63 | 24895 | 100% | n/a | n/a |
| R1 | refactor | fresh | B | 3 | $0.25 | $0.20 to $0.30 | 67 | 30439 | 100% | n/a | n/a |
| R2 | refactor | fresh | A | 3 | $0.36 | $0.26 to $0.52 | 101 | 32131 | 100% | n/a | n/a |
| R2 | refactor | fresh | B | 3 | $0.48 | $0.36 to $0.56 | 142 | 38513 | 100% | n/a | n/a |
| R3 | refactor | fresh | A | 3 | $0.40 | $0.34 to $0.44 | 107 | 34640 | 100% | n/a | n/a |
| R3 | refactor | fresh | B | 3 | $0.66 | $0.59 to $0.72 | 168 | 45769 | 100% | n/a | n/a |

Blind grades recorded: 0 of 102 runs.