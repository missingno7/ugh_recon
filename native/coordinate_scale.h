#ifndef NATIVE_COORDINATE_SCALE_H
#define NATIVE_COORDINATE_SCALE_H
#include <stdint.h>
typedef struct {
    uint16_t value;
    uint16_t removed_fraction;
} CoordinateScale;
/* Bit-pattern inputs/results; signed fractions round toward minus infinity.
 * The removed fraction is an observable output, not disposable scratch. */
CoordinateScale scale_level_y(uint16_t value);
CoordinateScale scale_level_speed(uint16_t value);
#endif
