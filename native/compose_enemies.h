#ifndef NATIVE_COMPOSE_ENEMIES_H
#define NATIVE_COMPOSE_ENEMIES_H
#include "game_boot.h"
/* The session frame loop calls the enemy passes at their accepted cuts:
 * erase among the erase passes; update after the actor update; draw back
 * after the actors' draw; draw front after the player's draw. Each returns
 * GS_OK, a consumed service failure, or GS_UNSUPPORTED for an unadmitted role.
 * The implementation is native/compose_enemies.c. While that is being
 * written, native/compose_enemies_stub.c provides the same operations for
 * levels with no active enemy slot. */
GSStatus game_enemies_erase(GameWorld *,GameServices *);
GSStatus game_enemies_update(GameWorld *,GameServices *);
GSStatus game_enemies_draw_back(GameWorld *,GameServices *);
GSStatus game_enemies_draw_front(GameWorld *,GameServices *);
#endif
