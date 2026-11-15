#ifndef NATIVE_FRONT_END_WORLD_H
#define NATIVE_FRONT_END_WORLD_H
#include <stdint.h>
/* Raw CP437 fields. The terminators belong to these physical allocations;
 * the password's biased comparison anchor is a view, never another buffer.
 * File contents/positions/active handles remain a service, not a second table. */
typedef struct NativeFrontEndWorld {
 uint8_t score_rows[107];
 uint8_t name_entry[13];
 uint8_t password[21];
 uint8_t level_characters[2];
 uint8_t row_stride;
 uint8_t file_handle_bytes[2];
 uint8_t difficulty_text[6];
 uint8_t players_text[10];
 uint8_t control_text[2][10];
} NativeFrontEndWorld;
/* Invocation-lifetime continuations; no historical RAM allocation. */
typedef struct NativeFrontEditor { uint16_t position, blink_word; } NativeFrontEditor;
typedef struct NativeFrontTextCursor { uint16_t position, x, y; } NativeFrontTextCursor;
NativeFrontEndWorld *native_front_end_world(void);
#endif
