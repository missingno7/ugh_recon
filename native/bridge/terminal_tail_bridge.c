#ifdef UGH_NATIVE_LIFECYCLE_WORLD
#include "lifecycle_world_bridge.h"
EXPORT int c_DosShutdownTail(Regs *r){return lifecycle_adapter_terminal(r);}
#else
#include "platform.h"
#include "../terminal_tail.h"
/* These are peer native services. Only this retiring machine adapter carries
 * near-return words, BIOS/DOS register requests and historical return status. */
static int terminal_near(int service,Regs *r) {
    uint16_t saved_cs=r->cs;
    r->sp=(uint16_t)(r->sp-2);
    wr16(r->ss,r->sp,(uint16_t)(G(loc_4EE6)+(service==0?3:13)));
    int status=service==0?c_FadeAndShutdownSound(r):c_RestoreKeyboardInterrupt(r);
    if (status!=UGH_CONTROL_TRANSFER && status!=UGH_DOS_EXIT) r->cs=saved_cs;
    if (!status) r->sp=(uint16_t)(r->sp+2);
    return status;
}
EXPORT int c_DosShutdownTail(Regs *r) {
    TerminalTail tail; terminal_tail_begin(&tail);
    for (;;) {
        int status;
        switch (terminal_tail_next(&tail)) {
        case TERMINAL_STOP_SOUND:
            status=terminal_near(0,r); if(status) return status; break;
        case TERMINAL_RESTORE_VIDEO:
            set_ah(r,0); logic(r,0,8);
            set_al(r,terminal_tail_video_mode(rd8(r->ds,D(SavedBiosVideoMode))));
            status=platform_interrupt(0x10,r); if(status) return status; break;
        case TERMINAL_RESTORE_INPUT:
            status=terminal_near(1,r); if(status) return status; break;
        case TERMINAL_EXIT:
            set_ah(r,0x4c); status=platform_interrupt(0x21,r);
            return status?status:UGH_DOS_EXIT;
        default: return UGH_UNSUPPORTED;
        }
    }
}
#endif
