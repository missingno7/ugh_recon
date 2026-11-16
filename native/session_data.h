#ifndef NATIVE_SESSION_DATA_H
#define NATIVE_SESSION_DATA_H
#include "../port/services.h"
#include "object_identities.h"
#include "player_world.h"
#include "platform_world.h"
#include "session.h"
typedef struct SessionDataView {GSResourceId resource;size_t offset,size;} SessionDataView;
typedef struct SessionActorSpec {
    ObjectResourceIdentity descriptor,journey;
    ObjectCallbackIdentity callback;
    SessionLoadClass kind;
} SessionActorSpec;
typedef struct SessionEnemySpec {
    ObjectResourceIdentity descriptor,list;
    ObjectCallbackIdentity callback;
    SessionLoadClass kind;
} SessionEnemySpec;
typedef struct SessionLevelSpec {
    SessionDataView record,platforms,actors,enemies,introduction;
    SessionActorSpec actor[16];
    SessionEnemySpec enemy[5];
    unsigned actor_count,enemy_count;
} SessionLevelSpec;
typedef struct SessionFrameSpec {
    uint16_t cycle_start[2],cycle_end[2],impact_limit[3],timer_divisor,timer_position;
} SessionFrameSpec;
const SessionFrameSpec *session_data_frame(void);
/* One store for the newly admitted player/platform domains. Identity cells
 * replace the compatibility-only descriptor/callback words in enemy/item
 * structs. Those words are never used by production composition. */
typedef struct GameSessionState {
    NativePlayerWorld players;
    NativePlatformsWorld platforms;
    ObjectResourceIdentity enemy_descriptor[5],enemy_list[5],item_descriptor[12];
    ObjectCallbackIdentity enemy_callback[5],item_callback[12];
    uint8_t actor_end[16],enemy_end[5];
    const SessionLevelSpec *level;
    uint16_t scale_scratch;
    uint8_t ready;
} GameSessionState;
GSStatus session_data_view(GameServices *,SessionDataView,GSBytes *);
GSStatus session_data_level(uint16_t,uint16_t,const SessionLevelSpec **);
GSStatus session_data_password(GameServices *,uint16_t,uint16_t,GSBytes *);
GSStatus session_data_passwords(GameServices *,uint16_t,GSBytes *);
uint16_t session_data_count(uint16_t);
GSStatus session_data_maps(GameServices *,GSBytes *);
struct GameWorld;
GSStatus game_session_construct(struct GameWorld *,GameServices *);
#endif
