#ifndef NATIVE_COMPOSE_OBJECTS_H
#define NATIVE_COMPOSE_OBJECTS_H
#include "game_boot.h"
#include "items.h"
/* Cursors are physical byte indices, retained at the actor-pass return cut.
 * Incoming player is a typed ordinal, independently live at direct entries. */
GSStatus game_actor_call(GameWorld *,GameServices *,uint16_t *,ObjectCallbackIdentity,size_t);
GSStatus game_actors_update(GameWorld *,GameServices *);
typedef struct GameItemSpawn {GSStatus status;ItemSpawnResult allocation;} GameItemSpawn;
GameItemSpawn game_item_spawn(GameWorld *,GameServices *,ObjectResourceIdentity,ObjectPosition,uint16_t,uint16_t);
GSStatus game_item_call(GameWorld *,GameServices *,size_t,ItemCallbackRole);
GSStatus game_items_update(GameWorld *,GameServices *);
#endif
