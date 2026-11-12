# Structured DOS data source

The 23 structured data modules under `src/data/` are generated, maintained source.
`metadata/data-layout.json` is their single curated description; `tools/datagen.py`
reads that description and the hash-locked expanded original to emit TASM source.
The ordinary build assembles the checked-in ASM directly and never runs a generator
or packer. `RESERVE.ASM` remains the separate existing virtual reservation.

This arrangement keeps the payload bytes reproducible while making names, object
boundaries, field widths, pointer expressions and comments editable in one place.
Renames go through `tools/rename.py`: it updates source declarations/references,
the permanent names ledger and the curated layout together. Regeneration preserves
those names. Literal strings are emitted from original CP437 bytes, with printable
ASCII quoted and control/high bytes explicit; Unicode conversion is never implicit.

## Organisation

All layout offsets are integers relative to the module's frame, with half-open
ranges. DGDATA begins at frame offset 0092, not zero; the linker supplies the earlier
runtime contribution. The description contains 2,548 objects and 2,644 labels.

Each module describes its frame, extent, segment alignment/class, optional group,
ordered external declarations, labels and ordered objects. An object has `start`,
`end`, `class`, `comment` and an exact partition of `fields`. A field has `start`,
`end`, `type` (`db`, `dw`, `dd`, `string`), a comment and optionally a symbolic `expr`.
Without `expr`, the initializer comes from the locked original at that address.
With `expr`, TASM emits the expression; full linking proves its bytes and fixups.
Labels carry the spelling, frame-relative offset, declaration type, public flag and
optional evidence-bearing contract. Stable symbol identities remain in names.json.

The generator rejects incomplete/overlapping partitions, invalid widths, duplicate
symbols, unlabelled objects, an UNKNOWN object without an UNKNOWN label, and changed
module extents. A label inside a literal field divides its emission without adding
bytes. This supports low/high-word views and mutable text fields. Symbolic fields
cannot be split by an interior label. Repeated equal values use `dup`; initialization
remains file-backed, including the 64,768-byte ICE scratch workspace.

DGDATA contains:

- The packed game header, symbolic far pointer offsets/segments, conversion constants,
  digit buffers and four option/password pointer vectors.
- Individual NUL-terminated passwords, original text/control bytes, menu edit fields,
  five fixed-width score rows and the DOS score filename.
- 46 sprite sequences, four demonstration pointer vectors and 28 motion scripts.
  Motion headers and opcodes have explicit word/byte widths and GAME callbacks.
- Packed state, map/input/HUD storage, two-player fields and the documented parallel
  platform, actor, enemy, falling-item, rain and timer arrays. Code-named variables
  have their existing names and contract comments at their storage definitions.
- 34 keyboard sequence records; their byte destination offsets are expressions
  between the actual action labels. The final FF sentinel is separate.
- One mutable and 81 original packed 26-byte level records, both level orders,
  platform/placement/itinerary/enemy/reward lists, instruction text and descriptors.
  Every documented pointer uses a label; shared FFFF sentinels have aliasing labels
  and occupy storage once. Unread fields remain explicitly reserved or unresolved.

Far data retains the original link bank boundaries. Each of 662 sprites has a label
and ID/dimensions/column-major-u8 description. The 662 directory records use
`dw offset Sprite_*`, then width/height bytes. The palette is 256 RGB6 triples;
the unused second half is preserved without claiming another loader use.
Eleven ADLX containers have typed 42-byte headers and labelled event payloads.
The 343F object is inside B3279, not a new linked bank. BE32 fields are typed `dd`
initializers with byte-swapped storage explicitly documented. TRCK retains the
original LE32 duplicate root size. There are no embedded FORM/8SVX samples.

## Packed resources

Each ICE stream remains one packed `db` object, including its 12-byte header;
paragraph fill is a separate zero object. These are the exact commands in its comment:

| Frame | Decoded content | Independent exact-repack check |
|---|---|---|
| 1A38 | 100 row-major 20x16 maps | `python tools/dataprobe.py repack 1A38` |
| 2BF6 | Bones Park logo, 320x200 indices plus RGB6 palette | `python tools/dataprobe.py repack 2BF6` |
| 2D9A | Play Byte logo, same layout | `python tools/dataprobe.py repack 2D9A` |
| 2F9E | present picture, same layout | `python tools/dataprobe.py repack 2F9E` |
| 2FB7 | Ugh title, same layout | `python tools/dataprobe.py repack 2FB7` |

These commands check the independent `ice_pack235` against complete original streams.
They do not alter the source or participate in building. A later editable-asset pipeline
would need lossless indexed pixel/map and palette files, a pinned deterministic
Pack-Ice 2.35 policy (including uppercase ICE!, search/tie/repeat behavior), explicit
paragraph fill, and all five complete-stream repack checks plus the full packed-file
gate. RGB screenshots alone cannot preserve original palette indices.

## Numeric views retained for TASM emission

256 of 259 GAME/TIMER numeric DGROUP views now use EXTRN labels. Exactly these three
GAME absolute views remain, alongside their actual storage labels in DGDATA:

| Name | DGROUP offset | Storage / reason |
|---|---|---|
| ActorDescriptors | 29AD | Actor descriptor parallel array; extra OFFSET fixups change plain order |
| ds_2A2D | 2A2D | Mechanically named actor parallel array; meaning is unresolved; same emission constraint |
| ActorOverlayOrScriptCallbacks | 2C2D | Actor overlay/script callback array; same emission constraint |

The original ledger identity controls both the EQU spelling and the storage label.
The code comments identify that relationship. All-EXTRN source has the exact image
and packed proof, but 39 plain relocation positions differ instead of the required
35. Retaining these three restores the original plain sequence (GAME 2, SOUND 26,
DGDATA 7). In the final context, converting each alone yields GAME differences
6 / 9 / 6 respectively, instead of 2. These are measured constraints for this
configuration, not a claim that no other natural source arrangement can work.

Pinned `TASM /kh8192 GAME.ASM,GAME.OBJ,GAME.LST` also shows that an
`equ offset ExternalStorageLabel` remains relocatable: it adds fixups and produces
the same first-view regression. Attempting an absolute derivation with
`offset ExternalStorageLabel - offset ext_5C09 + 092h` fails with
`Can't subtract dissimilar relative quantities`. Thus the retained EQUs visibly
identify their real storage labels in comments and retain their numeric values.
No relocation-layout order or proof transformation was changed.

## Byte accounting and remaining debt

`verify.py` checks the exact generated source/layout agreement read-only before
building. Its disjoint load-image classes use the curated object partition:

| Data-source class | Bytes | Meaning |
|---|---:|---|
| typed and labelled | 100,103 | Structures, strings, pointers, arrays and initialized workspace |
| known-format payload | 223,409 | 202,278 sprite pixels and 21,131 ADLX event bytes |
| packed streams | 42,138 | Five complete ICE streams |
| padding | 159 | Explicit bank/stream fill |
| UNKNOWN | 9 | Four FF bytes at 00D6..00DA, zero at 0CF9, four zeros at 3345..3349 |
| Total | 365,818 | Complete structured source contribution |

Reserved fields with known structural owners remain typed but have no invented
semantic names. Mechanical labels identify uncertain scalar/array meanings.
The zero at 0CF9 is an alignment candidate, without an identified reader or proven
alignment directive; it stays UNKNOWN. The pre-existing 4,584 assembly-owned data
bytes are conservatively reported as UNKNOWN separately. Total remaining file
data debt is therefore 4,593 bytes;
the separate 128 virtual bytes still have unknown historical owner/use. No data
format class is counted as exact ASM/C instruction reconstruction.

## Adding knowledge and checking changes

1. Establish the boundary, field type and meaning from code or a verified decoder.
   Preserve unread/reserved fields. Split the enclosing object/field ranges and
   give each new object a label, a one-line description and the justified class.
2. Edit `metadata/data-layout.json`, then run `python tools/datagen.py`.
   Add new identities with `python tools/symtab.py --register-data`; this preserves
   all existing permanent keys. Use `tools/rename.py MODULE:OLD NEW` for renames.
   Public spellings update every consumer and the layout's pointer expressions.
   UNKNOWN object names must retain an UNKNOWN prefix.
3. Run `python tools/datagen.py --check`, `python tools/symtab.py --check`, the
   relevant `tools/dataprobe.py` command and `python tools/census.py`.
4. Run `python tools/verify.py`, `python tools/asmverify.py` and
   `python tools/cjudge.py`. Require exit 0 for all, including the 35-position plain
   guard and complete expanded/packed equality. Never edit generated proof sources
   under build/link, oracle locks or outputs to manufacture equality.

The generation/check workflow deliberately describes this locked historical image.
A future behavior/data modification needs a separate editable asset/port workflow;
changing the oracle or teaching this generator to read candidate outputs would
invalidate its role here.
