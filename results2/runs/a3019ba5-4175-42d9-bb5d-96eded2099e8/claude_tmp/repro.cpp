#include <cstdio>
#include "modules/Euclid/EuclidEngine.hpp"
int main(){
  euclid::Sequencer s; s.load(48);
  for(int i=0;i<100;i++) s.process(false,false,48,4,16,0);
  // clock to step 2,3
  for(int k=0;k<3;k++){ s.process(false,true,48,4,16,0); for(int i=0;i<99;i++) s.process(false,false,48,4,16,0);}
  printf("before reset pos=%d\n", s.position);
  euclid::Sequencer::Out o=s.process(true,true,48,4,16,0);
  printf("same-sample reset+clock pos=%d struck=%d remaining=%d\n", o.position,o.struck,s.window.remaining);
  o=s.process(false,true,48,4,16,0);
  printf("clock 1 sample later pos=%d remaining=%d\n", o.position,s.window.remaining);
  return 0;}
