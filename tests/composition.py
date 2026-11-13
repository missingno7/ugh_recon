"""Composed native caller/callee cases from the integration edge ledger."""
from dataclasses import replace
from difftest import load_suite,Case
from emu import DATA_SEG
CASES=[]
a=load_suite('actors_states')
for target in ('ReadPassengerJourneyLeg','UpdatePassengerPlatformWait','UpdatePassengerDestinationDisplay',
               'UpdatePassengerQuestionDisplay','UpdatePassengerApproach','DeliverPassenger',
               'BoardWaterbornePassenger','UpdateStonePickupWait','ThrowCarriedStone'):
    entry=next(c for c in a.CASES if c.routine=='GAME:'+target)
    def setup(m,entry=entry,target=target):
        entry.setup(m)
        for i in (0,2,4):
            m.ww('DGROUP:ActorDescriptors',m.off('DGROUP:Data_7720'),i)
            m.ww('DGROUP:ActorUpdateOrScriptCursor',m.off('GAME:IgnoreActorState'),i)
        m.ww('DGROUP:ActorUpdateOrScriptCursor',m.off('GAME:'+target),6)
        m.ww('DGROUP:ActorDescriptors',0xffff,8)
    CASES.append(replace(entry,routine='GAME:DispatchActorUpdates',title='composed actor dispatcher '+target,
                         setup=setup,check=None))
for target in ('BeginBirdWarning','LaunchBirdTowardPlayer','UpdateBirdFlight','UpdateTriopterusPatrol',
               'UpdateTriopterusAlert','UpdateTriopterusCharge','AnimateTriopterusRecovery',
               'AnimateTriopterusImpactRecovery','UpdateDinoForce','UpdateFruitTreeAnimation','ReleaseTreeReward'):
    entry=next(c for c in a.CASES if c.routine=='GAME:'+target)
    def setup(m,entry=entry,target=target):
        entry.setup(m)
        for i in (0,2):
            m.ww('DGROUP:EnemyDescriptors',m.off('DGROUP:Data_76E4'),i)
            m.ww('DGROUP:EnemyStateCallbacks',m.off('GAME:IgnoreExhaustedTree'),i)
        m.ww('DGROUP:EnemyStateCallbacks',m.off('GAME:'+target),4)
        m.ww('DGROUP:EnemyDescriptors',0xffff,6)
    CASES.append(replace(entry,routine='GAME:DispatchEnemyStates',title='composed enemy dispatcher '+target,
                         setup=setup,check=None))
for entry,delta,target in load_suite('actors').BOUNDARIES:
    if entry.routine=='GAME:DispatchEnemyStates':continue
    def setup(m,entry=entry):
        entry.setup(m)
        # Select the allocator's returning path; the real full-pool corruption
        # is a separate unsupported diagnostic, never a repaired continuation.
        if entry.routine=='GAME:UpdateCarriedPassenger':m.ww('DGROUP:FallingItemSprites',0xffff,22)
    CASES.append(replace(entry,title='composed '+entry.title,setup=setup))
entry=next(c for c in a.CASES if c.routine=='GAME:ExpireOrCollectFallingItem')
def falling(m):
    entry.setup(m)
    for i in range(0,24,2):
        if i!=10:m.ww('DGROUP:FallingItemSprites',0xffff,i)
    m.ww('DGROUP:FallingItemCallbacks',m.off('GAME:ExpireOrCollectFallingItem'),10)
CASES.append(replace(entry,routine='GAME:DispatchFallingItems',title='composed item dispatcher expiry',setup=falling,check=None))

api=load_suite('sound_api');opl=load_suite('adlib')
def sound(m,reserved=1,playing=1,voices=1):
    api.base(m,1);opl.base(m)
    m.ww('SOUND:SoundDeviceBits',1);m.ww('SOUND:ReservedAdlibChannelCount',reserved)
    m.ww('SOUND:MainAdlxPlaying',playing);m.ww('SOUND:MusicVoiceCount',voices)
    m.ww('SOUND:MusicFadeScheduled',0);m.ww('SOUND:SoundIoDelayMultiplier',1)
    api.desc(m,8,0x28,5);api.desc(m,8,0x22,1);api.desc(m,8,0x24,8)
for routine,args in [('SetMusicTrackVolume',(165,)),('StopAdlibTrackChannel',(8,)),
                     ('RestoreAdlibVoiceAllocation',(8,)),('ApplyScannedMusicEvents',()),
                     ('StopSoundChannel',(8,)),('StartSoundOutputs',()),('StopMusicTrack',(0,))]:
    CASES.append(Case('native OPL '+routine,'C:'+routine,setup=sound,args=args,kind='far',out_regs=api.KEEP))
for reserved in (0,2):
    def setup(m,reserved=reserved):
        sound(m,reserved)
        api.desc(m,8,0x28,4);api.desc(m,8,0x22,1)
    CASES.append(Case('native OPL start allocation '+str(reserved),'C:StartAdlibTrackChannel',
                      setup=setup,args=(8,165),kind='far',out_regs=('AX',)+api.KEEP))
for fade in (0,3):
    def setup(m):
        api.parser_setup(m,api.adlx(voices=1));m.ww('SOUND:SoundIoDelayMultiplier',1)
        m.ww('SOUND:MusicFadeScheduled',0)
    CASES.append(Case('native music start fade '+str(fade),'C:StartMusicTrack',setup=setup,
                      args=(0x401,0x7200,fade,165),kind='far',out_regs=('AX',)+api.KEEP))
for step,duration,start,end in ((0,4,0,255),(2,4,255,0),(3,4,100,200),(0xfffe,0xffff,1,2)):
    def setup(m,step=step,duration=duration,start=start,end=end):
        sound(m)
        for n,v in [('MusicFadeStep',step),('MusicFadeDuration',duration),('MusicFadeStartVolume',start),('MusicFadeTargetVolume',end)]:
            m.ww('SOUND:'+n,v)
    CASES.append(Case(f'composed fade interpolation {step}/{duration}/{start}/{end}',
                      'SOUND:AdvanceMusicFade',setup=setup,kind='far',out_regs=opl.REGS))
def effect_expire(m):
    sound(m)
    m.ww('SOUND:CurrentAdlxRecordOffset',m.off('SOUND:AudioChannelStates')+8*42)
    m.ww('SOUND:CurrentAdlxSlot',8)
    api.desc(m,8,4,1);api.desc(m,8,0x28,5)
CASES.append(Case('composed effect control expires allocation','SOUND:HandleEffectAdlxControl',
                  setup=effect_expire,kind='far',regs=dict(AX=0x77,ES=0x9000,DI=0x100),out_regs=opl.REGS))
def section(m):
    sound(m,reserved=0)
    m.ww('SOUND:AdlxTickCount',10);m.ww('SOUND:AdlxTickHighWord',0)
    m.ww('SOUND:MainAdlxDeadlineLow',0);m.ww('SOUND:MainAdlxDeadlineHigh',0)
    m.ww('SOUND:MainAdlxSectionLoopEnabled',1);m.ww('SOUND:MainAdlxSectionEnd',0x100)
    m.ww('SOUND:MainAdlxCursor',0x100);m.ww('SOUND:MainAdlxCursorSegment',0x9000)
    m.ww('SOUND:FirstScannedEvent',0x100);m.ww('SOUND:FirstScannedEvent',0x9000,2)
    m.write(0x9000,0x100,b'\x81');m.ww('SOUND:ScannedMusicClockTicks',1);m.ww('SOUND:ScannedMusicClockTicks',0,2)
CASES.append(Case('composed tick section native apply voices','SOUND:TickAdlxPlayback',
                  setup=section,kind='far',out_regs=opl.REGS))

# Shutdown's cancellation performs TIMER removal in foreground, exposing live DS.
def shutdown_fade(m):
    sound(m);load_suite('timer_stack').timer_state(m,1)
    m.ww('SOUND:MusicFadeScheduled',1);m.ww('SOUND:MusicFadeTimerHandle',0)
    m.ww('SOUND:AdlibInitAttempted',0);m.ww('TIMER:TimerInterruptInstalled',0)
    m.ww('C:SoundSystemShutdown',0);m.write(DATA_SEG,2,b'\x00\x00')
def shutdown_check(m,r):
    assert m.rw('C:SoundSystemShutdown')==0 and m.read(DATA_SEG,2,2)==b'\x01\x00'
CASES.append(Case('foreground fade cancellation writes DGROUP latch','C:ShutdownSoundSystem',
                  setup=shutdown_fade,kind='far',out_regs=api.KEEP,check=shutdown_check))
# Caller -> DMA priming with actual mixer and sample interrupt handler.
dsp=load_suite('dsp')
prime=next(c for c in dsp.CASES if c.routine=='SOUND:PrimeSampleDmaPlayback' and c.title.startswith('prime composed 0'))
def prime_setup(m):
    prime.setup(m);m.ww('SOUND:SoundDeviceBits',2)
CASES.append(replace(prime,setup=prime_setup,routine='C:StartSoundOutputs',title='composed outputs actual sample priming',
                     out_regs=api.KEEP,check=None))

def stop_fade(m):
    sound(m)
    m.ww('DGROUP:LastActiveTimerSlotOffset',0xfffe)
    for i in range(0,32,2):m.ww('DGROUP:TimerSlotOffsetByHandle',0x8000,i)
    m.ww('DGROUP:EarliestTimerIntervalLow',0xffff);m.ww('DGROUP:EarliestTimerIntervalHigh',0xffff)
    m.ww('DGROUP:NextPitQuantumLow',0xd1eb);m.ww('DGROUP:NextPitQuantumHigh',1)
    m.ww('DGROUP:PreviousInt08Offset',m.off('GAME:FailDosCriticalError'))
    m.ww('DGROUP:PreviousInt08Segment',m.seg('GAME:FailDosCriticalError'))
    s,o=m.address('TIMER:HandleTimerInterrupt')
    m.write(0,0x20,o.to_bytes(2,'little')+s.to_bytes(2,'little'))
    for i in range(2):m.device.schedule(m.seg('C:StopMusicTrack'),m.off('C:StopMusicTrack')+0x95,irq=0,clocks=119275)
CASES.append(Case('native music fade wait actual TIMER callbacks','C:StopMusicTrack',setup=stop_fade,
                  args=(1,),kind='far',out_regs=('AX',)+api.KEEP,flags=0x202,budget=10000000))

# Actual built effects with the AdLib device enabled (including voice allocation).
for routine in ('ThrowCarriedStone','BeginBirdWarning','LaunchBirdTowardPlayer','ReleaseTreeReward'):
    entry=next(c for c in a.CASES if c.routine=='GAME:'+routine)
    def enabled(m,entry=entry):
        entry.setup(m)
        for x in range(8,12):
            for off,value in ((0x28,0),(0x22,0),(0x24,9)):api.desc(m,x,off,value)
        for n,v in [('SoundDeviceBits',1),('ReservedAdlibChannelCount',0),('MainAdlxPlaying',0),
                    ('MusicVoiceCount',0),('AdlxPlaybackGuard',0),('SoundIoDelayMultiplier',1)]:
            m.ww('SOUND:'+n,v)
    CASES.append(replace(entry,setup=enabled,title='enabled sound '+routine,check=None))
for routine,args in [('LoadAdlibChannel',(8,0x401,0x7200,165,1)),
                     ('PlayAdlibEffect',(0x401,0x7200,165,1))]:
    def setup(m):
        api.parser_setup(m,api.adlx(voices=1));m.ww('SOUND:SoundIoDelayMultiplier',1)
        m.ww('SOUND:AdlxPlaybackGuard',0)
    CASES.append(Case('native parsed voice '+routine,'C:'+routine,setup=setup,
                      args=args,kind='far',out_regs=('AX',)+api.KEEP))

# Main -> real password game -> Escape -> game-over/score -> menu -> Q.
def menu_game(m):
    load_suite('menu').composition_fixture(m)
    s,o=m.address('GAME:HandleKeyboardScanInterrupt')
    m.write(0,0x24,o.to_bytes(2,'little')+s.to_bytes(2,'little'))
    m.device.script(0x60,[0x3b,1,0x10])
    m.device.schedule(m.seg('GAME:loc_00E9'),m.off('GAME:loc_00E9'),irq=1)
    m.device.schedule(m.seg('GAME:RunGameFromPassword'),m.off('GAME:RunGameFromPassword')+0x174,irq=1)
    m.device.schedule(m.seg('GAME:loc_00E9'),m.off('GAME:loc_00E9'),irq=1)
    m.ww('DGROUP:WaterSurfaceByteOffset',18000)
CASES.append(Case('main F1 gameplay Escape score menu Q','GAME:RunMainMenuAndAttractLoop',
                  setup=menu_game,regs=dict(DS=DATA_SEG),out_regs=('IF','DF'),budget=100000000))

# Both compaction and restoration of displaced main voices through real OPL.
def compact_voices(m):
    sound(m,reserved=3,playing=1,voices=9)
    api.desc(m,8,0x28,5);api.desc(m,8,0x22,1);api.desc(m,8,0x24,8)
    api.desc(m,9,0x28,5);api.desc(m,9,0x22,2);api.desc(m,9,0x24,6)
CASES.append(Case('native voice compaction and displaced main restore','C:RestoreAdlibVoiceAllocation',
                  setup=compact_voices,args=(8,),kind='far',out_regs=api.KEEP))
def saved_section(m):
    sound(m,reserved=2,playing=1,voices=9)
CASES.append(Case('native scanned voices live and saved routing','C:ApplyScannedMusicEvents',
                  setup=saved_section,kind='far',out_regs=api.KEEP))
def displace_main(m):
    sound(m,reserved=0,playing=1,voices=9)
    api.desc(m,8,0x28,4);api.desc(m,8,0x22,2)
CASES.append(Case('native allocation displaces two main voices','C:StartAdlibTrackChannel',
                  setup=displace_main,args=(8,165),kind='far',out_regs=('AX',)+api.KEEP))
# Exercise the interpreter -> handler edges, not only handler -> interpreter tails.
for which in ('Main','Effect'):
    for opcode,payload in ((0x20,b''),(0x50,b''),(0x71,b'\x00')):
        def setup(m,which=which,opcode=opcode,payload=payload):
            opl.base(m)
            m.ww('SOUND:CurrentAdlxSlot',12 if which=='Main' else 8)
            m.ww('SOUND:CurrentAdlxRecordOffset',m.off('SOUND:AudioChannelStates')+8*42)
            m.ww('SOUND:AudioChannelStates',0x100,8*42+0x24)
            m.write(0x9000,0x100,bytes([opcode])+payload+b'\x81')
        CASES.append(Case(f'{which} dispatch native opcode {opcode:02x}','SOUND:Run'+which+'AdlxEvents',
                          setup=setup,regs=dict(ES=0x9000,DI=0x100),kind='far',out_regs=opl.REGS))
