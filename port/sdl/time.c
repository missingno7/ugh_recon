#include "backend.h"
#include <string.h>
/* Integer rational time: seventy complete event cycles occupy exactly a second.
 * Delayed rendering may delay delivery, but never skips or synthesizes a tick. */
uint64_t gs_time_tick_ns(uint64_t tick) {
    return tick/70*1000000000ull+(tick%70)*1000000000ull/70;
}
void gs_time_init(GSSdlTime *t,int paced) {
    memset(t,0,sizeof *t);t->paced=paced;t->epoch_ns=SDL_GetTicksNS();
}
static GSStatus deliver(void *context,GSEventKind kind,GSEvent *event) {
    GSSdlTime *t=context;if(!event)return GS_INVALID;
    if(t->suspended)return GS_EMPTY;
    if((unsigned)kind>GS_INPUT_OPPORTUNITY)return GS_INVALID;
    if(kind==GS_RETRACE_ACTIVE)t->retrace_tick++;
    if(kind==GS_TIMER_OPPORTUNITY)t->timer_tick++;
    t->tick=t->retrace_tick>t->timer_tick?t->retrace_tick:t->timer_tick;
    *event=(GSEvent){kind,t->tick,gs_time_tick_ns(t->tick)};
    return GS_OK;
}
static GSStatus suspend(void *context,int value) {
    GSSdlTime *t=context;uint64_t now=SDL_GetTicksNS();
    if(value&&!t->suspended){t->suspended=1;t->suspended_at=now;}
    if(!value&&t->suspended){t->epoch_ns+=now-t->suspended_at;t->suspended=0;}
    return GS_OK;
}
static GSStatus pace(void *context) {
    GSSdlTime *t=context;if(!t->paced||t->suspended)return GS_OK;
    uint64_t target=t->epoch_ns+gs_time_tick_ns(t->tick),now=SDL_GetTicksNS();
    if(target>now)SDL_DelayNS(target-now);
    return GS_OK;
}
GSTimeOps gs_time_operations(void){return (GSTimeOps){deliver,suspend,pace,NULL,NULL,NULL,NULL,NULL,NULL};}
