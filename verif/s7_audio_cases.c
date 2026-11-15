#include "native/compose_audio.h"
#include "port/test/backend.h"
#include "port/resources.h"
#include "resource_manifest.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#undef assert
#define assert(c) do{if(!(c)){fprintf(stderr,"check failed at line %u: %s\n",__LINE__,#c);exit(3);}}while(0)
static GameWorld *w;static GSTestBackend *b;static GSResourcePack pack;static GameServices s;
static unsigned effects,acks,pit,fail_after;
static void observe(void *ctx,GSTestEffect e){(void)ctx;effects++;if(e.kind==GST_ACK)acks++;if(e.kind==GST_PIT_COMMAND||e.kind==GST_PIT_COUNTER)pit++;}
static void reset(int card){
    gs_test_init(b);gs_test_startup(b,card);b->resources=gs_resources_operations();b->resource_context=&pack;
    s=gs_test_services(b);assert(game_world_construct(w,&s)==GS_OK);b->recorder=observe;effects=acks=pit=0;
}
static void init(void){reset(1);assert(game_audio_init(w,&s,1)==GS_OK);assert(w->audio_reset.devices==1&&w->timer.installed&&w->timer.count==2);effects=acks=pit=0;}
static GSStatus fail_opl(void *ctx,GSRegisterWrite r){(void)ctx;(void)r;return fail_after--?GS_OK:GS_IO_ERROR;}
static GSStatus fail_lifetime(void *ctx,GSTimerLifetimeRequest r,GSBinding *reply){(void)ctx;(void)r;(void)reply;return GS_IO_ERROR;}
static void profiles(void){
    reset(1);for(unsigned mask=0;mask<4;mask++)if(mask!=1){assert(game_audio_init(w,&s,(uint16_t)mask)==GS_UNSUPPORTED);assert(!effects&&!w->audio_attempted);}
    reset(0);assert(game_audio_init(w,&s,1)==GS_OK);assert(w->audio_attempted&&!w->audio_reset.devices&&!w->timer.installed);
    assert(game_audio_music_start(w,&s,0,0,200).status==GS_OK);assert(game_audio_effect(w,&s,0,200,1).status==GS_OK);
    assert(game_audio_terminal(w,&s)==GS_OK&&w->audio_shutdown==1&&!w->terminal_audio_latch);
    reset(1);s.audio.opl=fail_opl;fail_after=0;assert(game_audio_init(w,&s,1)==GS_IO_ERROR);assert(w->audio_attempted&&!w->timer.installed&&!w->audio_initialized);
    reset(1);w->audio_reset.devices=2;assert(game_audio_music_start(w,&s,game_audio_score_resource(),0,200).status==GS_UNSUPPORTED);
    assert(game_audio_effect(w,&s,game_audio_intro_resource(),200,1).status==GS_UNSUPPORTED);assert(game_audio_shutdown(w,&s)==GS_UNSUPPORTED);
}
static void music_and_effects(void){
    for(unsigned resource=0;resource<11;resource++){
        init();assert(game_audio_music_start(w,&s,game_audio_resource_id(resource),0,165).value==1);
        assert(w->audio.playing&&w->audio.channels[12].cursor.window==w->audio_data[resource].data);
        for(unsigned tick=0;tick<100;tick++)assert(game_audio_timer(w,&s)==GS_OK);
        assert(w->audio.ticks&&effects&&game_audio_elapsed(w).status==MUSIC_CLOCK_OK);
        assert(game_audio_terminal(w,&s)==GS_OK);
        assert(!w->timer.installed&&!w->audio_attempted&&!w->audio_reset.devices&&w->terminal_audio_latch&&!w->audio_shutdown);
    }
    init();assert(game_audio_music_start(w,&s,game_audio_score_resource(),5,165).status==GS_OK);
    assert(w->audio.fade.scheduled&&w->timer.count==3);
    assert(game_audio_effect(w,&s,game_audio_intro_resource(),225,1).value==8);
    assert(w->audio.reserved_voices&&w->audio.channels[8].control==5);
    assert(game_audio_music_stop(w,&s,5).status==GS_OK);
    assert(!w->audio.playing&&!w->audio.fade.scheduled&&!w->audio.reserved_voices);
    assert(w->audio.fade.step_count==6&&w->audio.playback_guard==0);
    assert(game_audio_shutdown(w,&s)==GS_OK);
    init();assert(game_audio_music_start(w,&s,game_audio_score_resource(),0,200).status==GS_OK);
    s.audio.opl=fail_opl;fail_after=0;assert(game_audio_volume(w,&s,73)==GS_IO_ERROR);assert(w->audio.track_volume==73);
    init();assert(game_audio_music_start(w,&s,0,0,200).status==GS_UNSUPPORTED);assert(!w->audio.playing);
    w->audio.ticks=0xffffffff;w->audio.time_origin=0xfffffffe;w->audio.ticks_per_unit=2;
    assert(game_audio_guarded_tick(w,&s)==GS_OK&&w->audio.ticks==1&&!w->audio.playback_guard);
    assert(game_audio_elapsed(w).units==1);w->audio.ticks_per_unit=0;assert(game_audio_elapsed(w).status==MUSIC_CLOCK_DIVIDE_BY_ZERO);
}
static void scheduler_boundaries(void){
    init();w->timer.slots[1].target=(TimerTarget){TIMER_ENTRY_FADE,TIMER_GROUP_TIMER};
    assert(game_audio_timer(w,&s)==GS_UNSUPPORTED&&!acks); /* mixed pair is open */
    init();w->timer_life.saved.role=TIMER_EXTERNAL_OTHER;assert(game_audio_callback(w,&s,TIMER_BIOS_CHAIN)==GS_UNSUPPORTED);
    init();w->timer.count=17;assert(game_audio_timer(w,&s)==GS_UNSUPPORTED&&!effects);
    init();w->audio.fade.scheduled=1;w->audio.fade.timer_handle=3;
    assert(game_audio_cancel_fade(w,&s)==GS_UNSUPPORTED&&w->audio.fade.scheduled==1);
    init();w->audio.fade.duration=0;w->audio.fade.step_count=65535;
    assert(game_audio_callback(w,&s,TIMER_MUSIC_FADE)==GS_UNSUPPORTED&&!w->audio.fade.step_count);
    init();w->audio.channels[8].control=5;w->audio.channels[8].voice_count=9;w->audio.reserved_voices=1;
    assert(game_audio_channel(w,&s,8,0,0).status==GS_UNSUPPORTED&&w->audio.channels[8].control==5);
    init();s.audio.timer_lifetime=fail_lifetime;assert(game_audio_shutdown(w,&s)==GS_IO_ERROR);
    assert(!w->timer.installed&&w->timer.count==1&&w->audio_attempted&&w->audio_reset.devices==1&&!pit);
    /* Descending consumption sees removal mutations. Both original removal
     * defects survive: do not repair a mixed pair or the handle-zero mapping. */
    init();int fade=timer_register(&w->timer,TIMER_MUSIC_FADE,119275);assert(fade>=0);
    int extra=timer_register(&w->timer,TIMER_ADLX_PLAYBACK,7);assert(extra>=0);
    w->audio.fade.scheduled=1;w->audio.fade.timer_handle=(uint16_t)fade;
    assert(game_audio_cancel_fade(w,&s)==GS_OK);assert(w->timer.count==3&&w->timer.by_handle[0]==(unsigned)extra);
    assert(timer_callback(w->timer.slots[1].target)==TIMER_OPEN);
}
int main(int argc,char **argv){
    _set_error_mode(_OUT_TO_STDERR);
    if(argc!=2)return 2;char error[256];assert(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)==GS_OK);
    w=calloc(1,sizeof *w);b=calloc(1,sizeof *b);assert(w&&b);profiles();music_and_effects();scheduler_boundaries();
    puts("PASS audio profiles, loaded playback, effects, fades, shutdown, clock, scheduler defects and failure prefixes");
    free(w);free(b);gs_resources_close(&pack);return 0;
}
