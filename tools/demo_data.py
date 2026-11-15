"""Build-time admission of demo DATA views and existing typed identity graph.

Only IDs, offsets within DATA, typed roles and instruction boundaries are emitted.
Historical pointer/callback words are consumed here, never resolved by the game.
"""
import json
import struct
from pathlib import Path
import cgen

ROOT=Path(__file__).resolve().parents[1]

def generate(rows,symbols):
    mz,_=cgen.read_symbols()
    graph=json.loads((ROOT/'metadata/object-identities.json').read_text())
    world=json.loads((ROOT/'metadata/resource-world.json').read_text())
    scripts=[r for r in graph['resources'] if r['kind']=='OBJECT_SCRIPT']
    assert len(scripts)==28 and sum(r['size'] for r in scripts)==5556
    def word(at):return struct.unpack_from('<H',mz.image,at)[0]
    def view(start,size):
        choices=[r for r in rows if r['image_start']<=start and start+size<=r['image_start']+r['size']]
        if not choices:raise ValueError('demo data outside admitted object')
        r=min(choices,key=lambda r:r['size'])
        return '{UINT64_C(%d),%d,%d}'%(r['id'],start-r['image_start'],size)
    lines=['/* Generated DATA-only demo admission. */',
           'static const GameDemoSpec demo_specs[]={']
    offset=0
    for r in scripts:
        v=world['views'][r['view']]
        assert v['token']==r['view']
        start=world['regions'][v['region']]['image_start']+v['offset']
        link=next(l for l in graph['links'] if l['source']==r['view'] and l['member']==6)
        assert link['kind']=='callback' and link['callback']['family']=='effect'
        assert word(start+6)==link['word']
        role=link['callback']['role']
        lines.append('{{OBJECT_SCRIPT,{%d},0},%s,%d,%d},'%(r['view'],view(start,r['size']),offset,role))
        offset+=r['size']
    lines+=['};','static const GameDemoVector demo_vectors[]={']
    for kind,name in [('COMPLETION','DemoTable_1020'),('PREGAME','DemoTable_1792'),('ATTRACT','DemoTable_1E40'),('REVEAL','DemoTable_24DE')]:
        at=symbols['DGROUP:'+name]['linear'];ids=[]
        while word(at)!=65535:
            r=next(r for r in scripts if r['word']==word(at))
            ids.append('{OBJECT_SCRIPT,{%d},0}'%r['view']);at+=2
        assert len(ids)<16
        lines.append('{DEMO_PRESENT_%s,%d,{%s}},'%(kind,len(ids),','.join(ids)))
    lines+=['};']
    lines+=['static const GameDemoBoundary demo_boundaries[]={']
    for r in scripts:
        lines+=['{%d,%d},'%(r['view'],p) for p in r['positions']]
    lines+=['};']
    # All physical actor/enemy/item cold scalar allocations are explicitly zero
    # DATA declarations. Reject a changed template rather than import RAM.
    for begin,end in [('ActorDescriptors','PassengerQuickDeliveryCountdowns'),('EnemyDescriptors','EnemyFlightSoundHandles'),('FallingItemDescriptors','FallingItemVerticalStep')]:
        a=symbols['DGROUP:'+begin]['linear'];b=symbols['DGROUP:'+end]['linear']+(32 if begin=='ActorDescriptors' else 10 if begin=='EnemyDescriptors' else 24)
        if any(mz.image[a:b]):raise ValueError('nonzero demo owner defaults: '+begin)
    for name,member,size in [('WaterSurfaceFrameCountdown','presentation.weather.countdown',1),('WaterSurfaceFrame','presentation.weather.frame',2),('WaterSurfaceByteOffset','presentation.weather.byte_offset',2),('DemoExitCode','demo_exit',2),('VgaRowStrideBytes','demo_resources.row_stride',1)]:
        start=symbols['DGROUP:'+name]['linear']
        lines.append('static const GameDemoDataView demo_default_%s=%s;'%(name,view(start,size)))
    off,frame=struct.unpack_from('<HH',mz.image,symbols['DGROUP:CompressedTileMapsPointer']['linear'])
    start=frame*16+off
    r=next(r for r in rows if r['name'].startswith('world.allocation.') and r['image_start']==start)
    lines.append('static const GameDemoDataView demo_maps=%s;'%view(start,r['size']))
    return lines

