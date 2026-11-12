"""List the surveyed data objects in the expanded UGH image.

  python tools/dataprobe.py list

Ranges are image-linear, half-open offsets. The checker makes sure the entries cover
all data frames in this survey exactly, including the DGROUP prefix pending the
runtime boundary investigation.
"""
from pathlib import Path
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from common import MZ, BUILD, load_json

IMAGE = BUILD / 'oracle' / 'UGH_X.EXE'

# start, end, kind, format / contents, confidence, code evidence, Amiga clue
OBJECTS = [
    (0x0A670, 0x1A370, 'scratch buffer', 'zero-filled 64,768-byte ICE! decode destination', 'code-supported', 'image 006055-00605D; 006031', 'none'),
    (0x1A370, 0x1A380, 'C data', '16 zero bytes; initialized DS frame, contents unknown', 'supported by code reading', 'C module prologues load DS=1A37', 'none'),
    (0x1A380, 0x1E1E4, 'compressed resource', 'ICE! stream; endpoint 0x3E63, 0x7D00 output bytes', 'header length decoded; image layout unresolved', 'image 00605D; pointer in DGROUP near 00A5', 'possible title / image asset'),
    (0x1E1E4, 0x1E1F0, 'zero alignment padding', '12 zero bytes after ICE! stream', 'verified bytes', 'image 00605D header endpoint', 'none'),
    (0x1E1F0, 0x2BC60, 'graphics / game data', '55,920 bytes; mixed zero and small-value fields; internal structure unknown', 'hypothesis', 'game pointer table at 59CA; VGA renderer 59E4 onward', 'possible Blocks / sprites / level imagery'),
    (0x2BC60, 0x2BF60, 'palette candidate', '768 bytes, 256 RGB triples with values in DAC-compatible range 0..63', 'hypothesis: VGA DAC source not tied to this pointer', 'DGROUP relocation at 5C145; DAC writer at 6222..6245', 'no direct match'),
    (0x2BF60, 0x2D999, 'compressed graphics resource', 'ICE! stream; endpoint 0x1A38, output size 0xFD00; reference render is 320x200 chunky', 'format supported by code; image seen in retained routine output; Python decoder mismatch', 'image 00605D; decompression calls 1F7C/1F83', 'possible title image; no DOS/Amiga byte match'),
    (0x2D999, 0x2D9A0, 'zero alignment padding', '7 zero bytes after ICE! stream', 'verified bytes', 'image 00605D header endpoint', 'none'),
    (0x2D9A0, 0x2F9DF, 'compressed graphics resource', 'ICE! stream; endpoint 0x203E, output size 0xFD00', 'header supported by code; Python decode currently diverges', 'image 00605D; decompression call 1F6F', 'possible graphics resource; no byte-level match established'),
    (0x2F9DF, 0x2F9E0, 'zero alignment padding', '1 zero byte after ICE! stream', 'verified bytes', 'image 00605D header endpoint', 'none'),
    (0x2F9E0, 0x2FB61, 'compressed graphics resource', 'ICE! stream; endpoint 0x0180, output size 0xFD00', 'header supported by code; Python decode currently diverges', 'image 00605D; decompression call 1F94', 'possible graphics resource'),
    (0x2FB61, 0x2FB70, 'zero alignment padding', '15 zero bytes after ICE! stream', 'verified bytes', 'image 00605D header endpoint', 'none'),
    (0x2FB70, 0x325AD, 'compressed graphics resource', 'ICE! stream; endpoint 0x2A3C, output size 0xFD00', 'header supported by code; Python decode currently diverges', 'image 00605D; decompression call 1FA8', 'possible graphics resource'),
    (0x325AD, 0x325B0, 'zero alignment padding', '3 zero bytes after ICE! stream', 'verified bytes', 'image 00605D header endpoint', 'none'),
    (0x325B0, 0x32600, 'music resource', '80-byte ADLX tagged header: AHDR / IMAP / TRCK', 'format supported by tags; playback semantics unknown', 'image 003778 passes segment to C:1852', 'music format counterpart unconfirmed'),
    (0x32600, 0x32650, 'music resource', '80-byte ADLX tagged header', 'format supported by tags; playback semantics unknown', 'image 00382E passes segment to C:1852', 'music format counterpart unconfirmed'),
    (0x32650, 0x326B0, 'music resource', '96-byte ADLX tagged header', 'format supported by tags; playback semantics unknown', 'image 003D4C passes segment to C:1852', 'music format counterpart unconfirmed'),
    (0x326B0, 0x32740, 'music resource', '144-byte ADLX tagged header', 'format supported by tags; playback semantics unknown', 'image 00153C passes segment to C:1852', 'music format counterpart unconfirmed'),
    (0x32740, 0x32790, 'music resource', '80-byte ADLX tagged header', 'format supported by tags; playback semantics unknown', 'image 002EA4 passes segment to C:1852', 'music format counterpart unconfirmed'),
    (0x32790, 0x343F0, 'music / sound bank', 'ADLX header plus 7,184 bytes of tagged/tracker data; further ADLX header at 343F0', 'format supported by tags; internal records unknown', 'image 001641,001C64 pass segment to C:0F88', 'possible music; Amiga TFMX files differ in format'),
    (0x343F0, 0x34440, 'music resource', '80-byte embedded ADLX header', 'format supported by tags; playback semantics unknown', 'embedded header; code pointer not identified', 'unconfirmed'),
    (0x34440, 0x36290, 'music / sound bank', 'ADLX header and 7,680 bytes of tracker data', 'format supported by tags; internal records unknown', 'image 00201F passes segment to C:0F88', 'possible music; no exact mapping'),
    (0x36290, 0x36320, 'music resource', '144-byte ADLX tagged header', 'format supported by tags; playback semantics unknown', 'image 001A8C passes segment to C:1852', 'unconfirmed'),
    (0x36320, 0x36370, 'music resource', '80-byte ADLX tagged header', 'format supported by tags; playback semantics unknown', 'image 00308E passes segment to C:1852', 'unconfirmed'),
    (0x36370, 0x37A70, 'music / sound bank', 'ADLX header and 5,808 bytes of tracker data', 'format supported by tags; internal records unknown', 'image 001422 passes segment to C:0F88', 'possible music; no exact mapping'),
    (0x37A70, 0x438A0, 'graphics / level bank', '48,688 bytes, sparse zero runs and low-valued records; raw format unknown', 'hypothesis', 'game pointer table at 59CE; renderer at 59E4', 'possible Blocks / level resource'),
    (0x438A0, 0x4E830, 'graphics / level bank', '44,944 bytes, sparse values; raw format unknown', 'hypothesis', 'game pointer table at 59D2; renderer at 59E4', 'possible level resource'),
    (0x4E830, 0x5B630, 'graphics / level bank', '52,736 bytes, sparse small-valued records; raw format unknown', 'hypothesis', 'game pointer table at 59D6; renderer at 59E4', 'possible level resource'),
    (0x5B630, 0x5C090, 'graphics table / bank', '2,656 bytes, repeating coordinate-like 16-bit values', 'hypothesis', 'game pointer table at 59DA/59DE', 'possible sprite or font data'),
    (0x5C090, 0x5C17E, 'DGROUP prefix', 'runtime-owned boundary not settled; 238-byte candidate before first game string at +00EE', 'boundary pending', 'runtime strings +002F/+003D; game strings begin +00EE', 'none'),
    (0x5C17E, 0x5C9B0, 'game string table', 'level names, NUL-terminated; offsets +00EE..+091F', 'supported by string scan', 'game reads DGROUP strings; direct code offsets include 1407, 151B, 1671', '117 common DOS/Amiga strings overall'),
    (0x5C9B0, 0x5CB74, 'credits text', 'credits and attribution strings, offsets +0920..+0AE3', 'supported by string scan', 'game credits/menu rendering in 13E9/1B26', 'names correspond to Amiga credits'),
    (0x5CB74, 0x5CD81, 'menu and score text', 'menu labels, prompts, defaults, high-score names/scores, offsets +0AE4..+0CF0', 'supported by string scan', 'game menu routine 13E9; high-score screens 1561 onward', 'content shared with Amiga'),
    (0x5CD81, 0x5FDCA, 'DGROUP tables / unknown', 'mixed binary region through offset +3D39, including UGH!.HI and opaque tables', 'unknown', 'DGROUP direct offsets; no complete object boundary established', 'no direct mapping'),
    (0x5FDCA, 0x633DC, 'level text and records', 'level title / instruction strings intermixed with binary fields; offsets +3D3A..+764B', 'text verified; record structure unknown', 'game level pointer/index code around 1FB7 and 1E9B', 'possible Texts.lo5, names/topics align semantically'),
    (0x633DC, 0x63EBE, 'DGROUP tail tables', 'binary tables and repeated small coordinate-like values; offsets +764C..+7E2D', 'hypothesis', 'game uses DGROUP offsets; individual readers unresolved', 'possible digits / font data'),
]

ICE_STREAMS = {
    0x1A38: (0x1A380, 0x1E1F0),
    0x2BF6: (0x2BF60, 0x2D9A0),
    0x2D9A: (0x2D9A0, 0x2F9E0),
    0x2F9E: (0x2F9E0, 0x2FB70),
    0x2FB7: (0x2FB70, 0x325B0),
}
GAME_CS_IMAGE = 0x13B0


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
        endpoint = int.from_bytes(self.source[6:8], 'big') - 1
        declared_size = int.from_bytes(self.source[10:12], 'big')
        if declared_size != output_size:
            raise ValueError(f'ICE! output field mismatch: {declared_size} != {output_size}')
        if endpoint != header_end or endpoint < 12 or endpoint >= len(self.source):
            raise ValueError(f'ICE! input endpoint mismatch: header={endpoint:04X}, object end={header_end:04X}')

        # 6089 loads [SI] into AH and decrements SI before entering 6099.
        si, ah, di = endpoint, self.source[endpoint], declared_size - 1
        # ES:DI is 0A67:0000 in the game. The 64K segment window extends
        # past the 0xFD00-byte declared output into the following image bytes;
        # ICE back-references can read that seeded tail, so preserve it.
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
                    raise ValueError('ICE literal prefix exceeded four tables')
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
            self.match_events.append((di, bx, dx, source_index))
            for _ in range(bx + 1):
                for _ in range(2):
                    if not 0 <= source_index < len(output):
                        raise ValueError(f'ICE back-reference outside output: src={source_index:04X} di={di:04X} bx={bx:04X} dx={dx:04X}')
                    if di < 0:
                        raise ValueError(f'ICE back-reference crossed output start: start={match_start:04X} di={di:04X} bx={bx:04X} dx={dx:04X}')
                    output[di] = output[source_index]
                    di -= 1
                    source_index = (source_index - 1) & 0xFFFF

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


def decode_ice(mz, frame):
    if frame not in ICE_STREAMS:
        raise SystemExit(f'frame {frame:04X} is not a surveyed ICE! object')
    start, region_end = ICE_STREAMS[frame]
    stream = mz.image[start:region_end]
    endpoint = int.from_bytes(stream[6:8], 'big') - 1
    output_size = int.from_bytes(stream[10:12], 'big')
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
    root = BUILD / 'workers' / 'data'
    raw_dir = root / 'decoded'
    png_dir = root / 'png'
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f'{base}.bin').write_bytes(decoded)
    if len(decoded) == 32000:
        palette = mz.image[0x2BC60:0x2BF60]
        _write_png(png_dir / f'{base}_320x100.png', 320, 100, _indexed_rgb(decoded, palette))
        _write_png(png_dir / f'{base}_160x200.png', 160, 200, _indexed_rgb(decoded, palette))
        planar = bytearray(320 * 100)
        plane_size = 80 * 100
        for y in range(100):
            for x in range(320):
                bit_index = 7 - (x & 7)
                source_at = y * 80 + (x >> 3)
                color = 0
                for plane in range(4):
                    color |= ((decoded[plane * plane_size + source_at] >> bit_index) & 1) << plane
                planar[y * 320 + x] = color
        _write_png(png_dir / f'{base}_320x100_planar4.png', 320, 100,
                   _indexed_rgb(planar, palette))
        return [f'{base}_320x100.png', f'{base}_160x200.png', f'{base}_320x100_planar4.png']
    if len(decoded) != 0xFD00:
        raise ValueError(f'no rendering layout for output size {len(decoded)}')

    pixels, embedded_palette = decoded[:64000], decoded[64000:]
    external_palette = mz.image[0x2BC60:0x2BF60]
    _write_png(png_dir / f'{base}_320x200_chunky_embedded.png', 320, 200,
               _indexed_rgb(pixels, embedded_palette))
    _write_png(png_dir / f'{base}_320x200_chunky_external.png', 320, 200,
               _indexed_rgb(pixels, external_palette))

    planar = bytearray(320 * 200)
    plane_size = 80 * 200
    for y in range(200):
        for x in range(320):
            bit_index = 7 - (x & 7)
            source_at = y * 80 + (x >> 3)
            color = 0
            for plane in range(4):
                color |= ((pixels[plane * plane_size + source_at] >> bit_index) & 1) << plane
            planar[y * 320 + x] = color
    _write_png(png_dir / f'{base}_320x200_planar4_embedded.png', 320, 200,
               _indexed_rgb(planar, embedded_palette))
    _write_png(png_dir / f'{base}_320x200_planar4_external.png', 320, 200,
               _indexed_rgb(planar, external_palette))
    return [f'{base}_320x200_chunky_embedded.png', f'{base}_320x200_chunky_external.png',
            f'{base}_320x200_planar4_embedded.png', f'{base}_320x200_planar4_external.png']


def validate():
    mz = MZ(IMAGE.read_bytes())
    if mz.identity() != load_json('oracle.json')['expanded']:
        raise SystemExit('expanded executable does not match metadata/oracle.json; run tools/oracle.py')
    start, end = 0x0A670, len(mz.image)
    cursor = start
    for a, b, *_ in OBJECTS:
        if a != cursor or b <= a:
            raise SystemExit(f'object coverage error at {cursor:06X}: next is {a:06X}..{b:06X}')
        cursor = b
    if cursor != end:
        raise SystemExit(f'object coverage ends {cursor:06X}, expected image end {end:06X}')
    if end != 0x63EBE:
        raise SystemExit(f'locked image size changed: expected scope end 63EBE, got {end:06X}')
    return mz


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'list':
        validate()
        print('start    end      size  kind                         format / contents | confidence | references | Amiga')
        for a, b, kind, fmt, conf, refs, amiga in OBJECTS:
            print(f'{a:06X}..{b:06X} {b-a:6}  {kind:28} {fmt} | {conf} | {refs} | {amiga}')
        print(f'coverage: {len(OBJECTS)} objects, {OBJECTS[-1][1]-OBJECTS[0][0]} bytes, exact')
        return

    if len(sys.argv) == 3 and sys.argv[1] == 'decode':
        mz = validate()
        frames = sorted(ICE_STREAMS) if sys.argv[2] == '--all' else [int(sys.argv[2], 16)]
        for frame in frames:
            decoded, endpoint, declared = decode_ice(mz, frame)
            pngs = render_decoded(frame, decoded, mz)
            print(f'{frame:04X}: endpoint={endpoint:04X}, decoded={len(decoded)} (header={declared}), PNGs={", ".join(pngs)}')
        return

    raise SystemExit('usage: python tools/dataprobe.py list | decode FRAME | decode --all')


if __name__ == '__main__':
    main()


