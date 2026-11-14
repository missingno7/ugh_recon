#ifndef NATIVE_MENUS_H
#define NATIVE_MENUS_H
#include <stdint.h>
#include "front_end.h"
typedef enum MenusTextKind {MENUS_TEXT_GLYPH,MENUS_TEXT_END,MENUS_TEXT_LINE,MENUS_TEXT_HALF_LINE} MenusTextKind;
typedef struct MenusTextStep {MenusTextKind kind;uint16_t glyph;uint8_t character,y_advance;} MenusTextStep;
MenusTextStep menus_text_step(uint8_t character);
int menus_text_centered(uint8_t first);
uint16_t menus_text_center_x(uint16_t count);
uint16_t menus_text_next_x(uint16_t x);
uint16_t menus_text_next_y(uint16_t y,uint8_t delimiter);
uint16_t menus_center_credits(uint16_t separators);
uint16_t menus_double_index(uint16_t index);
typedef struct MenusStringCopy {uint16_t source,destination;int8_t direction;uint8_t done;} MenusStringCopy;
MenusStringCopy menus_string_begin(uint16_t source,uint16_t destination,int reverse);
void menus_string_read(MenusStringCopy *copy,uint8_t character);
void menus_string_written(MenusStringCopy *copy);
typedef struct MenusControlCandidate {uint16_t mode,index;uint8_t keyboard;} MenusControlCandidate;
MenusControlCandidate menus_control_next(uint16_t mode);
int menus_control_present(uint16_t presence);
typedef enum MenusControlKey {MENUS_CONTROL_RESTART,MENUS_CONTROL_QUIT,MENUS_CONTROL_PLAYER0,MENUS_CONTROL_PLAYER1} MenusControlKey;
MenusControlKey menus_control_key(uint8_t scan);
uint16_t menus_difficulty_next(uint16_t difficulty);
void menus_toggle_players(FrontConfiguration *configuration);
int menus_session_complete(uint16_t level,uint16_t limit);
int16_t menus_credits_result(uint8_t scan);
uint16_t menus_water(unsigned screen);
uint16_t menus_attract_map_offset(int second);
int menus_draw_water(uint16_t y);
typedef struct MenusLabel {uint16_t index,destination;} MenusLabel;
MenusLabel menus_label(unsigned kind,uint16_t value);
uint8_t menus_level_ordinal(uint8_t level);
uint8_t menus_ascii_digit(uint8_t digit);
typedef struct MenusMapCopy {uint16_t source,destination,remaining;int8_t direction;} MenusMapCopy;
MenusMapCopy menus_map_begin(uint16_t source,uint16_t destination,int reverse);
void menus_map_advance(MenusMapCopy *copy);
typedef struct MenusHeaderItem {uint16_t sprite,x;} MenusHeaderItem;
MenusHeaderItem menus_header_item(unsigned ordinal,uint16_t previous_sprite);

/* Services are named by front-end purpose, not original code identities.
 * Reply is a fresh projection after the preceding synchronous service. */
typedef enum MenusMainAction {
 MENUS_MAIN_STOP_MUSIC,MENUS_MAIN_START_MUSIC,MENUS_MAIN_REVEAL,MENUS_MAIN_CREDITS,
 MENUS_MAIN_ATTRACT,MENUS_MAIN_SCORES,MENUS_MAIN_PREPARE_PALETTE,MENUS_MAIN_PREPARE_SCREEN,
 MENUS_MAIN_REDRAW,MENUS_MAIN_RESET_TIMEOUT,MENUS_MAIN_WAIT,MENUS_MAIN_POLL,
 MENUS_MAIN_RESTART_ATTRACT,MENUS_MAIN_EXIT_FADE,MENUS_MAIN_CONTROLS_FADE,
 MENUS_MAIN_CONTROLS,MENUS_MAIN_PLAYERS,MENUS_MAIN_DIFFICULTY,MENUS_MAIN_PASSWORD,
 MENUS_MAIN_PLAY_FADE,MENUS_MAIN_SESSION,MENUS_MAIN_CLEAR_SESSION,MENUS_MAIN_CHECK_SESSION,
 MENUS_MAIN_GAME_OVER,MENUS_MAIN_COMPLETION,MENUS_MAIN_INSERT_SCORES,
 MENUS_MAIN_DONE,MENUS_MAIN_BOUND
} MenusMainAction;
typedef struct MenusMainReply {uint8_t negative,zero,changed,scan,completed;uint16_t remaining;} MenusMainReply;
typedef struct MenusMain {MenusMainAction last;uint32_t budget;uint8_t started;} MenusMain;
MenusMainAction menus_main_next(MenusMain *menu,MenusMainReply reply);
#endif
