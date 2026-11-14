# Static Amiga evidence and first DOS correspondence

Worker `amiga`, 2026-11-13. No Amiga program or emulator was executed.
DOS remains authoritative for DOS behaviour. This is a semantic correspondence,
not a matching reconstruction, runtime comparison, or equivalence certificate.

The main findings are:

- All 69 one-player and 81 two-player level-order entries agree by map ID.
  All maps used by those orders are byte-identical after DOS ICE decoding.
- The original identifies DOS descriptor `76A8` as **Dino**, the stationary
  force-producing creature. DOS `766C`, currently named `Dinosaur*` in code,
  is **Triopterus**. Names are proposals only; no DOS source was edited.
- Two passenger itineraries, fares, rescue fares, bonus eligibility, physics,
  collision handling, pool capacities and several state timings differ.
- `JOKE` graphics are ILBM containers with their FORM tag replaced. The BODY
  uses byte-run encoding; there is no unidentified executable cruncher here.
- This disk contains one identified game executable, `t`. The installer uses
  `FILES.000`; its 68020 selection machinery is dormant.

## Reproduction and evidence boundary

Run from the repository root:

```text
python tools/amiga.py
```

Dependency: the already installed Capstone 5.0.7, plus Python's standard library.
No download or project installation was needed. Input is read only:

```text
assets/amiga/Ugh! (1992)(Play Byte).adf
901120 bytes
SHA-256 d2418ca9a3ebceab358dd2c46f0d4df8d0992540c2f91b39a2a28cbfde2ec9fc
```

The script checks that hash because its game-specific data anchors apply to this
disk. `--adf PATH` permits a byte-identical scratch copy; `--out PATH` changes the
output directory. The default is `build/amiga/`:

| Output | Meaning |
|---|---|
| `files/`, `disk.json` | 54 extracted files, OFS block identities, sizes and SHA-256 hashes |
| `t.lst`, `loader.lst`, `install.lst` | Recursive relocated instruction listings, with hunk-relative xrefs |
| `*.routines.json` | Entry/direct-call seeds and explicitly marked pointer candidates |
| `*.flow.json`, `*.xrefs.json` | Direct transfers, unresolved indirect sites, rejected decodes and data/code references |
| `*.hunks.json`, `*.hN.bin` | HUNK inventory, original relocation addends, synthetic load bases, relocated section images |
| `levels.json`, `layouts.json`, `descriptors.json` | Original Amiga records, bounded working tables, descriptor callback pointers |
| `formats.json`, `images/` | File-format census and 25 decoded ILBM PNGs; no asset is changed |
| `dos-comparison.json` | Read-only comparison against the locked existing DOS expansion, if present |

The optional DOS comparison calls the existing `dataprobe.levels()` decoder in
memory. It neither reads that worker's generated JSON as an oracle nor writes
its outputs. It checks the expansion against `metadata/oracle.json`. Without a
DOS expansion the Amiga listing and data extraction still run.

`metadata/amiga-map.json` contains 65 curated routine/table correspondences. Its
classifications concern each entry's stated property, not its entire containing
subsystem. An equal table does not establish equal consumers. Broad subsystem
entries generally say **similar purpose with different implementation**.

## Tooling evaluation

The OFS reader walks directory hash chains and file data chains, checks block
checksums, ownership, sequence numbers, loops and final file sizes. The HUNK
reader handles the CODE/DATA/BSS, RELOC32, SYMBOL and DEBUG records found here.
Every relocation retains its source hunk/site, target hunk and original addend.
Subtracting the selected base from each relocated field must recover every
original stored hunk byte. Synthetic bases start at `10000`, aligned to `1000`;
they are analysis coordinates, not an Amiga memory map.

Capstone recursive descent starts at the first hunk entry, follows direct calls,
conditional branches and fallthrough, then follows relocation-backed stored code
addresses, including callbacks materialized by MOVE/LEA. It also recognizes
PC-indexed vectors of branch stubs. Descriptor vectors of absolute callback
pointers are covered through their relocations. Register-indirect transfers
remain listed rather than assigned invented target sets.

**Candidate handling matters.** A CODE hunk also contains data. The `loader`
has embedded strings referenced by relocations, and decoding those pointers
produces plausible-looking junk. Candidate streams and their descendants are
marked in the listing and routine JSON. They are not certified routine starts.
The main game has six non-library register-indirect dispatch sites: `h0:00E98`
(top-level state), `05A28` (actors), `065D2` (enemies), `06BBE` (items), `07E14`
and `07FB8` (other state/script systems). Absolute descriptor callbacks establish
many targets; complete state-index invariants and indirect closure are unfinished.
Unused, unreferenced code is not recovered merely by linear sweeping.

| Binary | Hunks | RELOC32 sites | Decoded instructions | Routine seeds/candidates |
|---|---:|---:|---:|---:|
| `t` | 9 | 5213 | 8247 | 369 |
| `loader` | 3 | 1400 | 8154 | 175 |
| `install` | 4 | 351 | 1439 | 61 |

The `t` entry/direct-flow pass covers 10030 bytes; pointer-candidate flow expands
the diagnostic decode to 34934 bytes across its three CODE hunks. These numbers
are decode coverage, not proven code ownership. The main game has no exported
symbols; the installer has 319 HiSoft symbols.

Ghidra 12.1's headless analyzer was evaluated locally. Its standard installation
does **not** recognize this HUNK file directly (`No load spec found`). Raw import
with `BinaryLoader`, `68000:BE:32:MC68020`, base `10000` works. The small
`build/workers/amiga/AmigaProbe.java` uses Ghidra's independent pseudo-disassembler
to check instruction lengths at Capstone's hunk-0 addresses:

```text
python build/workers/amiga/evaluate_ghidra.py
t      exit 0: checked=7776 different=0
loader exit 0: checked=8154 different=5
```

All five loader disagreements are candidate streams in printable strings
(`02E7E`, `042C0`, `046E8`, `047CE`, `047F4`); none is entry/direct-flow evidence.
This is a decoder-length cross-check, not independent reachability proof.
The first shell-redirection invocation produced a PowerShell native-stderr
error despite a successful script; the Python runner captures the real exit code.
Logs and exact arguments/environment are retained in `ghidra-evaluation.json`.
Capstone is the default because the complete disk/HUNK/relocation workflow is
small and reproduces without a Ghidra project or third-party HUNK loader.

020 decoding is used for the guarded startup `MOVEC`, not as a claim that normal
gameplay requires a 68020. At `h0:00004` the program tests an Exec CPU flag and
passes `h0:00018` to a supervisor call only on the corresponding path. The latter
contains the cache-control instructions; the ordinary path skips it.

## Which game binary and which installer path?

The correspondence uses the disk's `t`:

```text
158228 bytes, 9 hunks
SHA-256 6826d1f7438e856367d2f78a6b546189517d1255e0f0ca526949d14e214355e7
```

Both `s/startup-sequence` and `UGH` run `loader` then `t`. The installer file list
`FILES.000` includes `UG1:t` and the shared graphics/music. No `FILES.020` or
second game file is present. Twelve disk files parse as ordinary HUNK files;
their inventory includes system commands, installer, loader, `TFMX.obj`, and `t`.
HUNK-header byte hits inside graphics fail structural parsing. The other files
are catalogued in `formats.json`; no separate packed game was identified. This
is a bounded negative result for this disk, not a claim about other releases or
arbitrary concealed/encrypted payloads.

The installer's debug symbols give especially clear evidence:

- `ASK020REQUEST`, `h0:00152`, constructs the 68020 prompt, but has no observed
  call path from the installer entry.
- `SETSRCDEVFILELIST`, `h0:007DA`, reads the CPU word, ANDs `000E`, and branches
  to `NO020` at `007EA`. That is also the next instruction: both outcomes select
  `FILELISTSTR` at `h2:00303`, the string `FILES.000`.
- `FILELIST1STR`, `h2:0030D`, contains `FILES.020` but is not selected there.
  The packed/unpacked install choices share this file-list selection.

Thus the observed installation copies the ordinary `t`; the prompt/string alone
does not prove a second build exists.

## Program structure and coordinates

Write Amiga addresses as `hunk:offset`, for example `t h8:0B58C`. DOS addresses
below are frame-relative: GAME `013B`, DGROUP `5C09`. Never compare a synthetic
Amiga address directly with a DOS linear offset.

| `t` hunk | Kind | Size | Supported role |
|---:|---|---:|---|
| 0 | CODE | 35412 | Main assembly game, device control, state machines and drawing helpers |
| 1 | BSS | 32052 | Scratch and map-bank load destination (`Raster` at offset `32`) |
| 2 | DATA/chip allocation | 30688 | Blitter/display working storage; not fully semantically partitioned |
| 3 | CODE | 592 | DOS file open/read/close and ILBM/8SVX chunk loader |
| 4 | BSS | 12 | Loader handle/length/compression state |
| 5 | CODE | 1488 | Object clipping/compositing and blitter helpers |
| 6 | DATA | 16 | Helper-module state/pointers |
| 7 | BSS | 8016 | Working buffer; complete ownership unresolved |
| 8 | DATA | 68848 | Text, descriptors, animation/script state, level records/lists, load buffers |

`loader` is a separate compiled-C intro program (frame links, library calls and
embedded diagnostics); it has a listing, but its compiler and routine-level DOS
intro correspondence remain unresolved. `t` loads the external TFMX program and
mdat/smpl banks. Its audio call addresses in reserved DATA space refer to code
loaded later; they must not be decoded from the initial zero-filled reservation.

## Anchors and data layout

The method begins with maps and displayed level text, then follows record
pointers into platform/actor/enemy lists and descriptor consumers. It does not
use similar instruction counts or arbitrary binary runs to assign identity.
DOS call/data relationships were checked with `tools/graph.py` for physics,
passenger boarding, Dino, Triopterus, tree rewards and water; the collected
graphs are in `build/workers/amiga/graph-*.txt`.

`Raster` and the decoded DOS bank are both 32000 bytes: 100 maps of 20x16 IDs.
Exactly 78 bytes differ: 18 in map 0 and 60 in map 90, both attract backgrounds.
The other 98 maps, including every map in either play order, agree byte for byte.
The stored platform lists and all principal level scalars agree before DOS
coordinate conversion. One displayed title is `STONE-I-ANAPOLIS` versus DOS
`STONE I ANAPOLIS` (two-player level 36).

Amiga level record (`h8:0B58C`, stride 38) versus DOS (`DS:3479`, stride 26):

| Meaning | Amiga byte offset/type | DOS byte offset/type |
|---|---|---|
| Map-bank byte offset | 00 u16 | 00 u16 |
| Platform, actor, enemy lists | 02/06/0A u32 pointers | 02/04/06 u16 near offsets |
| Initial completion count | 0E u16 | 08 u8; byte 09 retained |
| Mutable completion count | 10 u16; initialized from 0E | copied current-record count at 08 |
| Displayed text | 12 u32 pointer | 0A u16 near offset |
| Weather, reserved | 16/17 u8 | 0C u8 weather |
| Player 1 X/Y; player 2 X/Y | 18/1A/1C/1E u16 | 0D/0F/11/13 u16 |
| Water Y / increment | 20 u16 / 22 i16 | 15 u16 / 17 i16 |
| Trailing scalar | 24 u16 | 19 u8 retained |

Do not interpret every trailing/reserved field merely because it is equal.
DOS applies `y-(signed y>>2)` and speed/wait `v+(signed v>>1)` in selected
consumers. Equal raw level coordinates are not equal displayed coordinates.

Amiga platforms are nine words, including a long occupant field. Actor and enemy
placements are each 12 bytes; DOS uses six-byte actor entries and type-dependent
enemy tails. Amiga itineraries are `(u32 platform pointer,u16 wait)` pairs plus
FFFF, corresponding to DOS `(u16 platform index,u16 wait)` pairs. All 493 ordered
actor placements and 265 enemy placements have the same counts and type order;
checked enemy parameters agree. The same unique record is counted in both play
orders here. Two itinerary changes are real:

| Map/title | Ordered levels | Amiga first actor's platform sequence | DOS |
|---|---|---|---|
| 4, ELEVATOR ACTION | 1P59 / 2P69 | 1,0,4,2,3 | 0,0,4,2,3 |
| 3, DINO AND THE BIRD | 1P60 / 2P70 | 1,0,4,2,1 | 0,0,4,2,0 |

Wait words agree. These affect where that actor appears/travels under normal
level initialization; they are not normalized as coordinate encoding changes.

Working storage also differs structurally:

| Amiga table | Stride/count | DOS counterpart |
|---|---|---|
| `h8:0506A` platforms | 18 bytes x10, FFFF | eight parallel u16[10] arrays |
| `h8:05120` generic objects | 34 bytes x26, FFFF | distributed player/actor/enemy/item fields |
| `h8:0598E` craft state | 28 bytes x2 | parallel player fields |
| `h8:059C8` water | separate surface object/state | scalar Y32, pixel Y, phase/render state |
| `h8:059E4` actors | 32 bytes x5, FFFF | 24 parallel u16[16] arrays |
| `h8:05E76` enemies | 26 bytes x5, FFFF | 19 parallel u16[5] arrays |
| `h8:060B2` items | 18 bytes x5, FFFF | 12 parallel u16[12] arrays |

The tool asserts the table endpoints/sentinels. Generic object fields include
X32/Y32 at +04/+06, direct velocities at +08/+0A, targets at +10/+12, animation
object pointer +14, sprite origin offsets +18/+1A and active flag +1C. These are
not layout-compatible with the DOS arrays. Actor descriptors are 126 bytes,
enemy descriptors 110, item descriptors 30; DOS uses 74/60/20. Land/water actor
descriptors are adjacent on Amiga and switching adds/subtracts 126; DOS uses
the explicit paired-descriptor near pointer at +48.

## Craft physics, landing and crashes

The following summarizes the inspected normal-state path, not all death/demo
states. Amiga `h0:053AE` operates on 16-bit signed position/velocity words:

1. Weather byte 1 subtracts one from vx, byte 2 adds one. It subtracts one from
   the shared level timer per active craft update.
2. Surface contact uses `surfaceY32+128-craftY32`. Entering water damps vy with
   two arithmetic shifts and attaches the craft to the water object; continued
   submersion subtracts one from vy. Airborne gravity adds one and costs two
   timer units. Deeper immersion also has a byte-duration-dependent timer cost.
3. Horizontal controls add +/-2. Airborne up subtracts 3 from vy, releases the
   attachment and costs three timer units; down adds 2 when airborne. The
   water/attachment tests select different paths.
4. Clamp vx to -200..200 and vy to -100..200. `05896` integrates active objects
   by adding those words directly to X32/Y32, with word wrap.
5. `05958` scans inclusive platform X bounds and a downward crossed surface.
   `0557C` rejects landing speeds above 80; accepted landing snaps Y, zeros both
   velocities and stores the platform attachment.

DOS `MovePlayerWithVgaCollisions` (`1095`) instead retains raw velocity words,
uses acceleration 63 horizontally and 70 for thrust, clamps both words to
[-6144,6144], then adds `velocity SAR 6` to 1/32 positions. Air gravity is 27;
submerged accelerations include -193/-21. Water is based on cached pixel Y with
the craft's 18-pixel origin correction. Weather also adds vertical motion in
DOS. These are similar design rules with retuned arithmetic, not an exact
common fixed-point representation.

Amiga terrain collision `07480..07780` uses six blitter zero tests against masks,
separate left/right/top/bottom flags, reflections and slope responses. It tests
linear speed limits and low-word squared-speed expressions. Those word operations
must not be silently rewritten as an unbounded Euclidean norm. Hard/medium/easy
settings install linear limits 10/40/80 and squared limits 225/2500/10000.
DOS samples VGA palette-index bit 7, scans positions in pixel steps, computes an
impact magnitude, and compares 1380/2300/3100 for hard/medium/easy. Its reused
sample address in left/up scans remains a DOS quirk. No mask equivalence,
edge-case collision equivalence or duration conversion has been proved.

## Passengers and stones

Amiga `059FE/05A1E` dispatches descriptor-selected states: itinerary setup,
waiting for an unoccupied platform, arrival animation, waiting/bubbles, approach,
boarding, carried fare, delivery and departure. The land descriptor callbacks
at `h8:05A86+08..50` strongly correspond to DOS `149C..1C0E`. Occupancy is a
pointer/zero on Amiga versus an index/FFFF on DOS. Raw itinerary waits agree,
but DOS scales waits by three halves. Animation, movement and departure scheduling
are not instruction-by-instruction translations.

`05D20` frees the source platform, attaches the passenger to the carrier, hides
the walking sprite and loads fare. `07CDA` decrements fare toward its floor.
Delivery at `05D8C` releases the carrier and adds fare times multiplier to score.
This supports the DOS purpose contracts without certifying complete state traces.

| Passenger descriptor family | Amiga land max/floor | DOS land max/floor | Amiga water max/floor | DOS water max/floor |
|---|---:|---:|---:|---:|
| First pair (`05A86` / `7720`) | 800/200 | 1100/300 | 200/200 | 300/300 |
| Second pair (`05B82` / `77B4`) | 1900/400 | 2600/500 | 400/400 | 500/500 |
| Third pair (`05C7E` / `7848`) | 1200/300 | 1600/400 | 300/300 | 400/400 |

Two additional differences are established by the consumers:

- Amiga quick delivery tests `initialFare-currentFare <= 200` at `05D9E`.
  DOS separately initializes and decrements a 200-update boarding counter, then
  tests it for nonzero. The predicates and boundary/scheduling are different.
- Amiga floating approach `0619E` changes to the land descriptor before selecting
  state 38, reaching land boarding `05D20`. DOS `BoardWaterbornePassenger` reads
  the water fare first, then changes to the land descriptor. For the first pair
  that gives Amiga 800/200 versus DOS 300/300 on this rescue path.

Water passenger motion is reorganized, so callback slot number is insufficient
evidence of identical state meaning. Amiga `05F36` detects downward crossing and
damps vy/4; `05F82` accelerates upward by two until an upward surface crossing,
then snaps and floats. DOS `1DD5` has different buoyancy acceleration tests and
clamps; `1EC0` separately sinks an actor. Surface floating has broadly shared
craft-availability and expiry purposes but different predicates, units and timers.
The DOS signed/equality quirks are not resolved away by the simpler Amiga path.

Stones use the same eight-type descriptor scheme and a shared generic object.
Amiga `063F8` handles boundary damping, water/platform crossing, enemy contact
and gravity. Its contact scan `064B2` centrally selects an enemy hit callback.
DOS enemy updates call `FindThrownStoneHittingEnemy` instead. Their collision
geometry differs; naming agreement does not establish identical hit regions.

## Bird, Triopterus and Dino

| Type | Amiga descriptor | DOS descriptor | Independent identity anchors |
|---|---|---|---|
| Bird | `h8:05EFA` | `DS:7630` | INTRODUCING BIRD, matching placements, bird animation/resource |
| Triopterus | `h8:05F68` | `DS:766C` | INTRODUCING TRIOPTERUS, platform patrol/charge, TriOpt graphics |
| Dino | `h8:05FD6` | `DS:76A8` | INTRODUCING DINO, coordinate placement, Dino.lo5 animation |
| Reward tree | `h8:06044` | `DS:76E4` | platform plus reward-list placement and tree graphics |

Bird `065D4..0673C`: delay, warning cry, choose a craft, launch from the opposite
edge at a target height limited relative to water, fly toward the far X target,
and kill the selected craft on overlap. A stone hit awards 2500 and selects a
stunned/falling sequence. DOS has the same broad phases and score; warning delay
is 150 rather than 100, stun 350 rather than 300, and falling integration differs.

Triopterus `0673E..06A08`: patrol between platform endpoints inset by 16, notice
a craft on that platform, face it and wait, accelerate toward a signed target
speed, transfer horizontal motion/kick the craft upward on contact, then recover.
The score is 1400 in both. Alert waits are 100 versus DOS 150; stun is 300 versus
350. There is a concrete routing divergence: Amiga impact setup `0696C` selects
state `2C` and its countdown handler `069A0`. DOS `288F` selects descriptor +16,
which is `2844` (ordinary recovery), bypassing the nominal impact handler `28A3`.
The existing DOS contract explicitly records that quirk; retain it.

Dino `06A0A..06ACC` is the formerly unresolved stationary hazard, not the patrol
animal. Its animation auxiliary pointer changes force direction. `06A2C` affects
a craft when `0 <= DinoX32-craftX32 <= 3200` and `abs(craftY32-DinoY32) <= 320`,
adding/subtracting the placement force word to vx. Stone handling selects a
300-update stun and score 800. DOS `2973` uses an origin-adjusted rectangle and
animation-offset sign, adds +/-41 to its raw vx and uses a 350-update stun. The
art is a low rock/head-like creature, which explains the earlier cautious visual
reading; its filename, level introduction and consumer chain establish **Dino**.
They do not justify inventing a more specific biological identity.

The resource chain can be followed without executing initialization: `00434`
loads `Dino.lo5` into the allocation referenced at `h8:01A26`; `00A7C` builds its
ten 32x27 sprite descriptors at `h8:03EAE`. Dino's animation object at
`h8:045C2` points to the script `h8:04F72`, whose first sprite is `h8:03EAE`.
The enemy descriptor `h8:05FD6` points to that animation object at +3C/+40/+44/+48.

## Trees, rewards, items and water

The tree reward order is identical after mapping descriptor ordinals:
`0,8,5,7,6,1,4,3,2,FFFF` at Amiga `h8:0C194` / DOS `DS:3CB3`.
The central Amiga stone collision path handles tree hits; tree's `06AF2` callback
itself is RET. Release `06AF4` spawns at the tree position with twice the stone
velocities, clamping initial vy to -100..-20, advances the reward pointer, and
waits 100 updates. DOS `ReleaseTreeReward` spawns from the stone position with
its horizontal velocity and a different vertical transform, then waits 210.
Amiga selects exhausted state immediately after the last release; DOS selects
it at cooldown expiry. Both preserve the finite reward list; trajectories differ.

Amiga `07124` has five item slots and returns on a full pool. DOS has twelve;
its full-pool path consumes saved BX as the return IP. The Amiga's normal return
does not authorize repairing the DOS defect. Item flight `06BC8` handles damping,
water/platform landing and gravity; `06C82` collects/retire items and dispatches
timer, multiplier and life effects. Timer gain caps at 16300 (`3FAC`) on Amiga;
DOS has its own cap and byte/word effects. Equal reward names/order do not certify
the numeric rewards, pool behaviour or physics.

Water `079BC` adds the record increment every call, only storing a signed-positive
result. DOS `2D1C` toggles a phase, applies its increment every second call, and
clamps a negative result to zero. Amiga uses original Y32 geometry; DOS applies
its 3/4 transform and display cap. Both provide a moving surface for craft and
passengers. Copper/blitter/animation rendering versus DOS bit-6 tinting and VGA
surface patterns is a purpose correspondence, with no pixel/time equality claim.

## Graphics format and asset relationship

All 25 `.lo*` images parse as ILBM after treating JOKE as the outer FORM tag.
BMHD supplies dimensions, plane count and compression; CMAP is a palette; BODY
contains row-interleaved bitplanes. The format identification is consistent with
the primary [ILBM specification](https://wiki.amigaos.net/wiki/ILBM_IFF_Interleaved_Bitmap).
The executable's `h3:00210` directly supplies the decoding evidence. Its negative
control-byte path also treats `80` as a 129-byte repeat, unlike the specification's
no-op; none of the observed compressed BODY streams contains that control byte.
`Demo.lo5` is uncompressed. `TriOpt.lo5` has 14 trailing file bytes beyond the
declared container; the tool records those and decodes only the declared BODY.

PNG inspection confirms shared terrain, craft, passengers, bird, Triopterus,
Dino, fruit/items, tree and text content. Amiga terrain cells are 16x16; DOS
terrain is 16x12 and includes collision/color-index conventions of its own.
Three simple 16-to-12 row-selection probes did not recover all DOS terrain
pixels. These are related assets, not a proven lossless re-encoding of every
DOS sprite. The map bank comparison, in contrast, is exact for all playable maps.
Music remains a purpose correspondence: TFMX mdat/smpl versus ADLX/AdLib; no
melody/event/sample equivalence was established.

## Proposals, verification and unfinished questions

`build/workers/amiga/proposals.txt` contains only review proposals: change the
twelve `Dinosaur*` routine names in `25B1..295A` to `Triopterus*`, and name the
four mechanical routines `295B/2973/2A53/2A76` for Dino. Existing behaviour
comments should retain every quirk while changing the animal identity. No source,
relocation layout, region table, name ledger or closure certificate was changed.

The complete DOS gates ran in `build/workers/amiga/proof/`, a copied tools/src/
metadata tree with an independently generated oracle expansion, avoiding shared
build outputs. `oracle.py`, `verify.py`, `asmverify.py` and `cjudge.py` all exit 0:
FULL_PACKED_FILE; plain relocation guard 35; exact ASM contributions; 23/23 exact
C functions. This checks the copied baseline before proposals; it is not proof
that proposed names were applied. Logs are `gate-*.log`. The initial cold attempt
lacked the generated expansion and failed before compilation; `cold-gate-*.log`
retain that setup failure. `python tools/census.py` also passes in the live tree.

Remaining: full indirect target/invariant closure; loader compiler and intro
mapping; all animation scheduling and global update ordering; hardware mask
equivalence; real-time duration conversions; deep audio correspondence; unused
code/data ownership; complete sprite pixel conversion; provenance/other release
variants. No unresolved question blocks using the listing and bounded first map.
Use the mapped consumers to refine DOS contracts, and verify any implementation
change against DOS rather than substituting the Amiga algorithm.
