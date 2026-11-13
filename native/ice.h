#ifndef NATIVE_ICE_H
#define NATIVE_ICE_H
#include <stddef.h>
#include <stdint.h>

typedef enum IceStatus {
    ICE_OK, ICE_BAD_MAGIC, ICE_TRUNCATED, ICE_RANGE, ICE_LIMIT
} IceStatus;

typedef struct IceResult {
    size_t source_cursor;       /* next backward byte index (65535 after wrap) */
    size_t destination_cursor;
    size_t bytes_written;      /* counts writes, including repeated locations */
    unsigned tokens;
} IceResult;

/* DOS Pack-Ice dialect. Header starts at source[0]; buffers must not overlap.
 * Sizes are available storage, not header values. Output is in/out: malformed
 * references may read its seed bytes. High size words and initial output cursor
 * are ignored, as in DOS. Every backward index wraps modulo 65536; supply full
 * 65536-byte buffers to retain all malformed/wrapping behavior. Smaller buffers
 * return ICE_RANGE before an unavailable access. Partial writes remain on error.
 * A short header returns ICE_TRUNCATED. Bad magic writes nothing. The token
 * limit is the L1 harness's 2000000-iteration guard, not a DOS-format rule.
 * Result is always initialized. No allocation, I/O, device or global state.
 */
IceStatus ice_decode(const uint8_t *source, size_t source_size,
                     uint8_t *output, size_t output_size, IceResult *result);
#endif
