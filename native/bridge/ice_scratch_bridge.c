#include "ugh.h"
#include "../ice_scratch.h"
#include <string.h>

/* Same ordinary, disjoint RAM/resource/stack admission as ice_bridge.c.
 * The wrapper owns the fixed workspace binding; the codec owns decoding.
 * Bad signatures admit any incoming SI (including contiguous words at FFFF).
 * Recognized streams admit the application header-at-zero convention only.
 * Arithmetic flags after decoding are dead at both application return sites. */
EXPORT int c_UnpackIceToScratch(Regs *r) {
    r->es=UGH_S_ZERO_IceDecodeWorkspace;
    r->di=logic(r,0,16);
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
    IceScratchView view={input,sizeof input,output,sizeof output};
    IceScratchResult result;
    IceStatus status=ice_unpack_scratch(&view,&result);
    memcpy(ugh_mem+destination,output,sizeof output);
    r->si=result.source_cursor;
    r->di=result.workspace_cursor;
    return status==ICE_OK || status==ICE_BAD_MAGIC ? UGH_OK :
           status==ICE_LIMIT ? UGH_BUDGET : UGH_UNSUPPORTED;
}
