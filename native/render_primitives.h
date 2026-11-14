#ifndef NATIVE_RENDER_PRIMITIVES_H
#define NATIVE_RENDER_PRIMITIVES_H
#include <stdint.h>

/* All image positions are wrapping four-pixel cell offsets. These are borrowed
 * resources and working cursors, not another owner of the image or player. */
typedef struct RenderSpritePlacement {
    uint16_t destination,water,directory_index,y;
    uint8_t plane,bank,fixed_page;
} RenderSpritePlacement;
typedef struct RenderSpriteCursor {
    uint16_t source,destination,row_destination,water,initial_water;
    uint8_t plane,columns,height,rows,crossing,submerged,backward;
} RenderSpriteCursor;
typedef struct RenderPixelRequest {
    uint16_t source,destination;
    uint8_t value,write;
} RenderPixelRequest;
typedef struct RenderCopyRows {
    uint16_t source,destination,width,remaining;
} RenderCopyRows;
typedef struct RenderCopyRequest {
    uint16_t source,destination,count,source_end,destination_end;
    uint8_t backward;
} RenderCopyRequest;
typedef struct RenderDrawRequest { uint16_t sprite,x,y; uint8_t draw; } RenderDrawRequest;
typedef struct RenderRectangleSpec { uint16_t x,y,width,height; } RenderRectangleSpec;
typedef struct RenderPlayerAnimation {
    uint16_t countdown,sprite,cycle_start,cycle_end,rate,x,y;
} RenderPlayerAnimation;
typedef struct RenderAnimationResult {
    uint16_t countdown_first,countdown,sprite;
    uint8_t advance;
    RenderDrawRequest request;
} RenderAnimationResult;
typedef struct RenderPlayerCache { uint16_t sprite,x,y; } RenderPlayerCache;

RenderSpritePlacement render_sprite_place(uint16_t sprite,uint16_t x,uint16_t y,
    uint16_t surface,uint16_t playfield_height,uint16_t draw_page,uint16_t fixed_page);
void render_sprite_begin(RenderSpriteCursor *cursor,RenderSpritePlacement placement,
    uint16_t source,uint16_t dimensions,uint8_t backward);
RenderPixelRequest render_sprite_pixel(RenderSpriteCursor *cursor,uint8_t pixel);
void render_sprite_column(RenderSpriteCursor *cursor);
RenderCopyRows render_rectangle(uint16_t x,uint16_t y,uint16_t width,uint16_t height,
    uint16_t background_page,uint16_t draw_page);
void render_next_row(RenderCopyRows *rows);
RenderCopyRequest render_save(uint16_t source,uint16_t destination,uint16_t count,
    uint8_t backward);
RenderDrawRequest render_map_tile(uint16_t sprite,uint16_t packed_coordinates);
RenderDrawRequest render_map_cell(uint16_t ordinal,uint8_t tile);
RenderRectangleSpec render_tile_rectangle(uint16_t x,uint16_t y);
RenderRectangleSpec render_playfield_rectangle(uint16_t height);
RenderRectangleSpec render_sprite_rectangle(uint16_t x,uint16_t y,uint16_t dimensions);
uint16_t render_restore_sprite_index(uint16_t sprite);
uint8_t render_player_visible(uint16_t x,uint16_t y);
RenderDrawRequest render_player_restore(RenderPlayerCache cache);
RenderAnimationResult render_player_animation(RenderPlayerAnimation player);
void render_cache_store(RenderPlayerCache *cache,uint8_t field,uint16_t value);
#endif
