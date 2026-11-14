"""Actual independent L1 functions and maintained native/bridge code."""
import re
from closure_support import ROOT,function
from water_weather_shells import NAMES,SOURCES,BRIDGE
from water_weather_build import FILES,includes
HELPERS=['shift','byte_sub','byte_dec','inc','push','pop','dec8','cell','cmp8','water_tail']
def pair(folder,contract_pixels=False):
    folder.mkdir(parents=True,exist_ok=True)
    out='''#include "platform.h"
uint16_t wt_read(uint16_t,uint16_t);uint8_t wt_read8(uint16_t,uint16_t);void wt_write(uint16_t,uint16_t,uint16_t);void wt_write8(uint16_t,uint16_t,uint8_t);void wt_out(uint16_t,unsigned,uint32_t);int wt_near(uint16_t,uint16_t,Regs *);int wt_dispatch(uint16_t,uint16_t,Regs *);void wt_abort(void);void wt_mark(Regs *);
#define rd16 wt_read
#define rd8 wt_read8
#define wr16 wt_write
#define wr8 wt_write8
#define platform_out wt_out
#define ugh_call_near wt_near
#define ugh_dispatch wt_dispatch
#define abort wt_abort
'''
    out+='#include "'+(ROOT/'native/water_weather.c').as_posix()+'"\n'
    def renamed(body):
        for n in [*HELPERS,*['c_'+x for x in NAMES],'water_frame0','water_frame1','water_frame2']:body=re.sub(r'\b'+n+r'\b','reference_'+n,body)
        return body
    for name,source in [('shift','actors_states'),('byte_sub','actors_states'),('byte_dec','actors_states'),('inc','actors_states'),('push','actors_states'),('pop','actors_states'),('dec8','items_water'),('cell','items_water'),('cmp8','render')]:out+=renamed(function((ROOT/'c'/f'{source}.c').read_text(),name))+'\n'
    for source in ['actors_states','items_water','render','render_primitives']:
        raw=(ROOT/'c'/f'{source}.c').read_text();out+='\n'.join(l for l in raw.splitlines() if l.startswith('#define '))+'\n'
        if source=='items_water':
            a=raw.index('static const char water_frame0');b=raw.index('static int water_tail',a);out+=renamed(raw[a:b])+renamed(function(raw,'water_tail'))
        for name in NAMES:
            if SOURCES[name]!=source:continue
            body=function(raw,'c_'+name)
            if contract_pixels and name=='AdvanceWaterSurface':
                a=body.index('        push(r,r->ds);');b=body.index('r->ds=pop(r);',a)+len('r->ds=pop(r);');body=body[:a]+'wt_mark(r);'+body[b:]
            out+=renamed(body)+'\n'
        out+='\n'.join('#undef '+s for s in ['R','W','A','B','F','RI','WI','CALL','BI'])+'\n'
    bridge=includes(BRIDGE.read_text(),BRIDGE).replace('#include <stdlib.h>','')
    if contract_pixels:
        a=bridge.index('        ww_mark_begin(r,plan);');b=bridge.index('ww_mark_end(r,plan);',a)+len('ww_mark_end(r,plan);')
        bridge=bridge[:a]+'''ww_mark_begin(r,plan);ww_mark_position(plan,(uint16_t)((uint8_t)rd16(r->ds,D(PreviousWaterSurfaceY))*rd8(r->ds,D(VgaRowStrideBytes))));wt_mark(r);ww_mark_end(r,plan);'''+bridge[b:]
    out+=bridge;(folder/'pair.inc').write_text(out)
    return [*FILES,*[ROOT/'c'/f'{n}.c' for n in ['actors_states','items_water','render','render_primitives']],ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'c/platform.h',ROOT/'verif/water_weather_pair.py',ROOT/'verif/water_weather_shells.py']
