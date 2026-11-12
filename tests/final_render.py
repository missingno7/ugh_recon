"""Final rendering package: real resources, branch/width edges and full-state equality.

No fixture executes the oracle. Static rebuilt tables are allowed as inputs;
independent checks below assert random placement, cursor movement and priority.
"""
from difftest import Case
from emu import DATA_SEG
from dataprobe import ice_pack235

GENERAL=('AX','BX','CX','DX','SI','DI','BP')
FLAGS=('CF','PF','ZF','SF','OF','IF','DF') # AF undefined after logical operations
OUT=GENERAL+FLAGS
FULL=OUT+('AF',)
CASES=[]


def scene(m,real=False):
    m.ww('GAME:DrawPagePointer',0x4000)
    m.ww('GAME:BackgroundPagePointer',0)
    m.ww('GAME:FixedVgaPagePointer',0x9000)
    m.ww('GAME:PlayfieldHeight',192)
    m.ww('DGROUP:WaterYPixels',100)
    for p in range(4):
        m.device.planes[p*65536:(p+1)*65536]=bytes((i*17+p*37)&255 for i in range(256))*256
    if not real:
        m.ww('GAME:SpriteDirectoryPointer',0)
        m.ww('GAME:SpriteDirectoryPointer',0x7500,2)
        m.write(0x7500,0,bytes((0,0,3,2))*1024)
        for bank in ('SpritePixels0To216Pointer','SpritePixels217To297Pointer',
                     'SpritePixels298To546Pointer','SpritePixels547AndUpPointer'):
            m.ww('GAME:'+bank,0)
            m.ww('GAME:'+bank,0x7700,2)
        m.write(0x7700,0,bytes((5,0,7,8,9,10)))


def seed_random(m,seed):
    for i,v in enumerate(seed): m.ww('GAME:RandomStateWord'+str(i),v)


def next_random(seed,bound):
    a,b,c,d=seed
    t=a+bound; a=t&65535; carry=t>>16
    t=b+a+carry; b=t&65535; carry=t>>16
    t=c+b+carry; c=t&65535; carry=t>>16
    t=d+c+carry; d=t&65535; carry=t>>16
    a=(a+d+carry)&65535
    return (a,b,c,d),(a*bound)>>16


def respawn(water,direction,seed,index=0,stride=96,alternate=False):
    ds=0x7600 if alternate else DATA_SEG
    expected={}
    def setup(m):
        for label,v,size in (('WaterYPixels',water,2),('LevelRainDirection',direction,1),('VgaRowStrideBytes',stride,2)):
            m.write(ds,m.off('DGROUP:'+label),(v&((1<<(size*8))-1)).to_bytes(size,'little'))
        seed_random(m,seed)
        state,v=next_random(seed,(water+320)&65535)
        x,y=(v,0) if v<320 else (319 if direction==1 else 0,v-320)
        expected.update(state=state,offset=((y&255)*(stride&255)+(x>>2))&65535,phase=x&3)
    def check(m,r):
        def word(label): return int.from_bytes(m.read(ds,(m.off('DGROUP:'+label)+index)&65535,2),'little')
        assert word('RainParticleOffsets')==expected['offset']
        assert word('RainParticleXModuloFour')==expected['phase']
        assert tuple(m.rw('GAME:RandomStateWord'+str(i)) for i in range(4))==expected['state']
    return Case(f'respawn water={water} dir={direction} seed={seed} index={index:04x} stride={stride} alt={alternate}',
                'GAME:RespawnRainParticle',setup=setup,check=check,regs=dict(DS=ds,BX=index),out_regs=OUT,flags=0x602)


for water in (0,1,191,300,0xffff,0xfec0):
    for direction in (0,1,2,255):
        for seed in ((0,0,0,0),(0xffff,0xeeee,0xdddd,0xcccc)):
            CASES.append(respawn(water,direction,seed))
CASES += [respawn(300,1,(1234,5678,9012,3456),index=0xffff,stride=0x123,alternate=True),
          respawn(65535,2,(65535,65535,65535,65535),index=2,stride=0),
          respawn(300,1,(0,0,0,60000),stride=255),respawn(300,2,(0,0,0,60000))]


def advance(water,direction,limit,phases=(0,1,2,3),alternate=False):
    ds=0x7600 if alternate else DATA_SEG
    def setup(m):
        m.write(ds,m.off('DGROUP:WaterYPixels'),(water&65535).to_bytes(2,'little'))
        m.write(ds,m.off('DGROUP:WaterSurfaceByteOffset'),limit.to_bytes(2,'little'))
        m.write(ds,m.off('DGROUP:LevelRainDirection'),bytes((direction,)))
        m.write(ds,m.off('DGROUP:VgaRowStrideBytes'),b'\x60\x00')
        seed_random(m,(0xffff,0xabcd,0x1234,0x9876))
        index=((water+1)*2)&65535; n=0
        while True:
            for label,v in (('RainParticleOffsets',((n*100)+limit-400)&65535),
                            ('RainPreviousOffsets',0xabcd),('RainParticleXModuloFour',phases[n%len(phases)])):
                m.write(ds,(m.off('DGROUP:'+label)+index)&65535,v.to_bytes(2,'little'))
            index=(index-2)&65535; n+=1
            if index&0x8000: break
    return Case(f'advance water={water:04x} dir={direction} limit={limit} phases={phases} alt={alternate}',
                'GAME:AdvanceRainParticles',setup=setup,regs=dict(DS=ds),out_regs=FULL,flags=0x602)


for direction in (0,1,2,3,255):
    for limit in (0,1000,65535): CASES.append(advance(3,direction,limit))
CASES += [advance(0xffff,1,0),advance(0x4000,2,65535),advance(191,2,1000),
          advance(4,1,65535,(0x100,0x103,0xff,0x8000)),advance(2,2,1000,alternate=True)]


for count in (0,1,2,3):
    for real in (False,True):
        def setup(m,count=count,real=real): scene(m,real); m.ww('DGROUP:PlayerCount',count)
        CASES.append(Case(f'HUD borders players={count} real={real}','GAME:DrawHudBorders',
                          setup=setup,regs=dict(DS=DATA_SEG),out_regs=FULL))


for advance_cursor in (False,True):
    for digit,x,y in ((0,0,194),(9,319,194),(255,0xfffd,192),(10,0x7fff,191)):
        for real in (False,True):
            def setup(m,x=x,y=y,real=real):
                scene(m,real); m.ww('DGROUP:HudDigitCursorX',x); m.ww('DGROUP:HudDigitCursorY',y)
            def check(m,r,x=x,advance_cursor=advance_cursor):
                assert m.rw('DGROUP:HudDigitCursorX')==(x+(6 if advance_cursor else 0))&65535
            CASES.append(Case(f'HUD digit {digit} x={x} y={y} advance={advance_cursor} real={real}',
                'GAME:DrawHudDigitAndAdvance' if advance_cursor else 'GAME:DrawHudDigit',setup=setup,check=check,
                regs=dict(DS=DATA_SEG,AX=0xa500|digit),out_regs=FULL))


for digits,values in ((2,((0,0),(0,99),(99,0),(255,254),(12,13))),
                      (4,((0,0),(9999,0),(0,9999),(65535,12345),(1090,1091))),
                      (6,((0,0),(999999,0),(0,999999),(100000,99999),(123450,123451)))):
    for current,previous in values:
        for real in (False,True):
            def setup(m,real=real):
                scene(m,real); m.ww('DGROUP:HudDigitCursorX',0xfff9); m.ww('DGROUP:HudDigitCursorY',194)
            def check(m,r,digits=digits,current=current,previous=previous):
                assert m.rw('DGROUP:HudDigitCursorX')==(0xfff9+digits*6)&65535
                for j,n in enumerate((current,previous)):
                    expected=bytes(int(c) for c in f'{n:0{digits}d}')+b'\xff'
                    if n<10**digits:
                        assert m.read(DATA_SEG,m.off('DGROUP:DecimalDigitBuffer')+7*j,digits+1)==expected
            name={2:'Two',4:'Four',6:'Six'}[digits]
            CASES.append(Case(f'{digits} changed digits {current}/{previous} real={real}',
                f'GAME:RedrawChanged{name}DigitNumber',setup=setup,check=check,
                regs=dict(DS=DATA_SEG,AX=current&65535,DX=current>>16,BX=previous&65535,CX=previous>>16),out_regs=FULL))


def player_case(restore,index,x,y,rate=0,countdown=10,sprite=218,end=221,real=False):
    expected={}
    def setup(m):
        scene(m,real)
        for label,value in (('PlayerThrustAnimationRate',rate),('PlayerAnimationCountdowns',countdown),
                            ('PlayerSpriteIds',sprite),('PlayerAnimationCycleStarts',218),('PlayerAnimationCycleEnds',end),
                            ('PlayerPixelX',x),('PlayerYPixels',y),('PlayerCachedSpriteIds',sprite),
                            ('PlayerCachedPixelX',x),('PlayerCachedPixelY',y)):
            m.ww('DGROUP:'+label,value,index)
        c=(countdown-min(rate,90))&65535
        advanced=c>=32768
        expected.update(count=(c+200 if advanced else c)&65535,
                        sprite=(218 if ((sprite+1)&65535)>=end else (sprite+1)&65535) if advanced else sprite)
    def check(m,r):
        if restore:
            assert m.rw('DGROUP:PlayerCachedSpriteIds',index)==sprite
            assert m.rw('DGROUP:PlayerCachedPixelX',index)==x&65535
            assert m.rw('DGROUP:PlayerCachedPixelY',index)==y&65535
        else:
            assert m.rw('DGROUP:PlayerAnimationCountdowns',index)==expected['count']
            assert m.rw('DGROUP:PlayerSpriteIds',index)==expected['sprite']
    return Case(f'player restore={restore} i={index} xy={x},{y} rate={rate} count={countdown} id={sprite} end={end} real={real}',
                'GAME:RestorePlayerBackground' if restore else 'GAME:AnimateAndDrawPlayer',
                setup=setup,check=check,regs=dict(DS=DATA_SEG,BX=index),out_regs=OUT if restore else FULL,flags=0x602 if restore else 0x202)


for restore in (False,True):
    for index in (0,2):
        for x,y in ((-32,0),(-31,0),(319,0),(320,0),(0,-20),(0,-19),(0,191),(0,192)):
            CASES.append(player_case(restore,index,x,y))
    CASES.append(player_case(restore,2,5,10,real=True))
for rate,count,sprite,end in ((90,90,219,221),(91,89,219,221),(200,-500,220,221),
                              (-1,0,218,221),(-32768,0,218,221),(0,-1,220,221),
                              (0,-1,0x7fff,0x7fff)):
    # Last case's sprite wraps to signed negative, so no cycle wrap.
    c=player_case(False,0,0,0,rate,count,sprite,end)
    if sprite==0x7fff: c.check=None
    CASES.append(c)


for real in (False,True):
    for x,y,sprite in ((0,0,0),(3,10,218),(-1,-1,224),(319,191,0),(0x8000,0,0)):
        def setup(m,real=real):
            scene(m,real)
            # Nonzero pointer offset is deliberately discarded by this routine.
            if not real: m.ww('GAME:SpriteDirectoryPointer',0x1234)
        CASES.append(Case(f'restore sprite {sprite} x={x} y={y} real={real}',
            'GAME:RestoreSpriteBackground',setup=setup,regs=dict(DS=DATA_SEG,AX=x&65535,BX=y&65535,CX=sprite),
            out_regs=OUT,flags=0x602))
for height in (1,192,0):
    def setup(m,height=height): scene(m); m.ww('GAME:PlayfieldHeight',height)
    CASES.append(Case(f'restore playfield height={height}','GAME:RestorePlayfieldBackground',setup=setup,
                     regs=dict(DS=DATA_SEG),out_regs=OUT,flags=0x602,budget=40_000_000))


for real in (False,True):
    for tile,col,row in ((0,0,0),(255,19,15),(218,255,255)):
        def setup(m,real=real): scene(m,real)
        CASES.append(Case(f'map tile {tile} {col}/{row} real={real}','GAME:DrawMapTile',
            setup=setup,regs=dict(DS=DATA_SEG,AX=0xa500|tile,DX=(row<<8)|col),out_regs=FULL))
for real in (False,True):
    for reverse in (False,True):
        def setup(m,real=real,reverse=reverse):
            scene(m,real); m.ww('DGROUP:CurrentTileMapPointer',0xff80 if reverse else 0xfff0)
            m.ww('DGROUP:CurrentTileMapPointer',0x7600,2)
            start=0xff80 if reverse else 0xfff0
            for i in range(320): m.write(0x7600,(start+(-i if reverse else i))&65535,bytes((i%16,)))
            # DrawTileMap passes map DS on to sprite water lookup.
            m.write(0x7600,m.off('DGROUP:WaterYPixels'),b'\x64\x00')
        CASES.append(Case(f'tile map real={real} DF={reverse}','GAME:DrawTileMap',setup=setup,
            regs=dict(DS=DATA_SEG),flags=0x602 if reverse else 0x202,out_regs=FULL))


def hud_case(path,timer=7000,cached_width=10,fade=2,real=False):
    def setup(m):
        scene(m,real)
        vals={'PlayerCount':1,'ScoreLowWord':1234,'ScoreHighWord':0,'HudCachedScoreLow':1234,'HudCachedScoreHigh':0,
              'PlayerCarriedKinds':0,'HudCachedPlayerOneIconState':0,'PlayerTwoPassengerIconState':0,
              'HudCachedPlayerTwoIconState':0,'HudCachedFare':0,'LevelTimer':timer,'CachedTimerBarWidth':cached_width,
              'ScreenFadeStep':fade,'ScreenFadeLevel':10,'TimerBarDivisor':700,
              'HudLivesX':33,'HudScoreX':114,'HudLevelCounterX':169,'HudFareX':232,'HudMultiplierX':305,
              'HudPlayerOneIconX':215,'HudPlayerOneDestinationX':199,'HudPlayerTwoIconX':258,'HudPlayerTwoDestinationX':274,
              'PlayerDestinationIcons':1,'PlayerTwoDestinationIconIndex':2,'PlayerPassengerFares':1234,'PlayerTwoFare':4321}
        bs={'LivesRemaining':3,'HudCachedLives':3,'RemainingPassengerJourneys':7,'HudCachedLevelCounter':7,
            'ScoreMultiplier':2,'HudCachedMultiplier':2,'HudFareClearPending':0}
        for label,v in vals.items(): m.ww('DGROUP:'+label,v)
        for label,v in bs.items(): m.wb('DGROUP:'+label,v)
        m.ww('DGROUP:TimerBarPointer',0xfffa); m.ww('DGROUP:TimerBarPointer',0xa000,2)
        if path=='lives': m.wb('DGROUP:LivesRemaining',99)
        if path in ('score-low','score-priority'): m.ww('DGROUP:ScoreLowWord',1235)
        if path=='score-high': m.ww('DGROUP:ScoreHighWord',1)
        if path=='score-cap': m.ww('DGROUP:ScoreHighWord',16)
        if path=='score-cap-low': m.ww('DGROUP:ScoreHighWord',15); m.ww('DGROUP:ScoreLowWord',0x4240)
        if path=='score-max':
            m.ww('DGROUP:ScoreHighWord',15); m.ww('DGROUP:ScoreLowWord',0x423f)
            m.ww('DGROUP:HudCachedScoreHigh',15); m.ww('DGROUP:HudCachedScoreLow',0x423f)
        if path=='journeys': m.wb('DGROUP:RemainingPassengerJourneys',0)
        if path in ('icon-one','icon-one-priority','fare-one','fare-one-same'):
            m.ww('DGROUP:PlayerCarriedKinds',2)
            if path not in ('icon-one','icon-one-priority'): m.ww('DGROUP:HudCachedPlayerOneIconState',2)
            if path=='fare-one-same': m.ww('DGROUP:HudCachedFare',1234)
        if path in ('icon-two','fare-two','two-empty'):
            m.ww('DGROUP:PlayerCount',2)
            if path!='two-empty': m.ww('DGROUP:PlayerTwoPassengerIconState',3)
            if path=='fare-two': m.ww('DGROUP:HudCachedPlayerTwoIconState',3)
        if path=='fare-clear': m.wb('DGROUP:HudFareClearPending',255); m.ww('DGROUP:HudCachedFare',9999)
        if path=='fare-clear-same': m.wb('DGROUP:HudFareClearPending',255)
        if path=='multiplier': m.wb('DGROUP:ScoreMultiplier',99)
        if path.endswith('-priority'):
            m.ww('DGROUP:PlayerCount',2); m.ww('DGROUP:PlayerTwoPassengerIconState',3)
            m.ww('DGROUP:PlayerCarriedKinds',2); m.ww('DGROUP:HudCachedFare',9999)
            m.wb('DGROUP:ScoreMultiplier',99); m.wb('DGROUP:RemainingPassengerJourneys',8)
    def check(m,r):
        assert m.rw('DGROUP:HudDigitCursorY')==194
        if timer&0x8000:
            assert m.rw('DGROUP:LevelTimer')==65535
            assert m.rw('DGROUP:ScreenFadeStep')==(fade if fade&0x8000 else 65534)
        else: assert m.rw('DGROUP:CachedTimerBarWidth')==timer//700
        if path.startswith('score-cap'):
            assert (m.rw('DGROUP:ScoreHighWord')<<16)|m.rw('DGROUP:ScoreLowWord')==999999
        if path.startswith('fare-'): assert m.rb('DGROUP:HudFareClearPending')==0
        if path.endswith('-priority'):
            assert m.rw('DGROUP:HudCachedFare')==9999
            assert m.rb('DGROUP:HudCachedMultiplier')==2
            assert m.rw('DGROUP:HudCachedPlayerTwoIconState')==0
            assert m.rb('DGROUP:HudCachedLevelCounter')==(7 if path=='score-priority' else 8)
    return Case(f'HUD refresh {path} timer={timer} cached={cached_width} fade={fade} real={real}',
                'GAME:RefreshHudAndTimerBar',setup=setup,check=check,regs=dict(DS=DATA_SEG),out_regs=OUT)


for path in ('unchanged','lives','score-low','score-high','score-cap','score-cap-low','score-max','journeys',
             'icon-one','icon-two','fare-one','fare-one-same','fare-two','two-empty','fare-clear','fare-clear-same','multiplier',
             'score-priority','icon-one-priority'):
    CASES.append(hud_case(path))
    CASES.append(hud_case(path,real=True))
for timer,width,fade in ((0,1,2),(700,0,2),(2800,0,2),(2801,4,2),(6300,1,2),(7000,9,2),(7000,11,2),
                         (32767,0,2),(65535,10,2),(32768,10,0),(65535,10,65535),(65535,10,32768),
                         (7000,65535,2),(0,65535,2)):
    CASES.append(hud_case('unchanged',timer,width,fade))


for players in (1,2):
    for level in (0,30,68):
        def setup(m,players=players,level=level):
            m.ww('DGROUP:PlayerCount',players); m.ww('DGROUP:CurrentLevelIndex',level)
            m.ww('DGROUP:WaterSurfaceByteOffset',18000)
        def check(m,r):
            assert r['ES']==DATA_SEG and not r['FLAGS']&0x400
            assert m.rw('DGROUP:PlayerSpriteIds')==218 and m.rw('DGROUP:PlayerTwoSpriteId')==224
        CASES.append(Case(f'load real level={level} players={players}','GAME:LoadCurrentLevelState',
            setup=setup,check=check,regs=dict(DS=DATA_SEG),flags=0x602,out_regs=FULL,budget=15_000_000))


def synthetic_level(water,mode=0,empty=False,overlap=False):
    expected={}
    def setup(m):
        m.ww('DGROUP:PlayerCount',1); m.ww('DGROUP:CurrentLevelIndex',0)
        # A short independently packed stream isolates record/list coverage;
        # real levels above retain the rebuilt compressed tile-map bank.
        m.write(0x7800,0,ice_pack235(bytes((i*7)&255 for i in range(320))))
        m.ww('DGROUP:CompressedTileMapsPointer',0); m.ww('DGROUP:CompressedTileMapsPointer',0x7800,2)
        m.ww('DGROUP:LevelOrderTables',0x7000)
        # Destination above source: original reverse word copying retains all
        # inputs, unlike the destructive opposite overlap direction.
        record=m.off('DGROUP:CurrentLevelRecord')-2 if overlap else 0x7040
        m.write(DATA_SEG,0x7000,record.to_bytes(2,'little'))
        words=(0,0x7100,0x7200,0x7300,7,0)
        data=b''.join(v.to_bytes(2,'little') for v in words)+bytes((mode,))
        data+=b''.join((v&65535).to_bytes(2,'little') for v in (0,0xfffd,0xffff,0x7fff,water,0xffff))+b'\x55'
        assert len(data)==26
        m.write(DATA_SEG,record,data)
        def put(off,values): m.write(DATA_SEG,off,b''.join((v&65535).to_bytes(2,'little') for v in values))
        if empty:
            put(0x7100,(0x8000,)); put(0x7200,(0xffff,)); put(0x7300,(0xffff,))
        else:
            put(0x7100,(0,319,0xfffd,22,33,44,1,0xeeee, 10,300,0x7fff,77,88,99,2,0xdddd, 0x8000))
            special=m.off('DGROUP:Data_78DC')
            put(0x7200,(0x7400,0,0x1234,special,1,0x4321,0xffff))
            m.write(DATA_SEG,0x7408,b'\xef\xbe')
            tree=m.off('DGROUP:Data_76E4'); bird=m.off('DGROUP:Data_7630'); flyer=m.off('DGROUP:Data_76A8')
            put(0x7300,(tree,0,0xaaaa,bird,0xeeee,0xfffd,0x8001,flyer,0xffff,0xfffd,0xcccc,0xbbbb,
                        0x7400,1,0xeeee,0xfffd,0xffff))
        # Seed stale outputs; fields not explicitly reset must remain stale.
        for label in ('ActorX32','ActorY32','EnemyInitialDelays','EnemyHorizontalSpeeds',
                      'RainParticleXModuloFour','EnemyAnimationOrDropLists'):
            m.write(DATA_SEG,m.off('DGROUP:'+label),b'\xa5\x5a'*8)
        m.ww('DGROUP:WaterSurfaceByteOffset',0x3000)
        signed=water if water<32768 else water-65536
        expected['water']=min((water-signed//4)&65535,0x17e0)
        expected['copied']=data
    def check(m,r):
        assert m.rw('DGROUP:WaterY32')==expected['water']
        assert m.rw('DGROUP:WaterYPixels')==expected['water']//32
        assert m.rw('DGROUP:PlayerX32')==0xfe00
        assert m.rw('DGROUP:PlayerY32')==(-3-(-3//4)-320)&65535
        assert m.read(DATA_SEG,m.off('DGROUP:Data_264C'),320)==bytes((i*7)&255 for i in range(320))
        if not empty:
            assert m.rw('DGROUP:ActorUpdateOrScriptCursor')==0xbeef
            assert m.rw('DGROUP:ActorX32')==0x5aa5 # generic actor coordinate deliberately stale
            assert m.rw('DGROUP:ActorX32',2)==(99-8)*32
            assert m.rw('DGROUP:EnemyInitialDelays',2)==(-3+(-3//2))&65535
            assert m.rw('DGROUP:EnemyHorizontalSpeeds',6)==0x0002 # -(-3 - floor(-3/4))
    return Case(f'load synthetic water={water:04x} rain={mode} empty={empty} overlap={overlap}',
        'GAME:LoadCurrentLevelState',setup=setup,check=check,regs=dict(DS=DATA_SEG),flags=0x602,
        out_regs=FULL,budget=15_000_000)


CASES += [synthetic_level(v) for v in (0,1,0x1fd5,0x1fd6,0x1fd7,0x7fff,0x8000,0xfffd,0xffff)]
CASES += [synthetic_level(0,empty=True),synthetic_level(0,mode=1),synthetic_level(0,mode=2),
          synthetic_level(0,overlap=True)]
