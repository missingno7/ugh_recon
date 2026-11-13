#include "ugh.h"
typedef struct Target { uint16_t segment,offset; UghAdapter adapter; } Target;
static const Target targets[]={
#include "dispatch_table.inc"
};
UghAdapter ugh_resolve(uint16_t segment,uint16_t offset) {
    for(unsigned i=0;i<sizeof targets/sizeof targets[0];i++)
        if(targets[i].segment==segment && targets[i].offset==offset) return targets[i].adapter;
    return 0;
}
int ugh_dispatch(uint16_t segment,uint16_t offset,Regs *r) {
    UghAdapter fn=ugh_resolve(segment,offset);
    if(!fn) return UGH_BAD_CALLBACK;
    uint16_t cs=r->cs; r->cs=segment;
    int status=fn(r); if(status!=UGH_CONTROL_TRANSFER && status!=UGH_DOS_EXIT) r->cs=cs; return status;
}
int ugh_call_near(uint16_t target,uint16_t return_ip,Regs *r) {
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,return_ip);
    int status=ugh_dispatch(r->cs,target,r);
    if(!status) r->sp=(uint16_t)(r->sp+2);
    return status;
}
/* Entry after PUSHF/CALL FAR or IRQ frame creation. Only accepted IRET bodies
 * are legal. CALL FAR does not itself clear IF/TF. Unknown handlers fail. */
int ugh_dispatch_interrupt(uint16_t segment,uint16_t offset,Regs *r) {
    if(!((segment==GAME_SEG && (offset==G(FailDosCriticalError) || offset==G(HandleKeyboardScanInterrupt))) ||
         (segment==TIMER_SEG && offset==T(HandleTimerInterrupt)) ||
         (segment==SOUND_SEG && (offset==S(HandleDspProbeInterrupt) ||
          offset==S(HandleSampleDmaInterrupt) || offset==S(BeginSoundDelayMeasurement) ||
          offset==S(FinishSoundDelayMeasurement)))))
        return UGH_BAD_CALLBACK;
    UghAdapter fn=ugh_resolve(segment,offset); if(!fn) return UGH_BAD_CALLBACK;
    r->cs=segment; r->ip=offset; int status=fn(r); if(status) return status;
    r->ip=rd16(r->ss,r->sp); r->cs=rd16(r->ss,(uint16_t)(r->sp+2));
    r->flags=rd16(r->ss,(uint16_t)(r->sp+4)); r->sp=(uint16_t)(r->sp+6);
    return UGH_OK;
}
