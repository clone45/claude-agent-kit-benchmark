#!/usr/bin/env bash
# Checks that work without the Rack build toolchain.
#   vg_check.sh compile <Module ...|all>   syntax-only compile against the Rack SDK headers
#   vg_check.sh tests                       build and run the standalone tests in tests/euclid and tests/timeline
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="${RACK_SDK_DIR:-/mnt/c/Code/Rack-SDK}"
cmd="${1:-}"; shift || true
case "$cmd" in
  compile)
    rc=0
    if [ "${1:-all}" = all ]; then
      mods=$(ls "$ROOT"/src/modules/*.cpp)
    else
      mods=""
      for m in "$@"; do mods="$mods $ROOT/src/modules/$m.cpp"; done
    fi
    for f in $mods; do
      if [ ! -f "$f" ]; then echo "FAIL $(basename "$f"): no such module file"; rc=1; continue; fi
      if g++ -std=c++11 -fsyntax-only -DARCH_LIN -I"$ROOT/src" -I"$SDK/include" -I"$SDK/dep/include" "$f" 2>/tmp/vg_check_err.txt; then
        echo "ok   $(basename "$f")"
      else
        echo "FAIL $(basename "$f")"; head -40 /tmp/vg_check_err.txt; rc=1
      fi
    done
    exit $rc ;;
  tests)
    rc=0
    cd "$ROOT/tests/euclid" || exit 1
    for t in pattern_test engine_test seq3_parity_test; do
      if g++ -std=c++11 -O2 -I ../../src -o "/tmp/vg_$t" "$t.cpp"; then "/tmp/vg_$t" || rc=1; else echo "BUILD FAIL $t"; rc=1; fi
    done
    cd "$ROOT/tests/timeline" || exit 1
    for t in engine_test transport_test record_test chase_test scrollbar_test; do
      if g++ -std=c++11 -O2 -I ../../src/modules/Timeline -o "/tmp/vg_$t" "$t.cpp" -lm; then "/tmp/vg_$t" || rc=1; else echo "BUILD FAIL $t"; rc=1; fi
    done
    if g++ -std=c++11 -O1 -g -fsanitize=address -fno-omit-frame-pointer -I ../../src/modules/Timeline -o /tmp/vg_store_test store_test.cpp -lm; then /tmp/vg_store_test || rc=1; else echo "BUILD FAIL store_test"; rc=1; fi
    exit $rc ;;
  *)
    echo "usage: vg_check.sh compile <Module ...|all> | tests"; exit 2 ;;
esac
