#include "ugh.h"
#include "../ice.h"
#include <string.h>

/* Projection: ordinary RAM, disjoint source-read/output-write footprints,
 * immutable ICE tables, header at
 * zero on the recognized path. Bad magic retains arbitrary incoming SI.
 * No VGA/device aperture and no overlap with the live stack or code tables.
 * Successful caller observations: output RAM, SI/DI, preserved registers and
 * segments, DF clear. Arithmetic flags are dead at every application caller.
 */
EXPORT int c_UnpackIceStream(Regs *r) {
    uint16_t first=rd16(r->ds,r->si); r->si+=2; flag(r,DF,0);
    if (first!=0x4349) return UGH_OK;
    uint16_t second=rd16(r->ds,r->si); r->si+=2;
    if (second!=0x2145) return UGH_OK;
    if (r->si!=4) return UGH_UNSUPPORTED;
    uint32_t source=lin(r->ds,0), destination=lin(r->es,0);
    unsigned packed=rd8(r->ds,6)*256u+rd8(r->ds,7);
    unsigned unpacked=rd8(r->ds,10)*256u+rd8(r->ds,11);
    if (!packed) packed=65536u;
    if (!unpacked) unpacked=65536u;
    if (source<destination+unpacked && destination<source+packed) return UGH_UNSUPPORTED;
    uint8_t input[65536], output[65536];
    memcpy(input,ugh_mem+source,sizeof input);
    memcpy(output,ugh_mem+destination,sizeof output);
    IceResult result;
    IceStatus status=ice_decode(input,sizeof input,output,sizeof output,&result);
    memcpy(ugh_mem+destination,output,sizeof output);
    if (status==ICE_OK) {
        r->si=(uint16_t)result.source_cursor; r->di=(uint16_t)result.destination_cursor;
        return UGH_OK;
    }
    /* The L1 guard returns before publishing its local cursors. */
    r->si=10;
    return status==ICE_LIMIT ? UGH_BUDGET : UGH_UNSUPPORTED;
}
