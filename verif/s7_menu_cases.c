#include "native/compose_menu.h"
#include "native/compose_audio.h"
#include "native/game_startup.h"
#include "port/test/backend.h"
#include "port/resources.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c) do{if(!(c)){fprintf(stderr,"check failed line %u: %s\n",__LINE__,#c);exit(3);}}while(0)
static GameWorld *w;static GSTestBackend *b;static GSResourcePack pack;static GameServices services;
static unsigned scan,following,delivered;
static GSStatus pump(void *ctx,GSInputPollCut cut){
 if(cut==GS_INPUT_SCAN&&delivered<2&&(delivered==0||following)){GSTestRun run={delivered++?following:scan,1};return gs_test_stream(&((GSTestBackend*)ctx)->scans,&run,1,1);}return GS_OK;
}
static void fresh(void){
 gs_test_init(b);b->resources=gs_resources_operations();b->resource_context=&pack;services=gs_test_services(b);CHECK(game_world_construct(w,&services)==GS_OK);
 w->pages=(VideoPages){.height=192,.plane_copy_bytes=0x4800,.fixed=0,.displayed=0xa88,.draw=0x5a08,.background=0xa988};
 w->keyboard_saved=(GSBinding){1};w->input.loop_limit=3;w->input.enabled_axis_storage&=65280u;
 GSTestRun retraces[]={{0,1},{8,1}},absent[]={{255,10000}};
 CHECK(gs_test_stream(&b->retrace_samples,retraces,2,UINT32_MAX)==GS_OK);CHECK(gs_test_stream(&b->joystick,absent,1,UINT32_MAX)==GS_OK);
 delivered=following=0;services.input.pump=pump;
}
static GSStatus fail_opportunity(void *ctx,GSInputPollCut cut){(void)ctx;CHECK(cut==GS_INPUT_WAIT);return GS_IO_ERROR;}
static GSStatus fail_present(void *ctx){(void)ctx;return GS_IO_ERROR;}
static unsigned terminal_order,sound_mutations;
static void sound_reply(void *ctx,GSTestEffect effect){(void)ctx;if(effect.kind==GST_OPL){w->lifecycle.saved_bios_video_mode=0x17;sound_mutations++;}}

static GSStatus video(void *ctx,uint8_t mode){(void)ctx;CHECK(terminal_order++==0&&mode==0x17);b->flush_reply=0x1234;return GS_OK;}
static GSStatus binding(void *ctx,GSVectorOp op,GSBinding saved,GSBinding *reply){(void)ctx;CHECK(terminal_order++==1&&op==GS_VECTOR_RESTORE&&saved.token==1);*reply=saved;b->flush_reply=0xabcd;return GS_OK;}
static GSStatus terminate(void *ctx,uint8_t value){(void)ctx;CHECK(terminal_order++==2&&value==0xcd);return GS_OK;}
static GSStatus fail_video(void *ctx,uint8_t mode){(void)ctx;(void)mode;terminal_order++;return GS_IO_ERROR;}
int main(int argc,char **argv){
 CHECK(argc==2);char error[256];CHECK(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)==GS_OK);
 w=calloc(1,sizeof *w);b=calloc(1,sizeof *b);CHECK(w&&b);GameMenu menu;GameMenuResult result;
 /* Enter at the accepted screen decision to isolate F1's exact typed seam. */
 fresh();scan=59;game_menu_begin(&menu);menu.process.started=1;menu.process.last=MENUS_MAIN_PREPARE_PALETTE;
 w->run.configuration.players=2;w->run.configuration.player_bytes=4;w->run.configuration.difficulty=2;
 result=game_menu_run(w,&services,&menu);CHECK(result.kind==GAME_MENU_SESSION_ENTRY&&result.status==GS_OK&&menu.process.last==MENUS_MAIN_SESSION);
 CHECK(w->run.configuration.players==2&&w->run.configuration.player_bytes==4&&w->run.configuration.difficulty==2&&w->run.water_y==175);
 game_menu_session_return(&menu,1);CHECK(menu.reply.completed);
 /* Failed synchronous screen service leaves the consumed action and prefix. */
 fresh();game_menu_begin(&menu);menu.process.started=1;menu.process.last=MENUS_MAIN_PREPARE_PALETTE;services.video.present=fail_present;
 result=game_menu_run(w,&services,&menu);CHECK(result.kind==GAME_MENU_FAILED&&result.status==GS_IO_ERROR&&result.action==MENUS_MAIN_PREPARE_SCREEN&&w->frames==1&&w->run.water_y==175);
 fresh();game_menu_begin(&menu);menu.process.started=1;menu.process.last=MENUS_MAIN_WAIT;menu.reply.remaining=1;services.input.pump=fail_opportunity;
 result=game_menu_run(w,&services,&menu);CHECK(result.status==GS_IO_ERROR&&result.action==MENUS_MAIN_POLL&&w->frames==0&&delivered==0);
 /* Timeout consumes restart/fade and then the reveal's preparation prefix. */
 fresh();game_menu_begin(&menu);menu.process.started=1;menu.process.last=MENUS_MAIN_WAIT;menu.reply.remaining=0;services.video.present=fail_present;
 result=game_menu_run(w,&services,&menu);CHECK(result.status==GS_IO_ERROR&&result.action==MENUS_MAIN_REVEAL&&w->frames==1);
 /* Q consumes its fade, then returns EXIT to the terminal owner. */
 fresh();scan=16;game_menu_begin(&menu);menu.process.started=1;menu.process.last=MENUS_MAIN_PREPARE_PALETTE;
 result=game_menu_run(w,&services,&menu);CHECK(result.kind==GAME_MENU_EXIT&&result.action==MENUS_MAIN_EXIT_FADE);
 /* Controls retain calibration and skip missing joystick modes. */
 fresh();scan=1;w->input.joysticks[0].double_x=123;CHECK(game_menu_controls(w,&services)==GS_OK&&w->input.joysticks[0].double_x==123&&w->run.water_y==200);
 for(unsigned mode=0;mode<3;mode++){
  fresh();scan=59;following=1;w->run.configuration.control_mode[0]=mode==0?65535:mode==1?0:1;
  w->input.joysticks[0].present=w->input.joysticks[1].present=65535;
  CHECK(game_menu_controls(w,&services)==GS_OK&&w->run.configuration.control_mode[0]==(mode==0?0:mode==1?1:65535));
 }
 fresh();scan=59;following=1;w->run.configuration.control_mode[0]=65535;w->input.joysticks[0].present=0;w->input.joysticks[1].present=65535;
 CHECK(game_menu_controls(w,&services)==GS_OK&&w->run.configuration.control_mode[0]==1);
 /* Terminal reads the saved mode after sound, and exit from the input reply. */
 fresh();w->lifecycle.saved_bios_video_mode=0x17;services.lifecycle.video_set=video;services.input.vector=binding;services.lifecycle.terminate=terminate;terminal_order=0;
 CHECK(game_menu_terminal(w,&services)==GS_OK&&terminal_order==3&&w->lifecycle.terminal.cursor==4);
 fresh();gs_test_startup(b,1);services=gs_test_services(b);CHECK(game_audio_init(w,&services,1)==GS_OK);
 CHECK(game_audio_music_start(w,&services,game_audio_menu_resource(),0,165).status==GS_OK);
 w->lifecycle.saved_bios_video_mode=3;services.lifecycle.video_set=video;services.input.vector=binding;services.lifecycle.terminate=terminate;terminal_order=sound_mutations=0;b->recorder=sound_reply;
 CHECK(game_menu_terminal(w,&services)==GS_OK&&terminal_order==3&&sound_mutations&&w->audio.fade.duration==17);
 fresh();services.lifecycle.video_set=fail_video;terminal_order=0;CHECK(game_menu_terminal(w,&services)==GS_IO_ERROR&&terminal_order==1&&w->lifecycle.terminal.cursor==2&&!b->exited);
 free(w);free(b);gs_resources_close(&pack);puts("PASS menu session seam, consumed failures, timeout, Q, controls and live terminal reply");return 0;
}
