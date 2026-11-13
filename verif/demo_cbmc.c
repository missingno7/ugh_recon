/* Actual C relational proofs. RAM is normalized to disjoint scalar actor
 * cells plus one bytecode window; devices, source aliases and callbacks that
 * mutate interpreter input are excluded. The callback is an observation cut
 * after motion, before cursor publication; its real complete target set is
 * exercised by the compiled shipped enumeration and L0 integration suites. */
void __CPROVER_assume(_Bool);
void __CPROVER_assert(_Bool,const char *);
static uint8_t code[16];
static uint16_t cursor,restart,repeats,countdown,period,xword,yword,sprite,done;
static unsigned callbacks;
static uint16_t callback_x,callback_y,callback_sprite,callback_cursor;
uint16_t demo_read16(uint16_t segment,uint16_t address) {
    __CPROVER_assert(segment==0,"normalized ordinary RAM");
    if(address>=0x4000 && address<0x400f) return (uint16_t)(code[address-0x4000]+256u*code[address-0x4000+1]);
    if(address==D(ActorUpdateOrScriptCursor)) return cursor;
    if(address==D(ActorUpdateOrScriptCursor)+2) return 65535u;
    if(address==D(ActorPhaseOrDemoLoopCursor)) return restart;
    if(address==D(ActorMotionWaitOrDemoRepeats)) return repeats;
    if(address==D(ActorAnimationCountdowns)) return countdown;
    if(address==D(ActorVerticalOrDemoPeriod)) return period;
    if(address==D(ActorX32)) return xword;
    if(address==D(ActorY32)) return yword;
    if(address==D(ActorSpriteIds)) return sprite;
    if(address==D(ActorOverlayOrScriptCallbacks)) return G(IgnoreActorState);
    __CPROVER_assert(0,"read stays in declared footprint");return 0;
}
uint8_t demo_read8(uint16_t segment,uint16_t address) {
    __CPROVER_assert(segment==0 && address>=0x4000 && address<0x4010,"bytecode delta footprint");
    return code[address-0x4000];
}
void demo_write16(uint16_t segment,uint16_t address,uint16_t value) {
    __CPROVER_assert(segment==0,"normalized writable RAM");
    if(address==D(ActorUpdateOrScriptCursor)) cursor=value;
    else if(address==D(ActorPhaseOrDemoLoopCursor)) restart=value;
    else if(address==D(ActorMotionWaitOrDemoRepeats)) repeats=value;
    else if(address==D(ActorAnimationCountdowns)) countdown=value;
    else if(address==D(ActorX32)) xword=value;
    else if(address==D(ActorY32)) yword=value;
    else if(address==D(ActorSpriteIds)) sprite=value;
    else if(address==D(ActorPlatformOrScriptDone)) done=value;
    else __CPROVER_assert(0,"write stays in declared footprint");
}
int demo_callback(Regs *r,uint16_t target) {
    __CPROVER_assert(target==G(IgnoreActorState),"callback cut has known identity");
    callbacks++;callback_x=xword;callback_y=yword;callback_sprite=sprite;callback_cursor=r->si;
    return 0;
}
int main(void) {
#ifdef DEMO_PROOF_ARITHMETIC
    uint8_t value;uint16_t pixel;
    /* The runner extracts both reference helper bodies from maintained L1
     * statements verbatim, then supplies only their scalar/memory bindings. */
    Regs r={0};r.si=0x4000;code[0]=value;
    __CPROVER_assert(demo_delta(value)==reference_delta_value(&r),"all signed-byte deltas");
    r.ax=pixel;
    __CPROVER_assert(demo_pixel_position(pixel)==reference_pixel_value(&r),"all pixel word seeds");
#else
    uint8_t input_code[16];
    uint16_t initial_repeat,initial_count,initial_period,initial_x,initial_y,initial_sprite;
    uint16_t initial_restart;unsigned initial_done;
    for(unsigned i=0;i<16;i++) code[i]=input_code[i];
    __CPROVER_assume(initial_done<=1);
    repeats=initial_repeat;countdown=initial_count;period=initial_period;
    xword=initial_x;yword=initial_y;sprite=initial_sprite;done=initial_done?65535u:0;
    cursor=0x4000;restart=(uint16_t)(0x4000+initial_restart);
    DemoMotionScript script={0,0,initial_period,DEMO_EFFECT_NONE,code,16};
    DemoMotionSlot slot={&script,0,initial_restart,initial_repeat,initial_count,initial_done,{initial_x,initial_y},initial_sprite};
    DemoStep effects={0};Regs r={0};r.si=0x4000;
#ifdef DEMO_PROOF_INSTRUCTION
    reference_instruction(&r);
    demo_instruction(&slot,&effects);
    __CPROVER_assert((uint16_t)(0x4000+slot.cursor)==r.si,"instruction cursor relation");
#else
    /* Full countdown-to-yield proof on a canonical control window: any first
     * word, arbitrary deltas, then accessible motion at fallthrough/restart.
     * The instruction proof above admits every opcode and repeat state
     * independently of this composition shape. */
    __CPROVER_assume((code[3]&128u)==0 && (code[9]&128u)==0);
    restart=0x4008;slot.repeat_start=8;
    __CPROVER_assert(l1_AdvanceDemoScripts(&r)==0,"L1 step returns");
    __CPROVER_assert(demo_advance_slot(&slot,&effects),"native step returns");
    __CPROVER_assert(slot.cursor==(size_t)(cursor-0x4000),"tick cursor relation");
    __CPROVER_assert(slot.countdown==countdown,"all countdown/period word patterns");
#endif
    __CPROVER_assert(slot.repeat_count==repeats,"repeat encoding including positive and wrap");
#ifdef DEMO_PROOF_INSTRUCTION
    /* The retained restart is wholly arbitrary, even outside this window.
     * This instruction never dereferences it; only a subsequent transition
     * imposes its own accessible-instruction precondition. */
    __CPROVER_assert((uint16_t)(0x4000+slot.repeat_start)==restart,"restart relation including stale");
#else
    __CPROVER_assert(slot.repeat_start==(size_t)(restart-0x4000),"restart relation including stale");
#endif
    __CPROVER_assert(slot.finished==(done!=0),"sticky completion relation");
    __CPROVER_assert(slot.position.x32==xword && slot.position.y32==yword && slot.sprite==sprite,"motion and sprite relation");
    __CPROVER_assert(callbacks==(unsigned)effects.motion,"exactly one ordered callback on motion");
    if(effects.motion) {
        __CPROVER_assert(callback_x==slot.position.x32 && callback_y==slot.position.y32 && callback_sprite==slot.sprite,"callback sees new sprite and positions");
        __CPROVER_assert(callback_cursor==(uint16_t)(0x4000+slot.cursor),"callback cursor before store");
        __CPROVER_assert(r.ax==effects.last_delta,"retained last delta");
    }
#endif
    return 0;
}
