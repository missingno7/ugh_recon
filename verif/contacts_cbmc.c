/* Actual maintained L1 functions and L2 C, not a hand-written predicate model.
 * Normalized read-only RAM: arbitrary descriptor words, player positions,
 * platform words and count. No geometry/range/reachability assumptions.
 * For stone scanning, exactly STONES entries followed by FFFF, STONES<=16. */
void __CPROVER_assume(_Bool);
void __CPROVER_assert(_Bool,const char *);
typedef struct ContactInputs {
    uint16_t descriptor[4], count, platforms[2];
    ObjectPosition players[2], object;
    StoneContactView stones[STONES];
    uint16_t stone_descriptors[STONES], stone_handlers[STONES];
} ContactInputs;
static ContactInputs input;
static uint16_t input_word(uint16_t address) {
    if(address>=256 && address<264) return input.descriptor[(address-256)/2];
    if(address==D(PlayerCount)) return input.count;
    if(address>=D(PlayerX32) && address<D(PlayerX32)+4) return input.players[(address-D(PlayerX32))/2].x32;
    if(address>=D(PlayerY32) && address<D(PlayerY32)+4) return input.players[(address-D(PlayerY32))/2].y32;
    if(address>=D(PlayerPlatformIndices) && address<D(PlayerPlatformIndices)+4) return input.platforms[(address-D(PlayerPlatformIndices))/2];
#if KIND==3
    if(address>=D(ActorDescriptors) && address<=D(ActorDescriptors)+2*STONES) {
        unsigned i=(address-D(ActorDescriptors))/2;return i==STONES?65535u:input.stone_descriptors[i];
    }
    if(address>=D(ActorUpdateOrScriptCursor) && address<D(ActorUpdateOrScriptCursor)+2*STONES) return input.stone_handlers[(address-D(ActorUpdateOrScriptCursor))/2];
    if(address>=D(ActorVerticalOrDemoPeriod) && address<D(ActorVerticalOrDemoPeriod)+2*STONES) return input.stones[(address-D(ActorVerticalOrDemoPeriod))/2].vertical_step;
    if(address>=D(ActorX32) && address<D(ActorX32)+2*STONES) return input.stones[(address-D(ActorX32))/2].position.x32;
    if(address>=D(ActorY32) && address<D(ActorY32)+2*STONES) return input.stones[(address-D(ActorY32))/2].position.y32;
#endif
    if(address==D(EnemyX32) || address==D(ActorX32) || address==D(FallingItemX)) return input.object.x32;
    if(address==D(EnemyY32) || address==D(ActorY32) || address==D(FallingItemY)) return input.object.y32;
    __CPROVER_assert(0,"read stays in declared contact footprint");return 0;
}
uint16_t contacts_read_word(uint16_t segment,uint16_t address) {
    /* Optional equivalent word-RAM shim, avoiding duplicate byte-array muxes.
     * The admitted footprint has no overlapping words or devices. Both byte
     * and word profiles use exactly the same unconstrained input fields. */
    __CPROVER_assert(segment==0,"normalized read-only word RAM");
    return input_word(address);
}
uint8_t ugh_read(uint32_t address) {
    /* Arrays have both odd and even physical bases. Byte selection is relative
     * to each field base, never alignment of the physical address itself. */
    unsigned byte=0;
    __CPROVER_assert(address<65536u,"normalized segment footprint");
#define BYTES(base,size) if(address>=(base) && address<(base)+(size)) byte=(address-(base))&1u; else
    BYTES(256u,8u)
    BYTES(D(PlayerCount),2u)
    BYTES(D(PlayerX32),4u)
    BYTES(D(PlayerY32),4u)
    BYTES(D(PlayerPlatformIndices),4u)
#if KIND==3
    BYTES(D(ActorDescriptors),2u*(STONES+1u))
    BYTES(D(ActorUpdateOrScriptCursor),2u*STONES)
    BYTES(D(ActorVerticalOrDemoPeriod),2u*STONES)
    BYTES(D(ActorX32),2u*STONES)
    BYTES(D(ActorY32),2u*STONES)
#endif
    BYTES(D(EnemyX32),2u)
    BYTES(D(EnemyY32),2u)
    BYTES(D(ActorX32),2u)
    BYTES(D(ActorY32),2u)
    BYTES(D(FallingItemX),2u)
    BYTES(D(FallingItemY),2u)
    { __CPROVER_assert(0,"read byte stays in contact footprint"); }
#undef BYTES
    return (uint8_t)(input_word((uint16_t)(address-byte))>>(byte*8u));
}
void ugh_write(uint32_t address,uint8_t value) {
    (void)address;(void)value;__CPROVER_assert(0,"contacts never write RAM");
}
int main(void) {
    ContactInputs arbitrary;input=arbitrary;
    Regs old;old.ds=0;old.si=256;old.bx=0;
#if BRIDGE
    Regs modern=old;
#endif
    ObjectGeometry geometry={input.descriptor[0],input.descriptor[1],input.descriptor[2],input.descriptor[3]};
    ContactSelection result;
#if KIND==3
    for(unsigned i=0;i<STONES;i++) {
        __CPROVER_assume(input.stone_descriptors[i]!=65535u);
        input.stones[i].thrown_stone=input.stone_descriptors[i]==D(Data_78DC) && input.stone_handlers[i]==G(UpdateThrownStone);
    }
    int status=l1_FindThrownStoneHittingEnemy(&old);
    result=contact_stones(input.stones,STONES,input.object);
#else
#if KIND==0
    geometry.extent_x=3;geometry.extent_y=3;
    int status=l1_FindPlayerTouchingFallingItem(&old);
#elif KIND==1
    int status=l1_FindPlayerTouchingActor(&old);
#else
    int status=l1_FindPlayerTouchingEnemy(&old);
#endif
    result=contact_players(input.object,geometry,input.players,input.count);
#endif
    uint16_t index=result.index<0?65535u:(uint16_t)(result.index*2);
    __CPROVER_assert(status==0 && old.di==index,"first contact selection");
#if KIND==1
    __CPROVER_assert(old.ax==(result.index<0?result.boundary:input.platforms[result.index]),"actor platform and miss scratch");
#else
    __CPROVER_assert(old.ax==result.boundary,"last boundary or sentinel scratch");
#endif
    __CPROVER_assert(!!(old.flags&SF)==(result.index<0),"caller-observed miss sign");
    __CPROVER_assert(!!(old.flags&ZF)==(result.index==0),"caller-observed first-slot zero");
    __CPROVER_assert(!(old.flags&(CF|OF)),"TEST clears carry/overflow");
#if BRIDGE
#if KIND==0
    int bridge_status=c_FindPlayerTouchingFallingItem(&modern);
#elif KIND==1
    int bridge_status=c_FindPlayerTouchingActor(&modern);
#elif KIND==2
    int bridge_status=c_FindPlayerTouchingEnemy(&modern);
#else
    int bridge_status=c_FindThrownStoneHittingEnemy(&modern);
#endif
    __CPROVER_assert(bridge_status==status && old.ax==modern.ax && old.di==modern.di && old.flags==modern.flags,"bridge outputs and complete flags including L1 AF");
    __CPROVER_assert(old.bx==modern.bx && old.cx==modern.cx && old.dx==modern.dx && old.si==modern.si && old.bp==modern.bp && old.sp==modern.sp && old.cs==modern.cs && old.ds==modern.ds && old.es==modern.es && old.ss==modern.ss && old.ip==modern.ip,"preserved complete bridge shell");
#endif
    return 0;
}
