// Hidden acceptance tests for the Euclid per-step chance task (harness-authored).
//   g++ -std=c++11 -O2 -I src -o /tmp/vg_hidden_f1 tests/euclid/chance_hidden_test.cpp && /tmp/vg_hidden_f1
#include "modules/Euclid/EuclidEngine.hpp"
#include <cstdio>
#include <cstdint>
#include <cstdlib>

static int g_checks = 0, g_failures = 0;
static void check(const char* what, bool ok) { g_checks++; if (!ok) { g_failures++; std::printf("  FAIL: %s\n", what); } }

using namespace euclid;
static const int W = 48;

// The test's own model of the specified generator.
struct ModelRng {
    uint32_t state;
    explicit ModelRng(uint32_t s) : state(s ? s : 0x9E3779B9u) {}
    uint32_t next() { uint32_t x = state; x ^= x << 13; x ^= x >> 17; x ^= x << 5; return state = x; }
    int percent() { return (int)(next() % 100u); }
};

struct Rig {
    Sequencer seq; int hits, steps, rot, chance;
    Rig(int h, int s, int r, int c) : hits(h), steps(s), rot(r), chance(c) { seq.load(W); }
    Sequencer::Out idle()  { return seq.process(false, false, W, hits, steps, rot, chance); }
    Sequencer::Out clock() { return seq.process(false, true,  W, hits, steps, rot, chance); }
    Sequencer::Out reset() { return seq.process(true,  false, W, hits, steps, rot, chance); }
    void settle() { for (int i = 0; i < W; i++) idle(); }
};

int main()
{
    std::printf("chance: six-argument form equals chance 100\n");
    {
        Sequencer a, b; a.load(W); b.load(W);
        bool same = true;
        for (int i = 0; i < 200; i++) {
            bool clk = (i >= W) && (i % 3 == 0);
            bool rst = (i == 120);
            Sequencer::Out oa = a.process(rst, clk, W, 5, 8, 2);
            Sequencer::Out ob = b.process(rst, clk, W, 5, 8, 2, 100);
            if (oa.gate != ob.gate || oa.struck != ob.struck || oa.gate_gap != ob.gate_gap || oa.position != ob.position) same = false;
        }
        check("six-arg process matches chance 100 sample for sample", same);
    }

    std::printf("chance 0: never plays, still advances\n");
    {
        Rig r(4, 16, 0, 0); r.settle();
        bool anyStruck = false, anyGate = false; int lastPos = 0;
        for (int i = 0; i < 64; i++) { Sequencer::Out o = r.clock(); if (o.struck) anyStruck = true; if (o.gate) anyGate = true; lastPos = o.position; }
        check("chance 0 never strikes", !anyStruck);
        check("chance 0 keeps gate low", !anyGate);
        check("chance 0 still advances the playhead", lastPos == 0);  // 64 clocks on 16 steps
        Sequencer::Out o = r.reset();
        check("a reset with chance 0 does not strike step 1", !o.struck && !o.gate);
    }

    std::printf("chance 100: plays every hit\n");
    {
        Rig r(4, 16, 0, 100); r.settle();
        int strikes = 0;
        for (int i = 0; i < 64; i++) if (r.clock().struck) strikes++;
        check("chance 100 strikes every hit (16 of 64)", strikes == 16);
    }

    std::printf("determinism and the one-roll rule\n");
    {
        Rig r(5, 8, 1, 50); r.seq.rng.seed(12345u); r.settle();
        ModelRng m(12345u);
        bool same = true; int plays = 0, hitsLanded = 0;
        for (int i = 0; i < 400; i++) {
            Sequencer::Out o = r.clock();
            bool isHit = r.seq.pattern.hit[o.position];
            bool expect = false;
            if (isHit) { hitsLanded++; expect = m.percent() < 50; }
            if (expect) plays++;
            if (o.struck != expect) same = false;
            if (o.gate != expect) same = false;
        }
        check("seeded engine matches the specified generator roll for roll", same);
        check("some hits played and some did not", plays > 0 && plays < hitsLanded);
        Rig r2(5, 8, 1, 50); r2.seq.rng.seed(12345u); r2.settle();
        Rig r3(5, 8, 1, 50); r3.seq.rng.seed(12345u); r3.settle();
        bool twin = true;
        for (int i = 0; i < 400; i++) { Sequencer::Out a = r2.clock(), b = r3.clock(); if (a.struck != b.struck || a.gate != b.gate) twin = false; }
        check("two engines with the same seed agree", twin);
    }

    std::printf("a lost roll holds the gate low; a won roll holds it high\n");
    {
        Rig r(8, 8, 0, 50); r.seq.rng.seed(777u); r.settle();
        ModelRng m(777u);
        bool ok = true;
        for (int i = 0; i < 40; i++) {
            Sequencer::Out o = r.clock();
            bool expect = m.percent() < 50;
            if (o.struck != expect) ok = false;
            for (int k = 0; k < 10; k++) { Sequencer::Out s = r.idle(); if (s.gate != expect || s.struck) ok = false; }
        }
        check("gate follows the roll across idle samples and idle never re-rolls", ok);
    }

    std::printf("reset rolls step 1; clamping\n");
    {
        Rig r(4, 16, 0, 50); r.seq.rng.seed(99u); r.settle();
        ModelRng m(99u);
        Sequencer::Out o = r.reset();
        bool expect = m.percent() < 50;
        check("a reset onto a hit step takes one roll", o.struck == expect && o.gate == expect);
        Rig hi(4, 16, 0, 150); hi.settle(); int s1 = 0; for (int i = 0; i < 32; i++) if (hi.clock().struck) s1++;
        check("chance above 100 behaves as 100", s1 == 8);
        Rig lo(4, 16, 0, -5); lo.settle(); int s2 = 0; for (int i = 0; i < 32; i++) if (lo.clock().struck) s2++;
        check("chance below 0 behaves as 0", s2 == 0);
    }

    std::printf("chance_hidden_test: %d checks, %d failures\n", g_checks, g_failures);
    return g_failures ? 1 : 0;
}
