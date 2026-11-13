"""Timer table routines, including literal removal bugs and malformed offsets.

No device hooks or replacement callees: the missing DOS/vector routines are
deliberately absent. Expected minima below use Python integer ordering, and the
ordinary removal checks describe the observed stale/corrupt mapping contract.
"""
import random

from difftest import Case

OUT=('AX','BX','CX','DX','SI','DI','BP','CF','PF','AF','ZF','SF','OF','IF','DF')
PERIOD=('TimerIntervalLowBySlot','TimerIntervalHighBySlot')
REMAIN=('TimerRemainingLowBySlot','TimerRemainingHighBySlot')
SCALARS=PERIOD+REMAIN+('TimerCallbackDueBySlot',)
CASES=[]


def ww(m,name,value,delta=0):
    m.ww('DGROUP:'+name,value,delta)


def rw(m,name,delta=0):
    return m.rw('DGROUP:'+name,delta)


def state(m,periods,handles=None):
    """Populate 16 slots, retaining conspicuous inactive/stale words."""
    ww(m,'LastActiveTimerSlotOffset',2*(len(periods)-1))
    if handles is None:
        handles=list(range(0,32,2))
    for i in range(16):
        p=periods[i] if i<len(periods) else 0xA1239000+i*73
        ww(m,PERIOD[0],p,i*2)
        ww(m,PERIOD[1],p>>16,i*2)
        ww(m,REMAIN[0],0x1200+i*101,i*2)
        ww(m,REMAIN[1],0xE000+i*19,i*2)
        ww(m,'TimerCallbackDueBySlot',0x8000+i*7,i*2)
        ww(m,'TimerSlotOffsetByHandle',0x8000,i*2)
        ww(m,'TimerHandleBySlot',handles[i],i*2)
        # Real rebuilt callback addresses, never executed by these routines.
        key='SOUND:ClearSoundState' if i%2 else 'TIMER:HandleTimerInterrupt'
        ww(m,'TimerCallbackOffsetBySlot',m.off(key),i*4)
        ww(m,'TimerCallbackSegmentBySlot',m.seg(key),i*4)
    for i in range(len(periods)):
        ww(m,'TimerSlotOffsetByHandle',i*2,handles[i])
    ww(m,'EarliestTimerIntervalLow',0xDEAD)
    ww(m,'EarliestTimerIntervalHigh',0xBEEF)


def assert_minimum(m,r,expected):
    assert (r['CX']<<16)|r['BX']==expected, 'register minimum'
    assert (rw(m,'EarliestTimerIntervalHigh')<<16)|rw(m,'EarliestTimerIntervalLow')==expected
    assert not m.device.log, 'table operations must not request devices'


def setter(title,periods,index,new,flags=0x202,handles=None):
    before={}
    if handles is None:
        handles=list(range(0,32,2))
    after=list(periods)
    after[index]=new
    def setup(m):
        state(m,periods,handles)
        before['remaining']=[rw(m,n,i*2) for n in REMAIN for i in range(16)]
        before['due']=[rw(m,'TimerCallbackDueBySlot',i*2) for i in range(16)]
    def check(m,r):
        assert_minimum(m,r,min(after))
        assert [rw(m,PERIOD[0],i*2)|(rw(m,PERIOD[1],i*2)<<16)
                for i in range(len(periods))]==after
        assert [rw(m,n,i*2) for n in REMAIN for i in range(16)]==before['remaining']
        assert [rw(m,'TimerCallbackDueBySlot',i*2) for i in range(16)]==before['due']
    return Case(title,'TIMER:SetTimerCallbackInterval',setup=setup,kind='far',
                regs=dict(AX=handles[index],BX=new&65535,CX=new>>16),
                flags=flags,out_regs=OUT,check=check)


for title,periods,index,new in (
    ('setter sole BIOS period',[0x10000],0,0x1843),
    ('setter zero interval',[0x10000,0x1D1EB],1,0),
    ('setter new maximum',[0x10000,0x1843],1,0xFFFFFFFF),
    ('setter unsigned high above 8000',[0xFFFF0000,0x8000FFFF,0x7FFF0001],0,0x90000000),
    ('setter equal high low smaller',[0x12348000,0x1234FFFF,0x12340002],1,0x12340001),
    ('setter equal high low greater',[0x12340001,0x12340002],1,0x12348000),
    ('setter exact tie',[0x1D1EB,0x1843,0x1843],0,0x1843),
    ('setter 16 active / replace minimum',[0x10000]+[0x1843+i for i in range(15)],1,0x1D1EB),
):
    CASES.append(setter(title,periods,index,new))
CASES.append(setter('setter permuted handles / IF off DF on',[0x10000,10,20,30],2,0xFFFF,
                    flags=0x402,handles=[0,28,4,16]+list(range(8,32,2))))


def remover(title,periods,index,flags=0x202,handles=None):
    before={}
    if handles is None:
        handles=list(range(0,32,2))
    tail=2*(len(periods)-1)
    destination=2*index
    handle=handles[index]
    after=list(periods[:-1])
    if index<len(after):
        after[index]=periods[-1]
    expected=min([0x10000]+after)
    def setup(m):
        state(m,periods,handles)
        before['moved']={n:rw(m,n,tail) for n in SCALARS}
        before['pointers']={n:rw(m,n,tail) for n in
                            ('TimerCallbackOffsetBySlot','TimerCallbackSegmentBySlot')}
        before['tailhandle']=rw(m,'TimerHandleBySlot',tail)
        before['destinationhandle']=rw(m,'TimerHandleBySlot',destination)
    def check(m,r):
        assert rw(m,'LastActiveTimerSlotOffset')==tail-2
        assert rw(m,'TimerSlotOffsetByHandle',handle)==0x8000
        assert_minimum(m,r,expected)
        assert rw(m,'TimerHandleBySlot',tail)==before['tailhandle'], 'tail handle is self-stored'
        assert rw(m,'TimerHandleBySlot',destination)==before['destinationhandle'], 'no handle move'
        if destination!=tail:
            for n in SCALARS:
                assert rw(m,n,destination)==before['moved'][n], n
            for n in before['pointers']:
                assert rw(m,n,destination)==before['pointers'][n], 'undoubled callback displacement'
            assert rw(m,'TimerSlotOffsetByHandle')==(0x8000 if handle==0 else handles[len(periods)-1])
            assert r['AX']==handles[len(periods)-1]
        else:
            assert r['AX']==handle
    return Case(title,'TIMER:RemoveTimerCallback',setup=setup,kind='far',regs=dict(AX=handle),
                flags=flags,out_regs=OUT,check=check)


for title,periods,index in (
    ('remove tail / retain earlier minimum',[0x10000,0x1843,0x1D1EB],2),
    ('remove tail / cap above BIOS period',[0xFFFFFFFF,0x80000000],1),
    ('remove moved / callback half-pointer bug',[0x10000,0x1234,0x3210],1),
    ('remove moved / handle zero overwritten then freed',[0x10000,0x1843,0x1D1EB],0),
    ('remove moved / zero minimum',[0x10000,123,0,456],1),
    ('remove moved / exact ties',[0x10000,0x1843,0x1843,0x1843],1),
    ('remove moved / equal-high low branches',[0x12340001,0x1234FFFF,0x12340002],1),
    ('remove moved / unsigned 8000 high',[0x80000001,0xFFFFFFFF,0x7FFFFFFF],1),
    ('remove 16 slots',[0x10000]+[i*77 for i in range(1,16)],8),
):
    CASES.append(remover(title,periods,index))
CASES.append(remover('remove permuted handles / IF off DF on',[0x10000,100,200,300],1,
                    flags=0x402,handles=[0,28,4,16]+list(range(8,32,2))))


def underflow_setup(m):
    state(m,[0x10000])
    # Removing slot zero scans FFFEh once: low aliases LastActiveTimerSlotOffset,
    # high aliases inactive low slot 15. Arrange the latter as zero explicitly.
    ww(m,PERIOD[0],0,30)


def underflow_check(m,r):
    assert rw(m,'LastActiveTimerSlotOffset')==0xFFFE
    assert rw(m,'TimerSlotOffsetByHandle')==0x8000
    assert_minimum(m,r,0xFFFE)


CASES.append(Case('remove only slot / scan wrapped FFFE once','TIMER:RemoveTimerCallback',
                  setup=underflow_setup,regs=dict(AX=0),kind='far',out_regs=OUT,check=underflow_check))


def odd_setup(m):
    state(m,[0x10000,30,50])
    ww(m,'TimerSlotOffsetByHandle',3,3)


CASES.append(Case('setter unaligned handle and slot','TIMER:SetTimerCallbackInterval',
                  setup=odd_setup,regs=dict(AX=3,BX=0xFF00,CX=0x8000),kind='far',out_regs=OUT))


def special_setter(title,last,slot,new):
    def setup(m):
        state(m,[0x10000,10,20])
        ww(m,'LastActiveTimerSlotOffset',last)
        ww(m,'TimerSlotOffsetByHandle',slot,2)
    return Case(title,'TIMER:SetTimerCallbackInterval',setup=setup,
                regs=dict(AX=2,BX=new&65535,CX=new>>16),kind='far',out_regs=OUT)


CASES += [
    special_setter('setter effective offset wraps segment',4,0x85B2,7),
    special_setter('setter FFFE scan starts negative',0xFFFE,2,0xFFFFFFFF),
    special_setter('setter 8000 scan wraps signed boundary',0x8000,2,0x90008000),
    special_setter('setter FFFF odd scan starts negative',0xFFFF,2,0xFFFFFFFF),
    special_setter('setter invalid free-handle marker is literal slot',4,0x8000,9),
    # New low period aliases LastActiveTimerSlotOffset before it is re-read.
    special_setter('setter aliased period changes scan length',4,0xFFFE,0x60004),
]


def malformed_remove(title,last,destination,handle=2):
    def setup(m):
        state(m,[0x10000,10,20])
        ww(m,'LastActiveTimerSlotOffset',last)
        ww(m,'TimerSlotOffsetByHandle',destination,handle)
    return Case(title,'TIMER:RemoveTimerCallback',setup=setup,
                regs=dict(AX=handle),kind='far',out_regs=OUT)


CASES += [
    malformed_remove('remove destination aliases following array',4,32),
    malformed_remove('remove destination aliases handle map',4,160),
    malformed_remove('remove destination aliases last-slot cell',4,0xFFFE),
    malformed_remove('remove moved writes across wrapped offset',4,0x85B2),
    malformed_remove('remove last decrement wraps 8002 to 8000',0x8002,0x8002),
    malformed_remove('remove last decrement underflows 1 to FFFF',1,1),
    malformed_remove('remove invalid free handle literal destination',4,0x8000),
]


random_source=random.Random(0x0A32021B)
for i in range(12):
    count=random_source.randrange(2,17)
    periods=[random_source.getrandbits(32) for _ in range(count)]
    index=random_source.randrange(count)
    value=random_source.getrandbits(32)
    flags=(0x202,0x602,0x2,0x402)[i%4]
    CASES.append(setter(f'seeded setter {i}',periods,index,value,flags))
    CASES.append(remover(f'seeded remover {i}',periods,index,flags))


# Shared-service integration cases.

import struct
for operation in ('InstallTimerInterrupt','RestoreTimerInterrupt'):
    for installed in (0,1,2,0xffff):
        for initial_flags in (0x202,0x602,0x2):
            def setup(m,installed=installed):
                m.ww('TIMER:TimerInterruptInstalled',installed)
                m.write(0,0x20,struct.pack('<HH',0x1357,0x2468))
                m.ww('DGROUP:PreviousInt08Offset',0xabcd); m.ww('DGROUP:PreviousInt08Segment',0x4567)
                for n in ('TimerCallbackDueBySlot','TimerRemainingLowBySlot','TimerRemainingHighBySlot'):
                    for i in range(16): m.ww('DGROUP:'+n,0x9234+i,2*i)
            CASES.append(Case(f'{operation} installed={installed:04X} flags={initial_flags:04X}',
                'TIMER:'+operation,setup=setup,kind='far',flags=initial_flags,
                out_regs=tuple(x for x in OUT if x!='AF')))
for flags in (2,0x202,0x602,0xcd7):
    def setup(m):
        seg,off=m.address('GAME:FailDosCriticalError')
        m.ww('DGROUP:PreviousInt08Offset',off);m.ww('DGROUP:PreviousInt08Segment',seg)
    CASES.append(Case(f'chain accepted IRET target flags={flags:04X}',
        'TIMER:ChainSavedTimerInterrupt',setup=setup,regs=dict(DS=0x6c19),kind='far',flags=flags,out_regs=OUT))
# Whole-game timing fixture: chain the real callback through an explicit BIOS
# INT08 service, preserving its PUSHF/CALL FAR/IRET frame. No BIOS code is used.
from emu import DATA_SEG
for _ticks,_midnight in ((0,0),(0x1800af,0),(0x1800af,255),(0xffffffff,7)):
    def _bios_setup(m,ticks=_ticks,midnight=_midnight):
        m.ww('DGROUP:PreviousInt08Offset',0x100)
        m.ww('DGROUP:PreviousInt08Segment',0xf000)
        m.write(0x40,0x6c,ticks.to_bytes(4,'little'))
        m.write(0x40,0x70,bytes([midnight]))
    def _bios_check(m,r,ticks=_ticks,midnight=_midnight):
        next_tick=(ticks+1)&0xffffffff
        rollover=next_tick>=0x1800b0
        assert int.from_bytes(m.read(0x40,0x6c,4),'little')==(0 if rollover else next_tick)
        assert m.read(0x40,0x70,1)[0]==(midnight+rollover)&255
        assert m.device.log==[(1,0x20,1,0x20)]
    CASES.append(Case(f'BIOS timer chain { _ticks:08x}/{_midnight}',
                      'TIMER:ChainSavedTimerInterrupt',setup=_bios_setup,check=_bios_check,
                      regs=dict(DS=DATA_SEG),kind='far',out_regs=('AX','BX','CX','DX','SI','DI','BP','IF','DF')))
