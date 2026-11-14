"""Complete actual-C ABI shells; pixel blocks retain exact physical service code."""
import re,sys
from closure_support import ROOT,function
BRIDGE=ROOT/'native/bridge/water_weather_bridge.c'
NAMES=['AdvanceWaterSurface','DrawWaterSurface','DrawWaterSurfaceFrame0','DrawWaterSurfaceFrame1','DrawWaterSurfaceFrame2','AdvanceRainParticles','RespawnRainParticle','DrawRainParticles','RestoreRainBackground']
SOURCES={NAMES[0]:'actors_states',NAMES[1]:'items_water',**{n:'items_water' for n in NAMES[2:5]},NAMES[5]:'render',NAMES[6]:'render',NAMES[7]:'render_primitives',NAMES[8]:'render_primitives'}
def generated():
    actors=(ROOT/'c/actors_states.c').read_text();items=(ROOT/'c/items_water.c').read_text();render=(ROOT/'c/render.c').read_text();primitives=(ROOT/'c/render_primitives.c').read_text();out=''
    for source,names in [(actors,['shift','byte_sub','byte_dec','inc','push','pop']),(items,['dec8','cell']),(render,['cmp8'])]:
        for n in names:out+=function(source,n)+'\n'
    out+='''#define R(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define W(n,i,v) ww_write(r,plan,(uint16_t)(D(n)+(i)),(uint16_t)(v),2)
'''
    body=function(actors,'c_AdvanceWaterSurface').replace('{','{WeatherPlan storage;ww_open(r,&storage,0,1);WeatherPlan *plan=&storage;',1)
    body=body.replace('wr8(r->ds,D(WaterRestorePending),','ww_write(r,plan,D(WaterRestorePending),').replace('wr8(r->ds,D(WaterStepPhase),','ww_write(r,plan,D(WaterStepPhase),')
    body=body.replace('D(WaterRestorePending),0);','D(WaterRestorePending),0,1);').replace('D(WaterStepPhase),phase);','D(WaterStepPhase),phase,1);')
    body=body.replace('byte_dec(r,rd8(r->ds,D(WaterRestorePending))));','byte_dec(r,rd8(r->ds,D(WaterRestorePending))),1);')
    body=body.replace('        push(r,r->ds);','        ww_mark_begin(r,plan);push(r,r->ds);')
    line='r->ax=(uint16_t)((uint8_t)r->ax*rd8(r->ds,D(VgaRowStrideBytes)));';assert line in body
    body=body.replace(line,line+'r->ax=ww_mark_position(plan,r->ax);')
    body=body.replace('r->ds=pop(r);','r->ds=pop(r);ww_mark_end(r,plan);')
    body=body.replace('return UGH_OK;','{ww_complete(r,plan);return UGH_OK;}').replace('return ugh_dispatch(r->cs,G(RestoreBackgroundRectangle),r);','return ww_tail(r,plan,G(RestoreBackgroundRectangle));')
    out+=body+'\n#undef R\n#undef W\n'
    body=function(items,'c_DrawWaterSurface').replace('{','{WeatherPlan storage;ww_open(r,&storage,1,1);WeatherPlan *plan=&storage;',1)
    for name,width in [('WaterSurfaceFrameCountdown',1),('WaterSurfaceFrame',2),('WaterSurfaceByteOffset',2)]:
        pattern=r'wr'+str(width*8)+r'\(r->ds,D\('+name+r'\),([^;]+)\);'
        body,count=re.subn(pattern,lambda m:'ww_write(r,plan,D('+name+'),'+m[1]+','+str(width)+');',body);assert count
    body=body.replace('return ugh_dispatch(r->cs,target,r);','return ww_tail(r,plan,target);');out+=body+'\n'
    a=items.index('static const char water_frame0');b=items.index('static int water_tail',a);out+=items[a:b]
    body=function(items,'water_tail').replace('{','{unsigned frame=pattern==water_frame0?0u:pattern==water_frame1?1u:2u;WeatherFrameCursor cursor;const uint8_t colors[]={(uint8_t)(r->ax>>8),(uint8_t)r->bx,(uint8_t)(r->bx>>8),(uint8_t)r->cx,(uint8_t)(r->cx>>8)};weather_frame_begin(&cursor,colors,(uint8_t)r->ax);',1)
    body=body.replace('wr8(r->ds,(uint16_t)(r->di+x),value);','wr8(r->ds,(uint16_t)(r->di+x),ww_frame_pixel(&cursor,frame,x,value));')
    body=body.replace('platform_out(r->dx,1,value);','platform_out(r->dx,1,ww_frame_mask(&cursor,frame,value));').replace('platform_out(r->dx,1,15);','platform_out(r->dx,1,ww_frame_mask(&cursor,frame,15));')
    body=body.replace('return UGH_OK;','ww_require(weather_frame_next(&cursor,frame).kind==WW_DONE);return UGH_OK;');out+=body+'\n'
    for n in NAMES[2:5]:out+=function(items,'c_'+n)+'\n'
    out+='''#define R(n) rd16(r->ds,D(n))
#define RI(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WI(n,i,v) ww_write(r,plan,(uint16_t)(D(n)+(i)),(uint16_t)(v),2)
#define B(n) rd8(r->ds,D(n))
'''
    body=function(render,'c_RespawnRainParticle').replace('{','{WeatherPlan storage;ww_open(r,&storage,3,1);WeatherPlan *plan=&storage;',1)
    body=body.replace('CALL(NextRandomBelowAx,RespawnRainParticle,0x0a);','{int status=ww_random(r,plan,G(RespawnRainParticle)+0x0a);if(status)return status;}')
    out+=body.replace('return UGH_OK;','ww_complete(r,plan);return UGH_OK;')+'\n'
    body=function(render,'c_AdvanceRainParticles').replace('{','{int admitted=ww_rain_admit(r,1);',1)
    body=body.replace('r->bx=(uint16_t)((R(WaterYPixels)+1u)*2u);','r->bx=ww_first(r,1,(uint16_t)((R(WaterYPixels)+1u)*2u));')
    body=body.replace('    do {','    do {WeatherPlan storage;ww_open(r,&storage,2,admitted);WeatherPlan *plan=&storage;',1)
    body=body.replace('CALL(RespawnRainParticle,AdvanceRainParticles,0x56);','int status=ww_respawn(r,plan,G(AdvanceRainParticles)+0x56);if(status)return status;')
    body=body.replace('r->bx=sub16(r,r->bx,2,0);','ww_complete(r,plan);r->bx=ww_previous(r,r->bx);');out+=body+'\n#undef R\n#undef RI\n#undef WI\n#undef B\n'
    body=function(primitives,'c_DrawRainParticles').replace('{','{int admitted=ww_rain_admit(r,0);',1)
    line='r->bx=(uint16_t)(rd16(r->ds,D(WaterYPixels))*2u);';body=body.replace(line,'r->bx=ww_first(r,0,(uint16_t)(rd16(r->ds,D(WaterYPixels))*2u));')
    body=body.replace('    do {','    do {WeatherPlan storage;ww_open(r,&storage,4,admitted);WeatherPlan *plan=&storage;',1)
    body=body.replace('platform_out(r->dx,1,(uint8_t)r->ax);','platform_out(r->dx,1,ww_rain_mask(plan,(uint8_t)r->ax));')
    body=body.replace('wr8(r->es,r->di,(uint8_t)(r->ax>>8));','ww_rain_pixel(r,plan);')
    body=body.replace('r->bx=sub16(r,r->bx,2,0);','ww_complete(r,plan);r->bx=ww_previous(r,r->bx);');out+=body+'\n'
    body=function(primitives,'c_RestoreRainBackground').replace('{','{int admitted=ww_rain_admit(r,1);',1)
    body=body.replace('r->bx=(uint16_t)((rd16(r->ds,D(WaterYPixels))+1)*2);','r->bx=ww_first(r,1,(uint16_t)((rd16(r->ds,D(WaterYPixels))+1)*2));')
    body=body.replace('    do {','    do {WeatherPlan storage;ww_open(r,&storage,5,admitted);WeatherPlan *plan=&storage;',1)
    body=body.replace('set_al(r,rd8(r->es,r->si)); wr8(r->es,r->di,(uint8_t)r->ax);','ww_copy(r,plan);')
    body=body.replace('r->bx=sub16(r,r->bx,2,0);','ww_complete(r,plan);r->bx=ww_previous(r,r->bx);');out+=body+'\n'
    return out
def main():
    marker='/* BEGIN CHECKED WEATHER SHELLS */\n';expected=BRIDGE.read_text().split(marker)[0]+marker+generated()
    if '--write' in sys.argv:BRIDGE.write_text(expected)
    else:assert BRIDGE.read_text()==expected,'weather shell drift'
    print('PASS nine complete retained shells and four pixel-service loops')
if __name__=='__main__':main()
