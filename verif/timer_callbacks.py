"""Additional L0/bridge IRQ composition cases, owned by the timer worker."""
from difftest import Case

def state(m):
    m.ww('DGROUP:LastActiveTimerSlotOffset',4)
    for i in range(16):
        for name,value in [('TimerIntervalLowBySlot',100),('TimerIntervalHighBySlot',0),
                           ('TimerRemainingLowBySlot',1),('TimerRemainingHighBySlot',0),
                           ('TimerSlotOffsetByHandle',i*2 if i<3 else 0x8000),
                           ('TimerHandleBySlot',i*2),('TimerCallbackDueBySlot',0)]:
            m.ww('DGROUP:'+name,value,i*2)
        callback=['TIMER:ChainSavedTimerInterrupt','SOUND:ClearSoundState','SOUND:AdvanceMusicFade'][min(i,2)]
        m.ww('DGROUP:TimerCallbackOffsetBySlot',m.off(callback),i*4)
        m.ww('DGROUP:TimerCallbackSegmentBySlot',m.seg(callback),i*4)
    for name,value in [('NextPitQuantumLow',1),('NextPitQuantumHigh',0),
                       ('EarliestTimerIntervalLow',100),('EarliestTimerIntervalHigh',0),
                       ('PreviousInt08Offset',0x100),('PreviousInt08Segment',0xf000)]:
        m.ww('DGROUP:'+name,value)
    m.ww('SOUND:MusicFadeStep',0)
    m.ww('SOUND:MusicFadeDuration',0)
    m.ww('SOUND:MusicFadeTimerHandle',4)
    m.ww('SOUND:MusicFadeScheduled',1)
    m.wb('SOUND:MainAdlxPlaying',0x5a)

def check(m,r):
    assert m.rw('DGROUP:LastActiveTimerSlotOffset')==2
    assert m.rw('DGROUP:TimerSlotOffsetByHandle',4)==0x8000
    assert m.rw('SOUND:MusicFadeScheduled')==0
    # Tail fade removed itself before the lower clear/BIOS callbacks. Due flags
    # were cleared individually; a prefetched list or stale republish would differ.
    assert all(m.rw('DGROUP:TimerCallbackDueBySlot',i*2)==0 for i in range(3))
    assert m.read(0x40,0x6c,4)==bytes([1,0,0,0])

CASES=[Case('IRQ descending fade self-removal, clear, BIOS chain','TIMER:HandleTimerInterrupt',
            setup=state,kind='iret',check=check,
            out_regs=('AX','BX','CX','DX','SI','DI','BP','CF','PF','AF','ZF','SF','OF','IF','DF'))]
