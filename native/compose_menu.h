#ifndef NATIVE_COMPOSE_MENU_H
#define NATIVE_COMPOSE_MENU_H
#include "game_boot.h"
#include "menus.h"
/* SESSION_ENTRY leaves the live configuration/password with their owners.
 * The session slice consumes them, then resumes this same menu continuation. */
typedef enum GameMenuKind {GAME_MENU_SESSION_ENTRY,GAME_MENU_EXIT,
    GAME_MENU_FAILED} GameMenuKind;
typedef struct GameMenuResult {GameMenuKind kind;GSStatus status;MenusMainAction action;} GameMenuResult;
typedef struct GameMenu {MenusMain process;MenusMainReply reply;} GameMenu;
void game_menu_begin(GameMenu *);
/* Session reports its own end/limit decision before re-entering the loop. */
void game_menu_session_return(GameMenu *,int completed);
GameMenuResult game_menu_run(GameWorld *,GameServices *,GameMenu *);
GSStatus game_menu_controls(GameWorld *,GameServices *);
GSStatus game_menu_terminal(GameWorld *,GameServices *);
/* Full production entry. game_boot remains the independently verified startup
 * prefix; this entry consumes its pending main-menu lifecycle request. */
GameMenuResult game_main(GameWorld *,GameServices *,GameMenu *);
#endif
