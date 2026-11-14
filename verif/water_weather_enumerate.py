"""Complete small scalar domains and every compiled water color selector."""
import subprocess
from closure_support import ROOT,function,compile_c,receipt,save
from water_weather_build import OUT,FILES
def main():
    folder=OUT/'enumeration';folder.mkdir(parents=True,exist_ok=True);source=(ROOT/'c/items_water.c').read_text();a=source.index('static const char water_frame0');b=source.index('static int water_tail',a)
    tail=function(source,'water_tail');a2=tail.index('            switch(');b2=tail.index('            wr8(',a2)
    rain=function((ROOT/'c/render_primitives.c').read_text(),'c_DrawRainParticles');a3=rain.index('        unsigned shift=');b3=rain.index('        platform_out(',a3)
    code='#include "ugh.h"\n#include <stdio.h>\n#include <stdlib.h>\n#include "'+(ROOT/'native/water_weather.c').as_posix()+'"\n'
    code+=source[a:b]+'\nstatic uint8_t reference_color(unsigned frame,unsigned plane,unsigned x,const uint8_t colors[5]) {Regs storage,*r=&storage;r->ax=(uint16_t)(colors[0]<<8);r->bx=(uint16_t)(colors[1]|(uint16_t)colors[2]<<8);r->cx=(uint16_t)(colors[3]|(uint16_t)colors[4]<<8);const char *pattern=frame==0?water_frame0:frame==1?water_frame1:water_frame2;uint8_t value;'+tail[a2:b2]+'return value;}\n'
    code+='static uint8_t reference_mask(uint16_t modulo){Regs storage,*r=&storage;r->ax=0xab00;r->cx=modulo;'+rain[a3:b3]+'return (uint8_t)r->ax;}\n'
    code+='''int main(void){unsigned selectors=0;
 for(unsigned i=0;i<65536u;i++){
  if(weather_plane_mask((uint16_t)i)!=reference_mask((uint16_t)i))return 1;
  if(weather_first_particle((uint16_t)i,0)!=(uint16_t)(i*2u) || weather_first_particle((uint16_t)i,1)!=(uint16_t)((i+1u)*2u))return 1;
  Regs r={0};r.bx=(uint16_t)i;r.bx=sub16(&r,r.bx,2,0);if(weather_previous_particle((uint16_t)i)!=r.bx || weather_more_particles(r.bx)!=((int16_t)r.bx>=0))return 1;
 }
 for(unsigned frame=0;frame<3;frame++)for(unsigned cell=0;cell<320;cell++)for(unsigned color=0;color<5;color++)for(unsigned value=0;value<256;value++){
  uint8_t colors[5]={0};colors[color]=(uint8_t)value;
  if(weather_frame_color(frame,cell,colors)!=reference_color(frame,cell/80,cell%80,colors))return 1;
  selectors++;
 }
 printf("PASS all65536 masked-plane and index words, both initial count conventions; %u actual compiled color selector cases\\n",selectors);return 0;}
'''
    path=folder/'harness.c';path.write_text(code);exe=folder/'enumerate.exe';built=compile_c([path],exe,[ROOT/'c',ROOT/'native'])
    run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=600)
    save(folder/'result.json',receipt(built['command'],[*FILES,ROOT/'c/items_water.c',ROOT/'c/render_primitives.c',ROOT/'verif/water_weather_enumerate.py'],result='PASS' if not run.returncode else 'FAIL',stdout=run.stdout,stderr=run.stderr,returncode=run.returncode,scope='A for the complete16-bit masked-plane result. Full-word index arithmetic is additionally checked against actual SUB and documented initial expressions; actual-C B profiles cover the wrappers. Color selectors enumerate960 cells with all256 values in each of five individually varied channels, not the entire40-bit color tuple; B covers arbitrary simultaneous colors.'))
    print(run.stdout+run.stderr);assert not run.returncode
if __name__=='__main__':main()
