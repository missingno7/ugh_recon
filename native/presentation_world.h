#ifndef NATIVE_PRESENTATION_WORLD_H
#define NATIVE_PRESENTATION_WORLD_H
#include <stdint.h>
typedef struct NativeHudPresentation {
 uint16_t timer_width,cursor_x,cursor_y,layout_x[9],score_words[2],fare,retained_seed,icons[2];
 uint8_t multiplier,lives,counter,fare_pending,digits[2][7];
} NativeHudPresentation;
typedef struct NativeRainRecord {uint16_t position,previous,modulo;} NativeRainRecord;
typedef struct NativeWeatherPresentation {
 NativeRainRecord rain[193];
 uint16_t previous_y,byte_offset,frame;
 uint8_t pending,countdown,phase;
} NativeWeatherPresentation;
typedef struct NativePresentationWorld {
 NativeHudPresentation hud;
 NativeWeatherPresentation weather;
} NativePresentationWorld;
/* Shared water coordinates/step, player caches and actor histories are borrowers,
 * not duplicate members of this presentation owner. */
NativePresentationWorld *native_presentation_world(void);
#endif
