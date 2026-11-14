#include "ice_scratch.h"

IceStatus ice_unpack_scratch(const IceScratchView *view, IceScratchResult *result) {
    IceStatus status=ice_decode(view->source,view->source_size,
                                view->workspace,view->workspace_size,&result->decoder);
    result->workspace_cursor=0;
    result->source_cursor=10;
    if (status==ICE_OK) {
        result->source_cursor=(uint16_t)result->decoder.source_cursor;
        result->workspace_cursor=(uint16_t)result->decoder.destination_cursor;
    } else if (status==ICE_BAD_MAGIC) {
        result->source_cursor=(uint16_t)result->decoder.source_cursor;
    }
    return status;
}
