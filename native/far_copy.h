#ifndef NATIVE_FAR_COPY_H
#define NATIVE_FAR_COPY_H
#include <stdint.h>
/* Two borrowed 65536-byte rings, which may overlap at any byte alignment.
 * Each iteration reads before writing. Cursors wrap; count zero does no work.
 * Storage must be ordinary initialized RAM, without concurrent modification. */
void copy_ordered_bytes(uint8_t *destination, const uint8_t *source,
                        uint16_t destination_cursor, uint16_t source_cursor,
                        uint16_t count, int backwards);
#endif
