#ifndef NATIVE_FRONT_END_H
#define NATIVE_FRONT_END_H
#include <stdint.h>
/* Borrowed views of the existing front-end/session/input cells. No persistent
 * native copy owns these configuration words. */
typedef struct FrontConfiguration {uint16_t control_modes[2],players,player_bytes,water_y,level,difficulty;} FrontConfiguration;
typedef struct FrontBlink {uint8_t counter,character,write;} FrontBlink;
FrontBlink front_blink(uint16_t position,uint16_t capacity,uint8_t counter);
typedef enum FrontEditKind {FRONT_EDIT_IGNORE,FRONT_EDIT_STORE,FRONT_EDIT_ERASE,FRONT_EDIT_FINISH} FrontEditKind;
typedef struct FrontEditCommand {FrontEditKind kind;uint16_t position,erase[2];uint8_t character,erase_count,clear_current,empty,accepted;} FrontEditCommand;
FrontEditCommand front_edit_command(uint16_t position,uint16_t capacity,uint8_t character,int spaces);
typedef struct FrontRectangle {uint16_t x,y,width,height;} FrontRectangle;
FrontRectangle front_entry_rectangle(int score_name);
uint16_t front_next_byte_position(uint16_t position,int reverse);
#endif
