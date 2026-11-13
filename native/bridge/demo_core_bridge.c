#include "actor_projection.h"
#include "../demo_core.h"
int l1_InitializeDemoScripts(Regs *r);
int l1_AdvanceDemoScripts(Regs *r);
int l1_TestAllDemoScriptsFinished(Regs *r);
static int demo_bridge_environment(const Regs *r) {
    return r->ds==DATA_SEG && r->cs==GAME_SEG && !(r->flags&DF) &&
        rd16(r->cs,G(DemoRevealWidthPointer))==UGH_O_B5B63_SpriteDirectory_214+2 &&
        rd16(r->cs,(uint16_t)(G(DemoRevealWidthPointer)+2))==UGH_S_B5B63_SpriteDirectory_214;
}
static void demo_bridge_word(Regs *r,uint16_t base,size_t i,uint16_t value) {
    wr16(r->ds,(uint16_t)(base+2*i),value);
}
static int demo_bridge_advance(Regs *r,DemoResourceStorage *resources,DemoMotionScene *scene) {
    DemoStep effects[ACTOR_CAPACITY];
    /* Validate the entire control walk before publishing any effects. This
     * lets malformed script states fall back without a partial native step. */
    for(size_t i=0;i<scene->count;i++) if(!demo_advance_slot(&scene->slots[i],&effects[i])) return -1;
    r->bx=logic(r,0,16);
    for(size_t i=0;i<scene->count;i++) {
        DemoMotionSlot *slot=&scene->slots[i];DemoStep *effect=&effects[i];
        demo_bridge_word(r,D(ActorAnimationCountdowns),i,slot->countdown);
        if(effect->repeat_written) demo_bridge_word(r,D(ActorMotionWaitOrDemoRepeats),i,slot->repeat_count);
        size_t resource=(size_t)(slot->script-resources->scripts);
        uint16_t base=(uint16_t)(resources->headers[resource]+8);
        if(effect->restart_written) demo_bridge_word(r,D(ActorPhaseOrDemoLoopCursor),i,(uint16_t)(base+slot->repeat_start));
        if(effect->stopped) {demo_bridge_word(r,D(ActorPlatformOrScriptDone),i,65535u);r->ax=0;}
        if(effect->motion) {
            demo_bridge_word(r,D(ActorSpriteIds),i,slot->sprite);
            demo_bridge_word(r,D(ActorX32),i,slot->position.x32);
            demo_bridge_word(r,D(ActorY32),i,slot->position.y32);
            r->ax=effect->last_delta;r->si=(uint16_t)(base+slot->cursor);
            uint16_t target=slot->script->effect==DEMO_EFFECT_NONE ? G(IgnoreActorState) :
                slot->script->effect==DEMO_EFFECT_FADE_ON_HIDDEN ? G(StartDemoFadeWhenSpriteHidden) : G(SetDemoRevealSpriteWidth);
            /* Retain the real near frame and the complete stored-handler set.
             * Callback reads see new position/sprite and the OLD slot cursor. */
            int status=ugh_call_near(target,(uint16_t)(G(AdvanceDemoScripts)+0x42),r);
            if(status) return status;
        }
        if(effect->motion || effect->stopped) demo_bridge_word(r,D(ActorUpdateOrScriptCursor),i,(uint16_t)(base+slot->cursor));
        r->bx=(uint16_t)(r->bx+2);
    }
    r->si=65535u;sub16(r,r->si,65535u,0);return UGH_OK;
}
EXPORT int c_AdvanceDemoScripts(Regs *r) {
    DemoResourceStorage resources;DemoMotionScene scene;
    if(!demo_bridge_environment(r) || !actor_bridge_scripts(r->ds,&resources) ||
        !actor_bridge_demo_project(r->ds,&resources,&scene)) return l1_AdvanceDemoScripts(r);
    int result=demo_bridge_advance(r,&resources,&scene);
    return result<0 ? l1_AdvanceDemoScripts(r) : result;
}
EXPORT int c_InitializeDemoScripts(Regs *r) {
    DemoResourceStorage resources;DemoMotionScene scene;ActorRenderStorage render;
    if(!demo_bridge_environment(r) || !actor_bridge_scripts(r->ds,&resources)) return l1_InitializeDemoScripts(r);
    const DemoMotionScript *scripts[ACTOR_CAPACITY];size_t count=0;
    /* Only the four registered vectors are admitted. Synthetic/wrapping/alias
     * fixtures continue to execute the independent literal implementation. */
    if(r->si!=0x1020 && r->si!=0x1792 && r->si!=0x1e40 && r->si!=0x24de) return l1_InitializeDemoScripts(r);
    for(;;) {
        uint16_t header=rd16(r->ds,(uint16_t)(r->si+2*count));
        if(header==65535u) break;
        if(count==ACTOR_CAPACITY-1) return l1_InitializeDemoScripts(r);
        size_t n=0;while(n<resources.count && resources.headers[n]!=header) n++;
        if(n==resources.count) return l1_InitializeDemoScripts(r);
        scripts[count++]=&resources.scripts[n];
    }
    actor_bridge_render_project(r->ds,&render);
    demo_initialize(&scene,&render,scripts,count);
    for(size_t i=0;i<count;i++) {
        const DemoMotionSlot *slot=&scene.slots[i];const ActorRenderHistory *h=&render.slots[i];
        size_t n=(size_t)(slot->script-resources.scripts);
        demo_bridge_word(r,D(ActorPixelX),i,h->pixel_x);demo_bridge_word(r,D(ActorPreviousDrawX),i,h->previous_x);
        demo_bridge_word(r,D(ActorPixelY),i,h->pixel_y);demo_bridge_word(r,D(ActorPreviousDrawY),i,h->previous_y);
        demo_bridge_word(r,D(ActorX32),i,slot->position.x32);demo_bridge_word(r,D(ActorY32),i,slot->position.y32);
        demo_bridge_word(r,D(ActorVerticalOrDemoPeriod),i,slot->script->period);
        demo_bridge_word(r,D(ActorOverlayOrScriptCallbacks),i,rd16(r->ds,(uint16_t)(resources.headers[n]+6)));
        demo_bridge_word(r,D(ActorUpdateOrScriptCursor),i,(uint16_t)(resources.headers[n]+8));
        demo_bridge_word(r,D(ActorAnimationCountdowns),i,1);demo_bridge_word(r,D(ActorMotionWaitOrDemoRepeats),i,0);
        demo_bridge_word(r,D(ActorPlatformOrScriptDone),i,0);
    }
    demo_bridge_word(r,D(ActorUpdateOrScriptCursor),count,65535u);
    /* The non-actor reset contributions remain at their existing L1 boundary. */
    r->di=65535u;r->bx=(uint16_t)(2*count);
    int status=ugh_call_near(G(ResetSpriteEraseState),(uint16_t)(G(InitializeDemoScripts)+0x60),r);
    if(status) return status;
    /* Publish the actor reset from the persistent renderer object as well. */
    for(size_t i=0;i<ACTOR_CAPACITY;i++) {
        demo_bridge_word(r,D(ActorSpriteIds),i,scene.slots[i].sprite);
        demo_bridge_word(r,D(ActorEraseSprite),i,render.slots[i].erase_sprite);
    }
    return demo_bridge_advance(r,&resources,&scene);
}
EXPORT int c_TestAllDemoScriptsFinished(Regs *r) {
    DemoMotionScene scene;scene.count=0;
    if(!demo_bridge_environment(r)) return l1_TestAllDemoScriptsFinished(r);
    for(size_t i=0;i<ACTOR_CAPACITY;i++) {
        if(rd16(r->ds,(uint16_t)(D(ActorUpdateOrScriptCursor)+2*i))==65535u) {scene.count=i;break;}
        if(i==ACTOR_CAPACITY-1) return l1_TestAllDemoScriptsFinished(r);
        uint16_t done=rd16(r->ds,(uint16_t)(D(ActorPlatformOrScriptDone)+2*i));
        scene.slots[i].finished=done!=0;scene.count=i+1;
    }
    int finished=demo_all_finished(&scene);
    r->bx=logic(r,0,16);
    if(finished) {r->bx=(uint16_t)(2*scene.count);sub16(r,65535u,65535u,0);flag(r,CF,1);}
    else {
        size_t i=0;while(scene.slots[i].finished) i++;
        r->bx=(uint16_t)(2*(i+1));logic(r,0,16);flag(r,CF,0);
        /* L1 LOGIC retains AF from the preceding ADD BX,2. */
        flag(r,AF,(((uint16_t)(2*i)^2u^r->bx)&16u)!=0);
    }
    return UGH_OK;
}
