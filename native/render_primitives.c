#include "render_primitives.h"

static uint16_t render_quarter(uint16_t value) {
    return (uint16_t)((value>>2)|((value&0x8000u)?0xc000u:0));
}
RenderSpritePlacement render_sprite_place(uint16_t sprite,uint16_t x,uint16_t y,
    uint16_t surface,uint16_t playfield_height,uint16_t draw_page,uint16_t fixed_page) {
    RenderSpritePlacement p;
    p.fixed_page=(uint8_t)((int16_t)y>=(int16_t)playfield_height);
    p.y=p.fixed_page?(uint16_t)(y-192u):y;
    p.water=(uint16_t)(surface-p.y);
    p.destination=(uint16_t)((p.fixed_page?fixed_page:draw_page)+render_quarter(x)+(uint16_t)(p.y*96u));
    p.plane=(uint8_t)(1u<<(x&3u));
    p.directory_index=(uint16_t)(sprite*4u);
    p.bank=(uint8_t)(sprite>=547?3:sprite>=298?2:sprite>=217?1:0);
    return p;
}
void render_sprite_begin(RenderSpriteCursor *c,RenderSpritePlacement p,
    uint16_t source,uint16_t dimensions,uint8_t backward) {
    c->source=source;c->destination=c->row_destination=p.destination;
    c->water=c->initial_water=p.water;c->plane=p.plane;
    c->columns=(uint8_t)dimensions;c->height=c->rows=(uint8_t)(dimensions>>8);
    c->crossing=(uint8_t)((int16_t)p.water>=0 && (int16_t)p.water<c->height);
    c->submerged=(uint8_t)((int16_t)p.water<0);c->backward=backward;
}
RenderPixelRequest render_sprite_pixel(RenderSpriteCursor *c,uint8_t pixel) {
    RenderPixelRequest e;
    e.source=c->source;e.destination=c->row_destination;e.write=(uint8_t)(pixel!=0);
    e.value=pixel;
    if(pixel && (c->submerged || (c->crossing && (c->water&0x8000u))))e.value|=0x40u;
    c->source=(uint16_t)(c->source+(c->backward?-1:1));
    c->row_destination=(uint16_t)(c->row_destination+96u);
    if(c->crossing)c->water=(uint16_t)(c->water-1u);
    c->rows=(uint8_t)(c->rows-1u);
    return e;
}
void render_sprite_column(RenderSpriteCursor *c) {
    c->plane=(uint8_t)((c->plane<<1)&15u);
    if(!c->plane){c->plane=1;c->destination=(uint16_t)(c->destination+1u);}
    c->columns=(uint8_t)(c->columns-1u);
    c->rows=c->height;c->row_destination=c->destination;
    if(c->crossing)c->water=c->initial_water;
}
RenderCopyRows render_rectangle(uint16_t x,uint16_t y,uint16_t width,uint16_t height,
    uint16_t background_page,uint16_t draw_page) {
    RenderCopyRows r;uint16_t base=(uint16_t)(y*96u+render_quarter(x));
    r.source=(uint16_t)(base+background_page);r.destination=(uint16_t)(base+draw_page);
    /* Wrap both additions before shifting; zero height is a full word cycle. */
    r.width=(uint16_t)((uint16_t)((uint16_t)((x&3u)+width)+3u)>>2);
    r.remaining=height;return r;
}
void render_next_row(RenderCopyRows *r) {
    r->source=(uint16_t)(r->source+96u);r->destination=(uint16_t)(r->destination+96u);
    r->remaining=(uint16_t)(r->remaining-1u);
}
RenderCopyRequest render_save(uint16_t source,uint16_t destination,uint16_t count,uint8_t backward) {
    RenderCopyRequest r;r.source=source;r.destination=destination;r.count=count;r.backward=backward;
    r.source_end=(uint16_t)(source+(backward?-(int)count:(int)count));
    r.destination_end=(uint16_t)(destination+(backward?-(int)count:(int)count));return r;
}
RenderDrawRequest render_map_tile(uint16_t sprite,uint16_t packed_coordinates) {
    RenderDrawRequest r;r.sprite=(uint8_t)sprite;r.x=(uint16_t)((packed_coordinates&255u)*16u);
    r.y=(uint16_t)((packed_coordinates>>8)*12u);r.draw=1;return r;
}
RenderDrawRequest render_map_cell(uint16_t ordinal,uint8_t tile) {
    RenderDrawRequest r;r.sprite=tile;r.x=(uint16_t)((ordinal%20u)*16u);
    r.y=(uint16_t)((ordinal/20u)*12u);r.draw=1;return r;
}
RenderRectangleSpec render_tile_rectangle(uint16_t x,uint16_t y) {
    RenderRectangleSpec r;r.x=(uint16_t)(x*16u);r.y=(uint16_t)(y*12u);r.width=16;r.height=12;return r;
}
RenderRectangleSpec render_playfield_rectangle(uint16_t height) {
    RenderRectangleSpec r;r.x=r.y=0;r.width=320;r.height=height;return r;
}
RenderRectangleSpec render_sprite_rectangle(uint16_t x,uint16_t y,uint16_t dimensions) {
    RenderRectangleSpec r;r.x=x;r.y=y;r.width=(uint8_t)dimensions;r.height=(uint8_t)(dimensions>>8);return r;
}
uint16_t render_restore_sprite_index(uint16_t sprite) {
    /* Retained bug: the loaded directory offset is discarded by MOV SI,CX. */
    return (uint16_t)(sprite*4u);
}
uint8_t render_player_visible(uint16_t x,uint16_t y) {
    return (uint8_t)((int16_t)x>-32 && (int16_t)x<320 && (int16_t)y>-20 && (int16_t)y<192);
}
RenderDrawRequest render_player_restore(RenderPlayerCache cache) {
    RenderDrawRequest r;r.sprite=cache.sprite;r.x=cache.x;r.y=cache.y;
    r.draw=render_player_visible(cache.x,cache.y);return r;
}
RenderAnimationResult render_player_animation(RenderPlayerAnimation p) {
    RenderAnimationResult r;uint16_t rate=(int16_t)p.rate>90?90:p.rate;
    r.countdown_first=(uint16_t)(p.countdown-rate);r.countdown=r.countdown_first;
    r.sprite=p.sprite;r.advance=(uint8_t)((int16_t)r.countdown<0);
    if(r.advance){r.countdown=(uint16_t)(r.countdown+200u);r.sprite=(uint16_t)(r.sprite+1u);
        if((int16_t)r.sprite>=(int16_t)p.cycle_end)r.sprite=p.cycle_start;}
    r.request.sprite=r.sprite;r.request.x=p.x;r.request.y=p.y;
    r.request.draw=render_player_visible(p.x,p.y);return r;
}
void render_cache_store(RenderPlayerCache *cache,uint8_t field,uint16_t value) {
    if(field==0)cache->sprite=value;
    else if(field==1)cache->x=value;
    else if(field==2)cache->y=value;
}
