#include "ugh.h"

/* TRANSLATES SOUND:ClearSoundState
 * Called by C:InitializeSoundSystem. Resident bytes following this interval survive. */
EXPORT int c_ClearSoundState(Regs *r) {
    for(unsigned i=0;i<0x488;i++) wr8(SOUND_SEG,(uint16_t)(UGH_O_SOUND_ext_0664+i),0);
    r->ax=logic(r,0,16); r->cx=0; flag(r,DF,0);
    return UGH_OK;
}
