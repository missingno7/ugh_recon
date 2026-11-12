"""ADLX mutual families and OPL output; no substitute callees or oracle setup.

All entries are far. Full RAM/device/log comparison is automatic. Every GP,
IF and DF is checked; incidental arithmetic flags are not an event API output.
Untranslated C API call edges are listed separately in the worker report.
"""
from difftest import Case
import struct
import random

REGS=('AX','BX','CX','DX','SI','DI','BP','IF','DF')
CASES=[]


def base(m):
    # Stale high bytes matter: volume/gain are byte stores into word fields.
    for i in range(9):
        data=bytes(((i*31+j*17+3)&255) for j in range(20))
        m.write(m.seg('SOUND:AdlibVoiceStates'),m.off('SOUND:AdlibVoiceStates')+20*i,data)
        m.write(m.seg('SOUND:SavedAdlibVoiceStates'),m.off('SOUND:SavedAdlibVoiceStates')+20*i,data[::-1])
    for name,value in dict(SoundIoDelayMultiplier=1,MainAdlxPlaying=0,CurrentAdlxSlot=0,
            ReservedAdlibChannelCount=0,AdlxPlaybackGuard=0,AdlxTickCount=0xffff,
            AdlxTickHighWord=0xffff,MainAdlxSectionLoopEnabled=0,MusicFadeScheduled=0,
            AdlibInitAttempted=0,AdlxTimerPeriod=0,AdlxPlaybackTimerHandle=2,
            MusicFadeTimerHandle=2).items(): m.ww('SOUND:'+name,value)
    m.ww('TIMER:TimerInterruptInstalled',0)
    m.ww('DGROUP:LastActiveTimerSlotOffset',4)
    m.ww('DGROUP:EarliestTimerIntervalLow',0)
    m.ww('DGROUP:EarliestTimerIntervalHigh',1)
    for i in range(0,32,2):
        m.ww('DGROUP:TimerSlotOffsetByHandle',i if i<=4 else 0x8000,i)
        m.ww('DGROUP:TimerIntervalLowBySlot',0x2000+i,i)
        m.ww('DGROUP:TimerIntervalHighBySlot',0,i)
        m.ww('DGROUP:TimerHandleBySlot',i,i)
    m.ww('SOUND:CurrentAdlxRecordOffset',m.off('SOUND:AudioChannelStates')+8*42)
    s=m.seg('SOUND:AudioChannelStates');o=m.off('SOUND:AudioChannelStates')+8*42
    m.write(s,o,bytes(4*42))
    m.write(s,o+0x26,struct.pack('<H',0x100))
    m.write(0x9000,0x100,bytes(range(12)))


def add(title,routine,setup=None,regs=None,args=(),check=None,flags=0x602,out=REGS,budget=5000000):
    def init(m):
        base(m)
        if setup: setup(m)
    CASES.append(Case(title,'SOUND:'+routine,setup=init,regs=regs or {},args=args,
                      kind='far',out_regs=out,flags=flags,check=check,budget=budget))


for multiplier,bx in ((0,0x2063),(1,0x20ff),(255,0xff00)):
    def setup(m,multiplier=multiplier):m.ww('SOUND:SoundIoDelayMultiplier',0xa500|multiplier)
    def check(m,r,bx=bx):
        assert m.device.log==[(1,0x388,1,bx>>8),(1,0x389,1,bx&255)]
    add(f'write register delay {multiplier}','WriteAdlibRegister',setup,dict(BX=bx),check=check,out=REGS+('CF','OF'))

# Byte channel extraction, invalid values, IF on/off and packed-key byte.
for routine in ('KeyOffAdlibChannel','SetAdlibFrequency'):
    for ch in (0,8,9,255,0xff08):
        for flags in (0x2,0x602):
            def check(m,r,ch=ch,routine=routine,flags=flags):
                valid=(ch&255)<9
                assert len(m.device.log)==(4 if routine=='SetAdlibFrequency' else 2)*valid
                assert bool(r['FLAGS']&512)==(True if valid and routine=='SetAdlibFrequency' else bool(flags&512))
            add(f'{routine} channel {ch:04x} flags {flags:03x}',routine,args=(ch,0xabcd),flags=flags,check=check)

for channel,playing,slot,reserved,connection in (
        (0,0,0,0,0),(8,0,0,0,1),(9,1,12,2,1),(255,0,0,0,1),
        (0xff08,1,12,2,1),(7,1,13,2,0),(6,1,12,2,1),(8,0,12,2,1),
        (8,1,11,2,1),(8,1,12,0x10,1),(8,1,12,0x101,1),(8,1,12,10,1)):
    for volume,gain in ((0,255),(255,255),(129,73)):
        def setup(m,channel=channel,playing=playing,slot=slot,reserved=reserved,connection=connection,gain=gain):
            m.ww('SOUND:MainAdlxPlaying',playing);m.ww('SOUND:CurrentAdlxSlot',slot);m.ww('SOUND:ReservedAdlibChannelCount',reserved)
            if channel&255<9:
                i=(channel&255)*20
                m.ww('SOUND:AdlibConnectionFlags',0xfe00|connection,i)
                m.wb('SOUND:AdlibChannelGain',gain,i)
        def check(m,r,channel=channel,volume=volume,playing=playing,slot=slot,reserved=reserved,connection=connection,gain=gain):
            ch=channel&255
            if ch>=9: assert not m.device.log;return
            displaced=playing&1 and slot>=12 and reserved&15 and ch>=((9-(reserved&255))&255)
            assert m.rb('SOUND:'+('DisplacedAdlibVolume' if displaced else 'AdlibChannelVolume'),ch*20)==volume
            if displaced: assert not m.device.log;return
            level=m.rb('SOUND:AdlibCarrierLevel',ch*20)
            expected=((63-(((63-(level&63))*gain//256)*volume//256))|(level&192))&255
            assert m.device.log[1][3]==expected
            assert len(m.device.log)==(4 if connection else 2)
        add(f'volume {channel:04x}/{playing}/{slot}/{reserved:03x}/{connection}/{volume}/{gain}',
            'SetAdlibChannelVolume',setup,args=(channel,volume|0xab00),check=check)

for ch in (0,8,9,255,0xff08):
    for slot,reserved,playing in ((0,0,0),(12,2,0),(13,2,1),(11,2,1),(12,0x10,1),(12,10,1)):
        def setup(m,slot=slot,reserved=reserved,playing=playing):
            m.ww('SOUND:CurrentAdlxSlot',slot);m.ww('SOUND:ReservedAdlibChannelCount',reserved);m.ww('SOUND:MainAdlxPlaying',playing)
        add(f'gain {ch:04x}/{slot}/{reserved}/{playing}','SetAdlibChannelGain',setup,args=(ch,0xab9d))

for ch,slot,reserved,alias in ((0,0,0,0),(8,12,2,0),(7,12,2,0),(6,12,2,0),(8,13,2,0),
                             (8,12,0x10,0),(8,12,10,0),(9,0,0,0),(255,12,2,0),
                             (0xff08,0,0,0),(0,0,0,1),(0,0,0,2),(0,12,9,3),(0,0,0,4)):
    for connection in (0,1):
        def pointer(m,alias=alias):
            if alias:return m.seg('SOUND:AdlibVoiceStates'),m.off('SOUND:AdlibVoiceStates')+(1 if alias==2 else -1 if alias==4 else 0)
            return 0x9000,0xfffa
        def setup(m,ch=ch,slot=slot,reserved=reserved,alias=alias,connection=connection):
            m.ww('SOUND:CurrentAdlxSlot',slot);m.ww('SOUND:ReservedAdlibChannelCount',reserved)
            s,o=pointer(m,alias);payload=bytes((0x31,0x52,0x73,0x94,0xb5,0xd6,0xf7,0x18,0x39,0x5a,connection,0x80))
            for i,b in enumerate(payload):m.write(s,(o+i)&65535,bytes((b,)))
        def args(m,ch=ch,alias=alias):
            s,o=pointer(m,alias);return ch,o,s
        add(f'instrument {ch:04x}/{slot}/{reserved}/alias{alias}/connection{connection}',
            'LoadAdlibInstrument',setup,args=args)

for scheduled in (0,1,2,3):
    def setup(m,scheduled=scheduled):m.ww('SOUND:MusicFadeScheduled',scheduled)
    add(f'cancel fade scheduled {scheduled}','CancelMusicFade',setup)
    add(f'schedule fade scheduled {scheduled}','ScheduleMusicFade',setup)
for step,duration in ((0,0),(2,2),(0xfffe,0x7fff),(0x7fff,0),(0x8000,0x8000)):
    def setup(m,step=step,duration=duration):
        m.ww('SOUND:MusicFadeStep',step);m.ww('SOUND:MusicFadeDuration',duration);m.ww('SOUND:MusicFadeScheduled',1)
    add(f'fade expire {step:04x}/{duration:04x}','AdvanceMusicFade',setup)

# Event entry receives the opcode, not a new dispatch CALL. Every stream ends
# with a real wait handler, with distinct trailing bytes to expose bad skips.
def event(which,operation,opcode,payload=b'',reserved=0,slot=0,playing=0,base_channel=0,offset=0x100):
    def setup(m):
        m.ww('SOUND:CurrentAdlxSlot',slot);m.ww('SOUND:ReservedAdlibChannelCount',reserved);m.ww('SOUND:MainAdlxPlaying',playing)
        o=m.off('SOUND:AudioChannelStates')+8*42;s=m.seg('SOUND:AudioChannelStates')
        m.write(s,o+0x24,bytes((base_channel,)))
        for i,b in enumerate(payload+b'\x81'):
            m.write(0x9000,(offset+i)&65535,bytes((b,)))
    add(f'{which} {operation} {opcode:02x}/{reserved}/{slot}/{playing}/{base_channel}/{offset:04x}',
        f'Handle{which}Adlx{operation}',setup,dict(AX=0xa500|opcode,ES=0x9000,DI=offset))

for which in ('Main','Effect'):
    for ch in (0,6,7,8,9,15):
        for reserved,slot,playing,bc in ((0,0,0,0),(2,12,1,0),(2,13,0,0),(0,8,0,255)):
            if which=='Main' and bc:continue
            valid=((ch+bc)&255)<9
            for op,nibble in (('Frequency',0x10),('KeyOff',0x20),('Gain',0x30),('Instrument',0x40)):
                accepted=((ch+bc)&255)<=9 if op=='Instrument' and which=='Effect' else valid
                payload=(b'\xef\x32' if op=='Frequency' else bytes(range(11)) if op=='Instrument' else b'\x99' if op=='Gain' else b'') if accepted or op=='Gain' else b''
                event(which,op,nibble|ch,payload,reserved,slot,playing,bc)
    event(which,'NoOp',0x5f)
    event(which,'Gain',0x30,b'\x33',offset=0xffff)
    event(which,'Frequency',0x10,b'\x12\x34',offset=0xfffe)
    # Extensions: zero opcode consumes 3, other consumes length + 1.
    for opcode,payload in ((0x70,b'\xff\x11\x22'),(0x71,b'\x00'),(0x7f,b'\x03\x01\x02\x03')):
        event(which,'Control',opcode,payload)
    for period in (0,1,0x1234,0xffff):
        payload=struct.pack('>H',period)
        event(which,'TimerPeriod',0x60,payload)

for playing,period,request in ((1,100,200),(0,100,200),(2,0x100,0xffff),(1,65535,1),(1,65535,65535)):
    def setup(m,playing=playing,period=period,request=request):
        m.ww('SOUND:MainAdlxPlaying',playing);m.ww('SOUND:AdlxTimerPeriod',period)
        m.write(0x9000,0x100,struct.pack('>H',request)+b'\x81')
    add(f'effect timer ratio {playing}/{period}/{request}','HandleEffectAdlxTimerPeriod',setup,dict(AX=0x60,ES=0x9000,DI=0x100))

for which in ('Main','Effect'):
    for flags,repeat in ((0,0),(1,1),(1,2),(1,0x7fff),(1,0x8000),(1,0xffff),(3,0),(3,1)):
        # Effect expiry has an unavailable peer C edge; not composed acceptance.
        if which=='Effect' and not flags&2 and (repeat==0 or repeat==1 or repeat>=0x8000):continue
        def setup(m,which=which,flags=flags,repeat=repeat):
            if which=='Main':
                m.ww('SOUND:MainAdlxFlags',flags);m.ww('SOUND:MainAdlxRepeatCount',repeat)
                m.ww('SOUND:MainAdlxStartPointer',0xcafe);m.ww('SOUND:MainAdlxStartSegment',0x9000)
            else:
                s=m.seg('SOUND:AudioChannelStates');o=m.off('SOUND:AudioChannelStates')+8*42
                m.write(s,o+0x28,struct.pack('<H',flags));m.write(s,o+4,struct.pack('<HHH',repeat,0xcafe,0x9000))
        add(f'{which} end flags {flags} repeat {repeat:04x}',f'Handle{which}AdlxControl',setup,dict(AX=0xa577,ES=0x9000,DI=0x100))

for guard in (0,1,2,3):
    for low in (0,0xfffe,0xffff):
        def setup(m,guard=guard,low=low):m.ww('SOUND:AdlxPlaybackGuard',guard);m.ww('SOUND:AdlxTickCount',low)
        def check(m,r,guard=guard,low=low):
            expected=(0xffff0000+low+(1 if guard&1 else 2))&0xffffffff
            assert m.rw('SOUND:AdlxTickCount')+(m.rw('SOUND:AdlxTickHighWord')<<16)==expected
        add(f'guarded clock {guard}/{low:04x}','AdvanceGuardedSoundClock',setup,check=check)

# Tick due comparisons: strict high, equal low, before/at/after, guard, all
# four effects, flags filter, reserved nibble. Wait streams are actual handlers.
for guard in (0,1,2):
    for playing,reserved in ((0,0),(1,0),(1,2),(0,2),(1,0x10)):
        for high,low in ((0,0),(1,9),(1,10),(1,11),(2,0)):
            def setup(m,guard=guard,playing=playing,reserved=reserved,high=high,low=low):
                for n,v in dict(AdlxPlaybackGuard=guard,MainAdlxPlaying=playing,ReservedAdlibChannelCount=reserved,
                        AdlxTickCount=9,AdlxTickHighWord=1,MainAdlxDeadlineLow=low,MainAdlxDeadlineHigh=high,
                        MainAdlxCursor=0x100,MainAdlxCursorSegment=0x9000).items():m.ww('SOUND:'+n,v)
                m.write(0x9000,0x100,b'\x81')
                for i,f in enumerate((0,1,5,7)):
                    s=m.seg('SOUND:AudioChannelStates');o=m.off('SOUND:AudioChannelStates')+(8+i)*42
                    m.write(s,o+0x28,struct.pack('<H',f));m.write(s,o+0x1e,struct.pack('<HH',low,high))
                    m.write(s,o+0x10,struct.pack('<HH',0x100,0x9000));m.write(s,o+0x26,struct.pack('<H',0x180))
            add(f'tick {guard}/{playing}/{reserved}/{high}:{low}','TickAdlxPlayback',setup)

def section_before(m):
    m.ww('SOUND:MainAdlxPlaying',1);m.ww('SOUND:MainAdlxDeadlineHigh',0)
    m.ww('SOUND:MainAdlxSectionLoopEnabled',1);m.ww('SOUND:MainAdlxSectionEnd',0x101)
    m.ww('SOUND:MainAdlxCursor',0x100);m.ww('SOUND:MainAdlxCursorSegment',0x9000);m.write(0x9000,0x100,b'\x81')
add('tick section below threshold','TickAdlxPlayback',section_before)

for mutated_table in (False,True):
    def setup(m,mutated_table=mutated_table):
        if mutated_table:m.write(m.seg('SOUND:AdlibOperatorOffsets'),m.off('SOUND:AdlibOperatorOffsets'),bytes(range(0xe0,0xe9)))
    add(f'silence dynamic operators {mutated_table}','SilenceAdlibOperators',setup)
for attempted,installed in ((0,0),(1,0),(255,1),(0,1)):
    def setup(m,attempted=attempted,installed=installed):
        m.wb('SOUND:AdlibInitAttempted',attempted);m.ww('TIMER:TimerInterruptInstalled',installed)
        m.ww('DGROUP:PreviousInt08Offset',0x1234);m.ww('DGROUP:PreviousInt08Segment',0x5678)
    add(f'shutdown attempted {attempted} installed {installed}','ShutdownAdlibPlayback',setup)
for attempted in (1,255):
    def setup(m,attempted=attempted):m.wb('SOUND:AdlibInitAttempted',attempted)
    add(f'init already attempted {attempted}','InitializeAdlibPlayback',setup)
for statuses in ((0xe0,),(0,0),(0,0x20),(0,0xc0)):
    def setup(m,statuses=statuses):
        m.wb('SOUND:AdlibInitAttempted',0)
        m.device.script(0x388,statuses)
        seg=m.seg('SOUND:CalibrateSoundDelay')
        m.device.schedule(seg,m.off('SOUND:loc_1163'),skip=0,clocks=65536)
        m.device.schedule(seg,m.off('SOUND:loc_116B'),skip=1,clocks=65536)
        m.write(0,0x20,struct.pack('<HH',0x2468,0x1357))
    def check(m,r,statuses=statuses):
        assert r['AX']==(len(statuses)==2 and bool(statuses[1]&0xe0))
        assert m.rb('SOUND:AdlibInitAttempted')==1
    add(f'init probe {statuses}','InitializeAdlibPlayback',setup,flags=0x602,check=check,budget=5000000)

# First real event batches, directly in the rebuilt ADLX banks. The 42-byte
# container prefix is outside the event symbols; no oracle runs in setup.
for bank,track in (('B325B','325B'),('B3260','3260'),('B3265','3265'),('B326B','326B'),
                   ('B3274','3274'),('B3279','3279'),('B3279','343F'),('B3444','3444'),
                   ('B3629','3629'),('B3632','3632'),('B3637','3637')):
    for which in ('Main','Effect'):
        def setup(m,which=which):
            m.ww('SOUND:CurrentAdlxSlot',12 if which=='Main' else 8)
            m.ww('SOUND:MainAdlxPlaying',0)
        def regs(m,bank=bank,track=track):
            s,o=m.address(bank+':AdlxEvents_'+track);return dict(ES=s,DI=o)
        add(f'{which} real ADLX {track}',f'Handle{which}AdlxNoOp',setup,regs)
