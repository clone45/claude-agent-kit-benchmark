# Voxglitch

Working copy of the Voxglitch VCV Rack plugin, used for an evaluation. C++11. Each module is `src/modules/<Name>.cpp` plus headers in `src/modules/<Name>/`; shared code lives in `src/vgLib-2.0/`. The full plugin is NOT built here (no Rack build toolchain); use the checks below instead.

## Commands

- Compile-check one module against the Rack SDK headers (about 4 seconds): `bash scripts/vg_check.sh compile Euclid`, where the name is that of `src/modules/<Name>.cpp`. `bash scripts/vg_check.sh compile all` checks every module and takes a few minutes.
- Standalone engine tests, Rack-free, a few seconds: `bash scripts/vg_check.sh tests` builds and runs everything in `tests/euclid` and `tests/timeline`. The exact g++ line for one test is in each directory's `README.md`.
- Rack SDK headers are at `/mnt/c/Code/Rack-SDK/include` and `/mnt/c/Code/Rack-SDK/dep/include`, read-only.

## Rules

- Work autonomously. Nobody will answer questions; make reasonable decisions and finish the task.
- Do not commit, stash, or switch branches. Leave your changes in the working tree.
- Do not fetch anything from the network. Everything you need is in this tree.
- Do not run `make`; the plugin cannot be built here.
