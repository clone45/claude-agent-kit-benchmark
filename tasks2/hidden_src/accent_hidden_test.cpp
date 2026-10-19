// Hidden acceptance tests for the Euclid accent task (harness-authored).
//   g++ -std=c++11 -O2 -I src -o /tmp/vg_hidden_l1 tests/euclid/accent_hidden_test.cpp && /tmp/vg_hidden_l1
#include "modules/Euclid/EuclidEngine.hpp"
#include <cstdio>

static int g_checks = 0, g_failures = 0;
static void check(const char* what, bool ok) { g_checks++; if (!ok) { g_failures++; std::printf("  FAIL: %s\n", what); } }

using namespace euclid;
static const int W = 48;

struct Rig {
    Sequencer seq;
    Rig() { seq.load(W); }
    Sequencer::Out idle()  { return seq.process(false, false, W, 4, 16, 0); }
    Sequencer::Out clock() { return seq.process(false, true,  W, 4, 16, 0); }
    Sequencer::Out reset() { return seq.process(true,  false, W, 4, 16, 0); }
    void settle() { for (int i = 0; i < W; i++) idle(); }
};

int main()
{
    std::printf("accent off\n");
    {
        Rig r; r.settle(); bool any = false;
        for (int i = 0; i < 64; i++) if (r.clock().accent) any = true;
        check("default accent_every 0 never accents", !any);
        check("accent is false on idle samples", !r.idle().accent);
    }
    std::printf("every hit, every second hit\n");
    {
        Rig r; r.seq.accent_every = 1; r.settle(); int strikes = 0, accents = 0;
        for (int i = 0; i < 64; i++) { Sequencer::Out o = r.clock(); if (o.struck) strikes++; if (o.accent) accents++; if (o.accent && !o.struck) accents = -1000; }
        check("accent_every 1 accents every strike", strikes == 16 && accents == 16);
        Rig r2; r2.seq.accent_every = 2; r2.settle(); int n = 0; bool ok = true;
        for (int i = 0; i < 64; i++) { Sequencer::Out o = r2.clock(); if (o.struck) { n++; if (o.accent != (n % 2 == 0)) ok = false; } else if (o.accent) ok = false; }
        check("accent_every 2 accents the even strikes", ok && n == 16);
        Rig r3; r3.seq.accent_every = 3; r3.settle(); int m = 0; bool ok3 = true;
        for (int i = 0; i < 64; i++) { Sequencer::Out o = r3.clock(); if (o.struck) { m++; if (o.accent != (m % 3 == 0)) ok3 = false; } }
        check("accent_every 3 accents every third strike", ok3);
    }
    std::printf("reset restarts the count\n");
    {
        Rig r; r.seq.accent_every = 2; r.settle();
        int n = 0;
        while (n < 3) { if (r.clock().struck) n++; }           // three strikes: the third is odd
        Sequencer::Out o = r.reset();                          // step 1 of 4/16 is a hit: strike number 1
        check("the reset strike is hit number 1, not accented", o.struck && !o.accent);
        r.settle();
        int k = 0; bool okn = true;   // the reset strike was number 1, so the next strike is number 2
        while (k < 2) { Sequencer::Out c = r.clock(); if (c.struck) { k++; if (k == 1 && !c.accent) okn = false; if (k == 2 && c.accent) okn = false; } }
        check("counting resumes from the reset strike", okn);
    }
    std::printf("load zeroes; clamp; mid-run change keeps the count\n");
    {
        Rig r; r.seq.accent_every = 2; r.settle();
        int n = 0; while (n < 1) { if (r.clock().struck) n++; }
        r.seq.load(W); r.settle();
        int k = 0; bool ok = true;
        while (k < 2) { Sequencer::Out c = r.clock(); if (c.struck) { k++; if (k == 1 && c.accent) ok = false; if (k == 2 && !c.accent) ok = false; } }
        check("load zeroes the counter", ok);
        Rig c9; c9.seq.accent_every = 9; c9.settle(); int cnt = 0; bool okc = true;
        for (int i = 0; i < 160; i++) { Sequencer::Out o = c9.clock(); if (o.struck) { cnt++; if (o.accent != (cnt % 8 == 0)) okc = false; } }
        check("accent_every above 8 behaves as 8", okc && cnt == 40);
        Rig mid; mid.seq.accent_every = 4; mid.settle(); int q = 0;
        while (q < 3) { if (mid.clock().struck) q++; }
        mid.seq.accent_every = 2;
        Sequencer::Out next; do { next = mid.clock(); } while (!next.struck);  // strike number 4
        check("changing accent_every keeps the running count", next.accent);
    }
    std::printf("accent_hidden_test: %d checks, %d failures\n", g_checks, g_failures);
    return g_failures ? 1 : 0;
}
