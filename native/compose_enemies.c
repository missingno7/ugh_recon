#include "compose_enemies.h"
#include "compose_objects.h"
#include "compose_audio.h"
#include "compose_front_end.h"
#include "game_object_data.h"
#include "render_primitives.h"
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
static uint16_t pixel(uint16_t v){return (uint16_t)((v>>5)|((v&32768u)?63488u:0));}
static int signed_word(uint16_t v){return v<32768u?(int)v:(int)v-65536;}
static GSStatus resource_link(ObjectResourceIdentity id,uint16_t member,ObjectResourceIdentity *out){
    ObjectGraphLink l;TRY(game_object_link(id,member,&l));
    if(l.kind!=OBJECT_LINK_RESOURCE)return GS_UNSUPPORTED;*out=l.resource;return GS_OK;
}
static GSStatus animation(GameServices *s,ObjectResourceIdentity id,uint16_t cursor,HazardAnimation *out){
    if(id.kind!=OBJECT_ANIMATION)return GS_UNSUPPORTED;
    TRY(game_object_word(s,id,0,&out->first));
    return game_object_word(s,id,(uint16_t)(cursor+2u),&out->next);
}
/* These views are local borrowers. Publication consumes only the kernel's
 * ordered journal, leaving unused aliases and raw high bytes untouched. */
typedef struct EnemyBorrow {HazardSlot slot;HazardType type;HazardWorld world;LevelPlatform platforms[10];} EnemyBorrow;
static GSStatus borrow(GameWorld *w,GameServices *s,size_t n,ObjectResourceIdentity descriptor,
    HazardEntry entry,EnemyBorrow *b,int frames){
    NativeEnemySlot *a=w->enemies.slot+n;LevelEnemyKind kind;
    TRY(game_object_enemy_kind(descriptor,&kind));(void)kind;
    b->slot=(HazardSlot){.state=entry,.position={a->x32,a->y32},.platform=a->platform,
        .initial_delay=a->initial_delay,.speed=a->speed,.counter=a->counter,
        .animation_cursor=a->animation_offset,.animation_countdown=a->countdown,.sprite=a->sprite,
        .direction=a->direction_or_target_word,.flight_sound=a->sound_handle_word,.draw_x=a->draw_x,.draw_y=a->draw_y};
    for(unsigned i=0;i<13;i++){
        ObjectGraphLink l;TRY(game_object_link(descriptor,(uint16_t)(8+2*i),&l));
        if(l.kind!=OBJECT_LINK_CALLBACK||l.callback.kind!=OBJECT_CALLBACK_ENEMY)return GS_UNSUPPORTED;
        b->type.handlers[i]=l.callback.enemy;
    }
    TRY(game_object_word(s,descriptor,0,&b->type.geometry.anchor_x));
    TRY(game_object_word(s,descriptor,2,&b->type.geometry.anchor_y));
    TRY(game_object_word(s,descriptor,4,&b->type.geometry.extent_x));
    TRY(game_object_word(s,descriptor,6,&b->type.geometry.extent_y));
    TRY(game_object_word(s,descriptor,58,&b->type.score));
    unsigned frame=UINT16_MAX;int first_only=0;
    if(entry==H_BIRD_STUN){frame=signed_word(a->speed)<0?10:11;first_only=1;}
    if(entry==H_DINO_STUN){frame=10;first_only=1;}
    if(frames&&a->countdown==1){
        switch(entry){
        case H_TRIO_PATROL:frame=a->direction_or_target_word/2u;break;
        case H_TRIO_ALERT:if(a->counter!=1)frame=6+a->direction_or_target_word/2u;break;
        case H_TRIO_CHARGE:frame=2+a->direction_or_target_word/2u;break;
        case H_TRIO_RECOVER:frame=4+a->direction_or_target_word/2u;break;
        case H_TRIO_IMPACT:frame=8+a->direction_or_target_word/2u;break;
        case H_TRIO_STUNNED:if(a->counter!=1)frame=10+a->direction_or_target_word/2u;break;
        case H_DINO_FORCE:frame=2;break;case H_TREE_ANIMATE:frame=0;break;
        case H_BIRD_FLIGHT:
            if(signed_word((uint16_t)(a->x32+a->speed))>-1024&&signed_word((uint16_t)(a->x32+a->speed))<10240)
                TRY(animation(s,w->session.enemy_list[n],a->animation_offset,&b->type.flight));
            break;
        default:break;
        }
    }
    if(frame!=UINT16_MAX){
        if(frame>=12)return GS_UNSUPPORTED;
        ObjectResourceIdentity id;TRY(resource_link(descriptor,(uint16_t)(34+2*frame),&id));
        if(first_only)TRY(game_object_word(s,id,0,&b->type.animations[frame].first));
        else TRY(animation(s,id,a->animation_offset,b->type.animations+frame));
    }
    /* Patrol may reverse before selecting its frame. Both directional
     * vectors use the incoming cursor; the kernel decides which is live. */
    if(frames&&entry==H_TRIO_PATROL&&a->countdown==1){
        ObjectResourceIdentity id;unsigned other=(a->direction_or_target_word/2u)^1u;
        if(other>=2)return GS_UNSUPPORTED;
        TRY(resource_link(descriptor,(uint16_t)(34+2*other),&id));
        TRY(animation(s,id,a->animation_offset,b->type.animations+other));
    }
    if(entry==H_TREE_COOLDOWN&&a->counter==1){
        uint16_t word;TRY(game_object_word(s,w->session.enemy_list[n],0,&word));b->type.rewards_exhausted=word==UINT16_MAX;
    }
    HazardWorld *v=&b->world;
    v->player_count=w->run.configuration.players;
    if(w->run.configuration.player_bytes!=2&&w->run.configuration.player_bytes!=4)return GS_UNSUPPORTED;
    v->player_slots=w->run.configuration.player_bytes/2u;v->water_y32=w->run.record.water_fixed;
    v->fade_step=w->run.fade_step;v->fade_level=w->run.fade_level;v->score=w->run.score;
    for(size_t i=0;i<2;i++){
        NativePlayer *p=w->session.players.player+i;
        v->players[i]=(HazardPlayer){{p->fixed_x,p->fixed_y},p->platform,p->velocity_x,p->velocity_y};
    }
    v->stone_count=16;
    for(size_t i=0;i<16;i++){
        if(w->session.actor_end[i]&&v->stone_count==16)v->stone_count=i;
        GameActorSlot *p=w->actors.slot+i;ActorTypeId type;
        int stone=game_object_actor_id(p->descriptor,&type)==GS_OK&&type==ACTOR_STONE&&
            p->callback.kind==OBJECT_CALLBACK_ACTOR&&p->callback.actor==ACTOR_CALLBACK_UpdateThrownStone;
        v->stones[i]=(HazardStone){{p->position,stone,p->motion_or_period_word},p->delay_or_repeat_word,p->sprite};
    }
    for(size_t i=0;i<10;i++){
        NativePlatform *p=w->session.platforms.slot+i;b->platforms[i]=(LevelPlatform){.left=p->left,.right=p->right,.surface_y=p->height};
    }
    v->platforms=b->platforms;v->platform_count=10;
    if(entry==H_TRIO_PATROL&&a->countdown==1){
        /* The physical index is doubled as a wrapping word before the array
         * read; the platform-comparison word itself keeps its high bit. */
        uint16_t index=(uint16_t)(a->platform&32767u);
        if(index>=10)return GS_UNSUPPORTED;
        b->slot.platform=index;
        for(size_t i=0;i<2;i++)v->players[i].platform=v->players[i].platform==a->platform?index:UINT16_MAX;
    }
    if(entry==H_BIRD_LAUNCH){uint16_t target=(uint16_t)(a->direction_or_target_word^1u);
        if(signed_word(target)<signed_word(v->player_count)&&(target&32767u)>=2)return GS_UNSUPPORTED;}
    return GS_OK;
}
static GSStatus publish(GameWorld *w,size_t n,ObjectResourceIdentity descriptor,HazardEntry entry,HazardWrite e){
    NativeEnemySlot *a=w->enemies.slot+n;uint16_t v=e.value;
    switch(e.field){
    case HW_STATE:w->session.enemy_callback[n]=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ENEMY,.enemy=(HazardEntry)v};break;
    case HW_X:a->x32=v;break;case HW_Y:a->y32=v;break;case HW_SPEED:a->speed=v;break;
    case HW_COUNTER:a->counter=v;break;case HW_CURSOR:a->animation_offset=v;break;
    case HW_TICK:a->countdown=v;break;case HW_SPRITE:a->sprite=v;break;
    case HW_DIRECTION:a->direction_or_target_word=v;break;case HW_DRAW_X:a->draw_x=v;break;case HW_DRAW_Y:a->draw_y=v;break;
    case HW_LIST:
        if(entry==H_TREE_RELEASE)w->session.enemy_list[n].position=(uint16_t)(w->session.enemy_list[n].position+2u);
        else TRY(resource_link(descriptor,(uint16_t)(34+2*v),w->session.enemy_list+n));break;
    case HW_SCORE_LOW:w->run.score=(w->run.score&UINT32_C(0xffff0000))|v;break;
    case HW_SCORE_HIGH:w->run.score=(w->run.score&65535u)|((uint32_t)v<<16);break;
    case HW_FADE_STEP:w->run.fade_step=v;break;case HW_FADE_LEVEL:w->run.fade_level=v;break;
    case HW_STONE_VERTICAL:if(e.index>=16)return GS_UNSUPPORTED;
        if(entry==H_BIRD_FLIGHT)v=(uint16_t)(0u-w->actors.slot[e.index].motion_or_period_word);
        w->actors.slot[e.index].motion_or_period_word=v;break;
    case HW_STONE_SPRITE:if(e.index>=16)return GS_UNSUPPORTED;w->actors.slot[e.index].sprite=v;break;
    case HW_PLAYER_Y:w->session.players.player[e.index].fixed_y=v;break;
    case HW_PLAYER_HORIZONTAL:w->session.players.player[e.index].velocity_x=v;break;
    case HW_PLAYER_VERTICAL:w->session.players.player[e.index].velocity_y=v;break;
    case HW_PLAYER_PLATFORM:w->session.players.player[e.index].platform=v;break;
    default:return GS_UNSUPPORTED;
    }return GS_OK;
}
static GSStatus audio(GameWorld *w,GameServices *s,size_t n,HazardResult *r){
    if(r->audio==HA_NONE)return GS_OK;
    if(r->audio==HA_STOP)return game_audio_effect_stop(w,s,r->audio_handle);
    GameAudioResult a=game_audio_effect(w,s,game_object_enemy_effect(r->audio),255,r->audio==HA_FLIGHT?0:1);
    if(a.status!=GS_OK)return a.status;
    if(r->audio==HA_FLIGHT)w->enemies.slot[n].sound_handle_word=a.value;
    return GS_OK;
}
static GSStatus enemy_call(GameWorld *w,GameServices *s,size_t n,ObjectResourceIdentity descriptor,HazardEntry entry,size_t incoming,unsigned budget){
    if(!budget)return GS_OVERFLOW;
    if(entry==H_ZERO||(unsigned)entry>H_TREE_EMPTY)return GS_UNSUPPORTED;
    if(entry==H_IGNORE||entry==H_TREE_EMPTY)return GS_OK;
    if(entry==H_BIRD_STOP)return game_audio_effect_stop(w,s,w->enemies.slot[n].sound_handle_word);
    if(entry==H_TREE_RELEASE&&incoming>=16)return GS_UNSUPPORTED;
    /* Only these direct continuations consume the predecessor's retained
     * descriptor. Every other entry reloads its live physical identity. */
    int retained=entry==H_TRIO_ALERT_BEGIN||entry==H_TRIO_CHARGE_BEGIN||entry==H_TRIO_RECOVER_BEGIN||
        entry==H_TRIO_IMPACT_BEGIN||entry==H_BIRD_STUN||entry==H_TRIO_STUN||entry==H_DINO_STUN||entry==H_TREE_RELEASE;
    if(!retained)descriptor=w->session.enemy_descriptor[n];
    EnemyBorrow b={0};int dino_sound=entry==H_DINO_FORCE&&w->enemies.slot[n].countdown==1&&w->enemies.slot[n].animation_offset==4;
    TRY(borrow(w,s,n,descriptor,entry,&b,!dino_sound));
    uint16_t target=0;
    if(entry==H_BIRD_LAUNCH){
        target=(uint16_t)(b.slot.direction^1u);
        if(signed_word(target)>=signed_word(b.world.player_count))target=0;
        /* A selected 8000/8001 still addresses player 0/1 after SHL 1.
         * Give the kernel that bounded ordinal and retain the full stored word. */
        if(target&32768u){b.slot.direction=(uint16_t)((target&32767u)^1u);b.world.player_count=2;}
    }
    HazardResult r=hazard_step(entry,&b.slot,&b.type,&b.world,(int)incoming);size_t start=0;
    if(entry==H_BIRD_LAUNCH)r.writes[0].value=target;
    /* Dino's sound precedes its frame lookup and force contacts. Read all
     * borrowed operands again after that synchronous service returns. */
    if(dino_sound){
        for(size_t i=0;i<3;i++)TRY(publish(w,n,descriptor,entry,r.writes[i]));
        TRY(audio(w,s,n,&r));
        EnemyBorrow live={0};NativeEnemySlot saved=w->enemies.slot[n];
        /* Seed a local borrow only: no temporary publication to the owner. */
        TRY(borrow(w,s,n,descriptor,entry,&live,0));live.slot.animation_countdown=1;
        live.slot.animation_cursor=(uint16_t)(saved.animation_offset-2u);
        ObjectResourceIdentity id;TRY(resource_link(descriptor,38,&id));
        TRY(animation(s,id,live.slot.animation_cursor,live.type.animations+2));
        r=hazard_step(entry,&live.slot,&live.type,&live.world,(int)incoming);r.audio=HA_NONE;start=3;
    }
    int stopped=0;
    for(size_t i=start;i<r.count;i++){
        HazardWrite e=r.writes[i];
        if(r.audio==HA_STOP&&!stopped&&e.field==HW_STONE_VERTICAL){TRY(audio(w,s,n,&r));stopped=1;}
        if(r.spawn_item&&e.field==HW_LIST){
            ObjectResourceIdentity reward;TRY(resource_link(w->session.enemy_list[n],0,&reward));
            ObjectGraphLink spawn;TRY(game_object_link(reward,4,&spawn));
            if(spawn.kind!=OBJECT_LINK_CALLBACK||spawn.callback.kind!=OBJECT_CALLBACK_ITEM||spawn.callback.item!=ITEM_CALLBACK_SPAWN)return GS_UNSUPPORTED;
            GameItemSpawn item=game_item_spawn(w,s,reward,r.launch,r.launch_horizontal,r.launch_term);
            if(item.status!=GS_OK)return item.status;if(item.allocation.status==ITEM_POOL_FULL)return GS_UNSUPPORTED;
        }
        TRY(publish(w,n,descriptor,entry,e));
    }
    if(!stopped)TRY(audio(w,s,n,&r));
    if(r.has_tail){
        size_t stone=incoming;
        for(size_t i=0;i<r.count;i++)if(r.writes[i].field==HW_STONE_VERTICAL)stone=r.writes[i].index;
        return enemy_call(w,s,n,descriptor,r.tail,stone,budget-1);
    }return GS_OK;
}
GSStatus game_enemy_call(GameWorld *w,GameServices *s,size_t n,ObjectCallbackIdentity role,size_t stone){
    if(!w||!s||!w->session.ready)return GS_INVALID;
    if(n>=5||role.kind!=OBJECT_CALLBACK_ENEMY)return GS_UNSUPPORTED;
    return enemy_call(w,s,n,w->session.enemy_descriptor[n],role.enemy,stone,32);
}
/* Descriptor[5] is physically platform-left[0], not a sixth enemy slot. */
static GSStatus end(GameWorld *w){return w->session.platforms.slot[0].left==UINT16_MAX?GS_OK:GS_UNSUPPORTED;}
GSStatus game_enemies_update(GameWorld *w,GameServices *s){
    if(!w||!s||!w->session.ready)return GS_INVALID;
    for(size_t n=0;n<5;n++){
        if(w->session.enemy_end[n])return GS_OK;
        TRY(game_enemy_call(w,s,n,w->session.enemy_callback[n],0));
    }return end(w);
}
GSStatus game_enemies_erase(GameWorld *w,GameServices *s){
    if(!w||!s||!w->session.ready)return GS_INVALID;
    for(size_t n=0;n<5;n++){
        if(w->session.enemy_end[n])return GS_OK;
        NativeEnemySlot *a=w->enemies.slot+n;uint16_t old=a->erase_sprite;a->erase_sprite=a->sprite;
        if(old!=UINT16_MAX){
            uint16_t index=(uint16_t)(render_restore_sprite_index(old)/4u);if(index>=RESOURCE_SPRITE_RECORDS)return GS_UNSUPPORTED;
            RenderRectangleSpec r=render_sprite_rectangle(a->previous_x,a->previous_y,w->sprite_catalog.sprites[index].dimensions);
            TRY(game_front_restore(w,s,(FrontRectangle){r.x,r.y,r.width,r.height}));
        }
    }return end(w);
}
static GSStatus draw(GameWorld *w,GameServices *s,int front){
    if(!w||!s||!w->session.ready)return GS_INVALID;
    for(size_t n=0;n<5;n++){
        if(w->session.enemy_end[n])return GS_OK;
        LevelEnemyKind kind;TRY(game_object_enemy_kind(w->session.enemy_descriptor[n],&kind));
        int special=kind==LEVEL_DINO||kind==LEVEL_TREE;NativeEnemySlot *a=w->enemies.slot+n;
        if(special!=front&&a->sprite!=UINT16_MAX){
            a->previous_x=a->draw_x;a->previous_y=a->draw_y;a->draw_x=pixel(a->x32);a->draw_y=pixel(a->y32);
            if(signed_word(a->draw_y)<192)TRY(game_front_sprite_draw(w,s,a->sprite,a->draw_x,a->draw_y));
        }
    }return end(w);
}
GSStatus game_enemies_draw_back(GameWorld *w,GameServices *s){return draw(w,s,0);}
GSStatus game_enemies_draw_front(GameWorld *w,GameServices *s){return draw(w,s,1);}
