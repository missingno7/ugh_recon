/* Portable translations of two leaf entries from src/c/module.c.
 * Far cdecl; incoming DS, SI, DI, BP, SS/SP and IF/DF are preserved.
 * AX is the result; BX/CX/DX and arithmetic flags are compiler scratch.
 * Neither entry performs I/O or calls another application routine. */
#include "ugh.h"

/* One signed word argument. Only x > 12 rejects before loading ES; negative
 * indices use the low word of IMUL x,42 (0F41). Loaded bit 4 is tested at +28h.
 * Success copies the unnormalized far pointer +06h to +10h, segment first,
 * leaving deadline/repeat/flags untouched. Slot 12 aliases MainAdlxCursor.
 * ES is unchanged on x>12, otherwise SOUND. */
/* TRANSLATES C:ResetAdlibTrackChannelCursor */
EXPORT int c_ResetAdlibTrackChannelCursor(Regs *r) {
    int16_t slot=(int16_t)arg16(r,0);
    if(slot>12) { r->ax=0xffff; return UGH_OK; }
    uint16_t record=(uint16_t)(S(AudioChannelStates)+(uint16_t)(slot*42));
    r->es=SOUND_SEG;
    if(!(rd16(r->es,(uint16_t)(record+0x28))&4)) {
        r->ax=0xffff; return UGH_OK;
    }
    uint16_t segment=rd16(r->es,(uint16_t)(record+0x08));
    uint16_t offset=rd16(r->es,(uint16_t)(record+0x06));
    wr16(r->es,(uint16_t)(record+0x12),segment);
    wr16(r->es,(uint16_t)(record+0x10),offset);
    r->ax=1;
    return UGH_OK;
}

/* SHARED-REQUEST: generated aliases for compiler-owned switch storage/targets
 * are absent. Keep local entry-relative displacements until cgen exposes them.
 * They identify the exact 1B95 table and its eight original near targets, not
 * game state or guessed live segment values. */
#define DURATION_AT(delta) ((uint16_t)(UGH_O_C_GetMusicTrackDuration+(delta)))
static int duration_arm(uint16_t cs, uint8_t code) {
    unsigned nibble=code>>4;
    if(nibble>7) return 8;
    uint16_t target=rd16(cs,DURATION_AT(0x107+2*nibble));
    switch(target) {
    case DURATION_AT(0x92): return 0; /* 1B20 long wait */
    case DURATION_AT(0xae): return 1; /* 1B3C frequency */
    case DURATION_AT(0xb4): return 2; /* 1B42 key off */
    case DURATION_AT(0xb6): return 3; /* 1B44 volume */
    case DURATION_AT(0xb8): return 4; /* 1B46 instrument */
    case DURATION_AT(0xbe): return 6; /* 1B4C timer */
    case DURATION_AT(0xc0): return 7; /* 1B4E extension, including 77 */
    case DURATION_AT(0xd0): return 8; /* 1B5E default, also nibble 5 */
    default: return -1;
    }
}

/* No arguments. AX is low 16 bits of the unsigned 32-bit wait sum divided by
 * ticks/unit. ES always returns SOUND, including early zero returns. Inputs
 * are SOUND device bit 0, playing, rate, start far pointer and word length.
 * 1AF1/1B07/1B72: far-pointer segment stays fixed; offsets wrap, comparison is
 * unsigned offset-only. 1B32 truncates a long wait BEFORE adding to the dword.
 * Payload reads/skips ignore end; 5n adds code&7F, 77 consumes a length byte.
 * Runtime F_LUDIV@ is expressed as unsigned C division, not a matching claim. */
/* TRANSLATES C:GetMusicTrackDuration */
EXPORT int c_GetMusicTrackDuration(Regs *r) {
    r->es=SOUND_SEG;
    if(!(rd16(r->es,S(SoundDeviceBits))&1) ||
       !rd16(r->es,S(MainAdlxPlaying)) || !rd16(r->es,S(MusicTicksPerUnit))) {
        r->ax=0; return UGH_OK;
    }
    uint16_t p=rd16(r->es,S(MainAdlxStartPointer));
    uint16_t segment=rd16(r->es,(uint16_t)(S(MainAdlxStartPointer)+2));
    uint16_t end=(uint16_t)(p+rd16(r->es,S(MusicEventStreamLength)));
    uint32_t total=0;
    unsigned budget=5000000; /* malformed offset cycles must fail finitely */
    while(p<end) {
        if(!budget--) return UGH_BUDGET;
        uint8_t code=rd8(segment,p); p=(uint16_t)(p+1);
        int arm=duration_arm(r->cs,code);
        switch(arm) {
        case 0:
            total+=(uint16_t)(((uint16_t)code*256u+rd8(segment,p))*128u);
            p=(uint16_t)(p+1); break;
        case 1: case 6: p=(uint16_t)(p+2); break;
        case 2: break;
        case 3: p=(uint16_t)(p+1); break;
        case 4: p=(uint16_t)(p+11); break;
        case 7: p=(uint16_t)(p+rd8(segment,p)+1); break;
        case 8: total+=(code&0x7f); break;
        default: return UGH_BAD_CALLBACK;
        }
    }
    /* Reload divisor as compiled code does after scanning, rather than cache it. */
    r->ax=(uint16_t)(total/rd16(SOUND_SEG,S(MusicTicksPerUnit)));
    return UGH_OK;
}
