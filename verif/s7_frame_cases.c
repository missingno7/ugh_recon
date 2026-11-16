#include "native/compose_frame.h"
#include "native/compose_enemies.h"
#include "port/resources.h"
#include "port/test/backend.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"frame case %u: %s\n",__LINE__,#x);return 3;}}while(0)
static GSStatus fail_control(void *c,GSVideoRoute r,uint8_t v){(void)c;(void)r;(void)v;return GS_IO_ERROR;}
static GSStatus fail_pump(void *c,GSInputPollCut cut){(void)c;(void)cut;return GS_IO_ERROR;}
static void phase_at(GameSessionCursor *c,SessionPhase phase){game_session_begin(c,GAME_SESSION_PASSWORD);c->process.phase=phase;}
int main(int argc,char **argv){
    if(argc!=2)return 2;GSResourcePack pack;char error[256];
    CHECK(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)==GS_OK);
    GameWorld *w=calloc(1,sizeof *w);GSTestBackend *b=calloc(1,sizeof *b);CHECK(w&&b);
    gs_test_init(b);b->resources=gs_resources_operations();b->resource_context=&pack;
    GameServices s=gs_test_services(b);CHECK(game_world_construct(w,&s)==GS_OK);GameSessionCursor c;
    CHECK(game_session_begin(NULL,GAME_SESSION_PASSWORD)==GS_INVALID);
    CHECK(game_session_begin(&c,(GameSessionEntry)99)==GS_UNSUPPORTED&&c.result.kind==GAME_SESSION_UNSUPPORTED);
    CHECK(game_session_step(w,&s,&c)==GS_INVALID);
    /* Native publication of the accepted byte decrement, including sign exit. */
    const uint8_t lives[]={0,1,2,128,129,255},next[]={255,0,1,127,128,254};
    for(unsigned i=0;i<6;i++){
        phase_at(&c,SP_OUTCOME);w->run.completion=0;w->run.lives=lives[i];w->run.multiplier=9;
        CHECK(game_session_step(w,&s,&c)==GS_OK&&c.process.phase==SP_DECREMENT_LIVES);
        CHECK(game_session_step(w,&s,&c)==GS_OK&&w->run.lives==next[i]);
        if(i==2||i==3){
            CHECK(c.process.phase==SP_RESET_MULTIPLIER);CHECK(game_session_step(w,&s,&c)==GS_OK);
            CHECK(w->run.multiplier==1&&c.process.phase==SP_INITIALIZE_LEVEL);
        }else{
            CHECK(c.process.phase==SP_RETURN);CHECK(game_session_step(w,&s,&c)==GS_OK);
            CHECK(game_session_step(w,&s,&c)==GS_OK&&c.result.kind==GAME_SESSION_RETURNED);
        }
    }
    /* Word addition must publish before the unsigned level-limit request. */
    const uint16_t levels[]={65535,68,80},players[]={1,1,2},advanced[]={0,69,81};
    for(unsigned i=0;i<3;i++){
        phase_at(&c,SP_OUTCOME);w->run.completion=128;w->run.level=levels[i];w->run.lives=3;
        w->run.configuration.players=players[i];w->run.configuration.player_bytes=(uint16_t)(players[i]*2u);
        CHECK(game_session_step(w,&s,&c)==GS_OK&&c.process.phase==SP_INCREMENT_LEVEL);
        CHECK(game_session_step(w,&s,&c)==GS_OK&&w->run.level==advanced[i]&&w->run.lives==3);
        CHECK(game_session_step(w,&s,&c)==GS_OK&&c.process.phase==(i?SP_RETURN:SP_INITIALIZE_LEVEL));
    }
    /* Movement's equality-only continuation differs from erase/draw visits. */
    for(unsigned n=1;n<=2;n++){
        phase_at(&c,SP_MOVE_BEGIN);w->run.configuration.players=(uint16_t)n;w->run.configuration.player_bytes=(uint16_t)(n*2u);w->run.fade_level=194;
        CHECK(game_session_step(w,&s,&c)==GS_OK&&c.process.phase==SP_MOVE_PLAYER&&c.process.player_cursor==0);
        c.process.phase=SP_MOVE_NEXT;
        CHECK(game_session_step(w,&s,&c)==GS_OK&&c.process.player_cursor==2);
        CHECK(c.process.phase==(n==2?SP_MOVE_PLAYER:SP_UPDATE_ACTORS));
        if(n==2){c.process.phase=SP_MOVE_NEXT;CHECK(game_session_step(w,&s,&c)==GS_OK&&c.process.player_cursor==4&&c.process.phase==SP_UPDATE_ACTORS);}
    }
    /* Pause consumes each raw release/make/break opportunity independently. */
    phase_at(&c,SP_PAUSE_RELEASE);w->input.latest=0x19;CHECK(game_session_step(w,&s,&c)==GS_OK&&c.process.phase==SP_PAUSE_RELEASE);
    w->input.latest=0x99;CHECK(game_session_step(w,&s,&c)==GS_OK&&c.process.phase==SP_PAUSE_MAKE);
    w->input.latest=0x39;CHECK(game_session_step(w,&s,&c)==GS_OK&&c.process.phase==SP_PAUSE_BREAK);
    w->input.latest=0xb9;CHECK(game_session_step(w,&s,&c)==GS_OK&&c.process.phase==SP_ESCAPE);
    s.input.pump=fail_pump;phase_at(&c,SP_POLL_CONTROLS);w->session.players.player[0].right=123;
    CHECK(game_session_step(w,&s,&c)==GS_IO_ERROR&&c.result.kind==GAME_SESSION_SERVICE_ERROR&&c.process.pending&&w->session.players.player[0].right==123);
    s=gs_test_services(b);
    /* An unadmitted enemy role fails; a sentinel hides stale records. */
    w->session.enemy_end[0]=0;w->enemies.slot[0].counter=321;
    w->session.enemy_callback[0]=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ENEMY,.enemy=H_ZERO};
    CHECK(game_enemies_update(w,&s)==GS_UNSUPPORTED&&w->enemies.slot[0].counter==321);
    w->session.enemy_end[0]=1;
    CHECK(game_enemies_update(w,&s)==GS_OK&&game_enemies_erase(w,&s)==GS_OK&&game_enemies_draw_back(w,&s)==GS_OK&&game_enemies_draw_front(w,&s)==GS_OK&&w->enemies.slot[0].counter==321);
    /* A failed renderer consumes the preceding player animation publication. */
    s.video.control_write=fail_control;NativePlayer *p=w->session.players.player;p->animation=0;p->thrust=90;p->sprite=218;p->pixel_x=20;p->pixel_y=20;uint16_t palette=0;
    CHECK(game_frame_execute(w,&s,(SessionRequest){.action=SESSION_DRAW_PLAYER},&palette)==GS_IO_ERROR&&p->animation==110&&p->sprite==219);
    free(w);free(b);gs_resources_close(&pack);puts("PASS native frame/session byte lives, level wrap/limit, two-player equality, pause, unadmitted enemy and consumed failure cases");return 0;
}
