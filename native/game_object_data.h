#ifndef NATIVE_GAME_OBJECT_DATA_H
#define NATIVE_GAME_OBJECT_DATA_H
#include "game_boot.h"
/* Borrow pack DATA with the same family/view/position admission as the typed
 * identity registry, without linking the verification world's global provider. */
GSStatus game_object_resource(GameServices *,ObjectResourceIdentity,GSBytes *);
GSStatus game_object_word(GameServices *,ObjectResourceIdentity,uint16_t,uint16_t *);
GSStatus game_object_link(ObjectResourceIdentity,uint16_t,ObjectGraphLink *);
GSStatus game_object_actor_type(ActorTypeId,ObjectResourceIdentity *);
GSStatus game_object_actor_id(ObjectResourceIdentity,ActorTypeId *);
ObjectResourceIdentity game_object_bonus(void);
GSResourceId game_object_stone_effect(void);
GSResourceId game_object_bonus_effect(void);
GSStatus game_object_multiplier_limit(GameServices *,uint16_t,uint16_t *);
GSStatus game_object_enemy_type(LevelEnemyKind,ObjectResourceIdentity *);
GSStatus game_object_enemy_kind(ObjectResourceIdentity,LevelEnemyKind *);
GSResourceId game_object_enemy_effect(HazardAudio);
#endif
