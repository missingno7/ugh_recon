"""Actual bridge projector, arbitrary-prefix stores and RNG completion protocol."""
import argparse
from closure_support import ROOT,function
from water_weather_build import OUT
from water_weather_proof import common
from water_weather_limits import cbmc
def make(key,folder):
    code,inputs=common(folder)
    if key=='complete':
        inc=folder/'pair.inc';text=inc.read_text();old=function(text,'ww_require');text=text.replace(old,'static unsigned rejections;static void ww_require(int c){if(!c)rejections++;}\n');inc.write_text(text)
    code+='''int main(void){WeatherRam arbitrary;ram=arbitrary;slot=0;Regs r;r.cs=GAME_SEG;r.ds=DATA_SEG;r.bx=0;r.ss=0x9000;r.sp=0x8000;
 WeatherPlan p;ww_open(&r,&p,3,1);CHECK(p.active && p.particle_mode,"actual particle constructor");
'''
    if key=='projection':
        code+='''WeatherParticle any;p.particle=any;int expected=(any.position==ram.particle && any.previous==ram.particle_previous && any.modulo_four==ram.modulo);CHECK(ww_projection(&r,&p)==expected,"complete particle working-state predicate");
 WaterWeatherState state;p.state=state;p.particle_mode=0;
 expected=state.fixed_y==ram.fixed_y && state.surface_y==ram.surface && state.previous_y==ram.previous && state.byte_position==ram.position && state.frame==ram.frame && state.countdown==(uint8_t)(ram.bytes>>8) && state.phase==(uint8_t)ram.phase && state.restore_pending==(uint8_t)ram.bytes;
 CHECK(ww_projection(&r,&p)==expected,"complete water working-state predicate");
'''
    elif key=='open':
        code+='''CHECK(p.particle.position==ram.particle && p.particle.previous==ram.particle_previous && p.particle.modulo_four==ram.modulo && p.surface==ram.surface && p.inputs.direction==(uint8_t)ram.direction && p.inputs.row_stride==(uint8_t)ram.stride && p.inputs.increment==ram.increment,"selected slot and readonly inputs");p.particle_mode=0;CHECK(ww_projection(&r,&p),"complete actual water import");
 CHECK(p.result.count==1 && p.result.actions[0].kind==WW_RANDOM && p.result.actions[0].value==(uint16_t)(ram.surface+320u),"constructor publishes one pending RNG request");
'''
    elif key=='store':
        code+='''unsigned field;__CPROVER_assume(field<=WW_MODULO);size_t prefix;__CPROVER_assume(prefix<10);uint16_t value;
 const uint16_t bases[]={D(WaterY32),D(WaterYPixels),D(PreviousWaterSurfaceY),D(WaterSurfaceByteOffset),D(WaterSurfaceFrame),D(WaterSurfaceFrameCountdown),D(WaterStepPhase),D(WaterRestorePending),D(RainParticleOffsets),D(RainPreviousOffsets),D(RainParticleXModuloFour)};
 unsigned width=field>=WW_COUNTDOWN && field<=WW_PENDING?1:2;if(width==1)value&=255u;
 p.result.count=prefix+1;p.consumed=prefix;p.result.actions[prefix]=(WeatherAction){WW_STORE,(WeatherField)field,value,0};
 unsigned at;watch=at;observations=epoch=0;WeatherRam before=ram;
 ww_write(&r,&p,bases[field],value,width);CHECK(p.consumed==prefix+1 && observations==1,"one native store at arbitrary journal prefix");
 if(seen[0])CHECK(log[0].position==bases[field] && log[0].value==value && log[0].kind==(width==1?1u:0u),"native field/address/width/value binding");
 if(field==WW_PENDING)CHECK((ram.bytes&0xff00u)==(before.bytes&0xff00u),"countdown high byte survives pending store");
 if(field==WW_COUNTDOWN)CHECK((ram.bytes&255u)==(before.bytes&255u),"pending byte survives countdown store");
 if(field==WW_PHASE)CHECK((ram.phase&0xff00u)==(before.phase&0xff00u),"phase high byte frame");
'''
    elif key=='complete':
        code+='''_Bool leftover,pending;p.result.count=leftover?1:0;p.consumed=0;p.service_pending=pending;p.tail_seen=0;ww_complete(&r,&p);CHECK((rejections!=0)==(leftover || pending),"normal completion rejects all unconsumed requests and pending RNG/pixel service");
'''
    else:raise ValueError(key)
    return code+'return 0;}\n',inputs
def main():
    ap=argparse.ArgumentParser();ap.add_argument('key',choices=['open','projection','store','complete']);ap.add_argument('--timeout',type=int,default=120);a=ap.parse_args()
    folder=OUT/'kernel'/a.key;folder.mkdir(parents=True,exist_ok=True);code,inputs=make(a.key,folder);source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,[*inputs,ROOT/'verif/water_weather_harness.c',ROOT/'verif/water_weather_proof.py',ROOT/'verif/water_weather_kernel.py'],unwind=40,timeout=a.timeout,defines=['-DACTOR_VERIFY'],extra=['--no-array-field-sensitivity'])
    print(a.key,result['result'],round(result['seconds'],3),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
