"""Build-time admission for direct gameplay peers; no runtime word resolver."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate(rows, symbols):
    import cgen
    mz, _ = cgen.read_symbols()
    graph = json.loads((ROOT/'metadata/object-identities.json').read_text())
    world = json.loads((ROOT/'metadata/resource-world.json').read_text())
    links = list(graph['links'])
    # The earlier identity subcut enumerated +08..+2A (18 roles); retirement
    # consumes the nineteenth word at +2C. Admit this edge at build time using
    # the already registered typed callback domain, never a runtime decoder.
    for r in graph['resources']:
        if r['kind'] != 'OBJECT_ACTOR_DESCRIPTOR':
            continue
        if any(l['source'] == r['view'] and l['member'] == 44 for l in links):
            continue
        v = world['views'][r['view']]
        start = world['regions'][v['region']]['image_start'] + v['offset']
        word = int.from_bytes(mz.image[start+44:start+46], 'little')
        role = next(c for c in graph['callbacks'] if c['family'] == 'actor' and c['word'] == word)
        links.append(dict(source=r['view'], member=44, kind='callback', callback=role))
    links.sort(key=lambda l: (l['source'], l['member']))

    def view(start, size):
        choices = [r for r in rows if r['image_start'] <= start and
                   start + size <= r['image_start'] + r['size']]
        if not choices:
            raise ValueError('gameplay DATA outside admitted allocation')
        r = min(choices, key=lambda r: r['size'])
        return '{UINT64_C(%d),%d,%d}' % (r['id'], start-r['image_start'], size)

    def identity(r, position=0):
        return '{%s,{%d},%d}' % (r['kind'], r['view'], position)

    def callback(c):
        field = {'actor': 'actor', 'enemy': 'enemy', 'item': 'item', 'effect': 'effect'}[c['family']]
        if field == 'effect':
            return '{.kind=OBJECT_CALLBACK_DEMO_EFFECT,.effect={RESOURCE_DEMO_EFFECT,%s}}' % c['role']
        return '{.kind=OBJECT_CALLBACK_%s,.%s=%s}' % (field.upper(), field, c['role'])

    lines = ['/* Admitted DATA identities and graph links. No executable coordinates. */',
             'static const GameObjectData object_data[]={']
    for r in graph['resources']:
        v = world['views'][r['view']]
        start = world['regions'][v['region']]['image_start'] + v['offset']
        lines.append('{%s,%s},' % (identity(r), view(start, r['size'])))
    lines += ['};', 'static const GameObjectPosition object_positions[]={']
    for r in graph['resources']:
        lines += ['{%d,%d},' % (r['view'], p) for p in r['positions']]
    lines += ['};', 'static const ObjectGraphLink object_links[]={']
    for link in links:
        prefix = '{.source={%d},.member=%d,.kind=OBJECT_LINK_%s' % (
            link['source'], link['member'], link['kind'].upper())
        if link['kind'] == 'callback':
            prefix += ',.callback=' + callback(link['callback'])
        elif link['kind'] == 'resource':
            target = next(r for r in graph['resources'] if r['view'] == link['resource']['view'])
            prefix += ',.resource=' + identity(target, link['resource']['position'])
        elif link['kind'] == 'sprite':
            prefix += ',.sprite={RESOURCE_SPRITE_RECORD,%d}' % link['sprite']
        lines.append(prefix + '},')
    lines += ['};', 'static const ObjectResourceIdentity actor_types[]={']
    actors = [r for r in graph['resources'] if r['kind'] == 'OBJECT_ACTOR_DESCRIPTOR']
    assert len(actors) == 8
    lines += [identity(r) + ',' for r in sorted(actors, key=lambda r: r['word'])]
    lines += ['};']
    enemies = sorted((r for r in graph['resources'] if r['kind'] == 'OBJECT_ENEMY_DESCRIPTOR'), key=lambda r: r['word'])
    lines += ['static const ObjectResourceIdentity enemy_types[]={'] + [identity(r)+',' for r in enemies] + ['};']
    bonus = next(r for r in graph['resources'] if r['kind'] == 'OBJECT_ITEM_DESCRIPTOR' and
                 r['word'] == symbols['DGROUP:FallingDescriptor_7A38']['offset'])
    lines += ['static const ObjectResourceIdentity delivery_bonus=%s;' % identity(bonus),
              'static const SessionDataView multiplier_limits=%s;' %
              view(symbols['DGROUP:MultiplierLimitsByDifficulty']['linear'], 6)]
    for name, label in [('stone_effect', 'data.B3632.AdlxHeader_3632'),
                        ('bonus_effect', 'data.B3274.AdlxHeader_3274'),
                        ('bird_warning_effect', 'data.B325B.AdlxHeader_325B'),
                        ('bird_flight_effect', 'data.B3260.AdlxHeader_3260'),
                        ('dino_effect', 'data.B3265.AdlxHeader_3265')]:
        lines.append('static const GSResourceId %s=UINT64_C(%d);' %
                     (name, next(r['id'] for r in rows if r['name'] == label)))
    return lines
