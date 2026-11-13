/* Original far-cdecl TIMER stack wrappers. */
#include "ugh.h"
static void push(Regs *r,uint16_t x) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,x); }
static int call(Regs *r,uint16_t seg,uint16_t off,uint16_t ret,const uint16_t *a,unsigned n) {
    uint16_t sp=r->sp;
    for(unsigned i=n;i;i--) push(r,a[i-1]);
    push(r,r->cs); push(r,ret);
    int status=ugh_dispatch(seg,off,r); if(status!=UGH_CONTROL_TRANSFER) r->sp=sp; return status;
}
/* Four far-stack words; AX=handle, all other registers/FLAGS as the real
 * register callee. BP is visible to the callee at entry SP-2 and restored. */
/* TRANSLATES TIMER:RegisterTimerCallbackFromStack */
EXPORT int c_RegisterTimerCallbackFromStack(Regs *r) {
    uint16_t bp=r->bp,sp=r->sp;
    r->ax=arg16(r,0); r->dx=arg16(r,2); r->bx=arg16(r,4); r->cx=arg16(r,6);
    push(r,bp); r->bp=r->sp;
    int st=call(r,TIMER_SEG,T(RegisterTimerCallback),T(RegisterTimerCallbackFromStack)+0x13,0,0);
    r->sp=sp; r->bp=bp; return st;
}
/* One stack handle; DS becomes DGROUP through the removal callee. */
/* TRANSLATES TIMER:RemoveTimerCallbackFromStack */
EXPORT int c_RemoveTimerCallbackFromStack(Regs *r) {
    uint16_t bp=r->bp,sp=r->sp; r->ax=arg16(r,0); push(r,bp); r->bp=r->sp;
    int st=call(r,TIMER_SEG,T(RemoveTimerCallback),T(RemoveTimerCallbackFromStack)+0xa,0,0);
    r->sp=sp; r->bp=bp; return st;
}
/* Three words; the actual target is REMOVE, not the interval setter. */
/* TRANSLATES TIMER:loc_032F */
EXPORT int c_loc_032F(Regs *r) {
    uint16_t bp=r->bp,sp=r->sp;
    r->ax=arg16(r,0); r->bx=arg16(r,2); r->cx=arg16(r,4); push(r,bp); r->bp=r->sp;
    int st=call(r,TIMER_SEG,T(RemoveTimerCallback),T(loc_032F)+0x10,0,0);
    r->sp=sp; r->bp=bp; return st;
}

