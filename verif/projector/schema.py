"""Explicit test layout bindings. Unknown aliases are not assigned an owner.

All addresses below are generated from the frozen historical symbol header.
The GameWorld header itself contains no historical address or register model.
"""
import json
from pathlib import Path
import re

OWNERS=['audio','timer','actors','players','enemies','items','weather','configuration',
        'session','input','video','front_end','random','platforms']
MODULES=['DGROUP','GAME','SOUND','TIMER','C','CDATA']


def generate(frozen, folder):
    header=(frozen/'c/ugh_sym.h').read_text()
    load=int(re.search(r'#define UGH_LOAD (0x[\da-fA-F]+)',header)[1],16)
    defs={}
    for name,expr in re.findall(r'^#define\s+(UGH_[SO]_\w+)\s+([^\n]+)',header,re.M):
        defs[name]=eval(re.sub(r'(?<=[0-9a-fA-F])[uUlL]+\b','',expr),{'__builtins__':{}},{'UGH_LOAD':load})
    def sym(name,module=None):
        for mod in ([module] if module else MODULES):
            off=defs.get('UGH_O_'+mod+'_'+name);seg=defs.get('UGH_S_'+mod+'_'+name)
            if off is not None and seg is not None:return seg*16+off
        return None
    bindings=[];claimed={};skipped=[];missing=[]
    def add(name,field,width=2,count=1,module=None,kind=0,domain=0,shift=0,native_width=None,address=None,owner=None):
        address=sym(name,module) if address is None else address
        if address is None:missing.append(dict(name=name,field=field));return
        owner=owner or field.split('.')[0]
        if owner=='timers':owner='timer'
        owner=OWNERS.index(owner)
        for i in range(count):
            at=address+width*i;f=field+(f'[{i}]' if count>1 else '')
            overlap=sorted({claimed[a] for a in range(at,at+width) if a in claimed})
            if overlap:
                skipped.append(dict(name=name,field=f,address=at,width=width,
                    existing=[bindings[x]['field'] for x in overlap],reason='physical overlap; canonical binding retained, no second owner'))
                continue
            b=dict(name=name,field=f,address=at,width=width,native_width=native_width or width,
                   kind=kind,domain=domain,shift=shift,owner=owner)
            ident=len(bindings);bindings.append(b)
            for a in range(at,at+width):claimed[a]=ident
    def s(name,field,**kw):add(name,field,**kw)
    def identity(name,field,count=1,module=None,address=None,domain=3,owner=None):
        add(name,field,count=count,module=module,address=address,kind=1,domain=domain,owner=owner)

    # Exactly the canonical audio record/voice views; record12 is not copied again.
    channels=sym('AudioChannelStates','SOUND')
    offsets={'age':(0,4),'repeats':(4,2),'length':(10,2),'sample_mode':(12,2),
        'sample_rate':(14,2),'sample_half_length':(20,2),'reserved_word':(22,2),
        'sample_selector':(24,2),'sample_accumulator':(26,2),'volume':(28,2),
        'deadline':(30,4),'voice_count':(34,2),'first_voice':(36,2),'step_q8':(38,2),'control':(40,2)}
    for i in range(13):
        for f,(off,w) in offsets.items():s('AudioChannelStates',f'audio.channels[{i}].{f}',width=w,address=channels+42*i+off)
        for f,off in [('start',6),('cursor',16)]:
            s('AudioChannelStates',f'audio.channels[{i}].{f}.index',address=channels+42*i+off)
            identity('AudioChannelStates',f'audio.channels[{i}].{f}.bank',address=channels+42*i+off+2,domain=4)
    for source,target in [('AdlibVoiceStates','live'),('SavedAdlibVoiceStates','displaced'),('ScannedAdlibVoiceStates','scanned')]:
        base=sym(source,'SOUND')
        for i in range(9):
            s(source,f'audio.{target}[{i}].instrument',width=1,count=12,address=base+20*i)
            for f,off in [('volume',12),('gain',14),('owner',16),('frequency',18)]:s(source,f'audio.{target}[{i}].{f}',address=base+20*i+off)
    s('AdlibOperatorOffsets','audio.operator_index',width=1,count=9,module='SOUND')
    for name,field,width in [
        ('AdlxPlaybackGuard','guard',2),('MusicTicksPerUnit','rate',2),('AdlxTickCount','ticks',4),
        ('MainAdlxTimeOrigin','origin',4),('ScannedMusicClockTicks','scanned_ticks',4),
        ('MainAdlxPlaying','playing',2),('MainAdlxSectionLoopEnabled','section_loop',2),
        ('MusicFadeStep','fade_step',2),('MusicFadeDuration','fade_duration',2),
        ('MusicFadeStartVolume','fade_start',2),('MusicFadeTargetVolume','fade_target',2),
        ('MusicFadeScheduled','fade_scheduled',2),('MusicFadeTimerHandle','fade_handle',2),
        ('AdlxTimerPeriod','timer_period',2),('AdlxPlaybackTimerHandle','timer_handle',2),
        ('ReservedAdlibChannelCount','reserved_voices',2),('CurrentAdlxSlot','current_channel',2),
        ('MusicTrackVolume','track_volume',2),('SoundDeviceBits','devices',2),
        ('ActiveSampleVoiceCount','active_sample_voices',2),('SoundIoDelayMultiplier','delay_multiplier',2),
        ('CalibrationLoopRemainder','calibration_remainder',2),('CurrentAdlxRecordOffset','record_offset',2),
        ('AdlibInitAttempted','init_attempted',1),('SampleMixerBusy','mixer_busy',2),('DspBasePort','dsp_port',2),
        ('DspInterruptVector','dsp_vector',2),('ActiveSampleVoiceMask','sample_mask',2),('SoundBankLength','bank_length',4)]:
        s(name,'audio.'+field,width=width,module='SOUND')
    for name,field in [('FirstScannedEvent','section_start'),('MainAdlxSectionEnd','section_end')]:
        base=sym(name,'SOUND');s(name,'audio.'+field+'.index',address=base)
        identity(name,'audio.'+field+'.bank',address=base+2,domain=4)
    for name,field in [('AdlibInstrumentMap','instrument_map'),('SoundBankBase','bank')]:
        base=sym(name,'SOUND');s(name,'audio.'+field+'.index',address=base)
        identity(name,'audio.'+field+'.bank',address=base+2,domain=4)
    identity('PreviousCalibrationTimerVector','audio.previous_calibration_offset',domain=5)
    identity('PreviousCalibrationTimerSegment','audio.previous_calibration_bank',domain=4)
    for name,f in [('SoundSystemInitialized','initialized'),('SoundSystemShutdown','shutdown_latch')]:s(name,'audio.'+f,module='C')

    for i in range(16):
        for source,field,shift in [('TimerIntervalLowBySlot','interval',0),('TimerIntervalHighBySlot','interval',16),
            ('TimerRemainingLowBySlot','remaining',0),('TimerRemainingHighBySlot','remaining',16)]:
            s(source,f'timers.slots[{i}].{field}',address=sym(source)+2*i,native_width=4,shift=shift)
        for source,f in [('TimerCallbackDueBySlot','due'),('TimerHandleBySlot','handle')]:s(source,f'timers.slots[{i}].{f}',address=sym(source)+2*i)
        identity('TimerCallbackOffsetBySlot',f'timers.slots[{i}].target_offset',address=sym('TimerCallbackOffsetBySlot')+4*i,domain=5)
        identity('TimerCallbackSegmentBySlot',f'timers.slots[{i}].target_bank',address=sym('TimerCallbackSegmentBySlot')+4*i,domain=4)
    for name,f,w in [('LastActiveTimerSlotOffset','last_offset',2),('TimerInterruptInstalled','installed',2),
        ('ProgrammedPitDivisor','divisor',2),('NextPitQuantumLow','quantum',4),('EarliestTimerIntervalLow','earliest',4)]:s(name,'timers.'+f,width=w)
    s('TimerSlotOffsetByHandle','timers.by_handle',count=16)
    identity('PreviousInt08Offset','timers.previous_offset',domain=5)
    identity('PreviousInt08Segment','timers.previous_bank',domain=4)

    arrays={
      'actors':(16,{
        'descriptor':'ActorDescriptors','callback_or_cursor':'ActorUpdateOrScriptCursor','journey':'ActorJourneyCursors',
        'overlay':'ActorOverlayOrScriptCallbacks','platform_or_done':'ActorPlatformOrScriptDone',
        'source_platform':'ActorInitialPlatformIndices','destination_platform':'ActorDestinationPlatforms',
        'source_index':'ActorSourcePlatformByteIndices','destination_index':'ActorDestinationPlatformByteIndices',
        'x32':'ActorX32','y32':'ActorY32','pixel_x':'ActorPixelX','pixel_y':'ActorPixelY',
        'previous_x':'ActorPreviousDrawX','previous_y':'ActorPreviousDrawY','sprite':'ActorSpriteIds',
        'erase_sprite':'ActorEraseSprite','erase_overlay':'ActorEraseOverlaySprite',
        'animation_offset':'ActorAnimationByteOffsets','animation_countdown':'ActorAnimationCountdowns',
        'phase_or_demo_cursor':'ActorPhaseOrDemoLoopCursor','motion_wait_or_demo_repeats':'ActorMotionWaitOrDemoRepeats',
        'vertical_or_demo_period':'ActorVerticalOrDemoPeriod','quick_delivery_ticks':'PassengerQuickDeliveryCountdowns'}),
      'players':(2,{
        'x32':'PlayerX32','y32':'PlayerY32','pixel_x':'PlayerPixelX','pixel_y':'PlayerYPixels',
        'cached_x':'PlayerCachedPixelX','cached_y':'PlayerCachedPixelY','cached_sprite':'PlayerCachedSpriteIds',
        'vx':'PlayerHorizontalVelocities','vy':'PlayerVerticalVelocities','platform':'PlayerPlatformIndices',
        'sprite':'PlayerSpriteIds','impact':'PlayerImpactMagnitude','impact_limit':'PlayerImpactLimits',
        'thrust':'PlayerThrustAnimationRate','carried':'PlayerCarriedKinds','destination':'PlayerDestinationIcons',
        'fare':'PlayerPassengerFares','minimum_fare':'PlayerMinimumFares','up':'PlayerUpInput','down':'PlayerDownInput',
        'left':'PlayerLeftInput','right':'PlayerRightInput','action':'PlayerActionInput',
        'animation_countdown':'PlayerAnimationCountdowns','cycle_start':'PlayerAnimationCycleStarts','cycle_end':'PlayerAnimationCycleEnds'}),
      'enemies':(5,{
        'descriptor':'EnemyDescriptors','callback':'EnemyStateCallbacks','animation_or_drop':'EnemyAnimationOrDropLists',
        'platform':'EnemyPlatformIndices','x32':'EnemyX32','y32':'EnemyY32','draw_x':'EnemyDrawX','draw_y':'EnemyDrawY',
        'previous_x':'EnemyPreviousDrawX','previous_y':'EnemyPreviousDrawY','sprite':'EnemySpriteIds',
        'erase_sprite':'EnemyEraseSprite','animation_offset':'EnemyAnimationByteOffsets',
        'animation_countdown':'EnemyAnimationCountdowns','direction':'EnemyDirectionOrTargetPlayer',
        'speed':'EnemyHorizontalSpeeds','delay':'EnemyInitialDelays','counter':'EnemyStateCounters','sound_handle':'EnemyFlightSoundHandles'}),
      'items':(12,{
        'descriptor':'FallingItemDescriptors','callback':'FallingItemCallbacks','x32':'FallingItemX','y32':'FallingItemY',
        'draw_x':'FallingItemDrawX','draw_y':'FallingItemDrawY','previous_x':'FallingItemPreviousDrawX',
        'previous_y':'FallingItemPreviousDrawY','sprite':'FallingItemSprites','erase_sprite':'FallingItemEraseSprite',
        'motion_or_lifetime':'FallingItemMotionOrLifetime','vertical_step':'FallingItemVerticalStep'})}
    idfields={'descriptor','callback','callback_or_cursor','journey','overlay','animation_or_drop'}
    for owner,(count,fields) in arrays.items():
        for field,name in fields.items():
            if field in idfields:identity(name,owner+'.'+field,count=count,domain=5 if field in ['callback','callback_or_cursor'] else 3)
            else:s(name,owner+'.'+field,count=count)
    for n,f in [('PlatformLeftEdges','left'),('PlatformRightEdges','right'),('PlatformHeights','height'),
        ('PlatformArrivalPointsX','arrival'),('PlatformWaitingPointsX','waiting'),('PlatformSpawnX','spawn'),
        ('PlatformDestinationIcons','icon'),('PlatformActorOccupants','occupant')]:s(n,'platforms.'+f,count=10)
    for n,f,w in [('WaterY32','fixed_y',2),('WaterYPixels','surface_y',2),('PreviousWaterSurfaceY','previous_y',2),
        ('WaterSurfaceByteOffset','byte_offset',2),('WaterSurfaceFrame','frame',2),('WaterStepPhase','phase',1),
        ('WaterSurfaceFrameCountdown','countdown',1),('WaterRestorePending','pending',1),('LevelRainDirection','rain_direction',1)]:s(n,'weather.'+f,width=w)
    for n,f in [('RainParticleOffsets','particle'),('RainPreviousOffsets','previous_particle'),('RainParticleXModuloFour','modulo_four')]:s(n,'weather.'+f,count=193)
    for n,f in [('PlayerCount','players'),('PlayerArrayBytes','player_bytes')]:s(n,'configuration.'+f)
    s('PlayerOneControlMode','configuration.control_mode',count=2)
    for n,f,w in [('CurrentLevelIndex','level',2),('LevelTimer','timer',2),('ScreenFadeLevel','fade_level',2),
        ('ScreenFadeStep','fade_step',2),('LivesRemaining','lives',1),('ScoreMultiplier','multiplier',1),('LevelCompletionMarker','completion',1)]:s(n,'session.'+f,width=w)
    s('ScoreLowWord','session.score',native_width=4);s('ScoreHighWord','session.score',native_width=4,shift=16)
    s('CurrentLevelRecord','session.level_record',count=13)
    s('Data_264C','session.tile_map',width=1,count=320)
    for n,f in [('LatestInterruptScanCode','latest'),('CurrentKeyboardScanCode','current'),
        ('PreviousPolledScanCode','previous'),('KeyboardScanCodeChangeBits','change'),
        ('KeyboardSequenceIndex','sequence_index'),('JoystickEnabledAxisMask','enabled_axes')]:s(n,'input.'+f,width=1)
    s('JoystickSampleLoopLimit','input.sample_limit')
    for n,f in [('JoystickPresentFlags','present'),('JoystickButtonBits','buttons'),('JoystickLeftThresholds','left'),
        ('JoystickRightThresholds','right'),('JoystickUpThresholds','up'),('JoystickDownThresholds','down')]:s(n,'input.'+f,count=2)
    for n,f in [('DrawPagePointer','draw'),('DisplayedVgaPagePointer','displayed'),('BackgroundPagePointer','background'),('FixedVgaPagePointer','fixed')]:
        base=sym(n,'GAME');s(n,'video.'+f+'.index',address=base)
        identity(n,'video.'+f+'.bank',address=base+2,domain=4)
    for n,f in [('PlayfieldHeight','height'),('VgaPlaneCopyByteCount','copy_bytes')]:s(n,'video.'+f)
    for n,f in [('BaseRgbPalette','base_palette'),('FadedRgbPalette','faded_palette')]:s(n,'video.'+f,width=1,count=768)
    for n,f,count in [('HighScoreRows','scores',107),('PasswordEditBuffer','password',20),('HighScoreNameEntry','name',13)]:s(n,'front_end.'+f,width=1,count=count)
    s('HighScoreRowStride','front_end.stride',width=1);s('HighScoreFileHandle','front_end.file_handle')
    s('RandomStateStorage','random',count=4)

    # Do not choose a semantic owner merely because two requested views overlap.
    # The level descriptor's documented weather subfields are an explicit view;
    # other collisions remain unclassified bytes in the write journal. Header
    # capacities are not evidence that adjacent legacy arrays are independent.
    ambiguous=set();ambiguous_fields=[]
    by_field={b['field']:b for b in bindings}
    for row in skipped:
        if row['name']=='CurrentLevelRecord':
            row['reason']='documented encompassing level-record view; canonical weather subfield retained, no second owner'
            continue
        row['reason']='overlapping requested views: neither is assigned these bytes; retain in unclassified journal'
        ambiguous.update(range(row['address'],row['address']+row['width']))
        for field in row['existing']:
            b=by_field[field];ambiguous.update(range(b['address'],b['address']+b['width']))
    kept=[]
    for b in bindings:
        if any(a in ambiguous for a in range(b['address'],b['address']+b['width'])):ambiguous_fields.append(b)
        else:kept.append(b)
    bindings=kept;claimed={a:i for i,b in enumerate(bindings) for a in range(b['address'],b['address']+b['width'])}

    # Registered exact word identities. Domain5 is deliberately a word-fragment
    # registry, not a claim that every raw word denotes a valid executable target.
    registered={}
    for mod,domain in [('GAME',0),('SOUND',1),('TIMER',2),('DGROUP',3)]:
        for key,value in sorted(defs.items()):
            if key.startswith('UGH_O_'+mod+'_'):
                registered.setdefault((domain,value),key)
                if mod in ['GAME','SOUND','TIMER']:registered.setdefault((5,value),key)
    for key,value in sorted(defs.items()):
        if key.startswith('UGH_S_'):registered.setdefault((4,value),key)
    for value,label in [(0,'null'),(0xa000,'VGA aperture'),(0xf000,'fixture BIOS')]:registered.setdefault((4,value),label)
    identities=[dict(domain=dom,word=word,label=label) for (dom,word),label in sorted(registered.items())]
    generated=['static const Binding bindings[]={']
    for b in bindings:
        generated.append('{'+','.join(map(str,[b['address']]))+',offsetof(GameWorld,'+b['field']+'),'+','.join(map(str,[b['width'],b['native_width'],b['shift'],b['kind'],b['domain'],b['owner']]))+','+json.dumps(b['field'])+'},')
    generated+=['};','static IdentityEntry identities[]={{0,0,"unresolved"},']
    generated += ['{'+str(x['domain'])+','+str(x['word'])+','+json.dumps(x['label'])+'},' for x in identities]
    generated+=['};','static const char *owner_names[]={'+','.join(map(json.dumps,OWNERS))+'};']
    (folder/'bindings.inc').write_text('\n'.join(generated)+'\n')
    # Byte-shape equivalence is checked by _Static_assert for each service field.
    groups={
      'video':(1,['seq_index','map_mask','gc_index','read_map','gc','seq','crtc','attr','dac','crtc_index','attr_index','attr_phase','dac_index','dac_component']),
      'audio':(2,{'opl_index':'address','opl':'registers'}),
      'bus':(4,['pic_mask','dma_flip','dma_mode','dma_mask','dma_page','dma_address','dma_count','pit_divisor','pit_phase','pit_command','clocks','irq_count','irq_cursor','irqs']),
      'input':(8,{'script_count':'count','scripts':'scripts'}),
      'files':(16,{'files':'files','handles':'handles','io_limit':'io_limit','dos_error':'error','dos_error_skip':'error_skip'}),
      'lifetime':(32,{'video_mode':'mode','video_page':'page','video_columns':'columns','exit_code':'exit_code','exited':'exited'}),
      '':(64,{'error':'error'})}
    services=[]
    for group,(mask,members) in groups.items():
        for source,target in (members.items() if isinstance(members,dict) else [(n,n) for n in members]):
            services.append(dict(source=source,target=(group+'.' if group else '')+target,group=mask))
    services += [dict(source=n,target='video.'+n,group=128) for n in ['plane','latch']]
    generated=['static const ServiceBinding service_bindings[]={']
    for b in services:
        generated.append('{offsetof(Devices,'+b['source']+'),offsetof(ServiceState,'+b['target']+'),sizeof(((Devices*)0)->'+b['source']+'),'+str(b['group'])+','+json.dumps(b['target'])+'},')
    generated+=['};']
    for b in services:generated.append('_Static_assert(sizeof(((Devices*)0)->'+b['source']+')==sizeof(((ServiceState*)0)->'+b['target']+'),"service field shape");')
    (folder/'services.inc').write_text('\n'.join(generated)+'\n')
    model=json.loads((frozen/'metadata/program-model.json').read_text())
    coverage=[]
    for name,description in model['variables'].items():
        addresses=set() # no nearest-label guessing
        for mod in MODULES:
            a=sym(name,mod)
            if a is not None:addresses.add(a)
        canonical=[bindings[claimed[a]] for a in sorted(addresses) if a in claimed]
        coverage.append(dict(name=name,status='typed canonical/physical alias' if canonical else 'baseline or unclassified write journal',
            bindings=sorted({b['field'] for b in canonical}),writers=description.get('writers',[]),
            model_complete=description.get('complete',False),address_resolution='exact symbol only' if addresses else 'unresolved; no nearest-label assignment'))
    manifest=dict(bindings=bindings,identities=identities,service_bindings=services,skipped_overlaps=skipped,
        unclassified_overlapping_bindings=ambiguous_fields,
        missing_symbols=missing,model_coverage=coverage,owners=OWNERS,
        caveat='Named model coverage means the exact named cell starts in a declared typed binding; array extents are the explicit schema extents, not an unrestricted alias theorem.')
    (folder/'schema.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
