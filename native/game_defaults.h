#ifndef NATIVE_GAME_DEFAULTS_H
#define NATIVE_GAME_DEFAULTS_H
#include "../port/services.h"
/* Build-time data views only. These are semantic constructor fields, with no
 * executable coordinates, RAM fixture, or code-word resolver at runtime. */
typedef enum GameDefaultField {
 GD_RANDOM,GD_SCORES,GD_SEQUENCE,GD_BASE_PALETTE,GD_FADED_PALETTE,
 GD_PLAYERS,GD_PLAYER_BYTES,GD_CONTROL_ONE,GD_CONTROL_TWO,GD_DIFFICULTY,
 GD_LATEST,GD_PREVIOUS,GD_SCAN,GD_CHANGE,GD_INDEX,GD_AXES,GD_LIMIT,
 GD_ROW_STRIDE,GD_FILE_HANDLE,GD_OPERATOR_INDEX,GD_SAVED_MODE,GD_COUNT
} GameDefaultField;
typedef struct GameDefaultSpec {GSResourceId resource;size_t offset,size,destination;GameDefaultField field;} GameDefaultSpec;
GSStatus game_default_copy(GameServices *,GameDefaultField,void *,size_t);
GSStatus game_picture_resource(GameServices *,unsigned,GSBytes *);
#endif
