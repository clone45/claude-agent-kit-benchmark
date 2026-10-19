#include "modules/Euclid/EuclidEngine.hpp"
#include <cstdio>
int main(){
  euclid::Sequencer s; s.load(48);
  for(int i=0;i<100;i++) s.process(false,false,48,4,16,0);
  s.process(false,true,48,4,16,0); s.process(false,false,48,4,16,0);
  auto o=s.process(true,true,48,4,16,0);
  printf("old same-sample: pos=%d\n", o.position);
  s.process(true,false,48,4,16,0); o=s.process(false,true,48,4,16,0);
  printf("old clock 1 sample after reset: pos=%d\n", o.position);
}
