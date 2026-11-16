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
    if(kind==GS_TIMER_OPPORTUNITY){t->timer_tick++;t->timer_clocks+=t->pending_clocks;t->pending_clocks=0;}
    t->tick=t->retrace_tick>t->timer_tick?t->retrace_tick:t->timer_tick;
    /* A timer opportunity lasts its programmed PIT interval (1193182 Hz clock),
     * not a 70 Hz retrace period; counting it as 1/70 s made waits that spin
     * on many fast timer ticks sleep for many seconds of wall time. */
    uint64_t retrace_ns=gs_time_tick_ns(t->retrace_tick);
    uint64_t timer_ns=t->timer_clocks/1193182ull*1000000000ull+t->timer_clocks%1193182ull*1000000000ull/1193182ull;
    uint64_t now=retrace_ns>timer_ns?retrace_ns:timer_ns;if(now>t->now_ns)t->now_ns=now;
    *event=(GSEvent){kind,t->tick,t->now_ns};
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
    uint64_t target=t->epoch_ns+t->now_ns,now=SDL_GetTicksNS();
    if(target>now)SDL_DelayNS(target-now);
    return GS_OK;
}
GSTimeOps gs_time_operations(void){return (GSTimeOps){deliver,suspend,pace,NULL,NULL,NULL,NULL,NULL,NULL};}
