"""Small reader for Intel OMF objects and Borland OMF libraries.

The API deliberately exposes records and decoded names/indexes rather than linker
semantics.  Offsets in LEDATA/LIDATA and FIXUPP are segment relative.
"""
from dataclasses import dataclass, field
import struct


def records(data):
    """Yield (record type, payload without checksum) from an OMF byte stream."""
    p = 0
    while p + 3 <= len(data):
        typ = data[p]
        n = struct.unpack_from('<H', data, p + 1)[0]
        end = p + 3 + n
        if end > len(data) or n < 1:
            raise ValueError(f'truncated OMF record at {p:08X}')
        yield typ, data[p + 3:end - 1]
        p = end


def index(buf, p):
    b = buf[p]
    if b & 0x80:
        return ((b & 0x7f) << 8) | buf[p + 1], p + 2
    return b, p + 1


def name(buf, p):
    n = buf[p]
    return buf[p + 1:p + 1 + n].decode('latin1'), p + 1 + n


@dataclass
class Fixup:
    segment: int
    offset: int
    location: int
    self_relative: bool
    frame_method: int
    frame_datum: int | None
    target_method: int
    target_datum: int | None
    displacement: int | None
    thread: bool = False


@dataclass
class Module:
    module: str = ''
    names: list = field(default_factory=list)
    segments: list = field(default_factory=list)
    groups: list = field(default_factory=list)
    publics: list = field(default_factory=list)
    externals: list = field(default_factory=list)
    communal: list = field(default_factory=list)
    data: list = field(default_factory=list)
    fixups: list = field(default_factory=list)
    modend: bytes = b''
    comments: list = field(default_factory=list)


def _number(b, p):
    """OMF variable length numeric field."""
    x = b[p]
    if x & 0x80:
        return ((x & 0x7f) << 8) | b[p + 1], p + 2
    return x, p + 1


def _expand_lidata(b, p, width):
    out = bytearray()
    def rawnum(q, n):
        if q+n>len(b):raise ValueError('truncated LIDATA number')
        return int.from_bytes(b[q:q + n], 'little'), q + n
    def block(q):
        repeat, q = rawnum(q, width)
        count, q = rawnum(q, 2)
        if not count:
            length,q=rawnum(q,1)
            if q+length>len(b):raise ValueError('truncated LIDATA leaf')
            raw = b[q:q + length]
            return raw * repeat, q + length
        child = bytearray()
        for _ in range(count):
            v, q = block(q); child.extend(v)
        return child * repeat, q
    while p < len(b):
        v, p = block(p); out.extend(v)
    return bytes(out)


def parse(data):
    """Decode common OMF records into a Module. Unknown records are ignored."""
    m = Module()
    current = None
    frame_threads, target_threads = {}, {}
    for typ, b in records(data):
        p = 0
        if typ == 0x80:  # THEADR
            m.module, p = name(b, p)
        elif typ == 0x96:  # LNAMES
            while p < len(b):
                s, p = name(b, p); m.names.append(s)
        elif typ in (0x98, 0x99):  # SEGDEF / SEGDEF32
            attr = b[p]; p += 1
            if typ == 0x98:
                size, p = struct.unpack_from('<H', b, p)[0], p + 2
            else:
                size, p = struct.unpack_from('<I', b, p)[0], p + 4
            if attr & 0x02: size = size or (1 << 16 if typ == 0x98 else 1 << 32)
            sidx, p = index(b, p); cidx, p = index(b, p); oidx, p = index(b, p)
            m.segments.append(dict(index=len(m.segments) + 1, size=size, attr=attr,
                                   name=m.names[sidx - 1] if sidx else '',
                                   class_name=m.names[cidx - 1] if cidx else '',
                                   overlay=m.names[oidx - 1] if oidx else ''))
        elif typ == 0x9A:  # GRPDEF
            gi, p = index(b, p); items = []
            while p < len(b):
                tag = b[p]; p += 1
                if tag == 0xff:
                    v, p = index(b, p); items.append(('segment', v))
                elif tag == 0xfe:
                    v, p = index(b, p); items.append(('group', v))
                else: raise ValueError('unknown GRPDEF component')
            m.groups.append(dict(index=len(m.groups) + 1,
                                 name=m.names[gi - 1] if gi else '', items=items))
        elif typ in (0x90, 0x91):  # PUBDEF
            gidx, p = index(b, p); sidx, p = index(b, p)
            base = struct.unpack_from('<H', b, p)[0] if gidx == 0 and sidx == 0 else 0
            p += 2 if gidx == 0 and sidx == 0 else 0
            while p < len(b):
                nm, p = name(b, p)
                off, p = (struct.unpack_from('<I', b, p)[0], p + 4) if typ == 0x91 else (struct.unpack_from('<H', b, p)[0], p + 2)
                typidx, p = index(b, p)
                m.publics.append(dict(name=nm, group=gidx, segment=sidx, offset=off + base, type=typidx))
        elif typ in (0x8C, 0x8D):  # EXTDEF
            while p < len(b):
                nm, p = name(b, p); ti, p = index(b, p); m.externals.append(dict(name=nm, type=ti))
        elif typ in (0xB0, 0xB1):  # COMDEF
            while p < len(b):
                nm, p = name(b, p); ti, p = index(b, p); kind = b[p]; p += 1
                n, p = _number(b, p)
                if kind == 0x61: size, p = n, p
                elif kind == 0x62:
                    count, p = _number(b, p); size = n * count
                else: raise ValueError(f'unknown COMDEF kind {kind:02x}')
                m.communal.append(dict(name=nm, type=ti, size=size))
        elif typ in (0xA0, 0xA1):  # LEDATA
            seg, p = index(b, p); off, p = struct.unpack_from('<H' if typ == 0xA0 else '<I', b, p)[0], p + (2 if typ == 0xA0 else 4)
            current = (seg, off); m.data.append(dict(segment=seg, offset=off, data=b[p:], kind='LEDATA'))
        elif typ in (0xA2, 0xA3):  # LIDATA
            seg, p = index(b, p); off, p = struct.unpack_from('<H' if typ == 0xA2 else '<I', b, p)[0], p + (2 if typ == 0xA2 else 4)
            current = (seg, off); m.data.append(dict(segment=seg, offset=off, data=_expand_lidata(b, p, 2 if typ == 0xA2 else 4), kind='LIDATA'))
        elif typ in (0x9C, 0x9D):  # FIXUPP
            while p < len(b):
                first = b[p]
                if not first & 0x80:  # THREAD
                    p += 1; method = (first >> 2) & 7; slot = first & 3
                    datum = None
                    if method < 3 or not first & 0x40: datum, p = index(b, p)
                    table = frame_threads if first & 0x40 else target_threads
                    table[slot] = (method, datum)
                    continue
                hi, lo = b[p], b[p + 1]; p += 2
                locat = ((hi & 3) << 8) | lo; loc = (hi >> 2) & 15
                fd = b[p]; p += 1
                frame_method = (fd >> 4) & 7
                if fd & 0x80: fm, fdatum = frame_threads[frame_method & 3]; frame_method, frame_datum = fm, fdatum
                else:
                    frame_datum = None
                    if frame_method < 4: frame_datum, p = index(b, p)
                target_method = fd & 3
                if fd & 0x08: tm, tdatum = target_threads[target_method]; target_method, target_datum = tm, tdatum
                else: target_datum, p = index(b, p)
                disp = None
                if not fd & 0x04: disp, p = struct.unpack_from('<H', b, p)[0], p + 2
                if current:
                    m.fixups.append(Fixup(current[0], current[1] + locat, loc,
                                          bool(hi & 0x40), frame_method, frame_datum,
                                          target_method, target_datum, disp, False))
        elif typ == 0x8A: m.modend = b
        elif typ == 0x88: m.comments.append(b)
    return m


def library(data):
    """Return (page_size, [(module_name, object_bytes, library_page), ...]).

    Borland libraries use a two-byte dictionary page size; dictionary entries
    point at module streams that are packed between page boundaries. Scan for
    checksum-valid THEADR streams and retain complete THEADR..MODEND modules.
    """
    if len(data) < 4: raise ValueError('short library')
    page_size = struct.unpack_from('<H', data)[0]
    if not page_size or page_size > 8192: raise ValueError('invalid library page size')
    found, seen = [], set()
    for off in range(2, len(data) - 4):
        if data[off] != 0x80: continue
        p = off; end = None
        try:
            while p + 3 <= len(data):
                typ = data[p]; n = struct.unpack_from('<H', data, p + 1)[0]
                q = p + 3 + n
                if q > len(data) or n < 1: break
                if sum(data[p:q]) & 0xff: break
                p = q
                if typ == 0x8A: end = p; break
            if end and off not in seen:
                blob = data[off:end]; mod = parse(blob)
                if mod.module:
                    found.append((mod.module, blob, off)); seen.add(off)
        except (IndexError, ValueError, struct.error):
            continue
    return page_size, found
