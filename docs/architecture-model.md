# Architecture model of Ugh!

Worker archmodel, 2026-11-13. This is a recovered model, not a native API mandate,
a claim about original source spelling, or an equivalence certificate.

## Evidence grades and coordinates

**E — established:** directly exhibited by the exact DOS instructions/data or a
checked structural decoder; the stated local fact does not require an inferred intent.
**S — supported:** several consumers, dataflow, or independent Amiga evidence support
the interpretation, but completeness, ownership, or path invariants remain conditional.
**H — hypothesis:** a proposed interpretation or future boundary requiring further evidence.
Every table row carries a grade, or inherits the explicitly stated grade of its table.
E for a layout never upgrades the meaning of its reserved fields, or proves an entire port.

Addresses are hexadecimal, sizes/counts explicitly decimal where helpful. `G:xxxx`
means GAME frame `013B`, `S:xxxx` SOUND `0664`, `T:xxxx` TIMER `0A32`,
`C:xxxx` original C `0878`, and `D:xxxx` DGROUP `5C09`. Amiga `t hN:offset`
is hunk-relative. All source names here describe the current L0 identity;
addresses remain usable if a supervisor accepts a naming proposal.

The evidence base is [program-model.md](program-model.md),
[program-model.json](../metadata/program-model.json), [data.md](data.md),
[data-source.md](data-source.md), [amiga.md](amiga.md),
[amiga-map.json](../metadata/amiga-map.json), the three exact ASM modules and
[module.c](../src/c/module.c). Program-model reader/writer lists are conservative,
segment-conditional candidates, not complete alias analysis. Its 284 entries and
67 indirect sites supersede the older naming brief's 286-entry census.
No game, emulator, or original application was run for this work.

## Subsystems, state and interfaces

The following starts from **all twenty** program-model components. Membership stays
in that partition; scope changes here concern interpretation and future closure units.
Ownership is S: initializers, indexed aliases, rendering caches and IRQ access prevent
exclusive ownership being inferred just from named writers. Interfaces named below
are observed calls, shared state or synchronous effects; no event queue is established.

| Program component → recovered responsibility | Owned state / shared state | Interfaces and evidence | Grade |
|---|---|---|---|
| audio → common music/sample engine (75 entries) | 42-byte channels, three AdLib voice views, clock/fade/guard, PCM/DMA state in SOUND; shared with original C | GAME music/effect facade; registers TIMER callbacks `S:12E5/1939`; OPL/DSP/PIC/DMA and runtime arithmetic | S; C structs plus SOUND consumers, model audio writer groups |
| contacts (4) → borrowed geometry predicates | no persistent state established; player, actor, enemy, item views | `FindPlayerTouchingActor/Enemy/FallingItem`, `FindThrownStoneHittingEnemy`; DI/SF results | E local ABI, S boundary; `G:2196..2362` |
| demo (13) → motion-script interpreter and scene adapters | actor arrays as a distinct mode view; completion/repeat/cursor state, mutable reveal-sprite width | front end calls scripts, three near callbacks, rendering/audio/input/fade | S; `G:088D..0B4D`, four vectors/28 scripts |
| external_hooks (4) → unresolved broken interface | no service state established | far C/SOUND calls to near RETs at `G:001C..001F` corrupt control continuation | E defect; H intended services |
| falling_items (5) → flight, landed lifetime, collection | 12 slots; benefit writes shared level timer, lives, multiplier | passenger/tree spawn; `G:2B7F/2B96/2BE4/2C97/2CA9`; geometry predicate | S owner, E transitions |
| far_copy (1) → ordered far-byte copy | borrowed buffers; no persistent owner | four original-C callers, DF/count/overlap/wrapping contract | E; `G:0020..0038` |
| front_end (23) → menu, password, high scores, credits | edit buffers, configuration, score-file representation; shared score/game result | demos, game session, input/text/pictures/audio, DOS file I/O | S; `G:0063`, `03CD..0711`, `0776..088C` |
| hazards (31) → hazards and reward sources | five enemy slots, including tree; shared player motion/fade, score and stones | per-descriptor states, contacts, audio, item spawn | S; `G:2363..2B7E`; rename component scope to HazardOrRewardSource, not every symbol |
| ice (5) → resource decompression | borrowed input/output and immutable CS decoding tables | maps/pictures; internal bit helpers and distant match tail | E algorithm boundary under stream/alias contract; `G:4C81..4DDD` |
| input (8) → keyboard matching and joystick controls | scan matcher/state, actions, joystick calibration | IRQ09, BIOS/DOS, ports; menu/session poll | S; `G:450A/4567/45BF/50C6/51EC` |
| level_loader (2) → initial-state producer | current level/map and platform view; initializes every simulation family | ICE, coordinate conversion, descriptor initializers | S; `LoadCurrentLevelState G:3976`, `InitializeLevelDisplay`; initializing an array does not make it permanent loader state |
| numeric (7) → three independent services | decimal buffers/divisors; coordinate scratch; CS random words | formatting, loader, rain, DOS-time seeding | S split: decimal multi-entry group, coordinate scalers, RNG; no common native NumericState justified |
| passenger_stone (37) → gameplay actor view | 16-slot arrays; itineraries, platform occupancy and player attachment | descriptor callbacks, contacts, fare/score/bonus/audio, rendering caches | S; `G:1486..2195` |
| pictures (3) → packed-picture presentation | borrowed decoded pixels/palette | ICE, VGA upload/fade, retrace/input wait | S; `G:0B83/0BB8/4C81` |
| player_physics (2) → craft control and collision response | two player motion/attachment/impact fields; shared timer, fade | input view, planar VGA bit-7 reads, platform geometry | S; `G:0FE8/1095`; tile-only collision is unproved |
| render_hud (19) → draw/erase and HUD projection | per-page position/sprite caches, digit cursor and HUD cached values | sprites/text/numeric, VGA planes/pages/palette; reads all simulation families | S; `G:3D66..43xx`; cache writes belong to rendering even inside the session loop |
| sequencing (6) → lifecycle and ordered frame orchestration | phase encoded in call stack, fade direction and completion/lives/level words | startup, menu, level, simulation, render, input/audio | S; `G:0008/0063/0C07`; no universal enum phase recovered |
| timer (10) → PIT/IRQ callback scheduler | D:7A4C..7B7C plus CS install flag | far callbacks, stack adapters, saved external INT08 vector, IRQ/PIT/PIC/DOS | S boundary; E layout/stride defect; `T:0008..0340` |
| video_dos (20) → VGA and DOS video services | CS page/palette/work pointers, saved video/critical-error state | hardware capability boundary, input/retrace; all drawing clients | S; preserve actual access ordering/latches |
| water_weather (9) → surface and rain with draw coupling | water scalar phase/heights and 193 rain slots | restore/draw services, random source; geometry read by physics/actors | S; `G:2D2F..2DB8/3C04..3D4C` |

**S — boundaries to retain:** common audio ownership crosses the C/ASM language boundary;
actor storage crosses a mutually exclusive gameplay/demo lifetime; render caches cross
simulation-family ownership; timer/audio form a callback cycle even when direct SCCs do
not show it. The two eight-entry SOUND interpreter SCCs should each close with their
wait exits and voice services. **H — future split:** video into palette/page/blit services,
and front end into score persistence/menu. Their present outgoing interfaces still need review.

## Records and tables

### Immutable descriptions and decoded resources

**E layout / S semantic role** unless a row says otherwise. Near pointers below are
DGROUP data offsets or GAME code offsets according to the field, never interchangeable.
ROM-like inputs are still writable DOS memory: the reveal demo really changes sprite width.

| Record / extent | Fields by byte offset and meaning | Readers / writers | Amiga counterpart |
|---|---|---|---|
| Sprite directory: 662 × 4, 5B63:0000 | +0 u16 bank offset, +2 u8 width, +3 u8 height. ID chooses one of four banks at thresholds D9/12A/223. Pixel index = offset+x*height+y; zero transparent | sprite draw `G:425A..4263`, restore `43BC..43C9`; reveal callback changes width of sprite 214 and wrapper restores 127 | ILBM planes and runtime sprite objects; shared art S, exact generic sprite-descriptor field correspondence unresolved |
| Demo header: 28 × 8 followed by variable bytecode | +0/+2 i16 pixel X/Y; +4 u16 update period; +6 near callback; opcode starts +8 | `InitializeDemoScripts G:0AF7..0B28` reads all fields; `AdvanceDemoScripts` consumes copied period/callback. No header writer identified | other Amiga state/script systems exist (`h0:07E14/07FB8`); exact header mapping unresolved |
| Demo instruction | nonnegative u16 sprite + i8 dx + i8 dy (deltas ×4 into X32/Y32); 7FFF hidden; negative word sets repeat count except 8000 repeats/stops | `G:09D7..0A57`; loop start/counter live in actor scratch | exact bytecode correspondence unresolved |
| Passenger journey leg: 4 bytes, terminated by platform FFFF | +0 u16 platform index, +2 u16 raw wait; next leg +4 supplies destination while current +0 supplies source | `G:149C/14E7/14F3`; wait scaled 3/2, departure advances cursor four bytes (`1C05`). No immutable itinerary writer identified | `(u32 platform pointer,u16 wait)` = 6 bytes plus FFFF; same waits, two changed sequences |
| Level: 81 × 26 plus mutable copy D:28E9 | +00 map offset u16; +02/+04/+06 platform/actor/enemy near lists; +08 u8 objective count; +09 reserved; +0A text near; +0C weather u8; +0D/+0F P1 X/Y u16; +11/+13 P2 X/Y; +15 water Y32; +17 i16 increment; +19 reserved byte | `G:3976` copies 26 bytes; loader distributes fields, physics/weather/actor completion read mutable fields. `ReadPassengerJourneyLeg` writes count; reserved-byte semantics unknown | 38 bytes: +0 map; +2/+6/+A u32 lists; +E initial count/+10 mutable count; +12 u32 text; +16 weather/+17 reserved; +18/+1A/+1C/+1E starts; +20 Y/+22 increment/+24 tail |
| Platform input: 16 bytes, negative first word terminates | eight u16: left/right/Y/arrivalX/waitX/spawnX/icon/reserved | loader `G:3A67`; converts Y; runtime occupancy is separately initialized FFFF | 18 bytes; same platform scalars, long occupant field in working record |
| Actor placement: 6 bytes, FFFF descriptor terminates | descriptor, initial platform index, itinerary near pointer; stone 78DC treats third word differently / does not walk itinerary | loader `G:3AA9`, passenger/stone initializers; no source-list writer found | 12-byte placements; 493 ordered placements have matching type/count order |
| Enemy placement: variable, FFFF terminates | descriptor; bird/Triopterus total 8 bytes, Dino 10 (X/Y and skipped words), tree 6 (platform/reward-list). Skipped words retain structural ownership only | `G:3B1B..3BFE`, type-specific initialization | 12 bytes each; 265 placements agree in type/count and checked parameters |
| Animation sequence | u16 sprite IDs, FFFF sentinel; current offset is a byte offset, FFFE seed then +2 | state-specific descriptor selects vector, animation ticks load sprite and wrap/transition at sentinel | Amiga animation objects have script/sprite pointers; algorithms and scheduling reorganized |
| Actor descriptor: 8 × 74 at D:7720+4A*k | +0/+2 anchor offsets, +4/+6 contact extents; +08..2C nineteen code pointers; +2E..38 six animation near pointers; +3A/+3C retained scalar roles unresolved here; +3E animation period; +40 fare initial/+42 floor; +44 floating lifetime; +46 carried kind; +48 paired descriptor | handlers `G:149C..2195`; contact `2276` consumes geometry; boarding reads fares before water→land swap, floats read +44; descriptor fields are inputs | 126 bytes: same four words then nineteen u32 code pointers at +08..50, six u32 animations +54..68; retained +6C..72; +74 interval, +76 fare, +78 floor, +7A floating lifetime, +7C kind. Consumers h0:05AEC/05D24/07CDE/05FAE/05D56 support these tail meanings; pair switch adds/subtracts 126 |
| Enemy descriptor: 4 × 60 at D:7630/766C/76A8/76E4 | +0/+2 anchor, +4/+6 contact; +08..20 thirteen code pointers; +22..38 twelve animation pointers; +3A score. Zero callbacks retained | bird/Triopterus/Dino/tree handlers; contacts; loader; no blanket assertion that every slot is reached | 110 bytes: four words, thirteen u32 callbacks +08..38, twelve u32 animations +3C..68, score word +6C |
| Item descriptor: 11 × 20 at D:7970+14*k | +0 horizontal anchor/extent; +2 height; +4 spawn; +6 flight; +8 landing; +A pickup; +C launch impulse; +E benefit amount; +10 sprite; +12 benefit kind (0 timer,1 lives,otherwise multiplier) | `G:2B34/2B96..2D1B`, item contact `2207`; fields have phase-specific consumers | 30 bytes, with four u32 callbacks replacing four near words; parameter purposes similar, numeric effects differ |
| Tree reward list D:3CB3 | nine near item-descriptor pointers then FFFF; order 0,8,5,7,6,1,4,3,2 by mapped ordinals | tree cursor reads/advances; no list writer established | h8:0C194, same order (E table correspondence) |
| Keyboard matcher: 34 × 6 plus FF | three scan-code/FF bytes, destination offset byte, action-value byte, mutable matcher-state byte | initialize `G:450A`, ISR `4567`; keyboard writes action bytes, joystick polling writes words | hardware input reimplemented; no common matcher-layout claim |
| High-score row: 5 × 21 plus 00 FF | 14 name bytes, six right-aligned score characters, CR | `G:043A/0446/0452/04B3`; disk I/O complements all 107 bytes XOR FF | score persistence equivalence unresolved |
| ADLX container: 42-byte prefix | ADLX+BE32 root length; AHDR+BE32 10; payload LE16 version, channel byte, reserved bytes, ticks/unit at +6; IMAP+BE32 0; TRCK+LE32 duplicate root length; events at +42 | C loader/scanners and SOUND event interpreters; different invalid-channel advancement rules | TFMX mdat/smpl has similar audio purpose, different representation |

### Mutable slot storage and field-level access index

**E — physical shape:** DOS platforms, actors, hazards, items, players and rain use
parallel arrays, not packed slot structs. For a word family, access is `base + 2*slot`.
The following is the full field projection for each family. It preserves spare/stale
fields and phase unions. **S — meanings and access attribution:** comments come from
the curated data layout, checked against consumers; R/W lists are the program model's
named candidates under its segment/invariant assumptions. Initial bulk clears and
unresolved aliases can add writers. Empty sets mean no named candidate, not no reader.
Full site lists are in `program-model.json variables[Name]`; these do not certify exclusive ownership.

#### Player craft: 2 slots, 19 word arrays

| Field base / name | Meaning and reuse (S) | R candidates | W candidates |
|---|---|---|---|

| D:27D0 `PlayerX32` | Two signed position words in 1/32-pixel units, indexed by player byte index 0 or 2. | `DeliverPassenger`, `FindPlayerTouchingActor`, `FindPlayerTouchingEnemy`, `FindPlayerTouchingFallingItem`, `LaunchBirdTowardPlayer`, `MovePlayerWithVgaCollisions`, `ThrowCarriedStone`, `UpdateDinoForce`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge` | `LoadCurrentLevelState`, `MovePlayerWithVgaCollisions` |

| D:27D4 `PlayerY32` | Two signed position words in 1/32-pixel units; carried/impact geometry uses this anchor. | `DeliverPassenger`, `FindPlayerTouchingActor`, `FindPlayerTouchingEnemy`, `FindPlayerTouchingFallingItem`, `LaunchBirdTowardPlayer`, `MovePlayerWithVgaCollisions`, `ThrowCarriedStone`, `UpdateDinoForce`, `UpdateTriopterusCharge` | `LoadCurrentLevelState`, `MovePlayerWithVgaCollisions`, `UpdateTriopterusCharge` |

| D:27D8 `PlayerPixelX` | Two parallel signed word pixel X values, selected by byte index 0 or 2. | `AnimateAndDrawPlayer`, `CachePlayerDrawState`, `MovePlayerWithVgaCollisions`, `UpdateFloatingPassengerApproach`, `UpdatePassengerApproach` | `LoadCurrentLevelState`, `MovePlayerWithVgaCollisions` |

| D:27DC `PlayerYPixels` | Two cached pixel Y words derived by SAR 5; surface pickup requires water Y minus 18. | `AnimateAndDrawPlayer`, `CachePlayerDrawState`, `MovePlayerWithVgaCollisions`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingPassengerApproach`, `UpdatePassengerFloating` | `LoadCurrentLevelState`, `MovePlayerWithVgaCollisions` |

| D:27E0 `PlayerCachedPixelX` | Two prior pixel X values for restoring the previous frame on each draw page. | `RestorePlayerBackground` | `CachePlayerDrawState`, `LoadCurrentLevelState` |

| D:27E4 `PlayerCachedPixelY` | Two prior pixel Y values for restoring the previous frame on each draw page. | `RestorePlayerBackground` | `CachePlayerDrawState`, `LoadCurrentLevelState` |

| D:27E8 `PlayerSpriteIds` | Two current player animation sprite IDs; advanced between per-player cycle boundaries. | `AnimateAndDrawPlayer`, `CachePlayerDrawState` | `AnimateAndDrawPlayer`, `LoadCurrentLevelState` |

| D:27EC `PlayerCachedSpriteIds` | Two previous player sprite IDs used for restoration rectangle dimensions. | `RestorePlayerBackground` | `CachePlayerDrawState` |

| D:27F0 `PlayerAnimationCountdowns` | Two signed countdown words; negative values add 200 and advance the sprite once. | `AnimateAndDrawPlayer` | `AnimateAndDrawPlayer`, `LoadCurrentLevelState` |

| D:27F4 `PlayerThrustAnimationRate` | Two per-player words accumulating thrust's animation contribution during one movement update. Movement adds 3Fh or 5Ah; player drawing caps the rate at 5Ah before advancing its frame timer. | `AnimateAndDrawPlayer`, `MovePlayerWithVgaCollisions` | `MovePlayerWithVgaCollisions` |

| D:27F8 `PlayerPlatformIndices` | Two words: platform index or FFFF for airborne/unattached; not byte indices. | `FindPlayerTouchingActor`, `MovePlayerWithVgaCollisions`, `UpdateCarriedPassenger`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` | `LoadCurrentLevelState`, `MovePlayerWithVgaCollisions`, `UpdateTriopterusCharge` |

| D:27FC `PlayerCarriedKinds` | Two words: zero empty, descriptor +46 for passenger/stone; stone is kind four. | `RefreshHudAndTimerBar`, `UpdateFloatingPassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerFloating`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `UpdateStonePickupWait` | `AttachStoneToPlayer`, `BoardPassenger`, `BoardWaterbornePassenger`, `DeliverPassenger`, `LoadCurrentLevelState`, `ThrowCarriedStone` |

| D:2800 `HudCachedPlayerOneIconState` | Word cached passenger/icon state 27FC; change redraws both first-player icons. | `RefreshHudAndTimerBar` | `LoadCurrentLevelState`, `RefreshHudAndTimerBar` |

| D:2804 `PlayerDestinationIcons` | Two HUD icon indices: destination platform mapping, seven for stone, zero when empty. | `RefreshHudAndTimerBar` | `AttachStoneToPlayer`, `BoardPassenger`, `BoardWaterbornePassenger`, `DeliverPassenger`, `LoadCurrentLevelState`, `ThrowCarriedStone` |

| D:2808 `PlayerPassengerFares` | Two unsigned fare words; decrease toward minimum while passenger is carried. | `DeliverPassenger`, `RefreshHudAndTimerBar`, `UpdateCarriedPassenger` | `BoardPassenger`, `BoardWaterbornePassenger`, `LoadCurrentLevelState`, `UpdateCarriedPassenger` |

| D:280C `PlayerMinimumFares` | Two unsigned fare floors from descriptor +42; compared unsigned by 1A42. | `UpdateCarriedPassenger` | `BoardPassenger`, `BoardWaterbornePassenger` |

| D:2810 `PlayerHorizontalVelocities` | Two signed motion accumulators; player movement divides by 64 using SAR 6. | `MovePlayerWithVgaCollisions`, `ThrowCarriedStone`, `UpdateDinoForce` | `LoadCurrentLevelState`, `MovePlayerWithVgaCollisions`, `UpdateDinoForce`, `UpdateTriopterusCharge` |

| D:2814 `PlayerVerticalVelocities` | Two signed motion accumulators; player movement divides by 64 using SAR 6. | `MovePlayerWithVgaCollisions`, `ThrowCarriedStone`, `UpdatePassengerFloating` | `LoadCurrentLevelState`, `MovePlayerWithVgaCollisions`, `UpdateTriopterusCharge` |

| D:2818 `PlayerImpactMagnitude` | Two per-player impact-magnitude words, reset on each movement call and filled by collisions. Keeps the greater horizontal/vertical reflected magnitude for landing and difficulty-limit tests. | `MovePlayerWithVgaCollisions` | `MovePlayerWithVgaCollisions` |

#### Platforms: 10 slots, 8 word arrays

| Field base / name | Meaning and reuse (S) | R candidates | W candidates |
|---|---|---|---|

| D:290D `PlatformLeftEdges` | Ten signed pixel X bounds; FFFF terminates platform scans through this parallel array. | `AdvanceFallingItem`, `MovePlayerWithVgaCollisions`, `UpdateThrownStone`, `UpdateTriopterusPatrol` | `LoadCurrentLevelState` |

| D:2921 `PlatformRightEdges` | Ten pixel X bounds; stone landing uses inclusive bounds; patrol uses its own strict test. | `AdvanceFallingItem`, `MovePlayerWithVgaCollisions`, `UpdateThrownStone`, `UpdateTriopterusPatrol` | `LoadCurrentLevelState` |

| D:2935 `PlatformHeights` | Ten pixel Y values after aspect conversion; actor feet snap to these on landing. | `AdvanceFallingItem`, `DeliverPassenger`, `LoadCurrentLevelState`, `MovePlayerWithVgaCollisions`, `PlacePassengerOnPlatform`, `UpdateThrownStone` | `LoadCurrentLevelState` |

| D:2949 `PlatformArrivalPointsX` | Ten pixel X anchors used for passenger appearance and post-delivery departure. | `PlacePassengerOnPlatform`, `WalkPassengerToExit` | `LoadCurrentLevelState` |

| D:295D `PlatformWaitingPointsX` | Ten pixel X anchors passengers approach while waiting for a vehicle. | `UpdatePassengerPlatformWait` | `LoadCurrentLevelState` |

| D:2971 `PlatformSpawnX` | Word platform X values used to place actors/enemies after subtracting sprite origin offsets. | `LoadCurrentLevelState` | `LoadCurrentLevelState` |

| D:2985 `PlatformDestinationIcons` | Ten words mapping destination platform to the carried passenger HUD icon index. | `BoardPassenger`, `BoardWaterbornePassenger` | `LoadCurrentLevelState` |

| D:2999 `PlatformActorOccupants` | Ten actor byte indices; FFFF means unclaimed; appearance claims, boarding frees. | `WaitForPassengerPlatform` | `BeginPassengerResurfacing`, `BoardPassenger`, `BoardWaterbornePassenger`, `LoadCurrentLevelState`, `PlacePassengerOnPlatform`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay` |

#### Passenger/stone and demo storage: 16 slots, 24 word arrays

| Field base / name | Meaning and reuse (S) | R candidates | W candidates |
|---|---|---|---|

| D:29AD `ActorDescriptors` | Sixteen near DGROUP descriptor pointers; FFFF terminates the active actor list. | `AnimatePassengerArrival`, `AnimatePassengerDeparture`, `AttachStoneToPlayer`, `BeginPassengerApproach`, `BeginPassengerDeparture`, `BeginPassengerDestinationDisplay`, `BeginPassengerFloating`, `BeginPassengerPlatformWait`, `BeginPassengerQuestionDisplay`, `BeginPassengerResurfacing`, `BeginPassengerSinking`, `BeginStonePickupWait`, `BoardPassenger`, `BoardWaterbornePassenger`, `DeliverPassenger`, `DispatchActorUpdates`, `FindThrownStoneHittingEnemy`, `PlacePassengerOnPlatform`, `ReadPassengerJourneyLeg`, `RunGameFromPassword`, `ThrowCarriedStone`, `UpdateCarriedPassenger`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingPassengerApproach`, `UpdateFloatingQuestionDisplay`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerFloating`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `UpdatePassengerResurfacing`, `UpdatePassengerSinking`, `UpdateStonePickupWait`, `UpdateThrownStone`, `WaitForPassengerPlatform`, `WaitForStoneRelease`, `WalkPassengerToExit` | `BoardWaterbornePassenger`, `LoadCurrentLevelState`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay` |

| D:29CD `ActorInitialPlatformIndices` | Parallel actor word copied from placement; special descriptor 78DCh uses it as platform index. | `LoadCurrentLevelState` | `LoadCurrentLevelState` |

| D:29ED `ActorJourneyCursors` | Sixteen near journey pointers; current leg has source, delay, destination words. | `AnimatePassengerDeparture`, `ReadPassengerJourneyLeg` | `AnimatePassengerDeparture`, `LoadCurrentLevelState` |

| D:2A0D `ActorUpdateOrScriptCursor` | Sixteen near GAME callbacks in gameplay, or near DGROUP cursors in demo scripts. | `AdvanceDemoScripts`, `DispatchActorUpdates`, `DrawDemoSprites`, `EraseDemoSprites`, `FindThrownStoneHittingEnemy`, `TestAllDemoScriptsFinished` | `AdvanceDemoScripts`, `AttachStoneToPlayer`, `BeginPassengerApproach`, `BeginPassengerDeparture`, `BeginPassengerDestinationDisplay`, `BeginPassengerFloating`, `BeginPassengerPlatformWait`, `BeginPassengerQuestionDisplay`, `BeginPassengerResurfacing`, `BeginPassengerSinking`, `BeginStonePickupWait`, `BoardPassenger`, `BoardWaterbornePassenger`, `DeliverPassenger`, `InitializeDemoScripts`, `LoadCurrentLevelState`, `PlacePassengerOnPlatform`, `ReadPassengerJourneyLeg`, `ThrowCarriedStone`, `UpdatePassengerSinking`, `UpdateThrownStone` |

| D:2A2D `ds_2A2D` | Polymorphic actor scratch: wait mode, state timer, carrier byte index, or demo loop cursor. Effects: interpret per active callback/script; no single scalar role is established. | `AdvanceDemoScripts`, `DeliverPassenger`, `UpdateCarriedPassenger`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingQuestionDisplay`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `WaitForStoneRelease` | `AdvanceDemoScripts`, `AttachStoneToPlayer`, `BeginPassengerDestinationDisplay`, `BeginPassengerPlatformWait`, `BeginPassengerQuestionDisplay`, `BoardPassenger`, `BoardWaterbornePassenger`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingQuestionDisplay`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay` |

| D:2A4D `ActorPlatformOrScriptDone` | Sixteen words: current/source platform in gameplay; demo completion flag otherwise. | `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay` | `AdvanceDemoScripts`, `InitializeDemoScripts`, `ReadPassengerJourneyLeg` |

| D:2A6D `ActorDestinationPlatforms` | Sixteen destination platform indices read from journey cursor +4. | `BeginPassengerDestinationDisplay`, `UpdateCarriedPassenger` | `ReadPassengerJourneyLeg` |

| D:2A8D `ActorSourcePlatformByteIndices` | Sixteen source platform indices multiplied by two for parallel-array indexing. | `BeginPassengerResurfacing`, `BoardPassenger`, `BoardWaterbornePassenger`, `PlacePassengerOnPlatform`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `WaitForPassengerPlatform` | `ReadPassengerJourneyLeg` |

| D:2AAD `ActorDestinationPlatformByteIndices` | Sixteen destination indices multiplied by two for parallel-array indexing. | `BoardPassenger`, `BoardWaterbornePassenger`, `DeliverPassenger`, `WalkPassengerToExit` | `ReadPassengerJourneyLeg` |

| D:2ACD `ds_2ACD` | Polymorphic actor scratch: journey delay, thrown X speed, floating lifetime, demo repeat count. Effects: interpret per active callback/script; no single scalar role is established. | `AdvanceDemoScripts`, `ReleaseTreeReward`, `UpdatePassengerFloating`, `UpdateThrownStone`, `WaitForPassengerPlatform` | `AdvanceDemoScripts`, `BeginPassengerFloating`, `InitializeDemoScripts`, `ReadPassengerJourneyLeg`, `ThrowCarriedStone`, `UpdatePassengerFloating`, `WaitForPassengerPlatform` |

| D:2AED `ActorX32` | Sixteen signed positions in 1/32-pixel units; walking adds/subtracts 20h. | `AdvanceDemoScripts`, `DrawDemoSprites`, `FindPlayerTouchingActor`, `FindThrownStoneHittingEnemy`, `ReleaseTreeReward`, `RunGameFromPassword`, `SetDemoRevealSpriteWidth`, `UpdateFloatingPassengerApproach`, `UpdatePassengerApproach`, `UpdatePassengerPlatformWait`, `UpdateThrownStone`, `WalkPassengerToExit` | `AdvanceDemoScripts`, `DeliverPassenger`, `InitializeDemoScripts`, `LoadCurrentLevelState`, `PlacePassengerOnPlatform`, `PlaySpriteRevealDemo`, `ThrowCarriedStone`, `UpdateFloatingPassengerApproach`, `UpdatePassengerApproach`, `UpdatePassengerPlatformWait`, `UpdateThrownStone`, `WalkPassengerToExit` |

| D:2B0D `ActorY32` | Sixteen signed positions in 1/32-pixel units; thrown and waterborne actors update these. | `AdvanceDemoScripts`, `DrawDemoSprites`, `FindPlayerTouchingActor`, `FindThrownStoneHittingEnemy`, `ReleaseTreeReward`, `RunGameFromPassword`, `UpdatePassengerResurfacing`, `UpdatePassengerSinking`, `UpdateThrownStone` | `AdvanceDemoScripts`, `DeliverPassenger`, `InitializeDemoScripts`, `LoadCurrentLevelState`, `PlacePassengerOnPlatform`, `ThrowCarriedStone`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingPassengerApproach`, `UpdateFloatingQuestionDisplay`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerFloating`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `UpdatePassengerResurfacing`, `UpdatePassengerSinking`, `UpdateThrownStone` |

| D:2B2D `ActorPixelX` | Sixteen cached pixel X values; renderer updates these using ActorX32 SAR 5. | `DrawDemoSprites`, `RunGameFromPassword`, `UpdateFloatingPassengerApproach`, `UpdatePassengerApproach`, `UpdatePassengerPlatformWait`, `WalkPassengerToExit` | `DrawDemoSprites`, `InitializeDemoScripts`, `PlacePassengerOnPlatform`, `RunGameFromPassword` |

| D:2B4D `ActorPreviousDrawX` | Sixteen actor/demo previous-draw X words in pixels; rotated from current pixel X before drawing. The erase pass restores the background rectangle at this older position for each buffered page. | `EraseDemoSprites`, `RunGameFromPassword` | `DrawDemoSprites`, `InitializeDemoScripts`, `RunGameFromPassword` |

| D:2B6D `ActorPixelY` | Sixteen cached pixel Y values; water tests may use the preceding render's value. | `DrawDemoSprites`, `RunGameFromPassword`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingPassengerApproach`, `UpdateFloatingQuestionDisplay`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerFloating`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `UpdatePassengerResurfacing` | `DrawDemoSprites`, `InitializeDemoScripts`, `PlacePassengerOnPlatform`, `RunGameFromPassword` |

| D:2B8D `ActorPreviousDrawY` | Sixteen actor/demo previous-draw Y words in pixels; paired with ActorPreviousDrawX for erasing. These are parallel word arrays; demo initialization copies each starting Y here too. | `EraseDemoSprites`, `RunGameFromPassword` | `DrawDemoSprites`, `InitializeDemoScripts`, `RunGameFromPassword` |

| D:2BAD `ActorAnimationByteOffsets` | Sixteen word offsets into sprite vectors; FFFE initialization precedes a +2 step. | `AnimatePassengerArrival`, `AnimatePassengerDeparture`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingPassengerApproach`, `UpdateFloatingQuestionDisplay`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerFloating`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `UpdatePassengerResurfacing`, `UpdatePassengerSinking`, `WalkPassengerToExit` | `AnimatePassengerArrival`, `AnimatePassengerDeparture`, `BeginPassengerApproach`, `BeginPassengerDeparture`, `BeginPassengerDestinationDisplay`, `BeginPassengerFloating`, `BeginPassengerPlatformWait`, `BeginPassengerQuestionDisplay`, `BeginPassengerResurfacing`, `BeginPassengerSinking`, `BeginStonePickupWait`, `DeliverPassenger`, `PlacePassengerOnPlatform`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingPassengerApproach`, `UpdateFloatingQuestionDisplay`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerFloating`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `UpdatePassengerResurfacing`, `UpdatePassengerSinking`, `WalkPassengerToExit` |

| D:2BCD `ActorAnimationCountdowns` | Sixteen word update countdowns; frame advance occurs only when DEC reaches zero. | `AdvanceDemoScripts`, `AnimatePassengerArrival`, `AnimatePassengerDeparture`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingPassengerApproach`, `UpdateFloatingQuestionDisplay`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerFloating`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `UpdatePassengerResurfacing`, `UpdatePassengerSinking`, `WalkPassengerToExit` | `AdvanceDemoScripts`, `AnimatePassengerArrival`, `AnimatePassengerDeparture`, `BeginPassengerApproach`, `BeginPassengerDeparture`, `BeginPassengerDestinationDisplay`, `BeginPassengerFloating`, `BeginPassengerPlatformWait`, `BeginPassengerQuestionDisplay`, `BeginPassengerResurfacing`, `BeginPassengerSinking`, `BeginStonePickupWait`, `DeliverPassenger`, `InitializeDemoScripts`, `PlacePassengerOnPlatform`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingPassengerApproach`, `UpdateFloatingQuestionDisplay`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerFloating`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `UpdatePassengerResurfacing`, `UpdatePassengerSinking`, `WalkPassengerToExit` |

| D:2BED `ActorSpriteIds` | Sixteen current sprites; FFFF is hidden in gameplay, 7FFF is hidden in demo rendering. | `DrawDemoSprites`, `EraseDemoSprites`, `RunGameFromPassword`, `StartDemoFadeWhenSpriteHidden` | `AdvanceDemoScripts`, `AnimatePassengerArrival`, `AnimatePassengerDeparture`, `AnimateTriopterusImpactRecovery`, `AnimateTriopterusRecovery`, `AttachStoneToPlayer`, `BoardPassenger`, `BoardWaterbornePassenger`, `LoadCurrentLevelState`, `ReadPassengerJourneyLeg`, `ResetSpriteEraseState`, `ThrowCarriedStone`, `UpdateBirdFlight`, `UpdateFloatingDestinationDisplay`, `UpdateFloatingPassengerApproach`, `UpdateFloatingQuestionDisplay`, `UpdateFruitTreeAnimation`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerFloating`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay`, `UpdatePassengerResurfacing`, `UpdatePassengerSinking`, `UpdateStonePickupWait`, `UpdateThrownStone`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol`, `WaitForPassengerPlatform`, `WalkPassengerToExit` |

| D:2C0D `ActorEraseSprite` | Sixteen actor/demo sprite IDs used for background erasure; exchanged with current IDs each pass. FFFF skips erasure; demo erasure also skips hidden ID 7FFF. ResetSpriteEraseState writes FFFF. | `EraseDemoSprites`, `RunGameFromPassword` | `EraseDemoSprites`, `LoadCurrentLevelState`, `ResetSpriteEraseState`, `RunGameFromPassword` |

| D:2C2D `ActorOverlayOrScriptCallbacks` | Sixteen overlay sprites in gameplay; near GAME callbacks during demo interpretation. | `AdvanceDemoScripts`, `RunGameFromPassword` | `BeginPassengerApproach`, `BeginPassengerDestinationDisplay`, `BeginPassengerPlatformWait`, `BeginPassengerQuestionDisplay`, `BeginPassengerResurfacing`, `BeginPassengerSinking`, `InitializeDemoScripts`, `LoadCurrentLevelState`, `UpdatePassengerApproach`, `UpdatePassengerDestinationDisplay`, `UpdatePassengerPlatformWait`, `UpdatePassengerQuestionDisplay` |

| D:2C4D `ActorEraseOverlaySprite` | Sixteen actor overlay erase-sprite IDs, rotated from the live overlay field at 2C2D. The game erases these at actor previous X+11 and Y-13 decimal; FFFF suppresses erasure. | `RunGameFromPassword` | `LoadCurrentLevelState`, `RunGameFromPassword` |

| D:2C6D `ds_2C6D` | Polymorphic actor scratch: vertical speed in gameplay but update period in demo scripts. Effects: interpret per active callback/script; no single scalar role is established. | `AdvanceDemoScripts`, `AnimateTriopterusImpactRecovery`, `AnimateTriopterusRecovery`, `FindThrownStoneHittingEnemy`, `ReleaseTreeReward`, `UpdateBirdFlight`, `UpdateDinoForce`, `UpdateFruitTreeAnimation`, `UpdatePassengerResurfacing`, `UpdatePassengerSinking`, `UpdateThrownStone`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` | `AnimateTriopterusImpactRecovery`, `AnimateTriopterusRecovery`, `BeginPassengerResurfacing`, `BeginPassengerSinking`, `InitializeDemoScripts`, `ThrowCarriedStone`, `UpdateBirdFlight`, `UpdateDinoForce`, `UpdateFruitTreeAnimation`, `UpdatePassengerResurfacing`, `UpdatePassengerSinking`, `UpdateThrownStone`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` |

| D:2C8D `PassengerQuickDeliveryCountdowns` | Sixteen words; boarding sets 200, carrying decrements positives, delivery tests nonzero. | `DeliverPassenger`, `UpdateCarriedPassenger` | `BoardPassenger`, `BoardWaterbornePassenger`, `UpdateCarriedPassenger` |

#### Hazards and reward sources: 5 slots, 19 word arrays

| Field base / name | Meaning and reuse (S) | R candidates | W candidates |
|---|---|---|---|

| D:2CAD `EnemyDescriptors` | Five near DGROUP descriptor pointers; FFFF terminates enemy dispatch. | `AdvanceTreeRewardCooldown`, `AnimateTriopterusImpactRecovery`, `AnimateTriopterusRecovery`, `BeginBirdDelay`, `BeginBirdWarning`, `BeginTriopterusPatrol`, `DispatchEnemyStates`, `InitializeDinoAnimation`, `InitializeFruitTreeAnimation`, `LaunchBirdTowardPlayer`, `RunGameFromPassword`, `UpdateBirdFlight`, `UpdateDinoForce`, `UpdateFruitTreeAnimation`, `UpdateStunnedBird`, `UpdateStunnedDino`, `UpdateStunnedTriopterus`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol`, `WaitForBirdFlight`, `WaitForBirdWarning` | `LoadCurrentLevelState` |

| D:2CB7 `EnemyPlatformIndices` | Five platform indices used by the Triopterus and tree placement/state paths. | `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` | `LoadCurrentLevelState` |

| D:2CC1 `EnemyX32` | Five signed positions in 1/32-pixel units; bird flight and Triopterus charge update them. | `FindPlayerTouchingEnemy`, `FindThrownStoneHittingEnemy`, `InitializeFruitTreeAnimation`, `RunGameFromPassword`, `UpdateBirdFlight`, `UpdateDinoForce`, `UpdateStunnedBird`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` | `LaunchBirdTowardPlayer`, `LoadCurrentLevelState`, `UpdateBirdFlight`, `UpdateStunnedBird`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` |

| D:2CCB `EnemyY32` | Five signed positions in 1/32-pixel units; stone collision tests compare against these. | `FindPlayerTouchingEnemy`, `FindThrownStoneHittingEnemy`, `InitializeFruitTreeAnimation`, `RunGameFromPassword`, `UpdateDinoForce`, `UpdateStunnedBird` | `LaunchBirdTowardPlayer`, `LoadCurrentLevelState`, `UpdateStunnedBird` |

| D:2CD5 `EnemyAnimationOrDropLists` | Five near DGROUP pointers: bird animation vector, or tree falling-reward descriptor list. | `AdvanceTreeRewardCooldown`, `ReleaseTreeReward`, `UpdateBirdFlight` | `LaunchBirdTowardPlayer`, `LoadCurrentLevelState`, `ReleaseTreeReward` |

| D:2CDF `EnemyInitialDelays` | Five word delays; bird initialization copies its value into the active state countdown. | `BeginBirdDelay` | `LoadCurrentLevelState` |

| D:2CE9 `EnemyHorizontalSpeeds` | Five signed horizontal increments; patrol/flight reverse signs and charge adds acceleration. | `LaunchBirdTowardPlayer`, `StunBirdAndAwardScore`, `UpdateBirdFlight`, `UpdateStunnedBird`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` | `LaunchBirdTowardPlayer`, `LoadCurrentLevelState`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` |

| D:2CF3 `EnemyStateCallbacks` | Five near GAME callbacks called by 2363 with BX retained as enemy byte index. | `DispatchEnemyStates` | `AdvanceTreeRewardCooldown`, `BeginBirdDelay`, `BeginBirdWarning`, `BeginTriopterusAlert`, `BeginTriopterusCharge`, `BeginTriopterusImpactRecovery`, `BeginTriopterusPatrol`, `BeginTriopterusRecovery`, `InitializeDinoAnimation`, `InitializeFruitTreeAnimation`, `LaunchBirdTowardPlayer`, `LoadCurrentLevelState`, `ReleaseTreeReward`, `StunBirdAndAwardScore`, `StunDinoAndAwardScore`, `StunTriopterusAndAwardScore` |

| D:2CFD `EnemyStateCounters` | Five words reused as delays/stun timers, bird falling acceleration, or charge acceleration. | `AdvanceTreeRewardCooldown`, `UpdateStunnedBird`, `UpdateStunnedDino`, `UpdateStunnedTriopterus`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `WaitForBirdFlight`, `WaitForBirdWarning` | `AdvanceTreeRewardCooldown`, `BeginBirdDelay`, `BeginBirdWarning`, `BeginTriopterusAlert`, `BeginTriopterusCharge`, `ReleaseTreeReward`, `StunBirdAndAwardScore`, `StunDinoAndAwardScore`, `StunTriopterusAndAwardScore`, `UpdateStunnedBird`, `UpdateStunnedDino`, `UpdateStunnedTriopterus`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `WaitForBirdFlight`, `WaitForBirdWarning` |

| D:2D07 `EnemyDrawX` | Five enemy current-draw X words in pixels; game rendering fills them from signed fixed X SAR 5. Previous values rotate into EnemyPreviousDrawX for background restoration. | `RunGameFromPassword` | `InitializeFruitTreeAnimation`, `RunGameFromPassword` |

| D:2D11 `EnemyPreviousDrawX` | Five enemy previous-draw X words in pixels, used by the erasure pass at 0D34. | `RunGameFromPassword` | `RunGameFromPassword` |

| D:2D1B `EnemyDrawY` | Five enemy current-draw Y words in pixels; game rendering fills them from signed fixed Y SAR 5. Previous values rotate into EnemyPreviousDrawY for background restoration. | `RunGameFromPassword` | `InitializeFruitTreeAnimation`, `RunGameFromPassword` |

| D:2D25 `EnemyPreviousDrawY` | Five enemy previous-draw Y words in pixels, paired with EnemyPreviousDrawX for erasure. | `RunGameFromPassword` | `RunGameFromPassword` |

| D:2D2F `EnemyAnimationByteOffsets` | Five word sprite-vector byte offsets; FFFE initialization precedes +2 frame stepping. | `AnimateTriopterusImpactRecovery`, `AnimateTriopterusRecovery`, `UpdateBirdFlight`, `UpdateDinoForce`, `UpdateFruitTreeAnimation`, `UpdateStunnedTriopterus`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` | `AnimateTriopterusImpactRecovery`, `AnimateTriopterusRecovery`, `BeginBirdDelay`, `BeginTriopterusAlert`, `BeginTriopterusCharge`, `BeginTriopterusImpactRecovery`, `BeginTriopterusPatrol`, `BeginTriopterusRecovery`, `InitializeDinoAnimation`, `InitializeFruitTreeAnimation`, `StunTriopterusAndAwardScore`, `UpdateBirdFlight`, `UpdateDinoForce`, `UpdateFruitTreeAnimation`, `UpdateStunnedTriopterus`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` |

| D:2D39 `EnemyAnimationCountdowns` | Five word update countdowns; frame cadence varies by enemy state. | `AnimateTriopterusImpactRecovery`, `AnimateTriopterusRecovery`, `UpdateBirdFlight`, `UpdateDinoForce`, `UpdateFruitTreeAnimation`, `UpdateStunnedTriopterus`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` | `AnimateTriopterusImpactRecovery`, `AnimateTriopterusRecovery`, `BeginBirdDelay`, `BeginTriopterusAlert`, `BeginTriopterusCharge`, `BeginTriopterusImpactRecovery`, `BeginTriopterusPatrol`, `BeginTriopterusRecovery`, `InitializeDinoAnimation`, `InitializeFruitTreeAnimation`, `StunTriopterusAndAwardScore`, `UpdateBirdFlight`, `UpdateDinoForce`, `UpdateFruitTreeAnimation`, `UpdateStunnedTriopterus`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` |

| D:2D43 `EnemySpriteIds` | Five current sprite words; FFFF hides the enemy. | `RunGameFromPassword` | `AnimateTriopterusImpactRecovery`, `AnimateTriopterusRecovery`, `BeginBirdDelay`, `ReleaseTreeReward`, `ResetSpriteEraseState`, `StunBirdAndAwardScore`, `StunDinoAndAwardScore`, `UpdateBirdFlight`, `UpdateDinoForce`, `UpdateFruitTreeAnimation`, `UpdateStunnedTriopterus`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` |

| D:2D4D `EnemyEraseSprite` | Five enemy erase-sprite words, rotated from current sprite IDs at 2D43; FFFF skips erasure. | `RunGameFromPassword` | `ResetSpriteEraseState`, `RunGameFromPassword` |

| D:2D57 `EnemyDirectionOrTargetPlayer` | Five words: bird target player number 0/1, or Triopterus animation offset 0/2. | `AnimateTriopterusImpactRecovery`, `AnimateTriopterusRecovery`, `LaunchBirdTowardPlayer`, `UpdateBirdFlight`, `UpdateStunnedTriopterus`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` | `LaunchBirdTowardPlayer`, `LoadCurrentLevelState`, `UpdateTriopterusAlert`, `UpdateTriopterusCharge`, `UpdateTriopterusPatrol` |

| D:2D61 `EnemyFlightSoundHandles` | Five word C sound-channel handles; bird flight stores one and 25A0 stops it. | `StopBirdFlightSound` | `LaunchBirdTowardPlayer` |

#### Falling items: 12 slots, 12 word arrays

| Field base / name | Meaning and reuse (S) | R candidates | W candidates |
|---|---|---|---|

| D:2D6B `FallingItemDescriptors` | Twelve near descriptor-pointer words, indexed by even slot byte offset 0..16h. Spawn initializes a slot; flight, landing and collection consume its 20-byte descriptor. | `AdvanceFallingItem`, `ExpireOrCollectFallingItem`, `LandFallingItem` | `SpawnFallingItem` |

| D:2D83 `FallingItemCallbacks` | Twelve near GAME callback words for falling-item slots; dispatcher calls active slots. Spawn selects descriptor+6 (flight), landing switches to descriptor+0Ah (pickup). | `DispatchFallingItems` | `LandFallingItem`, `SpawnFallingItem` |

| D:2D9B `FallingItemSprites` | Twelve sprite-ID words: FFFFh disables dispatch/rendering and marks the usual free slot. Allocation accepts any negative word; spawn takes descriptor+10h as the sprite ID. | `DispatchFallingItems`, `RunGameFromPassword`, `SpawnFallingItem` | `AdvanceFallingItem`, `ExpireOrCollectFallingItem`, `ResetSpriteEraseState`, `SpawnFallingItem` |

| D:2DB3 `FallingItemEraseSprite` | Twelve falling-item erase-sprite words, rotated from current IDs at 2D9B; FFFF skips erasure. This DGROUP array is unrelated to the GAME CS jump table at the same numerical offset. | `RunGameFromPassword` | `ResetSpriteEraseState`, `RunGameFromPassword` |

| D:2DCB `FallingItemX` | Twelve signed X-position words in 1/32 pixel units, indexed by even item slot byte offset. Spawn subtracts descriptor[0]<<5; flight adds horizontal step, with signed offscreen limits. | `AdvanceFallingItem`, `FindPlayerTouchingFallingItem`, `RunGameFromPassword` | `AdvanceFallingItem`, `SpawnFallingItem` |

| D:2DE3 `FallingItemY` | Twelve signed Y-position words in 1/32 pixel units, indexed by even item slot byte offset. Spawn subtracts height<<4; flight adds vertical step; landing snaps using height<<5. | `AdvanceFallingItem`, `FindPlayerTouchingFallingItem`, `RunGameFromPassword` | `AdvanceFallingItem`, `SpawnFallingItem` |

| D:2DFB `FallingItemDrawX` | Twelve falling-item current-draw X words in pixels; each draw derives them from fixed X SAR 5. | `RunGameFromPassword` | `RunGameFromPassword` |

| D:2E13 `FallingItemPreviousDrawX` | Twelve falling-item previous-draw X words in pixels, copied before drawing and consumed by erase. | `RunGameFromPassword` | `RunGameFromPassword` |

| D:2E2B `FallingItemDrawY` | Twelve falling-item current-draw Y words in pixels; each draw derives them from fixed Y SAR 5. | `RunGameFromPassword` | `RunGameFromPassword` |

| D:2E43 `FallingItemPreviousDrawY` | Twelve falling-item previous-draw Y words in pixels, paired with FallingItemPreviousDrawX. | `RunGameFromPassword` | `RunGameFromPassword` |

| D:2E5B `FallingItemMotionOrLifetime` | Twelve state-dependent words: horizontal step during flight, countdown after landing. Spawn stores CX; landing replaces it with 0230h; pickup predecrements to equality zero. | `AdvanceFallingItem`, `ExpireOrCollectFallingItem` | `ExpireOrCollectFallingItem`, `LandFallingItem`, `SpawnFallingItem` |

| D:2E73 `FallingItemVerticalStep` | Twelve vertical-step words, in 1/32 pixel units per update, positive downward. Spawn writes -(launch term+descriptor[0Ch]); flight adds gravity 3 with word wrapping. | `AdvanceFallingItem` | `AdvanceFallingItem`, `SpawnFallingItem` |

#### Rain: 193 slots, 3 word arrays

| Field base / name | Meaning and reuse (S) | R candidates | W candidates |
|---|---|---|---|

| D:2E8B `RainParticleOffsets` | 193 current VGA byte offsets; level initialization clears all and optionally seeds them. | `AdvanceRainParticles`, `DrawRainParticles` | `AdvanceRainParticles`, `LoadCurrentLevelState`, `RespawnRainParticle` |

| D:300D `RainPreviousOffsets` | 193 previous VGA byte offsets retained before particle motion and used by restoration. | `RestoreRainBackground` | `AdvanceRainParticles`, `LoadCurrentLevelState` |

| D:318F `RainParticleXModuloFour` | 193 word plane indices (X modulo four), stored separately from particle byte offsets. | `AdvanceRainParticles`, `DrawRainParticles` | `AdvanceRainParticles`, `RespawnRainParticle` |

**E — lifetime aliases:** `D:2A0D` is GAME code in gameplay and DGROUP bytecode
in demos; `D:2C2D` is gameplay overlay sprite versus demo callback. `D:2A2D`
is wait-mode/state countdown/carrier byte index versus demo loop cursor;
`D:2ACD` is journey delay/thrown horizontal step/floating lifetime versus demo repeat count;
`D:2C6D` is vertical motion versus demo period. Item `D:2E5B` changes horizontal
step to lifetime at landing. Do not make one typed function pointer or one velocity
field stand for all these phases. Demo completion's biased base D:2A4B is an alias,
not another allocation. `PlayerTwo...` labels are interior second-element views.

**S — native projection:** one actor storage owner with mutually exclusive PassengerStone
and DemoMotion views; independent render-cache views. HazardOrRewardSource includes the tree.
For items a flight/landed phase view is justified, but fields left stale on retirement
remain part of the contract until observer/alias evidence permits their removal.

**E/S — Amiga working counterparts:** platform h8:0506A is 18×10, generic object
h8:05120 is 34×26, craft h8:0598E is 28×2, actors h8:059E4 are 32×5,
enemies h8:05E76 are 26×5, items h8:060B2 are 18×5; FFFF endpoints are
checked by `tools/amiga.py`. Generic object known fields: +04/+06 X32/Y32,
+08/+0A direct velocities, +10/+12 targets, +14 animation-object u32 pointer,
+18/+1A sprite-origin words, +1C active flag. Other generic fields remain unresolved here.
Sizes/counts alone do not justify
a field-by-field pairing to DOS scratch arrays. Amiga descriptors and object links
distribute state differently; native code need not impose either physical layout.

**S — additional Amiga field projections from the retained static listing:** the
following extends the size-only working-table map. Pointers are 32-bit, words 16-bit;
candidate-flow annotations in `build/amiga/t.lst` remain a limitation. No DOS byte
claim or unrestricted Amiga reachability proof follows from these observations.

| Amiga record | Known offsets, phase aliases and access evidence | DOS relationship |
|---|---|---|
| Actor 32 bytes | +00 generic-object pointer, +04 descriptor, +08 source platform/water attachment, +0C destination platform, +10 itinerary pointer (loader h0:06F08..06F2A); +14 countdown, +16 descriptor callback offset (05A1E/05A50); +18 waiting-position-reached byte in a cleared word (05AFE/05B4C/05B5E); +1A carried fare (05D24/05D9E); +1C selected carrier pointer (05A0E/05B40). Waiting claims platform +0E with actor pointer, boarding clears it (05A92/05D2E) | DOS distributes these roles among arrays and player fares; stored **offset into descriptor** becomes an installed near GAME handler. Thus one-to-one state-word copying is unjustified |
| Enemy 26 bytes | +00 generic-object pointer, +04 chosen craft pointer (065B8/0663E); +08 descriptor; +0C placement union (platform pointer or X/Y words); +10 countdown; +12 descriptor callback offset; +14 direction flag byte in cleared word; +16 initial-delay word and +18 speed/force word. Loader 06F56..06F74, dispatch 065C8, bird 065E2/066A2, Triopterus 06742/067C0, Dino 06A6A | Same descriptor/phase pattern with direct object links; DOS callback word holds code address, not descriptor-relative state value |
| Item 18 bytes | +00 generic-object pointer, +04 descriptor, +08 landed platform pointer (06C4C); +0C active byte (06B9E/07144/0718E), +0D reserved; +0E descriptor callback offset (06BB4/07174); +10 landed lifetime, initialized 400 at 06C74. Spawn 07124..0718C writes generic position/velocity and descriptor origin, then state +4; 06C66 selects +0C landing, 06C7A selects +10 collection | DOS retains twelve records rather than five and aliases lifetime with X step; Amiga has a separate item lifetime word. Amiga decrements after collection/zero tests while DOS predecrements, so lifetimes are not just scaled constants |
| Craft 28 bytes, partial | +00 generic object, +04 carried actor (05D36); +08 platform/water attachment (0544A); +10/+11 current/previous submersion-duration bytes (053F2/05410/0542E), +12 alternate-path flag (053B0); +18 control/state pointer loaded at 053EA. Other bytes require further consumer tracing | DOS has no proven interleaved craft record and uses cached pixel water tests; only logical roles map |

This adds concrete structural evidence for a shared descriptor-dispatch design while
also exposing a representation change: Amiga stores a descriptor-relative state index,
DOS stores handler addresses. Native enums with direct transitions are **H** until the
per-type allowed state sets and immediate-versus-next-update scheduling are closed.

#### Water, rain and timer records

| Storage | Layout and meanings | Readers / writers | Grade / Amiga |
|---|---|---|---|
| Water | mutable level +15 WaterY32 and +17 increment; D:2903 pixel Y, 2905 previous pixel Y, 2907 byte offset; phase flag elsewhere in HUD state | loader initializes; `AdvanceWaterSurface G:2D2F` toggles phase, increments every other call, clamps negative to zero, transforms/caps pixel Y; restore/draw use caches; craft/actors read surface | E local dataflow; Amiga h8:059C8 separate water object/state, `h0:079BC` increments every call and only stores positive results |
| Rain | current/previous VGA byte address and X mod 4, three arrays ×193 | `InitializeRainParticles/RespawnRainParticle/AdvanceRainParticles` write motion; `RestoreRainBackground` uses previous offsets, `DrawRainParticles` reads current offset/plane. Water pixel height determines inclusive active range | E arrays, S lifecycle; exact Amiga rain layout not established |
| Timer slot table | D:7A4C last slot **byte offset**; 16 words each at 7A4E period lo, 7A6E hi, 7A8E countdown lo, 7AAE hi, 7ACE due, 7AEE slot-offset-by-handle, 7B0E handle-by-slot; far pointers at 7B2E with 4-byte stride | install seeds slot zero/maps; register writes slot/handle/pointer/period; ISR subtracts quantum, reloads countdown and marks due, then clears flag before callback; remove moves last slot; setter updates period/countdown | E; `T:0008/00D2/01AA/021B/02C1`; no proven Amiga scheduler counterpart |
| Timer globals | 7B6E u32 next quantum, 7B72 saved INT08 far vector, 7B76 u32 earliest interval, 7B7A PIT divisor; CS install flag | install/restore/ISR/register/remove/setter share these | E; word divisor zero encodes 65536 PIT clocks; slot zero interval 00010000 |

**E — timer exception:** normal callback dispatch doubles the word-slot index for
4-byte pointers, but removal copies callback words at undoubled offsets (`T:025C..0268`).
Do not replace it with ordinary correct struct compaction. Pointers can become mixed pairs;
public register/stack APIs accept caller-supplied far pointers. **S — ownership contract
still needed:** handle bounds, capacity, invalid handles, reentrancy/CLI/POPF and callback
mutation of the table; do not close this as a pure sixteen-element container yet.

#### Audio records and overlapping views

**E:** `struct s_0014` in original C is exactly 42 bytes, base SOUND:0014,
stride 2A. Slots 0..7 are samples, 8..11 effects, record 12 overlays main-track
globals at SOUND:020C. SOUND uses both record-relative and absolute CS views.
Several C APIs accept 12, others require `<12`; preserve those inequalities.

| Relative field | Meaning / phase | Readers and writers (representative, not exclusive) | Grade |
|---|---|---|---|
| +00 u32 | age/order value used in oldest-channel selection | C:PlayAdlibEffect reads; complete producer semantics unresolved | E layout / S selection role |
| +04 u16 | repeat count, ignored decrement when flags bit 1 set | C sample/track setup; SOUND sample mixer and 77 end handlers | E |
| +06 far pointer | original sample/event stream | C loaders write; mixer/repeat/end/scanners read | E |
| +0A u16 | byte/event-stream length | C sample/ADLX loaders write, mixer/parser reads; main alias MusicEventStreamLength | E |
| +0C u16 | sample playback mode | sample loader writes 2/3, mixer consumes | E |
| +0E u16 | sample rate | sample loader writes; rate/step initialization consumes | E |
| +10 four bytes | PCM pair cursor low word in mixer view; far event cursor in ADLX view | C loader/start/reset; SOUND mixer versus event wait handlers | E union; not one universal pointer |
| +14 u16 | half-length for sample pairs | C sample loader writes length>>1; sample mixing uses | S |
| +16 u16 | retained field, purpose unresolved here | retain raw identity; no semantic rename | E layout only |
| +18 u16 | sample mode low-bit selector | C writes mode&1; sample mixer reads | S |
| +1A u16 | sample decoding accumulator/initial value 127 or 0 | C mode setup; SOUND mixing | S; complete compression semantics unverified without sample asset |
| +1C u16 | volume | C setter/start and SOUND volume/mixer paths | E |
| +1E u32 | next ADLX event deadline | C start sets clock+3; SOUND waits advance/check deadline; main aliases at 022A/022C | E |
| +22 u16 | ADLX voice count | C loader/start/reserve/restore, SOUND event selection | E |
| +24 u16 | first physical AdLib voice | C allocation/restore and SOUND effect interpreter | E |
| +26 u16 | sample step Q8 (ADLX initialized 0100) | C loaders write, SOUND mixer computes low16((pairCursor*step)>>8) | E |
| +28 u16 | flags: bit0 active, bit1 repeat, bit2 ADLX | C lifecycle/allocator and SOUND 77/mixer | E |

**E — AdLib voice records:** original `struct s_0278`, stride 20, three arrays at
SOUND:0278/032C/03E0 (live/saved/scanned), each nine records. +00 twelve instrument
working bytes (event payload advances only eleven), +0C track/effect volume,
+0E channel volume from opcode 3n (C:ScanMusicEvents case 30h),
+10 owner/effect slot (12 main), +12 frequency/block/key-on word. Original-C voice
allocation/restoration and scan/application paths read/write these; SOUND operator/frequency/
volume functions consume them. This is common audio state, not an independent C module API.

**E — shared clock state:** SOUND:0238 ticks/unit, 023A u32 clock, 023E u32 origin,
0242 scanned ticks and 0246..024C fade parameters; guard at 0236. Track elapsed time
subtracts origin then divides by ticks/unit, with original runtime arithmetic and zero-divisor
fault possibility. PIT periods may change, so these values are not interchangeable with
video frames or seconds. **S:** Amiga TFMX voice/sample records have a similar service role;
no field-level audio-layout or event equivalence has been established.

## State machines and dispatch

**E local transitions / S reachable-machine interpretation:** an active descriptor and
initialized mode/slot are preconditions. Numeric states below are descriptor field offsets,
not a new stored enum. Many transitions tail-jump immediately to an initializer, which
installs the update handler. A type family superset includes unused/zero fields; it is
not proof that all such callbacks occur along shipped play traces.

### Passengers, stones and waterborne passengers

| State / handler pair | Trigger and next state | Evidence |
|---|---|---|
| Journey `ReadPassengerJourneyLeg` (+08) → `WaitForPassengerPlatform` (+0A) | destination at cursor+4; raw source wait scaled 3/2; no destination hides actor and selects +2C | G:149C..1508 |
| Source wait → arrival `PlacePassengerOnPlatform` (+0C), `AnimatePassengerArrival` (+0E) | delay zero AND source occupant FFFF; claims platform with actor byte index; finite animation ends at +10 | G:1509..15B3 |
| `BeginPassengerPlatformWait` (+10), `UpdatePassengerPlatformWait` (+12) | walk to waiting X; empty craft on source prompts +14; water contact changes to paired descriptor then +08 | G:15B4..16F5 |
| Destination bubble (+14 begin, +16 update) | 140-update counter; missing/occupied craft selects +18; timeout selects +1C | G:16F6..17E5 |
| Question bubble (+18 begin, +1A update) | 140 updates; timeout retries +14 when eligible craft exists, else +10; water can swap descriptor | G:17E6..18C7 |
| Approach (+1C begin, +1E update) | one pixel per animation tick; X equals craft pixel X+16 → +20; lost platform → +18 | G:18C8..19DF |
| Board (+20) → carried (+22) | free platform, hide sprite, attach carrier DI, load initial/floor fare, quick counter 200; water boarding loads water fare BEFORE pair switch | G:19E0..1A41 |
| Carried → delivery (+24) | fare decrements unsigned toward floor; quick counter decrements while positive; owner platform equals destination | G:1A42..1A7D |
| Delivery → walk exit (+26) | award fare×multiplier; quick nonzero and multiplier below cap spawns multiplier item; clear carrier; walk to arrival X | G:1A7E..1BBD |
| Departure (+28 begin, +2A animate) | animation terminator advances itinerary by four and jumps +08; exhausted +2C is no-op | G:1BBE..1C0E |
| Water resurfacing (+08 begin,+0A update) | acceleration/clamp and upward surface crossing → floating +10; source occupancy freed | G:1DA8..1E9B |
| Water sinking (+0C begin,+0E update) | gravity 27h; unsigned Y32>=1800 hides and installs +2C for next update | G:1E9C..1F23 |
| Floating (+10 begin,+12 update) | load lifetime +44, track surface; eligible empty stationary surface craft → +14; lifetime exactly zero → +0C. Descriptor 77FE skips craft search | G:1F24..1FE1 |
| Floating bubble/question/approach | shared begin handlers but distinct +16/+1A/+1E update handlers; destination scan can see occupied craft, question timeout sinks, approach requires empty craft and exact surface Y-18; equality X → water board +20 | G:1FE2..2195 |
| Stone wait (+10 begin,+12 update) | sprite 0220, overlap with empty craft → attach +20 and wait-release +22 | G:1C0F..1C6A |
| Stone carried → throw (+24) | signed action BYTE negative; detach; sprite 0221; copy craft raw velocities SAR5; install thrown +26 | G:1C6B..1CED |
| Stone thrown → stone wait / retired | horizontal step, vy+=2, crossed platform snaps and jumps +10; signed offscreen limits hide/disable; hazards independently query descending thrown stones | G:1CEE..1DA7; 2196; descriptor 78DC |

**E — completion marker detail:** when objective DEC reaches zero, G:14BD loads AX=FFFE
for the fade, and G:14C7 stores **AL=FE** into LevelCompletionMarker. It is not a stored
Boolean zero from the preceding objective count. G:0FB1 tests its sign to select level advance.

### Hazards and tree

| Family / states | Transitions and triggering conditions | Evidence / grade |
|---|---|---|
| Bird D:7630: delay init/update (+08/+0A), warning init/update (+0C/+0E), launch/flight (+10/+12), hit/fall (+1C/+1E) | delay exactly zero → warning; warning **70 updates (46h)** → launch; alternate target craft and clip launch Y to water/FF80; fly horizontally; offscreen stops saved sound and restarts; animation expiry every four updates gates hit/contact checks; stone hit adds 2500, chooses falling frame, acceleration rises to 40 until offscreen | E G:2379..25B0, descriptor words; no 350-tick bird stun in DOS |
| Triopterus D:766C: patrol (+08/+0A), alert (+0C/+0E), charge (+10/+12), recovery (+14/+16), impact setup/nominal alternate (+18/+1A), hit/stun (+1C/+1E) | patrol platform endpoints, reverse speed/sign and direction; same-platform craft starts alert **140 updates (8Ch)**; target lost returns patrol; countdown zero starts charge; acceleration accumulates direction-1; contact transfers velocities/kicks craft upward, clears platform; target loss selects recovery; stone adds 1400 and 350-update stun; stun expiry returns patrol | E G:25B1..295A; impact initializer installs +16, so ordinary recovery runs instead of descriptor +1A alternate |
| Dino D:76A8: initialize (+10), force update (+12), hit/stun (+1C/+1E) | 15-update animation cadence, frame offset 6 plays sound; animation phase chooses +/-41 added to craft raw vx inside origin-adjusted rectangle; stone adds 800 and 350-update stun; exactly-zero expiry selects +10 | E G:295B..2A86, shared asset/type identity independently established by Amiga |
| Tree D:76E4: init/animate (+08/+0A), release/cooldown (+1C/+1E), exhausted (+20) | six-update animation; descending stone contact reverses/halves stone vy then releases reward at stone position, transforms its velocity, advances finite list, plays sound, sets 210 updates; cooldown zero chooses +0A or +20 if next pointer FFFF; exhausted returns immediately | E G:2A87..2B7E; init left-shifts fixed coordinates into cached draw fields, retained original quirk |

**E — correction to inherited summary:** [amiga.md](amiga.md) says DOS warning/alert
delays are 150 and describes a DOS bird stun of 350. Direct DOS source gives bird 46h=70,
Triopterus alert 8Ch=140, and bird falling acceleration rather than a 350 countdown.
350 applies to Triopterus/Dino. Use the DOS instructions/descriptor consumers for these
durations; no docs outside this work order were edited.

### Falling items and craft

| State | Transition | Evidence / grade |
|---|---|---|
| Item free (ordinary marker sprite FFFF; allocator accepts ANY negative sprite) | highest free slot initialized by descriptor +4 spawn; +6 flight callback and sprite +10 installed | E G:2B96; full pool consumes saved BX as RET IP and is not an ordinary failure result |
| Item flight `AdvanceFallingItem` | vy+=3, integrate words; offscreen retires sprite only; descending platform crossing with inclusive X geometry jumps +8 | E G:2BE4..2C96 |
| Item landing `LandFallingItem` | +A collection handler; horizontal step overwritten by lifetime 560 | E G:2C97..2CA8 |
| Item landed `ExpireOrCollectFallingItem` | predecrement to exactly zero retires before collection; otherwise SF-clear player contact awards timer/lives/multiplier then retires | E G:2CA9..2D1B; wrapping ADD before cap, byte writes to lives/multiplier |
| Craft attached / airborne / submerged | platform index FFFF separates unattached; input/water/gravity change velocity and detach; surface/platform/terrain tests reflect or attach; accepted landings zero motion, severe impact starts shared fade | S semantic states; E local rules G:1095..13FC. No stored craft state handler or descriptor enum established |
| Craft crash/level-exit presentation | impact>=difficulty limit, timer exhaustion, hostile contact or Escape can set negative fade; session continues selected updates while fading until level fade<0 | S flow; G:0C7D..0FA4, 1095, 2493; no separate proven native death animation machine |

### Game flow and update ordering

**E:** RunDosGame initializes DOS hardware/resources, shows logos, enters
RunMainMenuAndAttractLoop. Idle retraces lead through credits/attract/reveal scenes;
F1 starts, F2 password, F3 difficulty, F4 player count, F5 controls; Q returns to cleanup.
RunGameFromPassword selects start level, runs pre-game demo (ignoring its return), resets
score/lives/multiplier, initializes display/level and starts music. On each iteration:

1. Palette fade step or retrace wait; HUD/timer refresh.
2. Erase players, actors/overlays, hazards and items from cached old rectangles; restore rain.
3. Advance water; poll controls/pause/Escape; update eligible craft.
4. Actor callbacks, then hazard callbacks, then falling-item callbacks.
5. Draw actors; stationary Dino/tree; craft; mobile bird/Triopterus; falling items;
   actor overlays; rain advance/draw; water draw; swap page.

Evidence: `G:0C7D..0FA4`. **S:** the draw split expresses layering, not separate simulation
ownership. Geometry predicates often consume cached prior-render positions; running a fresh
pixel projection before all updates can change behavior. The pause path waits through raw
make/break scan transitions. Player loops include equality-after-adding-two quirks; they are
not conventional `< playerCount` loops.

**E:** fade<0 stops music. Negative completion marker increments level and checks mode's
level count; otherwise lives decrement, nonpositive ends session, surviving retries reset
multiplier and initialize the same level. Session return leads to completion demo when all
levels are done, score insertion/name entry when applicable, and menu. Game-over is this
life/session branch, not a proven separate callback state (`G:0FA7..0FE7`, menu G:0063).
Demo itself initializes slots then loops erase/step/draw/swap/fade/input; completion and
interrupts set DemoExitCode with SF/ZF return, not a promised AX result (`G:08D5..0988`).

### Complete stored-handler sets from the program model

**E table contents / S closure under invariants:** these are the model's complete
target-word sets under mode, descriptor, initialization and index assumptions. They are
conservative family supersets, not path-sensitive reachability proofs. Names were resolved
against the model's routine addresses; null/non-entry words are deliberately retained.

#### Actor update (36), site 013B:1492

`013B:149C` GAME:ReadPassengerJourneyLeg, `013B:1509` GAME:WaitForPassengerPlatform, `013B:153B` GAME:PlacePassengerOnPlatform, `013B:1582` GAME:AnimatePassengerArrival, `013B:15B4` GAME:BeginPassengerPlatformWait, `013B:15D7` GAME:UpdatePassengerPlatformWait, `013B:16F6` GAME:BeginPassengerDestinationDisplay, `013B:172A` GAME:UpdatePassengerDestinationDisplay, `013B:17E6` GAME:BeginPassengerQuestionDisplay, `013B:180A` GAME:UpdatePassengerQuestionDisplay, `013B:18C8` GAME:BeginPassengerApproach, `013B:18E6` GAME:UpdatePassengerApproach, `013B:19E0` GAME:BoardWaterbornePassenger, `013B:19FB` GAME:BoardPassenger, `013B:1A42` GAME:UpdateCarriedPassenger, `013B:1A7E` GAME:DeliverPassenger, `013B:1B29` GAME:WalkPassengerToExit, `013B:1BBE` GAME:BeginPassengerDeparture, `013B:1BD6` GAME:AnimatePassengerDeparture, `013B:1C0E` GAME:IgnoreActorState, `013B:1C0F` GAME:BeginStonePickupWait, `013B:1C27` GAME:UpdateStonePickupWait, `013B:1C48` GAME:AttachStoneToPlayer, `013B:1C6B` GAME:WaitForStoneRelease, `013B:1C81` GAME:ThrowCarriedStone, `013B:1CEE` GAME:UpdateThrownStone, `013B:1DA8` GAME:BeginPassengerResurfacing, `013B:1DD5` GAME:UpdatePassengerResurfacing, `013B:1E9C` GAME:BeginPassengerSinking, `013B:1EC0` GAME:UpdatePassengerSinking, `013B:1F24` GAME:BeginPassengerFloating, `013B:1F43` GAME:UpdatePassengerFloating, `013B:1FE2` GAME:UpdateFloatingDestinationDisplay, `013B:2068` GAME:UpdateFloatingQuestionDisplay, `013B:20C1` GAME:UpdateFloatingPassengerApproach, `013B:2195` GAME:IgnoreWaterbornePassengerState.

#### Hazard update (31 including zero), site 013B:236F

`013B:0000` NULL/non-entry, `013B:1C0E` GAME:IgnoreActorState, `013B:2379` GAME:BeginBirdDelay, `013B:239F` GAME:WaitForBirdFlight, `013B:23B0` GAME:BeginBirdWarning, `013B:23D9` GAME:WaitForBirdWarning, `013B:23EA` GAME:LaunchBirdTowardPlayer, `013B:2493` GAME:UpdateBirdFlight, `013B:252B` GAME:StunBirdAndAwardScore, `013B:255E` GAME:UpdateStunnedBird, `013B:25B1` GAME:BeginTriopterusPatrol, `013B:25C9` GAME:UpdateTriopterusPatrol, `013B:2667` GAME:BeginTriopterusAlert, `013B:2681` GAME:UpdateTriopterusAlert, `013B:272E` GAME:BeginTriopterusCharge, `013B:2748` GAME:UpdateTriopterusCharge, `013B:2830` GAME:BeginTriopterusRecovery, `013B:2844` GAME:AnimateTriopterusRecovery, `013B:288F` GAME:BeginTriopterusImpactRecovery, `013B:28A3` GAME:AnimateTriopterusImpactRecovery, `013B:28EE` GAME:StunTriopterusAndAwardScore, `013B:2914` GAME:UpdateStunnedTriopterus, `013B:295B` GAME:InitializeDinoAnimation, `013B:2973` GAME:UpdateDinoForce, `013B:2A53` GAME:StunDinoAndAwardScore, `013B:2A76` GAME:UpdateStunnedDino, `013B:2A87` GAME:InitializeFruitTreeAnimation, `013B:2AB5` GAME:UpdateFruitTreeAnimation, `013B:2B0C` GAME:ReleaseTreeReward, `013B:2B58` GAME:AdvanceTreeRewardCooldown, `013B:2B7E` GAME:IgnoreExhaustedTree.

#### Item update (2), site 013B:2B8C

`013B:2BE4` GAME:AdvanceFallingItem, `013B:2CA9` GAME:ExpireOrCollectFallingItem.

#### Demo callback (3), site 013B:0A15

`013B:0989` GAME:StartDemoFadeWhenSpriteHidden, `013B:099F` GAME:SetDemoRevealSpriteWidth, `013B:1C0E` GAME:IgnoreActorState.

#### Item spawn, site 013B:2B3A

`013B:2B96` GAME:SpawnFallingItem.

#### Item landing, site 013B:2C8E

`013B:2C97` GAME:LandFallingItem.

**E:** water render dispatch has three frame tail entries at G:2DB3, requiring
saved DS on the caller's stack; these consume it before near RET. **S:** timer dispatch
is only partially resolved: built targets T:0099, S:12E5, S:1939 plus caller-supplied
far pointers and potentially mixed pairs after removal. Saved INT08 is external and
expects PUSHF/far-call/IRET chaining. Neither these nor the four far-call/near-RET hooks
may be hidden behind an invented total callback API. The full 67-site inventory,
including all per-descriptor tail-jump sets, is `program-model.json indirect_sites`.

## Programmer conventions

| Convention | Consequence for a native contract | Evidence / grade |
|---|---|---|
| BX=2*slot through actor/enemy/item callbacks; SI=descriptor; DI often selected player/platform/stone byte index | register role is family-specific; callbacks preserve dispatch BX; player **number**, platform **number** and byte index are different units | E contracts/dispatch G:1486/2363/2B7F; bird target stores number 0/1, then doubles |
| Predicate finishes TEST DI with FFFF miss | SF, not a generic Boolean in AX, is immediately consumed; actor contact also loads AX platform with MOV preserving flags | E G:2202/2271/22E3/235E and callers |
| Scene functions return flags from status word | preserve SF/ZF across cleanup; AX can be changed by wrapper | E G:088D/08D5/0989 |
| near callback in GAME vs far timer callback vs far cdecl original C | typed signatures need separate interfaces; do not infer parameter preservation from ordinary C conventions | E stored words and RET/RETF/IRET; C callers remove arguments |
| Saved-stack tail entries and shared tails | water render frame entries need enclosing saved DS; decimal functions share suffixes; ICE match body lies beyond nearby routine intervals | E program model CFG/stack facts |
| Signed X32/Y32 positions, positive Y downward | pixel cache = SAR5; walking +-20h=one pixel; word wrap and signed comparisons retained; item/stone velocities already position steps, craft raw velocities SAR6 | E G:0E0F/1095/1CEE/2BE4 |
| Level aspect and speed conversions | Y becomes y-SAR(y,2); selected speed/wait becomes v+SAR(v,1); negative odd rounding differs from C `/` | E G:3D4D/3D5A; coordinate scratch write is observable until proved dead |
| VGA memory has row stride 96 bytes across planes | 320 visible columns correspond to 80 bytes/plane within stride; map is 20×16 tiles of 16×12=320×192; sprite bank pixels are column-major bytes, not VGA planes | E G:4172/425A, data decoder |
| FFFF sentinel/hidden conventions are family-specific | FFFF ends lists or hides gameplay sprite; demo 7FFF hides; FFFE seeds animation byte offset, next +2 selects first frame; equality-zero timers can wrap | E descriptor/script handlers |
| Multiple timing domains | animation/state counters count calls/updates; front end uses retraces; audio event ticks and ticks/unit use mutable PIT scheduling; timer slots use 32-bit quanta with 16-bit hardware divisor | E TIMER/SOUND and G:0C7D/239F; seconds conversion unresolved |
| Word reads with byte writes | preserve high byte and stale neighbors for lives/multiplier/action paths; do not replace with a new normalized integer without a projection proof | E G:2CF3/2D14, keyboard ISR vs joystick polling |

**S:** these conventions suggest hand-assembly record/dispatch families rather than
a universal object-oriented runtime. Their repeated field order is stronger evidence than
source adjacency. Original source files/types/register names are not recoverable uniquely.

## DOS and Amiga correspondence by subsystem

Classification applies to the stated property only. E/S grades measure support; they are
not modernization evidence levels A–D. Independent data equality and shared oddities are
stronger ancestry evidence than a similarly named routine. No cross-CPU execution was done.

| Subsystem(s) | Interpretation and concrete evidence | Class / grade |
|---|---|---|
| level_loader, immutable resources | all 69/81 order entries agree; all playable 20×16 maps agree; 78 changed bytes only in attract maps 0/90; platform scalars/type order agree; pointer widths/packed records differ | confirmed equivalent for enumerated tables E; supported close translation of level design S |
| passenger_stone | same itinerary/platform/arrival/request/board/delivery/departure phases and callback order; source platform occupancy pointer/zero becomes index/FFFF; waits scaled 3/2; fixed arrays enlarged 5→16 | supported common design, similar purpose with different scheduling S |
| passenger fare/rescue | land max/floors Amiga 800/200,1900/400,1200/300 vs DOS 1100/300,2600/500,1600/400; water 200/200,400/400,300/300 vs 300/300,500/500,400/400. DOS takes rescue fare before pair switch, Amiga after; quick bonus uses 200-update counter vs fare delta<=200 | confirmed differences E; do not unify rescue/bonus predicates |
| passenger itineraries | map4 first route Amiga 1,0,4,2,3 vs DOS 0,0,4,2,3; map3 Amiga 1,0,4,2,1 vs DOS 0,0,4,2,0; waits agree | confirmed differences E |
| stone and contacts | shared carry/throw/hit role; Amiga stone centrally calls enemy hit callback, DOS hazard scans stone slots; different contact geometry and update placement | similar purpose/different implementation S; contact equivalence unresolved |
| player_physics | Amiga direct velocities integrate into X32/Y32 (ax2/thrust3/gravity1; vx cap200, vy -100..200); DOS raw velocity cap +-6144, horizontal accel63/thrust70/gravity27, SAR6 integration; Amiga mask/blitter collision vs DOS palette bit7 | confirmed arithmetic differences E; reimplemented/retuned physics S |
| hazards/reward sources | same type/order, phases and hit scores 2500/1400/800; direction from animation for Dino; same finite tree reward order | close translation of design S; algorithms/timing differences E |
| Triopterus recovery | Amiga impact selects special countdown `h0:069A0`; DOS G:288F selects normal +16 update G:2844, bypassing nominal G:28A3 | confirmed difference E; not a shared bug |
| bird/Dino timing | common delay/warning/fly/fall and force/stun intent; see DOS-source correction above. Amiga bird warning100 vs DOS70; Triopterus alert100 vs DOS140; Triopterus/Dino stun300 vs DOS350 | confirmed local constants E; no real-time duration equivalence |
| falling_items | Amiga five slots and ordinary full return vs DOS twelve slots and saved-BX RET; both flight→landed→benefit; DOS timer cap5A3B vs Amiga3FAC; tree launch from tree with doubled stone velocity vs DOS stone position/velocity transform; cooldown100 vs210 | confirmed differences E; common design S |
| water_weather | both moving water surface supports craft/passengers; Amiga adds increment each call and stores signed-positive only; DOS applies every second call and clamps negative to0; Amiga copper/blitter vs DOS surface pattern and bit6 tint | similar purpose/different implementation S, local arithmetic difference E; rain field mapping unresolved |
| render_hud, video_dos | shared art/UI roles; Amiga16×16 terrain vs DOS16×12; no tested universal pixel conversion, mask equivalence or frame equality | similar purpose/different implementation S |
| audio, timer | external TFMX mdat/smpl vs ADLX/OPL and DSP/DMA/PIT; no voice/clock/scheduler equivalence established | similar audio purpose S, timer correspondence unresolved |
| input | OS/device-specific input and IRQ/joystick implementation; no matching record proof | similar purpose S, reimplementation supported |
| ice, pictures | DOS maps/logos use verified ICE streams and palette/chunky upload; Amiga assets JOKE/ILBM with blitter display and separate compiled-C intro loader | different representation E; intro/codec algorithm relationship unresolved |
| sequencing, front_end, demo | shared playable level order and scene/game roles; Amiga top-level indirect site h0:00E98 vs DOS direct procedural loops/fade flags | similar purpose S; full phase/script/scores correspondence unresolved |
| numeric, far_copy | DOS fixed aspect/speed conversions and segmented ordered copy serve port representation; a same-purpose Amiga helper is not identified | DOS-specific representation S; algorithm ancestry unresolved |
| external_hooks | DOS broken far calls to near RETs; Amiga asset-loading services exist but have no established one-to-one mapping to these stubs | DOS defect E; intended API H |

**S — ancestry conclusion:** level content, descriptor ordering, hazard phase structure,
score constants and finite reward order support a common design carried into DOS. Physics,
contact implementation, audio/hardware, mutable storage and several state transitions were
reimplemented or changed. No newly established shared **bug** is claimed here: wrong-stride
timer compaction and full-item-pool RET are DOS facts with no matching Amiga defect shown.

## Naming proposals and L0 recovery pilot

**S — proposals only:** Actor remains the storage-family name; PassengerStone and DemoMotion
are distinct views. Enemy storage includes a reward tree, so HazardOrRewardSource is the
component scope; concrete Bird/Triopterus/Dino names are already present and stay stable.
No blanket Actor→Passenger or Enemy→Hostile transformation is justified.
`build/proposals/architecture-model.txt` proposes only three mechanical polymorphic-word
names and their role comments. It does not rename a native interface or apply any rename.
The old labels survive in canonical L1 during this work. Decisions belong to the supervisor.

**E — pilot choice:** the validated scratch `build/workers/archmodel/records/src/asm/RECORDS.INC`
declares DemoMotionHeader (8), PassengerJourneyLeg (4),
SpriteDirectoryEntry (4), with no instances. These layouts have independently decoded
table extents and specific instruction readers; sprite draw and restore agree on dimensions,
journey setup/departure agree on stride, demo initializer agrees with all 28 decoded headers.
Named field offsets replace displacements only at their identified readers, including the
sprite width+height **word** read (do not narrow it). `SIZE` names replace header/leg sizes;
EQU names describe demo-hidden sprite, landed-item lifetime, and timer/life benefit kinds.
No phase-union scratch array is recast as a physical AoS; no unproved Amiga field offset is
copied into DOS. Canonical `src/` is unchanged: include staging/receipt support needs
`tools/build.py` and `tools/asmverify.py`, outside this work order's write list.
`build/workers/archmodel/integration.patch` is the tested integration patch for review.

TASM 3.0 MASM mode exposes these prefixed field names as flat symbols. Naming queries use
`RECORD:Type` and `FIELD:Type.Field`; they stay outside the address ledger. Declarations
have listing offsets but allocate no load-image bytes; the source audit must distinguish
them from emitted data. Includes must be staged into both build variants and the isolated
ASM gate, and hashed in source receipts, before this pilot can be integrated cleanly.
No fixed workstation include path, cached include, or output patch is needed.

## Next closure units and open questions

**S — order:** retain the ICE pilot and the concurrently assigned small units (ordered far
copy, decimal multi-entry group, coordinate scalers). The architecture supports those exact
boundaries; do not split decimal shared tails by physical interval. After those:

1. Define timer slot/handle/far-pair ownership and valid-operation assumptions, then slots
   plus stack adapters. Its defect and external callbacks are prerequisites, not cleanup.
2. Establish common audio projections/aliases, then clock helpers and each ADLX interpreter
   SCC together with wait exits; this closes a coherent owner across C and ASM.
3. Close immutable level/descriptor projection and narrow contact predicates, preserving
   signed bounds, cached geometry and flag outputs. They underpin several object machines.
4. Close falling-item flight/landing/collection under a reviewed full-pool contract. It has
   five routines, explicit phase union, and useful small transition domains, but global benefit
   byte stores and the abnormal failure path must remain visible.
5. Close the mode-specific demo interpreter once actor-storage lifetime and mutable sprite
   width ownership are agreed. Hazards/passengers then benefit from descriptor/contacts/render
   projections. Craft collision comes later because it observes VGA state directly.

| Open question | Grade now | Evidence that would settle it |
|---|---|---|
| Are actor gameplay/demo lifetimes disjoint on every reachable path, including callback corruption? | S intended mode separation | trace all writes/entry paths to shared arrays and prove mode-specific initialization/indices; malformed transfers remain outside any approved contract |
| Exact Amiga per-species working fields and script/animation/header correspondences? | unresolved | follow h0:05A28/065D2/06BBE plus animation consumers; map each offset's reads/writes and pointer origin, not just size |
| Which descriptor zero callbacks/alternate states are reachable? | S family supersets only | relational descriptor/state propagation and bounded initialized traces; preserve null words until excluded by a stated invariant |
| Exact meanings of actor descriptor +3A/+3C and reserved level +09/+19, skipped placement words? | unresolved | independent consumers or build/debug evidence; equal raw bytes alone cannot name them |
| Timer invalid handles, capacity, mis-strided moves, mixed far pairs and IRQ mutation? | E defect, S intended API | paired-word symbolic analysis of actual T:01AA..0340 plus foreground/IRQ interleavings and exact stack-adapter argument contracts |
| Item pool exhaustion reachable under shipped levels/rewards? | H exclusion | bounded capacity proof over spawn/retire ordering, including quick-delivery pickups and tree sequence; otherwise preserve abnormal transfer explicitly |
| Can stale render fields/high bytes be dropped? | H | every later read and alias after each transition, per-page cache projection, and differential scenarios at the exact frame-order boundary |
| Can craft VGA collision become geometry-only? | H | establish palette bit7 mask semantics, plane/latch state, collision sample order and edge cases including reused sample address |
| How many real-time seconds is a state update on either port? | unresolved | exact retrace/update/IRQ scheduling and changing timer periods; do not multiply all waits by a guessed refresh rate |
| Audio sample compression, record +16, full record12 aliases, or broken hook intent? | partial | sample assets and complete mixer consumers; all overlapping C/SOUND views; intended hook implementation evidence. A near RET does not define a valid service |
| Closely translated quirks shared across DOS and Amiga? | H beyond enumerated data/shape | instruction-level paired algorithms showing the same unusual observable result on the same logical inputs; retain actual confirmed differences |
| Original module/source arrangement and natural relocation order? | unresolved | link/OMF ordering evidence that retires fragment.py while retaining packed-file equality; this model adds no source-provenance claim |

The maintained proof remains full packed UGH.EXE equality, with exact ASM, exact original C,
runtime-library attribution, known-owner data and UNKNOWN debt reported separately by the
existing gates. Record declarations change readability, not proof class or debt ownership.
