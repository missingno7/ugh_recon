"""Decode, repack and inventory data in the locked Ugh! DOS image.

Commands: list; decode FRAME|--all; repack FRAME|--all; render --all;
levels; music [external.8svx]; dgroup. Artifacts go to build/workers/data3/.

Ranges are image-linear, half-open offsets. The checker makes sure the entries cover
all data frames exactly, including the attributed runtime DGROUP contributions.
Only the standard library is required. Code references use module:offset.
"""
from pathlib import Path
import struct
import sys
import zlib
import json
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from common import MZ, BUILD, load_json

IMAGE = BUILD / 'oracle' / 'UGH_X.EXE'

# Image ranges include each stream's separately classified paragraph padding.
ICE_STREAMS = {
    0x1A38: (0x1A380, 0x1E1F0),
    0x2BF6: (0x2BF60, 0x2D9A0),
    0x2D9A: (0x2D9A0, 0x2F9E0),
    0x2F9E: (0x2F9E0, 0x2FB70),
    0x2FB7: (0x2FB70, 0x325B0),
}
GAME_CS_IMAGE = 0x13B0
OUT = BUILD / 'workers' / 'data3'


def game_palette(mz):
    # 013B:466A duplicates the first 128 RGB triples into both palette halves.
    return mz.image[0x2BC60:0x2BDE0]*2


def graphics(mz):
    """GAME 013B:41FD: {u16 offset,u8 width,u8 height}; column-major pixels."""
    banks = [(0, 217, 0x1E1F0, 0x2BC60), (217, 298, 0x37A70, 0x438A0),
             (298, 547, 0x438A0, 0x4E830), (547, 662, 0x4E830, 0x5B630)]
    result = []
    for first, last, start, end in banks:
        cursor = 0
        for index in range(first, last):
            offset, w, h = struct.unpack_from('<HBB', mz.image, 0x5B630 + index * 4)
            if not w or not h or offset != cursor or start + offset + w*h > end:
                raise ValueError(f'bad sprite {index}: offset={offset}, cursor={cursor}, {w}x{h}')
            raw = mz.image[start+offset:start+offset+w*h]
            pixels = bytes(raw[x*h+y] for y in range(h) for x in range(w))
            # The transpose is lossless, including transparent zero pixels.
            if bytes(pixels[y*w+x] for x in range(w) for y in range(h)) != raw:
                raise ValueError(f'sprite {index} round-trip failed')
            result.append(dict(index=index, bank=f'{start//16:04X}', offset=offset,
                               width=w, height=h, pixels=pixels))
            cursor += w*h
        tail = mz.image[start+cursor:end]
        if any(tail):
            raise ValueError('nonzero graphics bank tail')
        print(f'bank {start//16:04X}: sprites {first}..{last-1}, {cursor} pixel bytes, {len(tail)} padding bytes')
    if any(mz.image[0x5B630+662*4:0x5C090]):
        raise ValueError('nonzero sprite directory padding')
    return result


def render_graphics(mz, sprites):
    palette = game_palette(mz)
    for bank in sorted({s['bank'] for s in sprites}):
        entries = [s for s in sprites if s['bank'] == bank]
        width = 1024
        positions, x, y, rowh = [], 2, 2, 0
        for s in entries:
            if x+s['width']+2 > width:
                x, y, rowh = 2, y+rowh+4, 0
            positions.append((x,y))
            x += s['width']+4
            rowh = max(rowh,s['height'])
        height = y+rowh+2
        sheet = bytearray(width*height)
        manifest = []
        for s, (x,y) in zip(entries,positions):
            for row in range(s['height']):
                sheet[(y+row)*width+x:(y+row)*width+x+s['width']] = s['pixels'][row*s['width']:(row+1)*s['width']]
            manifest.append({k:v for k,v in s.items() if k != 'pixels'} | dict(sheet_x=x,sheet_y=y))
        _write_png(OUT/'png'/f'bank_{bank}.png', width, height, _indexed_rgb(sheet,palette))
        (OUT/f'bank_{bank}.json').write_text(json.dumps(manifest,indent=2)+'\n')


def levels(mz):
    """GAME 013B:3976 loads 26 bytes; 4172 draws 20 columns x 16 rows."""
    d = mz.image[0x5C090:]
    maps, _, _ = decode_ice(mz, 0x1A38)
    if len(maps) != 100*320 or max(maps) >= 174:
        raise ValueError('invalid tile map bank')
    def word(p):
        return struct.unpack_from('<H',d,p)[0]
    def terminated(p, stride):
        records = []
        begin = p
        while word(p) != 0xffff:
            if p+stride > 0x7b7c or len(records) >= 100:
                raise ValueError(f'bad level list at {begin:04X}')
            records.append(list(struct.unpack_from('<'+'H'*(stride//2),d,p)))
            p += stride
        return records, p+2
    records = {}
    orders = []
    for players, order_start, names_start, count in [(1,0x3349,0xee,69),(2,0x33d5,0x492,81)]:
        passwords = []
        np = names_start
        for _ in range(count):
            end = d.index(0,np)
            passwords.append(d[np:end].decode('ascii'))
            np = end+1
        if d[np] != 0xff or word(order_start+2*count) != 0xffff:
            raise ValueError('level order/password sentinel mismatch')
        for n, password in enumerate(passwords):
            p = word(order_start+2*n)
            if not (0x3479 <= p < 0x3cb3 and (p-0x3479)%26 == 0):
                raise ValueError(f'invalid level record {p:04X}')
            if p not in records:
                map_offset, platform_p, actor_p, enemy_p = struct.unpack_from('<4H',d,p)
                title_p = word(p+10)
                if map_offset%320 or map_offset+320 > len(maps):
                    raise ValueError('invalid level map offset')
                title_end = d.index(0,title_p)
                title_raw = d[title_p:title_end]
                platforms, platform_end = terminated(platform_p,16)
                actors, actor_end = terminated(actor_p,6)
                enemies, enemy_end = [], enemy_p
                while word(enemy_end) != 0xffff:
                    descriptor = word(enemy_end)
                    stride = {0x76e4:6,0x76a8:10}.get(descriptor,8)
                    if not 0x7630 <= descriptor < 0x7a44 or len(enemies) >= 5:
                        raise ValueError(f'invalid enemy at {enemy_end:04X}: {descriptor:04X}')
                    enemies.append(list(struct.unpack_from('<'+'H'*(stride//2),d,enemy_end)))
                    enemy_end += stride
                enemy_end += 2
                records[p] = dict(record=f'{p:04X}', map=map_offset//320,
                    map_offset=map_offset, platforms_pointer=f'{platform_p:04X}',
                    actors_pointer=f'{actor_p:04X}', enemies_pointer=f'{enemy_p:04X}',
                    title_pointer=f'{title_p:04X}', title_raw=title_raw.hex(),
                    title=title_raw.replace(b'\xfe',b'').replace(b'\xfd',b' | ').decode('cp437').replace('\r',' / '),
                    passengers=d[p+8], reserved09=d[p+9], weather=d[p+12],
                    player1=list(struct.unpack_from('<HH',d,p+13)),
                    player2=list(struct.unpack_from('<HH',d,p+17)),
                    water=word(p+21), water_delta=struct.unpack_from('<h',d,p+23)[0],
                    reserved25=d[p+25], platforms=platforms, actors=actors, enemies=enemies,
                    spans=[['platforms',platform_p,platform_end],['actors',actor_p,actor_end],
                           ['enemies',enemy_p,enemy_end],['text',title_p,title_end+1]])
            orders.append(dict(players=players,number=n+1,password=password,**records[p]))
    if len(records) != 81:
        raise ValueError('level record coverage mismatch')
    return maps, orders


def dump_levels(mz, sprites, render=False):
    maps, orders = levels(mz)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'levels.json').write_text(json.dumps(orders,indent=2)+'\n',encoding='utf-8')
    lines = []
    for level in orders:
        lines.append(f"{level['players']}P {level['number']:02d} {level['password']} record={level['record']} map={level['map']:02d} {level['title']}")
        tilemap = maps[level['map_offset']:level['map_offset']+320]
        lines.extend(' '.join(f'{v:02X}' for v in tilemap[y*20:(y+1)*20]) for y in range(16))
    (OUT/'levels.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    if render:
        # All 100 maps, including menu/unused maps; draw exactly as 013B:4172.
        sheet = bytearray(5*320*20*192)
        for index in range(100):
            pixels = bytearray(320*192)
            for at,tile in enumerate(maps[index*320:(index+1)*320]):
                s = sprites[tile]
                if (s['width'],s['height']) != (16,12):
                    raise ValueError('tile dimensions mismatch')
                x, y = at%20*16, at//20*12
                for row in range(12):
                    pixels[(y+row)*320+x:(y+row)*320+x+16] = s['pixels'][row*16:(row+1)*16]
            _write_png(OUT/'png'/'maps'/f'{index:02d}.png',320,192,
                       _indexed_rgb(pixels,game_palette(mz)))
            x, y = index%5*320,index//5*192
            for row in range(192):
                sheet[(y+row)*1600+x:(y+row)*1600+x+320] = pixels[row*320:(row+1)*320]
        _write_png(OUT/'png'/'maps_all.png',1600,3840,
                   _indexed_rgb(sheet,game_palette(mz)))
    print(f'levels: {len(orders)} ordered entries, 81 unique records, 100 tile maps')


MUSIC_CALLS = {0x325b:['23CE'],0x3260:['2484'],0x3265:['29A2'],
    0x326b:['0192'],0x3274:['1AFA','2B4E'],0x3279:['0297','08BA'],
    0x343f:[],0x3444:['0C75'],0x3629:['06E2'],0x3632:['1CE4'],0x3637:['0078']}


def music(mz):
    """C 0878:0AA9 container, SOUND 0664:15D3/176B track interpreters."""
    results = []
    samples=[p for p in range(len(mz.image)-12)
             if mz.image[p:p+4]==b'FORM' and mz.image[p+8:p+12]==b'8SVX']
    if samples:
        raise ValueError(f'uninventoried embedded FORM/8SVX at {samples}')
    observed=[p for p in range(len(mz.image)-4) if mz.image[p:p+4]==b'ADLX']
    if observed != sorted(frame*16 for frame in MUSIC_CALLS):
        raise ValueError('ADLX signature census differs from the object inventory')
    for frame,calls in MUSIC_CALLS.items():
        start = frame*16
        root_size = struct.unpack_from('>I',mz.image,start+4)[0]
        raw = mz.image[start:start+root_size+8]
        if raw[:4] != b'ADLX' or raw[8:12] != b'AHDR':
            raise ValueError('invalid ADLX/AHDR tag')
        ahdr_size = struct.unpack_from('>I',raw,12)[0]
        ahdr = raw[16:16+ahdr_size]
        p = 16+ahdr_size
        if raw[p:p+4] != b'IMAP':
            raise ValueError('missing IMAP')
        imap_size = struct.unpack_from('>I',raw,p+4)[0]
        imap = raw[p+8:p+8+imap_size]
        p += 8+imap_size
        if raw[p:p+4] != b'TRCK':
            raise ValueError('missing TRCK')
        track_size_field = struct.unpack_from('<I',raw,p+4)[0]
        if ahdr_size != 10 or imap_size != 0 or track_size_field != root_size:
            raise ValueError('ADLX differs from observed container dialect')
        p += 8
        track_start = p
        events, ticks = [],0
        while p < len(raw):
            begin = p
            code = raw[p]
            p += 1
            op, channel = code >> 4, code & 15
            event = dict(offset=begin-track_start,code=f'{code:02X}',channel=channel,ticks=ticks)
            if code == 0x77:
                event['op'] = 'end_or_loop'
            elif op == 0:
                event['op'] = 'wait_long'
                event['delta'] = ((channel << 8)+raw[p]) << 7
                p += 1
                ticks += event['delta']
            elif op in (1,4) and channel >= 9:
                event['op'] = 'invalid_channel_noop'
            elif op == 1:
                event['op'] = 'frequency_key_on'
                event['value'] = struct.unpack_from('<H',raw,p)[0]
                p += 2
            elif op == 2:
                event['op'] = 'key_off'
            elif op == 3:
                event['op'] = 'volume'
                event['value'] = raw[p]
                p += 1
            elif op == 4:
                event['op'] = 'instrument'
                event['registers'] = raw[p:p+11].hex()
                p += 11
            elif op == 5:
                event['op'] = 'noop'
            elif op == 6:
                event['op'] = 'timer_period'
                event['pit_divisor'] = struct.unpack_from('>H',raw,p)[0]
                p += 2
            elif op == 7:
                length = raw[p]
                event['op'] = 'control' if code == 0x70 else 'extension'
                p += 3 if code == 0x70 else length+1
            else:
                event['op'] = 'wait_short'
                event['delta'] = code & 0x7f
                ticks += event['delta']
            if p > len(raw):
                raise ValueError(f'ADLX event overrun {frame:04X}+{begin:04X}')
            event['raw'] = raw[begin:p].hex()
            events.append(event)
        if not events or events[-1]['code'] != '77':
            raise ValueError(f'ADLX {frame:04X} does not end on 77')
        def encode_event(e):
            code=int(e['code'],16)
            payload=b''
            if e['op']=='wait_long':
                payload=bytes([(e['delta']>>7)&255])
            elif e['op']=='frequency_key_on':
                payload=struct.pack('<H',e['value'])
            elif e['op']=='volume':
                payload=bytes([e['value']])
            elif e['op']=='instrument':
                payload=bytes.fromhex(e['registers'])
            elif e['op']=='timer_period':
                payload=struct.pack('>H',e['pit_divisor'])
            elif e['op'] in ('extension','control'):
                payload=bytes.fromhex(e['raw'])[1:]
            return bytes([code])+payload
        rebuilt_track = b''.join(encode_event(e) for e in events)
        if rebuilt_track != raw[track_start:]:
            raise ValueError('track round-trip mismatch')
        rebuilt=(b'ADLX'+struct.pack('>I',root_size)+b'AHDR'+struct.pack('>I',ahdr_size)+ahdr+
                 b'IMAP'+struct.pack('>I',imap_size)+imap+b'TRCK'+struct.pack('<I',track_size_field)+rebuilt_track)
        if rebuilt != raw:
            raise ValueError('container round-trip mismatch')
        result = dict(frame=f'{frame:04X}',size=len(raw),root_size=root_size,
            ahdr=ahdr.hex(),version=struct.unpack_from('<H',ahdr)[0],channels=ahdr[2],
            ticks_per_unit=struct.unpack_from('<H',ahdr,6)[0],imap=imap.hex(),
            track_size_field=track_size_field,track_offset=track_start,track_length=len(rebuilt_track),
            total_ticks=ticks,calls=[f'GAME 013B:{c}' for c in calls],events=events)
        results.append(result)
        print(f"ADLX {frame:04X}: {len(raw)} bytes, {len(rebuilt_track)} track bytes, {len(events)} events, {ahdr[2]} channels, {ticks} ticks; calls={','.join(calls) or 'none found'}")
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'music.json').write_text(json.dumps(results,indent=2)+'\n')
    return results


def parse_form(raw):
    """IFF 8SVX dumper; C 0878:0176 consumes VHDR rate/compression and BODY.

    There are no actual FORM/8SVX resources in the executable. This handles external
    samples without confusing the substrings FORM in passwords and level titles.
    """
    if raw[:4] != b'FORM' or raw[8:12] != b'8SVX':
        raise ValueError('expected FORM/8SVX')
    size = struct.unpack_from('>I',raw,4)[0]+8
    if size > len(raw):
        raise ValueError('truncated FORM')
    chunks, p = [],12
    while p < size:
        n = struct.unpack_from('>I',raw,p+4)[0]
        payload = raw[p+8:p+8+n]
        if len(payload) != n:
            raise ValueError('truncated IFF chunk')
        item = dict(tag=raw[p:p+4].decode('ascii'),size=n,offset=p)
        if item['tag'] == 'VHDR':
            one,repeat,cycle,rate,octave,compression,volume = struct.unpack_from('>IIIHBBI',payload)
            item.update(one_shot=one,repeat=repeat,cycle=cycle,rate=rate,
                        octave=octave,compression=compression,volume=volume)
        chunks.append(item)
        p += 8+n+(n&1)
    if p != size:
        raise ValueError('IFF size mismatch')
    return dict(size=size,chunks=chunks)


DGROUP_OBJECTS = [
    (0,0x91,'runtime startup data','docs/runtime.md'),
    (0x91,0x92,'alignment','runtime WORD alignment'),
    (0x92,0xee,'game pointers and numeric constants','013B:450A,4634,466A,3F0F,0652'),
    (0xee,0x492,'69 one-player passwords and FF terminator','013B:0C07,06B5'),
    (0x492,0x91f,'81 two-player passwords and FF terminator','013B:0C07,06B5'),
    (0x91f,0xae4,'credits text','013B:07F6,077C'),
    (0xae4,0xc86,'menu text and edit fields','013B:0039,04CA,077C'),
    (0xc86,0xcf1,'five 21-byte score rows and 00 FF terminators','013B:0446,0452,04B3'),
    (0xcf1,0xcf9,'UGH!.HI filename','013B:0405'),
    (0xcf9,0xcfa,'zero byte (alignment candidate)','no direct reader found'),
    (0xcfa,0xd00,'three player animation boundaries','013B:41B8'),
    (0xd00,0x1020,'46 terminated sprite sequences','013B:1582,1646,2AB5; descriptors'),
    (0x1020,0x2614,'four demonstration tables and 28 motion scripts','013B:088D,08A2,08C7,08CF,0AEB,09D7'),
    (0x2614,0x261c,'four single-plane and four cumulative VGA masks','013B:4106,413A'),
    (0x261c,0x264c,'global game state and difficulty constants','013B:010E,0125,0C07,3F55'),
    (0x264c,0x278c,'current 20x16 tile map','013B:39AB,4172'),
    (0x278c,0x27a6,'input commands and control-option state','013B:45BF,04CA'),
    (0x27a6,0x27d0,'HUD, fade and cached score state','013B:3D66,3F55'),
    (0x27d0,0x281c,'two-player parallel state fields','013B:39B9,418D'),
    (0x281c,0x28e9,'34 six-byte keyboard sequences and FF sentinel','013B:450A,4567'),
    (0x28e9,0x2903,'current 26-byte level record','013B:3976'),
    (0x2903,0x2909,'water line current/previous and VGA extent','013B:2D2F,2DDA'),
    (0x2909,0x290d,'two level-order near pointers','013B:397D'),
    (0x290d,0x29ad,'eight parallel arrays of ten platform words','013B:3A67,13FD'),
    (0x29ad,0x2cad,'24 parallel arrays of sixteen actor words','013B:3AA9,149C'),
    (0x2cad,0x2d6b,'19 parallel arrays of five enemy words','013B:3B1B,23C8,25B1,295B,2A87'),
    (0x2d6b,0x2e8b,'12 parallel arrays of twelve falling-item words','013B:2B7F,2B96'),
    (0x2e8b,0x3311,'three parallel arrays of 193 rain words','013B:3C04,3C35,3C78,3D19'),
    (0x3311,0x3345,'joystick sampling/calibration state','013B:50C6,51EC'),
    (0x3345,0x3349,'four zero bytes, owner unknown','no direct reader found'),
    (0x3349,0x33d5,'69 one-player record pointers plus FFFF','013B:3976'),
    (0x33d5,0x3479,'81 two-player record pointers plus FFFF','013B:3976'),
    (0x3479,0x3cb3,'81 packed 26-byte level records','013B:3976'),
    (0x3cb3,0x7630,'level platforms, itineraries, actors, enemies, text, reward lists','013B:3A67..3BFE,149C,2B34,077C'),
    (0x7630,0x7720,'four 60-byte enemy descriptors','013B:23C8,25B1,295B,2A87'),
    (0x7720,0x7970,'eight 74-byte actor descriptors','013B:149C..2195'),
    (0x7970,0x7a4c,'eleven 20-byte falling-item descriptors','013B:2B34,2B96..2CAD'),
    (0x7a4c,0x7b7c,'timer dispatcher state, sixteen slots','0A32:0008,00D2,01AA,021B,02C1'),
    (0x7b7c,0x7e2e,'runtime library data and initialization table','docs/runtime.md'),
]


def dgroup(mz):
    """Dump consumer-defined structures and a byte-complete DGROUP subobject map."""
    d = mz.image[0x5C090:]
    subobjects = {}
    def word(p):
        return struct.unpack_from('<H',d,p)[0]
    def add(kind,a,b,reader,values=None):
        key = (kind,a,b)
        if key not in subobjects:
            subobjects[key] = dict(kind=kind,start=a,end=b,reader=reader,values=values)
    # FFFF-terminated animation vectors; all sprite IDs are bounded by the directory.
    if d[0x28e8] != 0xff:
        raise ValueError('keyboard table sentinel mismatch')
    for p in range(0x281c,0x28e8,6):
        codes=list(d[p:p+3])
        add('keyboard sequence',p,p+6,'013B:4567',dict(
            scancodes=codes,destination_offset=d[p+3],value=d[p+4],state=d[p+5]))
    p = 0xd00
    while p < 0x1020:
        start,values = p,[]
        while word(p) != 0xffff:
            values.append(word(p)); p += 2
        p += 2
        if any(v >= 662 for v in values):
            raise ValueError('invalid animation sprite')
        add('animation',start,p,'013B:1582,1646,2AB5',values)
    # The pointer tables define all motion-script starts, rather than heuristic scans.
    for table,limit in [(0x1020,0x1792),(0x1792,0x1e40),(0x1e40,0x24de),(0x24de,0x2614)]:
        p,starts = table,[]
        while word(p) != 0xffff:
            starts.append(word(p)); p += 2
        p += 2
        add('demo pointer table',table,p,'013B:0AEB',starts)
        starts = sorted(starts)
        if starts[0] != p:
            raise ValueError('gap after motion pointer table')
        for begin,end in zip(starts,starts[1:]+[limit]):
            x,y,period,callback = struct.unpack_from('<hhHH',d,begin)
            p,events = begin+8,[]
            while p < end:
                code = word(p); p += 2
                if code >= 0x8000:
                    events.append(dict(op='repeat_or_stop' if code==0x8000 else 'loop_count',value=code))
                else:
                    dx,dy = struct.unpack_from('<bb',d,p); p += 2
                    if code != 0x7fff and code >= 662:
                        raise ValueError(f'bad motion sprite {code} at {p-4:04X}, script {begin:04X}')
                    events.append(dict(op='frame',sprite=code,dx=dx,dy=dy))
            if p != end or not events or events[-1].get('value') != 0x8000:
                raise ValueError(f'motion script boundary mismatch {begin:04X}')
            add('motion script',begin,end,'013B:09D7,0AEB',dict(x=x,y=y,period=period,callback=f'013B:{callback:04X}',events=events))
    _,orders = levels(mz)
    for level in orders:
        for kind,a,b in level['spans']:
            add(kind,a,b,'013B:3976..3BFE,077C')
        for descriptor,platform,p in level['actors']:
            if descriptor != 0x78dc:
                begin,values = p,[]
                while word(p) != 0xffff:
                    values.append([word(p),word(p+2)]); p += 4
                add('passenger itinerary',begin,p+2,'013B:149C,14DD',values)
        for enemy in level['enemies']:
            if enemy[0] == 0x76e4:
                begin=p=enemy[2]
                values=[]
                while word(p) != 0xffff:
                    values.append(word(p)); p += 2
                if any(not (0x7970<=v<0x7a4c and (v-0x7970)%20==0) for v in values):
                    raise ValueError('bad falling-item descriptor pointer')
                add('tree reward list',begin,p+2,'013B:2B34',values)
    # These span checks prove the variable-size arena has neither omitted bytes nor
    # conflicting layouts. Reused FFFF sentinels can overlap with another empty list.
    covered=bytearray(0x7630-0x3cb3)
    owners={}
    for item in subobjects.values():
        a,b=item['start'],item['end']
        if 0x3cb3<=a<b<=0x7630:
            for p in range(a,b):
                if p in owners and d[p] != 0xff:
                    raise ValueError(f'conflicting level object layouts at {p:04X}')
                owners[p]=item['kind']
            covered[a-0x3cb3:b-0x3cb3]=b'\1'*(b-a)
    if not all(covered):
        raise ValueError('level arena contains unclassified bytes')
    for a,b,kind,stride,reader in [(0x7630,0x7720,'enemy descriptor',60,'013B:23C8..2B7E'),
            (0x7720,0x7970,'actor descriptor',74,'013B:149C..2195'),
            (0x7970,0x7a4c,'falling-item descriptor',20,'013B:2B96..2CAD')]:
        for p in range(a,b,stride):
            values=list(struct.unpack_from('<'+'H'*(stride//2),d,p))
            if struct.pack('<'+'H'*len(values),*values) != d[p:p+stride]:
                raise ValueError('descriptor round-trip failed')
            add(kind,p,p+stride,reader,values)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'dgroup.json').write_text(json.dumps(dict(
        objects=[dict(start=a,end=b,kind=k,reader=r) for a,b,k,r in DGROUP_OBJECTS],
        subobjects=sorted(subobjects.values(),key=lambda i:(i['start'],i['end'],i['kind']))),indent=2)+'\n')
    print(f'DGROUP: {len(DGROUP_OBJECTS)} exact-coverage ranges, {len(subobjects)} decoded subobjects; complete level arena')
    return subobjects


def dgroup_xrefs():
    """Numeric equates and instruction-address comments survive symbol renaming."""
    refs = {}
    for module in ['GAME','TIMER']:
        source=(ROOT/'src'/'asm'/f'{module}.ASM').read_text()
        constants={m[1]:int(m[2],16) for m in re.finditer(
            r'(?m)^(\w+)\s+equ\s+([0-9A-Fa-f]+)h\s*$',source)}
        for line in source.splitlines():
            address=re.search(r'; @([0-9A-F]{4})',line)
            if not address:
                continue
            for operand in re.findall(r'\[([^]]+)\]',line):
                for token in re.findall(r'\b\w+\b',operand):
                    if token in constants and 0x92<=constants[token]<0x7b7c:
                        a=constants[token]
                        refs.setdefault(a,[]).append(dict(module=module,
                            address=address[1],instruction=line.split(';')[0].strip()))
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'dgroup_xrefs.json').write_text(json.dumps(
        {f'{a:04X}':r for a,r in sorted(refs.items())},indent=2)+'\n')
    return refs


def object_table(mz):
    """Exact byte partition; finer decoded fields are in dgroup.json/sprite manifests."""
    rows=[]
    def add(a,b,kind,description,confidence,reader):
        rows.append((a,b,kind,description,confidence,reader))
    add(0xa670,0x1a370,'scratch','64768 zero bytes; ICE destination','supported-by-code','GAME 013B:4CA5')
    add(0x1a370,0x1a374,'C state','two initialized 16-bit flags','supported-by-code','C 0878:0003,008A; module.c g_0000/g_0002')
    add(0x1a374,0x1a380,'padding','12 zero bytes after C state','supported-by-code','paragraph placement of 1A38')
    def ice(frame,meaning):
        a,b=ICE_STREAMS[frame]
        n=struct.unpack_from('>I',mz.image,a+4)[0]
        add(a,a+n,'ICE resource',meaning,'verified-by-decode','GAME 013B:4CAD; exact independent repack235')
        add(a+n,b,'padding',f'{b-a-n} zero bytes','verified-by-decode','ICE header endpoint')
    ice(0x1a38,'100 row-major 20x16 tile maps')
    add(0x1e1f0,0x2bc58,'sprite pixels','IDs 0..216, column-major 8-bit indexed','verified-by-decode','GAME 013B:41FD; directory 5B63:0000')
    add(0x2bc58,0x2bc60,'padding','8 zero bytes','verified-by-decode','end of sprite 216')
    add(0x2bc60,0x2bf60,'VGA palette','256 RGB6 triples; first 128 copied twice, last 128 not read by that loader','supported-by-code','GAME 013B:466A,4E72; DGROUP 00B3')
    for frame,meaning in [(0x2bf6,'Bones Park logo'),(0x2d9a,'Play Byte logo'),(0x2f9e,'present'),(0x2fb7,'Ugh title')]:
        ice(frame,f'{meaning}; 320x200 indexed pixels plus RGB6 palette')
    for frame in MUSIC_CALLS:
        a=frame*16
        # The starts are paragraph-aligned, independent of embedded ADLX lengths.
        starts=sorted(f*16 for f in MUSIC_CALLS)+[0x37a70]
        end=starts[starts.index(a)+1]
        n=struct.unpack_from('>I',mz.image,a+4)[0]+8
        add(a,a+n,'ADLX','AdLib track with 42-byte container prefix','verified-by-decode','C 0878:0AA9; SOUND 0664:15D3,176B')
        add(a+n,end,'padding',f'{end-a-n} zero bytes','verified-by-decode','ADLX root size')
    for a,b,pixel_end,ids in [(0x37a70,0x438a0,0x4389e,'217..297'),
            (0x438a0,0x4e830,0x4e830,'298..546'),(0x4e830,0x5b630,0x5b630,'547..661')]:
        add(a,pixel_end,'sprite pixels',f'IDs {ids}, column-major 8-bit indexed','verified-by-decode','GAME 013B:41FD')
        if pixel_end<b:
            add(pixel_end,b,'padding',f'{b-pixel_end} zero bytes','verified-by-decode','sprite directory endpoint')
    add(0x5b630,0x5c088,'sprite directory','662 records: u16 offset, u8 width, u8 height','verified-by-decode','GAME 013B:425A,43BC')
    add(0x5c088,0x5c090,'padding','8 zero bytes','verified-by-decode','end of directory')
    for a,b,kind,reader in DGROUP_OBJECTS:
        confidence='unknown' if a==0x3345 else 'supported-by-code'
        if 0x3349<=a<0x7970 or a in (0xee,0x492,0xd00,0x1020):
            confidence='verified-by-decode'
        add(0x5c090+a,0x5c090+b,'DGROUP',kind,confidence,reader)
    return sorted(rows)


class IceDecoder:
    """Translation of the bit and copy operations in game image 00605D..00618A."""

    def __init__(self, source, game_image, destination_seed):
        self.source = source
        self.game = game_image
        self.destination_seed = destination_seed
        self.match_events = []

    def _cs_byte(self, offset):
        p = GAME_CS_IMAGE + (offset & 0xFFFF)
        if not 0 <= p < len(self.game):
            raise ValueError(f'ICE table address outside image: CS:{offset:04X}')
        return self.game[p]

    def _cs_word(self, offset):
        return self._cs_byte(offset) | (self._cs_byte(offset + 1) << 8)

    def decode(self, header_end, output_size):
        if self.source[:4] != b'ICE!':
            raise ValueError('not an ICE! stream')
        if len(self.source) < 12:
            raise ValueError('truncated ICE! header')
        endpoint = int.from_bytes(self.source[4:8], 'big') - 1
        declared_size = int.from_bytes(self.source[8:12], 'big')
        if not 0 < declared_size <= 0xffff:
            raise ValueError('ICE size outside the DOS 16-bit destination window')
        if declared_size != output_size:
            raise ValueError(f'ICE! output field mismatch: {declared_size} != {output_size}')
        if endpoint != header_end or endpoint < 12 or endpoint >= len(self.source):
            raise ValueError(f'ICE! input endpoint mismatch: header={endpoint:04X}, object end={header_end:04X}')

        # 6089 loads [SI] into AH and decrements SI before entering 6099.
        si, ah, di = endpoint, self.source[endpoint], declared_size - 1
        # Keep the 16-bit window, but require every match to reference decoded
        # output. None of these streams needs bytes from the following segment.
        output = bytearray(0x10000)
        output[:min(len(self.destination_seed), 0x10000)] = self.destination_seed[:0x10000]
        self.partial_output = output
        self.events = []

        def bit():
            nonlocal si, ah
            carry = ah >> 7
            ah = (ah << 1) & 0xFF
            if ah == 0:
                if si <= 0:
                    raise ValueError('ICE bitstream underflow')
                byte = self.source[si - 1]
                si -= 1
                ah = ((byte << 1) | carry) & 0xFF
                carry = byte >> 7
            return carry

        def bits(count):
            count = count if count < 0x8000 else count - 0x10000
            value = 0
            # The helper always consumes one bit before its DEC/JNS loop,
            # even when CX enters negative. Callers that want zero bits test
            # the sign before calling it.
            iterations = max(1, count + 1)
            if iterations > 16:
                raise ValueError(f'ICE bit count out of range: {iterations}')
            for _ in range(iterations):
                value = ((value << 1) | bit()) & 0xFFFF
            return value

        def literal(value):
            nonlocal di
            if di < 0:
                raise ValueError('ICE literal copy crossed output start')
            output[di] = value
            di -= 1

        def literal_run():
            nonlocal si, di
            if bit() == 0:
                if si <= 0:
                    raise ValueError('ICE literal stream underflow')
                byte = self.source[si - 1]
                si -= 1
                literal(byte)
                return

            bp, bh = 0x4DE7, 4
            while True:
                bp = (bp - 2) & 0xFFFF
                encoded = bits(self._cs_word(bp))
                if encoded != self._cs_word(bp + 0x14):
                    break
                bh = (bh - 1) & 0xFF
                if bh & 0x80:
                    break
            count = (encoded + self._cs_word(bp + 0x0A)) & 0xFFFF
            if count >= len(self.source):
                raise ValueError(f'ICE literal run is implausibly large: {count + 1}')
            for _ in range(count + 1):
                if si <= 0:
                    raise ValueError('ICE literal run crossed stream start')
                byte = self.source[si - 1]
                si -= 1
                literal(byte)

        def match():
            nonlocal di
            match_start = di
            bp = 3
            while bit():
                bp -= 1
                if bp < 0:
                    break
            signed_count = self._cs_byte(bp + 0x4E06)
            dx = 0 if signed_count & 0x80 else bits(signed_count)
            bx = (self._cs_byte(bp + 0x4E0B) + dx) & 0xFFFF

            if bx == 0:
                if bit():
                    bp, count = 0x003F, 8
                else:
                    bp, count = 0xFFFF, 5
                dx = (bp + bits(count)) & 0xFFFF
            else:
                bp = 1
                while bit():
                    bp -= 1
                    if bp < 0:
                        break
                signed_count = self._cs_byte(bp + 0x4E10)
                dx = 0 if signed_count & 0x80 else bits(signed_count)
                bp = (bp << 1) & 0xFFFF
                dx = (dx + self._cs_word(bp + 0x4E15)) & 0xFFFF
                if dx & 0x8000:
                    dx = (dx - bx) & 0xFFFF

            source_index = (bx + di + 2 + dx) & 0xFFFF
            if source_index <= di:
                raise ValueError('ICE match does not refer to already decoded output')
            self.match_events.append((di, bx, dx, source_index))
            for _ in range(bx + 2):
                if not 0 <= source_index < declared_size:
                    raise ValueError(f'ICE back-reference outside decoded data: src={source_index:04X}')
                if di < 0:
                    raise ValueError(f'ICE back-reference crossed output start: start={match_start:04X} di={di:04X} bx={bx:04X} dx={dx:04X}')
                output[di] = output[source_index]
                di -= 1
                source_index -= 1

        tokens = 0
        while True:
            before = di
            if bit():
                literal_run()
                self.events.append(('literal', before, di))
                if di == -1:
                    break
            elif di == -1:
                break
            before = di
            match()
            self.events.append(('match', before, di))
            tokens += 1
            if tokens > declared_size * 2:
                raise ValueError('ICE token limit exceeded')
        if di != -1:
            raise ValueError(f'ICE! produced {declared_size - di - 1} bytes, expected {declared_size}')
        return bytes(output[:declared_size])


def ice_encode_tokens(data, events, distances):
    """Inverse of GAME's ICE dialect. Events run from the end of output backwards.

    Used both by the independent greedy packer and to audit original token traces.
    Trace replay is a codec test, never a claim of independently recovered packing.
    """
    ops = []
    def bits(value, count):
        if not 0 <= value < 1 << count:
            raise ValueError(f'cannot encode {value} in {count} bits')
        ops.extend(('bit',(value >> i)&1) for i in range(count-1,-1,-1))
    def literals(begin,end):
        n = begin-end
        bits(1,1)
        if n == 1:
            bits(0,1)
        else:
            bits(1,1)
            for base, count, escape in [(2,2,3),(5,2,3),(8,3,7),(15,8,255),(270,15,32767)]:
                if n-base < escape or count == 15:
                    bits(n-base,count)
                    break
                bits(escape,count)
        ops.extend(('byte',data[i]) for i in range(begin,end,-1))
    def match(length,distance):
        if length == 2:
            bits(0,1)
        elif length == 3:
            bits(2,2)
        elif length <= 5:
            bits(6,3); bits(length-4,1)
        elif length <= 9:
            bits(14,4); bits(length-6,2)
        else:
            bits(15,4); bits(length-10,10)
        if length == 2:
            if distance <= 64:
                bits(0,1); bits(distance-1,6)
            else:
                bits(1,1); bits(distance-65,9)
        elif distance == 1:
            bits(2,2); bits(0,5)
        elif length <= distance <= length+30:
            bits(2,2); bits(distance-length+1,5)
        elif length+31 <= distance <= length+286:
            bits(0,1); bits(distance-length-31,8)
        else:
            bits(3,2); bits(distance-length-287,12)
    need_top, di, mi = True, len(data)-1, 0
    for kind,begin,end in events:
        if begin != di or end >= begin:
            raise ValueError('invalid token trace')
        if kind == 'literal':
            literals(begin,end)
            need_top = False
        else:
            if need_top:
                bits(0,1)
            match(begin-end,distances[mi])
            mi += 1
            need_top = True
        di = end
    if di != -1:
        raise ValueError('incomplete token trace')
    if need_top:
        bits(0,1)
    # Standard Pack-Ice's final bitplane-transform flag. This DOS routine stops
    # at DI=FFFF and does not consume it; every original has the zero flag.
    bits(0,1)
    bitvalues = [v for kind,v in ops if kind == 'bit']
    first = len(bitvalues)%8
    consumed = [sum(v << (7-i) for i,v in enumerate(bitvalues[:first])) | (1 << (7-first))]
    at, remaining = 0, first
    for kind,value in ops:
        if kind == 'byte':
            consumed.append(value)
        else:
            if remaining == 0:
                consumed.append(sum(v << (7-i) for i,v in enumerate(bitvalues[at:at+8])))
                remaining = 8
            at += 1
            remaining -= 1
    payload = bytes(reversed(consumed))
    return b'ICE!' + struct.pack('>II',len(payload)+12,len(data)) + payload


def ice_pack(data, tie='near', lazy=False):
    """Greedy Pack-Ice 2.x token ranges, backward search, max match 1033.

    Independent of original compressed bytes. No original token recipe is stored.
    Near/far tie choice and one-byte lookahead are exposed for reproducibility probes.
    """
    from bisect import bisect_right
    pairs = {}
    for p in range(1,len(data)):
        pairs.setdefault(data[p-1:p+1],[]).append(p)
    def find(di):
        if di < 1:
            return 0,0
        candidates = pairs.get(data[di-1:di+1],[])
        j = bisect_right(candidates,di)
        best, distance = 1,0
        for src in candidates[j:]:
            dist = src-di
            if dist > 5415:
                break
            maximum = min(di+1,1033,dist if dist != 1 else 1033)
            if maximum < best or maximum == best and tie == 'near':
                continue
            if dist > maximum+4382 and dist > 576:
                continue
            n = 2
            while n < maximum and data[di-n] == data[src-n]:
                n += 1
            if n == 2 and dist > 576 or n > 2 and dist > n+4382:
                continue
            if n > best or n == best and tie == 'far':
                best, distance = n,dist
                if best == min(di+1,1033) and tie == 'near':
                    break
        return (best,distance) if best >= 2 else (0,0)
    events, distances = [],[]
    di, literal_start = len(data)-1,None
    while di >= 0:
        length,distance = find(di)
        if length and lazy and di > 1 and find(di-1)[0] > length+1:
            length = 0
        if length:
            if literal_start is not None:
                events.append(('literal',literal_start,di))
                literal_start = None
            events.append(('match',di,di-length))
            distances.append(distance)
            di -= length
        else:
            if literal_start is None:
                literal_start = di
            di -= 1
    if literal_start is not None:
        events.append(('literal',literal_start,-1))
    return ice_encode_tokens(data,events,distances)


def ice_pack235(data, window=0x1580):
    """Forward greedy selection used by Pack-Ice 2.35, uppercase DOS magic.

    Search policy checked against Benjamin Gerard's unice68 native 2.35 port:
    https://github.com/benjihan/py-icepacker/blob/main/unice68/unice68_pack.c
    The token encoder above is independently derived from the DOS consumer.
    """
    from bisect import bisect_left
    pairs = {}
    for p in range(len(data)-1):
        pairs.setdefault(data[p:p+2],[]).append(p)
    pos, literal_start = 0,0
    forward = []
    # The original search reads a byte at its endpoint; pad the host buffer to
    # reproduce that comparison without an out-of-bounds read.
    padded = data+b'\0'*64
    while pos+3 <= len(data):
        end = min(pos+1033,len(data))
        q = pos+1
        while True:
            value = padded[q]
            q += 1
            if value != data[pos] or q >= end:
                break
        run = q-pos-2
        best, distance = 1,0
        end = min(pos+window,len(data))
        candidates = pairs.get(data[pos:pos+2],[])
        for target in candidates[bisect_left(candidates,pos+2):]:
            if target >= end:
                break
            if best == 1033:
                break
            length = 0
            while True:
                equal = padded[pos+length] == padded[target+length]
                length += 1
                if not equal or pos+length > target or target+length >= end:
                    break
            length = min(length-1,1033)
            offset = target-pos-length+1
            if length > best and (length <= 2 or offset <= 0x111f):
                best, distance = length,target-pos
        if run > 1 and run >= best:
            best,distance = run,1
        if best == 1 or best == 2 and distance > 576:
            pos += 1
            continue
        if literal_start < pos:
            forward.append(('literal',literal_start,pos,0))
        forward.append(('match',pos,pos+best,distance))
        pos += best
        literal_start = pos
    if literal_start < len(data):
        forward.append(('literal',literal_start,len(data),0))
    events = [(kind,end-1,start-1) for kind,start,end,_ in reversed(forward)]
    distances = [distance for kind,_,_,distance in reversed(forward) if kind == 'match']
    return ice_encode_tokens(data,events,distances)


def decode_ice(mz, frame):
    if frame not in ICE_STREAMS:
        raise SystemExit(f'frame {frame:04X} is not a surveyed ICE! object')
    start, region_end = ICE_STREAMS[frame]
    stream = mz.image[start:region_end]
    endpoint = int.from_bytes(stream[4:8], 'big') - 1
    output_size = int.from_bytes(stream[8:12], 'big')
    seed = mz.image[0x0A670:0x0A670 + 0x10000]
    return IceDecoder(stream, mz.image, seed).decode(endpoint, output_size), endpoint, output_size


def _write_png(path, width, height, rgb):
    if len(rgb) != width * height * 3:
        raise ValueError(f'PNG pixel length mismatch: {path}')
    def chunk(tag, payload):
        return (struct.pack('>I', len(payload)) + tag + payload +
                struct.pack('>I', zlib.crc32(tag + payload) & 0xFFFFFFFF))
    raw = b''.join(b'\0' + rgb[y * width * 3:(y + 1) * width * 3] for y in range(height))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' +
                     chunk(b'IHDR', struct.pack('>2I5B', width, height, 8, 2, 0, 0, 0)) +
                     chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def _palette_rgb(palette):
    if len(palette) != 768:
        raise ValueError('expected 256 RGB triples')
    if max(palette, default=0) <= 63:
        return bytes((v * 255 + 31) // 63 for v in palette)
    return palette


def _indexed_rgb(pixels, palette):
    palette = _palette_rgb(palette)
    rgb = bytearray(len(pixels) * 3)
    for i, color in enumerate(pixels):
        rgb[3*i:3*i+3] = palette[3*color:3*color+3]
    return rgb


def render_decoded(frame, decoded, mz):
    base = f'{frame:04X}'
    raw_dir = OUT / 'decoded'
    png_dir = OUT / 'png'
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f'{base}.bin').write_bytes(decoded)
    if len(decoded) == 32000:
        return []  # This is the tile-map bank, rendered by dump_levels().
    if len(decoded) != 0xFD00:
        raise ValueError(f'no rendering layout for output size {len(decoded)}')

    path = png_dir / f'{base}.png'
    _write_png(path,320,200,_indexed_rgb(decoded[:64000],decoded[64000:]))
    return [path.name]


def validate():
    mz = MZ(IMAGE.read_bytes())
    if mz.identity() != load_json('oracle.json')['expanded']:
        raise SystemExit('expanded executable does not match metadata/oracle.json; run tools/oracle.py')
    start, end = 0x0A670, len(mz.image)
    cursor = start
    for a, b, kind, *_ in object_table(mz):
        if a != cursor or b <= a:
            raise SystemExit(f'object coverage error at {cursor:06X}: next is {a:06X}..{b:06X}')
        cursor = b
        if kind == 'padding' and any(mz.image[a:b]):
            raise ValueError(f'nonzero padding at {a:06X}')
    if cursor != end:
        raise SystemExit(f'object coverage ends {cursor:06X}, expected image end {end:06X}')
    if end != 0x63EBE:
        raise SystemExit(f'locked image size changed: expected scope end 63EBE, got {end:06X}')
    return mz


def decode_command(mz, frames):
    results = []
    for frame in frames:
        decoded, endpoint, declared = decode_ice(mz, frame)
        reference = (BUILD/'workers'/'data'/'ice_2bf6_reference.bin' if frame==0x2bf6
                     else OUT/f'ice_{frame:04x}_reference.bin')
        checked = reference.exists()
        if checked and reference.read_bytes() != decoded:
            raise ValueError(f'ICE {frame:04X} differs from retained routine reference')
        render_decoded(frame,decoded,mz)
        results.append(dict(frame=f'{frame:04X}',endpoint=endpoint,declared=declared,
            decoded=len(decoded),sha256=hashlib.sha256(decoded).hexdigest(),
            reference_equal=True if checked else None))
        print(f'{frame:04X}: decoded {len(decoded)} = header {declared}; routine reference={checked}')
    (OUT/'decode.json').write_text(json.dumps(results,indent=2)+'\n')


def repack_command(mz,frames):
    results=[]
    for frame in frames:
        data,_,_=decode_ice(mz,frame)
        packed=ice_pack235(data)
        start,_=ICE_STREAMS[frame]
        original=mz.image[start:start+struct.unpack_from('>I',mz.image,start+4)[0]]
        different=sum(a!=b for a,b in zip(packed,original))+abs(len(packed)-len(original))
        if IceDecoder(packed,mz.image,b'').decode(len(packed)-1,len(data)) != data:
            raise ValueError('packer round-trip mismatch')
        results.append(dict(frame=f'{frame:04X}',original=len(original),packed=len(packed),
            different_positions=different,equal=packed==original,
            sha256=hashlib.sha256(packed).hexdigest()))
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/f'python235_{frame:04X}.ice').write_bytes(packed)
        print(f'{frame:04X}: {len(packed)} bytes, {different} differing positions; exact={packed==original}',flush=True)
    (OUT/'repack235.json').write_text(json.dumps(results,indent=2)+'\n')
    if not all(r['equal'] for r in results):
        raise SystemExit(1)


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['list','decode','render','repack','levels','music','dgroup'])
    parser.add_argument('target',nargs='?')
    parser.add_argument('--all',action='store_true')
    args=parser.parse_args()
    mz=validate()
    if args.command=='list':
        rows=object_table(mz)
        for a,b,kind,description,confidence,reader in rows:
            print(f'{a:06X}..{b:06X} {b-a:6} {kind}: {description} | {confidence} | {reader}')
        print(f'coverage: {len(rows)} objects, {rows[-1][1]-rows[0][0]} bytes, exact')
    elif args.command in ('decode','repack'):
        if not args.all and not args.target:
            parser.error('specify a hexadecimal frame or --all')
        frames=sorted(ICE_STREAMS) if args.all else [int(args.target,16)]
        (decode_command if args.command=='decode' else repack_command)(mz,frames)
    elif args.command=='render':
        if not args.all:
            parser.error('render requires --all')
        decode_command(mz,sorted(ICE_STREAMS))
        sprites=graphics(mz)
        render_graphics(mz,sprites)
        dump_levels(mz,sprites,render=True)
        print(f'PNG output: {OUT / "png"}')
    elif args.command=='levels':
        dump_levels(mz,graphics(mz))
    elif args.command=='music':
        if args.target:
            print(json.dumps(parse_form(Path(args.target).read_bytes()),indent=2))
        else:
            music(mz)
            print('embedded FORM/8SVX samples: 0 (FORM substrings are text)')
    elif args.command=='dgroup':
        dgroup(mz)
        refs=dgroup_xrefs()
        print(f'{len(refs)} directly referenced DGROUP field offsets; dgroup_xrefs.json')


if __name__ == '__main__':
    main()


