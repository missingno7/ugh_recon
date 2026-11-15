#include "compose_demo.h"
#include "compose_front_end.h"
#include "compose_audio.h"
#include "game_startup.h"
#include "game_defaults.h"
#include "demo_core.h"
#include "actor_resources.h"
#include "actor_render.h"
#include "render_primitives.h"
#include "menus.h"
#include "water_weather.h"
#include "ice.h"
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
GSStatus game_demo_map_resource(GameServices *,GSBytes *);
static uint16_t demo_word(const uint8_t *b){return (uint16_t)(b[0]|(uint16_t)b[1]<<8);}
static GSStatus control(GameServices *s,GSVideoRoute route,uint8_t value){return s->video.control_write(s->video_context,route,value);}
static GameDemoResource *script_resource(GameWorld *w,ObjectResourceIdentity id){
    if(id.kind!=OBJECT_SCRIPT||id.position)return 0;
    for(size_t i=0;i<GAME_DEMO_SCRIPTS;i++)if(w->demo_resources.scripts[i].identity.view.index==id.view.index)return w->demo_resources.scripts+i;
    return 0;
}
GSStatus game_demo_callback(GameWorld *w,GameServices *s,size_t index,ObjectCallbackIdentity callback){
    (void)s;
    if(!w||index>=ACTOR_CAPACITY||callback.kind!=OBJECT_CALLBACK_DEMO_EFFECT||callback.effect.kind!=RESOURCE_DEMO_EFFECT)return GS_UNSUPPORTED;
    switch(callback.effect.index){
    case DEMO_EFFECT_NONE:return GS_OK;
    case DEMO_EFFECT_FADE_ON_HIDDEN:{
        DemoFadeEffect effect=demo_presentation_fade(w->actors.slot[index].sprite,w->run.fade_level);
        if(effect.triggered){w->run.fade_step=effect.fade_step;w->run.fade_level=effect.level;}return GS_OK;}
    case DEMO_EFFECT_REVEAL_WIDTH:{
        DemoRevealWidth width=demo_presentation_width(w->actors.slot[index].position.x32);
        ResourceSpriteRecord *sprite=&w->sprite_catalog.sprites[214];
        sprite->dimensions=(uint16_t)((sprite->dimensions&65280u)|width.width);return GS_OK;}
    default:return GS_UNSUPPORTED;
    }
}
GSStatus game_demo_advance(GameWorld *w,GameServices *s){
    if(!w||!s||!w->demo_resources.ready)return GS_INVALID;
    for(size_t i=0;i<ACTOR_CAPACITY;i++){
        GameActorSlot *a=w->actors.slot+i;
        if(a->cursor==UINT16_MAX)return GS_OK;
        if(!a->demo)return GS_UNSUPPORTED;
        if(!script_resource(w,a->script))return GS_UNSUPPORTED;
        GSBytes b;TRY(game_demo_resource(w,a->script,&b));
        GSBytes instruction;ObjectResourceIdentity at=a->script;at.position=(uint16_t)(a->cursor+8u);
        if(a->cursor>UINT16_MAX-8u)return GS_UNSUPPORTED;
        TRY(game_demo_resource(w,at,&instruction));
        DemoMotionScript script={.period=a->motion_or_period_word,.code=b.data+8,.code_size=b.size-8};
        if(!demo_script_boundary(&script,a->cursor))return GS_UNSUPPORTED;
        if(a->delay_or_repeat_word){
            if(a->loop_script.kind!=OBJECT_SCRIPT||a->loop_script.position||a->loop_script.view.index!=a->script.view.index)return GS_UNSUPPORTED;
            if(a->loop_cursor>UINT16_MAX-8u||!demo_script_boundary(&script,a->loop_cursor))return GS_UNSUPPORTED;
            at.position=(uint16_t)(a->loop_cursor+8u);TRY(game_demo_resource(w,at,&instruction));
        }
        DemoMotionSlot slot={&script,a->cursor,a->loop_cursor,a->delay_or_repeat_word,a->animation.countdown,a->source_or_done!=0,a->position,a->sprite};
        DemoStep effects;if(!demo_advance_slot(&slot,&effects))return GS_UNSUPPORTED;
        a->animation.countdown=slot.countdown;
        if(effects.repeat_written)a->delay_or_repeat_word=slot.repeat_count;
        if(effects.restart_written){a->loop_cursor=(uint16_t)slot.repeat_start;a->loop_script=a->script;}
        if(effects.stopped)a->source_or_done=UINT16_MAX;
        if(effects.motion){
            a->sprite=slot.sprite;a->position=slot.position;
            /* Deliberately reload the callback after publication. The owner
             * still exposes the old cursor throughout this synchronous call. */
            TRY(game_demo_callback(w,s,i,a->callback));
        }
        if(effects.motion||effects.stopped)a->cursor=(uint16_t)slot.cursor;
        /* Next slot, period, repeat and callback are read only on its visit. */
    }return GS_OVERFLOW;
}
GSStatus game_demo_reset(GameWorld *w){
    if(!w)return GS_INVALID;
    for(size_t n=5;n;n--){w->enemies.slot[n-1].sprite=UINT16_MAX;w->enemies.slot[n-1].erase_sprite=UINT16_MAX;}
    for(size_t n=ACTOR_CAPACITY;n;n--){
        ActorRenderStorage render={0};render.slots[n-1]=w->actors.slot[n-1].history;
        ActorRenderInput input={0};ActorRenderResult result=actor_render_apply(ACTOR_RENDER_RESET,&render,n-1,&input);
        for(size_t j=0;j<result.count;j++)if(result.events[j].field==ACTOR_RENDER_CURRENT_SPRITE)w->actors.slot[n-1].sprite=result.events[j].value;
        w->actors.slot[n-1].history=render.slots[n-1];
    }
    for(size_t n=12;n;n--){w->items.slot[n-1].sprite=UINT16_MAX;w->items.slot[n-1].erase_sprite=UINT16_MAX;}
    return GS_OK;
}
GSStatus game_demo_initialize(GameWorld *w,GameServices *s,DemoPresentationKind kind){
    if(!w||!s||!w->demo_resources.ready)return GS_INVALID;
    ObjectResourceIdentity ids[ACTOR_CAPACITY];size_t count;TRY(game_demo_vector(kind,ids,&count));
    DemoMotionScene scene={0};ActorRenderStorage render;DemoMotionScript scripts[ACTOR_CAPACITY];const DemoMotionScript *pointers[ACTOR_CAPACITY];
    for(size_t i=0;i<ACTOR_CAPACITY;i++)render.slots[i]=w->actors.slot[i].history;
    for(size_t i=0;i<count;i++){
        GSBytes bytes;TRY(game_demo_resource(w,ids[i],&bytes));GameDemoResource *r=script_resource(w,ids[i]);if(!r)return GS_UNSUPPORTED;
        scripts[i]=(DemoMotionScript){demo_word(bytes.data),demo_word(bytes.data+2),demo_word(bytes.data+4),DEMO_EFFECT_NONE,bytes.data+8,bytes.size-8};
        pointers[i]=scripts+i;scene.slots[i].repeat_start=w->actors.slot[i].loop_cursor;
    }
    demo_initialize(&scene,&render,pointers,count);
    for(size_t i=0;i<count;i++){
        GameActorSlot *a=w->actors.slot+i;DemoMotionSlot *slot=scene.slots+i;
        a->demo=1;a->script=ids[i];a->callback=script_resource(w,ids[i])->callback;
        a->cursor=(uint16_t)slot->cursor;a->position=slot->position;a->motion_or_period_word=slot->script->period;
        a->animation.countdown=slot->countdown;a->delay_or_repeat_word=slot->repeat_count;a->source_or_done=0;
        a->history=render.slots[i];
    }
    w->actors.slot[count].cursor=UINT16_MAX;
    TRY(game_demo_reset(w));return game_demo_advance(w,s);
}
static GSStatus sprite_draw(GameWorld *w,GameServices *s,uint16_t sprite,uint16_t x,uint16_t y){
    if(sprite>=RESOURCE_SPRITE_RECORDS)return GS_UNSUPPORTED;
    RenderSpritePlacement p=render_sprite_place(sprite,x,y,w->run.water_y,w->pages.height,w->pages.draw,w->pages.fixed);
    w->front_data.renderer_water=p.water;TRY(control(s,GS_SEQ_INDEX,2));
    w->front_data.renderer_plane=(uint16_t)(2u+256u*p.plane);
    GSBytes bank;uint16_t ignored_source,ignored_dimensions;TRY(game_front_sprite(s,sprite,&bank,&ignored_source,&ignored_dimensions));
    ResourceSpriteRecord record=w->sprite_catalog.sprites[sprite];RenderSpriteCursor c;render_sprite_begin(&c,p,record.source_offset,record.dimensions,0);
    do{TRY(control(s,GS_SEQ_DATA,c.plane));do{
        if(c.source>=bank.size)return GS_UNSUPPORTED;
        RenderPixelRequest pixel=render_sprite_pixel(&c,bank.data[c.source]);
        if(pixel.write)TRY(s->video.store(s->video_context,pixel.destination,pixel.value));
    }while(c.rows);render_sprite_column(&c);}while(c.columns);
    return control(s,GS_SEQ_DATA,15);
}
static GSStatus render(GameWorld *w,GameServices *s,int draw,uint8_t *trigger){
    if(!w||!s||!w->demo_resources.ready)return GS_INVALID;
    for(size_t i=0;i<ACTOR_CAPACITY;i++){
        GameActorSlot *a=w->actors.slot+i;if(a->cursor==UINT16_MAX)return GS_OK;if(!a->demo)return GS_UNSUPPORTED;
        if(draw&&trigger)*trigger=(uint8_t)a->sprite;
        ActorRenderStorage render={0};render.slots[i]=a->history;
        ActorRenderInput input={a->position,a->sprite,a->overlay_sprite};
        ActorRenderResult result=actor_render_apply(draw?ACTOR_RENDER_DEMO_DRAW:ACTOR_RENDER_DEMO_ERASE,&render,i,&input);
        /* All stores in these two operations precede their pixel request. */
        a->history=render.slots[i];
        for(size_t j=0;j<result.count;j++){
            ActorRenderEvent e=result.events[j];
            if(e.kind==ACTOR_RENDER_DRAW)TRY(sprite_draw(w,s,e.sprite,e.x,e.y));
            else if(e.kind==ACTOR_RENDER_RESTORE){
                uint16_t index=(uint16_t)(render_restore_sprite_index(e.sprite)/4u);if(index>=RESOURCE_SPRITE_RECORDS)return GS_UNSUPPORTED;
                RenderRectangleSpec r=render_sprite_rectangle(e.x,e.y,w->sprite_catalog.sprites[index].dimensions);
                TRY(game_front_restore(w,s,(FrontRectangle){r.x,r.y,r.width,r.height}));
            }
        }
    }return GS_OVERFLOW;
}
GSStatus game_demo_render(GameWorld *w,GameServices *s,int draw){return render(w,s,draw,0);}
GSStatus game_demo_water(GameWorld *w,GameServices *s){
    if(!w||!s||!w->demo_resources.ready)return GS_INVALID;
    NativeWeatherPresentation *p=&w->presentation.weather;
    WaterWeatherState state={.surface_y=w->run.water_y,.byte_position=p->byte_offset,.frame=p->frame,.countdown=p->countdown};
    WeatherResult result=water_weather_prepare(&state,(WaterWeatherInputs){.row_stride=w->demo_resources.row_stride});
    p->byte_offset=state.byte_position;p->frame=state.frame;p->countdown=state.countdown;
    WeatherAction tail=result.actions[result.count-1];if(tail.kind!=WW_FRAME_TAIL||tail.value>4)return GS_UNSUPPORTED;
    TRY(control(s,GS_SEQ_INDEX,2));TRY(control(s,GS_SEQ_DATA,1));
    const uint8_t colors[]={84,85,86,87,88};WeatherFrameCursor c;weather_frame_begin(&c,colors,1);
    for(;;){WeatherAction e=weather_frame_next(&c,tail.value/2u);
        if(e.kind==WW_DONE)return GS_OK;
        if(e.kind==WW_MASK)TRY(control(s,GS_SEQ_DATA,(uint8_t)e.value));
        else if(e.kind==WW_PIXEL)TRY(s->video.store(s->video_context,(uint16_t)(w->pages.draw+tail.position+e.position),(uint8_t)e.value));
        else return GS_UNSUPPORTED;
    }
}
GSStatus game_demo_prepare(GameWorld *w,GameServices *s,int second){
    if(!w||!s||!w->demo_resources.ready)return GS_INVALID;
    w->run.water_y=menus_water(second?1:0);
    TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_SELECT,0}));
    for(unsigned i=0;i<video_blackening_batches();i++){
        TRY(game_video_next(w,s));for(unsigned j=0;j<3*video_blackening_entries();j++)TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_COMPONENT,0}));
    }
    TRY(game_clear_video(w,s));VideoCopyCursor copy=video_duplicate_begin(0,0,0);
    do{VideoDuplicateTransfer t=video_duplicate_transfer(&copy);for(unsigned j=0;j<2;j++){
        w->palette.base[t.destinations[j]]=w->front_data.source_palette[t.source];w->palette.base[t.destinations[j]+1]=w->front_data.source_palette[t.source+1];
    }video_duplicate_advance(&copy);}while(copy.remaining);
    GSBytes maps;TRY(game_demo_map_resource(s,&maps));IceResult decoded;
    if(ice_decode(maps.data,maps.size,w->scratch,sizeof w->scratch,&decoded)!=ICE_OK)return GS_INVALID;
    MenusMapCopy map=menus_map_begin(menus_attract_map_offset(second),0,0);
    do{if(map.source+1u>=sizeof w->scratch||map.destination+1u>=sizeof w->run.tiles)return GS_UNSUPPORTED;
        w->run.tiles[map.destination]=w->scratch[map.source];w->run.tiles[map.destination+1]=w->scratch[map.source+1];menus_map_advance(&map);
    }while(map.remaining);
    for(unsigned i=0;i<320;i++){RenderDrawRequest tile=render_map_cell((uint16_t)i,w->run.tiles[i]);TRY(sprite_draw(w,s,tile.sprite,tile.x,tile.y));}
    if(second)TRY(game_front_header(w,s));
    TRY(game_front_save_background(w,s));TRY(game_video_swap(w,s));
    TRY(game_front_restore(w,s,(FrontRectangle){0,0,320,w->pages.height}));
    if(menus_draw_water(w->run.water_y))TRY(game_demo_water(w,s));
    return game_video_swap(w,s);
}
GSStatus game_demo_music_stop(GameWorld *w,GameServices *s,uint16_t duration){
    if(!w||!s)return GS_INVALID;
    return game_audio_music_stop(w,s,duration).status;
}
GSStatus game_demo_music_start(GameWorld *w,GameServices *s,uint16_t volume){
    if(!w||!s)return GS_INVALID;
    return game_audio_music_start(w,s,game_audio_score_resource(),0,volume).status;
}
static GSStatus palette(GameWorld *w,GameServices *s,uint16_t *work){
    uint16_t factor=w->run.fade_level;
    VideoClearCursor c=video_scale_begin();do{w->palette.faded[c.position]=video_palette_scale(w->palette.base[c.position],factor).value;video_scale_advance(&c);}while(c.remaining);
    TRY(game_video_next(w,s));TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_SELECT,0}));
    VideoPaletteRange range=video_palette_range(0,0,216,0);
    do{for(unsigned j=0;j<3;j++)TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_COMPONENT,w->palette.faded[video_palette_advance(&range)]}));}while(--range.entries);
    *work=factor;return GS_OK;
}
static int finished(GameWorld *w){
    for(size_t i=0;i<ACTOR_CAPACITY;i++){GameActorSlot *a=w->actors.slot+i;if(a->cursor==UINT16_MAX)return 1;if(!a->source_or_done)return 0;}return 0;
}
/* Gameport charging retains the byte from the preceding draw operation. The
 * device ignores its bits, but the synchronous ordered service stream does
 * observe them. This is a typed service operand, not a register frame. */
static GSStatus sample(GameWorld *w,GameServices *s,uint8_t trigger){
    TRY(s->input.joystick_start(s->input_context,trigger));
    for(unsigned i=0;i<2;i++)TRY(s->input.buttons(s->input_context,i,&w->input.joysticks[i].buttons));
    GSJoystickCounts reply;TRY(s->input.counts(s->input_context,w->input.loop_limit,(uint8_t)w->input.enabled_axis_storage,&reply));
    for(unsigned i=0;i<2;i++){w->input.joysticks[i].x=reply.counts[2*i];w->input.joysticks[i].y=reply.counts[2*i+1];}
    return GS_OK;
}
static GameDemoResult play(GameWorld *w,GameServices *s,DemoPresentationKind kind,DemoPresentationKind vector){
    DemoPresentationCursor cursor=demo_presentation_begin(kind);DemoPresentationInput input={0};int16_t selection=0;uint8_t trigger=0;
    for(unsigned budget=0;budget<2000000;budget++){
        input.fade_level=w->run.fade_level;input.fade_step=w->run.fade_step;input.exit_code=w->demo_exit;input.water_y=w->run.water_y;
        DemoPresentationAction action=demo_presentation_next(&cursor,&input);GSStatus status=GS_OK;
        switch(action.kind){
        case DP_ACTION_EXIT:w->demo_exit=action.value;break;
        case DP_ACTION_LEVEL:w->run.fade_level=action.value;break;
        case DP_ACTION_STEP:w->run.fade_step=action.value;break;
        case DP_ACTION_VECTOR:vector=(DemoPresentationKind)action.value;break;
        case DP_ACTION_REVEAL_X:w->actors.slot[0].position.x32=action.value;break;
        case DP_ACTION_REPEAT:break;
        case DP_ACTION_DONE:return (GameDemoResult){GS_OK,kind==DEMO_PRESENT_RUN?(int16_t)action.value:selection};
        case DP_ACTION_SERVICE:
            switch(action.service){
            case DP_SERVICE_INITIALIZE:status=game_demo_initialize(w,s,vector);break;
            case DP_SERVICE_POLL_KEYBOARD:status=game_poll_input(w,s);input.key_word=(uint16_t)((w->input.change<<8)|(uint8_t)w->input.current_scan_storage);break;
            case DP_SERVICE_PALETTE:status=palette(w,s,&input.palette_work);break;
            case DP_SERVICE_RETRACE:status=game_video_next(w,s);break;
            case DP_SERVICE_ERASE:status=game_demo_render(w,s,0);break;
            case DP_SERVICE_WATER:status=game_demo_water(w,s);break;
            case DP_SERVICE_ADVANCE:status=game_demo_advance(w,s);break;
            case DP_SERVICE_DRAW:status=render(w,s,1,&trigger);break;
            case DP_SERVICE_SWAP:status=game_video_swap(w,s);break;
            case DP_SERVICE_TEST:input.finished=finished(w);break;
            case DP_SERVICE_JOYSTICK:status=sample(w,s,trigger);input.joystick_idle=!(w->input.joysticks[0].buttons|w->input.joysticks[1].buttons);break;
            case DP_SERVICE_PREPARE_ZERO:status=game_demo_prepare(w,s,0);break;
            case DP_SERVICE_PREPARE_NINETY:status=game_demo_prepare(w,s,1);break;
            case DP_SERVICE_MUSIC_STOP:status=game_demo_music_stop(w,s,action.value);break;
            case DP_SERVICE_MUSIC_START:status=game_demo_music_start(w,s,action.value);break;
            case DP_SERVICE_RUN:{GameDemoResult result=play(w,s,DEMO_PRESENT_RUN,vector);status=result.status;selection=result.selection;break;}
            case DP_SERVICE_REVEAL_WIDTH:status=game_demo_callback(w,s,0,(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_DEMO_EFFECT,.effect={RESOURCE_DEMO_EFFECT,DEMO_EFFECT_REVEAL_WIDTH}});break;
            default:status=GS_UNSUPPORTED;break;
            }break;
        default:status=GS_UNSUPPORTED;break;
        }
        if(status!=GS_OK)return (GameDemoResult){status,selection};
    }return (GameDemoResult){GS_OVERFLOW,selection};
}
GameDemoResult game_demo_play(GameWorld *w,GameServices *s,DemoPresentationKind kind){
    if(!w||!s||!w->demo_resources.ready)return (GameDemoResult){GS_INVALID,0};
    if(kind<DEMO_PRESENT_REVEAL||kind>DEMO_PRESENT_COMPLETION)return (GameDemoResult){GS_UNSUPPORTED,0};
    return play(w,s,kind,kind);
}
