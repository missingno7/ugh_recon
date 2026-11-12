"""Rebuild the TLINK runtime probe and compare its mapped _TEXT with UGH."""
from collections import Counter
from pathlib import Path
import re
import sys

from common import MZ, TOOLS, BUILD
from dos import dos
from omf import library, parse

ROOT = Path(__file__).resolve().parents[1]
WORK = BUILD / 'workers' / 'runtime' / 'probe'
IMAGE = BUILD / 'oracle' / 'UGH_X.EXE'
LIBDIR = TOOLS / 'borland-c++-3.0' / 'files' / 'LIB' / 'HLIB'
MAP_ROW = re.compile(r'^\s*([0-9A-F]+):([0-9A-F]+)\s+([0-9A-F]+)\s+'
                     r'C=([^ ]+)\s+S=([^ ]+)\s+G=([^ ]+)\s+M=(\S+)')
PUB_ROW = re.compile(r'^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?(\S+)\s*$')


def width(loc):
    return {0: 1, 1: 2, 2: 2, 3: 4, 4: 1, 5: 2, 9: 4}.get(loc, 0)


def _text(mod):
    return next((s for s in mod.segments if s['name'] == '_TEXT'), None)


def load_maps(path):
    rows, pubs = [], {}
    for line in path.read_text(errors='replace').splitlines():
        m = MAP_ROW.match(line)
        if m:
            frame, off, size = (int(m.group(i), 16) for i in (1, 2, 3))
            rows.append(dict(frame=frame, offset=off, size=size, cls=m[4],
                             segment=m[5], group=m[6], module=m[7]))
            continue
        p = PUB_ROW.match(line)
        if p:
            pubs[p[3].upper()] = (int(p[1], 16), int(p[2], 16))
    return rows, pubs


def main():
    if not IMAGE.exists():
        sys.exit('missing build/oracle/UGH_X.EXE; run python tools/oracle.py')
    mz = MZ(IMAGE.read_bytes())
    # Build every run. Source generation and tools are pinned / staged by this script.
    sys.path.insert(0, str(BUILD / 'workers' / 'runtime'))
    from makeprobe import build_probe
    libsize, libmembers = library((LIBDIR / 'CH.LIB').read_bytes())
    libmods = {name.upper(): parse(blob) for name, blob, _ in libmembers}
    c0 = parse((LIBDIR / 'C0H.OBJ').read_bytes())
    tasm0, tlink0 = build_probe(0)
    rows0, _ = load_maps(WORK / 'P.MAP')
    files_row0 = next((r for r in rows0 if r['module'].upper() == 'FILES' and
                       r['segment'] == '_DATA' and r['group'] == 'DGROUP'), None)
    files_mod = libmods.get('FILES')
    files_seg = next((s for s in files_mod.segments if s['name'] == '_DATA'), None) if files_mod else None
    if not files_row0 or not files_seg:
        sys.exit('baseline map or FILES _DATA contribution missing')
    raw = bytearray(files_seg['size']); covered_data = bytearray(files_seg['size'])
    for d in files_mod.data:
        if d['segment'] == files_seg['index']:
            raw[d['offset']:d['offset']+len(d['data'])] = d['data']
            covered_data[d['offset']:d['offset']+len(d['data'])] = b'\1'*len(d['data'])
    masked = set()
    for f in files_mod.fixups:
        if f.segment == files_seg['index']:
            masked.update(range(f.offset, min(files_seg['size'], f.offset+width(f.location))))
    signature = [i for i in range(files_seg['size']) if covered_data[i] and i not in masked]
    original_dgroup = mz.image[0x5c09*16:0x5c09*16+32302]
    anchors = [p for p in range(len(original_dgroup)-files_seg['size']+1)
               if all(original_dgroup[p+i] == raw[i] for i in signature)]
    if len(anchors) != 1:
        sys.exit(f'FILES data anchor is ambiguous: {len(anchors)} positions')
    files_anchor = anchors[0]
    pad_size = files_anchor - files_row0['offset']
    if pad_size < 0:
        sys.exit(f'FILES anchor precedes baseline map location: {pad_size}')
    tasm_out, tlink_out = build_probe(pad_size)
    print(tasm_out.strip())
    print(tlink_out.strip())
    probe_mz = MZ((WORK / 'P.EXE').read_bytes())
    rows, publics = load_maps(WORK / 'P.MAP')
    probe_obj = parse((WORK / 'P.OBJ').read_bytes())
    probe_rows = [r for r in rows if r['frame'] == 0 and r['segment'] == '_TEXT']
    p_row = next((r for r in probe_rows if r['module'].upper() == 'P.ASM'), None)
    if not p_row:
        sys.exit('probe map has no P.ASM _TEXT contribution')
    p_size = p_row['size']
    p_start = p_row['offset']
    modules = {'C0.ASM': c0, 'P.ASM': probe_obj, **libmods}
    dgroup_frame = next((r['frame'] for r in rows if r['group'] == 'DGROUP'), None)

    def normalized(start):
        return start if start < p_start else start - p_size

    probe_relocs = {(seg, off) for off, seg in probe_mz.relocs}
    orig_relocs = {(seg, off) for off, seg in mz.relocs}

    def symaddr(name):
        return publics.get(name.upper())

    def orig_frame(probe_frame, symbol=''):
        if probe_frame == 0: return 0
        if probe_frame == dgroup_frame: return 0x5c09
        if symbol.upper() == '_MAIN': return 0x013b
        return None

    def verify_fixup(row, mod, f, tseg):
        """Check this fixup against TLINK output, translating probe-only bases."""
        pa = row['offset'] + f.offset
        ia = normalized(row['offset']) + f.offset
        w = width(f.location)
        pb = probe_mz.image[pa:pa+w]
        ib = mz.image[ia:ia+w]
        target_name = ''
        target_addr = None
        if f.target_method == 2 and f.target_datum:
            target_name = mod.externals[f.target_datum-1]['name'].upper()
            target_addr = symaddr(target_name)
        if f.location == 3 and f.offset > 0:
            # Far call to the same _TEXT output segment: 9A off16 seg16 becomes
            # 90 0E E8 rel16, with no MZ relocation on the deleted segment word.
            startp, starti = pa - 1, ia - 1
            if target_addr and target_addr[0] == 0:
                pd = int.from_bytes(probe_mz.image[startp+3:startp+5], 'little', signed=True)
                idis = int.from_bytes(mz.image[starti+3:starti+5], 'little', signed=True)
                poff = target_addr[1] - (startp + 5)
                ioff = normalized(target_addr[1]) - (starti + 5)
                return (probe_mz.image[startp:startp+3] == b'\x90\x0e\xe8'
                        and mz.image[starti:starti+3] == b'\x90\x0e\xe8'
                        and pd == poff and idis == ioff
                        and (0, startp+3) not in probe_relocs
                        and (0, starti+3) not in orig_relocs)
            # The dummy probe main is intentionally in MAINSEG. In UGH the
            # far call remains a far call to the game segment 013B.
            if target_name == '_MAIN' and target_addr:
                po = int.from_bytes(probe_mz.image[startp+1:startp+3], 'little')
                io = int.from_bytes(mz.image[starti+1:starti+3], 'little')
                ps = int.from_bytes(probe_mz.image[startp+3:startp+5], 'little')
                iseg = int.from_bytes(mz.image[starti+3:starti+5], 'little')
                return (probe_mz.image[startp] == 0x9a and mz.image[starti] == 0x9a
                        and po == target_addr[1] and ps == target_addr[0]
                        and io == 0x0008 and iseg == 0x013b
                        and (0, starti+3) in orig_relocs)
            # Far pointers in data remain four bytes. Compare both resolved
            # components, translating the probe's later _TEXT targets back.
            if target_addr:
                po, ps = int.from_bytes(pb[:2], 'little'), int.from_bytes(pb[2:4], 'little')
                io, ins = int.from_bytes(ib[:2], 'little'), int.from_bytes(ib[2:4], 'little')
                return (po == target_addr[1] and ps == target_addr[0]
                        and io == normalized(target_addr[1])
                        and ins == orig_frame(target_addr[0], target_name))
        if pb == ib:
            return True
        if f.location == 2:
            # BASE16 fixups to _TEXT or DGROUP become TLINK MZ relocation words.
            pf, inf = int.from_bytes(pb, 'little'), int.from_bytes(ib, 'little')
            expected_probe = expected_image = None
            if f.frame_method == 5 and target_addr:
                expected_probe = target_addr[0]
                expected_image = orig_frame(target_addr[0], target_name)
            elif f.frame_method == 5 and f.target_method == 1 and f.target_datum:
                grp = next((g for g in mod.groups if g['index'] == f.target_datum), None)
                if grp and grp['name'].upper() == 'DGROUP':
                    expected_probe, expected_image = dgroup_frame, 0x5c09
            elif f.frame_method == 5 and f.target_method == 0 and f.target_datum:
                target_seg = next((s for s in mod.segments if s['index'] == f.target_datum), None)
                if target_seg:
                    outrow = next((r for r in rows if r['module'].upper() == mod.module.upper()
                                   and r['segment'] == target_seg['name']), None)
                    # Empty far-data aliases can share the DGROUP frame in this link.
                    if target_seg['name'] == '_TEXT': expected_probe, expected_image = 0, 0
                    elif outrow and outrow['frame'] == dgroup_frame:
                        expected_probe, expected_image = dgroup_frame, 0x5c09
            if expected_probe is not None and expected_image is not None:
                return pf == expected_probe and inf == expected_image
        if f.location == 1:
            pv = int.from_bytes(pb, 'little'); iv = int.from_bytes(ib, 'little')
            if target_addr:
                ef = target_addr[0]; eo = target_addr[1]
                if ef == 0:
                    return iv == normalized(eo) and pv == eo
                if ef == dgroup_frame:
                    return iv == eo and pv == eo
            # Segment-relative local _TEXT offsets shift by the probe caller stub.
            if f.target_method == 0 and f.target_datum:
                target_seg = next((s for s in mod.segments if s['index'] == f.target_datum), None)
                if target_seg and target_seg['name'] == '_TEXT':
                    expected = pv - p_size if pv >= p_start + p_size else pv
                    return iv == expected
            return pv == iv
        return pb == ib

    map_end = max((normalized(r['offset']) + r['size'] for r in probe_rows
                   if r['module'].upper() != 'P.ASM'), default=0)
    original = mz.image[:map_end]

    print(f'CH.LIB dictionary page={libsize}; probe _TEXT P.ASM={p_start:04X}-{p_start+p_size:04X}')
    print('member       probe range     image range     bytes  fixups checked  verdict')
    all_good = True
    unknown = []
    unresolved_fixups = []
    covered = bytearray(len(original))
    for row in probe_rows:
        name = row['module'].upper()
        if name == 'P.ASM':
            continue
        mod = modules.get(name)
        tseg = _text(mod) if mod else None
        start, size = row['offset'], row['size']
        image_start = normalized(start)
        image_end = image_start + size
        if size == 0:
            print(f'{name:12s} {start:04X}-{start:04X} {image_start:04X}-{image_end:04X} '
                  f'{0:5d} {0:14d} zero-length')
            continue
        if not tseg or size > tseg['size']:
            all_good = False; unknown.append((image_start, image_end, name, 'no matching OMF _TEXT'))
            print(f'{name:12s} {start:04X}-{start+size:04X} {image_start:04X}-{image_end:04X} '
                  f'{0:5d} {0:14d} UNKNOWN: no matching OMF _TEXT')
            continue
        fixups = [f for f in mod.fixups if f.segment == tseg['index']]
        mask = set()
        for f in fixups:
            mask.update(range(f.offset, min(size, f.offset + width(f.location))))
        checked = 0
        mismatches = []
        for i in range(size):
            dst = image_start + i
            if dst >= len(original):
                mismatches.append(i); continue
            covered[dst] = 1
            if i in mask:
                continue
            if probe_mz.image[start+i] != original[dst]:
                mismatches.append(i)
        fix_ok = [verify_fixup(row, mod, f, tseg) for f in fixups]
        checked = sum(fix_ok)
        for f, ok in zip(fixups, fix_ok):
            if not ok:
                atp, ati = start+f.offset, image_start+f.offset
                n = width(f.location)
                unresolved_fixups.append((name, ati, f.location,
                    probe_mz.image[atp:atp+n].hex(), mz.image[ati:ati+n].hex()))
        verdict = 'MATCH' if not mismatches and checked == len(fixups) else 'FAIL'
        if verdict != 'MATCH':
            all_good = False
            detail = (f'{len(mismatches)} non-fixup byte differences; '
                      f'{len(fixups)-checked}/{len(fixups)} fixups unresolved')
            unknown.append((image_start, image_end, name, detail))
        else:
            detail = 'all bytes/fixup bytes equal'
        print(f'{name:12s} {start:04X}-{start+size:04X} {image_start:04X}-{image_end:04X} '
              f'{size:5d} {checked:14d} {verdict}: {detail}')
    # TLINK rewrites 9A ptr16:16 calls whose resolved target is in the same
    # output segment as 90 0E E8 rel16. Verify each such call in the linked
    # probe and in the original image, including absence of the segment reloc.
    rewritten, rewrite_fail = [], []
    for row in probe_rows:
        name = row['module'].upper()
        if name == 'P.ASM': continue
        mod = modules.get(name)
        tseg = _text(mod) if mod else None
        if not tseg: continue
        for f in mod.fixups:
            if f.segment != tseg['index'] or f.location != 3: continue
            calloff = f.offset - 1
            if calloff < 0: continue
            first = next((d['data'][calloff-d['offset']] for d in mod.data
                          if d['segment'] == tseg['index'] and d['offset'] <= calloff < d['offset']+len(d['data'])), None)
            if first != 0x9a: continue
            target_name = None
            target_addr = None
            if f.target_method == 2 and f.target_datum:
                target_name = mod.externals[f.target_datum-1]['name'].upper()
                target_addr = publics.get(target_name)
            same_text = bool(target_addr and target_addr[0] == 0)
            if f.target_method == 0 and f.target_datum:
                ts = next((s for s in mod.segments if s['index'] == f.target_datum), None)
                same_text = bool(ts and ts['name'] == '_TEXT')
                if same_text: target_addr = (0, f.displacement or 0)
            if not same_text or not target_addr:
                continue
            probe_call = row['offset'] + calloff
            image_call = normalized(row['offset']) + calloff
            pb = probe_mz.image[probe_call:probe_call+5]
            ob = mz.image[image_call:image_call+5]
            probe_disp = int.from_bytes(pb[3:5], 'little', signed=True) if len(pb) == 5 else None
            image_disp = int.from_bytes(ob[3:5], 'little', signed=True) if len(ob) == 5 else None
            expected_probe = target_addr[1] - (probe_call + 5)
            expected_image = normalized(target_addr[1]) - (image_call + 5)
            probe_seg_site = probe_call + 3
            image_seg_site = image_call + 3
            ok = (pb[:3] == b'\x90\x0e\xe8' and ob[:3] == b'\x90\x0e\xe8'
                  and probe_disp == expected_probe and image_disp == expected_image
                  and (0, probe_seg_site) not in probe_relocs
                  and (0, image_seg_site) not in orig_relocs)
            info = (name, image_call, target_name, pb.hex(), ob.hex())
            if ok: rewritten.append(info)
            else: rewrite_fail.append(info)
    print(f'TLINK same-_TEXT far-call rewrites verified: {len(rewritten)}; failures: {len(rewrite_fail)}')
    for name, at, target, pb, ob in rewritten:
        print(f'  {name} 0000:{at:04X} -> {target}: probe={pb} image={ob}; no segment relocation')
    if rewrite_fail:
        all_good = False
        for name, at, target, pb, ob in rewrite_fail:
            print(f'  FAIL {name} 0000:{at:04X} -> {target}: probe={pb} image={ob}')
    # DGROUP is ordered startup, game modules, then extracted library members.
    # The P.ASM _DATA reservation reproduces the measured game-data span only;
    # its bytes are deliberately not treated as runtime evidence.
    group_rows = [r for r in rows if r['group'] == 'DGROUP']
    game_pad = next((r for r in group_rows if r['module'].upper() == 'P.ASM'
                     and r['segment'] == '_DATA'), None)
    files_row = next((r for r in group_rows if r['module'].upper() == 'FILES' and
                      r['segment'] == '_DATA'), None)
    group_end = max((r['offset']+r['size'] for r in group_rows), default=0)
    anchor_ok = bool(files_row and files_row['offset'] == files_anchor and
                     game_pad and game_pad['size'] == pad_size and
                     group_end == len(original_dgroup))
    print(f'DGROUP anchor: FILES initialized bytes uniquely match image offset {files_anchor:04X}; '
          f'probe offset {files_row["offset"] if files_row else -1:04X}; pad={pad_size:04X}; '
          f'map end={group_end:04X}; image group size={len(original_dgroup):04X}; '
          f'{"MATCH" if anchor_ok else "FAIL"}')
    if not anchor_ok: all_good = False
    print('DGROUP contribution comparison (map group offsets):')
    print('member       segment      range       bytes  fixups checked  verdict')
    data_unknown = []
    for row in group_rows:
        name = row['module'].upper()
        if name == 'P.ASM' and row['segment'] == '_DATA':
            print(f'GAME-DATA    _DATA        {row["offset"]:04X}-{row["offset"]+row["size"]:04X} '
                  f'{row["size"]:5d}              - layout placeholder; contents unverified')
            continue
        if not row['size']:
            continue
        mod = modules.get(name)
        seg = next((s for s in mod.segments if s['name'] == row['segment'] and
                    s['size'] == row['size']), None) if mod else None
        if not seg:
            all_good = False
            data_unknown.append((row['offset'], row['offset']+row['size'], name))
            print(f'{name:12s} {row["segment"]:12s} {row["offset"]:04X}-{row["offset"]+row["size"]:04X} '
                  f'{row["size"]:5d}              0 FAIL: no matching OMF segment')
            continue
        fixups = [f for f in mod.fixups if f.segment == seg['index']]
        mask = set()
        data_ok = []
        for f in fixups:
            mask.update(range(f.offset, min(row['size'], f.offset+width(f.location))))
        pbase = row['frame']*16 + row['offset']
        ibase = 0x5c09*16 + row['offset']
        diffs = [i for i in range(row['size']) if i not in mask and
                 probe_mz.image[pbase+i] != mz.image[ibase+i]]
        fchecked = 0
        for f in fixups:
            w = width(f.location)
            pb = probe_mz.image[pbase+f.offset:pbase+f.offset+w]
            ib = mz.image[ibase+f.offset:ibase+f.offset+w]
            tn, ta = '', None
            if f.target_method == 2 and f.target_datum:
                tn = mod.externals[f.target_datum-1]['name'].upper(); ta = symaddr(tn)
            if f.location == 2 and f.frame_method == 5 and ta:
                expected = orig_frame(ta[0], tn)
                ok = expected is not None and int.from_bytes(pb,'little') == ta[0] and int.from_bytes(ib,'little') == expected
            elif f.location == 2 and f.frame_method == 5 and f.target_method == 1:
                ok = int.from_bytes(pb,'little') == dgroup_frame and int.from_bytes(ib,'little') == 0x5c09
            elif f.location == 3 and ta:
                po, ps = int.from_bytes(pb[:2], 'little'), int.from_bytes(pb[2:4], 'little')
                io, ins = int.from_bytes(ib[:2], 'little'), int.from_bytes(ib[2:4], 'little')
                expected_frame = orig_frame(ta[0], tn)
                ok = (po == ta[1] and ps == ta[0] and io == normalized(ta[1])
                      and expected_frame is not None and ins == expected_frame)
            elif f.location == 3 and f.target_method == 0 and f.target_datum:
                target_seg = next((s for s in mod.segments if s['index'] == f.target_datum), None)
                target_row = next((r for r in rows if r['module'].upper() == name and
                                   target_seg and r['segment'] == target_seg['name']), None)
                if target_seg and target_seg['name'] == '_TEXT' and target_row:
                    po, ps = int.from_bytes(pb[:2], 'little'), int.from_bytes(pb[2:4], 'little')
                    io, ins = int.from_bytes(ib[:2], 'little'), int.from_bytes(ib[2:4], 'little')
                    ok = ps == 0 and ins == 0 and io == normalized(po)
                else:
                    ok = pb == ib
            elif f.location == 1 and ta and ta[0] == dgroup_frame:
                ok = int.from_bytes(pb,'little') == ta[1] and int.from_bytes(ib,'little') == ta[1]
            elif f.location == 1 and ta and ta[0] == 0:
                ok = int.from_bytes(pb,'little') == ta[1] and int.from_bytes(ib,'little') == normalized(ta[1])
            elif f.location == 1 and f.target_method == 0 and f.target_datum:
                target_seg = next((s for s in mod.segments if s['index'] == f.target_datum), None)
                if target_seg and target_seg['name'] == '_TEXT':
                    pv = int.from_bytes(pb,'little')
                    ok = int.from_bytes(ib,'little') == (pv-p_size if pv >= p_start+p_size else pv)
                else:
                    ok = pb == ib
            else:
                ok = pb == ib
            data_ok.append(bool(ok)); fchecked += bool(ok)
        for f, ok in zip(fixups, data_ok):
            if not ok:
                pa, ia = pbase+f.offset, ibase+f.offset
                unresolved_fixups.append((name, row['offset']+f.offset, f.location,
                    probe_mz.image[pa:pa+width(f.location)].hex(),
                    mz.image[ia:ia+width(f.location)].hex()))
        verdict = 'MATCH' if not diffs and fchecked == len(fixups) else 'FAIL'
        if verdict != 'MATCH':
            all_good = False
            data_unknown.append((row['offset'], row['offset']+row['size'], name))
        print(f'{name:12s} {row["segment"]:12s} {row["offset"]:04X}-{row["offset"]+row["size"]:04X} '
              f'{row["size"]:5d} {fchecked:14d} {verdict}: {len(diffs)} non-fixup differences; '
              f'{len(fixups)-fchecked}/{len(fixups)} fixups unresolved')
    if game_pad:
        print(f'Runtime/game DGROUP layout: C0H _DATA 0000-0091; game-data span '
              f'{game_pad["offset"]:04X}-{game_pad["offset"]+game_pad["size"]:04X}; '
              f'library data and _INIT_ follow it through 7E2E.')
    gaps, p = [], 0
    while p < len(original):
        if covered[p]: p += 1; continue
        q = p + 1
        while q < len(original) and not covered[q]: q += 1
        gaps.append((p, q)); p = q
    print(f'Original _TEXT bytes covered by mapped contributions: {sum(covered)}/{len(original)}')
    print(f'Normalized probe _TEXT end: {map_end:04X}; image game entry begins at 013B:0008 (linear 13B8)')
    print('UNKNOWN ranges:', ', '.join(f'{a:04X}-{b:04X}' for a,b in gaps) or 'none')
    if unknown:
        print('Member failures:', '; '.join(f'{n}@{a:04X}-{b:04X}: {why}' for a,b,n,why in unknown))
    if unresolved_fixups:
        print('Unresolved FIXUPP values (member, image site, loc type, probe value, image value):')
        for name, at, loc, pv, iv in unresolved_fixups:
            print(f'  {name} 0000:{at:04X} loc{loc} probe={pv} image={iv}')
    return 0 if all_good and not gaps and not data_unknown and map_end == len(original) else 1


if __name__ == '__main__':
    raise SystemExit(main())
