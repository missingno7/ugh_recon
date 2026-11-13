#include "actor_projection.h"
static uint16_t actor_type_identity(size_t index) { return (uint16_t)(D(Data_7720)+74u*index); }
static uint16_t actor_read(uint16_t segment,uint16_t base,size_t index) {
    return rd16(segment,(uint16_t)(base+2u*index));
}
const ActorType *actor_bridge_type(const ActorResourceStorage *storage,uint16_t identity) {
    for(size_t i=0;i<ACTOR_TYPE_COUNT;i++) if(identity==actor_type_identity(i)) return &storage->types[i];
    return 0;
}
int actor_bridge_resources(uint16_t segment,ActorResourceStorage *storage) {
    for(size_t i=0;i<ACTOR_TYPE_COUNT;i++) {
        uint16_t base=actor_type_identity(i);uint8_t raw[74];ActorAnimation animations[ACTOR_ANIMATION_COUNT];
        for(size_t j=0;j<74;j++) raw[j]=rd8(segment,(uint16_t)(base+j));
        for(size_t j=0;j<ACTOR_ANIMATION_COUNT;j++) {
            uint16_t p=rd16(segment,(uint16_t)(base+46+2*j));size_t count=0;
            if(p) for(;;) {
                if(p>65533u || count==ACTOR_RESOURCE_LIMIT) return 0;
                uint16_t sprite=rd16(segment,p); if(sprite==65535u) break;
                storage->animation_words[i][j][count++]=sprite;p=(uint16_t)(p+2);
            }
            animations[j].sprites=storage->animation_words[i][j];animations[j].count=count;
        }
        uint16_t pair=rd16(segment,(uint16_t)(base+72));
        const ActorType *paired=pair ? actor_bridge_type(storage,pair) : 0;
        if(pair && !paired) return 0;
        storage->types[i]=actor_type_resource((ActorTypeId)i,raw,animations,paired);
    }
    return 1;
}
int actor_bridge_journey(uint16_t segment,uint16_t base,PassengerJourneyLeg *legs,PassengerJourney *journey) {
    size_t count=0;uint16_t p=base;
    while(rd16(segment,p)!=65535u) {
        if(count==ACTOR_RESOURCE_LIMIT || p>65531u) return 0;
        legs[count].platform=rd16(segment,p);legs[count].wait=rd16(segment,(uint16_t)(p+2));
        count++;p=(uint16_t)(p+4);
    }
    journey->legs=legs;journey->count=count;return 1;
}
int actor_bridge_level(uint16_t segment,uint16_t record,const LevelDescription *level,
    const ActorResourceStorage *resources,ActorLevelStorage *storage) {
    if(level->actor_count>=ACTOR_CAPACITY) return 0;
    uint16_t p=rd16(segment,(uint16_t)(record+4));
    for(size_t i=0;i<level->actor_count;i++,p=(uint16_t)(p+6)) {
        if(p>65529u) return 0;
        ActorLevelEntry *entry=&storage->entries[i];
        entry->type=actor_bridge_type(resources,rd16(segment,p));if(!entry->type) return 0;
        entry->initial_platform=rd16(segment,(uint16_t)(p+2));
        entry->journey=(PassengerJourney){0,0};
        if(entry->type->id<ACTOR_STONE && !actor_bridge_journey(segment,rd16(segment,(uint16_t)(p+4)),storage->legs[i],&entry->journey)) return 0;
    }
    return rd16(segment,p)==65535u;
}
int actor_bridge_scripts(uint16_t segment,DemoResourceStorage *storage) {
    static const uint16_t tables[]={0x1020,0x1792,0x1e40,0x24de,0x2614};
    storage->count=0;
    for(size_t v=0;v<4;v++) {
        uint16_t starts[ACTOR_CAPACITY];size_t count=0;
        for(uint16_t p=tables[v];rd16(segment,p)!=65535u;p=(uint16_t)(p+2)) {
            if(count==ACTOR_CAPACITY-1) return 0;
            starts[count++]=rd16(segment,p);
        }
        for(size_t i=0;i<count;i++) {
            uint16_t begin=starts[i],end=tables[v+1];
            for(size_t j=0;j<count;j++) if(starts[j]>begin && starts[j]<end) end=starts[j];
            if(storage->count==DEMO_SCRIPT_COUNT || end<begin+10u || (size_t)(end-begin-8)>DEMO_CODE_LIMIT) return 0;
            size_t n=storage->count++;DemoMotionScript *script=&storage->scripts[n];
            storage->headers[n]=begin;
            script->initial_pixel_x=rd16(segment,begin);script->initial_pixel_y=rd16(segment,(uint16_t)(begin+2));
            script->period=rd16(segment,(uint16_t)(begin+4));
            uint16_t handler=rd16(segment,(uint16_t)(begin+6));
            if(handler==G(IgnoreActorState)) script->effect=DEMO_EFFECT_NONE;
            else if(handler==G(StartDemoFadeWhenSpriteHidden)) script->effect=DEMO_EFFECT_FADE_ON_HIDDEN;
            else if(handler==G(SetDemoRevealSpriteWidth)) script->effect=DEMO_EFFECT_REVEAL_WIDTH;
            else return 0;
            script->code=storage->code[n];script->code_size=end-begin-8u;
            for(size_t j=0;j<script->code_size;j++) storage->code[n][j]=rd8(segment,(uint16_t)(begin+8+j));
            size_t p=0;
            while(p<script->code_size) {
                if(script->code_size-p<2) return 0;
                uint16_t op=(uint16_t)(script->code[p]+256u*script->code[p+1]);
                size_t width=op<32768u?4:2;
                if(script->code_size-p<width) return 0;
                p+=width;
            }
            if(script->code[script->code_size-2]!=0 || script->code[script->code_size-1]!=128) return 0;
        }
    }
    return storage->count==DEMO_SCRIPT_COUNT;
}
int actor_bridge_script_cursor(const DemoResourceStorage *storage,uint16_t cursor,size_t *script,size_t *offset) {
    for(size_t i=0;i<storage->count;i++) {
        size_t base=storage->headers[i]+8u;
        if(cursor>=base && cursor-base<storage->scripts[i].code_size && demo_script_boundary(&storage->scripts[i],cursor-base)) {
            *script=i;*offset=cursor-base;return 1;
        }
    }
    return 0;
}
int actor_bridge_demo_project(uint16_t segment,const DemoResourceStorage *resources,DemoMotionScene *scene) {
    for(size_t i=0;i<ACTOR_CAPACITY;i++) {
        uint16_t p=actor_read(segment,D(ActorUpdateOrScriptCursor),i);
        if(p==65535u) {scene->count=i;return 1;}
        if(i==ACTOR_CAPACITY-1) return 0;
        size_t script,offset;
        if(!actor_bridge_script_cursor(resources,p,&script,&offset)) return 0;
        DemoMotionSlot *slot=&scene->slots[i];slot->script=&resources->scripts[script];slot->cursor=offset;
        slot->repeat_count=actor_read(segment,D(ActorMotionWaitOrDemoRepeats),i);
        slot->repeat_start=0; /* dormant stale pointer is never resolved */
        if(slot->repeat_count) {
            size_t restart_script;
            if(!actor_bridge_script_cursor(resources,actor_read(segment,D(ActorPhaseOrDemoLoopCursor),i),&restart_script,&slot->repeat_start) || restart_script!=script) return 0;
        }
        slot->countdown=actor_read(segment,D(ActorAnimationCountdowns),i);
        uint16_t done=actor_read(segment,D(ActorPlatformOrScriptDone),i);
        if(done!=0 && done!=65535u) return 0;
        slot->finished=done!=0;
        slot->position.x32=actor_read(segment,D(ActorX32),i);slot->position.y32=actor_read(segment,D(ActorY32),i);
        slot->sprite=actor_read(segment,D(ActorSpriteIds),i);
        if(actor_read(segment,D(ActorVerticalOrDemoPeriod),i)!=slot->script->period) return 0;
        uint16_t effect=slot->script->effect==DEMO_EFFECT_NONE ? G(IgnoreActorState) :
            slot->script->effect==DEMO_EFFECT_FADE_ON_HIDDEN ? G(StartDemoFadeWhenSpriteHidden) : G(SetDemoRevealSpriteWidth);
        if(actor_read(segment,D(ActorOverlayOrScriptCallbacks),i)!=effect) return 0;
    }
    return 0;
}
void actor_bridge_render_project(uint16_t segment,ActorRenderStorage *render) {
    for(size_t i=0;i<ACTOR_CAPACITY;i++) {
        ActorRenderHistory *h=&render->slots[i];
        h->pixel_x=actor_read(segment,D(ActorPixelX),i);h->pixel_y=actor_read(segment,D(ActorPixelY),i);
        h->previous_x=actor_read(segment,D(ActorPreviousDrawX),i);h->previous_y=actor_read(segment,D(ActorPreviousDrawY),i);
        h->erase_sprite=actor_read(segment,D(ActorEraseSprite),i);h->erase_overlay_sprite=actor_read(segment,D(ActorEraseOverlaySprite),i);
    }
}
int actor_bridge_alias_project(uint16_t segment,size_t index,ActorPhase phase,PassengerStoneSlot *slot) {
    if(index>=ACTOR_CAPACITY || (unsigned)phase>=ACTOR_PHASE_COUNT) return 0;
    slot->phase=phase;
#if !defined(NDEBUG) || defined(ACTOR_VERIFY)
    slot->waiting_pose=slot->request_ticks=slot->journey_wait=slot->horizontal_step=slot->floating_ticks=65535u;
    slot->carrier=(size_t)-1;
#endif
    unsigned valid=actor_phase_aliases(phase);
    if(valid&ACTOR_ALIAS_WAITING_POSE) slot->waiting_pose=actor_read(segment,D(ActorPhaseOrDemoLoopCursor),index);
    if(valid&ACTOR_ALIAS_REQUEST_TICKS) slot->request_ticks=actor_read(segment,D(ActorPhaseOrDemoLoopCursor),index);
    if(valid&ACTOR_ALIAS_CARRIER) {
        uint16_t value=actor_read(segment,D(ActorPhaseOrDemoLoopCursor),index);
        if(value!=0 && (value!=2 || rd16(segment,D(PlayerCount))!=2)) return 0;
        slot->carrier=value/2u;
    }
    if(valid&ACTOR_ALIAS_JOURNEY_WAIT) slot->journey_wait=actor_read(segment,D(ActorMotionWaitOrDemoRepeats),index);
    if(valid&ACTOR_ALIAS_HORIZONTAL_STEP) slot->horizontal_step=actor_read(segment,D(ActorMotionWaitOrDemoRepeats),index);
    if(valid&ACTOR_ALIAS_FLOATING_TICKS) slot->floating_ticks=actor_read(segment,D(ActorMotionWaitOrDemoRepeats),index);
    return 1;
}
int actor_bridge_alias_read(const PassengerStoneSlot *slot,ActorAlias member,uint16_t *value) {
    /* This is the sole alias read entry for subsequent passenger bridges.
     * Validation precedes the field access, including verification builds. */
    return actor_alias_value(slot,member,value);
}
