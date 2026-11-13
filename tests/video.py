"""Final video/input package: rebuilt code versus portable memory model.

No oracle execution occurs in setup. Independent checks cover DAC scaling,
palette copies, page geometry and stale calibration fields. IRQ cases execute
the real pilot keyboard interrupt at explicit original polling instructions.
"""
import struct
from difftest import Case
from emu import DATA_SEG
from dataprobe import IceDecoder, ice_pack235

GENERAL=('AX','BX','CX','DX','SI','DI','BP')
ARITH=('CF','PF','AF','ZF','SF','OF')
ALL=GENERAL+ARITH+('IF','DF')
LOGIC=GENERAL+('CF','PF','ZF','SF','OF','IF','DF')
CASES=[]


for routine,values in (
        ('WaitNextVerticalRetrace',[0,8]),
        ('WaitNextVerticalRetrace',[8,0xf8,9,1,0,0x80,0xff]),
        ('WaitThroughVerticalRetrace',[8,0]),
        ('WaitThroughVerticalRetrace',[1,0x80,0xf8,9,8,0x81])):
    for flags in (0x2,0x602):
        def setup(m,values=values): m.device.script(0x3da,values)
        def check(m,r,routine=routine):
            assert r['AX']&255==(8 if routine=='WaitNextVerticalRetrace' else 0)
            assert r['DX']==0x3da
        CASES.append(Case(f'{routine} {values} flags={flags:04x}','GAME:'+routine,
                          setup=setup,flags=flags,out_regs=LOGIC,check=check))


def input_setup(m,buttons=0,limit=7,mask=0):
    m.wb('GAME:LatestInterruptScanCode',0x9e)
    m.wb('DGROUP:CurrentKeyboardScanCode',0x1e)
    m.wb('DGROUP:JoystickEnabledAxisMask',mask)
    m.ww('DGROUP:JoystickSampleLoopLimit',limit)
    m.device.script(0x201,[0xff^buttons,0xff^buttons]+[0]*4)


for count,button in ((1,0),(3,0),(1,0x10),(0,0x80),(0xffff,0x20),(0x8000,0x40)):
    def setup(m,count=count,button=button):
        input_setup(m,button)
        if not button: m.device.script(0x3da,[0,8]*count)
    def check(m,r,count=count,button=button):
        assert r['AX']==0x39
        assert r['CX']==(count if button else 0)
        assert bool(r['FLAGS']&64)==(r['CX']==0)
        assert m.rb('DGROUP:CurrentKeyboardScanCode')==0x9e
    CASES.append(Case(f'input timeout count={count:04x} button={button:02x}',
                      'GAME:WaitForInputOrRetraceTimeout',setup=setup,
                      regs=dict(DS=DATA_SEG,CX=count,DX=0xbeef),flags=0x602,
                      out_regs=LOGIC,check=check))


def keyboard_irq(m,site,scan,skip=0):
    m.write(0,0x24,struct.pack('<HH',m.off('GAME:HandleKeyboardScanInterrupt'),
                             m.seg('GAME:HandleKeyboardScanInterrupt')))
    # A one-record sequence ending immediately; disabled action remains a real
    # handler branch and the interrupt still latches every raw byte.
    m.write(DATA_SEG,m.off('DGROUP:KeyboardSequenceRecords'),bytes((0x1e,255,0,0,0,0,255)))
    m.ww('DGROUP:PlayerOneControlMode',0)
    m.device.script(0x60,[scan]); m.device.pic_mask=0
    m.device.schedule(m.seg('GAME:'+site),m.off('GAME:'+site),irq=1,skip=skip,clocks=17)


for count,skip,scan in ((7,0,0xe0),(0,1,0x10),(0xffff,2,0x9f)):
    def setup(m,count=count,skip=skip,scan=scan):
        input_setup(m)
        keyboard_irq(m,'loc_449B',scan,skip)
        if skip: m.device.script(0x3da,[0,8]*skip)
    def check(m,r,count=count,skip=skip,scan=scan):
        assert r['AX']==scan|((scan^0x9e)<<8)
        assert r['CX']==(count-skip)&65535
        assert m.device.irq_cursor==1 and m.device.clocks==17
    CASES.append(Case(f'input scan IRQ count={count:04x} skip={skip} scan={scan:02x}',
                      'GAME:WaitForInputOrRetraceTimeout',setup=setup,
                      regs=dict(DS=DATA_SEG,CX=count,DX=0xbeef),out_regs=LOGIC,check=check))


for button in (0x10,0x20,0x40,0x80):
    def setup(m,button=button):
        input_setup(m,button); m.device.script(0x3da,[8,0,0,8])
    def check(m,r,button=button): assert r['AX']==button
    CASES.append(Case(f'scan wait button {button:02x}','GAME:WaitForScanChangeOrJoystickButton',
                      setup=setup,regs=dict(DS=DATA_SEG),flags=0x602,out_regs=LOGIC,check=check))


for skip,scan in ((0,0x1e),(1,0xe0),(3,0x9f)):
    def setup(m,skip=skip,scan=scan):
        input_setup(m); m.device.script(0x3da,[0,8]*(skip+1))
        # This polling CALL has no original label; use the measured instruction
        # displacement from the generated owning label, as in the C body.
        keyboard_irq(m,'loc_44DE',scan)
        m.device.irqs[0].offset=m.off('GAME:loc_44DE')+11
        m.device.irqs[0].skip=skip
    def check(m,r,scan=scan):
        assert r['AX']==scan|((scan^0x9e)<<8)
        assert m.device.irq_cursor==1
    CASES.append(Case(f'scan wait keyboard IRQ skip={skip} scan={scan:02x}',
                      'GAME:WaitForScanChangeOrJoystickButton',setup=setup,
                      regs=dict(DS=DATA_SEG),out_regs=LOGIC,check=check))


def picture(frame=None,raw=None,alias=False):
    expected={}
    def setup(m):
        scratch=m.seg('ZERO:IceDecodeWorkspace')
        # The zero bank is FD00 bytes, not a full segment: the first real ICE
        # resource begins immediately after it. Preserve that adjacent evidence.
        initial=bytearray(m.read(scratch,0,65536))
        initial[:0xfd00]=bytes((i*13+71)&255 for i in range(0xfd00))
        m.write(scratch,0,initial[:0xfd00])
        if frame is not None:
            resource=m.seg(f'B{frame:04X}:IceStream_{frame:04X}')
            stream=m.read(resource,0,65536)
            n=int.from_bytes(stream[8:12],'big'); end=int.from_bytes(stream[4:8],'big')-1
            decoded=IceDecoder(stream,m.raw_image,initial).decode(end,n)
            image=bytearray(initial); image[:n]=decoded
        else:
            resource=0x7500; m.write(resource,0,raw); image=initial
        expected['resource']=resource
        destseg=scratch if alias else m.seg('GAME:BaseRgbPalette')
        dest=0xfa02 if alias else m.off('GAME:BaseRgbPalette')
        m.ww('GAME:PicturePaletteDestination',dest)
        m.ww('GAME:PicturePaletteDestination',destseg,2)
        expected['dest']=(destseg,dest)
        pal=bytes(image[0xfa00:0xfd00])
        if alias: pal=pal[:2]*384  # MOVSW overlap propagates the first word.
        expected['palette']=pal
    def regs(m): return dict(SI=expected['resource'],DS=DATA_SEG,CX=0xbeef)
    def check(m,r):
        s,o=expected['dest']; assert m.read(s,o,768)==expected['palette']
        assert r['SI']==0xfd00 and r['DI']==o+768 and r['CX']==0xbeef
        assert r['ES']==s and not r['FLAGS']&0x400
    return Case(f'picture palette frame={frame} raw={None if raw is None else raw[:4]} alias={alias}',
                'GAME:UnpackPictureAndCopyPalette',setup=setup,regs=regs,flags=0x602,
                out_regs=GENERAL+('IF','DF'),check=check)


CASES += [picture(frame=f) for f in (0x1a38,0x2bf6,0x2d9a,0x2f9e,0x2fb7)]
CASES += [picture(raw=b'bad!'),picture(raw=b'ICxx'),picture(raw=b'bad!',alias=True),
          picture(raw=ice_pack235(bytes(range(256))*8))]


def palette_upload(reverse=False,alternate=False,wrap=False,real=False):
    expected={}
    ds=0x7300 if alternate else DATA_SEG
    def setup(m):
        m.device.script(0x3da,[8,0,0,8])
        if real:
            seg=m.rw('DGROUP:BasePalettePointer',2); off=m.rw('DGROUP:BasePalettePointer')
        else:
            seg=0x7500; off=0xffff if wrap else 0x500
            m.write(seg,0,bytes((i*23+19)&255 for i in range(65537)))
            m.write(ds,m.off('DGROUP:BasePalettePointer'),struct.pack('<HH',off,seg))
        values=[m.read(seg,(off+(-i if reverse else i))&65535,1)[0]&63 for i in range(768)]
        expected['dac']=bytes(values)
        expected['si']=(off+(-768 if reverse else 768))&65535
    def check(m,r):
        assert bytes(m.device.dac)==expected['dac']
        assert r['SI']==expected['si'] and r['BX']==0xff00 and r['DX']==0x3c9
        assert r['FLAGS']&512
    return Case(f'base upload DF={reverse} altDS={alternate} wrap={wrap} real={real}',
                'GAME:UploadBasePalette',setup=setup,regs=dict(DS=ds),
                flags=0x402 if reverse else 2,out_regs=ALL,check=check)


CASES += [palette_upload(real=True),palette_upload(),palette_upload(reverse=True),
          palette_upload(alternate=True),palette_upload(wrap=True),
          palette_upload(reverse=True,wrap=True)]


def scale(factor,reverse=False,alternate=False):
    ds=0x7300 if alternate else DATA_SEG
    expected={}
    def setup(m):
        base=bytes((i*73+11)&255 for i in range(768))
        m.write(m.seg('GAME:BaseRgbPalette'),m.off('GAME:BaseRgbPalette'),base)
        m.write(m.seg('GAME:FadedRgbPalette'),m.off('GAME:FadedRgbPalette'),bytes([0xa7])*768)
        m.write(ds,m.off('DGROUP:FadedPalettePointer'),struct.pack('<HH',m.off('GAME:FadedRgbPalette'),m.seg('GAME:FadedRgbPalette')))
        image=bytearray(m.read(m.seg('GAME:FadedRgbPalette'),0,65536))
        expected['fade']=bytes(((b*factor)>>8)&255 for b in base)
        off=m.off('GAME:FadedRgbPalette'); image[off:off+768]=expected['fade']
        expected['dac']=bytes(image[(off+(-i if reverse else i))&65535]&63 for i in range(651))
        m.device.dac[:]=bytes([37])*768
        m.device.script(0x3da,[0,8])
    def check(m,r):
        assert m.read(m.seg('GAME:FadedRgbPalette'),m.off('GAME:FadedRgbPalette'),768)==expected['fade']
        assert bytes(m.device.dac[:651])==expected['dac']
        assert bytes(m.device.dac[651:])==bytes([37])*117
        assert r['CX']==factor and r['BX']==0xd800 and r['FLAGS']&512
    return Case(f'scale {factor:04x} DF={reverse} altDS={alternate}',
                'GAME:ScaleAndUploadFadedPalette',setup=setup,regs=dict(DS=ds,CX=factor),
                flags=0x402 if reverse else 2,out_regs=ALL,check=check)


CASES += [scale(n) for n in (0,1,4,127,128,252,255,256,257,0x7fff,0x8000,0xffff)]
CASES += [scale(129,True),scale(256,alternate=True)]


for flags in (2,0x602):
    def setup(m):
        m.device.dac[:]=bytes([63])*768; m.device.dac_index=17; m.device.dac_component=2
        m.device.script(0x3da,[0,8]*8)
    def check(m,r):
        assert bytes(m.device.dac)==bytes(768) and r['CX']==0 and r['DX']==0x3c9
        assert r['FLAGS']&512
    CASES.append(Case(f'black palette flags={flags:04x}','GAME:BlackenVgaPalette',
                      setup=setup,flags=flags,out_regs=ALL,check=check))


for display,draw in ((0,0x3e80),(0xa88,0x5a08),(0xffff,0),(0x8000,0xffff),(0x1234,0x1234)):
    def setup(m,display=display,draw=draw):
        m.ww('GAME:DisplayedVgaPagePointer',display); m.ww('GAME:DrawPagePointer',draw)
        m.ww('GAME:DisplayedVgaPagePointer',0x7777,2); m.ww('GAME:DrawPagePointer',0x8888,2)
        m.device.script(0x3da,[8,9,0x80])
    def check(m,r,display=display,draw=draw):
        assert m.rw('GAME:DisplayedVgaPagePointer')==draw and m.rw('GAME:DrawPagePointer')==display
        assert m.rw('GAME:DisplayedVgaPagePointer',2)==0x7777 and m.rw('GAME:DrawPagePointer',2)==0x8888
        assert m.device.crtc[12]==draw>>8 and m.device.crtc[13]==draw&255
    CASES.append(Case(f'page swap {display:04x}/{draw:04x}','GAME:SwapAndDisplayVgaPage',
                      setup=setup,flags=0x602,out_regs=ALL,check=check))


for reverse,mode in ((False,0),(True,0),(False,1),(False,2),(False,3)):
    def setup(m,mode=mode):
        m.device.planes[:]=bytes((i*13+(i>>16)*19+71)&255 for i in range(4*65536))
        m.device.latch[:]=bytes((0x12,0x34,0x56,0x78))
        m.device.gc[5]=mode
        m.device.gc[0]=5; m.device.gc[1]=0; m.device.gc[3]=0; m.device.gc[8]=255
    def check(m,r,mode=mode):
        assert r['AX']==r['CX']==r['DI']==0 and r['ES']==0xa000 and r['DX']==0x3c5
        if mode==0: assert bytes(m.device.planes)==bytes(4*65536)
        if mode==1:
            assert all(bytes(m.device.planes[p*65536:(p+1)*65536])==bytes([m.device.latch[p]])*65536 for p in range(4))
    CASES.append(Case(f'clear all planes DF={reverse} mode={mode}','GAME:ClearAllVgaPlanes',
                      setup=setup,flags=0x602 if reverse else 0x202,out_regs=LOGIC,check=check))


for gameplay in (False,True):
    for reverse in (False,True):
        def setup(m):
            m.device.planes[:]=bytes([0x97])*(4*65536)
            m.device.seq[4]=0xff; m.device.crtc[:]=bytes([0xff])*25
            m.device.attr[16]=0x81; m.device.attr_phase=1; m.device.attr_index=3
            m.device.script(0x3da,[0,8]*9+[0])
        def check(m,r,gameplay=gameplay):
            assert m.rw('GAME:PlayfieldHeight')==(192 if gameplay else 200)
            assert m.rw('GAME:VgaPlaneCopyByteCount')==(0x4800 if gameplay else 0x3e80)
            assert m.rw('GAME:FixedVgaPagePointer')==0
            assert m.rw('GAME:DisplayedVgaPagePointer')==(0x5a08 if gameplay else 0x3e80)
            assert m.rw('GAME:DrawPagePointer')==(0xa88 if gameplay else 0)
            assert m.rw('GAME:BackgroundPagePointer')==(0xa988 if gameplay else 0x7d00)
            assert m.device.seq[4]==0xf7 and m.device.crtc[20]==0xbf and m.device.crtc[23]==0xff
            assert m.device.crtc[19]==(0x30 if gameplay else 0x28)
            assert m.device.attr[16]==0xa1
            assert bytes(m.device.planes)==bytes(4*65536)
        routine='ConfigureVgaGameplayPages' if gameplay else 'ConfigureVgaPicturePages'
        CASES.append(Case(f'{routine} DF={reverse}','GAME:'+routine,setup=setup,
                          flags=0x602 if reverse else 2,out_regs=LOGIC,check=check))


def calibration(presence,axes,alternate=False):
    ds=0x7300 if alternate else DATA_SEG
    expected={}
    def setup(m):
        def ww(name,value): m.write(ds,m.off('DGROUP:'+name),struct.pack('<H',value))
        for name in ('JoystickLeftThresholds','JoystickRightThresholds','JoystickUpThresholds','JoystickDownThresholds',
                     'SecondJoystickXLowThreshold','SecondJoystickXHighThreshold','SecondJoystickYLowThreshold','SecondJoystickYHighThreshold'):
            ww(name,0xbeef)
        ww('PlayerOneControlMode',0x8123); ww('PlayerTwoControlMode',0x8456)
        initial=0xf0|(0 if presence&1 else 3)|(0 if presence&2 else 12)
        # At a falling-axis read the sampler records CX without decrementing.
        # Static high-bit intervals therefore count down only on no-fall reads.
        values=[initial,0xff]
        for tick in range(max(axes)+1):
            low=sum((1<<i) for i,t in enumerate(axes) if tick<t)
            values.append(0xf0|low)
            # Simultaneous falling bits are processed in 1/2/4/8 priority.
            falls=sum(t==tick for t in axes)
            values.extend([0xf0|low]*max(0,falls-1))
        m.device.script(0x201,values)
        def counts(mask):
            # Independent forward counter for the finite waveform. Only reads
            # without a newly falling enabled axis consume a countdown tick.
            result=[65535]*4; elapsed=0; cursor=2
            while mask and elapsed<65535:
                falling=mask&~values[cursor]; cursor+=1
                if falling:
                    bit=falling&-falling; result[bit.bit_length()-1]=elapsed; mask^=bit
                else: elapsed+=1
            return result
        first=counts(3) if presence&1 else [0]*4
        second=counts(15 if presence&1 else 12) if presence&2 else [0]*4
        expected['centers']=[(2*n)&65535 for n in first[:2]+second[2:]]
        expected['thresholds']=first[:2]+second[2:]
    def check(m,r):
        def rw(name): return int.from_bytes(m.read(ds,m.off('DGROUP:'+name),2),'little')
        assert rw('JoystickPresentFlags')==(0xffff if presence&1 else 0)
        assert rw('SecondJoystickPresent')==(0xffff if presence&2 else 0)
        assert m.read(ds,m.off('DGROUP:JoystickEnabledAxisMask'),1)[0]==((3 if presence&1 else 0)|(12 if presence&2 else 0))
        assert rw('PlayerOneControlMode')==(0 if presence&1 else 0x8123)
        assert rw('PlayerTwoControlMode')==(1 if presence&2 else 0x8456)
        centers=[rw(name) for name in ('FirstJoystickXDoubleCenter','FirstJoystickYDoubleCenter',
                                       'SecondJoystickXDoubleCenter','SecondJoystickYDoubleCenter')]
        assert centers==expected['centers']
        assert rw('JoystickSampleLoopLimit')==max(centers) and r['AX']==max(centers)
        for i,(present,count,low,high) in enumerate((
                (presence&1,'FirstJoystickXCount','JoystickLeftThresholds','JoystickRightThresholds'),
                (presence&1,'FirstJoystickYCount','JoystickUpThresholds','JoystickDownThresholds'),
                (presence&2,'SecondJoystickXCount','SecondJoystickXLowThreshold','SecondJoystickXHighThreshold'),
                (presence&2,'SecondJoystickYCount','SecondJoystickYLowThreshold','SecondJoystickYHighThreshold'))):
            n=expected['thresholds'][i]
            assert rw(low)==((n-n//2)&65535 if present else 0xbeef)
            assert rw(high)==((n+n//2)&65535 if present else 0xbeef)
        assert r['FLAGS']&512
    return Case(f'calibrate present={presence} axes={axes} altDS={alternate}',
                'GAME:DetectAndCalibrateJoysticks',setup=setup,regs=dict(DS=ds),flags=0x402,
                out_regs=ALL,check=check)


CASES += [calibration(p,(0,0,0,0)) for p in (0,1,2,3)]
CASES += [calibration(3,a) for a in ((1,2,3,4),(4,3,2,1),(7,1,3,2),(1,7,2,3),
                                  (1,2,7,3),(1,2,3,7),(1,1,1,1),(0,5,0,5))]
CASES += [calibration(1,(1,7,3,4)),calibration(2,(3,4,9,3)),
          calibration(3,(3,1,4,2),True),calibration(1,(32768,32769,0,0))]

for count in (0,1,2,64,0xffff):
    def setup(m,n=count):m.device.script(0x3da,[0,8],cycles=n or 65536)
    CASES.append(Case(f'retrace count {count}','GAME:WaitRetraceCount',setup=setup,
                      regs=dict(CX=count,DX=0xbeef),out_regs=LOGIC,budget=3000000))
for name in ('FadePaletteIn','FadePaletteOut'):
    for reverse in (False,True):
        def setup(m):m.device.script(0x3da,[0,8],cycles=65)
        CASES.append(Case(name+f' complete reverse={reverse}','GAME:'+name,setup=setup,
                          regs=dict(DS=DATA_SEG,CX=0xabcd),flags=0x602 if reverse else 0x202,
                          out_regs=LOGIC,budget=3000000))

from difftest import load_suite
CASES.append(Case('startup subsystem complete initialisation','GAME:InitializeDosVideoInputAndSound',
                  setup=load_suite('menu').entry_quit,regs=dict(DS=DATA_SEG),
                  out_regs=('IF','DF'),budget=10000000))
def sound_init(m):m.wb('SOUND:AdlibInitAttempted',1)
CASES.append(Case('sound wrapper actual C initialisation','GAME:InitializeAdLibSound',setup=sound_init,
                  regs=dict(DS=DATA_SEG),out_regs=('IF','DF')))
CASES.append(Case('sound wrapper actual C shutdown','GAME:FadeAndShutdownSound',
                  regs=dict(DS=DATA_SEG),out_regs=('IF','DF')))
