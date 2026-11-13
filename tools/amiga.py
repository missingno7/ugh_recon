"""Static OFS/HUNK reader and recursive M68K listing. Never executes game code.

Addresses in reports are hunk-relative (h0:01234); synthetic relocated addresses
start at 0x10000, page-aligned. Only Capstone is required beyond Python.
"""
from __future__ import annotations
import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import struct
import zlib

import capstone as cs
from capstone import m68k as m

ROOT = Path(__file__).resolve().parents[1]
ADF = ROOT / 'assets/amiga/Ugh! (1992)(Play Byte).adf'
ADF_SHA256 = 'd2418ca9a3ebceab358dd2c46f0d4df8d0992540c2f91b39a2a28cbfde2ec9fc'
OUT = ROOT / 'build/amiga'


def u32(b, p=0):
    return struct.unpack_from('>I', b, p)[0]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=True) + '\n')


def extract(adf, dest):
    """Read OFS hash chains and linked data blocks, checking checksums/lengths."""
    assert adf[:4] == b'DOS\0' and len(adf) == 901120
    assert sha(adf) == ADF_SHA256, 'Static data anchors apply only to the documented ADF'
    visited = set()
    manifest = []

    def block(n):
        assert 2 <= n < len(adf) // 512, n
        b = adf[n*512:(n+1)*512]
        assert sum(struct.unpack('>128I', b)) & 0xffffffff == 0, ('checksum', n)
        return b

    def walk(n, parent=Path()):
        b = block(n)
        assert u32(b) == 2
        for k in range(72):
            child = u32(b, 24+4*k)
            while child:
                assert child not in visited, ('directory cycle', child)
                visited.add(child)
                h = block(child)
                assert u32(h) == 2
                name = h[433:433+h[432]].decode('latin1')
                assert name not in ('.', '..') and '/' not in name and '\\' not in name
                path = parent / name
                kind = struct.unpack_from('>i', h, 508)[0]
                if kind == 2:
                    walk(child, path)
                else:
                    assert kind == -3, (path, kind)
                    data = bytearray()
                    dn, seq, seen = u32(h, 16), 1, set()
                    while dn:
                        assert dn not in seen
                        seen.add(dn)
                        d = block(dn)
                        assert u32(d) == 8 and u32(d, 4) == child and u32(d, 8) == seq
                        count = u32(d, 12)
                        assert count <= 488
                        data.extend(d[24:24+count])
                        dn, seq = u32(d, 16), seq+1
                    assert len(data) == u32(h, 324), path
                    target = dest / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                    manifest.append(dict(path=path.as_posix(), block=child,
                                         size=len(data), sha256=sha(data)))
                child = u32(h, 496)
    walk(len(adf)//1024)
    return sorted(manifest, key=lambda r: r['path'].lower())


class Hunk:
    def __init__(self, data):
        self.raw = data
        self.hunks, self.relocs, self.symbols, self.debug = [], [], [], []
        self.pos = 0
        assert self.word() == 1011
        while (n := self.word()):
            self.take(n*4)
        count, first, last = self.word(), self.word(), self.word()
        assert first == 0 and last+1 == count
        sizes = []
        for _ in range(count):
            v = self.word()
            if v >> 30 == 3:
                self.word()  # extended memory attributes
            sizes.append(v & 0x3fffffff)
        current = -1
        while self.pos < len(data):
            tagpos = self.pos
            tag = self.word() & 0x3fffffff
            if tag in (1001, 1002, 1003):
                current += 1
                n = self.word()*4
                payload = self.take(n) if tag != 1003 else bytes(n)
                assert n <= sizes[current]*4
                self.hunks.append(dict(kind={1001:'CODE',1002:'DATA',1003:'BSS'}[tag],
                                       file_offset=tagpos+8, stored_size=n if tag!=1003 else 0,
                                       size=sizes[current]*4, data=bytearray(payload.ljust(sizes[current]*4,b'\0'))))
            elif tag == 1004:
                while (n := self.word()):
                    target = self.word()
                    for _ in range(n):
                        off = self.word()
                        self.relocs.append(dict(hunk=current, offset=off, target_hunk=target))
            elif tag == 1008:
                while (n := self.word()):
                    name = self.take(n*4).rstrip(b'\0').decode('latin1')
                    self.symbols.append(dict(hunk=current, name=name, offset=self.word()))
            elif tag in (1000, 1009):
                payload = self.take(self.word()*4)
                if tag == 1009:
                    self.debug.append(dict(hunk=current, size=len(payload), preview=payload[:64].hex()))
            elif tag != 1010:
                raise ValueError(f'unsupported HUNK {tag} at {tagpos:x}')
        assert len(self.hunks) == count
        base = 0x10000
        for h in self.hunks:
            h['base'] = base
            base += (h['size']+4095) & ~4095
        for r in self.relocs:
            h = self.hunks[r['hunk']]
            off = r['offset']
            assert off%2 == 0 and off+4 <= h['size']
            r['addend'] = u32(h['data'], off)
            r['address'] = self.hunks[r['target_hunk']]['base'] + r['addend']
            struct.pack_into('>I', h['data'], off, r['address'])
        # An independent subtraction check also catches duplicate relocation
        # sites; the file bytes stay immutable and are never repatched.
        restored = [bytearray(h['data']) for h in self.hunks]
        for r in self.relocs:
            struct.pack_into('>I',restored[r['hunk']],r['offset'],
                             u32(restored[r['hunk']],r['offset'])-self.hunks[r['target_hunk']]['base'])
        for h, original in zip(self.hunks,restored):
            if h['stored_size']:
                assert original[:h['stored_size']] == data[h['file_offset']:h['file_offset']+h['stored_size']]

    def take(self, n):
        p = self.pos
        self.pos += n
        assert self.pos <= len(self.raw)
        return self.raw[p:self.pos]

    def word(self):
        return u32(self.take(4))

    def locate(self, addr):
        for k, h in enumerate(self.hunks):
            if h['base'] <= addr < h['base']+h['size']:
                return k, addr-h['base']
        return None

    def coord(self, addr):
        p = self.locate(addr)
        return f'h{p[0]}:{p[1]:05x}' if p else f'${addr:08x}'

    def summary(self):
        return dict(sha256=sha(self.raw), size=len(self.raw),
                    hunks=[{k:v for k,v in h.items() if k!='data'} for h in self.hunks],
                    relocations=self.relocs, symbols=self.symbols, debug=self.debug)


def analyze(hf, dest, name):
    # 020 decodes the startup's guarded MOVEC as well as the game's 68000 code.
    md = cs.Cs(cs.CS_ARCH_M68K, cs.CS_MODE_BIG_ENDIAN | cs.CS_MODE_M68K_020)
    md.detail = True
    todo, insns, occupied, origins = deque(), {}, {}, {}
    trusted = True
    seeds, xrefs, edges, indirect, rejected = defaultdict(set), [], [], [], []

    def code(addr):
        loc = hf.locate(addr)
        return loc and not addr & 1 and hf.hunks[loc[0]]['kind'] == 'CODE'

    def seed(addr, reason):
        if code(addr):
            seeds[addr].add(reason)
            todo.append(addr)

    seed(hf.hunks[0]['base'], 'entry')
    # First follow direct flow. Later, relocation-backed stored pointers are
    # candidates, explicitly distinguished from entry/direct-call routines.
    def drain():
        while todo:
            addr = todo.popleft()
            while code(addr) and addr not in insns:
                if addr in occupied:
                    rejected.append(dict(address=hf.coord(addr), reason='overlapping decode'))
                    break
                k, off = hf.locate(addr)
                i = next(md.disasm(bytes(hf.hunks[k]['data'][off:off+22]), addr, 1), None)
                if not i or i.mnemonic.startswith('dc.') or i.size < 2:
                    rejected.append(dict(address=hf.coord(addr), reason='invalid instruction'))
                    break
                if any(a in occupied for a in range(addr,addr+i.size)):
                    break
                insns[addr] = i
                origins[addr] = 'entry/direct-flow' if trusted else 'pointer-candidate flow'
                occupied.update((a,addr) for a in range(addr,addr+i.size))
                refs = []
                for op in i.operands:
                    target = None
                    if op.type == m.M68K_OP_BR_DISP:
                        target = addr+2+op.br_disp.disp
                    elif op.type == m.M68K_OP_MEM:
                        if op.address_mode in (m.M68K_AM_ABSOLUTE_DATA_LONG,m.M68K_AM_ABSOLUTE_DATA_SHORT):
                            target = op.imm & 0xffffffff
                        elif op.address_mode == m.M68K_AM_PCI_DISP:
                            target = addr+2+op.mem.disp
                    elif op.type == m.M68K_OP_IMM and hf.locate(op.imm):
                        target = op.imm
                    if target is not None:
                        refs.append(target)
                        if hf.locate(target):
                            xrefs.append(dict(source=hf.coord(addr), target=hf.coord(target),
                                              instruction=f'{i.mnemonic} {i.op_str}'))
                mn = i.mnemonic.split('.')[0]
                branch = mn.startswith('b') and mn not in ('bchg','bclr','bset','btst') or mn.startswith('db')
                transfer = branch or mn in ('jsr','jmp')
                if transfer:
                    targets = refs[-1:]  # DBcc's final operand is the branch displacement
                    for target in targets:
                        edges.append(dict(source=hf.coord(addr),target=hf.coord(target),kind=mn))
                        if mn in ('bsr','jsr'):
                            seed(target,'direct call' if trusted else 'candidate-flow direct call')
                        elif code(target):
                            todo.append(target)
                    if not targets:
                        indirect.append(dict(address=hf.coord(addr),instruction=f'{i.mnemonic} {i.op_str}'))
                if mn in ('rts','rte','rtr','jmp','bra','illegal','stop'):
                    break
                addr += i.size
    drain()
    trusted = False
    # Absolute pointers to CODE hunks can also designate embedded data. Keep
    # their provenance; these seeds do NOT establish routine identity alone.
    for r in hf.relocs:
        site = hf.hunks[r['hunk']]['base']+r['offset']
        # Includes addresses materialized by LEA/MOVE (interrupt callbacks,
        # Exec Supervisor entry, and callback tables filled during startup).
        seed(r['address'],f'code address at {hf.coord(site)} (candidate)')
    drain()
    # Common hand-written dispatch: JMP (d8,PC,Dn.W), preceded by a bounded
    # index, over a vector of BRA.W/BRA.S or JMP instructions. Decode only
    # consecutive branch stubs, never arbitrary words as addresses.
    for _ in range(3):
        before = len(insns)
        for i in list(insns.values()):
            if i.mnemonic != 'jmp' or not i.operands:
                continue
            o = i.operands[0]
            if o.address_mode != m.M68K_AM_PCI_INDEX_8_BIT_DISP:
                continue
            target = i.address+2+o.mem.disp
            for _slot in range(128):
                loc = hf.locate(target)
                if not loc:
                    break
                k, off = loc
                j = next(md.disasm(bytes(hf.hunks[k]['data'][off:off+8]),target,1),None)
                if not j or j.mnemonic.split('.')[0] not in ('bra','jmp'):
                    break
                seed(target,f'branch-stub jump table from {hf.coord(i.address)}')
                target += j.size
        drain()
        if len(insns) == before:
            break
    routines = []
    for a in sorted(seeds):
        if a in insns:
            routines.append(dict(address=hf.coord(a),synthetic_address=a,
                                 provenance=origins[a],reasons=sorted(seeds[a])))
    bysource = defaultdict(list)
    for x in xrefs:
        bysource[x['source']].append(x['target'])
    with (dest/f'{name}.lst').open('w') as f:
        f.write('; Static recursive decode, relocated; candidate pointer seeds may be data.\n')
        for a, i in sorted(insns.items()):
            if a in seeds:
                f.write('\n; '+', '.join(sorted(seeds[a]))+'\n')
            suffix = ' ; '+', '.join(bysource[hf.coord(a)]) if bysource[hf.coord(a)] else ''
            if origins[a] != 'entry/direct-flow':
                suffix += ' ; candidate flow'
            f.write(f'{hf.coord(a):12} {i.bytes.hex():22} {i.mnemonic:10} {i.op_str}{suffix}\n')
    dump(dest/f'{name}.routines.json',routines)
    dump(dest/f'{name}.xrefs.json',xrefs)
    dump(dest/f'{name}.flow.json',dict(edges=edges,indirect=indirect,rejected=rejected,
                                     instructions=len(insns),decoded_bytes=len(occupied),
                                     entry_flow_bytes=sum(i.size for a,i in insns.items() if origins[a]=='entry/direct-flow'),
                                     caveat='Stored pointers to CODE may be embedded data; not complete control-flow proof.'))
    for k,h in enumerate(hf.hunks):
        (dest/f'{name}.h{k}.bin').write_bytes(h['data'])
    dump(dest/f'{name}.hunks.json',hf.summary())
    return dict(file=name,hunks=len(hf.hunks),relocations=len(hf.relocs),
                instructions=len(insns),routines_or_candidates=len(routines),indirect=len(indirect))


def bitmap(raw):
    """JOKE is a FORM-like ILBM wrapper, not executable compression.

    Decode the BODY's signed-byte literal/repeat runs as read at t h3:00210.
    In particular 80 means 129 repeats in this reader, not a no-op.
    """
    assert raw[:4] in (b'JOKE',b'FORM') and raw[8:12] == b'ILBM'
    end = u32(raw,4)+8
    assert end <= len(raw)
    chunks, p = {}, 12
    while p < end:
        tag, n = raw[p:p+4].decode('ascii'), u32(raw,p+4)
        assert p+8+n <= end
        chunks[tag] = raw[p+8:p+8+n]
        p += 8+n+(n&1)
    assert p == end
    bm = chunks['BMHD']
    w, h = struct.unpack_from('>HH',bm)
    planes, masking, compression = bm[8:11]
    assert compression in (0,1) and masking in (0,1,2)
    body = chunks['BODY']
    decoded, p, repeat80 = bytearray(), 0, 0
    if compression == 0:
        decoded.extend(body)
    else:
        while p < len(body):
            control = body[p]; p += 1
            if control < 128:
                n = control+1
                assert p+n <= len(body)
                decoded.extend(body[p:p+n]); p += n
            else:
                repeat80 += control == 128
                assert p < len(body)
                decoded.extend(body[p:p+1]*(257-control)); p += 1
    stride = ((w+15)//16)*2
    rowplanes = planes+(masking==1)
    assert len(decoded) == stride*h*rowplanes, (w,h,len(decoded),stride*h*rowplanes)
    pixels = bytes(sum(((decoded[(y*rowplanes+plane)*stride+x//8] >> (7-x%8))&1)<<plane
                       for plane in range(planes)) for y in range(h) for x in range(w))
    return dict(width=w,height=h,planes=planes,masking=masking,compression=compression,
                chunks={k:len(v) for k,v in chunks.items()},repeat80=repeat80,
                trailing_bytes=raw[end:].hex(),
                planar_sha256=sha(decoded),pixels_sha256=sha(pixels)), pixels, chunks.get('CMAP',b'')


def png(path,w,h,pixels,palette):
    def chunk(tag,data):
        return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    colors = palette.ljust(768,b'\0')
    rows = b''.join(b'\0'+b''.join(colors[v*3:v*3+3] for v in pixels[y*w:(y+1)*w])
                    for y in range(h))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+
                     chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b''))


def content(hf, dest, files):
    """Game-specific static data anchors; all offsets refer to this disk's t."""
    b = bytes(hf.hunks[8]['data']); base = hf.hunks[8]['base']
    word = lambda p: struct.unpack_from('>H',b,p)[0]
    def ptr(p):
        value = u32(b,p)-base
        assert 0 <= value < len(b), (p,value)
        return value
    def terminated(p,stride,read):
        result = []
        while word(p) != 65535:
            assert len(result)<100
            result.append(read(p)); p += stride
        return result
    def platform(value):
        n, rem = divmod(value-(base+0x506a),18)
        assert 0<=n<10 and rem==0, hex(value)
        return n
    def itinerary(p):
        return terminated(p,6,lambda q:[platform(u32(b,q)),word(q+4)])
    orders = []
    for players,ps,os,count in ((1,0x2fa,0xb330,69),(2,0x716,0xb446,81)):
        passwords = []
        for n in range(count):
            end = b.index(0,ps)
            assert b[end+1] == n+1
            passwords.append(bytes(c^42 for c in b[ps:end]).decode('ascii'))
            ps = end+2
        assert b[ps] == 255 and word(os+count*4) == 65535
        for n in range(count):
            r = ptr(os+4*n); tp=ptr(r+18)
            text = b[tp:b.index(0,tp)]
            plats = terminated(ptr(r+2),18,lambda q:list(struct.unpack_from('>9H',b,q)))
            actors = terminated(ptr(r+6),12,lambda q:dict(descriptor=f'h8:{ptr(q):05x}',
                initial_platform=platform(u32(b,q+4)) if u32(b,q+4) else None,
                itinerary=itinerary(ptr(q+8)) if u32(b,q+8) else None))
            enemies = terminated(ptr(r+10),12,lambda q:dict(descriptor=f'h8:{ptr(q):05x}',
                raw=b[q+4:q+12].hex(),platform=platform(u32(b,q+4))
                if base+0x506a <= u32(b,q+4) < base+0x506a+180 else None,
                parameters=[word(q+8),word(q+10)]))
            orders.append(dict(players=players,number=n+1,password=passwords[n],record=f'h8:{r:05x}',
                map=word(r)//320,title_raw=text.hex(),title=text.replace(b'\x80',b'').decode('ascii').replace('\r',' / '),
                passengers=word(r+14),mutable_remaining=word(r+16),weather=b[r+22],
                reserved23=b[r+23],player1=list(struct.unpack_from('>HH',b,r+24)),
                player2=list(struct.unpack_from('>HH',b,r+28)),water=word(r+32),
                water_delta=struct.unpack_from('>h',b,r+34)[0],reserved36=word(r+36),
                platforms=plats,actors=actors,enemies=enemies))
    assert len({r['record'] for r in orders}) == 81
    dump(dest/'levels.json',orders)
    descriptors=[]
    for family,starts,count,cbcount in (
            ('actor',[0x5a86+126*k for k in range(8)],126,19),
            ('enemy',[0x5efa,0x5f68,0x5fd6,0x6044],110,13),
            ('item',[0x610e+30*k for k in range(11)],30,4)):
        for p in starts:
            callbacks_at=8 if family!='item' else 4
            callbacks=[dict(offset=callbacks_at+4*k,
                            target=hf.coord(u32(b,p+callbacks_at+4*k))) for k in range(cbcount)]
            descriptors.append(dict(family=family,address=f'h8:{p:05x}',size=count,
                geometry=list(struct.unpack_from('>4H' if family!='item' else '>2H',b,p)),
                callbacks=callbacks,raw_relocated=b[p:p+count].hex()))
    dump(dest/'descriptors.json',descriptors)
    layouts=[]
    for name,start,stride,count in (('platform',0x506a,18,10),('object',0x5120,34,26),
                                    ('actor',0x59e4,32,5),('enemy',0x5e76,26,5),
                                    ('item',0x60b2,18,5)):
        assert word(start+stride*count)==65535
        layouts.append(dict(name=name,address=f'h8:{start:05x}',stride=stride,count=count,
                            sentinel=f'h8:{start+stride*count:05x}'))
    dump(dest/'layouts.json',layouts)
    formats=[]; images=dest/'images'; images.mkdir(exist_ok=True)
    for rec in files:
        raw=(dest/'files'/rec['path']).read_bytes()
        info=dict(path=rec['path'],magic=raw[:12].hex())
        if raw[:4] in (b'JOKE',b'FORM') and raw[8:12] == b'ILBM':
            meta,pixels,palette=bitmap(raw)
            info.update(format='ILBM',**meta)
            png(images/(Path(rec['path']).name+'.png'),meta['width'],meta['height'],pixels,palette)
        elif raw[:4]==b'\0\0\x03\xf3':
            try:
                obj=Hunk(raw)
                info.update(format='HUNK',hunks=len(obj.hunks),sha256=sha(raw))
            except (ValueError,AssertionError,struct.error) as error:
                info.update(format='HUNK (unsupported)',error=str(error))
        else:
            info['format']='other'
        info['embedded_hunk_headers']=[]
        for p in range(4,len(raw)-4,2):
            if raw[p:p+4]==b'\0\0\x03\xf3':
                try:
                    nested=Hunk(raw[p:])
                    candidate=dict(offset=p,valid=True,hunks=len(nested.hunks))
                except (ValueError,AssertionError,struct.error,IndexError):
                    candidate=dict(offset=p,valid=False)
                info['embedded_hunk_headers'].append(candidate)
        formats.append(info)
    dump(dest/'formats.json',formats)
    # Optional comparison uses the existing DOS decoder read-only, never its
    # generated JSON or a reference derived from this Amiga output.
    dosfile=ROOT/'build/oracle/UGH_X.EXE'
    if dosfile.exists():
        from common import MZ
        from dataprobe import levels
        raw=dosfile.read_bytes()
        lock=json.loads((ROOT/'metadata/oracle.json').read_text())
        assert sha(raw) == lock['expanded']['file_sha256'], 'DOS expansion differs from lock'
        mz=MZ(raw); maps,doslevels=levels(mz)
        raster=(dest/'files/Raster').read_bytes()
        assert len(raster)==len(maps)==32000
        differences=[dict(map=p//320,x=p%20,y=p%320//20,amiga=a,dos=d)
                     for p,(a,d) in enumerate(zip(raster,maps)) if a!=d]
        comparison=[]
        dgroup=mz.image[0x5c090:]
        actor_types={f'h8:{0x5a86+126*k:05x}':0x7720+74*k for k in range(8)}
        enemy_types=dict(zip(('h8:05efa','h8:05f68','h8:05fd6','h8:06044'),
                             (0x7630,0x766c,0x76a8,0x76e4)))
        def dos_itinerary(p):
            result=[]
            while struct.unpack_from('<H',dgroup,p)[0]!=65535:
                assert len(result)<100
                result.append(list(struct.unpack_from('<HH',dgroup,p))); p+=4
            return result
        amiga_rewards=[(ptr(p)-0x610e)//30 for p in range(0xc194,0xc1b8,4)]
        dos_rewards=[(struct.unpack_from('<H',dgroup,p)[0]-0x7970)//20
                     for p in range(0x3cb3,0x3cc5,2)]
        assert word(0xc1b8)==65535 and struct.unpack_from('<H',dgroup,0x3cc5)[0]==65535
        assert all((ptr(p)-0x610e)%30==0 for p in range(0xc194,0xc1b8,4))
        assert all(0<=v<11 for v in amiga_rewards+dos_rewards)
        for a,d in zip(orders,doslevels):
            assert (a['players'],a['number']) == (d['players'],d['number'])
            fields=('map','passengers','weather','player1','player2','water','water_delta','title')
            diff={k:dict(amiga=a[k],dos=d[k]) for k in fields if a[k]!=d[k]}
            pdiff=[]
            if len(a['platforms'])!=len(d['platforms']):
                pdiff.append('count')
            else:
                pdiff=[dict(index=i,amiga=ap,dos=dp) for i,(ap,dp) in enumerate(zip(a['platforms'],d['platforms'])) if ap[:8]!=dp]
            adiff=[]; ediff=[]
            if len(a['actors'])!=len(d['actors']):
                adiff.append(dict(field='count'))
            for i,(aa,dd) in enumerate(zip(a['actors'],d['actors'])):
                assert actor_types[aa['descriptor']]==dd[0]
                if aa['itinerary'] is not None:
                    steps=dos_itinerary(dd[2])
                    if aa['itinerary']!=steps:
                        adiff.append(dict(index=i,field='itinerary',amiga=aa['itinerary'],dos=steps,
                                          dos_pointer=f'5C09:{dd[2]:04x}'))
                elif aa['initial_platform']!=dd[1]:
                    adiff.append(dict(index=i,field='stone platform'))
            if len(a['enemies'])!=len(d['enemies']):
                ediff.append(dict(field='count'))
            for i,(aa,dd) in enumerate(zip(a['enemies'],d['enemies'])):
                assert enemy_types[aa['descriptor']]==dd[0]
                if dd[0] in (0x766c,0x76e4):
                    assert aa['platform']==dd[1]
                if dd[0]==0x7630:
                    values=list(struct.unpack('>IHH',bytes.fromhex(aa['raw'])))
                    if values!=dd[1:]:ediff.append(dict(index=i,amiga=values,dos=dd[1:]))
                elif dd[0]==0x766c:
                    if aa['parameters']!=dd[2:]:ediff.append(dict(index=i,field='parameters'))
                elif dd[0]==0x76a8:
                    values=list(struct.unpack('>4H',bytes.fromhex(aa['raw'])))
                    if values!=dd[1:]:ediff.append(dict(index=i,amiga=values,dos=dd[1:]))
            comparison.append(dict(players=a['players'],number=a['number'],amiga=a['record'],
                dos='5C09:'+d['record'],scalar_or_title_differences=diff,platform_differences=pdiff,
                actor_differences=adiff,enemy_differences=ediff,
                password=dict(amiga=a['password'],dos=d['password'])))
        dump(dest/'dos-comparison.json',dict(dos_expanded_sha256=sha(raw),
            note='Static data comparison only; identical records do not prove behaviour.',
            raster_amiga_sha256=sha(raster),raster_dos_sha256=sha(maps),
            tile_differences=differences,levels=comparison,
            reward_order=dict(amiga=amiga_rewards,dos=dos_rewards,equal=amiga_rewards==dos_rewards)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--adf', type=Path, default=ADF)
    p.add_argument('--out', type=Path, default=OUT)
    a = p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    adf = a.adf.read_bytes()
    files = extract(adf,a.out/'files')
    dump(a.out/'disk.json',dict(adf_sha256=sha(adf),files=files))
    results = []
    for name in ('t','loader','install'):
        hf = Hunk((a.out/'files'/name).read_bytes())
        results.append(analyze(hf,a.out,name))
        if name == 't':
            game = hf
    content(game,a.out,files)
    dump(a.out/'summary.json',dict(capstone=cs.__version__,programs=results))
    print(json.dumps(dict(files=len(files),programs=results),indent=2))


if __name__ == '__main__':
    main()
