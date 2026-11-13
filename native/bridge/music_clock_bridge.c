#include "ugh.h"
#include "../music_clock.h"

EXPORT int c_SwapDwordByteOrder(Regs *r)
{
    uint32_t value = arg16(r,0) | (uint32_t)arg16(r,2) * 65536u;
    uint32_t result = music_clock_swap_bytes(value);
    r->ax = (uint16_t)result;
    r->dx = (uint16_t)(result >> 16);
    return UGH_OK;
}

EXPORT int c_DisableMusicSectionLoop(Regs *r)
{
    r->es = SOUND_SEG;
    uint16_t playing = rd16(SOUND_SEG,S(MainAdlxPlaying));
    /* Do not introduce an inactive-path read/write of the loop flag. */
    if (playing)
        wr16(SOUND_SEG,S(MainAdlxSectionLoopEnabled),
             music_clock_disable_section_loop(playing,0));
    r->ax = 1;
    return UGH_OK;
}

EXPORT int c_GetElapsedMusicTime(Regs *r)
{
    r->es = SOUND_SEG;
    uint32_t ticks = rd32(SOUND_SEG,S(AdlxTickCount));
    uint32_t origin = rd32(SOUND_SEG,S(MainAdlxTimeOrigin));
    uint16_t rate = rd16(SOUND_SEG,S(MusicTicksPerUnit));
    MusicClockResult result = music_clock_elapsed(ticks,origin,rate);
    if (result.status == MUSIC_CLOCK_DIVIDE_BY_ZERO)
        return UGH_UNSUPPORTED; /* L1's explicit representation of original INT 0. */
    r->ax = (uint16_t)result.units;
    r->dx = (uint16_t)(result.units >> 16);
    return UGH_OK;
}
