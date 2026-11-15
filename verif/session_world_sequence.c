/* Native synchronous driver: independent action order, live replies and failures. */
#include "session_world.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"sequence line %u case %u cut %u\n",__LINE__,case_id,at);exit(3);}}while(0)
static unsigned case_id,at;
static const SessionAction startup[]={SESSION_PASSWORD,SESSION_SELECT_LEVEL,SESSION_PREGAME,SESSION_STOP_INITIAL_MUSIC,SESSION_RESET_GAME,SESSION_BLACK_PALETTE,SESSION_INITIALIZE_LEVEL,SESSION_START_MUSIC};
static const SessionAction frame[]={SESSION_WAIT_RETRACE,SESSION_HUD,SESSION_ERASE_PLAYER_BEGIN,SESSION_ERASE_PLAYER,SESSION_ERASE_PLAYER_NEXT,SESSION_ERASE_PLAYER,SESSION_ERASE_PLAYER_NEXT,SESSION_ERASE_ACTORS,SESSION_ERASE_ENEMIES,SESSION_ERASE_ITEMS,SESSION_RESTORE_RAIN,SESSION_ADVANCE_WATER,SESSION_IO_POINT,SESSION_POLL_CONTROLS,SESSION_PAUSE_RELEASE,SESSION_PAUSE_RELEASE,SESSION_PAUSE_MAKE,SESSION_PAUSE_MAKE,SESSION_PAUSE_BREAK,SESSION_PAUSE_BREAK,SESSION_ESCAPE,SESSION_MOVE_BEGIN,SESSION_MOVE_PLAYER,SESSION_MOVE_NEXT,SESSION_MOVE_PLAYER,SESSION_MOVE_NEXT,SESSION_UPDATE_ACTORS,SESSION_UPDATE_ENEMIES,SESSION_UPDATE_ITEMS,SESSION_DRAW_ACTORS,SESSION_DRAW_ENEMIES_BACK,SESSION_DRAW_PLAYER_BEGIN,SESSION_DRAW_PLAYER,SESSION_DRAW_PLAYER_NEXT,SESSION_DRAW_PLAYER,SESSION_DRAW_PLAYER_NEXT,SESSION_DRAW_ENEMIES_FRONT,SESSION_DRAW_ITEMS,SESSION_DRAW_OVERLAYS,SESSION_ADVANCE_RAIN,SESSION_DRAW_RAIN,SESSION_DRAW_WATER,SESSION_SWAP_PAGE};
static const SessionAction ending[]={SESSION_STOP_LEVEL_MUSIC,SESSION_OUTCOME,SESSION_DECREMENT_LIVES,SESSION_RETURN};
typedef struct Fixture {SessionWorld live;SessionAction expected[80];unsigned length,fail_at,pause_release,pause_make,pause_break;int status;uint32_t frames;unsigned observed,diagnostics;int completion,palette,diag_status;} Fixture;
static void setup(Fixture*f,int wet,int completion,int palette){
 memset(f,0,sizeof *f);at=0;f->live=(SessionWorld){0};f->live.player_count=1;f->live.player_bytes=2;f->live.lives=1;f->live.level=65535;f->live.level_limit=0;f->live.rain=(uint8_t)wet;f->live.password_reply=65535;f->fail_at=~0u;f->completion=completion;f->palette=palette;
 for(unsigned i=0;i<sizeof startup/sizeof *startup;i++)f->expected[f->length++]=startup[i];
 for(unsigned i=0;i<sizeof frame/sizeof *frame;i++){
  SessionAction action=frame[i];if(!wet && (action==SESSION_RESTORE_RAIN || action==SESSION_ADVANCE_RAIN || action==SESSION_DRAW_RAIN))continue;
  f->expected[f->length++]=i==0 && palette?SESSION_FADE_UPLOAD:action;
  if(i==0 && palette)f->expected[f->length++]=SESSION_FADE_ADVANCE;
 }
 for(unsigned i=0;i<sizeof ending/sizeof *ending;i++){
  SessionAction action=ending[i];if(completion && action==SESSION_DECREMENT_LIVES){f->expected[f->length++]=SESSION_INCREMENT_LEVEL;f->expected[f->length++]=SESSION_TEST_LEVEL_LIMIT;}else f->expected[f->length++]=action;
 }
}
static SessionWorld observe(void*context,SessionPhase phase){Fixture*f=context;f->observed++;(void)phase;return f->live;}
static int execute(void*context,SessionRequest e){Fixture*f=context;CHECK(at<f->length);CHECK(e.action==f->expected[at]);unsigned cut=at++;
 if(cut==f->fail_at)return f->status;
 switch(e.action){
 case SESSION_PASSWORD:f->live.password_reply=65535;break;
 case SESSION_SELECT_LEVEL:CHECK(e.value==65535);f->live.level=e.value;break;
 case SESSION_INITIALIZE_LEVEL:f->live.fade_level=f->palette?256:257;f->live.fade_rate=2;break;
 case SESSION_FADE_UPLOAD:f->live.palette_reply=91;f->live.fade_rate=65534;break;
 case SESSION_FADE_ADVANCE:CHECK(e.value==89);f->live.fade_level=e.value;break;
 /* A callback changes the real run configuration. Parent observations must die. */
 case SESSION_HUD:f->live.player_count=2;f->live.player_bytes=4;break;
 case SESSION_POLL_CONTROLS:f->live.scan=0x19;break;
 case SESSION_PAUSE_RELEASE:f->live.scan=++f->pause_release==2?0x99:0x19;break;
 case SESSION_PAUSE_MAKE:f->live.scan=++f->pause_make==2?0x1e:0x99;break;
 case SESSION_PAUSE_BREAK:f->live.scan=++f->pause_break==2?0x9e:0x1e;break;
 case SESSION_MOVE_PLAYER:CHECK(e.index==0 || e.index==2);break;
 case SESSION_MOVE_NEXT:CHECK(e.decision==(e.index==2));break;
 case SESSION_SWAP_PAGE:f->live.fade_level=65535;f->live.completion=f->completion?128:0;f->frames++;break;
 case SESSION_DECREMENT_LIVES:CHECK(e.value==0 && !e.decision);f->live.lives=(uint8_t)e.value;break;
 case SESSION_INCREMENT_LEVEL:CHECK(e.value==0);f->live.level=e.value;break;
 case SESSION_TEST_LEVEL_LIMIT:CHECK(!e.decision);break;
 default:break;
 }
 return 0;
}
static int diagnostic(void*context,const SessionProcess*p){Fixture*f=context;f->diagnostics++;CHECK(p->completed_frames==f->frames);return f->frames?f->diag_status:0;}
int main(void){unsigned prefixes=0;SessionServices services={observe,execute,diagnostic};Fixture f;
 for(int wet=0;wet<2;wet++)for(int complete=0;complete<2;complete++)for(int palette=0;palette<2;palette++){
  case_id++;setup(&f,wet,complete,palette);CHECK(session_world_run(&services,&f)==0);CHECK(at==f.length && f.frames==1 && f.pause_release==2 && f.pause_make==2 && f.pause_break==2);unsigned length=f.length;
  for(unsigned cut=0;cut<length;cut++)for(int status=1;status<=5;status++){
   case_id++;setup(&f,wet,complete,palette);f.fail_at=cut;f.status=status;
   CHECK(session_world_run(&services,&f)==status);CHECK(at==cut+1);CHECK(f.diagnostics==cut);CHECK(f.observed==cut*2+1);prefixes++;
  }
 }
 case_id++;setup(&f,1,0,0);f.diag_status=77;
 CHECK(session_world_run(&services,&f)==77);CHECK(at==f.length-4 && f.frames==1);
 /* Full-domain retained byte decrement and level wrap, without a host policy. */
 for(unsigned n=0;n<65536;n++){
  SessionProcess p;session_begin(&p);p.phase=SP_INCREMENT_LEVEL;SessionWorld w={0};w.level=(uint16_t)n;
  CHECK(session_next(&p,w).value==(uint16_t)(n+1u));
  if(n<256){session_begin(&p);p.phase=SP_DECREMENT_LIVES;w.lives=(uint8_t)n;SessionRequest e=session_next(&p,w);CHECK(e.value==(uint8_t)(n-1u));}
 }
 printf("{\"complete_flows\":8,\"failure_prefixes\":%u,\"level_values\":65536,\"lives_values\":256,\"pause_polls_per_frame\":6}\n",prefixes);return 0;
}
