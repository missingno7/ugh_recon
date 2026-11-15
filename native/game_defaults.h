#ifndef NATIVE_GAME_DEFAULTS_H
#define NATIVE_GAME_DEFAULTS_H
#include "../port/services.h"
/* Build-time data views only. These are semantic constructor fields, with no
 * executable coordinates, RAM fixture, or code-word resolver at runtime. */
typedef enum GameDefaultField {
 GD_RANDOM,GD_SCORES,GD_SEQUENCE,GD_BASE_PALETTE,GD_FADED_PALETTE,
 GD_PLAYERS,GD_PLAYER_BYTES,GD_CONTROL_ONE,GD_CONTROL_TWO,GD_DIFFICULTY,
 GD_LATEST,GD_PREVIOUS,GD_SCAN,GD_CHANGE,GD_INDEX,GD_AXES,GD_LIMIT,
 GD_ROW_STRIDE,GD_FILE_HANDLE,GD_OPERATOR_INDEX,GD_SAVED_MODE,
 GD_NAME,GD_PASSWORD,GD_LEVEL_CHARS,GD_DIFFICULTY_TEXT,GD_PLAYERS_TEXT,GD_CONTROL_TEXT_ONE,GD_CONTROL_TEXT_TWO,
 GD_DIGITS,GD_DIVISORS,GD_CREDITS,GD_MENU_TEXT,GD_SCORE_PROMPT,GD_SCORE_TITLE,GD_LEVEL_TITLE,GD_PASSWORD_TITLE,GD_SOURCE_PALETTE,GD_COUNT
} GameDefaultField;
typedef struct GameDefaultSpec {GSResourceId resource;size_t offset,size,destination;GameDefaultField field;} GameDefaultSpec;
GSStatus game_default_copy(GameServices *,GameDefaultField,void *,size_t);
GSStatus game_picture_resource(GameServices *,unsigned,GSBytes *);
GSStatus game_front_sprite(GameServices *,unsigned,GSBytes *,uint16_t *,uint16_t *);
GSStatus game_front_label(GameServices *,unsigned,unsigned,GSBytes *);
#endif
