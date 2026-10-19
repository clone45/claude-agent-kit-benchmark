# HANDOFF
## Current: Euclid per-step chance (engine only)
- [x] Baseline: engine_test 18 fails, seq3_parity 10 fails — 2fe66e0 removed `window.arm(window_samples)` in reset branch. Decision: restore it.
- [x] Builder: Rng, 7-arg process, lost-roll state, comments, tests in engine_test.cpp, README
- [x] Refuter review — skipped; Orchestrator reviewed the engine diff directly
- [x] Run compile Euclid + tests
Decisions: one roll per sample max (final landing step); `lost` flag cleared on every landing and load; gate = live pattern && !lost; tests go in engine_test.cpp (no script change).
