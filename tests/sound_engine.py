"""Direct SOUND leaves: full RAM, preserved registers, defined flags and PIC log.

No oracle execution in setup; synthetic state plus bytes of rebuilt data only.
The two ADLX dispatchers and DOS/DSP calibration boundaries are deliberately
absent until their real callees/platform services are accepted.
"""
import random
from difftest import Case

REGS=('AX','BX','CX','DX','SI','DI','BP','IF','DF')
ARITH=('CF','PF','AF','ZF','SF','OF')
CASES=[]


def get32(m,name):
    return m.rw(name) | m.rw(name,2)<<16


for al,mult in ((0,0),(1,0),(0,255),(1,1),(255,1),(2,128),(255,255),(128,0x100)):
    def setup(m,mult=mult): m.ww('SOUND:SoundIoDelayMultiplier',mult)
    def check(m,r,al=al,mult=mult):
        overflow=al*(mult&255)>255
        assert bool(r['FLAGS']&1)==overflow
        assert bool(r['FLAGS']&0x800)==overflow
    CASES.append(Case(f'delay AL={al} multiplier={mult:04x}','SOUND:DelaySoundIo',
                      setup=setup,regs=dict(AX=0xa500|al),kind='far',flags=0x602,
                      out_regs=REGS+('CF','OF'),check=check))


# Delta truncation BEFORE Q8 multiply is intentional. DEADLINE high carry,
# overflow and parity flags are compared, including wrap at FFFF:FFFF.
wait_values=[(0x00,0,0,0,0x100),(0x01,0,0xffff,0,0x100),
             (0x0f,255,0xffff,0xffff,0xffff),(0xa3,255,0x8000,0x7fff,0x1234),
             (0x80,1,0,0xffff,0),(0xff,255,1,0x8000,1),
             (0x07,1,0xffff,0x7fff,0x8000),(0x02,1,0x1234,0xff,0xff),
             (0xff,0,0xffff,0xffff,0x100)]
for effect in (False,True):
    for long in (False,True):
        for index,(opcode,payload,low,high,scale) in enumerate(wait_values):
            # Include arbitrary AX high bits; handlers see AL only.
            ax=opcode | 0xa500
            di=0xffff if index==3 else 0x1234
            record=0xffe0 if index==4 else 0x164
            def setup(m,effect=effect,long=long,payload=payload,low=low,high=high,
                      scale=scale,di=di,record=record):
                m.write(0x7800,di,bytes((payload,)))
                if effect:
                    m.ww('SOUND:CurrentAdlxRecordOffset',record)
                    s=m.seg('SOUND:ext_0664')
                    for off,v in ((0x1e,low),(0x20,high),(0x26,scale),(0x10,0xbeef)):
                        m.write(s,(record+off)&65535,v.to_bytes(2,'little'))
                else:
                    m.ww('SOUND:MainAdlxDeadlineLow',low)
                    m.ww('SOUND:MainAdlxDeadlineHigh',high)
                    m.ww('SOUND:MainAdlxCursor',0xbeef)
            def check(m,r,effect=effect,long=long,opcode=opcode,payload=payload,
                      low=low,high=high,scale=scale,di=di,record=record):
                delta=((((opcode&15)*256+payload)*128)&65535) if long else opcode&127
                if effect: delta=delta*scale//256
                expected=((high*65536+low)+delta)&0xffffffff
                end=(di+int(long))&65535
                if effect:
                    s=m.seg('SOUND:ext_0664')
                    def word(off): return int.from_bytes(m.read(s,(record+off)&65535,2),'little')
                    assert word(0x1e)==expected&65535 and word(0x20)==expected>>16
                    assert word(0x10)==end
                else:
                    assert get32(m,'SOUND:MainAdlxDeadlineLow')==expected
                    assert m.rw('SOUND:MainAdlxCursor')==end
            routine=f'SOUND:Handle{"Effect" if effect else "Main"}Adlx{"Long" if long else "Short"}Wait'
            CASES.append(Case(f'{routine} edge={index}',routine,kind='far',setup=setup,
                              regs=dict(AX=ax,ES=0x7800,DI=di),out_regs=REGS+ARITH,
                              flags=0x602,check=check))


for index in (0,1,7,8,12,1560,1561,0x8000,0xffff):
    def setup(m,index=index):
        s=m.seg('SOUND:SampleVoicePairCursor')
        off=(m.off('SOUND:SampleVoicePairCursor')+index*42)&65535
        m.write(s,off,b'\x5a\xa5')
    def check(m,r,index=index):
        assert r['AX']==index*42&65535
        s=m.seg('SOUND:SampleVoicePairCursor')
        off=(m.off('SOUND:SampleVoicePairCursor')+index*42)&65535
        assert m.read(s,off,2)==bytes(2)
        assert bool(r['FLAGS']&1)==(index*42>65535)
    CASES.append(Case(f'reset unchecked voice {index:04x}','SOUND:ResetSampleVoiceCursor',
                      kind='far',setup=setup,regs=dict(AX=index),out_regs=REGS+('CF','OF'),check=check))


def locate_setup(m):
    for prefix in ('One','Two'):
        for suffix in ('Address','Offset'): m.ww('SOUND:DmaMixBuffer'+prefix+suffix,0xffff)
        m.wb('SOUND:DmaMixBuffer'+prefix+'Page',0xff)


def locate_check(m,r):
    base=m.seg('SOUND:ext_0664')*16
    for prefix in ('One','Two'):
        offset=m.off('SOUND:DmaMixBuffer'+prefix+'Offset')+2
        address=base+offset
        assert (address&65535)+1024<65536 # fixed build cannot reach fallback
        assert m.rw('SOUND:DmaMixBuffer'+prefix+'Address')==address&65535
        assert m.rb('SOUND:DmaMixBuffer'+prefix+'Page')==address>>16
        assert m.rw('SOUND:DmaMixBuffer'+prefix+'Offset')==offset


CASES.append(Case('locate fixed relocation, stale headers','SOUND:LocateDmaMixBuffers',
                  kind='far',setup=locate_setup,flags=0x602,out_regs=REGS+ARITH,check=locate_check))


# Direct entry at actual wait events, without traversing untranslated event
# handlers. Offsets were found by reading the rebuilt ADLX event format.
for effect,long,frame,event_offset in ((False,True,0x3279,603),(False,False,0x3279,138),
                                      (True,True,0x325b,23),(True,False,0x325b,25)):
    key=f'B{frame:04X}:AdlxEvents_{frame:04X}'
    def setup(m,effect=effect):
        if effect:
            record=m.off('SOUND:AudioChannelStates')+8*42
            m.ww('SOUND:CurrentAdlxRecordOffset',record)
            for off,v in ((0x1e,0xfffe),(0x20,0x7fff),(0x26,0x1a5)):
                m.write(m.seg('SOUND:ext_0664'),record+off,v.to_bytes(2,'little'))
        else:
            m.ww('SOUND:MainAdlxDeadlineLow',0xfffe)
            m.ww('SOUND:MainAdlxDeadlineHigh',0x7fff)
    def regs(m,key=key,event_offset=event_offset):
        s,o=m.address(key); opcode=m.read(s,o+event_offset,1)[0]
        return dict(ES=s,DI=o+event_offset+1,AX=opcode)
    def check(m,r,key=key,event_offset=event_offset,effect=effect,long=long):
        s,o=m.address(key); data=m.read(s,o+event_offset,2)
        assert (data[0]>>4==0) if long else data[0]>=0x80
        delta=(((data[0]&15)*256+data[1])*128)&65535 if long else data[0]&127
        if effect: delta=delta*0x1a5//256
        expected=(0x7ffffffe+delta)&0xffffffff
        if effect:
            record=m.rw('SOUND:CurrentAdlxRecordOffset')
            actual=int.from_bytes(m.read(m.seg('SOUND:ext_0664'),record+0x1e,4),'little')
        else: actual=get32(m,'SOUND:MainAdlxDeadlineLow')
        assert actual==expected
    routine=f'SOUND:Handle{"Effect" if effect else "Main"}Adlx{"Long" if long else "Short"}Wait'
    CASES.append(Case(f'real ADLX {frame:04X}+{event_offset} {routine}',routine,kind='far',
                      setup=setup,regs=regs,out_regs=REGS+ARITH,check=check))


for old in (0,1,0xff):
    def setup(m,old=old): m.wb('SOUND:DspProbeIrqSeen',old)
    def check(m,r):
        assert m.rb('SOUND:DspProbeIrqSeen')==1
        assert m.device.log==[(1,0x20,1,0x20)]
    CASES.append(Case(f'probe IRQ old flag={old}','SOUND:HandleDspProbeInterrupt',
                      kind='iret',setup=setup,flags=0xed7,out_regs=REGS+ARITH,check=check))


def mixer_case(title,voices,request=8,count=None,mask=None,destination=None,real=False,
               alias=False):
    """voice dict: cursor,length,step,repeat,flags,volume,base; defaults ordinary.
    Reference below computes pairs from static fixture parameters, independently
    of the translated routine's scratch-cell algorithm. Alias cases use full
    RAM comparison, since their live read-after-write behavior is the subject.
    """
    values=[dict(cursor=0,length=16,step=0x200,repeat=1,flags=0,volume=255,
                 base=0x100+i*0x100) for i in range(len(voices))]
    for v,extra in zip(values,voices): v.update(extra)
    voice_count=len(values) if count is None else count
    voice_mask=(1<<len(values))-1 if mask is None else mask
    payload=bytes((0,127,128,255,64,192,1,254,17,239,90,166,33,222,99,156))*8
    def setup(m):
        m.ww('SOUND:ActiveSampleVoiceCount',voice_count)
        m.ww('SOUND:ActiveSampleVoiceMask',voice_mask | 0xa500)
        m.ww('SOUND:SampleMixerBusy',0x9999)
        m.ww('SOUND:SampleMixPairsRemaining',0xdead)
        m.ww('SOUND:SampleMixFirstSum',0xa55a); m.ww('SOUND:SampleMixSecondSum',0x5aa5)
        if real:
            # Real rebuilt bank bytes, preserved in-place; no runtime decoder.
            s,o=m.address('B1A38:IceStream_1A38')
        else: s,o=0x7800,0
        for i,v in enumerate(values):
            base=(o+v['base'])&65535
            if not real:
                # Byte stores explicitly support wrapping base+offset fixtures.
                for j,b in enumerate(payload): m.write(s,(base+j)&65535,bytes((b,)))
            for name,value in [('SampleVoicePairCursor',v['cursor']),('SampleVoiceByteLength',v['length']),
                               ('SampleVoiceStepQ8',v['step']),('SampleVoiceRepeatCount',v['repeat']),
                               ('SampleVoiceFlags',v['flags']),('SampleVoiceVolume',v['volume'])]:
                m.ww('SOUND:'+name,value,i*42)
            m.ww('SOUND:SampleVoiceDataPointer',base,i*42)
            m.ww('SOUND:SampleVoiceDataPointer',s,i*42+2)
        dest=destination if destination is not None else m.off('SOUND:DmaMixBufferOneOffset')+2
        if alias:
            m.ww('SOUND:SampleVoiceDataPointer',dest)
            m.ww('SOUND:SampleVoiceDataPointer',m.seg('SOUND:ext_0664'),2)
            m.write(m.seg('SOUND:ext_0664'),dest,payload[:32])
    def regs(m):
        dest=destination if destination is not None else m.off('SOUND:DmaMixBufferOneOffset')+2
        return dict(BX=request,DX=dest,DS=0x7654,ES=0x7543)
    def check(m,r):
        if voice_count==0:
            assert r['AX']==0 and m.rw('SOUND:SampleMixerBusy')==0x9999
            assert m.rw('SOUND:SampleMixFirstSum')==0xa55a
            return
        assert m.rw('SOUND:SampleMixerBusy')==0
        if alias: return
        vv=[dict(v) for v in values]; active=voice_mask; n=voice_count
        remaining=request//2; expected=bytearray()
        def signed(w): return w-65536 if w&32768 else w
        for _ in range(32768):
            sums=[0,0]; finished=False
            for i,v in enumerate(vv):
                if not active&(1<<i): continue
                offset=(v['cursor']*v['step']//256)&65535
                if offset>=v['length']:
                    if not v['flags']&2:
                        old=v['repeat']; v['repeat']=(old-1)&65535
                        if signed(old)<=1:
                            active^=1<<i; old=n; n=(n-1)&65535
                            if signed(old)<=1: finished=True; break
                            continue
                    v['cursor']=0; continue
                if real:
                    s,o=m.address('B1A38:IceStream_1A38')
                    pair=m.read(s,(o+v['base']+offset)&65535,2)
                else:
                    pair=bytes(payload[j] if 0<=j<len(payload) else 0 for j in (offset,offset+1))
                for k,b in enumerate(pair):
                    sb=b if b<128 else b-256
                    # Python // gives the arithmetic high byte even for negatives.
                    sums[k]+=sb*((v['volume']&255)//2)//256
                v['cursor']=(v['cursor']+1)&65535
            if finished: break
            for value in sums:
                value=signed(value&65535); divisor=signed(n)
                quotient=abs(value)//abs(divisor)*(1 if (value<0)==(divisor<0) else -1)
                expected.append((quotient+127)&255)
            remaining=(remaining-1)&65535
            if signed(remaining)<=0: break
        else: raise AssertionError('independent mixer model did not terminate')
        dest=destination if destination is not None else m.off('SOUND:DmaMixBufferOneOffset')+2
        bank=m.seg('SOUND:ext_0664')
        actual=bytes(m.read(bank,(dest+i)&65535,1)[0] for i in range(len(expected)))
        assert actual==expected, (actual,expected)
        assert r['AX']==(request-remaining)&65535
        assert m.rw('SOUND:ActiveSampleVoiceCount')==n
        assert m.rb('SOUND:ActiveSampleVoiceMask')==active
        for i,v in enumerate(vv):
            assert m.rw('SOUND:SampleVoicePairCursor',i*42)==v['cursor']
            assert m.rw('SOUND:SampleVoiceRepeatCount',i*42)==v['repeat']
    return Case('mix '+title,'SOUND:MixSampleVoicePairs',kind='far',setup=setup,regs=regs,
                out_regs=REGS+ARITH,flags=0x602,check=check)


CASES += [mixer_case('empty stale state',[],request=0),
          mixer_case('mask zero but count one',[{}],mask=0),
          mixer_case('one voice signed samples',[{}]),
          mixer_case('eight voices signed samples',[{} for _ in range(8)]),
          mixer_case('noncontiguous highest voice',[{} for _ in range(8)],mask=0x81,count=2),
          mixer_case('odd request',[{}],request=5),
          mixer_case('zero request runs once',[{}],request=0),
          mixer_case('one request runs once',[{}],request=1),
          mixer_case('maximum request early end',[dict(length=0)],request=65535),
          mixer_case('finite repeat skips pair',[dict(length=2,repeat=3)],request=12),
          mixer_case('infinite repeat skips pair',[dict(length=0,repeat=0,flags=2)]),
          mixer_case('last voice expires',[dict(length=0)]),
          mixer_case('first expires, remaining voice fills',[dict(length=0),{}]),
          mixer_case('last expires, earlier sum retained',[{},dict(length=0)]),
          mixer_case('all voices expire mid pair',[dict(length=0),dict(length=0)]),
          mixer_case('zero repeats',[dict(length=0,repeat=0)]),
          mixer_case('negative repeats overflow JLE',[dict(length=0,repeat=0x8000)]),
          mixer_case('FFFF repeats',[dict(length=0,repeat=0xffff)]),
          mixer_case('8000 active count overflow JLE',[dict(length=0)],count=0x8000),
          mixer_case('negative divisor',[{}],count=0xffff),
          mixer_case('low-byte volume zero',[dict(volume=0xff00)]),
          mixer_case('Q8 fractional step',[dict(step=0x81,volume=129)]),
          mixer_case('Q8 offset truncation',[dict(cursor=0xffff,step=0xffff,length=0xffff)]),
          mixer_case('cursor wraps FFFF to zero',[dict(cursor=0xffff,step=0)]),
          mixer_case('output wraps offset',[{}],destination=0xfffe),
          mixer_case('sample address wraps',[dict(base=0xfffe)],request=4),
          mixer_case('read prior output overlap',[dict(step=0)],alias=True),
          mixer_case('read overlapping byte pairs',[dict(step=0x100)],alias=True),
          mixer_case('real rebuilt bank bytes',[dict(base=0,length=128)],request=32,real=True),
          mixer_case('actual DMA request',[dict(length=0xffff,step=0)],request=1024)]

# Reproducible varied volumes, carries, masks, unsigned Q8 and early endings.
rng=random.Random(0x534f554e44)
for k in range(12):
    voices=[dict(length=rng.randrange(0,18),step=rng.choice((0,0x81,0x100,0x200,0xffff)),
                 volume=rng.randrange(65536),repeat=rng.choice((0,1,2,0x8000)),
                 flags=rng.choice((0,2,0xfffc))) for _ in range(rng.randrange(1,9))]
    CASES.append(mixer_case(f'fixed random {k}',voices,request=rng.randrange(1,20)))


# Shared-service integration cases.

import struct
for routine in ('BeginSoundDelayMeasurement','FinishSoundDelayMeasurement'):
    for cx,dx in ((0,0),(0xffff,0x1234),(7,0xffff)):
        def setup(m):m.ww('SOUND:PreviousCalibrationTimerVector',0x2468);m.ww('SOUND:PreviousCalibrationTimerSegment',0x1357)
        CASES.append(Case(routine+f' CX={cx:04x} DX={dx:04x}','SOUND:'+routine,setup=setup,
            regs=dict(CX=cx,DX=dx),kind='iret',flags=0xed7,out_regs=REGS+ARITH))
for busy in (0,1,7,65536):
    def setup(m,busy=busy):m.ww('SOUND:DspBasePort',0x220);m.device.script(0x22c,[0x81]*busy+([] if busy==65536 else [0x7f]))
    CASES.append(Case(f'DSP busy reads {busy}','SOUND:WriteSoundBlasterDsp',setup=setup,
        regs=dict(AX=0xa5d1),kind='far',out_regs=REGS+('CF','PF','ZF','SF','OF')))
for first,second in ((0,0),(3,5),(1,65537)):
    def setup(m,first=first,second=second):
        m.write(0,0x20,struct.pack('<HH',0x2468,0x1357))
        seg=m.seg('SOUND:CalibrateSoundDelay')
        m.device.schedule(seg,m.off('SOUND:loc_1163'),skip=first,clocks=65536)
        m.device.schedule(seg,m.off('SOUND:loc_116B'),skip=second,clocks=65536)
    def check(m,r,second=second):
        assert m.rw('SOUND:CalibrationLoopRemainder')==(-second)&65535
        assert m.rw('SOUND:SoundIoDelayMultiplier')==(m.off('SOUND:BeginSoundDelayMeasurement')+second//65536)&65535
        assert m.read(0,0x20,4)==struct.pack('<HH',0x2468,0x1357)
        assert m.device.irq_cursor==2
    CASES.append(Case(f'calibration IRQ visits {first}/{second}','SOUND:CalibrateSoundDelay',
        setup=setup,check=check,kind='far',flags=0x602,out_regs=REGS+ARITH))
for which in ('Main','Effect'):
    for opcode in (0x01,0x0f,0x80,0xff):
        def setup(m,opcode=opcode):
            m.write(0x9000,0xfffe,bytes((opcode,0x35)));m.ww('SOUND:CurrentAdlxRecordOffset',m.off('SOUND:AudioChannelStates'))
            m.ww('SOUND:AudioChannelStates',0x100,0x24)
        CASES.append(Case(f'{which} dispatcher wait {opcode:02x}','SOUND:Run'+which+'AdlxEvents',
            setup=setup,regs=dict(ES=0x9000,DI=0xfffe),kind='far',out_regs=REGS+ARITH))
