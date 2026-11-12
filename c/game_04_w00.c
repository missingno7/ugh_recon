#include "ugh.h"
#include "platform.h"

/* Near entries throughout; no cdecl arguments or hardware except water drawing.
 * DS is the actual input bank, ES/SS/SP and unmentioned registers are preserved.
 * Arithmetic flags are scratch except those produced by the final operation.
 * Original parallel arrays use BYTE indices (normally even 0..22). */
static uint16_t cell(uint16_t base, uint16_t index) { return (uint16_t)(base+index); }
static uint16_t sar5(Regs *r, uint16_t x) {
    uint16_t v=(uint16_t)((x>>5) | ((x&0x8000u) ? 0xf800u : 0));
    flag(r,CF,x&16u); szp(r,v,16); return v; /* OF/AF undefined. */
}
static uint16_t shl5(Regs *r, uint16_t x) {
    uint16_t v=(uint16_t)(x<<5);
    flag(r,CF,x&0x0800u); szp(r,v,16); return v; /* OF/AF undefined. */
}
static uint8_t dec8(Regs *r, uint8_t x) {
    uint8_t v=(uint8_t)(x-1);
    flag(r,OF,x==128); flag(r,AF,((x^1u^v)&16u)!=0); szp(r,v,8);
    return v; /* DEC preserves CF, including at zero. */
}

/* DS: enemy descriptor/counter/cursor/callback arrays; SI always loaded, DI/AX
 * only changed on expiry. Equality-only countdown; zero wraps to FFFF. */
/* TRANSLATES GAME:AdvanceTreeRewardCooldown */
EXPORT int c_AdvanceTreeRewardCooldown(Regs *r) {
    r->si=rd16(r->ds,cell(D(EnemyDescriptors),r->bx));
    uint16_t count=dec16(r,rd16(r->ds,cell(D(EnemyStateCounters),r->bx)));
    wr16(r->ds,cell(D(EnemyStateCounters),r->bx),count);
    if(!count) {
        r->di=rd16(r->ds,cell(D(EnemyAnimationOrDropLists),r->bx));
        uint16_t end=rd16(r->ds,r->di);
        sub16(r,end,65535,0);
        r->ax=rd16(r->ds,(uint16_t)(r->si+(end==65535 ? 0x20 : 0x0a)));
        wr16(r->ds,cell(D(EnemyStateCallbacks),r->bx),r->ax);
    }
    return UGH_OK;
}

/* No inputs beyond the near return frame. Preserves every register and flag. */
/* TRANSLATES GAME:IgnoreExhaustedTree */
EXPORT int c_IgnoreExhaustedTree(Regs *r) { (void)r; return UGH_OK; }

/* DS: item descriptor and slot arrays; SI descriptor, AX/BP launch position,
 * CX horizontal step, DX launch term. Success preserves BX/CX/SI, modifies
 * AX/BP/DX/DI, writes seven slot words. Height uses <<4, NOT <<5.
 * Full-pool RET jumps through saved BX: recognize the actual RET-only callback;
 * other corrupted continuations fail explicitly, never report safe allocation. */
/* TRANSLATES GAME:SpawnFallingItem */
EXPORT int c_SpawnFallingItem(Regs *r) {
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,r->bx);
    r->bx=22;
    for(;;) {
        uint16_t sprite=logic(r,rd16(r->ds,cell(D(FallingItemSprites),r->bx)),16);
        if(sprite&0x8000u) break;
        r->bx=sub16(r,r->bx,2,0);
        if((int16_t)r->bx<0) {
            uint16_t target=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2);
            if(target==G(IgnoreExhaustedTree)) return c_IgnoreExhaustedTree(r);
            /* RET consumed the saved BX, real return frame remains pending. */
            r->ip=target;
            return UGH_BAD_CALLBACK;
        }
    }
    wr16(r->ds,cell(D(FallingItemDescriptors),r->bx),r->si);
    r->di=(uint16_t)(rd16(r->ds,r->si)<<5);
    r->ax=sub16(r,r->ax,r->di,0);
    wr16(r->ds,cell(D(FallingItemX),r->bx),r->ax);
    r->di=(uint16_t)(rd16(r->ds,(uint16_t)(r->si+2))<<4);
    r->bp=sub16(r,r->bp,r->di,0);
    wr16(r->ds,cell(D(FallingItemY),r->bx),r->bp);
    wr16(r->ds,cell(D(FallingItemMotionOrLifetime),r->bx),r->cx);
    r->dx=add16(r,r->dx,rd16(r->ds,(uint16_t)(r->si+12)),0);
    r->dx=sub16(r,0,r->dx,0);
    wr16(r->ds,cell(D(FallingItemVerticalStep),r->bx),r->dx);
    r->ax=rd16(r->ds,(uint16_t)(r->si+16));
    wr16(r->ds,cell(D(FallingItemSprites),r->bx),r->ax);
    r->ax=rd16(r->ds,(uint16_t)(r->si+6));
    wr16(r->ds,cell(D(FallingItemCallbacks),r->bx),r->ax);
    r->bx=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2);
    return UGH_OK;
}

/* DS/BX select item. Loads SI and AX; callback=descriptor+10 and lifetime=560.
 * No flags changed. All motion words except the lifetime alias remain stale. */
/* TRANSLATES GAME:LandFallingItem */
EXPORT int c_LandFallingItem(Regs *r) {
    r->si=rd16(r->ds,cell(D(FallingItemDescriptors),r->bx));
    r->ax=rd16(r->ds,(uint16_t)(r->si+10));
    wr16(r->ds,cell(D(FallingItemCallbacks),r->bx),r->ax);
    wr16(r->ds,cell(D(FallingItemMotionOrLifetime),r->bx),0x230);
    return UGH_OK;
}

/* DS/BX select flight state. AX/SI always changed, CX/DX/DI path dependent.
 * All signed boundaries and shifts are from x86 Jcc/SAR. Offscreen removal
 * changes only the sprite. The landing JMP reads the original near address;
 * every built descriptor uses LandFallingItem, unknown targets fail. */
/* TRANSLATES GAME:AdvanceFallingItem */
EXPORT int c_AdvanceFallingItem(Regs *r) {
    r->si=rd16(r->ds,cell(D(FallingItemDescriptors),r->bx));
    r->ax=rd16(r->ds,cell(D(FallingItemMotionOrLifetime),r->bx));
    r->ax=add16(r,r->ax,rd16(r->ds,cell(D(FallingItemX),r->bx)),0);
    sub16(r,r->ax,0xfe00,0);
    if((int16_t)r->ax<=-512) goto remove;
    sub16(r,r->ax,0x2800,0);
    if((int16_t)r->ax>=0x2800) goto remove;
    wr16(r->ds,cell(D(FallingItemX),r->bx),r->ax);
    r->ax=rd16(r->ds,cell(D(FallingItemVerticalStep),r->bx));
    r->ax=add16(r,r->ax,3,0);
    wr16(r->ds,cell(D(FallingItemVerticalStep),r->bx),r->ax);
    logic(r,r->ax,16);
    if((int16_t)r->ax<0) {
        uint16_t o=cell(D(FallingItemY),r->bx);
        wr16(r->ds,o,add16(r,rd16(r->ds,o),r->ax,0));
        return UGH_OK;
    }
    r->cx=rd16(r->ds,cell(D(FallingItemY),r->bx));
    r->ax=add16(r,r->ax,r->cx,0);
    sub16(r,r->ax,0x1800,0);
    if((int16_t)r->ax>=0x1800) goto remove;
    wr16(r->ds,cell(D(FallingItemY),r->bx),r->ax);
    r->ax=sar5(r,r->ax); r->cx=sar5(r,r->cx);
    r->ax=add16(r,r->ax,rd16(r->ds,(uint16_t)(r->si+2)),0);
    r->cx=add16(r,r->cx,rd16(r->ds,(uint16_t)(r->si+2)),0);
    r->di=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        uint16_t left=logic(r,rd16(r->ds,cell(D(PlatformLeftEdges),r->di)),16);
        if((int16_t)left<0) return UGH_OK;
        uint16_t height=rd16(r->ds,cell(D(PlatformHeights),r->di));
        sub16(r,r->cx,height,0);
        if((int16_t)r->cx>=(int16_t)height) goto next;
        sub16(r,r->ax,height,0);
        if((int16_t)r->ax<(int16_t)height) goto next;
        r->dx=sar5(r,rd16(r->ds,cell(D(FallingItemX),r->bx)));
        r->dx=add16(r,r->dx,rd16(r->ds,r->si),0);
        sub16(r,r->dx,left,0);
        if((int16_t)r->dx<(int16_t)left) goto next;
        r->dx=dec16(r,r->dx);
        uint16_t right=rd16(r->ds,cell(D(PlatformRightEdges),r->di));
        sub16(r,r->dx,right,0);
        if((int16_t)r->dx>(int16_t)right) goto next;
        r->ax=rd16(r->ds,cell(D(PlatformHeights),r->di));
        r->ax=sub16(r,r->ax,rd16(r->ds,(uint16_t)(r->si+2)),0);
        r->ax=shl5(r,r->ax);
        wr16(r->ds,cell(D(FallingItemY),r->bx),r->ax);
        if(rd16(r->ds,(uint16_t)(r->si+8))==G(LandFallingItem)) return c_LandFallingItem(r);
        return UGH_BAD_CALLBACK;
next:
        r->di=add16(r,r->di,2,0);
    }
    return UGH_BUDGET;
remove:
    wr16(r->ds,cell(D(FallingItemSprites),r->bx),65535);
    return UGH_OK;
}

/* DS: score/lives. AX=0, arithmetic flags from XOR; other registers preserved.
 * Multiplier initialization writes ONE BYTE; its adjacent byte remains stale.
 * The score-only loc_396D entry is not an independent adapter here. */
/* TRANSLATES GAME:ResetScoreLivesAndMultiplier */
EXPORT int c_ResetScoreLivesAndMultiplier(Regs *r) {
    wr8(r->ds,D(LivesRemaining),3); wr8(r->ds,D(ScoreMultiplier),1);
    r->ax=logic(r,0,16);
    wr16(r->ds,D(ScoreLowWord),r->ax); wr16(r->ds,D(ScoreHighWord),r->ax);
    return UGH_OK;
}

/* The following strings transcribe the unrolled STORE OPERANDS, not executable
 * bytes or a converted game record. A/B/C/D/E select live AH/BL/BH/CL/CH.
 * Each row is one ordered 80-store plane run; offsets wrap independently. */
static const char water_frame0[] =
    "CDDBAACDCCBBBDDDCBBCCDBACCDCAACDCCCBBDDDCBBCCDBAACDDBAACDCCBBBDDDCBBCDCAABECCCBB"
    "CECAAADDCCBBBDDDBBBCCCAACDDBAACDCCBBBDDDCBBCCDBAACECAAADDCCBBBDDDBBCCDCAACDCCCBB"
    "CDCAABECCCBBDDDDBBBCCCAACECAAADDCCBBBDDDBBBCCCAABCDCAABECCCBBDDDDBBCDDBAACDCCBBB"
    "CDCAACDCCCBBDDDCBBCCDBAACDCAABECCCBBDDDDBBBCCCAACCDCAACDCCCBBDDDCBBCECAAADDCCBBB"
    ;
static const char water_frame1[] =
    "CECCBBBBBBCCDDDDEEEEEDCCCECCBBBBBBBCDDEDEEEEEDCCCCECCBBBBBBCCDDDDEEEEDCBBBBBBBCD"
    "DECCBBBBBBCDDEDDEEEEEDCCCECCBBBBBBCCDDDDEEEEEDCCCDECCBBBBBBCDDEDDEECECCBBBBBBBCD"
    "EDCBBBBBBBCDDEDDEEEEECCCDECCBBBBBBCDDEDDEEEEEDCCCEDCBBBBBBBCDDEDDEECECCBBBBBBCCD"
    "ECCBBBBBBBCDDEDEEEEEDCCCEDCBBBBBBBCDDEDDEEEEECCCCECCBBBBBBBCDDEDEEEDECCBBBBBBCDD"
    ;
static const char water_frame2[] =
    "DDDDCCCCCCDEEEDDEDEEDDDDDDDDCCCBCCCDEEDDEDEEEDDDDDDDDCCCCCCDEEEDDEDEDDDDCCBCCCDE"
    "DDDDCCBCCCDEEEDDEDEEDDDDDDDDCCCCCCDEEEDDEDEEDDDDDDDDDCCBCCCDEEEDDEDDDDDCCCBCCCDE"
    "DDDDCCBCCCDEEEDDDEEEDDDDDDDDCCBCCCDEEEDDEDEEDDDDDDDDDCCBCCCDEEEDDDEDDDDCCCCCCDEE"
    "DDDCCCBCCCDEEDDEDEEEDDDDDDDDCCBCCCDEEEDDDEEEDDDDDDDDCCCBCCCDEEDDEDEDDDDCCBCCCDEE"
    ;

static int water_tail(Regs *r, const char *pattern) {
    for(unsigned plane=0;plane<4;plane++) {
        for(unsigned x=0;x<80;x++) {
            uint8_t value;
            switch(pattern[plane*80+x]) {
            case 'A': value=(uint8_t)(r->ax>>8); break;
            case 'B': value=(uint8_t)r->bx; break;
            case 'C': value=(uint8_t)(r->bx>>8); break;
            case 'D': value=(uint8_t)r->cx; break;
            default: value=(uint8_t)(r->cx>>8); break;
            }
            wr8(r->ds,(uint16_t)(r->di+x),value);
        }
        if(plane<3) {
            uint8_t old=(uint8_t)r->ax, value=(uint8_t)(old<<1);
            flag(r,CF,old&128); flag(r,OF,((old^value)&128)!=0);
            szp(r,value,8); set_al(r,value);
            platform_out(r->dx,1,value);
        }
    }
    set_al(r,15); platform_out(r->dx,1,15);
    r->ds=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2);
    return UGH_OK;
}

/* TAIL ABI, not ordinary near CALL: SS:SP holds saved DS followed by near
 * return IP. DS:DI destination, DX=3C5 with sequencer index 2 and mask 1;
 * live AH/BL/BH/CL/CH colors (dispatcher supplies 54..58). Restores DS,
 * consumes its word, AL=15, other general registers preserved. Defined final
 * SHL flags CF/PF/ZF/SF/OF; DF/IF unchanged. Four ordered 80-byte plane runs. */
/* TRANSLATES GAME:DrawWaterSurfaceFrame0 */
EXPORT int c_DrawWaterSurfaceFrame0(Regs *r) { return water_tail(r,water_frame0); }
/* TRANSLATES GAME:DrawWaterSurfaceFrame1 */
EXPORT int c_DrawWaterSurfaceFrame1(Regs *r) { return water_tail(r,water_frame1); }
/* TRANSLATES GAME:DrawWaterSurfaceFrame2 */
EXPORT int c_DrawWaterSurfaceFrame2(Regs *r) { return water_tail(r,water_frame2); }

/* Near entry. DS supplies frame/countdown/Y/stride; CS page pointer and dispatch
 * table supply destination and original target. ES/BP preserved. AX/BX/CX/DX/
 * SI/DI changed; DS restored by frame tail. No clipping: AL(Y)*byte(stride),
 * 16-bit destination offset and doubled frame index wrap. Countdown is DEC8/
 * JNS, so 80h becomes 7Fh and does NOT reload. No hardware waits. */
/* TRANSLATES GAME:DrawWaterSurface */
EXPORT int c_DrawWaterSurface(Regs *r) {
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,r->ds);
    r->si=rd16(r->ds,D(WaterSurfaceFrame));
    uint8_t countdown=dec8(r,rd8(r->ds,D(WaterSurfaceFrameCountdown)));
    wr8(r->ds,D(WaterSurfaceFrameCountdown),countdown);
    if(countdown&128u) {
        wr8(r->ds,D(WaterSurfaceFrameCountdown),6);
        r->si=dec16(r,r->si);
        if((int16_t)r->si<0) r->si=2;
        wr16(r->ds,D(WaterSurfaceFrame),r->si);
    }
    r->ax=(uint16_t)((uint8_t)rd16(r->ds,D(WaterYPixels))*rd8(r->ds,D(VgaRowStrideBytes)));
    wr16(r->ds,D(WaterSurfaceByteOffset),r->ax);
    r->di=rd16(r->cs,G(DrawPagePointer)); r->ds=rd16(r->cs,G(DrawPagePointer)+2);
    r->di=add16(r,r->di,r->ax,0);
    r->dx=0x3c4; set_al(r,2); platform_out(r->dx,1,2);
    uint16_t cf=r->flags&CF;
    r->dx=add16(r,r->dx,1,0); flag(r,CF,cf);
    r->ax=0x5401; platform_out(r->dx,1,1);
    r->bx=0x5655; r->cx=0x5857;
    uint16_t old=r->si; r->si=(uint16_t)(r->si<<1);
    flag(r,CF,old&0x8000); flag(r,OF,((old^r->si)&0x8000)!=0); szp(r,r->si,16);
    uint16_t target=rd16(r->cs,cell(G(WaterSurfaceDispatch),r->si));
    if(target==G(DrawWaterSurfaceFrame0)) return c_DrawWaterSurfaceFrame0(r);
    if(target==G(DrawWaterSurfaceFrame1)) return c_DrawWaterSurfaceFrame1(r);
    if(target==G(DrawWaterSurfaceFrame2)) return c_DrawWaterSurfaceFrame2(r);
    return UGH_BAD_CALLBACK;
}
