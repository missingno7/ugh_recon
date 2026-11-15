# Remaining ownership and machine debt

Static audit at committed HEAD `c358a8419574a949b592db23424205062211bfca`. No game, compiler, solver or gate was run for this work order. All new files are under this worker directory. The source snapshot in `head/` comes from `git archive`, so close-stones-22's uncommitted work is excluded. The accepted step-4 receipts are historical evidence, not new results claimed here.

## What is already owned

An owned byte means the composed native host cold-imports it once, seals its RAM lane and serializes the native value into a separate observation view. Merely having a native working projection, a certificate calling a field “owned”, or a test-projector binding is not resident native ownership. Counts are historical observation bytes, not `sizeof` native structs or device plane storage.

| Resident owner / explicit provider state | Bytes |
|---|---|
| audio_world | 4306 |
| timing_world | 306 |
| palette_world | 1536 |
| input_world | 267 |
| video_pages | 20 |
| pixel_world | 4 |
| Total | 6439 |

Sources: `audio_world.memory`, `timing_world.memory`, `palette_world.memory`, `input_world.memory`, `video_pages.memory`, `pixel_world.memory`, and their bridge binding definitions. `audit.json.claims` expands the actual ranges and asserts no duplicate lane. Audio includes the logical clock and saved-vector provider bytes; timing is the remaining timer/lifetime bytes. Four planes, latches, DAC/OPL controls and event phase remain platform service state, outside 6,439.

The model has **392 names: 163 start in these bindings, 229 do not**. This is an exact named-start census, not a byte-size claim for a model symbol or an arbitrary alias theorem. All 392 have `complete=false`; conditional segment and indexed accesses need the source contracts too. Explicit `base+N` and `ds_XXXX` expressions are retained as raw aliases. In particular `ds_2A2D/2ACD/2C6D` map to raw DGROUP displacements and the accepted actor alias views; they do not acquire new scalar meanings.

The remaining 229 names split into 151 planned world/front-end/lifecycle names, 35 pending step-4 names and 43 resource/identity/workspace views. These are alias-bearing model counts, not distinct byte allocations.

The old test projector binds **269/392** model names. That includes many fields still live in RAM: it is observation coverage, not 269 native owners. The other 123 names use baseline/unclassified preservation or an explicit raw view. Each cut must replace its actual bytes with native serialization and require zero moved-owner journal publications. `schema/schema.json` retains the original overlap exclusions; `audit.json` keeps both classifications separately.

## Deferred boundaries that must stay shared

| Storage | Resident location at HEAD | Proposed one owner / borrowers |
|---|---|---|
| Water Y | RAM: fixed Y in current level record +15h; shared pixel Y and previous Y elsewhere | 5A LevelRun state; weather, loader, menus, demo, pixel clipping and passengers borrow it. Do not give weather another persistent Y. |
| PlayerCount, PlayerArrayBytes, both control modes, difficulty | RAM; input_world deliberately borrows them | 5A configuration. Menus, joystick calibration and input IRQ are writers, not owners of copies. Keep count and byte-count independent. |
| Five command words per player | RAM: five two-word arrays beginning D:278C/2790/2794/2798/279C | 5C player store. IRQ byte writes, joystick word clears/classification, loader bulk reset and physics/stone readers share it. Preserve stale high bytes. |
| Player draw caches | RAM: cached X/Y/sprite words, distinct from current simulation pixel coordinates | 5C player history. CachePlayerDrawState, loader seeds and restore consume the same values; never recompute at entry. |
| Actor render histories | RAM: current/prior pixel X/Y and erase main/overlay arrays | 5E persistent history shared across demo/gameplay. Loader, demo and placement seed different subsets; reset does not clear all history. |
| Enemy/item histories | RAM: current/prior draw X/Y and erase-sprite arrays | 5F / 5G. Session draw/erase loops and initializers borrow each family; keep generation order and clipping cuts. |
| Session/run scalars | RAM: score, lives, multiplier, timer, fade, completion, level, unknown D:27C8 | 5A common store; HUD, hazards, items, front end, demo and session are ordered borrowers/writers. Unknown word remains raw. |
| Current level record | RAM: 26 bytes D:28E9..2902 | 5A one record owner with typed subviews, then 6A direct loader. It contains live journey, rain and fixed-water fields, not an immutable second descriptor. |
| HUD/weather exclusive fields | RAM at this HEAD | 4P pending close-stones-22. Transfer only the accepted allocation map once committed; no ownership assumed from its in-progress files. |

## Exact named-cell ledger

The following 229 names are every model cell outside a current native binding. Tables are grouped by proposed cut, not by proven ownership. G = GAME, S = SOUND. W/R begin with the model's exact routine sets; `+` rows add checked enclosing/indirect writers; “None recorded” never proves immutable or unwritten. Additional enclosing and indirect writers are listed below the tables. Addresses are relocated physical observation starts only; they are not production identifiers. `T` means an old test-projector binding; `J` means baseline/unclassified preservation. Neither means resident native ownership.

### 4P: Pending step 4: exclusive HUD, decimal-history and weather storage (not yet accepted at this HEAD)

35 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| CachedTimerBarWidth | 6E936 | J | G:RefreshHudAndTimerBar | G:RefreshHudAndTimerBar |
| DecimalDigit1 | 6C259 | J | None recorded<br>+ Encode*DecimalDigits (indirect output prefix) | G:ShowLevelIntroduction<br>G:TestHighScoreQualification |
| DecimalDigit2 | 6C25A | J | None recorded<br>+ Encode*DecimalDigits (indirect output prefix) | G:TestHighScoreQualification |
| DecimalDigit3 | 6C25B | J | None recorded<br>+ Encode*DecimalDigits (indirect output prefix) | G:TestHighScoreQualification |
| DecimalDigit4 | 6C25C | J | None recorded<br>+ Encode*DecimalDigits (indirect output prefix) | G:TestHighScoreQualification |
| DecimalDigit5 | 6C25D | J | None recorded<br>+ Encode*DecimalDigits (indirect output prefix) | G:TestHighScoreQualification |
| DecimalDigitBuffer | 6C258 | J | None recorded<br>+ Encode*DecimalDigits (indirect output prefix) | G:ShowLevelIntroduction<br>G:TestHighScoreQualification |
| HudCachedFare | 6E956 | J | G:InitializeLevelDisplay<br>G:RefreshHudAndTimerBar | G:RefreshHudAndTimerBar |
| HudCachedLevelCounter | 6E95C | J | G:InitializeLevelDisplay<br>G:RefreshHudAndTimerBar | G:RefreshHudAndTimerBar |
| HudCachedLives | 6E95B | J | G:InitializeLevelDisplay<br>G:RefreshHudAndTimerBar | G:RefreshHudAndTimerBar |
| HudCachedMultiplier | 6E95A | J | G:InitializeLevelDisplay<br>G:RefreshHudAndTimerBar | G:RefreshHudAndTimerBar |
| HudCachedPlayerOneIconState | 6E990 | J | G:LoadCurrentLevelState<br>G:RefreshHudAndTimerBar | G:RefreshHudAndTimerBar |
| HudCachedPlayerTwoIconState | 6E992 | J | G:LoadCurrentLevelState<br>G:RefreshHudAndTimerBar | G:RefreshHudAndTimerBar |
| HudCachedScoreHigh | 6E954 | J | G:InitializeLevelDisplay<br>G:RefreshHudAndTimerBar | G:RefreshHudAndTimerBar |
| HudCachedScoreLow | 6E952 | J | G:InitializeLevelDisplay<br>G:RefreshHudAndTimerBar | G:RefreshHudAndTimerBar |
| HudDigitCursorX | 6E93C | J | G:DrawHudDigitAndAdvance<br>G:RedrawChangedFourDigitNumber<br>G:RedrawChangedSixDigitNumber<br>G:RedrawChangedTwoDigitNumber<br>G:RefreshHudAndTimerBar | G:DrawHudDigit<br>G:DrawHudDigitAndAdvance<br>G:RedrawChangedFourDigitNumber<br>G:RedrawChangedSixDigitNumber<br>G:RedrawChangedTwoDigitNumber |
| HudDigitCursorY | 6E93E | J | G:InitializeLevelDisplay<br>G:RefreshHudAndTimerBar | G:DrawHudDigit |
| HudFareClearPending | 6E95D | J | G:DeliverPassenger<br>G:LoadCurrentLevelState<br>G:RefreshHudAndTimerBar | G:RefreshHudAndTimerBar |
| HudFareX | 6E94A | J | G:InitializeLevelDisplay | G:RefreshHudAndTimerBar |
| HudLevelCounterX | 6E944 | J | G:InitializeLevelDisplay | G:RefreshHudAndTimerBar |
| HudLivesX | 6E940 | J | G:InitializeLevelDisplay | G:RefreshHudAndTimerBar |
| HudMultiplierX | 6E94C | J | G:InitializeLevelDisplay | G:RefreshHudAndTimerBar |
| HudPlayerOneDestinationX | 6E948 | J | G:InitializeLevelDisplay | G:RefreshHudAndTimerBar |
| HudPlayerOneIconX | 6E946 | J | G:InitializeLevelDisplay | G:RefreshHudAndTimerBar |
| HudPlayerTwoDestinationX | 6E950 | J | G:InitializeLevelDisplay | G:RefreshHudAndTimerBar |
| HudPlayerTwoIconX | 6E94E | J | G:InitializeLevelDisplay | G:RefreshHudAndTimerBar |
| HudScoreX | 6E942 | J | G:InitializeLevelDisplay | G:RefreshHudAndTimerBar |
| RainParticleOffsets | 6F01B | T | G:AdvanceRainParticles<br>G:LoadCurrentLevelState<br>G:RespawnRainParticle | G:AdvanceRainParticles<br>G:DrawRainParticles |
| RainParticleXModuloFour | 6F31F | T | G:AdvanceRainParticles<br>G:RespawnRainParticle | G:AdvanceRainParticles<br>G:DrawRainParticles |
| RainPreviousOffsets | 6F19D | T | G:AdvanceRainParticles<br>G:LoadCurrentLevelState | G:RestoreRainBackground |
| WaterRestorePending | 6E932 | T | G:AdvanceWaterSurface | G:AdvanceWaterSurface |
| WaterStepPhase | 6E95E | T | G:AdvanceWaterSurface | G:AdvanceWaterSurface |
| WaterSurfaceByteOffset | 6EA97 | T | G:DrawWaterSurface | G:AdvanceRainParticles |
| WaterSurfaceFrame | 6E934 | T | G:DrawWaterSurface | G:DrawWaterSurface |
| WaterSurfaceFrameCountdown | 6E933 | T | G:DrawWaterSurface | G:DrawWaterSurface |

### 5R: Resource identities, readonly tables and codec workspace (constness and aliases require provider review)

43 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| BasePalettePointer | 6C23B | J | None recorded | G:DuplicateSourcePaletteHalves<br>G:UploadBasePalette |
| CompressedTileMapsPointer | 6C233 | J | None recorded | G:LoadCurrentLevelState<br>G:PrepareAttractMap0<br>G:PrepareAttractMap90 |
| CurrentTileMapPointer | 6C22F | J | None recorded | G:DrawTileMap |
| DecimalHundredDivisor | 6C24E | J | None recorded | G:EncodeFourDecimalDigits |
| DecimalTenDivisor | 6C24D | J | None recorded | G:EncodeTwoDecimalDigits |
| DecimalTenThousandDivisor | 6C251 | J | None recorded | G:EncodeSixDecimalDigits |
| DecimalThousandDivisor | 6C24F | J | None recorded | G:EncodeFourDecimalDigits |
| DecodedImagePointer | 6C22B | J | None recorded | G:UploadChunkyImageToVgaPlanes |
| DemoCompletionScanBiasedBase | 6EBDB | T | None recorded | G:TestAllDemoScriptsFinished |
| DemoRevealWidthPointer | 15ADC | J | None recorded | G:SetDemoRevealSpriteWidth |
| DspProbeIrqOrder | 18798 | J | None recorded | S:ProbeSoundBlasterDmaIrq |
| DspProbeIrqOrderStorage | 18798 | J | None recorded | S:ProbeSoundBlasterDmaIrq |
| FadedPalettePointer | 6C23F | J | None recorded | G:ScaleAndUploadFadedPalette |
| IceDecodeWorkspace | 1A770 | J | None recorded | G:LoadCurrentLevelState<br>G:PrepareAttractMap0<br>G:PrepareAttractMap90 |
| IceMatchLengthBiases | 162BB | J | None recorded | G:DecodeIceLiteralAndMatchStream |
| IceMatchLengthBitCountsMinusOne | 162B6 | J | None recorded | G:DecodeIceLiteralAndMatchStream |
| IceMatchOffsetBiases | 162C5 | J | None recorded | G:DecodeIceLiteralAndMatchStream |
| IceMatchOffsetBitCountsMinusOne | 162C0 | J | None recorded | G:DecodeIceLiteralAndMatchStream |
| IceScratchPointer | 15AE0 | J | None recorded | G:UnpackPictureAndCopyPalette |
| KeyboardHandlerVector | 6C227 | J | None recorded | G:InstallKeyboardSequenceInterrupt |
| LevelCountsByPlayerMode | 6E7B4 | J | None recorded | G:RunGameFromPassword<br>G:RunMainMenuAndAttractLoop |
| LevelOrderTables | 6EA99 | J | None recorded | G:LoadCurrentLevelState |
| LevelWorkspacePointer | 6C247 | J | None recorded | G:InitializeLevelDisplay |
| MultiplierLimitsByDifficulty | 6E7B8 | J | None recorded | G:DeliverPassenger<br>G:ExpireOrCollectFallingItem |
| PaletteSourcePointer | 6C243 | J | None recorded | G:DuplicateSourcePaletteHalves |
| PasswordCompareBiasedBase | 6CCDD | J | None recorded | G:RunGameFromPassword |
| PicturePaletteDestination | 15AC4 | J | None recorded | G:UnpackPictureAndCopyPalette |
| PlayerAnimationCycleEnds | 6CE8C | J | None recorded | G:AnimateAndDrawPlayer |
| PlayerAnimationCycleStarts | 6CE8A | T | None recorded | G:AnimateAndDrawPlayer |
| PlayerImpactLimits | 6E7BE | T | None recorded | G:MovePlayerWithVgaCollisions |
| SpriteDirectoryPointer | 15AD8 | J | None recorded | G:DrawTransparentSprite<br>G:RestoreSpriteBackground |
| SpritePixels0To216Pointer | 15AC8 | J | None recorded | G:DrawTransparentSprite |
| SpritePixels217To297Pointer | 15ACC | J | None recorded | G:DrawTransparentSprite |
| SpritePixels298To546Pointer | 15AD0 | J | None recorded | G:DrawTransparentSprite |
| SpritePixels547AndUpPointer | 15AD4 | J | None recorded | G:DrawTransparentSprite |
| TimerBarDivisor | 6C255 | J | None recorded | G:RefreshHudAndTimerBar |
| TimerBarPointer | 6C237 | J | None recorded | G:RefreshHudAndTimerBar |
| VgaCumulativePlaneMasks | 6E7A8 | J | None recorded | G:RefreshHudAndTimerBar |
| VgaRowStrideBytes | 6C253 | J | None recorded | G:AdvanceWaterSurface<br>G:DrawWaterSurface<br>G:MovePlayerWithVgaCollisions<br>G:RespawnRainParticle |
| VgaSinglePlaneMasks | 6E7A4 | J | None recorded | G:RefreshHudAndTimerBar |
| WaterSurfaceDispatch | 14263 | J | None recorded | G:DrawWaterSurface |
| WaterSurfaceDispatchWords | 14263 | J | None recorded | G:DrawWaterSurface |
| ext_0A67 | 1A770 | J | None recorded | G:LoadCurrentLevelState<br>G:PrepareAttractMap0<br>G:PrepareAttractMap90 |

### 5A: Shared configuration, run scalars and the live level-record nucleus

30 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| CurrentLevelIndex | 6E7AC | T | G:RunGameFromPassword | G:LoadCurrentLevelState<br>G:RunGameFromPassword<br>G:RunMainMenuAndAttractLoop<br>G:ShowLevelIntroduction |
| CurrentLevelRecord | 6EA79 | T | G:LoadCurrentLevelState | None recorded |
| LevelActorList | 6EA7D | T | None recorded<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:LoadCurrentLevelState |
| LevelCompletionMarker | 6E95F | T | G:ReadPassengerJourneyLeg | G:RunGameFromPassword |
| LevelEnemyList | 6EA7F | T | None recorded<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:LoadCurrentLevelState |
| LevelIntroTextPointer | 6EA83 | T | None recorded<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:ShowLevelIntroduction |
| LevelPlatformList | 6EA7B | T | None recorded<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:LoadCurrentLevelState |
| LevelPlayerOneStartX | 6EA86 | J | None recorded<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:LoadCurrentLevelState |
| LevelPlayerOneStartY | 6EA88 | T | None recorded<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:LoadCurrentLevelState |
| LevelPlayerTwoStartX | 6EA8A | T | None recorded<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:LoadCurrentLevelState |
| LevelPlayerTwoStartY | 6EA8C | T | None recorded<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:LoadCurrentLevelState |
| LevelRainDirection | 6EA85 | T | None recorded<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:AdvanceRainParticles<br>G:LoadCurrentLevelState<br>G:MovePlayerWithVgaCollisions<br>G:RespawnRainParticle<br>G:RunGameFromPassword |
| LevelTimer | 6E7B2 | T | G:ExpireOrCollectFallingItem<br>G:InitializeLevelDisplay<br>G:MovePlayerWithVgaCollisions<br>G:RefreshHudAndTimerBar | G:ExpireOrCollectFallingItem<br>G:MovePlayerWithVgaCollisions<br>G:RefreshHudAndTimerBar |
| LivesRemaining | 6E7CC | T | G:ExpireOrCollectFallingItem<br>G:ResetScoreLivesAndMultiplier<br>G:RunGameFromPassword | G:ExpireOrCollectFallingItem<br>G:InitializeLevelDisplay<br>G:RefreshHudAndTimerBar<br>G:RunGameFromPassword |
| PlayerArrayBytes | 6E7C6 | T | G:RunMainMenuAndAttractLoop | G:RunGameFromPassword<br>G:RunMainMenuAndAttractLoop<br>G:ShowLevelIntroduction<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol |
| PlayerCount | 6E7C4 | T | G:RunMainMenuAndAttractLoop | G:DrawHudBorders<br>G:DrawMainMenu<br>G:FindPlayerTouchingActor<br>G:FindPlayerTouchingEnemy<br>G:FindPlayerTouchingFallingItem<br>G:InitializeLevelDisplay<br>G:LaunchBirdTowardPlayer<br>G:LoadCurrentLevelState<br>G:PollPlayerControls<br>G:RefreshHudAndTimerBar<br>G:RunGameFromPassword<br>G:RunMainMenuAndAttractLoop<br>G:UpdateDinoForce<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdatePassengerFloating |
| PlayerOneControlMode | 6E7CF | T | G:DetectAndCalibrateJoysticks<br>G:SelectPlayerControls | G:DrawControlOptions<br>G:HandleKeyboardScanInterrupt<br>G:PollPlayerControls<br>G:SelectPlayerControls |
| PlayerTwoControlMode | 6E7D1 | T | G:DetectAndCalibrateJoysticks<br>+ G:SelectPlayerControls (indexed mode word) | G:DrawControlOptions<br>G:PollPlayerControls |
| PreviousWaterSurfaceY | 6EA95 | T | G:AdvanceWaterSurface<br>G:LoadCurrentLevelState | G:AdvanceWaterSurface |
| RemainingPassengerJourneys | 6EA81 | T | G:ReadPassengerJourneyLeg<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:ReadPassengerJourneyLeg<br>G:RefreshHudAndTimerBar |
| ScoreHighWord | 6E7B0 | T | G:DeliverPassenger<br>G:InsertHighScoreAndClearScore<br>G:RefreshHudAndTimerBar<br>G:ResetScoreLivesAndMultiplier<br>G:StunBirdAndAwardScore<br>G:StunDinoAndAwardScore<br>G:StunTriopterusAndAwardScore | G:DeliverPassenger<br>G:InitializeLevelDisplay<br>G:InsertHighScoreAndClearScore<br>G:RefreshHudAndTimerBar<br>G:StunBirdAndAwardScore<br>G:StunDinoAndAwardScore<br>G:StunTriopterusAndAwardScore |
| ScoreLowWord | 6E7AE | T | G:DeliverPassenger<br>G:InsertHighScoreAndClearScore<br>G:RefreshHudAndTimerBar<br>G:ResetScoreLivesAndMultiplier<br>G:StunBirdAndAwardScore<br>G:StunDinoAndAwardScore<br>G:StunTriopterusAndAwardScore | G:DeliverPassenger<br>G:InitializeLevelDisplay<br>G:InsertHighScoreAndClearScore<br>G:RefreshHudAndTimerBar<br>G:StunBirdAndAwardScore<br>G:StunDinoAndAwardScore<br>G:StunTriopterusAndAwardScore |
| ScoreMultiplier | 6E7CD | T | G:ExpireOrCollectFallingItem<br>G:ResetScoreLivesAndMultiplier<br>G:RunGameFromPassword | G:DeliverPassenger<br>G:ExpireOrCollectFallingItem<br>G:InitializeLevelDisplay<br>G:RefreshHudAndTimerBar |
| ScreenFadeLevel | 6E938 | T | G:MovePlayerWithVgaCollisions<br>G:ReadPassengerJourneyLeg<br>G:RefreshHudAndTimerBar<br>G:RunGameFromPassword<br>G:RunScriptedDemo<br>G:StartDemoFadeWhenSpriteHidden<br>G:UpdateBirdFlight | G:MovePlayerWithVgaCollisions<br>G:ReadPassengerJourneyLeg<br>G:RefreshHudAndTimerBar<br>G:RunGameFromPassword<br>G:RunScriptedDemo<br>G:StartDemoFadeWhenSpriteHidden<br>G:UpdateBirdFlight |
| ScreenFadeStep | 6E93A | T | G:InitializeLevelDisplay<br>G:MovePlayerWithVgaCollisions<br>G:ReadPassengerJourneyLeg<br>G:RefreshHudAndTimerBar<br>G:RunGameFromPassword<br>G:RunScriptedDemo<br>G:StartDemoFadeWhenSpriteHidden<br>G:UpdateBirdFlight | G:MovePlayerWithVgaCollisions<br>G:RefreshHudAndTimerBar<br>G:RunGameFromPassword<br>G:RunScriptedDemo<br>G:UpdateBirdFlight |
| SelectedDifficulty | 6E7C8 | J | G:RunMainMenuAndAttractLoop | G:DeliverPassenger<br>G:DrawMainMenu<br>G:ExpireOrCollectFallingItem<br>G:MovePlayerWithVgaCollisions<br>G:RunMainMenuAndAttractLoop |
| WaterSurfaceStep | 6EA90 | J | None recorded<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:AdvanceWaterSurface |
| WaterY32 | 6EA8E | T | G:AdvanceWaterSurface<br>G:LoadCurrentLevelState<br>+ G:LoadCurrentLevelState (enclosing descending record copy) | G:AdvanceWaterSurface<br>G:LaunchBirdTowardPlayer<br>G:LoadCurrentLevelState |
| WaterYPixels | 6EA93 | T | G:AdvanceWaterSurface<br>G:InsertHighScoreAndClearScore<br>G:LoadCurrentLevelState<br>G:PrepareAttractMap0<br>G:PrepareAttractMap90<br>G:RunMainMenuAndAttractLoop<br>G:SelectPlayerControls<br>G:ShowCreditsPages<br>G:ShowHighScores<br>G:ShowLevelIntroduction | G:AdvanceRainParticles<br>G:AdvanceWaterSurface<br>G:DrawRainParticles<br>G:DrawTransparentSprite<br>G:DrawWaterSurface<br>G:MovePlayerWithVgaCollisions<br>G:PrepareAttractMap0<br>G:PrepareAttractMap90<br>G:RespawnRainParticle<br>G:RestoreRainBackground<br>G:RunScriptedDemo<br>G:ShowLevelIntroduction<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdateFloatingQuestionDisplay<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerFloating<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdatePassengerResurfacing |
| ds_27C8 | 6E958 | J | G:InitializeLevelDisplay | None recorded |

### 5B: Random state and the partial seconds reseed alias

6 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| RandomSecondsSeedByte | 163A8 | T | G:SeedRandomFromDosSeconds | None recorded |
| RandomStateStorage | 163A7 | T | G:NextRandomBelowAx | G:NextRandomBelowAx |
| RandomStateWord0 | 163A7 | T | G:NextRandomBelowAx | G:NextRandomBelowAx |
| RandomStateWord1 | 163A9 | T | G:NextRandomBelowAx | G:NextRandomBelowAx |
| RandomStateWord2 | 163AB | T | G:NextRandomBelowAx | G:NextRandomBelowAx |
| RandomStateWord3 | 163AD | T | G:NextRandomBelowAx | G:NextRandomBelowAx |

### 5C: Both players, commands, motion and draw caches

37 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| PlayerActionInput | 6E92C | T | G:PollPlayerControls<br>+ G:InitializeLevelDisplay (enclosing clear)<br>+ G:HandleKeyboardScanInterrupt (indexed command-byte view) | G:PollPlayerControls<br>G:WaitForStoneRelease |
| PlayerAnimationCountdowns | 6E980 | T | G:AnimateAndDrawPlayer<br>G:LoadCurrentLevelState | G:AnimateAndDrawPlayer |
| PlayerCachedPixelX | 6E970 | T | G:CachePlayerDrawState<br>G:LoadCurrentLevelState | G:RestorePlayerBackground |
| PlayerCachedPixelY | 6E974 | T | G:CachePlayerDrawState<br>G:LoadCurrentLevelState | G:RestorePlayerBackground |
| PlayerCachedSpriteIds | 6E97C | T | G:CachePlayerDrawState | G:RestorePlayerBackground |
| PlayerCarriedKinds | 6E98C | T | G:AttachStoneToPlayer<br>G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:DeliverPassenger<br>G:LoadCurrentLevelState<br>G:ThrowCarriedStone | G:RefreshHudAndTimerBar<br>G:UpdateFloatingPassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerFloating<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdateStonePickupWait |
| PlayerDestinationIcons | 6E994 | T | G:AttachStoneToPlayer<br>G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:DeliverPassenger<br>G:LoadCurrentLevelState<br>G:ThrowCarriedStone | G:RefreshHudAndTimerBar |
| PlayerDownInput | 6E920 | T | G:PollPlayerControls<br>+ G:InitializeLevelDisplay (enclosing clear)<br>+ G:HandleKeyboardScanInterrupt (indexed command-byte view) | G:MovePlayerWithVgaCollisions<br>G:PollPlayerControls |
| PlayerHorizontalVelocities | 6E9A0 | T | G:LoadCurrentLevelState<br>G:MovePlayerWithVgaCollisions<br>G:UpdateDinoForce<br>G:UpdateTriopterusCharge | G:MovePlayerWithVgaCollisions<br>G:ThrowCarriedStone<br>G:UpdateDinoForce |
| PlayerImpactMagnitude | 6E9A8 | T | G:MovePlayerWithVgaCollisions | G:MovePlayerWithVgaCollisions |
| PlayerLeftInput | 6E924 | T | G:PollPlayerControls<br>+ G:InitializeLevelDisplay (enclosing clear)<br>+ G:HandleKeyboardScanInterrupt (indexed command-byte view) | G:MovePlayerWithVgaCollisions<br>G:PollPlayerControls |
| PlayerMinimumFares | 6E99C | T | G:BoardPassenger<br>G:BoardWaterbornePassenger | G:UpdateCarriedPassenger |
| PlayerPassengerFares | 6E998 | T | G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:LoadCurrentLevelState<br>G:UpdateCarriedPassenger | G:DeliverPassenger<br>G:RefreshHudAndTimerBar<br>G:UpdateCarriedPassenger |
| PlayerPixelX | 6E968 | T | G:LoadCurrentLevelState<br>G:MovePlayerWithVgaCollisions | G:AnimateAndDrawPlayer<br>G:CachePlayerDrawState<br>G:MovePlayerWithVgaCollisions<br>G:UpdateFloatingPassengerApproach<br>G:UpdatePassengerApproach |
| PlayerPlatformIndices | 6E988 | T | G:LoadCurrentLevelState<br>G:MovePlayerWithVgaCollisions<br>G:UpdateTriopterusCharge | G:FindPlayerTouchingActor<br>G:MovePlayerWithVgaCollisions<br>G:UpdateCarriedPassenger<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol |
| PlayerRightInput | 6E928 | T | G:PollPlayerControls<br>+ G:InitializeLevelDisplay (enclosing clear)<br>+ G:HandleKeyboardScanInterrupt (indexed command-byte view) | G:MovePlayerWithVgaCollisions<br>G:PollPlayerControls |
| PlayerSpriteIds | 6E978 | T | G:AnimateAndDrawPlayer<br>G:LoadCurrentLevelState | G:AnimateAndDrawPlayer<br>G:CachePlayerDrawState |
| PlayerThrustAnimationRate | 6E984 | T | G:MovePlayerWithVgaCollisions | G:AnimateAndDrawPlayer<br>G:MovePlayerWithVgaCollisions |
| PlayerTwoAnimationCountdown | 6E982 | T | G:LoadCurrentLevelState | None recorded |
| PlayerTwoCachedPixelX | 6E972 | T | G:LoadCurrentLevelState | None recorded |
| PlayerTwoCachedPixelY | 6E976 | T | G:LoadCurrentLevelState | None recorded |
| PlayerTwoDestinationIconIndex | 6E996 | T | G:LoadCurrentLevelState | G:RefreshHudAndTimerBar |
| PlayerTwoFare | 6E99A | T | G:LoadCurrentLevelState | None recorded |
| PlayerTwoFixedX | 6E962 | T | G:LoadCurrentLevelState | None recorded |
| PlayerTwoFixedY | 6E966 | T | G:LoadCurrentLevelState | None recorded |
| PlayerTwoPassengerIconState | 6E98E | T | G:LoadCurrentLevelState | G:RefreshHudAndTimerBar |
| PlayerTwoPixelX | 6E96A | T | G:LoadCurrentLevelState | None recorded |
| PlayerTwoSpriteId | 6E97A | T | G:LoadCurrentLevelState | None recorded |
| PlayerUpInput | 6E91C | T | G:HandleKeyboardScanInterrupt<br>G:PollPlayerControls<br>+ G:InitializeLevelDisplay (enclosing clear) | G:MovePlayerWithVgaCollisions<br>G:PollPlayerControls |
| PlayerVerticalVelocities | 6E9A4 | T | G:LoadCurrentLevelState<br>G:MovePlayerWithVgaCollisions<br>G:UpdateTriopterusCharge | G:MovePlayerWithVgaCollisions<br>G:ThrowCarriedStone<br>G:UpdatePassengerFloating |
| PlayerX32 | 6E960 | T | G:LoadCurrentLevelState<br>G:MovePlayerWithVgaCollisions | G:DeliverPassenger<br>G:FindPlayerTouchingActor<br>G:FindPlayerTouchingEnemy<br>G:FindPlayerTouchingFallingItem<br>G:LaunchBirdTowardPlayer<br>G:MovePlayerWithVgaCollisions<br>G:ThrowCarriedStone<br>G:UpdateDinoForce<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge |
| PlayerY32 | 6E964 | T | G:LoadCurrentLevelState<br>G:MovePlayerWithVgaCollisions<br>G:UpdateTriopterusCharge | G:DeliverPassenger<br>G:FindPlayerTouchingActor<br>G:FindPlayerTouchingEnemy<br>G:FindPlayerTouchingFallingItem<br>G:LaunchBirdTowardPlayer<br>G:MovePlayerWithVgaCollisions<br>G:ThrowCarriedStone<br>G:UpdateDinoForce<br>G:UpdateTriopterusCharge |
| PlayerYPixels | 6E96C | T | G:LoadCurrentLevelState<br>G:MovePlayerWithVgaCollisions | G:AnimateAndDrawPlayer<br>G:CachePlayerDrawState<br>G:MovePlayerWithVgaCollisions<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdatePassengerFloating |
| SecondPlayerYPixels | 6E96E | T | G:LoadCurrentLevelState | G:UpdateFloatingDestinationDisplay |
| ds_27FA | 6E98A | T | G:LoadCurrentLevelState | None recorded |
| ds_2812 | 6E9A2 | T | G:LoadCurrentLevelState | None recorded |
| ds_2816 | 6E9A6 | T | G:LoadCurrentLevelState | None recorded |

### 5D: Platforms and mutable occupancy

8 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| PlatformActorOccupants | 6EB29 | T | G:BeginPassengerResurfacing<br>G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:LoadCurrentLevelState<br>G:PlacePassengerOnPlatform<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay | G:WaitForPassengerPlatform |
| PlatformArrivalPointsX | 6EAD9 | T | G:LoadCurrentLevelState | G:PlacePassengerOnPlatform<br>G:WalkPassengerToExit |
| PlatformDestinationIcons | 6EB15 | T | G:LoadCurrentLevelState | G:BoardPassenger<br>G:BoardWaterbornePassenger |
| PlatformHeights | 6EAC5 | T | G:LoadCurrentLevelState | G:AdvanceFallingItem<br>G:DeliverPassenger<br>G:LoadCurrentLevelState<br>G:MovePlayerWithVgaCollisions<br>G:PlacePassengerOnPlatform<br>G:UpdateThrownStone |
| PlatformLeftEdges | 6EA9D | T | G:LoadCurrentLevelState | G:AdvanceFallingItem<br>G:MovePlayerWithVgaCollisions<br>G:UpdateThrownStone<br>G:UpdateTriopterusPatrol |
| PlatformRightEdges | 6EAB1 | T | G:LoadCurrentLevelState | G:AdvanceFallingItem<br>G:MovePlayerWithVgaCollisions<br>G:UpdateThrownStone<br>G:UpdateTriopterusPatrol |
| PlatformSpawnX | 6EB01 | T | G:LoadCurrentLevelState | G:LoadCurrentLevelState |
| PlatformWaitingPointsX | 6EAED | T | G:LoadCurrentLevelState | G:UpdatePassengerPlatformWait |

### 5E: Shared actor/demo/stone/passenger slots and render histories

24 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| ActorAnimationByteOffsets | 6ED3D | T | G:AnimatePassengerArrival<br>G:AnimatePassengerDeparture<br>G:BeginPassengerApproach<br>G:BeginPassengerDeparture<br>G:BeginPassengerDestinationDisplay<br>G:BeginPassengerFloating<br>G:BeginPassengerPlatformWait<br>G:BeginPassengerQuestionDisplay<br>G:BeginPassengerResurfacing<br>G:BeginPassengerSinking<br>G:BeginStonePickupWait<br>G:DeliverPassenger<br>G:PlacePassengerOnPlatform<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdateFloatingQuestionDisplay<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerFloating<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdatePassengerResurfacing<br>G:UpdatePassengerSinking<br>G:WalkPassengerToExit | G:AnimatePassengerArrival<br>G:AnimatePassengerDeparture<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdateFloatingQuestionDisplay<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerFloating<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdatePassengerResurfacing<br>G:UpdatePassengerSinking<br>G:WalkPassengerToExit |
| ActorAnimationCountdowns | 6ED5D | T | G:AdvanceDemoScripts<br>G:AnimatePassengerArrival<br>G:AnimatePassengerDeparture<br>G:BeginPassengerApproach<br>G:BeginPassengerDeparture<br>G:BeginPassengerDestinationDisplay<br>G:BeginPassengerFloating<br>G:BeginPassengerPlatformWait<br>G:BeginPassengerQuestionDisplay<br>G:BeginPassengerResurfacing<br>G:BeginPassengerSinking<br>G:BeginStonePickupWait<br>G:DeliverPassenger<br>G:InitializeDemoScripts<br>G:PlacePassengerOnPlatform<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdateFloatingQuestionDisplay<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerFloating<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdatePassengerResurfacing<br>G:UpdatePassengerSinking<br>G:WalkPassengerToExit | G:AdvanceDemoScripts<br>G:AnimatePassengerArrival<br>G:AnimatePassengerDeparture<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdateFloatingQuestionDisplay<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerFloating<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdatePassengerResurfacing<br>G:UpdatePassengerSinking<br>G:WalkPassengerToExit |
| ActorDescriptors | 6EB3D | T | G:BoardWaterbornePassenger<br>G:LoadCurrentLevelState<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay | G:AnimatePassengerArrival<br>G:AnimatePassengerDeparture<br>G:AttachStoneToPlayer<br>G:BeginPassengerApproach<br>G:BeginPassengerDeparture<br>G:BeginPassengerDestinationDisplay<br>G:BeginPassengerFloating<br>G:BeginPassengerPlatformWait<br>G:BeginPassengerQuestionDisplay<br>G:BeginPassengerResurfacing<br>G:BeginPassengerSinking<br>G:BeginStonePickupWait<br>G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:DeliverPassenger<br>G:DispatchActorUpdates<br>G:FindThrownStoneHittingEnemy<br>G:PlacePassengerOnPlatform<br>G:ReadPassengerJourneyLeg<br>G:RunGameFromPassword<br>G:ThrowCarriedStone<br>G:UpdateCarriedPassenger<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdateFloatingQuestionDisplay<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerFloating<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdatePassengerResurfacing<br>G:UpdatePassengerSinking<br>G:UpdateStonePickupWait<br>G:UpdateThrownStone<br>G:WaitForPassengerPlatform<br>G:WaitForStoneRelease<br>G:WalkPassengerToExit |
| ActorDestinationPlatformByteIndices | 6EC3D | T | G:ReadPassengerJourneyLeg | G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:DeliverPassenger<br>G:WalkPassengerToExit |
| ActorDestinationPlatforms | 6EBFD | T | G:ReadPassengerJourneyLeg | G:BeginPassengerDestinationDisplay<br>G:UpdateCarriedPassenger |
| ActorEraseOverlaySprite | 6EDDD | T | G:LoadCurrentLevelState<br>G:RunGameFromPassword | G:RunGameFromPassword |
| ActorEraseSprite | 6ED9D | T | G:EraseDemoSprites<br>G:LoadCurrentLevelState<br>G:ResetSpriteEraseState<br>G:RunGameFromPassword | G:EraseDemoSprites<br>G:RunGameFromPassword |
| ActorInitialPlatformIndices | 6EB5D | T | G:LoadCurrentLevelState | G:LoadCurrentLevelState |
| ActorJourneyCursors | 6EB7D | T | G:AnimatePassengerDeparture<br>G:LoadCurrentLevelState | G:AnimatePassengerDeparture<br>G:ReadPassengerJourneyLeg |
| ActorOverlayOrScriptCallbacks | 6EDBD | T | G:BeginPassengerApproach<br>G:BeginPassengerDestinationDisplay<br>G:BeginPassengerPlatformWait<br>G:BeginPassengerQuestionDisplay<br>G:BeginPassengerResurfacing<br>G:BeginPassengerSinking<br>G:InitializeDemoScripts<br>G:LoadCurrentLevelState<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay | G:AdvanceDemoScripts<br>G:RunGameFromPassword |
| ActorPixelX | 6ECBD | T | G:DrawDemoSprites<br>G:InitializeDemoScripts<br>G:PlacePassengerOnPlatform<br>G:RunGameFromPassword | G:DrawDemoSprites<br>G:RunGameFromPassword<br>G:UpdateFloatingPassengerApproach<br>G:UpdatePassengerApproach<br>G:UpdatePassengerPlatformWait<br>G:WalkPassengerToExit |
| ActorPixelY | 6ECFD | T | G:DrawDemoSprites<br>G:InitializeDemoScripts<br>G:PlacePassengerOnPlatform<br>G:RunGameFromPassword | G:DrawDemoSprites<br>G:RunGameFromPassword<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdateFloatingQuestionDisplay<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerFloating<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdatePassengerResurfacing |
| ActorPlatformOrScriptDone | 6EBDD | T | G:AdvanceDemoScripts<br>G:InitializeDemoScripts<br>G:ReadPassengerJourneyLeg | G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay |
| ActorPreviousDrawX | 6ECDD | T | G:DrawDemoSprites<br>G:InitializeDemoScripts<br>G:RunGameFromPassword | G:EraseDemoSprites<br>G:RunGameFromPassword |
| ActorPreviousDrawY | 6ED1D | T | G:DrawDemoSprites<br>G:InitializeDemoScripts<br>G:RunGameFromPassword | G:EraseDemoSprites<br>G:RunGameFromPassword |
| ActorSourcePlatformByteIndices | 6EC1D | T | G:ReadPassengerJourneyLeg | G:BeginPassengerResurfacing<br>G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:PlacePassengerOnPlatform<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:WaitForPassengerPlatform |
| ActorSpriteIds | 6ED7D | T | G:AdvanceDemoScripts<br>G:AnimatePassengerArrival<br>G:AnimatePassengerDeparture<br>G:AnimateTriopterusImpactRecovery<br>G:AnimateTriopterusRecovery<br>G:AttachStoneToPlayer<br>G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:LoadCurrentLevelState<br>G:ReadPassengerJourneyLeg<br>G:ResetSpriteEraseState<br>G:ThrowCarriedStone<br>G:UpdateBirdFlight<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdateFloatingQuestionDisplay<br>G:UpdateFruitTreeAnimation<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerFloating<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdatePassengerResurfacing<br>G:UpdatePassengerSinking<br>G:UpdateStonePickupWait<br>G:UpdateThrownStone<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol<br>G:WaitForPassengerPlatform<br>G:WalkPassengerToExit | G:DrawDemoSprites<br>G:EraseDemoSprites<br>G:RunGameFromPassword<br>G:StartDemoFadeWhenSpriteHidden |
| ActorUpdateOrScriptCursor | 6EB9D | T | G:AdvanceDemoScripts<br>G:AttachStoneToPlayer<br>G:BeginPassengerApproach<br>G:BeginPassengerDeparture<br>G:BeginPassengerDestinationDisplay<br>G:BeginPassengerFloating<br>G:BeginPassengerPlatformWait<br>G:BeginPassengerQuestionDisplay<br>G:BeginPassengerResurfacing<br>G:BeginPassengerSinking<br>G:BeginStonePickupWait<br>G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:DeliverPassenger<br>G:InitializeDemoScripts<br>G:LoadCurrentLevelState<br>G:PlacePassengerOnPlatform<br>G:ReadPassengerJourneyLeg<br>G:ThrowCarriedStone<br>G:UpdatePassengerSinking<br>G:UpdateThrownStone | G:AdvanceDemoScripts<br>G:DispatchActorUpdates<br>G:DrawDemoSprites<br>G:EraseDemoSprites<br>G:FindThrownStoneHittingEnemy<br>G:TestAllDemoScriptsFinished |
| ActorX32 | 6EC7D | T | G:AdvanceDemoScripts<br>G:DeliverPassenger<br>G:InitializeDemoScripts<br>G:LoadCurrentLevelState<br>G:PlacePassengerOnPlatform<br>G:PlaySpriteRevealDemo<br>G:ThrowCarriedStone<br>G:UpdateFloatingPassengerApproach<br>G:UpdatePassengerApproach<br>G:UpdatePassengerPlatformWait<br>G:UpdateThrownStone<br>G:WalkPassengerToExit | G:AdvanceDemoScripts<br>G:DrawDemoSprites<br>G:FindPlayerTouchingActor<br>G:FindThrownStoneHittingEnemy<br>G:ReleaseTreeReward<br>G:RunGameFromPassword<br>G:SetDemoRevealSpriteWidth<br>G:UpdateFloatingPassengerApproach<br>G:UpdatePassengerApproach<br>G:UpdatePassengerPlatformWait<br>G:UpdateThrownStone<br>G:WalkPassengerToExit |
| ActorY32 | 6EC9D | T | G:AdvanceDemoScripts<br>G:DeliverPassenger<br>G:InitializeDemoScripts<br>G:LoadCurrentLevelState<br>G:PlacePassengerOnPlatform<br>G:ThrowCarriedStone<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingPassengerApproach<br>G:UpdateFloatingQuestionDisplay<br>G:UpdatePassengerApproach<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerFloating<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:UpdatePassengerResurfacing<br>G:UpdatePassengerSinking<br>G:UpdateThrownStone | G:AdvanceDemoScripts<br>G:DrawDemoSprites<br>G:FindPlayerTouchingActor<br>G:FindThrownStoneHittingEnemy<br>G:ReleaseTreeReward<br>G:RunGameFromPassword<br>G:UpdatePassengerResurfacing<br>G:UpdatePassengerSinking<br>G:UpdateThrownStone |
| PassengerQuickDeliveryCountdowns | 6EE1D | T | G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:UpdateCarriedPassenger | G:DeliverPassenger<br>G:UpdateCarriedPassenger |
| ds_2A2D | 6EBBD | J | G:AdvanceDemoScripts<br>G:AttachStoneToPlayer<br>G:BeginPassengerDestinationDisplay<br>G:BeginPassengerPlatformWait<br>G:BeginPassengerQuestionDisplay<br>G:BoardPassenger<br>G:BoardWaterbornePassenger<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingQuestionDisplay<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay | G:AdvanceDemoScripts<br>G:DeliverPassenger<br>G:UpdateCarriedPassenger<br>G:UpdateFloatingDestinationDisplay<br>G:UpdateFloatingQuestionDisplay<br>G:UpdatePassengerDestinationDisplay<br>G:UpdatePassengerPlatformWait<br>G:UpdatePassengerQuestionDisplay<br>G:WaitForStoneRelease |
| ds_2ACD | 6EC5D | J | G:AdvanceDemoScripts<br>G:BeginPassengerFloating<br>G:InitializeDemoScripts<br>G:ReadPassengerJourneyLeg<br>G:ThrowCarriedStone<br>G:UpdatePassengerFloating<br>G:WaitForPassengerPlatform | G:AdvanceDemoScripts<br>G:ReleaseTreeReward<br>G:UpdatePassengerFloating<br>G:UpdateThrownStone<br>G:WaitForPassengerPlatform |
| ds_2C6D | 6EDFD | J | G:AnimateTriopterusImpactRecovery<br>G:AnimateTriopterusRecovery<br>G:BeginPassengerResurfacing<br>G:BeginPassengerSinking<br>G:InitializeDemoScripts<br>G:ThrowCarriedStone<br>G:UpdateBirdFlight<br>G:UpdateDinoForce<br>G:UpdateFruitTreeAnimation<br>G:UpdatePassengerResurfacing<br>G:UpdatePassengerSinking<br>G:UpdateThrownStone<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol | G:AdvanceDemoScripts<br>G:AnimateTriopterusImpactRecovery<br>G:AnimateTriopterusRecovery<br>G:FindThrownStoneHittingEnemy<br>G:ReleaseTreeReward<br>G:UpdateBirdFlight<br>G:UpdateDinoForce<br>G:UpdateFruitTreeAnimation<br>G:UpdatePassengerResurfacing<br>G:UpdatePassengerSinking<br>G:UpdateThrownStone<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol |

### 5F: Enemy/hazard slots and render histories

19 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| EnemyAnimationByteOffsets | 6EEBF | T | G:AnimateTriopterusImpactRecovery<br>G:AnimateTriopterusRecovery<br>G:BeginBirdDelay<br>G:BeginTriopterusAlert<br>G:BeginTriopterusCharge<br>G:BeginTriopterusImpactRecovery<br>G:BeginTriopterusPatrol<br>G:BeginTriopterusRecovery<br>G:InitializeDinoAnimation<br>G:InitializeFruitTreeAnimation<br>G:StunTriopterusAndAwardScore<br>G:UpdateBirdFlight<br>G:UpdateDinoForce<br>G:UpdateFruitTreeAnimation<br>G:UpdateStunnedTriopterus<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol | G:AnimateTriopterusImpactRecovery<br>G:AnimateTriopterusRecovery<br>G:UpdateBirdFlight<br>G:UpdateDinoForce<br>G:UpdateFruitTreeAnimation<br>G:UpdateStunnedTriopterus<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol |
| EnemyAnimationCountdowns | 6EEC9 | T | G:AnimateTriopterusImpactRecovery<br>G:AnimateTriopterusRecovery<br>G:BeginBirdDelay<br>G:BeginTriopterusAlert<br>G:BeginTriopterusCharge<br>G:BeginTriopterusImpactRecovery<br>G:BeginTriopterusPatrol<br>G:BeginTriopterusRecovery<br>G:InitializeDinoAnimation<br>G:InitializeFruitTreeAnimation<br>G:StunTriopterusAndAwardScore<br>G:UpdateBirdFlight<br>G:UpdateDinoForce<br>G:UpdateFruitTreeAnimation<br>G:UpdateStunnedTriopterus<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol | G:AnimateTriopterusImpactRecovery<br>G:AnimateTriopterusRecovery<br>G:UpdateBirdFlight<br>G:UpdateDinoForce<br>G:UpdateFruitTreeAnimation<br>G:UpdateStunnedTriopterus<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol |
| EnemyAnimationOrDropLists | 6EE65 | T | G:LaunchBirdTowardPlayer<br>G:LoadCurrentLevelState<br>G:ReleaseTreeReward | G:AdvanceTreeRewardCooldown<br>G:ReleaseTreeReward<br>G:UpdateBirdFlight |
| EnemyDescriptors | 6EE3D | T | G:LoadCurrentLevelState | G:AdvanceTreeRewardCooldown<br>G:AnimateTriopterusImpactRecovery<br>G:AnimateTriopterusRecovery<br>G:BeginBirdDelay<br>G:BeginBirdWarning<br>G:BeginTriopterusPatrol<br>G:DispatchEnemyStates<br>G:InitializeDinoAnimation<br>G:InitializeFruitTreeAnimation<br>G:LaunchBirdTowardPlayer<br>G:RunGameFromPassword<br>G:UpdateBirdFlight<br>G:UpdateDinoForce<br>G:UpdateFruitTreeAnimation<br>G:UpdateStunnedBird<br>G:UpdateStunnedDino<br>G:UpdateStunnedTriopterus<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol<br>G:WaitForBirdFlight<br>G:WaitForBirdWarning |
| EnemyDirectionOrTargetPlayer | 6EEE7 | T | G:LaunchBirdTowardPlayer<br>G:LoadCurrentLevelState<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol | G:AnimateTriopterusImpactRecovery<br>G:AnimateTriopterusRecovery<br>G:LaunchBirdTowardPlayer<br>G:UpdateBirdFlight<br>G:UpdateStunnedTriopterus<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol |
| EnemyDrawX | 6EE97 | T | G:InitializeFruitTreeAnimation<br>G:RunGameFromPassword | G:RunGameFromPassword |
| EnemyDrawY | 6EEAB | T | G:InitializeFruitTreeAnimation<br>G:RunGameFromPassword | G:RunGameFromPassword |
| EnemyEraseSprite | 6EEDD | T | G:ResetSpriteEraseState<br>G:RunGameFromPassword | G:RunGameFromPassword |
| EnemyFlightSoundHandles | 6EEF1 | T | G:LaunchBirdTowardPlayer | G:StopBirdFlightSound |
| EnemyHorizontalSpeeds | 6EE79 | T | G:LaunchBirdTowardPlayer<br>G:LoadCurrentLevelState<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol | G:LaunchBirdTowardPlayer<br>G:StunBirdAndAwardScore<br>G:UpdateBirdFlight<br>G:UpdateStunnedBird<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol |
| EnemyInitialDelays | 6EE6F | T | G:LoadCurrentLevelState | G:BeginBirdDelay |
| EnemyPlatformIndices | 6EE47 | T | G:LoadCurrentLevelState | G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol |
| EnemyPreviousDrawX | 6EEA1 | T | G:RunGameFromPassword | G:RunGameFromPassword |
| EnemyPreviousDrawY | 6EEB5 | T | G:RunGameFromPassword | G:RunGameFromPassword |
| EnemySpriteIds | 6EED3 | T | G:AnimateTriopterusImpactRecovery<br>G:AnimateTriopterusRecovery<br>G:BeginBirdDelay<br>G:ReleaseTreeReward<br>G:ResetSpriteEraseState<br>G:StunBirdAndAwardScore<br>G:StunDinoAndAwardScore<br>G:UpdateBirdFlight<br>G:UpdateDinoForce<br>G:UpdateFruitTreeAnimation<br>G:UpdateStunnedTriopterus<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol | G:RunGameFromPassword |
| EnemyStateCallbacks | 6EE83 | T | G:AdvanceTreeRewardCooldown<br>G:BeginBirdDelay<br>G:BeginBirdWarning<br>G:BeginTriopterusAlert<br>G:BeginTriopterusCharge<br>G:BeginTriopterusImpactRecovery<br>G:BeginTriopterusPatrol<br>G:BeginTriopterusRecovery<br>G:InitializeDinoAnimation<br>G:InitializeFruitTreeAnimation<br>G:LaunchBirdTowardPlayer<br>G:LoadCurrentLevelState<br>G:ReleaseTreeReward<br>G:StunBirdAndAwardScore<br>G:StunDinoAndAwardScore<br>G:StunTriopterusAndAwardScore | G:DispatchEnemyStates |
| EnemyStateCounters | 6EE8D | T | G:AdvanceTreeRewardCooldown<br>G:BeginBirdDelay<br>G:BeginBirdWarning<br>G:BeginTriopterusAlert<br>G:BeginTriopterusCharge<br>G:ReleaseTreeReward<br>G:StunBirdAndAwardScore<br>G:StunDinoAndAwardScore<br>G:StunTriopterusAndAwardScore<br>G:UpdateStunnedBird<br>G:UpdateStunnedDino<br>G:UpdateStunnedTriopterus<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:WaitForBirdFlight<br>G:WaitForBirdWarning | G:AdvanceTreeRewardCooldown<br>G:UpdateStunnedBird<br>G:UpdateStunnedDino<br>G:UpdateStunnedTriopterus<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:WaitForBirdFlight<br>G:WaitForBirdWarning |
| EnemyX32 | 6EE51 | T | G:LaunchBirdTowardPlayer<br>G:LoadCurrentLevelState<br>G:UpdateBirdFlight<br>G:UpdateStunnedBird<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol | G:FindPlayerTouchingEnemy<br>G:FindThrownStoneHittingEnemy<br>G:InitializeFruitTreeAnimation<br>G:RunGameFromPassword<br>G:UpdateBirdFlight<br>G:UpdateDinoForce<br>G:UpdateStunnedBird<br>G:UpdateTriopterusAlert<br>G:UpdateTriopterusCharge<br>G:UpdateTriopterusPatrol |
| EnemyY32 | 6EE5B | T | G:LaunchBirdTowardPlayer<br>G:LoadCurrentLevelState<br>G:UpdateStunnedBird | G:FindPlayerTouchingEnemy<br>G:FindThrownStoneHittingEnemy<br>G:InitializeFruitTreeAnimation<br>G:RunGameFromPassword<br>G:UpdateDinoForce<br>G:UpdateStunnedBird |

### 5G: Falling items and render histories

12 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| FallingItemCallbacks | 6EF13 | T | G:LandFallingItem<br>G:SpawnFallingItem | G:DispatchFallingItems |
| FallingItemDescriptors | 6EEFB | T | G:SpawnFallingItem | G:AdvanceFallingItem<br>G:ExpireOrCollectFallingItem<br>G:LandFallingItem |
| FallingItemDrawX | 6EF8B | T | G:RunGameFromPassword | G:RunGameFromPassword |
| FallingItemDrawY | 6EFBB | T | G:RunGameFromPassword | G:RunGameFromPassword |
| FallingItemEraseSprite | 6EF43 | T | G:ResetSpriteEraseState<br>G:RunGameFromPassword | G:RunGameFromPassword |
| FallingItemMotionOrLifetime | 6EFEB | T | G:ExpireOrCollectFallingItem<br>G:LandFallingItem<br>G:SpawnFallingItem | G:AdvanceFallingItem<br>G:ExpireOrCollectFallingItem |
| FallingItemPreviousDrawX | 6EFA3 | T | G:RunGameFromPassword | G:RunGameFromPassword |
| FallingItemPreviousDrawY | 6EFD3 | T | G:RunGameFromPassword | G:RunGameFromPassword |
| FallingItemSprites | 6EF2B | T | G:AdvanceFallingItem<br>G:ExpireOrCollectFallingItem<br>G:ResetSpriteEraseState<br>G:SpawnFallingItem | G:DispatchFallingItems<br>G:RunGameFromPassword<br>G:SpawnFallingItem |
| FallingItemVerticalStep | 6F003 | T | G:AdvanceFallingItem<br>G:SpawnFallingItem | G:AdvanceFallingItem |
| FallingItemX | 6EF5B | T | G:AdvanceFallingItem<br>G:SpawnFallingItem | G:AdvanceFallingItem<br>G:FindPlayerTouchingFallingItem<br>G:RunGameFromPassword |
| FallingItemY | 6EF73 | T | G:AdvanceFallingItem<br>G:SpawnFallingItem | G:AdvanceFallingItem<br>G:FindPlayerTouchingFallingItem<br>G:RunGameFromPassword |

### 6A: Session/demo continuation and loader arithmetic scratch

2 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| CoordinateScaleScratch | 6E7D8 | J | G:ScaleLevelSpeedToThreeHalves<br>G:ScaleLevelYToThreeQuarters | G:ScaleLevelSpeedToThreeHalves<br>G:ScaleLevelYToThreeQuarters |
| DemoExitCode | 6E7DA | J | G:RunScriptedDemo | G:RunScriptedDemo |

### 6B: Front-end table, editors and mutable text

12 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| HighScoreFileHandle | 6C24B | T | G:LoadHighScores<br>G:SaveHighScores | G:LoadHighScores<br>G:SaveHighScores |
| HighScoreNameChars2To3 | 6CDFF | T | G:InsertHighScoreAndClearScore | None recorded |
| HighScoreNameChars4To5 | 6CE01 | T | G:InsertHighScoreAndClearScore | None recorded |
| HighScoreNameChars6To7 | 6CE03 | T | G:InsertHighScoreAndClearScore | None recorded |
| HighScoreNameChars8To9 | 6CE05 | T | G:InsertHighScoreAndClearScore | None recorded |
| HighScoreNameEntry | 6CDFD | T | G:InsertHighScoreAndClearScore | G:InsertHighScoreAndClearScore |
| HighScoreRowStride | 6C257 | T | None recorded | G:GetHighScoreDigits<br>G:GetHighScoreRow |
| HighScoreRows | 6CE16 | T | G:ComplementHighScoreTable<br>+ G:LoadHighScores (file-service read) | G:ComplementHighScoreTable |
| LevelNumberTensCharacter | 6CD8D | J | G:ShowLevelIntroduction | None recorded |
| LevelNumberUnitsCharacter | 6CD8E | J | G:ShowLevelIntroduction | None recorded |
| PasswordEditBuffer | 6CCDE | T | G:EditLevelPassword | G:RunGameFromPassword |
| PasswordEditChars2To3 | 6CCE0 | T | G:EditLevelPassword | None recorded |

### 6C: Lifecycle saved mode / terminal state

1 model names.

| Cell / raw alias | Observation start | Projector | Writers | Readers |
|---|---|---|---|---|
| SavedBiosVideoMode | 6C222 | J | G:InitializeDosVideoInputAndSound | G:InitializeDosVideoInputAndSound<br>G:RunDosGame<br>G:ShowStartupPictures |

## Enclosing writes, omitted cells and alias checks

The 392-cell model is not an exhaustive allocation manifest. These nonlocal effects must accompany the tables, even when a model row records no writer:

1. **Live 26-byte record.** `session_bridge.c:c_LoadCurrentLevelState` copies thirteen words **descending +24,+22,...,+0**. Record fields: +0 map, +2 platform list, +4 actor list, +6 enemy list, +8 journey byte, +9 reserved, +Ah intro text, +Ch rain byte, +Dh/+Fh/+11h/+13h player starts, +15h fixed water Y, +17h step, +19h reserved. The loader writes every subfield, including rows with no direct writer. `ReadPassengerJourneyLeg` changes +8; weather changes +15h; neither is a second record. Preserve odd/straddling word lanes and both reserved bytes. `LevelDescription.raw` is immutable source evidence, not another mutable runtime record. Sources: `native/level.h`, `session_bridge.c:load`, `water_weather.memory`.
2. **392-byte reset transaction.** `InitializeLevelDisplay` clears 196 words through LevelWorkspacePointer. The rebuilt resource binding is DGROUP:2648, so normal DF=0 touches D:2648..27CF and stops immediately before PlayerX32 at 27D0. It spans a four-byte prefix, the 320-byte tile map at 264C..278B, all twenty command bytes at 278C..279F, HUD/numeric scratch and D:27C8. It is not a licence to zero complete player records. Use an ordered multi-owner reset service, including the live DF/alias compatibility domain. `PrepareAttractMap0/90` also copy 160 words to Data_264C after decoding and consume the then-live DF. Sources: session_bridge.c / menus.memory.map; existing rebuilt image SHA256 2741638a508233a8d14a2a7bad5a4355eb527e4607b6509caec428582035cd4d (read only).
3. **Input commands are byte aliases.** `input_bridge.c` IRQ `INPUT_KEY_WRITE_ACTION` writes a byte through PlayerUpInput+position, while PollPlayerControls writes/clears words and the level reset clears their window. The other half of each word must survive byte writes. Calibration and controls menu both write mode words. This is why these cells remain outside NativeInputWorld.
4. **Second-player labels are aliases.** E.g. PlayerTwoFixedX is PlayerX32+2; ds_27FA is PlayerPlatformIndices+2; ds_2812/2816 are second velocity words. Preserve each physical byte once, not once per name. Player storage is not one contiguous independently owned block: D:2800..2803 are HudCachedPlayerOneIconState/HudCachedPlayerTwoIconState between carried-kind and destination arrays, and belong to the pending HUD owner. The player animation limits are the overlapping readonly start/end boundary table at D:0CFA/0CFC: start[1] and end[0] are the same word. The old projector intentionally leaves that overlapping word unclassified. Do not allocate two independent two-element arrays; expose a shared resource view and preserve its three physical words for the two ordinary indices.
5. **Actor aliases and history.** Actor physical store is 24 word arrays x16 slots, D:29AD..2CAC. ds_2A2D is phase/wait/carrier/demo-loop, ds_2ACD is journey wait/throw step/floating lifetime/demo repeat, and ds_2C6D is vertical motion/demo period. These names describe shared cells, not separately live values. Hazards borrow the selected stone's vertical cell; model conditional addressing does not prove every hazard field aliases it. Preserve unused values/history across mode transitions; one callback word is a game phase or a demo cursor according to mode. Source: `docs/actor-storage.md`, `actor_resources`, `actor_pass`.
6. **Sentinels and spill lanes.** Platforms: ten-word arrays; actors: sixteen-word arrays; enemy arrays: five words; items: twelve words. Capacity is not a theorem that every scan terminates in bounds. Current native actor admission needs an in-array sentinel (at most 15 active); an all-five enemy list would make its descriptor sentinel reach the next physical array head. Preserve/explicitly admit or reject these cases, never invent an extra independent sentinel allocation. Indexed/raw windows and declarations remain part of the router audit.
7. **Rain boundary pending.** Slots 0..192 are 193 words per array; the post-test slot 193 accesses the next array head. The modulo spill at D:3311 is already input-owned. The forthcoming 4P allocation map must route those aliases, not add a 194th unrelated particle. Loader clears 193 current/prior words but leaves dry modulo cells stale; wet load respawns 193 and performs 577 prewarm calls. This is pending, not credited as new ownership. Source: pixel_world.uncertainty and close-stones-21 REPORT's recorded boundary.
8. **Codec and mutable resources.** ICE's seeded 64-KiB workspace overlaps audio facade flags at +FD00..FD03; it already borrows moved bytes through the owner router and publishes only actual decoder writes. A portable workspace must not become a second RAM image or overwrite live borrowed flags. Sprite reveal mutates one width byte behind DemoRevealWidthPointer; that metadata is writable. DecimalDigitBuffer and current/prior HUD windows have implicit Encode* writers absent from the model. 4P must publish its full allocation map. HighScoreRows has file-read and complement/shift/insertion writers; score fields and name aliases share their existing storage. Indexed menu copy has no size bound and copies no NUL; arbitrary output aliases remain profile debt. Sources: audio_world.memory.shared_views, demo_presentation.memory, high_scores.memory, menus.memory.text, decimal.interface.
9. **Reached foreign shutdown view.** The audio facade shutdown writes1 through live DS at the C shutdown offset after timer removal; this reaches DGROUP:0002, not the native C flag. It is an unmodelled two-byte view, not a second audio owner. Preserve the known reached terminal observation. Before eliminating it from production, prove within the production admitted domain whether any later game read depends on it; otherwise represent it only as a verifier effect associated with that shutdown cut. Do not invent a game role or quietly omit the terminal write. Source: audio_world.memory.shared_views and its compiled shutdown-alias cases.
10. **Other unmodelled storage.** Keep an explicit allocation/write inventory for Data_264C, HUD digit histories, raw codec windows, text scratch/string output and descriptor/animation streams. Front-end edit/layout cursors and LifecycleProcess/SessionProcess/MenusMain are currently native automatic working continuations, not additional named RAM cells. They must be carried directly by the composed control flow. No 392-name checklist can replace a scan of baseline/journal writes after each cut.

## Step 7 debt ledger

Decision tags: D1 event scheduling; D2 live joystick units; D3 resource pack/missing data; D4 live random seed; D5 optional bit-exact compatibility profile. “Automatic” below means removable after replacement callers and proofs land, not safe to delete today.

| Debt | Current implementation / evidence | Retirement and decision |
|---|---|---|
| Verification entry ABI | 278 exported native c_* entries across the 51 bridge .c units; 49 bridge .c files spell Regs. Near/far frames, flags, CS/DS/ES, DF and post-callback cursor/register rereads survive even for direct native peers. The two files without Regs still borrow raw segments/resources. | Ordinary call scaffolding disappears with each bridge, after typed requests/replies replace every *live* value. Keep observer-only return identities in test adapters. Audit the reached foreign DGROUP:0002 audio-shutdown effect separately before classifying it as observer-only; it is not the native C flag. Retained wrapping, direction and alias semantics are not dead ABI. D5 applies to arbitrary foreign frames; ordinary direct composition needs no live-policy choice. |
| Pixel opaque continuation | pixel_service_continuation(kind, {first,second}, return_identity, PixelServiceContext*) casts context to Regs in verif/pixel_platform_model.inc, then performs ugh_call_near / ugh_dispatch for noncanonical CS or unknown tail. | Needs reviewed domain decision D5. Replace admitted known roles directly; unsupported foreign/unknown frames fail closed at the same effect prefix. Keep broad literal ABI only in a separate compatibility verifier. Never call it “just a port callback”. |
| Pixel opaque control | pixel_service_compatibility_write({identity}, width, value) forwards arbitrary original control binding to platform_out; direct water-frame APIs admit nonpixel/DAC/unsupported controls. | D5: explicit finite semantic control extensions, or explicit production rejection. Not automatically satisfied by indexed-pixel stores or a default GC state. Test the three continuation and six control-frame cases already recorded by pixel_world. |
| Other opaque service contexts | InputServiceContext / VideoServiceContext / PixelServiceContext hide ABI continuations in current providers; timer/audio vector bindings and terminal/DOS replies still carry machine details. | Ordinary contexts become native service continuations/statuses when their bridges retire. Preserve synchronous/error-prefix and service-cut behavior. D1 for live delivery, D5 for foreign stack/frame compatibility. An incomplete struct declaration alone is not retirement. |
| Compatibility declarations in ordinary headers | pixel_world.h declares both opaque compatibility services; input_world.h/video_pages.h also expose verification continuation contexts. These survive removal of bridge objects unless split or replaced. | Move verification-only declarations to test headers; production uses semantic service headers. Dead declarations do not justify machine-shaped context types. D5 for chosen wider behavior, otherwise mechanical header separation. |
| Audio/timer provider coordinates | TimingBinding.address/member registry, at[], open_words[32], previous[2], audio external_words[4], bank-word window mapping and native peer code-bank admission. Known token roles and unknown half-word splicing stay distinguishable. | Historical coordinates/word encodings belong only to the test serializer/provider. Production uses resource handles and callback enums with direct typed calls; retain semantic timer removal/phase quirks. Ordinary mapping removal automatic after typed callers; D5 for open fragments/foreign banks; D1 for live phase delivery. |
| Input/page/resource provider coordinates | InputKeyboardBinding first/second, current KeyboardHandlerVector, VideoBankIdentity and far-resource windows. Present providers translate to DOS vectors, bank words and pixel physical addresses. | Use provider-owned installation tokens, typed surface/resource identities and word positions. Do not do segment<<4 arithmetic in production game code. D2 controls live counts, D3 stable resource IDs/admission, D5 broader aliases, D1 input/retrace cuts. |
| Explicit API declines | audio_world:188 runs =94 fixtures x2 poison modes; timing_world:32 =16x2. Static comparison of accepted receipts finds **all 32 included in 188**, so do not add them to 220. Original profile used L1; composed profile returns 1, never falls back. | D5 must approve a production admitted domain or commission specific semantic extensions. Keep exact rejection list/status/error prefix as tests. Timer malformed slots/handles, resource/stack/DF/alias states are not all format errors. Production has an explicit Unsupported result, no hidden L1 escape. |
| Dormant fallback expressions | Static maintained bridge census:104 executable source-line expressions in 15 bridges (including AUDIO_LITERAL wrappers); prototypes excluded. Some are preprocessor-elided under composition. Last accepted pixel census records 121 generated fallback sites, zero taken over 21 runs; generated sites include legacy copies and are a different count. | After each bridge retires its references disappear, but the production admission/rejection policy must be explicit first (D5, sometimes D3). Zero observed is not an all-state never-taken proof. Kill every remaining symbol reference and test failure prefixes, including matches that previously relied on L1. |
| Four external hooks | c_loc_001C..001F are the only unreplaced game entries in the accepted census. They remain lone near RETs; broken far-call/near-RET transfers are explicit compatibility boundaries. | No invented game meaning or repaired return. Ordinary AdLib startup does not need them. Exclude hooks and fail closed on the unreachable digital/bank request; preserve broken-transfer tests only in compatibility verification (D5). |
| Reached foreign shutdown store | adlx_facade writes the live-DS C-shutdown-offset view, DGROUP:0002 after timer removal, while canonical C shutdown stays native. This is separate from the unreachable SB hooks. | Needs a reader/dependence audit before observer-only elimination. Keep its reached terminal effect in verification; if any admitted game read survives, add an explicit typed shared view, not a second AudioState field. No fabricated semantic role. D5 only for narrowing broader aliases, not permission to ignore the reached observation. |
| Digital/SB | Native policies exist, but startup requests 1, no sample resource ships/bank hooks are stubs, and DSP probe far CALL returns via near RET. Host has no SB output. | Ordinary production need not expose SB; reject optional requests explicitly. D5 if supporting digital API compatibility; it is not a reason to retain DOS dispatch in the shipped target. Preserve641=258fresh+383stale API evidence separately. |
| c/ translation units | hostbuild still links every one of 27 c/*.c, including all dormant L1 bodies; c/memory.c and generated c/platform.c provide the current machine and service backends. ugh.h inlines helpers in bridges. | Game bodies drop with adapters/fallback links. Hardware, IRQ/queue, file and observation services need actual replacement implementations before dispatch/memory/platform can drop. D1/D2/D3/D4/D5 apply to the respective live backend services; removal itself needs positive source/link manifests. |
| Resolver and dispatch table | c/dispatch.c ugh_resolve scans {segment,offset,adapter}; ugh_dispatch mutates/restores CS; near/far/interrupt/hook helpers encode frames and IRET. Actor/audio/pixel peer “direct calls” still enter c_* adapters. | Convert remaining state/callback references to closed typed identities and direct semantic signatures (steps 5/6). Delete resolver from production, not just its observed targets. D5 for unknown callback/frame requests; otherwise mechanical once peers are native. |
| Terminal reply liveness | terminal_tail.interface.widths consumes live AL after input restore; restore currently replaces AX with the queue-flush tail word. Saved mode is read unmasked after sound. | Carry explicit saved-mode and terminal-code replies across semantic services before removing Regs. Do not substitute a generic success code or use a pre-sound snapshot. D5 only if intentionally changing externally visible compatibility, otherwise direct semantic preservation. |
| Host observation hooks | host/main.c loads relocated MZ RAM, calls scenario_fixture and all cold imports, fabricates Regs/stack, then dispatches entry. host/digest.c hashes project_timing_observation, raw Devices/log and stack-return scalar. verif/projector contains historical layout, identities, journal and publication hooks. | All stay in the verification executable only. Production must not link them or cold-import a mutable RAM image. Replace with typed boot/default constructors and live services (PLAN). D3/D4/D1/D2 determine live inputs; observation removal needs no arbitrary change to game decisions. |
| Host SDL presenters are not independent ports yet | host/video.c reads device planes/controls; host/audio.c reads ugh_devices.opl_index; host/input.c and main/scenario services use BIOS/vector/port-shaped storage. Windows CNG/watchdog/file helpers are also coupled. | Refactor reusable SDL/OPL parts behind GameServices; do not link current host/*.c wholesale into production. D1 timing, D2 joystick, D3 files/resources, D4 seed. Optional compatibility device state must not reintroduce the banned machine (D5). |
| Generated composition hooks | tools/hostbuild.py rewrites memory byte access and far_copy/decimal/ICE sources, then appends service providers from verif/*platform_model.inc to a generated c/platform.c. | Make needed semantic services real production implementations; omit rewrites/machine hooks from production. Keep generation only for verification. D3/D5 for raw borrowed-window edge policy. |

### Per-bridge ABI / fallback inventory

Lexical counts, not execution counts: Regs occurrences, exported entries, executable fallback lines, and direct dispatcher/near/hook expressions. Included headers and macros can add more edges; see audit.json and the accepted census for expanded/runtime effects. All 51 bridge translation units are excluded from the proposed production source manifest until their semantic portions have moved out of adapters.

| Bridge .c | Regs tokens | c_* entries | Fallback lines | Direct machine expressions |
|---|---|---|---|---|
| actor_pass_bridge.c | 3 | 2 | 0 | 0 |
| actor_render_bridge.c | 12 | 3 | 0 | 0 |
| actor_resources_bridge.c | 0 | 0 | 0 | 0 |
| adlx_allocation_bridge.c | 15 | 4 | 3 | 0 |
| adlx_digital_bridge.c | 26 | 14 | 0 | 3 |
| adlx_effects_bridge.c | 26 | 10 | 10 | 0 |
| adlx_facade_bridge.c | 9 | 4 | 0 | 1 |
| adlx_lifetime_bridge.c | 10 | 6 | 0 | 0 |
| adlx_loader_bridge.c | 9 | 3 | 1 | 0 |
| adlx_main_bridge.c | 18 | 10 | 2 | 0 |
| adlx_music_bridge.c | 16 | 8 | 0 | 0 |
| adlx_samples_bridge.c | 8 | 3 | 0 | 0 |
| adlx_sections_bridge.c | 13 | 3 | 3 | 0 |
| adlx_voice_bridge.c | 11 | 7 | 1 | 0 |
| audio_world_bridge.c | 1 | 0 | 0 | 0 |
| contacts_bridge.c | 6 | 4 | 1 | 0 |
| coordinate_scale_bridge.c | 2 | 2 | 0 | 0 |
| decimal_bridge.c | 4 | 3 | 0 | 0 |
| demo_core_bridge.c | 9 | 3 | 8 | 2 |
| demo_presentation_bridge.c | 26 | 7 | 0 | 3 |
| far_copy_bridge.c | 1 | 1 | 0 | 0 |
| hazards_bridge.c | 118 | 31 | 30 | 4 |
| high_scores_bridge.c | 11 | 10 | 0 | 7 |
| hud_bridge.c | 12 | 7 | 0 | 0 |
| ice_bridge.c | 1 | 1 | 0 | 0 |
| ice_scratch_bridge.c | 1 | 1 | 0 | 0 |
| input_bridge.c | 12 | 8 | 0 | 1 |
| input_world_bridge.c | 3 | 0 | 0 | 0 |
| items_bridge.c | 17 | 5 | 5 | 1 |
| level_view_bridge.c | 0 | 0 | 0 | 0 |
| lifecycle_bridge.c | 8 | 4 | 0 | 3 |
| menus_bridge.c | 15 | 13 | 0 | 16 |
| music_clock_bridge.c | 3 | 3 | 0 | 0 |
| palette_world_bridge.c | 1 | 0 | 0 | 0 |
| passenger_delivery_bridge.c | 68 | 12 | 12 | 3 |
| passenger_itinerary_bridge.c | 42 | 8 | 7 | 2 |
| passenger_water_bridge.c | 48 | 10 | 9 | 1 |
| pictures_bridge.c | 5 | 3 | 0 | 2 |
| pixel_world_bridge.c | 2 | 0 | 0 | 0 |
| player_physics_bridge.c | 14 | 2 | 0 | 0 |
| random_bridge.c | 3 | 2 | 0 | 0 |
| render_primitives_bridge.c | 18 | 11 | 0 | 0 |
| session_bridge.c | 16 | 4 | 0 | 6 |
| stones_bridge.c | 19 | 6 | 7 | 5 |
| terminal_tail_bridge.c | 2 | 1 | 0 | 0 |
| timer_bridge.c | 9 | 4 | 5 | 1 |
| timer_lifetime_bridge.c | 7 | 6 | 0 | 0 |
| timing_world_bridge.c | 1 | 0 | 0 | 0 |
| video_dos_bridge.c | 32 | 20 | 0 | 1 |
| video_pages_bridge.c | 1 | 0 | 0 | 0 |
| water_weather_bridge.c | 34 | 9 | 0 | 0 |

### Currently linked c/ units

`c/abi.c`, `c/actors.c`, `c/actors_states.c`, `c/adlib.c`, `c/demo_scripts.c`, `c/dispatch.c`, `c/dos_input.c`, `c/dsp.c`, `c/game_services.c`, `c/ice.c`, `c/items_water.c`, `c/memory.c`, `c/menu.c`, `c/menu_helpers.c`, `c/music_analysis.c`, `c/music_clock.c`, `c/platform.c`, `c/render.c`, `c/render_primitives.c`, `c/scene.c`, `c/sound_api.c`, `c/sound_engine.c`, `c/sound_state.c`, `c/timer.c`, `c/timer_stack.c`, `c/timer_system.c`, `c/video.c`.

`tools/hostbuild.py:build` selects the entire c/*.c glob. Source-level native status and zero executed L1 bodies do not remove these link dependencies. The literal build must continue to link its independent L1 reference after the production target stops doing so.

## Sources and validation of this audit

Read committed certificates, docs/standalone-plan.md, docs/port-contract.md, docs/actor-storage.md, bridge/provider source, host source, the original OWNERS.md and static.json, and the accepted close-stones-21 / close-adlx-22/-23 receipts. The original ownership table is corroboration, not a frozen current assignment.

`python -B build/workers/close-adlx-24/audit.py` creates only this directory's committed-source snapshot, schema and audit.json; it asserts six owner footprints and 6,439 nonoverlapping bytes, and accounts for all 392 model names. `write_docs.py` creates this LEDGER and cut-cells.json; its assignment asserts all 229 remaining names occur exactly once. These are static consistency checks, not new projector/census/API/host gate executions. The historical API decline comparison is 32/32 subset 188. Pending HUD/weather work is neither read as accepted nor relocked.


## Source index

- Named sets and their incomplete/conditional attribution: [program-model.json: variables](../metadata/program-model.json), [original census OWNERS.md](../build/workers/close-adlx-19/OWNERS.md), [original static.json](../build/workers/close-adlx-19/static.json).
- Current resident bindings: [timing_world](../metadata/closure/timing_world.json), [audio_world](../metadata/closure/audio_world.json), [palette_world](../metadata/closure/palette_world.json), [input_world](../metadata/closure/input_world.json), [video_pages](../metadata/closure/video_pages.json), [pixel_world](../metadata/closure/pixel_world.json), each `memory` and `uncertainty`; expanded static bytes are in [audit.json](../build/workers/close-adlx-24/audit.json).
- Observation versus ownership and excluded overlaps: [projector schema](../verif/projector/schema.py), [generated schema](../build/workers/close-adlx-24/schema/schema.json), [projector observer](../verif/projector/observer.c), [test GameWorld layout](../verif/projector/world.h).
- Shared state/continuations: [actor storage](actor-storage.md), [actors.h](../native/actors.h), [front_end.h](../native/front_end.h), [session.h](../native/session.h), [lifecycle.h](../native/lifecycle.h), [level.h](../native/level.h); corresponding certificate `memory/interface/retained` fields.
- Literal-binding debt and source list: [hostbuild.py](../tools/hostbuild.py), [dispatch.c](../c/dispatch.c), [ugh.h](../c/ugh.h), [pixel provider](../verif/pixel_platform_model.inc), [pixel public service header](../native/pixel_world.h).
- Production startup/observation separation: [host main](../host/main.c), [scenario fixture](../host/scenario.c), [digest](../host/digest.c), [terminal_tail interface](../metadata/closure/terminal_tail.json).
- Policy constraints: [standalone plan](standalone-plan.md), [port contract](port-contract.md). No policy is chosen by this audit.

All maintained-source links refer to the pinned revision named at the top, not to pending edits. Its source text is preserved under this worker's `head/` snapshot.

## Cut 6B allocation delta

The front-end allocation audit is in [front-end-storage.md](front-end-storage.md).
It moves 182 bytes beyond the accepted enemy-world baseline of 11,959, for
12,141 native observation bytes. The twelve named cells include word aliases,
not twelve allocations. Four embedded indexed-label destinations add 36 bytes;
the name/password terminators belong to their existing physical fields.
PasswordCompareBiasedBase remains a view and adds no allocation. File contents
remain service state. No step 7/8 port policy or resource identity is added.
