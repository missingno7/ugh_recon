"""Actor, stone, collision and enemy leaf states; static fixtures only.

Real descriptors and animation sequences are read from the rebuilt program.
Controlled descriptors copy those records and select existing Ignore callbacks
for tails owned by other waves. Such cases test pointer/register flow, not the
untranslated native call edge; the worker report enumerates those edges.
"""
from difftest import Case
from emu import DATA_SEG
import random

GENERAL=('AX','BX','CX','DX','SI','DI','BP')
OUTPUT=GENERAL+('CF','PF','ZF','SF','OF','IF','DF')
CASES=[]
ACTOR=6
ENEMY=4
CONTROL=0x6000
SEQUENCE=0x6100


def word(m,off,value):
    m.write(DATA_SEG,off,bytes((value&255,(value>>8)&255)))


def fixture(m,actor='Data_7720',enemy='Data_766C',controlled=False):
    for n in ('ActorDescriptors','ActorUpdateOrScriptCursor','ActorSpriteIds',
              'ActorAnimationByteOffsets','ActorAnimationCountdowns','ActorX32',
              'ActorY32','ActorPixelX','ActorPixelY','ActorOverlayOrScriptCallbacks',
              'ActorSourcePlatformByteIndices','ActorDestinationPlatformByteIndices',
              'ActorDestinationPlatforms','ActorJourneyCursors','ds_2ACD','ds_2A2D',
              'ds_2C6D','PassengerQuickDeliveryCountdowns','EnemyDescriptors',
              'EnemyStateCallbacks','EnemyAnimationByteOffsets','EnemyAnimationCountdowns',
              'EnemySpriteIds','EnemyX32','EnemyY32','EnemyDrawX','EnemyDrawY',
              'EnemyHorizontalSpeeds','EnemyStateCounters','EnemyInitialDelays',
              'EnemyDirectionOrTargetPlayer'):
        for i in range(0,16,2): m.ww('DGROUP:'+n,0xa131+i*33,i)
    m.ww('DGROUP:ActorDescriptors',0xffff)
    m.ww('DGROUP:ActorDescriptors',m.off('DGROUP:'+actor),ACTOR)
    m.ww('DGROUP:ActorDescriptors',0xffff,ACTOR+2)
    m.ww('DGROUP:EnemyDescriptors',m.off('DGROUP:'+enemy),ENEMY)
    m.ww('DGROUP:EnemyDescriptors',0xffff,ENEMY+2)
    for n,v in (('ActorAnimationByteOffsets',0),('ActorAnimationCountdowns',2),
                ('ActorX32',3200),('ActorY32',2560),('ActorPixelX',100),('ActorPixelY',80),
                ('ActorSourcePlatformByteIndices',2),('ActorDestinationPlatformByteIndices',4),
                ('ActorDestinationPlatforms',3),('ds_2A2D',2),('ds_2ACD',2),('ds_2C6D',0),
                ('PassengerQuickDeliveryCountdowns',2),('ActorJourneyCursors',0xfffe)):
        m.ww('DGROUP:'+n,v,ACTOR)
    for n,v in (('EnemyAnimationByteOffsets',0),('EnemyAnimationCountdowns',2),
                ('EnemyX32',3200),('EnemyY32',2560),('EnemyHorizontalSpeeds',32),
                ('EnemyStateCounters',2),('EnemyDirectionOrTargetPlayer',0)):
        m.ww('DGROUP:'+n,v,ENEMY)
    for i in (0,2):
        for n,v in (('PlayerX32',3200),('PlayerY32',2560),('PlayerYPixels',82),
                    ('PlayerPixelX',100),('PlayerVerticalVelocities',0),
                    ('PlayerCarriedKinds',0),('PlayerPassengerFares',500),('PlayerMinimumFares',200),
                    ('PlayerPlatformIndices',4),('PlayerDestinationIcons',0xcdef)):
            m.ww('DGROUP:'+n,v,i)
    for i in (0,2,4,6):
        for n,v in (('PlatformActorOccupants',0xffff),('PlatformHeights',100),
                    ('PlatformArrivalPointsX',120),('PlatformLeftEdges',0),
                    ('PlatformRightEdges',200),('PlatformDestinationIcons',i+10)):
            m.ww('DGROUP:'+n,v,i)
    m.ww('DGROUP:PlatformLeftEdges',0xffff,8)
    m.ww('DGROUP:WaterYPixels',100)
    m.ww('DGROUP:PlayerCount',2)
    m.ww('DGROUP:ScoreLowWord',0xfffe)
    m.ww('DGROUP:ScoreHighWord',0xffff)
    if controlled:
        src=m.off('DGROUP:'+actor)
        m.write(DATA_SEG,CONTROL,m.read(DATA_SEG,src,0x4a))
        m.ww('DGROUP:ActorDescriptors',CONTROL,ACTOR)
        for f in range(8,0x2e,2): word(m,CONTROL+f,m.off('GAME:IgnoreActorState'))
        for f in range(0x2e,0x3a,2): word(m,CONTROL+f,SEQUENCE)
        word(m,CONTROL+0x3e,3)
        m.write(DATA_SEG,CONTROL+0x80,m.read(DATA_SEG,m.off('DGROUP:'+enemy),0x3c))
        m.ww('DGROUP:EnemyDescriptors',CONTROL+0x80,ENEMY)
        for f in range(8,0x22,2): word(m,CONTROL+0x80+f,m.off('GAME:IgnoreActorState'))
        for f in range(0x22,0x3a,2): word(m,CONTROL+0x80+f,SEQUENCE)
        for i,v in enumerate((101,102,0xffff,103,0xffff)):
            word(m,SEQUENCE+2*i,v)


def case(name,title,updates=(),*,actor='Data_7720',enemy='Data_766C',controlled=False,
         actor_state=True,setup=None,regs=None,check=None,reverse=False,outputs=OUTPUT):
    def init(m):
        fixture(m,actor,enemy,controlled)
        for n,v,i in updates: m.ww('DGROUP:'+n,v,i)
        if setup: setup(m)
    def inputs(m):
        values=dict(DS=DATA_SEG)
        if name not in ('DispatchEnemyStates','IgnoreActorState','IgnoreWaterbornePassengerState'):
            values['BX']=ACTOR if actor_state else ENEMY
        if name in ('BoardPassenger','AttachStoneToPlayer'): values['DI']=2
        if name in ('StunBirdAndAwardScore','StunDinosaurAndAwardScore','loc_2A53',
                    'BeginDinosaurAlert','BeginDinosaurCharge','BeginDinosaurRecovery',
                    'BeginDinosaurImpactRecovery','FindPlayerTouchingActor',
                    'FindPlayerTouchingEnemy','FindPlayerTouchingFallingItem'):
            values['SI']=((CONTROL if actor_state else CONTROL+0x80) if controlled
                          else m.off('DGROUP:'+(actor if actor_state else enemy)))
        if regs: values.update(regs(m) if callable(regs) else regs)
        return values
    if name in ('PlacePassengerOnPlatform','UpdateThrownStone','UpdatePassengerResurfacing',
                'InitializeFruitTreeAnimation'):
        outputs=tuple(n for n in outputs if n!='OF')  # SHL count>1 leaves OF undefined.
    CASES.append(Case(title,'GAME:'+name,setup=init,regs=inputs,out_regs=outputs,
                      flags=0x602 if reverse else 0x202,check=check))


# Every initializer reads a real descriptor; alternate indices and DF preserve
# state outside its selected arrays. All original general registers are compared.
actor_initializers=('PlacePassengerOnPlatform','BeginPassengerPlatformWait',
    'BeginPassengerDestinationDisplay','BeginPassengerQuestionDisplay','BeginPassengerApproach',
    'BoardPassenger','BeginPassengerDeparture','BeginStonePickupWait','AttachStoneToPlayer',
    'BeginPassengerResurfacing','BeginPassengerSinking','BeginPassengerFloating')
for n in actor_initializers:
    for alt in (False,True):
        case(n,n+(' reverse/alternate' if alt else ' built'),
             actor='Data_776A' if 'Resurfacing' in n or 'Sinking' in n or 'Floating' in n else
                   'Data_78DC' if 'Stone' in n else 'Data_7720',reverse=alt,
             regs=dict(DI=0 if alt else 2))
for dest in (0,5,6,0x7fff,0x8000,0xfef3,0xfef4,0xffff):
    case('BeginPassengerDestinationDisplay',f'destination wrapping/cap {dest:04x}',
         [('ActorDestinationPlatforms',dest,ACTOR)])
for n in ('BeginBirdDelay','BeginDinosaurPatrol','BeginDinosaurAlert','BeginDinosaurCharge',
          'BeginDinosaurRecovery','BeginDinosaurImpactRecovery','StunBirdAndAwardScore',
          'StunDinosaurAndAwardScore','loc_295B','loc_2A53','InitializeFruitTreeAnimation'):
    for alt in (False,True):
        enemy='Data_7630' if 'Bird' in n else 'Data_76A8' if n.startswith('loc_') else 'Data_76E4' if 'Fruit' in n else 'Data_766C'
        case(n,n+(' negative/overflow' if alt else ' built'),
             [('EnemyHorizontalSpeeds',0x8000 if alt else 0,ENEMY),
              ('EnemyX32',0xffff if alt else 3200,ENEMY),('EnemyY32',0x8001 if alt else 2560,ENEMY)],
             enemy=enemy,actor_state=False,reverse=alt)
for n in ('IgnoreActorState','IgnoreWaterbornePassengerState'):
    for df in (False,True): case(n,n+f' DF={df}',reverse=df,outputs=GENERAL+('CF','PF','AF','ZF','SF','OF','IF','DF'))

for delay,occupant in ((0,0xffff),(1,0xffff),(2,0xffff),(0xffff,0xffff),(0,0),(1,0xfffe)):
    case('WaitForPassengerPlatform',f'platform wait {delay}/{occupant}',
         [('ds_2ACD',delay,ACTOR),('PlatformActorOccupants',occupant,2)])
for ticks,offset in ((0,0),(2,0),(1,0xfffe),(1,0),(1,2)):
    case('AnimatePassengerArrival',f'arrival ticks={ticks} offset={offset}',
         [('ActorAnimationCountdowns',ticks,ACTOR),('ActorAnimationByteOffsets',offset,ACTOR)],
         controlled=True)
for ticks,offset in ((0,0),(2,0),(1,0xfffe),(1,0),(1,2)):
    case('AnimatePassengerDeparture',f'departure ticks={ticks} offset={offset}',
         [('ActorAnimationCountdowns',ticks,ACTOR),('ActorAnimationByteOffsets',offset,ACTOR)],controlled=True)
for fare,minimum in ((0,0),(200,200),(199,200),(201,200),(0xffff,0),(0x8000,0x7fff)):
    for ticks in (0,1,0x7fff,0x8000,0xffff):
        case('UpdateCarriedPassenger',f'fare={fare}/{minimum}, quick={ticks}',
             [('PlayerPassengerFares',fare,2),('PlayerMinimumFares',minimum,2),
              ('PassengerQuickDeliveryCountdowns',ticks,ACTOR)])
case('UpdateCarriedPassenger','delivery callback selected from controlled descriptor',
     [('PlayerPlatformIndices',3,2)],controlled=True)
for action in (0,1,0x7f,0x80,0xff):
    case('WaitForStoneRelease',f'action signed byte {action:02x}',controlled=True,
         setup=lambda m,v=action:m.wb('DGROUP:PlayerActionInput',v,2))
for action in (0x8000,0xff7f,0x0100,0xff01,0x0080):
    case('WaitForStoneRelease',f'action ignores adjacent high byte {action:04x}',controlled=True,
         setup=lambda m,v=action:m.ww('DGROUP:PlayerActionInput',v,2))

for ticks,x,offset,fixed in ((0,100,0,3200),(2,100,0,3200),(1,100,0xfffe,3200),
                            (1,200,0xfffe,6400),(1,112,0,3584),
                            (1,100,2,3552),(1,200,2,3552),(1,0x8000,0,0x8000)):
    case('WalkPassengerToExit',f'exit ticks={ticks}, x={x}, offset={offset}, x32={fixed}',
         [('ActorAnimationCountdowns',ticks,ACTOR),('ActorPixelX',x,ACTOR),
          ('ActorX32',fixed,ACTOR),('ActorAnimationByteOffsets',offset,ACTOR)],controlled=True)

# Stone screen limits, signed vertical velocity, all platform-crossing rejects
# and inclusive contact edges. A real stone descriptor lands at IgnoreActorState.
for x,vx,y,vy in ((0xfe00,0,1000,0),(0xfe01,0,1000,0),(0x27ff,0,1000,0),
                  (0x2800,0,1000,0),(0x7fff,1,1000,0),(0xffff,1,1000,0),
                  (3200,0,0x17ff,0),(3200,0,1000,0xfffc),(3200,0,1000,0xfffe),
                  (3200,0,0x17fe,0),(3200,0,0x17fd,0),(3200,0,0xffff,0)):
    case('UpdateThrownStone',f'stone physics {x:04x}/{vx:04x}/{y:04x}/{vy:04x}',
         [('ActorX32',x,ACTOR),('ds_2ACD',vx,ACTOR),('ActorY32',y,ACTOR),('ds_2C6D',vy,ACTOR)],actor='Data_78DC')
for height,left,right in ((39,0,200),(45,0,200),(41,105,200),(41,0,103),(41,104,104),
                          (40,104,104),(42,104,104)):
    case('UpdateThrownStone',f'stone platform {height}/{left}/{right}',
         [('ActorY32',1152,ACTOR),('ds_2C6D',62,ACTOR),
          ('PlatformHeights',height,0),('PlatformLeftEdges',left,0),('PlatformRightEdges',right,0)],actor='Data_78DC')

for n in ('UpdatePassengerResurfacing','UpdatePassengerSinking'):
    for ticks,off in ((0,0),(2,0),(1,0xfffe),(1,2)):
        case(n,f'{n} animation ticks={ticks}/offset={off}',
             [('ActorAnimationCountdowns',ticks,ACTOR),('ActorAnimationByteOffsets',off,ACTOR)],
             actor='Data_776A',controlled=True)
for velocity in (0,1,0x175,0x1800,0x7fff,0x8000,0xe7d8,0xe800,0xffff):
    for py in (80,107,108,109):
        case('UpdatePassengerResurfacing',f'resurface acceleration v={velocity:04x} py={py}',
             [('ds_2C6D',velocity,ACTOR),('ActorPixelY',py,ACTOR)],actor='Data_776A',controlled=True)
for y in (0,0xffff,0x17ff,0x1800,0x8000,3200,3300):
    for velocity in (0,0x17ff,0x7fff,0x8000,0xffff):
        case('UpdatePassengerSinking',f'sinking y={y:04x}/v={velocity:04x}',
             [('ActorY32',y,ACTOR),('ds_2C6D',velocity,ACTOR)],actor='Data_776A',controlled=True)
case('UpdatePassengerResurfacing','resurface crossing into real floating initializer',
     [('ActorY32',3000,ACTOR),('ds_2C6D',0xff00,ACTOR)],actor='Data_776A')

for desc in ('Data_776A','Data_77FE'):
    for count in (0,1,2,0xffff):
        case('UpdatePassengerFloating',f'floating real descriptor={desc} timer={count}',
             [('ds_2ACD',count,ACTOR),('PlayerCarriedKinds',1,0),('PlayerCarriedKinds',1,2)],actor=desc)
for py,vel,kind,count,who in ((82,0,0,1,0),(81,0,0,2,0),(82,1,0,2,0),
                             (82,0,1,2,0),(82,0,0,2,2),(82,0,0,1,2)):
    case('UpdatePassengerFloating',f'floating eligibility y={py} v={vel} kind={kind} count={count} who={who}',
         [('PlayerCarriedKinds',1,0),('PlayerCarriedKinds',1,2),
          ('PlayerCarriedKinds',kind,who),('PlayerVerticalVelocities',vel,who),
          ('PlayerYPixels',py,who),('PlayerCount',count,0)],actor='Data_776A',controlled=True)
for n in ('UpdateFloatingDestinationDisplay','UpdateFloatingQuestionDisplay','UpdateFloatingPassengerApproach'):
    for ticks,off,py,x,timeout in ((0,0,100,100,0),(2,0,100,100,2),(1,0xfffe,100,100,2),
                                 (1,2,82,100,1),(1,0,82,92,1),(1,0,82,80,2),
                                 (2,2,82,100,2),(2,2,82,80,2)):
        case(n,f'{n} ticks={ticks} off={off} py={py} x={x} timeout={timeout}',
             [('ActorAnimationCountdowns',ticks,ACTOR),('ActorAnimationByteOffsets',off,ACTOR),
              ('ActorPixelY',100 if ticks==0 else 80,ACTOR),('PlayerYPixels',py,0),
              ('PlayerYPixels',py,2),('PlayerPixelX',x,0),('PlayerPixelX',x,2),
              ('ds_2A2D',timeout,ACTOR)],actor='Data_776A',controlled=True)
for n in ('UpdateFloatingDestinationDisplay','UpdateFloatingPassengerApproach'):
    for count,kind,first,second in ((1,0,100,82),(2,0,100,82),(2,1,82,82),(2,1,100,100)):
        case(n,f'{n} search count={count} kind={kind} y={first}/{second}',
             [('PlayerCount',count,0),('PlayerCarriedKinds',kind,0),('PlayerCarriedKinds',kind,2),
              ('PlayerYPixels',first,0),('PlayerYPixels',second,2)],actor='Data_776A',controlled=True)

# Contact helpers: each separating plane, both equalities, second-player retry,
# nonstandard counts and signed wrap. Expected SF/DI derives from fixture inputs.
for n,xb,yb in (('FindPlayerTouchingActor','ActorX32','ActorY32'),
                ('FindPlayerTouchingEnemy','EnemyX32','EnemyY32'),
                ('FindPlayerTouchingFallingItem','FallingItemX','FallingItemY')):
    falling='Falling' in n
    for side,px,py in (('inside',3200,2560),('below',3200,3500),('above',3200,1000),
                       ('left',1000,2560),('right',5000,2560),
                       ('y high equal',3200,3264),('y low equal',3200,2176 if not falling else 2432),
                       ('x high equal',3520 if not falling else 3392,2560),
                       ('x low equal',2400 if not falling else 2528,2560),
                       ('one below y low',3200,2175 if not falling else 2431),
                       ('one above y high',3200,3265),
                       ('one below x low',2399 if not falling else 2527,2560),
                       ('one above x high',3521 if not falling else 3393,2560)):
        case(n,f'{n} contact {side}',[(xb,3200,ACTOR),(yb,2560,ACTOR),
             ('PlayerX32',px,0),('PlayerY32',py,0),('PlayerCount',1,0)],
             actor_state=True,regs=dict(SI=CONTROL),controlled=True,
             setup=lambda m: [word(m,CONTROL+o,v) for o,v in ((0,8),(2,22),(4,7),(6,7))])
    for count,who in ((1,2),(2,2),(3,2),(4,4)):
        def set_players(m,who=who):
            word(m,CONTROL,8); word(m,CONTROL+2,22); word(m,CONTROL+4,7); word(m,CONTROL+6,7)
            for i in (0,2,4): m.ww('DGROUP:PlayerY32',0x7000,i)
            m.ww('DGROUP:PlayerY32',2560,who)
        case(n,f'{n} retry count={count} hit slot={who}',[(xb,3200,ACTOR),(yb,2560,ACTOR),('PlayerCount',count,0)],
             controlled=True,setup=set_players,regs=dict(SI=CONTROL))

for mode in ('sentinel','wrong descriptor','wrong state','ascending','below','above','left','right','hit','second'):
    def stones(m,mode=mode):
        i=2 if mode=='second' else 0
        m.ww('DGROUP:ActorDescriptors',0,0)
        m.ww('DGROUP:ActorDescriptors',m.off('DGROUP:Data_78DC'),i)
        m.ww('DGROUP:ActorDescriptors',0xffff,i+2)
        m.ww('DGROUP:ActorUpdateOrScriptCursor',m.off('GAME:UpdateThrownStone'),i)
        m.ww('DGROUP:ds_2C6D',0,i)
        m.ww('DGROUP:ActorX32',3200,i); m.ww('DGROUP:ActorY32',2560,i)
        if mode=='sentinel': m.ww('DGROUP:ActorDescriptors',0xffff,0)
        if mode=='wrong descriptor': m.ww('DGROUP:ActorDescriptors',0,i)
        if mode=='wrong state': m.ww('DGROUP:ActorUpdateOrScriptCursor',0,i)
        if mode=='ascending': m.ww('DGROUP:ds_2C6D',0xffff,i)
        if mode in ('below','above'): m.ww('DGROUP:ActorY32',1000 if mode=='below' else 4000,i)
        if mode in ('left','right'): m.ww('DGROUP:ActorX32',1000 if mode=='left' else 5000,i)
    case('FindThrownStoneHittingEnemy','stone enemy contact '+mode,actor_state=False,setup=stones)

for n in ('WaitForBirdFlight','WaitForBirdWarning','loc_2A76'):
    for timer in (0,1,2,0x8000,0xffff):
        case(n,f'{n} equality timer {timer:04x}',[('EnemyStateCounters',timer,ENEMY)],
             actor_state=False,controlled=True)
for x,y,v,ticks in ((0xfc00,1000,0,0),(0xfc01,1000,0,0),(0x27ff,1000,0,0),
                     (0x2800,1000,0,0),(3200,0x17ff,32,0),(3200,0x17d8,32,40),
                     (3200,1000,32,39),(3200,1000,32,40),(3200,1000,32,41),
                     (3200,1000,32,0xffff)):
    case('UpdateStunnedBird',f'stunned bird {x:04x}/{y:04x}/{v}/{ticks}',
         [('EnemyX32',x,ENEMY),('EnemyY32',y,ENEMY),('EnemyHorizontalSpeeds',v,ENEMY),
          ('EnemyStateCounters',ticks,ENEMY)],actor_state=False,enemy='Data_7630')
for timer,ticks,offset,direction in ((0,1,0,0),(1,1,0,0),(2,0,0,0),
                                    (2,2,0,2),(2,1,0xfffe,0),(2,1,2,2)):
    case('UpdateStunnedDinosaur',f'stunned dinosaur {timer}/{ticks}/{offset}/{direction}',
         [('EnemyStateCounters',timer,ENEMY),('EnemyAnimationCountdowns',ticks,ENEMY),
          ('EnemyAnimationByteOffsets',offset,ENEMY),('EnemyDirectionOrTargetPlayer',direction,ENEMY)],
         actor_state=False,controlled=True)

for count in (0,1,4):
    def enemies(m,count=count):
        for i in range(count):
            m.ww('DGROUP:EnemyDescriptors',m.off('DGROUP:Data_766C'),2*i)
            m.ww('DGROUP:EnemyStateCallbacks',m.off('GAME:BeginDinosaurPatrol') if i%2 else m.off('GAME:IgnoreActorState'),2*i)
        m.ww('DGROUP:EnemyDescriptors',0xffff,2*count)
    case('DispatchEnemyStates',f'enemy dispatch count={count}',actor_state=False,setup=enemies)

# A few reproducible broad-width fixtures expose intermediate wrap/signed errors.
rng=random.Random(0x15092a87)
for n in ('FindPlayerTouchingActor','FindPlayerTouchingEnemy','FindPlayerTouchingFallingItem'):
    for i in range(12):
        values=[rng.randrange(65536) for _ in range(8)]
        def random_contact(m,v=values):
            for o,x in zip((0,2,4,6),v): word(m,CONTROL+o,x)
        case(n,f'{n} fixed-seed words {i}',
             [('ActorX32',values[4],ACTOR),('ActorY32',values[5],ACTOR),
              ('EnemyX32',values[4],ACTOR),('EnemyY32',values[5],ACTOR),
              ('FallingItemX',values[4],ACTOR),('FallingItemY',values[5],ACTOR),
              ('PlayerX32',values[6],0),('PlayerY32',values[7],0),('PlayerCount',1,0)],
             controlled=True,setup=random_contact,regs=dict(SI=CONTROL))

for height,left,right in ((46,0,200),(50,0,200),(48,109,200),(48,0,107),
                          (47,108,108),(48,108,108),(49,108,108)):
    case('UpdateThrownStone',f'stone foot crossing {height}/{left}/{right}',
         [('ActorY32',1152,ACTOR),('ds_2C6D',62,ACTOR),
          ('PlatformHeights',height,0),('PlatformLeftEdges',left,0),('PlatformRightEdges',right,0)],actor='Data_78DC')
for tick,off in ((0,4),(1,0xfffe),(1,2),(2,4)):
    case('UpdatePassengerFloating',f'floating sequence reset {tick}/{off}',
         [('ActorAnimationCountdowns',tick,ACTOR),('ActorAnimationByteOffsets',off,ACTOR)],
         actor='Data_776A',controlled=True)
case('UpdateFloatingPassengerApproach','floating approach left sequence reset',
     [('ActorAnimationCountdowns',2,ACTOR),('ActorAnimationByteOffsets',4,ACTOR),
      ('PlayerPixelX',80,0)],actor='Data_776A',controlled=True)
for n in ('StunBirdAndAwardScore','StunDinosaurAndAwardScore','loc_2A53'):
    for low,high,points in ((0,0,0),(0xffff,0,1),(0xffff,0xffff,0xffff),(0x7fff,0x7fff,1)):
        def score_fields(m,low=low,high=high,points=points):
            m.ww('DGROUP:ScoreLowWord',low); m.ww('DGROUP:ScoreHighWord',high)
            word(m,CONTROL+0x80+0x3a,points)
        def score_check(m,result,low=low,high=high,points=points):
            assert (m.rw('DGROUP:ScoreHighWord')<<16|m.rw('DGROUP:ScoreLowWord')) == (((high<<16)|low)+points)&0xffffffff
        case(n,f'{n} score carry {low:04x}/{high:04x}/{points:04x}',
             controlled=True,actor_state=False,setup=score_fields,check=score_check)

case('UpdatePassengerResurfacing','resurface exactly at surface in cached pixels',
     [('ActorPixelY',103,ACTOR)],actor='Data_776A',controlled=True)
case('UpdatePassengerResurfacing','resurface still below surface after upward motion',
     [('ActorY32',5000,ACTOR),('ds_2C6D',0xff00,ACTOR)],actor='Data_776A',controlled=True)
case('UpdatePassengerFloating','floating cached pixels already at surface',
     [('ActorPixelY',100,ACTOR)],actor='Data_776A',controlled=True)

# Composed local transitions using the unmodified shipped descriptor records.
for n,offset in (('AnimatePassengerArrival',0xfffe),('AnimatePassengerArrival',16),
                 ('AnimatePassengerDeparture',0xfffe),('AnimatePassengerDeparture',0)):
    case(n,f'{n} real finite sequence offset={offset}',
         [('ActorAnimationCountdowns',1,ACTOR),('ActorAnimationByteOffsets',offset,ACTOR)])
case('UpdateCarriedPassenger','carried water descriptor native no-op delivery callback',
     [('PlayerPlatformIndices',3,2)],actor='Data_776A')
case('WaitForStoneRelease','stone real descriptor nonnegative action',actor='Data_78DC',
     setup=lambda m:m.wb('DGROUP:PlayerActionInput',0x7f,2))
for n in ('UpdateFloatingDestinationDisplay','UpdateFloatingQuestionDisplay'):
    case(n,n+' real timeout transition',
         [('ActorAnimationCountdowns',1,ACTOR),('ActorAnimationByteOffsets',0xfffe,ACTOR),
          ('ds_2A2D',1,ACTOR)],actor='Data_776A')
for px in (80,110):
    case('UpdateFloatingPassengerApproach',f'floating real movement toward x={px}',
         [('ActorAnimationCountdowns',1,ACTOR),('ActorAnimationByteOffsets',0xfffe,ACTOR),
          ('PlayerPixelX',px,0),('PlayerPixelX',px,2)],actor='Data_776A')
case('UpdateFloatingPassengerApproach','floating real vehicle search fails',
     [('PlayerCarriedKinds',1,0),('PlayerCarriedKinds',1,2)],actor='Data_776A')

# Fully MOV-only entry paths preserve arithmetic flags as well as IF/DF.
preserving=set(actor_initializers)-{'PlacePassengerOnPlatform','BeginPassengerDestinationDisplay'}
preserving.update(('BeginBirdDelay','BeginDinosaurPatrol','BeginDinosaurAlert',
                  'BeginDinosaurCharge','BeginDinosaurRecovery','BeginDinosaurImpactRecovery',
                  'loc_295B'))
for c in CASES:
    if c.routine.split(':')[1] in preserving: c.out_regs=OUTPUT+('AF','OF')

# Every entry also runs with a relocated copy of the data bank. This is a valid
# synthetic segment flow, and detects accidental use of fixed DATA_SEG storage.
# The copy ends immediately below the loaded program and does not overlap it.
from dataclasses import replace
seen=set()
for original in list(CASES):
    if original.routine in seen: continue
    seen.add(original.routine)
    def alternate_setup(m,c=original):
        c.setup(m)
        m.write(0x10,0,m.read(DATA_SEG,0,65536))
    def alternate_regs(m,c=original):
        values=c.regs(m); values['DS']=0x10; return values
    CASES.append(replace(original,title=original.title+' alternate DS',setup=alternate_setup,
                         regs=alternate_regs,check=None))

# Native unresolved edges are checked up to the actual indirect transfer, with
# their unmodified built callbacks. The separate boundary driver compares the
# pre-transfer oracle state against the adapter's explicit BAD_CALLBACK result.
# It neither runs nor supplies a stand-in for any untranslated callee.
BOUNDARIES=[]
def boundary(name,title,delta,target,updates=(),**kw):
    case(name,title,updates,**kw)
    BOUNDARIES.append((CASES.pop(),delta,'GAME:'+target))

boundary('UpdateCarriedPassenger','native passenger delivery edge',0x1a7a-0x1a42,
         'DeliverPassenger',[('PlayerPlatformIndices',3,2)])
def departure_end(m):
    seq=m.rw('DGROUP:Data_7720',0x38)
    for offset in range(0,128,2):
        if int.from_bytes(m.read(DATA_SEG,seq+offset,2),'little')==0xffff:
            m.ww('DGROUP:ActorAnimationByteOffsets',offset-4,ACTOR)
            return
    raise AssertionError('built departure sequence lacks bounded sentinel')
boundary('AnimatePassengerDeparture','native next journey edge',0x1c0a-0x1bd6,
         'ReadPassengerJourneyLeg',[('ActorAnimationCountdowns',1,ACTOR)],setup=departure_end)
boundary('WaitForStoneRelease','native stone throw edge',0x1c7d-0x1c6b,
         'ThrowCarriedStone',actor='Data_78DC',setup=lambda m:m.wb('DGROUP:PlayerActionInput',0x80,2))
boundary('WaitForBirdFlight','native bird warning edge',0x23ac-0x239f,
         'BeginBirdWarning',[('EnemyStateCounters',1,ENEMY)],actor_state=False,enemy='Data_7630')
boundary('WaitForBirdWarning','native bird launch edge',0x23e6-0x23d9,
         'LaunchBirdTowardPlayer',[('EnemyStateCounters',1,ENEMY)],actor_state=False,enemy='Data_7630')
boundary('UpdateFloatingPassengerApproach','native waterborne boarding edge',0x213b-0x20c1,
         'BoardWaterbornePassenger',[('PlayerPixelX',92,0)],actor='Data_776A')
for target,descriptor in (
        ('BeginBirdWarning','Data_7630'),('LaunchBirdTowardPlayer','Data_7630'),
        ('UpdateBirdFlight','Data_7630'),('UpdateDinosaurPatrol','Data_766C'),
        ('UpdateDinosaurAlert','Data_766C'),('UpdateDinosaurCharge','Data_766C'),
        ('AnimateDinosaurRecovery','Data_766C'),('AnimateDinosaurImpactRecovery','Data_766C'),
        ('loc_2973','Data_76A8'),('UpdateFruitTreeAnimation','Data_76E4'),
        ('ReleaseTreeReward','Data_76E4'),('AdvanceTreeRewardCooldown','Data_76E4'),
        ('IgnoreExhaustedTree','Data_76E4')):
    def native_enemy(m,target=target,descriptor=descriptor):
        desc=m.off('DGROUP:'+descriptor)
        # Verify this is an original descriptor target before putting it in the
        # selected enemy's update slot, as initialization/previous states do.
        record=m.read(DATA_SEG,desc+8,26)
        assert m.off('GAME:'+target) in [int.from_bytes(record[i:i+2],'little') for i in range(0,26,2)]
        m.ww('DGROUP:EnemyDescriptors',desc,0)
        m.ww('DGROUP:EnemyStateCallbacks',m.off('GAME:'+target),0)
    boundary('DispatchEnemyStates','native enemy dispatcher edge '+target,0x236f-0x2363,
             target,actor_state=False,setup=native_enemy)
