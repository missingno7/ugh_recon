#include "session.h"

static uint16_t session_pixel(uint16_t value){return (uint16_t)((value>>5)|((value&0x8000u)?0xf800u:0));}
int session_should_move(uint16_t level,uint16_t rate){return (int16_t)level>192 || (int16_t)rate<=0;}
uint16_t session_password_list_key(uint16_t bytes){return (uint16_t)(bytes-2u);}
uint16_t session_level_count_key(uint16_t bytes){return (uint16_t)(bytes-2u);}
void session_begin(SessionProcess *p){
    p->phase=SP_PASSWORD;p->player_cursor=p->selected_level=0;p->completed_frames=0;
    p->pending=p->failed=0;p->request=(SessionRequest){SESSION_INVALID,0,0,0,0};
}
SessionRequest session_next(SessionProcess *p,SessionWorld w){
    SessionRequest e={SESSION_INVALID,0,0,0,0};
    if(p->failed || p->pending){p->failed=1;return e;}
    switch(p->phase){
    case SP_PASSWORD:e.action=SESSION_PASSWORD;e.index=session_password_list_key(w.player_bytes);break;
    case SP_SELECT_LEVEL:e.action=SESSION_SELECT_LEVEL;e.value=p->selected_level;break;
    case SP_PREGAME:e.action=SESSION_PREGAME;break;
    case SP_STOP_INITIAL_MUSIC:e.action=SESSION_STOP_INITIAL_MUSIC;e.value=17;break;
    case SP_RESET_GAME:e.action=SESSION_RESET_GAME;break;
    case SP_BLACK_PALETTE:e.action=SESSION_BLACK_PALETTE;break;
    case SP_INITIALIZE_LEVEL:e.action=SESSION_INITIALIZE_LEVEL;break;
    case SP_START_MUSIC:e.action=SESSION_START_MUSIC;e.value=0xa5;break;
    case SP_FRAME_BEGIN:
        if((int16_t)w.fade_level<0)e.action=SESSION_STOP_LEVEL_MUSIC;
        else if((int16_t)w.fade_level<=256)e.action=SESSION_FADE_UPLOAD;
        else e.action=SESSION_WAIT_RETRACE;
        e.value=e.action==SESSION_STOP_LEVEL_MUSIC?17:w.fade_level;break;
    case SP_FADE_ADVANCE:e.action=SESSION_FADE_ADVANCE;e.value=(uint16_t)(w.palette_reply+w.fade_rate);break;
    case SP_HUD:e.action=SESSION_HUD;break;
    case SP_ERASE_PLAYER_BEGIN:e.action=SESSION_ERASE_PLAYER_BEGIN;break;
    case SP_ERASE_PLAYER:e.action=SESSION_ERASE_PLAYER;e.index=p->player_cursor;break;
    case SP_ERASE_PLAYER_NEXT:e.action=SESSION_ERASE_PLAYER_NEXT;e.index=(uint16_t)(p->player_cursor+2u);e.decision=(uint8_t)(e.index!=w.player_bytes);break;
    case SP_ERASE_ACTORS:e.action=SESSION_ERASE_ACTORS;break;
    case SP_ERASE_ENEMIES:e.action=SESSION_ERASE_ENEMIES;break;
    case SP_ERASE_ITEMS:e.action=SESSION_ERASE_ITEMS;break;
    case SP_RESTORE_RAIN:e.action=w.rain?SESSION_RESTORE_RAIN:SESSION_ADVANCE_WATER;break;
    case SP_ADVANCE_WATER:e.action=SESSION_ADVANCE_WATER;break;
    case SP_IO_POINT:e.action=SESSION_IO_POINT;break;
    case SP_POLL_CONTROLS:e.action=SESSION_POLL_CONTROLS;break;
    case SP_PAUSE_RELEASE:e.action=SESSION_PAUSE_RELEASE;break;
    case SP_PAUSE_MAKE:e.action=SESSION_PAUSE_MAKE;break;
    case SP_PAUSE_BREAK:e.action=SESSION_PAUSE_BREAK;break;
    case SP_ESCAPE:e.action=SESSION_ESCAPE;e.decision=(uint8_t)(w.scan==1);e.index=(uint16_t)((int16_t)w.fade_rate>=0);e.other=0xfffe;e.value=(uint16_t)(w.fade_level-2u);break;
    case SP_MOVE_BEGIN:e.action=SESSION_MOVE_BEGIN;e.decision=(uint8_t)session_should_move(w.fade_level,w.fade_rate);break;
    case SP_MOVE_PLAYER:e.action=SESSION_MOVE_PLAYER;e.index=p->player_cursor;break;
    case SP_MOVE_NEXT:e.action=SESSION_MOVE_NEXT;e.index=(uint16_t)(p->player_cursor+2u);e.decision=(uint8_t)(e.index==w.player_count);break;
    case SP_UPDATE_ACTORS:e.action=SESSION_UPDATE_ACTORS;break;
    case SP_UPDATE_ENEMIES:e.action=SESSION_UPDATE_ENEMIES;break;
    case SP_UPDATE_ITEMS:e.action=SESSION_UPDATE_ITEMS;break;
    case SP_DRAW_ACTORS:e.action=SESSION_DRAW_ACTORS;break;
    case SP_DRAW_ENEMIES_BACK:e.action=SESSION_DRAW_ENEMIES_BACK;break;
    case SP_DRAW_PLAYER_BEGIN:e.action=SESSION_DRAW_PLAYER_BEGIN;break;
    case SP_DRAW_PLAYER:e.action=SESSION_DRAW_PLAYER;e.index=p->player_cursor;break;
    case SP_DRAW_PLAYER_NEXT:e.action=SESSION_DRAW_PLAYER_NEXT;e.index=(uint16_t)(p->player_cursor+2u);e.decision=(uint8_t)(e.index!=w.player_bytes);break;
    case SP_DRAW_ENEMIES_FRONT:e.action=SESSION_DRAW_ENEMIES_FRONT;break;
    case SP_DRAW_ITEMS:e.action=SESSION_DRAW_ITEMS;break;
    case SP_DRAW_OVERLAYS:e.action=SESSION_DRAW_OVERLAYS;break;
    case SP_ADVANCE_RAIN:e.action=w.rain?SESSION_ADVANCE_RAIN:SESSION_DRAW_WATER;break;
    case SP_DRAW_RAIN:e.action=SESSION_DRAW_RAIN;break;
    case SP_DRAW_WATER:e.action=SESSION_DRAW_WATER;break;
    case SP_SWAP_PAGE:e.action=SESSION_SWAP_PAGE;break;
    case SP_STOP_LEVEL_MUSIC:e.action=SESSION_STOP_LEVEL_MUSIC;e.value=17;break;
    case SP_OUTCOME:e.action=SESSION_OUTCOME;e.decision=(uint8_t)((w.completion&128u)!=0);break;
    case SP_DECREMENT_LIVES:e.action=SESSION_DECREMENT_LIVES;e.value=(uint8_t)(w.lives-1u);e.decision=(uint8_t)(e.value!=0 && !(e.value&128u));break;
    case SP_RESET_MULTIPLIER:e.action=SESSION_RESET_MULTIPLIER;e.value=1;break;
    case SP_INCREMENT_LEVEL:e.action=SESSION_INCREMENT_LEVEL;e.value=(uint16_t)(w.level+1u);break;
    case SP_TEST_LEVEL_LIMIT:e.action=SESSION_TEST_LEVEL_LIMIT;e.index=session_level_count_key(w.player_bytes);e.decision=(uint8_t)(w.level<w.level_limit);break;
    case SP_RETURN:e.action=SESSION_RETURN;break;
    case SP_DONE:e.action=SESSION_FINISHED;return e;
    }
    p->request=e;p->pending=1;return e;
}
int session_acknowledge(SessionProcess *p,SessionAction action,SessionWorld w){
    if(p->failed || !p->pending || p->request.action!=action){p->failed=1;return 0;}
    SessionRequest e=p->request;p->pending=0;
    switch(action){
    case SESSION_PASSWORD:p->selected_level=w.password_reply;p->phase=SP_SELECT_LEVEL;break;
    case SESSION_SELECT_LEVEL:p->phase=SP_PREGAME;break;case SESSION_PREGAME:p->phase=SP_STOP_INITIAL_MUSIC;break;
    case SESSION_STOP_INITIAL_MUSIC:p->phase=SP_RESET_GAME;break;case SESSION_RESET_GAME:p->phase=SP_BLACK_PALETTE;break;
    case SESSION_BLACK_PALETTE:p->phase=SP_INITIALIZE_LEVEL;break;case SESSION_INITIALIZE_LEVEL:p->completed_frames=0;p->phase=SP_START_MUSIC;break;
    case SESSION_START_MUSIC:p->phase=SP_FRAME_BEGIN;break;
    case SESSION_FADE_UPLOAD:p->phase=SP_FADE_ADVANCE;break;
    case SESSION_FADE_ADVANCE:case SESSION_WAIT_RETRACE:p->phase=SP_HUD;break;
    case SESSION_HUD:p->phase=SP_ERASE_PLAYER_BEGIN;break;
    case SESSION_ERASE_PLAYER_BEGIN:p->player_cursor=0;p->phase=SP_ERASE_PLAYER;break;
    case SESSION_ERASE_PLAYER:p->phase=SP_ERASE_PLAYER_NEXT;break;
    case SESSION_ERASE_PLAYER_NEXT:p->player_cursor=e.index;p->phase=e.decision?SP_ERASE_PLAYER:SP_ERASE_ACTORS;break;
    case SESSION_ERASE_ACTORS:p->phase=SP_ERASE_ENEMIES;break;
    case SESSION_ERASE_ENEMIES:p->phase=SP_ERASE_ITEMS;break;
    case SESSION_ERASE_ITEMS:p->phase=SP_RESTORE_RAIN;break;
    case SESSION_RESTORE_RAIN:p->phase=SP_ADVANCE_WATER;break;
    case SESSION_ADVANCE_WATER:p->phase=SP_IO_POINT;break;
    case SESSION_IO_POINT:p->phase=SP_POLL_CONTROLS;break;
    case SESSION_POLL_CONTROLS:p->phase=w.scan==0x19?SP_PAUSE_RELEASE:SP_ESCAPE;break;
    case SESSION_PAUSE_RELEASE:p->phase=w.scan==0x99?SP_PAUSE_MAKE:SP_PAUSE_RELEASE;break;
    case SESSION_PAUSE_MAKE:p->phase=(w.scan&128u)?SP_PAUSE_MAKE:SP_PAUSE_BREAK;break;
    case SESSION_PAUSE_BREAK:p->phase=(w.scan&128u)?SP_ESCAPE:SP_PAUSE_BREAK;break;
    case SESSION_ESCAPE:p->phase=SP_MOVE_BEGIN;break;
    case SESSION_MOVE_BEGIN:p->player_cursor=0;p->phase=e.decision?SP_MOVE_PLAYER:SP_UPDATE_ACTORS;break;
    case SESSION_MOVE_PLAYER:p->phase=SP_MOVE_NEXT;break;
    case SESSION_MOVE_NEXT:p->player_cursor=e.index;p->phase=e.decision?SP_MOVE_PLAYER:SP_UPDATE_ACTORS;break;
    case SESSION_UPDATE_ACTORS:p->phase=SP_UPDATE_ENEMIES;break;case SESSION_UPDATE_ENEMIES:p->phase=SP_UPDATE_ITEMS;break;
    case SESSION_UPDATE_ITEMS:p->phase=SP_DRAW_ACTORS;break;case SESSION_DRAW_ACTORS:p->phase=SP_DRAW_ENEMIES_BACK;break;
    case SESSION_DRAW_ENEMIES_BACK:p->phase=SP_DRAW_PLAYER_BEGIN;break;
    case SESSION_DRAW_PLAYER_BEGIN:p->player_cursor=0;p->phase=SP_DRAW_PLAYER;break;
    case SESSION_DRAW_PLAYER:p->phase=SP_DRAW_PLAYER_NEXT;break;
    case SESSION_DRAW_PLAYER_NEXT:p->player_cursor=e.index;p->phase=e.decision?SP_DRAW_PLAYER:SP_DRAW_ENEMIES_FRONT;break;
    case SESSION_DRAW_ENEMIES_FRONT:p->phase=SP_DRAW_ITEMS;break;
    case SESSION_DRAW_ITEMS:p->phase=SP_DRAW_OVERLAYS;break;
    case SESSION_DRAW_OVERLAYS:p->phase=SP_ADVANCE_RAIN;break;
    case SESSION_ADVANCE_RAIN:p->phase=SP_DRAW_RAIN;break;case SESSION_DRAW_RAIN:p->phase=SP_DRAW_WATER;break;
    case SESSION_DRAW_WATER:p->phase=SP_SWAP_PAGE;break;
    case SESSION_SWAP_PAGE:p->completed_frames++;p->phase=SP_FRAME_BEGIN;break;
    case SESSION_STOP_LEVEL_MUSIC:p->phase=SP_OUTCOME;break;
    case SESSION_OUTCOME:p->phase=e.decision?SP_INCREMENT_LEVEL:SP_DECREMENT_LIVES;break;
    case SESSION_DECREMENT_LIVES:p->phase=e.decision?SP_RESET_MULTIPLIER:SP_RETURN;break;
    case SESSION_RESET_MULTIPLIER:p->phase=SP_INITIALIZE_LEVEL;break;
    case SESSION_INCREMENT_LEVEL:p->phase=SP_TEST_LEVEL_LIMIT;break;
    case SESSION_TEST_LEVEL_LIMIT:p->phase=e.decision?SP_INITIALIZE_LEVEL:SP_RETURN;break;
    case SESSION_RETURN:p->phase=SP_DONE;break;
    default:p->failed=1;return 0;
    }
    return 1;
}
int session_complete(const SessionProcess *p){return p->phase==SP_DONE && !p->failed && !p->pending;}
void session_password_begin(SessionPassword *p){p->length=p->misses=p->level=0;}
void session_password_candidate(SessionPassword *p){p->length=p->misses=0;}
SessionPasswordResult session_password_byte(uint8_t value){return !value?PASSWORD_END:value==255?PASSWORD_DEFAULT:PASSWORD_MORE;}
int session_password_compare(SessionPassword *p,uint8_t candidate,uint8_t editor){
    p->length=(uint16_t)(p->length+1u);
    int mismatch=candidate!=editor;if(mismatch)p->misses=(uint16_t)(p->misses-1u);return mismatch;
}
int session_password_has_misses(const SessionPassword *p){return p->misses!=0;}
int session_password_needs_padding(const SessionPassword *p){return p->length<20;}
int session_password_padding(SessionPassword *p,uint8_t editor){if(editor!=32)return 0;p->length=(uint16_t)(p->length+1u);return 1;}
void session_password_reject(SessionPassword *p){p->level=(uint16_t)(p->level+1u);}
uint16_t session_password_selected(const SessionPassword *p,uint8_t default_marker){return default_marker?0:p->level;}
SessionRenderResult session_erase_layer(SessionRenderView v){
    SessionRenderResult r={0};r.store_erase=1;r.erase_sprite=v.sprite;
    r.restore=(uint8_t)(v.erase_sprite!=0xffff);r.sprite=v.erase_sprite;r.x=v.previous_x;r.y=v.previous_y;return r;
}
SessionRenderResult session_draw_layer(SessionRenderView v,uint8_t enabled){
    SessionRenderResult r={0};
    if(enabled && v.sprite!=0xffff){r.store_position=1;r.previous_x=v.pixel_x;r.previous_y=v.pixel_y;
        r.pixel_x=session_pixel(v.position.x32);r.pixel_y=session_pixel(v.position.y32);
        r.sprite=v.sprite;r.x=r.pixel_x;r.y=r.pixel_y;r.draw=(uint8_t)((int16_t)r.y<192);}
    return r;
}
int session_enemy_layer(uint8_t special,uint8_t front){return special!=front;}

/* The level lists are consumed one word at a time. In particular the second
 * Triopterus speed read is a new read, not a copy of the first one. */
typedef struct LoadStep {SessionLoadAction action;SessionLoadField field;SessionLoadArithmetic arithmetic;uint16_t value;} LoadStep;








static const LoadStep platforms[]={{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_PLATFORM_LEFT,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_PLATFORM_RIGHT,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},
 {LOAD_SCALE_Y,0,LOAD_VALUE,0},{LOAD_STORE,LF_PLATFORM_HEIGHT,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_PLATFORM_ARRIVAL,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},
 {LOAD_STORE,LF_PLATFORM_WAIT,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_PLATFORM_SPAWN,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_PLATFORM_ICON,LOAD_VALUE,0},{LOAD_SKIP,0,LOAD_VALUE,2},
 {LOAD_STORE,LF_PLATFORM_OCCUPANT,LOAD_KEEP_ACCUMULATOR,0xffff},{LOAD_END,0,LOAD_VALUE,0}};
static const LoadStep actors[]={{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ACTOR_DESCRIPTOR,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ACTOR_PLATFORM,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},
 {LOAD_STORE,LF_ACTOR_JOURNEY,LOAD_VALUE,0},{LOAD_STORE,LF_ACTOR_SPRITE,LOAD_SET_HIDDEN,0xffff},
 {LOAD_STORE,LF_ACTOR_ERASE,LOAD_KEEP_ACCUMULATOR,0xffff},{LOAD_STORE,LF_ACTOR_OVERLAY,LOAD_KEEP_ACCUMULATOR,0xffff},
 {LOAD_STORE,LF_ACTOR_ERASE_OVERLAY,LOAD_KEEP_ACCUMULATOR,0xffff},{LOAD_READ_DESCRIPTOR,0,LOAD_VALUE,0},{LOAD_STORE,LF_ACTOR_CALLBACK,LOAD_VALUE,0},
 {LOAD_READ_SPAWN,0,LOAD_VALUE,0},{LOAD_STORE,LF_ACTOR_X,LOAD_STONE_X,0},{LOAD_READ_HEIGHT,0,LOAD_VALUE,0},{LOAD_STORE,LF_ACTOR_Y,LOAD_STONE_Y,0},{LOAD_END,0,LOAD_VALUE,0}};
static const LoadStep trees[]={{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_DESCRIPTOR,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_PLATFORM,LOAD_VALUE,0},
 {LOAD_READ_SPAWN,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_X,LOAD_TREE_X,0},{LOAD_READ_HEIGHT,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_Y,LOAD_TREE_Y,0},
 {LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_LIST,LOAD_VALUE,0},{LOAD_CALLBACK,LF_ENEMY_CALLBACK,LOAD_KEEP_ACCUMULATOR,0},{LOAD_END,0,LOAD_VALUE,0}};
static const LoadStep birds[]={{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_DESCRIPTOR,LOAD_VALUE,0},{LOAD_SKIP,0,LOAD_VALUE,2},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_SCALE_SPEED,0,LOAD_VALUE,0},
 {LOAD_STORE,LF_ENEMY_DELAY,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_SPEED,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_DIRECTION,LOAD_KEEP_ACCUMULATOR,1},{LOAD_CALLBACK,LF_ENEMY_CALLBACK,LOAD_KEEP_ACCUMULATOR,0},{LOAD_END,0,LOAD_VALUE,0}};
static const LoadStep dinos[]={{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_DESCRIPTOR,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_X,LOAD_DINO_X,0},
 {LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_SCALE_Y,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_Y,LOAD_DINO_Y,0},{LOAD_SKIP,0,LOAD_VALUE,4},{LOAD_CALLBACK,LF_ENEMY_CALLBACK,LOAD_KEEP_ACCUMULATOR,0},{LOAD_END,0,LOAD_VALUE,0}};
static const LoadStep trios[]={{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_DESCRIPTOR,LOAD_VALUE,0},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_PLATFORM,LOAD_VALUE,0},
 {LOAD_READ_SPAWN,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_X,LOAD_TRIO_X,0},{LOAD_READ_HEIGHT,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_Y,LOAD_TRIO_Y,0},
 {LOAD_SKIP,0,LOAD_VALUE,2},{LOAD_READ_LIST,0,LOAD_VALUE,0},{LOAD_READ_REPEAT,0,LOAD_VALUE,0},{LOAD_STORE,LF_ENEMY_SPEED,LOAD_TRIO_SPEED,0},
 {LOAD_STORE,LF_ENEMY_DIRECTION,LOAD_KEEP_ACCUMULATOR,0},{LOAD_CALLBACK,LF_ENEMY_CALLBACK,LOAD_KEEP_ACCUMULATOR,0},{LOAD_END,0,LOAD_VALUE,0}};








void session_load_begin(SessionLoadRecord *r,SessionLoadFamily family,uint16_t slot){
 *r=(SessionLoadRecord){0};r->family=family;r->slot=slot;r->record_class=LOAD_ORDINARY;
}
uint16_t session_load_value(SessionLoadArithmetic a,uint16_t v,uint16_t repeated){
 switch(a){
 case LOAD_STONE_X:return (uint16_t)((v-8u)*32u);
 case LOAD_STONE_Y:return (uint16_t)((v-11u)*32u);
 case LOAD_TREE_X:case LOAD_TRIO_X:return (uint16_t)((v-16u)*32u);
 case LOAD_TREE_Y:return (uint16_t)((v-24u)*32u);
 case LOAD_TRIO_Y:return (uint16_t)((v-22u)*32u);
 case LOAD_DINO_X:return (uint16_t)(v*32u);
 case LOAD_DINO_Y:return (uint16_t)(v-704u);
 case LOAD_TRIO_SPEED:{uint16_t quarter=(uint16_t)((v>>2)|((v&0x8000u)?0xc000u:0));return (uint16_t)(quarter-repeated);}
 default:return v;
 }
}
SessionLoadRequest session_load_next(SessionLoadRecord *r){
 SessionLoadRequest e={LOAD_INVALID,0,LOAD_VALUE,r->slot,0,0};
 if(r->pending || r->failed || r->done){r->failed=1;return e;}
 const LoadStep *table;
 if(r->family==LOAD_PLATFORMS)table=platforms;
 else if(r->family==LOAD_ACTORS)table=actors;
 else if(r->family==LOAD_ENEMIES){
  switch(r->record_class){case LOAD_TREE:table=trees;break;case LOAD_BIRD:table=birds;break;
   case LOAD_DINO:table=dinos;break;default:table=trios;break;}
 }else{r->failed=1;return e;}
 if(r->list_end || (r->family==LOAD_ACTORS && r->record_class!=LOAD_STONE && r->cursor==12))e.action=LOAD_END;
 else {
  LoadStep s=table[r->cursor];e.action=s.action;e.field=s.field;e.arithmetic=s.arithmetic;
  e.value=s.arithmetic==LOAD_KEEP_ACCUMULATOR || s.arithmetic==LOAD_SET_HIDDEN?s.value:session_load_value(s.arithmetic,r->sample,r->repeat);
  if(e.action==LOAD_SKIP)e.value=s.value;
  if(e.action==LOAD_READ_DESCRIPTOR)e.index=r->record_class==LOAD_STONE?16:8;
  if(e.action==LOAD_READ_HEIGHT || e.action==LOAD_READ_SPAWN)e.index=(uint16_t)(r->platform*2u);
  if(e.action==LOAD_SCALE_Y && r->family==LOAD_ENEMIES)e.value=(uint16_t)(r->sample*32u);
  if(e.action==LOAD_CALLBACK)e.value=(uint16_t)r->record_class;
 }
 r->request=e;r->pending=1;return e;
}
int session_load_accept(SessionLoadRecord *r,SessionLoadAction action,uint16_t v,SessionLoadClass kind){
 if(r->failed || !r->pending || r->request.action!=action){r->failed=1;return 0;}
 SessionLoadRequest e=r->request;r->pending=0;
 if(action==LOAD_END){r->done=1;return 1;}
 if(action==LOAD_READ_REPEAT)r->repeat=v;
 else if(action==LOAD_READ_LIST || action==LOAD_READ_DESCRIPTOR || action==LOAD_READ_SPAWN || action==LOAD_READ_HEIGHT || action==LOAD_SCALE_Y || action==LOAD_SCALE_SPEED){
  r->sample=v;if(r->cursor==0){r->descriptor=v;r->record_class=kind;}
 }
 if(action==LOAD_STORE){
  if(e.field==LF_PLATFORM_LEFT)r->list_end=(uint8_t)((e.value&0x8000u)!=0);
  if(e.field==LF_ACTOR_DESCRIPTOR || e.field==LF_ENEMY_DESCRIPTOR)r->list_end=(uint8_t)(e.value==0xffff);
  if(e.field==LF_ACTOR_PLATFORM || e.field==LF_ENEMY_PLATFORM)r->platform=e.value;
 }
 r->cursor++;return 1;
}
uint16_t session_record_previous(uint16_t cursor){return (uint16_t)(cursor-2u);}
int session_record_more(uint16_t cursor){return !(cursor&0x8000u);}
uint16_t session_loader_mode_key(uint16_t players){return (uint16_t)((players-1u)*2u);}
uint16_t session_loader_level_key(uint16_t level){return (uint16_t)(level*2u);}
uint16_t session_water_cap(uint16_t scaled){return scaled>0x17e0u?0x17e0u:scaled;}
SessionPlayerSeed session_player_x(uint16_t raw){SessionPlayerSeed s;s.fixed=(uint16_t)(raw-512u);s.pixel=session_pixel(s.fixed);return s;}
SessionPlayerSeed session_player_y(uint16_t scaled){SessionPlayerSeed s;s.fixed=(uint16_t)(scaled-320u);s.pixel=session_pixel(s.fixed);return s;}
uint8_t session_display_byte(uint8_t value){uint8_t v=(uint8_t)(value+11u);return v>=100?(uint8_t)(v-100u):v;}
uint32_t session_display_score(uint32_t score){uint32_t v=score+111111u;return v>1000000u?v-1000000u:v;}
uint16_t session_display_layout(uint16_t players,unsigned field){
 static const uint16_t one[]={33,118,177,208,224,244,290,0,0};
 static const uint16_t two[]={33,114,169,199,215,232,305,258,274};
 return field<9?(players==2?two[field]:one[field]):0;
}
uint16_t session_copy_next(uint16_t cursor,uint8_t backwards){return (uint16_t)(cursor+(backwards?0xfffeu:2u));}
int session_count_more(uint16_t remaining){return remaining!=0;}
uint16_t session_prewarm_previous(uint16_t cursor){return (uint16_t)(cursor-1u);}
int session_rain_enabled(uint8_t direction){return direction!=0;}
uint16_t session_reset_value(unsigned field){return field==0?3:field==1?1:0;}
void session_display_begin(SessionDisplayProcess *p){*p=(SessionDisplayProcess){0};}
unsigned session_display_next(SessionDisplayProcess *p){
 if(p->pending || p->failed || p->cursor>13){p->failed=1;return 255;}
 if(p->cursor==13)return 13;
 p->pending=1;return p->cursor;
}
int session_display_consume(SessionDisplayProcess *p,unsigned action){
 if(p->failed || !p->pending || p->cursor!=action){p->failed=1;return 0;}
 p->pending=0;p->cursor++;return 1;
}
int session_display_complete(const SessionDisplayProcess *p){return p->cursor==13 && !p->pending && !p->failed;}
