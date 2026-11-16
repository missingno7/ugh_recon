"""Build-time level/resource identity extraction; emits DATA views and enums.

Executable words are read only here. The production tables contain no original
descriptor or callback words, address maps, observation bytes or RAM fixtures.
"""
import json
import struct
from pathlib import Path
import cgen
import dataprobe

ROOT = Path(__file__).resolve().parents[1]


def generate(rows, symbols):
    mz, _ = cgen.read_symbols()
    graph = json.loads((ROOT / 'metadata/object-identities.json').read_text())
    world = json.loads((ROOT / 'metadata/resource-world.json').read_text())
    resources = graph['resources']
    _, orders = dataprobe.levels(mz)
    base = cgen.FRAMES['DGROUP'] * 16

    def word(at):
        return struct.unpack_from('<H', mz.image, at)[0]

    def view(at, size):
        choices = [r for r in rows if r['image_start'] <= at and at + size <= r['image_start'] + r['size']]
        if not choices:
            raise ValueError('session DATA span outside resource allocation')
        r = min(choices, key=lambda r: r['size'])
        return '{UINT64_C(%d),%d,%d}' % (r['id'], at - r['image_start'], size)

    def identity(raw, kind):
        r = next(r for r in resources if r['kind'] == kind and raw in [r['word'] + p for p in r['positions']])
        return '{%s,{%d},%d}' % (kind, r['view'], raw - r['word']), r['view']

    levels = list({r['record']: r for r in orders}.values())
    lines = ['/* Generated shipped DATA identities. No executable coordinates. */',
             'static const SessionLevelSpec session_levels[]={']
    for r in levels:
        at = base + int(r['record'], 16)
        spans = {kind: view(base + start, end - start) for kind, start, end in r['spans']}
        actors = []
        for descriptor, platform, journey in r['actors']:
            desc, token = identity(descriptor, 'OBJECT_ACTOR_DESCRIPTOR')
            # Stone's ignored journey payload is zero, not an itinerary.
            leg = identity(journey, 'OBJECT_JOURNEY')[0] if journey else '{0}'
            stone = descriptor == symbols['DGROUP:Data_78DC']['offset']
            link = next(l for l in graph['links'] if l['source'] == token and l['member'] == (16 if stone else 8))
            assert link['kind'] == 'callback' and link['callback']['family'] == 'actor'
            actors.append('{%s,%s,{.kind=OBJECT_CALLBACK_ACTOR,.actor=%s},%s}' %
                          (desc, leg, link['callback']['role'], 'LOAD_STONE' if stone else 'LOAD_ORDINARY'))
        enemies = []
        kinds = {'Data_7630': ('LOAD_BIRD', 'H_BIRD_DELAY'), 'Data_766C': ('LOAD_TRIOPTERUS', 'H_TRIO_PATROL_BEGIN'),
                 'Data_76A8': ('LOAD_DINO', 'H_DINO_BEGIN'), 'Data_76E4': ('LOAD_TREE', 'H_TREE_BEGIN')}
        for entry in r['enemies']:
            desc, _ = identity(entry[0], 'OBJECT_ENEMY_DESCRIPTOR')
            kind, callback = next(v for name, v in kinds.items() if symbols['DGROUP:' + name]['offset'] == entry[0])
            drop = identity(entry[2], 'OBJECT_DROP_LIST')[0] if kind == 'LOAD_TREE' else '{0}'
            enemies.append('{%s,%s,{.kind=OBJECT_CALLBACK_ENEMY,.enemy=%s},%s}' % (desc, drop, callback, kind))
        lines.append('{%s,%s,%s,%s,%s,{%s},{%s},%d,%d},' %
                     (view(at, 26), spans['platforms'], spans['actors'], spans['enemies'], spans['text'],
                      ','.join(actors) or '{.kind=LOAD_ORDINARY}', ','.join(enemies) or '{.kind=LOAD_ORDINARY}', len(actors), len(enemies)))
    lines += ['};', 'static const uint16_t session_orders[2][81]={']
    for players in [1, 2]:
        lines.append('{' + ','.join(str(next(i for i, v in enumerate(levels) if v['record'] == r['record']))
                                   for r in orders if r['players'] == players) + '},')
    lines += ['};', 'static const SessionDataView session_password_lists[]={']
    pointers = symbols['DGROUP:PasswordListPointers']['linear']
    for players in [1, 2]:
        start = base + word(pointers + 2 * (players - 1))
        end = mz.image.index(b'\xff', start) + 1
        lines.append(view(start, end - start) + ',')
    lines += ['};']
    maps_at = symbols['DGROUP:CompressedTileMapsPointer']['linear']
    offset, frame = struct.unpack_from('<HH', mz.image, maps_at)
    maps = next(r for r in rows if r['name'].startswith('world.allocation.') and r['image_start'] == frame * 16 + offset)
    lines.append('static const SessionDataView session_maps=%s;' % view(maps['image_start'], maps['size']))
    # Explicit scalar defaults, not a struct dump. The two records are present
    # even when only player one is active. This list is independently observed
    # in the verification serializer, not parsed from a bridge at runtime.
    fields = [('PlayerUpInput', 'up'), ('PlayerDownInput', 'down'), ('PlayerLeftInput', 'left'),
              ('PlayerRightInput', 'right'), ('PlayerActionInput', 'action'), ('PlayerX32', 'fixed_x'),
              ('PlayerY32', 'fixed_y'), ('PlayerPixelX', 'pixel_x'), ('PlayerYPixels', 'pixel_y'),
              ('PlayerCachedPixelX', 'cached_x'), ('PlayerCachedPixelY', 'cached_y'), ('PlayerSpriteIds', 'sprite'),
              ('PlayerCachedSpriteIds', 'cached_sprite'), ('PlayerAnimationCountdowns', 'animation'),
              ('PlayerThrustAnimationRate', 'thrust'), ('PlayerPlatformIndices', 'platform'),
              ('PlayerCarriedKinds', 'carried'), ('PlayerDestinationIcons', 'destination'),
              ('PlayerPassengerFares', 'fare'), ('PlayerMinimumFares', 'minimum_fare'),
              ('PlayerHorizontalVelocities', 'velocity_x'), ('PlayerVerticalVelocities', 'velocity_y'),
              ('PlayerImpactMagnitude', 'impact')]
    lines += ['typedef struct SessionPlayerDefault {size_t member;SessionDataView data;} SessionPlayerDefault;',
              'static const SessionPlayerDefault session_player_fields[]={']
    for name, member in fields:
        for i in range(2):
            lines.append('{offsetof(NativePlayerWorld,player[%d].%s),%s},' %
                         (i, member, view(symbols['DGROUP:' + name]['linear'] + 2 * i, 2)))
    lines += ['};']
    for name in ['PlatformLeftEdges', 'PlatformRightEdges', 'PlatformHeights', 'PlatformArrivalPointsX',
                 'PlatformWaitingPointsX', 'PlatformSpawnX', 'PlatformDestinationIcons', 'PlatformActorOccupants']:
        at = symbols['DGROUP:' + name]['linear']
        if any(mz.image[at:at + 20]):
            raise ValueError('nonzero platform default: ' + name)
    def values(name, count):
        return ','.join(str(word(symbols['DGROUP:' + name]['linear'] + 2*i)) for i in range(count))
    lines.append('static const SessionFrameSpec session_frame_spec={{%s},{%s},{%s},%s,%s};' %
                 (values('PlayerAnimationCycleStarts', 2), values('PlayerAnimationCycleEnds', 2),
                  values('PlayerImpactLimits', 3), values('TimerBarDivisor', 1), values('TimerBarPointer', 1)))
    return lines
