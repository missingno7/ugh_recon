#include "level_projection.h"
static uint16_t projection_word(const uint8_t *raw) {
    return (uint16_t)(raw[0]+raw[1]*256u);
}
static void projection_bytes(uint16_t segment,uint16_t offset,uint8_t *raw,size_t size) {
    for(size_t i=0;i<size;i++) raw[i]=rd8(segment,(uint16_t)(offset+i));
}
ObjectGeometry level_bridge_geometry(uint16_t segment,uint16_t descriptor,int item) {
    uint8_t raw[8];
    /* Match operand-offset wrap and contiguous word bytes, including FFFF. */
    for(unsigned i=0;i<(item?2u:4u);i++) {
        uint16_t word=rd16(segment,(uint16_t)(descriptor+2u*i));
        raw[2*i]=(uint8_t)word;raw[2*i+1]=(uint8_t)(word>>8);
    }
    return item?level_item_geometry(raw):level_object_geometry(raw);
}
int level_bridge_project(uint16_t segment,uint16_t record,
    const uint8_t *map_bank,size_t map_size,LevelProjectionStorage *storage,LevelDescription *view) {
    uint8_t raw[26];projection_bytes(segment,record,raw,26);
    size_t map=projection_word(raw);
    if(map_size<320 || map>map_size-320) return 0;
    for(size_t i=0;i<320;i++) storage->tiles[i]=map_bank[map+i];
    uint16_t cursor=projection_word(raw+2);size_t np=0,na=0,ne=0;
    while(!(rd16(segment,cursor)&32768u)) {
        if(np==10) return 0;
        uint8_t input[16];projection_bytes(segment,cursor,input,16);
        storage->platforms[np++]=level_platform(input);cursor=(uint16_t)(cursor+16);
    }
    cursor=projection_word(raw+4);
    while(rd16(segment,cursor)!=65535u) {
        if(na==16) return 0;
        uint16_t descriptor=rd16(segment,cursor);
        LevelActorPlacement *entry=&storage->actors[na++];
        entry->geometry=level_bridge_geometry(segment,descriptor,0);
        entry->initial_platform=rd16(segment,(uint16_t)(cursor+2));
        projection_bytes(segment,(uint16_t)(cursor+4),entry->tail_raw,2);
        cursor=(uint16_t)(cursor+6);
    }
    cursor=projection_word(raw+6);
    while(rd16(segment,cursor)!=65535u) {
        if(ne==5) return 0;
        uint16_t descriptor=rd16(segment,cursor);
        LevelEnemyPlacement *entry=&storage->enemies[ne++];
        if(descriptor==D(Data_7630)) { entry->kind=LEVEL_BIRD;entry->raw_size=8; }
        else if(descriptor==D(Data_766C)) { entry->kind=LEVEL_TRIOPTERUS;entry->raw_size=8; }
        else if(descriptor==D(Data_76A8)) { entry->kind=LEVEL_DINO;entry->raw_size=10; }
        else if(descriptor==D(Data_76E4)) { entry->kind=LEVEL_TREE;entry->raw_size=6; }
        else return 0;
        entry->geometry=level_bridge_geometry(segment,descriptor,0);
        for(size_t i=0;i<10;i++) entry->raw[i]=0;
        projection_bytes(segment,cursor,entry->raw,entry->raw_size);
        cursor=(uint16_t)(cursor+entry->raw_size);
    }
    *view=level_description(raw,storage->tiles,storage->platforms,np,storage->actors,na,storage->enemies,ne);
    return 1;
}
