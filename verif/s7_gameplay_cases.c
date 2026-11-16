#include "native/compose_objects.h"
#include "native/compose_session.h"
#include "native/compose_audio.h"
#include "native/compose_demo.h"
#include "native/game_object_data.h"
#include "port/resources.h"
#include "port/test/backend.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"objects check %u: %s\n",__LINE__,#x);exit(3);}}while(0)
static GameWorld *w;static GSTestBackend *b;static GameServices s;static GSResourcePack pack;
static GSStatus (*saved_opl)(void *,GSRegisterWrite);
static unsigned opl_calls;static int failure;
static GSStatus mutate_opl(void *context,GSRegisterWrite event){
    ++opl_calls;
    /* A synchronous service may mutate borrowers before the delivery tail.
     * The original rereads destination, descriptor anchors and platform Y. */
    if(opl_calls==1){
        w->actors.slot[0].destination_platform=9;w->actors.slot[0].destination_byte_index=4;
        w->session.platforms.slot[2].height=173;
        CHECK(game_object_actor_type(ACTOR_PASSENGER_THREE_LAND,&w->actors.slot[0].descriptor)==GS_OK);
    }
    return failure?GS_IO_ERROR:saved_opl(context,event);
}
static void reset(int audio){
    gs_test_init(b);gs_test_startup(b,audio);b->resources=gs_resources_operations();b->resource_context=&pack;
    s=gs_test_services(b);CHECK(game_world_construct(w,&s)==GS_OK);
    w->run.configuration.players=2;w->run.configuration.player_bytes=4;w->run.level=0;w->run.water_y=200;
    CHECK(game_session_load(w,&s)==GS_OK);
    for(unsigned i=0;i<12;i++)w->items.slot[i].sprite=65535;
    if(audio)CHECK(game_audio_init(w,&s,1)==GS_OK);
    opl_calls=0;failure=0;
}
static GSStatus call(ActorCallback role,size_t player){
    uint16_t cursor=0;return game_actor_call(w,&s,&cursor,(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ACTOR,.actor=role},player);
}
static void delivery(void){
    GameActorSlot *a=w->actors.slot;
    CHECK(game_object_actor_type(ACTOR_PASSENGER_ONE_LAND,&a->descriptor)==GS_OK);
    a->callback=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ACTOR,.actor=ACTOR_CALLBACK_UpdateCarriedPassenger};
    a->source_or_done=0;a->source_byte_index=0;a->destination_platform=1;a->destination_byte_index=2;
    a->loop_cursor=0;a->quick_delivery_ticks=1;a->position=(ObjectPosition){123,456};a->animation=(ActorAnimationState){16,77};
    w->session.players.player[0].fare=4321;w->session.players.player[0].carried=1;w->session.players.player[0].destination=9;
    w->presentation.hud.fare_pending=23;w->run.multiplier=1;w->run.score=UINT32_MAX-10u;
}
static void failures_and_live_tail(void){
    reset(0);delivery();for(unsigned i=0;i<12;i++)w->items.slot[i].sprite=400;
    CHECK(call(ACTOR_CALLBACK_DeliverPassenger,0)==GS_UNSUPPORTED);
    CHECK(w->run.score==4310&&w->actors.slot[0].callback.actor==ACTOR_CALLBACK_WalkPassengerToExit);
    CHECK(w->session.players.player[0].carried==0&&w->session.players.player[0].destination==0);
    CHECK(w->actors.slot[0].position.y32==456&&w->actors.slot[0].animation.countdown==77&&w->presentation.hud.fare_pending==23);
    reset(1);delivery();saved_opl=s.audio.opl;s.audio.opl=mutate_opl;failure=1;
    CHECK(call(ACTOR_CALLBACK_DeliverPassenger,0)==GS_IO_ERROR&&opl_calls==1);
    CHECK(w->items.slot[11].sprite!=65535&&w->run.score==4310);
    CHECK(w->actors.slot[0].position.y32==456&&w->actors.slot[0].animation.countdown==77&&w->presentation.hud.fare_pending==23);
    reset(1);delivery();uint16_t anchor;CHECK(game_object_word(&s,w->actors.slot[0].descriptor,2,&anchor)==GS_OK);
    saved_opl=s.audio.opl;s.audio.opl=mutate_opl;
    CHECK(call(ACTOR_CALLBACK_DeliverPassenger,0)==GS_OK&&opl_calls>0);
    CHECK(w->actors.slot[0].position.y32==(uint16_t)((173u-anchor)*32u));
    CHECK(w->actors.slot[0].animation.byte_offset==65534&&w->actors.slot[0].animation.countdown==1&&w->presentation.hud.fare_pending==1);
    reset(0);CHECK(game_object_actor_type(ACTOR_STONE,&w->actors.slot[0].descriptor)==GS_OK);
    w->actors.slot[0].loop_cursor=0;w->audio_reset.devices=2;w->session.players.player[0].carried=7;
    CHECK(call(ACTOR_CALLBACK_ThrowCarriedStone,0)==GS_UNSUPPORTED);
    CHECK(w->actors.slot[0].callback.actor==ACTOR_CALLBACK_UpdateThrownStone&&w->actors.slot[0].sprite==545&&w->session.players.player[0].carried==0);
}
static void roles_and_passes(void){
    reset(0);GameActorSlot before=w->actors.slot[0];uint16_t cursor=0;
    CHECK(game_actor_call(w,&s,&cursor,(ObjectCallbackIdentity){0},0)==GS_UNSUPPORTED);
    CHECK(memcmp(&before,w->actors.slot,sizeof before)==0);
    cursor=1;CHECK(game_actor_call(w,&s,&cursor,(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ACTOR,.actor=ACTOR_CALLBACK_IgnoreActorState},0)==GS_UNSUPPORTED&&cursor==1);
    ObjectResourceIdentity invalid=w->actors.slot[0].journey;invalid.position=1;GSBytes bytes;
    CHECK(game_object_resource(&s,invalid,&bytes)==GS_UNSUPPORTED);
    CHECK(game_item_call(w,&s,12,ITEM_CALLBACK_COLLECT)==GS_UNSUPPORTED);
    CHECK(game_item_call(w,&s,0,ITEM_CALLBACK_SPAWN)==GS_UNSUPPORTED);
    w->session.actor_end[0]=1;CHECK(game_actors_update(w,&s)==GS_OK);
    w->session.actor_end[0]=0;w->session.actor_end[1]=0;
    CHECK(game_object_actor_type(ACTOR_STONE,&w->actors.slot[0].descriptor)==GS_OK);
    w->actors.slot[0].callback=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ACTOR,.actor=ACTOR_CALLBACK_BeginStonePickupWait};
    w->actors.slot[1].callback=(ObjectCallbackIdentity){0};w->actors.slot[2].sprite=123;
    CHECK(game_actors_update(w,&s)==GS_UNSUPPORTED);
    CHECK(w->actors.slot[0].callback.actor==ACTOR_CALLBACK_UpdateStonePickupWait&&w->actors.slot[0].animation.countdown==1&&w->actors.slot[2].sprite==123);
    ObjectResourceIdentity scripts[16];size_t count;CHECK(game_demo_vector(DEMO_PRESENT_PREGAME,scripts,&count)==GS_OK);
    w->actors.slot[0].loop_script=scripts[0];w->actors.slot[0].loop_cursor=88;
    CHECK(call(ACTOR_CALLBACK_AttachStoneToPlayer,1)==GS_OK);
    CHECK(w->actors.slot[0].loop_cursor==2&&!w->actors.slot[0].loop_script.kind);
    reset(0);ObjectResourceIdentity bonus=game_object_bonus();
    for(unsigned i=0;i<12;i++)w->items.slot[i].sprite=400;
    GameItemSpawn full=game_item_spawn(w,&s,bonus,(ObjectPosition){123,456},0,0);
    CHECK(full.status==GS_OK&&full.allocation.status==ITEM_POOL_FULL&&full.allocation.slot==-1);
    w->items.slot[11].sprite=65534;
    GameItemSpawn reuse=game_item_spawn(w,&s,bonus,(ObjectPosition){123,456},0,0);
    CHECK(reuse.status==GS_OK&&reuse.allocation.status==ITEM_SPAWNED&&reuse.allocation.slot==11);
    for(unsigned i=0;i<12;i++)w->items.slot[i].sprite=65535;
    w->session.item_descriptor[11]=bonus;w->session.item_callback[11]=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ITEM,.item=ITEM_CALLBACK_LAND};
    w->items.slot[11].sprite=65534;w->items.slot[11].motion_or_lifetime=17;
    w->items.slot[10].sprite=400;w->session.item_callback[10]=(ObjectCallbackIdentity){0};w->items.slot[9].motion_or_lifetime=23;
    CHECK(game_items_update(w,&s)==GS_UNSUPPORTED&&w->items.slot[11].motion_or_lifetime==560&&w->items.slot[9].motion_or_lifetime==23);
}
int main(int argc,char **argv){
    if(argc!=2)return 2;char error[256];CHECK(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)==GS_OK);
    w=calloc(1,sizeof *w);b=calloc(1,sizeof *b);CHECK(w&&b);
    roles_and_passes();failures_and_live_tail();free(w);free(b);gs_resources_close(&pack);
    puts("PASS object roles, live passes/aliases, full-pool and audio failure prefixes, live delivery tail");return 0;
}
