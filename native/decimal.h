#ifndef NATIVE_DECIMAL_H
#define NATIVE_DECIMAL_H
#include <stdint.h>
#include <stddef.h>
/* Divisors are live little-endian byte references: output may alias them. */
typedef struct {
    const uint8_t *ten, *hundred, *thousand, *ten_thousand;
} DecimalDivisors;
typedef struct {
    uint8_t *bytes;
    size_t capacity, cursor;
} DecimalOutput;
typedef enum { DECIMAL_OK, DECIMAL_DIVISION_ERROR } DecimalStatus;
typedef struct {
    DecimalStatus status;
    /* Last division's packed byte pair and thousand-stage remainder.
     * Kept for bridge diagnostics, including a failed division's partial work. */
    uint16_t last_pair, thousand_remainder;
} DecimalResult;
/* Numeric bytes, including leading zeros, then 255. Cursor points AT sentinel.
 * Positive capacity; cursor below capacity; valid initialized divisor bytes.
 * Full DOS wrap is retained with capacity 65536. Smaller rings are an extension.
 * No digit clamping or ASCII conversion. Division failure retains partial writes. */
DecimalResult decimal_two(uint8_t value, DecimalOutput *output, DecimalDivisors divisors);
DecimalResult decimal_four(uint16_t value, DecimalOutput *output, DecimalDivisors divisors);
DecimalResult decimal_six(uint32_t value, DecimalOutput *output, DecimalDivisors divisors);
#endif
