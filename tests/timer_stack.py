"""Original TIMER far-stack wrappers against real timer table bodies."""
from difftest import Case
KEEP=("SI","DI","BP","IF","DF")
ALL=("AX","BX","CX","DX")+KEEP+("CF","PF","AF","ZF","SF","OF")
CASES=[]
# Wrappers use real pilot table routines, including moved-slot bugs.
def timer_state(m,count):
    m.ww('DGROUP:LastActiveTimerSlotOffset',(count-1)*2)
    for i in range(16):
        for n,v in (('TimerIntervalLowBySlot',0 if not i else i*107),
                    ('TimerIntervalHighBySlot',1 if not i else 0),
                    ('TimerRemainingLowBySlot',0x100+i),('TimerRemainingHighBySlot',0x2345+i),
                    ('TimerCallbackDueBySlot',0x8000+i),('TimerHandleBySlot',i*2),
                    ('TimerSlotOffsetByHandle',i*2 if i<count else 0x8000)):
            m.ww('DGROUP:'+n,v,i*2)
        m.ww('DGROUP:TimerCallbackOffsetBySlot',m.off('SOUND:ClearSoundState'),i*4)
        m.ww('DGROUP:TimerCallbackSegmentBySlot',m.seg('SOUND:ClearSoundState'),i*4)
    m.ww('DGROUP:EarliestTimerIntervalLow',0)
    m.ww('DGROUP:EarliestTimerIntervalHigh',1)

for count,lo,hi,hole in ((1,0,0,False),(1,100,0,False),(4,0,1,True),(15,65535,65535,False),(2,1,2,False)):
    def setup(m,count=count,hole=hole):
        timer_state(m,count)
        if hole:
            m.ww('DGROUP:TimerSlotOffsetByHandle',0x8000,2)
            m.ww('DGROUP:TimerSlotOffsetByHandle',0,count*2)
    CASES.append(Case(f'far stack register {count} {hi}:{lo} hole={hole}','TIMER:RegisterTimerCallbackFromStack',
        kind='far',setup=setup,args=lambda m,lo=lo,hi=hi:(m.off('SOUND:ClearSoundState'),m.seg('SOUND:ClearSoundState'),lo,hi),out_regs=ALL,flags=0x602))
for name in ('RemoveTimerCallbackFromStack','loc_032F'):
    for count,index in ((2,1),(3,0),(4,1),(16,15),(3,2)):
        CASES.append(Case(f'{name} slots={count} index={index}','TIMER:'+name,kind='far',
            setup=lambda m,count=count:timer_state(m,count),args=(index*2,0xa55a,0x8001) if name=='loc_032F' else (index*2,),out_regs=ALL,flags=0x402))

