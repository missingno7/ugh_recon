# Steps 5-7: state composition and a machine-free production target

Planning baseline: committed `c358a8419574a949b592db23424205062211bfca` (pixel_world). This is a proposal, not a migration or a new gate result. The presentation/HUD/weather cut (4P) has since landed as `presentation_world`. It moved 1,221 more bytes, bringing native ownership to 7,660, and it left Water Y, the player draw caches and the actor histories for step 5. Reconcile its allocation manifest (`metadata/closure/presentation_world.json`) before implementing any overlapping cut below. The ledger accounts for all 392 model names:163 start in native bindings and 229 remain; six owner/provider groups cover 6,439 historical bytes.

The next state cut should be the small shared run/configuration nucleus, including the live current-level record, followed by players and then object families. Move storage once; keep existing algorithms and ordering. A source module called native today can still contain only a temporary working projection; no new owner may be inferred from its name.

## Composition rule for every cut

Use the accepted seal/import/serializer pattern, then replace island peer transfers with ordinary semantic calls. A proposed `GameWorld` contains the existing audio/timer, palette, input, page and pixel owners plus the new run, players, platforms, actors, hazards, items, resources, front-end and lifecycle owners. During staging it can hold references to existing authoritative stores; it must not copy their values into a second persistent aggregate. Consolidation of allocation is separate from inventing another state owner.

Keep `GameServices` separate: live indexed planes/latches/controls and DAC, OPL, input queues, timing delivery, file handles and lifecycle platform replies. Keep `GameResources` separate too: immutable data, stable descriptor/script/music/picture identities, and explicitly mutable reveal metadata/workspaces. A resource registry is not a code-address resolver. No new global replaces another unit's state silently.

Each moved field gets exactly one native getter/store route. Remaining legacy callers use a documented typed borrower or an explicitly tested shared byte view until their adapter retires. Callback/service boundaries must reread the live owner rather than republish stale parent snapshots. Retain unknown words/reserved bytes as raw retained fields with their actual write sites; do not infer a feature or normalize them.

## Acceptance recipe, repeated per landable cut

1. **Static allocation/borrowers:** publish exact physical observation byte manifest, aliases, all model readers/writers and additional literal/native bulk/indirect writes. Verify no overlap with accepted owners. An absent model writer is not a constness proof. Define typed production arguments/results separately from observer-only legacy identity/return metadata.
2. **Projector:** cold fixture import once; keep the live RAM lanes sealed. Serialize moved fields into the separate observation view at every frame and terminal boundary. Every moved byte must come from native owner/service state, with zero moved-owner journal publications; missed publication must stop, never resynchronize. Retain baseline/journal for *unmoved* unknown bytes until a later cut accounts for them.
3. **API and corpus replay:** retain independent L1/Unicorn evidence. Test whole RAM, live replies and ordered ports/services at each existing cut, including partial-service failure prefixes, DF and raw aliases within the admitted domain. Each claimed service stream must be instrumented, nonempty and count-checked. List every production-domain rejection explicitly, rather than counting it as equal. Do not silently inherit the old fallback's success.
4. **Router/proof:** all 256 byte values through every owned lane, word/alias/identity round trips, neighbor frame and dependence checks, partial writes and borrowed views. Use split actual-C properties for small updates;600s/8GiB per child, serial. Big mutable workspaces need generated overlap/bounds cases rather than a misleading whole-world solver profile.
5. **Census:** zero fallbacks or L1 game bodies over maintained runs; zero machine edges within the enlarged island. Count real callbacks/entries so an empty run cannot pass. Incoming hardware services and still-external ABI callers stay explicitly identified until their own cut. API admission failures fail closed.
6. **Integration:** clean committed-HEAD archive plus only the cut, scratch certificate promotion, closure/build,21/21 host checks in both variants, and openings 81/81 + audio 7/7 + deep 8/8. Keep literal pure L1. The projector uses all 20 scenarios plus smoke. Extend API witnesses for branches the scenarios do not reach; neither a scenario title nor an in-bounds capacity establishes coverage.
7. **Controls/relocks:** use the cut-specific defects below plus missed serialization and stale-parent-overwrite controls. Every defect must be observed by a positive comparator with exact scenario/boundary or API case. Relock changed/cascading certificates with scoped notes; no accepted claim is widened merely because storage moved.

These are proposed gates. This planning task ran only static consistency scripts, not these integration jobs.

## Ordered, coherent cuts

Exact model-cell sets are below and in [LEDGER.md](standalone-ledger.md); `cut-cells.json` has the complete routine reader/writer sets. They are model names, including aliases, not separate allocations. Nonmodel buffers and process continuations are stated explicitly. R can land independently alongside A; no implementation should take the pending 4P cells before that worker's review.

### 4P: Step 4 HUD, decimal-history and weather storage (landed as `presentation_world`)

Exact named cells (35): `CachedTimerBarWidth`, `DecimalDigit1`, `DecimalDigit2`, `DecimalDigit3`, `DecimalDigit4`, `DecimalDigit5`, `DecimalDigitBuffer`, `HudCachedFare`, `HudCachedLevelCounter`, `HudCachedLives`, `HudCachedMultiplier`, `HudCachedPlayerOneIconState`, `HudCachedPlayerTwoIconState`, `HudCachedScoreHigh`, `HudCachedScoreLow`, `HudDigitCursorX`, `HudDigitCursorY`, `HudFareClearPending`, `HudFareX`, `HudLevelCounterX`, `HudLivesX`, `HudMultiplierX`, `HudPlayerOneDestinationX`, `HudPlayerOneIconX`, `HudPlayerTwoDestinationX`, `HudPlayerTwoIconX`, `HudScoreX`, `RainParticleOffsets`, `RainParticleXModuloFour`, `RainPreviousOffsets`, `WaterRestorePending`, `WaterStepPhase`, `WaterSurfaceByteOffset`, `WaterSurfaceFrame`, `WaterSurfaceFrameCountdown`.

**Handoff, not a new assignment.** Read the accepted presentation owner only after it lands. At this HEAD the listed 35 names are still RAM-backed. It must settle actual numeric-history allocations and the rain slot 193/input-owned alias; preserve loader and decimal borrowers. Water Y, score/timer/fade, player caches and object histories are deliberately *not* claimed by this pending group. If its final manifest moves any listed raw alias, subtract that byte from later cuts and retain a borrower; never add another owner.

**Proof/risk:** inherit that cut's actual allocation/alias evidence and use all common gates. Do not guess its final byte total or count pending work as accepted.

### 5A: Shared configuration, run scalars and the live level-record nucleus

Exact named cells (30): `CurrentLevelIndex`, `CurrentLevelRecord`, `LevelActorList`, `LevelCompletionMarker`, `LevelEnemyList`, `LevelIntroTextPointer`, `LevelPlatformList`, `LevelPlayerOneStartX`, `LevelPlayerOneStartY`, `LevelPlayerTwoStartX`, `LevelPlayerTwoStartY`, `LevelRainDirection`, `LevelTimer`, `LivesRemaining`, `PlayerArrayBytes`, `PlayerCount`, `PlayerOneControlMode`, `PlayerTwoControlMode`, `PreviousWaterSurfaceY`, `RemainingPassengerJourneys`, `ScoreHighWord`, `ScoreLowWord`, `ScoreMultiplier`, `ScreenFadeLevel`, `ScreenFadeStep`, `SelectedDifficulty`, `WaterSurfaceStep`, `WaterY32`, `WaterYPixels`, `ds_27C8`.

**Owner:** one `RunState` and configuration plus one mutable `LevelRuntimeRecord`. Keep player count, PlayerArrayBytes and modes as distinct raw words, byte lives/multiplier/completion/journey/rain and wrapping score/timer/fade values. The26-byte record owns its odd-aligned water word and remaining-journeys byte; weather and passengers borrow those fields. Pixel water Y and previous Y are distinct values, never continuously recomputed from fixed Y. D:27C8 stays an unknown raw word. The320-byte tile map at Data_264C is also an explicit level working buffer even though it is absent from the 392-name set.

**Shared writers:** menus and joystick calibration write configuration; IRQ/control polling borrow it. HUD caps/changes score/timer/fade, hazards/items/passengers award or drain them, high scores clear score, session resets/progresses, weather and menus change water. Each gets a narrow live borrower; neither HUD nor SessionWorld is another persistent copy. Keep the loader's descending record stores and the 392-byte multi-owner clear as explicit ordered transactions. This storage-first cut can retain existing loader/frame adapters; direct sequencing follows6A.

**Seed:** stale score after passenger award, swapped score halves, lost second control mode, treating PlayerArrayBytes as derived, dropped keyboard high byte, water copied from a stale record, missing journey decrement, reserved-byte reset, incorrect odd water lane in a descending record store. Test live menu water save/restore and IRQ between request cuts. Common missed-serialization defect also applies.

**Risks:** this touches the most shared scalars. Review unknown/conditional views before sealing; include front-end, demo, two-player and hazard prefixes, not only gameplay. No live policy decision required under existing scripted services.

### 5B: Random state and the partial seconds reseed alias

Exact named cells (6): `RandomSecondsSeedByte`, `RandomStateStorage`, `RandomStateWord0`, `RandomStateWord1`, `RandomStateWord2`, `RandomStateWord3`.

**Owner:** `RandomState.word[4]` once, with the seconds byte as the high-byte alias of word0. RandomStateStorage/Word0..3/RandomSecondsSeedByte are views, not six allocations. All random consumers, including water respawn and hazards, borrow this state; initialization is separate from partial seeding.

**Seed:** replace the whole seed word, reorder recurrence word updates, skip bound-zero advancement, consume an extra random number during rain prewarm. Replay random API/full-domain small arithmetic and all common gates, including wet/deep levels.

**Risks/decisions:** extra RNG calls diverge far downstream. Storage and direct calls need no new policy; *live* seeding waits for D4, at the existing seed point only.

### 5R: Resource identities, readonly tables and codec workspace (constness and aliases require provider review)

Exact named cells (43): `BasePalettePointer`, `CompressedTileMapsPointer`, `CurrentTileMapPointer`, `DecimalHundredDivisor`, `DecimalTenDivisor`, `DecimalTenThousandDivisor`, `DecimalThousandDivisor`, `DecodedImagePointer`, `DemoCompletionScanBiasedBase`, `DemoRevealWidthPointer`, `DspProbeIrqOrder`, `DspProbeIrqOrderStorage`, `FadedPalettePointer`, `IceDecodeWorkspace`, `IceMatchLengthBiases`, `IceMatchLengthBitCountsMinusOne`, `IceMatchOffsetBiases`, `IceMatchOffsetBitCountsMinusOne`, `IceScratchPointer`, `KeyboardHandlerVector`, `LevelCountsByPlayerMode`, `LevelOrderTables`, `LevelWorkspacePointer`, `MultiplierLimitsByDifficulty`, `PaletteSourcePointer`, `PasswordCompareBiasedBase`, `PicturePaletteDestination`, `PlayerAnimationCycleEnds`, `PlayerAnimationCycleStarts`, `PlayerImpactLimits`, `SpriteDirectoryPointer`, `SpritePixels0To216Pointer`, `SpritePixels217To297Pointer`, `SpritePixels298To546Pointer`, `SpritePixels547AndUpPointer`, `TimerBarDivisor`, `TimerBarPointer`, `VgaCumulativePlaneMasks`, `VgaRowStrideBytes`, `VgaSinglePlaneMasks`, `WaterSurfaceDispatch`, `WaterSurfaceDispatchWords`, `ext_0A67`.

**Owner/bindings:** an explicit resource registry and bounded mutable codec workspace, not another 1-MiB RAM allocation. Most listed names are readonly data/reference cells or biased views, not game scalars. Base/faded/picture pointers borrow accepted palette storage; current-tile pointer borrows5A's map; KeyboardHandlerVector becomes the closed keyboard-handler role. DemoCompletionScanBiasedBase and PasswordCompareBiasedBase remain biased views of 5E/6B storage; do not allocate independent “resource” copies. `ext_0A67`, DecodedImagePointer and IceScratchPointer denote the same scratch resource binding. Keep mutable sprite reveal width in the registry's explicit metadata owner.

**Nonmodel data:** immutable 81 level records,150 ordered password entries, sprite directory/four pixel banks, descriptor/animation/journey/script tables, pictures, packed maps and ADLX resources. Retain raw reserved/skipped resource bytes and descriptor identity distinctions. Assign finite descriptor/callback roles in an extraction/build manifest, then validate package identities at runtime admission and use those roles. Verification alone maps them back to historical words. A retained raw-data provider may validate encoded words, but must not turn their original code addresses into a production dispatcher. Pure level/actor resource APIs are already accepted; remove their segment-reading helpers when all users borrow stable typed descriptors. Keep the live loader's ordered reads; do not eagerly normalize values that it mutates or rereads.

**Seed:** swapped resource identities, wrong player animation shared boundary word, clipping a workspace to nominal output, overwriting ICE's native-audio flag overlap, lost reveal width, stale decoded map after an attract/session transition, using a frame-start resource snapshot. Router tests include all provider identities and existing malformed/truncated/overlap cases.

**Risks/decisions:** a complete alias allocation manifest is larger than 43 names. Ordinary registered resources and current immutable data provider need no new pack decision; D3 selects a future package and missing-data behavior, D5 the wider full-window/foreign-resource compatibility domain. Split R into registry then workspace if the latter's overlaps cannot be reviewed in one cut; both retain the common gates.

### 5C: Both players, commands, motion and draw caches

Exact named cells (37): `PlayerActionInput`, `PlayerAnimationCountdowns`, `PlayerCachedPixelX`, `PlayerCachedPixelY`, `PlayerCachedSpriteIds`, `PlayerCarriedKinds`, `PlayerDestinationIcons`, `PlayerDownInput`, `PlayerHorizontalVelocities`, `PlayerImpactMagnitude`, `PlayerLeftInput`, `PlayerMinimumFares`, `PlayerPassengerFares`, `PlayerPixelX`, `PlayerPlatformIndices`, `PlayerRightInput`, `PlayerSpriteIds`, `PlayerThrustAnimationRate`, `PlayerTwoAnimationCountdown`, `PlayerTwoCachedPixelX`, `PlayerTwoCachedPixelY`, `PlayerTwoDestinationIconIndex`, `PlayerTwoFare`, `PlayerTwoFixedX`, `PlayerTwoFixedY`, `PlayerTwoPassengerIconState`, `PlayerTwoPixelX`, `PlayerTwoSpriteId`, `PlayerUpInput`, `PlayerVerticalVelocities`, `PlayerX32`, `PlayerY32`, `PlayerYPixels`, `SecondPlayerYPixels`, `ds_27FA`, `ds_2812`, `ds_2816`.

**Owner:** both player records, separate current simulation pixels and cached draw history, and the five two-word command arrays. Keep raw aliases for every second-player label. Exclude D:2800..2803 from player ownership: those are the two named HUD icon-cache words, interleaved between carried-kind and destination arrays, and belong to 4P. Retain genuinely unknown lanes only according to actual allocation/write evidence. Animation cycle bounds and difficulty impact table remain resource views from R, not per-player runtime arrays.

**Shared writers:** input IRQ writes command bytes and polling writes words; loader seeds selected fields and clears the encompassing command/HUD window; physics and hazards change motion/platform; passenger/stone code changes carried state, destination, fare and minimum fare; render/HUD updates animation and draw caches. Borrow one player store at each cut; no cached physics-versus-render copies. Typed byte views must cover low-byte IRQ stores without clearing stale high bytes.

**Seed:** byte store clears the high lane, player 0 write aliases player 1, rebuild caches from current position, clear caches or carried/fare values at a new level incorrectly, lose a Dino velocity update, read the old player snapshot after a stone service, reorder a collision read. Replay input, physics, renderer/HUD and interaction APIs with live pixel service replies; all common gates.

**Risks:** two-player and joystick order, D:2648 reset window, and simulation/cache freshness. No D2 choice needed to move commands; live joystick count units remain a backend decision.

### 5D: Platforms and mutable occupancy

Exact named cells (8): `PlatformActorOccupants`, `PlatformArrivalPointsX`, `PlatformDestinationIcons`, `PlatformHeights`, `PlatformLeftEdges`, `PlatformRightEdges`, `PlatformSpawnX`, `PlatformWaitingPointsX`.

**Owner:** the eight parallel 10-word platform arrays (160 bytes for their declared ordinary storage), including mutable occupancy. Geometry, spawn and destination fields retain raw word patterns; `reserved_raw` in source placements remains resource evidence.

**Shared writers:** loader populates geometry/initial occupancy; passengers board, resurface, place and approach through live occupancy; physics, stones, items and patrol read geometry. Give these operations borrowed platform views and ordered occupancy mutations. Avoid whole-array write-back after a passenger callback.

**Seed:** stale occupancy after boarding, duplicate occupancy on resurfacing, choose last rather than first equal platform, alter inclusive/signed boundary or sentinel test, recompute cached platform indices from geometry. Replay contact/platform/physics/passenger/stone/item APIs and all gates.

**Risks:** negative-left sentinel versus FFFF descriptor sentinels, capacity 10 versus valid active-prefix bound, saved source/destination byte indices. Broader invalid indices are explicit D5 admission, never a new spare slot.

### 5E: Shared actor/demo/stone/passenger slots and render histories

Exact named cells (24): `ActorAnimationByteOffsets`, `ActorAnimationCountdowns`, `ActorDescriptors`, `ActorDestinationPlatformByteIndices`, `ActorDestinationPlatforms`, `ActorEraseOverlaySprite`, `ActorEraseSprite`, `ActorInitialPlatformIndices`, `ActorJourneyCursors`, `ActorOverlayOrScriptCallbacks`, `ActorPixelX`, `ActorPixelY`, `ActorPlatformOrScriptDone`, `ActorPreviousDrawX`, `ActorPreviousDrawY`, `ActorSourcePlatformByteIndices`, `ActorSpriteIds`, `ActorUpdateOrScriptCursor`, `ActorX32`, `ActorY32`, `PassengerQuickDeliveryCountdowns`, `ds_2A2D`, `ds_2ACD`, `ds_2C6D`.

**Owner:** one 16-slot actor store with persistent renderer history and the accepted gameplay/demo views. The physical 24-array 768-byte vocabulary and raw alias cells are in docs/actor-storage.md. Retain inactive aliases and placement seeds; use a mode/phase-aware view, not independent persistent PassengerStoneSlot and DemoMotionScene copies. Resource IDs, itinerary cursor/leg, gameplay callback phase, demo bytecode cursor and demo effect are distinct typed identities. Retained raw words need not gain an invented gameplay name.

**Shared writers:** session loader and reset, demo initialization/update/reveal, passenger/stone transitions, hazard stone-contact effects and both render histories. `actor_pass` is already native, but still has a Regs adapter: make its callback service take the typed current actor and world, with a typed resume cursor. After every callback reread descriptor, live callback and modified cursor at the accepted cut. Demo callbacks must see new position/sprite and the *old* script cursor until original publication.

**Seed:** drop or reorder a callback, cache the pass target before a callback mutates it, ignore returned cursor, switch active alias too early, reset demo histories on mode change, replace7FFF withFFFF, update an alternate stone as the primary contact identity, clear stale overlay history in hidden/clipped cases. Replay every actor/demo/passenger/stone/render/actor-pass API, resource corpus and common gates.

**Risks:** this is the largest strongly coupled storage cut. Land storage+borrowers first, then direct callback/transition services in a second certificate if needed; each must pass the same gates. Preserve the in-array sentinel/domain and unknown callbacks as explicit Unsupported, with no resolver escape. D5 only for broader raw callback/alias states.

### 5F: Enemy/hazard slots and render histories

Exact named cells (19): `EnemyAnimationByteOffsets`, `EnemyAnimationCountdowns`, `EnemyAnimationOrDropLists`, `EnemyDescriptors`, `EnemyDirectionOrTargetPlayer`, `EnemyDrawX`, `EnemyDrawY`, `EnemyEraseSprite`, `EnemyFlightSoundHandles`, `EnemyHorizontalSpeeds`, `EnemyInitialDelays`, `EnemyPlatformIndices`, `EnemyPreviousDrawX`, `EnemyPreviousDrawY`, `EnemySpriteIds`, `EnemyStateCallbacks`, `EnemyStateCounters`, `EnemyX32`, `EnemyY32`.

**Owner:** enemy/hazard slots and current/prior render history, using the 19 five-word arrays (190 ordinary bytes). Keep descriptor, callback, animation/drop-list and sound-handle identities separate. Do not invent a sixth descriptor sentinel independent of the next physical array.

**Shared writers:** loader, tree/bird/Dino/Triopterus states, session draw/erase, reset and sound start/stop. Hazards borrow5C players,5D platforms,5E stones and 5A score/fade/water. Apply selected-stone and player effects immediately through those owners; no copied HazardWorld becomes authoritative. Direct typed sound requests consume live replies before continuing.

**Seed:** stale selected player's velocity, wrong stone ID, apply award after a failing service, lose bird sound handle, collapse target-player and direction alias, reorder front/back enemy rendering, normalize signed countdowns. Hazard/contact APIs plus all level groups are essential; zero scenario entry counts require explicit API evidence.

**Risks:** descriptor-relative callback graphs, indirect animation offsets and secondary writes. D3/D5 only if changing admitted resources or raw alias domain.

### 5G: Falling items and render histories

Exact named cells (12): `FallingItemCallbacks`, `FallingItemDescriptors`, `FallingItemDrawX`, `FallingItemDrawY`, `FallingItemEraseSprite`, `FallingItemMotionOrLifetime`, `FallingItemPreviousDrawX`, `FallingItemPreviousDrawY`, `FallingItemSprites`, `FallingItemVerticalStep`, `FallingItemX`, `FallingItemY`.

**Owner:** twelve falling-item slots including twelve arrays of descriptor/callback, motion-or-lifetime, draw/history/sprite and vertical step (288 declared bytes). Reuse accepted typed item-kind policies, with a single current record view for whichever callback is active.

**Shared writers:** release-tree/spawn logic, descend/collect/expire transitions, reset/session history passes; item awards use5A and player contact uses5C. Keep descending index order and current/prior draw generations, not a compacted vector that changes order.

**Seed:** reverse descending pass, collect twice, stale timer after a timer-item award, normalize the motion/lifetime alias, clear erase history for inactive items, publish fields after a service failure. Replay generated lifetime/contact/award cases, including full-pool and stale-tail slots, and all common gates.

**Risks:** reuse/inactive history, byte score/lives/multiplier arithmetic and raw item identities. D5 for broader callback/invalid-slot inputs.

### 6A: Session/demo continuation and loader arithmetic scratch

Exact named cells (2): `CoordinateScaleScratch`, `DemoExitCode`.

**Owner:** session/demo run continuations, loader scaler scratch and DemoExitCode. The persistent fields live in 5A/C/D/E/F/G or accepted4P, not in duplicate SessionWorld snapshots. Move `SessionProcess`, `SessionLoadRecord`, display/reset/frame cursors and demo continuation into direct native orchestration as needed; native automatic local variables are fine for blocking calls, explicit continuation state for event suspension.

**Direct services:** compose password lookup, live record/resource read, decode/map copy, player/platform/actor/enemy initialization, wet prewarm, display reset and complete frame sequence. Keep original service order and failure prefixes. Pass per-player cursor/index as a native value, preserve post-callback rereads, pause release/make/break polling and synchronous audio/timer cuts. The per-level verification guard remains diagnostic, not a gameplay timeout or a new end-of-level rule.

**Seed:** wrong descending record copy, reorder rain prewarm, reorder erase/update/draw phases, skip pause polling/delivery, advance frame/time during pause, continue after a failed resource service, confuse escaped return with level completion, turn the per-level guard into a game outcome. Session/sequencing/loader/differential cases and every 81+7+8 reference are the principal gate; prefix/API tests cover absent errors and API-only entries.

**Risks:** finite fixture methods currently enter mid-session. Direct startup path must also reach the same flows without fixture injection. Existing deterministic scheduling allows the cut now; live pacing waits for D1, new resource error policy for D3.

### 6B: Front-end table, editors and mutable text

Exact named cells (12): `HighScoreFileHandle`, `HighScoreNameChars2To3`, `HighScoreNameChars4To5`, `HighScoreNameChars6To7`, `HighScoreNameChars8To9`, `HighScoreNameEntry`, `HighScoreRowStride`, `HighScoreRows`, `LevelNumberTensCharacter`, `LevelNumberUnitsCharacter`, `PasswordEditBuffer`, `PasswordEditChars2To3`.

**Owner:** one high-score table/editor and password/text state. Preserve107 raw table bytes (five 21-byte rows plus two terminators), stride, file handle binding,12-character name editing with retained field tail,20-byte password buffer and its biased/word aliases, and mutable level-number text characters. Add the actual indexed-string scratch allocation and text cursor/edit/blink/menu continuations after an allocation audit; they are not all named in the 392 cells.

**Shared writers:** file read, complement/shift/insert/decimal consumers and direct menus/session. Score/config/water remain5A borrowers, commands5C/input remain shared services. File I/O becomes explicit open/read/write/close replies and byte spans, preserving short-read stale tail and the native logical open/close sequence, including leaked/unclosed bindings. A backend may flush/close an OS handle internally without inventing a logical game close; broader normalization is D5. No whole configuration snapshot may overwrite an input/menu mutation. Session alone retains password-to-level lookup.

**Seed:** copy a NUL that the indexed copy omits, bound or clip a retained overrun silently, reverse row shift, close a leaked handle in the logical flow, clear short-read tail, change tie qualification or digit order, miss a menu wrap, mask a release scan before raw dispatch, alter centering, restore stale Water Y after an intro service. Replay high-score/menu/password corpus and existing nonempty ordered-service drivers plus all gates; credits retain API-only evidence.

**Risks/decisions:** arbitrary output aliases and unbounded string/edit windows require explicit D5 policy; D3 chooses live file/package errors. The107-byte encoding and shipped password mapping are constraints, not choices.

### 6C: Lifecycle saved mode / terminal state

Exact named cells (1): `SavedBiosVideoMode`.

**Owner:** native lifecycle continuation and saved-mode binding, with typed terminal result. The only remaining named RAM cell here is SavedBiosVideoMode; service state also includes video/input/audio installation lifetimes, which remain with their respective owners. Do not put second saved vectors or sound flags in lifecycle.

**Direct order:** platform setup/query/save, critical-error binding, scores, existing seed point, picture mode/input install/calibration/AdLib-only init/clear; startup pictures; gameplay pages; menu/session loop. Terminal order remains stop/fade sound, saved video restore, keyboard restore, terminal exit; failure stops at the accepted consumed prefix. Read the unmasked saved-mode byte live after sound. Exit consumes the live low byte after input restoration (currently the BIOS queue-flush reply), so the typed terminal reply must retain that result rather than substitute exit 0. Startup pictures' Q/Escape/input paths and keyboard restoration must match. CPU probe/flags and DOS INT24 frame belong to the verification adapter; prove live semantic results before removing that shell.

**Seed:** swap sound/input teardown, restore input twice, use a post-init mode rather than saved mode, synthesize cleanup on a service failure, initialize device bit 2, repair an external hook, reseed each level, enter attract fixture instead of full startup. Replay lifecycle/terminal/picture APIs, startup/adlib/gameplay-adlib and all common gates.

**Risks/decisions:** typed `GameExit` and provider install tokens replace DOS return/IRET frames; no invented hook role. D1/D3/D4 and optional D5 are live-backend choices, not blockers for deterministic composition. At this cut there must be no semantic caller still requiring a Regs bridge; test adapters may remain solely in verification.

## Step 7: admission, service extraction and unlink

Do not jump from “zero executed L1 bodies” to deleting every dormant path. Follow [LEDGER.md](standalone-ledger.md)'s debt rows and per-bridge inventory:

1. Freeze a production admitted-domain manifest: supported resources, modes, callbacks and error replies; explicitly list 188 audio declines (including the 32 timing declines), pixel's two compatibility services and all still-live fallback guards. Preserve ordinary byte-wrap, stale fields and callback order. D5 is required to narrow broader accepted literal/API compatibility; D3 if admission changes data errors. Unsupported must fail closed with a typed result at the documented prefix.
2. Extract concrete port implementations from generated c/platform.c providers into independently tested service backends. Implement native input/vector tokens, scan/BIOS queues, axis/button measurement, retrace/event cuts, ordered OPL/DAC/indexed planes/latches, files/resources and terminal lifetimes. Keep the deterministic backend first; do not make a live OS scheduler a prerequisite to proving composition. The indexed backend must satisfy the full current pixel contract unless D5 explicitly adopts a narrower measured profile; hidden storage, lane mask/read plane, live latches/copies and collision index bits still matter on the shipped path.
3. Remove *all* Regs/signature/stack/segment/flag-helper interop between native peers. Some bridges merely discard wrappers; others still contain real sequencing, alias or failure-prefix work which must move into native semantic composition first. The51 bridge files are not production services simply because they call pure kernels. Separately prove whether the reached DGROUP:0002 shutdown write has an admitted game reader; keep its terminal observation in the test recorder even if it becomes observer-only. Resource projections in the two bridge files without Regs also need replacement.
4. Generate semantic resource/callback identities in the extraction/build manifest; runtime admission validates those registered data identities. Native descriptors hold enum roles, typed handles or direct validated functions, not offsets for c/dispatch.c. A retained image-data provider needs the same semantic manifest; it cannot use a runtime code-word-to-function resolver. Do not put historical offset->function maps in a newly named “platform” file. Unknown/open halves remain test compatibility data or explicit Unsupported, never an executable fallback.
5. Build a new positive production source manifest and fail its link if any forbidden dependency remains. Remove the 27 c/ units, dispatch table/resolver, memory router, machine devices and ugh.h helpers from that target. Do not delete the L1/reference implementation or verifier; separate targets are how the evidence remains independent.
6. Independently run deterministic scripted startup/frame/terminal service traces through the production semantic executable plus a *test-only* observation recorder. Compare with the same whole-game/projector/level references. The recorder serializes owner state and explicit service effects; it may keep historical return identities and retained-byte journals, but never supplies data from expected records and never resynchronizes a missed publication.

Each numbered step is a reviewable patch/certificate, not one unbounded rewrite. An nm grep alone cannot validate semantics; it complements the positive source/include/link manifests and the common evidence gates.

## Mechanically checkable production-target definition

Proposed target: `ugh-native` (name only, not created here).

**Positive link manifest:** accepted ordinary native algorithm C sources, resident native owner implementations, new semantic composition/boot/continuation modules, explicit native resource readers/default constructors, and a chosen port backend (SDL3/OPL plus ordinary C/runtime libraries). Audit each selected file and transitive include. No glob of c/, native/bridge/, host/ or verif/. Existing world storage can be aggregated by reference initially; the final manifest identifies exactly one store per state domain. Production code paths may not require generated replacement sources from tools/hostbuild.py.

**Concrete source-manifest proposal (paths below are a plan, not files created by this task):**

| Layer | Explicit sources / action |
|---|---|
| Existing pure kernels and owners | The following51 ordinary native files are the candidate allowlist. Keep their algorithms; split verification-only declarations and give owners native constructors before production admission. Unreachable digital policy kernels may remain linked as pure policies without a DOS/SB provider; no broken hook implementation is included. |
| New semantic composition | Proposed native/game_world.c, native/compose_players.c, native/compose_actors.c, native/compose_hazards.c, native/compose_items.c, native/compose_session.c, native/compose_front_end.c and native/compose_lifecycle.c. These hold typed borrowing, direct calls and continuations extracted from adapters, not renamed Regs shells. |
| New production backend | Proposed port/sdl/main.c, port/sdl/video.c, port/sdl/input.c, port/sdl/time.c, port/sdl/audio.c, port/sdl/files.c and port/resources.c. Link SDL3, the pinned standalone OPL implementation and ordinary runtime libraries as needed. Select exactly one implementation of each GameServices operation. |
| Build flags | A new target-specific manifest/compile command; no UGH_NATIVE_* verification interop defines, no forced bridge_fallbacks.h, no host-generated source rewrites or dispatch table. A generated resource/default-data manifest may be data, never game code or a RAM fixture. |

`native/actor_pass.c`, `native/actor_render.c`, `native/actor_resources.c`, `native/adlx_allocation.c`, `native/adlx_digital.c`, `native/adlx_effects.c`, `native/adlx_facade.c`, `native/adlx_lifetime.c`, `native/adlx_loader.c`, `native/adlx_main.c`, `native/adlx_music.c`, `native/adlx_samples.c`, `native/adlx_sections.c`, `native/adlx_voice.c`, `native/audio_world.c`, `native/contacts.c`, `native/coordinate_scale.c`, `native/decimal.c`, `native/demo_core.c`, `native/demo_presentation.c`, `native/far_copy.c`, `native/hazards.c`, `native/high_scores.c`, `native/hud.c`, `native/ice.c`, `native/ice_scratch.c`, `native/input.c`, `native/input_world.c`, `native/items.c`, `native/level_view.c`, `native/lifecycle.c`, `native/menus.c`, `native/music_clock.c`, `native/palette_world.c`, `native/passenger_delivery.c`, `native/passenger_itinerary.c`, `native/passenger_water.c`, `native/pictures.c`, `native/pixel_world.c`, `native/player_physics.c`, `native/random.c`, `native/render_primitives.c`, `native/session.c`, `native/stones.c`, `native/terminal_tail.c`, `native/timer.c`, `native/timer_lifetime.c`, `native/timing_world.c`, `native/video_dos.c`, `native/video_pages.c`, `native/water_weather.c`.

This is an explicit seed allowlist, not an instruction to glob native/*.c forever. The pending presentation owner must be added only after review; later semantic modules/headers get explicit manifest entries. Every selected source's transitive closure still has to pass the bans below.

**Excluded sources:** all 27 c/*.c, all current 51 native/bridge/*.c and their ABI/provider headers, c/dispatch_table.inc, c/ugh.h/c/ugh_sym.h, current host/main.c/scenario.c/digest.c, verif/projector and verif/*platform_model.inc, generated MZ relocation loaders/fixture/import/observation code. Current host audio/video/input source must be refactored before reuse, because it still reads machine device state. A portable data package/provider may retain original *data* encodings; loading a mutable 1-MiB DOS machine or game code is forbidden. Old-address resource translation and observer metadata stay outside ordinary game APIs.

**Banned dependencies and symbols:**

- Link/import/object manifests reject any c/ or bridge/verification object even if function-section garbage collection hides its symbols. Inspect objects/archive members and every transitive preprocessed include as well as the final map.
- No `l1_*`, `c_*` game entry, `ugh_*`, `ugh_mem`, `ugh_devices`, `Regs`, `UghAdapter`, `ugh_dispatch`, `ugh_resolve`, `ugh_call_near`, interrupt/far/ret-hook shims or dispatch_table target data. Public `c_*` may be reserved as a namespace to simplify the gate; do not confuse allowed C runtime symbols with game entries.
- No machine accessors/flags (`lin`, rd8/16/32, wr8/16/32, sub16/logic/flag register helpers), original `UGH_S_*`/`UGH_O_*` constants, segment-register or emulated-stack types in the production preprocessing closure. Names alone can collide, so combine token bans with an allowlisted header/symbol graph.
- No `*_cold_import`, `*_require_seal`, `*_shared_read/write`, historical `*_serialize/check_serialization`, `project_timing_observation`, `pr_*`, `sc_*`, `api_*` test entry wrappers, host_digest/host_symbol/scenario_fixture/scenario_defaults or a baseline/journal RAM observation buffer in the production closure. Ordinary serializers such as score file encoding are allowed; the ban is on historical observation machinery.
- No `pixel_service_continuation`, `pixel_service_compatibility_write`, opaque machine-context casts, saved vector coordinates, raw code-bank admissions or open target-word fragments unless replaced by a reviewed semantic role that no longer requires the machine. No real callback receives Regs. No game writes from SDL/audio threads; scheduling remains owned by the chosen event policy.

**Machine-free witness:** link and start with the MZ/RAM/dispatcher/reference files unavailable. The source manifest must still admit its chosen portable data provider. Run typed boot and scripted input to startup, menu, gameplay, pause and exit through the production path. Verify no 1-MiB emulated allocation, seg:off resolver or hidden interpreter is reintroduced under another name. A legitimate 64-KiB bounded codec buffer or four 64-Ki-cell video planes is explicit resource/service storage, not by itself a forbidden machine.

**Verification target:** keeps the independent literal variant and the native composition test adapters, projector, cold scenario import, full device/effect observer and source-built oracle resources. It can call a typed production core and attach a deterministic provider, but production must never call back into it. Build-level dependency direction is `verification -> native core`; it is never `native core -> verification`. Fresh serialization and negative controls must continue to catch stale state or missed publications. Host variant/executable identity checks remain verification gates.

**Startup instead of scenario_fixture:** a normal `main` creates the backend and a single GameWorld, admits/loads the selected resource set, constructs explicit cold game defaults from an independently generated *data* manifest (including retained initial words needed by future reads), obtains the chosen seed reply, and invokes a typed `game_boot`/LifecycleProcess path. That path performs accepted initialization, loads/defaults scores, installs input/calibrates counts, initializes AdLib with mask 1, shows startup pictures and enters menu/session. Runtime game initialization does not inject level number/password, fabricate BIOS/PIT port scripts, construct Regs, push a fake FFF0 return or skip to the attract fixture. Replay CLI options may supply semantic inputs through the same services, not patch game RAM. Typed completion exits through the ordered terminal services and backend cleanup.

## Decisions required before step 8

These are choices for the user, not defaults selected by this plan. Steps5/6 can use existing deterministic resources and event scripts without deciding them. Step7's production admission closure needs D5, and pack extraction/startup errors need D3 before broadening or narrowing their contracts.

| Decision | Options to choose | Constraints that are not choices |
|---|---|---|
| D1 Event scheduling | Keep deterministic virtual retrace/PIT scheduling; or define a live-time mapping/queue policy with catch-up and suspension behavior. | Preserve timer phase/order, exact wait level/edge sequences, synchronous cuts and pause delivery. Do not add game steps from vsync/audio callbacks or turn verification guards into game timeouts. |
| D2 Live joystick units | Synthetic calibrated counts from modern axes; or an emulated/measured 201h count provider. | Calibration and samples use the same wrapping 16-bit units, loop-limit/presence/button contract; native threshold/mapping decisions remain native. Two-player commands stay one shared store. |
| D3 Resources and missing data | Data-only provider derived from the rebuilt image; or extracted portable pack/stable IDs. Choose startup rejection/surfaced resource errors versus optional compatible full-window policy. | Keep mutable reveal metadata, loader read order/partial prefixes,107-byte score encoding/defaults/short read behavior as contracted. Missing-data behavior is not inferred from historical pictures, which have no missing-file path. No full mutable DOS machine. |
| D4 Live seed | Retain fixed/replay time; or live system seconds at the existing single seed point. | Only high byte of RNG word0 is partially reseeded; retain the four-word recurrence and bound-zero advancement. No full timestamp hash or per-level reseed. |
| D5 Compatibility profile | Shipped registered-resource/native domain with explicit Unsupported edges; or fund semantic extensions for selected wider APIs, with a separate literal compatibility verifier where machine frames are intrinsically required. | Review188/32 declines and both pixel opaque services, raw aliases/wrap and optional unreachable SB. No silent bug fixes or broadening of C/D VGA assumptions into an all-state theorem. A full emulated-DOS compatibility target cannot simultaneously satisfy the strict machine-free production definition above. |

Sources: [port-contract.md](port-contract.md), “Decisions for the port layer”; [standalone-plan.md](standalone-plan.md), steps 5-8; the per-cut certificate `interface`, `memory`, `retained`, `uncertainty` fields cited in LEDGER. This plan deliberately chooses none of the five policies.


## Source index

- Named sets and their incomplete/conditional attribution: [program-model.json: variables](../metadata/program-model.json), [original census OWNERS.md](../build/workers/close-adlx-19/OWNERS.md), [original static.json](../build/workers/close-adlx-19/static.json).
- Current resident bindings: [timing_world](../metadata/closure/timing_world.json), [audio_world](../metadata/closure/audio_world.json), [palette_world](../metadata/closure/palette_world.json), [input_world](../metadata/closure/input_world.json), [video_pages](../metadata/closure/video_pages.json), [pixel_world](../metadata/closure/pixel_world.json), each `memory` and `uncertainty`; expanded static bytes are in [audit.json](../build/workers/close-adlx-24/audit.json).
- Observation versus ownership and excluded overlaps: [projector schema](../verif/projector/schema.py), [generated schema](../build/workers/close-adlx-24/schema/schema.json), [projector observer](../verif/projector/observer.c), [test GameWorld layout](../verif/projector/world.h).
- Shared state/continuations: [actor storage](actor-storage.md), [actors.h](../native/actors.h), [front_end.h](../native/front_end.h), [session.h](../native/session.h), [lifecycle.h](../native/lifecycle.h), [level.h](../native/level.h); corresponding certificate `memory/interface/retained` fields.
- Literal-binding debt and source list: [hostbuild.py](../tools/hostbuild.py), [dispatch.c](../c/dispatch.c), [ugh.h](../c/ugh.h), [pixel provider](../verif/pixel_platform_model.inc), [pixel public service header](../native/pixel_world.h).
- Production startup/observation separation: [host main](../host/main.c), [scenario fixture](../host/scenario.c), [digest](../host/digest.c), [terminal_tail interface](../metadata/closure/terminal_tail.json).
- Policy constraints: [standalone plan](standalone-plan.md), [port contract](port-contract.md). No policy is chosen by this audit.

All maintained-source links refer to the pinned revision named at the top, not to pending edits. Its source text is preserved under this worker's `head/` snapshot.
