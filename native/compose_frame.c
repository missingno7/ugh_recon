#include "compose_frame.h"
#include "compose_objects.h"
#include "compose_enemies.h"
#include "compose_front_end.h"
#include "compose_demo.h"
#include "game_startup.h"
#include "actor_render.h"
#include "render_primitives.h"
#include "player_physics.h"
#include "water_weather.h"
#include "hud.h"
#include "decimal.h"
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
static GSStatus control(GameServices *s,GSVideoRoute route,uint8_t v){return s->video.control_write(s->video_context,route,v);}
static GSStatus restore(GameWorld *w,GameServices *s,uint16_t sprite,uint16_t x,uint16_t y){
    unsigned index=render_restore_sprite_index(sprite)/4u;
    if(index>=RESOURCE_SPRITE_RECORDS)return GS_UNSUPPORTED;
    RenderRectangleSpec r=render_sprite_rectangle(x,y,w->sprite_catalog.sprites[index].dimensions);
    return game_front_restore(w,s,(FrontRectangle){r.x,r.y,r.width,r.height});
}
static GSStatus actors_render(GameWorld *w,GameServices *s,ActorRenderOperation operation){
    for(size_t i=0;i<ACTOR_CAPACITY;i++){
        if(w->session.actor_end[i])return GS_OK;
        GameActorSlot *a=w->actors.slot+i;ActorRenderStorage storage={0};storage.slots[i]=a->history;
        ActorRenderInput input={a->position,a->sprite,a->overlay_sprite};
        ActorRenderResult result=actor_render_apply(operation,&storage,i,&input);
        for(size_t j=0;j<result.count;j++){
            ActorRenderEvent e=result.events[j];
            if(e.kind==ACTOR_RENDER_DRAW)TRY(game_front_sprite_draw(w,s,e.sprite,e.x,e.y));
            else if(e.kind==ACTOR_RENDER_RESTORE)TRY(restore(w,s,e.sprite,e.x,e.y));
            else switch(e.field){
            case ACTOR_RENDER_PIXEL_X:a->history.pixel_x=e.value;break;
            case ACTOR_RENDER_PIXEL_Y:a->history.pixel_y=e.value;break;
            case ACTOR_RENDER_PREVIOUS_X:a->history.previous_x=e.value;break;
            case ACTOR_RENDER_PREVIOUS_Y:a->history.previous_y=e.value;break;
            case ACTOR_RENDER_ERASE_SPRITE:a->history.erase_sprite=e.value;break;
            case ACTOR_RENDER_ERASE_OVERLAY:a->history.erase_overlay_sprite=e.value;break;
            case ACTOR_RENDER_CURRENT_SPRITE:a->sprite=e.value;break;
            }
        }
    }return GS_UNSUPPORTED;
}
static GSStatus items_render(GameWorld *w,GameServices *s,int draw){
    for(unsigned n=12;n;n--){
        NativeItemSlot *a=w->items.slot+n-1;
        SessionRenderView view={{a->x32,a->y32},a->sprite,a->erase_sprite,a->draw_x,a->draw_y,a->previous_x,a->previous_y};
        SessionRenderResult r=draw?session_draw_layer(view,1):session_erase_layer(view);
        if(r.store_erase)a->erase_sprite=r.erase_sprite;
        if(r.store_position){a->previous_x=r.previous_x;a->previous_y=r.previous_y;a->draw_x=r.pixel_x;a->draw_y=r.pixel_y;}
        if(r.restore)TRY(restore(w,s,r.sprite,r.x,r.y));
        if(r.draw)TRY(game_front_sprite_draw(w,s,r.sprite,r.x,r.y));
    }return GS_OK;
}
static GSStatus player_render(GameWorld *w,GameServices *s,unsigned i,int draw){
    if(i>=2)return GS_UNSUPPORTED;
    NativePlayer *p=w->session.players.player+i;
    if(!draw){
        RenderDrawRequest r=render_player_restore((RenderPlayerCache){p->cached_sprite,p->cached_x,p->cached_y});
        if(r.draw)TRY(restore(w,s,r.sprite,r.x,r.y));
        p->cached_sprite=p->sprite;p->cached_x=p->pixel_x;p->cached_y=p->pixel_y;
    }else{
        const SessionFrameSpec *spec=session_data_frame();
        RenderAnimationResult r=render_player_animation((RenderPlayerAnimation){p->animation,p->sprite,spec->cycle_start[i],spec->cycle_end[i],p->thrust,p->pixel_x,p->pixel_y});
        p->animation=r.countdown;p->sprite=r.sprite;
        if(r.request.draw)TRY(game_front_sprite_draw(w,s,r.request.sprite,r.request.x,r.request.y));
    }return GS_OK;
}
static void physics_store(GameWorld *w,NativePlayer *p,PlayerPhysicsEvent e){
    switch(e.field){
    case PF_TIMER:w->run.timer=e.value;break;case PF_IMPACT:p->impact=e.value;break;
    case PF_THRUST:p->thrust=e.value;break;case PF_VX:p->velocity_x=e.value;break;
    case PF_VY:p->velocity_y=e.value;break;case PF_X:p->fixed_x=e.value;break;
    case PF_PIXEL_X:p->pixel_x=e.value;break;case PF_PLATFORM:p->platform=e.value;break;
    case PF_Y:p->fixed_y=e.value;break;case PF_PIXEL_Y:p->pixel_y=e.value;break;
    case PF_FADE_RATE:w->run.fade_step=e.value;break;case PF_FADE_LEVEL:w->run.fade_level=e.value;break;
    }
}
static GSStatus move(GameWorld *w,GameServices *s,unsigned i){
    if(i>=2||w->run.configuration.difficulty>=3)return GS_UNSUPPORTED;
    NativePlayer *p=w->session.players.player+i;LevelPlatform platforms[10];size_t count=0;
    for(;count<10;count++){
        NativePlatform *a=w->session.platforms.slot+count;
        platforms[count]=(LevelPlatform){.left=a->left,.right=a->right,.surface_y=a->height};
        if((int16_t)a->left<0){count++;break;}
    }
    if(count==10&&(int16_t)platforms[9].left>=0)return GS_UNSUPPORTED;
    PlayerPhysicsView view={{p->fixed_x,p->fixed_y},p->pixel_x,p->pixel_y,p->platform,p->velocity_x,p->velocity_y,p->impact,p->thrust,p->left,p->right,p->up,p->down};
    PlayerPhysicsWorld world={w->run.timer,w->run.water_y,session_data_frame()->impact_limit[w->run.configuration.difficulty],w->run.fade_step,w->run.fade_level,w->run.record.rain,platforms,count};
    PlayerPhysicsProcess process;player_physics_begin(&process,&view,&world);
    for(;;){
        PlayerPhysicsEvent e=player_physics_poll(&process);if(process.failed)return GS_UNSUPPORTED;
        switch(e.kind){
        case PP_WRITE:physics_store(w,p,e);break;
        case PP_SELECT_PLANE_REGISTER:TRY(control(s,GS_GC_INDEX,(uint8_t)e.value));break;
        case PP_READ_PLANE:TRY(control(s,GS_GC_DATA,(uint8_t)e.value));break;
        case PP_SAMPLE:{
            uint16_t column=player_physics_sar((uint16_t)(e.probe.pixel_x+5u),2);
            uint16_t position=(uint16_t)(w->pages.background+(int32_t)(int16_t)e.probe.pixel_y*w->demo_resources.row_stride+column+e.probe.columns+e.probe.rows*96u);
            /* Four-pixel cells on the collision image's 96-cell rows. */
            static const uint16_t deltas[]={0,3,5,19u*96u,19u*96u+3u,19u*96u+5u,6u*96u,6u*96u+5u,12u*96u,12u*96u+5u};uint8_t samples[10];
            for(unsigned j=0;j<10;j++)TRY(s->video.read(s->video_context,(uint16_t)(position+deltas[j]),GS_COLLISION_READ,samples+j));
            player_physics_reply(&process,player_collision_sample(samples));break;}
        case PP_DONE:return GS_OK;
        }
    }
}
static HudValues hud_view(GameWorld *w){
    NativeHudPresentation *h=&w->presentation.hud;NativePlayer *p=w->session.players.player;
    return (HudValues){.cursor_x=h->cursor_x,.cursor_y=h->cursor_y,.lives=w->run.lives,.cached_lives=h->lives,
        .score_low=(uint16_t)w->run.score,.score_high=(uint16_t)(w->run.score>>16),.cached_score_low=h->score_words[0],.cached_score_high=h->score_words[1],
        .journeys=w->run.record.journeys,.cached_journeys=h->counter,.icon_one=p[0].carried,.cached_icon_one=h->icons[0],.icon_two=p[1].carried,.cached_icon_two=h->icons[1],
        .destination_one=p[0].destination,.destination_two=p[1].destination,.players=w->run.configuration.players,
        .fare_one=p[0].fare,.fare_two=p[1].fare,.cached_fare=h->fare,.clear_fare=h->fare_pending,
        .multiplier=w->run.multiplier,.cached_multiplier=h->multiplier,.timer=w->run.timer,.fade_step=w->run.fade_step,.fade_level=w->run.fade_level,.divisor=session_data_frame()->timer_divisor,.bar_width=h->timer_width,
        .lives_x=h->layout_x[0],.score_x=h->layout_x[1],.journeys_x=h->layout_x[2],.icon_one_x=h->layout_x[3],.destination_one_x=h->layout_x[4],.fare_x=h->layout_x[5],.multiplier_x=h->layout_x[6],.icon_two_x=h->layout_x[7],.destination_two_x=h->layout_x[8]};
}
static void hud_store(GameWorld *w,HudEffect e){
    NativeHudPresentation *h=&w->presentation.hud;
    switch(e.field){
    case HF_CURSOR_X:h->cursor_x=e.a;break;case HF_CURSOR_Y:h->cursor_y=e.a;break;
    case HF_LIVES:h->lives=(uint8_t)e.a;break;
    case HF_SCORE_LOW:w->run.score=(w->run.score&0xffff0000u)|e.a;break;
    case HF_SCORE_HIGH:w->run.score=(w->run.score&65535u)|((uint32_t)e.a<<16);break;
    case HF_CACHED_SCORE_LOW:h->score_words[0]=e.a;break;case HF_CACHED_SCORE_HIGH:h->score_words[1]=e.a;break;
    case HF_JOURNEYS:h->counter=(uint8_t)e.a;break;
    case HF_ICON_ONE:h->icons[0]=e.a;break;case HF_ICON_TWO:h->icons[1]=e.a;break;
    case HF_FARE:h->fare=e.a;break;case HF_CLEAR_FARE:h->fare_pending=(uint8_t)e.a;break;
    case HF_MULTIPLIER:h->multiplier=(uint8_t)e.a;break;case HF_TIMER:w->run.timer=e.a;break;
    case HF_FADE_STEP:w->run.fade_step=e.a;break;case HF_FADE_LEVEL:w->run.fade_level=e.a;break;
    case HF_BAR_WIDTH:h->timer_width=e.a;break;
    }
}
static GSStatus number(GameWorld *w,GameServices *s,HudEffect e){
    unsigned count=e.kind==HUD_NUMBER_TWO?2:e.kind==HUD_NUMBER_FOUR?4:6;
    TRY(game_front_digits(w,(uint32_t)e.a|((uint32_t)e.c<<16),count));
    uint8_t *d=w->front_data.divisors;DecimalDivisors divisors={d,d+1,d+2,d+4};
    DecimalOutput output={w->presentation.hud.digits[1],7,0};DecimalResult r;
    if(count==2)r=decimal_two((uint8_t)e.b,&output,divisors);
    else if(count==4)r=decimal_four(e.b,&output,divisors);
    else r=decimal_six((uint32_t)e.b|((uint32_t)e.d<<16),&output,divisors);
    if(r.status!=DECIMAL_OK)return GS_UNSUPPORTED;
    for(unsigned i=0;i<7;i++){
        NativeHudPresentation *h=&w->presentation.hud;
        HudDigitDecision decision=hud_changed_digit(w->front_data.digits[i],h->digits[1][i],h->cursor_x,(uint16_t)i);
        if(decision.done)return GS_OK;
        if(decision.draw){RenderDrawRequest draw=hud_digit(w->front_data.digits[i],h->cursor_x,h->cursor_y);TRY(game_front_sprite_draw(w,s,draw.sprite,draw.x,draw.y));}
        h->cursor_x=decision.next_x;
    }return GS_UNSUPPORTED;
}
static GSStatus bar(GameServices *s,HudEffect e){
    HudBarSpec b=hud_bar(e.a,e.b);TRY(control(s,GS_SEQ_INDEX,2));
    uint8_t mask=b.cumulative?(uint8_t)((1u<<(b.mask_index+1))-1u):(uint8_t)(1u<<b.mask_index);
    TRY(control(s,GS_SEQ_DATA,mask));
    for(unsigned row=0;row<3;row++)TRY(s->video.store(s->video_context,(uint16_t)(session_data_frame()->timer_position+hud_bar_row(b.cell,(uint8_t)row)),b.value));
    TRY(control(s,GS_SEQ_DATA,15));
    while(b.remaining){uint16_t cell=hud_bar_next(&b);for(unsigned row=0;row<3;row++)TRY(s->video.store(s->video_context,(uint16_t)(session_data_frame()->timer_position+hud_bar_row(cell,(uint8_t)row)),b.value));}
    return GS_OK;
}
static GSStatus hud(GameWorld *w,GameServices *s){
    HudStage stage=HUD_LIVES;
    while(stage!=HUD_DONE){
        HudValues v=hud_view(w);HudResult r;
        switch(stage){case HUD_LIVES:r=hud_lives(v);break;case HUD_SCORE:r=hud_score(v);break;
        case HUD_JOURNEYS:r=hud_journeys(v);break;case HUD_ICON_ONE:r=hud_icon_one(v);break;
        case HUD_ICON_TWO:r=hud_icon_two(v);break;case HUD_FARE:r=hud_fare(v);break;
        case HUD_MULTIPLIER:r=hud_multiplier(v);break;case HUD_TIMER:r=hud_timer(v);break;default:return GS_INVALID;}
        for(unsigned i=0;i<r.count;i++){
            HudEffect e=r.effects[i];switch(e.kind){
            case HUD_STORE:hud_store(w,e);break;
            case HUD_NUMBER_TWO:case HUD_NUMBER_FOUR:case HUD_NUMBER_SIX:TRY(number(w,s,e));break;
            case HUD_SPRITE:TRY(game_front_sprite_draw(w,s,e.a,e.b,e.c));break;
            case HUD_BAR:TRY(bar(s,e));break;case HUD_DIVISION_ERROR:return GS_UNSUPPORTED;
            }
        }stage=r.next;
    }return GS_OK;
}
static void weather_store(GameWorld *w,WeatherAction e){
    NativeWeatherPresentation *p=&w->presentation.weather;
    switch(e.field){case WW_FIXED_Y:w->run.record.water_fixed=e.value;break;case WW_SURFACE_Y:w->run.water_y=e.value;break;
    case WW_PREVIOUS_Y:p->previous_y=e.value;break;case WW_BYTE_POSITION:p->byte_offset=e.value;break;
    case WW_FRAME:p->frame=e.value;break;case WW_COUNTDOWN:p->countdown=(uint8_t)e.value;break;
    case WW_PHASE:p->phase=(uint8_t)e.value;break;case WW_PENDING:p->pending=(uint8_t)e.value;break;default:break;}
}
static GSStatus water_advance(GameWorld *w,GameServices *s){
    NativeWeatherPresentation *p=&w->presentation.weather;
    WaterWeatherState state={w->run.record.water_fixed,w->run.water_y,p->previous_y,p->byte_offset,p->frame,p->countdown,p->phase,p->pending};
    WeatherResult r=water_weather_advance(&state,(WaterWeatherInputs){.increment=w->run.record.water_step,.row_stride=w->demo_resources.row_stride});
    for(size_t i=0;i<r.count;i++){
        WeatherAction e=r.actions[i];
        if(e.kind==WW_STORE)weather_store(w,e);
        else if(e.kind==WW_MARK_ROW){
            TRY(control(s,GS_GC_INDEX,8));TRY(control(s,GS_GC_DATA,64));TRY(control(s,GS_GC_INDEX,3));TRY(control(s,GS_GC_DATA,16));
            for(unsigned n=80;n;n--){uint8_t reply;TRY(s->video.water_mark(s->video_context,(uint16_t)(w->pages.background+e.position+n-1),&reply));}
            TRY(control(s,GS_GC_INDEX,8));TRY(control(s,GS_GC_DATA,255));TRY(control(s,GS_GC_INDEX,3));TRY(control(s,GS_GC_DATA,0));
            r=water_weather_marked(&state);i=(size_t)-1;
        }else if(e.kind==WW_RESTORE_ROW)TRY(game_front_restore(w,s,(FrontRectangle){0,e.value,320,1}));
        else return GS_INVALID;
    }return GS_OK;
}
static GSStatus rain(GameWorld *w,GameServices *s,SessionAction action){
    int advance=action==SESSION_ADVANCE_RAIN,draw=action==SESSION_DRAW_RAIN;
    uint16_t index=weather_first_particle(w->run.water_y,!draw);if(index>=386)return GS_UNSUPPORTED;
    if(draw){TRY(control(s,GS_SEQ_INDEX,2));}
    else if(!advance){TRY(control(s,GS_GC_INDEX,8));TRY(control(s,GS_GC_DATA,0));}
    do{
        NativeRainRecord *r=w->presentation.weather.rain+index/2u;WeatherParticle p={r->position,r->previous,r->modulo};
        if(advance){
            WeatherResult result=weather_particle_advance(&p,w->presentation.weather.byte_offset,w->run.record.rain,!!(index&2));r->previous=p.previous;
            if(result.actions[result.count-1].kind==WW_RESPAWN){uint16_t value=random_next_below(&w->random,weather_random_bound(w->run.water_y));weather_particle_spawn(&p,value,(WaterWeatherInputs){.row_stride=w->demo_resources.row_stride,.direction=w->run.record.rain});}
            r->position=p.position;r->modulo=p.modulo_four;
        }else if(draw){
            WeatherResult result=weather_particle_draw(&p);TRY(control(s,GS_SEQ_DATA,(uint8_t)result.actions[0].value));
            TRY(s->video.store(s->video_context,(uint16_t)(w->pages.draw+result.actions[1].position),(uint8_t)result.actions[1].value));
        }else{WeatherResult result=weather_particle_restore(&p);uint8_t reply;uint16_t at=result.actions[0].position;TRY(s->video.copy(s->video_context,(uint16_t)(w->pages.background+at),(uint16_t)(w->pages.draw+at),&reply));}
        index=weather_previous_particle(index);
    }while(weather_more_particles(index));
    if(draw)return control(s,GS_SEQ_DATA,15);
    if(!advance)return control(s,GS_GC_DATA,255);
    return GS_OK;
}
static GSStatus controls(GameWorld *w,GameServices *s){
    TRY(game_poll_input(w,s));
    if(input_controls_need_sample(w->run.configuration.control_mode[0],w->run.configuration.control_mode[1],w->run.configuration.players))TRY(game_sample_input_trigger(w,s,(uint8_t)w->input.current_scan_storage));
    for(unsigned i=0;i<input_player_visits(w->run.configuration.players);i++){
        InputControlSource source=input_control_source(w->run.configuration.control_mode[i]);
        if(source.joystick){
            if(source.position>2||(source.position&1u))return GS_UNSUPPORTED;
            NativePlayer *p=w->session.players.player+i;InputCommands c=input_control_map(w->input.joysticks+source.position/2u);
            p->up=c.up;p->down=c.down;p->left=c.left;p->right=c.right;p->action=c.action;
        }
    }return GS_OK;
}
GSStatus game_frame_execute(GameWorld *w,GameServices *s,SessionRequest e,uint16_t *palette){
    if(!w||!s||!palette)return GS_INVALID;
    switch(e.action){
    case SESSION_FADE_UPLOAD:{
        VideoClearCursor c=video_scale_begin();do{w->palette.faded[c.position]=video_palette_scale(w->palette.base[c.position],e.value).value;video_scale_advance(&c);}while(c.remaining);
        TRY(game_video_next(w,s));TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_SELECT,0}));VideoPaletteRange range=video_palette_range(0,0,216,0);
        do{for(unsigned j=0;j<3;j++)TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_COMPONENT,w->palette.faded[video_palette_advance(&range)]}));}while(--range.entries);
        *palette=e.value;return GS_OK;}
    case SESSION_FADE_ADVANCE:w->run.fade_level=e.value;return GS_OK;
    case SESSION_WAIT_RETRACE:return game_video_next(w,s);
    case SESSION_HUD:return hud(w,s);
    case SESSION_ERASE_PLAYER_BEGIN:case SESSION_ERASE_PLAYER_NEXT:case SESSION_MOVE_BEGIN:case SESSION_MOVE_NEXT:case SESSION_DRAW_PLAYER_BEGIN:case SESSION_DRAW_PLAYER_NEXT:return GS_OK;
    case SESSION_ERASE_PLAYER:case SESSION_DRAW_PLAYER:case SESSION_MOVE_PLAYER:
        if(e.index&1u)return GS_UNSUPPORTED;
        return e.action==SESSION_MOVE_PLAYER?move(w,s,e.index/2u):player_render(w,s,e.index/2u,e.action==SESSION_DRAW_PLAYER);
    case SESSION_ERASE_ACTORS:return actors_render(w,s,ACTOR_RENDER_GAME_ERASE);
    case SESSION_ERASE_ENEMIES:return game_enemies_erase(w,s);
    case SESSION_ERASE_ITEMS:return items_render(w,s,0);
    case SESSION_RESTORE_RAIN:case SESSION_ADVANCE_RAIN:case SESSION_DRAW_RAIN:return rain(w,s,e.action);
    case SESSION_ADVANCE_WATER:return water_advance(w,s);
    case SESSION_IO_POINT:return s->input.pump(s->input_context,GS_INPUT_WAIT);
    case SESSION_POLL_CONTROLS:return controls(w,s);
    case SESSION_PAUSE_RELEASE:case SESSION_PAUSE_MAKE:case SESSION_PAUSE_BREAK:return game_poll_input(w,s);
    case SESSION_ESCAPE:
        if(e.decision){w->run.lives=0;if(e.index){w->run.fade_step=e.other;w->run.fade_level=e.value;}}return GS_OK;
    case SESSION_UPDATE_ACTORS:return game_actors_update(w,s);
    case SESSION_UPDATE_ENEMIES:return game_enemies_update(w,s);
    case SESSION_UPDATE_ITEMS:return game_items_update(w,s);
    case SESSION_DRAW_ACTORS:return actors_render(w,s,ACTOR_RENDER_GAME_DRAW);
    case SESSION_DRAW_ENEMIES_BACK:return game_enemies_draw_back(w,s);
    case SESSION_DRAW_ENEMIES_FRONT:return game_enemies_draw_front(w,s);
    case SESSION_DRAW_ITEMS:return items_render(w,s,1);
    case SESSION_DRAW_OVERLAYS:return actors_render(w,s,ACTOR_RENDER_GAME_OVERLAY);
    case SESSION_DRAW_WATER:return game_demo_water(w,s);
    case SESSION_SWAP_PAGE:return game_video_swap(w,s);
    default:return GS_UNSUPPORTED;
    }
}
