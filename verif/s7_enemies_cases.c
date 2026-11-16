#include "native/compose_enemies.h"
#include "native/compose_session.h"
#include "native/compose_audio.h"
#include "native/game_object_data.h"
#include "port/resources.h"
#include "port/test/backend.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"enemy check %u: %s\n",__LINE__,#x);exit(3);}}while(0)
static GameWorld *w;static GSTestBackend *b;static GameServices s;static GSResourcePack pack;
static GSStatus (*saved_opl)(void *,GSRegisterWrite);
static unsigned calls,mutation;static int fail;
static GSStatus opl(void *ctx,GSRegisterWrite event){
    if(!calls++){
        if(mutation==1){w->session.players.player[0].fixed_x=1024;w->session.players.player[0].fixed_y=1024;w->enemies.slot[0].animation_offset=4;}
        if(mutation==2)w->actors.slot[0].motion_or_period_word=100;
        if(mutation==3)CHECK(game_object_enemy_type(LEVEL_TRIOPTERUS,w->session.enemy_descriptor)==GS_OK);
        if(mutation==4)CHECK(game_object_enemy_type(LEVEL_TREE,w->session.enemy_descriptor)==GS_OK);
    }
    return fail?GS_IO_ERROR:saved_opl(ctx,event);
}
static GSStatus no_control(void *ctx,GSVideoRoute r,uint8_t v){(void)ctx;(void)r;(void)v;return GS_IO_ERROR;}
static void reset(int sound){
    gs_test_init(b);gs_test_startup(b,sound);b->resources=gs_resources_operations();b->resource_context=&pack;s=gs_test_services(b);
    CHECK(game_world_construct(w,&s)==GS_OK);w->run.configuration.players=2;w->run.configuration.player_bytes=4;
    w->run.level=0;CHECK(game_session_load(w,&s)==GS_OK);for(unsigned i=0;i<12;i++)w->items.slot[i].sprite=65535;
    if(sound)CHECK(game_audio_init(w,&s,1)==GS_OK);calls=mutation=0;fail=0;
}
static void kind(LevelEnemyKind kind){CHECK(game_object_enemy_type(kind,w->session.enemy_descriptor)==GS_OK);}
static GSStatus call(HazardEntry entry){return game_enemy_call(w,&s,0,(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ENEMY,.enemy=entry},0);}
static void stone(void){
    GameActorSlot *a=w->actors.slot;CHECK(game_object_actor_type(ACTOR_STONE,&a->descriptor)==GS_OK);
    a->callback=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ACTOR,.actor=ACTOR_CALLBACK_UpdateThrownStone};
    a->position=(ObjectPosition){1024,1024};a->motion_or_period_word=64;a->delay_or_repeat_word=65520;
    w->session.actor_end[0]=0;w->session.actor_end[1]=1;
}
static void prefixes(void){
    reset(0);kind(LEVEL_TREE);stone();NativeEnemySlot *a=w->enemies.slot;
    ObjectResourceIdentity list=w->session.enemy_list[0];for(unsigned i=0;i<12;i++)w->items.slot[i].sprite=400;
    a->animation_offset=27;a->countdown=0x80ff;a->direction_or_target_word=0xdead;
    CHECK(call(H_TREE_RELEASE)==GS_UNSUPPORTED);
    CHECK(w->session.enemy_callback[0].enemy==H_TREE_COOLDOWN&&a->counter==210&&a->sprite==232);
    CHECK(w->session.enemy_list[0].position==list.position&&a->animation_offset==27&&a->countdown==0x80ff&&a->direction_or_target_word==0xdead);
    reset(0);kind(LEVEL_TREE);w->actors.slot[15].position=(ObjectPosition){777,888};w->actors.slot[15].delay_or_repeat_word=48879;
    CHECK(game_enemy_call(w,&s,0,(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ENEMY,.enemy=H_TREE_RELEASE},15)==GS_OK);
    CHECK(w->items.slot[11].motion_or_lifetime==48879);
    reset(1);kind(LEVEL_BIRD);a=w->enemies.slot;saved_opl=s.audio.opl;s.audio.opl=opl;fail=1;
    a->counter=1;a->sprite=123;CHECK(call(H_BIRD_WARNING)==GS_IO_ERROR);
    CHECK(w->session.enemy_callback[0].enemy==H_BIRD_WARN_WAIT&&a->counter==70&&a->sprite==123&&calls);
    reset(1);kind(LEVEL_DINO);a=w->enemies.slot;a->animation_offset=4;a->countdown=1;a->sprite=123;
    saved_opl=s.audio.opl;s.audio.opl=opl;fail=1;CHECK(call(H_DINO_FORCE)==GS_IO_ERROR);
    CHECK(a->animation_offset==6&&a->countdown==15&&a->sprite==123);
    reset(1);kind(LEVEL_TREE);stone();a=w->enemies.slot;list=w->session.enemy_list[0];
    saved_opl=s.audio.opl;s.audio.opl=opl;fail=1;CHECK(call(H_TREE_RELEASE)==GS_IO_ERROR);
    CHECK(w->session.enemy_list[0].position==list.position+2&&w->items.slot[11].sprite!=65535&&a->counter==210&&a->sprite==232);
    reset(1);kind(LEVEL_BIRD);a=w->enemies.slot;CHECK(call(H_BIRD_LAUNCH)==GS_OK);
    a->x32=1024;a->y32=1024;a->speed=0;a->countdown=1;a->animation_offset=65534;stone();
    saved_opl=s.audio.opl;s.audio.opl=opl;fail=1;CHECK(call(H_BIRD_FLIGHT)==GS_IO_ERROR);
    CHECK(a->countdown==4&&a->animation_offset==0&&w->actors.slot[0].motion_or_period_word==64&&w->session.enemy_callback[0].enemy==H_BIRD_FLIGHT);
    reset(0);a=w->enemies.slot;a->erase_sprite=232;a->sprite=123;a->previous_x=10;a->previous_y=20;
    w->enemies.slot[1].erase_sprite=999;w->session.enemy_end[0]=0;w->session.enemy_end[1]=0;
    s.video.control_write=no_control;CHECK(game_enemies_erase(w,&s)==GS_IO_ERROR);CHECK(a->erase_sprite==123&&w->enemies.slot[1].erase_sprite==999);
    reset(0);kind(LEVEL_TREE);a=w->enemies.slot;a->sprite=232;a->x32=1024;a->y32=1024;a->draw_x=12;a->draw_y=13;
    s.video.control_write=no_control;CHECK(game_enemies_draw_back(w,&s)==GS_IO_ERROR);
    CHECK(a->previous_x==12&&a->previous_y==13&&a->draw_x==32&&a->draw_y==32);
}
static void live_and_aliases(void){
    reset(0);kind(LEVEL_TREE);NativeEnemySlot *a=w->enemies.slot;
    a->x32=123;a->y32=456;w->session.enemy_end[0]=0;w->session.enemy_end[1]=0;
    w->session.enemy_callback[0]=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ENEMY,.enemy=H_TREE_BEGIN};
    w->session.enemy_callback[1]=(ObjectCallbackIdentity){0};CHECK(game_enemies_update(w,&s)==GS_UNSUPPORTED);
    CHECK(a->draw_x==(uint16_t)(123u<<5)&&a->draw_y==(uint16_t)(456u<<5));
    for(unsigned i=0;i<5;i++){w->session.enemy_end[i]=0;w->session.enemy_callback[i]=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ENEMY,.enemy=H_IGNORE};}
    w->session.platforms.slot[0].left=65535;CHECK(game_enemies_update(w,&s)==GS_OK);
    w->session.platforms.slot[0].left=12;CHECK(game_enemies_update(w,&s)==GS_UNSUPPORTED);
    CHECK(call(H_ZERO)==GS_UNSUPPORTED);CHECK(call((HazardEntry)999)==GS_UNSUPPORTED);
    CHECK(game_enemy_call(w,&s,5,(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ENEMY,.enemy=H_IGNORE},0)==GS_UNSUPPORTED);
    CHECK(game_enemy_call(w,&s,0,(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ACTOR},0)==GS_UNSUPPORTED);
    reset(0);kind(LEVEL_TRIOPTERUS);a=w->enemies.slot;a->countdown=1;a->direction_or_target_word=20;
    CHECK(call(H_TRIO_CHARGE)==GS_UNSUPPORTED); /* animation index 12 is not a vector */
    reset(0);kind(LEVEL_BIRD);a=w->enemies.slot;a->sound_handle_word=0xffff;
    CHECK(call(H_BIRD_STOP)==GS_OK);a->counter=0;CHECK(call(H_BIRD_WAIT)==GS_OK&&a->counter==65535);
    a->direction_or_target_word=32768;w->session.players.player[1].fixed_x=0;CHECK(call(H_BIRD_LAUNCH)==GS_OK&&a->direction_or_target_word==32769&&a->x32==10208);
    a->countdown=0x8000;a->animation_offset=0x1235;a->direction_or_target_word=0x8001;a->x32=1024;a->speed=0;
    CHECK(call(H_BIRD_FLIGHT)==GS_OK&&a->countdown==0x7fff&&a->animation_offset==0x1235&&a->direction_or_target_word==0x8001);
    reset(0);kind(LEVEL_TRIOPTERUS);a=w->enemies.slot;a->platform=0;a->counter=7;a->countdown=0x8000;a->direction_or_target_word=0;
    for(unsigned i=0;i<2;i++)w->session.players.player[i].platform=65535;
    CHECK(call(H_TRIO_PATROL)==GS_OK);w->session.players.player[1].platform=0;CHECK(call(H_TRIO_PATROL)==GS_OK);
    CHECK(w->session.enemy_callback[0].enemy==H_TRIO_ALERT&&a->counter==140&&a->animation_offset==65534&&a->countdown==1);
    reset(1);kind(LEVEL_DINO);a=w->enemies.slot;a->x32=1024;a->y32=1024;a->animation_offset=4;a->countdown=1;
    w->session.players.player[0].velocity_x=0;saved_opl=s.audio.opl;s.audio.opl=opl;mutation=1;
    CHECK(call(H_DINO_FORCE)==GS_OK&&calls);CHECK(a->animation_offset==4); /* live offset is not overwritten */
    reset(1);kind(LEVEL_BIRD);a=w->enemies.slot;a->x32=1024;a->y32=1024;a->speed=0;a->countdown=1;a->animation_offset=65534;
    CHECK(call(H_BIRD_LAUNCH)==GS_OK); /* initialize a real live sound handle */
    a->x32=1024;a->y32=1024;a->speed=0;stone();saved_opl=s.audio.opl;s.audio.opl=opl;mutation=2;
    CHECK(call(H_BIRD_FLIGHT)==GS_OK);CHECK(calls&&w->actors.slot[0].motion_or_period_word==(uint16_t)-100);
    reset(1);kind(LEVEL_BIRD);a=w->enemies.slot;CHECK(call(H_BIRD_LAUNCH)==GS_OK);
    a->x32=64512;a->speed=65500;a->initial_delay=77;saved_opl=s.audio.opl;s.audio.opl=opl;mutation=3;
    CHECK(call(H_BIRD_FLIGHT)==GS_OK&&calls);CHECK(w->session.enemy_callback[0].enemy==H_TRIO_PATROL&&a->counter==77&&a->sprite==65535);
    reset(1);kind(LEVEL_BIRD);a=w->enemies.slot;CHECK(call(H_BIRD_LAUNCH)==GS_OK);
    a->x32=1024;a->y32=1024;a->speed=0;a->countdown=1;a->animation_offset=65534;stone();
    saved_opl=s.audio.opl;s.audio.opl=opl;mutation=4;CHECK(call(H_BIRD_FLIGHT)==GS_OK&&calls);
    CHECK(w->session.enemy_callback[0].enemy==H_BIRD_FALL);LevelEnemyKind now;CHECK(game_object_enemy_kind(w->session.enemy_descriptor[0],&now)==GS_OK&&now==LEVEL_TREE);
}
int main(int argc,char **argv){
    if(argc!=2)return 2;char error[256];CHECK(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)==GS_OK);
    w=calloc(1,sizeof *w);b=calloc(1,sizeof *b);CHECK(w&&b);prefixes();live_and_aliases();
    gs_resources_close(&pack);free(w);free(b);puts("PASS focused enemy failure prefixes, live services, alias bounds and raw words");return 0;
}
