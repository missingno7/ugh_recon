"""DSP/DMA: actual pilot callees, complete RAM and ordered device comparison.

Fixtures supply raw DSP status/data bytes and real IRQ frames, never mutate game
state from a device hook. No patching of executable bytes or callee substitutions.
There is no embedded DOS PCM sample; real-data cases deliberately use rebuilt
resource bytes as signed samples, without claiming those bytes were PCM assets.
"""
import struct
from difftest import Case

REGS=('AX','BX','CX','DX','SI','DI','BP','IF','DF')
ARITH=('CF','PF','AF','ZF','SF','OF')
LOGIC=('CF','PF','ZF','SF','OF')
CASES=[]


def sound(m,name): return 'SOUND:'+name


def dsp(m,base=0x220,status=(),reads=()):
    m.ww('SOUND:DspBasePort',base)
    if status: m.device.script(base+12,status)
    if reads: m.device.script(base+14,reads)


for index,(count,address,page,status) in enumerate((
    (0,0,0,[0]*3),(1,0xffff,0xff,[0]*3),(0x27,0xfff0,1,[0x80,0x7f]*3),
    (0x28,0x1234,0x12,[1]*3),(0x100,0xff00,0x7f,[0]*3),
    (0x400,0xfc00,2,[0]*3),(0x8000,0x8000,0x80,[0]*3),
    (0xffff,0x8001,0xff,[0xff,0x81,0x7e,0,0]),
    (2,0x3456,3,[0x80]*65536+[0,0]),
)):
    def setup(m,status=status,index=index):
        dsp(m,base=0x200+0x10*(index%7),status=status)
        m.device.dma_flip=1; m.device.dma_address=0xabcd; m.device.dma_count=0x7654
        m.device.dma_page=0x44; m.device.dma_mode=0xff; m.device.dma_mask=0xff
    def check(m,r,count=count,address=address,page=page):
        n=(count-1)&65535
        assert (m.device.dma_address,m.device.dma_count,m.device.dma_page)==(address,n,page)
        assert (m.device.dma_flip,m.device.dma_mode,m.device.dma_mask)==(0,0x49,1)
        assert r['BX']==count and r['AX']==0xa500|(n>>8)
        outs=[(p,v) for k,p,w,v in m.device.log if k==1]
        base=m.rw('SOUND:DspBasePort')
        assert outs==[(10,5),(12,0),(11,0x49),(2,address&255),(2,address>>8),
                      (0x83,page),(3,n&255),(3,n>>8),(10,1),
                      (base+12,0x14),(base+12,n&255),(base+12,n>>8)]
    CASES.append(Case(f'DMA count={count:04x} address={address:04x} page={page:02x}',
                      'SOUND:StartDmaSampleBlock',setup=setup,
                      regs=dict(AX=0xa55a,BX=count,CX=(page<<8)|0x69,DX=address),
                      kind='far',flags=0x602,out_regs=REGS+ARITH,check=check))


for bits,rate in ((0,0),(0,65535),(1,8000),(0xfffd,1000),(2,0),(2,1),(2,999),
                  (2,1000),(2,1001),(2,3906),(2,3907),(2,8000),(2,11025),
                  (2,22050),(2,44100),(2,65535),(0xffff,32768)):
    def setup(m,bits=bits):
        m.ww('SOUND:SoundDeviceBits',bits); dsp(m,status=[0x81,0,0xff,0x7f])
    def check(m,r,bits=bits,rate=rate):
        if bits&2 and rate>=1000:
            assert m.device.log==[(2,0x22c,1,0x81),(2,0x22c,1,0),(1,0x22c,1,0x40),
                                  (2,0x22c,1,0xff),(2,0x22c,1,0x7f),
                                  (1,0x22c,1,(-(1000000//rate))&255)]
        else: assert not m.device.log
    CASES.append(Case(f'rate bits={bits:04x} rate={rate}','SOUND:SetDspSampleRate',
                      setup=setup,args=(rate,),kind='far',flags=0x602,
                      out_regs=REGS+LOGIC+(('AF',) if bits&2 and rate<1000 else ()),check=check))


for index,(not_ready,response) in enumerate(((0,0xaa),(1,0xaa),(98,0xaa),(99,0xaa),
    (100,0xaa),(0,0),(0,0x29),(0,0x2a),(0,0x7f),(0,0x80),(0,0xab),(0,0xff),(100,0xff))):
    base=0x200+0x10*(index%7)
    def setup(m,not_ready=not_ready,response=response,base=base,index=index):
        ready=[0x7f]*not_ready+([] if not_ready==100 else [0x81])
        dsp(m,base=base,reads=ready); m.device.script(base+10,[response])
        m.ww('SOUND:SoundIoDelayMultiplier',(0x100,0,1,0xffff)[index%4])
    def check(m,r,not_ready=not_ready,response=response,base=base):
        polls=min(not_ready+1,100)
        assert r['AX']==response and r['CX']==100-polls and r['DX']==base+10
        assert bool(r['FLAGS']&1)==(response!=0xaa)
        assert m.device.log[:2]==[(1,base+6,1,1),(1,base+6,1,0)]
        assert m.device.log[-1]==(2,base+10,1,response)
        assert len(m.device.log)==polls+3
    CASES.append(Case(f'reset base={base:03x} waits={not_ready} response={response:02x}',
                      'SOUND:ResetSoundBlasterDsp',setup=setup,kind='far',
                      flags=0x602,out_regs=REGS+ARITH,check=check))


def buffers(m,counts=(40,40),offsets=None):
    for i,prefix in enumerate(('One','Two')):
        off=m.off('SOUND:DmaMixBuffer'+prefix+'Offset')+2 if offsets is None else offsets[i]
        physical=m.seg('SOUND:ext_0664')*16+off
        m.ww('SOUND:DmaMixBuffer'+prefix+'Count',counts[i])
        m.wb('SOUND:DmaMixBuffer'+prefix+'Page',physical>>16)
        m.ww('SOUND:DmaMixBuffer'+prefix+'Address',physical&65535)
        m.ww('SOUND:DmaMixBuffer'+prefix+'Offset',off)
        # Wrapped byte stores let the fixture exercise actual word offset wrap.
        for j in range(1024): m.write(m.seg('SOUND:ext_0664'),(off+j)&65535,b'\xa5')


def voice(m,mode):
    m.ww('SOUND:ActiveSampleVoiceCount',0 if mode=='none' else 1)
    m.ww('SOUND:ActiveSampleVoiceMask',0xa500 if mode in ('none','silent') else 0xa501)
    m.ww('SOUND:SampleMixerBusy',0x1234)
    if mode=='none': return
    bank,off=(m.address('B1A38:IceStream_1A38') if mode=='real' else (0x7800,0xfffe))
    if mode!='real': m.write(bank,off,b'\x80\x7f')
    for name,v in (('SampleVoiceDataPointer',off),('SampleVoicePairCursor',0),
                   ('SampleVoiceByteLength',0 if mode=='expire' else 0xffff),
                   ('SampleVoiceRepeatCount',1),('SampleVoiceFlags',0),
                   ('SampleVoiceVolume',255),('SampleVoiceStepQ8',0)):
        m.ww('SOUND:'+name,v)
    m.ww('SOUND:SampleVoiceDataPointer',bank,2)


def irq_case(title,select=1,queued=40,busy=0,mode='none',mask=0x20,pic=0x85,offsets=None):
    initial={}
    def setup(m):
        buffers(m,counts=(queued,queued),offsets=offsets); dsp(m,status=[0]*3,reads=[0x80])
        voice(m,mode); m.wb('SOUND:DspIrqBusy',busy)
        m.wb('SOUND:DmaMixBufferSelect',select); m.wb('SOUND:DspPicIrqMask',mask)
        m.device.pic_mask=pic
        initial['counts']=[m.rw('SOUND:DmaMixBuffer'+p+'Count') for p in ('One','Two')]
    def check(m,r):
        assert m.device.log[0]==(1,0x20,1,0x20)
        if busy&1:
            assert m.device.log==[(1,0x20,1,0x20)]
            assert m.rb('SOUND:DspIrqBusy')==busy
            assert m.rb('SOUND:DmaMixBufferSelect')==select
            return
        assert m.rb('SOUND:DspIrqBusy')==0
        assert m.device.log[1]==(2,0x22e,1,0x80)
        if queued<40:
            assert m.device.pic_mask==pic|mask
            assert m.rb('SOUND:DmaMixBufferSelect')==select
            assert [m.rw('SOUND:DmaMixBuffer'+p+'Count') for p in ('One','Two')]==initial['counts']
            assert m.device.log==[(1,0x20,1,0x20),(2,0x22e,1,0x80),
                                  (2,0x21,1,pic),(1,0x21,1,pic|mask)]
        else:
            chosen='One' if select&1 else 'Two'; other='Two' if select&1 else 'One'
            assert m.rw('SOUND:DmaMixBuffer'+chosen+'Count')==0
            assert m.rb('SOUND:DmaMixBufferSelect')==select^1
            assert m.rw('SOUND:DmaMixBuffer'+other+'Count')==(
                0 if mode=='none' else 512 if mode=='expire' else 1024)
            assert m.device.dma_count==(queued-1)&65535
            assert m.device.pic_mask==pic
            if mode=='expire':
                assert m.rw('SOUND:ActiveSampleVoiceCount')==0
                assert m.rb('SOUND:ActiveSampleVoiceMask')==0
            if mode=='silent' and offsets is None:
                off=m.rw('SOUND:DmaMixBuffer'+other+'Offset'); seg=m.seg('SOUND:ext_0664')
                assert bytes(m.read(seg,(off+i)&65535,1)[0] for i in range(1024))==b'\x7f'*1024
    return Case('IRQ '+title,'SOUND:HandleSampleDmaInterrupt',setup=setup,kind='iret',
                flags=0xed7,out_regs=REGS+ARITH,check=check)


for busy in (1,3,0xff): CASES.append(irq_case(f'reentry busy={busy:02x}',busy=busy))
for select in (0,1,2,3,0xfe,0xff):
    for queued in (0,39,40,0xffff):
        CASES.append(irq_case(f'select={select:02x} queued={queued:04x}',select=select,queued=queued,
                             busy=0xfe,mask=0 if select==2 else 0x84,pic=0x20))
for select in (0,1):
    for mode in ('silent','sample','expire','real'):
        CASES.append(irq_case(f'select={select} mix={mode}',select=select,queued=1024,mode=mode))
# Wrapped output overwrites the low SOUND globals and enables voice mask bits
# partway through mixing. Full live RAM comparison tests that alias behavior;
# a fixed all-7F expected buffer would wrongly assume immutable voice records.
CASES.append(irq_case('wrapped opposite destination aliases voice state',select=1,
                     mode='silent',offsets=(0x9000,0xfffe)))


for bits,count,busy in ((0,1,1),(1,1,1),(0xfffd,1,1),(2,0,0),(2,0xffff,0),
                        (2,0x8000,0),(2,0,0xfffe)):
    def setup(m,bits=bits,count=count,busy=busy):
        m.ww('SOUND:SoundDeviceBits',bits); m.ww('SOUND:ActiveSampleVoiceCount',count)
        m.ww('SOUND:SampleMixerBusy',busy)
    def check(m,r): assert not m.device.log
    CASES.append(Case(f'prime early bits={bits:04x} count={count:04x} busy={busy:04x}',
                      'SOUND:PrimeSampleDmaPlayback',setup=setup,kind='far',flags=0x602,
                      out_regs=REGS+LOGIC+(('AF',) if bits&2 else ()),check=check))


for index,(mode,irq_busy,waits,flags) in enumerate((
    ('silent',0,None,0x602),('sample',0,None,0x402),('real',0,None,0x202),
    ('expire',0,None,0x602),('silent',1,None,0x602),('silent',0,0,0x602),
    ('sample',0,1,0x602),('silent',0,3,0x202),
)):
    initial={}
    def setup(m,mode=mode,irq_busy=irq_busy,waits=waits,initial=initial):
        dsp(m,status=[0]*10,reads=[0x80]*3); buffers(m,counts=(40,40))
        voice(m,mode); m.ww('SOUND:SoundDeviceBits',0xffff)
        m.ww('SOUND:SampleMixerBusy',1 if waits is not None else 0xfffe)
        m.wb('SOUND:DspIrqBusy',irq_busy); m.wb('SOUND:DmaMixBufferSelect',0)
        m.wb('SOUND:DspPicIrqMask',0x20); m.device.pic_mask=0x84
        if waits is not None:
            m.write(0,4*13,struct.pack('<HH',m.off('SOUND:HandleSampleDmaInterrupt'),
                                     m.seg('SOUND:HandleSampleDmaInterrupt')))
            m.device.schedule(m.seg('SOUND:loc_1EA3'),m.off('SOUND:loc_1EA3'),irq=5,skip=waits,clocks=37)
        initial['one']=m.rw('SOUND:DmaMixBufferOneOffset')
    def check(m,r,mode=mode,irq_busy=irq_busy,waits=waits):
        assert m.rw('SOUND:SampleMixerBusy')==0
        assert m.device.irq_cursor==int(waits is not None)
        if irq_busy:
            assert m.rw('SOUND:DmaMixBufferOneCount')==1024
            assert m.rb('SOUND:DmaMixBufferSelect')==1
            assert m.rb('SOUND:DspIrqBusy')==1
        else:
            assert m.rw('SOUND:DmaMixBufferOneCount')==0
            assert m.rb('SOUND:DmaMixBufferSelect')==0
            assert m.rb('SOUND:DspIrqBusy')==0
            assert m.rw('SOUND:DmaMixBufferTwoCount')== (0 if mode=='expire' else 1024)
        assert m.device.pic_mask==0x84
        assert [v for k,p,w,v in m.device.log if k==1 and p==0x22c].count(0xd0)==1
    CASES.append(Case(f'prime composed {index} {mode} irq-busy={irq_busy} wait={waits}',
                      'SOUND:PrimeSampleDmaPlayback',setup=setup,kind='far',flags=flags,
                      out_regs=REGS+LOGIC,check=check))
