"""Leaf C contracts: signed cursor slots and nominal ADLX duration scanning.

Expected synthetic totals are authored from event definitions; no setup runs the
oracle. Real resource timing values come from the structural census in data.md.
"""
from difftest import Case

PRESERVED = ('SI', 'DI', 'BP', 'IF', 'DF')
OUTPUTS = ('AX',) + PRESERVED
CASES = []


def cursor(slot, bits, pointer=(0xFEDC, 0xA5B6), df=False):
    delta = slot * 42
    accepted = slot <= 12 and bool(bits & 4)

    def setup(m):
        # Static stale state makes collateral field clearing observable.
        s, base = m.address('SOUND:AudioChannelStates')
        for i in range(42):
            m.write(s, (base + delta + i) & 65535, bytes(((i * 29 + 17) & 255,)))
        m.ww('SOUND:AudioChannelStates', pointer[0], delta + 6)
        m.ww('SOUND:AudioChannelStates', pointer[1], delta + 8)
        m.ww('SOUND:AudioChannelStates', bits, delta + 0x28)

    def check(m, result):
        assert result['AX'] == (1 if accepted else 65535)
        if accepted:
            assert m.rw('SOUND:AudioChannelStates', delta + 0x10) == pointer[0]
            assert m.rw('SOUND:AudioChannelStates', delta + 0x12) == pointer[1]
        if slot == 12 and accepted:
            assert m.rw('SOUND:MainAdlxCursor') == pointer[0]
            assert m.rw('SOUND:MainAdlxCursor', 2) == pointer[1]

    return Case(f'cursor slot={slot} flags={bits:04X} pointer={pointer} DF={df}',
                'C:ResetAdlibTrackChannelCursor', setup=setup, args=(slot & 65535,),
                kind='far', out_regs=OUTPUTS, flags=0x602 if df else 0x202, check=check)


CASES += [cursor(slot, 4, (0x1234 + slot, 0x789A + slot)) for slot in range(13)]
CASES += [cursor(slot, bits, df=True) for slot, bits in
          ((13, 4), (32767, 0xFFFF), (0, 0), (12, 0xFFFB), (8, 1), (9, 2),
           (10, 0x8000), (11, 0xFFFF), (-1, 4), (-2, 0), (-3, 0xFFFF),
           (-32768, 4), (-32767, 4), (-1561, 4))]
CASES += [cursor(12, 7, pointer, True) for pointer in ((0, 0), (65535, 65535), (15, 0xFFFF))]


def sound_state(m, segment, offset, length, rate=1, devices=1, playing=1):
    m.ww('SOUND:SoundDeviceBits', devices)
    m.ww('SOUND:MainAdlxPlaying', playing)
    m.ww('SOUND:MusicTicksPerUnit', rate)
    m.ww('SOUND:MainAdlxStartPointer', offset)
    m.ww('SOUND:MainAdlxStartPointer', segment, 2)
    m.ww('SOUND:MusicEventStreamLength', length)


def duration(title, stream, ticks, *, rate=1, length=None, offset=0x120,
             segment=0x7500, devices=1, playing=1, df=False, fill=None):
    if length is None:
        length = len(stream)
    expected = ((ticks // rate) & 65535) if devices & 1 and playing and rate else 0

    def setup(m):
        if fill is not None:
            m.write(segment, 0, bytes((fill,)) * 65536)
        for i, value in enumerate(stream):
            m.write(segment, (offset + i) & 65535, bytes((value,)))
        sound_state(m, segment, offset, length, rate, devices, playing)

    def check(m, result):
        assert result['AX'] == expected, (title, result['AX'], expected)
        assert result['ES'] == m.seg('SOUND:SoundDeviceBits')

    return Case(title, 'C:GetMusicTrackDuration', setup=setup, kind='far',
                out_regs=OUTPUTS, flags=0x602 if df else 0x202, check=check)


# Every entry guard, including non-boolean flags and maximum divisor.
for devices, playing, rate in ((0, 1, 1), (2, 1, 1), (0x8000, 1, 1),
                                (1, 0, 1), (1, 1, 0), (0, 0, 0),
                                (0xFFFF, 2, 1), (1, 0x8000, 65535), (1, 0xFFFF, 7)):
    CASES.append(duration(f'guards {devices:04X}/{playing:04X}/{rate}', b'\xff', 127,
                          devices=devices, playing=playing, rate=rate, df=True))

CASES += [duration('empty stream', b'', 0),
          duration('end offset wraps below start', b'\xff' * 32, 0,
                   offset=0xFFF0, length=32, segment=0x9000),
          duration('end offset wraps exactly zero', b'\xff', 0,
                   offset=65535, segment=0x9000),
          duration('maximum length zero waits', b'\x20', 0, length=65535,
                   offset=0, segment=0x9000, fill=0x20),
          duration('unsigned high offsets', b'\xff\x81', 128,
                   offset=0x8000, segment=0x9000, df=True),
          duration('A20 enabled stream', b'\xff\x81', 128,
                   offset=0x100, segment=0xFFF0)]

# Every switch arm and low-channel nibble, with payloads that would add time if
# accidentally interpreted. 5n follows the scanner's default arm and adds time.
for nibble in range(16):
    code = (nibble << 4) | 0xF
    payload = {0: b'\xff', 1: b'\xff\xff', 2: b'', 3: b'\xff',
               4: b'\xff' * 11, 6: b'\xff\xff', 7: b'\x03\xff\xff\xff'}.get(nibble, b'')
    ticks = 65408 if nibble == 0 else (code & 127 if nibble not in (1, 2, 3, 4, 6, 7) else 0)
    CASES.append(duration(f'opcode {code:02X} payload then short wait', bytes((code,)) + payload + b'\x83',
                          ticks + 3, df=bool(nibble & 1)))

for code, low, ticks in ((0, 0, 0), (0, 1, 128), (1, 255, 65408),
                         (2, 0, 0), (15, 0, 32768), (15, 255, 65408)):
    CASES.append(duration(f'long wait {code:02X}/{low:02X}', bytes((code, low)), ticks))
    # Rate 1 can conceal an accidentally widened wait in the 16-bit return.
    CASES.append(duration(f'long wait truncation before division {code:02X}/{low:02X}',
                          bytes((code, low)), ticks, rate=420))
for code in (0x80, 0x81, 0xFE, 0xFF, 0x50, 0x5F):
    CASES.append(duration(f'single short/default {code:02X}', bytes((code,)), code & 127))
for code in (0x70, 0x77, 0x7F):
    for size in (0, 255):
        CASES.append(duration(f'extension {code:02X} length {size}',
                              bytes((code, size)) + b'\xff' * size + b'\x81', 1))

# Truncated nominal payloads deliberately read/skip beyond the declared extent.
for code, payload in ((0x0F, b'\xff'), (0x1F, b'\xff\xff'), (0x3F, b'\xff'),
                       (0x4D, b'\xff' * 11), (0x6F, b'\xff\xff'), (0x77, b'\xff')):
    CASES.append(duration(f'truncated {code:02X}', bytes((code,)) + payload,
                          65408 if code == 15 else 0, length=1))

CASES += [duration('dword carry and quotient truncation', b'\xff' * 1024, 130048),
          duration('dword carry divided', b'\xff' * 1024, 130048, rate=65535),
          duration('long wait accumulation', b'\x01\xff' * 1024, 66977792, rate=7),
          duration('odd far offset segment alias', b'\xff\x81', 128,
                   offset=0x131, segment=0x74FF)]

# Skip wraps back to low offset; scanning continues through the same segment.
# All filler key-off codes contribute zero. At FFFE an authored wait exits.
def wrap_skip_setup(m):
    m.write(0x9000, 0, b'\x20' * 65536)
    # On the second traversal an instrument at FFED skips the initial extension.
    m.write(0x9000, 0xFFED, b'\x4F')
    m.write(0x9000, 0xFFF0, b'\x7F\xFF')
    m.write(0x9000, 0xFFFE, b'\x81')
    sound_state(m, 0x9000, 0xFFF0, 15)

def wrap_skip_check(m, result):
    assert result['AX'] == 1

CASES.append(Case('extension offset wraps then exits', 'C:GetMusicTrackDuration',
                  setup=wrap_skip_setup, kind='far', out_regs=OUTPUTS,
                  check=wrap_skip_check))


# The compiler's original switch table is read from CS, not a native callback.
# Redirect a known entry to another known target, without copying code bytes.
def redirected_setup(m):
    m.write(0x7500, 0x120, b'\x20\x83\x84\x81')
    sound_state(m, 0x7500, 0x120, 4)
    s, entry = m.address('C:GetMusicTrackDuration')
    m.write(s, entry + 0x107 + 2 * 2, (entry + 0xAE).to_bytes(2, 'little'))

def redirected_check(m, result):
    assert result['AX'] == 1  # key-off dispatch now skips two authored waits

CASES.append(Case('original switch target redirect', 'C:GetMusicTrackDuration',
                  setup=redirected_setup, check=redirected_check, kind='far', out_regs=OUTPUTS))


def real_track(bank, tag, ticks):
    header = f'{bank}:AdlxHeader_{tag}'
    events = f'{bank}:AdlxEvents_{tag}'

    def setup(m):
        s, h = m.address(header)
        se, p = m.address(events)
        assert m.read(s, h, 4) == b'ADLX'
        length = int.from_bytes(m.read(s, h + 4, 4), 'big') - 34
        rate = int.from_bytes(m.read(s, h + 22, 2), 'little')
        sound_state(m, se, p, length, rate)

    def check(m, result):
        assert result['AX'] == ticks // 420, (tag, result['AX'])

    return Case(f'rebuilt ADLX {tag}', 'C:GetMusicTrackDuration', setup=setup,
                check=check, kind='far', out_regs=OUTPUTS)


CASES += [real_track('B3279' if tag == '343F' else 'B' + tag, tag, ticks)
          for tag, ticks in (('325B', 420), ('3260', 420), ('3265', 1260), ('326B', 840),
                             ('3274', 420), ('3279', 87360), ('343F', 6720), ('3444', 60480),
                             ('3629', 840), ('3632', 210), ('3637', 50400))]
