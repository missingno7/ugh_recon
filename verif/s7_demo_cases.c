#include "native/compose_demo.h"
#include "native/game_startup.h"
#include "port/test/backend.h"
#include "port/resources.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(c) do{if(!(c)){fprintf(stderr,"check failed line %u: %s\n",__LINE__,#c);exit(3);}}while(0)
static GameWorld *w;static GSTestBackend *b;static GSResourcePack pack;static GameServices services;
static void fresh(void){
    gs_test_init(b);b->resources=gs_resources_operations();b->resource_context=&pack;services=gs_test_services(b);
    CHECK(game_world_construct(w,&services)==GS_OK);
    w->pages=(VideoPages){.height=192,.plane_copy_bytes=0x4800,.fixed=0,.displayed=0xa88,.draw=0x5a08,.background=0xa988};
    w->input.loop_limit=3;w->input.enabled_axis_storage&=65280u;
    GSTestRun retraces[]={{0,1},{8,1}},absent[]={{255,10000}};
    CHECK(gs_test_stream(&b->retrace_samples,retraces,2,UINT32_MAX)==GS_OK);CHECK(gs_test_stream(&b->joystick,absent,1,UINT32_MAX)==GS_OK);
}
static GSStatus stop_present(void *context){(void)context;return GS_IO_ERROR;}
static unsigned palette_mutated;
static void mutate_palette(void *context,GSTestEffect effect){
    (void)context;
    if(!palette_mutated&&w->actors.slot[0].demo&&effect.kind==GST_DAC){
        palette_mutated=1;w->run.fade_level=123;w->run.fade_step=65532;
    }
}
int main(int argc,char **argv){
    CHECK(argc==2);char error[256];CHECK(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)==GS_OK);
    w=calloc(1,sizeof *w);b=calloc(1,sizeof *b);CHECK(w&&b);fresh();
    /* All identity boundaries, including interior/nonregistered rejection. */
    for(unsigned n=0;n<GAME_DEMO_SCRIPTS;n++){
        ObjectResourceIdentity id=w->demo_resources.scripts[n].identity;GSBytes bytes;
        CHECK(game_demo_resource(w,id,&bytes)==GS_OK);id.position=1;CHECK(game_demo_resource(w,id,&bytes)==GS_UNSUPPORTED);
        id.position=8;CHECK(game_demo_resource(w,id,&bytes)==GS_OK);id.position=9;CHECK(game_demo_resource(w,id,&bytes)==GS_UNSUPPORTED);
    }
    /* The descending reset covers all owners; dormant cells stay live. */
    for(unsigned i=0;i<16;i++){w->actors.slot[i].sprite=42;w->actors.slot[i].history=(ActorRenderHistory){1,2,3,4,5,6};w->actors.slot[i].loop_cursor=333;w->actors.slot[i].quick_delivery_ticks=444;}
    for(unsigned i=0;i<5;i++){w->enemies.slot[i].sprite=1;w->enemies.slot[i].erase_sprite=2;w->enemies.slot[i].direction_or_target_word=123;}
    for(unsigned i=0;i<12;i++){w->items.slot[i].sprite=1;w->items.slot[i].erase_sprite=2;w->items.slot[i].motion_or_lifetime=456;}
    CHECK(game_demo_reset(w)==GS_OK);
    for(unsigned i=0;i<16;i++){GameActorSlot *a=w->actors.slot+i;CHECK(a->sprite==65535&&a->history.erase_sprite==65535&&a->history.erase_overlay_sprite==6&&a->history.previous_x==3&&a->history.pixel_y==2&&a->loop_cursor==333&&a->quick_delivery_ticks==444);}
    for(unsigned i=0;i<5;i++)CHECK(w->enemies.slot[i].sprite==65535&&w->enemies.slot[i].erase_sprite==65535&&w->enemies.slot[i].direction_or_target_word==123);
    for(unsigned i=0;i<12;i++)CHECK(w->items.slot[i].sprite==65535&&w->items.slot[i].erase_sprite==65535&&w->items.slot[i].motion_or_lifetime==456);
    fresh();CHECK(game_demo_initialize(w,&services,DEMO_PRESENT_REVEAL)==GS_OK);
    GameActorSlot *actor=w->actors.slot;GameDemoResource *r=0;
    /* An admitted instruction identity cannot stand in for a header. */
    actor->script.position=8;CHECK(game_demo_advance(w,&services)==GS_UNSUPPORTED);actor->script.position=0;
    ObjectResourceIdentity saved_loop=actor->loop_script;actor->delay_or_repeat_word=1;actor->loop_script.kind=OBJECT_RESOURCE_UNSUPPORTED;
    CHECK(game_demo_advance(w,&services)==GS_UNSUPPORTED);actor->delay_or_repeat_word=0;actor->loop_script=saved_loop;
    for(unsigned i=0;i<GAME_DEMO_SCRIPTS;i++)if(w->demo_resources.scripts[i].identity.view.index==actor->script.view.index)r=w->demo_resources.scripts+i;
    CHECK(r);uint8_t *data=w->demo_resources.bytes+r->offset;
    /* Unsupported callback still observes the new position while cursor stays
     * at its old instruction. No later actor is visited after this prefix. */
    data[8]=214;data[9]=0;data[10]=3;data[11]=255;
    actor->cursor=0;actor->delay_or_repeat_word=0;actor->animation.countdown=1;actor->position=(ObjectPosition){100,200};actor->callback.kind=OBJECT_CALLBACK_ACTOR;actor->callback.actor=ACTOR_CALLBACK_BoardPassenger;
    w->actors.slot[1].animation.countdown=123;
    CHECK(game_demo_advance(w,&services)==GS_UNSUPPORTED);
    CHECK(actor->position.x32==112&&actor->position.y32==196&&actor->sprite==214&&actor->cursor==0&&w->actors.slot[1].animation.countdown==123);
    actor->callback=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_DEMO_EFFECT,.effect={RESOURCE_DEMO_EFFECT,DEMO_EFFECT_REVEAL_WIDTH}};
    actor->animation.countdown=1;CHECK(game_demo_advance(w,&services)==GS_OK);CHECK(actor->cursor==4);
    CHECK((w->sprite_catalog.sprites[214].dimensions&255u)==127);
    CHECK(game_demo_callback(w,&services,16,actor->callback)==GS_UNSUPPORTED);
    actor->callback.effect.index=3;CHECK(game_demo_callback(w,&services,0,actor->callback)==GS_UNSUPPORTED);
    /* Low-byte width stores preserve height and do not normalize negatives. */
    actor->position.x32=321*32;uint16_t height=w->sprite_catalog.sprites[214].dimensions&65280u;
    actor->callback.effect.index=DEMO_EFFECT_REVEAL_WIDTH;CHECK(game_demo_callback(w,&services,0,actor->callback)==GS_OK);
    CHECK(w->sprite_catalog.sprites[214].dimensions==(height|255));
    actor->sprite=DEMO_HIDDEN_SPRITE;w->run.fade_level=1;actor->callback.effect.index=DEMO_EFFECT_FADE_ON_HIDDEN;
    CHECK(game_demo_callback(w,&services,0,actor->callback)==GS_OK&&w->run.fade_level==65533&&w->run.fade_step==65532);
    /* A presentation failure retains page/frame stores that precede it. */
    fresh();CHECK(game_demo_initialize(w,&services,DEMO_PRESENT_REVEAL)==GS_OK);
    services.video.present=stop_present;CHECK(game_video_swap(w,&services)==GS_IO_ERROR);CHECK(w->frames==1);
    /* Active music uses the real typed facade, including initialized timers. */
    fresh();gs_test_startup(b,1);services=gs_test_services(b);
    CHECK(game_initialize_audio(w,&services)==GS_OK);
    CHECK(game_demo_music_start(w,&services,165)==GS_OK&&w->audio.playing);
    CHECK(game_demo_music_stop(w,&services,17)==GS_OK);
    GameDemoResult result;
    /* The palette service returns its retained factor, then presentation adds
     * the live fade step. A synchronous peer must not replace that factor by
     * a fresh read of the fade-level owner after the upload. */
    fresh();palette_mutated=0;b->recorder=mutate_palette;
    result=game_demo_play(w,&services,DEMO_PRESENT_REVEAL);
    CHECK(result.status==GS_OK&&palette_mutated&&w->run.fade_level==65532&&w->frames==3);
    /* Complete all wrappers with explicit external Escape, including reveal's
     * cleanup and the original exit result across that cleanup. */
    for(unsigned kind=DEMO_PRESENT_REVEAL;kind<=DEMO_PRESENT_COMPLETION;kind++){
        fresh();GSTestRun scans[]={{0,1},{1,1}};CHECK(gs_test_stream(&b->scans,scans,2,1)==GS_OK);
        result=game_demo_play(w,&services,(DemoPresentationKind)kind);CHECK(result.status==GS_OK&&result.selection==1);
        CHECK((int16_t)w->run.fade_level<0&&w->run.fade_step==65532);
        if(kind==DEMO_PRESENT_REVEAL)CHECK(w->actors.slot[0].position.x32==0&&(w->sprite_catalog.sprites[214].dimensions&255u)==127);
    }
    gs_resources_close(&pack);free(w);free(b);puts("PASS demo identity, callback cuts, aliases, width, failure, audio seam and wrapper cases");return 0;
}
