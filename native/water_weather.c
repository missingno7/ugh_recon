#include "water_weather.h"
static int ww_signed(uint16_t x){return x<32768u?(int)x:(int)x-65536;}
static void ww_append(WeatherResult *r,WeatherActionKind kind,WeatherField field,uint16_t value,uint16_t position){
 r->actions[r->count++]=(WeatherAction){kind,field,value,position};
}
static void ww_store(WeatherResult *r,WeatherField field,uint16_t value){ww_append(r,WW_STORE,field,value,0);}
uint16_t weather_random_bound(uint16_t y){return (uint16_t)(320u+y);}
WeatherResult weather_particle_request(uint16_t y){WeatherResult r={0};ww_append(&r,WW_RANDOM,0,weather_random_bound(y),0);return r;}
uint16_t weather_first_particle(uint16_t y,int extra){return (uint16_t)((y+(extra?1u:0u))*2u);}
uint16_t weather_previous_particle(uint16_t index){return (uint16_t)(index-2u);}
int weather_more_particles(uint16_t index){return index<32768u;}
uint8_t weather_plane_mask(uint16_t modulo){unsigned count=modulo&31u;return count<8?(uint8_t)(1u<<count):0;}
WeatherResult water_weather_advance(WaterWeatherState *s,WaterWeatherInputs in){
 WeatherResult r={0};
 if(s->restore_pending){s->restore_pending=0;ww_store(&r,WW_PENDING,0);}
 else {
  s->previous_y=s->surface_y;ww_store(&r,WW_PREVIOUS_Y,s->previous_y);
  s->phase^=1;ww_store(&r,WW_PHASE,s->phase);
  if(!s->phase){s->fixed_y=(uint16_t)(s->fixed_y+in.increment);if(ww_signed(s->fixed_y)<0)s->fixed_y=0;}
  ww_store(&r,WW_FIXED_Y,s->fixed_y);
  s->surface_y=(uint16_t)((s->fixed_y>>5)|((s->fixed_y&32768u)?0xf800u:0u));ww_store(&r,WW_SURFACE_Y,s->surface_y);
  if(s->surface_y==s->previous_y)return r;
  /* Latch read/write policy: descending80 cells, mark bit6 in the background.
   * The service retains live VGA configuration and prescribed GC setup/reset. */
  ww_append(&r,WW_MARK_ROW,0,0,(uint16_t)((uint8_t)s->previous_y*in.row_stride));
  return r;
 }
 ww_append(&r,WW_RESTORE_ROW,0,s->previous_y,0);return r;
}
WeatherResult water_weather_marked(WaterWeatherState *s){WeatherResult r={0};s->restore_pending=(uint8_t)(s->restore_pending-1u);ww_store(&r,WW_PENDING,s->restore_pending);ww_append(&r,WW_RESTORE_ROW,0,s->previous_y,0);return r;}
WeatherResult water_weather_prepare(WaterWeatherState *s,WaterWeatherInputs in){
 WeatherResult r={0};s->countdown=(uint8_t)(s->countdown-1u);ww_store(&r,WW_COUNTDOWN,s->countdown);
 if(s->countdown&128u){s->countdown=6;ww_store(&r,WW_COUNTDOWN,6);s->frame=(uint16_t)(s->frame-1u);if(ww_signed(s->frame)<0)s->frame=2;ww_store(&r,WW_FRAME,s->frame);}
 s->byte_position=(uint16_t)((uint8_t)s->surface_y*in.row_stride);ww_store(&r,WW_BYTE_POSITION,s->byte_position);
 ww_append(&r,WW_FRAME_TAIL,0,(uint16_t)(s->frame*2u),s->byte_position);return r;
}
WeatherResult weather_particle_advance(WeatherParticle *p,uint16_t boundary,uint8_t direction,int alternate){
 WeatherResult r={0};p->previous=p->position;ww_store(&r,WW_PREVIOUS,p->previous);
 uint16_t drift=(uint16_t)(((unsigned)direction-1u)*2u-1u);
 uint16_t position=(uint16_t)(p->position+192u+(alternate?0u:96u));
 uint16_t modulo=(uint16_t)(p->modulo_four+drift+drift+(alternate?0u:drift));
 /* TEST00FC deliberately ignores high bits; do not replace with modulo>=4. */
 if(modulo&252u)position=(uint16_t)(position+drift);
 modulo&=3u;
 if(position>=boundary)ww_append(&r,WW_RESPAWN,0,0,0);
 else{p->position=position;p->modulo_four=modulo;ww_store(&r,WW_PARTICLE,position);ww_store(&r,WW_MODULO,modulo);}
 return r;
}
WeatherResult weather_particle_spawn(WeatherParticle *p,uint16_t random_value,WaterWeatherInputs in){
 WeatherResult r={0};uint16_t x,y;
 if(random_value<320u){x=random_value;y=0;}
 else{y=(uint16_t)(random_value-320u);x=in.direction==1?319:0;}
 p->position=(uint16_t)((uint8_t)y*in.row_stride+(x>>2));p->modulo_four=x&3u;
 ww_store(&r,WW_PARTICLE,p->position);ww_store(&r,WW_MODULO,p->modulo_four);return r;
}
WeatherResult weather_particle_draw(const WeatherParticle *p){WeatherResult r={0};ww_append(&r,WW_MASK,0,weather_plane_mask(p->modulo_four),0);ww_append(&r,WW_PIXEL,0,0x5b,p->position);return r;}
WeatherResult weather_particle_restore(const WeatherParticle *p){WeatherResult r={0};ww_append(&r,WW_COPY,0,0,p->previous);return r;}
/* WEATHER_COLOR_RECIPES */
static const char weather_frame0[] =
    "CDDBAACDCCBBBDDDCBBCCDBACCDCAACDCCCBBDDDCBBCCDBAACDDBAACDCCBBBDDDCBBCDCAABECCCBB"
    "CECAAADDCCBBBDDDBBBCCCAACDDBAACDCCBBBDDDCBBCCDBAACECAAADDCCBBBDDDBBCCDCAACDCCCBB"
    "CDCAABECCCBBDDDDBBBCCCAACECAAADDCCBBBDDDBBBCCCAABCDCAABECCCBBDDDDBBCDDBAACDCCBBB"
    "CDCAACDCCCBBDDDCBBCCDBAACDCAABECCCBBDDDDBBBCCCAACCDCAACDCCCBBDDDCBBCECAAADDCCBBB"
    ;
static const char weather_frame1[] =
    "CECCBBBBBBCCDDDDEEEEEDCCCECCBBBBBBBCDDEDEEEEEDCCCCECCBBBBBBCCDDDDEEEEDCBBBBBBBCD"
    "DECCBBBBBBCDDEDDEEEEEDCCCECCBBBBBBCCDDDDEEEEEDCCCDECCBBBBBBCDDEDDEECECCBBBBBBBCD"
    "EDCBBBBBBBCDDEDDEEEEECCCDECCBBBBBBCDDEDDEEEEEDCCCEDCBBBBBBBCDDEDDEECECCBBBBBBCCD"
    "ECCBBBBBBBCDDEDEEEEEDCCCEDCBBBBBBBCDDEDDEEEEECCCCECCBBBBBBBCDDEDEEEDECCBBBBBBCDD"
    ;
static const char weather_frame2[] =
    "DDDDCCCCCCDEEEDDEDEEDDDDDDDDCCCBCCCDEEDDEDEEEDDDDDDDDCCCCCCDEEEDDEDEDDDDCCBCCCDE"
    "DDDDCCBCCCDEEEDDEDEEDDDDDDDDCCCCCCDEEEDDEDEEDDDDDDDDDCCBCCCDEEEDDEDDDDDCCCBCCCDE"
    "DDDDCCBCCCDEEEDDDEEEDDDDDDDDCCBCCCDEEEDDEDEEDDDDDDDDDCCBCCCDEEEDDDEDDDDCCCCCCDEE"
    "DDDCCCBCCCDEEDDEDEEEDDDDDDDDCCBCCCDEEEDDDEEEDDDDDDDDCCCBCCCDEEDDEDEDDDDCCBCCCDEE"
    ;

uint8_t weather_frame_color(unsigned frame,unsigned cell,const uint8_t colors[5]) {
 const char *recipes[]={weather_frame0,weather_frame1,weather_frame2};return colors[(unsigned)(recipes[frame][cell]-'A')];
}
void weather_frame_begin(WeatherFrameCursor *c,const uint8_t colors[5],uint8_t mask){
 *c=(WeatherFrameCursor){.mask=mask};for(unsigned i=0;i<5;i++)c->colors[i]=colors[i];
}
WeatherAction weather_frame_next(WeatherFrameCursor *c,unsigned frame){
 if(c->finished)return (WeatherAction){.kind=WW_DONE};
 if(c->mask_due){c->mask_due=0;if(c->plane==4){c->finished=1;return (WeatherAction){.kind=WW_MASK,.value=15};}
  c->mask=(uint8_t)(c->mask<<1);return (WeatherAction){.kind=WW_MASK,.value=c->mask};}
 WeatherAction event={.kind=WW_PIXEL,.value=weather_frame_color(frame,c->plane*80+c->column,c->colors),.position=(uint16_t)c->column};
 if(++c->column==80){c->column=0;c->plane++;c->mask_due=1;}return event;
}
