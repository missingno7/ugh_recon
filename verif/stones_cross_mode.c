/* A real demo initialization -> first-level load -> native stone -> actual
 * gameplay draw path. Renderer history must survive both native transitions. */
#include "ugh.h"
#include "actor_projection.h"
int stones_actual_gameplay_draw(Regs *r);
EXPORT int stones_cross_mode(void) {
    Regs r={0};r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=0x9000;r.sp=0x1000;r.flags=0x202;r.si=0x1792;
    if(c_InitializeDemoScripts(&r)) return -1;
    ActorRenderStorage history;actor_bridge_render_project(DATA_SEG,&history);ActorRenderHistory before=history.slots[2];
    if(before.pixel_x!=320 || before.pixel_y!=106 || before.previous_x!=320 || before.previous_y!=106) return -2;
    wr16(DATA_SEG,D(PlayerCount),1);wr16(DATA_SEG,D(CurrentLevelIndex),0);
    if(c_LoadCurrentLevelState(&r)) return -3;
    if(c_DispatchActorUpdates(&r) || c_ResetSpriteEraseState(&r)) return -4;
    actor_bridge_render_project(DATA_SEG,&history);
    if(history.slots[2].pixel_x!=before.pixel_x || history.slots[2].pixel_y!=before.pixel_y) return -5;
    r.bx=4;if(c_UpdateStonePickupWait(&r)) return -6;
    if(rd16(DATA_SEG,(uint16_t)(D(ActorSpriteIds)+4))!=0x220) return -7;
    if(stones_actual_gameplay_draw(&r)) return -8;
    actor_bridge_render_project(DATA_SEG,&history);
    if(history.slots[2].previous_x!=before.pixel_x || history.slots[2].previous_y!=before.pixel_y) return -9;
    if(history.slots[2].pixel_x==before.pixel_x && history.slots[2].pixel_y==before.pixel_y) return -10;
    return 1;
}
