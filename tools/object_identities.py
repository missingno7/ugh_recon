"""Extract the typed actor/enemy/item graph from the validated plain build.

Only the verification manifest/bindings contain historical words. Native graph
links contain existing resource view tokens, relative positions and enum roles.
No function pointers or code-word-to-function resolver are generated.
"""
import argparse
import json
import re
import struct
from pathlib import Path
import cgen

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ['metadata/object-identities.json', 'native/object_identities.inc',
           'native/bridge/object_identity_bindings.inc']
FAMILIES = {'actor descriptor': 'OBJECT_ACTOR_DESCRIPTOR',
            'enemy descriptor': 'OBJECT_ENEMY_DESCRIPTOR',
            'falling-item descriptor': 'OBJECT_ITEM_DESCRIPTOR',
            'passenger itinerary': 'OBJECT_JOURNEY', 'motion script': 'OBJECT_SCRIPT',
            'animation': 'OBJECT_ANIMATION', 'tree reward list': 'OBJECT_DROP_LIST'}
ITEMS = {'SpawnFallingItem': 'ITEM_CALLBACK_SPAWN', 'AdvanceFallingItem': 'ITEM_CALLBACK_ADVANCE',
         'LandFallingItem': 'ITEM_CALLBACK_LAND', 'ExpireOrCollectFallingItem': 'ITEM_CALLBACK_COLLECT'}
EFFECTS = {'IgnoreActorState': 0, 'StartDemoFadeWhenSpriteHidden': 1, 'SetDemoRevealSpriteWidth': 2}


def extract():
    mz, symbols = cgen.read_symbols()
    world = json.loads((ROOT / 'metadata/resource-world.json').read_text())
    base = cgen.FRAMES['DGROUP'] * 16
    word = lambda at: struct.unpack_from('<H', mz.image, at)[0]
    actor = re.findall(r'\bACTOR_CALLBACK_(\w+)', (ROOT / 'native/actor_pass.h').read_text())
    actor = {n: 'ACTOR_CALLBACK_' + n for n in actor if n not in ['UNSUPPORTED', 'COUNT']}
    hazard = dict((name, role) for role, name in re.findall(
        r'case (H_\w+):return G\((\w+)\);',
        (ROOT / 'native/bridge/hazards_bridge.c').read_text()))
    callback_rows = []
    for family, roles in [('actor', actor), ('enemy', hazard), ('item', ITEMS)]:
        for name, role in sorted(roles.items()):
            callback_rows.append(dict(family=family, word=symbols['GAME:' + name]['offset'], role=role))
    callback_rows += [dict(family='effect', word=symbols['GAME:' + n]['offset'], role=v)
                      for n, v in EFFECTS.items()]
    callback_rows.append(dict(family='enemy', word=0, role='H_ZERO'))
    resources = []
    for view in world['views']:
        prefix = view['name'].split('.')[0]
        if prefix not in FAMILIES:
            continue
        at = world['regions'][view['region']]['image_start'] + view['offset']
        positions = [0]
        if prefix == 'motion script':
            positions = [0]; p = 8
            while p < view['size']:
                positions.append(p)
                p += 4 if word(at + p) < 32768 else 2
            if p != view['size']:
                raise ValueError('partial script opcode: ' + view['name'])
        elif prefix == 'passenger itinerary':
            positions = list(range(0, view['size'], 4))
        elif prefix in ['animation', 'tree reward list']:
            positions = list(range(0, view['size'], 2))
        resources.append(dict(name=view['name'], kind=FAMILIES[prefix], view=view['token'],
                              word=at-base, size=view['size'], positions=positions))

    def reference(kind, raw):
        for row in resources:
            if row['kind'] == kind and raw-row['word'] in row['positions']:
                return dict(kind=kind, view=row['view'], position=raw-row['word'])
        raise ValueError(f'unregistered {kind} reference {raw:04x}')

    def callback(family, raw):
        for row in callback_rows:
            if row['family'] == family and row['word'] == raw:
                return dict(family=family, role=row['role'])
        if raw == 0:
            return dict(family='empty', role=0)
        raise ValueError(f'unregistered {family} callback {raw:04x}')

    links = []
    for row in resources:
        kind = row['kind']; at = base + row['word']
        def add(member, category, target=None):
            raw = word(at + member)
            result = dict(source=row['view'], member=member, word=raw, kind=category)
            if category == 'resource':
                if raw == 0: result['kind'] = 'empty'
                elif raw == 65535: result['kind'] = 'end'
                else: result['resource'] = reference(target, raw)
            elif category == 'callback':
                result['callback'] = callback(target, raw)
            elif category == 'sprite':
                if raw == 65535: result['kind'] = 'end'
                elif raw >= 662: raise ValueError('unregistered sprite')
                else: result['sprite'] = raw
            links.append(result)
        if kind == 'OBJECT_ACTOR_DESCRIPTOR':
            for p in range(8, 44, 2): add(p, 'callback', 'actor')
            for p in range(46, 58, 2): add(p, 'resource', 'OBJECT_ANIMATION')
            add(72, 'resource', 'OBJECT_ACTOR_DESCRIPTOR')
        elif kind == 'OBJECT_ENEMY_DESCRIPTOR':
            for p in range(8, 34, 2): add(p, 'callback', 'enemy')
            # The tree's first animation operand is its reward-list seed.
            for p in range(34, 58, 2):
                raw = word(at+p)
                target = 'OBJECT_DROP_LIST' if any(r['kind']=='OBJECT_DROP_LIST' and r['word']==raw for r in resources) else 'OBJECT_ANIMATION'
                add(p, 'resource', target)
        elif kind == 'OBJECT_ITEM_DESCRIPTOR':
            for p in range(4, 12, 2): add(p, 'callback', 'item')
            add(16, 'sprite')
        elif kind == 'OBJECT_SCRIPT': add(6, 'callback', 'effect')
        elif kind == 'OBJECT_ANIMATION':
            for p in range(0, row['size'], 2): add(p, 'sprite')
        elif kind == 'OBJECT_DROP_LIST':
            for p in range(0, row['size'], 2): add(p, 'resource', 'OBJECT_ITEM_DESCRIPTOR')
    manifest = dict(schema=1, source='metadata/resource-world.json',
                    resources=resources, callbacks=callback_rows, links=links)
    native = ['/* Generated by tools/object_identities.py; no historical words. */',
              'static const ObjectResourceIdentity object_resources[]={']
    for row in resources:
        for p in row['positions']:
            native.append(' {' + row['kind'] + ',{' + str(row['view']) + '},' + str(p) + '},')
    native += ['};', 'static const ObjectGraphLink object_links[]={']
    for link in links:
        resource = link.get('resource', {})
        ref = '{'+resource.get('kind','OBJECT_RESOURCE_UNSUPPORTED')+',{'+str(resource.get('view',0))+'},'+str(resource.get('position',0))+'}'
        cb = link.get('callback', {}); family = cb.get('family', 'unsupported')
        role = str(cb.get('role',0))
        callback_value = '{OBJECT_CALLBACK_' + family.upper() + ','
        callback_value += (role if family=='actor' else 'ACTOR_CALLBACK_UNSUPPORTED')+','
        callback_value += (role if family=='enemy' else 'H_ZERO')+','
        callback_value += (role if family=='item' else 'ITEM_CALLBACK_UNSUPPORTED')+','
        callback_value += '{RESOURCE_DEMO_EFFECT,'+(role if family=='effect' else '0')+'}}'
        callback_value = callback_value.replace('OBJECT_CALLBACK_EFFECT', 'OBJECT_CALLBACK_DEMO_EFFECT')
        native.append(' {{'+str(link['source'])+'},'+str(link['member'])+',OBJECT_LINK_'+link['kind'].upper()+','+ref+','+callback_value+',{RESOURCE_SPRITE_RECORD,'+str(link.get('sprite',0))+'}},')
    native += ['};', '']
    bridge = ['/* Generated verification-only historical transport bindings. */',
              'static const ObjectLegacyResource object_legacy_resources[]={']
    bridge += [' {'+r['kind']+',{'+str(r['view'])+'},'+str(r['word'])+'},' for r in resources]
    bridge += ['};', 'static const ObjectLegacyCallback object_legacy_callbacks[]={']
    for row in callback_rows:
        bridge.append(' {OBJECT_LEGACY_'+row['family'].upper()+','+str(row['word'])+','+str(row['role'])+'},')
    bridge += ['};', '']
    return [json.dumps(manifest, indent=2)+'\n', '\n'.join(native), '\n'.join(bridge)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    for name, content in zip(OUTPUTS, extract()):
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text() != content: raise ValueError('stale generated identity graph: '+name)
        else: path.write_text(content, encoding='utf-8', newline='\n')
    print('PASS object identity graph' + (' check' if args.check else ' generation'))


if __name__ == '__main__': main()
