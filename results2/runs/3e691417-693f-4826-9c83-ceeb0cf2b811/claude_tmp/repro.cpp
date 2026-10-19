#include "modules/Euclid/EuclidEngine.hpp"
#include <cstdio>
int main(){
  euclid::Sequencer s; s.load(48);
  for(int i=0;i<100;i++) s.process(false,false,48,4,16,0);
  for(int k=0;k<3;k++) s.process(false,true,48,4,16,0), s.process(false,false,48,4,16,0);
  printf("before reset pos=%d remaining=%d\n", s.position, s.window.remaining);
  auto o=s.process(true,true,48,4,16,0);
  printf("same-sample: pos=%d remaining=%d\n", o.position, s.window.remaining);
  o=s.process(false,true,48,4,16,0);
  printf("clock +1: pos=%d remaining=%d\n", o.position, s.window.remaining);
  return 0;}
