"""Package-local contracts, independent value/pixel checks, and full RAM comparison."""
from difftest import Case
from emu import DATA_SEG

GENERAL=('AX','BX','CX','DX','SI','DI','BP')
ARITH=('CF','PF','AF','ZF','SF','OF')
CASES=[]


def scale_case(value, speed, alternate=False):
    name='ScaleLevelSpeedToThreeHalves' if speed else 'ScaleLevelYToThreeQuarters'
    ds=0x7600 if alternate else DATA_SEG
    def setup(m):
        m.write(ds,m.off('DGROUP:CoordinateScaleScratch'),b'\x5a\xa5')
    def check(m,r):
        signed=value if value<32768 else value-65536
        removed=signed//(2 if speed else 4)
        expected=(value+removed if speed else value-removed)&65535
        assert r['AX']==expected
        assert int.from_bytes(m.read(ds,m.off('DGROUP:CoordinateScaleScratch'),2),'little')==removed&65535
    return Case(f'{name} {value:04X} alternate DS={alternate}','GAME:'+name,
                setup=setup,check=check,regs=dict(AX=value,DS=ds),flags=0x602,
                out_regs=GENERAL+ARITH+('DF','IF'))


for speed in (False,True):
    for value in (0,1,2,3,4,5,0x3fff,0x4000,0x5555,0x5556,0x7fff,
                  0x8000,0x8001,0xaaaa,0xaaab,0xfffb,0xfffc,0xfffd,0xfffe,0xffff):
        CASES.append(scale_case(value,speed))
    CASES.append(scale_case(0xfffd,speed,True))


def cache_case(index,alternate=False):
    ds=0x7600 if alternate else DATA_SEG
    pairs=(('PlayerSpriteIds','PlayerCachedSpriteIds'),('PlayerPixelX','PlayerCachedPixelX'),
           ('PlayerYPixels','PlayerCachedPixelY'))
    def setup(m):
        for i,(src,dst) in enumerate(pairs):
            m.write(ds,(m.off('DGROUP:'+src)+index)&65535,bytes((0x81+i,0xfe-i)))
            m.write(ds,(m.off('DGROUP:'+dst)+index)&65535,b'\x55\xaa')
    def check(m,r):
        for i,(_,dst) in enumerate(pairs):
            assert m.read(ds,(m.off('DGROUP:'+dst)+index)&65535,2)==bytes((0x81+i,0xfe-i))
    return Case(f'cache index={index:04X} alternate DS={alternate}','GAME:CachePlayerDrawState',
                setup=setup,check=check,regs=dict(BX=index,DS=ds),flags=0xed7,
                flag_inputs=ARITH,out_regs=GENERAL+ARITH+('DF','IF'))


CASES += [cache_case(i) for i in (0,2,1,0xffff,0xd820)]+[cache_case(2,True)]


def decimal_case(digits,value,dest=0x500,alternate=False,alias=False,custom=False,signed_edge=False):
    ds=0x7600 if alternate else DATA_SEG
    name={2:'EncodeTwoDecimalDigits',4:'EncodeFourDecimalDigits',6:'EncodeSixDecimalDigits'}[digits]
    expected={}
    def setup(m):
        divisors={'DecimalTenDivisor':bytes((7 if custom else 10,)),
                  'DecimalHundredDivisor':bytes((91 if custom else 100,)),
                  'DecimalThousandDivisor':(997 if custom else 1000).to_bytes(2,'little'),
                  'DecimalTenThousandDivisor':(65535 if signed_edge else 9991 if custom else 10000).to_bytes(2,'little')}
        if alternate or custom or signed_edge:
            for label,data in divisors.items(): m.write(ds,m.off('DGROUP:'+label),data)
        start=m.off('DGROUP:DecimalTenDivisor') if alias else dest
        # Independently evaluate ordered decimal writes on a private static RAM
        # fixture, including outputs that overwrite divisors before a shared tail.
        memory=bytearray(m.read(ds,0,65536)); cursor=start
        def put(v):
            nonlocal cursor
            memory[cursor]=v&255; cursor=(cursor+1)&65535
        def word(label):
            o=m.off('DGROUP:'+label); return memory[o] | memory[(o+1)&65535]<<8
        v=value
        if digits==6:
            # The signed high-word stopping test can stop immediately with a
            # large unsigned remainder. Compute that domain independently.
            if ((v-100000)&0xffffffff)&0x80000000:
                put(0)
            else:
                put(v//100000); v%=100000
            divisor=word('DecimalTenThousandDivisor')
            put(v//divisor); v%=divisor
        if digits>=4:
            divisor=word('DecimalThousandDivisor')
            put(v//divisor); v%=divisor
            divisor=memory[m.off('DGROUP:DecimalHundredDivisor')]
            put(v//divisor); v%=divisor
        else: v&=255
        divisor=memory[m.off('DGROUP:DecimalTenDivisor')]
        put(v//divisor); put(v%divisor); put(255)
        expected.update(memory=memory,start=start,end=cursor)
    def check(m,r):
        start=expected['start']
        assert r['SI']==(start+digits)&65535
        for i in range(digits+1):
            o=(start+i)&65535
            assert m.read(ds,o,1)[0]==expected['memory'][o]
    def regs(m):
        return dict(AX=(value&65535) if digits!=2 else 0xa500|(value&255),DX=value>>16,
                    DS=ds,SI=m.off('DGROUP:DecimalTenDivisor') if alias else dest)
    return Case(f'decimal {digits} {value} dest={dest:04X} alt={alternate} alias={alias} custom={custom}',
                'GAME:'+name,setup=setup,check=check,regs=regs,flags=0x602,
                out_regs=GENERAL+('DF','IF'))


for digits,values in ((2,(0,1,9,10,11,89,90,99,100,255)),
                      (4,(0,1,9,10,99,100,999,1000,9999,10000,65535)),
                      (6,(0,1,9999,10000,65535,99999,100000,100001,999999,1000000,25599999,25600000))):
    CASES.extend(decimal_case(digits,v) for v in values)
    CASES += [decimal_case(digits,89,0xffff),decimal_case(digits,89,alternate=True),
              decimal_case(digits,89,custom=True)]
# First output overwrites the ten divisor with 12; the shared tail reads it live.
CASES.append(decimal_case(4,12345,alias=True))
CASES += [decimal_case(6,v,signed_edge=True) for v in (0x80010000,0x80020000,0xfffe0000)]


def rain_case(water,phases,alternate=False):
    ds=0x7600 if alternate else DATA_SEG
    expected={}
    def setup(m):
        m.write(ds,m.off('DGROUP:WaterYPixels'),(water&65535).to_bytes(2,'little'))
        m.ww('GAME:DrawPagePointer',0xfffc)
        index=(water*2)&65535
        indices=[]
        while True:
            indices.append(index)
            index=(index-2)&65535
            if index&0x8000: break
        for i,index in enumerate(indices):
            for label,v in (('RainParticleOffsets',(i*97)&65535),
                            ('RainParticleXModuloFour',phases[i%len(phases)])):
                m.write(ds,(m.off('DGROUP:'+label)+index)&65535,(v&65535).to_bytes(2,'little'))
        m.device.planes[:]=bytes((i*7+19)&255 for i in range(4*65536))
        planes=bytearray(m.device.planes)
        # Read static state after all setup, so table aliases are intentional.
        for index in indices:
            def rw(label):
                return int.from_bytes(m.read(ds,(m.off('DGROUP:'+label)+index)&65535,2),'little')
            shift=rw('RainParticleXModuloFour')&31
            mask=(1<<shift)&255
            offset=(rw('RainParticleOffsets')+0xfffc)&65535
            for p in range(4):
                if mask&(1<<p): planes[p*65536+offset]=0x5b
        expected['planes']=planes
    def check(m,r):
        assert m.device.planes==expected['planes']
        assert r['AX']==0x5b0f and r['ES']==0xa000 and m.device.map_mask==15
    return Case(f'rain water={water:04X}, phases={phases}, alt={alternate}',
                'GAME:DrawRainParticles',setup=setup,check=check,regs=dict(DS=ds),
                flags=0x602,out_regs=GENERAL+ARITH+('DF','IF'))


CASES += [rain_case(0,(0,)),rain_case(3,(0,1,2,3)),rain_case(191,(3,2,1,0)),
          rain_case(8,(4,7,8,31,32,33,0x100,0xff)),rain_case(0xffff,(2,)),
          rain_case(0x8000,(1,)),rain_case(3,(0,1,2,3),True)]
CASES.append(rain_case(0x4000,(0,1,2,3)))


BANKS=('SpritePixels0To216Pointer','SpritePixels217To297Pointer',
       'SpritePixels298To546Pointer','SpritePixels547AndUpPointer')


def sprite_case(sprite,x,y,water,width=5,height=4,real=False,reverse=False,
                source_wrap=False,playfield=192,alternate=False):
    expected={}
    ds=0x7600 if alternate else DATA_SEG
    def setup(m):
        m.ww('GAME:DrawPagePointer',0xfff8)
        m.ww('GAME:FixedVgaPagePointer',0xe321)
        m.ww('GAME:PlayfieldHeight',playfield)
        m.ww('GAME:RendererScratchWord',0xa55a)
        m.ww('GAME:SpritePlaneStateScratch',0x5aa5)
        m.write(ds,m.off('DGROUP:WaterYPixels'),(water&65535).to_bytes(2,'little'))
        if not real:
            m.ww('GAME:SpriteDirectoryPointer',0x100)
            m.ww('GAME:SpriteDirectoryPointer',0x7500,2)
            m.write(0x7500,(0x100+sprite*4)&65535,
                    bytes((0xf0 if source_wrap else 0x10,0xff if source_wrap else 0,width,height)))
            for i,bank in enumerate(BANKS):
                m.ww('GAME:'+bank,i*0x1000)
                m.ww('GAME:'+bank,0x9000,2)
            # Independent bytes vary with bank, contain zeros and pre-set shade bits.
            m.write(0x9000,0,bytes(0 if i%7==0 else (i*13+i//4096*17)&255 for i in range(65536)))
        directory=(m.rw('GAME:SpriteDirectoryPointer')+sprite*4)&65535
        directory_seg=m.rw('GAME:SpriteDirectoryPointer',2)
        record=m.read(directory_seg,directory,4)
        source=int.from_bytes(record[:2],'little')
        w,h=record[2],record[3]
        bank=BANKS[sum(sprite>=v for v in (217,298,547))]
        source=(source+m.rw('GAME:'+bank))&65535
        source_seg=m.rw('GAME:'+bank,2)
        data=bytes(m.read(source_seg,(source+(-i if reverse else i))&65535,1)[0]
                   for i in range((w or 256)*(h or 256)))
        m.device.planes[:]=bytes((i*11+0x95)&255 for i in range(4*65536))
        planes=bytearray(m.device.planes)
        yy=y if y<playfield else y-192
        threshold=(water-yy)&65535
        signed=threshold if threshold<32768 else threshold-65536
        page=0xfff8 if y<playfield else 0xe321
        # Walk screen rows in the independent model; packed source is column-major.
        for row in range(h or 256):
            for col in range(w or 256):
                pixel=data[col*(h or 256)+row]
                if pixel:
                    # Zero height selects the all-above path when threshold>=0.
                    shade=signed<0 or (signed<h and row>signed)
                    if shade: pixel|=0x40
                    address=(page+x//4+yy*96+(x%4+col)//4+row*96)&65535
                    plane=(x+col)%4
                    planes[plane*65536+address]=pixel
        expected.update(planes=planes,threshold=threshold,
                        bp=(threshold-(h or 256))&65535 if 0<=signed<h else threshold)
    def check(m,r):
        assert m.device.planes==expected['planes']
        assert m.rw('GAME:RendererScratchWord')==expected['threshold']
        assert r['BP']==expected['bp']
        assert m.device.seq_index==2 and m.device.map_mask==15
    return Case(f'sprite {sprite} x={x} y={y} water={water} {width}x{height} real={real} '
                f'DF={reverse} wrap={source_wrap} playfield={playfield} alt={alternate}',
                'GAME:DrawTransparentSprite',setup=setup,check=check,
                regs=dict(AX=sprite,BX=x&65535,CX=y&65535,DS=ds),
                flags=0x602 if reverse else 0x202,out_regs=GENERAL+ARITH+('DF','IF'))


# All bank boundaries, all planes, three shading bodies and both page branches.
for sprite in (0,216,217,297,298,546,547,600):
    CASES.append(sprite_case(sprite,sprite%4,20,21))
for water in (19,20,21,23,24,25):
    CASES.append(sprite_case(217,3,20,water))
CASES += [sprite_case(298,-1,-2,0),sprite_case(547,-32768,191,0),
          sprite_case(0,32767,192,2),sprite_case(216,5,193,1),
          sprite_case(0,1,190,191,playfield=180),
          sprite_case(217,2,20,22,reverse=True,source_wrap=True),
          sprite_case(0,2,20,22,reverse=True),
          sprite_case(0,3,20,21,source_wrap=True),
          sprite_case(0,3,-32768,32767),sprite_case(0,3,32767,32768),
          sprite_case(600,2,20,21,alternate=True),
          sprite_case(0,3,20,21,width=0,height=2),
          sprite_case(217,3,20,21,width=2,height=0),
          sprite_case(547,3,20,19,width=2,height=0),
          sprite_case(298,3,20,20,width=0,height=0)]
for sprite in (0,216,217,297,298,546,547,600):
    CASES.append(sprite_case(sprite,3,30,32,real=True))


# Shared-service integration cases.

for mask in (1,5,15):
    for mode in (0,0x10):
        for reverse in (False,True):
            for count in (0,1,13):
                def setup(m,mask=mask,mode=mode,count=count,reverse=reverse):
                    m.device.map_mask=mask;m.device.gc[5]=mode
                    for p in range(4): m.device.planes[p*65536:(p+1)*65536]=bytes((p*37+i*13)&255 for i in range(256))*256
                    m.ww('GAME:DrawPagePointer',0xfffa if reverse else 0x1200)
                    m.ww('GAME:BackgroundPagePointer',0x6000);m.ww('GAME:VgaPlaneCopyByteCount',count)
                CASES.append(Case(f'save latch page mask={mask} mode={mode} reverse={reverse} n={count}',
                    'GAME:SaveDrawPageBackground',setup=setup,flags=0x602 if reverse else 0x202,
                    out_regs=('AX','BX','CX','DX','SI','DI','BP','CF','PF','ZF','SF','OF','IF','DF')))
for x,y,w,h in ((0,0,1,1),(3,2,16,3),(0xffff,0xffff,9,2),(0x8000,0,0,1),(0,0,0,0),(0x7fff,5,0xffff,2)):
    for mask in (5,15):
        def setup(m,mask=mask):
            m.device.map_mask=mask
            for p in range(4):m.device.planes[p*65536:(p+1)*65536]=bytes((i*17+p*29)&255 for i in range(256))*256
            m.ww('GAME:DrawPagePointer',0x4000);m.ww('GAME:BackgroundPagePointer',0)
        CASES.append(Case(f'restore rectangle {x:04x}/{y:04x}/{w:04x}/{h:04x} mask={mask}',
            'GAME:RestoreBackgroundRectangle',setup=setup,regs=dict(AX=x,BX=y,CX=w,DX=h),flags=0x602,
            out_regs=('AX','BX','CX','DX','SI','DI','BP','CF','PF','ZF','SF','OF','IF','DF')))
for column,row in ((0,0),(1,2),(0xffff,0xffff)):
    CASES.append(Case(f'restore tile {column}/{row}','GAME:RestoreTileBackground',setup=setup,
        regs=dict(AX=column,BX=row),flags=0x602,out_regs=('AX','BX','CX','DX','SI','DI','BP','IF','DF')))
for water in (0,2,0xffff,0x8000):
    def setup(m,water=water):
        m.ww('DGROUP:WaterYPixels',water);m.ww('GAME:BackgroundPagePointer',0);m.ww('GAME:DrawPagePointer',0x4000)
        for i in range(6):m.ww('DGROUP:RainPreviousOffsets',0x123+i,2*i)
        for p in range(4):m.device.planes[p*65536:(p+1)*65536]=bytes((i+p*31)&255 for i in range(256))*256
    CASES.append(Case(f'restore rain water={water:04x}','GAME:RestoreRainBackground',setup=setup,
        regs=dict(DS=0x6c19),out_regs=('AX','BX','CX','DX','SI','DI','BP','CF','PF','AF','ZF','SF','OF','IF','DF')))
