#ifndef NATIVE_HUD_H
#define NATIVE_HUD_H
#include <stdint.h>
#include "render_primitives.h"

/* Borrowed canonical HUD values. Byte fields are imported zero-extended;
 * projection changes only their original byte, not its neighbor. */
typedef struct HudValues {
    uint16_t cursor_x,cursor_y,lives,cached_lives,score_low,score_high,cached_score_low,cached_score_high;
    uint16_t journeys,cached_journeys,icon_one,cached_icon_one,icon_two,cached_icon_two;
    uint16_t destination_one,destination_two,players,fare_one,fare_two,cached_fare,clear_fare;
    uint16_t multiplier,cached_multiplier,timer,fade_step,fade_level,divisor,bar_width;
    uint16_t lives_x,score_x,journeys_x,icon_one_x,icon_two_x,destination_one_x,destination_two_x,fare_x,multiplier_x;
} HudValues;
typedef enum HudStage {HUD_LIVES,HUD_SCORE,HUD_JOURNEYS,HUD_ICON_ONE,HUD_ICON_TWO,
    HUD_FARE,HUD_MULTIPLIER,HUD_TIMER,HUD_DONE} HudStage;
typedef enum HudField {HF_CURSOR_X,HF_CURSOR_Y,HF_LIVES,HF_SCORE_LOW,HF_SCORE_HIGH,
    HF_CACHED_SCORE_LOW,HF_CACHED_SCORE_HIGH,HF_JOURNEYS,HF_ICON_ONE,HF_ICON_TWO,
    HF_FARE,HF_CLEAR_FARE,HF_MULTIPLIER,HF_TIMER,HF_FADE_STEP,HF_FADE_LEVEL,HF_BAR_WIDTH} HudField;
typedef enum HudEffectKind {HUD_STORE,HUD_NUMBER_TWO,HUD_NUMBER_FOUR,HUD_NUMBER_SIX,
    HUD_SPRITE,HUD_BAR,HUD_DIVISION_ERROR} HudEffectKind;
typedef struct HudEffect {HudEffectKind kind;HudField field;uint16_t a,b,c,d,e;} HudEffect;
typedef struct HudResult {HudEffect effects[8];unsigned count;HudStage next;} HudResult;
typedef struct HudDigitDecision {uint16_t next_x,next_index;uint8_t done,draw;} HudDigitDecision;
typedef struct HudBarSpec {uint16_t cell,remaining;uint8_t cumulative,mask_index,value;} HudBarSpec;

RenderDrawRequest hud_digit(uint8_t digit,uint16_t x,uint16_t y);
RenderDrawRequest hud_border(uint16_t players,uint8_t second);
uint16_t hud_advance(uint16_t x);
HudDigitDecision hud_changed_digit(uint8_t current,uint8_t previous,uint16_t x,uint16_t index);
HudResult hud_lives(HudValues values);
HudResult hud_score(HudValues values);
HudResult hud_journeys(HudValues values);
HudResult hud_icon_one(HudValues values);
HudResult hud_icon_two(HudValues values);
HudResult hud_fare(HudValues values);
HudResult hud_multiplier(HudValues values);
HudResult hud_timer(HudValues values);
void hud_project_store(HudValues *values,HudEffect effect);
HudBarSpec hud_bar(uint16_t width,uint16_t previous);
uint16_t hud_bar_next(HudBarSpec *bar);
uint16_t hud_bar_row(uint16_t cell,uint8_t row);
#endif
