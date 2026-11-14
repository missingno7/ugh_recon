#ifndef NATIVE_SESSION_H
#define NATIVE_SESSION_H
#include <stdint.h>
#include "geometry.h"

/* Private continuation state, not a recovered universal game-mode enum. The
 * persistent lives/score/level/fade/render values remain in their existing owners. */
typedef enum SessionAction {
    SESSION_PASSWORD,SESSION_SELECT_LEVEL,SESSION_PREGAME,SESSION_STOP_INITIAL_MUSIC,
    SESSION_RESET_GAME,SESSION_BLACK_PALETTE,SESSION_INITIALIZE_LEVEL,SESSION_START_MUSIC,
    SESSION_FADE_UPLOAD,SESSION_FADE_ADVANCE,SESSION_WAIT_RETRACE,SESSION_HUD,
    SESSION_ERASE_PLAYER_BEGIN,SESSION_ERASE_PLAYER,SESSION_ERASE_PLAYER_NEXT,
    SESSION_ERASE_ACTORS,SESSION_ERASE_ENEMIES,SESSION_ERASE_ITEMS,SESSION_RESTORE_RAIN,
    SESSION_ADVANCE_WATER,SESSION_IO_POINT,SESSION_POLL_CONTROLS,
    SESSION_PAUSE_RELEASE,SESSION_PAUSE_MAKE,SESSION_PAUSE_BREAK,SESSION_ESCAPE,
    SESSION_MOVE_BEGIN,SESSION_MOVE_PLAYER,SESSION_MOVE_NEXT,SESSION_UPDATE_ACTORS,
    SESSION_UPDATE_ENEMIES,SESSION_UPDATE_ITEMS,SESSION_DRAW_ACTORS,SESSION_DRAW_ENEMIES_BACK,
    SESSION_DRAW_PLAYER_BEGIN,SESSION_DRAW_PLAYER,SESSION_DRAW_PLAYER_NEXT,
    SESSION_DRAW_ENEMIES_FRONT,SESSION_DRAW_ITEMS,SESSION_DRAW_OVERLAYS,
    SESSION_ADVANCE_RAIN,SESSION_DRAW_RAIN,SESSION_DRAW_WATER,SESSION_SWAP_PAGE,
    SESSION_STOP_LEVEL_MUSIC,SESSION_OUTCOME,SESSION_DECREMENT_LIVES,SESSION_RESET_MULTIPLIER,
    SESSION_INCREMENT_LEVEL,SESSION_TEST_LEVEL_LIMIT,SESSION_RETURN,SESSION_FINISHED,SESSION_INVALID
} SessionAction;
typedef enum SessionPhase {
    SP_PASSWORD,SP_SELECT_LEVEL,SP_PREGAME,SP_STOP_INITIAL_MUSIC,SP_RESET_GAME,SP_BLACK_PALETTE,
    SP_INITIALIZE_LEVEL,SP_START_MUSIC,SP_FRAME_BEGIN,SP_FADE_ADVANCE,SP_HUD,
    SP_ERASE_PLAYER_BEGIN,SP_ERASE_PLAYER,SP_ERASE_PLAYER_NEXT,SP_ERASE_ACTORS,
    SP_ERASE_ENEMIES,SP_ERASE_ITEMS,SP_RESTORE_RAIN,SP_ADVANCE_WATER,SP_IO_POINT,
    SP_POLL_CONTROLS,SP_PAUSE_RELEASE,SP_PAUSE_MAKE,SP_PAUSE_BREAK,SP_ESCAPE,SP_MOVE_BEGIN,
    SP_MOVE_PLAYER,SP_MOVE_NEXT,SP_UPDATE_ACTORS,SP_UPDATE_ENEMIES,SP_UPDATE_ITEMS,
    SP_DRAW_ACTORS,SP_DRAW_ENEMIES_BACK,SP_DRAW_PLAYER_BEGIN,SP_DRAW_PLAYER,SP_DRAW_PLAYER_NEXT,
    SP_DRAW_ENEMIES_FRONT,SP_DRAW_ITEMS,SP_DRAW_OVERLAYS,SP_ADVANCE_RAIN,SP_DRAW_RAIN,
    SP_DRAW_WATER,SP_SWAP_PAGE,SP_STOP_LEVEL_MUSIC,SP_OUTCOME,SP_DECREMENT_LIVES,
    SP_RESET_MULTIPLIER,SP_INCREMENT_LEVEL,SP_TEST_LEVEL_LIMIT,SP_RETURN,SP_DONE
} SessionPhase;
typedef struct SessionWorld {
    uint16_t fade_level,fade_rate,palette_reply,player_bytes,player_count,level,level_limit;
    uint16_t password_reply;
    uint8_t lives,completion,rain,scan;
} SessionWorld;
typedef struct SessionRequest {
    SessionAction action;
    uint16_t index,value,other;
    uint8_t decision;
} SessionRequest;
typedef struct SessionProcess {
    SessionPhase phase;
    SessionRequest request;
    uint16_t player_cursor,selected_level;
    uint32_t completed_frames;
    uint8_t pending,failed;
} SessionProcess;

void session_begin(SessionProcess *process);
SessionRequest session_next(SessionProcess *process,SessionWorld world);
int session_acknowledge(SessionProcess *process,SessionAction action,SessionWorld reply);
int session_complete(const SessionProcess *process);
int session_should_move(uint16_t fade_level,uint16_t fade_rate);
uint16_t session_password_list_key(uint16_t player_bytes);
uint16_t session_level_count_key(uint16_t player_bytes);

typedef enum SessionPasswordResult {PASSWORD_MORE,PASSWORD_END,PASSWORD_DEFAULT} SessionPasswordResult;
typedef struct SessionPassword {uint16_t length,misses,level;} SessionPassword;
void session_password_begin(SessionPassword *password);
void session_password_candidate(SessionPassword *password);
SessionPasswordResult session_password_byte(uint8_t value);
int session_password_compare(SessionPassword *password,uint8_t candidate,uint8_t editor);
int session_password_has_misses(const SessionPassword *password);
int session_password_needs_padding(const SessionPassword *password);
int session_password_padding(SessionPassword *password,uint8_t editor);
void session_password_reject(SessionPassword *password);
uint16_t session_password_selected(const SessionPassword *password,uint8_t default_marker);

typedef struct SessionRenderView {
    ObjectPosition position;
    uint16_t sprite,erase_sprite,pixel_x,pixel_y,previous_x,previous_y;
} SessionRenderView;
typedef struct SessionRenderResult {
    uint16_t erase_sprite,pixel_x,pixel_y,previous_x,previous_y;
    uint16_t sprite,x,y;
    uint8_t store_erase,store_position,draw,restore;
} SessionRenderResult;
SessionRenderResult session_erase_layer(SessionRenderView view);
SessionRenderResult session_draw_layer(SessionRenderView view,uint8_t enabled);
int session_enemy_layer(uint8_t special,uint8_t front);

typedef enum SessionLoadFamily {LOAD_PLATFORMS,LOAD_ACTORS,LOAD_ENEMIES} SessionLoadFamily;
typedef enum SessionLoadClass {LOAD_ORDINARY,LOAD_STONE,LOAD_TREE,LOAD_BIRD,LOAD_DINO,LOAD_TRIOPTERUS} SessionLoadClass;
typedef enum SessionLoadAction {LOAD_READ_LIST,LOAD_READ_DESCRIPTOR,LOAD_READ_SPAWN,
    LOAD_READ_HEIGHT,LOAD_READ_REPEAT,LOAD_SKIP,LOAD_SCALE_Y,LOAD_SCALE_SPEED,
    LOAD_STORE,LOAD_CALLBACK,LOAD_END,LOAD_INVALID} SessionLoadAction;
typedef enum SessionLoadField {
    LF_PLATFORM_LEFT,LF_PLATFORM_RIGHT,LF_PLATFORM_HEIGHT,LF_PLATFORM_ARRIVAL,
    LF_PLATFORM_WAIT,LF_PLATFORM_SPAWN,LF_PLATFORM_ICON,LF_PLATFORM_OCCUPANT,
    LF_ACTOR_DESCRIPTOR,LF_ACTOR_PLATFORM,LF_ACTOR_JOURNEY,LF_ACTOR_SPRITE,
    LF_ACTOR_ERASE,LF_ACTOR_OVERLAY,LF_ACTOR_ERASE_OVERLAY,LF_ACTOR_CALLBACK,LF_ACTOR_X,LF_ACTOR_Y,
    LF_ENEMY_DESCRIPTOR,LF_ENEMY_PLATFORM,LF_ENEMY_X,LF_ENEMY_Y,LF_ENEMY_LIST,
    LF_ENEMY_DELAY,LF_ENEMY_SPEED,LF_ENEMY_DIRECTION,LF_ENEMY_CALLBACK
} SessionLoadField;
typedef enum SessionLoadArithmetic {LOAD_VALUE,LOAD_KEEP_ACCUMULATOR,LOAD_SET_HIDDEN,
    LOAD_STONE_X,LOAD_STONE_Y,LOAD_TREE_X,LOAD_TREE_Y,LOAD_TRIO_X,LOAD_TRIO_Y,
    LOAD_DINO_X,LOAD_DINO_Y,LOAD_TRIO_SPEED} SessionLoadArithmetic;
typedef struct SessionLoadRequest {
    SessionLoadAction action;SessionLoadField field;SessionLoadArithmetic arithmetic;
    uint16_t slot,index,value; /* resource index or exact published value */
} SessionLoadRequest;
typedef struct SessionLoadRecord {
    SessionLoadFamily family;SessionLoadClass record_class;
    SessionLoadRequest request;
    uint16_t slot,sample,repeat,descriptor,platform;
    uint8_t cursor,pending,failed,list_end,done;
} SessionLoadRecord;
void session_load_begin(SessionLoadRecord *record,SessionLoadFamily family,uint16_t slot);
SessionLoadRequest session_load_next(SessionLoadRecord *record);
int session_load_accept(SessionLoadRecord *record,SessionLoadAction action,uint16_t value,SessionLoadClass record_class);
uint16_t session_load_value(SessionLoadArithmetic arithmetic,uint16_t value,uint16_t repeated);
uint16_t session_record_previous(uint16_t cursor);
int session_record_more(uint16_t cursor);
uint16_t session_loader_mode_key(uint16_t players);
uint16_t session_loader_level_key(uint16_t level);
uint16_t session_water_cap(uint16_t scaled);
typedef struct SessionPlayerSeed {uint16_t fixed,pixel;} SessionPlayerSeed;
SessionPlayerSeed session_player_x(uint16_t raw);
SessionPlayerSeed session_player_y(uint16_t scaled);
uint8_t session_display_byte(uint8_t value);
uint32_t session_display_score(uint32_t score);
uint16_t session_display_layout(uint16_t players,unsigned field);
uint16_t session_copy_next(uint16_t cursor,uint8_t backwards);
int session_count_more(uint16_t remaining);
uint16_t session_prewarm_previous(uint16_t cursor);
int session_rain_enabled(uint8_t direction);
uint16_t session_reset_value(unsigned field);
/* Ordered display services, ending in the erase-history reset tail. */
typedef struct SessionDisplayProcess {uint8_t cursor,pending,failed;} SessionDisplayProcess;
void session_display_begin(SessionDisplayProcess *process);
unsigned session_display_next(SessionDisplayProcess *process);
int session_display_consume(SessionDisplayProcess *process,unsigned action);
int session_display_complete(const SessionDisplayProcess *process);
#endif
