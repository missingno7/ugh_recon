#include "native/compose_session.h"
#include "port/resources.h"
#include "port/test/backend.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"session check failed at %u: %s\n",__LINE__,#x);return 3;}}while(0)
static GSResourceOps resources;
static void *resource_context;
static unsigned reads,fail_on;
static GSStatus fail_view(void *context,GSResourceId id,GSBytes *out,GSResourceClass *kind){
    (void)context;if(++reads==fail_on)return GS_IO_ERROR;
    return resources.view(resource_context,id,out,kind);
}
int main(int argc,char **argv){
    if(argc!=2)return 2;GSResourcePack pack;char error[256];
    CHECK(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)==GS_OK);
    GameWorld *w=calloc(1,sizeof *w);GSTestBackend *b=calloc(1,sizeof *b);CHECK(w&&b);
    gs_test_init(b);b->resources=gs_resources_operations();b->resource_context=&pack;
    GameServices s=gs_test_services(b);CHECK(game_world_construct(w,&s)==GS_OK);
    GameSessionResult invalid=game_session_run(w,&s,(GameSessionEntry)77);
    CHECK(invalid.kind==GAME_SESSION_UNSUPPORTED&&invalid.status==GS_UNSUPPORTED&&invalid.action==SESSION_INVALID);
    uint16_t level=999;w->run.configuration.player_bytes=2;w->run.configuration.players=1;
    memset(w->front.password,32,20);memcpy(w->front.password,"CAVITY",6);
    CHECK(game_session_password(w,&s,&level)==GS_OK&&level==0);
    w->front.password[19]='X';CHECK(game_session_password(w,&s,&level)==GS_OK&&level==0);
    /* Invalid padding falls back, never accepts a longer level's prefix. */
    GSBytes pw;CHECK(session_data_password(&s,2,1,&pw)==GS_OK);
    memset(w->front.password,32,20);memcpy(w->front.password,pw.data,pw.size-1);w->front.password[19]='X';
    CHECK(game_session_password(w,&s,&level)==GS_OK&&level==0);
    w->run.configuration.player_bytes=6;level=999;
    CHECK(game_session_password(w,&s,&level)==GS_UNSUPPORTED&&level==999);
    w->run.configuration.player_bytes=2;w->run.level=69;
    CHECK(game_session_load(w,&s)==GS_UNSUPPORTED&&!w->session.level);
    resources=s.resources;resource_context=s.resources_context;s.resources.view=fail_view;
    w->run.level=0;reads=0;fail_on=1;w->run.timer=12;
    CHECK(game_session_load(w,&s)==GS_IO_ERROR&&reads==1&&!w->session.level&&w->run.timer==12);
    /* Initialize clears several owners before attempting the first resource.
     * A failure retains that prefix, without drawing or synthesized cleanup. */
    w->run.lives=255;w->run.multiplier=255;w->run.score=1000000;
    w->session.players.player[1].action=123;w->run.tiles[319]=123;w->demo_exit=123;
    w->run.completion=255;w->presentation.weather.pending=255;
    w->presentation.hud.layout_x[8]=123;w->presentation.hud.icons[1]=123;
    reads=0;fail_on=1;unsigned stage=99;
    CHECK(game_session_initialize(w,&s,&stage)==GS_IO_ERROR&&stage==0&&reads==1);
    CHECK(w->run.timer==0x5a3b&&w->run.fade_level==0&&w->run.fade_step==2);
    CHECK(w->session.players.player[1].action==0&&w->run.tiles[319]==0&&w->demo_exit==0);
    CHECK(w->run.completion==0&&w->presentation.weather.pending==0);
    CHECK(w->presentation.hud.layout_x[8]==0&&w->presentation.hud.icons[1]==123);
    CHECK(w->presentation.hud.lives==10&&w->presentation.hud.multiplier==10);
    CHECK(w->presentation.hud.score_words[0]==(uint16_t)111111&&w->presentation.hud.score_words[1]==(111111u>>16));
    CHECK(b->presents==0);free(w);free(b);gs_resources_close(&pack);
    puts("PASS session typed entry, password padding/modes, load and multi-owner-clear failure prefixes");return 0;
}
