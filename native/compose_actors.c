#include "compose_objects.h"
#include "compose_demo.h"
#include "compose_audio.h"
#include "game_object_data.h"
#include "passenger_itinerary.h"
#include "passenger_delivery.h"
#include "passenger_water.h"
#include "stones.h"
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
/* Local kernel views borrow physical owners. Only journals are published;
 * inactive semantic aliases never write back over their active peer. */
typedef struct ActorBorrow {
    PassengerStoneSlot slot;ActorType type[2];
    uint16_t frames[2][ACTOR_ANIMATION_COUNT][256];
    PassengerJourney journey;PassengerJourneyLeg legs[256];
    LevelPlatform platforms[10];
} ActorBorrow;
static GSStatus actor_itinerary(GameWorld *,GameServices *,size_t,ItineraryEntry,unsigned);
static GSStatus actor_delivery(GameWorld *,GameServices *,size_t,PassengerDeliveryEntry,size_t,unsigned);
static GSStatus actor_water(GameWorld *,GameServices *,size_t,PassengerWaterEntry,unsigned);
static GSStatus actor_stone(GameWorld *,GameServices *,size_t,ActorCallback,size_t,unsigned);
static GSStatus role_at(GameActorSlot *a,unsigned member,ObjectCallbackIdentity *out){
    ObjectGraphLink l;TRY(game_object_link(a->descriptor,(uint16_t)member,&l));
    if(l.kind!=OBJECT_LINK_CALLBACK||l.callback.kind!=OBJECT_CALLBACK_ACTOR)return GS_UNSUPPORTED;
    *out=l.callback;return GS_OK;
}
static GSStatus require_role(GameActorSlot *a,unsigned member,ActorCallback role){
    ObjectCallbackIdentity id;TRY(role_at(a,member,&id));return id.actor==role?GS_OK:GS_UNSUPPORTED;
}
static void alias(GameActorSlot *a,uint16_t value){
    a->loop_cursor=value;a->loop_script=(ObjectResourceIdentity){0};
}
static GSStatus phase(GameActorSlot *a,ActorPhase value){
    unsigned member;
    switch(value){
    case ACTOR_READ_JOURNEY:member=8;break;
    case ACTOR_WAIT_FOR_PLATFORM:case ACTOR_RESURFACING:member=10;break;
    case ACTOR_ARRIVING:case ACTOR_SINKING:member=14;break;
    case ACTOR_PLATFORM_WAIT:case ACTOR_STONE_WAIT:case ACTOR_FLOATING:member=18;break;
    case ACTOR_DESTINATION_REQUEST:case ACTOR_FLOATING_DESTINATION_REQUEST:member=22;break;
    case ACTOR_QUESTION:case ACTOR_FLOATING_QUESTION:member=26;break;
    case ACTOR_APPROACH:case ACTOR_FLOATING_APPROACH:member=30;break;
    case ACTOR_CARRIED_PASSENGER:case ACTOR_CARRIED_STONE:member=34;break;
    case ACTOR_WALK_TO_EXIT:case ACTOR_THROWN_STONE:member=38;break;
    case ACTOR_DEPARTING:member=42;break;
    case ACTOR_RETIRED:member=44;break;
    default:return GS_UNSUPPORTED;
    }
    return role_at(a,member,&a->callback);
}
static GSStatus type_borrow(GameServices *s,ObjectResourceIdentity id,ActorType *type,
    uint16_t frames[ACTOR_ANIMATION_COUNT][256],int animations){
    ActorTypeId kind;TRY(game_object_actor_id(id,&kind));GSBytes bytes;TRY(game_object_resource(s,id,&bytes));
    if(bytes.size!=74)return GS_UNSUPPORTED;
    ActorAnimation vectors[ACTOR_ANIMATION_COUNT]={0};
    if(animations)for(unsigned i=0;i<ACTOR_ANIMATION_COUNT;i++){
        ObjectGraphLink l;TRY(game_object_link(id,(uint16_t)(46+2*i),&l));
        if(l.kind!=OBJECT_LINK_RESOURCE||l.resource.kind!=OBJECT_ANIMATION)return GS_UNSUPPORTED;
        GSBytes b;TRY(game_object_resource(s,l.resource,&b));size_t count=0;
        for(;count<256&&2*count+1<b.size;count++){
            uint16_t v=(uint16_t)(b.data[2*count]|(uint16_t)b.data[2*count+1]<<8);
            if(v==UINT16_MAX)break;frames[i][count]=v;
        }
        if(count==256||2*count+1>=b.size)return GS_UNSUPPORTED;
        vectors[i]=(ActorAnimation){frames[i],count};
    }
    *type=actor_type_resource(kind,bytes.data,vectors,0);return GS_OK;
}
static GSStatus borrow(GameWorld *w,GameServices *s,size_t n,ActorPhase current,ActorBorrow *b){
    GameActorSlot *a=w->actors.slot+n;
    if(a->demo)return GS_UNSUPPORTED;
    TRY(type_borrow(s,a->descriptor,b->type,b->frames[0],current!=ACTOR_BEGIN_STONE_WAIT&&current!=ACTOR_STONE_WAIT&&current!=ACTOR_CARRIED_STONE&&current!=ACTOR_THROWN_STONE));
    if(b->type[0].id<ACTOR_STONE){
        ObjectGraphLink pair;TRY(game_object_link(a->descriptor,72,&pair));
        if(pair.kind!=OBJECT_LINK_RESOURCE||pair.resource.kind!=OBJECT_ACTOR_DESCRIPTOR)return GS_UNSUPPORTED;
        TRY(type_borrow(s,pair.resource,b->type+1,b->frames[1],0));b->type[0].paired_type=b->type+1;
    }
    b->slot=(PassengerStoneSlot){.type=b->type,.phase=current,.source_platform=a->source_or_done,
        .destination_platform=a->destination_platform,.position=a->position,.sprite=a->sprite,.overlay_sprite=a->overlay_sprite,
        .animation=a->animation,.vertical_motion=a->motion_or_period_word,.quick_delivery_ticks=a->quick_delivery_ticks};
    unsigned aliases=actor_phase_aliases(current);
    if(aliases&ACTOR_ALIAS_WAITING_POSE)b->slot.waiting_pose=a->loop_cursor;
    if(aliases&ACTOR_ALIAS_REQUEST_TICKS)b->slot.request_ticks=a->loop_cursor;
    if(aliases&ACTOR_ALIAS_CARRIER){
        if((a->loop_cursor&1u)||a->loop_cursor>=4)return GS_UNSUPPORTED;
        b->slot.carrier=a->loop_cursor/2u;
    }
    if(aliases&ACTOR_ALIAS_JOURNEY_WAIT)b->slot.journey_wait=a->delay_or_repeat_word;
    if(aliases&ACTOR_ALIAS_HORIZONTAL_STEP)b->slot.horizontal_step=a->delay_or_repeat_word;
    if(aliases&ACTOR_ALIAS_FLOATING_TICKS)b->slot.floating_ticks=a->delay_or_repeat_word;
    for(size_t i=0;i<10;i++){
        NativePlatform *p=w->session.platforms.slot+i;
        b->platforms[i]=(LevelPlatform){p->left,p->right,p->height,p->arrival,p->wait,p->spawn,p->icon,0};
    }return GS_OK;
}
static GSStatus publish_itinerary(GameWorld *w,size_t n,const ItineraryResult *r){
    GameActorSlot *a=w->actors.slot+n;
    if(r->failed)return GS_UNSUPPORTED;
    for(size_t i=0;i<r->count;i++){
        ItineraryWrite e=r->writes[i];uint16_t v=e.value;
        switch(e.field){
        case IT_PHASE:TRY(phase(a,(ActorPhase)v));break;
        case IT_SOURCE:a->source_or_done=v;break;case IT_DESTINATION:a->destination_platform=v;break;
        case IT_SOURCE_INDEX:a->source_byte_index=(uint16_t)(2u*v);break;case IT_DESTINATION_INDEX:a->destination_byte_index=(uint16_t)(2u*v);break;
        case IT_DELAY:a->delay_or_repeat_word=v;break;
        case IT_X:a->position.x32=v;break;case IT_Y:a->position.y32=v;break;
        case IT_PIXEL_X:a->history.pixel_x=v;break;case IT_PIXEL_Y:a->history.pixel_y=v;break;
        case IT_CURSOR:a->animation.byte_offset=v;break;case IT_COUNTDOWN:a->animation.countdown=v;break;
        case IT_SPRITE:a->sprite=v;break;
        case IT_JOURNEY:a->journey.position=(uint16_t)(a->journey.position+4u*v);break;
        case IT_OCCUPANT:if(e.index>=10)return GS_UNSUPPORTED;w->session.platforms.slot[e.index].occupant=(uint16_t)(2u*v);break;
        case IT_REMAINING:w->run.record.journeys=(uint8_t)v;break;case IT_COMPLETION:w->run.completion=(uint8_t)v;break;
        case IT_FADE_RATE:w->run.fade_step=v;break;case IT_FADE_LEVEL:w->run.fade_level=v;break;
        default:return GS_UNSUPPORTED;
        }
    }return GS_OK;
}
static GSStatus actor_itinerary(GameWorld *w,GameServices *s,size_t n,ItineraryEntry entry,unsigned budget){
    if(!budget)return GS_OVERFLOW;
    if(entry==IT_IGNORE){actor_reserved_return();return GS_OK;}
    ActorPhase current=entry==IT_WAIT||entry==IT_PLACE?ACTOR_WAIT_FOR_PLATFORM:entry==IT_ARRIVAL?ACTOR_ARRIVING:
        entry==IT_WALK||entry==IT_BEGIN_DEPARTURE?ACTOR_WALK_TO_EXIT:entry==IT_DEPARTURE?ACTOR_DEPARTING:ACTOR_READ_JOURNEY;
    ActorBorrow b={0};TRY(borrow(w,s,n,current,&b));GameActorSlot *a=w->actors.slot+n;
    if((entry==IT_WAIT||entry==IT_PLACE)&&(a->source_or_done>=10||a->source_byte_index!=2u*a->source_or_done))return GS_UNSUPPORTED;
    if(entry==IT_WALK&&(a->destination_platform>=10||a->destination_byte_index!=2u*a->destination_platform))return GS_UNSUPPORTED;
    ItineraryPlatformUse uses[10];for(size_t i=0;i<10;i++)uses[i]=(ItineraryPlatformUse){w->session.platforms.slot[i].occupant==UINT16_MAX,0};
    ItineraryWorld world={b.platforms,uses,10,n,w->run.record.journeys,w->run.completion,w->run.fade_step,w->run.fade_level};
    if(entry==IT_READ){
        if(a->journey.kind!=OBJECT_JOURNEY)return GS_UNSUPPORTED;
        GSBytes bytes;TRY(game_object_resource(s,a->journey,&bytes));size_t count=0;
        while(count<256&&4*count+1<bytes.size){
            uint16_t platform=(uint16_t)(bytes.data[4*count]|(uint16_t)bytes.data[4*count+1]<<8);
            if(platform==UINT16_MAX)break;
            if(4*count+3>=bytes.size)return GS_UNSUPPORTED;
            b.legs[count]=(PassengerJourneyLeg){platform,(uint16_t)(bytes.data[4*count+2]|(uint16_t)bytes.data[4*count+3]<<8)};count++;
        }
        if(!count||count==256||4*count+1>=bytes.size)return GS_UNSUPPORTED;
        b.journey=(PassengerJourney){b.legs,count};b.slot.journey=(PassengerJourneyCursor){&b.journey,0};
        if(count>1){CoordinateScale scaled=scale_level_speed(b.legs[0].wait);w->session.scale_scratch=scaled.removed_fraction;}
    }
    ItineraryResult r=itinerary_apply(entry,&b.slot,&a->history,&world);TRY(publish_itinerary(w,n,&r));
    switch(r.next){
    case IT_NEXT_NONE:return GS_OK;
    case IT_NEXT_PLACE:TRY(require_role(a,12,ACTOR_CALLBACK_PlacePassengerOnPlatform));return actor_itinerary(w,s,n,IT_PLACE,budget-1);
    case IT_NEXT_PLATFORM_WAIT:TRY(require_role(a,16,ACTOR_CALLBACK_BeginPassengerPlatformWait));return actor_delivery(w,s,n,PD_BEGIN_WAIT,0,budget-1);
    case IT_NEXT_DEPARTURE:TRY(require_role(a,40,ACTOR_CALLBACK_BeginPassengerDeparture));return actor_itinerary(w,s,n,IT_BEGIN_DEPARTURE,budget-1);
    case IT_NEXT_READ:TRY(require_role(a,8,ACTOR_CALLBACK_ReadPassengerJourneyLeg));return actor_itinerary(w,s,n,IT_READ,budget-1);
    case IT_NEXT_IGNORE:TRY(require_role(a,44,ACTOR_CALLBACK_IgnoreActorState));return GS_OK;
    default:return GS_UNSUPPORTED;
    }
}
static GSStatus publish_delivery(GameWorld *w,size_t n,const PassengerDeliveryResult *r){
    if(r->failed)return GS_UNSUPPORTED;
    GameActorSlot *a=w->actors.slot+n;
    for(size_t i=0;i<r->count;i++){
        PassengerDeliveryWrite e=r->writes[i];uint16_t v=e.value;
        switch(e.field){
        case PD_PHASE:TRY(phase(a,(ActorPhase)v));break;
        case PD_TYPE:TRY(game_object_actor_type((ActorTypeId)v,&a->descriptor));break;
        case PD_CURSOR:a->animation.byte_offset=v;break;case PD_TICK:a->animation.countdown=v;break;
        case PD_POSE:case PD_REQUEST:alias(a,v);break;case PD_CARRIER:alias(a,(uint16_t)(2u*v));break;
        case PD_SPRITE:a->sprite=v;break;case PD_OVERLAY:a->overlay_sprite=v;break;
        case PD_X:a->position.x32=v;break;case PD_Y:a->position.y32=v;break;case PD_QUICK:a->quick_delivery_ticks=v;break;
        case PD_OCCUPANT_CLEAR:if(e.index>=10)return GS_UNSUPPORTED;w->session.platforms.slot[e.index].occupant=v;break;
        case PD_FARE:case PD_FLOOR:case PD_KIND:case PD_ICON:{
            if(e.index>=2)return GS_UNSUPPORTED;NativePlayer *p=w->session.players.player+e.index;
            if(e.field==PD_FARE)p->fare=v;else if(e.field==PD_FLOOR)p->minimum_fare=v;else if(e.field==PD_KIND)p->carried=v;else p->destination=v;break;}
        case PD_SCORE_LOW:w->run.score=(w->run.score&UINT32_C(0xffff0000))|v;break;
        case PD_SCORE_HIGH:w->run.score=(w->run.score&65535u)|((uint32_t)v<<16);break;
        case PD_HUD_CLEAR:w->presentation.hud.fare_pending=(uint8_t)v;break;
        default:return GS_UNSUPPORTED;
        }
    }return GS_OK;
}
static GSStatus actor_delivery(GameWorld *w,GameServices *s,size_t n,PassengerDeliveryEntry entry,size_t incoming,unsigned budget){
    if(!budget)return GS_OVERFLOW;
    if(incoming>=2||(w->run.configuration.player_bytes!=2&&w->run.configuration.player_bytes!=4))return GS_UNSUPPORTED;
    ActorPhase current=entry==PD_WAIT?ACTOR_PLATFORM_WAIT:entry==PD_DESTINATION?ACTOR_DESTINATION_REQUEST:
        entry==PD_QUESTION?ACTOR_QUESTION:entry==PD_APPROACH?ACTOR_APPROACH:entry==PD_CARRIED||entry==PD_DELIVER?ACTOR_CARRIED_PASSENGER:ACTOR_READ_JOURNEY;
    ActorBorrow b={0};TRY(borrow(w,s,n,current,&b));GameActorSlot *a=w->actors.slot+n;
    if(b.type[0].id>=ACTOR_STONE||a->source_or_done>=10||a->destination_platform>=10)return GS_UNSUPPORTED;
    ObjectResourceIdentity retained_descriptor=a->descriptor;
    if(current==ACTOR_CARRIED_PASSENGER&&b.slot.carrier>=w->run.configuration.player_bytes/2u)return GS_UNSUPPORTED;
    PassengerDeliveryWorld world={.player_count=w->run.configuration.players,.player_slots=w->run.configuration.player_bytes/2u,
        .platforms=b.platforms,.platform_count=10,.water_pixel_y=w->run.water_y,.multiplier=w->run.multiplier,
        .score=w->run.score,.hud_clear=w->presentation.hud.fare_pending};
    if(entry==PD_DELIVER)TRY(game_object_multiplier_limit(s,w->run.configuration.difficulty,&world.multiplier_limit));
    for(size_t i=0;i<2;i++){
        NativePlayer *p=w->session.players.player+i;
        world.craft[i]=(PassengerCraft){{p->fixed_x,p->fixed_y},p->pixel_x,p->platform,p->carried,p->destination,p->fare,p->minimum_fare};
    }
    PassengerDeliveryResult r=passenger_delivery_apply(entry,&b.slot,&a->history,&world,incoming);TRY(publish_delivery(w,n,&r));
    if(r.spawn_bonus){
        GameItemSpawn spawn=game_item_spawn(w,s,game_object_bonus(),r.launch,0,0);TRY(spawn.status);
        /* The original full-pool return consumes the saved actor index as a
         * code return. It has no admitted normal gameplay continuation. */
        if(spawn.allocation.status==ITEM_POOL_FULL)return GS_UNSUPPORTED;
        TRY(game_audio_effect(w,s,game_object_bonus_effect(),255,1).status);
        /* The descriptor identity is retained across audio; its anchor bytes,
         * destination byte-index and platform height are fresh reads. Do not
         * replace the retained identity with the actor's new descriptor. */
        if((a->destination_byte_index&1u)||a->destination_byte_index>=20)return GS_UNSUPPORTED;
        ActorType retained={0};TRY(game_object_word(s,retained_descriptor,2,&retained.geometry.anchor_y));
        PassengerStoneSlot finish={.type=&retained,.destination_platform=a->destination_byte_index/2u};
        for(unsigned i=0;i<10;i++)b.platforms[i].surface_y=w->session.platforms.slot[i].height;
        world.platforms=b.platforms;
        PassengerDeliveryResult tail=passenger_delivery_finish(&finish,&world);TRY(publish_delivery(w,n,&tail));
    }
    switch(r.next){
    case PD_NEXT_NONE:return GS_OK;
    case PD_NEXT_WAIT:TRY(require_role(a,16,ACTOR_CALLBACK_BeginPassengerPlatformWait));return actor_delivery(w,s,n,PD_BEGIN_WAIT,0,budget-1);
    case PD_NEXT_DESTINATION:TRY(require_role(a,20,ACTOR_CALLBACK_BeginPassengerDestinationDisplay));return actor_delivery(w,s,n,PD_BEGIN_DESTINATION,0,budget-1);
    case PD_NEXT_QUESTION:TRY(require_role(a,24,ACTOR_CALLBACK_BeginPassengerQuestionDisplay));return actor_delivery(w,s,n,PD_BEGIN_QUESTION,0,budget-1);
    case PD_NEXT_APPROACH:TRY(require_role(a,28,ACTOR_CALLBACK_BeginPassengerApproach));return actor_delivery(w,s,n,PD_BEGIN_APPROACH,0,budget-1);
    case PD_NEXT_BOARD:TRY(require_role(a,32,ACTOR_CALLBACK_BoardPassenger));return actor_delivery(w,s,n,PD_BOARD,(size_t)r.selected,budget-1);
    case PD_NEXT_DELIVER:TRY(require_role(a,36,ACTOR_CALLBACK_DeliverPassenger));return actor_delivery(w,s,n,PD_DELIVER,(size_t)r.selected,budget-1);
    case PD_NEXT_WATER:TRY(require_role(a,8,ACTOR_CALLBACK_BeginPassengerResurfacing));return actor_water(w,s,n,PW_BEGIN_RESURFACE,budget-1);
    default:return GS_UNSUPPORTED;
    }
}
static GSStatus publish_water(GameWorld *w,size_t n,const PassengerWaterResult *r){
    if(r->failed)return GS_UNSUPPORTED;
    GameActorSlot *a=w->actors.slot+n;
    for(size_t i=0;i<r->count;i++){
        PassengerWaterWrite e=r->writes[i];uint16_t v=e.value;
        switch(e.field){
        case PW_PHASE:TRY(phase(a,(ActorPhase)v));break;
        case PW_CURSOR:a->animation.byte_offset=v;break;case PW_TICK:a->animation.countdown=v;break;
        case PW_OVERLAY:a->overlay_sprite=v;break;case PW_VELOCITY:a->motion_or_period_word=v;break;
        case PW_Y:a->position.y32=v;break;case PW_X:a->position.x32=v;break;case PW_SPRITE:a->sprite=v;break;
        case PW_LIFETIME:a->delay_or_repeat_word=v;break;case PW_REQUEST:alias(a,v);break;
        case PW_OCCUPANT_CLEAR:if(e.index>=10)return GS_UNSUPPORTED;w->session.platforms.slot[e.index].occupant=v;break;
        default:return GS_UNSUPPORTED;
        }
    }return GS_OK;
}
static GSStatus actor_water(GameWorld *w,GameServices *s,size_t n,PassengerWaterEntry entry,unsigned budget){
    if(!budget)return GS_OVERFLOW;
    if(entry==PW_IGNORE)return GS_OK;
    ActorPhase current=entry==PW_RESURFACE?ACTOR_RESURFACING:entry==PW_SINK?ACTOR_SINKING:entry==PW_FLOAT?ACTOR_FLOATING:
        entry==PW_DESTINATION?ACTOR_FLOATING_DESTINATION_REQUEST:entry==PW_QUESTION?ACTOR_FLOATING_QUESTION:entry==PW_APPROACH?ACTOR_FLOATING_APPROACH:ACTOR_READ_JOURNEY;
    ActorBorrow b={0};TRY(borrow(w,s,n,current,&b));GameActorSlot *a=w->actors.slot+n;
    if(b.type[0].id>=ACTOR_STONE||!(b.type[0].id&1u)||w->run.configuration.players<1||w->run.configuration.players>2)return GS_UNSUPPORTED;
    PassengerWaterWorld world={.player_count=w->run.configuration.players,.platform_count=10,.surface_y=w->run.water_y};
    for(size_t i=0;i<2;i++){
        NativePlayer *p=w->session.players.player+i;world.craft[i]=(WaterCraft){p->pixel_x,p->pixel_y,p->velocity_y,p->carried};
    }
    PassengerWaterResult r=passenger_water_apply(entry,&b.slot,&a->history,&world);TRY(publish_water(w,n,&r));
    switch(r.next){
    case PW_NEXT_NONE:return GS_OK;
    case PW_NEXT_FLOAT:TRY(require_role(a,16,ACTOR_CALLBACK_BeginPassengerFloating));return actor_water(w,s,n,PW_BEGIN_FLOAT,budget-1);
    case PW_NEXT_SINK:TRY(require_role(a,12,ACTOR_CALLBACK_BeginPassengerSinking));return actor_water(w,s,n,PW_BEGIN_SINK,budget-1);
    case PW_NEXT_DESTINATION:TRY(require_role(a,20,ACTOR_CALLBACK_BeginPassengerDestinationDisplay));return actor_delivery(w,s,n,PD_BEGIN_DESTINATION,0,budget-1);
    case PW_NEXT_QUESTION:TRY(require_role(a,24,ACTOR_CALLBACK_BeginPassengerQuestionDisplay));return actor_delivery(w,s,n,PD_BEGIN_QUESTION,0,budget-1);
    case PW_NEXT_APPROACH:TRY(require_role(a,28,ACTOR_CALLBACK_BeginPassengerApproach));return actor_delivery(w,s,n,PD_BEGIN_APPROACH,0,budget-1);
    case PW_NEXT_BOARD:TRY(require_role(a,32,ACTOR_CALLBACK_BoardWaterbornePassenger));return actor_delivery(w,s,n,PD_RESCUE,(size_t)r.selected,budget-1);
    default:return GS_UNSUPPORTED;
    }
}
static GSStatus actor_stone(GameWorld *w,GameServices *s,size_t n,ActorCallback role,size_t incoming,unsigned budget){
    if(!budget)return GS_OVERFLOW;
    ActorPhase current=role==ACTOR_CALLBACK_BeginStonePickupWait?ACTOR_BEGIN_STONE_WAIT:
        role==ACTOR_CALLBACK_UpdateStonePickupWait||role==ACTOR_CALLBACK_AttachStoneToPlayer?ACTOR_STONE_WAIT:
        role==ACTOR_CALLBACK_UpdateThrownStone?ACTOR_THROWN_STONE:ACTOR_CARRIED_STONE;
    ActorBorrow b={0};TRY(borrow(w,s,n,current,&b));GameActorSlot *a=w->actors.slot+n;
    if(b.type[0].id<ACTOR_STONE||incoming>=2)return GS_UNSUPPORTED;
    StonePlayer players[2];for(size_t i=0;i<2;i++){
        NativePlayer *p=w->session.players.player+i;
        players[i]=(StonePlayer){{p->fixed_x,p->fixed_y},p->velocity_x,p->velocity_y,p->carried,p->destination,p->action};
    }
    switch(role){
    case ACTOR_CALLBACK_BeginStonePickupWait:
        stone_begin_wait(&b.slot);TRY(phase(a,b.slot.phase));a->animation=b.slot.animation;return GS_OK;
    case ACTOR_CALLBACK_UpdateStonePickupWait:{
        StoneResult r=stone_pickup_wait(&b.slot,players,w->run.configuration.players);
        if(r.exit==STONE_PICKUP){TRY(require_role(a,32,ACTOR_CALLBACK_AttachStoneToPlayer));return actor_stone(w,s,n,ACTOR_CALLBACK_AttachStoneToPlayer,(size_t)r.contact.index,budget-1);}
        a->sprite=b.slot.sprite;return GS_OK;}
    case ACTOR_CALLBACK_AttachStoneToPlayer:
        stone_attach(&b.slot,players,incoming);TRY(phase(a,b.slot.phase));
        w->session.players.player[incoming].carried=players[incoming].carried_kind;w->session.players.player[incoming].destination=players[incoming].destination_icon;
        alias(a,(uint16_t)(2u*b.slot.carrier));a->sprite=b.slot.sprite;return GS_OK;
    case ACTOR_CALLBACK_WaitForStoneRelease:
        if(!stone_release_requested(&b.slot,players))return GS_OK;
        TRY(require_role(a,36,ACTOR_CALLBACK_ThrowCarriedStone));return actor_stone(w,s,n,ACTOR_CALLBACK_ThrowCarriedStone,b.slot.carrier,budget-1);
    case ACTOR_CALLBACK_ThrowCarriedStone:
        stone_throw(&b.slot,players,incoming);w->session.players.player[incoming].carried=players[incoming].carried_kind;
        w->session.players.player[incoming].destination=players[incoming].destination_icon;
        a->delay_or_repeat_word=b.slot.horizontal_step;a->motion_or_period_word=b.slot.vertical_motion;
        a->position=b.slot.position;a->sprite=b.slot.sprite;TRY(phase(a,b.slot.phase));
        return game_audio_effect(w,s,game_object_stone_effect(),255,1).status;
    case ACTOR_CALLBACK_UpdateThrownStone:{
        size_t count=0;while(count<10&&!(b.platforms[count].left&32768u))count++;
        if(count==10)return GS_UNSUPPORTED;
        StoneResult r=stone_flight(&b.slot,b.platforms,count);a->position=b.slot.position;a->motion_or_period_word=b.slot.vertical_motion;a->sprite=b.slot.sprite;
        if(r.exit==STONE_OUT_LEFT||r.exit==STONE_OUT_RIGHT||r.exit==STONE_OUT_BOTTOM)TRY(phase(a,ACTOR_RETIRED));
        if(r.exit==STONE_LANDING){TRY(require_role(a,16,ACTOR_CALLBACK_BeginStonePickupWait));return actor_stone(w,s,n,ACTOR_CALLBACK_BeginStonePickupWait,0,budget-1);}
        return GS_OK;}
    default:return GS_UNSUPPORTED;
    }
}
GSStatus game_actor_call(GameWorld *w,GameServices *s,uint16_t *cursor,ObjectCallbackIdentity role,size_t incoming){
    if(!w||!s||!cursor||!w->session.ready)return GS_INVALID;
    if((*cursor&1u)||*cursor>=32)return GS_UNSUPPORTED;
    size_t n=*cursor/2u;
    if(role.kind==OBJECT_CALLBACK_DEMO_EFFECT)return game_demo_callback(w,s,n,role);
    if(role.kind!=OBJECT_CALLBACK_ACTOR)return GS_UNSUPPORTED;
    switch(role.actor){
#define IT(name,entry) case ACTOR_CALLBACK_##name:return actor_itinerary(w,s,n,entry,32)
    IT(ReadPassengerJourneyLeg,IT_READ);IT(WaitForPassengerPlatform,IT_WAIT);IT(PlacePassengerOnPlatform,IT_PLACE);
    IT(AnimatePassengerArrival,IT_ARRIVAL);IT(WalkPassengerToExit,IT_WALK);IT(BeginPassengerDeparture,IT_BEGIN_DEPARTURE);IT(AnimatePassengerDeparture,IT_DEPARTURE);
    IT(IgnoreActorState,IT_IGNORE);
#undef IT
#define PD(name,entry) case ACTOR_CALLBACK_##name:return actor_delivery(w,s,n,entry,incoming,32)
    PD(BeginPassengerPlatformWait,PD_BEGIN_WAIT);PD(UpdatePassengerPlatformWait,PD_WAIT);
    PD(BeginPassengerDestinationDisplay,PD_BEGIN_DESTINATION);PD(UpdatePassengerDestinationDisplay,PD_DESTINATION);
    PD(BeginPassengerQuestionDisplay,PD_BEGIN_QUESTION);PD(UpdatePassengerQuestionDisplay,PD_QUESTION);
    PD(BeginPassengerApproach,PD_BEGIN_APPROACH);PD(UpdatePassengerApproach,PD_APPROACH);
    PD(BoardWaterbornePassenger,PD_RESCUE);PD(BoardPassenger,PD_BOARD);PD(UpdateCarriedPassenger,PD_CARRIED);PD(DeliverPassenger,PD_DELIVER);
#undef PD
#define PW(name,entry) case ACTOR_CALLBACK_##name:return actor_water(w,s,n,entry,32)
    PW(BeginPassengerResurfacing,PW_BEGIN_RESURFACE);PW(UpdatePassengerResurfacing,PW_RESURFACE);
    PW(BeginPassengerSinking,PW_BEGIN_SINK);PW(UpdatePassengerSinking,PW_SINK);PW(BeginPassengerFloating,PW_BEGIN_FLOAT);PW(UpdatePassengerFloating,PW_FLOAT);
    PW(UpdateFloatingDestinationDisplay,PW_DESTINATION);PW(UpdateFloatingQuestionDisplay,PW_QUESTION);PW(UpdateFloatingPassengerApproach,PW_APPROACH);PW(IgnoreWaterbornePassengerState,PW_IGNORE);
#undef PW
    case ACTOR_CALLBACK_BeginStonePickupWait:case ACTOR_CALLBACK_UpdateStonePickupWait:case ACTOR_CALLBACK_AttachStoneToPlayer:
    case ACTOR_CALLBACK_WaitForStoneRelease:case ACTOR_CALLBACK_ThrowCarriedStone:case ACTOR_CALLBACK_UpdateThrownStone:
        return actor_stone(w,s,n,role.actor,incoming,32);
    default:return GS_UNSUPPORTED;
    }
}
GSStatus game_actors_update(GameWorld *w,GameServices *s){
    if(!w||!s||!w->session.ready)return GS_INVALID;
    ActorPass pass;actor_pass_begin(&pass);
    for(;;){
        if((pass.cursor&1u)||pass.cursor>=32)return GS_UNSUPPORTED;
        size_t n=pass.cursor/2u;
        if(w->session.actor_end[n])return GS_OK;
        ObjectCallbackIdentity role=w->actors.slot[n].callback;
        ActorPassAction action=actor_pass_select(&pass,0,role.kind==OBJECT_CALLBACK_DEMO_EFFECT?ACTOR_CALLBACK_IgnoreActorState:role.actor);
        if(action!=ACTOR_PASS_CALL)return action==ACTOR_PASS_LIMIT?GS_OVERFLOW:GS_UNSUPPORTED;
        uint16_t returned=pass.cursor;TRY(game_actor_call(w,s,&returned,role,0));actor_pass_resume(&pass,returned);
    }
}
