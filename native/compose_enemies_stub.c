#include "compose_enemies.h"
/* Replaced by the supervisor's enemy composition at integration. A sentinel
 * terminates the active list; stale slots behind it are deliberately ignored. */
static GSStatus empty(GameWorld *w,GameServices *s){
    if(!w||!s||!w->session.ready)return GS_INVALID;
    return w->session.enemy_end[0]?GS_OK:GS_UNSUPPORTED;
}
GSStatus game_enemies_erase(GameWorld *w,GameServices *s){return empty(w,s);}
GSStatus game_enemies_update(GameWorld *w,GameServices *s){return empty(w,s);}
GSStatus game_enemies_draw_back(GameWorld *w,GameServices *s){return empty(w,s);}
GSStatus game_enemies_draw_front(GameWorld *w,GameServices *s){return empty(w,s);}
