"""Real descriptor/sequence cases for final actor/item callbacks.

No substituted callbacks, no oracle-produced setup. Sound-reaching boundaries
are explicitly excluded from acceptance and listed in the worker report.
"""
from difftest import Case
from emu import DATA_SEG
import random

CASES=[]
GENERAL=('AX','BX','CX','DX','SI','DI','BP')
# Multi-bit SHL/SAR leave OF undefined. AF is undefined after logic/shifts.
OUTPUT=GENERAL+('CF','PF','ZF','SF','IF','DF')
DEFINED=OUTPUT+('OF',)
ACTOR=6
ENEMY=4
ITEM=10
JOURNEY=0x6200


def word(m,off,value,bank=DATA_SEG):
    m.write(bank,off,(value&65535).to_bytes(2,'little'))


def fixture(m,actor='Data_7720',enemy='Data_766C'):
    # Deliberately stale neighboring arrays detect unintended writes and clears.
    for n in ('ActorDescriptors','ActorUpdateOrScriptCursor','ActorSpriteIds',
              'ActorAnimationByteOffsets','ActorAnimationCountdowns','ActorX32',
              'ActorY32','ActorPixelX','ActorPixelY','ActorOverlayOrScriptCallbacks',
              'ActorSourcePlatformByteIndices','ActorDestinationPlatformByteIndices',
              'ActorDestinationPlatforms','ActorPlatformOrScriptDone','ActorJourneyCursors',
              'ds_2ACD','ds_2A2D','ds_2C6D','PassengerQuickDeliveryCountdowns',
              'EnemyDescriptors','EnemyStateCallbacks','EnemyAnimationByteOffsets',
              'EnemyAnimationCountdowns','EnemySpriteIds','EnemyX32','EnemyY32',
              'EnemyHorizontalSpeeds','EnemyStateCounters','EnemyDirectionOrTargetPlayer',
              'EnemyPlatformIndices','EnemyAnimationOrDropLists','FallingItemDescriptors',
              'FallingItemSprites','FallingItemCallbacks','FallingItemX','FallingItemY',
              'FallingItemMotionOrLifetime','FallingItemVerticalStep'):
        for i in range(0,24,2): m.ww('DGROUP:'+n,0xa131+i*33,i)
    m.ww('DGROUP:ActorDescriptors',0xffff)
    m.ww('DGROUP:ActorDescriptors',m.off('DGROUP:'+actor),ACTOR)
    m.ww('DGROUP:ActorDescriptors',0xffff,ACTOR+2)
    m.ww('DGROUP:EnemyDescriptors',m.off('DGROUP:'+enemy),ENEMY)
    m.ww('DGROUP:EnemyDescriptors',0xffff,ENEMY+2)
    for n,v in (('ActorAnimationByteOffsets',0),('ActorAnimationCountdowns',2),
                ('ActorX32',3200),('ActorY32',1280),('ActorPixelX',100),('ActorPixelY',40),
                ('ActorSourcePlatformByteIndices',2),('ActorDestinationPlatformByteIndices',4),
                ('ActorDestinationPlatforms',3),('ActorPlatformOrScriptDone',3),('ds_2A2D',2),
                ('ds_2ACD',2),('ds_2C6D',0),('PassengerQuickDeliveryCountdowns',0),
                ('ActorJourneyCursors',JOURNEY)):
        m.ww('DGROUP:'+n,v,ACTOR)
    for n,v in (('EnemyAnimationByteOffsets',0),('EnemyAnimationCountdowns',2),
                ('EnemyX32',3200),('EnemyY32',2560),('EnemyHorizontalSpeeds',32),
                ('EnemyStateCounters',2),('EnemyDirectionOrTargetPlayer',0),
                ('EnemyPlatformIndices',3)):
        m.ww('DGROUP:'+n,v,ENEMY)
    m.ww('DGROUP:EnemyAnimationOrDropLists',m.rw('DGROUP:'+enemy,0x22),ENEMY)
    for n,v in (('FallingItemDescriptors',m.off('DGROUP:FallingDescriptor_7A38')),
                ('FallingItemSprites',297),('FallingItemX',3200),('FallingItemY',2560),
                ('FallingItemMotionOrLifetime',5)):
        m.ww('DGROUP:'+n,v,ITEM)
    for i in (0,2):
        for n,v in (('PlayerX32',3200),('PlayerY32',0x6000),('PlayerYPixels',40),
                    ('PlayerPixelX',100),('PlayerCarriedKinds',0),('PlayerPassengerFares',500),
                    ('PlayerMinimumFares',200),('PlayerPlatformIndices',0xffff),
                    ('PlayerDestinationIcons',0xcdef),('PlayerHorizontalVelocities',0x7ff0),
                    ('PlayerVerticalVelocities',0x8000)):
            m.ww('DGROUP:'+n,v,i)
    for i in (0,2,4,6):
        for n,v in (('PlatformActorOccupants',ACTOR),('PlatformHeights',100),
                    ('PlatformArrivalPointsX',120),('PlatformWaitingPointsX',110),
                    ('PlatformLeftEdges',0),('PlatformRightEdges',200),
                    ('PlatformDestinationIcons',i+10)):
            m.ww('DGROUP:'+n,v,i)
    m.ww('DGROUP:PlatformLeftEdges',0xffff,8)
    m.ww('DGROUP:WaterYPixels',100)
    m.ww('DGROUP:WaterY32',3200)
    m.ww('DGROUP:PlayerCount',2)
    m.ww('DGROUP:PlayerArrayBytes',4)
    m.ww('DGROUP:ScoreLowWord',0xfffe)
    m.ww('DGROUP:ScoreHighWord',0xffff)
    m.ww('DGROUP:ScoreMultiplier',2)
    m.ww('DGROUP:SelectedDifficulty',0)
    m.ww('DGROUP:ScreenFadeStep',0)
    m.ww('DGROUP:ScreenFadeLevel',1)
    for i,v in enumerate((2,21,3)): word(m,JOURNEY+2*i,v)


def case(name,title,updates=(),*,actor='Data_7720',enemy='Data_766C',
         slot=ACTOR,setup=None,regs=None,check=None,outputs=OUTPUT,df=False):
    def init(m):
        fixture(m,actor,enemy)
        for n,v,i in updates: m.ww('DGROUP:'+n,v,i)
        if setup: setup(m)
    def inputs(m):
        result=dict(DS=DATA_SEG,BX=slot)
        if name in ('BoardWaterbornePassenger','DeliverPassenger'): result['DI']=2
        if regs: result.update(regs(m) if callable(regs) else regs)
        return result
    CASES.append(Case(title,'GAME:'+name,setup=init,regs=inputs,out_regs=outputs,
                      flags=0x602 if df else 0x202,check=check))


# Read real-shaped journey words with zero/sign/max inputs; retirement uses
# the actual descriptor +2C (IgnoreActorState), not a patched handler.
for source,dest,delay in ((2,3,21),(0,0,0),(0x8000,0x7fff,0xffff),
                          (0xffff,0xfffe,0x8000),(0x7fff,0x8000,0x7fff)):
    def setup(m,s=source,d=dest,t=delay):
        for i,v in enumerate((s,t,d)): word(m,JOURNEY+2*i,v)
    case('ReadPassengerJourneyLeg',f'journey source={source:x} dest={dest:x} delay={delay:x}',
         setup=setup,outputs=DEFINED)
for remaining in (0,1,2,0x7f,0x80,0x81,0xff):
    def setup(m,v=remaining):
        word(m,JOURNEY+4,0xffff); m.wb('DGROUP:RemainingPassengerJourneys',v)
        m.wb('DGROUP:LevelCompletionMarker',0x53)
    def check(m,r,v=remaining):
        changed=(v-1)&255
        assert m.rb('DGROUP:RemainingPassengerJourneys')==(v if changed&128 else changed)
        assert m.rb('DGROUP:LevelCompletionMarker')==(0xfe if v==1 else 0x53)
    case('ReadPassengerJourneyLeg',f'journey exhausted remaining={remaining:x}',setup=setup,check=check,outputs=DEFINED)

# Water transition, including a wrapped subtraction whose JS differs from JL.
passenger=('UpdatePassengerPlatformWait','UpdatePassengerDestinationDisplay',
           'UpdatePassengerQuestionDisplay','UpdatePassengerApproach')
for n in passenger:
    for y,water in ((95,100),(94,100),(0x7fff,1),(0x8000,0x7fff)):
        case(n,f'{n} water cached={y:x} water={water:x}',
             [('ActorPixelY',y,ACTOR),('WaterYPixels',water,0)])
    # Contact with off-platform player switches to paired water descriptor.
    case(n,n+' contact off platform', [('PlayerY32',1280,0)])
    case(n,n+' second player water contact', [('PlayerY32',1280,2)])

# Platform wait: left/right/wait sequences, equality position, tick skip/zero,
# wrap-to-first frame, both players, occupied and absent vehicles.
for ticks in (0,1,2):
    for x in (90,102,110):
        for offset in (0,0xfffe):
            case('UpdatePassengerPlatformWait',f'wait ticks={ticks} x={x} off={offset:x}',
                 [('ActorAnimationCountdowns',ticks,ACTOR),('ActorPixelX',x,ACTOR),
                  ('ActorAnimationByteOffsets',offset,ACTOR)])
for scratch in (0,1,0xffff):
    case('UpdatePassengerPlatformWait',f'wait idle scratch={scratch:x}',
         [('ActorAnimationCountdowns',1,ACTOR),('ActorPixelX',102,ACTOR),('ds_2A2D',scratch,ACTOR)])
for player in (0,2):
    for carried in (0,4):
        case('UpdatePassengerPlatformWait',f'wait player={player} carried={carried}',
             [('PlayerPlatformIndices',3,player),('PlayerCarriedKinds',carried,player)])

for n in ('UpdatePassengerDestinationDisplay','UpdatePassengerQuestionDisplay'):
    for ticks in (0,1,2):
        for count in (0,1,2):
            case(n,f'{n} ticks={ticks} countdown={count}',
                 [('PlayerPlatformIndices',3,2),('ActorAnimationCountdowns',ticks,ACTOR),('ds_2A2D',count,ACTOR)])
    for index in range(0,12,2):
        case(n,f'{n} sequence off={index}',
             [('PlayerPlatformIndices',3,0),('ActorAnimationCountdowns',1,ACTOR),('ActorAnimationByteOffsets',index,ACTOR),('ds_2A2D',10,ACTOR)])
    for platforms,carry in (((0xffff,0xffff),0),((3,3),4),((0xffff,3),4),((3,3),0)):
        case(n,f'{n} platform scan {platforms} carried={carry}',
             [('PlayerPlatformIndices',platforms[0],0),('PlayerPlatformIndices',platforms[1],2),
              ('PlayerCarriedKinds',carry,0),('PlayerCarriedKinds',carry,2),('ds_2A2D',1,ACTOR)])

for ticks in (0,1,2):
    for x in (90,108,120):
        for player in (0,2):
            case('UpdatePassengerApproach',f'approach tick={ticks} x={x} player={player}',
                 [('PlayerPlatformIndices',3,player),('ActorAnimationCountdowns',ticks,ACTOR),('ActorPixelX',x,ACTOR)])
case('UpdatePassengerApproach','approach platform lost')
case('UpdatePassengerApproach','approach occupied still boards',
     [('PlayerPlatformIndices',3,0),('PlayerCarriedKinds',4,0),('ActorPixelX',108,ACTOR)])

for descriptor in ('Data_776A','Data_77FE','Data_7892'):
    for player in (0,2):
        case('BoardWaterbornePassenger',f'water board {descriptor} player={player}',actor=descriptor,
             regs=dict(DI=player),outputs=GENERAL+('CF','PF','AF','ZF','SF','OF','IF','DF'),df=True)

for fare,mult,quick in ((0,0,0),(500,2,0),(0xffff,0xffff,0),(0x8000,2,0),(501,8,1),(0xffff,0xffff,1)):
    case('DeliverPassenger',f'deliver fare={fare} mult={mult} quick={quick}',
         [('PlayerPassengerFares',fare,2),('ScoreMultiplier',mult,0),('PassengerQuickDeliveryCountdowns',quick,ACTOR)],df=True)

for player in (0,2):
    for carry in (0,1,0xffff):
        case('UpdateStonePickupWait',f'stone touch player={player} carried={carry}',actor='Data_78DC',
             updates=[('PlayerY32',1280,player),('PlayerCarriedKinds',carry,player)],outputs=DEFINED)
case('UpdateStonePickupWait','stone misses both players',actor='Data_78DC',outputs=DEFINED)

# Descending thrown stone set up geometrically against the real enemy box.
def stone_hit(m,speed=31):
    m.ww('DGROUP:ActorDescriptors',m.off('DGROUP:Data_78DC'))
    m.ww('DGROUP:ActorDescriptors',0xffff,2)
    m.ww('DGROUP:ActorUpdateOrScriptCursor',m.off('GAME:UpdateThrownStone'))
    m.ww('DGROUP:ds_2C6D',speed)
    m.ww('DGROUP:ActorX32',3200)
    m.ww('DGROUP:ActorY32',2560)


def enemy_case(n,title,updates=(),**kwargs):
    case(n,title,updates,slot=ENEMY,**kwargs)


for ticks in (0,1,2):
    for direction in (0,2):
        enemy_case('UpdateDinosaurPatrol',f'patrol tick={ticks} dir={direction}',
                   [('EnemyAnimationCountdowns',ticks,ENEMY),('EnemyDirectionOrTargetPlayer',direction,ENEMY)])
for x,speed in ((0,-32),(0,0),(3200,32),(5300,32),(0x7fff,32),(0x8000,-32)):
    enemy_case('UpdateDinosaurPatrol',f'patrol bounds x={x} speed={speed}',
               [('EnemyAnimationCountdowns',1,ENEMY),('EnemyX32',x,ENEMY),('EnemyHorizontalSpeeds',speed,ENEMY)])
for player in (0,2):
    enemy_case('UpdateDinosaurPatrol',f'patrol notice player={player}', [('PlayerPlatformIndices',3,player)])
enemy_case('UpdateDinosaurPatrol','patrol stone hit',setup=stone_hit)

for ticks in (0,1,2):
    for count in (0,1,2):
        enemy_case('UpdateDinosaurAlert',f'alert tick={ticks} state={count}',
                   [('EnemyAnimationCountdowns',ticks,ENEMY),('EnemyStateCounters',count,ENEMY)])
for n in ('UpdateDinosaurAlert','UpdateDinosaurCharge'):
    for player in (0,2):
        for x in (0,3200,6400,0x8000):
            for speed in (32,0xffe0):
                enemy_case(n,f'{n} facing player={player} x={x:x} speed={speed:x}',
                           [('PlayerPlatformIndices',3,player),('PlayerX32',x,player),('EnemyHorizontalSpeeds',speed,ENEMY)])
    enemy_case(n,n+' stone hit',setup=stone_hit)
    for offset in (0xfffe,0,2,4,6,8,10,12):
        enemy_case(n,f'{n} animation offset={offset:x}',
                   [('EnemyAnimationCountdowns',1,ENEMY),('EnemyAnimationByteOffsets',offset,ENEMY)])

for player in (0,2):
    for speed in (0,32,0xffe0,0x8000):
        enemy_case('UpdateDinosaurCharge',f'charge impact player={player} speed={speed:x}',
                   [('PlayerPlatformIndices',3,player),('PlayerY32',2560,player),('EnemyHorizontalSpeeds',speed,ENEMY)])

for n,field in (('AnimateDinosaurRecovery',0x2a),('AnimateDinosaurImpactRecovery',0x32)):
    for ticks in (0,1,2):
        for direction in (0,2):
            for offset in (0xfffe,0,2,4,6,8,10,12):
                enemy_case(n,f'{n} tick={ticks} dir={direction} off={offset:x}',
                           [('EnemyAnimationCountdowns',ticks,ENEMY),('EnemyDirectionOrTargetPlayer',direction,ENEMY),('EnemyAnimationByteOffsets',offset,ENEMY)])
    enemy_case(n,n+' stone hit',setup=stone_hit)

for ticks in (0,1,2):
    for offset in (0xfffe,0,2,4,6,8):
        enemy_case('UpdateFruitTreeAnimation',f'tree tick={ticks} offset={offset:x}',enemy='Data_76E4',
                   updates=[('EnemyAnimationCountdowns',ticks,ENEMY),('EnemyAnimationByteOffsets',offset,ENEMY)])

for ticks in (0,1,2):
    for offset in (0xfffe,0,2,4,6,8,10):
        # Offset 4 increments to 6 and reaches the missing C sound API.
        if ticks==1 and offset==4: continue
        enemy_case('loc_2973',f'hazard tick={ticks} offset={offset:x}',enemy='Data_76A8',
                   updates=[('EnemyAnimationCountdowns',ticks,ENEMY),('EnemyAnimationByteOffsets',offset,ENEMY)])
for x,y in ((0,0),(3000,2304),(0,2304),(3300,2304),(100,0xffff),(100,0x8000)):
    for phase in (4,6):
        enemy_case('loc_2973',f'hazard box x={x:x} y={y:x} phase={phase}',enemy='Data_76A8',
                   updates=[('EnemyAnimationByteOffsets',phase,ENEMY),('PlayerX32',x,0),('PlayerY32',y,0)])
enemy_case('loc_2973','hazard stone hit',enemy='Data_76A8',setup=stone_hit)

for ticks in (0,1,2):
    for offset in (0xfffe,0,2,4,6,8):
        enemy_case('UpdateBirdFlight',f'bird tick={ticks} offset={offset:x}',enemy='Data_7630',
                   updates=[('EnemyAnimationCountdowns',ticks,ENEMY),('EnemyAnimationByteOffsets',offset,ENEMY)])
for player,target,fade in ((0,0,0),(0,1,0),(2,1,0),(2,0,0),(0,0,0xffff)):
    enemy_case('UpdateBirdFlight',f'bird contact player={player} target={target} fade={fade:x}',enemy='Data_7630',
               updates=[('EnemyAnimationCountdowns',1,ENEMY),('EnemyDirectionOrTargetPlayer',target,ENEMY),
                        ('PlayerY32',2560,player),('ScreenFadeStep',fade,0)])

# Item benefit descriptor is a static copy with its type/reward words changed.
# Callbacks remain untouched; no original program is run during setup.
for kind in (0,1,2,0xffff):
    values=((0,0),(0x5a3a,1),(0x5a3b,1),(0xffff,2),(0x8000,0x8000)) if kind==0 else \
           ((0,0),(98,1),(99,1),(255,2),(0xabff,2)) if kind==1 else \
           ((0,0),(1,0),(8,0),(0x100,0),(0xff,0))
    for value,reward in values:
        for player in (0,2):
            def setup(m,k=kind,v=value,w=reward,p=player):
                d=m.off('DGROUP:FallingDescriptor_7A38')
                m.write(DATA_SEG,0x6300,m.read(DATA_SEG,d,20))
                word(m,0x6300+0x12,k); word(m,0x6300+0x0e,w)
                m.ww('DGROUP:FallingItemDescriptors',0x6300,ITEM)
                m.ww('DGROUP:PlayerY32',2560,p)
                if k==0: m.ww('DGROUP:LevelTimer',v)
                elif k==1: m.ww('DGROUP:LivesRemaining',v)
                else: m.ww('DGROUP:ScoreMultiplier',v)
            case('ExpireOrCollectFallingItem',f'item kind={kind:x} value={value:x} reward={reward:x} player={player}',
                 slot=ITEM,setup=setup,outputs=DEFINED)
for lifetime in (0,1,2,0xffff):
    case('ExpireOrCollectFallingItem',f'item no contact lifetime={lifetime:x}',slot=ITEM,
         updates=[('FallingItemMotionOrLifetime',lifetime,ITEM)],outputs=DEFINED)

for pending,phase,y32,pixels,step in ((0,0,3200,100,32),(0,1,3200,100,1),
        (0,1,3200,100,32),(0,1,3200,100,-32),(0,1,0,0,-1),
        (0,1,0x7fff,1023,1),(0,0,0xffff,100,1),(0,2,3200,100,32),
        (1,0,3200,100,32),(0xff,1,3200,100,32)):
    def setup(m,p=pending,ph=phase,y=y32,yp=pixels,s=step):
        m.wb('DGROUP:WaterRestorePending',p); m.wb('DGROUP:WaterStepPhase',ph)
        for n,v in (('WaterY32',y),('WaterYPixels',yp),('WaterSurfaceStep',s),
                    ('PreviousWaterSurfaceY',17),('VgaRowStrideBytes',96)):
            m.ww('DGROUP:'+n,v)
        m.ww('GAME:BackgroundPagePointer',0x1000); m.ww('GAME:BackgroundPagePointer',0xa000,2)
        m.ww('GAME:DrawPagePointer',0x5000); m.ww('GAME:DrawPagePointer',0xa000,2)
        m.device.planes[:]=bytes((i*29+77)&255 for i in range(4*65536))
    case('AdvanceWaterSurface',f'water pending={pending} phase={phase} fixed={y32:x} pixel={pixels} step={step}',
         setup=setup,outputs=DEFINED,df=True)

# Reproducible sign/wrap cases for native state arithmetic, with real tables.
rng=random.Random(0x1992)
for i in range(20):
    n=('UpdateDinosaurPatrol','UpdateDinosaurAlert','UpdateDinosaurCharge')[i%3]
    enemy_case(n,f'{n} seeded {i}',updates=[('EnemyX32',rng.randrange(65536),ENEMY),
               ('EnemyHorizontalSpeeds',rng.randrange(65536),ENEMY),('EnemyStateCounters',rng.randrange(65536),ENEMY),
               ('PlayerX32',rng.randrange(65536),0),('PlayerPlatformIndices',3,0)],df=bool(i&1))

# Last real frame followed by the built FFFF word exercises each loop reset.
for n,x in (('UpdatePassengerPlatformWait',90),('UpdatePassengerPlatformWait',110),
            ('UpdatePassengerApproach',90),('UpdatePassengerApproach',120)):
    case(n,n+f' real walk sentinel x={x}',
         [('ActorAnimationCountdowns',1,ACTOR),('ActorAnimationByteOffsets',16,ACTOR),
          ('ActorPixelX',x,ACTOR),('PlayerPlatformIndices',3,0)])
case('UpdatePassengerPlatformWait','platform wait real idle sentinel',
     [('ActorAnimationCountdowns',1,ACTOR),('ActorAnimationByteOffsets',6,ACTOR),
      ('ActorPixelX',102,ACTOR),('ds_2A2D',1,ACTOR)])
for n in passenger:
    case(n,n+' contact on platform',
         [('PlayerY32',1280,0),('PlayerPlatformIndices',3,0)])
for n,descriptor,offset in (('UpdateDinosaurPatrol','Data_766C',10),
        ('UpdateFruitTreeAnimation','Data_76E4',26),('UpdateBirdFlight','Data_7630',22),
        ('loc_2973','Data_76A8',18)):
    enemy_case(n,n+' real sequence sentinel',enemy=descriptor,
               updates=[('EnemyAnimationCountdowns',1,ENEMY),('EnemyAnimationByteOffsets',offset,ENEMY)])
enemy_case('loc_2973','hazard lower horizontal miss',enemy='Data_76A8',
           updates=[('PlayerX32',0xfe3f,0),('PlayerY32',2304,0)])

# Independent known answers supplement full-state comparisons for narrow stores
# and score carry. These inspect only the original routine result.
def known_item(m,r):
    assert m.rw('DGROUP:FallingItemSprites',ITEM)==0xffff
    assert m.rw('DGROUP:ScoreMultiplier')==2
    assert m.rb('DGROUP:LivesRemaining')==0x34


case('ExpireOrCollectFallingItem','item known multiplier and untouched lives',slot=ITEM,
     updates=[('PlayerY32',2560,0),('ScoreMultiplier',1,0)],
     setup=lambda m:m.wb('DGROUP:LivesRemaining',0x34),check=known_item,outputs=DEFINED)


def known_score(m,r):
    assert m.rw('DGROUP:ScoreLowWord')==998
    assert m.rw('DGROUP:ScoreHighWord')==0
    assert m.rb('DGROUP:HudFareClearPending')==1


case('DeliverPassenger','delivery known ADD/ADC overflow',check=known_score)

# Dynamic DS is part of the ABI, not a fixed DGROUP assumption.
# Copy a static snapshot into a distinct bank; both sides get identical bytes.
for n,slot,actor,enemy in (
        ('ReadPassengerJourneyLeg',ACTOR,'Data_7720','Data_766C'),
        ('UpdatePassengerPlatformWait',ACTOR,'Data_7720','Data_766C'),
        ('UpdatePassengerDestinationDisplay',ACTOR,'Data_7720','Data_766C'),
        ('UpdatePassengerQuestionDisplay',ACTOR,'Data_7720','Data_766C'),
        ('UpdatePassengerApproach',ACTOR,'Data_7720','Data_766C'),
        ('BoardWaterbornePassenger',ACTOR,'Data_776A','Data_766C'),
        ('UpdateStonePickupWait',ACTOR,'Data_78DC','Data_766C'),
        ('DeliverPassenger',ACTOR,'Data_7720','Data_766C'),
        ('UpdateDinosaurPatrol',ENEMY,'Data_7720','Data_766C'),
        ('UpdateDinosaurAlert',ENEMY,'Data_7720','Data_766C'),
        ('UpdateDinosaurCharge',ENEMY,'Data_7720','Data_766C'),
        ('AnimateDinosaurRecovery',ENEMY,'Data_7720','Data_766C'),
        ('AnimateDinosaurImpactRecovery',ENEMY,'Data_7720','Data_766C'),
        ('UpdateFruitTreeAnimation',ENEMY,'Data_7720','Data_76E4'),
        ('UpdateBirdFlight',ENEMY,'Data_7720','Data_7630'),
        ('loc_2973',ENEMY,'Data_7720','Data_76A8'),
        ('ExpireOrCollectFallingItem',ITEM,'Data_7720','Data_766C')):
    def copy_bank(m): m.write(0x8500,0,m.read(DATA_SEG,0,65536))
    case(n,n+' dynamic DS bank',slot=slot,actor=actor,enemy=enemy,
         setup=copy_bank,regs=dict(DS=0x8500),df=True)

# Explicit unresolved-composition diagnostics. These are NOT acceptance cases:
# native execution must return UGH_BAD_CALLBACK until peer adapters arrive.
BOUNDARIES=[]


def boundary(*args,**kwargs):
    case(*args,**kwargs)
    BOUNDARIES.append(CASES.pop())


boundary('DeliverPassenger','UNVERIFIED delivery reward -> C:PlayAdlibEffect',
         [('PassengerQuickDeliveryCountdowns',1,ACTOR),('ScoreMultiplier',1,0)])
boundary('loc_2973','UNVERIFIED hazard frame six -> C:PlayAdlibEffect',slot=ENEMY,enemy='Data_76A8',
         updates=[('EnemyAnimationCountdowns',1,ENEMY),('EnemyAnimationByteOffsets',4,ENEMY)])
for x in (0xfc00,0x2800):
    boundary('UpdateBirdFlight',f'UNVERIFIED bird x={x:x} -> StopBirdFlightSound',slot=ENEMY,enemy='Data_7630',
             updates=[('EnemyX32',x,ENEMY),('EnemyHorizontalSpeeds',0,ENEMY)])
boundary('UpdateBirdFlight','UNVERIFIED bird stone hit -> StopBirdFlightSound',slot=ENEMY,enemy='Data_7630',
         updates=[('EnemyAnimationCountdowns',1,ENEMY)],setup=stone_hit)


def tree_boundary(m):
    stone_hit(m)
    word(m,0x6400,m.off('DGROUP:FallingDescriptor_7A38')); word(m,0x6402,0xffff)
    m.ww('DGROUP:EnemyAnimationOrDropLists',0x6400,ENEMY)


boundary('UpdateFruitTreeAnimation','UNVERIFIED tree stone hit -> ReleaseTreeReward',slot=ENEMY,enemy='Data_76E4',
         updates=[('EnemyAnimationCountdowns',1,ENEMY)],setup=tree_boundary)
