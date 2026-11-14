#include "menus.h"
MenusTextStep menus_text_step(uint8_t character)
{
 MenusTextStep result={MENUS_TEXT_GLYPH,0,character,0};
 if(!character) result.kind=MENUS_TEXT_END;
 else if(character==13) {result.kind=MENUS_TEXT_LINE;result.y_advance=16;}
 else if(character==253) {result.kind=MENUS_TEXT_HALF_LINE;result.y_advance=8;}
 else {
  if(character==142) character=91;else if(character==153) character=92;else if(character==154) character=93;
  result.character=character;result.glyph=(uint16_t)(character+567u);
 }
 return result;
}
int menus_text_centered(uint8_t first) {return first==254;}
uint16_t menus_text_center_x(uint16_t count) {return (uint16_t)((uint16_t)(320u-(uint16_t)(count<<4))>>1);}
uint16_t menus_text_next_x(uint16_t x) {return (uint16_t)(x+16u);}
uint16_t menus_text_next_y(uint16_t y,uint8_t delimiter) {MenusTextStep layout=menus_text_step(delimiter);return (uint16_t)(y+layout.y_advance);}
uint16_t menus_center_credits(uint16_t separators) {uint16_t height=(uint16_t)((uint16_t)(separators+1u)<<4);return (uint16_t)(((uint16_t)(144u-height)>>1)+56u);}
uint16_t menus_double_index(uint16_t index) {return (uint16_t)(index*2u);}
MenusStringCopy menus_string_begin(uint16_t source,uint16_t destination,int reverse) {MenusStringCopy copy={source,destination,(int8_t)(reverse ? -1 : 1),0};return copy;}
void menus_string_read(MenusStringCopy *copy,uint8_t character) {copy->source=(uint16_t)(copy->source+copy->direction);copy->done=(uint8_t)!character;}
void menus_string_written(MenusStringCopy *copy) {copy->destination=(uint16_t)(copy->destination+copy->direction);}
MenusControlCandidate menus_control_next(uint16_t mode)
{MenusControlCandidate candidate={(uint16_t)(mode+1u),0,0};candidate.keyboard=(uint8_t)((int16_t)candidate.mode>=2);candidate.index=(uint16_t)(candidate.mode*2u);if(candidate.keyboard) candidate.mode=65535;return candidate;}
int menus_control_present(uint16_t presence) {return (int16_t)presence<0;}
MenusControlKey menus_control_key(uint8_t scan) {return scan==1 ? MENUS_CONTROL_QUIT : scan==59 ? MENUS_CONTROL_PLAYER0 : scan==60 ? MENUS_CONTROL_PLAYER1 : MENUS_CONTROL_RESTART;}
uint16_t menus_difficulty_next(uint16_t difficulty) {uint16_t next=(uint16_t)(difficulty+1u);return next>=3 ? 0 : next;}
void menus_toggle_players(FrontConfiguration *configuration) {configuration->players^=3;configuration->player_bytes=(uint16_t)(configuration->players*2u);}
int menus_session_complete(uint16_t level,uint16_t limit) {return level>=limit;}
int16_t menus_credits_result(uint8_t scan) {scan&=127;return scan==16 ? -1 : scan==1 ? 1 : 0;}
uint16_t menus_water(unsigned screen) {return screen==0 ? 180 : screen==1 ? 192 : screen==2 ? 175 : 200;}
uint16_t menus_attract_map_offset(int second) {return second ? 28800 : 0;}
int menus_draw_water(uint16_t y) {return (int16_t)y<192;}
MenusLabel menus_label(unsigned kind,uint16_t value)
{
 MenusLabel plan={value,41};
 if(kind==1) {plan.index=(uint16_t)(value-1u);plan.destination=53;}
 else if(kind>=2) {plan.index=(uint16_t)(value+1u);plan.destination=(uint16_t)(kind==2 ? 15 : 41);}
 return plan;
}
uint8_t menus_level_ordinal(uint8_t level) {return (uint8_t)(level+1u);}
uint8_t menus_ascii_digit(uint8_t digit) {return (uint8_t)(digit+48u);}
MenusMapCopy menus_map_begin(uint16_t source,uint16_t destination,int reverse) {MenusMapCopy copy={source,destination,160,(int8_t)(reverse ? -1 : 1)};return copy;}
void menus_map_advance(MenusMapCopy *copy) {copy->source=(uint16_t)(copy->source+2*copy->direction);copy->destination=(uint16_t)(copy->destination+2*copy->direction);copy->remaining--;}
MenusHeaderItem menus_header_item(unsigned ordinal,uint16_t previous_sprite)
{MenusHeaderItem item={(uint16_t)(ordinal==0 ? 215 : ordinal==1 ? previous_sprite+1u : 214),(uint16_t)(ordinal==0 ? 16 : ordinal==1 ? 227 : 97)};return item;}
MenusMainAction menus_main_next(MenusMain *menu,MenusMainReply reply)
{
 MenusMainAction action=MENUS_MAIN_DONE;
 if(!menu->started) {menu->started=1;action=MENUS_MAIN_STOP_MUSIC;}
 else switch(menu->last) {
 case MENUS_MAIN_STOP_MUSIC:action=MENUS_MAIN_START_MUSIC;break;
 case MENUS_MAIN_START_MUSIC:action=MENUS_MAIN_REVEAL;break;
 case MENUS_MAIN_REVEAL:case MENUS_MAIN_CREDITS:case MENUS_MAIN_ATTRACT:
  if(reply.negative) action=MENUS_MAIN_DONE;
  else if(!reply.zero) action=MENUS_MAIN_PREPARE_PALETTE;
  else action=menu->last==MENUS_MAIN_REVEAL ? MENUS_MAIN_CREDITS : menu->last==MENUS_MAIN_CREDITS ? MENUS_MAIN_ATTRACT : MENUS_MAIN_SCORES;
  break;
 case MENUS_MAIN_SCORES:action=reply.negative ? MENUS_MAIN_DONE : MENUS_MAIN_PREPARE_PALETTE;break;
 case MENUS_MAIN_PREPARE_PALETTE:case MENUS_MAIN_CONTROLS:action=MENUS_MAIN_PREPARE_SCREEN;break;
 case MENUS_MAIN_PREPARE_SCREEN:case MENUS_MAIN_REDRAW:case MENUS_MAIN_PASSWORD:case MENUS_MAIN_PLAYERS:case MENUS_MAIN_DIFFICULTY:
  action=menu->last==MENUS_MAIN_PREPARE_SCREEN || menu->last==MENUS_MAIN_REDRAW ? MENUS_MAIN_RESET_TIMEOUT : MENUS_MAIN_REDRAW;break;
 case MENUS_MAIN_RESET_TIMEOUT:menu->budget=100000;action=MENUS_MAIN_WAIT;break;
 case MENUS_MAIN_WAIT:action=reply.remaining ? MENUS_MAIN_POLL : MENUS_MAIN_RESTART_ATTRACT;break;
 case MENUS_MAIN_POLL:
  if(!reply.changed) {action=MENUS_MAIN_WAIT;break;}
  switch(reply.scan) {
  case 46:action=MENUS_MAIN_RESTART_ATTRACT;break;
  case 16:action=MENUS_MAIN_EXIT_FADE;break;
  case 63:action=MENUS_MAIN_CONTROLS_FADE;break;
  case 62:action=MENUS_MAIN_PLAYERS;break;
  case 61:action=MENUS_MAIN_DIFFICULTY;break;
  case 60:action=MENUS_MAIN_PASSWORD;break;
  case 59:action=MENUS_MAIN_PLAY_FADE;break;
  default:action=MENUS_MAIN_RESET_TIMEOUT;break;
  }break;
 case MENUS_MAIN_CONTROLS_FADE:action=MENUS_MAIN_CONTROLS;break;
 case MENUS_MAIN_PLAY_FADE:action=MENUS_MAIN_SESSION;break;
 case MENUS_MAIN_SESSION:action=MENUS_MAIN_CLEAR_SESSION;break;
 case MENUS_MAIN_CLEAR_SESSION:action=MENUS_MAIN_CHECK_SESSION;break;
 case MENUS_MAIN_CHECK_SESSION:action=reply.completed ? MENUS_MAIN_COMPLETION : MENUS_MAIN_GAME_OVER;break;
 case MENUS_MAIN_GAME_OVER:case MENUS_MAIN_COMPLETION:action=MENUS_MAIN_INSERT_SCORES;break;
 case MENUS_MAIN_INSERT_SCORES:action=MENUS_MAIN_STOP_MUSIC;break;
 case MENUS_MAIN_RESTART_ATTRACT:action=MENUS_MAIN_REVEAL;break;
 default:break;
 }
 if(action==MENUS_MAIN_WAIT) {if(!menu->budget) action=MENUS_MAIN_BOUND;else menu->budget--;}
 menu->last=action;return action;
}
