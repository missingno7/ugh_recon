#ifndef NATIVE_COMPOSE_DEMO_H
#define NATIVE_COMPOSE_DEMO_H
#include "game_boot.h"
#include "demo_presentation.h"
typedef struct GameDemoResult {GSStatus status;int16_t selection;} GameDemoResult;
GSStatus game_demo_construct(GameWorld *,GameServices *);
GSStatus game_demo_resource(GameWorld *,ObjectResourceIdentity,GSBytes *);
GSStatus game_demo_vector(DemoPresentationKind,ObjectResourceIdentity *,size_t *);
/* The typed callback is loaded from the actor after position publication and
 * before cursor publication. Only the three admitted demo peers execute. */
GSStatus game_demo_callback(GameWorld *,GameServices *,size_t,ObjectCallbackIdentity);
GSStatus game_demo_initialize(GameWorld *,GameServices *,DemoPresentationKind);
GSStatus game_demo_advance(GameWorld *,GameServices *);
GSStatus game_demo_reset(GameWorld *);
GSStatus game_demo_render(GameWorld *,GameServices *,int);
GSStatus game_demo_prepare(GameWorld *,GameServices *,int);
GSStatus game_demo_water(GameWorld *,GameServices *);
/* Music peers share the composed audio timeline and service failure prefixes. */
GSStatus game_demo_music_stop(GameWorld *,GameServices *,uint16_t);
GSStatus game_demo_music_start(GameWorld *,GameServices *,uint16_t);
GameDemoResult game_demo_play(GameWorld *,GameServices *,DemoPresentationKind);
#endif
