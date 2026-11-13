#include "ugh.h"

EXPORT int ugh_call_near_ret_hook(Regs *r,uint16_t target,uint16_t return_ip) {
    /* Restrict this rule to the four independently reconstructed RET leaves. */
    if(target<G(loc_001C) || target>G(loc_001F)) return UGH_BAD_CALLBACK;
    UghAdapter fn=ugh_resolve(GAME_SEG,target); if(!fn) return UGH_BAD_CALLBACK;
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,r->cs);
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,return_ip);
    r->cs=GAME_SEG; r->ip=target; int st=fn(r); if(st) return st;
    r->ip=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2);
    return UGH_CONTROL_TRANSFER;
}
