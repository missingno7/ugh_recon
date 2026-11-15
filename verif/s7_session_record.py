"""Observation-only session projection. No generated value feeds GameWorld."""
import json
import re
import cgen


def projection(full=False):
    mz, symbols = cgen.read_symbols()
    load = cgen.LOAD * 16
    graph = json.loads((cgen.ROOT / 'metadata/object-identities.json').read_text())

    def a(name, module='DGROUP'):
        return load + symbols[module + ':' + name]['linear']

    ids = '\n'.join('case %d:return %d;' % (r['view'], r['word']) for r in graph['resources'])
    roles = {l['callback']['role']: l['word'] for l in graph['links']
             if l['kind'] == 'callback' and l['callback']['family'] == 'actor'}
    actors = '\n'.join('case %s:return %d;' % pair for pair in roles.items())
    enemies = [('H_TREE_BEGIN', 'InitializeFruitTreeAnimation'), ('H_BIRD_DELAY', 'BeginBirdDelay'),
               ('H_DINO_BEGIN', 'InitializeDinoAnimation'), ('H_TRIO_PATROL_BEGIN', 'BeginTriopterusPatrol')]
    enemy_roles = '\n'.join('case %s:return %d;' % (role, symbols['GAME:' + name]['offset']) for role, name in enemies)
    helpers = '''static uint16_t origin(ObjectResourceIdentity id){
 if(id.kind==OBJECT_RESOURCE_UNSUPPORTED)return 0;
 switch(id.view.index){IDS default:exit(9);}}
static uint16_t actor_callback(ObjectCallbackIdentity id){
 if(id.kind==OBJECT_CALLBACK_UNSUPPORTED)return 0;
 if(id.kind!=OBJECT_CALLBACK_ACTOR)return 0;
 switch(id.actor){ACTORS default:exit(9);}}
static uint16_t enemy_callback(ObjectCallbackIdentity id){
 if(id.kind==OBJECT_CALLBACK_UNSUPPORTED)return 0;
 if(id.kind!=OBJECT_CALLBACK_ENEMY)exit(9);
 switch(id.enemy){ENEMIES default:exit(9);}}
'''.replace('IDS', ids).replace('ACTORS', actors).replace('ENEMIES', enemy_roles)
    lines, ranges = [], []

    def field(name, expr, width=2, module='DGROUP'):
        at = a(name, module)
        lines.append('put(%d,%s,%d);' % (at, expr, width))
        ranges.append((at, width, name))

    # Physical field mapping is independent of the constructors' default table.
    bridge = (cgen.ROOT / 'native/bridge/player_world_bridge.c').read_text()
    for name, member in re.findall(r' WORD\((\w+),(\w+)\)', bridge):
        if name=='n':continue
        for i in range(2):
            at = a(name) + 2 * i
            lines.append('put(%d,w->session.players.player[%d].%s,2);' % (at, i, member))
            ranges.append((at, 2, name + str(i)))
    platform_fields = [('PlatformLeftEdges', 'left'), ('PlatformRightEdges', 'right'), ('PlatformHeights', 'height'),
                       ('PlatformArrivalPointsX', 'arrival'), ('PlatformWaitingPointsX', 'wait'), ('PlatformSpawnX', 'spawn'),
                       ('PlatformDestinationIcons', 'icon'), ('PlatformActorOccupants', 'occupant')]
    for name, member in platform_fields:
        for i in range(10):
            field_expr = 'w->session.platforms.slot[%d].%s' % (i, member)
            at = a(name) + 2 * i
            lines.append('put(%d,%s,2);' % (at, field_expr)); ranges.append((at, 2, name + str(i)))
    actor_fields = [('ActorInitialPlatformIndices', 'initial_platform'), ('ActorPlatformOrScriptDone', 'source_or_done'),
                    ('ActorDestinationPlatforms', 'destination_platform'), ('ActorSourcePlatformByteIndices', 'source_byte_index'),
                    ('ActorDestinationPlatformByteIndices', 'destination_byte_index'), ('ActorMotionWaitOrDemoRepeats', 'delay_or_repeat_word'),
                    ('ActorX32', 'position.x32'), ('ActorY32', 'position.y32'), ('ActorPixelX', 'history.pixel_x'),
                    ('ActorPreviousDrawX', 'history.previous_x'), ('ActorPixelY', 'history.pixel_y'), ('ActorPreviousDrawY', 'history.previous_y'),
                    ('ActorAnimationByteOffsets', 'animation.byte_offset'), ('ActorAnimationCountdowns', 'animation.countdown'),
                    ('ActorSpriteIds', 'sprite'), ('ActorEraseSprite', 'history.erase_sprite'), ('ActorOverlayOrScriptCallbacks', 'overlay_sprite'),
                    ('ActorEraseOverlaySprite', 'history.erase_overlay_sprite'), ('ActorVerticalOrDemoPeriod', 'motion_or_period_word'),
                    ('PassengerQuickDeliveryCountdowns', 'quick_delivery_ticks')]
    for i in range(16):
        for name, member in actor_fields:
            at = a(name) + 2 * i
            expr='w->actors.slot[%d].%s'%(i,member)
            if full and member=='overlay_sprite':expr='w->actors.slot[%d].demo?effect_word(w->actors.slot[%d].callback):%s'%(i,i,expr)
            lines.append('put(%d,%s,2);' % (at, expr)); ranges.append((at, 2, name + str(i)))
        for name, expr in [('ActorDescriptors', 'w->session.actor_end[%d]?65535:origin(w->actors.slot[%d].descriptor)' % (i, i)),
                           ('ActorJourneyCursors', 'origin(w->actors.slot[%d].journey)+w->actors.slot[%d].journey.position' % (i, i)),
                           ('ActorUpdateOrScriptCursor', 'actor_callback(w->actors.slot[%d].callback)' % i),
                           ('ActorPhaseOrDemoLoopCursor', 'w->actors.slot[%d].loop_cursor' % i)]:
            at = a(name) + 2 * i
            if full and name=='ActorUpdateOrScriptCursor':
                expr='w->actors.slot[%d].cursor==65535?65535:w->actors.slot[%d].demo?(origin(w->actors.slot[%d].script)+8+w->actors.slot[%d].cursor):(%s)'%(i,i,i,i,expr)
            if full and name=='ActorPhaseOrDemoLoopCursor':
                expr='w->actors.slot[%d].loop_script.kind?origin(w->actors.slot[%d].loop_script)+8+w->actors.slot[%d].loop_cursor:(%s)'%(i,i,i,expr)
            lines.append('put(%d,%s,2);' % (at, expr)); ranges.append((at, 2, name + str(i)))
    enemy_fields = [('EnemyPlatformIndices', 'platform'), ('EnemyX32', 'x32'), ('EnemyY32', 'y32'),
                    ('EnemyInitialDelays', 'initial_delay'), ('EnemyHorizontalSpeeds', 'speed'), ('EnemyStateCounters', 'counter'),
                    ('EnemyDrawX', 'draw_x'), ('EnemyPreviousDrawX', 'previous_x'), ('EnemyDrawY', 'draw_y'), ('EnemyPreviousDrawY', 'previous_y'),
                    ('EnemyAnimationByteOffsets', 'animation_offset'), ('EnemyAnimationCountdowns', 'countdown'), ('EnemySpriteIds', 'sprite'),
                    ('EnemyEraseSprite', 'erase_sprite'), ('EnemyDirectionOrTargetPlayer', 'direction_or_target_word'), ('EnemyFlightSoundHandles', 'sound_handle_word')]
    for i in range(5):
        for name, member in enemy_fields:
            at = a(name) + 2 * i
            lines.append('put(%d,w->enemies.slot[%d].%s,2);' % (at, i, member)); ranges.append((at, 2, name + str(i)))
        for name, expr in [('EnemyDescriptors', 'w->session.enemy_end[%d]?65535:origin(w->session.enemy_descriptor[%d])' % (i, i)),
                           ('EnemyAnimationOrDropLists', 'origin(w->session.enemy_list[%d])+w->session.enemy_list[%d].position' % (i, i)),
                           ('EnemyStateCallbacks', 'enemy_callback(w->session.enemy_callback[%d])' % i)]:
            at = a(name) + 2 * i
            lines.append('put(%d,%s,2);' % (at, expr)); ranges.append((at, 2, name + str(i)))
    for i in range(193):
        for name, member in [('RainParticleOffsets', 'position'), ('RainPreviousOffsets', 'previous'), ('RainParticleXModuloFour', 'modulo')]:
            at = a(name) + 2 * i
            lines.append('put(%d,w->presentation.weather.rain[%d].%s,2);' % (at, i, member)); ranges.append((at, 2, name + str(i)))
    for name, expr, width, module in [('CoordinateScaleScratch', 'w->session.scale_scratch', 2, 'DGROUP'),
                                    ('RendererScratchWord', 'w->front_data.renderer_water', 2, 'GAME'),
                                    ('WaterYPixels', 'w->run.water_y', 2, 'DGROUP'),
                                    ('PreviousWaterSurfaceY', 'w->presentation.weather.previous_y', 2, 'DGROUP'),
                                    ('HudCachedPlayerOneIconState', 'w->presentation.hud.icons[0]', 2, 'DGROUP'),
                                    ('HudCachedPlayerTwoIconState', 'w->presentation.hud.icons[1]', 2, 'DGROUP'),
                                    ('HudFareClearPending', 'w->presentation.hud.fare_pending', 1, 'DGROUP')]:
        field(name, expr, width, module)
    for i in range(4):
        at = a('RandomStateStorage', 'GAME') + 2 * i
        lines.append('put(%d,w->random.word[%d],2);' % (at, i)); ranges.append((at, 2, 'random' + str(i)))
    for name, member, size in [('Data_264C', 'run.tiles', 320)]:
        lines.append('memcpy(observation+%d,w->%s,%d);' % (a(name), member, size)); ranges.append((a(name), size, name))
    # Scalar record only. Original DATA pointer transports are observation
    # metadata in full-frame recording, never production scalar stores.
    for name, member, width in [('CurrentLevelRecord', 'map.value', 2), ('RemainingPassengerJourneys', 'journeys', 1),
                               ('LevelRainDirection', 'rain', 1), ('LevelPlayerOneStartX', 'player_start[0][0]', 2),
                               ('LevelPlayerOneStartY', 'player_start[0][1]', 2), ('LevelPlayerTwoStartX', 'player_start[1][0]', 2),
                               ('LevelPlayerTwoStartY', 'player_start[1][1]', 2), ('WaterY32', 'water_fixed', 2), ('WaterSurfaceStep', 'water_step', 2)]:
        field(name, 'w->run.record.' + member, width)
    if full:
        for name,member,width in [('CurrentLevelIndex','run.level',2),('LivesRemaining','run.lives',1),
                                  ('ScoreMultiplier','run.multiplier',1),('ScoreLowWord','run.score',4),
                                  ('LevelTimer','run.timer',2),('LevelCompletionMarker','run.completion',1)]:field(name,'w->'+member,width)
        bridge=(cgen.ROOT/'native/bridge/presentation_world_bridge.c').read_text()
        for macro,name,member in re.findall(r'\b(WORD|BYTE)\((\w+),([\w.]+)\)',bridge):
            if name=='n':continue
            field(name,'w->presentation.'+member,1 if macro=='BYTE' else 2)
        for i in range(9):
            lines.append('put(%d,w->presentation.hud.layout_x[%d],2);'%(a('HudLivesX')+2*i,i))
        for i in range(2):lines.append('put(%d,w->presentation.hud.score_words[%d],2);'%(a('HudCachedScoreLow')+2*i,i))
        lines.append('put(%d,w->run.record.reserved_before_text,1);put(%d,w->run.record.reserved_tail,1);'%(a('CurrentLevelRecord')+9,a('CurrentLevelRecord')+25))
        # The packed current record's pointer lanes are observation transport
        # only. Lookup is keyed by the retained typed level, never executable.
        import dataprobe
        levels=list({r['record']:r for r in dataprobe.levels(mz)[1]}.values())
        cases=[]
        for r in levels:
            at=cgen.FRAMES['DGROUP']*16+int(r['record'],16)
            raw=mz.image[at:at+26]
            cases.append('case %d:%s break;'%(int(r['record'],16),''.join('put(%d,%d,2);'%(a('CurrentLevelRecord')+i,int.from_bytes(raw[i:i+2],'little')) for i in [2,4,6,10])))
        # Resource offsets are not used in game code; this switch is confined
        # to the separately linked historical observer.
        orders=dataprobe.levels(mz)[1]
        tables=[]
        for players in [1,2]:tables.append('{'+','.join(str(int(r['record'],16)) for r in orders if r['players']==players)+'}')
        helpers+='static const uint16_t record_origins[2][81]={'+','.join(tables)+'};\n'
        lines.append('if(w->session.level){unsigned origin_record=record_origins[w->run.configuration.players-1][(uint16_t)(w->run.level*2u)/2u];switch(origin_record){'+''.join(cases)+'default:exit(9);}put(%d,0,2);}'%a('Data_27A0'))
    # A fault in the observer must be caught independently of constructor code.
    lines += ['#ifdef S7_SESSION_MISS_SECOND_PLAYER', 'put(%d,0,2);' % (a('PlayerX32') + 2), '#endif']
    return helpers, '\n'.join(lines), ranges
