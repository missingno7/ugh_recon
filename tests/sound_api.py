"""Original C API / timer wrapper differential tests; no peer replacement stubs.

Cases requiring absent final-wave OPL/DSP callees are listed in the worker report,
not represented as passing composed calls. All cases compare full nonstack RAM,
live DS/ES, cdecl argument words, preserved registers and return values.
"""
from difftest import Case,load_suite
import struct
timer_state=load_suite('timer_stack').timer_state

KEEP=('SI','DI','BP','IF','DF')
ALL=('AX','BX','CX','DX')+KEEP+('CF','PF','AF','ZF','SF','OF')
CASES=[]

def ww(m,n,v,d=0): m.ww('SOUND:'+n,v,d)
def rw(m,n,d=0): return m.rw('SOUND:'+n,d)
def desc(m,x,d,v): ww(m,'AudioChannelStates',v,42*x+d)
def base(m,bits=0):
    s,o=m.address('SOUND:AudioChannelStates')
    m.write(s,o,bytes((i*37+91)&255 for i in range(13*42)))
    for n,v in dict(SoundDeviceBits=bits,SampleMixerBusy=0,ActiveSampleVoiceCount=0,
                    ActiveSampleVoiceMask=0,ReservedAdlibChannelCount=0,MusicVoiceCount=0,
                    MainAdlxPlaying=0,AdlxPlaybackGuard=0xa523,CurrentAdlxSlot=0x1234,
                    MusicTicksPerUnit=3,MusicTrackVolume=0xabc,MainAdlxSectionLoopEnabled=0xbeef).items(): ww(m,n,v)
    for x in range(8,13):
        for d,v in ((0x28,0),(0x22,0),(0x24,9)): desc(m,x,d,v)

def add(title,name,setup=None,args=(),regs=None,check=None,ret=True,df=False):
    CASES.append(Case(title,'C:'+name,setup=setup,args=args,regs=regs or {},kind='far',
                      out_regs=(('AX',) if ret else ())+KEEP,flags=0x602 if df else 0x202,check=check))

def result(value):
    def check(m,r): assert r['AX']==value&65535,(r['AX'],value)
    return check

# Rejection, active/inactive flags, unsigned/signed slot boundaries and device gates.
for bits in (0,1,2,3):
    for x in (0,7,8,11,12,13,0x8000,0xffff):
        def setup(m,bits=bits,x=x):
            base(m,bits)
            if x<8:
                ww(m,'ActiveSampleVoiceMask',1<<x); ww(m,'ActiveSampleVoiceCount',1)
        expected=-1 if x>12 else 1
        add(f'stop sound bits={bits} x={x}','StopSoundChannel',setup,(x,),check=result(expected))
for x in (0,7):
    add(f'stop inactive sample {x}','StopSoundChannel',lambda m:base(m,2),(x,),check=result(-1))
for bits in (0,1):
    for x in (7,8,11,12,13,0xffff):
        for flags in (0,1,4,5):
            def setup(m,bits=bits,x=x,flags=flags):
                base(m,bits)
                if x in (8,11,12): desc(m,x,0x28,flags)
            add(f'stop ADLX bits={bits} x={x} flags={flags}','StopAdlibTrackChannel',setup,(x,),ret=False)

# Synthetic ADLX chunks use the format's mixed endian fields.
def adlx(voices=0,rate=0x1234,root=90,ahsize=16,imsize=4):
    h=bytearray(b'ADLX'+struct.pack('>I',root)+b'AHDR'+struct.pack('>I',ahsize)+bytes(ahsize)+b'IMAP'+struct.pack('>I',imsize)+bytes(imsize)+b'TRCK'+struct.pack('>I',16)+bytes(32))
    h[18]=voices; h[19]=0xa7; h[22:24]=struct.pack('<H',rate)
    return bytes(h)

def parser_setup(m,data,bits=1,reserved=0,off=0x401):
    base(m,bits); ww(m,'ReservedAdlibChannelCount',reserved)
    # Store using far offset wrap, just like the parser, including FFFF edges.
    for i,b in enumerate(data): m.write(0x7200,(off+i)&65535,bytes([b]))

for x in (7,8,11,12,13,0xffff):
    for bits in (0,1):
        add(f'parse slot gate {bits}/{x}','LoadAdlibTrackData',lambda m,bits=bits:parser_setup(m,adlx(),bits),
            (x,0x401,0x7200,2),check=result(1 if bits and 8<=x<=12 else -1))
for pos in (0,1,2,3,8,9,10,11,32,33,34,35,44,45,46,47):
    h=bytearray(adlx()); h[pos]=0
    add(f'parse tag fail byte {pos}','LoadAdlibTrackData',lambda m,h=bytes(h):parser_setup(m,h),
        (8,0x401,0x7200,1),check=result(-1))
for x,reserved,voices,n,off in ((8,0,9,0,0x401),(11,8,1,2,0x401),(8,9,1,1,0x401),
                               (8,10,255,0xffff,0x401),(12,9,255,0,0x401),
                               (8,0,0,1,0xfff0),(12,0,3,0xffff,0xfff0)):
    add(f'parse voices {x}/{reserved}/{voices} n={n} off={off:x}','LoadAdlibTrackData',
        lambda m,reserved=reserved,voices=voices,off=off:parser_setup(m,adlx(voices),reserved=reserved,off=off),
        (x,off,0x7200,n),check=result(-1 if x!=12 and voices>((9-reserved)&65535) else 1))

for x in (0,7,8,11,12,13,0xffff):
    add(f'load ADLX wrapper invalid parser {x}','LoadAdlibChannel',lambda m:parser_setup(m,b'BAD!'),
        (x,0x401,0x7200,0x4321,3),check=result(-1 if x<8 else 1))
for x in (8,11,12):
    add(f'load ADLX wrapper valid {x}','LoadAdlibChannel',lambda m:parser_setup(m,adlx()),
        (x,0x401,0x7200,0xffff,0),check=result(1))

for x,bits,flags,n,voices,reserved in ((8,0,4,10,0,0),(7,1,4,0x8000,0,0),(13,1,4,0x100,0,0),
    (0xffff,1,4,1,0,0),(8,1,0,255,0,0),(11,1,5,256,0,0),(8,1,4,0x100,0,0),
    (11,1,4,0xffff,0,0),(12,1,4,0x1234,0,0),(8,1,4,19,10,0),(8,1,4,19,2,8)):
    def setup(m,x=x,bits=bits,flags=flags,voices=voices,reserved=reserved):
        base(m,bits); ww(m,'ReservedAdlibChannelCount',reserved)
        if 8<=x<=12:
            desc(m,x,0x28,flags); desc(m,x,0x22,voices)
        ww(m,'AdlxTickCount',0xfffe); ww(m,'AdlxTickCount',0xffff,2)
    expected=1 if bits and 8<=x<=12 and flags==4 and voices+reserved<=9 else -1
    add(f'start ADLX {x}/{bits}/{flags}/{n}/{voices}/{reserved}','StartAdlibTrackChannel',setup,(x,n),check=result(expected))

# Zero-voice allocation still adjusts flags and other descriptors' bases.
for baseidx,reserved,flags in ((9,0,4),(9,0,0),(5,4,4),(0x8001,0,4)):
    def setup(m,baseidx=baseidx,reserved=reserved,flags=flags):
        base(m,1); ww(m,'ReservedAdlibChannelCount',reserved); desc(m,8,0x24,baseidx)
        for x in range(9,12): desc(m,x,0x28,flags); desc(m,x,0x24,x-8)
    # n=0: begin=end, except malformed base can run empty compaction? signed negative skips.
    add(f'restore zero allocation base={baseidx}','RestoreAdlibVoiceAllocation',setup,(8,),ret=False)

for bits,playing,voices in ((0,0,0),(1,0,0),(1,1,0),(3,0,3)):
    def setup(m,bits=bits,playing=playing,voices=voices): base(m,bits); ww(m,'MainAdlxPlaying',playing); ww(m,'MusicVoiceCount',voices)
    add(f'music volume gate {bits}/{playing}/{voices}','SetMusicTrackVolume',setup,(0xffff,),check=result(1 if bits&1 and playing else -1))
for bits,playing in ((0,0),(1,0)):
    def setup(m,bits=bits,playing=playing): base(m,bits); ww(m,'MainAdlxPlaying',playing)
    add(f'stop music gate {bits}/{playing}','StopMusicTrack',setup,(0,),check=result(-1))
add('start music no device','StartMusicTrack',lambda m:base(m,0),(0x401,0x7200,0,255),check=result(-1))
for bits in (0,2,1):
    add(f'outputs no queued voices {bits}','StartSoundOutputs',lambda m,bits=bits:base(m,bits),ret=False)
for latch in (1,0x8000,0xffff):
    def setup(m,latch=latch): base(m,0); m.ww('C:SoundSystemShutdown',latch)
    add(f'shutdown already latched {latch}','ShutdownSoundSystem',setup,ret=False)
for bits in (0,1):
    def setup(m,bits=bits):
        base(m,bits); ww(m,'MainAdlxTimeOrigin',0xfff0); ww(m,'MainAdlxTimeOrigin',0xffff,2)
        ww(m,'ScannedMusicClockTicks',0x30); ww(m,'ScannedMusicClockTicks',1,2)
        ww(m,'FirstScannedEvent',0xfeed); ww(m,'FirstScannedEvent',0x7200,2)
    add(f'apply no music voices {bits}','ApplyScannedMusicEvents',setup,ret=False)

for scenario in ('disabled','free invalid','free valid','replace inactive-loaded'):
    def setup(m,scenario=scenario):
        parser_setup(m,adlx() if scenario=='free valid' else b'BAD!',bits=0 if scenario=='disabled' else 1)
        if scenario=='replace inactive-loaded':
            for x in range(8,12): desc(m,x,0x28,1)
    add('effect '+scenario,'PlayAdlibEffect',setup,(0x401,0x7200,0x1234,0),check=result(-1 if scenario in ('disabled','replace inactive-loaded') else 8))

# IFF parser covers short-circuit tag searches and normalized huge pointers.
def iff(length=7,compressed=0):
    h=bytearray(b'FORM'+struct.pack('>I',80)+b'8SVX'+b'VHDR'+bytes(24)+b'BODY'+struct.pack('>I',length)+bytes(32))
    h[32:34]=b'\x1f\x40'; h[35]=compressed
    return bytes(h)

def iffsetup(m,h,bits=2,seg=0x7100,off=0xfff9):
    base(m,bits)
    # Huge increments normalize modulo 1 MiB. First char uses incoming pointer.
    a=seg*16+off
    for i,b in enumerate(h): m.write(((a+i)&0xfffff)>>4,((a+i)&15),bytes([b]))
for bits,x in ((0,0),(1,0),(2,8),(2,0xffff)):
    add(f'IFF gate {bits}/{x}','LoadIffSample',lambda m,bits=bits:iffsetup(m,iff(),bits=bits),
        (x,0xfff9,0x7100,255,1,256),check=result(-1))
for pos in (0,1,2,3):
    h=bytearray(iff()); h[pos]=0
    add(f'IFF FORM fail {pos}','LoadIffSample',lambda m,h=bytes(h):iffsetup(m,h),(0,0xfff9,0x7100,255,1,256),check=result(-1))
for length,vol,count,stepword,compressed,x in ((0,0,0,0,0,0),(1,255,1,256,0,7),(7,256,2,0xffff,1,0),(64000,65535,0xffff,1,0,3),(64001,1,1,256,0,0)):
    add(f'IFF valid {length}/{vol}/{count}/{stepword}/{compressed}/{x}','LoadIffSample',
        lambda m,length=length,compressed=compressed:iffsetup(m,iff(length,compressed)),
        (x,0xfff9,0x7100,vol,count,stepword),check=result(-1 if length>64000 else 1))
for tag in ('VHDR','BODY'):
    h=bytearray(iff()); pos=h.index(tag.encode()); h[pos:pos+4]=b'XXXX'; h[4:8]=struct.pack('>I',60)
    add(f'IFF missing {tag}','LoadIffSample',lambda m,h=bytes(h):iffsetup(m,h),(0,0xfff9,0x7100,42,0,256),check=result(-1))

# Bank table, word multiplication wrap, equality upper bound, bad format and both loaders.
def banksetup(m,payload,banklen=4096,index=0):
    base(m,3); seg,off=0x7100,0x123
    ww(m,'SoundBankBase',off); ww(m,'SoundBankBase',seg,2); ww(m,'SoundBankLength',banklen); ww(m,'SoundBankLength',0,2)
    m.write(seg,off,struct.pack('<I',16))
    entry=off+16+((index*12)&65535)+8
    m.write(seg,entry,struct.pack('<I',128))
    m.write(seg,off+128,payload)
for x,index,banklen,payload,expect in ((12,0,4096,b'BAD!',-1),(0,0,23,b'BAD!',-1),(0,0,24,b'BAD!',-1),
    (0,0,4096,b'BAD!',-1),(8,0,4096,adlx(),1),(0,0,4096,iff(),1),
    (8,0x8000,4096,adlx(),1),(7,0,4096,adlx(),-1)):
    add(f'bank x={x} index={index} length={banklen} tag={payload[:4]}','LoadBankSoundByIndex',
        lambda m,payload=payload,banklen=banklen,index=index:banksetup(m,payload,banklen,index),
        (x,index,0x1234,2,0x100),check=result(expect))

# Scan: every opcode in both passes, overshoot, wrap, exact end rejection,
# payload size bugs, long waits >65535, channel 15 and explicit switch table dispatch.
def scansetup(m,stream,bits=1,playing=1,voices=9,off=0x601,rate=1):
    base(m,bits); ww(m,'MainAdlxPlaying',playing); ww(m,'MusicVoiceCount',voices); ww(m,'MusicTicksPerUnit',rate)
    ww(m,'MainAdlxStartPointer',off); ww(m,'MainAdlxStartPointer',0x7200,2); ww(m,'MusicEventStreamLength',len(stream))
    for i,b in enumerate(stream): m.write(0x7200,(off+i)&65535,bytes([b]))
for bits,playing in ((0,0),(0,1),(1,0)):
    add(f'scan gate {bits}/{playing}','ScanMusicEvents',lambda m,bits=bits,playing=playing:scansetup(m,b'\x81\x82',bits,playing),
        (1,2),check=result(-1))
streams=[b'\x81\x82\x83\x80',b'\x0f\xff\x81\x80',b'\x01\xff\x81\x80',
         b'\x10\x34\xa0\x20\x30\xff\x40'+bytes(range(12))+b'\x60\x12\x34\x70\x02zz\x85\x87\x80',
         b'\x1f\x34\xe0\x2f\x3f\x80\x4f'+bytes(range(12))+b'\x77\x00\x81\x82\x80']
for i,stream in enumerate(streams):
    for a,b in ((0,0),(1,2),(2,1),(0xffff,0xffff)):
        add(f'scan stream {i} thresholds {a}/{b}','ScanMusicEvents',lambda m,stream=stream:scansetup(m,stream),
            (a,b),df=True)
for stream,off,a,b in ((b'\x81',0x601,1,2),(b'\x81\x82\x80',0xfffe,1,2),(b'\x81\x82\x80',0x601,0,0)):
    add(f'scan edge {stream.hex()} off={off:x}','ScanMusicEvents',lambda m,stream=stream,off=off:scansetup(m,stream,off=off),
        (a,b),df=True)

# Real built resource data, without executing the oracle to prepare a fixture.
for bank in ('325B','326B','3279','3444'):
    label='B'+bank+':AdlxHeader_'+bank
    def setup(m): base(m,1)
    add('real ADLX '+bank,'LoadAdlibTrackData',setup,
        args=lambda m,label=label:(12,m.off(label),m.seg(label),0),check=result(1))
for off in (0xfffa,0xfffb,0xffff):
    add(f'parse two-word size wrap {off:x}','LoadAdlibTrackData',lambda m,off=off:parser_setup(m,adlx(),off=off),
        (12,off,0x7200,1),check=result(1))

# Bounded timer delivery runs the real TIMER ISR and translated ClearSoundState.
# This clears the voice mask while the caller is waiting, testing its recheck.
def busy_irq(m,owner,delta,skip):
    timer_state(m,1)
    m.ww('DGROUP:TimerIntervalLowBySlot',100); m.ww('DGROUP:TimerIntervalHighBySlot',0)
    m.ww('DGROUP:TimerRemainingLowBySlot',1); m.ww('DGROUP:TimerRemainingHighBySlot',0)
    for n in ('NextPitQuantumLow','EarliestTimerIntervalLow','ProgrammedPitDivisor'): m.ww('DGROUP:'+n,100)
    for n in ('NextPitQuantumHigh','EarliestTimerIntervalHigh'): m.ww('DGROUP:'+n,0)
    m.write(0,32,struct.pack('<HH',m.off('TIMER:HandleTimerInterrupt'),m.seg('TIMER:HandleTimerInterrupt')))
    ww(m,'SampleMixerBusy',1)
    m.device.schedule(m.seg('C:'+owner),m.off('C:'+owner)+delta,skip=skip,clocks=177)
for skip in (0,1,3):
    def setup(m,skip=skip):
        base(m,2); ww(m,'ActiveSampleVoiceMask',8); ww(m,'ActiveSampleVoiceCount',1)
        busy_irq(m,'StopSoundChannel',0x53,skip)
    add(f'stop sample real timer wait skip={skip}','StopSoundChannel',setup,(3,),check=result(1))
    def setup(m,skip=skip):
        iffsetup(m,iff()); busy_irq(m,'LoadIffSample',0x4e7,skip)
    add(f'IFF real timer wait skip={skip}','LoadIffSample',setup,(0,0xfff9,0x7100,255,0,256),check=result(1))

for bank in ('325B','326B','3279','3444'):
    label='B'+bank+':AdlxHeader_'+bank
    for a,b in ((0,1),(1,2)):
        def setup(m,label=label):
            base(m,1); s,o=m.address(label)
            length=int.from_bytes(m.read(s,o+4,4),'big')-34
            ww(m,'MainAdlxStartPointer',o+42); ww(m,'MainAdlxStartPointer',s,2)
            ww(m,'MusicEventStreamLength',length); ww(m,'MusicTicksPerUnit',int.from_bytes(m.read(s,o+22,2),'little'))
            ww(m,'MusicVoiceCount',m.read(s,o+18,1)[0]); ww(m,'MainAdlxPlaying',1)
        add(f'real scan {bank} {a}/{b}','ScanMusicEvents',setup,(a,b),df=True)

# A malformed base of 8000h with n=0 reaches a real OPL compaction call.
# See REPORT.md: it is retained as an unresolved diagnostic, not an accepted case.
# 8001h above exercises the signed-loop exit without crossing that absent peer.

for seg,off in ((0xffff,0xf),(0xf000,0xfff9),(0x7100,0x123)):
    add(f'IFF huge representation {seg:x}:{off:x}','LoadIffSample',
        lambda m,seg=seg,off=off:iffsetup(m,iff(),seg=seg,off=off),
        (7,off,seg,256,0,0xffff),check=result(1))
for shift in (0,-16,-8):
    def setup(m,shift=shift):
        base(m,1); s,o=m.address('SOUND:AudioChannelStates'); p=o+8*42+shift
        m.write(s,p,adlx())
    add(f'ADLX descriptor aliases resource {shift}','LoadAdlibTrackData',setup,
        lambda m,shift=shift:(8,m.off('SOUND:AudioChannelStates')+8*42+shift,m.seg('SOUND:AudioChannelStates'),0))

for tag in ('VHDR','BODY'):
    for index in (1,2,3):
        h=bytearray(iff()); pos=h.index(tag.encode()); h[pos+index]=0
        add(f'IFF partial {tag} match {index}','LoadIffSample',lambda m,h=bytes(h):iffsetup(m,h),
            (0,0xfff9,0x7100,255,1,256),check=result(-1))
for length in (65536,0xffffffff):
    add(f'IFF high length {length:x}','LoadIffSample',lambda m,length=length:iffsetup(m,iff(length)),
        (7,0xfff9,0x7100,255,1,256),check=result(-1))
def iffactive(m):
    iffsetup(m,iff()); ww(m,'ActiveSampleVoiceMask',0xa5); ww(m,'ActiveSampleVoiceCount',4)
add('IFF replaces already active sample','LoadIffSample',iffactive,(0,0xfff9,0x7100,255,1,256),check=result(1))
for magic in (b'FORM8SVX',b'ADLXAHDR'):
    for j,position in enumerate((0,1,2,3,8,9,10,11)):
        h=bytearray(iff() if magic.startswith(b'FORM') else adlx()); h[position]=0
        add(f'bank tag short circuit {magic!r}/{j}','LoadBankSoundByIndex',
            lambda m,h=bytes(h):banksetup(m,h),(8,0,255,1,256),check=result(-1))

for stream,a,b,rate in ((b'\x70\x02ab\x81\x82\x80',1,2,1),
                        (b'\x81\x77\x00\x82\x80',1,2,1),
                        (b'\x0f\xff\x81\x80',2,3,65535)):
    add(f'scan extension and high threshold {stream.hex()}/{rate}','ScanMusicEvents',
        lambda m,stream=stream,rate=rate:scansetup(m,stream,rate=rate),(a,b),df=True)
for stamps in ((99,2,80,40),(0xffffffff,0x80000000,0,0x7fffffff),(1,1,1,1)):
    def setup(m,stamps=stamps):
        parser_setup(m,adlx())
        for x,stamp in zip(range(8,12),stamps):
            desc(m,x,0x28,5); desc(m,x,0,stamp); desc(m,x,2,stamp>>16)
    add(f'effect replace unsigned minimum {stamps}','PlayAdlibEffect',setup,(0x401,0x7200,19,0),
        check=result(8+stamps.index(min(stamps))))

for bits in (0,1):
    def setup(m):
        base(m,0);m.wb('SOUND:AdlibInitAttempted',1)
    add(f'initialize complete bits={bits}','InitializeSoundSystem',setup,(bits,),check=result(bits))

for statuses in ((0xe0,),(0,0xc0)):
    def setup(m,statuses=statuses):
        base(m,0);m.wb('SOUND:AdlibInitAttempted',0)
        m.device.script(0x388,statuses)
        for site in ('loc_1163','loc_116B'):
            m.device.schedule(m.seg('SOUND:'+site),m.off('SOUND:'+site),clocks=65536)
    add(f'initialize actual OPL probe {statuses}','InitializeSoundSystem',setup,(1,),check=result(int(len(statuses)==2)))

# Reinitialization tears down an actually allocated prior AdLib timer first.
def reinitialize(m):
    base(m,1);timer_state(m,1)
    m.ww('C:SoundSystemInitialized',1);m.ww('C:SoundSystemShutdown',0)
    m.wb('SOUND:AdlibInitAttempted',1);m.ww('SOUND:AdlxPlaybackTimerHandle',0)
    m.ww('TIMER:TimerInterruptInstalled',1);m.ww('SOUND:SoundIoDelayMultiplier',1)
    m.device.script(0x388,[0xe0])
    for site in ('loc_1163','loc_116B'):
        m.device.schedule(m.seg('SOUND:'+site),m.off('SOUND:'+site),clocks=65536)
add('initialize replaces prior actual AdLib timer','InitializeSoundSystem',reinitialize,(1,),check=result(0))
