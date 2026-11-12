"""Sixteen-slot registration, minimum selection, IRQ countdown and real far callback dispatch."""
from difftest import Case
from emu import LOAD

GENERAL=('AX','BX','CX','DX','SI','DI','BP','CF','PF','AF','ZF','SF','OF','IF','DF')


def timer_state(m,slots=1):
    m.ww('DGROUP:LastActiveTimerSlotOffset',(slots-1)*2)
    for i in range(16):
        m.ww('DGROUP:TimerSlotOffsetByHandle',i*2 if i<slots else 0x8000,i*2)
        m.ww('DGROUP:TimerHandleBySlot',i*2,i*2)
        for name in ('TimerIntervalLowBySlot','TimerRemainingLowBySlot'):
            m.ww('DGROUP:'+name,1000 if i else 0,i*2)
        for name in ('TimerIntervalHighBySlot','TimerRemainingHighBySlot'):
            m.ww('DGROUP:'+name,0 if i else 1,i*2)
        # Actual translated far-returning SOUND routine, with an observable RAM effect.
        m.ww('DGROUP:TimerCallbackOffsetBySlot',m.off('SOUND:ClearSoundState'),i*4)
        m.ww('DGROUP:TimerCallbackSegmentBySlot',m.seg('SOUND:ClearSoundState'),i*4)
    m.ww('DGROUP:EarliestTimerIntervalLow',0)
    m.ww('DGROUP:EarliestTimerIntervalHigh',1)


CASES=[]
for slots,low,high,hole in ((1,100,0,None),(4,0,1,2),(15,0xFFFF,0,None),(1,0,0,None),(2,1,2,None),
                            (1,99,1,None)):
    def setup(m,slots=slots,hole=hole,low=low):
        timer_state(m,slots)
        if slots==1 and low==99: m.ww('DGROUP:EarliestTimerIntervalLow',100)
        if hole is not None:
            m.ww('DGROUP:TimerSlotOffsetByHandle',0x8000,hole)
            m.ww('DGROUP:TimerSlotOffsetByHandle',0,slots*2) # force the backward free-handle search
    CASES.append(Case(f'register slots={slots}, interval={high:04X}:{low:04X}, hole={hole}',
                      'TIMER:RegisterTimerCallback',setup=setup,kind='far',
                      regs=lambda m,low=low,high=high:dict(AX=m.off('SOUND:ClearSoundState'),
                          DX=m.seg('SOUND:ClearSoundState'),BX=low,CX=high),out_regs=GENERAL))

for count,remaining,quantum,divisor in ((1,200,100,100),(1,100,100,0),(2,1,100,0),
                                       (16,0,1,1),(2,0x10000,1,0),(2,0x80000000,0,0)):
    def setup(m,count=count,remaining=remaining,quantum=quantum,divisor=divisor):
        timer_state(m,count)
        for i in range(count):
            m.ww('DGROUP:TimerRemainingLowBySlot',remaining,i*2)
            m.ww('DGROUP:TimerRemainingHighBySlot',remaining>>16,i*2)
        m.ww('DGROUP:NextPitQuantumLow',quantum)
        m.ww('DGROUP:NextPitQuantumHigh',quantum>>16)
        m.ww('DGROUP:EarliestTimerIntervalLow',0x1234)
        m.ww('DGROUP:EarliestTimerIntervalHigh',0)
        m.ww('DGROUP:ProgrammedPitDivisor',divisor)
        m.wb('SOUND:MainAdlxPlaying',0x5A)
    CASES.append(Case(f'IRQ slots={count}, remaining={remaining:08X}, quantum={quantum}',
                      'TIMER:HandleTimerInterrupt',setup=setup,kind='iret',out_regs=GENERAL))
