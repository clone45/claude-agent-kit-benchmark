// Hidden acceptance tests for the VX Drum Sequencer direction task (harness-authored).
//   g++ -std=c++11 -O2 -I src/modules/VXDrumSequencer -o /tmp/vg_hidden_f2 tests/vx_drum_sequencer/direction_hidden_test.cpp && /tmp/vg_hidden_f2
#include "VXDrumSequencerEngine.hpp"
#include <cstdio>

static int g_checks = 0, g_failures = 0;
static void check(const char* what, bool ok) { g_checks++; if (!ok) { g_failures++; std::printf("  FAIL: %s\n", what); } }

using namespace vx_drum_sequencer;

static bool runSeq(Playhead& h, int length, const int* want, int n)
{
    for (int i = 0; i < n; i++) if (h.advance(length) != want[i]) return false;
    return true;
}

int main()
{
    std::printf("forward unchanged\n");
    {
        Playhead h; const int want[] = {1, 2, 3, 0, 1, 2, 3, 0};
        check("forward wraps as before", runSeq(h, 4, want, 8));
        Playhead d; d.direction = FORWARD; check("direction defaults to FORWARD", d.direction == FORWARD);
    }
    std::printf("backward\n");
    {
        Playhead h; h.direction = BACKWARD; const int want[] = {3, 2, 1, 0, 3, 2};
        check("backward from step 1 wraps to the last step", runSeq(h, 4, want, 6));
        Playhead s; s.direction = BACKWARD; s.position = 7;
        check("backward from beyond the length goes to the last step", s.advance(4) == 3);
        Playhead one; one.direction = BACKWARD; check("backward on length 1 stays on 0", one.advance(1) == 0 && one.advance(1) == 0);
        Playhead ho; ho.direction = BACKWARD; ho.rewind(); check("hand-off lands on step 1 backward too", ho.advance(4) == 0);
    }
    std::printf("pendulum\n");
    {
        Playhead h; h.direction = PENDULUM; const int want[] = {1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1};
        check("pendulum bounces without repeating the ends", runSeq(h, 4, want, 13));
        Playhead one; one.direction = PENDULUM; check("pendulum on length 1 stays on 0", one.advance(1) == 0 && one.advance(1) == 0);
        Playhead two; two.direction = PENDULUM; const int w2[] = {1, 0, 1, 0, 1};
        check("pendulum on length 2 alternates", runSeq(two, 2, w2, 5));
        Playhead s; s.direction = PENDULUM; s.position = 9; const int ws[] = {3, 2, 1, 0, 1};
        check("pendulum beyond the length goes to the last step then backward", runSeq(s, 4, ws, 5));
        Playhead ho; ho.direction = PENDULUM; ho.advance(4); ho.advance(4); ho.advance(4); ho.advance(4);  // now at 2 heading backward
        ho.rewind(); const int wh[] = {0, 1, 2};
        check("hand-off lands on step 1 and heads forward", runSeq(ho, 4, wh, 3));
        Playhead rs; rs.direction = PENDULUM; rs.advance(4); rs.advance(4); rs.advance(4); rs.advance(4);
        rs.reset(); const int wr[] = {1, 2, 3, 2};
        check("reset puts step 1 current and heads forward", rs.position == 0 && runSeq(rs, 4, wr, 4));
    }
    std::printf("sequencer API\n");
    {
        Sequencer s;
        check("sequencer default direction is FORWARD", s.direction() == FORWARD);
        s.setDirection(PENDULUM); check("setDirection stores PENDULUM", s.direction() == PENDULUM && s.head.direction == PENDULUM);
        s.setDirection(BACKWARD); check("setDirection stores BACKWARD", s.direction() == BACKWARD);
        s.setDirection(7); check("an out-of-range direction becomes FORWARD", s.direction() == FORWARD);
        s.setDirection(-1); check("a negative direction becomes FORWARD", s.direction() == FORWARD);
    }
    std::printf("direction_hidden_test: %d checks, %d failures\n", g_checks, g_failures);
    return g_failures ? 1 : 0;
}
