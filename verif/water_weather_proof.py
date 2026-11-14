"""Actual-C output/frame/dependence pieces, with bounded service seams."""
import argparse,re
from closure_support import ROOT,function
from water_weather_build import OUT,FILES
from water_weather_pair import pair
from water_weather_limits import cbmc

PURE={'advance-water':'water_weather_advance(&s,in)','marked':'water_weather_marked(&s)','prepare':'water_weather_prepare(&s,in)',
 'advance-particle':'weather_particle_advance(&p,boundary,in.direction,alternate)',
 'spawn':'weather_particle_spawn(&p,reply,in)','request':'weather_particle_request(surface)',
 'draw-particle':'weather_particle_draw(&p)','restore-particle':'weather_particle_restore(&p)'}
SOUT={'advance-water':['fixed_y','surface_y','previous_y','phase','restore_pending'],'marked':['restore_pending'],'prepare':['frame','countdown','byte_position']}
POUT={'advance-particle':['position','previous','modulo_four'],'spawn':['position','modulo_four']}
SALL=['fixed_y','surface_y','previous_y','byte_position','frame','countdown','phase','restore_pending']
PALL=['position','previous','modulo_four']
SIN={'advance-water':['fixed_y','surface_y','phase','restore_pending'],'marked':['previous_y','restore_pending'],'prepare':['frame','surface_y','countdown']}
PIN={'advance-particle':['position','modulo_four'],'spawn':[],'draw-particle':['position','modulo_four'],'restore-particle':['previous']}
def pure(key,mode):
    code='#include "'+(ROOT/'native/water_weather.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\nint main(void){\n'
    code+='WaterWeatherState s;WeatherParticle p;WaterWeatherInputs in;uint16_t boundary,reply,surface;_Bool alternate;\n'
    if mode=='frame':
        code+='WaterWeatherState before=s;WeatherParticle prior=p;WaterWeatherInputs inputs=in;WeatherResult result='+PURE[key]+';CHECK(result.count<=10,"bounded actual journal");\n'
        for f in SALL:
            if f not in SOUT.get(key,[]):code+=f'CHECK(s.{f}==before.{f},"other water member frame");\n'
        for f in PALL:
            if f not in POUT.get(key,[]):code+=f'CHECK(p.{f}==prior.{f},"other particle member frame");\n'
        code+='size_t at;__CPROVER_assume(at<sizeof(in));CHECK(((unsigned char *)&in)[at]==((unsigned char *)&inputs)[at],"arbitrary borrowed input byte frame");\n'
        for obj,old,typ,allowed in [('s','before','WaterWeatherState',SOUT.get(key,[])),('p','prior','WeatherParticle',POUT.get(key,[]))]:
            code+=f'size_t watch_{obj};__CPROVER_assume(watch_{obj}<sizeof({obj}));\n'
            expr=' || '.join(f'(watch_{obj}>=(size_t)((unsigned char *)&{obj}.{f}-(unsigned char *)&{obj}) && watch_{obj}<(size_t)((unsigned char *)&{obj}.{f}-(unsigned char *)&{obj})+sizeof({obj}.{f}))' for f in allowed) or '0'
            code+=f'if(!({expr}))CHECK(((unsigned char *)&{obj})[watch_{obj}]==((unsigned char *)&{old})[watch_{obj}],"arbitrary other native byte including padding");\n'
    else:
        code+='WaterWeatherState other;WeatherParticle second;\n'
        for f in sorted(set(SIN.get(key,[])+SOUT.get(key,[]))):code+=f'other.{f}=s.{f};\n'
        for f in sorted(set(PIN.get(key,[])+POUT.get(key,[]))):code+=f'second.{f}=p.{f};\n'
        code+='WeatherResult a='+PURE[key]+';\n'
        call=PURE[key].replace('&s,','&other,').replace('&s)','&other)').replace('&p,','&second,').replace('&p)','&second)')
        code+='WeatherResult b='+call+';CHECK(a.count==b.count,"event count dependence");size_t i;if(i<a.count){CHECK(a.actions[i].kind==b.actions[i].kind && a.actions[i].field==b.actions[i].field && a.actions[i].value==b.actions[i].value && a.actions[i].position==b.actions[i].position,"arbitrary event dependence");}\n'
        for f in SOUT.get(key,[]):code+=f'CHECK(s.{f}==other.{f},"working water output dependence");\n'
        for f in POUT.get(key,[]):code+=f'CHECK(p.{f}==second.{f},"working particle output dependence");\n'
    return code+'return 0;}\n'
def common(folder):
    inputs=pair(folder,contract_pixels=True)
    raw=(ROOT/'verif/water_weather_harness.c').read_text().split('#ifndef SYMBOLIC')[0]
    return '#define SYMBOLIC\n'+raw,inputs
def output(key,folder):
    code,inputs=common(folder)
    if key in ['prepare','marked']:
        raw=(ROOT/'c/items_water.c').read_text() if key=='prepare' else (ROOT/'c/actors_states.c').read_text()
        if key=='prepare':
            body=function(raw,'c_DrawWaterSurface');fragment=body[body.index('{')+1:body.index('    r->di=rd16(r->cs,G(DrawPagePointer))')]
            modern=fragment
            for name,width in [('WaterSurfaceFrameCountdown',1),('WaterSurfaceFrame',2),('WaterSurfaceByteOffset',2)]:
                modern=re.sub(r'wr'+str(width*8)+r'\(r->ds,D\('+name+r'\),([^;]+)\);',lambda m:'ww_write(r,plan,D('+name+'),'+m[1]+','+str(width)+');',modern)
            fragment=fragment.replace('dec8(', 'reference_dec8(')
        else:
            fragment='wr8(r->ds,D(WaterRestorePending),reference_byte_dec(r,rd8(r->ds,D(WaterRestorePending))));'
            modern='ww_write(r,plan,D(WaterRestorePending),byte_dec(r,rd8(r->ds,D(WaterRestorePending))),1);'
        code+='static int reference_piece(Regs *r){'+fragment+'return UGH_OK;}\n'
        code+='static int bridge_piece(Regs *r){WeatherPlan storage;ww_open(r,&storage,1,1);WeatherPlan *plan=&storage;plan->active=1;\n'
        if key=='marked':code+='plan->state.restore_pending=(uint8_t)ram.bytes;plan->state.countdown=(uint8_t)(ram.bytes>>8);plan->state.frame=ram.frame;plan->state.byte_position=ram.position;plan->result=water_weather_marked(&plan->state);plan->consumed=0;\n'
        code+=modern+'CHECK(ww_projection(r,plan) && plan->consumed+1==plan->result.count,"complete global stores before pending service");\n'
        code+='WeatherAction e=plan->result.actions[plan->consumed];'
        if key=='prepare':code+='CHECK(e.kind==WW_FRAME_TAIL && e.value==(uint16_t)(r->si*2u) && e.position==r->ax,"full-word selected frame and byte-position seam");'
        else:code+='CHECK(e.kind==WW_RESTORE_ROW && e.value==ram.previous,"marked restore-row continuation");'
        code+='return UGH_OK;}\n'
    if key=='advance-particle':
        original=function((ROOT/'c/render.c').read_text(),'c_AdvanceRainParticles');a=original.index('        r->ax=RI(');b=original.index('        r->bx=sub16',a);fragment=original[a:b]
        code+='''#define R(n) wt_read(r->ds,D(n))
#define RI(n,i) wt_read(r->ds,(uint16_t)(D(n)+(i)))
#define WI(n,i,v) wt_write(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define CALL(n,f,d) do{int status=wt_near(G(n),G(f)+(d),r);if(status)return status;}while(0)
static int reference_piece(Regs *r){'''+fragment+'''return UGH_OK;}
#undef WI
#undef CALL
#define WI(n,i,v) ww_write(r,plan,(uint16_t)(D(n)+(i)),(uint16_t)(v),2)
#define CALL(n,f,d) do{int status=ww_respawn(r,plan,G(f)+(d));if(status)return status;}while(0)
static int bridge_piece(Regs *r){WeatherPlan storage;ww_open(r,&storage,2,1);WeatherPlan *plan=&storage;'''+fragment+'''ww_complete(r,plan);return UGH_OK;}
'''
    if key in ['draw-particle','restore-particle']:
        source=(ROOT/'c/render_primitives.c').read_text();name='DrawRainParticles' if key=='draw-particle' else 'RestoreRainBackground';body=function(source,'c_'+name)
        a=body.index('    do {')+len('    do {');b=body.index('        r->bx=sub16',a);fragment=body[a:b]
        modern=fragment
        if key=='draw-particle':modern=modern.replace('platform_out(r->dx,1,(uint8_t)r->ax);','platform_out(r->dx,1,ww_rain_mask(plan,(uint8_t)r->ax));').replace('wr8(r->es,r->di,(uint8_t)(r->ax>>8));','ww_rain_pixel(r,plan);')
        else:modern=modern.replace('set_al(r,rd8(r->es,r->si)); wr8(r->es,r->di,(uint8_t)r->ax);','ww_copy(r,plan);')
        code+='static int reference_piece(Regs *r){'+fragment+'return UGH_OK;}\n'
        code+='static int bridge_piece(Regs *r){WeatherPlan storage;ww_open(r,&storage,'+('4' if key=='draw-particle' else '5')+',1);WeatherPlan *plan=&storage;'+modern+'ww_complete(r,plan);return UGH_OK;}\n'
    code+='''int main(void){WeatherRam arbitrary;ram=arbitrary;uint16_t index;__CPROVER_assume(index<193);slot=(uint16_t)(2u*index);
 Regs r;r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=0x9000;r.sp=0x8000;r.bx=slot;r.dx=0x3c5;
 uint16_t flags,reply,di;service_flags=flags;random_reply=reply;service_di=di;int status;__CPROVER_assume(status>=0 && status<=5);service_status=status;
 unsigned arbitrary_watch;watch=arbitrary_watch;WeatherRam before=ram;Regs a=r,b=r;modern=epoch=observations=0;
'''
    if key=='advance-particle':
        code+='a.bp=b.bp=(uint16_t)(((unsigned)(uint8_t)ram.direction-1u)*2u-1u);CHECK(a.bp==b.bp,"same cached drift at arbitrary physical-slot cut");int left=reference_piece(&a);\n'
    elif key in ['draw-particle','restore-particle']:
        code+='a.es=b.es=0xa000;a.bp=b.bp=ram.draw;a.cx=b.cx=ram.background;a.ax=b.ax=(uint16_t)((r.ax&255u)|0x5b00u);int left=reference_piece(&a);\n'
    elif key in ['prepare','marked']:code+='int left=reference_piece(&a);\n'
    elif key in ['advance-water','spawn']:
        i={'advance-water':0,'spawn':6}[key]
        code+=f'int left=execute({i},&a);\n'
    else:raise ValueError(key)
    code+='WeatherRam after=ram;unsigned length=observations;ram=before;modern=epoch=1;observations=0;\n'
    code+='int right=bridge_piece(&b);\n' if key in ['advance-particle','prepare','marked','draw-particle','restore-particle'] else f'int right=execute({i},&b);\n'
    code+='''CHECK(left==right && observations==length && seen[0]==seen[1],"complete status and observation count");
 if(seen[0])CHECK(log[0].kind==log[1].kind && log[0].bank==log[1].bank && log[0].position==log[1].position && log[0].value==log[1].value,"arbitrary ordered store/service parameters");
 for(unsigned i=0;i<sizeof(Regs);i++)CHECK(((unsigned char *)&a)[i]==((unsigned char *)&b)[i],"complete register and flag ABI");
 size_t at;__CPROVER_assume(at<sizeof(ram));CHECK(((unsigned char *)&ram)[at]==((unsigned char *)&after)[at],"arbitrary full normalized RAM byte and high-byte frame");return 0;}
'''
    return code,inputs
def kernel(key):
    code='#include "ugh.h"\n#include "'+(ROOT/'native/water_weather.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\n'
    if key=='index':
        render=(ROOT/'c/render.c').read_text();pixels=(ROOT/'c/render_primitives.c').read_text()
        statements=[]
        for source,name,extra in [(render,'AdvanceRainParticles',1),(pixels,'DrawRainParticles',0),(pixels,'RestoreRainBackground',1)]:
            body=function(source,'c_'+name);start=body.index('r->bx=');end=body.index(';',start)+1
            statements.append(body[start:end]+f'CHECK(r->bx==weather_first_particle(y,{extra}),"actual '+name+' initial word expression");\n')
        body=function(render,'c_AdvanceRainParticles');start=body.index('r->bx=sub16');end=body.index(';',start)+1;backedge=body[start:end]
        return code+'''#define R(n) y
#define rd16(s,o) y
int main(void){uint16_t y,index;Regs storage,*r=&storage;
'''+''.join(statements)+'r->bx=index;'+backedge+'''CHECK(r->bx==weather_previous_particle(index) && weather_more_particles(r->bx)==((int16_t)r->bx>=0),"actual SUB/signed post-test backedge");return 0;}
'''
    if key=='mask':return code+'''int main(void){uint16_t modulo;unsigned shift=modulo&31u;uint8_t original=shift<8?(uint8_t)(1u<<shift):0;CHECK(weather_plane_mask(modulo)==original,"286 masked shift count, not normalized modulo4");return 0;}
'''
    if key=='frame-color':
        source=(ROOT/'c/items_water.c').read_text();a=source.index('static const char water_frame0');b=source.index('static int water_tail',a);code+=source[a:b]
        body=function(source,'water_tail');a=body.index('            switch(');b=body.index('            wr8(',a);switch=body[a:b]
        return code+'''int main(void){unsigned frame,plane,x;__CPROVER_assume(frame<3 && plane<4 && x<80);Regs storage,*r=&storage;uint8_t colors[]={(uint8_t)(r->ax>>8),(uint8_t)r->bx,(uint8_t)(r->bx>>8),(uint8_t)r->cx,(uint8_t)(r->cx>>8)};const char *pattern=frame==0?water_frame0:frame==1?water_frame1:water_frame2;uint8_t value;
'''+switch+'''CHECK(value==weather_frame_color(frame,plane*80+x,colors),"actual store-operand recipe, every cell and all live color bytes");return 0;}
'''
    if key=='cursor':return code+'''int main(void){WeatherFrameCursor c;unsigned frame;__CPROVER_assume(frame<3);__CPROVER_assume(c.plane<5 && c.column<80);__CPROVER_assume(c.mask_due==0 || c.mask_due==1);__CPROVER_assume(c.finished==0 || c.finished==1);__CPROVER_assume(c.finished || (c.mask_due?c.plane>0:c.plane<4));WeatherFrameCursor before=c;WeatherAction event=weather_frame_next(&c,frame);
 for(unsigned i=0;i<5;i++)CHECK(c.colors[i]==before.colors[i],"all borrowed colors remain unchanged");
 if(before.finished)CHECK(event.kind==WW_DONE && c.mask==before.mask && c.plane==before.plane && c.column==before.column && c.finished==before.finished && c.mask_due==before.mask_due,"terminal frame sequence and complete private frame");
 else if(before.mask_due){CHECK(event.kind==WW_MASK && c.mask_due==0 && c.plane==before.plane && c.column==before.column,"mask follows whole plane");if(before.plane==4)CHECK(event.value==15 && c.finished && c.mask==before.mask,"forced final all-plane mask");else CHECK(event.value==(uint8_t)(before.mask<<1) && c.mask==event.value && !c.finished,"raw byte plane-mask shift");}
 else {CHECK(event.kind==WW_PIXEL && event.position==before.column && event.value==weather_frame_color(frame,before.plane*80+before.column,before.colors),"actual next native pixel");CHECK(c.column==(before.column==79?0:before.column+1) && c.plane==before.plane+(before.column==79) && c.mask_due==(before.column==79) && c.mask==before.mask && !c.finished,"four planes of80 ordered cells");}return 0;}
'''
    if key=='frame-begin':return code+'''int main(void){WeatherFrameCursor c;uint8_t colors[5],mask;uint8_t before[5];for(unsigned i=0;i<5;i++)before[i]=colors[i];weather_frame_begin(&c,colors,mask);CHECK(c.mask==mask && c.plane==0 && c.column==0 && !c.mask_due && !c.finished,"actual frame constructor and raw mask");for(unsigned i=0;i<5;i++)CHECK(c.colors[i]==before[i] && colors[i]==before[i],"all live color bytes and input frame");return 0;}
'''
    if key=='request':return code+'''int main(void){uint16_t y;Regs r;r.ax=add16(&r,320,y,0);WeatherResult result=weather_particle_request(y);CHECK(result.count==1 && result.actions[0].kind==WW_RANDOM && result.actions[0].value==r.ax,"one RNG request, full wrapping bound including zero");return 0;}
'''
    raise ValueError(key)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('key');ap.add_argument('mode',choices=['outputs','frame','dependence'],nargs='?',default='outputs');ap.add_argument('--timeout',type=int,default=120);a=ap.parse_args()
    folder=OUT/'proofs'/(a.key+'-'+a.mode);folder.mkdir(parents=True,exist_ok=True)
    if a.mode!='outputs':code=pure(a.key,a.mode);inputs=FILES
    elif a.key in ['advance-water','prepare','marked','spawn','advance-particle','draw-particle','restore-particle']:code,inputs=output(a.key,folder)
    else:code=kernel(a.key);inputs=FILES
    path=folder/'harness.c';path.write_text(code)
    result=cbmc(path,folder,[*inputs,ROOT/'verif/water_weather_proof.py',ROOT/'verif/water_weather_harness.c',ROOT/'c/items_water.c',ROOT/'c/render.c'],unwind=40,timeout=a.timeout,defines=['-DACTOR_VERIFY'],extra=['--no-array-field-sensitivity'])
    print(a.key,a.mode,result['result'],round(result['seconds'],3),result.get('peak_private_bytes'),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
