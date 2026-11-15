#ifndef NATIVE_COMPOSE_FRONT_END_H
#define NATIVE_COMPOSE_FRONT_END_H
#include "game_boot.h"
#include "front_end.h"
#include "pictures.h"
/* Shipped CP437 byte spans, including their delimiters. The cursor is local to
 * the caller; mutable strings are always borrowed from the owning world. */
typedef struct GameFrontText {GSBytes bytes;size_t position;uint16_t x,y;uint8_t delimiter;} GameFrontText;
typedef struct GameFrontResult {GSStatus status;int16_t selection;} GameFrontResult;
typedef enum GameFrontRecipient {GAME_FRONT_BIOS_EDITOR,GAME_FRONT_SCAN_HANDLER} GameFrontRecipient;
GSStatus game_front_recipient(GameWorld *,GameServices *,GameFrontRecipient);
GSStatus game_front_scores_file(GameWorld *,GameServices *,int saving);
GSStatus game_front_digits(GameWorld *,uint32_t,unsigned);
GSStatus game_front_sprite_draw(GameWorld *,GameServices *,uint16_t,uint16_t,uint16_t);
GSStatus game_front_text_line(GameWorld *,GameServices *,GameFrontText *);
GSStatus game_front_text_block(GameWorld *,GameServices *,GameFrontText *);
GSStatus game_front_restore(GameWorld *,GameServices *,FrontRectangle);
GSStatus game_front_save_background(GameWorld *,GameServices *);
GSStatus game_front_header(GameWorld *,GameServices *);
GSStatus game_front_menu_draw(GameWorld *,GameServices *);
GSStatus game_front_password(GameWorld *,GameServices *);
GSStatus game_front_name(GameWorld *,GameServices *);
GameFrontResult game_front_scores_show(GameWorld *,GameServices *);
GameFrontResult game_front_scores_insert(GameWorld *,GameServices *);
GameFrontResult game_front_credits(GameWorld *,GameServices *);
GameFrontResult game_front_picture(GameWorld *,GameServices *,PictureKind,uint16_t);
/* Session supplies semantic text/password views; lookup remains its owner. */
GSStatus game_front_introduction(GameWorld *,GameServices *,GSBytes,GSBytes);
#endif
