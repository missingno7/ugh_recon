#ifndef NATIVE_ITEMS_H
#define NATIVE_ITEMS_H
#include "contacts.h"
#include "level.h"

enum { FALLING_ITEM_CAPACITY = 12 };
typedef enum FallingItemPhase { ITEM_FLIGHT, ITEM_LANDED } FallingItemPhase;
typedef enum ItemBenefit { ITEM_TIMER, ITEM_LIVES, ITEM_MULTIPLIER } ItemBenefit;
typedef struct FallingItemType {
    ObjectGeometry geometry;
    uint16_t launch_impulse, amount, sprite;
    ItemBenefit benefit; /* every descriptor kind other than 0/1 is multiplier */
} FallingItemType;
typedef struct FallingItem {
    FallingItemType type;
    FallingItemPhase phase; /* stored handler, retained even when inactive */
    uint16_t sprite; /* FFFF inactive; other negative sprites still dispatch */
    ObjectPosition position;
    uint16_t vertical_step;
    /* One retained storage cell: flight horizontal displacement, then landed
     * lifetime. Landing overwrites it; retirement leaves it stale. */
    uint16_t motion_or_lifetime;
} FallingItem;
typedef struct ItemBenefits {
    uint16_t timer, multiplier, multiplier_limit;
    uint8_t lives;
} ItemBenefits;
typedef enum ItemSpawnStatus { ITEM_SPAWNED, ITEM_POOL_FULL } ItemSpawnStatus;
typedef struct ItemSpawnResult { ItemSpawnStatus status; int slot; } ItemSpawnResult;
typedef enum ItemFlightExit {
    ITEM_OUT_LEFT, ITEM_OUT_RIGHT, ITEM_RISING, ITEM_OUT_BOTTOM,
    ITEM_FLYING, ITEM_TOUCHDOWN
} ItemFlightExit;
typedef struct ItemFlightResult {
    ItemFlightExit exit;
    size_t platform; /* count on miss, selected index on touchdown */
    int horizontal_platform; /* last platform whose X bounds were tested */
    int right_tested;
} ItemFlightResult;
typedef struct ItemCollectionResult {
    int expired, collected;
    ContactSelection contact;
} ItemCollectionResult;
typedef struct ItemUpdateResult {
    ItemFlightResult flight;
    ItemCollectionResult collection;
} ItemUpdateResult;

ItemSpawnResult items_spawn(FallingItem items[12], FallingItemType type,
    ObjectPosition launch, uint16_t horizontal, uint16_t launch_term);
void item_land(FallingItem *item);
ItemFlightResult item_advance(FallingItem *item, const LevelPlatform *platforms, size_t count);
ItemCollectionResult item_collect(FallingItem *item, const ObjectPosition players[2],
    uint16_t player_count, ItemBenefits *benefits);
/* Cursor is an exclusive upper bound; starts at capacity, visits descending.
 * Inspect live slots each time, so callback effects are never precomputed. */
int items_next(const FallingItem items[12], size_t *cursor);
ItemUpdateResult item_update(FallingItem *item,const LevelPlatform *platforms,size_t count,
    const ObjectPosition players[2],uint16_t player_count,ItemBenefits *benefits);
void items_dispatch(FallingItem items[12],const LevelPlatform *platforms,size_t count,
    const ObjectPosition players[2],uint16_t player_count,ItemBenefits *benefits);
#endif
