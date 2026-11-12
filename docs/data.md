# DOS data reference

The object table is an exact partition of image `00A670..063EBE`: 366,670 bytes,
including the scratch segment, alignment and already-attributed runtime DGROUP data.
It is not a new measurement of raw-data source debt. Image offsets are hexadecimal,
ranges are half-open, and code addresses are **module frame:offset**, not image offsets.
For example GAME `013B:41FD` is image `0055AD`; the old survey's “cs:59E4” was
actually image `0059E4`, GAME `013B:4634`.

Confidence is per object: **verified-by-decode** means an implemented parser/decoder
checks the stated boundaries and invariants (and round trips where described);
**supported-by-code** means the consumer establishes the layout, without executing
the game; **unknown** means ownership or meaning is not established. Parsing words
does not establish the meaning of every word. No data classification counts as exact
ASM or exact C source reconstruction. `src/` was not edited.

`python tools/dataprobe.py list` checks this partition against the locked expansion.
All generated artifacts below are under `build/workers/data3/`, unless stated otherwise.

## Object table

| Image range | Bytes | Object / layout | Confidence | Consumer / evidence |
|---|---:|---|---|---|
| `00A670..01A370` | 64,768 | scratch: 64768 zero bytes; ICE destination | supported-by-code | GAME 013B:4CA5 |
| `01A370..01A374` | 4 | C state: two initialized 16-bit flags | supported-by-code | C 0878:0003,008A; module.c g_0000/g_0002 |
| `01A374..01A380` | 12 | padding: 12 zero bytes after C state | supported-by-code | paragraph placement of 1A38 |
| `01A380..01E1E4` | 15,972 | ICE resource: 100 row-major 20x16 tile maps | verified-by-decode | GAME 013B:4CAD; exact independent repack235 |
| `01E1E4..01E1F0` | 12 | padding: 12 zero bytes | verified-by-decode | ICE header endpoint |
| `01E1F0..02BC58` | 55,912 | sprite pixels: IDs 0..216, column-major 8-bit indexed | verified-by-decode | GAME 013B:41FD; directory 5B63:0000 |
| `02BC58..02BC60` | 8 | padding: 8 zero bytes | verified-by-decode | end of sprite 216 |
| `02BC60..02BF60` | 768 | VGA palette: 256 RGB6 triples; first 128 copied twice, last 128 not read by that loader | supported-by-code | GAME 013B:466A,4E72; DGROUP 00B3 |
| `02BF60..02D999` | 6,713 | ICE resource: Bones Park logo; 320x200 indexed pixels plus RGB6 palette | verified-by-decode | GAME 013B:4CAD; exact independent repack235 |
| `02D999..02D9A0` | 7 | padding: 7 zero bytes | verified-by-decode | ICE header endpoint |
| `02D9A0..02F9DF` | 8,255 | ICE resource: Play Byte logo; 320x200 indexed pixels plus RGB6 palette | verified-by-decode | GAME 013B:4CAD; exact independent repack235 |
| `02F9DF..02F9E0` | 1 | padding: 1 zero bytes | verified-by-decode | ICE header endpoint |
| `02F9E0..02FB61` | 385 | ICE resource: present; 320x200 indexed pixels plus RGB6 palette | verified-by-decode | GAME 013B:4CAD; exact independent repack235 |
| `02FB61..02FB70` | 15 | padding: 15 zero bytes | verified-by-decode | ICE header endpoint |
| `02FB70..0325AD` | 10,813 | ICE resource: Ugh title; 320x200 indexed pixels plus RGB6 palette | verified-by-decode | GAME 013B:4CAD; exact independent repack235 |
| `0325AD..0325B0` | 3 | padding: 3 zero bytes | verified-by-decode | ICE header endpoint |
| `0325B0..0325F7` | 71 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `0325F7..032600` | 9 | padding: 9 zero bytes | verified-by-decode | ADLX root size |
| `032600..032647` | 71 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `032647..032650` | 9 | padding: 9 zero bytes | verified-by-decode | ADLX root size |
| `032650..0326A1` | 81 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `0326A1..0326B0` | 15 | padding: 15 zero bytes | verified-by-decode | ADLX root size |
| `0326B0..032734` | 132 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `032734..032740` | 12 | padding: 12 zero bytes | verified-by-decode | ADLX root size |
| `032740..03278E` | 78 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `03278E..032790` | 2 | padding: 2 zero bytes | verified-by-decode | ADLX root size |
| `032790..0343E1` | 7,249 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `0343E1..0343F0` | 15 | padding: 15 zero bytes | verified-by-decode | ADLX root size |
| `0343F0..034437` | 71 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `034437..034440` | 9 | padding: 9 zero bytes | verified-by-decode | ADLX root size |
| `034440..03628B` | 7,755 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `03628B..036290` | 5 | padding: 5 zero bytes | verified-by-decode | ADLX root size |
| `036290..036313` | 131 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `036313..036320` | 13 | padding: 13 zero bytes | verified-by-decode | ADLX root size |
| `036320..036367` | 71 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `036367..036370` | 9 | padding: 9 zero bytes | verified-by-decode | ADLX root size |
| `036370..037A6B` | 5,883 | ADLX: AdLib track with 42-byte container prefix | verified-by-decode | C 0878:0AA9; SOUND 0664:15D3,176B |
| `037A6B..037A70` | 5 | padding: 5 zero bytes | verified-by-decode | ADLX root size |
| `037A70..04389E` | 48,686 | sprite pixels: IDs 217..297, column-major 8-bit indexed | verified-by-decode | GAME 013B:41FD |
| `04389E..0438A0` | 2 | padding: 2 zero bytes | verified-by-decode | sprite directory endpoint |
| `0438A0..04E830` | 44,944 | sprite pixels: IDs 298..546, column-major 8-bit indexed | verified-by-decode | GAME 013B:41FD |
| `04E830..05B630` | 52,736 | sprite pixels: IDs 547..661, column-major 8-bit indexed | verified-by-decode | GAME 013B:41FD |
| `05B630..05C088` | 2,648 | sprite directory: 662 records: u16 offset, u8 width, u8 height | verified-by-decode | GAME 013B:425A,43BC |
| `05C088..05C090` | 8 | padding: 8 zero bytes | verified-by-decode | end of directory |
| `05C090..05C121` | 145 | DGROUP: runtime startup data | supported-by-code | docs/runtime.md |
| `05C121..05C122` | 1 | DGROUP: alignment | supported-by-code | runtime WORD alignment |
| `05C122..05C17E` | 92 | DGROUP: game pointers and numeric constants | supported-by-code | 013B:450A,4634,466A,3F0F,0652 |
| `05C17E..05C522` | 932 | DGROUP: 69 one-player passwords and FF terminator | verified-by-decode | 013B:0C07,06B5 |
| `05C522..05C9AF` | 1,165 | DGROUP: 81 two-player passwords and FF terminator | verified-by-decode | 013B:0C07,06B5 |
| `05C9AF..05CB74` | 453 | DGROUP: credits text | supported-by-code | 013B:07F6,077C |
| `05CB74..05CD16` | 418 | DGROUP: menu text and edit fields | supported-by-code | 013B:0039,04CA,077C |
| `05CD16..05CD81` | 107 | DGROUP: five 21-byte score rows and 00 FF terminators | supported-by-code | 013B:0446,0452,04B3 |
| `05CD81..05CD89` | 8 | DGROUP: UGH!.HI filename | supported-by-code | 013B:0405 |
| `05CD89..05CD8A` | 1 | DGROUP: zero byte (alignment candidate) | supported-by-code | no direct reader found |
| `05CD8A..05CD90` | 6 | DGROUP: three player animation boundaries | supported-by-code | 013B:41B8 |
| `05CD90..05D0B0` | 800 | DGROUP: 46 terminated sprite sequences | verified-by-decode | 013B:1582,1646,2AB5; descriptors |
| `05D0B0..05E6A4` | 5,620 | DGROUP: four demonstration tables and 28 motion scripts | verified-by-decode | 013B:088D,08A2,08C7,08CF,0AEB,09D7 |
| `05E6A4..05E6AC` | 8 | DGROUP: four single-plane and four cumulative VGA masks | supported-by-code | 013B:4106,413A |
| `05E6AC..05E6DC` | 48 | DGROUP: global game state and difficulty constants | supported-by-code | 013B:010E,0125,0C07,3F55 |
| `05E6DC..05E81C` | 320 | DGROUP: current 20x16 tile map | supported-by-code | 013B:39AB,4172 |
| `05E81C..05E836` | 26 | DGROUP: input commands and control-option state | supported-by-code | 013B:45BF,04CA |
| `05E836..05E860` | 42 | DGROUP: HUD, fade and cached score state | supported-by-code | 013B:3D66,3F55 |
| `05E860..05E8AC` | 76 | DGROUP: two-player parallel state fields | supported-by-code | 013B:39B9,418D |
| `05E8AC..05E979` | 205 | DGROUP: 34 six-byte keyboard sequences and FF sentinel | supported-by-code | 013B:450A,4567 |
| `05E979..05E993` | 26 | DGROUP: current 26-byte level record | supported-by-code | 013B:3976 |
| `05E993..05E999` | 6 | DGROUP: water line current/previous and VGA extent | supported-by-code | 013B:2D2F,2DDA |
| `05E999..05E99D` | 4 | DGROUP: two level-order near pointers | supported-by-code | 013B:397D |
| `05E99D..05EA3D` | 160 | DGROUP: eight parallel arrays of ten platform words | supported-by-code | 013B:3A67,13FD |
| `05EA3D..05ED3D` | 768 | DGROUP: 24 parallel arrays of sixteen actor words | supported-by-code | 013B:3AA9,149C |
| `05ED3D..05EDFB` | 190 | DGROUP: 19 parallel arrays of five enemy words | supported-by-code | 013B:3B1B,23C8,25B1,295B,2A87 |
| `05EDFB..05EF1B` | 288 | DGROUP: 12 parallel arrays of twelve falling-item words | supported-by-code | 013B:2B7F,2B96 |
| `05EF1B..05F3A1` | 1,158 | DGROUP: three parallel arrays of 193 rain words | supported-by-code | 013B:3C04,3C35,3C78,3D19 |
| `05F3A1..05F3D5` | 52 | DGROUP: joystick sampling/calibration state | supported-by-code | 013B:50C6,51EC |
| `05F3D5..05F3D9` | 4 | DGROUP: four zero bytes, owner unknown | unknown | no direct reader found |
| `05F3D9..05F465` | 140 | DGROUP: 69 one-player record pointers plus FFFF | verified-by-decode | 013B:3976 |
| `05F465..05F509` | 164 | DGROUP: 81 two-player record pointers plus FFFF | verified-by-decode | 013B:3976 |
| `05F509..05FD43` | 2,106 | DGROUP: 81 packed 26-byte level records | verified-by-decode | 013B:3976 |
| `05FD43..0636C0` | 14,717 | DGROUP: level platforms, itineraries, actors, enemies, text, reward lists | verified-by-decode | 013B:3A67..3BFE,149C,2B34,077C |
| `0636C0..0637B0` | 240 | DGROUP: four 60-byte enemy descriptors | verified-by-decode | 013B:23C8,25B1,295B,2A87 |
| `0637B0..063A00` | 592 | DGROUP: eight 74-byte actor descriptors | verified-by-decode | 013B:149C..2195 |
| `063A00..063ADC` | 220 | DGROUP: eleven 20-byte falling-item descriptors | supported-by-code | 013B:2B34,2B96..2CAD |
| `063ADC..063C0C` | 304 | DGROUP: timer dispatcher state, sixteen slots | supported-by-code | 0A32:0008,00D2,01AA,021B,02C1 |
| `063C0C..063EBE` | 690 | DGROUP: runtime library data and initialization table | supported-by-code | docs/runtime.md |

## Pack-Ice

**Verified:** all five decodes equal original-routine references byte for byte, and
all five independently repack to the complete original ICE stream, including headers.
`decode --all` fails on a length/invalid-reference error or an available retained
reference mismatch. `repack --all` fails on any compressed-byte difference. The
stream's following paragraph fill is separate and remains explicitly zero.

| Frame | Decoded bytes | Packed bytes | Differing repack bytes | Meaning |
|---|---:|---:|---:|---|
| `1A38` | 32,000 | 15,972 | 0 | 100 tile maps |
| `2BF6` | 64,768 | 6,713 | 0 | Bones Park Software Artistic logo |
| `2D9A` | 64,768 | 8,255 | 0 | Play Byte logo |
| `2F9E` | 64,768 | 385 | 0 | present |
| `2FB7` | 64,768 | 10,813 | 0 | Ugh! title |

Header: `ICE!`, big-endian u32 packed size **including the 12-byte header**, then
big-endian u32 unpacked size. The DOS routine uses the low word of each size;
all original high words are zero. Both byte and bit input run backward. The bit
byte has a sentinel; when shifting empties it, fetch the next preceding byte and
rotate through carry. Helpers are GAME `013B:4D2A` / `4D37`; the latter reads
`CX+1` bits. Literal lengths use successive ranges 1, 2..4, 5..7, 8..14,
15..269, 270..33037. Matches are 2, 3, 4..5, 6..9, 10..1033 bytes, with
length-dependent offset codes. The copy at `4DCC..4DD7` is **BX+2 bytes**:
one initial byte, then BX+1 loop bytes. The earlier transcription incorrectly
copied 2*(BX+1). No match in these streams needs bytes outside the declared output.

The 64,768-byte results are 64,000 row-major indexed pixels (320x200), followed by
768 bytes of RGB6 triples. GAME `013B:4C81` copies the palette from decoded
`FA00`; `4634` uploads the chunky pixels to unchained VGA. All four PNGs were
visually inspected. `1A38` is **not a picture**: its 32,000 bytes are the 100 tile
maps consumed at `3976`, `39AB`, `4172`.

The independent Python `ice_pack235` uses forward greedy matching, a `1580h` search
window, maximum match length 1033, closest equal-length match, and repeat-run handling.
It generates uppercase `ICE!` directly, without patching a result or consulting the
original token sequence. The public native Pack-Ice 2.35 port provided the search-policy
cross-check: [unice68_pack.c](https://github.com/benjihan/py-icepacker/blob/main/unice68/unice68_pack.c).
Its retained C probe emits `Ice!`; case-normalizing that probe is only a diagnostic.
The Python command compares complete original bytes without normalization.

`crosscheck_ice.py` performed exactly one authorized Unicorn routine invocation for
each of 1A38, 2D9A, 2F9E, 2FB7. The retained earlier worker's
`build/workers/data/ice_2bf6_reference.bin` supplied 2BF6; it was not regenerated.
The four new references, `decode.json` (SHA-256), `repack235.json`, and the five
`python235_*.ice` outputs retain the evidence. Unicorn is not a dataprobe dependency.

## Sprite banks and palettes

**Verified layout:** four pixel banks, not four-plane bitmaps, plus a directory
in 5B63. GAME `013B:425A` reads directory entry `index*4`:
`u16 little-endian bank_offset; u8 width; u8 height`. Indices select banks by
`<00D9` = 1E1F, `<012A` = 37A7, `<0223` = 438A, otherwise 4E83.
There are exactly 662 entries (0..661), followed by eight zero bytes. The four
bank payloads are 55,912 / 48,686 / 44,944 / 52,736 bytes; tails are 8 / 2 / 0 / 0.
Every entry starts exactly where the previous entry's width*height bytes end.

Pixels are column-major: `source[offset + x*height + y]`, one **8-bit color index**
per pixel. GAME `013B:42B1..4344` selects VGA map-mask bits 1,2,4,8 for successive
columns; the destination byte advances only when the mask wraps. This is hardware
plane selection, not planar asset encoding. Zero pixels are skipped (transparent);
there is no separate mask plane. Underwater pixels OR `40h` into their color index
according to their Y coordinate and the water line. `43B9` uses the same dimensions
to restore the old sprite rectangle.

`render --all` transposes every sprite, proves the inverse transpose equals its
original pixel bytes, and writes four compact `png/bank_*.png` sheets. The JSON
beside each sheet gives every ID, offset, native dimensions and sheet position.
All sheets were inspected: terrain and HUD art in 1E1F; trees, bird, dinosaur,
fruit and effects in 37A7; passenger/vehicle frames in 438A; Triopterus, digits
and font in 4E83. The first 174 entries are 16x12 terrain tiles, not 16x16 tiles.
GAME `013B:077C` maps text characters to sprite `character+0237h`; special codes
8E/99/9A map to 5B/5C/5D before that addition. HUD small digits are 204..213.

**Palette source supported by code:** DGROUP `00B3` is `2BC6:0000`.
GAME `013B:466A` copies its first 384 bytes (128 RGB triples) to both halves of
the CS palette at `4681`. DGROUP `00AB` points there, `00AF` points to the fade
buffer at `4981`. `4E36` scales channels by CX/256; `4E72` writes RGB triples
through ports 3C8/3C9. Index bit 6 selects the second 64-color, water-tinted
quarter. The source block's **last 384 bytes are not read by this loader**;
preserve them, without claiming an additional palette-switch use. Sheets/maps use
the actual duplicated first-half palette. The title/logo images use their own
decoded 256-entry palettes, loaded via `4C81`. No Amiga palette proves a DOS byte.

## Levels

**Verified structural decode:** 100 row-major maps of 20x16 tile IDs, 81 distinct
level records, 69 one-player order entries and 81 two-player entries. Every byte
of DGROUP `3CB3..7630` belongs to decoded platform/actor/enemy/text/itinerary/reward
objects; there are no uncovered gaps. Some lists share an FFFF sentinel.

GAME `013B:3976` selects DGROUP order table `3349` or `33D5` through pointers at
`2909`, indexes it by current level, then copies **26 bytes** to `28E9`.
The original level records are contiguous at `3479..3CB3`. These are packed
records, so unaligned words must not receive C-compiler padding:

| Byte offset | Layout / use |
|---|---|
| 00 | u16 byte offset into unpacked 1A38; divisible by 320 |
| 02 | u16 near pointer to platform list |
| 04 | u16 near pointer to passenger/stone placements |
| 06 | u16 near pointer to enemy placements |
| 08 | u8 remaining passenger count; byte 09 preserved, meaning unresolved |
| 0A | u16 near pointer to title/instruction text |
| 0C | u8 weather mode; 0 none, 1/2 rain direction (`3C78`) |
| 0D / 0F | u16 player 1 initial X / Y in 1/32 units |
| 11 / 13 | u16 player 2 initial X / Y in 1/32 units |
| 15 | u16 initial water line in 1/32 units |
| 17 | i16 water-line increment (`2D42`) |
| 19 | u8 preserved; no read found after the level copy |

Y coordinates are transformed by `3D4D`: y - (signed y >> 2). Player setup
subtracts 0200h from X and 0140h from transformed Y before shifting right by 5.
Water is capped to 17E0h before shifting. The maps render at 320x192 because
`4172` advances X by 16 and Y by 12.

Platform list (`3A67`): repeated **eight u16 words**, ending with a single
negative/FFFF first word. Fields: left/right collision bounds, Y (transformed
by 3D4D), boarding/walking X, waiting X, enemy/tree attachment X, HUD/destination
identifier, and a skipped/reserved eighth word. `13FD`, `153B`, `1617`, `1B29`
show the three different X uses. Passenger placements (`3AA9`) are three u16:
descriptor pointer, initial platform index, itinerary pointer, ending with FFFF.
An itinerary is repeated `(u16 platform_index,u16 wait)` plus FFFF;
`149C/14DD` advance it and multiply waits by 3/2. Descriptor 78DC is the stone
case and does not interpret its third word as an itinerary.

Enemy placements (`3B1B`) have a descriptor word and type-dependent tails:
7630 (bird) and 766C (Triopterus) occupy 8 bytes; 76A8 (dinosaur) occupies 10;
76E4 (tree/reward source) occupies 6. The list ends with FFFF. Bird and Triopterus
tails hold platform/parameter/speed words; dinosaur uses X,Y plus two skipped
words; tree uses platform index and reward-list pointer. The single shared reward
list at `3CB3` contains nine near pointers into the falling-item descriptors and
FFFF, consumed at `2B34`. Preserve skipped fields as explicit reserved words.

`levels.json` contains every field and list; `levels.txt` includes every map as hex
tile IDs. `png/maps/00.png..99.png` and `png/maps_all.png` render **all** maps,
including those absent from either play order. The full sheet and representative
levels were visually inspected. Map 0 is used by `0720`; map 90 (offset 7080h)
by `0712`. Unreferenced maps remain data, not discarded padding.

The uppercase sequences formerly called “level names” at `00EE` and `0492`
are the **password lists**, selected by player count at `0C07` and displayed at
`06B5`. Real displayed level names/instructions are the record's text pointer.
Both lists are NUL-separated strings with a final FF byte. The order is:

| Players | Level | Password | Map | Record | Displayed title / instruction |
|---:|---:|---|---:|---|---|
| 1 | 1 | CAVITY | 1 | `3479` | INTRODUCING / PLATFORMS |
| 1 | 2 | FIRSTCOMMUNION | 28 | `371D` | INTRODUCING BIRD! |
| 1 | 3 | FIGURATIVETHEATRE | 9 | `3549` | INTRODUCING / FUNNY WATER |
| 1 | 4 | BURNTOFFERINGS | 5 | `34E1` | INTRODUCING / DINO |
| 1 | 5 | MYSTERIUMINQUITATIS | 2 | `3493` | INTRODUCING / TRIOPTERUS! |
| 1 | 6 | DREAMFORMOTHER | 24 | `36B5` | INTRODUCING / DIVING |
| 1 | 7 | UNCERTAINJOURNEY | 6 | `34FB` | ZICK ZACK |
| 1 | 8 | SPIRITUALCRAMP | 64 | `3A91` | FUNNY WATER BUT / YOU WILL MAKE IT |
| 1 | 9 | ROMEOSDISTRESS | 23 | `369B` | BOTTLENECK I |
| 1 | 10 | RESURRECTION | 29 | `3737` | HOW CAN I GET / OVER THERE? |
| 1 | 11 | PRAYER | 51 | `3959` | NASTY TREE |
| 1 | 12 | DEATHWISH | 70 | `3B13` | BIG CAVE |
| 1 | 13 | DOGS | 71 | `3B2D` | DIVING FUN |
| 1 | 14 | DESPERATEHELL | 20 | `364D` | PRETTY PLATFORMS |
| 1 | 15 | AWAKEATTHEWALL | 65 | `3AAB` | THE TRIOPS AND YOU |
| 1 | 16 | SLEEPWALK | 66 | `3AC5` | THE EASY CAVE |
| 1 | 17 | THEDROWNING | 15 | `35CB` | MY FIGHT AGAINST / THE TRIOP |
| 1 | 18 | THEBLUEHOUR | 67 | `3ADF` | DINO LIKES / THE LADIES |
| 1 | 19 | ASEVENINGFALLS | 8 | `352F` | DIVING FOR / PROFESSIONALS |
| 1 | 20 | ANDROGYNOUSNOISE | 26 | `36E9` | A CAPITAL G |
| 1 | 21 | HANDPERMEATES | 73 | `3B61` | EASY TRIOP |
| 1 | 22 | ELECTRADESCENDING | 22 | `3681` | MANY DESTINATIONS |
| 1 | 23 | CERVIXCOUCH | 69 | `3AF9` | TOWER OF ATLANTIS |
| 1 | 24 | THISGLASSHOUSE | 39 | `383B` | A CAVE UNDER WATER |
| 1 | 25 | FLEEINGSOMNAMBULIST | 43 | `38A3` | THE CHRISTMAS TREE |
| 1 | 26 | THESOMNOLENTPERSUIT | 42 | `3889` | IN THE CAVE |
| 1 | 27 | ASHES | 72 | `3B47` | TREES ON THE TOP |
| 1 | 28 | ASHESPARTII | 38 | `3821` | DIVERS DELIGHT II |
| 1 | 29 | WHENIWASBED | 34 | `37B9` | BOTTLENECK / FOR BEGINNERS |
| 1 | 30 | LAMENTOVERTHESHADOWS | 11 | `357D` | ESPECIALLY FOR YOU |
| 1 | 31 | FACE | 44 | `38BD` | TWISTING / BY THE POOL |
| 1 | 32 | THELUXURYOFTEARS | 53 | `398D` | TRIOPTERUS NASTIUS |
| 1 | 33 | OFTHEWOUND | 56 | `39C1` | MAY THE FORCE / BE WITH YOU |
| 1 | 34 | BELIEVERSOFTHEUNPURE | 61 | `3A43` | THE LAST TRIOPTERUS |
| 1 | 35 | OUVERTURE | 52 | `3973` | WODDEN PROBLEMS |
| 1 | 36 | WINDKISSEDPICTURES | 30 | `3751` | ZICK ZACK DIVING |
| 1 | 37 | THELAKEOFFIRE | 18 | `3619` | A DAY AT WOOLWORTH |
| 1 | 38 | BLASTOFTHEBOUGH | 7 | `3515` | BEWARE OF THE DINO |
| 1 | 39 | AMATERASU | 14 | `35B1` | TINA TRIOP / AND / DONALD DONI |
| 1 | 40 | THEABSOLUTE | 12 | `3597` | TWO TRIOPS |
| 1 | 41 | LACRIMACHRISTI | 37 | `3807` | THE STAIRWAY / TO HEAVEN |
| 1 | 42 | BETWEENYOUTH | 45 | `38D7` | RACE FOR FUEL |
| 1 | 43 | AFTERTHERAIN | 46 | `38F1` | GIRLS THEY WANNA / HAVE FUN |
| 1 | 44 | WILLOTHEWISP | 54 | `39A7` | LONELY TREE |
| 1 | 45 | TALESOFINNOCENCE | 47 | `390B` | TRICKY DIVING |
| 1 | 46 | STRAPPINGMEDOWN | 57 | `39DB` | IN A SMALL CAVE |
| 1 | 47 | THEDANZIGWALTZ | 59 | `3A0F` | GRANNYS HOME |
| 1 | 48 | CHIMEREDESIDELA | 40 | `3855` | THE CAPITAL I |
| 1 | 49 | SILENTTHUNDER | 62 | `3A5D` | BIRDY IN THE CAVE |
| 1 | 50 | STRANGEFORTUNE | 60 | `3A29` | THE LITTLE CHAMBER |
| 1 | 51 | VENTRILOQUIST | 58 | `39F5` | DON'T MESS WITH / THE TRIOP |
| 1 | 52 | GLOOMYSUNDAY | 48 | `3925` | LOST IN A CAGE |
| 1 | 53 | THEDEATHOFJOSEF | 32 | `3785` | DIVERS DELIGHT I |
| 1 | 54 | SONGOFSOLOMON | 16 | `35E5` | DIAGONAL DISASTER |
| 1 | 55 | SICKOFLOVE | 17 | `35FF` | DON'T DROWN / THE GRANNY |
| 1 | 56 | VANITY | 41 | `386F` | GREETINGS / FROM ALFRED |
| 1 | 57 | FOURHORSEMEN | 49 | `393F` | TOWER OF BABEL |
| 1 | 58 | 1983 | 19 | `3633` | DANGER DUNGEON |
| 1 | 59 | OMEGADAWN | 4 | `34C7` | ELEVATOR ACTION |
| 1 | 60 | ARINGINGINTHEIREARS | 3 | `34AD` | DINO AND THE BIRD |
| 1 | 61 | THEGOLDENAGE | 27 | `3703` | DINOS DEEP DUNGEON |
| 1 | 62 | ALPHASUNSET | 33 | `379F` | UNKNOWN DESTINATION |
| 1 | 63 | SPILTBLOOD | 74 | `3B7B` | DUNGEON DIVERS |
| 1 | 64 | RAWWAR | 25 | `36CF` | WHAT A RAINY DAY |
| 1 | 65 | REFLECTIONS | 10 | `3563` | TWO BIRDS / BUT EASY TWO FLY |
| 1 | 66 | CHURCHOFNORETURN | 63 | `3A77` | TO BE ON THE TREE |
| 1 | 67 | WHATSTHEVERDICT | 21 | `3667` | TWO TREES AND / A TRICKY TUNNEL |
| 1 | 68 | ZEROSEX | 35 | `37D3` | NEPTUNS FORK |
| 1 | 69 | THISISHERESY | 31 | `376B` | ANCHOR DOWN |
| 2 | 1 | ALONEINTOTHEALONE | 1 | `3479` | INTRODUCING / PLATFORMS |
| 2 | 2 | ONLYSHADOWSOFHOOKS | 28 | `371D` | INTRODUCING BIRD! |
| 2 | 3 | CHRISTSFIRSTHOWLING | 9 | `3549` | INTRODUCING / FUNNY WATER |
| 2 | 4 | FIELDSOFRAPE | 5 | `34E1` | INTRODUCING / DINO |
| 2 | 5 | GREATBLACKTIME | 2 | `3493` | INTRODUCING / TRIOPTERUS! |
| 2 | 6 | MALDORORESTMORT | 24 | `36B5` | INTRODUCING / DIVING |
| 2 | 7 | ADAYINDOGLAND | 6 | `34FB` | ZICK ZACK |
| 2 | 8 | EXTRAECCLASIAM | 64 | `3A91` | FUNNY WATER BUT / YOU WILL MAKE IT |
| 2 | 9 | NULLASALUS | 23 | `369B` | BOTTLENECK I |
| 2 | 10 | THESHELLSHAVECRACKED | 29 | `3737` | HOW CAN I GET / OVER THERE? |
| 2 | 11 | FROMBROKENCROSS | 51 | `3959` | NASTY TREE |
| 2 | 12 | STPETERSKEYALLBLOODY | 36 | `37ED` | EASY! / ISN'T IT? |
| 2 | 13 | BENEDICTION | 70 | `3B13` | BIG CAVE |
| 2 | 14 | BLESSING | 71 | `3B2D` | DIVING FUN |
| 2 | 15 | NORTH | 20 | `364D` | PRETTY PLATFORMS |
| 2 | 16 | BLACKSUNBLOODYMOON | 65 | `3AAB` | THE TRIOPS AND YOU |
| 2 | 17 | OHCOALBLACKSMITH | 66 | `3AC5` | THE EASY CAVE |
| 2 | 18 | PANZERRUNE | 82 | `3C17` | SIX PACK |
| 2 | 19 | BLACKFLOWERSPLEASE | 15 | `35CB` | MY FIGHT AGAINST / THE TRIOP |
| 2 | 20 | THEFINALCHURCH | 67 | `3ADF` | DINO LIKES / THE LADIES |
| 2 | 21 | THESUMMEROFLOVE | 8 | `352F` | DIVING FOR / PROFESSIONALS |
| 2 | 22 | HEYHOTHENODDYOH | 26 | `36E9` | A CAPITAL G |
| 2 | 23 | BEAUSOLEIL | 73 | `3B61` | EASY TRIOP |
| 2 | 24 | SCARLETWOMAN | 78 | `3BAF` | DIVIDE AND CONQUER |
| 2 | 25 | THESTAIRSONG | 22 | `3681` | MANY DESTINATIONS |
| 2 | 26 | HULLOANGEL | 69 | `3AF9` | TOWER OF ATLANTIS |
| 2 | 27 | SINCEYESTERDAY | 39 | `383B` | A CAVE UNDER WATER |
| 2 | 28 | VALEDICTION | 43 | `38A3` | THE CHRISTMAS TREE |
| 2 | 29 | MALEDICTION | 42 | `3889` | IN THE CAVE |
| 2 | 30 | DOGUN | 79 | `3BC9` | FRUIT ALL THE TIME |
| 2 | 31 | FOREVERCHANGING | 72 | `3B47` | TREES ON THE TOP |
| 2 | 32 | THEBALLADOF | 38 | `3821` | DIVERS DELIGHT II |
| 2 | 33 | THEPALECHRIST | 34 | `37B9` | BOTTLENECK / FOR BEGINNERS |
| 2 | 34 | CHRISTANDTHE | 11 | `357D` | ESPECIALLY FOR YOU |
| 2 | 35 | PALEQUEENS | 44 | `38BD` | TWISTING / BY THE POOL |
| 2 | 36 | MIGHTYINSORROW | 76 | `3B95` | STONE I ANAPOLIS |
| 2 | 37 | THEREDFACEOFGOD | 53 | `398D` | TRIOPTERUS NASTIUS |
| 2 | 38 | THEBREATHAND | 56 | `39C1` | MAY THE FORCE / BE WITH YOU |
| 2 | 39 | PAINOFGOD | 61 | `3A43` | THE LAST TRIOPTERUS |
| 2 | 40 | THATSALLFOLKS | 52 | `3973` | WODDEN PROBLEMS |
| 2 | 41 | HAPPYBIRTHDAY | 30 | `3751` | ZICK ZACK DIVING |
| 2 | 42 | THEBIRDSHAVE | 80 | `3BE3` | TRAFFIC PASSAGE |
| 2 | 43 | STOPPEDSINGING | 18 | `3619` | A DAY AT WOOLWORTH |
| 2 | 44 | KHORBAINYESDMIGS | 7 | `3515` | BEWARE OF THE DINO |
| 2 | 45 | LAMENTFORHER | 14 | `35B1` | TINA TRIOP / AND / DONALD DONI |
| 2 | 46 | THEDEATHOFTHECORN | 12 | `3597` | TWO TRIOPS |
| 2 | 47 | ASONGFORDOUGLAS | 37 | `3807` | THE STAIRWAY / TO HEAVEN |
| 2 | 48 | AFTERHESDEAD | 81 | `3BFD` | PASSING WALL |
| 2 | 49 | TERRATEGITTERRAM | 45 | `38D7` | RACE FOR FUEL |
| 2 | 50 | BE | 46 | `38F1` | GIRLS THEY WANNA / HAVE FUN |
| 2 | 51 | HOOVES | 54 | `39A7` | LONELY TREE |
| 2 | 52 | HORSEY | 47 | `390B` | TRICKY DIVING |
| 2 | 53 | THEYRETURNEDTO | 57 | `39DB` | IN A SMALL CAVE |
| 2 | 54 | THEIREARTH | 83 | `3C31` | DOUBLE TROUBLE |
| 2 | 55 | FALLING | 59 | `3A0F` | GRANNYS HOME |
| 2 | 56 | THEDREAMOFASHADOW | 40 | `3855` | THE CAPITAL I |
| 2 | 57 | OFSMOKE | 62 | `3A5D` | BIRDY IN THE CAVE |
| 2 | 58 | PASSINGHORSES | 60 | `3A29` | THE LITTLE CHAMBER |
| 2 | 59 | ANYWAYPEOPLEDIE | 58 | `39F5` | DON'T MESS WITH / THE TRIOP |
| 2 | 60 | TOBLACKENEDEARTH | 84 | `3C4B` | WHERE IS THE STONE? |
| 2 | 61 | OHMERRYGOROUND | 48 | `3925` | LOST IN A CAGE |
| 2 | 62 | CROWLEYMASSUNVEILED | 32 | `3785` | DIVERS DELIGHT I |
| 2 | 63 | PAPERBACKHONEY | 16 | `35E5` | DIAGONAL DISASTER |
| 2 | 64 | THEFALLOF | 17 | `35FF` | DON'T DROWN / THE GRANNY |
| 2 | 65 | CHRISTOPHERROBIN | 41 | `386F` | GREETINGS / FROM ALFRED |
| 2 | 66 | ABEGINNING | 87 | `3C7F` | NEARLY DROWNING |
| 2 | 67 | THEDESCENTOFLONG | 49 | `393F` | TOWER OF BABEL |
| 2 | 68 | SATANANDBABYLON | 19 | `3633` | DANGER DUNGEON |
| 2 | 69 | ASADNESSSONG | 4 | `34C7` | ELEVATOR ACTION |
| 2 | 70 | INTHEHEARTOFTHEWOOD | 3 | `34AD` | DINO AND THE BIRD |
| 2 | 71 | ANDWHATIFOUNDTHERE | 27 | `3703` | DINOS DEEP DUNGEON |
| 2 | 72 | MARYWAITSINSILENCE | 88 | `3C99` | STILL DROWNING |
| 2 | 73 | ASILENCESONG | 33 | `379F` | UNKNOWN DESTINATION |
| 2 | 74 | ALAMENTFORMYSUZANNE | 74 | `3B7B` | DUNGEON DIVERS |
| 2 | 75 | RIVERDEADBANK | 25 | `36CF` | WHAT A RAINY DAY |
| 2 | 76 | ALLTHESTARSAREDEAD | 10 | `3563` | TWO BIRDS / BUT EASY TWO FLY |
| 2 | 77 | ROSYSTARTEARS | 63 | `3A77` | TO BE ON THE TREE |
| 2 | 78 | FROMHEAVEN | 85 | `3C65` | AND WHERE / IS THE TREE? |
| 2 | 79 | WHENTHEMAYRAINCOMES | 21 | `3667` | TWO TREES AND / A TRICKY TUNNEL |
| 2 | 80 | THUNDERPERFECTMIND | 35 | `37D3` | NEPTUNS FORK |
| 2 | 81 | ASADSADNESSSONG | 31 | `376B` | ANCHOR DOWN |

## ADLX music and effects; FORM samples

**Verified structural decode:** eleven standalone ADLX objects, 21,593 actual
container bytes plus separately checked zero alignment; 11,285 events. `music`
checks all event bounds and reconstructs each track/container from decoded fields
byte for byte. It is a format dumper, not an audio-rendering or behavioral certificate.
The three long objects are songs; the eight short objects are effects (one has no
identified caller). No embedded FORM/8SVX sample exists: raw `FORM` hits are parts
of passwords or instruction text. The C module's sample API is present, but game
callbacks `013B:001C..001F` are stubs and no external sample-bank load is implemented.

Container as actually consumed by C `0878:0AA9`:
`ADLX + BE32 root_size; AHDR + BE32 10 + 10-byte header; IMAP + BE32 0;
TRCK + LE32 root_size + events`. The root size excludes its own 8 bytes;
the TRCK word **duplicates root_size in the opposite endian order**, rather than
stating the following event extent. C sets event length to root_size-34. Thus every
observed track begins at offset 42. Do not “correct” these fields to standard IFF.
AHDR payload: LE16 version 2; byte 2 channel count; byte 3 reserved; bytes 4..5
preserved with no consumer found; LE16 at 6 is ticks per timing unit (420 here,
read into SOUND:0238); LE16 at 8 is preserved, consistent with a timer-period value,
but the actual playback period is set by a track event.

The high nibble dispatches through SOUND `0664:174B` / `1919`, the low nibble
selects a channel. The long-song interpreter is at `15D3`, effects at `176B`.
Effects reserve physical AdLib channels using a per-effect base; see C `0CFC`.

| Code | Bytes after code | Meaning from SOUND / C |
|---|---:|---|
| 0n | 1 | wait `(((n<<8)+next)<<7)` ticks |
| 1n | 2 LE | packed OPL frequency/block/key-on word, sent via `1503` |
| 2n | 0 | key off via `14B1` |
| 3n | 1 | channel volume via `1571` |
| 4n | 11 | instrument registers; `1377` copies an extra twelfth working byte, but event advancement is eleven |
| 5n | 0 | no-op |
| 6n | 2 BE | PIT timer period; `16B2` / `184A` |
| 70 | 3 | length/control byte plus two skipped bytes in SOUND; not present in these tracks |
| 71..7F, except 77 | length byte + length | extension skip; not present here |
| 77 | 0 | end/repeat according to playback flags and remaining loop count |
| 80..FF | 0 | wait code & 7F ticks |

Invalid channels matter: in the song interpreter, 1n/4n with n>=9 skip no payload.
All eleven streams end `4D 77`: 4D is one such no-op, **not** a truncated instrument.
The C seek/duration scanners `11AD` / `1A8E` skip nominal opcode payloads without
that channel check, so they are not a safe substitute for the actual SOUND parser.
Frequency words go to A0/B0 OPL registers (word high byte is the B0 control value).
Instrument bytes map to 20/40/60/80/E0 for modulator, 20/40/60/80/E0 for carrier,
then C0 feedback/connection; the melodic OPL operator-index table is in SOUND.

| Frame | Container bytes | Track bytes | Channels | Ticks per pass | GAME 013B call(s) / use |
|---|---:|---:|---:|---:|---|
| `325B` | 71 | 29 | 1 | 420 | 23CE; bird event |
| `3260` | 71 | 29 | 1 | 420 | 2484; bird event, loop flag |
| `3265` | 81 | 39 | 1 | 1260 | 29A2; dinosaur event |
| `326B` | 132 | 90 | 2 | 840 | 0192; password accepted/start transition |
| `3274` | 78 | 36 | 1 | 420 | 1AFA, 2B4E; passenger/reward event |
| `3279` | 7249 | 7207 | 9 | 87360 | 0297, 08BA; score/end sequence |
| `343F` | 71 | 29 | 1 | 6720 | none; no caller found |
| `3444` | 7755 | 7713 | 7 | 60480 | 0C75; gameplay song |
| `3629` | 131 | 89 | 2 | 840 | 06E2; level information transition |
| `3632` | 71 | 29 | 1 | 210 | 1CE4; passenger/stone event |
| `3637` | 5883 | 5841 | 9 | 50400 | 0078; menu song |

Songs start through C `0878:0F88`; effects through `1852`. The call-site table
records exact code references, while the use labels are interpretations of their
surrounding game paths, not recovered tune titles. PIT divisor values and tick
deltas are retained in `music.json`; ticks alone are not seconds when periods change.

**FORM support is code-supported, not asset-verified.** `music FILE.8svx` dumps
standard big-endian FORM/8SVX chunks (including odd-size padding). VHDR payload
is u32 one-shot count, repeat count, cycle count, u16 sample rate, u8 octave,
u8 compression, u32 volume; BODY contains the sample bytes. C `0878:0176`
searches tags bytewise instead of walking all IFF chunks; it reads VHDR payload
offsets 12..13 as rate and offset 15 as compression, then BODY's BE32 size.
It rejects BODY>64000, rounds size down to even, selects mode 2 when compression
is zero and 3 otherwise, and initializes one of eight sample channels. The dumper
preserves compression metadata; it does not claim a verified compressed-sample
audio decoder in the absence of a DOS sample. The external-bank API `06E4` uses
a LE32 directory offset, 12-byte index records beginning directory+8, and a LE32
object offset in each record; both FORM and ADLX tags are accepted there.

## Remaining DGROUP formats

All ranges and consumers are in the object table above. `dgroup` emits 655 decoded
subobjects, including 46 terminated animation vectors, four demonstration pointer
tables, 28 motion scripts, 195 itineraries, 34 keyboard records and all descriptors.
`dgroup_xrefs.json` lists 259 direct field offsets, with numeric code addresses
and complete read/write instructions. It is an index into consumers, not a proof
that indirect accesses or polymorphic fields have been semantically named.

Text: NUL ends a text block; CR advances a line by 16 pixels; FD advances by 8;
FE starts centered text (GAME `013B:077C`). Preserve original CP437 bytes and
control bytes. Credits end FF. Menu templates contain live edit fields.
The five score rows at `0C86` are each 14 name bytes, six right-aligned decimal
score bytes, CR; the whole table then has 00 FF. `03CD` XORs all 107 bytes with FF
for disk I/O to `UGH!.HI`, while `043A/0446` select name/score with stride 21.

Header DGROUP `0092..00EE` is packed: 0092 previous BIOS video mode (u8);
0093 old INT09 far pointer; 0097 new INT09 far pointer (013B:4567); 009B ICE
destination far pointer (0A67:0); 009F current-map pointer (5C09:264C);
00A3 compressed tile-map pointer (1A38:0); 00A7 VGA HUD-bar pointer (A000:0130);
00AB base palette, 00AF faded palette, 00B3 source palette far pointers;
00B7 clearing-workspace pointer (5C09:2648); 00BB DOS file handle (u16);
00BD/BE divisors 10/100 (u8), 00BF/C1 divisors 1000/10000 (u16),
00C3 VGA row stride 96 (u16), 00C5 timer-bar divisor 700 (u16), 00C7 score stride
21 (u8). 00C8..00D5 are two seven-byte digit work buffers; 00D6..00D9 are four
FF bytes with no direct reader found. 00DA has three difficulty-label near pointers,
00E0 two player-count-label pointers, 00E4 three control-label pointers, and
00EA the two password-list pointers. Each far pointer is little-endian offset,
segment; preserve relocation sites, including the two GAME palette-buffer pointers.

The three words at `0CFA` are the boundaries DA/E0/E6 of the two player frame cycles.
`0D00..1020` are u16 sprite vectors terminated FFFF. Enemy/actor descriptors point
to these vectors, so those values are offsets, not sprite IDs. Each motion script
has `(i16 x,i16 y,u16 update_period,u16 GAME_callback)` then a bytecode: nonnegative
u16 sprite (7FFF hides the sprite), i8 dx, i8 dy; a negative word other than 8000
sets a repeat counter; 8000 repeats that block until the counter reaches zero, then
continues, or stops if no repeat remains (`09D7`). Motion deltas add dx*4/dy*4 to
positions stored in 1/32 units. Table starts 1020/1792/1E40/24DE are FFFF-terminated
near-pointer vectors. Every script's exact end is checked against the next script.

Working storage uses **parallel arrays**, not interleaved structs:

| DGROUP range | Element layout | Consumer |
|---|---|---|
| 2614..261C | two u8[4] arrays: 1,2,4,8 and 1,3,7,15 | GAME 4106/413A |
| 261C..264C | packed scalar bytes/words; level, score u32, timer, level counts 69/81, difficulty limits, player count, controls | GAME 010E/0125/0C50/3F55 |
| 264C..278C | u8 tiles[16][20] | GAME 39AB/4172 |
| 278C..27A6 | input/action bytes plus menu/control fields; some unreferenced slots | GAME 45BF/04CA |
| 27A6..27D0 | packed cached HUD words, fade values and byte flags | GAME 3D66/3F55 |
| 27D0..281C | 19 two-word fields; fixed/pixel positions, old positions, frame cycles, passenger attachment, HUD state | GAME 39B9/418D |
| 281C..28E9 | 34 records: three scan-code/FF bytes, action destination offset, action value, mutable matcher state; one FF sentinel | GAME 450A/4567 |
| 28E9..2903 | one packed level record (above) | GAME 3976 |
| 2903..2909 | three u16 water/display values | GAME 2D2F/2DDA |
| 2909..290D | two u16 level-order pointers | GAME 397D |
| 290D..29AD | eight u16[10] arrays at 290D/2921/2935/2949/295D/2971/2985/2999: platform bounds/Y/three X values/destination/current occupant | GAME 3A67/13FD |
| 29AD..2CAD | 24 u16[16], base = 29AD+20h*k; descriptor, placement, itinerary, dispatch/animation state, positions, timing and cached sprites | GAME 3AA9/149C/09D7 |
| 2CAD..2D6B | 19 u16[5], base = 2CAD+0Ah*k; enemy descriptor/platform, positions, speed, callback and animation state | GAME 3B1B and 2379/25B1/295B/2A87 |
| 2D6B..2E8B | 12 u16[12], base = 2D6B+18h*k; falling-item descriptor/callback, sprite, positions and motion | GAME 2B7F/2B96 |
| 2E8B..3311 | three u16[193] at 2E8B/300D/318F: current VGA offset, prior VGA offset, X mod 4 | GAME 3C35/3C78/3D19 |
| 3311..3345 | joystick u16 values at stride 2 plus byte detection flags at 3341; overlapping byte/word tests require original widths | GAME 50C6/51EC |
| 3345..3349 | four zero bytes; owner/use **unknown** | none found |

Descriptor families are structurally decoded and round-tripped as LE16 fields:
enemy 7630/766C/76A8/76E4 have 30 words (60 bytes); eight actor states at
7720 + 4Ah*k have 37 words (74 bytes); falling-item records at 7970 + 14h*k
have ten words (20 bytes). Enemy/actor first four words are geometry/motion
parameters. Their following words include near GAME callbacks and DGROUP animation
vectors; preserve zero entries. Actor offsets 08..2C are 19 GAME callbacks,
2E..38 six animation-vector pointers, 3A..46 seven state/timing/reward words,
48 the paired actor-state descriptor. Enemy offsets 08..20 are 13 callbacks,
22..38 twelve animation pointers, 3A a scalar. Some enemy slots are unused zero.
Falling items have geometry at 00/02, callbacks at 04/06/08/0A, and four scalar
words at 0C/0E/10/12 (animation timing/reward/sprite/type); exact semantic names
for every scalar are not established. All field values are retained in `dgroup.json`.

Timer storage at `7A4C..7B7C` is initialized zero. `7A4C` is the active last-slot
index; seven u16[16] arrays at 7A4E/7A6E (period low/high), 7A8E/7AAE (countdown
low/high), 7ACE (pending flags), 7AEE/7B0E (handle/slot maps); sixteen far callback
pointers at 7B2E; elapsed step u32 at 7B6E; old INT08 far pointer at 7B72;
next timer step u32 at 7B76 and last programmed divisor u16 at 7B7A.
TIMER `0A32:0008/00D2/01AA/021B/02C1` establish these fields. This is application
timer state, separate from Borland runtime data starting at `7B7C`.

## Source representation and remaining uncertainty

| Object class | Proposed readable source | Byte-exactness risk |
|---|---|---|
| ICE pictures/maps | indexed pixel/map bytes plus original RGB6 palette; convert with `ice_pack235`, then explicit paragraph zeros | proven exact for all five current streams; preserve indices, not colors reconstructed from RGB PNGs |
| Sprite pixels/directory | indexed per-sprite assets, explicit ID order, dimensions and LE16 offsets; column-major converter | exact inverse transpose and all endpoints proven; preserve transparent zeros, unused sprites and padding |
| ADLX | typed event lists with explicit raw reserved AHDR fields, original odd length fields and 4D marker | all current objects parse/re-encode; do not normalize endian quirks or unused fields |
| Passwords/text/scores | original byte strings with FE/FD/CR/NUL/FF escapes and explicit fixed-width score fields | preserve CP437 and mutable field widths; Unicode rewriting changes bytes |
| Level/descriptor/animation/motion tables | packed TASM DB/DW fields with labels and explicit widths; callback/data pointers distinguished | preserve unaligned words, shared sentinels, skipped fields and near-pointer addends |
| Working zero storage and C flags | labelled scalar/array zero initializers with exact extents | preserve existing initialized bytes, not BSS; current OMF reader has a known LIDATA issue, so do not assume DUP is accepted |
| Runtime | original C0H/CH.LIB contributions | already attributed separately; do not rewrite |
| Unread/reserved bytes | explicit labelled preserved data until ownership is shown | four zeros at 3345 and four FF bytes at 00D6 remain unresolved; 0CF9 is alignment-supported only |

Other limited uncertainties: the unused second half of 2BC6, the caller of ADLX
343F, AHDR unused fields, level bytes 09/19, skipped placement words, and some
descriptor/working-state scalar names. These do not obstruct structural loading
or the five exact repacks. No PCM sample decode is claimed. The Amiga files remain
semantic clues only; they were not needed to prove these DOS formats.

Negative results, with reproducible probes: the earlier fixed 16x16/four-bitplane
bank guess is rejected by `python tools/dataprobe.py render --all` and the actual
column-copy consumer. Treating 1A38 as a chunky picture renders noise; it is the
map bank. A backward-greedy ICE packer with near/far ties and lazy on/off produced
valid but nonidentical streams (`ice_pack(data,tie,lazy)`, results in `repack.json`);
forward Pack-Ice 2.35 fixes that. Replaying decoded original tokens reproduced all
streams but was only a codec diagnostic, never independent packing proof. Treating
ADLX as normal IFF length/endian conventions overran the last instrument; SOUND's
invalid-channel 4D handling and duplicate root-size TRCK field explain it.

Commands: `python tools/dataprobe.py list`, `decode --all`, `repack --all`,
`render --all`, `levels`, `music`, `dgroup`; `python tools/census.py` remains the
coarse region gate. No oracle relock, source rename or metadata edit is part of this work.
