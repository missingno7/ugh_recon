#ifndef NATIVE_ICE_SCRATCH_H
#define NATIVE_ICE_SCRATCH_H
#include "ice.h"

/* Borrowed storage, owned by the resource loader, not by the decoder. The
 * packed header is at source[0]. The two available byte windows are disjoint;
 * full 65536-byte windows retain malformed-stream wrap and seed-byte reads.
 * No allocation, clearing, or implicit workspace initialization takes place. */
typedef struct IceScratchView {
    const uint8_t *source;
    size_t source_size;
    uint8_t *workspace;
    size_t workspace_size;
} IceScratchView;

typedef struct IceScratchResult {
    IceResult decoder;
    uint16_t source_cursor;
    uint16_t workspace_cursor;
} IceScratchResult;

/* The scratch entry starts the workspace cursor at zero. Only a completed
 * decode publishes the decoder's local cursors. On bad magic the signature
 * scan is published; on decoder errors the header cursor remains ten. Partial
 * workspace writes survive, including the retained two-million-token guard.
 * TRUNCATED/RANGE are the codec's storage-safety extensions, not DOS returns. */
IceStatus ice_unpack_scratch(const IceScratchView *view, IceScratchResult *result);
#endif
