"""Actual VGA aperture, read modes, aliases, ordered latch and sampler cases."""
import subprocess
from closure_support import ROOT,function,compile_c,receipt,save
from player_physics_build import OUT,FILES
def main():
    folder=OUT/'pixels';folder.mkdir(parents=True,exist_ok=True)
    reference=function((ROOT/'c/demo_scripts.c').read_text(),'c_SamplePlayerCollisionPixels').replace('c_SamplePlayerCollisionPixels','reference_sample')
    bridge=function((ROOT/'native/bridge/player_physics_bridge.c').read_text(),'c_SamplePlayerCollisionPixels')
    text='''#include "platform.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "'''+(ROOT/'native/player_physics.h').as_posix()+'''"
Devices ugh_devices;
'''+reference+bridge+'''
static unsigned cases;
static const uint16_t delta[]={0,3,5,0x720,0x723,0x725,0x240,0x245,0x480,0x485};
static void check(uint16_t segment,uint16_t origin,unsigned pattern,unsigned bit,unsigned map,unsigned mode,unsigned compare,unsigned care) {
 for(unsigned i=0;i<10;i++) {
  uint32_t physical=lin(segment,(uint16_t)(origin+delta[i]));
  if(physical>=0xa0000u && physical<0xb0000u) {
   for(unsigned plane=0;plane<4;plane++) {
    unsigned rotate=(i+plane*3u)%10u;
    uint8_t value=(uint8_t)(((pattern>>rotate)&1u)<<bit);
    if(mode)value=(uint8_t)((((pattern>>plane)&1u)?255u:0u)^(i*17u));
    ugh_devices.plane[plane][(uint16_t)physical]=value;
   }
  } else ugh_mem[physical]=(uint8_t)(((pattern>>i)&1u)<<bit);
 }
 ugh_devices.read_map=(uint8_t)map;ugh_devices.gc[4]=(uint8_t)map;
 ugh_devices.gc[5]=(uint8_t)(mode?8:0);ugh_devices.gc[2]=(uint8_t)compare;ugh_devices.gc[7]=(uint8_t)care;
 /* Write masks/rotate have no effect on aperture reads and must survive. */
 ugh_devices.map_mask=(uint8_t)pattern;ugh_devices.gc[8]=(uint8_t)(pattern>>2);ugh_devices.gc[3]=(uint8_t)bit;
 Regs initial={.ax=(uint16_t)(0xa500u|pattern),.bx=0x8000,.cx=0xffff,.dx=0x3cf,.si=origin,.di=0x7fff,.bp=0x3f,
  .sp=0x8000,.cs=GAME_SEG,.ds=DATA_SEG,.es=segment,.ss=0x9000,.ip=0x7777,.flags=(uint16_t)(0xffffu^(pattern*17u))};
 uint8_t latch[4]={0x31,0x72,0xc3,0x94};memcpy(ugh_devices.latch,latch,4);
 Regs a=initial,b=initial;int left=reference_sample(&a);uint8_t after[4];memcpy(after,ugh_devices.latch,4);
 memcpy(ugh_devices.latch,latch,4);int right=c_SamplePlayerCollisionPixels(&b);
 if(left!=right || memcmp(&a,&b,sizeof(a)) || memcmp(after,ugh_devices.latch,4) || ugh_devices.gc[8]!=(uint8_t)(pattern>>2) || ugh_devices.map_mask!=(uint8_t)pattern) {
  fprintf(stderr,"FAIL pixel case %u\\n",cases);exit(1);
 }
 cases++;
}
int main(void) {
 for(unsigned pattern=0;pattern<1024;pattern++)for(unsigned bit=0;bit<8;bit++)for(unsigned map=0;map<4;map++)check(0xa000,0x1234,pattern,bit,map,0,0,0);
 for(unsigned compare=0;compare<16;compare++)for(unsigned care=0;care<16;care++)for(unsigned planes=0;planes<16;planes++)for(unsigned map=0;map<4;map++)check(0xa000,0xfffd,planes,7,map,1,compare,care);
 const uint16_t segments[]={0,0x9000,0x9fff,0xa000,0xa001,0xafff,0xb000,0xffff};
 const uint16_t origins[]={0,1,15,16,0xf8df,0xfdbf,0xfffa,0xffff};
 for(unsigned s=0;s<8;s++)for(unsigned o=0;o<8;o++)for(unsigned pattern=0;pattern<1024;pattern++)check(segments[s],origins[o],pattern,7,pattern&3u,0,0,0);
 printf("PASS %u actual aperture sampler cases; every ten-bit mask in all eight bit positions/four planes, read-mode1 compare/care, aliases/wrapped origins and final four latches\\n",cases);
 return 0;
}
'''
    source=folder/'harness.c';source.write_text(text);exe=folder/'pixels.exe'
    built=compile_c([source,ROOT/'c/memory.c',ROOT/'native/player_physics.c'],exe,[ROOT/'c',ROOT/'native'])
    run=subprocess.run([str(exe)],capture_output=True,text=True)
    save(folder/'result.json',receipt(built['command'],[*FILES,ROOT/'c/memory.c',ROOT/'c/demo_scripts.c',ROOT/'c/ugh.h',ROOT/'c/platform.h',ROOT/'verif/player_physics_pixels.py'],result='PASS' if not run.returncode else 'FAIL',stdout=run.stdout,stderr=run.stderr,returncode=run.returncode))
    print(run.stdout+run.stderr,flush=True);assert not run.returncode
if __name__=='__main__':main()
