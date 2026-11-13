/* Actual native decoders over arbitrary bytes, independently asserted resource
 * field relations. This proves the decoding contract, not the whole loader. */
void __CPROVER_assert(_Bool,const char *);
static uint16_t expected_word(const uint8_t *p) { return (uint16_t)(p[0]+256u*p[1]); }
int main(void) {
    uint8_t raw[26],tiles[320];LevelPlatform platforms[1];
    LevelActorPlacement actors[1];LevelEnemyPlacement enemies[1];
    LevelDescription view=level_description(raw,tiles,platforms,1,actors,1,enemies,1);
    for(unsigned i=0;i<26;i++) __CPROVER_assert(view.raw[i]==raw[i],"all record bytes retained");
    __CPROVER_assert(view.objectives==raw[8] && view.weather==raw[12],"byte fields");
    __CPROVER_assert(view.player_starts[0].x32==expected_word(raw+13) && view.player_starts[0].y32==expected_word(raw+15) && view.player_starts[1].x32==expected_word(raw+17) && view.player_starts[1].y32==expected_word(raw+19),"unaligned start words");
    __CPROVER_assert(view.water_y32==expected_word(raw+21) && view.water_increment==expected_word(raw+23),"water words before conversion");
    __CPROVER_assert(view.tiles==tiles && view.platforms==platforms && view.actors==actors && view.enemies==enemies && view.platform_count==1 && view.actor_count==1 && view.enemy_count==1,"borrowed immutable views");
    ObjectGeometry g=level_object_geometry(raw),item=level_item_geometry(raw);
    __CPROVER_assert(g.anchor_x==expected_word(raw) && g.anchor_y==expected_word(raw+2) && g.extent_x==expected_word(raw+4) && g.extent_y==expected_word(raw+6),"descriptor geometry");
    __CPROVER_assert(item.anchor_x==g.anchor_x && item.anchor_y==g.anchor_y && item.extent_x==3 && item.extent_y==3,"item implicit extents");
    LevelPlatform platform=level_platform(raw);uint16_t y=expected_word(raw+4);
    int32_t signed_y=y<32768u?(int32_t)y:(int32_t)y-65536;
    int32_t floor_quarter=signed_y>=0?signed_y/4:-((-signed_y+3)/4);
    __CPROVER_assert(platform.surface_y==(uint16_t)(y-floor_quarter),"platform signed aspect conversion");
    __CPROVER_assert(platform.left==expected_word(raw) && platform.right==expected_word(raw+2) && platform.arrival_x==expected_word(raw+6) && platform.waiting_x==expected_word(raw+8) && platform.spawn_x==expected_word(raw+10) && platform.destination_icon==expected_word(raw+12) && platform.reserved_raw==expected_word(raw+14),"platform fields including skipped raw word");
    for(unsigned i=0;i<26;i++) __CPROVER_assert(raw[i]==view.raw[i],"input unchanged");
    return 0;
}
