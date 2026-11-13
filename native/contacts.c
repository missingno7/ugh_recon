#include "contacts.h"
static int32_t signed_word(uint16_t word) {
    return word<32768u ? (int32_t)word : (int32_t)word-65536;
}
ContactProbe contact_player(ObjectPosition object, ObjectGeometry geometry, ObjectPosition player) {
    ContactProbe result={0,(uint16_t)(geometry.anchor_y*32u+object.y32)};
    if(signed_word(result.boundary)<signed_word(player.y32)) return result;
    result.boundary=(uint16_t)((uint16_t)(geometry.anchor_y-geometry.extent_y-geometry.extent_y)*32u+object.y32-640u);
    if(signed_word(result.boundary)>signed_word(player.y32)) return result;
    result.boundary=(uint16_t)((uint16_t)(geometry.anchor_x+geometry.extent_x)*32u+object.x32-160u);
    if(signed_word(result.boundary)<signed_word(player.x32)) return result;
    result.boundary=(uint16_t)((uint16_t)(geometry.anchor_x-geometry.extent_x)*32u+object.x32-832u);
    if(signed_word(result.boundary)>signed_word(player.x32)) return result;
    result.touching=1; return result;
}
ContactProbe contact_stone(ObjectPosition stone, ObjectPosition enemy) {
    ContactProbe result={0,(uint16_t)(stone.y32+256u)};
    if(signed_word(result.boundary)<signed_word(enemy.y32)) return result;
    result.boundary=(uint16_t)(result.boundary-896u);
    if(signed_word(result.boundary)>signed_word(enemy.y32)) return result;
    result.boundary=(uint16_t)(stone.x32+384u);
    if(signed_word(result.boundary)<signed_word(enemy.x32)) return result;
    result.boundary=(uint16_t)(result.boundary-1216u);
    if(signed_word(result.boundary)>signed_word(enemy.x32)) return result;
    result.touching=1; return result;
}
ContactSelection contact_players(ObjectPosition object, ObjectGeometry geometry,
    const ObjectPosition players[2], uint16_t player_count) {
    ContactProbe probe=contact_player(object,geometry,players[0]);
    ContactSelection result={probe.touching?0:-1,probe.boundary};
    /* Retained equality retry bug: zero/odd/large counts still test player 0. */
    if(!probe.touching && player_count==2) {
        probe=contact_player(object,geometry,players[1]);
        result.index=probe.touching?1:-1; result.boundary=probe.boundary;
    }
    return result;
}
ContactSelection contact_stones(const StoneContactView *stones, size_t count, ObjectPosition enemy) {
    ContactSelection result={-1,65535u}; /* sentinel descriptor is final scratch on miss */
    for(size_t i=0;i<count;i++) {
        if(stones[i].thrown_stone && !(stones[i].vertical_step&32768u)) {
            ContactProbe probe=contact_stone(stones[i].position,enemy);
            if(probe.touching) { result.index=(int)i; result.boundary=probe.boundary; return result; }
        }
    }
    return result;
}
