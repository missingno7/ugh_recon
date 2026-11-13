#include "ugh.h"
#include "../far_copy.h"

/* RAM-only projection. Arguments are sampled before writes, as in L1.
 * Excludes VGA, code, concurrent IRQ writes, and live L0 save/return words. */
EXPORT int c_CopyFarBytes(Regs *r) {
    uint16_t source=arg16(r,4), source_segment=arg16(r,6);
    uint16_t destination=arg16(r,8), destination_segment=arg16(r,10);
    uint16_t count=arg16(r,0);
    copy_ordered_bytes(ugh_mem+lin(destination_segment,0),
                       ugh_mem+lin(source_segment,0),destination,source,count,
                       (r->flags&DF)!=0);
    r->cx=0; /* Retained: RestoreAdlibVoiceAllocation observes the zero. */
    return UGH_OK;
}
