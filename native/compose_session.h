#ifndef NATIVE_COMPOSE_SESSION_H
#define NATIVE_COMPOSE_SESSION_H
#include "game_boot.h"
#include "session.h"
/* The menu edits the single front.password store, then enters here. No level,
 * actor fixture or callback transport is part of this seam. */
typedef enum GameSessionEntry { GAME_SESSION_PASSWORD } GameSessionEntry;
typedef enum GameSessionKind { GAME_SESSION_RETURNED, GAME_SESSION_UNSUPPORTED,
    GAME_SESSION_SERVICE_ERROR, GAME_SESSION_QUIT } GameSessionKind;
typedef struct GameSessionResult {
    GameSessionKind kind;
    GSStatus status;
    SessionAction action;
    unsigned display_stage;
    uint32_t completed_frames;
} GameSessionResult;
GSStatus game_session_password(GameWorld *,GameServices *,uint16_t *);
GSStatus game_session_load(GameWorld *,GameServices *);
GSStatus game_session_initialize(GameWorld *,GameServices *,unsigned *);
GameSessionResult game_session_run(GameWorld *,GameServices *,GameSessionEntry);
#endif
