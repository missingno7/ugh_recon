# Actor storage: facts and proposed native views

Worker **actor-design**, 2026-11-13. Analysis and design only. The supervisor must
review the proposal; no native type, closure status, or production implementation
is introduced by this document. The draft is
[actors.h](../build/workers/actor-design/actors.h).

The recommendation is **separate gameplay and demo views, plus persistent renderer
history for the same physical slots**. Their update control is mode exclusive,
but their storage lifetimes are **not disjoint**: an ordinary pre-game-demo to
first-level path reads demo pixel caches in gameplay. Do not clear, reconstruct,
or union away that history on a mode change.

## Evidence and limits

Coordinates below are hexadecimal: `G:` is GAME frame `013B`, `D:` is DGROUP
`5C09`; ranges exclude their upper endpoint. Routine names are modern identities.
The maintained [GAME.ASM](../src/asm/GAME.ASM), its instruction markers, the
[program model](../metadata/program-model.json), and the locked expanded oracle
are the DOS evidence. The model's coarse variable lists alone are insufficient:
they omit the biased completion read and do not explain hazard writes through a
selected stone index. The access appendix below supplies instruction-level sets.

**Established local facts** here mean decoded instructions and bounded immutable
resource enumeration. **Supported path conclusions** additionally assume normal
entry points, DS=DGROUP, DF=0, built descriptors/scripts, valid indices and no
pointer corruption. These are static findings, not equivalence evidence at levels
A-D of modernization. No game or original application was run.

The checked-in model's freshness command returned `metadata/program-model.json
stale`. A fresh model was generated **only** in worker scratch. Comparison found
the actor access instructions/operands/owners and three component records unchanged
after accounting for three accepted cell-name aliases; both relevant indirect-site
records agree exactly. Source-line/receipt changes also explain full-record drift.
See the verification section
and [model-comparison.json](../build/workers/actor-design/model-comparison.json).
Nothing in shared metadata was regenerated.

The audit found 24 arrays, 426 direct or biased memory-access instructions, 81
unique level records in 150 ordered entries, at most five level actors, and demo
vectors of 15/6/5/2 entries (28 scripts). Actor storage is `D:29AD..2CAD`, 768 bytes:
24 independent word arrays of capacity 16, indexed by **2*slot**, not interleaved
records. `2CAD` itself starts enemy storage. An original active prefix needs an
in-array sentinel: its maximum length is 15, despite physical capacity 16.

## The cells and their owners

This table defines the projection vocabulary. The complete readers/writers by
routine and instruction are in the access appendix. “Unused” means no use in that
mode under the stated bounded-index contract; bytes can remain stale.

| D: base | Gameplay view | Demo view | Owner / projection decision |
|---|---|---|---|
| 29AD | descriptor identity; FFFF ends dispatch/draw scans | unused | gameplay type, never the update state |
| 29CD | placement's initial platform; read only for stone positioning | unused | loader input; omit from persistent native slot |
| 29ED | current itinerary leg pointer | unused | journey resource + logical leg index; stone's third placement word is not an itinerary |
| 2A0D | near GAME update handler | near DGROUP bytecode cursor; FFFF ends prefix | gameplay phase versus script + byte offset; never one pointer type |
| 2A2D | platform-wait pose (FFFF/0/1), request/question countdown, or carrier byte index 0/2 | loop restart cursor | phase-specific gameplay aliases versus bytecode offset |
| 2A4D | source/current journey platform number | sticky completion word 0/FFFF | source platform versus completion; not the list terminator |
| 2A6D | destination platform number | unused | gameplay journey state |
| 2A8D | source platform number doubled | unused | derive from source only under paired-write invariant |
| 2AAD | destination platform number doubled | unused | derive from destination only under paired-write invariant |
| 2ACD | scaled journey delay, thrown horizontal step, or floating lifetime | signed repeat-count encoding | separate semantic aliases in gameplay; wrapping repeat word in demo |
| 2AED | X32 word | X32 word | active simulation owns position |
| 2B0D | Y32 word | Y32 word | active simulation owns position |
| 2B2D | last cached pixel X | last cached pixel X | renderer history, with explicit placement/scene seed writes |
| 2B4D | prior cached pixel X for erasing | same | renderer history |
| 2B6D | last cached pixel Y | same | renderer history; also gameplay input |
| 2B8D | prior cached pixel Y for erasing | same | renderer history |
| 2BAD | wrapping animation-vector byte offset, initially FFFE | unused | gameplay animation state |
| 2BCD | predecrement animation countdown | predecrement instruction countdown | separate mode countdowns; zero can wrap |
| 2BED | sprite output; FFFF hidden | sprite output; 7FFF hidden | simulation output, read by renderer; reset service also writes it |
| 2C0D | sprite retained by erase pass | same | renderer-owned erase history |
| 2C2D | destination/question overlay sprite; FFFF absent | near GAME per-frame callback | gameplay presentation output versus typed demo effect |
| 2C4D | previous overlay sprite | unused | renderer-owned erase history |
| 2C6D | thrown vertical step, or raw water-motion accumulator integrated with SAR 6 | immutable header period copied to slot | gameplay motion versus demo cadence; hazard code can modify a selected stone |
| 2C8D | quick-delivery counter; boarding sets 200 | unused | gameplay passenger state |

Important separations established by consumers:

* **Descriptor:** `G:1488` uses `29AD` only to terminate dispatch; state handlers
  load it to select geometry, animation, scalar parameters and transition actions.
  Descriptors are eight records of 74 bytes, `D:7720+4A*k`. The nineteen code words
  are at +08..2C, six animation pointers at +2E..38, period +3E, fare/floor +40/+42,
  floating lifetime +44, carried kind +46, paired descriptor +48. +3A/+3C have no
  actor consumer in this audit; they do not gain invented native meanings.
* **Update:** `G:1492` calls `2A0D`; initializers copy a **descriptor code word**
  there. It is neither the descriptor itself nor an animation cursor. The native
  state enum replaces this stored code identity, with direct transition actions.
* **Script cursor:** `G:09D9/09F6/0A4E` load/read/advance `2A0D` as data. The demo
  callback instead comes from header +6 through `G:0B21/0B24` to `2C2D`, then
  `G:0A15` calls it. Demo never reads actor descriptors.
* **Itinerary:** `G:149C/14A0/14E7/14F3` use `29ED` as a four-byte-leg cursor:
  current +0 is source, +2 is wait, next leg +0 is destination. Departure adds
  four at `1C05`. This is distinct from all three pointers above.

The first six descriptor identities are three land/water pairs
`7720/776A`, `77B4/77FE`, `7848/7892`; `78DC/7926` are distinct stone identities.
Shipped placement lists select **only** `7720`, `77B4`, `7848`, `78DC`, respectively
77, 51, 67 and 74 placements across unique records. Water types arise by pair
switch, not direct placement. `7926` has stone callbacks but is not a shipped
placement, and `G:21A4` only recognizes **78DC** for hazard contact. Preserve that
identity distinction. No generic “any stone type” collision rule is justified.

### Renderer ownership is not exclusive access

The renderer owns the six cache arrays `2B2D/2B4D/2B6D/2B8D/2C0D/2C4D` as
persistent history. Passenger placement explicitly seeds current pixels
(`G:1557/156A`); demo initialization seeds both current and previous pixels
(`0AF9/0AFD/0B0B/0B0F`). These writes are part of the calling operations, not a
license to recalculate caches at every bridge entry.

Gameplay erase first copies current sprite to erase sprite at `0CCA`, then uses
the *old* erase sprite and previous position (`0CC6/0CD6/0CDA`). Only after a
non-hidden old sprite and Y<192 does it exchange the overlay cache at `0CEA..0CF2`.
Consequently overlay history can remain stale when the actor is hidden or clipped;
do not perform an unconditional overlay swap. Overlay rectangles use X+11/Y-13
(`0D02/0D09`); draw uses the same offsets at `0F7C/0F83`.

Gameplay draw skips FFFF before touching pixel caches (`0DF3..0DFA`), copies
current pixels to previous at `0DFF..0E0B`, and only then writes X32/Y32 SAR 5 to
current pixels (`0E0F..0E21`). The caches still update when the later Y clip rejects
the draw. Demo does the corresponding rotation at `0A70..0A92`, skips 7FFF first,
and checks signed upper X/Y bounds afterward (`0A96/0A9F`). Demo erase rotates its
sprite cache at `0ABD..0AC5`, skipping restoration for either FFFF or 7FFF. These
are two-cache histories used with alternating pages, not a freshly derived
position or an invented independent array indexed by page number.

Gameplay reads cached X in platform waiting, approach, floating approach and
walk-to-exit (`162C/196F/2124/1B46`); cached Y feeds water tests and resurfacing
(`15E4/1733/1813/18EF/1E0B/1F7C/1FE9/206F/20C8`). These reads precede the frame's
actor draw. Replacing them with the latest X32/Y32 SAR 5 changes scheduling.
The simulation owns current sprite/overlay outputs; the renderer does not own
their state transitions merely because it draws them.

### Hazard access to actors is a real external dependency

`FindThrownStoneHittingEnemy G:2196` scans the active actor prefix (ascending slot
order, `2198/21FA`), accepting descriptor `78DC`, handler `1CEE`, and nonnegative
vertical step (`21A4/21AC/21B7`). “Descending stone” means **motion direction**,
not reverse slot order. It returns the selected actor byte index in DI. The hazard
updates then negate vertical motion and set sprite 0222. Exact writers are in the
appendix: bird `24F6/24FA`, Triopterus `2659/265D`, `26CF/26D3`, `278A/278E`,
`2881/2885`, nominal alternate recovery `28E0/28E4`, Dino `2A4B`, and tree
`2AF2/2AFA/2AFE`. Tree further reads actor position and velocity at
`2B1F/2B23/2B27/2B2B`. These are accesses to the selected **actor**, not enemy
scratch misidentified by the program model. Closure must retain their timing
after actor updates and before actor drawing (`0DDE/0DE1/0DE4`). The concurrently
assigned hazard worker's files are not changed by this proposal.

## Entries, initialization and lifetime result

There is no actor-mode tag written beside these arrays. The caller/control path
selects their interpretation. Exact paths and initializers:

| Entry / exit | Control evidence and storage effects |
|---|---|
| Reveal demo | menu `G:0080` calls `PlaySpriteRevealDemo 088D`; prepares map 0; vector `D:24DE` selected at `0890`, calls common runner at `0893`. After return, slot 0 X32 is explicitly zeroed at `0899`, then width callback called at `089D`, preserving returned status flags. |
| Attract demo | menu `009A` calls `PlayAttractDemo 08CF`; prepares map 90 at `08CF`, vector `D:1E40` at `08D2`, falls into runner. |
| Pre-game demo | `RunGameFromPassword` calls `PlayPreGameDemo` at `0C54`; wrapper `08C7/08CA/08CD` selects map 0/vector `D:1792`. **Return status is ignored**; session always continues to reset score/lives and initialize level at `0C61/0C67`. |
| Completion demo | menu's post-session level-count branch `0162/0166` calls `PlayGameCompletionDemo` at `01AC`; wrapper `08A2..08C5` changes music and selects map 0/vector `D:1020`. Returns to score/menu through `01AF/01A6/01A9`. |
| Common demo entry | `RunScriptedDemo 08D5` calls `InitializeDemoScripts`, whose actual routine entry is **0AEB**, not the header-reading interior point 0AF7. It writes the per-slot fields listed below, sentinel at `0B44`, calls reset at `0B48`, and tail-steps interpreter at `0B4B` **before** runner clears exit/fade values at `08D8..08E0`. Preserve that order, including callback side effects during this first step. |
| Demo loop / exit | `0911/0922/0925/0928/092B`: erase, interpret, draw, page swap, completion test; input and completion request fade. Negative fade exits at `08F0/08F5` to `0982/0988` with flags from exit-code TEST. No storage cleanup on return. |
| Gameplay entry / retry / next level | first `0C67`, retry `0FD0`, next-level branch `0FE5` all enter `InitializeLevelDisplay 3D66`; its `3E52` calls `LoadCurrentLevelState 3976`, whose actor-list block starts `3AA9`. `3E73` dispatches actors once, then `3E76` tail-calls reset. |
| Gameplay exit | negative fade at `0C84/0C89` enters `0FA7`; lives/completion select retry/next-level/return (`0FB1..0FE7`). No actor storage cleanup at return. Menu can then select completion/demo sequence; every actual demo runner first initializes scripts. |

`PrepareAttractMap0/90 G:0720/0712` shares `072A..0773`: map, palette, pages and
water only, **not actor initialization**. Its REP copies 320 bytes to `D:264C`
(`0745/0748/074B`). Likewise level display's clear at `3D69/3D6F` uses
`LevelWorkspacePointer = D:2648` and 392 bytes, ending at `27D0`, below actors.
Neither is a hidden whole-actor clear.

### Exactly what each entry initializes

For every demo vector entry, `G:0AF7..0B3B` sets current/previous pixel X/Y from
the header; X32/Y32 from the wrapping left shift by five; period from header +4;
callback from +6; cursor to header+8; countdown to one; repeats to zero; done to
zero. `0B44` writes FFFF only to the cursor at the sentinel slot. Descriptor,
itinerary, gameplay animation offset, destination/byte-index words, quick timer,
overlay erase history and **loop-start cursor 2A2D** are untouched. Reset then
sets all sixteen current/erase sprite words FFFF (`0B65/0B69`), and the immediate
step predecrements each countdown to zero and executes its first motion command.
All built periods are 1 or 2. The general word algorithm still predecrements zero
to FFFF and can therefore wait a full wrap; do not rewrite it as a positive timer.

For gameplay, `G:3AB0` writes each descriptor including the sentinel. For active
entries only, `3ABF/3AC4` copy initial platform and third placement word; `3ACB`,
`3ACF`, `3AD3`, `3AD7` write FFFF to sprite, erase sprite, overlay, erase overlay.
Non-stone initialization stores descriptor +8 as update (`3AE4/3AE7`). Stone
78DC stores descriptor +10 (`3AED/3AF0`) and sets X32/Y32 to
`(spawnX-8)<<5`, `(platformHeight-11)<<5` (`3AF4..3B12`); it does **not** set
pixel caches. All other cells are left alone until their state initializer.
The bootstrap dispatch at `3E73` runs land journey setup or stone-wait setup;
reset at `3E76` then hides all sixteen current/erase sprites again.

Land journey setup initializes source/destination and doubled indices together
(`14DD/14E3/14E9/14EF`), and scaled delay (`14F9`), before the wait handler reads
them. Placement sets positions/current pixels and animation before arrival reads
them. Wait/bubble/carrier transitions initialize the phase scratch before its
next live use. Throw initializes both motion terms; resurfacing/sinking initialize
vertical motion; floating initializes lifetime; boarding initializes carrier and
quick timer. Thus the **simulation-only** reuse is supported as separate initialized
views for the shipped entry contract. An exhausted itinerary can leave other cells
stale because it hides the sprite and installs a no-op at `14CA/14D7`.

For demos, the stale loop-start cell is never consumed just because it survived
gameplay: repeats start at zero (`0B37`); only a negative non-8000 instruction
stores both repeat count and restart pointer (`0A23/0A27`); only a still-nonzero
incremented count loads restart (`0A38..0A3F`). The audit traversed all 28 built
scripts to their stop marker, with a poisoned/unset loop-start variable, without
a stale-pointer read. That is bounded evidence about the bytecode/control model,
not execution of L0 or a proof for malformed bytecode.

### A normal cross-mode read: lifetimes are not disjoint

There is a concrete path without corruption or an invalid callback:

1. Start the first 1P level (`CAVITY`; actor placements are land passenger,
   land passenger, stone 78DC). The mandatory pre-game vector `D:1792` has six
   entries, and **slot 2** selects header `D:1CBC`, starting at pixel (320,106).
2. Demo initialization writes slot 2 pixel caches at `G:0AF9/0B0B` and previous
   caches at `0AFD/0B0F`. An immediate input exit still preserves those writes;
   any normal demo drawing can replace them with later demo pixels. Neither
   wrapper return nor `0C61` clears them.
3. The first level's stone occupies the same physical slot. Loader `3AF4..3B12`
   writes only its fixed position. `BeginStonePickupWait 1C0F` writes handler and
   animation fields, reset writes only sprites. Slot 2 pixel caches survive.
4. In the first normal gameplay update `UpdateStonePickupWait` sets sprite 0220
   at `1C41` if no empty craft touches it (the ordinary initial placement has
   player starts away from this stone). Then `G:0DFF/0E03` reads those **demo**
   pixel caches and `0E07/0E0B` copies them into the previous-draw history before
   `0E16/0E21` replaces current pixels with the stone's position.
5. The following erase pass reads previous coordinates at `0CD6/0CDA` for the
   prior erase-sprite word, subject to its Y clip. This history can affect which
   background rectangle is restored; it is not safe to treat the read as dead.

Even without the last observation, step 4 is a definite cross-mode value read.
Do not claim universal lifetime disjointness. The narrower supported result is:
**normal mode dispatch is exclusive; gameplay/demo semantic controls are
initialized before live reuse; renderer history persists across modes**.
The architecture model's question including arbitrary callback corruption cannot
support an unconditional typed-state claim: corrupted pointers can bypass all
initializers. It is already answered negatively on an ordinary valid path.

## Proposed representation and canonical projection

The header draft uses the existing `ObjectPosition` and `ObjectGeometry` style:
word bit patterns, explicit retained wrap and signed comparisons in algorithms,
normal resource pointers/indices, and no original addresses or register model.
It proposes only actor-specific types, no entity registry, allocation system,
universal callback signature, or events framework.

* `GameplayActors` contains the active count and `PassengerStoneSlot`s. A slot
  has a distinct immutable `ActorType`, a stored `ActorPhase`, a typed itinerary
  cursor, platform numbers, fixed position, sprite/overlay outputs and animation.
  Carrier is a player number. State-specific scratch roles have separate named
  members. They are **semantic aliases**, not simultaneously valid inputs.
* `DemoMotionScene` contains slots with a script resource, byte offsets into its
  code, repeat count, countdown, completion, fixed position and sprite. Script
  header effect is `NONE`, `FADE_ON_HIDDEN`, or `REVEAL_WIDTH`. A stopped slot is
  still in the active prefix and continues to predecrement/reload its countdown;
  it is not disabled, removed, or changed to a null cursor.
* `ActorRenderStorage` is a third, persistent object of sixteen histories. Both
  views refer to it by the same slot number through their eventual interfaces.
  Do not embed an independently reset copy in either scene. Presentation outputs
  remain in their simulation view; only cache/erase history belongs here.

Why separate views rather than a union: the two modes have different controls,
resources and meanings, and preserved renderer values outlive mode switches. A C
union would silently make overwriting the gameplay/demo member look like ending
all actor state, while overlay **sprite IDs** and demo **effects** are unrelated
typed values. Union-punning also would not define a conversion from near code
words to near data cursors. Why not one universal record: it admits nonsensical
states such as a demo cursor with a gameplay carrier and suggests a single
dispatcher/type system which DOS does not have. The few shared physical cells
are a bridge concern. Two small mode records and a shared history express the
observed consumers; only the currently active view is authoritative.

A tagged union containing **only** the two semantic views, with history outside,
could later be a valid memory-saving implementation choice after proving its
entry/re-entry conversions. The evidence does not prohibit that arrangement.
This draft avoids committing to it: sixteen slots offer no established storage
pressure, independent types serve the two closures directly, and the DOS address
overlap does not itself justify native overlay layout or implicit conversions.

The independent gameplay aliases make state code readable without normalizing
the original's storage on every transition. This is a deliberate small amount
of duplicate **native capacity**, not a claim that DOS stored several independent
values. A union for gameplay scratch is unnecessary too: transitions can leave a
cell stale, and isolated initializer/handler bridges must preserve that distinction.

### Projection rules

Projection is parameterized by the **entry's known mode**, never guessed from a
handler-looking word or from sprite visibility. It reads the active prefix's
mode-specific terminator: gameplay descriptor FFFF, demo cursor FFFF. It does not
dereference the sentinel slot or unused tail as a live actor. The renderer object
retains all sixteen histories; sprite reset genuinely touches all sixteen slots.

| Original fields | Native projection / inverse rule |
|---|---|
| 29AD | resolve one of eight `ActorType` resource identities. Inverse uses that exact identity, preserving primary/alternate stone and land/water pairing. |
| 29CD | consume as placement input for stone initialization; retain untouched bytes in the bridge after load. No future slot input uses it. |
| 29ED | for passengers resolve a registered journey and current leg. Inverse is that resource's DOS base + 4*leg. For stones do not resolve/dereference; keep its raw placement word bridge-side. |
| 2A0D gameplay | resolve the 21 stored phases below; reverse through the approved phase map. Direct initializer bridges call named actions. Family-superset words not established as stored phases are a bridge contract failure/fallback, not silently “retired.” |
| 2A0D demo | resolve script identity and byte offset from its code beginning (header+8). The stop marker's offset remains valid after completion. Validate the cursor is an instruction boundary in that script. |
| 2A2D gameplay | platform-wait phase -> `waiting_pose`; four land/water request/question phases -> `request_ticks`; carried passenger/stone -> `carrier=word/2`. Other phases have no live input from this cell; inverse writes only an operation's actual effect. Carrier conversion requires exactly 0 or 2 and a valid player. |
| 2A2D demo | `repeat_start` byte offset in the same script, meaningful only when repeats!=0. With zero repeats its stale word is unprojected and unchanged until the interpreter actually sets it. |
| 2A4D/2A8D gameplay | source platform and its doubled index. Project one number only where valid, requiring the paired-write invariant; store both only when journey setup writes them. |
| 2A6D/2AAD gameplay | destination and doubled index, same rule. Preserve their stale words when journey exhaustion does not write them. |
| 2A4D demo | zero -> not finished, FFFF -> finished. This is sticky until scene initialization; native bool is allowed only under that two-value invariant. Completion scan at `09CB` actually uses `2A4B+BX` **after** BX+=2; it reads this slot's 2A4D, not another unmodeled field. |
| 2ACD gameplay | wait-for-platform -> `journey_wait`; thrown stone -> `horizontal_step`; floating -> `floating_ticks`. Tree release borrows the thrown stone's horizontal step. Other phases do not consume this cell. |
| 2ACD demo | `repeat_count` is the exact word encoding; negative non-8000 installs it, each repeat marker increments toward zero. Do not reinterpret as a conventional unsigned iteration count without a separate proof. |
| 2AED/2B0D | copy word patterns to active view's `ObjectPosition`; inverse word copy. Do not aspect-scale again. |
| 2B2D/2B4D/2B6D/2B8D | exact `ActorRenderHistory` word copies. Never recompute during projection. Only the actual draw/placement/scene operations write them. |
| 2BAD/2BCD gameplay | retain animation byte offset and countdown words, including FFFE seed, zero, and wrap. Vector resource mapping validates accessible sprite reads. |
| 2BCD demo | exact countdown word; script period is the immutable input it reloads, not the current countdown. |
| 2BED | active view's exact current sprite. Preserve FFFF vs 7FFF; do not collapse both to a shared invisible Boolean. |
| 2C0D/2C4D | erase sprite/overlay word copies in persistent render history. Demo does not write overlay history. |
| 2C2D gameplay | exact overlay sprite output. It is not part of renderer-owned history until the erase rotation writes 2C4D. |
| 2C2D demo | resolve only the three built code identities to `script->effect`; validate identity against the selected header. Inverse only on scene initialization; no overlay-sprite write from a dormant gameplay snapshot. |
| 2C6D gameplay | `vertical_motion` word; interpretation depends on phase: direct thrown step versus water raw term SAR 6. Keep hazard reversal as a word operation. |
| 2C6D demo | validate against `script->period`, an immutable copied input for the current scene. Inverse writes it only at initialization; malformed/mutated-period cases need an extended contract or L1 fallback. |
| 2C8D | exact `quick_delivery_ticks`, live only for carried passenger/delivery; untouched in demo. Decrement only positive signed values, test delivery bonus for nonzero. |

The bridge must be **effect preserving**, not a dump of every host struct member
back into RAM. On entry it projects the inputs live for that routine/action and
imports renderer caches separately. On return it publishes the exact original
write footprint for the path taken, plus any explicitly returned cross-component
effects. This is especially necessary when one cell has several native aliases.
Each closure's narrow bridge should express those writes directly; no shared
generic entity-change tracker is proposed.

For example, boarding writes `carrier` to 2A2D and sets the carried phase; it must
not subsequently publish `waiting_pose` or an old request counter into that cell.
Beginning approach does **not** write 2A2D: it must preserve the old request word,
even though that word has no live approach meaning. Demo writes the loop cursor
only on a repeat directive, never by serializing the inactive gameplay aliases.
Switching from demo to gameplay reprojects after the actual loader/bootstrap;
it neither flushes the old demo snapshot nor zeros uninitialized cells. A full
round-trip of all 768 raw bytes is a bridge diagnostic using a bridge-only raw
shadow, not a requirement to expose dormant raw cells in ordinary native types.

Before eliminating redundant indices or replacing pointers, a bridge checks:
registered immutable resources; DS/DF and bounds; active prefix/sentinel; descriptor
family and admissible stored phase; accessible journey/animation/script extents;
valid carrier/platform indices at the sites that use them; paired source/destination
number/index cells where live; copied demo period/effect identity. Failed assumptions
must use an explicit L1 fallback or reject the case in that closure's contract.
Do not reinterpret unknown handler words as a valid default, truncate invalid
indices, or let a typed pointer hide a wrap/alias case admitted by the tests.

### Side effects outside the slot

Itinerary exhaustion changes remaining objectives, fade and completion marker
(`14AB..14C7`, AL=FE on the completion path). Appearance/boarding/resurfacing mutate
platform occupancy. Boarding and delivery mutate player attachment, fare/floor,
destination HUD and quick timer; delivery changes score, HUD clear pending and
may spawn a multiplier item and sound. Throw detaches and plays sound. These are
closure interface effects, not fields to add to a generic actor record.

Demo effects are synchronous after the sprite and both position deltas, before
cursor store (`09FF..0A19/0A4E`). `FADE_ON_HIDDEN` applies only to sprite==7FFF and
changes both fade step and current fade (`0989..099A`). `REVEAL_WIDTH` reads X32,
SAR 5, performs wrapping `320-x`, a signed upper clamp to 127 that replaces AL,
and stores the **low byte** through the separate mutable sprite-width reference
(`099F..09BA`). That byte belongs to the sprite resource/presentation adapter,
not to an actor slot. Do not make a whole immutable sprite bank writable to solve
this one exception. Preserve the reveal wrapper's post-return zero-X width reset.

## Complete handler sets and native names

The program model's actor site `G:1492` contains **36** target words: the union of
nineteen transition fields across eight descriptors. This is a complete family
superset under its explicit descriptor/mode/index assumptions, not 36 proven
persistently stored update states. Following the actual store origins and shipped
placement entry gives **21 stored-phase candidates** (including the loader's
transiently stored stone initializer). The table below covers **all 36**, distinguishing
immediate actions from phases. A function which tail-enters an initializer executes
its writes now; it does not defer them by one tick in a native dispatcher.

| G: entry | L0 identity | Proposed native phase or immediate action | Reachability condition |
|---|---|---|---|
| 149C | ReadPassengerJourneyLeg | `ACTOR_READ_JOURNEY` / read journey | land placement or departure tail; exhaustion installs retired |
| 1509 | WaitForPassengerPlatform | `ACTOR_WAIT_FOR_PLATFORM` | valid source/destination leg, initialized scaled wait |
| 153B | PlacePassengerOnPlatform | action place passenger -> `ACTOR_ARRIVING` | source delay expired and platform unoccupied |
| 1582 | AnimatePassengerArrival | `ACTOR_ARRIVING` | placement initialized positions, animation and occupancy |
| 15B4 | BeginPassengerPlatformWait | action begin platform wait -> `ACTOR_PLATFORM_WAIT` | land arrival terminator or question retry |
| 15D7 | UpdatePassengerPlatformWait | `ACTOR_PLATFORM_WAIT` | land descriptor; may pair-switch to water |
| 16F6 | BeginPassengerDestinationDisplay | action begin destination request -> land/water request phase | shared action selects descriptor +16; destination initialized |
| 172A | UpdatePassengerDestinationDisplay | `ACTOR_DESTINATION_REQUEST` | land descriptor and request initialized |
| 17E6 | BeginPassengerQuestionDisplay | action begin question -> land/water question phase | shared action selects descriptor +1A |
| 180A | UpdatePassengerQuestionDisplay | `ACTOR_QUESTION` | land descriptor and request initialized |
| 18C8 | BeginPassengerApproach | action begin approach -> land/water approach phase | shared action selects descriptor +1E |
| 18E6 | UpdatePassengerApproach | `ACTOR_APPROACH` | land descriptor; selected player's platform matches source |
| 19E0 | BoardWaterbornePassenger | action board from water -> `ACTOR_CARRIED_PASSENGER` | water approach selects +20; reads water fare/floor **before** pair-switch |
| 19FB | BoardPassenger | action board -> `ACTOR_CARRIED_PASSENGER` | land approach; DI is selected carrier; attachment fields become initialized |
| 1A42 | UpdateCarriedPassenger | `ACTOR_CARRIED_PASSENGER` | land descriptor after boarding, valid carrier and quick timer |
| 1A7E | DeliverPassenger | action deliver -> `ACTOR_WALK_TO_EXIT` | carrier platform equals destination; incoming selected carrier live |
| 1B29 | WalkPassengerToExit | `ACTOR_WALK_TO_EXIT` | land delivery; itinerary and destination still retained |
| 1BBE | BeginPassengerDeparture | action begin departure -> `ACTOR_DEPARTING` | exit arrival-X reached |
| 1BD6 | AnimatePassengerDeparture | `ACTOR_DEPARTING` | terminator advances journey and immediately reads next leg |
| 1C0E | IgnoreActorState | `ACTOR_RETIRED` / no-op action | exhausted journey, retired stone/water; also unused descriptor fields and demo no-effect callback |
| 1C0F | BeginStonePickupWait | `ACTOR_BEGIN_STONE_WAIT`; action -> `ACTOR_STONE_WAIT` | loader stores primary stone +10; later stone landings tail-enter it immediately |
| 1C27 | UpdateStonePickupWait | `ACTOR_STONE_WAIT` | stone setup completed; overlap and empty craft permit attach |
| 1C48 | AttachStoneToPlayer | action attach stone -> `ACTOR_CARRIED_STONE` | selected empty touching carrier |
| 1C6B | WaitForStoneRelease | `ACTOR_CARRIED_STONE` | initialized carrier; signed action **byte** negative throws |
| 1C81 | ThrowCarriedStone | action throw -> `ACTOR_THROWN_STONE` | carrier live; motion copied from raw craft velocities SAR 5 |
| 1CEE | UpdateThrownStone | `ACTOR_THROWN_STONE` | initialized position/steps; only primary stone recognized by enemy query |
| 1DA8 | BeginPassengerResurfacing | action begin resurfacing -> `ACTOR_RESURFACING` | water pair selected from land update; retains journey source index |
| 1DD5 | UpdatePassengerResurfacing | `ACTOR_RESURFACING` | water type; vertical raw accumulator initialized zero; reads cached Y |
| 1E9C | BeginPassengerSinking | action begin sinking -> `ACTOR_SINKING` | floating lifetime/question expiry; clears overlay and initializes motion |
| 1EC0 | UpdatePassengerSinking | `ACTOR_SINKING` | water type; unsigned lower-screen threshold retires |
| 1F24 | BeginPassengerFloating | action begin floating -> `ACTOR_FLOATING` | resurfacing crossed surface; loads descriptor lifetime |
| 1F43 | UpdatePassengerFloating | `ACTOR_FLOATING` | water type; **77FE skips carrier search** and only times out |
| 1FE2 | UpdateFloatingDestinationDisplay | `ACTOR_FLOATING_DESTINATION_REQUEST` | reachable for 776A/7892 after request action; excluded for 77FE by its floating-search guard under normal entry |
| 2068 | UpdateFloatingQuestionDisplay | `ACTOR_FLOATING_QUESTION` | same water-entry invariant; timeout sinks instead of land retry |
| 20C1 | UpdateFloatingPassengerApproach | `ACTOR_FLOATING_APPROACH` | same water-entry invariant; empty craft at exact water Y-18; no stationary-velocity check here |
| 2195 | IgnoreWaterbornePassengerState | no-op action (no distinct persistent phase) | water descriptor +24/+26 only; normal water boarding first changes to land then selects +22, so these words are unreachable under paired-descriptor/entry invariants |

Besides the 21 stored candidates and unused water no-op 2195, the remaining
fourteen entries are immediate initializer/transition actions, not extra ticking
phases. Isolated bridges for them must
preserve their direct-entry contracts rather than inventing stored-state reachability.
The alternate stone 7926 is in the model's descriptor superset but excluded by
shipped placement and by the primary-only stone hit check. Malformed calls,
corrupted state, nulls from another descriptor family, or a direct entry into a
water action with a land descriptor are outside the proposed normal-state contract.

Demo has a different, complete set at `G:0A15`:

| G: entry | L0 identity | Native effect | Invariant |
|---|---|---|---|
| 0989 | StartDemoFadeWhenSpriteHidden | `DEMO_EFFECT_FADE_ON_HIDDEN` | callback copied from a registered header; fade only on exact 7FFF sprite |
| 099F | SetDemoRevealSpriteWidth | `DEMO_EFFECT_REVEAL_WIDTH` | registered reveal sprite-width byte; callback X32 slot valid |
| 1C0E | IgnoreActorState | `DEMO_EFFECT_NONE` | header's no-effect callback; reuse of the RET entry does not make it gameplay dispatch |

All 28 headers enumerate only these three. `loc_0B4E` is a separate unexplained
RET entry included among the model's 13 demo routines; it is **not** in the callback
set and must not be used as a substitute identity for `IgnoreActorState`.
Demo opcodes are a separate interpreter state machine: nonnegative sprite plus
signed-byte dx/dy times four; negative non-8000 repeat declaration; 8000 repeat or
sticky stop. Its cursor is not a gameplay phase enum. `TestAllDemoScriptsFinished`
terminates on the cursor sentinel and tests completion nonzero, not sprite hidden.

## Closure plan

These are proposed work units and order, not granted statuses. The two mode
closures may proceed independently once the supervisor accepts the shared
projection and renderer history boundary. Keep L1 as the independent reference.

1. **Resource/projection contract.** Review this draft and move only accepted
   types into a supervisor-owned shared header. Extend the existing level adapter
   to resolve actor descriptors, animations, journeys and demo scripts. Preserve
   descriptor identity and the primary-stone distinction. Specify bounded
   immutable-resource, count/sentinel and alias fallback rules. Agree the hazard
   bridge's actor query/rebound access using this view; do not let it privately
   invent another actor struct. Dependencies: geometry, level, contacts and the
   supervisor's hazard work. No change to the current native headers is made here.
2. **Renderer history boundary.** Establish the actor portions of the inline
   gameplay erase/draw/overlay loops and demo draw/erase, plus reset's actor
   contribution. Test both page histories, hidden/clipped transitions and overlay
   swap guards. Preserve cache inputs at pre-update boundaries and explicit
   placement/scene seed writes. The complete `render_hud` component is larger;
   this contract need not wait for all HUD or sprite rendering to close.
3. **Stone lifecycle (six entries).** `1C0F/1C27/1C48/1C6B/1C81/1CEE`: wait,
   pickup, carry, throw, flight/landing/retire as one unit. Dependencies: contact
   predicate, platform geometry, player attachment/action/velocity input, sound
   effect facade, renderer history. Hazard query/rebound is an explicit borrower
   and must see same-frame updates and selected slot ordering. Test wrap,
   signed boundaries, action-byte/high-byte behavior, platform crossing, offscreen
   retirement, primary/alternate identity and cache survival from a demo.
4. **Passenger itinerary/appearance/departure (seven entries plus no-op).**
   `149C/1509/153B/1582/1B29/1BBE/1BD6`, and `1C0E`. Dependencies: typed journey,
   platforms/occupancy, coordinate scaler, renderer history, a named continuation
   to waiting. Retain objective decrement/completion AL=FE and animation sentinel
   lookahead; test exhaustion, occupancy competition and delay zero/wrap. Calls
   into remaining L1 passenger handlers stay in the bridge temporarily.
5. **Passenger waiting/request/approach/attachment/delivery (twelve entries).**
   `15B4/15D7/16F6/172A/17E6/180A/18C8/18E6/19E0/19FB/1A42/1A7E` as one coupled
   unit, including the shared water-boarding entry. Dependencies: prior unit,
   player/platform views, cached geometry, contacts, score/HUD/benefits, item
   spawn and audio interfaces. Test 140-tick request scheduling, cached-X exact
   approach equality, carrier selection, unsigned fare floor, quick counter and
   rescue fare-before-pair order. Item exhaustion remains its existing abnormal
   bridge behavior; no assumption that full pool is impossible is introduced.
6. **Water passenger continuation (nine entries plus no-op).**
   `1DA8/1DD5/1E9C/1EC0/1F24/1F43/1FE2/2068/20C1`, `2195`, shares the preceding
   request/approach initializers and water boarding. Dependencies: water surface,
   cached pixels, journey/occupancy and shared attachment transitions. Test raw
   velocity SAR 6, signed/unsigned thresholds, surface equalities, lifetime
   exactly-zero wrap and second-pair no-rescue invariant. Combine the passenger
   certificates only after their immediate-tail transitions agree end to end.
7. **Demo core (three entries).** `InitializeDemoScripts 0AEB`,
   `AdvanceDemoScripts 09D7`, `TestAllDemoScriptsFinished 09BC` together. Initialization
   immediately executes the interpreter, and completion is a parallel cell, so
   splitting these loses the important boundary. Enumerate built bytecode and
   edge cases (period zero, signed deltas, repeats, stop re-entry); compare L1/L2
   persistent projected state and ordered callback effects. Prove small arithmetic
   helpers exhaustively where feasible; script traversal is only bounded model
   evidence until it runs the actual implementation.
8. **Demo presentation and scene integration (nine real entries, one retained
   unexplained RET).** Close draw/erase with the accepted renderer boundary,
   the two effects, common runner and four wrappers. `loc_0B4E` receives a separate
   trivial contract only if needed, never a fabricated callback role. Dependencies:
   palette/retrace/page operations, water draw, input, music and mutable width-byte
   adapter. Test pre-initialization-step callback ordering, completed versus
   interrupted returns, ignored pre-game return and reveal cleanup. Integrate
   scenarios that interrupt every demo, then enter/retry/finish gameplay while
   keeping all sixteen cache histories. This is the required cross-mode check.

Each implementation work order must name its admitted direct-entry states and
actual memory/effect footprint, register/flag liveness at L1 callers, indirect
targets, retained quirks and fallback behavior. Use C differential cases first;
stronger evidence is per property, not inferred from this static design. Run
closure checks and required host checks only when production integration actually
occurs. A passing scene test cannot replace the missing mode/cell contract.

## What Amiga clarifies, and what it does not

[amiga.md](amiga.md), “Working storage” and “Passengers and stones,” plus its
[curated map](../metadata/amiga-map.json), provide independent meaning evidence:

| Amiga evidence | DOS interpretation supported | Classification / limit |
|---|---|---|
| `t h8:059E4`, 32-byte actor records x5, separate from `h8:05120`, generic objects 34 bytes x26 | journey/state bookkeeping is distinct from position/velocity/presentation machinery; a universal entity record is not required by the game's design | supported common design, different implementation; **do not import the five-slot capacity or offsets** |
| Generic object +04/+06 position, +08/+0A velocity, +14 animation object, +18/+1A origin, +1C active | reinforces geometry/motion/animation roles and supports separating renderer concerns from passenger itinerary control | similar purpose, not a field-for-field mapping of the 24 DOS arrays |
| `h0:059FE/05A1E`, land descriptor `h8:05A86+08..50`; occupancy pointer/zero | itinerary -> unoccupied source -> arrival -> request/approach -> board -> delivery -> departure is a recovered passenger state machine | supported common state design; DOS uses indices/FFFF and scales raw waits by 3/2 |
| `h0:05D20`, `07CDA`, `05D8C` | boarding attachment, decreasing fare/floor and delivery award explain DOS carrier/fare/quick-delivery storage | similar purpose with confirmed differences: Amiga bonus is fare delta<=200, DOS has separate 200-update counter |
| `h0:05F36/05F82`, `0619E` | water descriptors represent resurfacing/floating/rescue phases, not an unrelated entity pool | similar purpose/different motion; Amiga changes to land before loading boarding fare, DOS reads water fare first |
| `h0:063F8/064B2` | stone motion and hostile contact roles are clear | different ownership: Amiga central stone path selects enemy hit; DOS hazards query and mutate selected stone |
| Amiga descriptor stride 126, adjacent land/water pair switching by stride | the paired types are two views of one passenger identity | DOS explicitly follows descriptor +48; no pointer arithmetic based on Amiga stride |

Amiga fixed arrays and the 26 generic objects are not evidence for reducing DOS
capacity or replacing its render scheduling. No exact Amiga motion-header,
bytecode or per-cache correspondence was established in that report; none is
asserted here. Its five **item** slots are also distinct from five actor slots
and do not constrain DOS actors. Confirmed itinerary, fare, physics and rescue
differences remain DOS behavior, not design cleanups.

## Verification and remaining review decisions

Reproduction commands (static analysis only):

```text
python tools/progmodel.py --check
python build/workers/actor-design/model_snapshot.py
python build/workers/actor-design/audit.py
C:\msys64\mingw64\bin\gcc.exe -std=c11 -Wall -Wextra -Werror -pedantic -fsyntax-only -I native -x c build/workers/actor-design/actors.h
```

The first command reports inherited model staleness. The second checks fresh
source/build receipts and creates only worker-local evidence; the third checks
the locked expanded SHA-256 and the enumerated bounds/access/script facts. The
last checks that the header is a valid standalone draft against existing geometry.
Detailed results and limitations are in
[REPORT.md](../build/workers/actor-design/REPORT.md). No source edit was proposed,
so `verify.py`, `asmverify.py`, `cjudge.py`, host builds and shared tooling writes
were not run for this design task.

Supervisor decisions needed: accept or revise the split views and semantic-alias
publication rule; assign the persistent renderer owner and explicit seed-write
interface; agree primary-stone identity access with hazards; choose admitted
bounded resources versus L1 fallbacks per closure. These are review choices,
not blockers to the analysis. Unknown descriptor +3A/+3C and exact Amiga script
correspondence remain unnamed. No positive claim about corruption-safe lifetime
separation or unrestricted typed equivalence is made.

## Access appendix: complete bounded cell reference sets

The following table is generated by the worker's audit from decoded memory
operands, with the biased `G:09CB` completion read attributed to `2A4D`. **G** is
gameplay (including level loader, inline session rendering, contacts and hazard
borrowers); **D** is demo (including scene initialization/draw/erase/effects);
**B** is the shared reset service. R/W list the actual instruction offsets, not
merely routine entry addresses. Shared boarding suffix instructions appear under
both routine owners intentionally. `none` is an empty reference set for that mode.

Completeness is for the named GAME instructions, built data/normal pointer
origins and in-range array accesses; arbitrary far-memory corruption, malformed
indices, or forged bytecode/descriptors can alias anything and are not hidden by
these sets. Source names `ds_2A2D/ds_2ACD/ds_2C6D` in older metadata are the same
physical cells named by roles here. Routine identities plus instruction offsets
make this appendix independently navigable in GAME.ASM.

<!-- Generated by build/workers/actor-design/audit.py. -->
| Cell | Mode / access | Routine and instruction offsets (all G:) |
|---|---|---|
| 29AD `ActorDescriptors` | G R | `AnimatePassengerArrival` 158B; `AnimatePassengerDeparture` 1BDF; `AttachStoneToPlayer` 1C48; `BeginPassengerApproach` 18C8; `BeginPassengerDeparture` 1BBE; `BeginPassengerDestinationDisplay` 16F6; `BeginPassengerFloating` 1F24; `BeginPassengerPlatformWait` 15B4; `BeginPassengerQuestionDisplay` 17E6; `BeginPassengerResurfacing` 1DA8; `BeginPassengerSinking` 1E9C; `BeginStonePickupWait` 1C0F; `BoardPassenger` 19FB; `BoardWaterbornePassenger` 19E0; `DeliverPassenger` 1A7E; `DispatchActorUpdates` 1488; `FindThrownStoneHittingEnemy` 2198; `PlacePassengerOnPlatform` 153B; `ReadPassengerJourneyLeg` 14D0,14FD; `RunGameFromPassword` 0CB8,0DE9,0F56; `ThrowCarriedStone` 1C81; `UpdateCarriedPassenger` 1A76; `UpdateFloatingDestinationDisplay` 1FE2; `UpdateFloatingPassengerApproach` 20C1; `UpdateFloatingQuestionDisplay` 2068; `UpdatePassengerApproach` 18E6; `UpdatePassengerDestinationDisplay` 172A; `UpdatePassengerFloating` 1F43; `UpdatePassengerPlatformWait` 15DB; `UpdatePassengerQuestionDisplay` 180A; `UpdatePassengerResurfacing` 1DD5; `UpdatePassengerSinking` 1EC0; `UpdateStonePickupWait` 1C27; `UpdateThrownStone` 1CEE; `WaitForPassengerPlatform` 1533; `WaitForStoneRelease` 1C79; `WalkPassengerToExit` 1B2D |
| 29AD `ActorDescriptors` | G W | `BoardWaterbornePassenger` 19F5; `LoadCurrentLevelState` 3AB0; `UpdatePassengerApproach` 191B,1935; `UpdatePassengerDestinationDisplay` 175F,1779; `UpdatePassengerPlatformWait` 1610,16C9; `UpdatePassengerQuestionDisplay` 183F,1859 |
| 29AD `ActorDescriptors` | D R | none |
| 29AD `ActorDescriptors` | D W | none |
| 29AD `ActorDescriptors` | B R | none |
| 29AD `ActorDescriptors` | B W | none |
| 29CD `ActorInitialPlatformIndices` | G R | `LoadCurrentLevelState` 3AF4 |
| 29CD `ActorInitialPlatformIndices` | G W | `LoadCurrentLevelState` 3ABF |
| 29CD `ActorInitialPlatformIndices` | D R | none |
| 29CD `ActorInitialPlatformIndices` | D W | none |
| 29CD `ActorInitialPlatformIndices` | B R | none |
| 29CD `ActorInitialPlatformIndices` | B W | none |
| 29ED `ActorJourneyCursors` | G R | `AnimatePassengerDeparture` 1C05; `ReadPassengerJourneyLeg` 149C |
| 29ED `ActorJourneyCursors` | G W | `AnimatePassengerDeparture` 1C05; `LoadCurrentLevelState` 3AC4 |
| 29ED `ActorJourneyCursors` | D R | none |
| 29ED `ActorJourneyCursors` | D W | none |
| 29ED `ActorJourneyCursors` | B R | none |
| 29ED `ActorJourneyCursors` | B W | none |
| 2A0D `ActorUpdateOrScriptCursor` | G R | `DispatchActorUpdates` 1492; `FindThrownStoneHittingEnemy` 21AC |
| 2A0D `ActorUpdateOrScriptCursor` | G W | `AttachStoneToPlayer` 1C4F; `BeginPassengerApproach` 18CF; `BeginPassengerDeparture` 1BC5; `BeginPassengerDestinationDisplay` 16FD; `BeginPassengerFloating` 1F2B; `BeginPassengerPlatformWait` 15BB; `BeginPassengerQuestionDisplay` 17ED; `BeginPassengerResurfacing` 1DAF; `BeginPassengerSinking` 1EA3; `BeginStonePickupWait` 1C16; `BoardPassenger` 1A10; `BoardWaterbornePassenger` 1A10; `DeliverPassenger` 1A85; `LoadCurrentLevelState` 3AE7,3AF0; `PlacePassengerOnPlatform` 1542; `ReadPassengerJourneyLeg` 14D7,1504; `ThrowCarriedStone` 1CD4; `UpdatePassengerSinking` 1F13; `UpdateThrownStone` 1D41 |
| 2A0D `ActorUpdateOrScriptCursor` | D R | `AdvanceDemoScripts` 09D9; `DrawDemoSprites` 0A5A; `EraseDemoSprites` 0AB3; `TestAllDemoScriptsFinished` 09BE |
| 2A0D `ActorUpdateOrScriptCursor` | D W | `AdvanceDemoScripts` 0A4E; `InitializeDemoScripts` 0B2B,0B44 |
| 2A0D `ActorUpdateOrScriptCursor` | B R | none |
| 2A0D `ActorUpdateOrScriptCursor` | B W | none |
| 2A2D `ActorPhaseOrDemoLoopCursor` | G R | `DeliverPassenger` 1A9B; `UpdateCarriedPassenger` 1A42; `UpdateFloatingDestinationDisplay` 205B; `UpdateFloatingQuestionDisplay` 20B4; `UpdatePassengerDestinationDisplay` 17D9; `UpdatePassengerPlatformWait` 168E; `UpdatePassengerQuestionDisplay` 1892; `WaitForStoneRelease` 1C6B |
| 2A2D `ActorPhaseOrDemoLoopCursor` | G W | `AttachStoneToPlayer` 1C60; `BeginPassengerDestinationDisplay` 1723; `BeginPassengerPlatformWait` 15CE; `BeginPassengerQuestionDisplay` 1803; `BoardPassenger` 1A27; `BoardWaterbornePassenger` 1A27; `UpdateFloatingDestinationDisplay` 205B; `UpdateFloatingQuestionDisplay` 20B4; `UpdatePassengerDestinationDisplay` 17D9; `UpdatePassengerPlatformWait` 163B,16B0; `UpdatePassengerQuestionDisplay` 1892 |
| 2A2D `ActorPhaseOrDemoLoopCursor` | D R | `AdvanceDemoScripts` 0A3F |
| 2A2D `ActorPhaseOrDemoLoopCursor` | D W | `AdvanceDemoScripts` 0A27 |
| 2A2D `ActorPhaseOrDemoLoopCursor` | B R | none |
| 2A2D `ActorPhaseOrDemoLoopCursor` | B W | none |
| 2A4D `ActorPlatformOrScriptDone` | G R | `UpdatePassengerApproach` 193C; `UpdatePassengerDestinationDisplay` 1780; `UpdatePassengerPlatformWait` 16D0; `UpdatePassengerQuestionDisplay` 189F |
| 2A4D `ActorPlatformOrScriptDone` | G W | `ReadPassengerJourneyLeg` 14E9 |
| 2A4D `ActorPlatformOrScriptDone` | D R | `TestAllDemoScriptsFinished` 09CB |
| 2A4D `ActorPlatformOrScriptDone` | D W | `AdvanceDemoScripts` 0A48; `InitializeDemoScripts` 0B3B |
| 2A4D `ActorPlatformOrScriptDone` | B R | none |
| 2A4D `ActorPlatformOrScriptDone` | B W | none |
| 2A6D `ActorDestinationPlatforms` | G R | `BeginPassengerDestinationDisplay` 170D; `UpdateCarriedPassenger` 1A69 |
| 2A6D `ActorDestinationPlatforms` | G W | `ReadPassengerJourneyLeg` 14DD |
| 2A6D `ActorDestinationPlatforms` | D R | none |
| 2A6D `ActorDestinationPlatforms` | D W | none |
| 2A6D `ActorDestinationPlatforms` | B R | none |
| 2A6D `ActorDestinationPlatforms` | B W | none |
| 2A8D `ActorSourcePlatformByteIndices` | G R | `BeginPassengerResurfacing` 1DB3; `BoardPassenger` 1A37; `BoardWaterbornePassenger` 1A37; `PlacePassengerOnPlatform` 1546; `UpdatePassengerApproach` 1909; `UpdatePassengerDestinationDisplay` 174D; `UpdatePassengerPlatformWait` 15D7,15FE; `UpdatePassengerQuestionDisplay` 182D,189B; `WaitForPassengerPlatform` 1525 |
| 2A8D `ActorSourcePlatformByteIndices` | G W | `ReadPassengerJourneyLeg` 14EF |
| 2A8D `ActorSourcePlatformByteIndices` | D R | none |
| 2A8D `ActorSourcePlatformByteIndices` | D W | none |
| 2A8D `ActorSourcePlatformByteIndices` | B R | none |
| 2A8D `ActorSourcePlatformByteIndices` | B W | none |
| 2AAD `ActorDestinationPlatformByteIndices` | G R | `BoardPassenger` 1A1B; `BoardWaterbornePassenger` 1A1B; `DeliverPassenger` 1B04; `WalkPassengerToExit` 1B29,1BA2 |
| 2AAD `ActorDestinationPlatformByteIndices` | G W | `ReadPassengerJourneyLeg` 14E3 |
| 2AAD `ActorDestinationPlatformByteIndices` | D R | none |
| 2AAD `ActorDestinationPlatformByteIndices` | D W | none |
| 2AAD `ActorDestinationPlatformByteIndices` | B R | none |
| 2AAD `ActorDestinationPlatformByteIndices` | B W | none |
| 2ACD `ActorMotionWaitOrDemoRepeats` | G R | `ReleaseTreeReward` 2B27; `UpdatePassengerFloating` 1FD5; `UpdateThrownStone` 1CF2; `WaitForPassengerPlatform` 150F |
| 2ACD `ActorMotionWaitOrDemoRepeats` | G W | `BeginPassengerFloating` 1F3E; `ReadPassengerJourneyLeg` 14F9; `ThrowCarriedStone` 1C96; `UpdatePassengerFloating` 1FD5; `WaitForPassengerPlatform` 151C |
| 2ACD `ActorMotionWaitOrDemoRepeats` | D R | `AdvanceDemoScripts` 0A2D |
| 2ACD `ActorMotionWaitOrDemoRepeats` | D W | `AdvanceDemoScripts` 0A23,0A39; `InitializeDemoScripts` 0B37 |
| 2ACD `ActorMotionWaitOrDemoRepeats` | B R | none |
| 2ACD `ActorMotionWaitOrDemoRepeats` | B W | none |
| 2AED `ActorX32` | G R | `FindPlayerTouchingActor` 22AF,22C7; `FindThrownStoneHittingEnemy` 21DE; `ReleaseTreeReward` 2B1F; `RunGameFromPassword` 0E0F; `UpdateFloatingPassengerApproach` 2163,218F; `UpdatePassengerApproach` 19AE,19DA; `UpdatePassengerPlatformWait` 1663,1687; `UpdateThrownStone` 1CF6,1D76; `WalkPassengerToExit` 1B77,1B9B,1BA8 |
| 2AED `ActorX32` | G W | `DeliverPassenger` 1AA3; `LoadCurrentLevelState` 3B04; `PlacePassengerOnPlatform` 1571; `ThrowCarriedStone` 1CBB; `UpdateFloatingPassengerApproach` 2163,218F; `UpdatePassengerApproach` 19AE,19DA; `UpdatePassengerPlatformWait` 1663,1687; `UpdateThrownStone` 1D0A; `WalkPassengerToExit` 1B77,1B9B |
| 2AED `ActorX32` | D R | `AdvanceDemoScripts` 0A08; `DrawDemoSprites` 0A80; `SetDemoRevealSpriteWidth` 09A2 |
| 2AED `ActorX32` | D W | `AdvanceDemoScripts` 0A08; `InitializeDemoScripts` 0B04; `PlaySpriteRevealDemo` 0899 |
| 2AED `ActorX32` | B R | none |
| 2AED `ActorX32` | B W | none |
| 2B0D `ActorY32` | G R | `FindPlayerTouchingActor` 227E,2297; `FindThrownStoneHittingEnemy` 21C2; `ReleaseTreeReward` 2B23; `RunGameFromPassword` 0E1A; `UpdatePassengerResurfacing` 1E6A; `UpdatePassengerSinking` 1F04; `UpdateThrownStone` 1D21,1D28,1D2C |
| 2B0D `ActorY32` | G W | `DeliverPassenger` 1B14; `LoadCurrentLevelState` 3B12; `PlacePassengerOnPlatform` 155E; `ThrowCarriedStone` 1CC7; `UpdateFloatingDestinationDisplay` 1FF8; `UpdateFloatingPassengerApproach` 20D7; `UpdateFloatingQuestionDisplay` 207E; `UpdatePassengerApproach` 1905; `UpdatePassengerDestinationDisplay` 1749; `UpdatePassengerFloating` 1F8B; `UpdatePassengerPlatformWait` 15FA; `UpdatePassengerQuestionDisplay` 1829; `UpdatePassengerResurfacing` 1E6E,1E94; `UpdatePassengerSinking` 1F1F; `UpdateThrownStone` 1D21,1D47,1D9B |
| 2B0D `ActorY32` | D R | `AdvanceDemoScripts` 0A11; `DrawDemoSprites` 0A8B |
| 2B0D `ActorY32` | D W | `AdvanceDemoScripts` 0A11; `InitializeDemoScripts` 0B16 |
| 2B0D `ActorY32` | B R | none |
| 2B0D `ActorY32` | B W | none |
| 2B2D `ActorPixelX` | G R | `RunGameFromPassword` 0DFF,0F78; `UpdateFloatingPassengerApproach` 2124; `UpdatePassengerApproach` 196F; `UpdatePassengerPlatformWait` 162C; `WalkPassengerToExit` 1B46 |
| 2B2D `ActorPixelX` | G W | `PlacePassengerOnPlatform` 156A; `RunGameFromPassword` 0E16 |
| 2B2D `ActorPixelX` | D R | `DrawDemoSprites` 0A70 |
| 2B2D `ActorPixelX` | D W | `DrawDemoSprites` 0A87; `InitializeDemoScripts` 0AF9 |
| 2B2D `ActorPixelX` | B R | none |
| 2B2D `ActorPixelX` | B W | none |
| 2B4D `ActorPreviousDrawX` | G R | `RunGameFromPassword` 0CD6,0CFE |
| 2B4D `ActorPreviousDrawX` | G W | `RunGameFromPassword` 0E07 |
| 2B4D `ActorPreviousDrawX` | D R | `EraseDemoSprites` 0ADA |
| 2B4D `ActorPreviousDrawX` | D W | `DrawDemoSprites` 0A78; `InitializeDemoScripts` 0AFD |
| 2B4D `ActorPreviousDrawX` | B R | none |
| 2B4D `ActorPreviousDrawX` | B W | none |
| 2B6D `ActorPixelY` | G R | `RunGameFromPassword` 0E03,0F7F; `UpdateFloatingDestinationDisplay` 1FE9; `UpdateFloatingPassengerApproach` 20C8; `UpdateFloatingQuestionDisplay` 206F; `UpdatePassengerApproach` 18EF; `UpdatePassengerDestinationDisplay` 1733; `UpdatePassengerFloating` 1F7C; `UpdatePassengerPlatformWait` 15E4; `UpdatePassengerQuestionDisplay` 1813; `UpdatePassengerResurfacing` 1E0B |
| 2B6D `ActorPixelY` | G W | `PlacePassengerOnPlatform` 1557; `RunGameFromPassword` 0E21 |
| 2B6D `ActorPixelY` | D R | `DrawDemoSprites` 0A74 |
| 2B6D `ActorPixelY` | D W | `DrawDemoSprites` 0A92; `InitializeDemoScripts` 0B0B |
| 2B6D `ActorPixelY` | B R | none |
| 2B6D `ActorPixelY` | B W | none |
| 2B8D `ActorPreviousDrawY` | G R | `RunGameFromPassword` 0CDA,0D05 |
| 2B8D `ActorPreviousDrawY` | G W | `RunGameFromPassword` 0E0B |
| 2B8D `ActorPreviousDrawY` | D R | `EraseDemoSprites` 0ADE |
| 2B8D `ActorPreviousDrawY` | D W | `DrawDemoSprites` 0A7C; `InitializeDemoScripts` 0B0F |
| 2B8D `ActorPreviousDrawY` | B R | none |
| 2B8D `ActorPreviousDrawY` | B W | none |
| 2BAD `ActorAnimationByteOffsets` | G R | `AnimatePassengerArrival` 1596,159E; `AnimatePassengerDeparture` 1BEA,1BF2; `UpdateFloatingDestinationDisplay` 2039,2041; `UpdateFloatingPassengerApproach` 211E,2141,216D; `UpdateFloatingQuestionDisplay` 2092,209A; `UpdatePassengerApproach` 1969,198C,19B8; `UpdatePassengerDestinationDisplay` 17B7,17BF; `UpdatePassengerFloating` 1F57,1F5F; `UpdatePassengerPlatformWait` 1627,1649,166D,16A1; `UpdatePassengerQuestionDisplay` 1870,1878; `UpdatePassengerResurfacing` 1DE9,1DF1; `UpdatePassengerSinking` 1ED4,1EDC; `WalkPassengerToExit` 1B41,1B5D,1B81 |
| 2BAD `ActorAnimationByteOffsets` | G W | `AnimatePassengerArrival` 1596; `AnimatePassengerDeparture` 1BEA; `BeginPassengerApproach` 18D3; `BeginPassengerDeparture` 1BC9; `BeginPassengerDestinationDisplay` 1701; `BeginPassengerFloating` 1F2F; `BeginPassengerPlatformWait` 15BF; `BeginPassengerQuestionDisplay` 17F1; `BeginPassengerResurfacing` 1DC2; `BeginPassengerSinking` 1EAD; `BeginStonePickupWait` 1C1A; `DeliverPassenger` 1B18; `PlacePassengerOnPlatform` 1575; `UpdateFloatingDestinationDisplay` 2039,204F; `UpdateFloatingPassengerApproach` 211E,214F,217B; `UpdateFloatingQuestionDisplay` 2092,20A8; `UpdatePassengerApproach` 1969,199A,19C6; `UpdatePassengerDestinationDisplay` 17B7,17CD; `UpdatePassengerFloating` 1F57,1F6D; `UpdatePassengerPlatformWait` 1627,1657,167B,1698; `UpdatePassengerQuestionDisplay` 1870,1886; `UpdatePassengerResurfacing` 1DE9,1DFF; `UpdatePassengerSinking` 1ED4,1EEA; `WalkPassengerToExit` 1B41,1B6B,1B8F |
| 2BAD `ActorAnimationByteOffsets` | D R | none |
| 2BAD `ActorAnimationByteOffsets` | D W | none |
| 2BAD `ActorAnimationByteOffsets` | B R | none |
| 2BAD `ActorAnimationByteOffsets` | B W | none |
| 2BCD `ActorAnimationCountdowns` | G R | `AnimatePassengerArrival` 1582; `AnimatePassengerDeparture` 1BD6; `UpdateFloatingDestinationDisplay` 2029; `UpdateFloatingPassengerApproach` 210E; `UpdateFloatingQuestionDisplay` 2082; `UpdatePassengerApproach` 1959; `UpdatePassengerDestinationDisplay` 17A7; `UpdatePassengerFloating` 1F47; `UpdatePassengerPlatformWait` 1617; `UpdatePassengerQuestionDisplay` 1860; `UpdatePassengerResurfacing` 1DD9; `UpdatePassengerSinking` 1EC4; `WalkPassengerToExit` 1B31 |
| 2BCD `ActorAnimationCountdowns` | G W | `AnimatePassengerArrival` 1582,1592; `AnimatePassengerDeparture` 1BD6,1BE6; `BeginPassengerApproach` 18D9; `BeginPassengerDeparture` 1BCF; `BeginPassengerDestinationDisplay` 1707; `BeginPassengerFloating` 1F35; `BeginPassengerPlatformWait` 15C5; `BeginPassengerQuestionDisplay` 17F7; `BeginPassengerResurfacing` 1DC8; `BeginPassengerSinking` 1EB3; `BeginStonePickupWait` 1C20; `DeliverPassenger` 1B21; `PlacePassengerOnPlatform` 157B; `UpdateFloatingDestinationDisplay` 2029,2035; `UpdateFloatingPassengerApproach` 210E,211A; `UpdateFloatingQuestionDisplay` 2082,208E; `UpdatePassengerApproach` 1959,1965; `UpdatePassengerDestinationDisplay` 17A7,17B3; `UpdatePassengerFloating` 1F47,1F53; `UpdatePassengerPlatformWait` 1617,1623; `UpdatePassengerQuestionDisplay` 1860,186C; `UpdatePassengerResurfacing` 1DD9,1DE5; `UpdatePassengerSinking` 1EC4,1ED0; `WalkPassengerToExit` 1B31,1B3D |
| 2BCD `ActorAnimationCountdowns` | D R | `AdvanceDemoScripts` 09E5 |
| 2BCD `ActorAnimationCountdowns` | D W | `AdvanceDemoScripts` 09E5,09F2; `InitializeDemoScripts` 0B2F |
| 2BCD `ActorAnimationCountdowns` | B R | none |
| 2BCD `ActorAnimationCountdowns` | B W | none |
| 2BED `ActorSpriteIds` | G R | `RunGameFromPassword` 0CC2,0DF3,0F60 |
| 2BED `ActorSpriteIds` | G W | `AnimatePassengerArrival` 15AF; `AnimatePassengerDeparture` 1BF8; `AnimateTriopterusImpactRecovery` 28E4; `AnimateTriopterusRecovery` 2885; `AttachStoneToPlayer` 1C64; `BoardPassenger` 1A2B; `BoardWaterbornePassenger` 1A2B; `LoadCurrentLevelState` 3ACB; `ReadPassengerJourneyLeg` 14CA; `ThrowCarriedStone` 1CCB; `UpdateBirdFlight` 24FA; `UpdateFloatingDestinationDisplay` 2057; `UpdateFloatingPassengerApproach` 2157,2183; `UpdateFloatingQuestionDisplay` 20B0; `UpdateFruitTreeAnimation` 2AFE; `UpdatePassengerApproach` 19A2,19CE; `UpdatePassengerDestinationDisplay` 17D5; `UpdatePassengerFloating` 1F75; `UpdatePassengerPlatformWait` 165F,1683,16AC; `UpdatePassengerQuestionDisplay` 188E; `UpdatePassengerResurfacing` 1E07; `UpdatePassengerSinking` 1EF2,1F17; `UpdateStonePickupWait` 1C41; `UpdateThrownStone` 1D38; `UpdateTriopterusAlert` 26D3; `UpdateTriopterusCharge` 278E; `UpdateTriopterusPatrol` 265D; `WaitForPassengerPlatform` 1509; `WalkPassengerToExit` 1B73,1B97 |
| 2BED `ActorSpriteIds` | D R | `DrawDemoSprites` 0A64; `EraseDemoSprites` 0ABD; `StartDemoFadeWhenSpriteHidden` 0989 |
| 2BED `ActorSpriteIds` | D W | `AdvanceDemoScripts` 09FF |
| 2BED `ActorSpriteIds` | B R | none |
| 2BED `ActorSpriteIds` | B W | `ResetSpriteEraseState` 0B65 |
| 2C0D `ActorEraseSprite` | G R | `RunGameFromPassword` 0CC6 |
| 2C0D `ActorEraseSprite` | G W | `LoadCurrentLevelState` 3ACF; `RunGameFromPassword` 0CCA |
| 2C0D `ActorEraseSprite` | D R | `EraseDemoSprites` 0AC1 |
| 2C0D `ActorEraseSprite` | D W | `EraseDemoSprites` 0AC5 |
| 2C0D `ActorEraseSprite` | B R | none |
| 2C0D `ActorEraseSprite` | B W | `ResetSpriteEraseState` 0B69 |
| 2C2D `ActorOverlayOrScriptCallbacks` | G R | `RunGameFromPassword` 0CEA,0F6C |
| 2C2D `ActorOverlayOrScriptCallbacks` | G W | `BeginPassengerApproach` 18DF; `BeginPassengerDestinationDisplay` 171F; `BeginPassengerPlatformWait` 15D2; `BeginPassengerQuestionDisplay` 17FD; `BeginPassengerResurfacing` 1DBE; `BeginPassengerSinking` 1EA7; `LoadCurrentLevelState` 3AD3; `UpdatePassengerApproach` 1914; `UpdatePassengerDestinationDisplay` 1758; `UpdatePassengerPlatformWait` 1609; `UpdatePassengerQuestionDisplay` 1838 |
| 2C2D `ActorOverlayOrScriptCallbacks` | D R | `AdvanceDemoScripts` 0A15 |
| 2C2D `ActorOverlayOrScriptCallbacks` | D W | `InitializeDemoScripts` 0B24 |
| 2C2D `ActorOverlayOrScriptCallbacks` | B R | none |
| 2C2D `ActorOverlayOrScriptCallbacks` | B W | none |
| 2C4D `ActorEraseOverlaySprite` | G R | `RunGameFromPassword` 0CEE |
| 2C4D `ActorEraseOverlaySprite` | G W | `LoadCurrentLevelState` 3AD7; `RunGameFromPassword` 0CF2 |
| 2C4D `ActorEraseOverlaySprite` | D R | none |
| 2C4D `ActorEraseOverlaySprite` | D W | none |
| 2C4D `ActorEraseOverlaySprite` | B R | none |
| 2C4D `ActorEraseOverlaySprite` | B W | none |
| 2C6D `ActorVerticalOrDemoPeriod` | G R | `AnimateTriopterusImpactRecovery` 28E0; `AnimateTriopterusRecovery` 2881; `FindThrownStoneHittingEnemy` 21B7; `ReleaseTreeReward` 2B2B; `UpdateBirdFlight` 24F6; `UpdateDinoForce` 2A4B; `UpdateFruitTreeAnimation` 2AF2; `UpdatePassengerResurfacing` 1E22,1E72; `UpdatePassengerSinking` 1EF6; `UpdateThrownStone` 1D0E; `UpdateTriopterusAlert` 26CF; `UpdateTriopterusCharge` 278A; `UpdateTriopterusPatrol` 2659 |
| 2C6D `ActorVerticalOrDemoPeriod` | G W | `AnimateTriopterusImpactRecovery` 28E0; `AnimateTriopterusRecovery` 2881; `BeginPassengerResurfacing` 1DCE; `BeginPassengerSinking` 1EB9; `ThrowCarriedStone` 1CA1; `UpdateBirdFlight` 24F6; `UpdateDinoForce` 2A4B; `UpdateFruitTreeAnimation` 2AFA; `UpdatePassengerResurfacing` 1E63; `UpdatePassengerSinking` 1EFD; `UpdateThrownStone` 1D15; `UpdateTriopterusAlert` 26CF; `UpdateTriopterusCharge` 278A; `UpdateTriopterusPatrol` 2659 |
| 2C6D `ActorVerticalOrDemoPeriod` | D R | `AdvanceDemoScripts` 09EE |
| 2C6D `ActorVerticalOrDemoPeriod` | D W | `InitializeDemoScripts` 0B1D |
| 2C6D `ActorVerticalOrDemoPeriod` | B R | none |
| 2C6D `ActorVerticalOrDemoPeriod` | B W | none |
| 2C8D `PassengerQuickDeliveryCountdowns` | G R | `DeliverPassenger` 1AB7; `UpdateCarriedPassenger` 1A58 |
| 2C8D `PassengerQuickDeliveryCountdowns` | G W | `BoardPassenger` 1A31; `BoardWaterbornePassenger` 1A31; `UpdateCarriedPassenger` 1A65 |
| 2C8D `PassengerQuickDeliveryCountdowns` | D R | none |
| 2C8D `PassengerQuickDeliveryCountdowns` | D W | none |
| 2C8D `PassengerQuickDeliveryCountdowns` | B R | none |
| 2C8D `PassengerQuickDeliveryCountdowns` | B W | none |

## Supervisor decision (2026-11-13)

Accepted as the representation for the passenger/stone and demo closures:

- Three native objects: `GameplayActors` (passenger/stone slots), `DemoMotionScene` (demo slots)
  and a persistent `ActorRenderStorage` of sixteen renderer histories that outlives mode switches.
  The finding that justifies the third object (demo pixel caches read by the first gameplay
  update of slot 2 on the first level) is the deciding evidence; neither view may reset it.
- No union and no single universal record, for the reasons given above. A tagged union of the two
  semantic views stays possible later, only after its conversions are proved.
- Condition on the semantic aliases in `PassengerStoneSlot` (several named members for one
  retained cell): the native code may read only the member that the current phase defines, and
  the first closure that adopts the header adds a mechanical check of that rule (a per-phase
  table of valid members, enforced in the bridge's projection in debug and verification builds).
- The header moves from `build/workers/actor-design/actors.h` to `native/actors.h` in the work
  order of the first passenger/stone or demo closure, which names it as introduced shared types.
