#include <cstdio>
#include "modules/Euclid/EuclidEngine.hpp"
using namespace vgLib_v2;
int main(){
  int rates[]={11025,22050,32000,44100,48000,64000,88200,96000,128000,176400,192000,352800,384000,705600,768000};
  int bad=0;
  for(int ri=0;ri<15;ri++){ int W=ResetClockWindow::samplesFor((float)rates[ri]);
   for(int steps=1;steps<=32;steps+=7) for(int pre=0;pre<40;pre+=3) for(int d=0; d<=W+2; d++){
    euclid::Sequencer s; s.load(W);
    for(int i=0;i<W;i++) s.process(false,false,W,steps,steps,0);
    for(int k=0;k<pre;k++){ s.process(false,true,W,steps,steps,0); s.process(false,false,W,steps,steps,0);}
    for(int i=0;i<pre*13%50;i++) s.process(false,false,W,steps,steps,0);
    euclid::Sequencer::Out o;
    if(d==0){ o=s.process(true,true,W,steps,steps,0);} else { o=s.process(true,false,W,steps,steps,0); for(int i=1;i<d;i++) s.process(false,false,W,steps,steps,0); o=s.process(false,true,W,steps,steps,0);}
    int expect = (d==0||d<W) ? 0 : (1%steps);
    if(o.position!=expect){ if(bad<10) printf("rate %d W %d steps %d pre %d d %d pos %d expect %d\n",rates[ri],W,steps,pre,d,o.position,expect); bad++; }
   }}
  printf("bad=%d\n",bad);}
