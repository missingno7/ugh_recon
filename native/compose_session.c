#include "compose_session.h"
#include "compose_demo.h"
#include "compose_front_end.h"
#include "compose_audio.h"
#include "game_startup.h"
#include "coordinate_scale.h"
#include "water_weather.h"
#include "render_primitives.h"
#include "hud.h"
#include "ice.h"
#include <string.h>
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
static uint16_t word(const uint8_t *p){return (uint16_t)(p[0]|(uint16_t)p[1]<<8);}
static uint16_t pixel(uint16_t v){return (uint16_t)((v>>5)|((v&32768u)?63488u:0));}
static uint16_t scale_y(GameWorld *w,uint16_t v){CoordinateScale r=scale_level_y(v);w->session.scale_scratch=r.removed_fraction;return r.value;}
static uint16_t scale_speed(GameWorld *w,uint16_t v){CoordinateScale r=scale_level_speed(v);w->session.scale_scratch=r.removed_fraction;return r.value;}
GSStatus game_session_password(GameWorld *w,GameServices *s,uint16_t *level){
    if(!w||!s||!level)return GS_INVALID;
    GSBytes list;TRY(session_data_passwords(s,w->run.configuration.player_bytes,&list));
    SessionPassword p;session_password_begin(&p);size_t at=0;
    for(;;){
        session_password_candidate(&p);
        for(;;){
            if(at>=list.size)return GS_UNSUPPORTED;
            uint8_t ch=list.data[at++];SessionPasswordResult decision=session_password_byte(ch);
            if(decision==PASSWORD_DEFAULT){*level=session_password_selected(&p,1);return GS_OK;}
            if(decision==PASSWORD_END)break;
            if(p.length>=20)return GS_UNSUPPORTED;
            session_password_compare(&p,ch,w->front.password[p.length]);
        }
        if(!session_password_has_misses(&p)){
            while(session_password_needs_padding(&p)&&session_password_padding(&p,w->front.password[p.length])){}
            if(!session_password_needs_padding(&p)){*level=session_password_selected(&p,0);return GS_OK;}
        }
        session_password_reject(&p);
    }
}
/* Only the typed identities generated from the admitted DATA graph are stored.
 * The list's transport words are skipped; no code word is decoded at runtime. */
static GSStatus load_store(GameWorld *w,const SessionLevelSpec *l,SessionLoadFamily family,
    SessionLoadRequest e,unsigned n){
    uint16_t v=e.value;
    if(family==LOAD_PLATFORMS){
        if(n>=10)return GS_UNSUPPORTED;
        NativePlatform *p=w->session.platforms.slot+n;
        switch(e.field){
        case LF_PLATFORM_LEFT:p->left=v;break;case LF_PLATFORM_RIGHT:p->right=v;break;
        case LF_PLATFORM_HEIGHT:p->height=v;break;case LF_PLATFORM_ARRIVAL:p->arrival=v;break;
        case LF_PLATFORM_WAIT:p->wait=v;break;case LF_PLATFORM_SPAWN:p->spawn=v;break;
        case LF_PLATFORM_ICON:p->icon=v;break;case LF_PLATFORM_OCCUPANT:p->occupant=v;break;
        default:return GS_INVALID;
        }return GS_OK;
    }
    if(family==LOAD_ACTORS){
        if(n>=16)return GS_UNSUPPORTED;
        GameActorSlot *a=w->actors.slot+n;
        switch(e.field){
        case LF_ACTOR_DESCRIPTOR:
            w->session.actor_end[n]=(uint8_t)(v==65535);
            a->descriptor=v==65535?(ObjectResourceIdentity){0}:l->actor[n].descriptor;break;
        case LF_ACTOR_PLATFORM:a->initial_platform=v;break;
        case LF_ACTOR_JOURNEY:a->journey=l->actor[n].journey;break;
        case LF_ACTOR_SPRITE:a->sprite=v;break;case LF_ACTOR_ERASE:a->history.erase_sprite=v;break;
        case LF_ACTOR_OVERLAY:a->overlay_sprite=v;break;case LF_ACTOR_ERASE_OVERLAY:a->history.erase_overlay_sprite=v;break;
        case LF_ACTOR_CALLBACK:a->callback=l->actor[n].callback;a->demo=0;break;
        case LF_ACTOR_X:a->position.x32=v;break;case LF_ACTOR_Y:a->position.y32=v;break;
        default:return GS_INVALID;
        }return GS_OK;
    }
    if(n>=5)return GS_UNSUPPORTED;
    NativeEnemySlot *a=w->enemies.slot+n;
    switch(e.field){
    case LF_ENEMY_DESCRIPTOR:w->session.enemy_end[n]=(uint8_t)(v==65535);w->session.enemy_descriptor[n]=v==65535?(ObjectResourceIdentity){0}:l->enemy[n].descriptor;break;
    case LF_ENEMY_PLATFORM:a->platform=v;break;case LF_ENEMY_X:a->x32=v;break;case LF_ENEMY_Y:a->y32=v;break;
    case LF_ENEMY_LIST:w->session.enemy_list[n]=l->enemy[n].list;break;
    case LF_ENEMY_DELAY:a->initial_delay=v;break;case LF_ENEMY_SPEED:a->speed=v;break;
    case LF_ENEMY_DIRECTION:a->direction_or_target_word=v;break;
    default:return GS_INVALID;
    }return GS_OK;
}
static GSStatus load_list(GameWorld *w,GameServices *s,const SessionLevelSpec *l,SessionLoadFamily family){
    SessionDataView view=family==LOAD_PLATFORMS?l->platforms:family==LOAD_ACTORS?l->actors:l->enemies;
    GSBytes b;TRY(session_data_view(s,view,&b));size_t at=0;
    for(unsigned n=0;n<(family==LOAD_PLATFORMS?10u:family==LOAD_ACTORS?16u:5u);n++){
        SessionLoadRecord r;session_load_begin(&r,family,(uint16_t)(n*2u));
        SessionLoadClass kind=LOAD_ORDINARY;
        for(;;){
            SessionLoadRequest e=session_load_next(&r);uint16_t reply=0;
            switch(e.action){
            case LOAD_READ_LIST:
                if(at+2>b.size)return GS_UNSUPPORTED;
                reply=word(b.data+at);at+=2;
                if(!r.cursor&&family!=LOAD_PLATFORMS){
                    unsigned count=family==LOAD_ACTORS?l->actor_count:l->enemy_count;
                    /* Admission rejects a changed list extent at its consumed
                     * read. Nonterminal identity words are never interpreted. */
                    if((reply==65535)!=(n==count))return GS_UNSUPPORTED;
                    if(n<count)kind=family==LOAD_ACTORS?l->actor[n].kind:l->enemy[n].kind;
                    reply=n==count?65535:0;
                }else if((family==LOAD_ACTORS&&r.cursor==4)||(family==LOAD_ENEMIES&&kind==LOAD_TREE&&r.cursor==8))reply=0;
                break;
            case LOAD_READ_DESCRIPTOR:reply=0;break; /* typed callback published below */
            case LOAD_READ_SPAWN:case LOAD_READ_HEIGHT:
                if(r.platform>=10)return GS_UNSUPPORTED;
                reply=e.action==LOAD_READ_SPAWN?w->session.platforms.slot[r.platform].spawn:w->session.platforms.slot[r.platform].height;break;
            case LOAD_READ_REPEAT:if(at<2||at>b.size)return GS_UNSUPPORTED;reply=word(b.data+at-2);break;
            case LOAD_SCALE_Y:reply=scale_y(w,e.value);break;
            case LOAD_SCALE_SPEED:reply=scale_speed(w,e.value);break;
            case LOAD_SKIP:if(e.value>b.size-at)return GS_UNSUPPORTED;at+=e.value;break;
            case LOAD_STORE:TRY(load_store(w,l,family,e,n));break;
            case LOAD_CALLBACK:w->session.enemy_callback[n]=l->enemy[n].callback;break;
            case LOAD_END:break;
            default:return GS_INVALID;
            }
            if(!session_load_accept(&r,e.action,reply,kind))return GS_INVALID;
            if(e.action==LOAD_END){if(r.list_end)return GS_OK;break;}
        }
    }return GS_UNSUPPORTED;
}
static void spawn_rain(GameWorld *w,unsigned n){
    NativeRainRecord *r=w->presentation.weather.rain+n;WeatherParticle p={r->position,r->previous,r->modulo};
    uint16_t value=random_next_below(&w->random,weather_random_bound(w->run.water_y));
    weather_particle_spawn(&p,value,(WaterWeatherInputs){.row_stride=w->demo_resources.row_stride,.direction=w->run.record.rain});
    r->position=p.position;r->modulo=p.modulo_four;
}
static GSStatus advance_rain(GameWorld *w){
    uint16_t index=weather_first_particle(w->run.water_y,1);
    if(index>=386)return GS_UNSUPPORTED;
    do{
        NativeRainRecord *r=w->presentation.weather.rain+index/2u;WeatherParticle p={r->position,r->previous,r->modulo};
        WeatherResult result=weather_particle_advance(&p,w->presentation.weather.byte_offset,w->run.record.rain,!!(index&2));
        r->previous=p.previous;
        if(result.count>1&&result.actions[1].kind==WW_RESPAWN)spawn_rain(w,index/2u);
        else{r->position=p.position;r->modulo=p.modulo_four;}
        index=weather_previous_particle(index);
    }while(weather_more_particles(index));return GS_OK;
}
/* Word publications run from byte 24 down to zero. Pointer transports are
 * represented by the selected typed level spec; all scalar fields remain live. */
static void record_store(GameWorld *w,unsigned at,uint8_t v){
    LevelRuntimeRecord *r=&w->run.record;
    if(at==8)r->journeys=v;else if(at==9)r->reserved_before_text=v;
    else if(at==12)r->rain=v;else if(at==25)r->reserved_tail=v;
    else{
        uint16_t *field=at<2?&r->map.value:at>=13&&at<21?&r->player_start[(at-13)/4][((at-13)%4)/2]:at>=21&&at<23?&r->water_fixed:at>=23&&at<25?&r->water_step:0;
        if(field){unsigned shift=at<2?at*8u:((at-13u)&1u)*8u;*field=(uint16_t)((*field&~(255u<<shift))|((uint16_t)v<<shift));}
    }
}
GSStatus game_session_load(GameWorld *w,GameServices *s){
    if(!w||!s||!w->session.ready)return GS_INVALID;
    const SessionLevelSpec *l;TRY(session_data_level(w->run.configuration.players,w->run.level,&l));
    GSBytes b;TRY(session_data_view(s,l->record,&b));
    for(uint16_t at=24;;at=session_record_previous(at)){
        record_store(w,at,b.data[at]);record_store(w,at+1u,b.data[at+1u]);if(!at)break;
    }
    w->session.level=l;w->front_data.renderer_water=w->run.record.map.value;
    GSBytes maps;TRY(session_data_maps(s,&maps));IceResult decoded;
    if(ice_decode(maps.data,maps.size,w->scratch,sizeof w->scratch,&decoded)!=ICE_OK)return GS_INVALID;
    uint16_t source=w->run.record.map.value,destination=0,remaining=160;
    do{if(source+1u>=decoded.bytes_written||destination+1u>=320)return GS_UNSUPPORTED;
        w->run.tiles[destination]=w->scratch[source];w->run.tiles[destination+1]=w->scratch[source+1];
        source=session_copy_next(source,0);destination=session_copy_next(destination,0);remaining--;
    }while(session_count_more(remaining));
    for(unsigned i=0;i<2;i++){
        NativePlayer *p=w->session.players.player+i;
        SessionPlayerSeed x=session_player_x(w->run.record.player_start[i][0]);
        p->fixed_x=x.fixed;p->pixel_x=x.pixel;p->cached_x=x.pixel;
        SessionPlayerSeed y=session_player_y(scale_y(w,w->run.record.player_start[i][1]));
        p->fixed_y=y.fixed;p->pixel_y=y.pixel;p->cached_y=y.pixel;
    }
    /* Original order is field-major, including the dormant second record. */
    for(unsigned i=0;i<2;i++)w->session.players.player[i].platform=65535;
    for(unsigned i=0;i<2;i++)w->session.players.player[i].animation=65535;
    w->session.players.player[0].sprite=218;w->session.players.player[1].sprite=224;
    w->presentation.hud.icons[0]=w->presentation.hud.icons[1]=65535;w->presentation.hud.fare_pending=255;
    for(unsigned i=0;i<2;i++)w->session.players.player[i].carried=0;
    for(unsigned i=0;i<2;i++)w->session.players.player[i].destination=0;
    for(unsigned i=0;i<2;i++)w->session.players.player[i].fare=0;
    for(unsigned i=0;i<2;i++)w->session.players.player[i].velocity_x=0;
    for(unsigned i=0;i<2;i++)w->session.players.player[i].velocity_y=0;
    w->run.record.water_fixed=session_water_cap(scale_y(w,w->run.record.water_fixed));
    w->run.water_y=pixel(w->run.record.water_fixed);w->presentation.weather.previous_y=w->run.water_y;
    TRY(load_list(w,s,l,LOAD_PLATFORMS));TRY(load_list(w,s,l,LOAD_ACTORS));TRY(load_list(w,s,l,LOAD_ENEMIES));
    for(uint16_t i=384;;i=session_record_previous(i)){
        w->presentation.weather.rain[i/2u].position=0;w->presentation.weather.rain[i/2u].previous=0;if(!i)break;
    }
    if(session_rain_enabled(w->run.record.rain)){
        for(uint16_t i=384;;i=session_record_previous(i)){spawn_rain(w,i/2u);if(!i)break;}
        for(uint16_t i=576;;i=session_prewarm_previous(i)){TRY(advance_rain(w));if(!i)break;}
    }return GS_OK;
}
static void clear_workspace(GameWorld *w){
    w->session.scale_scratch=0;w->demo_exit=0;memset(w->run.tiles,0,320);
    for(unsigned i=0;i<2;i++){
        NativePlayer *p=w->session.players.player+i;p->up=p->down=p->left=p->right=p->action=0;
    }
    NativeHudPresentation *h=&w->presentation.hud;
    h->timer_width=h->cursor_x=h->cursor_y=0;memset(h->layout_x,0,sizeof h->layout_x);
    h->score_words[0]=h->score_words[1]=h->fare=h->retained_seed=0;
    h->multiplier=h->lives=h->counter=h->fare_pending=0;
    w->presentation.weather.pending=w->presentation.weather.countdown=w->presentation.weather.phase=0;
    w->presentation.weather.frame=0;w->run.fade_level=w->run.fade_step=0;w->run.completion=0;
}
static GSStatus black(GameWorld *w,GameServices *s){
    TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_SELECT,0}));
    for(unsigned i=0;i<video_blackening_batches();i++){
        TRY(game_video_next(w,s));for(unsigned j=0;j<3*video_blackening_entries();j++)TRY(s->video.dac(s->video_context,(GSDacWrite){GS_DAC_COMPONENT,0}));
    }return GS_OK;
}
GSStatus game_session_initialize(GameWorld *w,GameServices *s,unsigned *stage){
    if(!w||!s||!stage||!w->session.ready)return GS_INVALID;
    *stage=0;clear_workspace(w);w->run.timer=0x5a3b;w->presentation.hud.retained_seed=65535;w->run.fade_step=2;
    NativeHudPresentation *h=&w->presentation.hud;
    h->lives=session_display_byte(w->run.lives);h->multiplier=session_display_byte(w->run.multiplier);
    h->counter=99;h->fare=9999;uint32_t score=session_display_score(w->run.score);
    h->score_words[0]=(uint16_t)score;h->score_words[1]=(uint16_t)(score>>16);h->cursor_y=194;
    /* layout indices follow their physical owner's order (icon before target). */
    static const unsigned fields[]={0,1,2,4,3,5,6,7,8};
    for(unsigned i=0;i<(w->run.configuration.players==2?9u:7u);i++)h->layout_x[i]=session_display_layout(w->run.configuration.players,fields[i]);
    SessionDisplayProcess p;session_display_begin(&p);
    for(;;){
        *stage=session_display_next(&p);
        switch(*stage){
        case 0:TRY(game_session_load(w,s));break;
        case 1:{GSBytes text,password;TRY(session_data_view(s,w->session.level->introduction,&text));
            TRY(session_data_password(s,w->run.configuration.player_bytes,(uint8_t)w->run.level,&password));
            TRY(game_front_introduction(w,s,text,password));break;}
        case 2:TRY(game_clear_video(w,s));break;
        case 3:TRY(black(w,s));break;
        case 4:{VideoCopyCursor c=video_duplicate_begin(0,0,0);do{VideoDuplicateTransfer t=video_duplicate_transfer(&c);for(unsigned j=0;j<2;j++){
            w->palette.base[t.destinations[j]]=w->front_data.source_palette[t.source];w->palette.base[t.destinations[j]+1]=w->front_data.source_palette[t.source+1];
        }video_duplicate_advance(&c);}while(c.remaining);break;}
        case 5:for(unsigned i=0;i<320;i++){RenderDrawRequest t=render_map_cell((uint16_t)i,w->run.tiles[i]);TRY(game_front_sprite_draw(w,s,t.sprite,t.x,t.y));}break;
        case 6:TRY(game_front_save_background(w,s));break;
        case 7:TRY(game_video_swap(w,s));break;
        case 8:TRY(game_front_restore(w,s,(FrontRectangle){0,0,320,w->pages.height}));break;
        case 9:for(unsigned i=0;i<2;i++){RenderDrawRequest t=hud_border(w->run.configuration.players,(uint8_t)i);TRY(game_front_sprite_draw(w,s,t.sprite,t.x,t.y));}break;
        /* Typed gameplay peers are deliberately a closed boundary until their
         * direct native continuations are composed. Never call a bridge. */
        case 10:if(!w->session.enemy_end[0])return GS_UNSUPPORTED;break;
        case 11:if(!w->session.actor_end[0])return GS_UNSUPPORTED;break;
        case 12:TRY(game_demo_reset(w));break;
        case 13:return session_display_complete(&p)?GS_OK:GS_INVALID;
        default:return GS_INVALID;
        }
        if(!session_display_consume(&p,*stage))return GS_INVALID;
    }
}
static SessionWorld observe(GameWorld *w,uint16_t password,uint16_t palette){
    return (SessionWorld){.fade_level=w->run.fade_level,.fade_rate=w->run.fade_step,.palette_reply=palette,
        .player_bytes=w->run.configuration.player_bytes,.player_count=w->run.configuration.players,.level=w->run.level,
        .level_limit=session_data_count(w->run.configuration.player_bytes),.password_reply=password,
        .lives=w->run.lives,.completion=w->run.completion,.rain=w->run.record.rain,.scan=(uint8_t)w->input.current_scan_storage};
}
GameSessionResult game_session_run(GameWorld *w,GameServices *s,GameSessionEntry entry){
    GameSessionResult result={GAME_SESSION_SERVICE_ERROR,GS_INVALID,SESSION_INVALID,0,0};
    if(!w||!s||!w->session.ready)return result;
    if(entry!=GAME_SESSION_PASSWORD){result.kind=GAME_SESSION_UNSUPPORTED;result.status=GS_UNSUPPORTED;return result;}
    SessionProcess p;session_begin(&p);uint16_t password=0,palette=0;
    for(;;){
        SessionRequest e=session_next(&p,observe(w,password,palette));GSStatus status=GS_OK;result.action=e.action;
        switch(e.action){
        case SESSION_PASSWORD:status=game_session_password(w,s,&password);break;
        case SESSION_SELECT_LEVEL:w->run.level=e.value;break;
        case SESSION_PREGAME:status=game_demo_play(w,s,DEMO_PRESENT_PREGAME).status;break;
        case SESSION_STOP_INITIAL_MUSIC:case SESSION_STOP_LEVEL_MUSIC:status=game_audio_music_stop(w,s,e.value).status;break;
        case SESSION_RESET_GAME:w->run.lives=(uint8_t)session_reset_value(0);w->run.multiplier=(uint8_t)session_reset_value(1);w->run.score=0;break;
        case SESSION_BLACK_PALETTE:status=black(w,s);break;
        case SESSION_INITIALIZE_LEVEL:status=game_session_initialize(w,s,&result.display_stage);break;
        case SESSION_DECREMENT_LIVES:w->run.lives=(uint8_t)e.value;break;
        case SESSION_RESET_MULTIPLIER:w->run.multiplier=(uint8_t)e.value;break;
        case SESSION_INCREMENT_LEVEL:w->run.level=e.value;break;
        case SESSION_TEST_LEVEL_LIMIT:case SESSION_OUTCOME:case SESSION_RETURN:break;
        case SESSION_FINISHED:result.kind=GAME_SESSION_RETURNED;result.status=GS_OK;return result;
        default:status=GS_UNSUPPORTED;break;
        }
        result.completed_frames=p.completed_frames;
        if(status!=GS_OK){result.status=status;result.kind=status==GS_UNSUPPORTED?GAME_SESSION_UNSUPPORTED:status==GS_QUIT?GAME_SESSION_QUIT:GAME_SESSION_SERVICE_ERROR;return result;}
        if(!session_acknowledge(&p,e.action,observe(w,password,palette))){result.status=GS_INVALID;return result;}
        /* No frame guard here: the verification host's 100000-frame bound is
         * not a game timeout. Future frame execution continues this process. */
    }
}
