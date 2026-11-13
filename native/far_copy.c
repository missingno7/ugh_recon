#include "far_copy.h"

void copy_ordered_bytes(uint8_t *destination, const uint8_t *source,
                        uint16_t destination_cursor, uint16_t source_cursor,
                        uint16_t count, int backwards) {
    /* Retained: direction and ordered overlap differ from memcpy/memmove. */
    unsigned increment=backwards ? 65535u : 1u;
    for (unsigned copied=0; copied<count; ++copied) {
        destination[destination_cursor]=source[source_cursor];
        source_cursor=(uint16_t)(source_cursor+increment);
        destination_cursor=(uint16_t)(destination_cursor+increment);
    }
}
