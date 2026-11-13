"""Scene package: real callees, full RAM/VGA comparison, no dependency stubs."""
import random
import struct
from difftest import Case
from emu import DATA_SEG

GENERAL=('AX','BX','CX','DX','SI','DI','BP')
OUT=GENERAL+('CF','PF','AF','ZF','SF','OF','IF','DF')
CASES=[]
def words(*v): return struct.pack('<'+'H'*len(v),*(x&65535 for x in v))
def put(m,ds,name,value,index=0): m.write(ds,(m.off('DGROUP:'+name)+index)&65535,words(value))
def get(m,ds,name,index=0): return int.from_bytes(m.read(ds,(m.off('DGROUP:'+name)+index)&65535,2),'little')


def initialize_case(n=1,xy=(10,20),period=3,callback='IgnoreActorState',
                    token=7,ds=DATA_SEG,vector=0x5000,script=0x6000,real=None):
    expected={}
    def setup(m):
        # Poison stale arrays independently of register poisoning.
        for name in ('ActorSpriteIds','ActorEraseSprite','ActorX32','ActorY32',
                     'ActorPixelX','ActorPixelY','ActorPreviousDrawX','ActorPreviousDrawY',
                     'ActorAnimationCountdowns','ActorMotionWaitOrDemoRepeats','ActorPlatformOrScriptDone'):
            for i in range(16): put(m,ds,name,0xa751+i,2*i)
        if real:
            expected['si']=m.off('DGROUP:'+real)
            pointers=[]
            for i in range(16):
                p=get(m,ds,real,2*i)
                if p==65535: break
                pointers.append(p)
            expected['n']=len(pointers)
        else:
            expected['si']=vector; expected['n']=n
            for i in range(n):
                p=(script+i*32)&65535
                m.write(ds,(vector+i*2)&65535,words(p))
                data=words(xy[0]+i,xy[1]-i,period,m.off('GAME:'+callback))
                data+=words(token) if token==0x8000 else struct.pack('<HBB',token,0xff,2)
                # Word operands are contiguous at FFFF; the next effective read wraps.
                for j in range(0,8,2): m.write(ds,(p+j)&65535,data[j:j+2])
                m.write(ds,(p+8)&65535,data[8:10])
                for j in range(10,len(data)): m.write(ds,(p+j)&65535,data[j:j+1])
            m.write(ds,(vector+2*n)&65535,words(65535))
        expected['headers']=[]; expected['active']=expected['n']
        for i in range(expected['n']):
            p=int.from_bytes(m.read(ds,(expected['si']+2*i)&65535,2),'little')
            if (p+8)&65535==65535: expected['active']=min(expected['active'],i)
            x=int.from_bytes(m.read(ds,p,2),'little')
            y=int.from_bytes(m.read(ds,(p+2)&65535,2),'little')
            expected['headers'].append((x,y))
    def regs(m): return dict(DS=ds,SI=expected['si'])
    def check(m,r):
        assert r['BX']==2*expected['active'] and r['SI']==65535
        for i,(x,y) in enumerate(expected['headers']):
            assert get(m,ds,'ActorPixelX',2*i)==x
            assert get(m,ds,'ActorPixelY',2*i)==y
            assert get(m,ds,'ActorPreviousDrawX',2*i)==x
            assert get(m,ds,'ActorPreviousDrawY',2*i)==y
        for i in range(16): assert get(m,ds,'ActorEraseSprite',2*i)==65535
        if not real and token!=0x8000:
            for i,(x,y) in enumerate(expected['headers'][:expected['active']]):
                assert get(m,ds,'ActorX32',2*i)==(x*32-4)&65535
                assert get(m,ds,'ActorY32',2*i)==(y*32+8)&65535
    return Case(f'initialize n={n} xy={xy} period={period} cb={callback} token={token:x} '
                f'ds={ds:x} vector={vector:x} script={script:x} real={real}',
                'GAME:InitializeDemoScripts',setup=setup,regs=regs,check=check,out_regs=OUT)


CASES += [initialize_case(n=0),initialize_case(),initialize_case(n=16),
          initialize_case(xy=(-32768,32767),period=0),
          initialize_case(xy=(-1,-2),period=65535),
          initialize_case(callback='SetDemoRevealSpriteWidth',xy=(300,-1)),
          initialize_case(callback='StartDemoFadeWhenSpriteHidden',token=0x7fff),
          initialize_case(token=0x8000),initialize_case(ds=0x7500),
          initialize_case(script=0xfff7),initialize_case(script=0xfff5),
          initialize_case(script=0xfff9),initialize_case(vector=0xfffe,n=2)]
for table in ('DemoTable_1020','DemoTable_1792','DemoTable_1E40','DemoTable_24DE'):
    CASES.append(initialize_case(real=table))


def alias_header_setup(m):
    # X32 storage overwrites the header Y word before that word is loaded.
    header=(m.off('DGROUP:ActorX32')-2)&65535
    m.write(DATA_SEG,0x5000,words(header,65535))
    m.write(DATA_SEG,header,words(0x1234,0x7ffe,3,m.off('GAME:IgnoreActorState'))+
            struct.pack('<HBB',7,255,2))
def alias_header_check(m,r):
    assert m.rw('DGROUP:ActorPixelY')==0x4680
    assert m.rw('DGROUP:ActorX32')==0x467c
    assert m.rw('DGROUP:ActorY32')==0xd008
CASES.append(Case('initialize header Y aliases live X32','GAME:InitializeDemoScripts',
                  setup=alias_header_setup,regs=dict(DS=DATA_SEG,SI=0x5000),
                  check=alias_header_check,out_regs=OUT))


def draw_case(slots,ds=DATA_SEG,reverse=False,real=False):
    def setup(m):
        for i,(sprite,x,y) in enumerate(slots):
            for name,value in (('ActorUpdateOrScriptCursor',0x6000),('ActorSpriteIds',sprite),
                               ('ActorX32',x),('ActorY32',y),('ActorPixelX',1234+i),
                               ('ActorPixelY',5678+i),('ActorPreviousDrawX',0xabcd),('ActorPreviousDrawY',0x1234)):
                put(m,ds,name,value,i*2)
        put(m,ds,'ActorUpdateOrScriptCursor',65535,2*len(slots))
        put(m,ds,'WaterYPixels',100)
        m.ww('GAME:DrawPagePointer',0x4000); m.ww('GAME:PlayfieldHeight',192)
        if not real:
            m.ww('GAME:SpriteDirectoryPointer',0x100)
            m.ww('GAME:SpriteDirectoryPointer',0x9000,2)
            for sprite,_,_ in slots:
                if sprite==0x7fff: continue
                m.write(0x9000,(0x100+4*sprite)&65535,words(0x8000,0x0305))
            for bank in ('SpritePixels0To216Pointer','SpritePixels217To297Pointer',
                         'SpritePixels298To546Pointer','SpritePixels547AndUpPointer'):
                m.ww('GAME:'+bank,0); m.ww('GAME:'+bank,0x9000,2)
            m.write(0x9000,0x7fe0,bytes((i*17)&255 for i in range(64)))
        m.device.planes[:]=bytes([0x35])*(4*65536)
    def check(m,r):
        assert r['SI']==len(slots)*2
        for i,(sprite,x,y) in enumerate(slots):
            if sprite==0x7fff:
                assert get(m,ds,'ActorPixelX',2*i)==1234+i
                assert get(m,ds,'ActorPreviousDrawX',2*i)==0xabcd
            else:
                sx=x if x<32768 else x-65536; sy=y if y<32768 else y-65536
                assert get(m,ds,'ActorPixelX',2*i)==(sx//32)&65535
                assert get(m,ds,'ActorPixelY',2*i)==(sy//32)&65535
                assert get(m,ds,'ActorPreviousDrawX',2*i)==1234+i
                assert get(m,ds,'ActorPreviousDrawY',2*i)==5678+i
    return Case(f'draw {slots} ds={ds:x} reverse={reverse} real={real}','GAME:DrawDemoSprites',
                setup=setup,regs=dict(DS=ds),flags=0x602 if reverse else 0x202,check=check,out_regs=OUT)


CASES += [draw_case([]),draw_case([(0x7fff,0,0)]),
          draw_case([(0,320*32,0)]),draw_case([(0,0,192*32)]),
          draw_case([(0,319*32+31,191*32+31)]),draw_case([(217,65535,65535)]),
          draw_case([(0,0x8000,0x8000)]),draw_case([(0,0x7fff,0x7fff)]),
          draw_case([(0,0,99*32),(217,33,100*32),(298,65,101*32),(547,97,98*32)]),
          draw_case([(0,0,0)],ds=0x7500),draw_case([(0,0,0)],reverse=True),
          draw_case([(214,300*32,100*32),(0x7fff,0,0)],real=True),
          draw_case([(0xffff,0,0)]),draw_case([(0x8000,0,0)]),
          draw_case([(0x7fff if i%3==0 else 0,i*32,i*32) for i in range(16)])]


def control_case(modes=(-1,-1),count=1,thresholds=(1,3,1,3),buttons=(0xff,0xff),
                 values=(),mask=0,scan=0x9e,old=0x1e,ds=DATA_SEG,reverse=False):
    def setup(m):
        for name,value in (('PlayerCount',count),('PlayerOneControlMode',modes[0]),
                           ('PlayerTwoControlMode',modes[1]),('JoystickSampleLoopLimit',10)):
            put(m,ds,name,value)
        m.write(ds,m.off('DGROUP:JoystickEnabledAxisMask'),bytes([mask]))
        for i in (0,2):
            for name,value in zip(('JoystickLeftThresholds','JoystickRightThresholds',
                                   'JoystickUpThresholds','JoystickDownThresholds'),thresholds): put(m,ds,name,value,i)
            for name in ('PlayerUpInput','PlayerDownInput','PlayerLeftInput','PlayerRightInput','PlayerActionInput'):
                put(m,ds,name,0xab80+i,i)
        m.write(ds,m.off('DGROUP:CurrentKeyboardScanCode'),bytes([old]))
        m.wb('GAME:LatestInterruptScanCode',scan)
        m.device.script(0x201,[*buttons,*values])
    def check(m,r):
        assert r['AX']==scan+((scan^old)<<8)
        assert r['BX']==(4 if count==2 else 2)
        for i,mode in enumerate(modes[:2 if count==2 else 1]):
            if ((mode*2)&65535)>=32768:
                for name in ('PlayerUpInput','PlayerDownInput','PlayerLeftInput','PlayerRightInput','PlayerActionInput'):
                    assert get(m,ds,name,i*2)==0xab80+i*2
            else:
                for name in ('PlayerUpInput','PlayerDownInput','PlayerLeftInput','PlayerRightInput','PlayerActionInput'):
                    assert get(m,ds,name,i*2) in (0,65535)
    return Case(f'controls {modes} count={count} thresholds={thresholds} buttons={buttons} '
                f'axis={values} mask={mask} scan={scan:x} old={old:x} ds={ds:x} DF={reverse}',
                'GAME:PollPlayerControls',setup=setup,regs=dict(DS=ds),check=check,out_regs=OUT,
                flags=0x602 if reverse else 0x202)


for modes in ((-1,-1),(-1,1),(0,-1),(1,0),(0,1)):
    for count in (1,2,0,3): CASES.append(control_case(modes,count))
for thresholds in ((10,20,10,20),(9,11,9,11),(0,10,0,10),(-1,0,-1,0),
                   (-32768,32767,-32768,32767),(32767,-32768,32767,-32768)):
    CASES.append(control_case((0,1),2,thresholds,buttons=(0xcf,0x3f)))
CASES += [control_case((0,1),2,mask=15,values=(0xff,0xff,0xfe,0xfc,0xf8,0xf0),buttons=(0xef,0xbf)),
          control_case(ds=0x7500,scan=0xe0,old=0xe0),control_case((0,-1),reverse=True),
          control_case((-32768,-1),scan=0x10),control_case((0x4000,-1)),
          control_case((-1,-1),count=2,scan=0,old=255)]


def move_case(title='',slot=0,ds=DATA_SEG,x=3200,y=2560,hv=0,vv=0,water=200,
              platform=-1,left=0,right=0,up=0,down=0,rain=0,solid=False,
              limits=(3100,2300,1380),difficulty=0,fade=2,timer=1000,
              platforms=(),sparse=(),pixel=None,row=96,page=0x2000,page_seg=0xa000,
              expected=None,reverse=False):
    def setup(m):
        for name,value in (('PlayerX32',x),('PlayerY32',y),('PlayerPixelX',x//32 if pixel is None else pixel[0]),
                           ('PlayerYPixels',y//32 if pixel is None else pixel[1]),('PlayerHorizontalVelocities',hv),
                           ('PlayerVerticalVelocities',vv),('PlayerPlatformIndices',platform),('PlayerLeftInput',left),
                           ('PlayerRightInput',right),('PlayerUpInput',up),('PlayerDownInput',down),
                           ('PlayerImpactMagnitude',0x6789),('PlayerThrustAnimationRate',0x8765)):
            put(m,ds,name,value,slot)
        for name,value in (('WaterYPixels',water),('LevelTimer',timer),('VgaRowStrideBytes',row),
                           ('SelectedDifficulty',difficulty),('ScreenFadeStep',fade),('ScreenFadeLevel',256)):
            put(m,ds,name,value)
        m.write(ds,m.off('DGROUP:LevelRainDirection'),bytes([rain]))
        for i,value in enumerate(limits): put(m,ds,'PlayerImpactLimits',value,2*i)
        for i,(lo,hi,height) in enumerate(platforms):
            for name,value in (('PlatformLeftEdges',lo),('PlatformRightEdges',hi),('PlatformHeights',height)):
                put(m,ds,name,value,i*2)
        put(m,ds,'PlatformLeftEdges',65535,2*len(platforms))
        m.ww('GAME:BackgroundPagePointer',page); m.ww('GAME:BackgroundPagePointer',page_seg,2)
        m.device.planes[:]=bytes([0x80 if solid else 0x17])*(4*65536)
        for plane,offset,value in sparse: m.device.planes[plane*65536+(offset&65535)]=value
    def check(m,r):
        assert r['BX']==slot
        if expected:
            for name,value in expected.items():
                assert get(m,ds,name,slot if name.startswith('Player') else 0)==value&65535, name
    return Case('move '+title+f' slot={slot} ds={ds:x} x/y={x}/{y} v={hv}/{vv} '
                f'water={water} platform={platform} inputs={left}/{right}/{up}/{down} rain={rain} '
                f'solid={solid} limits={limits} difficulty={difficulty} fade={fade} timer={timer} '
                f'platforms={platforms} sparse={sparse} pixel={pixel} stride={row} page={page:x}/{page_seg:x}',
                'GAME:MovePlayerWithVgaCollisions',setup=setup,regs=dict(DS=ds,BX=slot),check=check,out_regs=OUT,
                flags=0x602 if reverse else 0x202)


CASES.append(move_case('gravity known answer',expected={'LevelTimer':997,'PlayerVerticalVelocities':27,
                 'PlayerX32':3200,'PlayerY32':2560,'PlayerImpactMagnitude':0,'PlayerThrustAnimationRate':0}))
for solid in (False,True):
    for hv,vv in ((-4096,0),(4096,0),(0,-4096),(0,4096),(-6144,-6144),(6144,6144),
                  (-32768,-32768),(32767,32767),(0,0),(-1,-1),(63,37),(-63,-90)):
        CASES.append(move_case(hv=hv,vv=vv,solid=solid))
for x,y in ((-512,-608),(-513,-609),(9728,6112),(9729,6113),(-32768,-32768),
             (32767,32767),(3200+31,2560+31)):
    CASES.append(move_case(x=x,y=y,hv=2048,vv=2048))
    CASES.append(move_case(x=x,y=y,hv=-2048,vv=-2048))
for water in (60,98,97,99,200,-32768,32767):
    for platform in (-1,0):
        for vv in (-64,0,64): CASES.append(move_case(water=water,platform=platform,vv=vv,up=1,down=1))
for left,right,up,down in ((1,0,0,0),(0,1,0,0),(1,1,0,0),(0,0,1,0),(0,0,0,1),(1,1,1,1)):
    for water in (60,200): CASES.append(move_case(left=left,right=right,up=up,down=down,water=water))
for rain in (0,1,2,3,255):
    for water in (60,200): CASES.append(move_case(rain=rain,water=water))
for limits in ((0,0,0),(2048,2048,2048),(2049,2049,2049),(65535,65535,65535)):
    for fade in (-4,0,2): CASES.append(move_case(hv=4096,vv=4096,solid=True,limits=limits,fade=fade))
for difficulty in (0,1,2): CASES.append(move_case(hv=3100,vv=1380,solid=True,difficulty=difficulty))
for platforms in ((),((0,319,100),),((0,319,99),(117,120,100),(0,115,100),(116,116,100)),
                  ((0,319,99),(117,120,100),(0,115,100))):
    CASES.append(move_case(vv=2048,solid=True,platforms=platforms))
CASES += [move_case(slot=2,left=1,down=1,solid=True,hv=-2048,vv=-2048),
          move_case(ds=0x7500,solid=True,hv=2048,vv=2048),move_case(timer=0),
          move_case(page=0xfff0,row=-96,x=-500,y=-600,hv=-4096,vv=-4096),
          move_case(page_seg=0x9fff,page=0x10,hv=2048,vv=2048,solid=True),
          move_case(water=97,vv=-4096),move_case(water=97,vv=-2048),
          move_case(pixel=(-3,-5),x=3201,y=2561,hv=0,vv=0,row=-96)]
# Only a later, different sample address is solid. These discriminate the
# original stationary left/up probes from the advancing right/down probes.
CASES += [
    move_case('left reuses address',hv=-6144,sparse=((0,0x3e19,0x80),),
              expected={'PlayerImpactMagnitude':0,'PlayerX32':3104}),
    move_case('up reuses address',vv=-6144,sparse=((1,0x3d5a,0x80),),
              expected={'PlayerImpactMagnitude':0,'PlayerY32':2464}),
    move_case('right advances plane and byte',x=3231,hv=6144,sparse=((0,0x3e1b,0x80),),
              expected={'PlayerImpactMagnitude':6144,'PlayerX32':3264,'PlayerHorizontalVelocities':-3072}),
    move_case('down advances row',vv=6144,sparse=((1,0x3eda,0x80),),
              expected={'PlayerImpactMagnitude':6144,'PlayerY32':2592,'PlayerVerticalVelocities':-3072}),
    move_case('horizontal negative thrust wraps',hv=-32768,left=1),
    move_case('horizontal positive thrust wraps',hv=32767,right=1),
    move_case('vertical negative thrust wraps',vv=-32768,up=1,water=98),
    move_case('vertical positive gravity wraps',vv=32767,water=200),
    move_case('DF survives collisions',hv=-4096,vv=4096,solid=True,reverse=True),
]
# Fixed-seed state variation: valid platform sentinels, finite loop sizes.
seed=random.Random(0xf15ce)
for i in range(24):
    CASES.append(move_case('seeded '+str(i),slot=seed.choice((0,2)),x=seed.randrange(-600,9800),
                  y=seed.randrange(-650,6200),hv=seed.randrange(-8000,8000),vv=seed.randrange(-8000,8000),
                  water=seed.randrange(0,200),platform=seed.choice((-1,0)),left=seed.randrange(2),
                  right=seed.randrange(2),up=seed.randrange(2),down=seed.randrange(2),rain=seed.randrange(4),
                  solid=bool(seed.randrange(2)),difficulty=seed.randrange(3),fade=seed.choice((-2,0,2))))

# Finite button input terminates each actual built demo after its normal fade.
# Neither script callbacks nor render/sound callees are replaced.
from difftest import load_suite
for n in ('PlaySpriteRevealDemo','PlayPreGameDemo','PlayAttractDemo','PlayGameCompletionDemo'):
    setup=load_suite('menu').composition_fixture
    CASES.append(Case(n+' real tables button exit','GAME:'+n,setup=setup,
                      regs=dict(DS=DATA_SEG),out_regs=GENERAL+('CF','PF','ZF','SF','OF','IF','DF'),budget=30000000))
for old in (0xffff,0x7fff,0,214):
    def setup(m,old=old):
        m.ww('DGROUP:ActorUpdateOrScriptCursor',0)
        m.ww('DGROUP:ActorUpdateOrScriptCursor',0xffff,2)
        m.ww('DGROUP:ActorEraseSprite',old)
        m.ww('DGROUP:ActorSpriteIds',215)
        m.ww('DGROUP:ActorPreviousDrawX',16);m.ww('DGROUP:ActorPreviousDrawY',24)
    CASES.append(Case(f'erase sprite {old:x}','GAME:EraseDemoSprites',setup=setup,
                      regs=dict(DS=DATA_SEG),out_regs=OUT,flags=0x602,budget=10000000))
for resource in ('B2D9A:ext_2D9A','B2BF6:ext_2BF6'):
    def setup(m):load_suite('menu').composition_fixture(m)
    CASES.append(Case(resource+' full picture','GAME:ShowPackedPictureAndWait',setup=setup,
                      regs=lambda m,resource=resource:dict(DS=DATA_SEG,SI=m.seg(resource),CX=1),
                      out_regs=GENERAL+('CF','PF','ZF','SF','OF','IF','DF'),budget=15000000))
# Direct script loop with an empty vector still renders and fades normally.
def empty_demo(m):
    load_suite('menu').composition_fixture(m)
    m.write(DATA_SEG,0x6000,words(0xffff))
CASES.append(Case('empty script completed fade','GAME:RunScriptedDemo',setup=empty_demo,
                  regs=dict(DS=DATA_SEG,SI=0x6000),out_regs=GENERAL+('CF','PF','ZF','SF','OF','IF','DF'),budget=10000000))

CASES.append(Case('credits complete first page button','GAME:ShowCreditsPages',
                  setup=load_suite('menu').composition_fixture,regs=dict(DS=DATA_SEG),
                  out_regs=GENERAL+('CF','PF','ZF','SF','OF','IF','DF'),budget=20000000))

def game_escape(m):
    load_suite('menu').composition_fixture(m)
    m.wb('GAME:LatestInterruptScanCode',1)
    m.ww('DGROUP:WaterSurfaceByteOffset',18000)
CASES.append(Case('full gameplay Escape through actual level','GAME:RunGameFromPassword',setup=game_escape,
                  regs=dict(DS=DATA_SEG),out_regs=('SI','DI','BP','IF','DF'),budget=60000000))

def startup_quit(m):
    load_suite('menu').composition_fixture(m)
    s,o=m.address('GAME:HandleKeyboardScanInterrupt')
    m.write(0,0x24,o.to_bytes(2,'little')+s.to_bytes(2,'little'))
    m.device.script(0x60,[0x10]);m.device.schedule(m.seg('GAME:loc_449B'),m.off('GAME:loc_449B'),irq=1)
CASES.append(Case('startup pictures Q and actual shutdown','GAME:ShowStartupPictures',setup=startup_quit,
                  regs=dict(DS=DATA_SEG),kind='exit',out_regs=('IF','DF'),budget=20000000))
