/* Translated copy of the three named src/c/module.c functions. See architecture.md:
 * GCC has 32-bit int and native pointers; deleting far/huge is not a compatibility layer.
 * All shared lvalues still address assembly-owned memory. */
#include "ugh.h"

/* TRANSLATES C:SwapDwordByteOrder */
EXPORT int c_SwapDwordByteOrder(Regs *r) {
    uint32_t x=arg16(r,0) | (uint32_t)arg16(r,2)*65536u;
    uint32_t y=(x>>24) | ((x>>8)&0xff00u) | ((x<<8)&0xff0000u) | (x<<24);
    r->ax=(uint16_t)y; r->dx=(uint16_t)(y>>16); return UGH_OK;
}

/* TRANSLATES C:DisableMusicSectionLoop */
EXPORT int c_DisableMusicSectionLoop(Regs *r) {
    r->es=SOUND_SEG; /* Borland loads far globals through ES and leaves it live. */
    if(rd16(SOUND_SEG,S(MainAdlxPlaying))) wr16(SOUND_SEG,S(MainAdlxSectionLoopEnabled),0);
    r->ax=1; return UGH_OK;
}

/* TRANSLATES C:GetElapsedMusicTime */
EXPORT int c_GetElapsedMusicTime(Regs *r) {
    r->es=SOUND_SEG;
    uint32_t ticks=rd32(SOUND_SEG,S(AdlxTickCount));
    uint32_t origin=rd32(SOUND_SEG,S(MainAdlxTimeOrigin));
    uint16_t rate=rd16(SOUND_SEG,S(MusicTicksPerUnit));
    if(!rate) return UGH_UNSUPPORTED; /* original INT 0, not a guessed answer */
    uint32_t result=(uint32_t)(ticks-origin)/rate;
    r->ax=(uint16_t)result; r->dx=(uint16_t)(result>>16); return UGH_OK;
}
