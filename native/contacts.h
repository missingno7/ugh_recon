#ifndef NATIVE_CONTACTS_H
#define NATIVE_CONTACTS_H
#include <stddef.h>
#include <stdint.h>
#include "geometry.h"
typedef struct ContactProbe {
    int touching;
    /* Last constructed boundary. Retained for the bridge's observable scratch
     * result; it is never an unwrapped or normalized rectangle coordinate. */
    uint16_t boundary;
} ContactProbe;
typedef struct ContactSelection {
    int index; /* Selected slot number or -1; ascending search, first hit wins. */
    uint16_t boundary;
} ContactSelection;
typedef struct StoneContactView {
    ObjectPosition position;
    /* The bridge classifies stone descriptor AND thrown handler. No generic
     * state-machine enum is introduced for this borrowed predicate input. */
    int thrown_stone;
    uint16_t vertical_step; /* negative words are ineligible (G:21B7) */
} StoneContactView;
ContactProbe contact_player(ObjectPosition object, ObjectGeometry geometry, ObjectPosition player);
ContactProbe contact_stone(ObjectPosition stone, ObjectPosition enemy);
ContactSelection contact_players(ObjectPosition object, ObjectGeometry geometry,
    const ObjectPosition players[2], uint16_t player_count);
/* Sentinel already resolved to count by bridge; first eligible hit wins. */
ContactSelection contact_stones(const StoneContactView *stones, size_t count, ObjectPosition enemy);
#endif
