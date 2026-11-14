#include "platform.h"
#include "../water_weather.h"
#include <stdlib.h>
typedef struct WeatherPlan {
 WaterWeatherState state;WaterWeatherInputs inputs;WeatherParticle particle;
 WeatherResult result;size_t consumed;uint16_t data,index,surface;
 WeatherAction service;int active,particle_mode,tail_seen,service_pending;
} WeatherPlan;
static void ww_require(int c){if(!c)abort();}
static uint16_t ww_read(Regs *r,uint16_t base,uint16_t index){return rd16(r->ds,(uint16_t)(base+index));}
static WeatherAction ww_take(WeatherPlan *p,WeatherActionKind kind){
 ww_require(p->consumed<p->result.count);WeatherAction action=p->result.actions[p->consumed++];ww_require(action.kind==kind);return action;
}
static void ww_write(Regs *r,WeatherPlan *p,uint16_t address,uint16_t value,unsigned width){
 if(p->active){WeatherAction e=ww_take(p,WW_STORE);static const uint16_t base[]={D(WaterY32),D(WaterYPixels),D(PreviousWaterSurfaceY),D(WaterSurfaceByteOffset),D(WaterSurfaceFrame),D(WaterSurfaceFrameCountdown),D(WaterStepPhase),D(WaterRestorePending),D(RainParticleOffsets),D(RainPreviousOffsets),D(RainParticleXModuloFour)};
  ww_require(e.field<=WW_MODULO && address==(uint16_t)(base[e.field]+(e.field>=WW_PARTICLE?p->index:0)) && value==e.value && width==((e.field>=WW_COUNTDOWN && e.field<=WW_PENDING)?1u:2u));value=e.value;}
 if(width==1)wr8(r->ds,address,(uint8_t)value);else wr16(r->ds,address,value);
}
static int ww_projection(Regs *r,WeatherPlan *p){
#ifdef ACTOR_VERIFY
 if(p->particle_mode){return p->particle.position==ww_read(r,D(RainParticleOffsets),p->index) && p->particle.previous==ww_read(r,D(RainPreviousOffsets),p->index) && p->particle.modulo_four==ww_read(r,D(RainParticleXModuloFour),p->index);}
 WaterWeatherState *s=&p->state;
 return s->fixed_y==ww_read(r,D(WaterY32),0) && s->surface_y==ww_read(r,D(WaterYPixels),0) && s->previous_y==ww_read(r,D(PreviousWaterSurfaceY),0) && s->byte_position==ww_read(r,D(WaterSurfaceByteOffset),0) && s->frame==ww_read(r,D(WaterSurfaceFrame),0) && s->countdown==rd8(r->ds,D(WaterSurfaceFrameCountdown)) && s->phase==rd8(r->ds,D(WaterStepPhase)) && s->restore_pending==rd8(r->ds,D(WaterRestorePending));
#else
 (void)r;(void)p;return 1;
#endif
}
static void ww_complete(Regs *r,WeatherPlan *p){if(p->active)ww_require(!p->service_pending && p->consumed==p->result.count && (p->tail_seen || ww_projection(r,p)));}
static void ww_open(Regs *r,WeatherPlan *p,unsigned operation,int admitted){
 *p=(WeatherPlan){0};if(!admitted || r->ds!=DATA_SEG || r->cs!=GAME_SEG)return;
 p->data=r->ds;p->index=r->bx;p->surface=rd16(r->ds,D(WaterYPixels));
 p->inputs=(WaterWeatherInputs){rd16(r->ds,D(WaterSurfaceStep)),rd8(r->ds,D(VgaRowStrideBytes)),rd8(r->ds,D(LevelRainDirection))};
 p->state=(WaterWeatherState){rd16(r->ds,D(WaterY32)),p->surface,rd16(r->ds,D(PreviousWaterSurfaceY)),rd16(r->ds,D(WaterSurfaceByteOffset)),rd16(r->ds,D(WaterSurfaceFrame)),rd8(r->ds,D(WaterSurfaceFrameCountdown)),rd8(r->ds,D(WaterStepPhase)),rd8(r->ds,D(WaterRestorePending))};
 if(operation>=2){if((r->bx&1u) || r->bx>=386u)return;p->particle_mode=1;p->particle=(WeatherParticle){ww_read(r,D(RainParticleOffsets),r->bx),ww_read(r,D(RainPreviousOffsets),r->bx),ww_read(r,D(RainParticleXModuloFour),r->bx)};}
 if(operation==0)p->result=water_weather_advance(&p->state,p->inputs);
 else if(operation==1){p->result=water_weather_prepare(&p->state,p->inputs);uint16_t key=p->result.actions[p->result.count-1].value;if(key>4)return;const uint16_t targets[]={G(DrawWaterSurfaceFrame0),G(DrawWaterSurfaceFrame1),G(DrawWaterSurfaceFrame2)};if(rd16(r->cs,(uint16_t)(G(WaterSurfaceDispatch)+key))!=targets[key/2u])return;}
 else if(operation==2)p->result=weather_particle_advance(&p->particle,p->state.byte_position,p->inputs.direction,(r->bx&2u)!=0);
 else if(operation==3)p->result=weather_particle_request(p->surface);
 else if(operation==4)p->result=weather_particle_draw(&p->particle);
 else if(operation==5)p->result=weather_particle_restore(&p->particle);
 p->active=1;
}
static void ww_mark_begin(Regs *r,WeatherPlan *p){if(p->active){p->service=ww_take(p,WW_MARK_ROW);ww_require(p->consumed==p->result.count && ww_projection(r,p));p->service_pending=1;}}
static uint16_t ww_mark_position(WeatherPlan *p,uint16_t expected){if(p->active){ww_require(p->service_pending && p->service.position==expected);return p->service.position;}return expected;}
static void ww_mark_end(Regs *r,WeatherPlan *p){if(p->active){ww_require(p->service_pending && ww_projection(r,p));p->service_pending=0;p->result=water_weather_marked(&p->state);p->consumed=0;}}
static int ww_tail(Regs *r,WeatherPlan *p,uint16_t target){
 if(p->active){WeatherAction e=ww_take(p,target==G(RestoreBackgroundRectangle)?WW_RESTORE_ROW:WW_FRAME_TAIL);
  if(e.kind==WW_RESTORE_ROW){ww_require(r->ax==0 && r->bx==e.value && r->cx==320 && r->dx==1);r->bx=e.value;}
  else {ww_require(r->si==e.value && target==rd16(r->cs,(uint16_t)(G(WaterSurfaceDispatch)+e.value)) && r->di==(uint16_t)(rd16(r->cs,G(DrawPagePointer))+e.position) && r->ds==rd16(r->cs,G(DrawPagePointer)+2u));r->si=e.value;r->di=(uint16_t)(rd16(r->cs,G(DrawPagePointer))+e.position);}
  Regs data=*r;data.ds=p->data;ww_require(ww_projection(&data,p) && !p->service_pending && p->consumed==p->result.count);p->tail_seen=1;
 }
 return ugh_dispatch(r->cs,target,r);
}
static int ww_random(Regs *r,WeatherPlan *p,uint16_t ret){
 if(p->active){WeatherAction e=ww_take(p,WW_RANDOM);ww_require(r->ax==e.value && p->consumed==p->result.count && !p->service_pending && ww_projection(r,p));r->ax=e.value;p->service_pending=1;}
 int status=ugh_call_near(G(NextRandomBelowAx),ret,r);
 if(p->active && !status){p->service_pending=0;p->result=weather_particle_spawn(&p->particle,r->ax,p->inputs);p->consumed=0;}
 return status;
}
static int ww_respawn(Regs *r,WeatherPlan *p,uint16_t ret){
 if(p->active){ww_take(p,WW_RESPAWN);ww_require(p->consumed==p->result.count && r->bx==p->index && ww_projection(r,p));r->bx=p->index;p->tail_seen=1;}
 return ugh_call_near(G(RespawnRainParticle),ret,r);
}
static int ww_rain_admit(Regs *r,int extra){return r->ds==DATA_SEG && r->cs==GAME_SEG && weather_first_particle(rd16(r->ds,D(WaterYPixels)),extra)<386u;}
static uint16_t ww_first(Regs *r,int extra,uint16_t expected){if(r->ds!=DATA_SEG)return expected;uint16_t actual=weather_first_particle(rd16(r->ds,D(WaterYPixels)),extra);ww_require(actual==expected);return actual;}
static uint16_t ww_previous(Regs *r,uint16_t index){uint16_t value=weather_previous_particle(index);ww_require(value==sub16(r,index,2,0));ww_require(weather_more_particles(value)==((int16_t)value>=0));return value;}
static uint8_t ww_rain_mask(WeatherPlan *p,uint8_t expected){if(p->active){WeatherAction e=ww_take(p,WW_MASK);ww_require(e.value==expected);return (uint8_t)e.value;}return expected;}
static void ww_rain_pixel(Regs *r,WeatherPlan *p){if(p->active){WeatherAction e=ww_take(p,WW_PIXEL);ww_require(r->es==0xa000 && r->di==(uint16_t)(r->bp+e.position) && (uint8_t)(r->ax>>8)==e.value);r->di=(uint16_t)(r->bp+e.position);wr8(r->es,r->di,(uint8_t)e.value);}else wr8(r->es,r->di,(uint8_t)(r->ax>>8));}
static void ww_copy(Regs *r,WeatherPlan *p){if(p->active){WeatherAction e=ww_take(p,WW_COPY);ww_require(r->es==0xa000 && r->si==(uint16_t)(r->cx+e.position) && r->di==(uint16_t)(r->bp+e.position) && ww_projection(r,p));r->si=(uint16_t)(r->cx+e.position);r->di=(uint16_t)(r->bp+e.position);}set_al(r,rd8(r->es,r->si));wr8(r->es,r->di,(uint8_t)r->ax);}
static uint8_t ww_frame_pixel(WeatherFrameCursor *c,unsigned frame,unsigned column,uint8_t expected){WeatherAction e=weather_frame_next(c,frame);ww_require(e.kind==WW_PIXEL && e.position==column && e.value==expected);return (uint8_t)e.value;}
static uint8_t ww_frame_mask(WeatherFrameCursor *c,unsigned frame,uint8_t expected){WeatherAction e=weather_frame_next(c,frame);ww_require(e.kind==WW_MASK && e.value==expected);return (uint8_t)e.value;}
/* BEGIN CHECKED WEATHER SHELLS */
static uint16_t shift(Regs *r,uint16_t v,unsigned n,int right) {
    for(unsigned i=0;i<n;i++) {
        flag(r,CF,right?(v&1):(v&0x8000));
        v=right?(uint16_t)((v>>1)|(v&0x8000)):(uint16_t)(v<<1);
    }
    szp(r,v,16); if(n==1) flag(r,OF,right?0:(!!(v&0x8000)^!!(r->flags&CF)));
    return v;
}

static uint8_t byte_sub(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^v)&128)!=0);
    flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8); return v;
}

static uint8_t byte_dec(Regs *r,uint8_t a) {
    uint16_t cf=r->flags&CF; uint8_t v=byte_sub(r,a,1); flag(r,CF,cf); return v;
}

static uint16_t inc(Regs *r,uint16_t v) {
    uint16_t cf=r->flags&CF; v=add16(r,v,1,0); flag(r,CF,cf); return v;
}

static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }

static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

static uint8_t dec8(Regs *r, uint8_t x) {
    uint8_t v=(uint8_t)(x-1);
    flag(r,OF,x==128); flag(r,AF,((x^1u^v)&16u)!=0); szp(r,v,8);
    return v; /* DEC preserves CF, including at zero. */
}

static uint16_t cell(uint16_t base, uint16_t index) { return (uint16_t)(base+index); }

static void cmp8(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^v)&128)!=0);
    flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8);
}

#define R(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define W(n,i,v) ww_write(r,plan,(uint16_t)(D(n)+(i)),(uint16_t)(v),2)
EXPORT int c_AdvanceWaterSurface(Regs *r) {WeatherPlan storage;ww_open(r,&storage,0,1);WeatherPlan *plan=&storage;
    logic(r,rd8(r->ds,D(WaterRestorePending)),8);
    if(!(r->flags&ZF)) ww_write(r,plan,D(WaterRestorePending),0,1);
    else {
        r->ax=R(WaterYPixels,0); W(PreviousWaterSurfaceY,0,r->ax); r->ax=R(WaterY32,0);
        uint8_t phase=(uint8_t)logic(r,rd8(r->ds,D(WaterStepPhase))^1,8); ww_write(r,plan,D(WaterStepPhase),phase,1);
        if(!phase) { r->ax=add16(r,r->ax,R(WaterSurfaceStep,0),0); if(r->flags&SF) r->ax=logic(r,0,16); }
        W(WaterY32,0,r->ax); r->ax=shift(r,r->ax,5,1); W(WaterYPixels,0,r->ax); sub16(r,r->ax,R(PreviousWaterSurfaceY,0),0);
        if(r->flags&ZF) {ww_complete(r,plan);return UGH_OK;}
        ww_mark_begin(r,plan);push(r,r->ds); r->dx=0x3ce; set_al(r,8); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=inc(r,r->dx); set_al(r,0x40); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=dec16(r,r->dx); set_al(r,3); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=inc(r,r->dx); set_al(r,0x10); platform_out(r->dx,1,(uint8_t)r->ax);
        r->ax=R(PreviousWaterSurfaceY,0); r->ax=(uint16_t)((uint8_t)r->ax*rd8(r->ds,D(VgaRowStrideBytes)));r->ax=ww_mark_position(plan,r->ax);
        flag(r,CF,r->ax>255); flag(r,OF,r->ax>255);
        r->si=rd16(r->cs,G(BackgroundPagePointer)); r->ds=rd16(r->cs,(uint16_t)(G(BackgroundPagePointer)+2)); r->si=add16(r,r->si,r->ax,0);
        r->bx=79; set_al(r,0x40);
        do { set_ah(r,rd8(r->ds,(uint16_t)(r->bx+r->si))); wr8(r->ds,(uint16_t)(r->bx+r->si),(uint8_t)r->ax); r->bx=dec16(r,r->bx); } while(!(r->flags&SF));
        r->dx=0x3ce; set_al(r,8); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=inc(r,r->dx); set_al(r,255); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=dec16(r,r->dx); set_al(r,3); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=inc(r,r->dx); set_al(r,(uint8_t)logic(r,0,8)); platform_out(r->dx,1,(uint8_t)r->ax);
        r->ds=pop(r);ww_mark_end(r,plan); ww_write(r,plan,D(WaterRestorePending),byte_dec(r,rd8(r->ds,D(WaterRestorePending))),1);
    }
    r->ax=logic(r,0,16); r->bx=R(PreviousWaterSurfaceY,0); r->cx=320; r->dx=1;
    return ww_tail(r,plan,G(RestoreBackgroundRectangle));
}

#undef R
#undef W
EXPORT int c_DrawWaterSurface(Regs *r) {WeatherPlan storage;ww_open(r,&storage,1,1);WeatherPlan *plan=&storage;
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,r->ds);
    r->si=rd16(r->ds,D(WaterSurfaceFrame));
    uint8_t countdown=dec8(r,rd8(r->ds,D(WaterSurfaceFrameCountdown)));
    ww_write(r,plan,D(WaterSurfaceFrameCountdown),countdown,1);
    if(countdown&128u) {
        ww_write(r,plan,D(WaterSurfaceFrameCountdown),6,1);
        r->si=dec16(r,r->si);
        if((int16_t)r->si<0) r->si=2;
        ww_write(r,plan,D(WaterSurfaceFrame),r->si,2);
    }
    r->ax=(uint16_t)((uint8_t)rd16(r->ds,D(WaterYPixels))*rd8(r->ds,D(VgaRowStrideBytes)));
    ww_write(r,plan,D(WaterSurfaceByteOffset),r->ax,2);
    r->di=rd16(r->cs,G(DrawPagePointer)); r->ds=rd16(r->cs,G(DrawPagePointer)+2);
    r->di=add16(r,r->di,r->ax,0);
    r->dx=0x3c4; set_al(r,2); platform_out(r->dx,1,2);
    uint16_t cf=r->flags&CF;
    r->dx=add16(r,r->dx,1,0); flag(r,CF,cf);
    r->ax=0x5401; platform_out(r->dx,1,1);
    r->bx=0x5655; r->cx=0x5857;
    uint16_t old=r->si; r->si=(uint16_t)(r->si<<1);
    flag(r,CF,old&0x8000); flag(r,OF,((old^r->si)&0x8000)!=0); szp(r,r->si,16);
    uint16_t target=rd16(r->cs,cell(G(WaterSurfaceDispatch),r->si));
    return ww_tail(r,plan,target);
}

static const char water_frame0[] =
    "CDDBAACDCCBBBDDDCBBCCDBACCDCAACDCCCBBDDDCBBCCDBAACDDBAACDCCBBBDDDCBBCDCAABECCCBB"
    "CECAAADDCCBBBDDDBBBCCCAACDDBAACDCCBBBDDDCBBCCDBAACECAAADDCCBBBDDDBBCCDCAACDCCCBB"
    "CDCAABECCCBBDDDDBBBCCCAACECAAADDCCBBBDDDBBBCCCAABCDCAABECCCBBDDDDBBCDDBAACDCCBBB"
    "CDCAACDCCCBBDDDCBBCCDBAACDCAABECCCBBDDDDBBBCCCAACCDCAACDCCCBBDDDCBBCECAAADDCCBBB"
    ;
static const char water_frame1[] =
    "CECCBBBBBBCCDDDDEEEEEDCCCECCBBBBBBBCDDEDEEEEEDCCCCECCBBBBBBCCDDDDEEEEDCBBBBBBBCD"
    "DECCBBBBBBCDDEDDEEEEEDCCCECCBBBBBBCCDDDDEEEEEDCCCDECCBBBBBBCDDEDDEECECCBBBBBBBCD"
    "EDCBBBBBBBCDDEDDEEEEECCCDECCBBBBBBCDDEDDEEEEEDCCCEDCBBBBBBBCDDEDDEECECCBBBBBBCCD"
    "ECCBBBBBBBCDDEDEEEEEDCCCEDCBBBBBBBCDDEDDEEEEECCCCECCBBBBBBBCDDEDEEEDECCBBBBBBCDD"
    ;
static const char water_frame2[] =
    "DDDDCCCCCCDEEEDDEDEEDDDDDDDDCCCBCCCDEEDDEDEEEDDDDDDDDCCCCCCDEEEDDEDEDDDDCCBCCCDE"
    "DDDDCCBCCCDEEEDDEDEEDDDDDDDDCCCCCCDEEEDDEDEEDDDDDDDDDCCBCCCDEEEDDEDDDDDCCCBCCCDE"
    "DDDDCCBCCCDEEEDDDEEEDDDDDDDDCCBCCCDEEEDDEDEEDDDDDDDDDCCBCCCDEEEDDDEDDDDCCCCCCDEE"
    "DDDCCCBCCCDEEDDEDEEEDDDDDDDDCCBCCCDEEEDDDEEEDDDDDDDDCCCBCCCDEEDDEDEDDDDCCBCCCDEE"
    ;

static int water_tail(Regs *r, const char *pattern) {unsigned frame=pattern==water_frame0?0u:pattern==water_frame1?1u:2u;WeatherFrameCursor cursor;const uint8_t colors[]={(uint8_t)(r->ax>>8),(uint8_t)r->bx,(uint8_t)(r->bx>>8),(uint8_t)r->cx,(uint8_t)(r->cx>>8)};weather_frame_begin(&cursor,colors,(uint8_t)r->ax);
    for(unsigned plane=0;plane<4;plane++) {
        for(unsigned x=0;x<80;x++) {
            uint8_t value;
            switch(pattern[plane*80+x]) {
            case 'A': value=(uint8_t)(r->ax>>8); break;
            case 'B': value=(uint8_t)r->bx; break;
            case 'C': value=(uint8_t)(r->bx>>8); break;
            case 'D': value=(uint8_t)r->cx; break;
            default: value=(uint8_t)(r->cx>>8); break;
            }
            wr8(r->ds,(uint16_t)(r->di+x),ww_frame_pixel(&cursor,frame,x,value));
        }
        if(plane<3) {
            uint8_t old=(uint8_t)r->ax, value=(uint8_t)(old<<1);
            flag(r,CF,old&128); flag(r,OF,((old^value)&128)!=0);
            szp(r,value,8); set_al(r,value);
            platform_out(r->dx,1,ww_frame_mask(&cursor,frame,value));
        }
    }
    set_al(r,15); platform_out(r->dx,1,ww_frame_mask(&cursor,frame,15));
    r->ds=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2);
    ww_require(weather_frame_next(&cursor,frame).kind==WW_DONE);return UGH_OK;
}

EXPORT int c_DrawWaterSurfaceFrame0(Regs *r) { return water_tail(r,water_frame0); }

EXPORT int c_DrawWaterSurfaceFrame1(Regs *r) { return water_tail(r,water_frame1); }

EXPORT int c_DrawWaterSurfaceFrame2(Regs *r) { return water_tail(r,water_frame2); }

#define R(n) rd16(r->ds,D(n))
#define RI(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WI(n,i,v) ww_write(r,plan,(uint16_t)(D(n)+(i)),(uint16_t)(v),2)
#define B(n) rd8(r->ds,D(n))
EXPORT int c_RespawnRainParticle(Regs *r) {WeatherPlan storage;ww_open(r,&storage,3,1);WeatherPlan *plan=&storage;
    r->ax=add16(r,320,R(WaterYPixels),0);
    {int status=ww_random(r,plan,G(RespawnRainParticle)+0x0a);if(status)return status;}
    sub16(r,r->ax,320,0);
    if(r->ax<320) { r->cx=r->ax; r->ax=logic(r,0,16); }
    else {
        r->ax=sub16(r,r->ax,320,0);
        cmp8(r,B(LevelRainDirection),1);
        if(B(LevelRainDirection)==1) r->cx=319;
        else r->cx=logic(r,0,16);
    }
    r->ax=(uint16_t)((uint8_t)r->ax*B(VgaRowStrideBytes));
    r->dx=(uint16_t)(r->cx>>2);
    r->ax=add16(r,r->ax,r->dx,0);
    WI(RainParticleOffsets,r->bx,r->ax);
    r->cx=logic(r,r->cx&3,16); WI(RainParticleXModuloFour,r->bx,r->cx);
    ww_complete(r,plan);return UGH_OK;
}

EXPORT int c_AdvanceRainParticles(Regs *r) {int admitted=ww_rain_admit(r,1);
    r->bx=ww_first(r,1,(uint16_t)((R(WaterYPixels)+1u)*2u));
    r->ax=B(LevelRainDirection); r->bp=(uint16_t)((r->ax-1u)*2u-1u);
    do {WeatherPlan storage;ww_open(r,&storage,2,admitted);WeatherPlan *plan=&storage;
        r->ax=RI(RainParticleOffsets,r->bx); WI(RainPreviousOffsets,r->bx,r->ax);
        r->ax=(uint16_t)(r->ax+192u);
        if(!(r->bx&2)) r->ax=(uint16_t)(r->ax+96u);
        r->cx=RI(RainParticleXModuloFour,r->bx);
        r->cx=(uint16_t)(r->cx+r->bp+r->bp);
        if(!(r->bx&2)) r->cx=(uint16_t)(r->cx+r->bp);
        if(r->cx&0xfc) r->ax=(uint16_t)(r->ax+r->bp);
        r->cx=logic(r,r->cx&3,16);
        sub16(r,r->ax,R(WaterSurfaceByteOffset),0);
        if(r->ax>=R(WaterSurfaceByteOffset)) { int status=ww_respawn(r,plan,G(AdvanceRainParticles)+0x56);if(status)return status; }
        else { WI(RainParticleOffsets,r->bx,r->ax); WI(RainParticleXModuloFour,r->bx,r->cx); }
        ww_complete(r,plan);r->bx=ww_previous(r,r->bx);
    } while(!(r->bx&0x8000u));
    return UGH_OK;
}

#undef R
#undef RI
#undef WI
#undef B
EXPORT int c_DrawRainParticles(Regs *r) {int admitted=ww_rain_admit(r,0);
    r->bx=ww_first(r,0,(uint16_t)(rd16(r->ds,D(WaterYPixels))*2u));
    r->dx=0x3c4; set_al(r,2); platform_out(r->dx,1,2); r->dx++;
    r->es=0xa000; r->bp=rd16(r->cs,G(DrawPagePointer)); set_ah(r,0x5b);
    do {WeatherPlan storage;ww_open(r,&storage,4,admitted);WeatherPlan *plan=&storage;
        r->cx=rd16(r->ds,(uint16_t)(D(RainParticleXModuloFour)+r->bx));
        unsigned shift=r->cx&31u;
        set_al(r,shift<8 ? (uint8_t)(1u<<shift) : 0);
        platform_out(r->dx,1,ww_rain_mask(plan,(uint8_t)r->ax));
        r->di=rd16(r->ds,(uint16_t)(D(RainParticleOffsets)+r->bx));
        r->di=(uint16_t)(r->di+r->bp);
        ww_rain_pixel(r,plan);
        ww_complete(r,plan);r->bx=ww_previous(r,r->bx);
    } while(!(r->bx&0x8000u));
    set_al(r,15); platform_out(r->dx,1,15);
    return UGH_OK;
}

EXPORT int c_RestoreRainBackground(Regs *r) {int admitted=ww_rain_admit(r,1);
    r->dx=0x3ce; set_al(r,8); platform_out(r->dx,1,8);
    r->dx=0x3cf; set_al(r,0); platform_out(r->dx,1,0);
    r->di=0xa000; r->es=r->di; r->cx=rd16(r->cs,G(BackgroundPagePointer));
    r->bp=rd16(r->cs,G(DrawPagePointer));
    r->bx=ww_first(r,1,(uint16_t)((rd16(r->ds,D(WaterYPixels))+1)*2));
    do {WeatherPlan storage;ww_open(r,&storage,5,admitted);WeatherPlan *plan=&storage;
        r->si=r->cx; r->di=r->bp;
        r->si=add16(r,r->si,rd16(r->ds,(uint16_t)(D(RainPreviousOffsets)+r->bx)),0);
        r->di=add16(r,r->di,rd16(r->ds,(uint16_t)(D(RainPreviousOffsets)+r->bx)),0);
        ww_copy(r,plan);
        ww_complete(r,plan);r->bx=ww_previous(r,r->bx);
    } while((int16_t)r->bx>=0);
    set_al(r,255); platform_out(r->dx,1,255); return UGH_OK;
}

