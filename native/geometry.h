/* Geometry borrowed by contacts, not an object/state-machine representation. */
#ifndef NATIVE_GEOMETRY_H
#define NATIVE_GEOMETRY_H
#include <stdint.h>
typedef struct ObjectGeometry {
    /* Descriptor +0/+2, pixel anchor words: GAME:2278/22A7,22F3/2322. */
    uint16_t anchor_x, anchor_y;
    /* Descriptor +4/+6; subtracted twice vertically, once either side in X.
     * Falling items instead use the literal 3 in both fields (2209..2259).
     * Words are bit patterns; scaling/addition wraps before signed comparison. */
    uint16_t extent_x, extent_y;
} ObjectGeometry;
typedef struct ObjectPosition {
    /* Current X32/Y32 arrays, not the rendering pixel caches. G:2196..2362. */
    uint16_t x32, y32;
} ObjectPosition;
#endif
