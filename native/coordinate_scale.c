#include "coordinate_scale.h"

static uint16_t floor_fraction(uint16_t value, unsigned shift) {
    return (uint16_t)((value>>shift) |
                      ((value&32768u) ? (65535u<<(16u-shift)) : 0u));
}
CoordinateScale scale_level_y(uint16_t value) {
    uint16_t fraction=floor_fraction(value,2);
    return (CoordinateScale){(uint16_t)(value-fraction),fraction};
}
CoordinateScale scale_level_speed(uint16_t value) {
    uint16_t fraction=floor_fraction(value,1);
    /* Retained: result wraps at 16 bits, including signed overflow. */
    return (CoordinateScale){(uint16_t)(value+fraction),fraction};
}
