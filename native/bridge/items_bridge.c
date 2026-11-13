#include "ugh.h"
#include "../items.h"

int l1_SpawnFallingItem(Regs *r);
int l1_AdvanceFallingItem(Regs *r);
int l1_LandFallingItem(Regs *r);
int l1_ExpireOrCollectFallingItem(Regs *r);

static uint16_t item_word(Regs *r,uint16_t base,uint16_t index) {
    return rd16(r->ds,(uint16_t)(base+index));
}
static FallingItemType item_type(Regs *r,uint16_t descriptor) {
    FallingItemType type;
    type.geometry.anchor_x=rd16(r->ds,descriptor);
    type.geometry.anchor_y=rd16(r->ds,(uint16_t)(descriptor+2));
    type.geometry.extent_x=3;type.geometry.extent_y=3;
    type.launch_impulse=rd16(r->ds,(uint16_t)(descriptor+12));
    type.amount=rd16(r->ds,(uint16_t)(descriptor+14));
    type.sprite=rd16(r->ds,(uint16_t)(descriptor+16));
    uint16_t kind=rd16(r->ds,(uint16_t)(descriptor+18));
    type.benefit=kind==0?ITEM_TIMER:kind==1?ITEM_LIVES:ITEM_MULTIPLIER;
    return type;
}
static FallingItem item_project(Regs *r,uint16_t index) {
    FallingItem item;
    item.type=item_type(r,item_word(r,D(FallingItemDescriptors),index));
    item.phase=item_word(r,D(FallingItemCallbacks),index)==G(ExpireOrCollectFallingItem)?ITEM_LANDED:ITEM_FLIGHT;
    item.sprite=item_word(r,D(FallingItemSprites),index);
    item.position.x32=item_word(r,D(FallingItemX),index);
    item.position.y32=item_word(r,D(FallingItemY),index);
    item.vertical_step=item_word(r,D(FallingItemVerticalStep),index);
    item.motion_or_lifetime=item_word(r,D(FallingItemMotionOrLifetime),index);
    return item;
}
static void item_publish(Regs *r,uint16_t index,const FallingItem *item) {
    wr16(r->ds,(uint16_t)(D(FallingItemSprites)+index),item->sprite);
    wr16(r->ds,(uint16_t)(D(FallingItemX)+index),item->position.x32);
    wr16(r->ds,(uint16_t)(D(FallingItemY)+index),item->position.y32);
    wr16(r->ds,(uint16_t)(D(FallingItemVerticalStep)+index),item->vertical_step);
    wr16(r->ds,(uint16_t)(D(FallingItemMotionOrLifetime)+index),item->motion_or_lifetime);
}
static int item_ordinary(Regs *r,uint16_t descriptor) {
    /* This projection samples an immutable descriptor. Mutable descriptor/output
     * aliases retain L1's sequential reads, including the maintained alias case.
     * Effective descriptor offsets may wrap; its operand bytes are contiguous. */
    if(r->bx>22 || (r->bx&1)) return 0;
    if(lin(r->ds,0)<0xc0000u && lin(r->ds,65535)>=0xa0000u) return 0;
    for(unsigned i=0;i<20;i++) {
        uint16_t at=(uint16_t)(descriptor+i);
        if(at>=D(FallingItemDescriptors) && at<D(FallingItemMotionOrLifetime)+24) return 0;
        if(at>=D(LivesRemaining) && at<D(ScoreMultiplier)+2) return 0;
        if(at>=D(LevelTimer) && at<D(LevelTimer)+2) return 0;
    }
    return 1;
}
static uint16_t item_sar(Regs *r,uint16_t value) {
    flag(r,CF,value&16u);
    value=(uint16_t)((value>>5)|((value&32768u)?63488u:0));szp(r,value,16);return value;
}
static uint16_t item_shl(Regs *r,uint16_t value) {
    flag(r,CF,value&2048u);value=(uint16_t)(value<<5);szp(r,value,16);return value;
}
static uint8_t item_byte_add(Regs *r,uint8_t a,uint8_t b) {
    uint8_t value=(uint8_t)(a+b);
    flag(r,CF,(unsigned)a+b>255);flag(r,OF,((~(a^b))&(a^value)&128)!=0);
    flag(r,AF,((a^b^value)&16)!=0);szp(r,value,8);return value;
}

EXPORT int c_SpawnFallingItem(Regs *r) {
    /* Incoming BX is a saved caller value, not an item index. */
    uint16_t saved=r->bx;r->bx=0;
    int ordinary=item_ordinary(r,r->si);r->bx=saved;
    if(!ordinary) return l1_SpawnFallingItem(r);
    FallingItem slots[12];
    for(unsigned i=0;i<12;i++) slots[i].sprite=item_word(r,D(FallingItemSprites),(uint16_t)(2*i));
    FallingItemType type=item_type(r,r->si);
    ObjectPosition launch={r->ax,r->bp};
    ItemSpawnResult result=items_spawn(slots,type,launch,r->cx,r->dx);
    r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,saved);
    r->bx=22;
    while(result.status==ITEM_POOL_FULL || r->bx!=(uint16_t)(result.slot*2)) {
        logic(r,item_word(r,D(FallingItemSprites),r->bx),16);
        r->bx=sub16(r,r->bx,2,0);
        if(r->bx==65534u) {
            uint16_t target=rd16(r->ss,r->sp);r->sp=(uint16_t)(r->sp+2);
            /* Exact L1 abnormal RET boundary: the caller return is pending.
             * The RET-only target can continue; every other target stays open. */
            if(target==G(IgnoreExhaustedTree)) return UGH_OK;
            r->ip=target;return UGH_CONTROL_TRANSFER;
        }
    }
    logic(r,item_word(r,D(FallingItemSprites),r->bx),16);
    FallingItem *item=&slots[result.slot];
    wr16(r->ds,(uint16_t)(D(FallingItemDescriptors)+r->bx),r->si);
    r->di=(uint16_t)(type.geometry.anchor_x<<5);r->ax=sub16(r,r->ax,r->di,0);
    r->di=(uint16_t)(type.geometry.anchor_y<<4);r->bp=sub16(r,r->bp,r->di,0);
    r->dx=add16(r,r->dx,type.launch_impulse,0);r->dx=sub16(r,0,r->dx,0);
    item_publish(r,r->bx,item);
    r->ax=type.sprite;r->ax=rd16(r->ds,(uint16_t)(r->si+6));
    wr16(r->ds,(uint16_t)(D(FallingItemCallbacks)+r->bx),r->ax);
    r->bx=rd16(r->ss,r->sp);r->sp=(uint16_t)(r->sp+2);return UGH_OK;
}
EXPORT int c_LandFallingItem(Regs *r) {
    uint16_t descriptor=item_word(r,D(FallingItemDescriptors),r->bx);
    if(!item_ordinary(r,descriptor)) return l1_LandFallingItem(r);
    FallingItem item=item_project(r,r->bx);item_land(&item);
    r->si=descriptor;r->ax=rd16(r->ds,(uint16_t)(descriptor+10));
    wr16(r->ds,(uint16_t)(D(FallingItemCallbacks)+r->bx),r->ax);
    wr16(r->ds,(uint16_t)(D(FallingItemMotionOrLifetime)+r->bx),item.motion_or_lifetime);
    return UGH_OK;
}
EXPORT int c_AdvanceFallingItem(Regs *r) {
    uint16_t descriptor=item_word(r,D(FallingItemDescriptors),r->bx);
    if(!item_ordinary(r,descriptor) || rd16(r->ds,(uint16_t)(descriptor+8))!=G(LandFallingItem))
        return l1_AdvanceFallingItem(r);
    LevelPlatform platforms[10];size_t count=0;
    for(;;) {
        uint16_t left=item_word(r,D(PlatformLeftEdges),(uint16_t)(count*2));
        if(left&32768u) break;
        if(count==10) return l1_AdvanceFallingItem(r);
        platforms[count].left=left;
        platforms[count].right=item_word(r,D(PlatformRightEdges),(uint16_t)(count*2));
        platforms[count].surface_y=item_word(r,D(PlatformHeights),(uint16_t)(count*2));count++;
    }
    FallingItem before=item_project(r,r->bx),item=before;
    item.phase=ITEM_FLIGHT; /* direct flight entry, independent of stale handler */
    ItemFlightResult result=item_update(&item,platforms,count,0,0,0).flight;
    r->si=descriptor;
    r->ax=add16(r,before.motion_or_lifetime,before.position.x32,0);
    sub16(r,r->ax,65024u,0);
    if(result.exit==ITEM_OUT_LEFT) goto done;
    sub16(r,r->ax,10240,0);
    if(result.exit==ITEM_OUT_RIGHT) goto done;
    r->ax=add16(r,before.vertical_step,3,0);logic(r,r->ax,16);
    if(result.exit==ITEM_RISING) { add16(r,before.position.y32,r->ax,0);goto done; }
    r->cx=before.position.y32;r->ax=add16(r,r->ax,r->cx,0);sub16(r,r->ax,6144,0);
    if(result.exit==ITEM_OUT_BOTTOM) goto done;
    r->ax=item_sar(r,r->ax);r->cx=item_sar(r,r->cx);
    r->ax=add16(r,r->ax,before.type.geometry.anchor_y,0);
    r->cx=add16(r,r->cx,before.type.geometry.anchor_y,0);
    r->di=logic(r,0,16);
    /* Replay only the machine shell. Transition decisions and slot writes are
     * the native result; ordinary loop comparisons reconstruct scratch flags. */
    for(size_t i=0;i<=result.platform;i++) {
        uint16_t left=i==count?item_word(r,D(PlatformLeftEdges),(uint16_t)(2*i)):platforms[i].left;
        logic(r,left,16);
        if(i==count) break;
        uint16_t height=platforms[i].surface_y;
        sub16(r,r->cx,height,0);
        if((int16_t)r->cx<(int16_t)height) {
            sub16(r,r->ax,height,0);
            if((int16_t)r->ax>=(int16_t)height) {
                r->dx=item_sar(r,item.position.x32);r->dx=add16(r,r->dx,before.type.geometry.anchor_x,0);
                sub16(r,r->dx,left,0);
                if((int16_t)r->dx>=(int16_t)left) {
                    r->dx=dec16(r,r->dx);sub16(r,r->dx,platforms[i].right,0);
                }
            }
        }
        if(result.exit==ITEM_TOUCHDOWN && i==result.platform) {
            r->ax=sub16(r,height,before.type.geometry.anchor_y,0);r->ax=item_shl(r,r->ax);
            r->ax=rd16(r->ds,(uint16_t)(descriptor+10));break;
        }
        r->di=add16(r,r->di,2,0);
    }
done:
    item_publish(r,r->bx,&item);
    if(result.exit==ITEM_TOUCHDOWN)
        wr16(r->ds,(uint16_t)(D(FallingItemCallbacks)+r->bx),r->ax);
    return UGH_OK;
}
EXPORT int c_ExpireOrCollectFallingItem(Regs *r) {
    uint16_t descriptor=item_word(r,D(FallingItemDescriptors),r->bx);
    if(!item_ordinary(r,descriptor)) return l1_ExpireOrCollectFallingItem(r);
    FallingItem item=item_project(r,r->bx);
    ObjectPosition players[2];
    for(unsigned i=0;i<2;i++) {
        players[i].x32=item_word(r,D(PlayerX32),(uint16_t)(2*i));
        players[i].y32=item_word(r,D(PlayerY32),(uint16_t)(2*i));
    }
    uint16_t count=rd16(r->ds,D(PlayerCount)),difficulty=rd16(r->ds,D(SelectedDifficulty));
    ItemBenefits before={rd16(r->ds,D(LevelTimer)),rd16(r->ds,D(ScoreMultiplier)),
        item_word(r,D(MultiplierLimitsByDifficulty),(uint16_t)(difficulty*2u)),rd8(r->ds,D(LivesRemaining))};
    ItemBenefits benefits=before;
    item.phase=ITEM_LANDED; /* direct landed entry admits any lifetime word */
    ItemCollectionResult result=item_update(&item,0,0,players,count,&benefits).collection;
    dec16(r,item_word(r,D(FallingItemMotionOrLifetime),r->bx));
    wr16(r->ds,(uint16_t)(D(FallingItemMotionOrLifetime)+r->bx),item.motion_or_lifetime);
    if(result.expired) goto done;
    r->si=descriptor;r->ax=result.contact.boundary;
    r->di=result.contact.index<0?65535u:(uint16_t)(2*result.contact.index);
    if(result.contact.index<0) sub16(r,count==2?4:2,count,0);
    else sub16(r,r->ax,players[result.contact.index].x32,0);
    logic(r,r->di,16);
    if(!result.collected) return UGH_OK;
    r->ax=rd16(r->ds,(uint16_t)(descriptor+18));sub16(r,r->ax,0,0);
    if(item.type.benefit==ITEM_TIMER) {
        r->ax=add16(r,item.type.amount,before.timer,0);sub16(r,r->ax,23099,0);
        r->ax=benefits.timer;wr16(r->ds,D(LevelTimer),benefits.timer);
    } else {
        sub16(r,r->ax,1,0);
        if(item.type.benefit==ITEM_LIVES) {
            r->ax=item.type.amount;set_al(r,item_byte_add(r,(uint8_t)r->ax,before.lives));
            uint8_t a=(uint8_t)r->ax,v=(uint8_t)(a-99u);
            flag(r,CF,a<99);flag(r,OF,((a^99u)&(a^v)&128)!=0);
            flag(r,AF,((a^99u^v)&16)!=0);szp(r,v,8);
            set_al(r,benefits.lives);wr8(r->ds,D(LivesRemaining),benefits.lives);
        } else {
            r->ax=before.multiplier;
            uint16_t v=difficulty;
            for(unsigned i=0;i<1;i++) { flag(r,CF,v&32768u);v=(uint16_t)(v<<1); }
            szp(r,v,16);flag(r,OF,!!(v&32768u)^!!(r->flags&CF));r->di=v;
            sub16(r,r->ax,before.multiplier_limit,0);
            if(before.multiplier<before.multiplier_limit) {
                uint16_t carry=r->flags&CF;set_al(r,item_byte_add(r,(uint8_t)r->ax,1));flag(r,CF,carry);
                wr8(r->ds,D(ScoreMultiplier),(uint8_t)benefits.multiplier);
            }
        }
    }
done:
    wr16(r->ds,(uint16_t)(D(FallingItemSprites)+r->bx),item.sprite);return UGH_OK;
}
EXPORT int c_DispatchFallingItems(Regs *r) {
    FallingItem slots[12];size_t cursor=12;r->bx=22;
    /* Reproject sprite identities after each callback; dispatch never snapshots
     * a future callback list. Unknown stored words keep the L1 dispatch error. */
    for(;;) {
        for(unsigned i=0;i<12;i++) slots[i].sprite=item_word(r,D(FallingItemSprites),(uint16_t)(2*i));
        int selected=items_next(slots,&cursor);
        while(r->bx!=(selected<0?65534u:(uint16_t)(2*selected))) {
            sub16(r,item_word(r,D(FallingItemSprites),r->bx),65535u,0);
            r->bx=sub16(r,r->bx,2,0);
        }
        if(selected<0) return UGH_OK;
        sub16(r,slots[selected].sprite,65535u,0);
        uint16_t target=item_word(r,D(FallingItemCallbacks),r->bx);
        int status=ugh_call_near(target,(uint16_t)(G(DispatchFallingItems)+17),r);
        if(status) return status;
        r->bx=sub16(r,r->bx,2,0);
    }
}
