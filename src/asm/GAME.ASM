; Maintained reconstruction; asmgen.py is the bootstrap, asmverify.py is the gate.
; Image contribution 013B8..0664C (end exclusive).
.286
JUMPS
; Real DGROUP storage; independent addresses are bound in asm-map.json.
extrn SavedBiosVideoMode:byte
extrn PreviousKeyboardVector:byte
extrn PreviousKeyboardVectorSegment:byte
extrn KeyboardHandlerVector:byte
extrn DecodedImagePointer:byte
extrn CurrentTileMapPointer:byte
extrn CompressedTileMapsPointer:byte
extrn TimerBarPointer:byte
extrn BasePalettePointer:byte
extrn FadedPalettePointer:byte
extrn PaletteSourcePointer:byte
extrn LevelWorkspacePointer:byte
extrn HighScoreFileHandle:byte
extrn DecimalTenDivisor:byte
extrn DecimalHundredDivisor:byte
extrn DecimalThousandDivisor:byte
extrn DecimalTenThousandDivisor:byte
extrn VgaRowStrideBytes:byte
extrn TimerBarDivisor:byte
extrn HighScoreRowStride:byte
extrn DecimalDigitBuffer:byte
extrn DecimalDigit1:byte
extrn DecimalDigit2:byte
extrn DecimalDigit3:byte
extrn DecimalDigit4:byte
extrn DecimalDigit5:byte
extrn PasswordCompareBiasedBase:byte
extrn PasswordEditBuffer:byte
extrn PasswordEditChars2To3:byte
extrn LevelNumberTensCharacter:byte
extrn LevelNumberUnitsCharacter:byte
extrn HighScoreNameEntry:byte
extrn HighScoreNameChars2To3:byte
extrn HighScoreNameChars4To5:byte
extrn HighScoreNameChars6To7:byte
extrn HighScoreNameChars8To9:byte
extrn HighScoreRows:byte
extrn PlayerAnimationCycleStarts:byte
extrn PlayerAnimationCycleEnds:byte
extrn VgaSinglePlaneMasks:byte
extrn VgaCumulativePlaneMasks:byte
extrn CurrentLevelIndex:byte
extrn ScoreLowWord:byte
extrn ScoreHighWord:byte
extrn LevelTimer:byte
extrn LevelCountsByPlayerMode:byte
extrn MultiplierLimitsByDifficulty:byte
extrn PlayerImpactLimits:byte
extrn PlayerCount:byte
extrn PlayerArrayBytes:byte
extrn SelectedDifficulty:byte
extrn LivesRemaining:byte
extrn ScoreMultiplier:byte
extrn PlayerOneControlMode:byte
extrn PlayerTwoControlMode:byte
extrn CurrentKeyboardScanCode:byte
extrn PreviousPolledScanCode:byte
extrn KeyboardScanCodeChangeBits:byte
extrn KeyboardSequenceIndex:byte
extrn CoordinateScaleScratch:byte
extrn DemoExitCode:byte
extrn PlayerUpInput:byte
extrn PlayerDownInput:byte
extrn PlayerLeftInput:byte
extrn PlayerRightInput:byte
extrn PlayerActionInput:byte
extrn WaterRestorePending:byte
extrn WaterSurfaceFrameCountdown:byte
extrn WaterSurfaceFrame:byte
extrn CachedTimerBarWidth:byte
extrn ScreenFadeLevel:byte
extrn ScreenFadeStep:byte
extrn HudDigitCursorX:byte
extrn HudDigitCursorY:byte
extrn HudLivesX:byte
extrn HudScoreX:byte
extrn HudLevelCounterX:byte
extrn HudPlayerOneIconX:byte
extrn HudPlayerOneDestinationX:byte
extrn HudFareX:byte
extrn HudMultiplierX:byte
extrn HudPlayerTwoIconX:byte
extrn HudPlayerTwoDestinationX:byte
extrn HudCachedScoreLow:byte
extrn HudCachedScoreHigh:byte
extrn HudCachedFare:byte
extrn ds_27C8:byte
extrn HudCachedMultiplier:byte
extrn HudCachedLives:byte
extrn HudCachedLevelCounter:byte
extrn HudFareClearPending:byte
extrn WaterStepPhase:byte
extrn LevelCompletionMarker:byte
extrn PlayerX32:byte
extrn PlayerTwoFixedX:byte
extrn PlayerY32:byte
extrn PlayerTwoFixedY:byte
extrn PlayerPixelX:byte
extrn PlayerTwoPixelX:byte
extrn PlayerYPixels:byte
extrn SecondPlayerYPixels:byte
extrn PlayerCachedPixelX:byte
extrn PlayerTwoCachedPixelX:byte
extrn PlayerCachedPixelY:byte
extrn PlayerTwoCachedPixelY:byte
extrn PlayerSpriteIds:byte
extrn PlayerTwoSpriteId:byte
extrn PlayerCachedSpriteIds:byte
extrn PlayerAnimationCountdowns:byte
extrn PlayerTwoAnimationCountdown:byte
extrn PlayerThrustAnimationRate:byte
extrn PlayerPlatformIndices:byte
extrn ds_27FA:byte
extrn PlayerCarriedKinds:byte
extrn PlayerTwoPassengerIconState:byte
extrn HudCachedPlayerOneIconState:byte
extrn HudCachedPlayerTwoIconState:byte
extrn PlayerDestinationIcons:byte
extrn PlayerTwoDestinationIconIndex:byte
extrn PlayerPassengerFares:byte
extrn PlayerTwoFare:byte
extrn PlayerMinimumFares:byte
extrn PlayerHorizontalVelocities:byte
extrn ds_2812:byte
extrn PlayerVerticalVelocities:byte
extrn ds_2816:byte
extrn PlayerImpactMagnitude:byte
extrn KeyboardSequenceRecords:byte
extrn KeyboardSequenceNextScan:byte
extrn KeyboardSequenceActionIndex:byte
extrn KeyboardSequenceActionValue:byte
extrn KeyboardSequenceCandidateState:byte
extrn CurrentLevelRecord:byte
extrn LevelPlatformList:byte
extrn LevelActorList:byte
extrn LevelEnemyList:byte
extrn RemainingPassengerJourneys:byte
extrn LevelIntroTextPointer:byte
extrn LevelRainDirection:byte
extrn LevelPlayerOneStartX:byte
extrn LevelPlayerOneStartY:byte
extrn LevelPlayerTwoStartX:byte
extrn LevelPlayerTwoStartY:byte
extrn WaterY32:byte
extrn WaterSurfaceStep:byte
extrn WaterYPixels:byte
extrn PreviousWaterSurfaceY:byte
extrn WaterSurfaceByteOffset:byte
extrn LevelOrderTables:byte
extrn PlatformLeftEdges:byte
extrn PlatformRightEdges:byte
extrn PlatformHeights:byte
extrn PlatformArrivalPointsX:byte
extrn PlatformWaitingPointsX:byte
extrn PlatformSpawnX:byte
extrn PlatformDestinationIcons:byte
extrn PlatformActorOccupants:byte
extrn ActorInitialPlatformIndices:byte
extrn ActorJourneyCursors:byte
extrn ActorUpdateOrScriptCursor:byte
extrn DemoCompletionScanBiasedBase:byte
extrn ActorPlatformOrScriptDone:byte
extrn ActorDestinationPlatforms:byte
extrn ActorSourcePlatformByteIndices:byte
extrn ActorDestinationPlatformByteIndices:byte
extrn ds_2ACD:byte
extrn ActorX32:byte
extrn ActorY32:byte
extrn ActorPixelX:byte
extrn ActorPreviousDrawX:byte
extrn ActorPixelY:byte
extrn ActorPreviousDrawY:byte
extrn ActorAnimationByteOffsets:byte
extrn ActorAnimationCountdowns:byte
extrn ActorSpriteIds:byte
extrn ActorEraseSprite:byte
extrn ActorEraseOverlaySprite:byte
extrn ds_2C6D:byte
extrn PassengerQuickDeliveryCountdowns:byte
extrn EnemyDescriptors:byte
extrn EnemyPlatformIndices:byte
extrn EnemyX32:byte
extrn EnemyY32:byte
extrn EnemyAnimationOrDropLists:byte
extrn EnemyInitialDelays:byte
extrn EnemyHorizontalSpeeds:byte
extrn EnemyStateCallbacks:byte
extrn EnemyStateCounters:byte
extrn EnemyDrawX:byte
extrn EnemyPreviousDrawX:byte
extrn EnemyDrawY:byte
extrn EnemyPreviousDrawY:byte
extrn EnemyAnimationByteOffsets:byte
extrn EnemyAnimationCountdowns:byte
extrn EnemySpriteIds:byte
extrn EnemyEraseSprite:byte
extrn EnemyDirectionOrTargetPlayer:byte
extrn EnemyFlightSoundHandles:byte
extrn FallingItemDescriptors:byte
extrn FallingItemCallbacks:byte
extrn FallingItemSprites:byte
extrn FallingItemEraseSprite:byte
extrn FallingItemX:byte
extrn FallingItemY:byte
extrn FallingItemDrawX:byte
extrn FallingItemPreviousDrawX:byte
extrn FallingItemDrawY:byte
extrn FallingItemPreviousDrawY:byte
extrn FallingItemMotionOrLifetime:byte
extrn FallingItemVerticalStep:byte
extrn RainParticleOffsets:byte
extrn RainPreviousOffsets:byte
extrn RainParticleXModuloFour:byte
extrn JoystickPresentFlags:byte
extrn SecondJoystickPresent:byte
extrn FirstJoystickXCount:byte
extrn SecondJoystickXCount:byte
extrn FirstJoystickYCount:byte
extrn SecondJoystickYCount:byte
extrn JoystickButtonBits:byte
extrn SecondJoystickButtonBits:byte
extrn ds_3321:byte
extrn ds_3323:byte
extrn ds_3325:byte
extrn ds_3327:byte
extrn FirstJoystickXDoubleCenter:byte
extrn SecondJoystickXDoubleCenter:byte
extrn FirstJoystickYDoubleCenter:byte
extrn SecondJoystickYDoubleCenter:byte
extrn JoystickLeftThresholds:byte
extrn SecondJoystickXLowThreshold:byte
extrn JoystickRightThresholds:byte
extrn SecondJoystickXHighThreshold:byte
extrn JoystickUpThresholds:byte
extrn SecondJoystickYLowThreshold:byte
extrn JoystickDownThresholds:byte
extrn SecondJoystickYHighThreshold:byte
extrn JoystickEnabledAxisMask:byte
extrn JoystickSampleLoopLimit:byte
; This frame is known before CODE; other far-bank declarations follow CODE.
extrn ext_3629:far
extrn _InitializeSoundSystem:far
extrn _ShutdownSoundSystem:far
extrn _StartMusicTrack:far
extrn _StopMusicTrack:far
extrn _StopAdlibTrackChannel:far
extrn _PlayAdlibEffect:far
extrn ext_5C09:far
GAMESEG segment word public 'CODE'
assume cs:GAMESEG
public ext_013B
ext_013B label far
GAME_BASE label byte
public _main
_main equ GAME_BASE+00h
public _fn_013B_001E
_fn_013B_001E equ GAME_BASE+016h
public _fn_013B_001F
_fn_013B_001F equ GAME_BASE+017h
public _fn_013B_001D
_fn_013B_001D equ GAME_BASE+015h
public _fn_013B_001C
_fn_013B_001C equ GAME_BASE+014h
public _CopyFarBytes
_CopyFarBytes equ GAME_BASE+018h
; Absolute view of DGDATA label ActorDescriptors; OFFSET extern adds fixups.
; Retained for TASM 3.0 plain relocation order; see docs/data-source.md.
ActorDescriptors equ 029ADh
; Absolute view of DGDATA label ds_2A2D; OFFSET extern adds fixups.
; Retained for TASM 3.0 plain relocation order; see docs/data-source.md.
ds_2A2D equ 02A2Dh
; Absolute view of DGDATA label ActorOverlayOrScriptCallbacks; OFFSET extern adds fixups.
; Retained for TASM 3.0 plain relocation order; see docs/data-source.md.
ActorOverlayOrScriptCallbacks equ 02C2Dh
; CONTRACT (tools/apply.py)
; CS offset view of the three near water-frame targets indexed by 2*WaterSurfaceFrame.
; Consumer 2DFEh jumps here; actual word storage is WaterSurfaceDispatchWords at 2DB3h.
; END CONTRACT
WaterSurfaceDispatch equ GAME_BASE+02DABh
; CONTRACT (tools/apply.py)
; Raw last port-60h byte written by INT 09h and sampled at 44F1h.
; END CONTRACT
LatestInterruptScanCode equ GAME_BASE+04501h
; CONTRACT (tools/apply.py)
; CS word caching AX during sprite setup: AH is current plane mask; AL is register index 2.
; END CONTRACT
SpritePlaneStateScratch equ GAME_BASE+045F4h
; CONTRACT (tools/apply.py)
; CS scratch word: level tile-map offset during load, waterY minus spriteY during drawing.
; END CONTRACT
RendererScratchWord equ GAME_BASE+045F6h
; CONTRACT (tools/apply.py)
; CS word selecting playfield versus HUD drawing; initialized to 200 or 192 by video setup.
; END CONTRACT
PlayfieldHeight equ GAME_BASE+045F8h
; CONTRACT (tools/apply.py)
; Per-plane copy count: 3E80h for picture mode, 4800h for gameplay mode.
; END CONTRACT
VgaPlaneCopyByteCount equ GAME_BASE+045FAh
; CONTRACT (tools/apply.py)
; Far A000h page pointer; low word is zero in both video configurations.
; END CONTRACT
FixedVgaPagePointer equ GAME_BASE+045FCh
; CONTRACT (tools/apply.py)
; Far A000h display-page pointer; offset swaps with draw-page offset at 4EBBh.
; END CONTRACT
DisplayedVgaPagePointer equ GAME_BASE+04600h
; CONTRACT (tools/apply.py)
; CS far A000 pointer; low word is current draw-page offset and swaps on page flips.
; END CONTRACT
DrawPagePointer equ GAME_BASE+04604h
; CONTRACT (tools/apply.py)
; CS far A000 pointer to the saved background used by latch restoration and water tests.
; END CONTRACT
BackgroundPagePointer equ GAME_BASE+04608h
; CONTRACT (tools/apply.py)
; Far pointer to CS:4681h; picture loader copies 768 palette bytes here.
; END CONTRACT
PicturePaletteDestination equ GAME_BASE+0460Ch
; CONTRACT (tools/apply.py)
; CS far pointer to column-major sprite pixels for IDs below D9h.
; END CONTRACT
SpritePixels0To216Pointer equ GAME_BASE+04610h
; CONTRACT (tools/apply.py)
; CS far pointer selected for sprite IDs D9h through 129h.
; END CONTRACT
SpritePixels217To297Pointer equ GAME_BASE+04614h
; CONTRACT (tools/apply.py)
; CS far pointer selected for sprite IDs 12Ah through 222h.
; END CONTRACT
SpritePixels298To546Pointer equ GAME_BASE+04618h
; CONTRACT (tools/apply.py)
; CS far pointer selected for sprite IDs at or above 223h; no upper-bound check.
; END CONTRACT
SpritePixels547AndUpPointer equ GAME_BASE+0461Ch
; CONTRACT (tools/apply.py)
; CS far pointer to ID*4 records: word pixel-bank offset, byte width, byte height.
; END CONTRACT
SpriteDirectoryPointer equ GAME_BASE+04620h
; CONTRACT (tools/apply.py)
; CS far pointer to sprite 214's width byte: 5B63:035A = directory + 214 decimal * 4 + 2.
; SetDemoRevealSpriteWidth writes through it; this is a data pointer, not executable code.
; END CONTRACT
DemoRevealWidthPointer equ GAME_BASE+04624h
; CONTRACT (tools/apply.py)
; Far pointer to zero offset of the scratch segment, used by the picture loader.
; END CONTRACT
IceScratchPointer equ GAME_BASE+04628h
; CONTRACT (tools/apply.py)
; 768 component bytes; 466Ah duplicates colors 0..127 and 4C81h copies picture RGB.
; END CONTRACT
BaseRgbPalette equ GAME_BASE+04679h
; CONTRACT (tools/apply.py)
; 768 component bytes written from base palette using component*factor >> 8.
; END CONTRACT
FadedRgbPalette equ GAME_BASE+04979h
; CONTRACT (tools/apply.py)
; Decoder initializes BP here then subtracts two before each literal-code table lookup.
; END CONTRACT
IceLiteralCodeTablePivot equ GAME_BASE+04DDFh
; CONTRACT (tools/apply.py)
; Biased byte anchor: indexes -1..3 give 9,1,0,FF,FF; signed FF suppresses bit reads.
; END CONTRACT
IceMatchLengthBitCountsMinusOne equ GAME_BASE+04DFEh
; CONTRACT (tools/apply.py)
; Biased byte anchor: indexes -1..3 give 8,4,2,1,0, added to length bits (length-2).
; END CONTRACT
IceMatchLengthBiases equ GAME_BASE+04E03h
; CONTRACT (tools/apply.py)
; Byte counts for match offsets, indexed by unary offset class including -1.
; END CONTRACT
IceMatchOffsetBitCountsMinusOne equ GAME_BASE+04E08h
; CONTRACT (tools/apply.py)
; Word offset biases; negative class also subtracts the match length minus two.
; END CONTRACT
IceMatchOffsetBiases equ GAME_BASE+04E0Dh
; CONTRACT (tools/apply.py)
; First ADD/ADC state word; its high byte alone is replaced by DOS seconds.
; END CONTRACT
RandomStateWord0 equ GAME_BASE+04EEFh
; CONTRACT (tools/apply.py)
; High-byte view of random state word zero, written from DOS time DH.
; END CONTRACT
RandomSecondsSeedByte equ GAME_BASE+04EF0h
; CONTRACT (tools/apply.py)
; Second 16-bit state word, updated by ADC using first intermediate word.
; END CONTRACT
RandomStateWord1 equ GAME_BASE+04EF1h
; CONTRACT (tools/apply.py)
; Third 16-bit state word, updated by ADC using second intermediate word.
; END CONTRACT
RandomStateWord2 equ GAME_BASE+04EF3h
; CONTRACT (tools/apply.py)
; Fourth 16-bit state word, updated by ADC and fed back into state word zero.
; END CONTRACT
RandomStateWord3 equ GAME_BASE+04EF5h
; CONTRACT (tools/apply.py)
; Enter the DOS game: select DGROUP, initialize hardware, show logos and run the menu.
; Effects: initialization at 4F5E loads scores; the tail at 4EE6 restores video/input and exits.
; The fixed _main contribution alias remains a linker entry; this label names its code.
; END CONTRACT
RunDosGame:
    mov dx, seg ext_5C09 ; @0008
    mov ds, dx ; @000B
    call InitializeDosVideoInputAndSound ; @000D
    call ShowStartupPictures ; @0010
    call ConfigureVgaGameplayPages ; @0013
    call RunMainMenuAndAttractLoop ; @0016
    jmp near ptr loc_4EE6 ; @0019
; CONTRACT (tools/apply.py)
; Unimplemented C-facing hook: original byte is a near RET, with no result assignment.
; C:00F5 consumes DX:AX as a bank length after passing one dword argument.
; Quirk: a far caller gets no CS pop; do not translate this as a valid far length callback.
; END CONTRACT
loc_001C:
    ret ; @001C
; CONTRACT (tools/apply.py)
; Unimplemented C-facing hook: original byte is a near RET, with no result assignment.
; C:00F5 passes three dwords and interprets DX:AX as a huge data pointer.
; Quirk: a far caller gets no CS pop; neither pointer validity nor callback purpose is proven.
; END CONTRACT
loc_001D:
    ret ; @001D
; CONTRACT (tools/apply.py)
; Unimplemented C-facing hook: original byte is a near RET and leaves registers/flags intact.
; C:0003 calls it after 001F nine times when the device-mask bit 2 path succeeds.
; Quirk: far-call return convention is inconsistent; retain the mechanical name.
; END CONTRACT
loc_001E:
    ret ; @001E
; CONTRACT (tools/apply.py)
; Unimplemented C/SOUND hook: original byte is a near RET; registers/flags are unchanged.
; SOUND calls it in pairs around DSP/PIC/vector operations; C:0003 calls it nine times.
; Quirk: far callers get no CS pop. A hardware-delay purpose is only a hypothesis.
; END CONTRACT
loc_001F:
    ret ; @001F
; PROC/ARG/USES reproduces the entire 0020..0038 routine.
; CONTRACT (tools/apply.py)
; Copy bytes between far pointers without pointer normalization or overlap protection.
; In: far cdecl stack BP+6 byte count, BP+8 unused word, BP+0A source, BP+0E destination.
; Out: REP MOVSB consumes the low count word; CX becomes zero. DS/ES/SI/DI/BP are restored.
; Effects/quirks: obeys incoming DF, wraps 16-bit offsets, and does not read BP+8.
; C callers pass a dword count, then source and destination; caller removes arguments.
; END CONTRACT
CopyFarBytes proc C far uses ds es si di
    arg arg_0006:word, arg_0008:word, arg_000A:dword, arg_000E:dword
    lds si, arg_000A ; @0028
    les di, arg_000E ; @002B
    mov cx, arg_0006 ; @002E
    rep movsb ; @0031
    ret ; @0033 automatic USES restore, LEAVE and far return
CopyFarBytes endp
; CONTRACT (tools/apply.py)
; Refresh difficulty/player-mode text in the main menu and display the rendered page.
; In: DS=DGROUP, difficulty at 2638 and player count at 2634; uses text tables DA/E0.
; Out: replaces fixed menu fields at B0D/B19 and draws block AE4 starting at Y=48h.
; END CONTRACT
DrawMainMenu:
    call RestorePlayfieldBackground ; @0039
    mov bx, word ptr ds:[SelectedDifficulty] ; @003C
    mov si, 0DAh ; @0040
    mov di, 0B0Dh ; @0043
    call CopyIndexedMenuString ; @0046
    mov bx, word ptr ds:[PlayerCount] ; @0049
    dec bx ; @004D
    mov si, 0E0h ; @004E
    mov di, 0B19h ; @0051
    call CopyIndexedMenuString ; @0054
    mov si, 0AE4h ; @0057
    mov cx, 048h ; @005A
    call DrawTextBlock ; @005D
    jmp near ptr SwapAndDisplayVgaPage ; @0060
; CONTRACT (tools/apply.py)
; Run the music-backed attract sequence, main menu, control/password editors and game sessions.
; In: DS=DGROUP and initialized video/input; F1 starts play, F2 password, F3 difficulty,
; F4 player count, F5 controls. Idle waits 0834h retraces before restarting attract screens.
; Out: Q scan code 10h or a negative attract-screen result returns toward DOS shutdown.
; Effects: invokes gameplay at 0C07, tests the level limit, then checks/inserts the score.
; Quirk: F4 XORs player count with 3 and stores twice that value at 2636.
; END CONTRACT
RunMainMenuAndAttractLoop:
    push 011h ; @0063
    call far ptr _StopMusicTrack ; @0065
    add sp, 2 ; @006A
    push word ptr 0A5h ; @006D
    push 0 ; @0070
loc_0072:
    push seg ext_3637 ; @0072
    nop ; @0075
    push 0 ; @0076
loc_0078:
    call far ptr _StartMusicTrack ; @0078
    add sp, 8 ; @007D
loc_0080:
    call PlaySpriteRevealDemo ; @0080
    js loc_00FE ; @0083
    jne loc_00AF ; @0088
    call ShowCreditsPages ; @008D
    js loc_00FE ; @0090
    jne loc_00AF ; @0095
    call PlayAttractDemo ; @009A
    js loc_00FE ; @009D
    jne loc_00AF ; @00A2
    call ShowHighScores ; @00A7
    js loc_00FE ; @00AA
loc_00AF:
    call DuplicateSourcePaletteHalves ; @00AF
loc_00B2:
    mov word ptr ds:[WaterYPixels], 0AFh ; @00B2
    mov cx, 028h ; @00B8
    call WaitRetraceCount ; @00BB
    call ClearAllVgaPlanes ; @00BE
    call DrawMenuHeaderSprites ; @00C1
    call SaveDrawPageBackground ; @00C4
    call SwapAndDisplayVgaPage ; @00C7
    call RestorePlayfieldBackground ; @00CA
    call DrawMainMenu ; @00CD
    call FadePaletteIn ; @00D0
    jmp short loc_00D8 ; @00D3
loc_00D5:
    call DrawMainMenu ; @00D5
loc_00D8:
    mov cx, 0834h ; @00D8
loc_00DB:
    call WaitNextVerticalRetrace ; @00DB
    dec cx ; @00DE
    jne loc_00E9 ; @00DF
loc_00E4:
    call FadePaletteOut ; @00E4
    jmp short loc_0080 ; @00E7
loc_00E9:
    call PollKeyboardScanChange ; @00E9
    and ah, ah ; @00EC
    je short loc_00DB ; @00EE
    cmp al, 02Eh ; @00F0
    je short loc_00E4 ; @00F2
    cmp al, 010h ; @00F4
    jne loc_00FF ; @00F6
    jmp near ptr FadePaletteOut ; @00FB
loc_00FE:
    ret ; @00FE
loc_00FF:
    cmp al, 03Fh ; @00FF
    jne loc_010E ; @0101
    call FadePaletteOut ; @0106
    call SelectPlayerControls ; @0109
    jmp short loc_00B2 ; @010C
loc_010E:
    cmp al, 03Eh ; @010E
    jne loc_0125 ; @0110
    mov ax, word ptr ds:[PlayerCount] ; @0115
    xor ax, word ptr 03h ; @0118
    mov word ptr ds:[PlayerCount], ax ; @011B
    shl ax, 1 ; @011E
    mov word ptr ds:[PlayerArrayBytes], ax ; @0120
    jmp short loc_00D5 ; @0123
loc_0125:
    cmp al, 03Dh ; @0125
    jne loc_013F ; @0127
    mov ax, word ptr ds:[SelectedDifficulty] ; @012C
    inc ax ; @012F
    cmp ax, word ptr 03h ; @0130
    jb loc_013A ; @0133
    xor ax, ax ; @0138
loc_013A:
    mov word ptr ds:[SelectedDifficulty], ax ; @013A
    jmp short loc_00D5 ; @013D
loc_013F:
    cmp al, 03Ch ; @013F
    jne loc_014B ; @0141
    call EditLevelPassword ; @0146
    jmp short loc_00D5 ; @0149
loc_014B:
    cmp al, 03Bh ; @014B
    jne short loc_00D8 ; @014D
    call FadePaletteOut ; @014F
    call RunGameFromPassword ; @0152
    call ClearAllVgaPlanes ; @0155
    mov bx, word ptr ds:[PlayerArrayBytes] ; @0158
    sub bx, 2 ; @015C
    mov ax, word ptr ds:[CurrentLevelIndex] ; @015F
    cmp ax, word ptr [bx + LevelCountsByPlayerMode] ; @0162
loc_0166:
    jae loc_01AC ; @0166
    mov word ptr ds:[WaterYPixels], 0C8h ; @016B
    mov si, 0C0Ch ; @0171
    mov cx, 048h ; @0174
    call DrawTextBlock ; @0177
    call SwapAndDisplayVgaPage ; @017A
    push 011h ; @017D
    call far ptr _StopMusicTrack ; @017F
    add sp, 2 ; @0184
    push 1 ; @0187
    push word ptr 0E1h ; @0189
loc_018C:
    push seg ext_326B ; @018C
    nop ; @018F
    push 0 ; @0190
loc_0192:
    call far ptr _PlayAdlibEffect ; @0192
    add sp, 8 ; @0197
    call FadePaletteIn ; @019A
    mov cx, 02BCh ; @019D
    call WaitForInputOrRetraceTimeout ; @01A0
    call FadePaletteOut ; @01A3
loc_01A6:
    call InsertHighScoreAndClearScore ; @01A6
    jmp near ptr RunMainMenuAndAttractLoop ; @01A9
loc_01AC:
    call PlayGameCompletionDemo ; @01AC
    jmp short loc_01A6 ; @01AF
; CONTRACT (tools/apply.py)
; Show the TOP FIVE high-score text with menu-header sprites and palette fades.
; In: DS=DGROUP; waits up to 0578h retraces through 4497, also accepting keyboard/joystick.
; Out: AX=FFFFh with SF=1 for scan code 10h after masking bit 7; otherwise AX=1, SF=0.
; ZF=0 on both exits; callers use SF to request shutdown.
; END CONTRACT
ShowHighScores:
    mov word ptr ds:[WaterYPixels], 0C8h ; @01B1
    mov cx, 028h ; @01B7
    call WaitRetraceCount ; @01BA
    call ClearAllVgaPlanes ; @01BD
    call DrawMenuHeaderSprites ; @01C0
    mov si, 0C7Bh ; @01C3
    mov cx, 050h ; @01C6
    call DrawTextBlock ; @01C9
    call SwapAndDisplayVgaPage ; @01CC
    call FadePaletteIn ; @01CF
    mov cx, 0578h ; @01D2
    call WaitForInputOrRetraceTimeout ; @01D5
    push ax ; @01D8
    call FadePaletteOut ; @01D9
    pop ax ; @01DC
    and al, 07Fh ; @01DD
    cmp al, 010h ; @01DF
    jne loc_01EB ; @01E1
    mov ax, 0FFFFh ; @01E6
    jmp short loc_01EE ; @01E9
loc_01EB:
    mov ax, 1 ; @01EB
loc_01EE:
    and ax, ax ; @01EE
    ret ; @01F0
; CONTRACT (tools/apply.py)
; Restore the name-entry rectangle, redraw the editable high-score name and display it.
; In: DS=DGROUP, name bytes at C6D; redraws a 320x16 rectangle at Y=A0h.
; Preserves BX and SI explicitly so the editor retains cursor-blink state and character index.
; END CONTRACT
DrawHighScoreNameEntry:
    push bx ; @01F1
    push si ; @01F2
    xor ax, ax ; @01F3
    mov bx, 0A0h ; @01F5
    mov cx, 0140h ; @01F8
    mov dx, 010h ; @01FB
    call RestoreBackgroundRectangle ; @01FE
    mov si, 0C6Dh ; @0201
    mov cx, 0A0h ; @0204
    call DrawTextLine ; @0207
    call SwapAndDisplayVgaPage ; @020A
    pop si ; @020D
    pop bx ; @020E
    ret ; @020F
; CONTRACT (tools/apply.py)
; Insert the current score into the first qualifying TOP FIVE row and ask for its name.
; In: DS=DGROUP, unsigned score words at 261E/2620; score text uses six leading-space digits.
; Effects: shifts lower rows, accepts up to 12 letters/digits/spaces with lowercase uppercased,
; supports backspace, and commits on Enter; empty input becomes INCOGNITUS plus spaces.
; Saves scores and shows TOP FIVE on insertion. Both insertion and rejection clear 261E/2620.
; Quirks: ties qualify; only 20 of 21 row bytes shift; BIOS INT16 entry temporarily restores
; the old INT09 handler, then reinstalls the game's handler. No Escape cancellation path.
; END CONTRACT
InsertHighScoreAndClearScore:
    mov si, 0C8h ; @0210
    mov ax, word ptr ds:[ScoreLowWord] ; @0213
    mov dx, word ptr ds:[ScoreHighWord] ; @0216
    call EncodeSixDecimalDigits ; @021A
    xor ah, ah ; @021D
    xor si, si ; @021F
loc_0221:
    mov al, byte ptr [si + 0C8h] ; @0221
    add al, 030h ; @0225
    cmp al, 030h ; @0227
    je loc_0230 ; @0229
    dec ah ; @022E
loc_0230:
    test ah, 0FFh ; @0230
    jne loc_0241 ; @0233
    cmp al, 030h ; @0238
    jne loc_0241 ; @023A
    mov al, 020h ; @023F
loc_0241:
    mov byte ptr [si + 0C8h], al ; @0241
    inc si ; @0245
    cmp si, 6 ; @0246
    jne short loc_0221 ; @0249
    xor cl, cl ; @024B
loc_024D:
    call TestHighScoreQualification ; @024D
    jb loc_0260 ; @0250
    inc cl ; @0255
    cmp cl, 5 ; @0257
    nop ; @025A
    jne short loc_024D ; @025B
    jmp near ptr loc_03C9 ; @025D
loc_0260:
    xor ch, ch ; @0260
    push cx ; @0262
    mov bp, cx ; @0263
    mov cl, 3 ; @0265
    nop ; @0267
    nop ; @0268
loc_0269:
    call CopyHighScoreRowDown ; @0269
    dec cx ; @026C
    cmp cx, bp ; @026D
    jge short loc_0269 ; @026F
    mov cx, bp ; @0271
    call GetHighScoreDigits ; @0273
    mov si, 5 ; @0276
loc_0279:
    mov al, byte ptr [si + 0C8h] ; @0279
    mov byte ptr [bx + si], al ; @027D
    dec si ; @027F
    jns short loc_0279 ; @0280
    push 011h ; @0282
loc_0284:
    call far ptr _StopMusicTrack ; @0284
    add sp, 2 ; @0289
    push word ptr 0A5h ; @028C
    push 0 ; @028F
loc_0291:
    push seg ext_3279 ; @0291
    nop ; @0294
    push 0 ; @0295
loc_0297:
    call far ptr _StartMusicTrack ; @0297
    add sp, 8 ; @029C
    call RestoreKeyboardInterrupt ; @029F
    mov si, 0Bh ; @02A2
    nop ; @02A5
    mov al, 020h ; @02A6
loc_02A8:
    mov byte ptr [si + HighScoreNameEntry], al ; @02A8
    dec si ; @02AC
    jns short loc_02A8 ; @02AD
    mov word ptr ds:[WaterYPixels], 09Fh ; @02AF
    mov cx, 028h ; @02B5
    call WaitRetraceCount ; @02B8
    call ClearAllVgaPlanes ; @02BB
    call DrawMenuHeaderSprites ; @02BE
    mov si, 0C23h ; @02C1
    mov cx, 050h ; @02C4
    call DrawTextBlock ; @02C7
    call SaveDrawPageBackground ; @02CA
    call SwapAndDisplayVgaPage ; @02CD
    call RestorePlayfieldBackground ; @02D0
    call FadePaletteIn ; @02D3
    xor si, si ; @02D6
loc_02D8:
    xor bl, bl ; @02D8
loc_02DA:
    call WaitVerticalRetraceActive ; @02DA
    dec bl ; @02DD
    test bl, 010h ; @02DF
    je loc_02EB ; @02E2
    mov al, 03Fh ; @02E7
    jmp short loc_02ED ; @02E9
loc_02EB:
    mov al, 020h ; @02EB
loc_02ED:
    cmp si, 0Ch ; @02ED
    nop ; @02F0
    jae loc_02FA ; @02F1
    mov byte ptr [si + HighScoreNameEntry], al ; @02F6
loc_02FA:
    call DrawHighScoreNameEntry ; @02FA
    mov ah, 1 ; @02FD
    int 016h ; @02FF
    je short loc_02DA ; @0301
    xor ah, ah ; @0303
    int 016h ; @0305
    cmp al, 8 ; @0307
    jne loc_0328 ; @0309
    and si, si ; @030E
    je short loc_02DA ; @0310
    mov al, 020h ; @0312
    cmp si, 0Ch ; @0314
    nop ; @0317
    jae loc_0321 ; @0318
    mov byte ptr [si + HighScoreNameEntry], al ; @031D
loc_0321:
    dec si ; @0321
    mov byte ptr [si + HighScoreNameEntry], al ; @0322
    jmp short loc_02D8 ; @0326
loc_0328:
    cmp al, 041h ; @0328
    jb loc_0336 ; @032A
    cmp al, 05Ah ; @032F
    jbe loc_0356 ; @0331
loc_0336:
    cmp al, 061h ; @0336
    jb loc_0348 ; @0338
    cmp al, 07Ah ; @033D
    ja loc_0348 ; @033F
    sub al, 020h ; @0344
    jmp short loc_0356 ; @0346
loc_0348:
    cmp al, 030h ; @0348
    jb loc_0367 ; @034A
    cmp al, 039h ; @034F
    ja loc_0367 ; @0351
loc_0356:
    cmp si, 0Ch ; @0356
    nop ; @0359
    jae loc_02DA ; @035A JUMPS expansion
loc_035F:
    mov byte ptr [si + HighScoreNameEntry], al ; @035F
    inc si ; @0363
    jmp near ptr loc_02D8 ; @0364
loc_0367:
    cmp al, 020h ; @0367
    je short loc_0356 ; @0369
    cmp al, 0Dh ; @036B
    je loc_0375 ; @036D
    jmp near ptr loc_02DA ; @0372
loc_0375:
    cmp si, 0Ch ; @0375
    nop ; @0378
    jae loc_03AC ; @0379
    mov byte ptr [si + HighScoreNameEntry], 020h ; @037E
    nop ; @0383
    call DrawHighScoreNameEntry ; @0384
    and si, si ; @0387
    jne loc_03AC ; @0389
    mov word ptr ds:[HighScoreNameEntry], 04E49h ; @038E
    mov word ptr ds:[HighScoreNameChars2To3], 04F43h ; @0394
    mov word ptr ds:[HighScoreNameChars4To5], 04E47h ; @039A
    mov word ptr ds:[HighScoreNameChars6To7], 05449h ; @03A0
    mov word ptr ds:[HighScoreNameChars8To9], 05355h ; @03A6
loc_03AC:
    pop cx ; @03AC
    call GetHighScoreRow ; @03AD
    mov si, 0Bh ; @03B0
    nop ; @03B3
loc_03B4:
    mov al, byte ptr [si + HighScoreNameEntry] ; @03B4
    mov byte ptr [bx + si], al ; @03B8
    dec si ; @03BA
    jns short loc_03B4 ; @03BB
    call InstallKeyboardSequenceInterrupt ; @03BD
    call FadePaletteOut ; @03C0
    call SaveHighScores ; @03C3
    call ShowHighScores ; @03C6
loc_03C9:
    jmp near ptr loc_396D ; @03C9
loc_03CC:
    ret ; @03CC
; CONTRACT (tools/apply.py)
; XOR all 107 score-table bytes, including the two trailing terminators, with FFh.
; In: DS=DGROUP; range C86..CF0 inclusive. Out: SI=FFFFh and CF=0 after the reverse loop.
; Applying twice restores plaintext; this is also the common tail of score-file routines.
; END CONTRACT
ComplementHighScoreTable:
    mov si, 06Ah ; @03CD
    nop ; @03D0
loc_03D1:
    xor byte ptr [si + HighScoreRows], 0FFh ; @03D1
    dec si ; @03D6
    jns short loc_03D1 ; @03D7
    ret ; @03D9
; CONTRACT (tools/apply.py)
; Complement the score table, create/truncate UGH!.HI and request a 107-byte DOS write.
; In: DS=DGROUP; DOS INT21 AH=3Ch/40h uses filename CF1 and buffer C86.
; Out: always complements the table back, even on failure; does not provide error status.
; Quirks: never closes a successfully created handle, ignores short writes, and the common
; complement tail clears CF, discarding create/write errors. Handle is saved at 00BB.
; END CONTRACT
SaveHighScores:
    call ComplementHighScoreTable ; @03DA
    mov dx, 0CF1h ; @03DD
    mov cx, 0 ; @03E0
    mov ah, 03Ch ; @03E3
    int 021h ; @03E5
    jb loc_0403 ; @03E7
    mov word ptr ds:[HighScoreFileHandle], ax ; @03EC
    mov cx, 06Bh ; @03EF
    nop ; @03F2
    mov dx, 0C86h ; @03F3
    mov bx, word ptr ds:[HighScoreFileHandle] ; @03F6
    mov ah, 040h ; @03FA
    int 021h ; @03FC
    jb loc_0403 ; @03FE
loc_0403:
    jmp short ComplementHighScoreTable ; @0403
; CONTRACT (tools/apply.py)
; Open UGH!.HI read-only, request 107 bytes into the score table, close and complement it.
; In: DS=DGROUP; DOS INT21 AH=3Dh/3Fh/3Eh uses filename CF1 and buffer C86.
; Out: open/read/close carry errors return without complementing; successful close decodes.
; Quirks: short reads count as success; read errors leak the open handle. No table validation
; or rollback occurs, so errors/short reads can leave partially replaced or encoded bytes.
; END CONTRACT
LoadHighScores:
    mov dx, 0CF1h ; @0405
    mov ax, 03D00h ; @0408
    int 021h ; @040B
    jb loc_0438 ; @040D
    mov word ptr ds:[HighScoreFileHandle], ax ; @0412
    mov cx, 06Bh ; @0415
    nop ; @0418
    mov dx, 0C86h ; @0419
    mov ah, 03Fh ; @041C
    mov bx, word ptr ds:[HighScoreFileHandle] ; @041E
    int 021h ; @0422
    jb loc_0438 ; @0424
    mov bx, word ptr ds:[HighScoreFileHandle] ; @0429
    mov ah, 03Eh ; @042D
    int 021h ; @042F
    jb loc_0438 ; @0431
    jmp short ComplementHighScoreTable ; @0436
loc_0438:
    jmp short loc_03CC ; @0438
; CONTRACT (tools/apply.py)
; Locate the name/start of a fixed-width high-score row in DGROUP.
; In: CL zero-based row (callers use 0..4), DS=DGROUP, byte stride at C7 (21).
; Out: AX=BX=C86 + unsigned(CL)*stride, modulo 65536; CX is unchanged.
; END CONTRACT
GetHighScoreRow:
    mov al, cl ; @043A
    mul byte ptr ds:[HighScoreRowStride] ; @043C
    add ax, word ptr 0C86h ; @0440
    mov bx, ax ; @0443
    ret ; @0445
; CONTRACT (tools/apply.py)
; Locate the six score characters within a fixed-width high-score row.
; In: CL zero-based row (callers use 0..4), DS=DGROUP, byte stride at C7 (21).
; Out: AX=BX=C94 + unsigned(CL)*stride, modulo 65536; CX is unchanged.
; END CONTRACT
GetHighScoreDigits:
    mov al, cl ; @0446
    mul byte ptr ds:[HighScoreRowStride] ; @0448
    add ax, word ptr 0C94h ; @044C
    mov bx, ax ; @044F
    ret ; @0451
; CONTRACT (tools/apply.py)
; Test whether the candidate six-character score is at least the selected row's score.
; In: CL row index, DS=DGROUP, candidate characters C8..CD (spaces and ASCII digits).
; Out: CF=1 if candidate >= stored score, CF=0 if less; BX points to stored score.
; Quirk: compares unsigned bytes left-to-right, counts ties as qualifying, preserves CX;
; ZF is from the last examined CMP and is not a general equality result.
; END CONTRACT
TestHighScoreQualification:
    call GetHighScoreDigits ; @0452
    mov al, byte ptr ds:[DecimalDigitBuffer] ; @0455
    cmp al, byte ptr [bx] ; @0458
    jb loc_04AF ; @045A
    ja loc_04B1 ; @045F
    mov al, byte ptr ds:[DecimalDigit1] ; @0464
    cmp al, byte ptr [bx + 1] ; @0467
    jb loc_04AF ; @046A
    ja loc_04B1 ; @046F
    mov al, byte ptr ds:[DecimalDigit2] ; @0474
    cmp al, byte ptr [bx + 2] ; @0477
    jb loc_04AF ; @047A
    ja loc_04B1 ; @047F
    mov al, byte ptr ds:[DecimalDigit3] ; @0484
    cmp al, byte ptr [bx + 3] ; @0487
    jb loc_04AF ; @048A
    ja loc_04B1 ; @048F
    mov al, byte ptr ds:[DecimalDigit4] ; @0494
    cmp al, byte ptr [bx + 4] ; @0497
    jb loc_04AF ; @049A
    ja loc_04B1 ; @049F
    mov al, byte ptr ds:[DecimalDigit5] ; @04A4
    cmp al, byte ptr [bx + 5] ; @04A7
    jae loc_04B1 ; @04AA
loc_04AF:
    clc ; @04AF
    ret ; @04B0
loc_04B1:
    stc ; @04B1
    ret ; @04B2
; CONTRACT (tools/apply.py)
; Copy one high-score row down by one slot, leaving the destination CR untouched.
; In: CL source row (insertion uses 3 down to the insertion row), DS=DGROUP, stride C7.
; Out: copies exactly 20 bytes forward to source+21; BX/DI advance 20, DX=FFFFh.
; Quirk: the 21st byte (CR) is deliberately not copied; CX is unchanged.
; END CONTRACT
CopyHighScoreRowDown:
    call GetHighScoreRow ; @04B3
    mov di, bx ; @04B6
    add di, 015h ; @04B8
    nop ; @04BB
    mov dx, 013h ; @04BC
    nop ; @04BF
loc_04C0:
    mov al, byte ptr [bx] ; @04C0
    mov byte ptr [di], al ; @04C2
    inc bx ; @04C4
    inc di ; @04C5
    dec dx ; @04C6
    jns short loc_04C0 ; @04C7
    ret ; @04C9
; CONTRACT (tools/apply.py)
; Edit the main menu's 20-character, space-padded level-password field using BIOS INT16.
; In: DS=DGROUP. Clears B4E..B61; accepts letters/digits, uppercases lowercase, backspaces,
; and commits on Enter. Empty entry writes NONE; spaces and Escape are not accepted input.
; Effects: restores old INT09 and flushes BIOS keys before editing; tail reinstalls game INT09.
; Cursor blinks as '?' at the current position; no NUL terminator is appended to the field.
; END CONTRACT
EditLevelPassword:
    call RestoreKeyboardInterrupt ; @04CA
    call RestorePlayfieldBackground ; @04CD
    call DrawMainMenu ; @04D0
    mov si, 013h ; @04D3
    nop ; @04D6
    mov al, 020h ; @04D7
loc_04D9:
    mov byte ptr [si + PasswordEditBuffer], al ; @04D9
    dec si ; @04DD
    jns short loc_04D9 ; @04DE
    xor si, si ; @04E0
loc_04E2:
    xor bl, bl ; @04E2
loc_04E4:
    call WaitVerticalRetraceActive ; @04E4
    dec bl ; @04E7
    test bl, 010h ; @04E9
    je loc_04F5 ; @04EC
    mov al, 03Fh ; @04F1
    jmp short loc_04F7 ; @04F3
loc_04F5:
    mov al, 020h ; @04F5
loc_04F7:
    cmp si, 014h ; @04F7
    nop ; @04FA
    jae loc_0504 ; @04FB
    mov byte ptr [si + PasswordEditBuffer], al ; @0500
loc_0504:
    push bx ; @0504
    push si ; @0505
    xor ax, ax ; @0506
    mov bx, 0B0h ; @0508
    mov cx, 0140h ; @050B
    mov dx, 010h ; @050E
    call RestoreBackgroundRectangle ; @0511
    mov si, 0B4Eh ; @0514
    mov cx, 0B0h ; @0517
    call DrawTextLine ; @051A
    call SwapAndDisplayVgaPage ; @051D
    pop si ; @0520
    pop bx ; @0521
    mov ah, 1 ; @0522
    int 016h ; @0524
    je short loc_04E4 ; @0526
    xor ah, ah ; @0528
    int 016h ; @052A
    cmp al, 8 ; @052C
    jne loc_054D ; @052E
    and si, si ; @0533
    je short loc_04E4 ; @0535
    mov al, 020h ; @0537
    cmp si, 014h ; @0539
    nop ; @053C
    jae loc_0546 ; @053D
    mov byte ptr [si + PasswordEditBuffer], al ; @0542
loc_0546:
    dec si ; @0546
    mov byte ptr [si + PasswordEditBuffer], al ; @0547
    jmp short loc_04E2 ; @054B
loc_054D:
    cmp al, 041h ; @054D
    jb loc_055B ; @054F
    cmp al, 05Ah ; @0554
    jbe loc_057B ; @0556
loc_055B:
    cmp al, 061h ; @055B
    jb loc_056D ; @055D
    cmp al, 07Ah ; @0562
    ja loc_056D ; @0564
    sub al, 020h ; @0569
    jmp short loc_057B ; @056B
loc_056D:
    cmp al, 030h ; @056D
    jb loc_058C ; @056F
    cmp al, 039h ; @0574
    ja loc_058C ; @0576
loc_057B:
    cmp si, 014h ; @057B
    nop ; @057E
    jae loc_04E4 ; @057F JUMPS expansion
loc_0584:
    mov byte ptr [si + PasswordEditBuffer], al ; @0584
    inc si ; @0588
    jmp near ptr loc_04E2 ; @0589
loc_058C:
    cmp al, 0Dh ; @058C
    je loc_0596 ; @058E
    jmp near ptr loc_04E4 ; @0593
loc_0596:
    cmp si, 014h ; @0596
    nop ; @0599
    jae loc_05B8 ; @059A
    mov byte ptr [si + PasswordEditBuffer], 020h ; @059F
    nop ; @05A4
    and si, si ; @05A5
    jne loc_05B8 ; @05A7
    mov word ptr ds:[PasswordEditBuffer], 04F4Eh ; @05AC
    mov word ptr ds:[PasswordEditChars2To3], 0454Eh ; @05B2
loc_05B8:
    jmp near ptr InstallKeyboardSequenceInterrupt ; @05B8
; CONTRACT (tools/apply.py)
; Refresh both control-option labels and display the control-options text block at B64.
; In: DS=DGROUP, signed control words 263F/2641; each word+1 indexes table E4.
; Out: copies KEYBOARD / JOYSTICK A / JOYSTICK B text into fields B73/B8D and swaps pages.
; END CONTRACT
DrawControlOptions:
    call RestorePlayfieldBackground ; @05BB
    mov bx, word ptr ds:[PlayerOneControlMode] ; @05BE
    inc bx ; @05C2
    mov si, 0E4h ; @05C3
    mov di, 0B73h ; @05C6
    call CopyIndexedMenuString ; @05C9
    mov bx, word ptr ds:[PlayerTwoControlMode] ; @05CC
    inc bx ; @05D0
    mov si, 0E4h ; @05D1
    mov di, 0B8Dh ; @05D4
    call CopyIndexedMenuString ; @05D7
    mov si, 0B64h ; @05DA
    mov cx, 050h ; @05DD
    call DrawTextBlock ; @05E0
    jmp near ptr SwapAndDisplayVgaPage ; @05E3
; CONTRACT (tools/apply.py)
; Show control options; F1/F2 cycle the corresponding player's enabled input device.
; In: DS=DGROUP; 263F/2641 use -1 keyboard, 0 joystick A, 1 joystick B.
; Out: negative presence words at 3311+2*device permit joystick selection; absent devices skip.
; Effects: redraws on change; Escape or an 0834h-retrace idle timeout fades back to the menu.
; Quirks: signed candidate >=2 wraps to -1; unrecognized keys restart the timeout.
; END CONTRACT
SelectPlayerControls:
    mov word ptr ds:[WaterYPixels], 0C8h ; @05E6
    mov cx, 028h ; @05EC
    call WaitRetraceCount ; @05EF
    call DrawControlOptions ; @05F2
    call FadePaletteIn ; @05F5
    jmp short loc_05FD ; @05F8
loc_05FA:
    call DrawControlOptions ; @05FA
loc_05FD:
    mov cx, 0834h ; @05FD
loc_0600:
    call WaitNextVerticalRetrace ; @0600
    dec cx ; @0603
    jne loc_060C ; @0604
loc_0609:
    jmp near ptr FadePaletteOut ; @0609
loc_060C:
    call PollKeyboardScanChange ; @060C
    and ah, ah ; @060F
    je short loc_0600 ; @0611
    cmp al, 1 ; @0613
    je short loc_0609 ; @0615
    cmp al, 03Bh ; @0617
    jne loc_0644 ; @0619
    xor bx, bx ; @061E
loc_0620:
    mov ax, word ptr [bx + PlayerOneControlMode] ; @0620
loc_0624:
    inc ax ; @0624
    cmp ax, word ptr 02h ; @0625
    jge loc_063B ; @0628
    mov si, ax ; @062D
    shl si, 1 ; @062F
    test word ptr [si + JoystickPresentFlags], 0FFFFh ; @0631
    jns short loc_0624 ; @0637
    jmp short loc_063E ; @0639
loc_063B:
    mov ax, 0FFFFh ; @063B
loc_063E:
    mov word ptr [bx + PlayerOneControlMode], ax ; @063E
    jmp short loc_05FA ; @0642
loc_0644:
    cmp al, 03Ch ; @0644
    jne loc_0650 ; @0646
    mov bx, 2 ; @064B
    jmp short loc_0620 ; @064E
loc_0650:
    jmp short loc_05FD ; @0650
; CONTRACT (tools/apply.py)
; Copy a selected NUL-terminated menu string into a mutable field in the same segment.
; In: DS:SI table of near offsets, BX zero-based index, DS:DI destination; assumes DF=0.
; Out: ES=DS, BX doubled, SI past source NUL, DI past last copied byte, ZF=1.
; Quirk: copies neither the terminator nor padding; destination tail bytes remain unchanged.
; END CONTRACT
CopyIndexedMenuString:
    push ds ; @0652
    pop es ; @0653
    shl bx, 1 ; @0654
    mov si, word ptr [bx + si] ; @0656
loc_0658:
    lodsb ; @0658
    and al, al ; @0659
    je loc_0663 ; @065B
    stosb ; @0660
    jmp short loc_0658 ; @0661
loc_0663:
    ret ; @0663
; CONTRACT (tools/apply.py)
; Show level number, level instruction/title text and the current player-mode password.
; In: DS=DGROUP, level index 261C, text near pointer 28F3, twice-player-count at 2636.
; Effects: writes two ASCII level digits into BFD/BFE; scans NUL-separated password strings,
; plays transition sound, fades in, waits for keyboard/joystick, then fades out.
; Out: restores water/display line word 2903 after temporarily using AFh.
; Quirks: level number and password traversal use only the low level byte, incremented mod 256.
; END CONTRACT
ShowLevelIntroduction:
    call ClearAllVgaPlanes ; @0664
    mov ax, word ptr ds:[WaterYPixels] ; @0667
    push ax ; @066A
    mov word ptr ds:[WaterYPixels], 0AFh ; @066B
    mov al, byte ptr ds:[CurrentLevelIndex] ; @0671
    inc al ; @0674
    mov si, 0C8h ; @0676
    call EncodeTwoDecimalDigits ; @0679
    mov al, byte ptr ds:[DecimalDigitBuffer] ; @067C
    add al, 030h ; @067F
    mov byte ptr ds:[LevelNumberTensCharacter], al ; @0681
    mov al, byte ptr ds:[DecimalDigit1] ; @0684
    add al, 030h ; @0687
    mov byte ptr ds:[LevelNumberUnitsCharacter], al ; @0689
    mov cx, 020h ; @068C
    mov si, 0BF6h ; @068F
    call DrawTextLine ; @0692
    add cx, 020h ; @0695
    mov si, word ptr ds:[LevelIntroTextPointer] ; @0698
    call DrawTextBlock ; @069C
    mov cx, 0A0h ; @069F
    mov si, 0C00h ; @06A2
    call DrawTextLine ; @06A5
    mov dl, byte ptr ds:[CurrentLevelIndex] ; @06A8
    inc dl ; @06AC
    mov bx, word ptr ds:[PlayerArrayBytes] ; @06AE
    sub bx, 2 ; @06B2
    mov si, word ptr [bx + 0EAh] ; @06B5
loc_06B9:
    dec dl ; @06B9
    je loc_06C7 ; @06BB
loc_06C0:
    lodsb ; @06C0
    and al, al ; @06C1
    jne short loc_06C0 ; @06C3
    je short loc_06B9 ; @06C5
loc_06C7:
    call DrawTextLine ; @06C7
    call SwapAndDisplayVgaPage ; @06CA
    push 011h ; @06CD
loc_06CF:
    call far ptr _StopMusicTrack ; @06CF
    add sp, 2 ; @06D4
    push 1 ; @06D7
    push word ptr 0E1h ; @06D9
loc_06DC:
    push seg ext_3629 ; @06DC
    nop ; @06DF
    push 0 ; @06E0
loc_06E2:
    call far ptr _PlayAdlibEffect ; @06E2
    add sp, 8 ; @06E7
    call FadePaletteIn ; @06EA
    call WaitForScanChangeOrJoystickButton ; @06ED
    pop ax ; @06F0
    mov word ptr ds:[WaterYPixels], ax ; @06F1
    jmp near ptr FadePaletteOut ; @06F4
; CONTRACT (tools/apply.py)
; Draw the three fixed menu-header sprites through the VGA sprite renderer at 41FD.
; In: DS=DGROUP and initialized graphics. IDs D7/D8 draw at (10h,0)/(E3h,0),
; ID D6 at (61h,0). Out: AX=D6h, BX=61h, CX=0; tail-jumps to the final sprite draw.
; END CONTRACT
DrawMenuHeaderSprites:
    mov ax, 0D7h ; @06F7
    mov bx, 010h ; @06FA
    xor cx, cx ; @06FD
    call DrawTransparentSprite ; @06FF
    inc ax ; @0702
    mov bx, 0E3h ; @0703
    call DrawTransparentSprite ; @0706
    mov ax, 0D6h ; @0709
    mov bx, 061h ; @070C
    jmp near ptr DrawTransparentSprite ; @070F
; CONTRACT (tools/apply.py)
; Prepare attract background map 90 with the full 192-pixel display height and menu header.
; In: DS=DGROUP; sets line 2903=C0h, SI=7080h into unpacked maps and DI=1.
; Effects: shares tail 072A with 0720; decompresses tile maps, copies 320 bytes to 264C,
; renders the map, header and background pages. Skips the below-C0h animated-water step.
; END CONTRACT
PrepareAttractMap90:
    mov word ptr ds:[WaterYPixels], 0C0h ; @0712
    mov si, 07080h ; @0718
    mov di, 1 ; @071B
    jmp short loc_072A ; @071E
; CONTRACT (tools/apply.py)
; Prepare attract background map 0 with line 2903=B4h and no menu header.
; In: DS=DGROUP; SI=0, DI=0 feed shared body 072A, also entered by 0712.
; Effects: blacks the palette, clears video, restores base colors, decompresses tile maps,
; copies 320 bytes to DGROUP:264C, renders tiles and prepares page/background buffers.
; Quirk: executes animated water at 2DB9 only when signed line 2903 is below C0h.
; END CONTRACT
PrepareAttractMap0:
    mov word ptr ds:[WaterYPixels], 0B4h ; @0720
    xor si, si ; @0726
    xor di, di ; @0728
loc_072A:
    push di ; @072A
    push ds ; @072B
    push si ; @072C
    call BlackenVgaPalette ; @072D
    call ClearAllVgaPlanes ; @0730
    call DuplicateSourcePaletteHalves ; @0733
    lds si, dword ptr ds:[CompressedTileMapsPointer] ; @0736
    call UnpackIceToScratch ; @073A
    push es ; @073D
    pop ds ; @073E
    pop si ; @073F
    mov di, seg ext_5C09 ; @0740
    mov es, di ; @0743
    mov di, 0264Ch ; @0745
    mov cx, 0A0h ; @0748
    rep movsw ; @074B
    pop ds ; @074D
    call DrawTileMap ; @074E
    pop di ; @0751
    and di, di ; @0752
    je loc_075C ; @0754
    call DrawMenuHeaderSprites ; @0759
loc_075C:
    call SaveDrawPageBackground ; @075C
    call SwapAndDisplayVgaPage ; @075F
    call RestorePlayfieldBackground ; @0762
    cmp word ptr ds:[WaterYPixels], word ptr 0C0h ; @0765
    jge loc_0773 ; @076B
    call DrawWaterSurface ; @0770
loc_0773:
    jmp near ptr SwapAndDisplayVgaPage ; @0773
; CONTRACT (tools/apply.py)
; Draw successive text lines until a NUL byte ends the block.
; In: DS:SI encoded text, CX Y coordinate; forward direction expected.
; Out: SI past terminating NUL, AL=0 and ZF=1; CX includes all CR/FD line advances.
; Effects: repeats 077C while its returned ZF is clear; no FF sentinel handling here.
; END CONTRACT
DrawTextBlock:
    call DrawTextLine ; @0776
    jne short DrawTextBlock ; @0779
    ret ; @077B
; CONTRACT (tools/apply.py)
; Draw one encoded line as sprites, optionally centered by an initial FEh control byte.
; In: DS:SI text, CX Y coordinate; DF=0 expected. Ordinary lines begin at X=0.
; Out: SI past delimiter, AL=0/0Dh/FDh; ZF=1 only for NUL. CR adds 16 to CX, FD adds 8.
; Effects: characters use sprite index byte+237h and advance X by 16; 8E/99/9A map to 5B/5C/5D.
; Quirks: centering uses 16-bit (320 - (character_count<<4))>>1; no clipping/length guard.
; BP may change both in the centering scan and in the sprite callee; BX is the final X.
; END CONTRACT
DrawTextLine:
    xor bx, bx ; @077C
    lodsb ; @077E
    mov di, si ; @077F
    cmp al, 0FEh ; @0781
    jne loc_07AC ; @0783
    mov bp, 0FFFFh ; @0788
loc_078B:
    lodsb ; @078B
    inc bp ; @078C
    cmp al, 0 ; @078D
    je loc_079F ; @078F
    cmp al, 0Dh ; @0794
    je loc_079F ; @0796
    cmp al, 0FDh ; @079B
    jne short loc_078B ; @079D
loc_079F:
    shl bp, 4 ; @079F
    mov bx, 0140h ; @07A2
    sub bx, bp ; @07A5
    shr bx, 1 ; @07A7
    mov si, di ; @07A9
loc_07AB:
    lodsb ; @07AB
loc_07AC:
    cmp al, 0Dh ; @07AC
    je loc_07ED ; @07AE
    cmp al, 0FDh ; @07B3
    je loc_07F0 ; @07B5
    cmp al, 0 ; @07BA
    je loc_07F3 ; @07BC
    cmp al, 08Eh ; @07C1
    jne loc_07CC ; @07C3
    mov al, 05Bh ; @07C8
    jmp short loc_07E0 ; @07CA
loc_07CC:
    cmp al, 099h ; @07CC
    jne loc_07D7 ; @07CE
    mov al, 05Ch ; @07D3
    jmp short loc_07E0 ; @07D5
loc_07D7:
    cmp al, 09Ah ; @07D7
    jne loc_07E0 ; @07D9
    mov al, 05Dh ; @07DE
loc_07E0:
    xor ah, ah ; @07E0
    add ax, word ptr 0237h ; @07E2
    call DrawTransparentSprite ; @07E5
    add bx, 010h ; @07E8
    jmp short loc_07AB ; @07EB
loc_07ED:
    add cx, 8 ; @07ED
loc_07F0:
    add cx, 8 ; @07F0
loc_07F3:
    and al, al ; @07F3
    ret ; @07F5
; CONTRACT (tools/apply.py)
; Display successive NUL-terminated credits pages at DGROUP:091F, ending at an FF byte.
; In: DS=DGROUP, DF=0; initialized video, keyboard and joystick services.
; Out: AX=FFFF for Q, 1 for Escape, 0 for other input or end of pages; SF/ZF describe AX.
; Effects/quirks: page timeout advances; counts CR and FD equally when centering vertically.
; Draws the background/title sprites, swaps VGA pages, fades in/out and waits on retrace.
; END CONTRACT
ShowCreditsPages:
    mov word ptr ds:[WaterYPixels], 0C8h ; @07F6
    call DuplicateSourcePaletteHalves ; @07FC
    mov si, 091Fh ; @07FF
loc_0802:
    push si ; @0802
    mov cx, 028h ; @0803
    call WaitRetraceCount ; @0806
    call ClearAllVgaPlanes ; @0809
    call DrawMenuHeaderSprites ; @080C
    call SaveDrawPageBackground ; @080F
    call SwapAndDisplayVgaPage ; @0812
    call RestorePlayfieldBackground ; @0815
    pop si ; @0818
    mov di, si ; @0819
    xor bp, bp ; @081B
    cmp byte ptr [si], 0FFh ; @081D
    je loc_088A ; @0820
loc_0825:
    lodsb ; @0825
    cmp al, 0FDh ; @0826
    je loc_0834 ; @0828
    cmp al, 0Dh ; @082D
    jne loc_0837 ; @082F
loc_0834:
    inc bp ; @0834
    jmp short loc_0825 ; @0835
loc_0837:
    cmp al, 0 ; @0837
    jne short loc_0825 ; @0839
    inc bp ; @083B
    shl bp, 4 ; @083C
    mov cx, 090h ; @083F
    sub cx, bp ; @0842
    shr cx, 1 ; @0844
    add cx, 038h ; @0846
    mov si, di ; @0849
    call DrawTextBlock ; @084B
    push si ; @084E
    call SwapAndDisplayVgaPage ; @084F
    call FadePaletteIn ; @0852
    mov cx, 015Eh ; @0855
    call WaitForInputOrRetraceTimeout ; @0858
    pushf ; @085B
    push ax ; @085C
    call FadePaletteOut ; @085D
    pop ax ; @0860
    popf ; @0861
    pop si ; @0862
    jne loc_086A ; @0863
    jmp short loc_0802 ; @0868
loc_086A:
    and al, 07Fh ; @086A
    cmp al, 010h ; @086C
    je loc_087F ; @086E
    cmp al, 1 ; @0873
    je loc_0884 ; @0875
    jne loc_088A ; @087A
loc_087F:
    mov ax, 0FFFFh ; @087F
    jmp short loc_0887 ; @0882
loc_0884:
    mov ax, 1 ; @0884
loc_0887:
    and ax, ax ; @0887
    ret ; @0889
loc_088A:
    xor ax, ax ; @088A
    ret ; @088C
; CONTRACT (tools/apply.py)
; Play the two-script reveal scene at DGROUP:24DE on the standard demo background.
; In: DS=DGROUP, DF=0; shared video/input state initialized.
; Out: SF/ZF from RunScriptedDemo survive the final width restoration; AX is not its status.
; Effects/quirks: resets actor slot zero X to zero and restores sprite 214 width to 127 decimal.
; END CONTRACT
PlaySpriteRevealDemo:
    call PrepareAttractMap0 ; @088D
    mov si, 024DEh ; @0890
    call RunScriptedDemo ; @0893
    pushf ; @0896
    xor bx, bx ; @0897
    mov word ptr ds:[ActorX32], bx ; @0899
    call SetDemoRevealSpriteWidth ; @089D
    popf ; @08A0
    ret ; @08A1
; CONTRACT (tools/apply.py)
; Play the scripted scene selected after completing the available levels.
; In: DS=DGROUP, DF=0; called by the menu after its level-count comparison succeeds.
; Out: SF/ZF are the RunScriptedDemo exit status; other outputs follow that shared tail.
; Effects: stops the old track with control 11h; starts bank 3279 and script table 1020.
; END CONTRACT
PlayGameCompletionDemo:
    call PrepareAttractMap0 ; @08A2
    push 011h ; @08A5
    call far ptr _StopMusicTrack ; @08A7
    add sp, 2 ; @08AC
    push word ptr 0A5h ; @08AF
    push 0 ; @08B2
loc_08B4:
    push seg ext_3279 ; @08B4
    nop ; @08B7
    push 0 ; @08B8
loc_08BA:
    call far ptr _StartMusicTrack ; @08BA
    add sp, 8 ; @08BF
    mov si, 01020h ; @08C2
    jmp short RunScriptedDemo ; @08C5
; CONTRACT (tools/apply.py)
; Play script table 1792 before the password-selected game begins.
; In: DS=DGROUP, DF=0; the caller has already selected the starting level.
; Out: SF/ZF are the RunScriptedDemo exit status, although RunGameFromPassword ignores it.
; Effects: prepares the standard demo background and tail-jumps to RunScriptedDemo.
; END CONTRACT
PlayPreGameDemo:
    call PrepareAttractMap0 ; @08C7
    mov si, 01792h ; @08CA
    jmp short RunScriptedDemo ; @08CD
; CONTRACT (tools/apply.py)
; Play script table 1E40 in the menu's attract sequence, after the credits pages.
; In: DS=DGROUP, DF=0; initialized shared video/input state.
; Out: SF/ZF are the RunScriptedDemo exit status.
; Effects/quirks: prepares the alternate background, then falls through into RunScriptedDemo.
; END CONTRACT
PlayAttractDemo:
    call PrepareAttractMap90 ; @08CF
    mov si, 01E40h ; @08D2
; CONTRACT (tools/apply.py)
; Run a terminated vector of motion scripts, rendering and fading until finished or interrupted.
; In: DS:SI points to an FFFF-terminated vector of near script pointers; DF=0.
; Out: SF/ZF reflect DemoExitCode: FFFF=Q, 1=Escape, 0=finished/other key/joystick.
; Effects/quirks: returns flags from TEST of memory, not a promised AX result; uses VGA swaps,
; retrace pacing and palette fades. Any key-code change can end the scene, including releases.
; END CONTRACT
RunScriptedDemo:
    call InitializeDemoScripts ; @08D5
    xor ax, ax ; @08D8
    mov word ptr ds:[DemoExitCode], ax ; @08DA
    mov word ptr ds:[ScreenFadeLevel], ax ; @08DD
    mov word ptr ds:[ScreenFadeStep], 4 ; @08E0
    call PollKeyboardScanChange ; @08E6
loc_08E9:
    mov cx, word ptr ds:[ScreenFadeLevel] ; @08E9
    cmp cx, 0 ; @08ED
    jge loc_08F8 ; @08F0
    jmp near ptr loc_0982 ; @08F5
loc_08F8:
    cmp cx, word ptr 0100h ; @08F8
    jg loc_090E ; @08FC
    call ScaleAndUploadFadedPalette ; @0901
    add cx, word ptr ds:[ScreenFadeStep] ; @0904
    mov word ptr ds:[ScreenFadeLevel], cx ; @0908
    jmp short loc_0911 ; @090C
loc_090E:
    call WaitNextVerticalRetrace ; @090E
loc_0911:
    call EraseDemoSprites ; @0911
    cmp word ptr ds:[WaterYPixels], word ptr 0C0h ; @0914
    jge loc_0922 ; @091A
    call DrawWaterSurface ; @091F
loc_0922:
    call AdvanceDemoScripts ; @0922
    call DrawDemoSprites ; @0925
    call SwapAndDisplayVgaPage ; @0928
    call TestAllDemoScriptsFinished ; @092B
    jb loc_0968 ; @092E
    call SampleJoystickAxesAndButtons ; @0933
    jne loc_0962 ; @0936
    call PollKeyboardScanChange ; @093B
    and ah, ah ; @093E
    je short loc_08E9 ; @0940
    and al, 07Fh ; @0942
    cmp al, 010h ; @0944
    jne loc_0953 ; @0946
    mov word ptr ds:[DemoExitCode], 0FFFFh ; @094B
    jmp short loc_0968 ; @0951
loc_0953:
    cmp al, 1 ; @0953
    jne loc_0962 ; @0955
    mov word ptr ds:[DemoExitCode], 1 ; @095A
    jmp short loc_0968 ; @0960
loc_0962:
    mov word ptr ds:[DemoExitCode], 0 ; @0962
loc_0968:
    cmp word ptr ds:[ScreenFadeStep], 0 ; @0968
    jge loc_0975 ; @096D
    jmp near ptr loc_08E9 ; @0972
loc_0975:
    mov ax, 0FFFCh ; @0975
    mov word ptr ds:[ScreenFadeStep], ax ; @0978
    add word ptr ds:[ScreenFadeLevel], ax ; @097B
    jmp near ptr loc_08E9 ; @097F
loc_0982:
    test word ptr ds:[DemoExitCode], 0FFFFh ; @0982
    ret ; @0988
; CONTRACT (tools/apply.py)
; Script callback: start fading the scene when this slot selects hidden sprite 7FFF.
; In: DS=DGROUP; BX is a word-array byte index; current sprite is at BX+2BED.
; Out: if hidden, sets ScreenFadeStep=-4 and immediately adds it to ScreenFadeLevel.
; Clobbers/preserves: preserves BX and SI for the script interpreter; AX/flags may change.
; Effects/quirks: reached indirectly from script 1CBC, despite no direct call-graph callers.
; END CONTRACT
public StartDemoFadeWhenSpriteHidden
StartDemoFadeWhenSpriteHidden:
    cmp word ptr [bx + ActorSpriteIds], word ptr 07FFFh ; @0989
    jne loc_099E ; @098F
    mov ax, 0FFFCh ; @0994
    mov word ptr ds:[ScreenFadeStep], ax ; @0997
    add word ptr ds:[ScreenFadeLevel], ax ; @099A
loc_099E:
    ret ; @099E
; CONTRACT (tools/apply.py)
; Change sprite 214's directory width to reveal the visible portion of a moving demo sprite.
; In: DS=DGROUP; BX indexes the slot's X in 1/32-pixel units at BX+2AED; DF=0.
; Out: writes low byte of min_signed(320 decimal - (X SAR 5),127 decimal) via CS:462C.
; Clobbers/preserves: AX,CX,ES,DI/flags change; BX and SI survive the callback.
; Effects/quirks: no lower clamp; negative widths wrap to a byte. The pointed data is writable.
; END CONTRACT
public SetDemoRevealSpriteWidth
SetDemoRevealSpriteWidth:
    mov ax, 0140h ; @099F
    mov cx, word ptr [bx + ActorX32] ; @09A2
    sar cx, 5 ; @09A6
    sub ax, cx ; @09A9
    cmp ax, word ptr 07Fh ; @09AB
    jle loc_09B5 ; @09AE
    mov al, 07Fh ; @09B3
loc_09B5:
    les di, dword ptr cs:[DemoRevealWidthPointer] ; @09B5
    stosb ; @09BA
    ret ; @09BB
; CONTRACT (tools/apply.py)
; Test completion words for all motion scripts up to the FFFF script-pointer sentinel.
; In: DS=DGROUP; arrays initialized by InitializeDemoScripts.
; Out: CF=1 if every preceding completion word is nonzero (also for an empty vector), else CF=0.
; Clobbers/preserves: BX advances before testing BX+2A4B, which addresses the prior slot's flag.
; END CONTRACT
TestAllDemoScriptsFinished:
    xor bx, bx ; @09BC
loc_09BE:
    cmp word ptr [bx + ActorUpdateOrScriptCursor], -1 ; @09BE
    je loc_09D5 ; @09C3
    add bx, 2 ; @09C8
    test word ptr [bx + DemoCompletionScanBiasedBase], 0FFFFh ; @09CB
    jne short loc_09BE ; @09D1
    clc ; @09D3
    ret ; @09D4
loc_09D5:
    stc ; @09D5
    ret ; @09D6
; CONTRACT (tools/apply.py)
; Advance each due demo script, update its sprite/position, and invoke its near callback.
; In: DS=DGROUP, DF=0; script arrays have an FFFF pointer sentinel; callbacks preserve BX/SI.
; Out: countdowns, cursors, repeat state, sprites and fixed positions change; callbacks may fade.
; Effects/quirks: i8 deltas are sign-extended then multiplied by four with 16-bit wrapping.
; Negative words set repeat state; 8000 repeats toward zero or pins the cursor and marks finished.
; A zero period decrements through FFFF; there is no bounds check or malformed-script guard.
; END CONTRACT
AdvanceDemoScripts:
    xor bx, bx ; @09D7
loc_09D9:
    mov si, word ptr [bx + ActorUpdateOrScriptCursor] ; @09D9
    cmp si, -1 ; @09DD
    je loc_0A57 ; @09E0
    dec word ptr [bx + ActorAnimationCountdowns] ; @09E5
    jne loc_0A52 ; @09E9
    mov ax, word ptr [bx + ds_2C6D] ; @09EE
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @09F2
loc_09F6:
    lodsw ; @09F6
    cmp ax, word ptr 00h ; @09F7
    jl loc_0A1B ; @09FA
    mov word ptr [bx + ActorSpriteIds], ax ; @09FF
    lodsb ; @0A03
    cbw ; @0A04
    shl ax, 2 ; @0A05
    add word ptr [bx + ActorX32], ax ; @0A08
    lodsb ; @0A0C
    cbw ; @0A0D
    shl ax, 2 ; @0A0E
    add word ptr [bx + ActorY32], ax ; @0A11
    call word ptr [bx + ActorOverlayOrScriptCallbacks] ; @0A15
    jmp short loc_0A4E ; @0A19
loc_0A1B:
    cmp ax, word ptr 08000h ; @0A1B
    je loc_0A2D ; @0A1E
    mov word ptr [bx + ds_2ACD], ax ; @0A23
    mov word ptr [bx + ds_2A2D], si ; @0A27
    jmp short loc_09F6 ; @0A2B
loc_0A2D:
    mov ax, word ptr [bx + ds_2ACD] ; @0A2D
    and ax, ax ; @0A31
    je loc_0A45 ; @0A33
    inc ax ; @0A38
    mov word ptr [bx + ds_2ACD], ax ; @0A39
    je short loc_09F6 ; @0A3D
    mov si, word ptr [bx + ds_2A2D] ; @0A3F
    jmp short loc_09F6 ; @0A43
loc_0A45:
    sub si, 2 ; @0A45
    mov word ptr [bx + ActorPlatformOrScriptDone], 0FFFFh ; @0A48
loc_0A4E:
    mov word ptr [bx + ActorUpdateOrScriptCursor], si ; @0A4E
loc_0A52:
    add bx, 2 ; @0A52
    jmp short loc_09D9 ; @0A55
loc_0A57:
    ret ; @0A57
; CONTRACT (tools/apply.py)
; Draw visible demo sprites and advance their current/previous pixel-position caches.
; In: DS=DGROUP; the demo script-pointer array ends in FFFF; positions use 1/32-pixel units.
; Out: caches change only for sprites other than 7FFF; rendered pixels go to the VGA draw page.
; Effects/quirks: signed upper tests X<320 and Y<192 decimal; no lower-bound test here.
; END CONTRACT
DrawDemoSprites:
    xor si, si ; @0A58
loc_0A5A:
    cmp word ptr [si + ActorUpdateOrScriptCursor], -1 ; @0A5A
    je loc_0AB0 ; @0A5F
    mov ax, word ptr [si + ActorSpriteIds] ; @0A64
    cmp ax, word ptr 07FFFh ; @0A68
    je loc_0AAB ; @0A6B
    mov bx, word ptr [si + ActorPixelX] ; @0A70
    mov cx, word ptr [si + ActorPixelY] ; @0A74
    mov word ptr [si + ActorPreviousDrawX], bx ; @0A78
    mov word ptr [si + ActorPreviousDrawY], cx ; @0A7C
    mov bx, word ptr [si + ActorX32] ; @0A80
    sar bx, 5 ; @0A84
    mov word ptr [si + ActorPixelX], bx ; @0A87
    mov cx, word ptr [si + ActorY32] ; @0A8B
    sar cx, 5 ; @0A8F
    mov word ptr [si + ActorPixelY], cx ; @0A92
    cmp bx, word ptr 0140h ; @0A96
    jge loc_0AAB ; @0A9A
    cmp cx, word ptr 0C0h ; @0A9F
    jge loc_0AAB ; @0AA3
    call DrawTransparentSprite ; @0AA8
loc_0AAB:
    add si, 2 ; @0AAB
    jmp short loc_0A5A ; @0AAE
loc_0AB0:
    ret ; @0AB0
; CONTRACT (tools/apply.py)
; Restore demo sprite rectangles from the background, using the older draw-position cache.
; In: DS=DGROUP; FFFF-terminated demo script array, cached sprites and pixel positions.
; Out: copies each current sprite into its erase cache; skips old sprites FFFF and 7FFF.
; Effects: VGA background restoration through 43B9; sprite caches and positions are parallel arrays.
; END CONTRACT
EraseDemoSprites:
    xor si, si ; @0AB1
loc_0AB3:
    cmp word ptr [si + ActorUpdateOrScriptCursor], -1 ; @0AB3
    je loc_0AEA ; @0AB8
    mov ax, word ptr [si + ActorSpriteIds] ; @0ABD
    mov cx, word ptr [si + ActorEraseSprite] ; @0AC1
    mov word ptr [si + ActorEraseSprite], ax ; @0AC5
    cmp cx, -1 ; @0AC9
    je loc_0AE5 ; @0ACC
    cmp cx, word ptr 07FFFh ; @0AD1
    je loc_0AE5 ; @0AD5
    mov ax, word ptr [si + ActorPreviousDrawX] ; @0ADA
    mov bx, word ptr [si + ActorPreviousDrawY] ; @0ADE
    call RestoreSpriteBackground ; @0AE2
loc_0AE5:
    add si, 2 ; @0AE5
    jmp short loc_0AB3 ; @0AE8
loc_0AEA:
    ret ; @0AEA
; CONTRACT (tools/apply.py)
; Initialize motion slots from a near-pointer vector, clear sprite caches, execute first steps.
; In: DS:SI is an FFFF-terminated vector; scripts start with X,Y,period,near callback; DF=0.
; Script header X/Y are signed pixels, stored directly in pixel and previous-draw arrays.
; The initializer shifts those words left five for the live X32/Y32 fixed-point arrays.
; Out: positions, cursors, periods and completion/repeat words initialized.
; Effects: resets actor/enemy/item sprite caches; tail-jumps to AdvanceDemoScripts.
; Quirk: no capacity check; the vector and sentinel must fit the sixteen-slot parallel arrays.
; END CONTRACT
InitializeDemoScripts:
    xor bx, bx ; @0AEB
loc_0AED:
    mov di, word ptr [bx + si] ; @0AED
    cmp di, -1 ; @0AEF
    je loc_0B44 ; @0AF2
    mov ax, word ptr [di] ; @0AF7
    mov word ptr [bx + ActorPixelX], ax ; @0AF9
    mov word ptr [bx + ActorPreviousDrawX], ax ; @0AFD
    shl ax, 5 ; @0B01
    mov word ptr [bx + ActorX32], ax ; @0B04
    mov ax, word ptr [di + 2] ; @0B08
    mov word ptr [bx + ActorPixelY], ax ; @0B0B
    mov word ptr [bx + ActorPreviousDrawY], ax ; @0B0F
    shl ax, 5 ; @0B13
    mov word ptr [bx + ActorY32], ax ; @0B16
    mov ax, word ptr [di + 4] ; @0B1A
    mov word ptr [bx + ds_2C6D], ax ; @0B1D
    mov ax, word ptr [di + 6] ; @0B21
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], ax ; @0B24
    add di, 8 ; @0B28
    mov word ptr [bx + ActorUpdateOrScriptCursor], di ; @0B2B
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @0B2F
    xor ax, ax ; @0B35
    mov word ptr [bx + ds_2ACD], ax ; @0B37
    mov word ptr [bx + ActorPlatformOrScriptDone], ax ; @0B3B
    add bx, 2 ; @0B3F
    jmp short loc_0AED ; @0B42
loc_0B44:
    mov word ptr [bx + ActorUpdateOrScriptCursor], di ; @0B44
    call ResetSpriteEraseState ; @0B48
    jmp near ptr AdvanceDemoScripts ; @0B4B
; CONTRACT (tools/apply.py)
; Unreferenced one-instruction RET seed; its intended application role is not established.
; Out: returns without changing registers or flags; no caller ABI is inferred from this seed.
; END CONTRACT
loc_0B4E:
    ret ; @0B4E
; CONTRACT (tools/apply.py)
; Set current/erase sprite words to FFFF for five enemies, sixteen actors and twelve falling items.
; In: DS=DGROUP; these are parallel word arrays, not interleaved records.
; Out: sprite words reset only; positions, script pointers and callbacks are not initialized here.
; Clobbers/preserves: AX=FFFF and SI=FFFE on return; arithmetic flags change.
; END CONTRACT
ResetSpriteEraseState:
    mov ax, 0FFFFh ; @0B4F
    mov si, 8 ; @0B52
loc_0B55:
    mov word ptr [si + EnemySpriteIds], ax ; @0B55
    mov word ptr [si + EnemyEraseSprite], ax ; @0B59
    sub si, 2 ; @0B5D
    jns short loc_0B55 ; @0B60
    mov si, 01Eh ; @0B62
loc_0B65:
    mov word ptr [si + ActorSpriteIds], ax ; @0B65
    mov word ptr [si + ActorEraseSprite], ax ; @0B69
    sub si, 2 ; @0B6D
    jns short loc_0B65 ; @0B70
    mov si, 016h ; @0B72
loc_0B75:
    mov word ptr [si + FallingItemSprites], ax ; @0B75
    mov word ptr [si + FallingItemEraseSprite], ax ; @0B79
    sub si, 2 ; @0B7D
    jns short loc_0B75 ; @0B80
    ret ; @0B82
; CONTRACT (tools/apply.py)
; Expand and display one packed picture, fade in, wait for input/timeout, and fade out.
; In: SI is the picture bank segment; CX is the retrace-count timeout; DS=DGROUP.
; Out: AX=1 for Escape, FFFF for Q, 0 otherwise; SF/ZF reflect AX, including timeout.
; Effects: decompresses the picture/palette, writes planar VGA pixels and swaps the display page.
; END CONTRACT
ShowPackedPictureAndWait:
    push cx ; @0B83
    call UnpackPictureAndCopyPalette ; @0B84
    call UploadChunkyImageToVgaPlanes ; @0B87
    call SwapAndDisplayVgaPage ; @0B8A
    call FadePaletteIn ; @0B8D
    pop cx ; @0B90
    call WaitForInputOrRetraceTimeout ; @0B91
    push ax ; @0B94
    call FadePaletteOut ; @0B95
    pop ax ; @0B98
    and al, 07Fh ; @0B99
    cmp al, 1 ; @0B9B
    je loc_0BB2 ; @0B9D
    cmp al, 010h ; @0BA2
    je loc_0BAD ; @0BA4
    xor ax, ax ; @0BA9
    jmp short loc_0BB5 ; @0BAB
loc_0BAD:
    mov ax, 0FFFFh ; @0BAD
    jmp short loc_0BB5 ; @0BB0
loc_0BB2:
    mov ax, 1 ; @0BB2
loc_0BB5:
    and ax, ax ; @0BB5
    ret ; @0BB7
; CONTRACT (tools/apply.py)
; Show startup pictures from banks 2D9A,2BF6,2F9E,2FB7 with per-picture timeouts.
; In: DS=DGROUP; graphics and input initialized by startup.
; Out: timeout continues, Escape skips the remaining pictures, Q exits through 4EE6 without return.
; Effects: the Q path cleans up sound/keyboard, restores BIOS video mode and exits DOS.
; END CONTRACT
ShowStartupPictures:
    mov si, seg ext_2D9A ; @0BB8
    nop ; @0BBB
    mov cx, 0118h ; @0BBC
    call ShowPackedPictureAndWait ; @0BBF
    js loc_0C04 ; @0BC2
    jne loc_0C03 ; @0BC7
    mov si, seg ext_2BF6 ; @0BCC
    nop ; @0BCF
    mov cx, 0118h ; @0BD0
    call ShowPackedPictureAndWait ; @0BD3
    js loc_0C04 ; @0BD6
    jne loc_0C03 ; @0BDB
    mov si, seg ext_2F9E ; @0BE0
    nop ; @0BE3
    mov cx, 08Ch ; @0BE4
    call ShowPackedPictureAndWait ; @0BE7
    js loc_0C04 ; @0BEA
    jne loc_0C03 ; @0BEF
    mov si, seg ext_2FB7 ; @0BF4
    nop ; @0BF7
    mov cx, 01A4h ; @0BF8
    call ShowPackedPictureAndWait ; @0BFB
    js loc_0C04 ; @0BFE
loc_0C03:
    ret ; @0C03
loc_0C04:
    jmp near ptr loc_4EE6 ; @0C04
; CONTRACT (tools/apply.py)
; Select a level from the entered password and run gameplay across retries and subsequent levels.
; In: DS=DGROUP, DF=0; player count, password edit field and configuration already set.
; Out: returns after lives are exhausted, Escape, or the selected player mode's level count is met.
; Effects: owns the erase/input/move/update/draw/swap loop; starts/stops music and controls fades.
; Quirks: ignores the pre-game demo result; player movement repeats on equality after BX+=2.
; Pause polls raw make/break code transitions; shared fade direction also signals life/level exit.
; END CONTRACT
RunGameFromPassword:
    xor cx, cx ; @0C07
    mov bx, word ptr ds:[PlayerArrayBytes] ; @0C09
    mov si, word ptr [bx + 0E8h] ; @0C0D
loc_0C11:
    xor bx, bx ; @0C11
    xor bp, bp ; @0C13
loc_0C15:
    lodsb ; @0C15
    and al, al ; @0C16
    je loc_0C2E ; @0C18
    cmp al, 0FFh ; @0C1D
    je loc_0C38 ; @0C1F
    inc bx ; @0C24
    cmp al, byte ptr [bx + PasswordCompareBiasedBase] ; @0C25
    je short loc_0C15 ; @0C29
    dec bp ; @0C2B
    jmp short loc_0C15 ; @0C2C
loc_0C2E:
    and bp, bp ; @0C2E
    je loc_0C3C ; @0C30
loc_0C35:
    inc cx ; @0C35
    jmp short loc_0C11 ; @0C36
loc_0C38:
    xor cx, cx ; @0C38
    jmp short loc_0C50 ; @0C3A
loc_0C3C:
    cmp bx, 014h ; @0C3C
    nop ; @0C3F
    jae loc_0C50 ; @0C40
    mov al, 020h ; @0C45
    cmp byte ptr [bx + PasswordEditBuffer], al ; @0C47
    jne short loc_0C35 ; @0C4B
    inc bx ; @0C4D
    jmp short loc_0C3C ; @0C4E
loc_0C50:
    mov word ptr ds:[CurrentLevelIndex], cx ; @0C50
    call PlayPreGameDemo ; @0C54
    push 011h ; @0C57
loc_0C59:
    call far ptr _StopMusicTrack ; @0C59
    add sp, 2 ; @0C5E
    call ResetScoreLivesAndMultiplier ; @0C61
    call BlackenVgaPalette ; @0C64
loc_0C67:
    call InitializeLevelDisplay ; @0C67
    push word ptr 0A5h ; @0C6A
    push 0 ; @0C6D
loc_0C6F:
    push seg ext_3444 ; @0C6F
    nop ; @0C72
    push 0 ; @0C73
loc_0C75:
    call far ptr _StartMusicTrack ; @0C75
    add sp, 8 ; @0C7A
loc_0C7D:
    mov cx, word ptr ds:[ScreenFadeLevel] ; @0C7D
    cmp cx, 0 ; @0C81
    jge loc_0C8C ; @0C84
    jmp near ptr loc_0FA7 ; @0C89
loc_0C8C:
    cmp cx, word ptr 0100h ; @0C8C
    jg loc_0CA2 ; @0C90
    call ScaleAndUploadFadedPalette ; @0C95
    add cx, word ptr ds:[ScreenFadeStep] ; @0C98
    mov word ptr ds:[ScreenFadeLevel], cx ; @0C9C
    jmp short loc_0CA5 ; @0CA0
loc_0CA2:
    call WaitNextVerticalRetrace ; @0CA2
loc_0CA5:
    call RefreshHudAndTimerBar ; @0CA5
    xor bx, bx ; @0CA8
loc_0CAA:
    call RestorePlayerBackground ; @0CAA
    add bx, 2 ; @0CAD
    cmp bx, word ptr ds:[PlayerArrayBytes] ; @0CB0
    jne short loc_0CAA ; @0CB4
    xor si, si ; @0CB6
loc_0CB8:
    cmp word ptr [si + ActorDescriptors], -1 ; @0CB8
    je loc_0D14 ; @0CBD
    mov ax, word ptr [si + ActorSpriteIds] ; @0CC2
    mov cx, word ptr [si + ActorEraseSprite] ; @0CC6
    mov word ptr [si + ActorEraseSprite], ax ; @0CCA
    cmp cx, -1 ; @0CCE
    je loc_0D0F ; @0CD1
    mov ax, word ptr [si + ActorPreviousDrawX] ; @0CD6
    mov bx, word ptr [si + ActorPreviousDrawY] ; @0CDA
    cmp bx, word ptr 0C0h ; @0CDE
    jge loc_0D0F ; @0CE2
    call RestoreSpriteBackground ; @0CE7
    mov ax, word ptr [si + ActorOverlayOrScriptCallbacks] ; @0CEA
    mov cx, word ptr [si + ActorEraseOverlaySprite] ; @0CEE
    mov word ptr [si + ActorEraseOverlaySprite], ax ; @0CF2
    cmp cx, -1 ; @0CF6
    je loc_0D0F ; @0CF9
    mov ax, word ptr [si + ActorPreviousDrawX] ; @0CFE
    add ax, word ptr 0Bh ; @0D02
    mov bx, word ptr [si + ActorPreviousDrawY] ; @0D05
    add bx, -0Dh ; @0D09
    call RestoreSpriteBackground ; @0D0C
loc_0D0F:
    add si, 2 ; @0D0F
    jmp short loc_0CB8 ; @0D12
loc_0D14:
    xor si, si ; @0D14
loc_0D16:
    cmp word ptr [si + EnemyDescriptors], -1 ; @0D16
    je loc_0D44 ; @0D1B
    mov ax, word ptr [si + EnemySpriteIds] ; @0D20
    mov cx, word ptr [si + EnemyEraseSprite] ; @0D24
    mov word ptr [si + EnemyEraseSprite], ax ; @0D28
    cmp cx, -1 ; @0D2C
    je loc_0D3F ; @0D2F
    mov ax, word ptr [si + EnemyPreviousDrawX] ; @0D34
    mov bx, word ptr [si + EnemyPreviousDrawY] ; @0D38
    call RestoreSpriteBackground ; @0D3C
loc_0D3F:
    add si, 2 ; @0D3F
    jmp short loc_0D16 ; @0D42
loc_0D44:
    mov si, 016h ; @0D44
loc_0D47:
    mov ax, word ptr [si + FallingItemSprites] ; @0D47
    mov cx, word ptr [si + FallingItemEraseSprite] ; @0D4B
    mov word ptr [si + FallingItemEraseSprite], ax ; @0D4F
    cmp cx, -1 ; @0D53
    je loc_0D66 ; @0D56
    mov ax, word ptr [si + FallingItemPreviousDrawX] ; @0D5B
    mov bx, word ptr [si + FallingItemPreviousDrawY] ; @0D5F
    call RestoreSpriteBackground ; @0D63
loc_0D66:
    sub si, 2 ; @0D66
    jns short loc_0D47 ; @0D69
    cmp byte ptr ds:[LevelRainDirection], 0 ; @0D6B
    je loc_0D78 ; @0D70
    call RestoreRainBackground ; @0D75
loc_0D78:
    call AdvanceWaterSurface ; @0D78
    call PollPlayerControls ; @0D7B
    cmp al, 019h ; @0D7E
    jne loc_0D9A ; @0D80
loc_0D85:
    call PollKeyboardScanChange ; @0D85
    cmp al, 099h ; @0D88
    jne short loc_0D85 ; @0D8A
loc_0D8C:
    call PollKeyboardScanChange ; @0D8C
    test al, 0FFh ; @0D8F
    js short loc_0D8C ; @0D91
loc_0D93:
    call PollKeyboardScanChange ; @0D93
    test al, 0FFh ; @0D96
    jns short loc_0D93 ; @0D98
loc_0D9A:
    cmp al, 1 ; @0D9A
    jne loc_0DBB ; @0D9C
    mov byte ptr ds:[LivesRemaining], 0 ; @0DA1
    nop ; @0DA6
    cmp word ptr ds:[ScreenFadeStep], 0 ; @0DA7
    jl loc_0DBB ; @0DAC
    mov ax, 0FFFEh ; @0DB1
    mov word ptr ds:[ScreenFadeStep], ax ; @0DB4
    add word ptr ds:[ScreenFadeLevel], ax ; @0DB7
loc_0DBB:
    cmp word ptr ds:[ScreenFadeLevel], word ptr 0C0h ; @0DBB
    jg loc_0DD0 ; @0DC1
    cmp word ptr ds:[ScreenFadeStep], 0 ; @0DC6
    jg loc_0DDE ; @0DCB
loc_0DD0:
    xor bx, bx ; @0DD0
loc_0DD2:
    call MovePlayerWithVgaCollisions ; @0DD2
    add bx, 2 ; @0DD5
    cmp bx, word ptr ds:[PlayerCount] ; @0DD8
    je short loc_0DD2 ; @0DDC
loc_0DDE:
    call DispatchActorUpdates ; @0DDE
    call DispatchEnemyStates ; @0DE1
    call DispatchFallingItems ; @0DE4
    xor si, si ; @0DE7
loc_0DE9:
    cmp word ptr [si + ActorDescriptors], -1 ; @0DE9
    je loc_0E3E ; @0DEE
    mov ax, word ptr [si + ActorSpriteIds] ; @0DF3
    cmp ax, word ptr 0FFFFh ; @0DF7
    je loc_0E39 ; @0DFA
    mov bx, word ptr [si + ActorPixelX] ; @0DFF
    mov cx, word ptr [si + ActorPixelY] ; @0E03
    mov word ptr [si + ActorPreviousDrawX], bx ; @0E07
    mov word ptr [si + ActorPreviousDrawY], cx ; @0E0B
    mov bx, word ptr [si + ActorX32] ; @0E0F
    sar bx, 5 ; @0E13
    mov word ptr [si + ActorPixelX], bx ; @0E16
    mov cx, word ptr [si + ActorY32] ; @0E1A
    sar cx, 5 ; @0E1E
    mov word ptr [si + ActorPixelY], cx ; @0E21
    cmp cx, word ptr 0C0h ; @0E25
    jge loc_0E39 ; @0E29
    cmp cx, -0Bh ; @0E2E
    jle loc_0E39 ; @0E31
    call DrawTransparentSprite ; @0E36
loc_0E39:
    add si, 2 ; @0E39
    jmp short loc_0DE9 ; @0E3C
loc_0E3E:
    xor si, si ; @0E3E
loc_0E40:
    mov ax, word ptr [si + EnemyDescriptors] ; @0E40
    cmp ax, word ptr 0FFFFh ; @0E44
    je loc_0E9F ; @0E47
    cmp ax, word ptr 076E4h ; @0E4C
    je loc_0E5C ; @0E4F
    cmp ax, word ptr 076A8h ; @0E54
    jne loc_0E9A ; @0E57
loc_0E5C:
    mov ax, word ptr [si + EnemySpriteIds] ; @0E5C
    cmp ax, word ptr 0FFFFh ; @0E60
    je loc_0E9A ; @0E63
    mov bx, word ptr [si + EnemyDrawX] ; @0E68
    mov cx, word ptr [si + EnemyDrawY] ; @0E6C
    mov word ptr [si + EnemyPreviousDrawX], bx ; @0E70
    mov word ptr [si + EnemyPreviousDrawY], cx ; @0E74
    mov bx, word ptr [si + EnemyX32] ; @0E78
    sar bx, 5 ; @0E7C
    mov word ptr [si + EnemyDrawX], bx ; @0E7F
    mov cx, word ptr [si + EnemyY32] ; @0E83
    sar cx, 5 ; @0E87
    mov word ptr [si + EnemyDrawY], cx ; @0E8A
    cmp cx, word ptr 0C0h ; @0E8E
    jge loc_0E9A ; @0E92
    call DrawTransparentSprite ; @0E97
loc_0E9A:
    add si, 2 ; @0E9A
    jmp short loc_0E40 ; @0E9D
loc_0E9F:
    xor bx, bx ; @0E9F
loc_0EA1:
    call AnimateAndDrawPlayer ; @0EA1
    add bx, 2 ; @0EA4
    cmp bx, word ptr ds:[PlayerArrayBytes] ; @0EA7
    jne short loc_0EA1 ; @0EAB
    xor si, si ; @0EAD
loc_0EAF:
    mov ax, word ptr [si + EnemyDescriptors] ; @0EAF
    cmp ax, word ptr 0FFFFh ; @0EB3
    je loc_0F0E ; @0EB6
    cmp ax, word ptr 076E4h ; @0EBB
    je loc_0F09 ; @0EBE
    cmp ax, word ptr 076A8h ; @0EC3
    je loc_0F09 ; @0EC6
    mov ax, word ptr [si + EnemySpriteIds] ; @0ECB
    cmp ax, word ptr 0FFFFh ; @0ECF
    je loc_0F09 ; @0ED2
    mov bx, word ptr [si + EnemyDrawX] ; @0ED7
    mov cx, word ptr [si + EnemyDrawY] ; @0EDB
    mov word ptr [si + EnemyPreviousDrawX], bx ; @0EDF
    mov word ptr [si + EnemyPreviousDrawY], cx ; @0EE3
    mov bx, word ptr [si + EnemyX32] ; @0EE7
    sar bx, 5 ; @0EEB
    mov word ptr [si + EnemyDrawX], bx ; @0EEE
    mov cx, word ptr [si + EnemyY32] ; @0EF2
    sar cx, 5 ; @0EF6
    mov word ptr [si + EnemyDrawY], cx ; @0EF9
    cmp cx, word ptr 0C0h ; @0EFD
    jge loc_0F09 ; @0F01
    call DrawTransparentSprite ; @0F06
loc_0F09:
    add si, 2 ; @0F09
    jmp short loc_0EAF ; @0F0C
loc_0F0E:
    mov si, 016h ; @0F0E
loc_0F11:
    mov ax, word ptr [si + FallingItemSprites] ; @0F11
    cmp ax, word ptr 0FFFFh ; @0F15
    je loc_0F4F ; @0F18
    mov bx, word ptr [si + FallingItemDrawX] ; @0F1D
    mov cx, word ptr [si + FallingItemDrawY] ; @0F21
    mov word ptr [si + FallingItemPreviousDrawX], bx ; @0F25
    mov word ptr [si + FallingItemPreviousDrawY], cx ; @0F29
    mov bx, word ptr [si + FallingItemX] ; @0F2D
    sar bx, 5 ; @0F31
    mov word ptr [si + FallingItemDrawX], bx ; @0F34
    mov cx, word ptr [si + FallingItemY] ; @0F38
    sar cx, 5 ; @0F3C
    mov word ptr [si + FallingItemDrawY], cx ; @0F3F
    cmp cx, word ptr 0C0h ; @0F43
    jge loc_0F4F ; @0F47
    call DrawTransparentSprite ; @0F4C
loc_0F4F:
    sub si, 2 ; @0F4F
    jns short loc_0F11 ; @0F52
    xor si, si ; @0F54
loc_0F56:
    cmp word ptr [si + ActorDescriptors], -1 ; @0F56
    je loc_0F8E ; @0F5B
    mov ax, word ptr [si + ActorSpriteIds] ; @0F60
    cmp ax, word ptr 0FFFFh ; @0F64
    je loc_0F89 ; @0F67
    mov ax, word ptr [si + ActorOverlayOrScriptCallbacks] ; @0F6C
    cmp ax, word ptr 0FFFFh ; @0F70
    je loc_0F89 ; @0F73
    mov bx, word ptr [si + ActorPixelX] ; @0F78
    add bx, 0Bh ; @0F7C
    mov cx, word ptr [si + ActorPixelY] ; @0F7F
    add cx, -0Dh ; @0F83
    call DrawTransparentSprite ; @0F86
loc_0F89:
    add si, 2 ; @0F89
    jmp short loc_0F56 ; @0F8C
loc_0F8E:
    cmp byte ptr ds:[LevelRainDirection], 0 ; @0F8E
    je loc_0F9E ; @0F93
    call AdvanceRainParticles ; @0F98
    call DrawRainParticles ; @0F9B
loc_0F9E:
    call DrawWaterSurface ; @0F9E
    call SwapAndDisplayVgaPage ; @0FA1
    jmp near ptr loc_0C7D ; @0FA4
loc_0FA7:
    push 011h ; @0FA7
loc_0FA9:
    call far ptr _StopMusicTrack ; @0FA9
    add sp, 2 ; @0FAE
    test byte ptr ds:[LevelCompletionMarker], 0FFh ; @0FB1
    nop ; @0FB6
    js loc_0FD3 ; @0FB7
    dec byte ptr ds:[LivesRemaining] ; @0FBC
    je loc_0FE7 ; @0FC0
    js loc_0FE7 ; @0FC5
    mov byte ptr ds:[ScoreMultiplier], 1 ; @0FCA
    nop ; @0FCF
loc_0FD0:
    jmp near ptr loc_0C67 ; @0FD0
loc_0FD3:
    mov ax, word ptr ds:[CurrentLevelIndex] ; @0FD3
    inc ax ; @0FD6
    mov word ptr ds:[CurrentLevelIndex], ax ; @0FD7
    mov bx, word ptr ds:[PlayerArrayBytes] ; @0FDA
    sub bx, 2 ; @0FDE
    cmp ax, word ptr [bx + LevelCountsByPlayerMode] ; @0FE1
    jb short loc_0FD0 ; @0FE5
loc_0FE7:
    ret ; @0FE7
; CONTRACT (tools/apply.py)
; Poll keyboard state and map each joystick-controlled player's axes/buttons into action words.
; In: DS=DGROUP; control selectors, joystick thresholds and keyboard ISR action bytes initialized.
; Out: AL=current keyboard scan code, AH=scan-code XOR change bits; keyboard-mode actions retained.
; Effects/quirks: joystick-mode actions become 0/FFFF words; keyboard ISR writes only action bytes.
; After BX+=2, repeats only while BX equals the player-count value; preserve this equality branch.
; END CONTRACT
PollPlayerControls:
    call PollKeyboardScanChange ; @0FE8
    test word ptr ds:[PlayerOneControlMode], 0FFFFh ; @0FEB
    jns loc_100B ; @0FF1
    test word ptr ds:[PlayerTwoControlMode], 0FFFFh ; @0FF6
    js loc_100E ; @0FFC
    cmp word ptr ds:[PlayerCount], 2 ; @1001
    jne loc_100E ; @1006
loc_100B:
    call SampleJoystickAxesAndButtons ; @100B
loc_100E:
    xor bx, bx ; @100E
loc_1010:
    mov si, word ptr [bx + PlayerOneControlMode] ; @1010
    shl si, 1 ; @1014
    and si, si ; @1016
    js loc_1084 ; @1018
    xor ax, ax ; @101D
    mov word ptr [bx + PlayerUpInput], ax ; @101F
    mov word ptr [bx + PlayerDownInput], ax ; @1023
    mov word ptr [bx + PlayerLeftInput], ax ; @1027
    mov word ptr [bx + PlayerRightInput], ax ; @102B
    mov word ptr [bx + PlayerActionInput], ax ; @102F
    mov ax, word ptr [si + FirstJoystickXCount] ; @1033
    cmp ax, word ptr [si + JoystickLeftThresholds] ; @1037
    jg loc_1046 ; @103B
    dec word ptr [bx + PlayerLeftInput] ; @1040
    jmp short loc_1053 ; @1044
loc_1046:
    cmp ax, word ptr [si + JoystickRightThresholds] ; @1046
    jl loc_1053 ; @104A
    dec word ptr [bx + PlayerRightInput] ; @104F
loc_1053:
    mov ax, word ptr [si + FirstJoystickYCount] ; @1053
    cmp ax, word ptr [si + JoystickUpThresholds] ; @1057
    jg loc_1066 ; @105B
    dec word ptr [bx + PlayerUpInput] ; @1060
    jmp short loc_1073 ; @1064
loc_1066:
    cmp ax, word ptr [si + JoystickDownThresholds] ; @1066
    jl loc_1073 ; @106A
    dec word ptr [bx + PlayerDownInput] ; @106F
loc_1073:
    test word ptr [si + JoystickButtonBits], 0FFFFh ; @1073
    je loc_1084 ; @1079
    dec word ptr [bx + PlayerActionInput] ; @107E
    jmp short loc_1084 ; @1082
loc_1084:
    add bx, 2 ; @1084
    cmp bx, word ptr ds:[PlayerCount] ; @1087
    je short loc_1010 ; @108B
    mov al, byte ptr ds:[CurrentKeyboardScanCode] ; @108D
    mov ah, byte ptr ds:[KeyboardScanCodeChangeBits] ; @1090
    ret ; @1094
; CONTRACT (tools/apply.py)
; Integrate one player's thrust, water effects and movement, with VGA-pixel collision/landing tests.
; In: DS=DGROUP; BX=0 or 2 selects the player; positions, velocities, actions and level state set.
; Out: fixed/pixel positions, velocities, platform attachment, impact and animation rate updated.
; Clobbers/preserves: preserves BX/DS; AX,CX,DX,SI,DI,BP,ES and flags change.
; Effects: programs VGA graphics-controller read map at 3CE/3CF; tests palette-index bit 7.
; Quirks: signed SAR and 16-bit wrap are required; left/up collision scans reuse one sample address.
; Impact at or above the difficulty limit starts a -2 fade only if the current fade step is >=0.
; END CONTRACT
MovePlayerWithVgaCollisions:
    dec word ptr ds:[LevelTimer] ; @1095
    xor ax, ax ; @1099
    mov word ptr [bx + PlayerImpactMagnitude], ax ; @109B
    mov word ptr [bx + PlayerThrustAnimationRate], ax ; @109F
    mov cx, word ptr [bx + PlayerYPixels] ; @10A3
    sub cx, word ptr ds:[WaterYPixels] ; @10A7
    add cx, 012h ; @10AB
    js loc_10BA ; @10AE
    je loc_10BA ; @10B3
    mov ch, 1 ; @10B8
loc_10BA:
    test word ptr [bx + PlayerPlatformIndices], 0FFFFh ; @10BA
    jns loc_122A ; @10C0 JUMPS expansion
loc_10C5:
    test ch, 0FFh ; @10C5
    jns loc_10F1 ; @10C8
    mov al, byte ptr ds:[LevelRainDirection] ; @10CD
    and al, al ; @10D0
    je loc_10F1 ; @10D2
    xor ah, ah ; @10D7
    dec ax ; @10D9
    shl ax, 1 ; @10DA
    dec ax ; @10DC
    shl ax, 5 ; @10DD
    add word ptr [bx + PlayerHorizontalVelocities], ax ; @10E0
    sar ax, 1 ; @10E4
    jns loc_10ED ; @10E6
    neg ax ; @10EB
loc_10ED:
    add word ptr [bx + PlayerVerticalVelocities], ax ; @10ED
loc_10F1:
    mov ax, word ptr [bx + PlayerHorizontalVelocities] ; @10F1
    test word ptr [bx + PlayerLeftInput], 0FFFFh ; @10F5
    je loc_110A ; @10FB
    sub ax, word ptr 03Fh ; @1100
    add word ptr [bx + PlayerThrustAnimationRate], 03Fh ; @1103
    jmp short loc_111D ; @1108
loc_110A:
    test word ptr [bx + PlayerRightInput], 0FFFFh ; @110A
    je loc_111D ; @1110
    add ax, word ptr 03Fh ; @1115
    add word ptr [bx + PlayerThrustAnimationRate], 03Fh ; @1118
loc_111D:
    and ax, word ptr 0FFFFh ; @111D
    jns loc_1132 ; @1120
    cmp ax, word ptr 0E800h ; @1125
    jge loc_113D ; @1128
    mov ax, 0E800h ; @112D
    jmp short loc_113D ; @1130
loc_1132:
    cmp ax, word ptr 01800h ; @1132
    jle loc_113D ; @1135
    mov ax, 01800h ; @113A
loc_113D:
    mov word ptr [bx + PlayerHorizontalVelocities], ax ; @113D
    sar ax, 6 ; @1141
    add ax, word ptr [bx + PlayerX32] ; @1144
    cmp ax, word ptr 0FE00h ; @1148
    jge loc_1155 ; @114B
    mov ax, 0FE00h ; @1150
    jmp short loc_1160 ; @1153
loc_1155:
    cmp ax, word ptr 02600h ; @1155
    jle loc_1166 ; @1158
    mov ax, 02600h ; @115D
loc_1160:
    mov word ptr [bx + PlayerHorizontalVelocities], 0 ; @1160
loc_1166:
    mov di, ax ; @1166
    push cx ; @1168
    mov ax, word ptr [bx + PlayerYPixels] ; @1169
    imul word ptr ds:[VgaRowStrideBytes] ; @116D
    mov si, word ptr [bx + PlayerPixelX] ; @1171
    add si, 5 ; @1175
    sar si, 2 ; @1178
    add ax, si ; @117B
    les si, dword ptr cs:[BackgroundPagePointer] ; @117D
    add si, ax ; @1182
    mov dx, 03CEh ; @1184
    mov al, 4 ; @1187
    out dx, al ; @1189
    inc dx ; @118A
    mov ax, word ptr [bx + PlayerPixelX] ; @118B
    add ax, word ptr 025h ; @118F
    and ax, word ptr 03h ; @1192
    mov cl, al ; @1195
    out dx, al ; @1197
    mov bp, di ; @1198
    mov ax, di ; @119A
    sar ax, 5 ; @119C
    cmp ax, word ptr [bx + PlayerPixelX] ; @119F
    je loc_121E ; @11A3
    mov bp, word ptr [bx + PlayerX32] ; @11A8
    cmp di, bp ; @11AC
    jg loc_11DA ; @11AE
    dec cl ; @11B3
    jns loc_11BE ; @11B5
    and cl, 3 ; @11BA
    dec si ; @11BD
loc_11BE:
    mov al, cl ; @11BE
    out dx, al ; @11C0
loc_11C1:
    call SamplePlayerCollisionPixels ; @11C1
    jns loc_11D1 ; @11C4
    and bp, 0FFE0h ; @11C9
    add bp, 020h ; @11CC
    jmp short loc_1201 ; @11CF
loc_11D1:
    sub bp, 020h ; @11D1
    cmp bp, di ; @11D4
    jg short loc_11C1 ; @11D6
    jmp short loc_121C ; @11D8
loc_11DA:
    inc cl ; @11DA
    cmp cl, 4 ; @11DC
    jb loc_11E8 ; @11DF
    and cl, 3 ; @11E4
    inc si ; @11E7
loc_11E8:
    mov al, cl ; @11E8
    out dx, al ; @11EA
    call SamplePlayerCollisionPixels ; @11EB
    jns loc_11F8 ; @11EE
    and bp, 0FFE0h ; @11F3
    jmp short loc_1201 ; @11F6
loc_11F8:
    add bp, 020h ; @11F8
    cmp bp, di ; @11FB
    jl short loc_11DA ; @11FD
    jmp short loc_121C ; @11FF
loc_1201:
    mov ax, word ptr [bx + PlayerHorizontalVelocities] ; @1201
    neg ax ; @1205
    sar ax, 1 ; @1207
    mov word ptr [bx + PlayerHorizontalVelocities], ax ; @1209
    shl ax, 1 ; @120D
    jns loc_1216 ; @120F
    neg ax ; @1214
loc_1216:
    mov word ptr [bx + PlayerImpactMagnitude], ax ; @1216
    jmp short loc_121E ; @121A
loc_121C:
    mov bp, di ; @121C
loc_121E:
    mov word ptr [bx + PlayerX32], bp ; @121E
    sar bp, 5 ; @1222
    mov word ptr [bx + PlayerPixelX], bp ; @1225
    pop cx ; @1229
loc_122A:
    mov ax, word ptr [bx + PlayerVerticalVelocities] ; @122A
    and ch, 0FFh ; @122E
    js loc_1258 ; @1231
    je loc_1280 ; @1236
    sub word ptr ds:[LevelTimer], 2 ; @123B
    cmp ax, word ptr 00h ; @1240
    jle loc_124D ; @1243
    sub ax, word ptr 0C1h ; @1248
    jmp short loc_129E ; @124B
loc_124D:
    sub ax, word ptr 015h ; @124D
    mov word ptr [bx + PlayerPlatformIndices], 0FFFFh ; @1250
    jmp short loc_129E ; @1256
loc_1258:
    test word ptr [bx + PlayerPlatformIndices], 0FFFFh ; @1258
    jns loc_1280 ; @125E
    add ax, word ptr 01Bh ; @1263
    sub word ptr ds:[LevelTimer], 2 ; @1266
    test word ptr [bx + PlayerDownInput], 0FFFFh ; @126B
    je loc_1280 ; @1271
    add ax, word ptr 046h ; @1276
    add word ptr [bx + PlayerThrustAnimationRate], 05Ah ; @1279
    jmp short loc_129E ; @127E
loc_1280:
    test word ptr [bx + PlayerUpInput], 0FFFFh ; @1280
    je loc_129E ; @1286
    sub word ptr ds:[LevelTimer], 3 ; @128B
    sub ax, word ptr 046h ; @1290
    add word ptr [bx + PlayerThrustAnimationRate], 05Ah ; @1293
    mov word ptr [bx + PlayerPlatformIndices], 0FFFFh ; @1298
loc_129E:
    and ax, word ptr 0FFFFh ; @129E
    jns loc_12B3 ; @12A1
    cmp ax, word ptr 0E800h ; @12A6
    jge loc_12BE ; @12A9
    mov ax, 0E800h ; @12AE
    jmp short loc_12BE ; @12B1
loc_12B3:
    cmp ax, word ptr 01800h ; @12B3
    jle loc_12BE ; @12B6
    mov ax, 01800h ; @12BB
loc_12BE:
    mov word ptr [bx + PlayerVerticalVelocities], ax ; @12BE
    sar ax, 6 ; @12C2
    add ax, word ptr [bx + PlayerY32] ; @12C5
    cmp ax, word ptr 0FDA0h ; @12C9
    jge loc_12D6 ; @12CC
    mov ax, 0FDA0h ; @12D1
    jmp short loc_12E1 ; @12D4
loc_12D6:
    cmp ax, word ptr 017E0h ; @12D6
    jle loc_12E7 ; @12D9
    mov ax, 017E0h ; @12DE
loc_12E1:
    mov word ptr [bx + PlayerVerticalVelocities], 0 ; @12E1
loc_12E7:
    and ch, 0FFh ; @12E7
    js loc_1319 ; @12EA
    je loc_1319 ; @12EF
    mov dx, ax ; @12F4
    sar dx, 5 ; @12F6
    sub dx, word ptr ds:[WaterYPixels] ; @12F9
    add dx, 012h ; @12FD
    je loc_130A ; @1300
    jns loc_1319 ; @1305
loc_130A:
    mov word ptr [bx + PlayerVerticalVelocities], 0 ; @130A
    mov ax, word ptr ds:[WaterYPixels] ; @1310
    shl ax, 5 ; @1313
    sub ax, word ptr 0240h ; @1316
loc_1319:
    mov di, ax ; @1319
    mov dx, 03CEh ; @131B
    mov al, 4 ; @131E
    out dx, al ; @1320
    inc dx ; @1321
    mov ax, word ptr [bx + PlayerPixelX] ; @1322
    add ax, word ptr 025h ; @1326
    and ax, word ptr 03h ; @1329
    out dx, al ; @132C
    mov ax, word ptr [bx + PlayerYPixels] ; @132D
    imul word ptr ds:[VgaRowStrideBytes] ; @1331
    mov si, word ptr [bx + PlayerPixelX] ; @1335
    add si, 5 ; @1339
    sar si, 2 ; @133C
    add ax, si ; @133F
    les si, dword ptr cs:[BackgroundPagePointer] ; @1341
    add si, ax ; @1346
    mov bp, di ; @1348
    mov ax, di ; @134A
    sar ax, 5 ; @134C
    cmp ax, word ptr [bx + PlayerYPixels] ; @134F
    je loc_1424 ; @1353 JUMPS expansion
loc_1358:
    mov bp, word ptr [bx + PlayerY32] ; @1358
    cmp di, bp ; @135C
    jg loc_1380 ; @135E
    sub si, 060h ; @1363
loc_1366:
    call SamplePlayerCollisionPixels ; @1366
    jns loc_1376 ; @1369
    and bp, 0FFE0h ; @136E
    add bp, 020h ; @1371
    jmp short loc_139A ; @1374
loc_1376:
    sub bp, 020h ; @1376
    cmp bp, di ; @1379
    jg short loc_1366 ; @137B
    jmp near ptr loc_1422 ; @137D
loc_1380:
    add si, 060h ; @1380
    call SamplePlayerCollisionPixels ; @1383
    jns loc_1390 ; @1386
    and bp, 0FFE0h ; @138B
    jmp short loc_139A ; @138E
loc_1390:
    add bp, 020h ; @1390
    cmp bp, di ; @1393
    jl short loc_1380 ; @1395
    jmp near ptr loc_1422 ; @1397
loc_139A:
    mov ax, word ptr [bx + PlayerVerticalVelocities] ; @139A
    neg ax ; @139E
    sar ax, 1 ; @13A0
    mov word ptr [bx + PlayerVerticalVelocities], ax ; @13A2
    shl ax, 1 ; @13A6
    jns loc_13AF ; @13A8
    neg ax ; @13AD
loc_13AF:
    cmp ax, word ptr [bx + PlayerImpactMagnitude] ; @13AF
    jle loc_13BC ; @13B3
    mov word ptr [bx + PlayerImpactMagnitude], ax ; @13B8
loc_13BC:
    test word ptr [bx + PlayerVerticalVelocities], 0FFFFh ; @13BC
    jns loc_1424 ; @13C2
    mov ax, word ptr [bx + PlayerImpactMagnitude] ; @13C7
    mov si, word ptr ds:[SelectedDifficulty] ; @13CB
    shl si, 1 ; @13CF
    cmp ax, word ptr [si + PlayerImpactLimits] ; @13D1
    jge loc_1424 ; @13D5
    xor si, si ; @13DA
    mov ax, bp ; @13DC
    sar ax, 5 ; @13DE
    add ax, word ptr 014h ; @13E1
loc_13E4:
    test word ptr [si + PlatformLeftEdges], 0FFFFh ; @13E4
    js loc_1424 ; @13EA
    cmp word ptr [si + PlatformHeights], ax ; @13EF
    je loc_13FD ; @13F3
loc_13F8:
    add si, 2 ; @13F8
    jmp short loc_13E4 ; @13FB
loc_13FD:
    mov cx, word ptr [bx + PlayerPixelX] ; @13FD
    add cx, 010h ; @1401
    cmp cx, word ptr [si + PlatformLeftEdges] ; @1404
    jl short loc_13F8 ; @1408
    cmp cx, word ptr [si + PlatformRightEdges] ; @140A
    jg short loc_13F8 ; @140E
    shr si, 1 ; @1410
    mov word ptr [bx + PlayerPlatformIndices], si ; @1412
    xor ax, ax ; @1416
    mov word ptr [bx + PlayerHorizontalVelocities], ax ; @1418
    mov word ptr [bx + PlayerVerticalVelocities], ax ; @141C
    jmp short loc_1424 ; @1420
loc_1422:
    mov bp, di ; @1422
loc_1424:
    mov word ptr [bx + PlayerY32], bp ; @1424
    sar bp, 5 ; @1428
    mov word ptr [bx + PlayerYPixels], bp ; @142B
    mov ax, word ptr [bx + PlayerImpactMagnitude] ; @142F
    mov si, word ptr ds:[SelectedDifficulty] ; @1433
    shl si, 1 ; @1437
    cmp ax, word ptr [si + PlayerImpactLimits] ; @1439
    jl loc_1456 ; @143D
    cmp word ptr ds:[ScreenFadeStep], 0 ; @1442
    jl loc_1456 ; @1447
    mov ax, 0FFFEh ; @144C
    mov word ptr ds:[ScreenFadeStep], ax ; @144F
    add word ptr ds:[ScreenFadeLevel], ax ; @1452
loc_1456:
    ret ; @1456
; CONTRACT (tools/apply.py)
; OR ten player collision samples in the currently selected VGA read plane.
; In: ES:SI is the upper-left plane byte; caller selected read-map plane; row stride is 60h bytes.
; Out: AL is the OR; SF tests any pixel's bit 7, ZF tests all-zero; CF=OF=0 from the final OR.
; Clobbers/preserves: changes only AL/flags; does not advance SI or select/restore the VGA plane.
; END CONTRACT
SamplePlayerCollisionPixels:
    mov al, byte ptr es:[si] ; @1457
    or al, byte ptr es:[si + 3] ; @145A
    or al, byte ptr es:[si + 5] ; @145E
    or al, byte ptr es:[si + 0720h] ; @1462
    or al, byte ptr es:[si + 0723h] ; @1467
    or al, byte ptr es:[si + 0725h] ; @146C
    or al, byte ptr es:[si + 0240h] ; @1471
    or al, byte ptr es:[si + 0245h] ; @1476
    or al, byte ptr es:[si + 0480h] ; @147B
    or al, byte ptr es:[si + 0485h] ; @1480
    ret ; @1485
; CONTRACT (tools/apply.py)
; Invoke each active actor's near state-update callback until the descriptor sentinel FFFF.
; In: DS=DGROUP; actor descriptors at 29AD and callbacks at 2A0D; callbacks preserve BX iteration.
; Out: actor-specific state changes; no combined status or callee register preservation implied.
; Effects/quirks: BX is a byte index into parallel word arrays, not a record pointer.
; 2A0D holds code pointers here but bytecode cursors during demos; do not unify the two uses.
; END CONTRACT
DispatchActorUpdates:
    xor bx, bx ; @1486
loc_1488:
    cmp word ptr [bx + ActorDescriptors], -1 ; @1488
    je loc_149B ; @148D
    call word ptr [bx + ActorUpdateOrScriptCursor] ; @1492
    add bx, 2 ; @1496
    jmp short loc_1488 ; @1499
loc_149B:
    ret ; @149B
; CONTRACT (tools/apply.py)
; Read the next passenger journey leg, or retire a completed passenger.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: source/destination platform indices and delay; FFFF destination hides the actor.
; Effects: completion decrements the byte objective count unless DEC sets SF; zero starts fade-out.
; Effects: an exhausted journey installs and tail-jumps to descriptor callback +2C.
; END CONTRACT
public ReadPassengerJourneyLeg
ReadPassengerJourneyLeg:
    mov di, word ptr [bx + ActorJourneyCursors] ; @149C
    mov ax, word ptr [di + 4] ; @14A0
    cmp ax, word ptr 0FFFFh ; @14A3
    jne loc_14DD ; @14A6
    mov al, byte ptr ds:[RemainingPassengerJourneys] ; @14AB
    dec al ; @14AE
    js loc_14CA ; @14B0
    mov byte ptr ds:[RemainingPassengerJourneys], al ; @14B5
    jne loc_14CA ; @14B8
    mov ax, 0FFFEh ; @14BD
    mov word ptr ds:[ScreenFadeStep], ax ; @14C0
    add word ptr ds:[ScreenFadeLevel], ax ; @14C3
    mov byte ptr ds:[LevelCompletionMarker], al ; @14C7
loc_14CA:
    mov word ptr [bx + ActorSpriteIds], 0FFFFh ; @14CA
    mov si, word ptr [bx + ActorDescriptors] ; @14D0
    mov ax, word ptr [si + 02Ch] ; @14D4
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @14D7
    jmp ax ; @14DB
loc_14DD:
    mov word ptr [bx + ActorDestinationPlatforms], ax ; @14DD
    shl ax, 1 ; @14E1
    mov word ptr [bx + ActorDestinationPlatformByteIndices], ax ; @14E3
    mov ax, word ptr [di] ; @14E7
    mov word ptr [bx + ActorPlatformOrScriptDone], ax ; @14E9
    shl ax, 1 ; @14ED
    mov word ptr [bx + ActorSourcePlatformByteIndices], ax ; @14EF
    mov ax, word ptr [di + 2] ; @14F3
    call ScaleLevelSpeedToThreeHalves ; @14F6
    mov word ptr [bx + ds_2ACD], ax ; @14F9
    mov si, word ptr [bx + ActorDescriptors] ; @14FD
    mov ax, word ptr [si + 0Ah] ; @1501
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1504
    ret ; @1508
; CONTRACT (tools/apply.py)
; Wait for the journey delay and a free source platform.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: hides the actor; decrements nonzero delay, then tail-jumps through descriptor +0C.
; Effects: the platform occupant must equal FFFF; zero delay is immediately eligible.
; END CONTRACT
public WaitForPassengerPlatform
WaitForPassengerPlatform:
    mov word ptr [bx + ActorSpriteIds], 0FFFFh ; @1509
    mov ax, word ptr [bx + ds_2ACD] ; @150F
    cmp ax, word ptr 00h ; @1513
    je loc_1525 ; @1516
    dec ax ; @151B
    mov word ptr [bx + ds_2ACD], ax ; @151C
    jne loc_153A ; @1520
loc_1525:
    mov di, word ptr [bx + ActorSourcePlatformByteIndices] ; @1525
    cmp word ptr [di + PlatformActorOccupants], -1 ; @1529
    jne loc_153A ; @152E
    mov si, word ptr [bx + ActorDescriptors] ; @1533
    jmp word ptr [si + 0Ch] ; @1537
loc_153A:
    ret ; @153A
; CONTRACT (tools/apply.py)
; Claim the source platform and place the passenger at its arrival point.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: installs descriptor +0E; writes pixel and x32 positions, animation offset FFFE/ticks 1.
; Effects: platform occupant stores BX, a byte index into actor parallel arrays.
; END CONTRACT
public PlacePassengerOnPlatform
PlacePassengerOnPlatform:
    mov si, word ptr [bx + ActorDescriptors] ; @153B
    mov ax, word ptr [si + 0Eh] ; @153F
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1542
    mov di, word ptr [bx + ActorSourcePlatformByteIndices] ; @1546
    mov word ptr [di + PlatformActorOccupants], bx ; @154A
    mov ax, word ptr [si + 2] ; @154E
    neg ax ; @1551
    add ax, word ptr [di + PlatformHeights] ; @1553
    mov word ptr [bx + ActorPixelY], ax ; @1557
    shl ax, 5 ; @155B
    mov word ptr [bx + ActorY32], ax ; @155E
    mov ax, word ptr [si] ; @1562
    neg ax ; @1564
    add ax, word ptr [di + PlatformArrivalPointsX] ; @1566
    mov word ptr [bx + ActorPixelX], ax ; @156A
    shl ax, 5 ; @156E
    mov word ptr [bx + ActorX32], ax ; @1571
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @1575
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @157B
    ret ; @1581
; CONTRACT (tools/apply.py)
; Play the passenger arrival sequence before entering platform waiting.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: on countdown expiry selects descriptor +36 animation; FFFF tail-jumps through +10.
; Effects: the sprite is not changed on frames where the countdown remains nonzero.
; END CONTRACT
public AnimatePassengerArrival
AnimatePassengerArrival:
    dec word ptr [bx + ActorAnimationCountdowns] ; @1582
    jne loc_15B3 ; @1586
    mov si, word ptr [bx + ActorDescriptors] ; @158B
    mov ax, word ptr [si + 03Eh] ; @158F
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @1592
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @1596
    mov di, word ptr [si + 036h] ; @159B
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @159E
    mov ax, word ptr [di] ; @15A2
    cmp ax, word ptr 0FFFFh ; @15A4
    jne loc_15AF ; @15A7
    jmp word ptr [si + 010h] ; @15AC
loc_15AF:
    mov word ptr [bx + ActorSpriteIds], ax ; @15AF
loc_15B3:
    ret ; @15B3
; CONTRACT (tools/apply.py)
; Enter passenger platform waiting with no overlay.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: installs descriptor +12; resets animation to offset FFFE/ticks 1.
; Effects: writes FFFF to both state scratch and overlay fields.
; END CONTRACT
public BeginPassengerPlatformWait
BeginPassengerPlatformWait:
    mov si, word ptr [bx + ActorDescriptors] ; @15B4
    mov ax, word ptr [si + 012h] ; @15B8
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @15BB
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @15BF
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @15C5
    mov ax, 0FFFFh ; @15CB
    mov word ptr [bx + ds_2A2D], ax ; @15CE
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], ax ; @15D2
    ret ; @15D6
; CONTRACT (tools/apply.py)
; Walk to the platform waiting point and look for an empty player vehicle.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: animates/moves one pixel per animation tick; may tail-jump to request or water state.
; Effects: tests water against cached pixel Y; collision helper returns SF and player platform AX.
; END CONTRACT
public UpdatePassengerPlatformWait
UpdatePassengerPlatformWait:
    mov di, word ptr [bx + ActorSourcePlatformByteIndices] ; @15D7
    mov si, word ptr [bx + ActorDescriptors] ; @15DB
    mov ax, word ptr [si + 2] ; @15DF
    sar ax, 1 ; @15E2
    add ax, word ptr [bx + ActorPixelY] ; @15E4
    sub ax, word ptr ds:[WaterYPixels] ; @15E8
    js loc_1617 ; @15EC
    mov ax, word ptr ds:[WaterYPixels] ; @15F1
    add ax, word ptr [si + 2] ; @15F4
    shl ax, 5 ; @15F7
    mov word ptr [bx + ActorY32], ax ; @15FA
    mov di, word ptr [bx + ActorSourcePlatformByteIndices] ; @15FE
    mov ax, 0FFFFh ; @1602
    mov word ptr [di + PlatformActorOccupants], ax ; @1605
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], ax ; @1609
    mov si, word ptr [si + 048h] ; @160D
    mov word ptr [bx + ActorDescriptors], si ; @1610
    jmp word ptr [si + 8] ; @1614
loc_1617:
    dec word ptr [bx + ActorAnimationCountdowns] ; @1617
    jne loc_16B6 ; @161B JUMPS expansion
loc_1620:
    mov ax, word ptr [si + 03Eh] ; @1620
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @1623
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @1627
    mov ax, word ptr [bx + ActorPixelX] ; @162C
    add ax, word ptr [si] ; @1630
    cmp ax, word ptr [di + PlatformWaitingPointsX] ; @1632
    je loc_168E ; @1636
    mov word ptr [bx + ds_2A2D], 0 ; @163B
    jl loc_166A ; @1641
loc_1646:
    mov di, word ptr [si + 032h] ; @1646
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @1649
    mov ax, word ptr [di] ; @164D
    cmp ax, word ptr 0FFFFh ; @164F
    jne loc_165F ; @1652
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @1657
    jmp short loc_1646 ; @165D
loc_165F:
    mov word ptr [bx + ActorSpriteIds], ax ; @165F
    sub word ptr [bx + ActorX32], 020h ; @1663
    jmp short loc_16B6 ; @1668
loc_166A:
    mov di, word ptr [si + 034h] ; @166A
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @166D
    mov ax, word ptr [di] ; @1671
    cmp ax, word ptr 0FFFFh ; @1673
    jne loc_1683 ; @1676
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @167B
    jmp short loc_166A ; @1681
loc_1683:
    mov word ptr [bx + ActorSpriteIds], ax ; @1683
    add word ptr [bx + ActorX32], 020h ; @1687
    jmp short loc_16B6 ; @168C
loc_168E:
    cmp word ptr [bx + ds_2A2D], 1 ; @168E
    je loc_169E ; @1693
loc_1698:
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @1698
loc_169E:
    mov di, word ptr [si + 02Eh] ; @169E
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @16A1
    mov ax, word ptr [di] ; @16A5
    cmp ax, word ptr 0FFFFh ; @16A7
    je short loc_1698 ; @16AA
    mov word ptr [bx + ActorSpriteIds], ax ; @16AC
    mov word ptr [bx + ds_2A2D], 1 ; @16B0
loc_16B6:
    call FindPlayerTouchingActor ; @16B6
    js loc_16D0 ; @16B9
    cmp ax, word ptr 0FFFFh ; @16BE
    jne loc_16D0 ; @16C1
    mov si, word ptr [si + 048h] ; @16C6
    mov word ptr [bx + ActorDescriptors], si ; @16C9
    jmp word ptr [si + 8] ; @16CD
loc_16D0:
    mov ax, word ptr [bx + ActorPlatformOrScriptDone] ; @16D0
    xor di, di ; @16D4
loc_16D6:
    cmp ax, word ptr [di + PlayerPlatformIndices] ; @16D6
    jne loc_16EC ; @16DA
    cmp word ptr [di + PlayerCarriedKinds], 0 ; @16DF
    jne loc_16EC ; @16E4
    jmp word ptr [si + 014h] ; @16E9
loc_16EC:
    add di, 2 ; @16EC
    cmp di, word ptr ds:[PlayerArrayBytes] ; @16EF
    jne short loc_16D6 ; @16F3
    ret ; @16F5
; CONTRACT (tools/apply.py)
; Start the timed destination bubble for a waiting passenger.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: installs descriptor +16, resets animation, and starts a 140-update state countdown.
; Effects: overlay is destination+010C, capped to sprite 0111 by an unsigned comparison.
; END CONTRACT
public BeginPassengerDestinationDisplay
BeginPassengerDestinationDisplay:
    mov si, word ptr [bx + ActorDescriptors] ; @16F6
    mov ax, word ptr [si + 016h] ; @16FA
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @16FD
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @1701
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @1707
    mov ax, word ptr [bx + ActorDestinationPlatforms] ; @170D
    add ax, word ptr 010Ch ; @1711
    cmp ax, word ptr 0112h ; @1714
    jb loc_171F ; @1717
    mov ax, 0111h ; @171C
loc_171F:
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], ax ; @171F
    mov word ptr [bx + ds_2A2D], 08Ch ; @1723
    ret ; @1729
; CONTRACT (tools/apply.py)
; Animate a destination request while an empty vehicle remains on the source platform.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: water/contact can switch descriptor; missing/occupied vehicle jumps through +18.
; Effects: a 140-update countdown ends at descriptor +1C, independently of animation ticks.
; END CONTRACT
public UpdatePassengerDestinationDisplay
UpdatePassengerDestinationDisplay:
    mov si, word ptr [bx + ActorDescriptors] ; @172A
    mov ax, word ptr [si + 2] ; @172E
    sar ax, 1 ; @1731
    add ax, word ptr [bx + ActorPixelY] ; @1733
    sub ax, word ptr ds:[WaterYPixels] ; @1737
    js loc_1766 ; @173B
    mov ax, word ptr ds:[WaterYPixels] ; @1740
    add ax, word ptr [si + 2] ; @1743
    shl ax, 5 ; @1746
    mov word ptr [bx + ActorY32], ax ; @1749
    mov di, word ptr [bx + ActorSourcePlatformByteIndices] ; @174D
    mov ax, 0FFFFh ; @1751
    mov word ptr [di + PlatformActorOccupants], ax ; @1754
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], ax ; @1758
    mov si, word ptr [si + 048h] ; @175C
    mov word ptr [bx + ActorDescriptors], si ; @175F
    jmp word ptr [si + 8] ; @1763
loc_1766:
    call FindPlayerTouchingActor ; @1766
    js loc_1780 ; @1769
    cmp ax, word ptr 0FFFFh ; @176E
    jne loc_1780 ; @1771
    mov si, word ptr [si + 048h] ; @1776
    mov word ptr [bx + ActorDescriptors], si ; @1779
    jmp word ptr [si + 8] ; @177D
loc_1780:
    mov ax, word ptr [bx + ActorPlatformOrScriptDone] ; @1780
    xor di, di ; @1784
loc_1786:
    cmp ax, word ptr [di + PlayerPlatformIndices] ; @1786
    jne loc_179B ; @178A
    cmp word ptr [di + PlayerCarriedKinds], 0 ; @178F
    jne loc_17A4 ; @1794
    jmp short loc_17A7 ; @1799
loc_179B:
    add di, 2 ; @179B
    cmp di, word ptr ds:[PlayerArrayBytes] ; @179E
    jne short loc_1786 ; @17A2
loc_17A4:
    jmp word ptr [si + 018h] ; @17A4
loc_17A7:
    dec word ptr [bx + ActorAnimationCountdowns] ; @17A7
    jne loc_17D9 ; @17AB
    mov ax, word ptr [si + 03Eh] ; @17B0
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @17B3
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @17B7
loc_17BC:
    mov di, word ptr [si + 030h] ; @17BC
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @17BF
    mov ax, word ptr [di] ; @17C3
    cmp ax, word ptr 0FFFFh ; @17C5
    jne loc_17D5 ; @17C8
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @17CD
    jmp short loc_17BC ; @17D3
loc_17D5:
    mov word ptr [bx + ActorSpriteIds], ax ; @17D5
loc_17D9:
    dec word ptr [bx + ds_2A2D] ; @17D9
    jne loc_17E5 ; @17DD
    jmp word ptr [si + 01Ch] ; @17E2
loc_17E5:
    ret ; @17E5
; CONTRACT (tools/apply.py)
; Start the passenger question bubble and its timeout.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: installs descriptor +1A; sets overlay sprite 0112 and state countdown 140.
; Effects: animation offset FFFE and ticks 1 force the first frame on the next update.
; END CONTRACT
public BeginPassengerQuestionDisplay
BeginPassengerQuestionDisplay:
    mov si, word ptr [bx + ActorDescriptors] ; @17E6
    mov ax, word ptr [si + 01Ah] ; @17EA
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @17ED
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @17F1
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @17F7
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], 0112h ; @17FD
    mov word ptr [bx + ds_2A2D], 08Ch ; @1803
    ret ; @1809
; CONTRACT (tools/apply.py)
; Animate the question bubble, then retry pickup or return to waiting.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: handles water/contact, advances descriptor +30 animation, and decrements state timer.
; Effects: at exactly zero, an empty vehicle on source platform selects +14; otherwise +10.
; END CONTRACT
public UpdatePassengerQuestionDisplay
UpdatePassengerQuestionDisplay:
    mov si, word ptr [bx + ActorDescriptors] ; @180A
    mov ax, word ptr [si + 2] ; @180E
    sar ax, 1 ; @1811
    add ax, word ptr [bx + ActorPixelY] ; @1813
    sub ax, word ptr ds:[WaterYPixels] ; @1817
    js loc_1846 ; @181B
    mov ax, word ptr ds:[WaterYPixels] ; @1820
    add ax, word ptr [si + 2] ; @1823
    shl ax, 5 ; @1826
    mov word ptr [bx + ActorY32], ax ; @1829
    mov di, word ptr [bx + ActorSourcePlatformByteIndices] ; @182D
    mov ax, 0FFFFh ; @1831
    mov word ptr [di + PlatformActorOccupants], ax ; @1834
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], ax ; @1838
    mov si, word ptr [si + 048h] ; @183C
    mov word ptr [bx + ActorDescriptors], si ; @183F
    jmp word ptr [si + 8] ; @1843
loc_1846:
    call FindPlayerTouchingActor ; @1846
    js loc_1860 ; @1849
    cmp ax, word ptr 0FFFFh ; @184E
    jne loc_1860 ; @1851
    mov si, word ptr [si + 048h] ; @1856
    mov word ptr [bx + ActorDescriptors], si ; @1859
    jmp word ptr [si + 8] ; @185D
loc_1860:
    dec word ptr [bx + ActorAnimationCountdowns] ; @1860
    jne loc_1892 ; @1864
    mov ax, word ptr [si + 03Eh] ; @1869
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @186C
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @1870
loc_1875:
    mov di, word ptr [si + 030h] ; @1875
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @1878
    mov ax, word ptr [di] ; @187C
    cmp ax, word ptr 0FFFFh ; @187E
    jne loc_188E ; @1881
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @1886
    jmp short loc_1875 ; @188C
loc_188E:
    mov word ptr [bx + ActorSpriteIds], ax ; @188E
loc_1892:
    dec word ptr [bx + ds_2A2D] ; @1892
    jne loc_18C7 ; @1896
    mov di, word ptr [bx + ActorSourcePlatformByteIndices] ; @189B
    mov ax, word ptr [bx + ActorPlatformOrScriptDone] ; @189F
    xor di, di ; @18A3
loc_18A5:
    cmp ax, word ptr [di + PlayerPlatformIndices] ; @18A5
    jne loc_18BB ; @18A9
    cmp word ptr [di + PlayerCarriedKinds], 0 ; @18AE
    jne loc_18BB ; @18B3
    jmp word ptr [si + 014h] ; @18B8
loc_18BB:
    add di, 2 ; @18BB
    cmp di, word ptr ds:[PlayerArrayBytes] ; @18BE
    jne short loc_18A5 ; @18C2
    jmp word ptr [si + 010h] ; @18C4
loc_18C7:
    ret ; @18C7
; CONTRACT (tools/apply.py)
; Start walking toward a player vehicle without an overlay.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: installs descriptor +1E and resets animation offset FFFE/ticks 1; overlay becomes FFFF.
; END CONTRACT
public BeginPassengerApproach
BeginPassengerApproach:
    mov si, word ptr [bx + ActorDescriptors] ; @18C8
    mov ax, word ptr [si + 01Eh] ; @18CC
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @18CF
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @18D3
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @18D9
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], 0FFFFh ; @18DF
    ret ; @18E5
; CONTRACT (tools/apply.py)
; Walk the passenger toward a vehicle on the source platform.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: when actor anchor X equals player pixel X+16, tail-jumps through descriptor +20.
; Effects: platform loss selects +18; movement is one pixel only when animation ticks expire.
; Effects: water/contact may swap the descriptor and tail-jump to its +08 callback.
; END CONTRACT
public UpdatePassengerApproach
UpdatePassengerApproach:
    mov si, word ptr [bx + ActorDescriptors] ; @18E6
    mov ax, word ptr [si + 2] ; @18EA
    sar ax, 1 ; @18ED
    add ax, word ptr [bx + ActorPixelY] ; @18EF
    sub ax, word ptr ds:[WaterYPixels] ; @18F3
    js loc_1922 ; @18F7
    mov ax, word ptr ds:[WaterYPixels] ; @18FC
    add ax, word ptr [si + 2] ; @18FF
    shl ax, 5 ; @1902
    mov word ptr [bx + ActorY32], ax ; @1905
    mov di, word ptr [bx + ActorSourcePlatformByteIndices] ; @1909
    mov ax, 0FFFFh ; @190D
    mov word ptr [di + PlatformActorOccupants], ax ; @1910
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], ax ; @1914
    mov si, word ptr [si + 048h] ; @1918
    mov word ptr [bx + ActorDescriptors], si ; @191B
    jmp word ptr [si + 8] ; @191F
loc_1922:
    call FindPlayerTouchingActor ; @1922
    js loc_193C ; @1925
    cmp ax, word ptr 0FFFFh ; @192A
    jne loc_193C ; @192D
    mov si, word ptr [si + 048h] ; @1932
    mov word ptr [bx + ActorDescriptors], si ; @1935
    jmp word ptr [si + 8] ; @1939
loc_193C:
    mov ax, word ptr [bx + ActorPlatformOrScriptDone] ; @193C
    xor di, di ; @1940
loc_1942:
    cmp ax, word ptr [di + PlayerPlatformIndices] ; @1942
    je loc_1957 ; @1946
    add di, 2 ; @194B
    cmp di, word ptr ds:[PlayerArrayBytes] ; @194E
    jne short loc_1942 ; @1952
    jmp word ptr [si + 018h] ; @1954
loc_1957:
    xor cx, cx ; @1957
    dec word ptr [bx + ActorAnimationCountdowns] ; @1959
    jne loc_196F ; @195D
    mov ax, word ptr [si + 03Eh] ; @1962
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @1965
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @1969
    inc cx ; @196E
loc_196F:
    mov ax, word ptr [bx + ActorPixelX] ; @196F
    add ax, word ptr [si] ; @1973
    sub ax, word ptr 010h ; @1975
    cmp ax, word ptr [di + PlayerPixelX] ; @1978
    jg loc_1989 ; @197C
    jl loc_19B5 ; @1981
    jmp word ptr [si + 020h] ; @1986
loc_1989:
    mov di, word ptr [si + 032h] ; @1989
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @198C
    mov ax, word ptr [di] ; @1990
    cmp ax, word ptr 0FFFFh ; @1992
    jne loc_19A2 ; @1995
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @199A
    jmp short loc_1989 ; @19A0
loc_19A2:
    mov word ptr [bx + ActorSpriteIds], ax ; @19A2
    and cx, 0FFFFh ; @19A6
    je loc_19DF ; @19A9
    sub word ptr [bx + ActorX32], 020h ; @19AE
    jmp short loc_19DF ; @19B3
loc_19B5:
    mov di, word ptr [si + 034h] ; @19B5
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @19B8
    mov ax, word ptr [di] ; @19BC
    cmp ax, word ptr 0FFFFh ; @19BE
    jne loc_19CE ; @19C1
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @19C6
    jmp short loc_19B5 ; @19CC
loc_19CE:
    mov word ptr [bx + ActorSpriteIds], ax ; @19CE
    and cx, 0FFFFh ; @19D2
    je loc_19DF ; @19D5
    add word ptr [bx + ActorX32], 020h ; @19DA
loc_19DF:
    ret ; @19DF
; CONTRACT (tools/apply.py)
; Board a waterborne passenger and switch back to its paired land descriptor.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; In: DI is the player byte index found by the approach state.
; Out: copies fare bounds from the old descriptor, swaps descriptor via +48, then uses 1A0D tail.
; Effects: fare bounds deliberately come from the old descriptor, not the paired descriptor.
; END CONTRACT
public BoardWaterbornePassenger
BoardWaterbornePassenger:
    mov si, word ptr [bx + ActorDescriptors] ; @19E0
    mov ax, word ptr [si + 040h] ; @19E4
    mov word ptr [di + PlayerPassengerFares], ax ; @19E7
    mov ax, word ptr [si + 042h] ; @19EB
    mov word ptr [di + PlayerMinimumFares], ax ; @19EE
    mov si, word ptr [si + 048h] ; @19F2
    mov word ptr [bx + ActorDescriptors], si ; @19F5
    jmp short loc_1A0D ; @19F9
; CONTRACT (tools/apply.py)
; Attach a passenger to the selected player vehicle.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; In: DI is the player byte index found by the approach state.
; Out: copies fare bounds; shared tail installs +22, destination icon, owner index, hidden sprite.
; Effects: frees source platform and starts a 200-update quick-delivery counter.
; END CONTRACT
public BoardPassenger
BoardPassenger:
    mov si, word ptr [bx + ActorDescriptors] ; @19FB
    mov ax, word ptr [si + 040h] ; @19FF
    mov word ptr [di + PlayerPassengerFares], ax ; @1A02
    mov ax, word ptr [si + 042h] ; @1A06
    mov word ptr [di + PlayerMinimumFares], ax ; @1A09
loc_1A0D:
    mov ax, word ptr [si + 022h] ; @1A0D
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1A10
    mov ax, word ptr [si + 046h] ; @1A14
    mov word ptr [di + PlayerCarriedKinds], ax ; @1A17
    mov si, word ptr [bx + ActorDestinationPlatformByteIndices] ; @1A1B
    mov ax, word ptr [si + PlatformDestinationIcons] ; @1A1F
    mov word ptr [di + PlayerDestinationIcons], ax ; @1A23
    mov word ptr [bx + ds_2A2D], di ; @1A27
    mov word ptr [bx + ActorSpriteIds], 0FFFFh ; @1A2B
    mov word ptr [bx + PassengerQuickDeliveryCountdowns], 0C8h ; @1A31
    mov di, word ptr [bx + ActorSourcePlatformByteIndices] ; @1A37
    mov word ptr [di + PlatformActorOccupants], 0FFFFh ; @1A3B
    ret ; @1A41
; CONTRACT (tools/apply.py)
; Reduce the fare toward its floor and wait for the destination platform.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: unsigned fare comparison controls decrement; positive quick-delivery ticks decrement.
; Effects: destination platform equality tail-jumps through descriptor +24 with DI=owner.
; END CONTRACT
public UpdateCarriedPassenger
UpdateCarriedPassenger:
    mov di, word ptr [bx + ds_2A2D] ; @1A42
    mov ax, word ptr [di + PlayerPassengerFares] ; @1A46
    cmp ax, word ptr [di + PlayerMinimumFares] ; @1A4A
    jbe loc_1A58 ; @1A4E
    dec ax ; @1A53
    mov word ptr [di + PlayerPassengerFares], ax ; @1A54
loc_1A58:
    mov ax, word ptr [bx + PassengerQuickDeliveryCountdowns] ; @1A58
    cmp ax, word ptr 00h ; @1A5C
    jle loc_1A69 ; @1A5F
    dec ax ; @1A64
    mov word ptr [bx + PassengerQuickDeliveryCountdowns], ax ; @1A65
loc_1A69:
    mov ax, word ptr [bx + ActorDestinationPlatforms] ; @1A69
    cmp ax, word ptr [di + PlayerPlatformIndices] ; @1A6D
    jne loc_1A7D ; @1A71
    mov si, word ptr [bx + ActorDescriptors] ; @1A76
    jmp word ptr [si + 024h] ; @1A7A
loc_1A7D:
    ret ; @1A7D
; CONTRACT (tools/apply.py)
; Unload at the destination, award the fare, and optionally spawn a multiplier pickup.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; In: DI must already equal the carrying player byte index; BX selects the passenger.
; Out: clears carried kind/icon; adds fare times the word at 263D to the 32-bit score.
; Effects: nonzero quick-delivery ticks and multiplier below difficulty limit spawn 7A38 item.
; Effects: calls C:fn_1852 for effect 3274; installs +26 and positions the passenger for exit.
; END CONTRACT
public DeliverPassenger
DeliverPassenger:
    mov si, word ptr [bx + ActorDescriptors] ; @1A7E
    mov ax, word ptr [si + 026h] ; @1A82
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1A85
    xor ax, ax ; @1A89
    mov word ptr [di + PlayerCarriedKinds], ax ; @1A8B
    mov word ptr [di + PlayerDestinationIcons], ax ; @1A8F
    mov ax, 010h ; @1A93
    sub ax, word ptr [si] ; @1A96
    shl ax, 5 ; @1A98
    mov di, word ptr [bx + ds_2A2D] ; @1A9B
    add ax, word ptr [di + PlayerX32] ; @1A9F
    mov word ptr [bx + ActorX32], ax ; @1AA3
    mov ax, word ptr [di + PlayerPassengerFares] ; @1AA7
    mul word ptr ds:[ScoreMultiplier] ; @1AAB
    add word ptr ds:[ScoreLowWord], ax ; @1AAF
    adc word ptr ds:[ScoreHighWord], dx ; @1AB3
    test word ptr [bx + PassengerQuickDeliveryCountdowns], 0FFFFh ; @1AB7
loc_1ABD:
    je loc_1B04 ; @1ABD
    push si ; @1AC2
    mov ax, word ptr ds:[ScoreMultiplier] ; @1AC3
    mov si, word ptr ds:[SelectedDifficulty] ; @1AC6
    shl si, 1 ; @1ACA
    cmp ax, word ptr [si + MultiplierLimitsByDifficulty] ; @1ACC
loc_1AD0:
    jae loc_1B03 ; @1AD0
    mov ax, word ptr [di + PlayerX32] ; @1AD5
    add ax, word ptr 0200h ; @1AD9
    mov bp, word ptr [di + PlayerY32] ; @1ADC
    add bp, word ptr 0140h ; @1AE0
    xor cx, cx ; @1AE4
    xor dx, dx ; @1AE6
    mov si, 07A38h ; @1AE8
    call word ptr [si + 4] ; @1AEB
    push bx ; @1AEE
    push 1 ; @1AEF
    push word ptr 0FFh ; @1AF1
loc_1AF4:
    push seg ext_3274 ; @1AF4
    nop ; @1AF7
    push 0 ; @1AF8
loc_1AFA:
    call far ptr _PlayAdlibEffect ; @1AFA
    add sp, 8 ; @1AFF
    pop bx ; @1B02
loc_1B03:
    pop si ; @1B03
loc_1B04:
    mov di, word ptr [bx + ActorDestinationPlatformByteIndices] ; @1B04
    mov ax, word ptr [si + 2] ; @1B08
    neg ax ; @1B0B
    add ax, word ptr [di + PlatformHeights] ; @1B0D
    shl ax, 5 ; @1B11
    mov word ptr [bx + ActorY32], ax ; @1B14
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @1B18
    mov ax, 1 ; @1B1E
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @1B21
    mov byte ptr ds:[HudFareClearPending], al ; @1B25
    ret ; @1B28
; CONTRACT (tools/apply.py)
; Walk a delivered passenger to the destination platform arrival point.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: moves/animates on countdown expiry, then tail-jumps through descriptor +28.
; Effects: arrival is checked using both cached pixel X and freshly shifted x32 position.
; END CONTRACT
public WalkPassengerToExit
WalkPassengerToExit:
    mov di, word ptr [bx + ActorDestinationPlatformByteIndices] ; @1B29
    mov si, word ptr [bx + ActorDescriptors] ; @1B2D
    dec word ptr [bx + ActorAnimationCountdowns] ; @1B31
    jne loc_1BBD ; @1B35 JUMPS expansion
loc_1B3A:
    mov ax, word ptr [si + 03Eh] ; @1B3A
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @1B3D
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @1B41
    mov ax, word ptr [bx + ActorPixelX] ; @1B46
    add ax, word ptr [si] ; @1B4A
    cmp ax, word ptr [di + PlatformArrivalPointsX] ; @1B4C
    je loc_1BBA ; @1B50
    jl loc_1B7E ; @1B55
loc_1B5A:
    mov di, word ptr [si + 032h] ; @1B5A
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @1B5D
    mov ax, word ptr [di] ; @1B61
    cmp ax, word ptr 0FFFFh ; @1B63
    jne loc_1B73 ; @1B66
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @1B6B
    jmp short loc_1B5A ; @1B71
loc_1B73:
    mov word ptr [bx + ActorSpriteIds], ax ; @1B73
    sub word ptr [bx + ActorX32], 020h ; @1B77
    jmp short loc_1BA2 ; @1B7C
loc_1B7E:
    mov di, word ptr [si + 034h] ; @1B7E
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @1B81
    mov ax, word ptr [di] ; @1B85
    cmp ax, word ptr 0FFFFh ; @1B87
    jne loc_1B97 ; @1B8A
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @1B8F
    jmp short loc_1B7E ; @1B95
loc_1B97:
    mov word ptr [bx + ActorSpriteIds], ax ; @1B97
    add word ptr [bx + ActorX32], 020h ; @1B9B
    jmp short loc_1BA2 ; @1BA0
loc_1BA2:
    mov di, word ptr [bx + ActorDestinationPlatformByteIndices] ; @1BA2
    xor cx, cx ; @1BA6
    mov ax, word ptr [bx + ActorX32] ; @1BA8
    sar ax, 5 ; @1BAC
    add ax, word ptr [si] ; @1BAF
    cmp ax, word ptr [di + PlatformArrivalPointsX] ; @1BB1
    jne loc_1BBD ; @1BB5
loc_1BBA:
    jmp word ptr [si + 028h] ; @1BBA
loc_1BBD:
    ret ; @1BBD
; CONTRACT (tools/apply.py)
; Start the passenger departure animation.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: installs descriptor +2A and sets animation offset FFFE/ticks 1.
; END CONTRACT
public BeginPassengerDeparture
BeginPassengerDeparture:
    mov si, word ptr [bx + ActorDescriptors] ; @1BBE
    mov ax, word ptr [si + 02Ah] ; @1BC2
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1BC5
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @1BC9
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @1BCF
    ret ; @1BD5
; CONTRACT (tools/apply.py)
; Play the departure sequence and advance the journey cursor.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: writes the current sprite; if the following word is FFFF, advances journey by four.
; Effects: tail-jumps through descriptor +08 at sequence end; does not display its sentinel.
; END CONTRACT
public AnimatePassengerDeparture
AnimatePassengerDeparture:
    dec word ptr [bx + ActorAnimationCountdowns] ; @1BD6
    jne loc_1C0D ; @1BDA
    mov si, word ptr [bx + ActorDescriptors] ; @1BDF
    mov ax, word ptr [si + 03Eh] ; @1BE3
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @1BE6
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @1BEA
    mov di, word ptr [si + 038h] ; @1BEF
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @1BF2
    mov ax, word ptr [di] ; @1BF6
    mov word ptr [bx + ActorSpriteIds], ax ; @1BF8
    cmp word ptr [di + 2], -1 ; @1BFC
    jne loc_1C0D ; @1C00
    add word ptr [bx + ActorJourneyCursors], 4 ; @1C05
    jmp word ptr [si + 8] ; @1C0A
loc_1C0D:
    ret ; @1C0D
; CONTRACT (tools/apply.py)
; Return immediately for unused actor/enemy descriptor callbacks.
; Out: near RET; registers and flags are unchanged.
; END CONTRACT
public IgnoreActorState
IgnoreActorState:
    ret ; @1C0E
; CONTRACT (tools/apply.py)
; Enter the stone actor pickup-wait state.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: installs descriptor +12 and initializes animation offset FFFE/ticks 1.
; END CONTRACT
public BeginStonePickupWait
BeginStonePickupWait:
    mov si, word ptr [bx + ActorDescriptors] ; @1C0F
    mov ax, word ptr [si + 012h] ; @1C13
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1C16
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @1C1A
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @1C20
    ret ; @1C26
; CONTRACT (tools/apply.py)
; Offer stone sprite 0220 until an overlapping empty vehicle picks it up.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: collision success with carried-kind zero tail-jumps through descriptor +20.
; Effects: SF from 2276 is consumed before testing carried kind; otherwise sets sprite 0220.
; END CONTRACT
public UpdateStonePickupWait
UpdateStonePickupWait:
    mov si, word ptr [bx + ActorDescriptors] ; @1C27
    call FindPlayerTouchingActor ; @1C2B
    js loc_1C41 ; @1C2E
    test word ptr [di + PlayerCarriedKinds], 0FFFFh ; @1C33
    jne loc_1C41 ; @1C39
    jmp word ptr [si + 020h] ; @1C3E
loc_1C41:
    mov word ptr [bx + ActorSpriteIds], 0220h ; @1C41
    ret ; @1C47
; CONTRACT (tools/apply.py)
; Attach the stone actor to a player vehicle.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; In: DI is the overlapping player byte index.
; Out: installs +22; stores carried kind, icon 7, owner DI, and hidden actor sprite FFFF.
; END CONTRACT
public AttachStoneToPlayer
AttachStoneToPlayer:
    mov si, word ptr [bx + ActorDescriptors] ; @1C48
    mov ax, word ptr [si + 022h] ; @1C4C
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1C4F
    mov ax, word ptr [si + 046h] ; @1C53
    mov word ptr [di + PlayerCarriedKinds], ax ; @1C56
    mov word ptr [di + PlayerDestinationIcons], 7 ; @1C5A
    mov word ptr [bx + ds_2A2D], di ; @1C60
    mov word ptr [bx + ActorSpriteIds], 0FFFFh ; @1C64
    ret ; @1C6A
; CONTRACT (tools/apply.py)
; Wait for the carrying player's action byte to become negative.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: a negative byte at 279C+owner tail-jumps through descriptor +24.
; Effects: this is a signed byte test; it is not a nonzero word test.
; END CONTRACT
public WaitForStoneRelease
WaitForStoneRelease:
    mov di, word ptr [bx + ds_2A2D] ; @1C6B
    test byte ptr [di + PlayerActionInput], 0FFh ; @1C6F
    jns loc_1C80 ; @1C74
    mov si, word ptr [bx + ActorDescriptors] ; @1C79
    jmp word ptr [si + 024h] ; @1C7D
loc_1C80:
    ret ; @1C80
; CONTRACT (tools/apply.py)
; Release a stone using the carrying vehicle's position and velocities.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; In: DI must be the owner byte index from the release test.
; Out: clears carried kind/icon; copies player velocities SAR 5; installs descriptor +26.
; Effects: sets sprite 0221, uses x32/y32 geometry offsets, and plays effect 3632 via C.
; END CONTRACT
public ThrowCarriedStone
ThrowCarriedStone:
    mov si, word ptr [bx + ActorDescriptors] ; @1C81
    xor ax, ax ; @1C85
    mov word ptr [di + PlayerCarriedKinds], ax ; @1C87
    mov word ptr [di + PlayerDestinationIcons], ax ; @1C8B
    mov ax, word ptr [di + PlayerHorizontalVelocities] ; @1C8F
    sar ax, 5 ; @1C93
    mov word ptr [bx + ds_2ACD], ax ; @1C96
    mov ax, word ptr [di + PlayerVerticalVelocities] ; @1C9A
    sar ax, 5 ; @1C9E
    mov word ptr [bx + ds_2C6D], ax ; @1CA1
    mov ax, word ptr [di + PlayerX32] ; @1CA5
    mov bp, word ptr [di + PlayerY32] ; @1CA9
    add ax, word ptr 0200h ; @1CAD
    add bp, word ptr 0140h ; @1CB0
    mov di, word ptr [si] ; @1CB4
    shl di, 5 ; @1CB6
    sub ax, di ; @1CB9
    mov word ptr [bx + ActorX32], ax ; @1CBB
    mov di, word ptr [si + 2] ; @1CBF
    shl di, 4 ; @1CC2
    sub bp, di ; @1CC5
    mov word ptr [bx + ActorY32], bp ; @1CC7
    mov word ptr [bx + ActorSpriteIds], 0221h ; @1CCB
    mov ax, word ptr [si + 026h] ; @1CD1
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1CD4
    push bx ; @1CD8
    push 1 ; @1CD9
    push word ptr 0FFh ; @1CDB
loc_1CDE:
    push seg ext_3632 ; @1CDE
    nop ; @1CE1
    push 0 ; @1CE2
loc_1CE4:
    call far ptr _PlayAdlibEffect ; @1CE4
    add sp, 8 ; @1CE9
    pop bx ; @1CEC
    ret ; @1CED
; CONTRACT (tools/apply.py)
; Move the thrown stone with gravity and detect a crossed platform surface.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: x32 adds copied horizontal speed; vertical speed adds 2 and then updates y32.
; Effects: signed bounds X<=FE00 or X>=2800, or descending Y>=1800, hide/disable it.
; Effects: platform crossing uses cached old/new foot Y and inclusive horizontal bounds.
; Effects: landing snaps to platform height and tail-jumps through descriptor +10 with DI.
; END CONTRACT
public UpdateThrownStone
UpdateThrownStone:
    mov si, word ptr [bx + ActorDescriptors] ; @1CEE
    mov ax, word ptr [bx + ds_2ACD] ; @1CF2
    add ax, word ptr [bx + ActorX32] ; @1CF6
    cmp ax, word ptr 0FE00h ; @1CFA
    jle loc_1D38 ; @1CFD
    cmp ax, word ptr 02800h ; @1D02
    jge loc_1D38 ; @1D05
    mov word ptr [bx + ActorX32], ax ; @1D0A
    mov ax, word ptr [bx + ds_2C6D] ; @1D0E
    add ax, word ptr 02h ; @1D12
    mov word ptr [bx + ds_2C6D], ax ; @1D15
    test ax, 0FFFFh ; @1D19
    jns loc_1D28 ; @1D1C
    add word ptr [bx + ActorY32], ax ; @1D21
    jmp near ptr loc_1DA7 ; @1D25
loc_1D28:
    mov cx, word ptr [bx + ActorY32] ; @1D28
    add ax, word ptr [bx + ActorY32] ; @1D2C
    cmp ax, word ptr 01800h ; @1D30
    jl loc_1D47 ; @1D33
loc_1D38:
    mov word ptr [bx + ActorSpriteIds], 0FFFFh ; @1D38
    mov ax, word ptr [si + 02Ch] ; @1D3E
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1D41
    jmp short loc_1DA7 ; @1D45
loc_1D47:
    mov word ptr [bx + ActorY32], ax ; @1D47
    sar ax, 5 ; @1D4B
    sar cx, 5 ; @1D4E
    add ax, word ptr [si + 2] ; @1D51
    add cx, word ptr [si + 2] ; @1D54
    xor di, di ; @1D57
loc_1D59:
    test word ptr [di + PlatformLeftEdges], 0FFFFh ; @1D59
    js loc_1DA7 ; @1D5F
    cmp cx, word ptr [di + PlatformHeights] ; @1D64
    jg loc_1DA2 ; @1D68
    cmp ax, word ptr [di + PlatformHeights] ; @1D6D
    jl loc_1DA2 ; @1D71
    mov dx, word ptr [bx + ActorX32] ; @1D76
    sar dx, 5 ; @1D7A
    add dx, word ptr [si] ; @1D7D
    cmp dx, word ptr [di + PlatformLeftEdges] ; @1D7F
    jl loc_1DA2 ; @1D83
    cmp dx, word ptr [di + PlatformRightEdges] ; @1D88
    jg loc_1DA2 ; @1D8C
    mov ax, word ptr [di + PlatformHeights] ; @1D91
    sub ax, word ptr [si + 2] ; @1D95
    shl ax, 5 ; @1D98
    mov word ptr [bx + ActorY32], ax ; @1D9B
    jmp word ptr [si + 010h] ; @1D9F
loc_1DA2:
    add di, 2 ; @1DA2
    jmp short loc_1D59 ; @1DA5
loc_1DA7:
    ret ; @1DA7
; CONTRACT (tools/apply.py)
; Switch a waterborne passenger into its resurfacing state.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: installs descriptor +0A; frees source platform, hides overlay, clears vertical velocity.
; Effects: resets animation offset FFFE/ticks 1.
; END CONTRACT
public BeginPassengerResurfacing
BeginPassengerResurfacing:
    mov si, word ptr [bx + ActorDescriptors] ; @1DA8
    mov ax, word ptr [si + 0Ah] ; @1DAC
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1DAF
    mov di, word ptr [bx + ActorSourcePlatformByteIndices] ; @1DB3
    mov ax, 0FFFFh ; @1DB7
    mov word ptr [di + PlatformActorOccupants], ax ; @1DBA
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], ax ; @1DBE
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @1DC2
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @1DC8
    mov word ptr [bx + ds_2C6D], 0 ; @1DCE
    ret ; @1DD4
; CONTRACT (tools/apply.py)
; Animate and accelerate a waterborne passenger toward the surface.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: velocity is clamped signed to E800..1800; y32 adds velocity SAR 6.
; Effects: acceleration is +27h, -175h, or -5Ch according to signed surface/velocity tests.
; Effects: an upward surface crossing snaps Y and tail-jumps through descriptor +10.
; END CONTRACT
public UpdatePassengerResurfacing
UpdatePassengerResurfacing:
    mov si, word ptr [bx + ActorDescriptors] ; @1DD5
    dec word ptr [bx + ActorAnimationCountdowns] ; @1DD9
    jne loc_1DEE ; @1DDD
    mov ax, word ptr [si + 03Eh] ; @1DE2
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @1DE5
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @1DE9
loc_1DEE:
    mov di, word ptr [si + 02Eh] ; @1DEE
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @1DF1
    mov ax, word ptr [di] ; @1DF5
    cmp ax, word ptr 0FFFFh ; @1DF7
    jne loc_1E07 ; @1DFA
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @1DFF
    jmp short loc_1DEE ; @1E05
loc_1E07:
    mov word ptr [bx + ActorSpriteIds], ax ; @1E07
    mov cx, word ptr [bx + ActorPixelY] ; @1E0B
    sub cx, word ptr [si + 2] ; @1E0F
    sub cx, word ptr ds:[WaterYPixels] ; @1E12
    js loc_1E22 ; @1E16
    je loc_1E22 ; @1E1B
    mov ch, 1 ; @1E20
loc_1E22:
    mov ax, word ptr [bx + ds_2C6D] ; @1E22
    and ch, 0FFh ; @1E26
    js loc_1E40 ; @1E29
    cmp ax, word ptr 00h ; @1E2E
    jle loc_1E3B ; @1E31
    sub ax, word ptr 0175h ; @1E36
    jmp short loc_1E43 ; @1E39
loc_1E3B:
    sub ax, word ptr 05Ch ; @1E3B
    jmp short loc_1E43 ; @1E3E
loc_1E40:
    add ax, word ptr 027h ; @1E40
loc_1E43:
    and ax, word ptr 0FFFFh ; @1E43
    jns loc_1E58 ; @1E46
    cmp ax, word ptr 0E800h ; @1E4B
    jge loc_1E63 ; @1E4E
    mov ax, 0E800h ; @1E53
    jmp short loc_1E63 ; @1E56
loc_1E58:
    cmp ax, word ptr 01800h ; @1E58
    jle loc_1E63 ; @1E5B
    mov ax, 01800h ; @1E60
loc_1E63:
    mov word ptr [bx + ds_2C6D], ax ; @1E63
    sar ax, 6 ; @1E67
    add ax, word ptr [bx + ActorY32] ; @1E6A
    mov word ptr [bx + ActorY32], ax ; @1E6E
    cmp word ptr [bx + ds_2C6D], 0 ; @1E72
    jge loc_1E9B ; @1E77
    sar ax, 5 ; @1E7C
    sub ax, word ptr [si + 2] ; @1E7F
    cmp ax, word ptr ds:[WaterYPixels] ; @1E82
    jg loc_1E9B ; @1E86
    mov ax, word ptr ds:[WaterYPixels] ; @1E8B
    sub ax, word ptr [si + 2] ; @1E8E
    shl ax, 5 ; @1E91
    mov word ptr [bx + ActorY32], ax ; @1E94
    jmp word ptr [si + 010h] ; @1E98
loc_1E9B:
    ret ; @1E9B
; CONTRACT (tools/apply.py)
; Start a waterborne passenger sinking with zero vertical velocity.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: installs descriptor +0E; hides overlay and resets animation offset FFFE/ticks 1.
; END CONTRACT
public BeginPassengerSinking
BeginPassengerSinking:
    mov si, word ptr [bx + ActorDescriptors] ; @1E9C
    mov ax, word ptr [si + 0Eh] ; @1EA0
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1EA3
    mov word ptr [bx + ActorOverlayOrScriptCallbacks], 0FFFFh ; @1EA7
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @1EAD
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @1EB3
    mov word ptr [bx + ds_2C6D], 0 ; @1EB9
    ret ; @1EBF
; CONTRACT (tools/apply.py)
; Animate a sinking passenger and add gravity until it leaves the scene.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: velocity adds 27h; y32 adds velocity SAR 6; unsigned Y>=1800 hides the sprite.
; Effects: offscreen path installs descriptor +2C without jumping to it in this update.
; END CONTRACT
public UpdatePassengerSinking
UpdatePassengerSinking:
    mov si, word ptr [bx + ActorDescriptors] ; @1EC0
    dec word ptr [bx + ActorAnimationCountdowns] ; @1EC4
    jne loc_1ED9 ; @1EC8
    mov ax, word ptr [si + 03Eh] ; @1ECD
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @1ED0
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @1ED4
loc_1ED9:
    mov di, word ptr [si + 02Eh] ; @1ED9
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @1EDC
    mov ax, word ptr [di] ; @1EE0
    cmp ax, word ptr 0FFFFh ; @1EE2
    jne loc_1EF2 ; @1EE5
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @1EEA
    jmp short loc_1ED9 ; @1EF0
loc_1EF2:
    mov word ptr [bx + ActorSpriteIds], ax ; @1EF2
    mov ax, word ptr [bx + ds_2C6D] ; @1EF6
    add ax, word ptr 027h ; @1EFA
    mov word ptr [bx + ds_2C6D], ax ; @1EFD
    sar ax, 6 ; @1F01
    add ax, word ptr [bx + ActorY32] ; @1F04
    cmp ax, word ptr 01800h ; @1F08
    jb loc_1F1F ; @1F0B
    mov ax, word ptr [si + 02Ch] ; @1F10
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1F13
    mov word ptr [bx + ActorSpriteIds], 0FFFFh ; @1F17
    jmp short loc_1F23 ; @1F1D
loc_1F1F:
    mov word ptr [bx + ActorY32], ax ; @1F1F
loc_1F23:
    ret ; @1F23
; CONTRACT (tools/apply.py)
; Start floating at the water surface with a descriptor-defined lifetime.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: installs descriptor +12; resets animation and loads state delay from descriptor +44.
; END CONTRACT
public BeginPassengerFloating
BeginPassengerFloating:
    mov si, word ptr [bx + ActorDescriptors] ; @1F24
    mov ax, word ptr [si + 012h] ; @1F28
    mov word ptr [bx + ActorUpdateOrScriptCursor], ax ; @1F2B
    mov word ptr [bx + ActorAnimationByteOffsets], 0FFFEh ; @1F2F
    mov word ptr [bx + ActorAnimationCountdowns], 1 ; @1F35
    mov ax, word ptr [si + 044h] ; @1F3B
    mov word ptr [bx + ds_2ACD], ax ; @1F3E
    ret ; @1F42
; CONTRACT (tools/apply.py)
; Keep a passenger at the water surface and seek an empty stationary vehicle.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: loops descriptor +30 animation; eligible vehicle selects +14; delay zero selects +0C.
; Effects: descriptor 77FE skips vehicle search; other searches require vertical velocity zero.
; Effects: vehicle cached Y must equal water Y-18 exactly.
; END CONTRACT
public UpdatePassengerFloating
UpdatePassengerFloating:
    mov si, word ptr [bx + ActorDescriptors] ; @1F43
    dec word ptr [bx + ActorAnimationCountdowns] ; @1F47
    jne loc_1F5C ; @1F4B
    mov ax, word ptr [si + 03Eh] ; @1F50
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @1F53
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @1F57
loc_1F5C:
    mov di, word ptr [si + 030h] ; @1F5C
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @1F5F
    mov ax, word ptr [di] ; @1F63
    cmp ax, word ptr 0FFFFh ; @1F65
    jne loc_1F75 ; @1F68
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @1F6D
    jmp short loc_1F5C ; @1F73
loc_1F75:
    mov word ptr [bx + ActorSpriteIds], ax ; @1F75
    mov ax, word ptr ds:[WaterYPixels] ; @1F79
    cmp ax, word ptr [bx + ActorPixelY] ; @1F7C
    je loc_1F8F ; @1F80
    sub ax, word ptr [si + 2] ; @1F85
    shl ax, 5 ; @1F88
    mov word ptr [bx + ActorY32], ax ; @1F8B
loc_1F8F:
    cmp si, word ptr 077FEh ; @1F8F
    je loc_1FD5 ; @1F93
    xor di, di ; @1F98
loc_1F9A:
    cmp word ptr [di + PlayerVerticalVelocities], 0 ; @1F9A
    jne loc_1FBE ; @1F9F
    cmp word ptr [di + PlayerCarriedKinds], 0 ; @1FA4
    jne loc_1FBE ; @1FA9
    mov cx, word ptr [di + PlayerYPixels] ; @1FAE
    sub cx, word ptr ds:[WaterYPixels] ; @1FB2
    add cx, 012h ; @1FB6
    je loc_1FD2 ; @1FB9
loc_1FBE:
    add di, 2 ; @1FBE
    cmp di, 4 ; @1FC1
    jae loc_1FD5 ; @1FC4
    cmp word ptr ds:[PlayerCount], 2 ; @1FC9
    je short loc_1F9A ; @1FCE
    jmp short loc_1FD5 ; @1FD0
loc_1FD2:
    jmp word ptr [si + 014h] ; @1FD2
loc_1FD5:
    dec word ptr [bx + ds_2ACD] ; @1FD5
    jne loc_1FE1 ; @1FD9
    jmp word ptr [si + 0Ch] ; @1FDE
loc_1FE1:
    ret ; @1FE1
; CONTRACT (tools/apply.py)
; Show a floating passenger's destination while any vehicle is at surface height.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: maintains water Y, loops +30 animation, and ends state countdown at descriptor +1C.
; Effects: checks vehicle Y only, including occupied vehicles; no match selects descriptor +18.
; END CONTRACT
public UpdateFloatingDestinationDisplay
UpdateFloatingDestinationDisplay:
    mov si, word ptr [bx + ActorDescriptors] ; @1FE2
    mov ax, word ptr ds:[WaterYPixels] ; @1FE6
    cmp ax, word ptr [bx + ActorPixelY] ; @1FE9
    je loc_1FFC ; @1FED
    sub ax, word ptr [si + 2] ; @1FF2
    shl ax, 5 ; @1FF5
    mov word ptr [bx + ActorY32], ax ; @1FF8
loc_1FFC:
    mov cx, word ptr ds:[PlayerYPixels] ; @1FFC
    sub cx, word ptr ds:[WaterYPixels] ; @2000
    add cx, 012h ; @2004
    je loc_2029 ; @2007
    cmp word ptr ds:[PlayerCount], 2 ; @200C
    jne loc_2026 ; @2011
    mov cx, word ptr ds:[SecondPlayerYPixels] ; @2016
    sub cx, word ptr ds:[WaterYPixels] ; @201A
    add cx, 012h ; @201E
    je loc_2029 ; @2021
loc_2026:
    jmp word ptr [si + 018h] ; @2026
loc_2029:
    dec word ptr [bx + ActorAnimationCountdowns] ; @2029
    jne loc_205B ; @202D
    mov ax, word ptr [si + 03Eh] ; @2032
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @2035
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @2039
loc_203E:
    mov di, word ptr [si + 030h] ; @203E
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @2041
    mov ax, word ptr [di] ; @2045
    cmp ax, word ptr 0FFFFh ; @2047
    jne loc_2057 ; @204A
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @204F
    jmp short loc_203E ; @2055
loc_2057:
    mov word ptr [bx + ActorSpriteIds], ax ; @2057
loc_205B:
    dec word ptr [bx + ds_2A2D] ; @205B
    jne loc_2067 ; @205F
    jmp word ptr [si + 01Ch] ; @2064
loc_2067:
    ret ; @2067
; CONTRACT (tools/apply.py)
; Animate a floating passenger's question bubble until its timeout.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: maintains water Y and +30 animation; exactly-zero state timer selects descriptor +0C.
; END CONTRACT
public UpdateFloatingQuestionDisplay
UpdateFloatingQuestionDisplay:
    mov si, word ptr [bx + ActorDescriptors] ; @2068
    mov ax, word ptr ds:[WaterYPixels] ; @206C
    cmp ax, word ptr [bx + ActorPixelY] ; @206F
    je loc_2082 ; @2073
    sub ax, word ptr [si + 2] ; @2078
    shl ax, 5 ; @207B
    mov word ptr [bx + ActorY32], ax ; @207E
loc_2082:
    dec word ptr [bx + ActorAnimationCountdowns] ; @2082
    jne loc_20B4 ; @2086
    mov ax, word ptr [si + 03Eh] ; @208B
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @208E
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @2092
loc_2097:
    mov di, word ptr [si + 030h] ; @2097
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @209A
    mov ax, word ptr [di] ; @209E
    cmp ax, word ptr 0FFFFh ; @20A0
    jne loc_20B0 ; @20A3
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @20A8
    jmp short loc_2097 ; @20AE
loc_20B0:
    mov word ptr [bx + ActorSpriteIds], ax ; @20B0
loc_20B4:
    dec word ptr [bx + ds_2A2D] ; @20B4
    jne loc_20C0 ; @20B8
    jmp word ptr [si + 0Ch] ; @20BD
loc_20C0:
    ret ; @20C0
; CONTRACT (tools/apply.py)
; Move a floating passenger horizontally toward an empty surface vehicle.
; In: BX is actor byte index (2*slot); DS=DGROUP.
; Out: no eligible vehicle selects +18; horizontal equality selects +20 with DI=player.
; Effects: cached vehicle Y must equal water Y-18; movement occurs on animation ticks only.
; END CONTRACT
public UpdateFloatingPassengerApproach
UpdateFloatingPassengerApproach:
    mov si, word ptr [bx + ActorDescriptors] ; @20C1
    mov ax, word ptr ds:[WaterYPixels] ; @20C5
    cmp ax, word ptr [bx + ActorPixelY] ; @20C8
    je loc_20DB ; @20CC
    sub ax, word ptr [si + 2] ; @20D1
    shl ax, 5 ; @20D4
    mov word ptr [bx + ActorY32], ax ; @20D7
loc_20DB:
    xor di, di ; @20DB
loc_20DD:
    cmp word ptr [di + PlayerCarriedKinds], 0 ; @20DD
    jne loc_20F7 ; @20E2
    mov cx, word ptr [di + PlayerYPixels] ; @20E7
    sub cx, word ptr ds:[WaterYPixels] ; @20EB
    add cx, 012h ; @20EF
    je loc_210C ; @20F2
loc_20F7:
    add di, 2 ; @20F7
    cmp di, 4 ; @20FA
    jae loc_2109 ; @20FD
    cmp word ptr ds:[PlayerCount], 2 ; @2102
    je short loc_20DD ; @2107
loc_2109:
    jmp word ptr [si + 018h] ; @2109
loc_210C:
    xor cx, cx ; @210C
    dec word ptr [bx + ActorAnimationCountdowns] ; @210E
    jne loc_2124 ; @2112
    mov ax, word ptr [si + 03Eh] ; @2117
    mov word ptr [bx + ActorAnimationCountdowns], ax ; @211A
    add word ptr [bx + ActorAnimationByteOffsets], 2 ; @211E
    inc cx ; @2123
loc_2124:
    mov ax, word ptr [bx + ActorPixelX] ; @2124
    add ax, word ptr [si] ; @2128
    sub ax, word ptr 010h ; @212A
    cmp ax, word ptr [di + PlayerPixelX] ; @212D
    jg loc_213E ; @2131
    jl loc_216A ; @2136
    jmp word ptr [si + 020h] ; @213B
loc_213E:
    mov di, word ptr [si + 032h] ; @213E
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @2141
    mov ax, word ptr [di] ; @2145
    cmp ax, word ptr 0FFFFh ; @2147
    jne loc_2157 ; @214A
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @214F
    jmp short loc_213E ; @2155
loc_2157:
    mov word ptr [bx + ActorSpriteIds], ax ; @2157
    and cx, 0FFFFh ; @215B
    je loc_2194 ; @215E
    sub word ptr [bx + ActorX32], 020h ; @2163
    jmp short loc_2194 ; @2168
loc_216A:
    mov di, word ptr [si + 034h] ; @216A
    add di, word ptr [bx + ActorAnimationByteOffsets] ; @216D
    mov ax, word ptr [di] ; @2171
    cmp ax, word ptr 0FFFFh ; @2173
    jne loc_2183 ; @2176
    mov word ptr [bx + ActorAnimationByteOffsets], 0 ; @217B
    jmp short loc_216A ; @2181
loc_2183:
    mov word ptr [bx + ActorSpriteIds], ax ; @2183
    and cx, 0FFFFh ; @2187
    je loc_2194 ; @218A
    add word ptr [bx + ActorX32], 020h ; @218F
loc_2194:
    ret ; @2194
; CONTRACT (tools/apply.py)
; Return immediately for unused waterborne passenger callbacks.
; Out: near RET; registers and flags are unchanged.
; END CONTRACT
public IgnoreWaterbornePassengerState
IgnoreWaterbornePassengerState:
    ret ; @2195
; CONTRACT (tools/apply.py)
; Find a descending thrown-stone actor overlapping the selected enemy.
; In: BX is enemy byte index; DS=DGROUP.
; Out: DI is actor byte index or FFFF; final TEST DI sets SF for miss, clears SF for hit.
; Effects: requires descriptor 78DC, update callback 1CEE, and nonnegative stone Y velocity.
; Effects: scans until actor descriptor FFFF; does not modify SI or BX.
; END CONTRACT
FindThrownStoneHittingEnemy:
    xor di, di ; @2196
loc_2198:
    mov ax, word ptr [di + ActorDescriptors] ; @2198
    cmp ax, word ptr 0FFFFh ; @219C
    je loc_21FF ; @219F
    cmp ax, word ptr 078DCh ; @21A4
    jne loc_21FA ; @21A7
    cmp word ptr [di + ActorUpdateOrScriptCursor], word ptr 01CEEh ; @21AC
    jne loc_21FA ; @21B2
    test word ptr [di + ds_2C6D], 0FFFFh ; @21B7
    js loc_21FA ; @21BD
    mov ax, word ptr [di + ActorY32] ; @21C2
    add ax, word ptr 0100h ; @21C6
    cmp ax, word ptr [bx + EnemyY32] ; @21C9
    jl loc_21FA ; @21CD
    sub ax, word ptr 0380h ; @21D2
    cmp ax, word ptr [bx + EnemyY32] ; @21D5
    jg loc_21FA ; @21D9
    mov ax, word ptr [di + ActorX32] ; @21DE
    add ax, word ptr 0180h ; @21E2
    cmp ax, word ptr [bx + EnemyX32] ; @21E5
    jl loc_21FA ; @21E9
    sub ax, word ptr 04C0h ; @21EE
    cmp ax, word ptr [bx + EnemyX32] ; @21F1
    jle loc_2202 ; @21F5
loc_21FA:
    add di, 2 ; @21FA
    jmp short loc_2198 ; @21FD
loc_21FF:
    mov di, 0FFFFh ; @21FF
loc_2202:
    test di, 0FFFFh ; @2202
    ret ; @2206
; CONTRACT (tools/apply.py)
; Find a player overlapping the selected falling item.
; In: BX is falling-item byte index; SI is its descriptor; DS=DGROUP.
; Out: DI=player byte index or FFFF; SF from final TEST DI reports miss.
; Effects: signed x32/y32 tests; second-player retry compares DI=2 to player count, not bytes.
; Preserves: BX and SI; clobbers AX, DI, and flags.
; END CONTRACT
FindPlayerTouchingFallingItem:
    xor di, di ; @2207
loc_2209:
    mov ax, word ptr [si + 2] ; @2209
    shl ax, 5 ; @220C
    add ax, word ptr [bx + FallingItemY] ; @220F
    cmp ax, word ptr [di + PlayerY32] ; @2213
    jl loc_2265 ; @2217
    mov ax, word ptr [si + 2] ; @221C
    sub ax, word ptr 06h ; @221F
    shl ax, 5 ; @2222
    add ax, word ptr [bx + FallingItemY] ; @2225
    sub ax, word ptr 0280h ; @2229
    cmp ax, word ptr [di + PlayerY32] ; @222C
    jg loc_2265 ; @2230
    mov ax, word ptr [si] ; @2235
    add ax, word ptr 03h ; @2237
    shl ax, 5 ; @223A
    add ax, word ptr [bx + FallingItemX] ; @223D
    sub ax, word ptr 0A0h ; @2241
    cmp ax, word ptr [di + PlayerX32] ; @2244
    jl loc_2265 ; @2248
    mov ax, word ptr [si] ; @224D
    sub ax, word ptr 03h ; @224F
    shl ax, 5 ; @2252
    add ax, word ptr [bx + FallingItemX] ; @2255
    sub ax, word ptr 0340h ; @2259
    cmp ax, word ptr [di + PlayerX32] ; @225C
    jle loc_2271 ; @2260
loc_2265:
    add di, 2 ; @2265
    cmp di, word ptr ds:[PlayerCount] ; @2268
    je short loc_2209 ; @226C
    mov di, 0FFFFh ; @226E
loc_2271:
    test di, 0FFFFh ; @2271
    ret ; @2275
; CONTRACT (tools/apply.py)
; Find a player overlapping the selected actor's descriptor-sized contact box.
; In: BX is actor byte index; SI is its descriptor; DS=DGROUP.
; Out: DI=player byte index or FFFF; SF indicates miss; on hit AX is player platform index.
; Effects: MOV AX on hit preserves TEST DI flags; callers branch immediately on SF.
; Effects: second-player retry compares DI=2 to player count, not player-array byte extent.
; Preserves: BX and SI; clobbers AX, DI, and flags.
; END CONTRACT
FindPlayerTouchingActor:
    xor di, di ; @2276
loc_2278:
    mov ax, word ptr [si + 2] ; @2278
    shl ax, 5 ; @227B
    add ax, word ptr [bx + ActorY32] ; @227E
    cmp ax, word ptr [di + PlayerY32] ; @2282
    jl loc_22D7 ; @2286
    mov ax, word ptr [si + 2] ; @228B
    sub ax, word ptr [si + 6] ; @228E
    sub ax, word ptr [si + 6] ; @2291
    shl ax, 5 ; @2294
    add ax, word ptr [bx + ActorY32] ; @2297
    sub ax, word ptr 0280h ; @229B
    cmp ax, word ptr [di + PlayerY32] ; @229E
    jg loc_22D7 ; @22A2
    mov ax, word ptr [si] ; @22A7
    add ax, word ptr [si + 4] ; @22A9
    shl ax, 5 ; @22AC
    add ax, word ptr [bx + ActorX32] ; @22AF
    sub ax, word ptr 0A0h ; @22B3
    cmp ax, word ptr [di + PlayerX32] ; @22B6
    jl loc_22D7 ; @22BA
    mov ax, word ptr [si] ; @22BF
    sub ax, word ptr [si + 4] ; @22C1
    shl ax, 5 ; @22C4
    add ax, word ptr [bx + ActorX32] ; @22C7
    sub ax, word ptr 0340h ; @22CB
    cmp ax, word ptr [di + PlayerX32] ; @22CE
    jle loc_22E3 ; @22D2
loc_22D7:
    add di, 2 ; @22D7
    cmp di, word ptr ds:[PlayerCount] ; @22DA
    je short loc_2278 ; @22DE
    mov di, 0FFFFh ; @22E0
loc_22E3:
    test di, 0FFFFh ; @22E3
    js loc_22F0 ; @22E7
    mov ax, word ptr [di + PlayerPlatformIndices] ; @22EC
loc_22F0:
    ret ; @22F0
; CONTRACT (tools/apply.py)
; Find a player overlapping the selected enemy's descriptor-sized contact box.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: DI=player byte index or FFFF; final TEST DI sets SF on miss.
; Effects: signed bounds; second-player retry compares DI=2 to count, not byte extent.
; Preserves: BX and SI; clobbers AX, DI, and flags.
; END CONTRACT
FindPlayerTouchingEnemy:
    xor di, di ; @22F1
loc_22F3:
    mov ax, word ptr [si + 2] ; @22F3
    shl ax, 5 ; @22F6
    add ax, word ptr [bx + EnemyY32] ; @22F9
    cmp ax, word ptr [di + PlayerY32] ; @22FD
    jl loc_2352 ; @2301
    mov ax, word ptr [si + 2] ; @2306
    sub ax, word ptr [si + 6] ; @2309
    sub ax, word ptr [si + 6] ; @230C
    shl ax, 5 ; @230F
    add ax, word ptr [bx + EnemyY32] ; @2312
    sub ax, word ptr 0280h ; @2316
    cmp ax, word ptr [di + PlayerY32] ; @2319
    jg loc_2352 ; @231D
    mov ax, word ptr [si] ; @2322
    add ax, word ptr [si + 4] ; @2324
    shl ax, 5 ; @2327
    add ax, word ptr [bx + EnemyX32] ; @232A
    sub ax, word ptr 0A0h ; @232E
    cmp ax, word ptr [di + PlayerX32] ; @2331
    jl loc_2352 ; @2335
    mov ax, word ptr [si] ; @233A
    sub ax, word ptr [si + 4] ; @233C
    shl ax, 5 ; @233F
    add ax, word ptr [bx + EnemyX32] ; @2342
    sub ax, word ptr 0340h ; @2346
    cmp ax, word ptr [di + PlayerX32] ; @2349
    jle loc_235E ; @234D
loc_2352:
    add di, 2 ; @2352
    cmp di, word ptr ds:[PlayerCount] ; @2355
    je short loc_22F3 ; @2359
    mov di, 0FFFFh ; @235B
loc_235E:
    test di, 0FFFFh ; @235E
    ret ; @2362
; CONTRACT (tools/apply.py)
; Call each enemy's near state callback until the descriptor FFFF sentinel.
; In: DS=DGROUP; enemy descriptor and callback parallel arrays are initialized.
; Out: BX advances by two per enemy and ends at the descriptor sentinel.
; Effects: callback entries must preserve BX; callbacks may tail-jump through descriptors.
; END CONTRACT
DispatchEnemyStates:
    xor bx, bx ; @2363
loc_2365:
    cmp word ptr [bx + EnemyDescriptors], -1 ; @2365
    je loc_2378 ; @236A
    call word ptr [bx + EnemyStateCallbacks] ; @236F
    add bx, 2 ; @2373
    jmp short loc_2365 ; @2376
loc_2378:
    ret ; @2378
; CONTRACT (tools/apply.py)
; Initialize the flying bird's inter-flight delay.
; In: BX is enemy byte index; DS=DGROUP.
; Out: installs descriptor +0A; hides sprite, resets animation, and copies delay from 2CDF.
; END CONTRACT
public BeginBirdDelay
BeginBirdDelay:
    mov si, word ptr [bx + EnemyDescriptors] ; @2379
    mov ax, word ptr [si + 0Ah] ; @237D
    mov word ptr [bx + EnemyStateCallbacks], ax ; @2380
    mov word ptr [bx + EnemyAnimationByteOffsets], 0FFFEh ; @2384
    mov word ptr [bx + EnemyAnimationCountdowns], 1 ; @238A
    mov word ptr [bx + EnemySpriteIds], 0FFFFh ; @2390
    mov ax, word ptr [bx + EnemyInitialDelays] ; @2396
    mov word ptr [bx + EnemyStateCounters], ax ; @239A
    ret ; @239E
; CONTRACT (tools/apply.py)
; Count down the bird's delay before its warning state.
; In: BX is enemy byte index; DS=DGROUP.
; Out: exactly-zero state countdown tail-jumps through descriptor +0C.
; END CONTRACT
public WaitForBirdFlight
WaitForBirdFlight:
    dec word ptr [bx + EnemyStateCounters] ; @239F
    jne loc_23AF ; @23A3
    mov si, word ptr [bx + EnemyDescriptors] ; @23A8
    jmp word ptr [si + 0Ch] ; @23AC
loc_23AF:
    ret ; @23AF
; CONTRACT (tools/apply.py)
; Start the bird warning sound and a 70-update delay.
; In: BX is enemy byte index; DS=DGROUP.
; Out: installs descriptor +0E and plays effect 325B through C:fn_1852.
; Effects: explicitly saves/restores BX and ES around the far C call.
; END CONTRACT
public BeginBirdWarning
BeginBirdWarning:
    mov si, word ptr [bx + EnemyDescriptors] ; @23B0
    mov ax, word ptr [si + 0Eh] ; @23B4
    mov word ptr [bx + EnemyStateCallbacks], ax ; @23B7
    mov word ptr [bx + EnemyStateCounters], 046h ; @23BB
    push bx ; @23C1
    push es ; @23C2
    push 1 ; @23C3
    push word ptr 0FFh ; @23C5
loc_23C8:
    push seg ext_325B ; @23C8
    nop ; @23CB
    push 0 ; @23CC
loc_23CE:
    call far ptr _PlayAdlibEffect ; @23CE
    add sp, 8 ; @23D3
    pop es ; @23D6
    pop bx ; @23D7
    ret ; @23D8
; CONTRACT (tools/apply.py)
; Count down the bird warning before positioning a flight.
; In: BX is enemy byte index; DS=DGROUP.
; Out: exactly-zero state countdown tail-jumps through descriptor +10.
; END CONTRACT
public WaitForBirdWarning
WaitForBirdWarning:
    dec word ptr [bx + EnemyStateCounters] ; @23D9
    jne loc_23E9 ; @23DD
    mov si, word ptr [bx + EnemyDescriptors] ; @23E2
    jmp word ptr [si + 010h] ; @23E6
loc_23E9:
    ret ; @23E9
; CONTRACT (tools/apply.py)
; Alternate target players and start a horizontal bird flight from the opposite side.
; In: BX is enemy byte index; DS=DGROUP.
; Out: sets speed sign, X, clipped Y, direction animation, target player, and descriptor +12.
; Effects: plays looping effect 3260 and stores its returned channel handle in 2D61+BX.
; Effects: X=27E0 for leftward flight or FC20 for rightward; Y clamps against water and FF80.
; END CONTRACT
public LaunchBirdTowardPlayer
LaunchBirdTowardPlayer:
    mov si, word ptr [bx + EnemyDescriptors] ; @23EA
    mov di, word ptr [bx + EnemyDirectionOrTargetPlayer] ; @23EE
    xor di, 1 ; @23F2
    cmp di, word ptr ds:[PlayerCount] ; @23F5
    jl loc_2400 ; @23F9
    xor di, di ; @23FE
loc_2400:
    mov word ptr [bx + EnemyDirectionOrTargetPlayer], di ; @2400
    shl di, 1 ; @2404
    cmp word ptr [di + PlayerX32], word ptr 01400h ; @2406
    jge loc_242B ; @240C
    mov ax, word ptr [bx + EnemyHorizontalSpeeds] ; @2411
    and ax, word ptr 0FFFFh ; @2415
    js loc_2423 ; @2418
    neg ax ; @241D
    mov word ptr [bx + EnemyHorizontalSpeeds], ax ; @241F
loc_2423:
    mov ax, 027E0h ; @2423
    mov cx, word ptr [si + 022h] ; @2426
    jmp short loc_2443 ; @2429
loc_242B:
    mov ax, word ptr [bx + EnemyHorizontalSpeeds] ; @242B
    and ax, word ptr 0FFFFh ; @242F
    jns loc_243D ; @2432
    neg ax ; @2437
    mov word ptr [bx + EnemyHorizontalSpeeds], ax ; @2439
loc_243D:
    mov ax, 0FC20h ; @243D
    mov cx, word ptr [si + 024h] ; @2440
loc_2443:
    mov word ptr [bx + EnemyX32], ax ; @2443
    mov word ptr [bx + EnemyAnimationOrDropLists], cx ; @2447
    mov ax, word ptr [di + PlayerY32] ; @244B
    add ax, word ptr 0340h ; @244F
    cmp ax, word ptr ds:[WaterY32] ; @2452
    jle loc_245E ; @2456
    mov ax, word ptr ds:[WaterY32] ; @245B
loc_245E:
    sub ax, word ptr 0340h ; @245E
    cmp ax, word ptr 0FF80h ; @2461
    jge loc_246C ; @2464
    mov ax, 0FF80h ; @2469
loc_246C:
    mov word ptr [bx + EnemyY32], ax ; @246C
    mov ax, word ptr [si + 012h] ; @2470
    mov word ptr [bx + EnemyStateCallbacks], ax ; @2473
    push es ; @2477
    push bx ; @2478
    push 0 ; @2479
    push word ptr 0FFh ; @247B
loc_247E:
    push seg ext_3260 ; @247E
    nop ; @2481
    push 0 ; @2482
loc_2484:
    call far ptr _PlayAdlibEffect ; @2484
    add sp, 8 ; @2489
    pop bx ; @248C
    pop es ; @248D
    mov word ptr [bx + EnemyFlightSoundHandles], ax ; @248E
    ret ; @2492
; CONTRACT (tools/apply.py)
; Move and animate the bird; test stone hits and contact with its targeted player.
; In: BX is enemy byte index; DS=DGROUP.
; Out: offscreen stops sound and resets bird; stone hit reverses stone Y speed and selects +1C.
; Effects: contact fades the scene only for the target player and when fade step is nonnegative.
; Effects: collision tests occur only when the four-update animation countdown expires.
; END CONTRACT
public UpdateBirdFlight
UpdateBirdFlight:
    mov si, word ptr [bx + EnemyDescriptors] ; @2493
    mov ax, word ptr [bx + EnemyHorizontalSpeeds] ; @2497
    add ax, word ptr [bx + EnemyX32] ; @249B
    cmp ax, word ptr 0FC00h ; @249F
    jle loc_24AF ; @24A2
    cmp ax, word ptr 02800h ; @24A7
    jl loc_24B5 ; @24AA
loc_24AF:
    call StopBirdFlightSound ; @24AF
    jmp word ptr [si + 8] ; @24B2
loc_24B5:
    mov word ptr [bx + EnemyX32], ax ; @24B5
    dec word ptr [bx + EnemyAnimationCountdowns] ; @24B9
    jne loc_252A ; @24BD
    mov word ptr [bx + EnemyAnimationCountdowns], 4 ; @24C2
    add word ptr [bx + EnemyAnimationByteOffsets], 2 ; @24C8
loc_24CD:
    mov di, word ptr [bx + EnemyAnimationOrDropLists] ; @24CD
    add di, word ptr [bx + EnemyAnimationByteOffsets] ; @24D1
    mov ax, word ptr [di] ; @24D5
    cmp ax, word ptr 0FFFFh ; @24D7
    jne loc_24E7 ; @24DA
    mov word ptr [bx + EnemyAnimationByteOffsets], 0 ; @24DF
    jmp short loc_24CD ; @24E5
loc_24E7:
    mov word ptr [bx + EnemySpriteIds], ax ; @24E7
    call FindThrownStoneHittingEnemy ; @24EB
    js loc_2503 ; @24EE
    call StopBirdFlightSound ; @24F3
    neg word ptr [di + ds_2C6D] ; @24F6
    mov word ptr [di + ActorSpriteIds], 0222h ; @24FA
    jmp word ptr [si + 01Ch] ; @2500
loc_2503:
    call FindPlayerTouchingEnemy ; @2503
    js loc_252A ; @2506
    shr di, 1 ; @250B
    cmp di, word ptr [bx + EnemyDirectionOrTargetPlayer] ; @250D
    jne loc_252A ; @2511
    cmp word ptr ds:[ScreenFadeStep], 0 ; @2516
    jl loc_252A ; @251B
    mov ax, 0FFFEh ; @2520
    mov word ptr ds:[ScreenFadeStep], ax ; @2523
    add word ptr ds:[ScreenFadeLevel], ax ; @2526
loc_252A:
    ret ; @252A
; CONTRACT (tools/apply.py)
; Award the bird hit score and select its falling sprite.
; In: BX is enemy byte index; SI is enemy descriptor; DS=DGROUP.
; Out: installs descriptor +1E, adds descriptor +3A to 32-bit score, clears fall acceleration.
; Effects: chooses first frame from +36 or +38 according to horizontal speed sign.
; END CONTRACT
public StunBirdAndAwardScore
StunBirdAndAwardScore:
    mov ax, word ptr [si + 01Eh] ; @252B
    mov word ptr [bx + EnemyStateCallbacks], ax ; @252E
    mov ax, word ptr [si + 03Ah] ; @2532
    add word ptr ds:[ScoreLowWord], ax ; @2535
    adc word ptr ds:[ScoreHighWord], 0 ; @2539
    mov word ptr [bx + EnemyStateCounters], 0 ; @253E
    test word ptr [bx + EnemyHorizontalSpeeds], 0FFFFh ; @2544
    js loc_2554 ; @254A
    mov si, word ptr [si + 038h] ; @254F
    jmp short loc_2557 ; @2552
loc_2554:
    mov si, word ptr [si + 036h] ; @2554
loc_2557:
    mov ax, word ptr [si] ; @2557
    mov word ptr [bx + EnemySpriteIds], ax ; @2559
    ret ; @255D
; CONTRACT (tools/apply.py)
; Move a stunned bird sideways and accelerate its fall.
; In: BX is enemy byte index; DS=DGROUP.
; Out: fall acceleration rises to 40; signed screen exits tail-jump through descriptor +08.
; END CONTRACT
public UpdateStunnedBird
UpdateStunnedBird:
    mov ax, word ptr [bx + EnemyHorizontalSpeeds] ; @255E
    add ax, word ptr [bx + EnemyX32] ; @2562
    cmp ax, word ptr 0FC00h ; @2566
    jle loc_2576 ; @2569
    cmp ax, word ptr 02800h ; @256E
    jl loc_257D ; @2571
loc_2576:
    mov si, word ptr [bx + EnemyDescriptors] ; @2576
    jmp word ptr [si + 8] ; @257A
loc_257D:
    mov word ptr [bx + EnemyX32], ax ; @257D
    mov ax, word ptr [bx + EnemyStateCounters] ; @2581
    cmp ax, word ptr 028h ; @2585
    jge loc_2592 ; @2588
    inc ax ; @258D
    mov word ptr [bx + EnemyStateCounters], ax ; @258E
loc_2592:
    add ax, word ptr [bx + EnemyY32] ; @2592
    cmp ax, word ptr 01800h ; @2596
    jge short loc_2576 ; @2599
    mov word ptr [bx + EnemyY32], ax ; @259B
    ret ; @259F
; CONTRACT (tools/apply.py)
; Stop the bird flight effect using its saved channel handle.
; In: BX is enemy byte index; handle is 2D61+BX; DS=DGROUP.
; Effects: calls C:fn_1768 with one word argument; explicitly preserves BX and SI.
; END CONTRACT
StopBirdFlightSound:
    push bx ; @25A0
    push si ; @25A1
    push word ptr [bx + EnemyFlightSoundHandles] ; @25A2
loc_25A6:
    call far ptr _StopAdlibTrackChannel ; @25A6
    add sp, 2 ; @25AB
    pop si ; @25AE
    pop bx ; @25AF
    ret ; @25B0
; CONTRACT (tools/apply.py)
; Initialize the ground dinosaur's patrol animation.
; In: BX is enemy byte index; DS=DGROUP.
; Out: installs descriptor +0A and resets animation offset FFFE/ticks 1.
; END CONTRACT
public BeginTriopterusPatrol
; CONTRACT (tools/apply.py)
; Initialize the ground Triopterus's patrol animation.
; In: BX is enemy byte index; DS=DGROUP.
; Out: installs descriptor +0A and resets animation offset FFFE/ticks 1.
; END CONTRACT
BeginTriopterusPatrol:
    mov si, word ptr [bx + EnemyDescriptors] ; @25B1
    mov ax, word ptr [si + 0Ah] ; @25B5
    mov word ptr [bx + EnemyStateCallbacks], ax ; @25B8
    mov word ptr [bx + EnemyAnimationByteOffsets], 0FFFEh ; @25BC
    mov word ptr [bx + EnemyAnimationCountdowns], 1 ; @25C2
    ret ; @25C8
; CONTRACT (tools/apply.py)
; Patrol within the assigned platform and notice players or thrown stones.
; In: BX is enemy byte index; DS=DGROUP.
; Out: every four ticks moves, reverses at platform bounds, and loops directional animation.
; Effects: same-platform player selects +0C; stone hit reverses its Y speed and selects +1C.
; END CONTRACT
public UpdateTriopterusPatrol
; CONTRACT (tools/apply.py)
; Patrol within the assigned platform and notice players or thrown stones.
; In: BX is enemy byte index; DS=DGROUP.
; Out: every four ticks moves, reverses at platform bounds, and loops directional animation.
; Effects: same-platform player selects +0C; stone hit reverses its Y speed and selects +1C.
; END CONTRACT
UpdateTriopterusPatrol:
    mov si, word ptr [bx + EnemyDescriptors] ; @25C9
    dec word ptr [bx + EnemyAnimationCountdowns] ; @25CD
    jne loc_2636 ; @25D1
    mov di, word ptr [bx + EnemyPlatformIndices] ; @25D6
    shl di, 1 ; @25DA
    mov ax, word ptr [bx + EnemyHorizontalSpeeds] ; @25DC
    add ax, word ptr [bx + EnemyX32] ; @25E0
    mov word ptr [bx + EnemyX32], ax ; @25E4
    sar ax, 5 ; @25E8
    cmp ax, word ptr [di + PlatformLeftEdges] ; @25EB
    jl loc_2600 ; @25EF
    add ax, word ptr 020h ; @25F4
    cmp ax, word ptr [di + PlatformRightEdges] ; @25F7
    jl loc_2609 ; @25FB
loc_2600:
    neg word ptr [bx + EnemyHorizontalSpeeds] ; @2600
    xor word ptr [bx + EnemyDirectionOrTargetPlayer], 2 ; @2604
loc_2609:
    mov word ptr [bx + EnemyAnimationCountdowns], 4 ; @2609
    add word ptr [bx + EnemyAnimationByteOffsets], 2 ; @260F
loc_2614:
    mov bp, word ptr [bx + EnemyDirectionOrTargetPlayer] ; @2614
    mov di, word ptr ds:[bp + si + 022h] ; @2618
    add di, word ptr [bx + EnemyAnimationByteOffsets] ; @261C
    mov ax, word ptr [di] ; @2620
    cmp ax, word ptr 0FFFFh ; @2622
    jne loc_2632 ; @2625
    mov word ptr [bx + EnemyAnimationByteOffsets], 0 ; @262A
    jmp short loc_2614 ; @2630
loc_2632:
    mov word ptr [bx + EnemySpriteIds], ax ; @2632
loc_2636:
    mov ax, word ptr [bx + EnemyPlatformIndices] ; @2636
    xor di, di ; @263A
loc_263C:
    cmp ax, word ptr [di + PlayerPlatformIndices] ; @263C
    jne loc_2648 ; @2640
    jmp word ptr [si + 0Ch] ; @2645
loc_2648:
    add di, 2 ; @2648
    cmp di, word ptr ds:[PlayerArrayBytes] ; @264B
    jne short loc_263C ; @264F
    call FindThrownStoneHittingEnemy ; @2651
    js loc_2666 ; @2654
    neg word ptr [di + ds_2C6D] ; @2659
    mov word ptr [di + ActorSpriteIds], 0222h ; @265D
    jmp word ptr [si + 01Ch] ; @2663
loc_2666:
    ret ; @2666
; CONTRACT (tools/apply.py)
; Start the dinosaur's 140-update alert state.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +0E and resets animation offset FFFE/ticks 1.
; END CONTRACT
public BeginTriopterusAlert
; CONTRACT (tools/apply.py)
; Start the Triopterus's 140-update alert state.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +0E and resets animation offset FFFE/ticks 1.
; END CONTRACT
BeginTriopterusAlert:
    mov ax, word ptr [si + 0Eh] ; @2667
    mov word ptr [bx + EnemyStateCallbacks], ax ; @266A
    mov word ptr [bx + EnemyAnimationByteOffsets], 0FFFEh ; @266E
    mov word ptr [bx + EnemyAnimationCountdowns], 1 ; @2674
    mov word ptr [bx + EnemyStateCounters], 08Ch ; @267A
    ret ; @2680
; CONTRACT (tools/apply.py)
; Animate the alert dinosaur and face a player on its platform.
; In: BX is enemy byte index; DS=DGROUP.
; Out: timer zero selects +10; player leaves platform selects +08; stone hit selects +1C.
; Effects: five-update animation; direction and speed sign track the first matching player.
; END CONTRACT
public UpdateTriopterusAlert
; CONTRACT (tools/apply.py)
; Animate the alert Triopterus and face a player on its platform.
; In: BX is enemy byte index; DS=DGROUP.
; Out: timer zero selects +10; player leaves platform selects +08; stone hit selects +1C.
; Effects: five-update animation; direction and speed sign track the first matching player.
; END CONTRACT
UpdateTriopterusAlert:
    mov si, word ptr [bx + EnemyDescriptors] ; @2681
    dec word ptr [bx + EnemyStateCounters] ; @2685
    jne loc_2691 ; @2689
    jmp word ptr [si + 010h] ; @268E
loc_2691:
    dec word ptr [bx + EnemyAnimationCountdowns] ; @2691
    jne loc_26C7 ; @2695
    mov word ptr [bx + EnemyAnimationCountdowns], 5 ; @269A
    add word ptr [bx + EnemyAnimationByteOffsets], 2 ; @26A0
loc_26A5:
    mov bp, word ptr [bx + EnemyDirectionOrTargetPlayer] ; @26A5
    mov di, word ptr ds:[bp + si + 02Eh] ; @26A9
    add di, word ptr [bx + EnemyAnimationByteOffsets] ; @26AD
    mov ax, word ptr [di] ; @26B1
    cmp ax, word ptr 0FFFFh ; @26B3
    jne loc_26C3 ; @26B6
    mov word ptr [bx + EnemyAnimationByteOffsets], 0 ; @26BB
    jmp short loc_26A5 ; @26C1
loc_26C3:
    mov word ptr [bx + EnemySpriteIds], ax ; @26C3
loc_26C7:
    call FindThrownStoneHittingEnemy ; @26C7
    js loc_26DC ; @26CA
    neg word ptr [di + ds_2C6D] ; @26CF
    mov word ptr [di + ActorSpriteIds], 0222h ; @26D3
    jmp word ptr [si + 01Ch] ; @26D9
loc_26DC:
    mov ax, word ptr [bx + EnemyPlatformIndices] ; @26DC
    xor di, di ; @26E0
loc_26E2:
    cmp ax, word ptr [di + PlayerPlatformIndices] ; @26E2
    je loc_26F7 ; @26E6
    add di, 2 ; @26EB
    cmp di, word ptr ds:[PlayerArrayBytes] ; @26EE
    jne short loc_26E2 ; @26F2
    jmp word ptr [si + 8] ; @26F4
loc_26F7:
    mov cx, word ptr [bx + EnemyHorizontalSpeeds] ; @26F7
    mov ax, word ptr [bx + EnemyX32] ; @26FB
    cmp ax, word ptr [di + PlayerX32] ; @26FF
    jl loc_2717 ; @2703
    xor ax, ax ; @2708
    test cx, 0FFFFh ; @270A
    js loc_2725 ; @270E
    neg cx ; @2713
    jmp short loc_2725 ; @2715
loc_2717:
    mov ax, 2 ; @2717
    test cx, 0FFFFh ; @271A
    jns loc_2725 ; @271E
    neg cx ; @2723
loc_2725:
    mov word ptr [bx + EnemyDirectionOrTargetPlayer], ax ; @2725
    mov word ptr [bx + EnemyHorizontalSpeeds], cx ; @2729
    ret ; @272D
; CONTRACT (tools/apply.py)
; Initialize the dinosaur charge animation and acceleration.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +12; resets animation and clears state acceleration.
; END CONTRACT
public BeginTriopterusCharge
; CONTRACT (tools/apply.py)
; Initialize the Triopterus charge animation and acceleration.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +12; resets animation and clears state acceleration.
; END CONTRACT
BeginTriopterusCharge:
    mov ax, word ptr [si + 012h] ; @272E
    mov word ptr [bx + EnemyStateCallbacks], ax ; @2731
    mov word ptr [bx + EnemyAnimationByteOffsets], 0FFFEh ; @2735
    mov word ptr [bx + EnemyAnimationCountdowns], 1 ; @273B
    mov word ptr [bx + EnemyStateCounters], 0 ; @2741
    ret ; @2747
; CONTRACT (tools/apply.py)
; Charge toward a same-platform player and transfer impact motion on contact.
; In: BX is enemy byte index; DS=DGROUP.
; Out: no platform player selects +14; contact kicks player upward, clears platform, selects +18.
; Effects: acceleration adds direction-1 each update; X adds speed plus new acceleration.
; Effects: player X velocity=(speed+acceleration)<<5, Y velocity uses the same value <<4.
; END CONTRACT
public UpdateTriopterusCharge
; CONTRACT (tools/apply.py)
; Charge toward a same-platform player and transfer impact motion on contact.
; In: BX is enemy byte index; DS=DGROUP.
; Out: no platform player selects +14; contact kicks player upward, clears platform, selects +18.
; Effects: acceleration adds direction-1 each update; X adds speed plus new acceleration.
; Effects: player X velocity=(speed+acceleration)<<5, Y velocity uses the same value <<4.
; END CONTRACT
UpdateTriopterusCharge:
    mov si, word ptr [bx + EnemyDescriptors] ; @2748
    dec word ptr [bx + EnemyAnimationCountdowns] ; @274C
    jne loc_2782 ; @2750
    mov word ptr [bx + EnemyAnimationCountdowns], 4 ; @2755
    add word ptr [bx + EnemyAnimationByteOffsets], 2 ; @275B
loc_2760:
    mov bp, word ptr [bx + EnemyDirectionOrTargetPlayer] ; @2760
    mov di, word ptr ds:[bp + si + 026h] ; @2764
    add di, word ptr [bx + EnemyAnimationByteOffsets] ; @2768
    mov ax, word ptr [di] ; @276C
    cmp ax, word ptr 0FFFFh ; @276E
    jne loc_277E ; @2771
    mov word ptr [bx + EnemyAnimationByteOffsets], 0 ; @2776
    jmp short loc_2760 ; @277C
loc_277E:
    mov word ptr [bx + EnemySpriteIds], ax ; @277E
loc_2782:
    call FindThrownStoneHittingEnemy ; @2782
    js loc_2797 ; @2785
    neg word ptr [di + ds_2C6D] ; @278A
    mov word ptr [di + ActorSpriteIds], 0222h ; @278E
    jmp word ptr [si + 01Ch] ; @2794
loc_2797:
    mov ax, word ptr [bx + EnemyPlatformIndices] ; @2797
    xor di, di ; @279B
loc_279D:
    cmp ax, word ptr [di + PlayerPlatformIndices] ; @279D
    je loc_27B2 ; @27A1
    add di, 2 ; @27A6
    cmp di, word ptr ds:[PlayerArrayBytes] ; @27A9
    jne short loc_279D ; @27AD
    jmp word ptr [si + 014h] ; @27AF
loc_27B2:
    mov cx, word ptr [bx + EnemyHorizontalSpeeds] ; @27B2
    mov ax, word ptr [bx + EnemyX32] ; @27B6
    cmp ax, word ptr [di + PlayerX32] ; @27BA
    jl loc_27D2 ; @27BE
    xor ax, ax ; @27C3
    test cx, 0FFFFh ; @27C5
    js loc_27E0 ; @27C9
    neg cx ; @27CE
    jmp short loc_27E0 ; @27D0
loc_27D2:
    mov ax, 2 ; @27D2
    test cx, 0FFFFh ; @27D5
    jns loc_27E0 ; @27D9
    neg cx ; @27DE
loc_27E0:
    mov word ptr [bx + EnemyDirectionOrTargetPlayer], ax ; @27E0
    mov word ptr [bx + EnemyHorizontalSpeeds], cx ; @27E4
    mov ax, word ptr [bx + EnemyDirectionOrTargetPlayer] ; @27E8
    dec ax ; @27EC
    add ax, word ptr [bx + EnemyStateCounters] ; @27ED
    mov word ptr [bx + EnemyStateCounters], ax ; @27F1
    add ax, word ptr [bx + EnemyHorizontalSpeeds] ; @27F5
    add ax, word ptr [bx + EnemyX32] ; @27F9
    mov word ptr [bx + EnemyX32], ax ; @27FD
    call FindPlayerTouchingEnemy ; @2801
    js loc_282F ; @2804
    sub word ptr [di + PlayerY32], 020h ; @2809
    mov ax, word ptr [bx + EnemyHorizontalSpeeds] ; @280E
    add ax, word ptr [bx + EnemyStateCounters] ; @2812
    push ax ; @2816
    shl ax, 5 ; @2817
    mov word ptr [di + PlayerHorizontalVelocities], ax ; @281A
    pop ax ; @281E
    shl ax, 4 ; @281F
    mov word ptr [di + PlayerVerticalVelocities], ax ; @2822
    mov word ptr [di + PlayerPlatformIndices], 0FFFFh ; @2826
    jmp word ptr [si + 018h] ; @282C
loc_282F:
    ret ; @282F
; CONTRACT (tools/apply.py)
; Start the dinosaur recovery animation after losing its platform target.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +16 and resets animation offset FFFE/ticks 1.
; END CONTRACT
public BeginTriopterusRecovery
; CONTRACT (tools/apply.py)
; Start the Triopterus recovery animation after losing its platform target.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +16 and resets animation offset FFFE/ticks 1.
; END CONTRACT
BeginTriopterusRecovery:
    mov ax, word ptr [si + 016h] ; @2830
    mov word ptr [bx + EnemyStateCallbacks], ax ; @2833
    mov word ptr [bx + EnemyAnimationByteOffsets], 0FFFEh ; @2837
    mov word ptr [bx + EnemyAnimationCountdowns], 1 ; @283D
    ret ; @2843
; CONTRACT (tools/apply.py)
; Play the dinosaur's finite directional recovery sequence.
; In: BX is enemy byte index; DS=DGROUP.
; Out: sequence FFFF selects +08; a stone hit reverses stone Y speed and selects +1C.
; Effects: advances descriptor +2A/+2C sequence every four updates.
; END CONTRACT
public AnimateTriopterusRecovery
; CONTRACT (tools/apply.py)
; Play the Triopterus's finite directional recovery sequence.
; In: BX is enemy byte index; DS=DGROUP.
; Out: sequence FFFF selects +08; a stone hit reverses stone Y speed and selects +1C.
; Effects: advances descriptor +2A/+2C sequence every four updates.
; END CONTRACT
AnimateTriopterusRecovery:
    mov si, word ptr [bx + EnemyDescriptors] ; @2844
    dec word ptr [bx + EnemyAnimationCountdowns] ; @2848
    jne loc_2879 ; @284C
    mov word ptr [bx + EnemyAnimationCountdowns], 4 ; @2851
    add word ptr [bx + EnemyAnimationByteOffsets], 2 ; @2857
    mov bp, word ptr [bx + EnemyDirectionOrTargetPlayer] ; @285C
    mov di, word ptr ds:[bp + si + 02Ah] ; @2860
    add di, word ptr [bx + EnemyAnimationByteOffsets] ; @2864
    mov ax, word ptr [di] ; @2868
    cmp ax, word ptr 0FFFFh ; @286A
    jne loc_2875 ; @286D
    jmp word ptr [si + 8] ; @2872
loc_2875:
    mov word ptr [bx + EnemySpriteIds], ax ; @2875
loc_2879:
    call FindThrownStoneHittingEnemy ; @2879
    js loc_288E ; @287C
    neg word ptr [di + ds_2C6D] ; @2881
    mov word ptr [di + ActorSpriteIds], 0222h ; @2885
    jmp word ptr [si + 01Ch] ; @288B
loc_288E:
    ret ; @288E
; CONTRACT (tools/apply.py)
; Start the dinosaur recovery sequence following a player impact.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +16, not +1A; resets animation offset FFFE/ticks 1.
; Effects: supplied descriptor therefore routes subsequent updates to 2844, not 28A3.
; END CONTRACT
public BeginTriopterusImpactRecovery
; CONTRACT (tools/apply.py)
; Start the Triopterus recovery sequence following a player impact.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +16, not +1A; resets animation offset FFFE/ticks 1.
; Effects: supplied descriptor therefore routes subsequent updates to 2844, not 28A3.
; END CONTRACT
BeginTriopterusImpactRecovery:
    mov ax, word ptr [si + 016h] ; @288F
    mov word ptr [bx + EnemyStateCallbacks], ax ; @2892
    mov word ptr [bx + EnemyAnimationByteOffsets], 0FFFEh ; @2896
    mov word ptr [bx + EnemyAnimationCountdowns], 1 ; @289C
    ret ; @28A2
; CONTRACT (tools/apply.py)
; Play the alternate directional dinosaur recovery sequence.
; In: BX is enemy byte index; DS=DGROUP.
; Out: descriptor +32/+34 FFFF selects +08; a stone hit reverses stone Y speed/selects +1C.
; Effects: descriptor +1A points here, but initializer 288F installs +16 instead.
; END CONTRACT
public AnimateTriopterusImpactRecovery
; CONTRACT (tools/apply.py)
; Play the alternate directional Triopterus recovery sequence.
; In: BX is enemy byte index; DS=DGROUP.
; Out: descriptor +32/+34 FFFF selects +08; a stone hit reverses stone Y speed/selects +1C.
; Effects: descriptor +1A points here, but initializer 288F installs +16 instead.
; END CONTRACT
AnimateTriopterusImpactRecovery:
    mov si, word ptr [bx + EnemyDescriptors] ; @28A3
    dec word ptr [bx + EnemyAnimationCountdowns] ; @28A7
    jne loc_28D8 ; @28AB
    mov word ptr [bx + EnemyAnimationCountdowns], 4 ; @28B0
    add word ptr [bx + EnemyAnimationByteOffsets], 2 ; @28B6
    mov bp, word ptr [bx + EnemyDirectionOrTargetPlayer] ; @28BB
    mov di, word ptr ds:[bp + si + 032h] ; @28BF
    add di, word ptr [bx + EnemyAnimationByteOffsets] ; @28C3
    mov ax, word ptr [di] ; @28C7
    cmp ax, word ptr 0FFFFh ; @28C9
    jne loc_28D4 ; @28CC
    jmp word ptr [si + 8] ; @28D1
loc_28D4:
    mov word ptr [bx + EnemySpriteIds], ax ; @28D4
loc_28D8:
    call FindThrownStoneHittingEnemy ; @28D8
    js loc_28ED ; @28DB
    neg word ptr [di + ds_2C6D] ; @28E0
    mov word ptr [di + ActorSpriteIds], 0222h ; @28E4
    jmp word ptr [si + 01Ch] ; @28EA
loc_28ED:
    ret ; @28ED
; CONTRACT (tools/apply.py)
; Award dinosaur hit points and start its 350-update stun animation.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +1E, adds +3A to 32-bit score, resets animation and stun timer.
; END CONTRACT
public StunTriopterusAndAwardScore
; CONTRACT (tools/apply.py)
; Award Triopterus hit points and start its 350-update stun animation.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +1E, adds +3A to 32-bit score, resets animation and stun timer.
; END CONTRACT
StunTriopterusAndAwardScore:
    mov ax, word ptr [si + 01Eh] ; @28EE
    mov word ptr [bx + EnemyStateCallbacks], ax ; @28F1
    mov ax, word ptr [si + 03Ah] ; @28F5
    add word ptr ds:[ScoreLowWord], ax ; @28F8
    adc word ptr ds:[ScoreHighWord], 0 ; @28FC
    mov word ptr [bx + EnemyAnimationByteOffsets], 0FFFEh ; @2901
    mov word ptr [bx + EnemyAnimationCountdowns], 1 ; @2907
    mov word ptr [bx + EnemyStateCounters], 015Eh ; @290D
    ret ; @2913
; CONTRACT (tools/apply.py)
; Loop the directional stunned dinosaur sequence until recovery.
; In: BX is enemy byte index; DS=DGROUP.
; Out: timer zero selects descriptor +08; animation +36/+38 advances every four updates.
; END CONTRACT
public UpdateStunnedTriopterus
; CONTRACT (tools/apply.py)
; Loop the directional stunned Triopterus sequence until recovery.
; In: BX is enemy byte index; DS=DGROUP.
; Out: timer zero selects descriptor +08; animation +36/+38 advances every four updates.
; END CONTRACT
UpdateStunnedTriopterus:
    mov si, word ptr [bx + EnemyDescriptors] ; @2914
    dec word ptr [bx + EnemyStateCounters] ; @2918
    jne loc_2924 ; @291C
    jmp word ptr [si + 8] ; @2921
loc_2924:
    dec word ptr [bx + EnemyAnimationCountdowns] ; @2924
    jne loc_295A ; @2928
    mov word ptr [bx + EnemyAnimationCountdowns], 4 ; @292D
    add word ptr [bx + EnemyAnimationByteOffsets], 2 ; @2933
loc_2938:
    mov bp, word ptr [bx + EnemyDirectionOrTargetPlayer] ; @2938
    mov di, word ptr ds:[bp + si + 036h] ; @293C
    add di, word ptr [bx + EnemyAnimationByteOffsets] ; @2940
    mov ax, word ptr [di] ; @2944
    cmp ax, word ptr 0FFFFh ; @2946
    jne loc_2956 ; @2949
    mov word ptr [bx + EnemyAnimationByteOffsets], 0 ; @294E
    jmp short loc_2938 ; @2954
loc_2956:
    mov word ptr [bx + EnemySpriteIds], ax ; @2956
loc_295A:
    ret ; @295A
; CONTRACT (tools/apply.py)
; Initialize descriptor 76A8's stationary hazard animation.
; In: BX is enemy byte index; DS=DGROUP.
; Out: installs descriptor +12 and resets animation offset FFFE/ticks 1.
; END CONTRACT
public InitializeDinoAnimation
; CONTRACT (tools/apply.py)
; Initialize Dino's stationary force animation (descriptor 76A8).
; In: BX is enemy byte index; DS=DGROUP.
; Out: installs descriptor +12 and resets animation offset FFFE/ticks 1.
; END CONTRACT
InitializeDinoAnimation:
    mov si, word ptr [bx + EnemyDescriptors] ; @295B
    mov ax, word ptr [si + 012h] ; @295F
    mov word ptr [bx + EnemyStateCallbacks], ax ; @2962
    mov word ptr [bx + EnemyAnimationByteOffsets], 0FFFEh ; @2966
    mov word ptr [bx + EnemyAnimationCountdowns], 1 ; @296C
    ret ; @2972
; CONTRACT (tools/apply.py)
; Animate descriptor 76A8 and push nearby players horizontally.
; In: BX is enemy byte index; DS=DGROUP.
; Out: loops +26 sequence every 15 updates; frame offset 6 plays effect 3265.
; Effects: adds +29h or -29h to player X velocity by animation phase; stone hit selects +1C.
; Effects: player scan retries on DI=2 equal to player count; does not use player-array bytes.
; END CONTRACT
public UpdateDinoForce
; CONTRACT (tools/apply.py)
; Animate Dino and push nearby players horizontally.
; In: BX is enemy byte index; DS=DGROUP.
; Out: loops +26 sequence every 15 updates; frame offset 6 plays effect 3265.
; Effects: adds +29h or -29h to player X velocity by animation phase; stone hit selects +1C.
; Effects: player scan retries on DI=2 equal to player count; does not use player-array bytes.
; END CONTRACT
UpdateDinoForce:
    mov si, word ptr [bx + EnemyDescriptors] ; @2973
    dec word ptr [bx + EnemyAnimationCountdowns] ; @2977
loc_297B:
    jne loc_29C9 ; @297B
    mov word ptr [bx + EnemyAnimationCountdowns], 0Fh ; @2980
    add word ptr [bx + EnemyAnimationByteOffsets], 2 ; @2986
    cmp word ptr [bx + EnemyAnimationByteOffsets], 6 ; @298B
loc_2990:
    jne loc_29AC ; @2990
    push bx ; @2995
    push si ; @2996
    push 1 ; @2997
    push word ptr 0FFh ; @2999
loc_299C:
    push seg ext_3265 ; @299C
    nop ; @299F
    push 0 ; @29A0
loc_29A2:
    call far ptr _PlayAdlibEffect ; @29A2
    add sp, 8 ; @29A7
    pop si ; @29AA
    pop bx ; @29AB
loc_29AC:
    mov di, word ptr [si + 026h] ; @29AC
    add di, word ptr [bx + EnemyAnimationByteOffsets] ; @29AF
    mov ax, word ptr [di] ; @29B3
    cmp ax, word ptr 0FFFFh ; @29B5
    jne loc_29C5 ; @29B8
    mov word ptr [bx + EnemyAnimationByteOffsets], 0 ; @29BD
    jmp short loc_29AC ; @29C3
loc_29C5:
    mov word ptr [bx + EnemySpriteIds], ax ; @29C5
loc_29C9:
    xor di, di ; @29C9
loc_29CB:
    mov ax, word ptr [si + 2] ; @29CB
    sub ax, word ptr 09h ; @29CE
    shl ax, 5 ; @29D1
    add ax, word ptr [bx + EnemyY32] ; @29D4
    cmp ax, word ptr [di + PlayerY32] ; @29D8
    jl loc_2A3A ; @29DC
    mov ax, word ptr [si + 2] ; @29E1
    sub ax, word ptr 01Eh ; @29E4
    shl ax, 5 ; @29E7
    add ax, word ptr [bx + EnemyY32] ; @29EA
    cmp ax, word ptr [di + PlayerY32] ; @29EE
    jg loc_2A3A ; @29F2
    mov ax, word ptr [si] ; @29F7
    sub ax, word ptr 010h ; @29F9
    shl ax, 5 ; @29FC
    add ax, word ptr [bx + EnemyX32] ; @29FF
    cmp ax, word ptr [di + PlayerX32] ; @2A03
    jl loc_2A3A ; @2A07
    mov ax, word ptr [si] ; @2A0C
    sub ax, word ptr 068h ; @2A0E
    shl ax, 5 ; @2A11
    add ax, word ptr [bx + EnemyX32] ; @2A14
    sub ax, word ptr 0340h ; @2A18
    cmp ax, word ptr [di + PlayerX32] ; @2A1B
    jg loc_2A3A ; @2A1F
    cmp word ptr [bx + EnemyAnimationByteOffsets], 5 ; @2A24
    jl loc_2A33 ; @2A29
    mov ax, 0FFD7h ; @2A2E
    jmp short loc_2A36 ; @2A31
loc_2A33:
    mov ax, 029h ; @2A33
loc_2A36:
    add word ptr [di + PlayerHorizontalVelocities], ax ; @2A36
loc_2A3A:
    add di, 2 ; @2A3A
    cmp di, word ptr ds:[PlayerCount] ; @2A3D
    je short loc_29CB ; @2A41
    call FindThrownStoneHittingEnemy ; @2A43
    js loc_2A52 ; @2A46
    neg word ptr [di + ds_2C6D] ; @2A4B
    jmp word ptr [si + 01Ch] ; @2A4F
loc_2A52:
    ret ; @2A52
; CONTRACT (tools/apply.py)
; Award descriptor 76A8's hit score and select its 350-update stun state.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +1E, adds +3A to 32-bit score, and chooses first +36 sprite.
; END CONTRACT
public StunDinoAndAwardScore
; CONTRACT (tools/apply.py)
; Award Dino's hit score and select its 350-update stun state.
; In: BX is enemy byte index; SI is its descriptor; DS=DGROUP.
; Out: installs descriptor +1E, adds +3A to 32-bit score, and chooses first +36 sprite.
; END CONTRACT
StunDinoAndAwardScore:
    mov ax, word ptr [si + 01Eh] ; @2A53
    mov word ptr [bx + EnemyStateCallbacks], ax ; @2A56
    mov ax, word ptr [si + 03Ah] ; @2A5A
    add word ptr ds:[ScoreLowWord], ax ; @2A5D
    adc word ptr ds:[ScoreHighWord], 0 ; @2A61
    mov word ptr [bx + EnemyStateCounters], 015Eh ; @2A66
    mov si, word ptr [si + 036h] ; @2A6C
    mov ax, word ptr [si] ; @2A6F
    mov word ptr [bx + EnemySpriteIds], ax ; @2A71
    ret ; @2A75
; CONTRACT (tools/apply.py)
; Count down descriptor 76A8's stun timer.
; In: BX is enemy byte index; DS=DGROUP.
; Out: exactly-zero state countdown tail-jumps through descriptor +10.
; END CONTRACT
public UpdateStunnedDino
; CONTRACT (tools/apply.py)
; Count down Dino's stun timer.
; In: BX is enemy byte index; DS=DGROUP.
; Out: exactly-zero state countdown tail-jumps through descriptor +10.
; END CONTRACT
UpdateStunnedDino:
    dec word ptr [bx + EnemyStateCounters] ; @2A76
    jne loc_2A86 ; @2A7A
    mov si, word ptr [bx + EnemyDescriptors] ; @2A7F
    jmp word ptr [si + 010h] ; @2A83
loc_2A86:
    ret ; @2A86
; CONTRACT (tools/apply.py)
; Initialize descriptor 76E4's tree animation and cached positions.
; In: BX is enemy byte index; DS=DGROUP.
; Out: installs +0A; resets animation; writes x32/y32 shifted LEFT five to cached fields.
; Effects: the left shifts are preserved even though the renderer later treats caches as pixels.
; END CONTRACT
public InitializeFruitTreeAnimation
InitializeFruitTreeAnimation:
    mov si, word ptr [bx + EnemyDescriptors] ; @2A87
    mov ax, word ptr [si + 0Ah] ; @2A8B
    mov word ptr [bx + EnemyStateCallbacks], ax ; @2A8E
    mov word ptr [bx + EnemyAnimationByteOffsets], 0FFFEh ; @2A92
    mov word ptr [bx + EnemyAnimationCountdowns], 1 ; @2A98
    mov ax, word ptr [bx + EnemyX32] ; @2A9E
    shl ax, 5 ; @2AA2
    mov word ptr [bx + EnemyDrawX], ax ; @2AA5
    mov ax, word ptr [bx + EnemyY32] ; @2AA9
    shl ax, 5 ; @2AAD
    mov word ptr [bx + EnemyDrawY], ax ; @2AB0
    ret ; @2AB4
; CONTRACT (tools/apply.py)
; Animate the tree and react to a descending thrown stone.
; In: BX is enemy byte index; DS=DGROUP.
; Out: every six updates loops +22 sequence; a hit sets stone sprite 0222 and selects +1C.
; Effects: stone vertical speed becomes NEG then SAR 1; +1C spawns the next falling reward.
; END CONTRACT
public UpdateFruitTreeAnimation
UpdateFruitTreeAnimation:
    dec word ptr [bx + EnemyAnimationCountdowns] ; @2AB5
    jne loc_2B0B ; @2AB9
    mov si, word ptr [bx + EnemyDescriptors] ; @2ABE
    mov word ptr [bx + EnemyAnimationCountdowns], 6 ; @2AC2
    add word ptr [bx + EnemyAnimationByteOffsets], 2 ; @2AC8
loc_2ACD:
    mov di, word ptr [si + 022h] ; @2ACD
    add di, word ptr [bx + EnemyAnimationByteOffsets] ; @2AD0
    mov ax, word ptr [di] ; @2AD4
    cmp ax, word ptr 0FFFFh ; @2AD6
    jne loc_2AE6 ; @2AD9
    mov word ptr [bx + EnemyAnimationByteOffsets], 0 ; @2ADE
    jmp short loc_2ACD ; @2AE4
loc_2AE6:
    mov word ptr [bx + EnemySpriteIds], ax ; @2AE6
    call FindThrownStoneHittingEnemy ; @2AEA
    js loc_2B0B ; @2AED
    mov ax, word ptr [di + ds_2C6D] ; @2AF2
    neg ax ; @2AF6
    sar ax, 1 ; @2AF8
    mov word ptr [di + ds_2C6D], ax ; @2AFA
    mov word ptr [di + ActorSpriteIds], 0222h ; @2AFE
    mov si, word ptr [bx + EnemyDescriptors] ; @2B04
    jmp word ptr [si + 01Ch] ; @2B08
loc_2B0B:
    ret ; @2B0B
; CONTRACT (tools/apply.py)
; Release the next tree reward at the colliding thrown stone and play the reward effect.
; In: DS=DGROUP; BX=tree slot byte index; SI=tree descriptor; DI=stone actor byte index.
; Out: tree callback=descriptor+1Eh, cooldown=210, sprite=00E8h; reward cursor advances 2.
; The item receives stone X/Y, horizontal speed and NEG(vertical speed) SAR 2.
; Effects: indirect descriptor+4 spawn, then far C effect 1852 with 3274:0, FFh, 1.
; BX is saved around the C call; spawn's full-pool stack defect is inherited.
; END CONTRACT
public ReleaseTreeReward
ReleaseTreeReward:
    mov ax, word ptr [si + 01Eh] ; @2B0C
    mov word ptr [bx + EnemyStateCallbacks], ax ; @2B0F
    mov word ptr [bx + EnemyStateCounters], 0D2h ; @2B13
    mov word ptr [bx + EnemySpriteIds], 0E8h ; @2B19
    mov ax, word ptr [di + ActorX32] ; @2B1F
    mov bp, word ptr [di + ActorY32] ; @2B23
    mov cx, word ptr [di + ds_2ACD] ; @2B27
    mov dx, word ptr [di + ds_2C6D] ; @2B2B
    neg dx ; @2B2F
    sar dx, 2 ; @2B31
    mov si, word ptr [bx + EnemyAnimationOrDropLists] ; @2B34
    mov si, word ptr [si] ; @2B38
    call word ptr [si + 4] ; @2B3A
    add word ptr [bx + EnemyAnimationOrDropLists], 2 ; @2B3D
    push bx ; @2B42
    push 1 ; @2B43
    push word ptr 0FFh ; @2B45
loc_2B48:
    push seg ext_3274 ; @2B48
    nop ; @2B4B
    push 0 ; @2B4C
loc_2B4E:
    call far ptr _PlayAdlibEffect ; @2B4E
    add sp, 8 ; @2B53
    pop bx ; @2B56
    ret ; @2B57
; CONTRACT (tools/apply.py)
; Count down the tree reward delay and select its next descriptor callback at zero.
; In: DS=DGROUP; BX=tree slot byte index; tree reward cursor references a near-pointer list.
; Out: decrement the 16-bit delay; at zero choose descriptor+0Ah, or +20h on FFFFh.
; Effects/quirks: equality-only expiry; zero on entry wraps to FFFFh without transitioning.
; END CONTRACT
public AdvanceTreeRewardCooldown
AdvanceTreeRewardCooldown:
    mov si, word ptr [bx + EnemyDescriptors] ; @2B58
    dec word ptr [bx + EnemyStateCounters] ; @2B5C
    jne loc_2B7D ; @2B60
    mov di, word ptr [bx + EnemyAnimationOrDropLists] ; @2B65
    cmp word ptr [di], -1 ; @2B69
    je loc_2B76 ; @2B6C
    mov ax, word ptr [si + 0Ah] ; @2B71
    jmp short loc_2B79 ; @2B74
loc_2B76:
    mov ax, word ptr [si + 020h] ; @2B76
loc_2B79:
    mov word ptr [bx + EnemyStateCallbacks], ax ; @2B79
loc_2B7D:
    ret ; @2B7D
; CONTRACT (tools/apply.py)
; No-op callback selected when the tree reward list is exhausted.
; In: a near callback return address; descriptor 76E4h holds this entry at +20h.
; Out: immediate near return; registers and flags unchanged.
; END CONTRACT
public IgnoreExhaustedTree
IgnoreExhaustedTree:
    ret ; @2B7E
; CONTRACT (tools/apply.py)
; Dispatch active falling-item slots from slot 11 down to slot 0.
; In: DS=DGROUP; twelve parallel word arrays use even byte indices 0..16h.
; Out: call each non-FFFFh sprite slot's near callback in FallingItemCallbacks.
; Clobbers: BX ends FFFEh with the observed callbacks; callbacks must preserve the slot BX.
; Effects/quirks: dispatch tests exactly FFFFh, whereas allocation accepts any negative sprite.
; END CONTRACT
DispatchFallingItems:
    mov bx, 016h ; @2B7F
loc_2B82:
    cmp word ptr [bx + FallingItemSprites], -1 ; @2B82
    je loc_2B90 ; @2B87
    call word ptr [bx + FallingItemCallbacks] ; @2B8C
loc_2B90:
    sub bx, 2 ; @2B90
    jns short loc_2B82 ; @2B93
    ret ; @2B95
; CONTRACT (tools/apply.py)
; Allocate the highest free falling-item slot and initialize its descriptor-driven flight.
; In: DS=DGROUP; SI=item descriptor; AX/BP=launch X/Y in 1/32 pixel units;
; CX=horizontal step; DX=vertical launch term; any sprite with bit 15 set is free.
; Out on success: X=AX-(descriptor[0]<<5), Y=BP-(descriptor[2]<<4);
; vertical step=-(DX+descriptor[0Ch]);
; sprite=descriptor[10h], callback=descriptor[6]; BX restored, AX/BP/DX/DI changed.
; Original bug: when all 12 slots are occupied, RET consumes the saved input BX as IP;
; the real return address stays on the stack. This path is not a normal failure return.
; END CONTRACT
public SpawnFallingItem
SpawnFallingItem:
    push bx ; @2B96
    mov bx, 016h ; @2B97
loc_2B9A:
    test word ptr [bx + FallingItemSprites], 0FFFFh ; @2B9A
    js loc_2BAC ; @2BA0
    sub bx, 2 ; @2BA5
    jns short loc_2B9A ; @2BA8
    jmp short loc_2BE3 ; @2BAA
loc_2BAC:
    mov word ptr [bx + FallingItemDescriptors], si ; @2BAC
    mov di, word ptr [si] ; @2BB0
    shl di, 5 ; @2BB2
    sub ax, di ; @2BB5
    mov word ptr [bx + FallingItemX], ax ; @2BB7
    mov di, word ptr [si + 2] ; @2BBB
    shl di, 4 ; @2BBE
    sub bp, di ; @2BC1
    mov word ptr [bx + FallingItemY], bp ; @2BC3
    mov word ptr [bx + FallingItemMotionOrLifetime], cx ; @2BC7
    add dx, word ptr [si + 0Ch] ; @2BCB
    neg dx ; @2BCE
    mov word ptr [bx + FallingItemVerticalStep], dx ; @2BD0
    mov ax, word ptr [si + 010h] ; @2BD4
    mov word ptr [bx + FallingItemSprites], ax ; @2BD7
    mov ax, word ptr [si + 6] ; @2BDB
    mov word ptr [bx + FallingItemCallbacks], ax ; @2BDE
    pop bx ; @2BE2
loc_2BE3:
    ret ; @2BE3
; CONTRACT (tools/apply.py)
; Advance one item in flight, apply gravity, and tail-dispatch its platform landing callback.
; In: DS=DGROUP; BX=item slot byte index; positions and steps use 1/32 pixel units.
; Out: X+=horizontal step, vertical step+=3; Y+=vertical step, with 16-bit wrapping.
; Disable sprite on signed X<=-0200h or X>=2800h, or descending Y>=1800h.
; On descent, require old bottom<platform Y<=new bottom, center>=left and center-1<=right.
; Landing snaps Y to (platform Y-height)<<5 and JMPs descriptor+8; DI=platform byte index.
; No platform test while rising. Offscreen removal changes only the sprite, leaving stale fields.
; END CONTRACT
public AdvanceFallingItem
AdvanceFallingItem:
    mov si, word ptr [bx + FallingItemDescriptors] ; @2BE4
    mov ax, word ptr [bx + FallingItemMotionOrLifetime] ; @2BE8
    add ax, word ptr [bx + FallingItemX] ; @2BEC
    cmp ax, word ptr 0FE00h ; @2BF0
    jle loc_2C2D ; @2BF3
    cmp ax, word ptr 02800h ; @2BF8
    jge loc_2C2D ; @2BFB
    mov word ptr [bx + FallingItemX], ax ; @2C00
    mov ax, word ptr [bx + FallingItemVerticalStep] ; @2C04
    add ax, word ptr 03h ; @2C08
    mov word ptr [bx + FallingItemVerticalStep], ax ; @2C0B
    test ax, 0FFFFh ; @2C0F
    jns loc_2C1D ; @2C12
    add word ptr [bx + FallingItemY], ax ; @2C17
    jmp short loc_2C96 ; @2C1B
loc_2C1D:
    mov cx, word ptr [bx + FallingItemY] ; @2C1D
    add ax, word ptr [bx + FallingItemY] ; @2C21
    cmp ax, word ptr 01800h ; @2C25
    jl loc_2C35 ; @2C28
loc_2C2D:
    mov word ptr [bx + FallingItemSprites], 0FFFFh ; @2C2D
    jmp short loc_2C96 ; @2C33
loc_2C35:
    mov word ptr [bx + FallingItemY], ax ; @2C35
    sar ax, 5 ; @2C39
    sar cx, 5 ; @2C3C
    add ax, word ptr [si + 2] ; @2C3F
    add cx, word ptr [si + 2] ; @2C42
    xor di, di ; @2C45
loc_2C47:
    test word ptr [di + PlatformLeftEdges], 0FFFFh ; @2C47
    js loc_2C96 ; @2C4D
    cmp cx, word ptr [di + PlatformHeights] ; @2C52
    jge loc_2C91 ; @2C56
    cmp ax, word ptr [di + PlatformHeights] ; @2C5B
    jl loc_2C91 ; @2C5F
    mov dx, word ptr [bx + FallingItemX] ; @2C64
    sar dx, 5 ; @2C68
    add dx, word ptr [si] ; @2C6B
    cmp dx, word ptr [di + PlatformLeftEdges] ; @2C6D
    jl loc_2C91 ; @2C71
    dec dx ; @2C76
    cmp dx, word ptr [di + PlatformRightEdges] ; @2C77
    jg loc_2C91 ; @2C7B
    mov ax, word ptr [di + PlatformHeights] ; @2C80
    sub ax, word ptr [si + 2] ; @2C84
    shl ax, 5 ; @2C87
    mov word ptr [bx + FallingItemY], ax ; @2C8A
    jmp word ptr [si + 8] ; @2C8E
loc_2C91:
    add di, 2 ; @2C91
    jmp short loc_2C47 ; @2C94
loc_2C96:
    ret ; @2C96
; CONTRACT (tools/apply.py)
; Switch a landed falling item to its descriptor's pickup callback and start its lifetime.
; In: DS=DGROUP; BX=item slot byte index.
; Out: callback=descriptor[0Ah]; FallingItemMotionOrLifetime=0230h (560 updates).
; The former horizontal-step word is reused as a countdown; no motion words are cleared.
; END CONTRACT
public LandFallingItem
LandFallingItem:
    mov si, word ptr [bx + FallingItemDescriptors] ; @2C97
    mov ax, word ptr [si + 0Ah] ; @2C9B
    mov word ptr [bx + FallingItemCallbacks], ax ; @2C9E
    mov word ptr [bx + FallingItemMotionOrLifetime], 0230h ; @2CA2
    ret ; @2CA8
; CONTRACT (tools/apply.py)
; Expire a landed item, or award its descriptor-selected benefit on player overlap.
; In: DS=DGROUP; BX=item slot byte index; descriptor+12h is benefit kind.
; Out: decrement lifetime; zero disables sprite. Otherwise call 2207h and use its SF;
; SF clear awards kind 0: timer += descriptor[0Eh], unsigned cap 5A3Bh;
; kind 1: low-byte lives += reward, unsigned cap 99; other kinds: increment multiplier
; only if its word value is below the difficulty limit. Every collected item is disabled.
; Effects/quirks: ADD wraps before capping; lives and multiplier stores write only AL.
; Timer/multiplier reads are words; no score or sound is awarded directly here.
; END CONTRACT
public ExpireOrCollectFallingItem
ExpireOrCollectFallingItem:
    dec word ptr [bx + FallingItemMotionOrLifetime] ; @2CA9
    jne loc_2CBA ; @2CAD
loc_2CB2:
    mov word ptr [bx + FallingItemSprites], 0FFFFh ; @2CB2
    jmp short loc_2D1B ; @2CB8
loc_2CBA:
    mov si, word ptr [bx + FallingItemDescriptors] ; @2CBA
    call FindPlayerTouchingFallingItem ; @2CBE
    js loc_2D1B ; @2CC1
    mov ax, word ptr [si + 012h] ; @2CC6
    cmp ax, word ptr 00h ; @2CC9
    jne loc_2CE8 ; @2CCC
    mov ax, word ptr [si + 0Eh] ; @2CD1
    add ax, word ptr ds:[LevelTimer] ; @2CD4
    cmp ax, word ptr 05A3Bh ; @2CD8
    jbe loc_2CE3 ; @2CDB
    mov ax, 05A3Bh ; @2CE0
loc_2CE3:
    mov word ptr ds:[LevelTimer], ax ; @2CE3
    jmp short loc_2CB2 ; @2CE6
loc_2CE8:
    cmp ax, word ptr 01h ; @2CE8
    jne loc_2D05 ; @2CEB
    mov ax, word ptr [si + 0Eh] ; @2CF0
    add al, byte ptr ds:[LivesRemaining] ; @2CF3
    cmp al, 063h ; @2CF7
    jbe loc_2D00 ; @2CF9
    mov al, 063h ; @2CFE
loc_2D00:
    mov byte ptr ds:[LivesRemaining], al ; @2D00
    jmp short loc_2CB2 ; @2D03
loc_2D05:
    mov ax, word ptr ds:[ScoreMultiplier] ; @2D05
    mov di, word ptr ds:[SelectedDifficulty] ; @2D08
    shl di, 1 ; @2D0C
    cmp ax, word ptr [di + MultiplierLimitsByDifficulty] ; @2D0E
    jae short loc_2CB2 ; @2D12
    inc al ; @2D14
    mov byte ptr ds:[ScoreMultiplier], al ; @2D16
    jmp short loc_2CB2 ; @2D19
loc_2D1B:
    ret ; @2D1B
; CONTRACT (tools/apply.py)
; Advance the fixed-point water boundary and restore its former display row.
; In: DS=DGROUP; current fixed Y at 28FEh, signed step at WaterSurfaceStep.
; Out: absent pending restore, save previous pixel Y and toggle WaterStepPhase;
; only phase zero adds the step, clamps a negative wrapped sum to zero, then SAR 5.
; If the pixel row changes, XOR background color bit 40h across its old 80-byte row,
; set WaterRestorePending=FFh and restore that 320x1 row through a JMP to 43EAh.
; The next call clears pending and restores that same row again, skipping advancement.
; Effects: VGA GC bit mask FFh->40h->FFh, data rotate 0->10h->0; read latches before writes.
; DS is restored after the background access; ES may change through the restore tail.
; END CONTRACT
AdvanceWaterSurface:
    test byte ptr ds:[WaterRestorePending], 0FFh ; @2D1C
    nop ; @2D21
    je loc_2D2F ; @2D22
    mov byte ptr ds:[WaterRestorePending], 0 ; @2D27
    nop ; @2D2C
    jmp short loc_2DA3 ; @2D2D
loc_2D2F:
    mov ax, word ptr ds:[WaterYPixels] ; @2D2F
    mov word ptr ds:[PreviousWaterSurfaceY], ax ; @2D32
    mov ax, word ptr ds:[WaterY32] ; @2D35
    xor byte ptr ds:[WaterStepPhase], 1 ; @2D38
    jne loc_2D4D ; @2D3D
    add ax, word ptr ds:[WaterSurfaceStep] ; @2D42
    jns loc_2D4D ; @2D46
    xor ax, ax ; @2D4B
loc_2D4D:
    mov word ptr ds:[WaterY32], ax ; @2D4D
    sar ax, 5 ; @2D50
    mov word ptr ds:[WaterYPixels], ax ; @2D53
    cmp ax, word ptr ds:[PreviousWaterSurfaceY] ; @2D56
    je loc_2DB2 ; @2D5A
    push ds ; @2D5F
    mov dx, 03CEh ; @2D60
    mov al, 8 ; @2D63
    out dx, al ; @2D65
    inc dx ; @2D66
    mov al, 040h ; @2D67
    out dx, al ; @2D69
    dec dx ; @2D6A
    mov al, 3 ; @2D6B
    out dx, al ; @2D6D
    inc dx ; @2D6E
    mov al, 010h ; @2D6F
    out dx, al ; @2D71
    mov ax, word ptr ds:[PreviousWaterSurfaceY] ; @2D72
    mul byte ptr ds:[VgaRowStrideBytes] ; @2D75
    lds si, dword ptr cs:[BackgroundPagePointer] ; @2D79
    add si, ax ; @2D7E
    mov bx, 04Fh ; @2D80
    mov al, 040h ; @2D83
loc_2D85:
    mov ah, byte ptr [bx + si] ; @2D85
    mov byte ptr [bx + si], al ; @2D87
    dec bx ; @2D89
    jns short loc_2D85 ; @2D8A
    mov dx, 03CEh ; @2D8C
    mov al, 8 ; @2D8F
    out dx, al ; @2D91
    inc dx ; @2D92
    mov al, 0FFh ; @2D93
    out dx, al ; @2D95
    dec dx ; @2D96
    mov al, 3 ; @2D97
    out dx, al ; @2D99
    inc dx ; @2D9A
    xor al, al ; @2D9B
    out dx, al ; @2D9D
    pop ds ; @2D9E
    dec byte ptr ds:[WaterRestorePending] ; @2D9F
loc_2DA3:
    xor ax, ax ; @2DA3
    mov bx, word ptr ds:[PreviousWaterSurfaceY] ; @2DA5
    mov cx, 0140h ; @2DA9
    mov dx, 1 ; @2DAC
    jmp near ptr RestoreBackgroundRectangle ; @2DAF
loc_2DB2:
    ret ; @2DB2
; CONTRACT (tools/apply.py)
; Three CS near target words: DrawWaterSurfaceFrame0, DrawWaterSurfaceFrame1, frame 2.
; Target tails share DrawWaterSurface's saved DS and return address; these are not far pointers.
; END CONTRACT
WaterSurfaceDispatchWords:
    dw offset DrawWaterSurfaceFrame0
    dw offset DrawWaterSurfaceFrame1
    dw offset DrawWaterSurfaceFrame2
; CONTRACT (tools/apply.py)
; Animate and draw the 320-pixel water surface across four unchained VGA planes.
; In: DS=DGROUP; WaterSurfaceFrame must be 0..2; pixel Y at DGROUP:2903h.
; Out: decrement byte countdown; on sign set reset to 6 and cycle frame 0->2->1->0.
; WaterSurfaceByteOffset=AL(Y)*low-byte(VgaRowStrideBytes), before page-base addition.
; Effects: save DS, load DS:DI from CS:460Ch plus row offset; select sequencer register 2,
; plane mask 1, colors 54h..58h, then JMP through the three-word CS dispatch table.
; Frame tails consume the saved DS, restore mask 0Fh and return to this routine's caller.
; No range checks or clipping; AL multiplication and offsets retain 16-bit behavior.
; END CONTRACT
DrawWaterSurface:
    push ds ; @2DB9
    mov si, word ptr ds:[WaterSurfaceFrame] ; @2DBA
    dec byte ptr ds:[WaterSurfaceFrameCountdown] ; @2DBE
    jns loc_2DDA ; @2DC2
    mov byte ptr ds:[WaterSurfaceFrameCountdown], 6 ; @2DC7
    nop ; @2DCC
    dec si ; @2DCD
    jns loc_2DD6 ; @2DCE
    mov si, 2 ; @2DD3
loc_2DD6:
    mov word ptr ds:[WaterSurfaceFrame], si ; @2DD6
loc_2DDA:
    mov ax, word ptr ds:[WaterYPixels] ; @2DDA
    mul byte ptr ds:[VgaRowStrideBytes] ; @2DDD
    mov word ptr ds:[WaterSurfaceByteOffset], ax ; @2DE1
    lds di, dword ptr cs:[DrawPagePointer] ; @2DE4
    add di, ax ; @2DE9
    mov dx, 03C4h ; @2DEB
    mov al, 2 ; @2DEE
    out dx, al ; @2DF0
    inc dx ; @2DF1
    mov ax, 05401h ; @2DF2
    out dx, al ; @2DF5
    mov bx, 05655h ; @2DF6
    mov cx, 05857h ; @2DF9
    shl si, 1 ; @2DFC
    jmp word ptr cs:[si + WaterSurfaceDispatch] ; @2DFE
; CONTRACT (tools/apply.py)
; Draw water animation frame 0, a tail entry of DrawWaterSurface, not an ordinary callee.
; In: DS:DI=VGA row; DX=03C5h, sequencer index=2, mask=1; AX=5401h, BX=5655h, CX=5857h.
; Stack top is saved DGROUP DS, followed by DrawWaterSurface's near return address.
; Out: 80 byte stores per plane, masks 1/2/4/8; final AL=0Fh written as the map mask.
; Consume saved DS and near-return to caller; DI/DX/BX/CX remain as supplied by dispatcher.
; END CONTRACT
DrawWaterSurfaceFrame0:
    mov byte ptr [di], bh ; @2E03
    mov byte ptr [di + 1], cl ; @2E05
    mov byte ptr [di + 2], cl ; @2E08
    mov byte ptr [di + 3], bl ; @2E0B
    mov byte ptr [di + 4], ah ; @2E0E
    mov byte ptr [di + 5], ah ; @2E11
    mov byte ptr [di + 6], bh ; @2E14
    mov byte ptr [di + 7], cl ; @2E17
    mov byte ptr [di + 8], bh ; @2E1A
    mov byte ptr [di + 9], bh ; @2E1D
    mov byte ptr [di + 0Ah], bl ; @2E20
    mov byte ptr [di + 0Bh], bl ; @2E23
    mov byte ptr [di + 0Ch], bl ; @2E26
    mov byte ptr [di + 0Dh], cl ; @2E29
    mov byte ptr [di + 0Eh], cl ; @2E2C
    mov byte ptr [di + 0Fh], cl ; @2E2F
    mov byte ptr [di + 010h], bh ; @2E32
    mov byte ptr [di + 011h], bl ; @2E35
    mov byte ptr [di + 012h], bl ; @2E38
    mov byte ptr [di + 013h], bh ; @2E3B
    mov byte ptr [di + 014h], bh ; @2E3E
    mov byte ptr [di + 015h], cl ; @2E41
    mov byte ptr [di + 016h], bl ; @2E44
    mov byte ptr [di + 017h], ah ; @2E47
    mov byte ptr [di + 018h], bh ; @2E4A
    mov byte ptr [di + 019h], bh ; @2E4D
    mov byte ptr [di + 01Ah], cl ; @2E50
    mov byte ptr [di + 01Bh], bh ; @2E53
    mov byte ptr [di + 01Ch], ah ; @2E56
    mov byte ptr [di + 01Dh], ah ; @2E59
    mov byte ptr [di + 01Eh], bh ; @2E5C
    mov byte ptr [di + 01Fh], cl ; @2E5F
    mov byte ptr [di + 020h], bh ; @2E62
    mov byte ptr [di + 021h], bh ; @2E65
    mov byte ptr [di + 022h], bh ; @2E68
    mov byte ptr [di + 023h], bl ; @2E6B
    mov byte ptr [di + 024h], bl ; @2E6E
    mov byte ptr [di + 025h], cl ; @2E71
    mov byte ptr [di + 026h], cl ; @2E74
    mov byte ptr [di + 027h], cl ; @2E77
    mov byte ptr [di + 028h], bh ; @2E7A
    mov byte ptr [di + 029h], bl ; @2E7D
    mov byte ptr [di + 02Ah], bl ; @2E80
    mov byte ptr [di + 02Bh], bh ; @2E83
    mov byte ptr [di + 02Ch], bh ; @2E86
    mov byte ptr [di + 02Dh], cl ; @2E89
    mov byte ptr [di + 02Eh], bl ; @2E8C
    mov byte ptr [di + 02Fh], ah ; @2E8F
    mov byte ptr [di + 030h], ah ; @2E92
    mov byte ptr [di + 031h], bh ; @2E95
    mov byte ptr [di + 032h], cl ; @2E98
    mov byte ptr [di + 033h], cl ; @2E9B
    mov byte ptr [di + 034h], bl ; @2E9E
    mov byte ptr [di + 035h], ah ; @2EA1
    mov byte ptr [di + 036h], ah ; @2EA4
    mov byte ptr [di + 037h], bh ; @2EA7
    mov byte ptr [di + 038h], cl ; @2EAA
    mov byte ptr [di + 039h], bh ; @2EAD
    mov byte ptr [di + 03Ah], bh ; @2EB0
    mov byte ptr [di + 03Bh], bl ; @2EB3
    mov byte ptr [di + 03Ch], bl ; @2EB6
    mov byte ptr [di + 03Dh], bl ; @2EB9
    mov byte ptr [di + 03Eh], cl ; @2EBC
    mov byte ptr [di + 03Fh], cl ; @2EBF
    mov byte ptr [di + 040h], cl ; @2EC2
    mov byte ptr [di + 041h], bh ; @2EC5
    mov byte ptr [di + 042h], bl ; @2EC8
    mov byte ptr [di + 043h], bl ; @2ECB
    mov byte ptr [di + 044h], bh ; @2ECE
    mov byte ptr [di + 045h], cl ; @2ED1
    mov byte ptr [di + 046h], bh ; @2ED4
    mov byte ptr [di + 047h], ah ; @2ED7
    mov byte ptr [di + 048h], ah ; @2EDA
    mov byte ptr [di + 049h], bl ; @2EDD
    mov byte ptr [di + 04Ah], ch ; @2EE0
    mov byte ptr [di + 04Bh], bh ; @2EE3
    mov byte ptr [di + 04Ch], bh ; @2EE6
    mov byte ptr [di + 04Dh], bh ; @2EE9
    mov byte ptr [di + 04Eh], bl ; @2EEC
    mov byte ptr [di + 04Fh], bl ; @2EEF
    shl al, 1 ; @2EF2
    out dx, al ; @2EF4
    mov byte ptr [di], bh ; @2EF5
    mov byte ptr [di + 1], ch ; @2EF7
    mov byte ptr [di + 2], bh ; @2EFA
    mov byte ptr [di + 3], ah ; @2EFD
    mov byte ptr [di + 4], ah ; @2F00
    mov byte ptr [di + 5], ah ; @2F03
    mov byte ptr [di + 6], cl ; @2F06
    mov byte ptr [di + 7], cl ; @2F09
    mov byte ptr [di + 8], bh ; @2F0C
    mov byte ptr [di + 9], bh ; @2F0F
    mov byte ptr [di + 0Ah], bl ; @2F12
    mov byte ptr [di + 0Bh], bl ; @2F15
    mov byte ptr [di + 0Ch], bl ; @2F18
    mov byte ptr [di + 0Dh], cl ; @2F1B
    mov byte ptr [di + 0Eh], cl ; @2F1E
    mov byte ptr [di + 0Fh], cl ; @2F21
    mov byte ptr [di + 010h], bl ; @2F24
    mov byte ptr [di + 011h], bl ; @2F27
    mov byte ptr [di + 012h], bl ; @2F2A
    mov byte ptr [di + 013h], bh ; @2F2D
    mov byte ptr [di + 014h], bh ; @2F30
    mov byte ptr [di + 015h], bh ; @2F33
    mov byte ptr [di + 016h], ah ; @2F36
    mov byte ptr [di + 017h], ah ; @2F39
    mov byte ptr [di + 018h], bh ; @2F3C
    mov byte ptr [di + 019h], cl ; @2F3F
    mov byte ptr [di + 01Ah], cl ; @2F42
    mov byte ptr [di + 01Bh], bl ; @2F45
    mov byte ptr [di + 01Ch], ah ; @2F48
    mov byte ptr [di + 01Dh], ah ; @2F4B
    mov byte ptr [di + 01Eh], bh ; @2F4E
    mov byte ptr [di + 01Fh], cl ; @2F51
    mov byte ptr [di + 020h], bh ; @2F54
    mov byte ptr [di + 021h], bh ; @2F57
    mov byte ptr [di + 022h], bl ; @2F5A
    mov byte ptr [di + 023h], bl ; @2F5D
    mov byte ptr [di + 024h], bl ; @2F60
    mov byte ptr [di + 025h], cl ; @2F63
    mov byte ptr [di + 026h], cl ; @2F66
    mov byte ptr [di + 027h], cl ; @2F69
    mov byte ptr [di + 028h], bh ; @2F6C
    mov byte ptr [di + 029h], bl ; @2F6F
    mov byte ptr [di + 02Ah], bl ; @2F72
    mov byte ptr [di + 02Bh], bh ; @2F75
    mov byte ptr [di + 02Ch], bh ; @2F78
    mov byte ptr [di + 02Dh], cl ; @2F7B
    mov byte ptr [di + 02Eh], bl ; @2F7E
    mov byte ptr [di + 02Fh], ah ; @2F81
    mov byte ptr [di + 030h], ah ; @2F84
    mov byte ptr [di + 031h], bh ; @2F87
    mov byte ptr [di + 032h], ch ; @2F8A
    mov byte ptr [di + 033h], bh ; @2F8D
    mov byte ptr [di + 034h], ah ; @2F90
    mov byte ptr [di + 035h], ah ; @2F93
    mov byte ptr [di + 036h], ah ; @2F96
    mov byte ptr [di + 037h], cl ; @2F99
    mov byte ptr [di + 038h], cl ; @2F9C
    mov byte ptr [di + 039h], bh ; @2F9F
    mov byte ptr [di + 03Ah], bh ; @2FA2
    mov byte ptr [di + 03Bh], bl ; @2FA5
    mov byte ptr [di + 03Ch], bl ; @2FA8
    mov byte ptr [di + 03Dh], bl ; @2FAB
    mov byte ptr [di + 03Eh], cl ; @2FAE
    mov byte ptr [di + 03Fh], cl ; @2FB1
    mov byte ptr [di + 040h], cl ; @2FB4
    mov byte ptr [di + 041h], bl ; @2FB7
    mov byte ptr [di + 042h], bl ; @2FBA
    mov byte ptr [di + 043h], bh ; @2FBD
    mov byte ptr [di + 044h], bh ; @2FC0
    mov byte ptr [di + 045h], cl ; @2FC3
    mov byte ptr [di + 046h], bh ; @2FC6
    mov byte ptr [di + 047h], ah ; @2FC9
    mov byte ptr [di + 048h], ah ; @2FCC
    mov byte ptr [di + 049h], bh ; @2FCF
    mov byte ptr [di + 04Ah], cl ; @2FD2
    mov byte ptr [di + 04Bh], bh ; @2FD5
    mov byte ptr [di + 04Ch], bh ; @2FD8
    mov byte ptr [di + 04Dh], bh ; @2FDB
    mov byte ptr [di + 04Eh], bl ; @2FDE
    mov byte ptr [di + 04Fh], bl ; @2FE1
    shl al, 1 ; @2FE4
    out dx, al ; @2FE6
    mov byte ptr [di], bh ; @2FE7
    mov byte ptr [di + 1], cl ; @2FE9
    mov byte ptr [di + 2], bh ; @2FEC
    mov byte ptr [di + 3], ah ; @2FEF
    mov byte ptr [di + 4], ah ; @2FF2
    mov byte ptr [di + 5], bl ; @2FF5
    mov byte ptr [di + 6], ch ; @2FF8
    mov byte ptr [di + 7], bh ; @2FFB
    mov byte ptr [di + 8], bh ; @2FFE
    mov byte ptr [di + 9], bh ; @3001
    mov byte ptr [di + 0Ah], bl ; @3004
    mov byte ptr [di + 0Bh], bl ; @3007
    mov byte ptr [di + 0Ch], cl ; @300A
    mov byte ptr [di + 0Dh], cl ; @300D
    mov byte ptr [di + 0Eh], cl ; @3010
    mov byte ptr [di + 0Fh], cl ; @3013
    mov byte ptr [di + 010h], bl ; @3016
    mov byte ptr [di + 011h], bl ; @3019
    mov byte ptr [di + 012h], bl ; @301C
    mov byte ptr [di + 013h], bh ; @301F
    mov byte ptr [di + 014h], bh ; @3022
    mov byte ptr [di + 015h], bh ; @3025
    mov byte ptr [di + 016h], ah ; @3028
    mov byte ptr [di + 017h], ah ; @302B
    mov byte ptr [di + 018h], bh ; @302E
    mov byte ptr [di + 019h], ch ; @3031
    mov byte ptr [di + 01Ah], bh ; @3034
    mov byte ptr [di + 01Bh], ah ; @3037
    mov byte ptr [di + 01Ch], ah ; @303A
    mov byte ptr [di + 01Dh], ah ; @303D
    mov byte ptr [di + 01Eh], cl ; @3040
    mov byte ptr [di + 01Fh], cl ; @3043
    mov byte ptr [di + 020h], bh ; @3046
    mov byte ptr [di + 021h], bh ; @3049
    mov byte ptr [di + 022h], bl ; @304C
    mov byte ptr [di + 023h], bl ; @304F
    mov byte ptr [di + 024h], bl ; @3052
    mov byte ptr [di + 025h], cl ; @3055
    mov byte ptr [di + 026h], cl ; @3058
    mov byte ptr [di + 027h], cl ; @305B
    mov byte ptr [di + 028h], bl ; @305E
    mov byte ptr [di + 029h], bl ; @3061
    mov byte ptr [di + 02Ah], bl ; @3064
    mov byte ptr [di + 02Bh], bh ; @3067
    mov byte ptr [di + 02Ch], bh ; @306A
    mov byte ptr [di + 02Dh], bh ; @306D
    mov byte ptr [di + 02Eh], ah ; @3070
    mov byte ptr [di + 02Fh], ah ; @3073
    mov byte ptr [di + 030h], bl ; @3076
    mov byte ptr [di + 031h], bh ; @3079
    mov byte ptr [di + 032h], cl ; @307C
    mov byte ptr [di + 033h], bh ; @307F
    mov byte ptr [di + 034h], ah ; @3082
    mov byte ptr [di + 035h], ah ; @3085
    mov byte ptr [di + 036h], bl ; @3088
    mov byte ptr [di + 037h], ch ; @308B
    mov byte ptr [di + 038h], bh ; @308E
    mov byte ptr [di + 039h], bh ; @3091
    mov byte ptr [di + 03Ah], bh ; @3094
    mov byte ptr [di + 03Bh], bl ; @3097
    mov byte ptr [di + 03Ch], bl ; @309A
    mov byte ptr [di + 03Dh], cl ; @309D
    mov byte ptr [di + 03Eh], cl ; @30A0
    mov byte ptr [di + 03Fh], cl ; @30A3
    mov byte ptr [di + 040h], cl ; @30A6
    mov byte ptr [di + 041h], bl ; @30A9
    mov byte ptr [di + 042h], bl ; @30AC
    mov byte ptr [di + 043h], bh ; @30AF
    mov byte ptr [di + 044h], cl ; @30B2
    mov byte ptr [di + 045h], cl ; @30B5
    mov byte ptr [di + 046h], bl ; @30B8
    mov byte ptr [di + 047h], ah ; @30BB
    mov byte ptr [di + 048h], ah ; @30BE
    mov byte ptr [di + 049h], bh ; @30C1
    mov byte ptr [di + 04Ah], cl ; @30C4
    mov byte ptr [di + 04Bh], bh ; @30C7
    mov byte ptr [di + 04Ch], bh ; @30CA
    mov byte ptr [di + 04Dh], bl ; @30CD
    mov byte ptr [di + 04Eh], bl ; @30D0
    mov byte ptr [di + 04Fh], bl ; @30D3
    shl al, 1 ; @30D6
    out dx, al ; @30D8
    mov byte ptr [di], bh ; @30D9
    mov byte ptr [di + 1], cl ; @30DB
    mov byte ptr [di + 2], bh ; @30DE
    mov byte ptr [di + 3], ah ; @30E1
    mov byte ptr [di + 4], ah ; @30E4
    mov byte ptr [di + 5], bh ; @30E7
    mov byte ptr [di + 6], cl ; @30EA
    mov byte ptr [di + 7], bh ; @30ED
    mov byte ptr [di + 8], bh ; @30F0
    mov byte ptr [di + 9], bh ; @30F3
    mov byte ptr [di + 0Ah], bl ; @30F6
    mov byte ptr [di + 0Bh], bl ; @30F9
    mov byte ptr [di + 0Ch], cl ; @30FC
    mov byte ptr [di + 0Dh], cl ; @30FF
    mov byte ptr [di + 0Eh], cl ; @3102
    mov byte ptr [di + 0Fh], bh ; @3105
    mov byte ptr [di + 010h], bl ; @3108
    mov byte ptr [di + 011h], bl ; @310B
    mov byte ptr [di + 012h], bh ; @310E
    mov byte ptr [di + 013h], bh ; @3111
    mov byte ptr [di + 014h], cl ; @3114
    mov byte ptr [di + 015h], bl ; @3117
    mov byte ptr [di + 016h], ah ; @311A
    mov byte ptr [di + 017h], ah ; @311D
    mov byte ptr [di + 018h], bh ; @3120
    mov byte ptr [di + 019h], cl ; @3123
    mov byte ptr [di + 01Ah], bh ; @3126
    mov byte ptr [di + 01Bh], ah ; @3129
    mov byte ptr [di + 01Ch], ah ; @312C
    mov byte ptr [di + 01Dh], bl ; @312F
    mov byte ptr [di + 01Eh], ch ; @3132
    mov byte ptr [di + 01Fh], bh ; @3135
    mov byte ptr [di + 020h], bh ; @3138
    mov byte ptr [di + 021h], bh ; @313B
    mov byte ptr [di + 022h], bl ; @313E
    mov byte ptr [di + 023h], bl ; @3141
    mov byte ptr [di + 024h], cl ; @3144
    mov byte ptr [di + 025h], cl ; @3147
    mov byte ptr [di + 026h], cl ; @314A
    mov byte ptr [di + 027h], cl ; @314D
    mov byte ptr [di + 028h], bl ; @3150
    mov byte ptr [di + 029h], bl ; @3153
    mov byte ptr [di + 02Ah], bl ; @3156
    mov byte ptr [di + 02Bh], bh ; @3159
    mov byte ptr [di + 02Ch], bh ; @315C
    mov byte ptr [di + 02Dh], bh ; @315F
    mov byte ptr [di + 02Eh], ah ; @3162
    mov byte ptr [di + 02Fh], ah ; @3165
    mov byte ptr [di + 030h], bh ; @3168
    mov byte ptr [di + 031h], bh ; @316B
    mov byte ptr [di + 032h], cl ; @316E
    mov byte ptr [di + 033h], bh ; @3171
    mov byte ptr [di + 034h], ah ; @3174
    mov byte ptr [di + 035h], ah ; @3177
    mov byte ptr [di + 036h], bh ; @317A
    mov byte ptr [di + 037h], cl ; @317D
    mov byte ptr [di + 038h], bh ; @3180
    mov byte ptr [di + 039h], bh ; @3183
    mov byte ptr [di + 03Ah], bh ; @3186
    mov byte ptr [di + 03Bh], bl ; @3189
    mov byte ptr [di + 03Ch], bl ; @318C
    mov byte ptr [di + 03Dh], cl ; @318F
    mov byte ptr [di + 03Eh], cl ; @3192
    mov byte ptr [di + 03Fh], cl ; @3195
    mov byte ptr [di + 040h], bh ; @3198
    mov byte ptr [di + 041h], bl ; @319B
    mov byte ptr [di + 042h], bl ; @319E
    mov byte ptr [di + 043h], bh ; @31A1
    mov byte ptr [di + 044h], ch ; @31A4
    mov byte ptr [di + 045h], bh ; @31A7
    mov byte ptr [di + 046h], ah ; @31AA
    mov byte ptr [di + 047h], ah ; @31AD
    mov byte ptr [di + 048h], ah ; @31B0
    mov byte ptr [di + 049h], cl ; @31B3
    mov byte ptr [di + 04Ah], cl ; @31B6
    mov byte ptr [di + 04Bh], bh ; @31B9
    mov byte ptr [di + 04Ch], bh ; @31BC
    mov byte ptr [di + 04Dh], bl ; @31BF
    mov byte ptr [di + 04Eh], bl ; @31C2
    mov byte ptr [di + 04Fh], bl ; @31C5
    mov al, 0Fh ; @31C8
    out dx, al ; @31CA
    pop ds ; @31CB
    ret ; @31CC
; CONTRACT (tools/apply.py)
; Draw water animation frame 1, a tail entry of DrawWaterSurface, not an ordinary callee.
; In: DS:DI=VGA row; DX=03C5h, sequencer index=2, mask=1; AX=5401h, BX=5655h, CX=5857h.
; Stack top is saved DGROUP DS, followed by DrawWaterSurface's near return address.
; Out: 80 byte stores per plane, masks 1/2/4/8; final AL=0Fh written as the map mask.
; Consume saved DS and near-return to caller; DI/DX/BX/CX remain as supplied by dispatcher.
; END CONTRACT
DrawWaterSurfaceFrame1:
    mov byte ptr [di], bh ; @31CD
    mov byte ptr [di + 1], ch ; @31CF
    mov byte ptr [di + 2], bh ; @31D2
    mov byte ptr [di + 3], bh ; @31D5
    mov byte ptr [di + 4], bl ; @31D8
    mov byte ptr [di + 5], bl ; @31DB
    mov byte ptr [di + 6], bl ; @31DE
    mov byte ptr [di + 7], bl ; @31E1
    mov byte ptr [di + 8], bl ; @31E4
    mov byte ptr [di + 9], bl ; @31E7
    mov byte ptr [di + 0Ah], bh ; @31EA
    mov byte ptr [di + 0Bh], bh ; @31ED
    mov byte ptr [di + 0Ch], cl ; @31F0
    mov byte ptr [di + 0Dh], cl ; @31F3
    mov byte ptr [di + 0Eh], cl ; @31F6
    mov byte ptr [di + 0Fh], cl ; @31F9
    mov byte ptr [di + 010h], ch ; @31FC
    mov byte ptr [di + 011h], ch ; @31FF
    mov byte ptr [di + 012h], ch ; @3202
    mov byte ptr [di + 013h], ch ; @3205
    mov byte ptr [di + 014h], ch ; @3208
    mov byte ptr [di + 015h], cl ; @320B
    mov byte ptr [di + 016h], bh ; @320E
    mov byte ptr [di + 017h], bh ; @3211
    mov byte ptr [di + 018h], bh ; @3214
    mov byte ptr [di + 019h], ch ; @3217
    mov byte ptr [di + 01Ah], bh ; @321A
    mov byte ptr [di + 01Bh], bh ; @321D
    mov byte ptr [di + 01Ch], bl ; @3220
    mov byte ptr [di + 01Dh], bl ; @3223
    mov byte ptr [di + 01Eh], bl ; @3226
    mov byte ptr [di + 01Fh], bl ; @3229
    mov byte ptr [di + 020h], bl ; @322C
    mov byte ptr [di + 021h], bl ; @322F
    mov byte ptr [di + 022h], bl ; @3232
    mov byte ptr [di + 023h], bh ; @3235
    mov byte ptr [di + 024h], cl ; @3238
    mov byte ptr [di + 025h], cl ; @323B
    mov byte ptr [di + 026h], ch ; @323E
    mov byte ptr [di + 027h], cl ; @3241
    mov byte ptr [di + 028h], ch ; @3244
    mov byte ptr [di + 029h], ch ; @3247
    mov byte ptr [di + 02Ah], ch ; @324A
    mov byte ptr [di + 02Bh], ch ; @324D
    mov byte ptr [di + 02Ch], ch ; @3250
    mov byte ptr [di + 02Dh], cl ; @3253
    mov byte ptr [di + 02Eh], bh ; @3256
    mov byte ptr [di + 02Fh], bh ; @3259
    mov byte ptr [di + 030h], bh ; @325C
    mov byte ptr [di + 031h], bh ; @325F
    mov byte ptr [di + 032h], ch ; @3262
    mov byte ptr [di + 033h], bh ; @3265
    mov byte ptr [di + 034h], bh ; @3268
    mov byte ptr [di + 035h], bl ; @326B
    mov byte ptr [di + 036h], bl ; @326E
    mov byte ptr [di + 037h], bl ; @3271
    mov byte ptr [di + 038h], bl ; @3274
    mov byte ptr [di + 039h], bl ; @3277
    mov byte ptr [di + 03Ah], bl ; @327A
    mov byte ptr [di + 03Bh], bh ; @327D
    mov byte ptr [di + 03Ch], bh ; @3280
    mov byte ptr [di + 03Dh], cl ; @3283
    mov byte ptr [di + 03Eh], cl ; @3286
    mov byte ptr [di + 03Fh], cl ; @3289
    mov byte ptr [di + 040h], cl ; @328C
    mov byte ptr [di + 041h], ch ; @328F
    mov byte ptr [di + 042h], ch ; @3292
    mov byte ptr [di + 043h], ch ; @3295
    mov byte ptr [di + 044h], ch ; @3298
    mov byte ptr [di + 045h], cl ; @329B
    mov byte ptr [di + 046h], bh ; @329E
    mov byte ptr [di + 047h], bl ; @32A1
    mov byte ptr [di + 048h], bl ; @32A4
    mov byte ptr [di + 049h], bl ; @32A7
    mov byte ptr [di + 04Ah], bl ; @32AA
    mov byte ptr [di + 04Bh], bl ; @32AD
    mov byte ptr [di + 04Ch], bl ; @32B0
    mov byte ptr [di + 04Dh], bl ; @32B3
    mov byte ptr [di + 04Eh], bh ; @32B6
    mov byte ptr [di + 04Fh], cl ; @32B9
    shl al, 1 ; @32BC
    out dx, al ; @32BE
    mov byte ptr [di], cl ; @32BF
    mov byte ptr [di + 1], ch ; @32C1
    mov byte ptr [di + 2], bh ; @32C4
    mov byte ptr [di + 3], bh ; @32C7
    mov byte ptr [di + 4], bl ; @32CA
    mov byte ptr [di + 5], bl ; @32CD
    mov byte ptr [di + 6], bl ; @32D0
    mov byte ptr [di + 7], bl ; @32D3
    mov byte ptr [di + 8], bl ; @32D6
    mov byte ptr [di + 9], bl ; @32D9
    mov byte ptr [di + 0Ah], bh ; @32DC
    mov byte ptr [di + 0Bh], cl ; @32DF
    mov byte ptr [di + 0Ch], cl ; @32E2
    mov byte ptr [di + 0Dh], ch ; @32E5
    mov byte ptr [di + 0Eh], cl ; @32E8
    mov byte ptr [di + 0Fh], cl ; @32EB
    mov byte ptr [di + 010h], ch ; @32EE
    mov byte ptr [di + 011h], ch ; @32F1
    mov byte ptr [di + 012h], ch ; @32F4
    mov byte ptr [di + 013h], ch ; @32F7
    mov byte ptr [di + 014h], ch ; @32FA
    mov byte ptr [di + 015h], cl ; @32FD
    mov byte ptr [di + 016h], bh ; @3300
    mov byte ptr [di + 017h], bh ; @3303
    mov byte ptr [di + 018h], bh ; @3306
    mov byte ptr [di + 019h], ch ; @3309
    mov byte ptr [di + 01Ah], bh ; @330C
    mov byte ptr [di + 01Bh], bh ; @330F
    mov byte ptr [di + 01Ch], bl ; @3312
    mov byte ptr [di + 01Dh], bl ; @3315
    mov byte ptr [di + 01Eh], bl ; @3318
    mov byte ptr [di + 01Fh], bl ; @331B
    mov byte ptr [di + 020h], bl ; @331E
    mov byte ptr [di + 021h], bl ; @3321
    mov byte ptr [di + 022h], bh ; @3324
    mov byte ptr [di + 023h], bh ; @3327
    mov byte ptr [di + 024h], cl ; @332A
    mov byte ptr [di + 025h], cl ; @332D
    mov byte ptr [di + 026h], cl ; @3330
    mov byte ptr [di + 027h], cl ; @3333
    mov byte ptr [di + 028h], ch ; @3336
    mov byte ptr [di + 029h], ch ; @3339
    mov byte ptr [di + 02Ah], ch ; @333C
    mov byte ptr [di + 02Bh], ch ; @333F
    mov byte ptr [di + 02Ch], ch ; @3342
    mov byte ptr [di + 02Dh], cl ; @3345
    mov byte ptr [di + 02Eh], bh ; @3348
    mov byte ptr [di + 02Fh], bh ; @334B
    mov byte ptr [di + 030h], bh ; @334E
    mov byte ptr [di + 031h], cl ; @3351
    mov byte ptr [di + 032h], ch ; @3354
    mov byte ptr [di + 033h], bh ; @3357
    mov byte ptr [di + 034h], bh ; @335A
    mov byte ptr [di + 035h], bl ; @335D
    mov byte ptr [di + 036h], bl ; @3360
    mov byte ptr [di + 037h], bl ; @3363
    mov byte ptr [di + 038h], bl ; @3366
    mov byte ptr [di + 039h], bl ; @3369
    mov byte ptr [di + 03Ah], bl ; @336C
    mov byte ptr [di + 03Bh], bh ; @336F
    mov byte ptr [di + 03Ch], cl ; @3372
    mov byte ptr [di + 03Dh], cl ; @3375
    mov byte ptr [di + 03Eh], ch ; @3378
    mov byte ptr [di + 03Fh], cl ; @337B
    mov byte ptr [di + 040h], cl ; @337E
    mov byte ptr [di + 041h], ch ; @3381
    mov byte ptr [di + 042h], ch ; @3384
    mov byte ptr [di + 043h], bh ; @3387
    mov byte ptr [di + 044h], ch ; @338A
    mov byte ptr [di + 045h], bh ; @338D
    mov byte ptr [di + 046h], bh ; @3390
    mov byte ptr [di + 047h], bl ; @3393
    mov byte ptr [di + 048h], bl ; @3396
    mov byte ptr [di + 049h], bl ; @3399
    mov byte ptr [di + 04Ah], bl ; @339C
    mov byte ptr [di + 04Bh], bl ; @339F
    mov byte ptr [di + 04Ch], bl ; @33A2
    mov byte ptr [di + 04Dh], bl ; @33A5
    mov byte ptr [di + 04Eh], bh ; @33A8
    mov byte ptr [di + 04Fh], cl ; @33AB
    shl al, 1 ; @33AE
    out dx, al ; @33B0
    mov byte ptr [di], ch ; @33B1
    mov byte ptr [di + 1], cl ; @33B3
    mov byte ptr [di + 2], bh ; @33B6
    mov byte ptr [di + 3], bl ; @33B9
    mov byte ptr [di + 4], bl ; @33BC
    mov byte ptr [di + 5], bl ; @33BF
    mov byte ptr [di + 6], bl ; @33C2
    mov byte ptr [di + 7], bl ; @33C5
    mov byte ptr [di + 8], bl ; @33C8
    mov byte ptr [di + 9], bl ; @33CB
    mov byte ptr [di + 0Ah], bh ; @33CE
    mov byte ptr [di + 0Bh], cl ; @33D1
    mov byte ptr [di + 0Ch], cl ; @33D4
    mov byte ptr [di + 0Dh], ch ; @33D7
    mov byte ptr [di + 0Eh], cl ; @33DA
    mov byte ptr [di + 0Fh], cl ; @33DD
    mov byte ptr [di + 010h], ch ; @33E0
    mov byte ptr [di + 011h], ch ; @33E3
    mov byte ptr [di + 012h], ch ; @33E6
    mov byte ptr [di + 013h], ch ; @33E9
    mov byte ptr [di + 014h], ch ; @33EC
    mov byte ptr [di + 015h], bh ; @33EF
    mov byte ptr [di + 016h], bh ; @33F2
    mov byte ptr [di + 017h], bh ; @33F5
    mov byte ptr [di + 018h], cl ; @33F8
    mov byte ptr [di + 019h], ch ; @33FB
    mov byte ptr [di + 01Ah], bh ; @33FE
    mov byte ptr [di + 01Bh], bh ; @3401
    mov byte ptr [di + 01Ch], bl ; @3404
    mov byte ptr [di + 01Dh], bl ; @3407
    mov byte ptr [di + 01Eh], bl ; @340A
    mov byte ptr [di + 01Fh], bl ; @340D
    mov byte ptr [di + 020h], bl ; @3410
    mov byte ptr [di + 021h], bl ; @3413
    mov byte ptr [di + 022h], bh ; @3416
    mov byte ptr [di + 023h], cl ; @3419
    mov byte ptr [di + 024h], cl ; @341C
    mov byte ptr [di + 025h], ch ; @341F
    mov byte ptr [di + 026h], cl ; @3422
    mov byte ptr [di + 027h], cl ; @3425
    mov byte ptr [di + 028h], ch ; @3428
    mov byte ptr [di + 029h], ch ; @342B
    mov byte ptr [di + 02Ah], ch ; @342E
    mov byte ptr [di + 02Bh], ch ; @3431
    mov byte ptr [di + 02Ch], ch ; @3434
    mov byte ptr [di + 02Dh], cl ; @3437
    mov byte ptr [di + 02Eh], bh ; @343A
    mov byte ptr [di + 02Fh], bh ; @343D
    mov byte ptr [di + 030h], bh ; @3440
    mov byte ptr [di + 031h], ch ; @3443
    mov byte ptr [di + 032h], cl ; @3446
    mov byte ptr [di + 033h], bh ; @3449
    mov byte ptr [di + 034h], bl ; @344C
    mov byte ptr [di + 035h], bl ; @344F
    mov byte ptr [di + 036h], bl ; @3452
    mov byte ptr [di + 037h], bl ; @3455
    mov byte ptr [di + 038h], bl ; @3458
    mov byte ptr [di + 039h], bl ; @345B
    mov byte ptr [di + 03Ah], bl ; @345E
    mov byte ptr [di + 03Bh], bh ; @3461
    mov byte ptr [di + 03Ch], cl ; @3464
    mov byte ptr [di + 03Dh], cl ; @3467
    mov byte ptr [di + 03Eh], ch ; @346A
    mov byte ptr [di + 03Fh], cl ; @346D
    mov byte ptr [di + 040h], cl ; @3470
    mov byte ptr [di + 041h], ch ; @3473
    mov byte ptr [di + 042h], ch ; @3476
    mov byte ptr [di + 043h], bh ; @3479
    mov byte ptr [di + 044h], ch ; @347C
    mov byte ptr [di + 045h], bh ; @347F
    mov byte ptr [di + 046h], bh ; @3482
    mov byte ptr [di + 047h], bl ; @3485
    mov byte ptr [di + 048h], bl ; @3488
    mov byte ptr [di + 049h], bl ; @348B
    mov byte ptr [di + 04Ah], bl ; @348E
    mov byte ptr [di + 04Bh], bl ; @3491
    mov byte ptr [di + 04Ch], bl ; @3494
    mov byte ptr [di + 04Dh], bh ; @3497
    mov byte ptr [di + 04Eh], bh ; @349A
    mov byte ptr [di + 04Fh], cl ; @349D
    shl al, 1 ; @34A0
    out dx, al ; @34A2
    mov byte ptr [di], ch ; @34A3
    mov byte ptr [di + 1], bh ; @34A5
    mov byte ptr [di + 2], bh ; @34A8
    mov byte ptr [di + 3], bl ; @34AB
    mov byte ptr [di + 4], bl ; @34AE
    mov byte ptr [di + 5], bl ; @34B1
    mov byte ptr [di + 6], bl ; @34B4
    mov byte ptr [di + 7], bl ; @34B7
    mov byte ptr [di + 8], bl ; @34BA
    mov byte ptr [di + 9], bl ; @34BD
    mov byte ptr [di + 0Ah], bh ; @34C0
    mov byte ptr [di + 0Bh], cl ; @34C3
    mov byte ptr [di + 0Ch], cl ; @34C6
    mov byte ptr [di + 0Dh], ch ; @34C9
    mov byte ptr [di + 0Eh], cl ; @34CC
    mov byte ptr [di + 0Fh], ch ; @34CF
    mov byte ptr [di + 010h], ch ; @34D2
    mov byte ptr [di + 011h], ch ; @34D5
    mov byte ptr [di + 012h], ch ; @34D8
    mov byte ptr [di + 013h], ch ; @34DB
    mov byte ptr [di + 014h], cl ; @34DE
    mov byte ptr [di + 015h], bh ; @34E1
    mov byte ptr [di + 016h], bh ; @34E4
    mov byte ptr [di + 017h], bh ; @34E7
    mov byte ptr [di + 018h], ch ; @34EA
    mov byte ptr [di + 019h], cl ; @34ED
    mov byte ptr [di + 01Ah], bh ; @34F0
    mov byte ptr [di + 01Bh], bl ; @34F3
    mov byte ptr [di + 01Ch], bl ; @34F6
    mov byte ptr [di + 01Dh], bl ; @34F9
    mov byte ptr [di + 01Eh], bl ; @34FC
    mov byte ptr [di + 01Fh], bl ; @34FF
    mov byte ptr [di + 020h], bl ; @3502
    mov byte ptr [di + 021h], bl ; @3505
    mov byte ptr [di + 022h], bh ; @3508
    mov byte ptr [di + 023h], cl ; @350B
    mov byte ptr [di + 024h], cl ; @350E
    mov byte ptr [di + 025h], ch ; @3511
    mov byte ptr [di + 026h], cl ; @3514
    mov byte ptr [di + 027h], cl ; @3517
    mov byte ptr [di + 028h], ch ; @351A
    mov byte ptr [di + 029h], ch ; @351D
    mov byte ptr [di + 02Ah], ch ; @3520
    mov byte ptr [di + 02Bh], ch ; @3523
    mov byte ptr [di + 02Ch], ch ; @3526
    mov byte ptr [di + 02Dh], bh ; @3529
    mov byte ptr [di + 02Eh], bh ; @352C
    mov byte ptr [di + 02Fh], bh ; @352F
    mov byte ptr [di + 030h], bh ; @3532
    mov byte ptr [di + 031h], ch ; @3535
    mov byte ptr [di + 032h], bh ; @3538
    mov byte ptr [di + 033h], bh ; @353B
    mov byte ptr [di + 034h], bl ; @353E
    mov byte ptr [di + 035h], bl ; @3541
    mov byte ptr [di + 036h], bl ; @3544
    mov byte ptr [di + 037h], bl ; @3547
    mov byte ptr [di + 038h], bl ; @354A
    mov byte ptr [di + 039h], bl ; @354D
    mov byte ptr [di + 03Ah], bl ; @3550
    mov byte ptr [di + 03Bh], bh ; @3553
    mov byte ptr [di + 03Ch], cl ; @3556
    mov byte ptr [di + 03Dh], cl ; @3559
    mov byte ptr [di + 03Eh], ch ; @355C
    mov byte ptr [di + 03Fh], cl ; @355F
    mov byte ptr [di + 040h], ch ; @3562
    mov byte ptr [di + 041h], ch ; @3565
    mov byte ptr [di + 042h], ch ; @3568
    mov byte ptr [di + 043h], cl ; @356B
    mov byte ptr [di + 044h], ch ; @356E
    mov byte ptr [di + 045h], bh ; @3571
    mov byte ptr [di + 046h], bh ; @3574
    mov byte ptr [di + 047h], bl ; @3577
    mov byte ptr [di + 048h], bl ; @357A
    mov byte ptr [di + 049h], bl ; @357D
    mov byte ptr [di + 04Ah], bl ; @3580
    mov byte ptr [di + 04Bh], bl ; @3583
    mov byte ptr [di + 04Ch], bl ; @3586
    mov byte ptr [di + 04Dh], bh ; @3589
    mov byte ptr [di + 04Eh], cl ; @358C
    mov byte ptr [di + 04Fh], cl ; @358F
    mov al, 0Fh ; @3592
    out dx, al ; @3594
    pop ds ; @3595
    ret ; @3596
; CONTRACT (tools/apply.py)
; Draw water animation frame 2, a tail entry of DrawWaterSurface, not an ordinary callee.
; In: DS:DI=VGA row; DX=03C5h, sequencer index=2, mask=1; AX=5401h, BX=5655h, CX=5857h.
; Stack top is saved DGROUP DS, followed by DrawWaterSurface's near return address.
; Out: 80 byte stores per plane, masks 1/2/4/8; final AL=0Fh written as the map mask.
; Consume saved DS and near-return to caller; DI/DX/BX/CX remain as supplied by dispatcher.
; END CONTRACT
DrawWaterSurfaceFrame2:
    mov byte ptr [di], cl ; @3597
    mov byte ptr [di + 1], cl ; @3599
    mov byte ptr [di + 2], cl ; @359C
    mov byte ptr [di + 3], cl ; @359F
    mov byte ptr [di + 4], bh ; @35A2
    mov byte ptr [di + 5], bh ; @35A5
    mov byte ptr [di + 6], bh ; @35A8
    mov byte ptr [di + 7], bh ; @35AB
    mov byte ptr [di + 8], bh ; @35AE
    mov byte ptr [di + 9], bh ; @35B1
    mov byte ptr [di + 0Ah], cl ; @35B4
    mov byte ptr [di + 0Bh], ch ; @35B7
    mov byte ptr [di + 0Ch], ch ; @35BA
    mov byte ptr [di + 0Dh], ch ; @35BD
    mov byte ptr [di + 0Eh], cl ; @35C0
    mov byte ptr [di + 0Fh], cl ; @35C3
    mov byte ptr [di + 010h], ch ; @35C6
    mov byte ptr [di + 011h], cl ; @35C9
    mov byte ptr [di + 012h], ch ; @35CC
    mov byte ptr [di + 013h], ch ; @35CF
    mov byte ptr [di + 014h], cl ; @35D2
    mov byte ptr [di + 015h], cl ; @35D5
    mov byte ptr [di + 016h], cl ; @35D8
    mov byte ptr [di + 017h], cl ; @35DB
    mov byte ptr [di + 018h], cl ; @35DE
    mov byte ptr [di + 019h], cl ; @35E1
    mov byte ptr [di + 01Ah], cl ; @35E4
    mov byte ptr [di + 01Bh], cl ; @35E7
    mov byte ptr [di + 01Ch], bh ; @35EA
    mov byte ptr [di + 01Dh], bh ; @35ED
    mov byte ptr [di + 01Eh], bh ; @35F0
    mov byte ptr [di + 01Fh], bl ; @35F3
    mov byte ptr [di + 020h], bh ; @35F6
    mov byte ptr [di + 021h], bh ; @35F9
    mov byte ptr [di + 022h], bh ; @35FC
    mov byte ptr [di + 023h], cl ; @35FF
    mov byte ptr [di + 024h], ch ; @3602
    mov byte ptr [di + 025h], ch ; @3605
    mov byte ptr [di + 026h], cl ; @3608
    mov byte ptr [di + 027h], cl ; @360B
    mov byte ptr [di + 028h], ch ; @360E
    mov byte ptr [di + 029h], cl ; @3611
    mov byte ptr [di + 02Ah], ch ; @3614
    mov byte ptr [di + 02Bh], ch ; @3617
    mov byte ptr [di + 02Ch], ch ; @361A
    mov byte ptr [di + 02Dh], cl ; @361D
    mov byte ptr [di + 02Eh], cl ; @3620
    mov byte ptr [di + 02Fh], cl ; @3623
    mov byte ptr [di + 030h], cl ; @3626
    mov byte ptr [di + 031h], cl ; @3629
    mov byte ptr [di + 032h], cl ; @362C
    mov byte ptr [di + 033h], cl ; @362F
    mov byte ptr [di + 034h], cl ; @3632
    mov byte ptr [di + 035h], bh ; @3635
    mov byte ptr [di + 036h], bh ; @3638
    mov byte ptr [di + 037h], bh ; @363B
    mov byte ptr [di + 038h], bh ; @363E
    mov byte ptr [di + 039h], bh ; @3641
    mov byte ptr [di + 03Ah], bh ; @3644
    mov byte ptr [di + 03Bh], cl ; @3647
    mov byte ptr [di + 03Ch], ch ; @364A
    mov byte ptr [di + 03Dh], ch ; @364D
    mov byte ptr [di + 03Eh], ch ; @3650
    mov byte ptr [di + 03Fh], cl ; @3653
    mov byte ptr [di + 040h], cl ; @3656
    mov byte ptr [di + 041h], ch ; @3659
    mov byte ptr [di + 042h], cl ; @365C
    mov byte ptr [di + 043h], ch ; @365F
    mov byte ptr [di + 044h], cl ; @3662
    mov byte ptr [di + 045h], cl ; @3665
    mov byte ptr [di + 046h], cl ; @3668
    mov byte ptr [di + 047h], cl ; @366B
    mov byte ptr [di + 048h], bh ; @366E
    mov byte ptr [di + 049h], bh ; @3671
    mov byte ptr [di + 04Ah], bl ; @3674
    mov byte ptr [di + 04Bh], bh ; @3677
    mov byte ptr [di + 04Ch], bh ; @367A
    mov byte ptr [di + 04Dh], bh ; @367D
    mov byte ptr [di + 04Eh], cl ; @3680
    mov byte ptr [di + 04Fh], ch ; @3683
    shl al, 1 ; @3686
    out dx, al ; @3688
    mov byte ptr [di], cl ; @3689
    mov byte ptr [di + 1], cl ; @368B
    mov byte ptr [di + 2], cl ; @368E
    mov byte ptr [di + 3], cl ; @3691
    mov byte ptr [di + 4], bh ; @3694
    mov byte ptr [di + 5], bh ; @3697
    mov byte ptr [di + 6], bl ; @369A
    mov byte ptr [di + 7], bh ; @369D
    mov byte ptr [di + 8], bh ; @36A0
    mov byte ptr [di + 9], bh ; @36A3
    mov byte ptr [di + 0Ah], cl ; @36A6
    mov byte ptr [di + 0Bh], ch ; @36A9
    mov byte ptr [di + 0Ch], ch ; @36AC
    mov byte ptr [di + 0Dh], ch ; @36AF
    mov byte ptr [di + 0Eh], cl ; @36B2
    mov byte ptr [di + 0Fh], cl ; @36B5
    mov byte ptr [di + 010h], ch ; @36B8
    mov byte ptr [di + 011h], cl ; @36BB
    mov byte ptr [di + 012h], ch ; @36BE
    mov byte ptr [di + 013h], ch ; @36C1
    mov byte ptr [di + 014h], cl ; @36C4
    mov byte ptr [di + 015h], cl ; @36C7
    mov byte ptr [di + 016h], cl ; @36CA
    mov byte ptr [di + 017h], cl ; @36CD
    mov byte ptr [di + 018h], cl ; @36D0
    mov byte ptr [di + 019h], cl ; @36D3
    mov byte ptr [di + 01Ah], cl ; @36D6
    mov byte ptr [di + 01Bh], cl ; @36D9
    mov byte ptr [di + 01Ch], bh ; @36DC
    mov byte ptr [di + 01Dh], bh ; @36DF
    mov byte ptr [di + 01Eh], bh ; @36E2
    mov byte ptr [di + 01Fh], bh ; @36E5
    mov byte ptr [di + 020h], bh ; @36E8
    mov byte ptr [di + 021h], bh ; @36EB
    mov byte ptr [di + 022h], cl ; @36EE
    mov byte ptr [di + 023h], ch ; @36F1
    mov byte ptr [di + 024h], ch ; @36F4
    mov byte ptr [di + 025h], ch ; @36F7
    mov byte ptr [di + 026h], cl ; @36FA
    mov byte ptr [di + 027h], cl ; @36FD
    mov byte ptr [di + 028h], ch ; @3700
    mov byte ptr [di + 029h], cl ; @3703
    mov byte ptr [di + 02Ah], ch ; @3706
    mov byte ptr [di + 02Bh], ch ; @3709
    mov byte ptr [di + 02Ch], cl ; @370C
    mov byte ptr [di + 02Dh], cl ; @370F
    mov byte ptr [di + 02Eh], cl ; @3712
    mov byte ptr [di + 02Fh], cl ; @3715
    mov byte ptr [di + 030h], cl ; @3718
    mov byte ptr [di + 031h], cl ; @371B
    mov byte ptr [di + 032h], cl ; @371E
    mov byte ptr [di + 033h], cl ; @3721
    mov byte ptr [di + 034h], cl ; @3724
    mov byte ptr [di + 035h], bh ; @3727
    mov byte ptr [di + 036h], bh ; @372A
    mov byte ptr [di + 037h], bl ; @372D
    mov byte ptr [di + 038h], bh ; @3730
    mov byte ptr [di + 039h], bh ; @3733
    mov byte ptr [di + 03Ah], bh ; @3736
    mov byte ptr [di + 03Bh], cl ; @3739
    mov byte ptr [di + 03Ch], ch ; @373C
    mov byte ptr [di + 03Dh], ch ; @373F
    mov byte ptr [di + 03Eh], ch ; @3742
    mov byte ptr [di + 03Fh], cl ; @3745
    mov byte ptr [di + 040h], cl ; @3748
    mov byte ptr [di + 041h], ch ; @374B
    mov byte ptr [di + 042h], cl ; @374E
    mov byte ptr [di + 043h], cl ; @3751
    mov byte ptr [di + 044h], cl ; @3754
    mov byte ptr [di + 045h], cl ; @3757
    mov byte ptr [di + 046h], cl ; @375A
    mov byte ptr [di + 047h], bh ; @375D
    mov byte ptr [di + 048h], bh ; @3760
    mov byte ptr [di + 049h], bh ; @3763
    mov byte ptr [di + 04Ah], bl ; @3766
    mov byte ptr [di + 04Bh], bh ; @3769
    mov byte ptr [di + 04Ch], bh ; @376C
    mov byte ptr [di + 04Dh], bh ; @376F
    mov byte ptr [di + 04Eh], cl ; @3772
    mov byte ptr [di + 04Fh], ch ; @3775
    shl al, 1 ; @3778
    out dx, al ; @377A
    mov byte ptr [di], cl ; @377B
    mov byte ptr [di + 1], cl ; @377D
    mov byte ptr [di + 2], cl ; @3780
    mov byte ptr [di + 3], cl ; @3783
    mov byte ptr [di + 4], bh ; @3786
    mov byte ptr [di + 5], bh ; @3789
    mov byte ptr [di + 6], bl ; @378C
    mov byte ptr [di + 7], bh ; @378F
    mov byte ptr [di + 8], bh ; @3792
    mov byte ptr [di + 9], bh ; @3795
    mov byte ptr [di + 0Ah], cl ; @3798
    mov byte ptr [di + 0Bh], ch ; @379B
    mov byte ptr [di + 0Ch], ch ; @379E
    mov byte ptr [di + 0Dh], ch ; @37A1
    mov byte ptr [di + 0Eh], cl ; @37A4
    mov byte ptr [di + 0Fh], cl ; @37A7
    mov byte ptr [di + 010h], cl ; @37AA
    mov byte ptr [di + 011h], ch ; @37AD
    mov byte ptr [di + 012h], ch ; @37B0
    mov byte ptr [di + 013h], ch ; @37B3
    mov byte ptr [di + 014h], cl ; @37B6
    mov byte ptr [di + 015h], cl ; @37B9
    mov byte ptr [di + 016h], cl ; @37BC
    mov byte ptr [di + 017h], cl ; @37BF
    mov byte ptr [di + 018h], cl ; @37C2
    mov byte ptr [di + 019h], cl ; @37C5
    mov byte ptr [di + 01Ah], cl ; @37C8
    mov byte ptr [di + 01Bh], cl ; @37CB
    mov byte ptr [di + 01Ch], bh ; @37CE
    mov byte ptr [di + 01Dh], bh ; @37D1
    mov byte ptr [di + 01Eh], bl ; @37D4
    mov byte ptr [di + 01Fh], bh ; @37D7
    mov byte ptr [di + 020h], bh ; @37DA
    mov byte ptr [di + 021h], bh ; @37DD
    mov byte ptr [di + 022h], cl ; @37E0
    mov byte ptr [di + 023h], ch ; @37E3
    mov byte ptr [di + 024h], ch ; @37E6
    mov byte ptr [di + 025h], ch ; @37E9
    mov byte ptr [di + 026h], cl ; @37EC
    mov byte ptr [di + 027h], cl ; @37EF
    mov byte ptr [di + 028h], ch ; @37F2
    mov byte ptr [di + 029h], cl ; @37F5
    mov byte ptr [di + 02Ah], ch ; @37F8
    mov byte ptr [di + 02Bh], ch ; @37FB
    mov byte ptr [di + 02Ch], cl ; @37FE
    mov byte ptr [di + 02Dh], cl ; @3801
    mov byte ptr [di + 02Eh], cl ; @3804
    mov byte ptr [di + 02Fh], cl ; @3807
    mov byte ptr [di + 030h], cl ; @380A
    mov byte ptr [di + 031h], cl ; @380D
    mov byte ptr [di + 032h], cl ; @3810
    mov byte ptr [di + 033h], cl ; @3813
    mov byte ptr [di + 034h], cl ; @3816
    mov byte ptr [di + 035h], bh ; @3819
    mov byte ptr [di + 036h], bh ; @381C
    mov byte ptr [di + 037h], bl ; @381F
    mov byte ptr [di + 038h], bh ; @3822
    mov byte ptr [di + 039h], bh ; @3825
    mov byte ptr [di + 03Ah], bh ; @3828
    mov byte ptr [di + 03Bh], cl ; @382B
    mov byte ptr [di + 03Ch], ch ; @382E
    mov byte ptr [di + 03Dh], ch ; @3831
    mov byte ptr [di + 03Eh], ch ; @3834
    mov byte ptr [di + 03Fh], cl ; @3837
    mov byte ptr [di + 040h], cl ; @383A
    mov byte ptr [di + 041h], cl ; @383D
    mov byte ptr [di + 042h], ch ; @3840
    mov byte ptr [di + 043h], cl ; @3843
    mov byte ptr [di + 044h], cl ; @3846
    mov byte ptr [di + 045h], cl ; @3849
    mov byte ptr [di + 046h], cl ; @384C
    mov byte ptr [di + 047h], bh ; @384F
    mov byte ptr [di + 048h], bh ; @3852
    mov byte ptr [di + 049h], bh ; @3855
    mov byte ptr [di + 04Ah], bh ; @3858
    mov byte ptr [di + 04Bh], bh ; @385B
    mov byte ptr [di + 04Ch], bh ; @385E
    mov byte ptr [di + 04Dh], cl ; @3861
    mov byte ptr [di + 04Eh], ch ; @3864
    mov byte ptr [di + 04Fh], ch ; @3867
    shl al, 1 ; @386A
    out dx, al ; @386C
    mov byte ptr [di], cl ; @386D
    mov byte ptr [di + 1], cl ; @386F
    mov byte ptr [di + 2], cl ; @3872
    mov byte ptr [di + 3], bh ; @3875
    mov byte ptr [di + 4], bh ; @3878
    mov byte ptr [di + 5], bh ; @387B
    mov byte ptr [di + 6], bl ; @387E
    mov byte ptr [di + 7], bh ; @3881
    mov byte ptr [di + 8], bh ; @3884
    mov byte ptr [di + 9], bh ; @3887
    mov byte ptr [di + 0Ah], cl ; @388A
    mov byte ptr [di + 0Bh], ch ; @388D
    mov byte ptr [di + 0Ch], ch ; @3890
    mov byte ptr [di + 0Dh], cl ; @3893
    mov byte ptr [di + 0Eh], cl ; @3896
    mov byte ptr [di + 0Fh], ch ; @3899
    mov byte ptr [di + 010h], cl ; @389C
    mov byte ptr [di + 011h], ch ; @389F
    mov byte ptr [di + 012h], ch ; @38A2
    mov byte ptr [di + 013h], ch ; @38A5
    mov byte ptr [di + 014h], cl ; @38A8
    mov byte ptr [di + 015h], cl ; @38AB
    mov byte ptr [di + 016h], cl ; @38AE
    mov byte ptr [di + 017h], cl ; @38B1
    mov byte ptr [di + 018h], cl ; @38B4
    mov byte ptr [di + 019h], cl ; @38B7
    mov byte ptr [di + 01Ah], cl ; @38BA
    mov byte ptr [di + 01Bh], cl ; @38BD
    mov byte ptr [di + 01Ch], bh ; @38C0
    mov byte ptr [di + 01Dh], bh ; @38C3
    mov byte ptr [di + 01Eh], bl ; @38C6
    mov byte ptr [di + 01Fh], bh ; @38C9
    mov byte ptr [di + 020h], bh ; @38CC
    mov byte ptr [di + 021h], bh ; @38CF
    mov byte ptr [di + 022h], cl ; @38D2
    mov byte ptr [di + 023h], ch ; @38D5
    mov byte ptr [di + 024h], ch ; @38D8
    mov byte ptr [di + 025h], ch ; @38DB
    mov byte ptr [di + 026h], cl ; @38DE
    mov byte ptr [di + 027h], cl ; @38E1
    mov byte ptr [di + 028h], cl ; @38E4
    mov byte ptr [di + 029h], ch ; @38E7
    mov byte ptr [di + 02Ah], ch ; @38EA
    mov byte ptr [di + 02Bh], ch ; @38ED
    mov byte ptr [di + 02Ch], cl ; @38F0
    mov byte ptr [di + 02Dh], cl ; @38F3
    mov byte ptr [di + 02Eh], cl ; @38F6
    mov byte ptr [di + 02Fh], cl ; @38F9
    mov byte ptr [di + 030h], cl ; @38FC
    mov byte ptr [di + 031h], cl ; @38FF
    mov byte ptr [di + 032h], cl ; @3902
    mov byte ptr [di + 033h], cl ; @3905
    mov byte ptr [di + 034h], bh ; @3908
    mov byte ptr [di + 035h], bh ; @390B
    mov byte ptr [di + 036h], bh ; @390E
    mov byte ptr [di + 037h], bl ; @3911
    mov byte ptr [di + 038h], bh ; @3914
    mov byte ptr [di + 039h], bh ; @3917
    mov byte ptr [di + 03Ah], bh ; @391A
    mov byte ptr [di + 03Bh], cl ; @391D
    mov byte ptr [di + 03Ch], ch ; @3920
    mov byte ptr [di + 03Dh], ch ; @3923
    mov byte ptr [di + 03Eh], cl ; @3926
    mov byte ptr [di + 03Fh], cl ; @3929
    mov byte ptr [di + 040h], ch ; @392C
    mov byte ptr [di + 041h], cl ; @392F
    mov byte ptr [di + 042h], ch ; @3932
    mov byte ptr [di + 043h], cl ; @3935
    mov byte ptr [di + 044h], cl ; @3938
    mov byte ptr [di + 045h], cl ; @393B
    mov byte ptr [di + 046h], cl ; @393E
    mov byte ptr [di + 047h], bh ; @3941
    mov byte ptr [di + 048h], bh ; @3944
    mov byte ptr [di + 049h], bl ; @3947
    mov byte ptr [di + 04Ah], bh ; @394A
    mov byte ptr [di + 04Bh], bh ; @394D
    mov byte ptr [di + 04Ch], bh ; @3950
    mov byte ptr [di + 04Dh], cl ; @3953
    mov byte ptr [di + 04Eh], ch ; @3956
    mov byte ptr [di + 04Fh], ch ; @3959
    mov al, 0Fh ; @395C
    out dx, al ; @395E
    pop ds ; @395F
    ret ; @3960
; CONTRACT (tools/apply.py)
; Initialize a new game with three lives, multiplier one and a zero 32-bit score.
; In: DS=DGROUP.
; Out: byte LivesRemaining=3, byte ScoreMultiplier=1, words 261Eh/2620h=0, AX=0.
; Effects/quirks: multiplier is read elsewhere as a word; this initializes only its low byte.
; Internal 396Dh clears only the score and must retain its separate entry semantics.
; END CONTRACT
ResetScoreLivesAndMultiplier:
    mov byte ptr ds:[LivesRemaining], 3 ; @3961
    nop ; @3966
    mov byte ptr ds:[ScoreMultiplier], 1 ; @3967
    nop ; @396C
loc_396D:
    xor ax, ax ; @396D
    mov word ptr ds:[ScoreLowWord], ax ; @396F
    mov word ptr ds:[ScoreHighWord], ax ; @3972
    ret ; @3975
; CONTRACT (tools/apply.py)
; Load the selected level record, unpack its tile map, and initialize player and entity arrays.
; In: DS=DGROUP; player count 2634 selects a level-order table, 261C indexes that table.
; Out: copies 26 record bytes and 320 map bytes; sets callbacks, coordinates and rain state.
; Effects/quirks: list termination differs by family; no bounds checks on list lengths or indices.
; Y scaling is signed; positions use 1/32 units. Special descriptor identities choose layouts.
; Preserves DS through decompression; leaves ES=DGROUP and DF clear. Calls no DOS services.
; END CONTRACT
LoadCurrentLevelState:
    mov bx, word ptr ds:[PlayerCount] ; @3976
    dec bx ; @397A
    shl bx, 1 ; @397B
    mov bx, word ptr [bx + LevelOrderTables] ; @397D
    mov si, word ptr ds:[CurrentLevelIndex] ; @3981
    shl si, 1 ; @3985
    mov bx, word ptr [bx + si] ; @3987
    mov si, 018h ; @3989
    nop ; @398C
loc_398D:
    mov ax, word ptr [bx + si] ; @398D
    mov word ptr [si + CurrentLevelRecord], ax ; @398F
    sub si, 2 ; @3993
    jns short loc_398D ; @3996
    mov word ptr cs:[RendererScratchWord], ax ; @3998
    push ds ; @399C
    lds si, dword ptr ds:[CompressedTileMapsPointer] ; @399D
    call UnpackIceToScratch ; @39A1
    push es ; @39A4
    pop ds ; @39A5
    mov si, word ptr cs:[RendererScratchWord] ; @39A6
loc_39AB:
    mov dx, seg ext_5C09 ; @39AB
    mov es, dx ; @39AE
    mov di, 0264Ch ; @39B0
    mov cx, 0A0h ; @39B3
    rep movsw ; @39B6
    pop ds ; @39B8
    mov ax, word ptr ds:[LevelPlayerOneStartX] ; @39B9
    sub ax, word ptr 0200h ; @39BC
    mov word ptr ds:[PlayerX32], ax ; @39BF
    sar ax, 5 ; @39C2
    mov word ptr ds:[PlayerPixelX], ax ; @39C5
    mov word ptr ds:[PlayerCachedPixelX], ax ; @39C8
    mov ax, word ptr ds:[LevelPlayerOneStartY] ; @39CB
    call ScaleLevelYToThreeQuarters ; @39CE
    sub ax, word ptr 0140h ; @39D1
    mov word ptr ds:[PlayerY32], ax ; @39D4
    sar ax, 5 ; @39D7
    mov word ptr ds:[PlayerYPixels], ax ; @39DA
    mov word ptr ds:[PlayerCachedPixelY], ax ; @39DD
    mov ax, word ptr ds:[LevelPlayerTwoStartX] ; @39E0
    sub ax, word ptr 0200h ; @39E3
    mov word ptr ds:[PlayerTwoFixedX], ax ; @39E6
    sar ax, 5 ; @39E9
    mov word ptr ds:[PlayerTwoPixelX], ax ; @39EC
    mov word ptr ds:[PlayerTwoCachedPixelX], ax ; @39EF
    mov ax, word ptr ds:[LevelPlayerTwoStartY] ; @39F2
    call ScaleLevelYToThreeQuarters ; @39F5
    sub ax, word ptr 0140h ; @39F8
    mov word ptr ds:[PlayerTwoFixedY], ax ; @39FB
    sar ax, 5 ; @39FE
    mov word ptr ds:[SecondPlayerYPixels], ax ; @3A01
    mov word ptr ds:[PlayerTwoCachedPixelY], ax ; @3A04
    mov ax, 0FFFFh ; @3A07
    mov word ptr ds:[PlayerPlatformIndices], ax ; @3A0A
    mov word ptr ds:[ds_27FA], ax ; @3A0D
    mov word ptr ds:[PlayerAnimationCountdowns], ax ; @3A10
    mov word ptr ds:[PlayerTwoAnimationCountdown], ax ; @3A13
    mov word ptr ds:[PlayerSpriteIds], 0DAh ; @3A16
    mov word ptr ds:[PlayerTwoSpriteId], 0E0h ; @3A1C
    mov word ptr ds:[HudCachedPlayerOneIconState], ax ; @3A22
    mov word ptr ds:[HudCachedPlayerTwoIconState], ax ; @3A25
    mov byte ptr ds:[HudFareClearPending], al ; @3A28
    inc ax ; @3A2B
    mov word ptr ds:[PlayerCarriedKinds], ax ; @3A2C
    mov word ptr ds:[PlayerTwoPassengerIconState], ax ; @3A2F
    mov word ptr ds:[PlayerDestinationIcons], ax ; @3A32
    mov word ptr ds:[PlayerTwoDestinationIconIndex], ax ; @3A35
    mov word ptr ds:[PlayerPassengerFares], ax ; @3A38
    mov word ptr ds:[PlayerTwoFare], ax ; @3A3B
    mov word ptr ds:[PlayerHorizontalVelocities], ax ; @3A3E
    mov word ptr ds:[ds_2812], ax ; @3A41
    mov word ptr ds:[PlayerVerticalVelocities], ax ; @3A44
    mov word ptr ds:[ds_2816], ax ; @3A47
    mov ax, word ptr ds:[WaterY32] ; @3A4A
    call ScaleLevelYToThreeQuarters ; @3A4D
    cmp ax, word ptr 017E0h ; @3A50
    jbe loc_3A5B ; @3A53
    mov ax, 017E0h ; @3A58
loc_3A5B:
    mov word ptr ds:[WaterY32], ax ; @3A5B
    sar ax, 5 ; @3A5E
    mov word ptr ds:[WaterYPixels], ax ; @3A61
    mov word ptr ds:[PreviousWaterSurfaceY], ax ; @3A64
    mov si, word ptr ds:[LevelPlatformList] ; @3A67
    xor di, di ; @3A6B
loc_3A6D:
    lodsw ; @3A6D
    mov word ptr [di + PlatformLeftEdges], ax ; @3A6E
    and ax, word ptr 0FFFFh ; @3A72
    js loc_3AA9 ; @3A75
    lodsw ; @3A7A
    mov word ptr [di + PlatformRightEdges], ax ; @3A7B
    lodsw ; @3A7F
    call ScaleLevelYToThreeQuarters ; @3A80
    mov word ptr [di + PlatformHeights], ax ; @3A83
    lodsw ; @3A87
    mov word ptr [di + PlatformArrivalPointsX], ax ; @3A88
    lodsw ; @3A8C
    mov word ptr [di + PlatformWaitingPointsX], ax ; @3A8D
    lodsw ; @3A91
    mov word ptr [di + PlatformSpawnX], ax ; @3A92
    lodsw ; @3A96
    mov word ptr [di + PlatformDestinationIcons], ax ; @3A97
    add si, 2 ; @3A9B
    mov word ptr [di + PlatformActorOccupants], 0FFFFh ; @3A9E
    add di, 2 ; @3AA4
    jmp short loc_3A6D ; @3AA7
loc_3AA9:
    mov si, word ptr ds:[LevelActorList] ; @3AA9
    xor di, di ; @3AAD
loc_3AAF:
    lodsw ; @3AAF
    mov word ptr [di + ActorDescriptors], ax ; @3AB0
    cmp ax, word ptr 0FFFFh ; @3AB4
    je loc_3B1B ; @3AB7
    mov bx, ax ; @3ABC
    lodsw ; @3ABE
    mov word ptr [di + ActorInitialPlatformIndices], ax ; @3ABF
    lodsw ; @3AC3
    mov word ptr [di + ActorJourneyCursors], ax ; @3AC4
    mov ax, 0FFFFh ; @3AC8
    mov word ptr [di + ActorSpriteIds], ax ; @3ACB
    mov word ptr [di + ActorEraseSprite], ax ; @3ACF
    mov word ptr [di + ActorOverlayOrScriptCallbacks], ax ; @3AD3
    mov word ptr [di + ActorEraseOverlaySprite], ax ; @3AD7
    cmp bx, word ptr 078DCh ; @3ADB
    je loc_3AED ; @3ADF
    mov ax, word ptr [bx + 8] ; @3AE4
    mov word ptr [di + ActorUpdateOrScriptCursor], ax ; @3AE7
    jmp short loc_3B16 ; @3AEB
loc_3AED:
    mov ax, word ptr [bx + 010h] ; @3AED
    mov word ptr [di + ActorUpdateOrScriptCursor], ax ; @3AF0
    mov bx, word ptr [di + ActorInitialPlatformIndices] ; @3AF4
    shl bx, 1 ; @3AF8
    mov ax, word ptr [bx + PlatformSpawnX] ; @3AFA
    sub ax, word ptr 08h ; @3AFE
    shl ax, 5 ; @3B01
    mov word ptr [di + ActorX32], ax ; @3B04
    mov ax, word ptr [bx + PlatformHeights] ; @3B08
    sub ax, word ptr 0Bh ; @3B0C
    shl ax, 5 ; @3B0F
    mov word ptr [di + ActorY32], ax ; @3B12
loc_3B16:
    add di, 2 ; @3B16
    jmp short loc_3AAF ; @3B19
loc_3B1B:
    mov si, word ptr ds:[LevelEnemyList] ; @3B1B
    xor di, di ; @3B1F
loc_3B21:
    lodsw ; @3B21
    mov word ptr [di + EnemyDescriptors], ax ; @3B22
    cmp ax, word ptr 0FFFFh ; @3B26
    jne loc_3B31 ; @3B29
    jmp near ptr loc_3C04 ; @3B2E
loc_3B31:
    cmp ax, word ptr 076E4h ; @3B31
    jne loc_3B6C ; @3B34
    lodsw ; @3B39
    mov word ptr [di + EnemyPlatformIndices], ax ; @3B3A
    mov bx, ax ; @3B3E
    shl bx, 1 ; @3B40
    mov ax, word ptr [bx + PlatformSpawnX] ; @3B42
    sub ax, word ptr 010h ; @3B46
    shl ax, 5 ; @3B49
    mov word ptr [di + EnemyX32], ax ; @3B4C
    mov ax, word ptr [bx + PlatformHeights] ; @3B50
    sub ax, word ptr 018h ; @3B54
    shl ax, 5 ; @3B57
    mov word ptr [di + EnemyY32], ax ; @3B5A
    lodsw ; @3B5E
    mov word ptr [di + EnemyAnimationOrDropLists], ax ; @3B5F
    mov word ptr [di + EnemyStateCallbacks], offset InitializeFruitTreeAnimation ; @3B63
    jmp near ptr loc_3BFE ; @3B69
loc_3B6C:
    cmp ax, word ptr 07630h ; @3B6C
    jne loc_3B92 ; @3B6F
    add si, 2 ; @3B74
    lodsw ; @3B77
    call ScaleLevelSpeedToThreeHalves ; @3B78
    mov word ptr [di + EnemyInitialDelays], ax ; @3B7B
    lodsw ; @3B7F
    mov word ptr [di + EnemyHorizontalSpeeds], ax ; @3B80
    mov word ptr [di + EnemyDirectionOrTargetPlayer], 1 ; @3B84
    mov word ptr [di + EnemyStateCallbacks], offset BeginBirdDelay ; @3B8A
    jmp short loc_3BFE ; @3B90
loc_3B92:
    cmp ax, word ptr 076A8h ; @3B92
    jne loc_3BBB ; @3B95
    lodsw ; @3B9A
    shl ax, 5 ; @3B9B
    mov word ptr [di + EnemyX32], ax ; @3B9E
    lodsw ; @3BA2
    shl ax, 5 ; @3BA3
    call ScaleLevelYToThreeQuarters ; @3BA6
    sub ax, word ptr 02C0h ; @3BA9
    mov word ptr [di + EnemyY32], ax ; @3BAC
    add si, 4 ; @3BB0
    mov word ptr [di + EnemyStateCallbacks], offset InitializeDinoAnimation ; @3BB3
    jmp short loc_3BFE ; @3BB9
loc_3BBB:
    lodsw ; @3BBB
    mov word ptr [di + EnemyPlatformIndices], ax ; @3BBC
    mov bx, ax ; @3BC0
    shl bx, 1 ; @3BC2
    mov ax, word ptr [bx + PlatformSpawnX] ; @3BC4
    sub ax, word ptr 010h ; @3BC8
    shl ax, 5 ; @3BCB
    mov word ptr [di + EnemyX32], ax ; @3BCE
    mov ax, word ptr [bx + PlatformHeights] ; @3BD2
    sub ax, word ptr 016h ; @3BD6
    shl ax, 5 ; @3BD9
    mov word ptr [di + EnemyY32], ax ; @3BDC
    add si, 2 ; @3BE0
    lodsw ; @3BE3
    sar ax, 2 ; @3BE4
    neg ax ; @3BE7
    add ax, word ptr [si - 2] ; @3BE9
    neg ax ; @3BEC
    mov word ptr [di + EnemyHorizontalSpeeds], ax ; @3BEE
    mov word ptr [di + EnemyDirectionOrTargetPlayer], 0 ; @3BF2
    mov word ptr [di + EnemyStateCallbacks], offset BeginTriopterusPatrol ; @3BF8
loc_3BFE:
    add di, 2 ; @3BFE
    jmp near ptr loc_3B21 ; @3C01
loc_3C04:
    mov bx, 0180h ; @3C04
    xor ax, ax ; @3C07
loc_3C09:
    mov word ptr [bx + RainParticleOffsets], ax ; @3C09
    mov word ptr [bx + RainPreviousOffsets], ax ; @3C0D
    sub bx, 2 ; @3C11
    jns short loc_3C09 ; @3C14
    cmp byte ptr ds:[LevelRainDirection], 0 ; @3C16
    je loc_3C34 ; @3C1B
    mov bx, 0180h ; @3C20
loc_3C23:
    call RespawnRainParticle ; @3C23
    sub bx, 2 ; @3C26
    jns short loc_3C23 ; @3C29
    mov si, 0240h ; @3C2B
loc_3C2E:
    call AdvanceRainParticles ; @3C2E
    dec si ; @3C31
    jns short loc_3C2E ; @3C32
loc_3C34:
    ret ; @3C34
; CONTRACT (tools/apply.py)
; Choose a random top/side entry point for one rain particle above the water line.
; In: DS=DGROUP; BX is an even byte index; 2903 is water Y; 28F5 is rain direction.
; Out: writes byte offset at 2E8B+BX and X modulo four at 318F+BX; advances random state.
; Preserves BX via the random helper; clobbers AX,CX,DX. Row multiplication uses AL only.
; END CONTRACT
RespawnRainParticle:
    mov ax, 0140h ; @3C35
    add ax, word ptr ds:[WaterYPixels] ; @3C38
    call NextRandomBelowAx ; @3C3C
    cmp ax, word ptr 0140h ; @3C3F
    jae loc_3C4D ; @3C42
    mov cx, ax ; @3C47
    xor ax, ax ; @3C49
    jmp short loc_3C61 ; @3C4B
loc_3C4D:
    sub ax, word ptr 0140h ; @3C4D
    cmp byte ptr ds:[LevelRainDirection], 1 ; @3C50
    jne loc_3C5F ; @3C55
    mov cx, 013Fh ; @3C5A
    jmp short loc_3C61 ; @3C5D
loc_3C5F:
    xor cx, cx ; @3C5F
loc_3C61:
    mul byte ptr ds:[VgaRowStrideBytes] ; @3C61
    mov dx, cx ; @3C65
    shr dx, 2 ; @3C67
    add ax, dx ; @3C6A
    mov word ptr [bx + RainParticleOffsets], ax ; @3C6C
    and cx, 3 ; @3C70
    mov word ptr [bx + RainParticleXModuloFour], cx ; @3C73
    ret ; @3C77
; CONTRACT (tools/apply.py)
; Advance rain offsets and retain their prior positions for background restoration.
; In: DS=DGROUP; 2903 water Y, 2907 byte-offset limit, 28F5 direction (1 left, 2 right).
; Out: updates indices waterY+1 down to zero, inclusive; respawns offsets at/above the limit.
; Effects/quirks: alternating particles move two or three rows; X carries use low-byte TEST FC.
; Clobbers BX and BP; performs no VGA access. Initialization deliberately runs 577 iterations.
; END CONTRACT
AdvanceRainParticles:
    mov bx, word ptr ds:[WaterYPixels] ; @3C78
    inc bx ; @3C7C
    shl bx, 1 ; @3C7D
    mov al, byte ptr ds:[LevelRainDirection] ; @3C7F
    xor ah, ah ; @3C82
    mov bp, ax ; @3C84
    dec bp ; @3C86
    shl bp, 1 ; @3C87
    dec bp ; @3C89
loc_3C8A:
    mov ax, word ptr [bx + RainParticleOffsets] ; @3C8A
    mov word ptr [bx + RainPreviousOffsets], ax ; @3C8E
    add ax, word ptr 0C0h ; @3C92
    test bx, 2 ; @3C95
    jne loc_3CA1 ; @3C99
    add ax, word ptr 060h ; @3C9E
loc_3CA1:
    mov cx, word ptr [bx + RainParticleXModuloFour] ; @3CA1
    add cx, bp ; @3CA5
    add cx, bp ; @3CA7
    test bx, 2 ; @3CA9
    jne loc_3CB4 ; @3CAD
    add cx, bp ; @3CB2
loc_3CB4:
    test cx, 0FCh ; @3CB4
    je loc_3CBF ; @3CB8
    add ax, bp ; @3CBD
loc_3CBF:
    and cx, 3 ; @3CBF
    cmp ax, word ptr ds:[WaterSurfaceByteOffset] ; @3CC2
    jb loc_3CD0 ; @3CC6
    call RespawnRainParticle ; @3CCB
    jmp short loc_3CD8 ; @3CCE
loc_3CD0:
    mov word ptr [bx + RainParticleOffsets], ax ; @3CD0
    mov word ptr [bx + RainParticleXModuloFour], cx ; @3CD4
loc_3CD8:
    sub bx, 2 ; @3CD8
    jns short loc_3C8A ; @3CDB
    ret ; @3CDD
; CONTRACT (tools/apply.py)
; Restore the previous rain positions from the background VGA page to the draw page.
; In: DS=DGROUP; prior offsets 300D, water Y 2903; CS page pointers 4610 and 460C.
; Effects: VGA GC bit mask is set to zero for latch copies, then forced to FFh on return.
; Copies indices waterY+1 through zero across enabled planes; assumes compatible VGA state.
; Out: ES=A000h; clobbers AX,BX,CX,DX,SI,DI,BP. Does not restore prior GC selection or mask.
; END CONTRACT
RestoreRainBackground:
    mov dx, 03CEh ; @3CDE
    mov al, 8 ; @3CE1
    out dx, al ; @3CE3
    inc dx ; @3CE4
    mov al, 0 ; @3CE5
    out dx, al ; @3CE7
    mov di, 0A000h ; @3CE8
    mov es, di ; @3CEB
    mov cx, word ptr cs:[BackgroundPagePointer] ; @3CED
    mov bp, word ptr cs:[DrawPagePointer] ; @3CF2
    mov bx, word ptr ds:[WaterYPixels] ; @3CF7
    inc bx ; @3CFB
    shl bx, 1 ; @3CFC
loc_3CFE:
    mov si, cx ; @3CFE
    mov di, bp ; @3D00
    add si, word ptr [bx + RainPreviousOffsets] ; @3D02
    add di, word ptr [bx + RainPreviousOffsets] ; @3D06
    mov al, byte ptr es:[si] ; @3D0A
    mov byte ptr es:[di], al ; @3D0D
    sub bx, 2 ; @3D10
    jns short loc_3CFE ; @3D13
    mov al, 0FFh ; @3D15
    out dx, al ; @3D17
    ret ; @3D18
; CONTRACT (tools/apply.py)
; Plot rain pixels in color 5Bh on the current draw page, one VGA plane per particle.
; In: DS=DGROUP; water Y 2903, current offsets 2E8B and X modulo four 318F.
; Effects: visits indices waterY down to zero, inclusive; selects Sequencer map mask register 2.
; Out: forces map mask 0Fh; ES=A000h; clobbers AX,BX,CX,DX,DI,BP. No clipping is performed.
; END CONTRACT
DrawRainParticles:
    mov bx, word ptr ds:[WaterYPixels] ; @3D19
    shl bx, 1 ; @3D1D
    mov dx, 03C4h ; @3D1F
    mov al, 2 ; @3D22
    out dx, al ; @3D24
    inc dx ; @3D25
    mov di, 0A000h ; @3D26
    mov es, di ; @3D29
    mov bp, word ptr cs:[DrawPagePointer] ; @3D2B
    mov ah, 05Bh ; @3D30
loc_3D32:
    mov cx, word ptr [bx + RainParticleXModuloFour] ; @3D32
    mov al, 1 ; @3D36
    shl al, cl ; @3D38
    out dx, al ; @3D3A
    mov di, word ptr [bx + RainParticleOffsets] ; @3D3B
    add di, bp ; @3D3F
    mov byte ptr es:[di], ah ; @3D41
    sub bx, 2 ; @3D44
    jns short loc_3D32 ; @3D47
    mov al, 0Fh ; @3D49
    out dx, al ; @3D4B
    ret ; @3D4C
; CONTRACT (tools/apply.py)
; Convert a signed level Y value using AX - arithmetic_shift_right(AX,2).
; In: AX is a signed 16-bit coordinate; DS=DGROUP.
; Out: AX is the wrapped result; 2648 receives the signed quarter value; flags from SUB.
; Effects/quirks: rounds the removed quarter toward negative infinity; no multiply/divide rewrite.
; END CONTRACT
ScaleLevelYToThreeQuarters:
    push ax ; @3D4D
    sar ax, 2 ; @3D4E
    mov word ptr ds:[CoordinateScaleScratch], ax ; @3D51
    pop ax ; @3D54
    sub ax, word ptr ds:[CoordinateScaleScratch] ; @3D55
    ret ; @3D59
; CONTRACT (tools/apply.py)
; Scale a signed level speed using AX + arithmetic_shift_right(AX,1).
; In: AX is a signed 16-bit value; DS=DGROUP.
; Out: AX is the wrapped result; 2648 receives the signed half value; flags from ADD.
; Effects/quirks: negative odd values require arithmetic-shift rounding, not C truncating division.
; END CONTRACT
ScaleLevelSpeedToThreeHalves:
    push ax ; @3D5A
    sar ax, 1 ; @3D5B
    mov word ptr ds:[CoordinateScaleScratch], ax ; @3D5D
    pop ax ; @3D60
    add ax, word ptr ds:[CoordinateScaleScratch] ; @3D61
    ret ; @3D65
; CONTRACT (tools/apply.py)
; Reset level workspace and HUD caches, load the level, and prepare its VGA display pages.
; In: DS=DGROUP; current level, player count, score and life/multiplier counters.
; Effects: clears 392 bytes through 00B7; initializes timer to 23099; loads and renders the map.
; Draws HUD borders, copies background, initializes actors/enemies and tail-jumps to 0B4F.
; Cache values are deliberately different from live values to force later HUD redraws.
; Callees perform palette/retrace I/O; no new interrupt handler is installed here.
; END CONTRACT
InitializeLevelDisplay:
    mov cx, 0C4h ; @3D66
    les di, dword ptr ds:[LevelWorkspacePointer] ; @3D69
    xor ax, ax ; @3D6D
    rep stosw ; @3D6F
    mov word ptr ds:[LevelTimer], 05A3Bh ; @3D71
    mov ax, 0FFFFh ; @3D77
    mov word ptr ds:[ds_27C8], ax ; @3D7A
    mov word ptr ds:[ScreenFadeStep], 2 ; @3D7D
    mov al, byte ptr ds:[LivesRemaining] ; @3D83
    add al, 0Bh ; @3D86
    cmp al, 064h ; @3D88
    jb loc_3D91 ; @3D8A
    sub al, 064h ; @3D8F
loc_3D91:
    mov byte ptr ds:[HudCachedLives], al ; @3D91
    mov al, byte ptr ds:[ScoreMultiplier] ; @3D94
    add al, 0Bh ; @3D97
    cmp al, 064h ; @3D99
    jb loc_3DA2 ; @3D9B
    sub al, 064h ; @3DA0
loc_3DA2:
    mov byte ptr ds:[HudCachedMultiplier], al ; @3DA2
    mov byte ptr ds:[HudCachedLevelCounter], 063h ; @3DA5
    nop ; @3DAA
    mov word ptr ds:[HudCachedFare], 0270Fh ; @3DAB
    mov ax, word ptr ds:[ScoreLowWord] ; @3DB1
    mov dx, word ptr ds:[ScoreHighWord] ; @3DB4
    add ax, word ptr 0B207h ; @3DB8
    adc dx, 1 ; @3DBB
    cmp dx, 0Fh ; @3DBE
    jb loc_3DD9 ; @3DC1
    ja loc_3DD3 ; @3DC6
    cmp ax, word ptr 04240h ; @3DCB
    jbe loc_3DD9 ; @3DCE
loc_3DD3:
    sub ax, word ptr 04240h ; @3DD3
    sbb dx, 0Fh ; @3DD6
loc_3DD9:
    mov word ptr ds:[HudCachedScoreLow], ax ; @3DD9
    mov word ptr ds:[HudCachedScoreHigh], dx ; @3DDC
    mov word ptr ds:[HudDigitCursorY], 0C2h ; @3DE0
    cmp word ptr ds:[PlayerCount], 2 ; @3DE6
    je loc_3E1C ; @3DEB
    mov word ptr ds:[HudLivesX], 021h ; @3DF0
    mov word ptr ds:[HudScoreX], 076h ; @3DF6
    mov word ptr ds:[HudLevelCounterX], 0B1h ; @3DFC
    mov word ptr ds:[HudPlayerOneDestinationX], 0D0h ; @3E02
    mov word ptr ds:[HudPlayerOneIconX], 0E0h ; @3E08
    mov word ptr ds:[HudFareX], 0F4h ; @3E0E
    mov word ptr ds:[HudMultiplierX], 0122h ; @3E14
    jmp short loc_3E52 ; @3E1A
loc_3E1C:
    mov word ptr ds:[HudLivesX], 021h ; @3E1C
    mov word ptr ds:[HudScoreX], 072h ; @3E22
    mov word ptr ds:[HudLevelCounterX], 0A9h ; @3E28
    mov word ptr ds:[HudPlayerOneDestinationX], 0C7h ; @3E2E
    mov word ptr ds:[HudPlayerOneIconX], 0D7h ; @3E34
    mov word ptr ds:[HudFareX], 0E8h ; @3E3A
    mov word ptr ds:[HudMultiplierX], 0131h ; @3E40
    mov word ptr ds:[HudPlayerTwoIconX], 0102h ; @3E46
    mov word ptr ds:[HudPlayerTwoDestinationX], 0112h ; @3E4C
loc_3E52:
    call LoadCurrentLevelState ; @3E52
    call ShowLevelIntroduction ; @3E55
    call ClearAllVgaPlanes ; @3E58
    call BlackenVgaPalette ; @3E5B
    call DuplicateSourcePaletteHalves ; @3E5E
    call DrawTileMap ; @3E61
    call SaveDrawPageBackground ; @3E64
    call SwapAndDisplayVgaPage ; @3E67
    call RestorePlayfieldBackground ; @3E6A
    call DrawHudBorders ; @3E6D
    call DispatchEnemyStates ; @3E70
    call DispatchActorUpdates ; @3E73
    jmp near ptr ResetSpriteEraseState ; @3E76
; CONTRACT (tools/apply.py)
; Draw left/right HUD border sprites selected by one-player versus two-player mode.
; In: DS=DGROUP; 2634 player count; initialized VGA pages and sprite pointers.
; Effects: sprites AEh/AFh or B0h/B1h at X=0/255, Y=193 via 41FD; tail-call for right edge.
; Clobbers AX,BX,CX,BP; sprite drawing changes VGA map mask and shared CS scratch.
; END CONTRACT
DrawHudBorders:
    cmp word ptr ds:[PlayerCount], 2 ; @3E79
    je loc_3E8B ; @3E7E
    mov ax, 0AEh ; @3E83
    mov bp, 0AFh ; @3E86
    jmp short loc_3E91 ; @3E89
loc_3E8B:
    mov ax, 0B0h ; @3E8B
    mov bp, 0B1h ; @3E8E
loc_3E91:
    push bp ; @3E91
    xor bx, bx ; @3E92
    mov cx, 0C1h ; @3E94
    call DrawTransparentSprite ; @3E97
    pop ax ; @3E9A
    mov bx, 0FFh ; @3E9B
    jmp near ptr DrawTransparentSprite ; @3E9E
; CONTRACT (tools/apply.py)
; Draw one HUD digit and advance the shared horizontal cursor by six pixels.
; In: AL is a digit value; DS=DGROUP; 27AC/27AE are cursor X/Y.
; Out: AX preserved by digit helper; cursor X wraps at 16 bits; flags from ADD.
; Reachability: unreferenced pattern seed; no observed caller establishes live use.
; END CONTRACT
DrawHudDigitAndAdvance:
    call DrawHudDigit ; @3EA1
    add word ptr ds:[HudDigitCursorX], 6 ; @3EA4
    ret ; @3EA9
; CONTRACT (tools/apply.py)
; Draw sprite CCh+AL at the shared HUD digit cursor without advancing the cursor.
; In: AL is a digit value; DS=DGROUP; 27AC/27AE give pixel X/Y.
; Out: preserves AX; sets BX/CX to cursor X/Y; BP is clobbered by 41FD.
; Effects: transparent planar VGA sprite drawing; no digit range check.
; END CONTRACT
DrawHudDigit:
    push ax ; @3EAA
    xor ah, ah ; @3EAB
    add ax, word ptr 0CCh ; @3EAD
    mov bx, word ptr ds:[HudDigitCursorX] ; @3EB0
    mov cx, word ptr ds:[HudDigitCursorY] ; @3EB4
    call DrawTransparentSprite ; @3EB8
    pop ax ; @3EBB
    ret ; @3EBC
; CONTRACT (tools/apply.py)
; Encode current/previous six-digit values and redraw only changed HUD digits.
; In: DX:AX current score, CX:BX previous score, normally 0..999999; DS=DGROUP.
; Out: overwrites digit buffers 00C8 and 00CF; advances 27AC six pixels per digit.
; Effects/quirks: jumps to shared 3EDD comparison tail owned physically by 3ECF.
; The comparison draws zero digits normally; it does not blank or suppress leading zeros.
; END CONTRACT
RedrawChangedSixDigitNumber:
    mov si, 0C8h ; @3EBD
    call EncodeSixDecimalDigits ; @3EC0
    mov ax, bx ; @3EC3
    mov dx, cx ; @3EC5
    mov si, 0CFh ; @3EC7
    call EncodeSixDecimalDigits ; @3ECA
    jmp short loc_3EDD ; @3ECD
; CONTRACT (tools/apply.py)
; Encode current/previous four-digit values and redraw only changed HUD digits.
; In: AX current value and BX previous value, normally 0..9999; DS=DGROUP.
; Out: overwrites digit buffers 00C8 and 00CF; advances 27AC by 24 pixels.
; Effects/quirks: 3EDD is also entered by six-digit and two-digit wrappers; digits are numeric.
; END CONTRACT
RedrawChangedFourDigitNumber:
    mov si, 0C8h ; @3ECF
    call EncodeFourDecimalDigits ; @3ED2
    mov ax, bx ; @3ED5
    mov si, 0CFh ; @3ED7
    call EncodeFourDecimalDigits ; @3EDA
loc_3EDD:
    xor si, si ; @3EDD
loc_3EDF:
    mov al, byte ptr [si + 0C8h] ; @3EDF
    cmp al, 0FFh ; @3EE3
    je loc_3EFE ; @3EE5
    cmp al, byte ptr [si + 0CFh] ; @3EEA
    je loc_3EF6 ; @3EEE
    call DrawHudDigit ; @3EF3
loc_3EF6:
    add word ptr ds:[HudDigitCursorX], 6 ; @3EF6
    inc si ; @3EFB
    jmp short loc_3EDF ; @3EFC
loc_3EFE:
    ret ; @3EFE
; CONTRACT (tools/apply.py)
; Encode current/previous two-digit values and redraw only changed HUD digits.
; In: AL current value and BL previous value, normally 0..99; DS=DGROUP.
; Out: overwrites digit buffers 00C8 and 00CF; advances 27AC by 12 pixels.
; Effects: jumps to shared 3EDD tail; sprite drawing clobbers BP even when AX is preserved.
; END CONTRACT
RedrawChangedTwoDigitNumber:
    mov si, 0C8h ; @3EFF
    call EncodeTwoDecimalDigits ; @3F02
    mov al, bl ; @3F05
    mov si, 0CFh ; @3F07
    call EncodeTwoDecimalDigits ; @3F0A
    jmp short loc_3EDD ; @3F0D
; CONTRACT (tools/apply.py)
; Encode a bounded unsigned score as six numeric decimal bytes followed by FFh.
; In: DX:AX normally 0..999999; DS:SI output buffer; DGROUP divisors at 00C1/BF/BE/BD.
; Out: SI points at the FFh sentinel; AX,DX are destroyed; CX preserved.
; Effects/quirks: repeated 32-bit subtraction tests signed high-word sign, not unsigned borrow.
; Falls through 3F2F and 3F43; this is not a general unsigned-32 decimal conversion.
; END CONTRACT
EncodeSixDecimalDigits:
    push cx ; @3F0F
    mov cl, 0FFh ; @3F10
loc_3F12:
    inc cl ; @3F12
    sub ax, word ptr 086A0h ; @3F14
    sbb dx, 1 ; @3F17
    jns short loc_3F12 ; @3F1A
    add ax, word ptr 086A0h ; @3F1C
    adc dx, 1 ; @3F1F
    mov byte ptr [si], cl ; @3F22
    inc si ; @3F24
    div word ptr ds:[DecimalTenThousandDivisor] ; @3F25
    mov byte ptr [si], al ; @3F29
    inc si ; @3F2B
    mov ax, dx ; @3F2C
    pop cx ; @3F2E
; CONTRACT (tools/apply.py)
; Encode a bounded word as four numeric decimal bytes followed by FFh.
; In: AX normally 0..9999; DS:SI output buffer; DS=DGROUP for divisors 1000,100,10.
; Out: SI points at the FFh sentinel; AX,DX destroyed. Falls through to 3F43.
; Effects/quirks: uses unsigned DIV with no input checks; values above range need not be digits.
; END CONTRACT
EncodeFourDecimalDigits:
    xor dx, dx ; @3F2F
    div word ptr ds:[DecimalThousandDivisor] ; @3F31
    mov byte ptr [si], al ; @3F35
    inc si ; @3F37
    mov ax, dx ; @3F38
    div byte ptr ds:[DecimalHundredDivisor] ; @3F3A
    mov byte ptr [si], al ; @3F3E
    inc si ; @3F40
    mov al, ah ; @3F41
; CONTRACT (tools/apply.py)
; Encode AL as tens and units numeric bytes followed by FFh; there is no ASCII conversion.
; In: AL normally 0..99; DS:SI output buffer; DS=DGROUP supplies divisor ten at 00BD.
; Out: SI points at the FFh sentinel; AX destroyed; DX is unchanged by this tail.
; Effects/quirks: ignores input AH. DIV flags are undefined; callers must not use them as a result.
; END CONTRACT
EncodeTwoDecimalDigits:
    xor ah, ah ; @3F43
    div byte ptr ds:[DecimalTenDivisor] ; @3F45
    mov byte ptr [si], al ; @3F49
    inc si ; @3F4B
    mov al, ah ; @3F4C
    mov byte ptr [si], al ; @3F4E
    inc si ; @3F50
    mov byte ptr [si], 0FFh ; @3F51
    ret ; @3F54
; CONTRACT (tools/apply.py)
; Refresh cached HUD counters/icons/fare and update the three-row timer bar.
; In: DS=DGROUP; live score/counters/player state, cached HUD state and timer 2622.
; Out: caps score at 999999; updates caches; negative timer sets -1 and starts fade-out if needed.
; Effects/quirks: prioritized redraw branches skip lower-priority fields until a later call.
; Bar width is unsigned timer/700; shrink clears only one column per call, even after a jump.
; Uses VGA map mask port 3C5h and restores mask 0Fh; DS is restored after VGA writes.
; END CONTRACT
RefreshHudAndTimerBar:
    mov word ptr ds:[HudDigitCursorY], 0C2h ; @3F55
    mov al, byte ptr ds:[LivesRemaining] ; @3F5B
    mov bl, byte ptr ds:[HudCachedLives] ; @3F5E
    cmp al, bl ; @3F62
    je loc_3F77 ; @3F64
    mov byte ptr ds:[HudCachedLives], al ; @3F69
    mov bp, word ptr ds:[HudLivesX] ; @3F6C
    mov word ptr ds:[HudDigitCursorX], bp ; @3F70
    call RedrawChangedTwoDigitNumber ; @3F74
loc_3F77:
    mov ax, word ptr ds:[ScoreLowWord] ; @3F77
    mov dx, word ptr ds:[ScoreHighWord] ; @3F7A
    cmp dx, 0Fh ; @3F7E
    jb loc_3FA0 ; @3F81
    ja loc_3F93 ; @3F86
    cmp ax, word ptr 0423Fh ; @3F8B
    jbe loc_3FA0 ; @3F8E
loc_3F93:
    mov dx, 0Fh ; @3F93
    mov ax, 0423Fh ; @3F96
    mov word ptr ds:[ScoreLowWord], ax ; @3F99
    mov word ptr ds:[ScoreHighWord], dx ; @3F9C
loc_3FA0:
    mov bx, word ptr ds:[HudCachedScoreLow] ; @3FA0
    mov cx, word ptr ds:[HudCachedScoreHigh] ; @3FA4
    cmp ax, bx ; @3FA8
    jne loc_3FB6 ; @3FAA
    cmp dx, cx ; @3FAF
    je loc_3FCB ; @3FB1
loc_3FB6:
    mov word ptr ds:[HudCachedScoreLow], ax ; @3FB6
    mov word ptr ds:[HudCachedScoreHigh], dx ; @3FB9
    mov bp, word ptr ds:[HudScoreX] ; @3FBD
    mov word ptr ds:[HudDigitCursorX], bp ; @3FC1
    call RedrawChangedSixDigitNumber ; @3FC5
    jmp near ptr loc_40BA ; @3FC8
loc_3FCB:
    mov al, byte ptr ds:[RemainingPassengerJourneys] ; @3FCB
    mov bl, byte ptr ds:[HudCachedLevelCounter] ; @3FCE
    cmp al, bl ; @3FD2
    je loc_3FE7 ; @3FD4
    mov byte ptr ds:[HudCachedLevelCounter], al ; @3FD9
    mov bp, word ptr ds:[HudLevelCounterX] ; @3FDC
    mov word ptr ds:[HudDigitCursorX], bp ; @3FE0
    call RedrawChangedTwoDigitNumber ; @3FE4
loc_3FE7:
    mov ax, word ptr ds:[PlayerCarriedKinds] ; @3FE7
    cmp ax, word ptr ds:[HudCachedPlayerOneIconState] ; @3FEA
    je loc_4013 ; @3FEE
    mov word ptr ds:[HudCachedPlayerOneIconState], ax ; @3FF3
    add ax, word ptr 0B2h ; @3FF6
    mov bx, word ptr ds:[HudPlayerOneIconX] ; @3FF9
    mov cx, 0C1h ; @3FFD
    call DrawTransparentSprite ; @4000
    mov ax, word ptr ds:[PlayerDestinationIcons] ; @4003
    add ax, word ptr 0B7h ; @4006
    mov bx, word ptr ds:[HudPlayerOneDestinationX] ; @4009
    call DrawTransparentSprite ; @400D
    jmp near ptr loc_40BA ; @4010
loc_4013:
    cmp word ptr ds:[PlayerCount], 2 ; @4013
    jne loc_4048 ; @4018
    mov ax, word ptr ds:[PlayerTwoPassengerIconState] ; @401D
    cmp ax, word ptr ds:[HudCachedPlayerTwoIconState] ; @4020
    je loc_4048 ; @4024
    mov word ptr ds:[HudCachedPlayerTwoIconState], ax ; @4029
    add ax, word ptr 0BFh ; @402C
    mov bx, word ptr ds:[HudPlayerTwoIconX] ; @402F
    mov cx, 0C1h ; @4033
    call DrawTransparentSprite ; @4036
    mov ax, word ptr ds:[PlayerTwoDestinationIconIndex] ; @4039
    add ax, word ptr 0C4h ; @403C
    mov bx, word ptr ds:[HudPlayerTwoDestinationX] ; @403F
    call DrawTransparentSprite ; @4043
    jmp short loc_40BA ; @4046
loc_4048:
    mov bp, word ptr ds:[HudFareX] ; @4048
    mov word ptr ds:[HudDigitCursorX], bp ; @404C
    cmp word ptr ds:[PlayerCarriedKinds], 0 ; @4050
    je loc_405E ; @4055
    xor di, di ; @405A
    jmp short loc_4075 ; @405C
loc_405E:
    cmp word ptr ds:[PlayerCount], 2 ; @405E
    jne loc_407B ; @4063
    cmp word ptr ds:[PlayerTwoPassengerIconState], 0 ; @4068
    je loc_407B ; @406D
    mov di, 2 ; @4072
loc_4075:
    mov ax, word ptr [di + PlayerPassengerFares] ; @4075
    jmp short loc_4087 ; @4079
loc_407B:
    cmp byte ptr ds:[HudFareClearPending], 0 ; @407B
    je loc_409E ; @4080
    xor ax, ax ; @4085
loc_4087:
    mov bx, word ptr ds:[HudCachedFare] ; @4087
    cmp ax, bx ; @408B
    je loc_4098 ; @408D
    mov word ptr ds:[HudCachedFare], ax ; @4092
    call RedrawChangedFourDigitNumber ; @4095
loc_4098:
    mov byte ptr ds:[HudFareClearPending], 0 ; @4098
    nop ; @409D
loc_409E:
    mov al, byte ptr ds:[ScoreMultiplier] ; @409E
    mov bl, byte ptr ds:[HudCachedMultiplier] ; @40A1
    cmp al, bl ; @40A5
    je loc_40BA ; @40A7
    mov byte ptr ds:[HudCachedMultiplier], al ; @40AC
    mov bp, word ptr ds:[HudMultiplierX] ; @40AF
    mov word ptr ds:[HudDigitCursorX], bp ; @40B3
    call RedrawChangedTwoDigitNumber ; @40B7
loc_40BA:
    mov ax, word ptr ds:[LevelTimer] ; @40BA
    cmp ax, word ptr 00h ; @40BD
    jge loc_40E2 ; @40C0
    mov word ptr ds:[LevelTimer], 0FFFFh ; @40C5
    cmp word ptr ds:[ScreenFadeStep], 0 ; @40CB
    jl loc_40DF ; @40D0
    mov ax, 0FFFEh ; @40D5
    mov word ptr ds:[ScreenFadeStep], ax ; @40D8
    add word ptr ds:[ScreenFadeLevel], ax ; @40DB
loc_40DF:
    jmp near ptr loc_4171 ; @40DF
loc_40E2:
    push ds ; @40E2
    xor dx, dx ; @40E3
    div word ptr ds:[TimerBarDivisor] ; @40E5
    push ax ; @40E9
    cmp ax, word ptr ds:[CachedTimerBarWidth] ; @40EA
    je loc_416C ; @40EE
    jg loc_4124 ; @40F3
    mov bp, ax ; @40F8
    mov bx, ax ; @40FA
    and bx, 3 ; @40FC
    mov dx, 03C4h ; @40FF
    mov al, 2 ; @4102
    out dx, al ; @4104
    inc dx ; @4105
    mov al, byte ptr [bx + VgaSinglePlaneMasks] ; @4106
    out dx, al ; @410A
    shr bp, 2 ; @410B
    lds si, dword ptr ds:[TimerBarPointer] ; @410E
    add si, bp ; @4112
    xor al, al ; @4114
    mov byte ptr [si], al ; @4116
    mov byte ptr [si + 060h], al ; @4118
    mov byte ptr [si + 0C0h], al ; @411B
    mov al, 0Fh ; @411F
    out dx, al ; @4121
    jmp short loc_416C ; @4122
loc_4124:
    mov di, word ptr ds:[CachedTimerBarWidth] ; @4124
    shr di, 2 ; @4128
    dec ax ; @412B
    mov bp, ax ; @412C
    mov bx, ax ; @412E
    and bx, 3 ; @4130
    mov dx, 03C4h ; @4133
    mov al, 2 ; @4136
    out dx, al ; @4138
    inc dx ; @4139
    mov al, byte ptr [bx + VgaCumulativePlaneMasks] ; @413A
    out dx, al ; @413E
    shr bp, 2 ; @413F
    lds si, dword ptr ds:[TimerBarPointer] ; @4142
    add si, bp ; @4146
    mov al, 032h ; @4148
    mov byte ptr [si], al ; @414A
    mov byte ptr [si + 060h], al ; @414C
    mov byte ptr [si + 0C0h], al ; @414F
    mov al, 0Fh ; @4153
    out dx, al ; @4155
    sub bp, di ; @4156
    je loc_416C ; @4158
    mov al, 032h ; @415D
loc_415F:
    dec si ; @415F
    mov byte ptr [si], al ; @4160
    mov byte ptr [si + 060h], al ; @4162
    mov byte ptr [si + 0C0h], al ; @4165
    dec bp ; @4169
    jne short loc_415F ; @416A
loc_416C:
    pop ax ; @416C
    pop ds ; @416D
    mov word ptr ds:[CachedTimerBarWidth], ax ; @416E
loc_4171:
    ret ; @4171
; CONTRACT (tools/apply.py)
; Draw the 20-column by 16-row byte tile map through the sprite renderer.
; Out: DS becomes the map segment; SI changes by +320 with DF clear or -320 with DF set.
; DL/DH finish at 20/16. The later water lookup uses the resulting live DS.
; END CONTRACT
DrawTileMap:
    lds si, dword ptr ds:[CurrentTileMapPointer] ; @4172
    xor dh, dh ; @4176
loc_4178:
    xor dl, dl ; @4178
loc_417A:
    lodsb ; @417A
    call DrawMapTile ; @417B
    inc dl ; @417E
    cmp dl, 014h ; @4180
    jne short loc_417A ; @4183
    inc dh ; @4185
    cmp dh, 010h ; @4187
    jne short loc_4178 ; @418A
    ret ; @418C
; CONTRACT (tools/apply.py)
; Advance one player rotor/frame cycle according to activity, then draw its current sprite.
; In: DS=DGROUP; BX=0 or 2 selects parallel player fields; activity 27F4 and countdown 27F0.
; Out: consumes min(signed activity,90); a negative countdown adds 200 and advances once.
; Cycle wraps at 0CFC+BX to 0CFA+BX; no catch-up loop for a large negative countdown.
; Effects: signed bounds -32<X<320 and -20<Y<192 gate drawing. BX is preserved; BP is not.
; END CONTRACT
AnimateAndDrawPlayer:
    mov ax, word ptr [bx + PlayerThrustAnimationRate] ; @418D
    cmp ax, word ptr 05Ah ; @4191
    jle loc_419C ; @4194
    mov ax, 05Ah ; @4199
loc_419C:
    sub word ptr [bx + PlayerAnimationCountdowns], ax ; @419C
    mov ax, word ptr [bx + PlayerAnimationCountdowns] ; @41A0
    cmp ax, word ptr 00h ; @41A4
    jge loc_41C9 ; @41A7
    add ax, word ptr 0C8h ; @41AC
    mov word ptr [bx + PlayerAnimationCountdowns], ax ; @41AF
    mov ax, word ptr [bx + PlayerSpriteIds] ; @41B3
    inc ax ; @41B7
    cmp ax, word ptr [bx + PlayerAnimationCycleEnds] ; @41B8
    jl loc_41C5 ; @41BC
    mov ax, word ptr [bx + PlayerAnimationCycleStarts] ; @41C1
loc_41C5:
    mov word ptr [bx + PlayerSpriteIds], ax ; @41C5
loc_41C9:
    mov ax, word ptr [bx + PlayerSpriteIds] ; @41C9
    push bx ; @41CD
    mov cx, word ptr [bx + PlayerYPixels] ; @41CE
    cmp cx, -014h ; @41D2
    jle loc_41FB ; @41D5
    cmp cx, word ptr 0C0h ; @41DA
    jge loc_41FB ; @41DE
    mov bx, word ptr [bx + PlayerPixelX] ; @41E3
    cmp bx, -020h ; @41E7
    jle loc_41FB ; @41EA
    cmp bx, word ptr 0140h ; @41EF
    jge loc_41FB ; @41F3
    call DrawTransparentSprite ; @41F8
loc_41FB:
    pop bx ; @41FB
    ret ; @41FC
; CONTRACT (tools/apply.py)
; Draw a column-major indexed sprite with zero transparency and water palette-bit shading.
; In: AX sprite ID; BX signed pixel X; CX signed pixel Y; DS=DGROUP for water Y 2903.
; Effects: selects one of four pixel banks; directory record is offset,width,height at ID*4.
; Y at/above playfield height selects HUD page and subtracts 192; rows below water OR color 40h.
; No clipping or ID/size checks; address arithmetic wraps to 16 bits; zero dimensions wrap loops.
; Preserves AX,BX,CX,DX,SI,DI,DS,ES; clobbers BP and flags. Requires DF clear; CS scratch is shared.
; VGA Sequencer map mask is forced to 0Fh; prior map mask/selection are not restored.
; END CONTRACT
DrawTransparentSprite:
    push ax ; @41FD
    push bx ; @41FE
    push cx ; @41FF
    push dx ; @4200
    push si ; @4201
    push di ; @4202
    push es ; @4203
    push ds ; @4204
    push ax ; @4205
    mov di, word ptr cs:[DrawPagePointer] ; @4206
    cmp cx, word ptr cs:[PlayfieldHeight] ; @420B
    jl loc_421E ; @4210
    mov di, word ptr cs:[FixedVgaPagePointer] ; @4215
    sub cx, word ptr 0C0h ; @421A
loc_421E:
    mov ax, word ptr ds:[WaterYPixels] ; @421E
    sub ax, cx ; @4221
    mov word ptr cs:[RendererScratchWord], ax ; @4223
    mov ax, bx ; @4227
    sar ax, 1 ; @4229
    sar ax, 1 ; @422B
    add di, ax ; @422D
    mov ax, cx ; @422F
    shl ax, 5 ; @4231
    add di, ax ; @4234
    shl ax, 1 ; @4236
    add di, ax ; @4238
    mov ax, 0A000h ; @423A
    mov es, ax ; @423D
    mov dx, 03C4h ; @423F
    mov al, 2 ; @4242
    out dx, al ; @4244
    inc dx ; @4245
    mov cl, bl ; @4246
    and cl, 3 ; @4248
    mov ah, 1 ; @424B
    shl ah, cl ; @424D
    pop bx ; @424F
    mov word ptr cs:[SpritePlaneStateScratch], ax ; @4250
    mov ax, bx ; @4254
    shl bx, 1 ; @4256
    shl bx, 1 ; @4258
    lds si, dword ptr cs:[SpriteDirectoryPointer] ; @425A
    add si, bx ; @425F
    mov bx, word ptr [si] ; @4261
    mov cx, word ptr [si + 2] ; @4263
    pop ds ; @4266
    push ds ; @4267
    lds si, dword ptr cs:[SpritePixels0To216Pointer] ; @4268
    cmp ax, word ptr 0D9h ; @426D
    jb loc_4294 ; @4270
    lds si, dword ptr cs:[SpritePixels217To297Pointer] ; @4275
    cmp ax, word ptr 012Ah ; @427A
    jb loc_4294 ; @427D
    lds si, dword ptr cs:[SpritePixels298To546Pointer] ; @4282
    cmp ax, word ptr 0223h ; @4287
    jb loc_4294 ; @428A
    lds si, dword ptr cs:[SpritePixels547AndUpPointer] ; @428F
loc_4294:
    add si, bx ; @4294
    mov ax, word ptr cs:[SpritePlaneStateScratch] ; @4296
    mov bp, word ptr cs:[RendererScratchWord] ; @429A
    and bp, bp ; @429F
    js loc_42ED ; @42A1
    mov bl, ch ; @42A6
    xor bh, bh ; @42A8
    cmp bp, bx ; @42AA
    jge loc_431C ; @42AC
loc_42B1:
    mov al, ah ; @42B1
    out dx, al ; @42B3
    push di ; @42B4
    mov bl, ch ; @42B5
    mov bp, word ptr cs:[RendererScratchWord] ; @42B7
loc_42BC:
    lodsb ; @42BC
    or al, al ; @42BD
    je loc_42D0 ; @42BF
    and bp, bp ; @42C4
    jns loc_42CD ; @42C6
    or al, 040h ; @42CB
loc_42CD:
    mov byte ptr es:[di], al ; @42CD
loc_42D0:
    add di, 060h ; @42D0
    dec bp ; @42D3
    dec bl ; @42D4
    jne short loc_42BC ; @42D6
    pop di ; @42D8
    shl ah, 1 ; @42D9
    and ah, 0Fh ; @42DB
    jne loc_42E6 ; @42DE
    inc ah ; @42E3
    inc di ; @42E5
loc_42E6:
    dec cl ; @42E6
    jne short loc_42B1 ; @42E8
    jmp loc_4346 ; @42EA
loc_42ED:
    mov al, ah ; @42ED
    out dx, al ; @42EF
    push di ; @42F0
    mov bl, ch ; @42F1
loc_42F3:
    lodsb ; @42F3
    or al, al ; @42F4
    je loc_4300 ; @42F6
    or al, 040h ; @42FB
    mov byte ptr es:[di], al ; @42FD
loc_4300:
    add di, 060h ; @4300
    dec bl ; @4303
    jne short loc_42F3 ; @4305
    pop di ; @4307
    shl ah, 1 ; @4308
    and ah, 0Fh ; @430A
    jne loc_4315 ; @430D
    inc ah ; @4312
    inc di ; @4314
loc_4315:
    dec cl ; @4315
    jne short loc_42ED ; @4317
    jmp loc_4346 ; @4319
loc_431C:
    mov al, ah ; @431C
    out dx, al ; @431E
    push di ; @431F
    mov bl, ch ; @4320
loc_4322:
    lodsb ; @4322
    or al, al ; @4323
    je loc_432D ; @4325
    mov byte ptr es:[di], al ; @432A
loc_432D:
    add di, 060h ; @432D
    dec bl ; @4330
    jne short loc_4322 ; @4332
    pop di ; @4334
    shl ah, 1 ; @4335
    and ah, 0Fh ; @4337
    jne loc_4342 ; @433A
    inc ah ; @433F
    inc di ; @4341
loc_4342:
    dec cl ; @4342
    jne short loc_431C ; @4344
loc_4346:
    mov al, 0Fh ; @4346
    out dx, al ; @4348
    pop ds ; @4349
    pop es ; @434A
    pop di ; @434B
    pop si ; @434C
    pop dx ; @434D
    pop cx ; @434E
    pop bx ; @434F
    pop ax ; @4350
    ret ; @4351
; CONTRACT (tools/apply.py)
; Cache the player sprite ID and pixel X/Y for later background restoration.
; In: DS=DGROUP; BX=0 or 2 selects current fields 27E8/27D8/27DC.
; Out: writes cached fields 27EC/27E0/27E4; preserves AX and other registers; MOV leaves flags.
; END CONTRACT
CachePlayerDrawState:
    push ax ; @4352
    mov ax, word ptr [bx + PlayerSpriteIds] ; @4353
    mov word ptr [bx + PlayerCachedSpriteIds], ax ; @4357
    mov ax, word ptr [bx + PlayerPixelX] ; @435B
    mov word ptr [bx + PlayerCachedPixelX], ax ; @435F
    mov ax, word ptr [bx + PlayerYPixels] ; @4363
    mov word ptr [bx + PlayerCachedPixelY], ax ; @4367
    pop ax ; @436B
    ret ; @436C
; CONTRACT (tools/apply.py)
; Restore the cached player sprite rectangle, then cache the current draw state.
; In: DS=DGROUP; BX=0 or 2 selects cached sprite and pixel coordinates.
; Effects: signed bounds -32<X<320 and -20<Y<192 gate restoration; cache always advances.
; Preserves AX,BX; CX becomes cached sprite width when restoration runs; DI is clobbered then.
; Calls latch-copy helper in VGA write mode one; does not perform pixel clipping.
; END CONTRACT
RestorePlayerBackground:
    push ax ; @436D
    push bx ; @436E
    mov cx, word ptr [bx + PlayerCachedSpriteIds] ; @436F
    mov ax, word ptr [bx + PlayerCachedPixelX] ; @4373
    cmp ax, word ptr 0FFE0h ; @4377
    jle loc_439F ; @437A
    cmp ax, word ptr 0140h ; @437F
    jge loc_439F ; @4382
    mov bx, word ptr [bx + PlayerCachedPixelY] ; @4387
    cmp bx, -014h ; @438B
    jle loc_439F ; @438E
    cmp bx, word ptr 0C0h ; @4393
    jge loc_439F ; @4397
    call RestoreSpriteBackground ; @439C
loc_439F:
    pop bx ; @439F
    call CachePlayerDrawState ; @43A0
    pop ax ; @43A3
    ret ; @43A4
; CONTRACT (tools/apply.py)
; Restore the full 320-pixel-wide playfield from the background VGA page.
; In: CS playfield height 4600 and page pointers 4610/460C; compatible VGA plane state.
; Effects: calls 43EA at X=0,Y=0,width=320,height=4600; preserves BX,SI and incoming DS/ES.
; Clobbers AX,CX,DX,DI; forces VGA write mode zero afterward and clears DF.
; END CONTRACT
RestorePlayfieldBackground:
    push bx ; @43A5
    push si ; @43A6
    xor ax, ax ; @43A7
    mov bx, ax ; @43A9
    mov cx, 0140h ; @43AB
    mov dx, word ptr cs:[PlayfieldHeight] ; @43AE
    call RestoreBackgroundRectangle ; @43B3
    pop si ; @43B6
    pop bx ; @43B7
    ret ; @43B8
; CONTRACT (tools/apply.py)
; Restore a background rectangle using the width/height of a previous sprite.
; In: AX signed pixel X, BX pixel Y, CX sprite ID; CS directory pointer and page pointers.
; Effects/quirks: LDS loads directory segment but its offset is discarded; lookup uses ID*4.
; Out: CX is sprite width; preserves AX,BX,DX,SI,DS,ES; DI/flags clobbered; DF clear.
; Calls 43EA; assumes directory offset zero and valid nonzero dimensions. No clipping.
; END CONTRACT
RestoreSpriteBackground:
    push dx ; @43B9
    push si ; @43BA
    push ds ; @43BB
    lds si, dword ptr cs:[SpriteDirectoryPointer] ; @43BC
    mov si, cx ; @43C1
    shl si, 2 ; @43C3
    mov cl, byte ptr [si + 2] ; @43C6
    mov dl, byte ptr [si + 3] ; @43C9
    xor ch, ch ; @43CC
    xor dh, dh ; @43CE
    call RestoreBackgroundRectangle ; @43D0
    pop ds ; @43D3
    pop si ; @43D4
    pop dx ; @43D5
    ret ; @43D6
; CONTRACT (tools/apply.py)
; Restore one 16-by-12 pixel tile rectangle from the background VGA page.
; In: AX tile column, BX tile row; CS page pointers; no observed caller (pattern seed).
; Effects: computes X=column*16 and Y=row*12 with 16-bit wrap; falls through into 43EA.
; Out: AX=X, BX=Y, CX=16, DX=12; DI clobbered. VGA write mode forced to zero; DF clear.
; END CONTRACT
RestoreTileBackground:
    shl ax, 4 ; @43D7
    mov cx, bx ; @43DA
    add bx, bx ; @43DC
    add bx, cx ; @43DE
    shl bx, 1 ; @43E0
    shl bx, 1 ; @43E2
    mov cx, 010h ; @43E4
    mov dx, 0Ch ; @43E7
; CONTRACT (tools/apply.py)
; Copy a rectangle from the background VGA page to the draw page using VGA latches.
; In: AX signed pixel X, BX pixel Y, CX width in pixels, DX height in rows; CS page pointers.
; Effects: write mode one; copies ceil(((X & 3)+width)/4) whole VGA bytes per row, stride 96.
; No clipping or edge-plane masking: neighboring pixels in touched byte groups are restored too.
; Height zero wraps through 65536 rows; arithmetic is 16-bit. Sets DF clear before each REP.
; Preserves AX,BX,CX,DX,SI,DS,ES; clobbers DI and flags; forces write mode zero on return.
; END CONTRACT
RestoreBackgroundRectangle:
    push bx ; @43EA
    push cx ; @43EB
    push si ; @43EC
    push es ; @43ED
    push ds ; @43EE
    push ax ; @43EF
    push dx ; @43F0
    mov dx, 03CEh ; @43F1
    mov al, 5 ; @43F4
    out dx, al ; @43F6
    inc dx ; @43F7
    in al, dx ; @43F8
    and al, 0FCh ; @43F9
    inc al ; @43FB
    out dx, al ; @43FD
    pop dx ; @43FE
    pop ax ; @43FF
    push ax ; @4400
    push dx ; @4401
    shl bx, 5 ; @4402
    mov si, bx ; @4405
    shl bx, 1 ; @4407
    add si, bx ; @4409
    mov bx, ax ; @440B
    sar ax, 2 ; @440D
    add si, ax ; @4410
    mov di, si ; @4412
    add si, word ptr cs:[BackgroundPagePointer] ; @4414
    add di, word ptr cs:[DrawPagePointer] ; @4419
    mov ax, 0A000h ; @441E
    mov ds, ax ; @4421
    mov es, ax ; @4423
    mov ax, bx ; @4425
    and ax, word ptr 03h ; @4427
    add ax, cx ; @442A
    add ax, word ptr 03h ; @442C
    shr ax, 1 ; @442F
    shr ax, 1 ; @4431
loc_4433:
    push si ; @4433
    push di ; @4434
    mov cx, ax ; @4435
    cld ; @4437
    rep movsb ; @4438
    pop di ; @443A
    pop si ; @443B
    add si, 060h ; @443C
    add di, 060h ; @443F
    dec dx ; @4442
    jne short loc_4433 ; @4443
    mov dx, 03CFh ; @4445
    in al, dx ; @4448
    and al, 0FCh ; @4449
    out dx, al ; @444B
    pop dx ; @444C
    pop ax ; @444D
    pop ds ; @444E
    pop es ; @444F
    pop si ; @4450
    pop cx ; @4451
    pop bx ; @4452
    ret ; @4453
; CONTRACT (tools/apply.py)
; Draw one byte tile ID at its map column/row in 16-by-12 pixel spacing.
; In: AL sprite ID, DL column, DH row; DS=DGROUP; active sprite/page state.
; Out: AX zero-extended tile ID, DX and SI preserved; BX=X and CX=Y; BP clobbered.
; Effects: calls 41FD without clipping; tile size is placement spacing, not a size validation.
; END CONTRACT
DrawMapTile:
    xor ah, ah ; @4454
    push si ; @4456
    push ax ; @4457
    push dx ; @4458
    mov bl, dl ; @4459
    xor bh, bh ; @445B
    shl bx, 4 ; @445D
    push ax ; @4460
    mov al, 0Ch ; @4461
    mul dh ; @4463
    mov cx, ax ; @4465
    pop ax ; @4467
    call DrawTransparentSprite ; @4468
    pop dx ; @446B
    pop ax ; @446C
    pop si ; @446D
    ret ; @446E
; CONTRACT (tools/apply.py)
; Copy the draw VGA page to the background page for later rectangle/rain restoration.
; In: CS far pointers 460C/4610 and byte count 4602; DF clear; compatible enabled planes.
; Effects: selects GC mode register 5, sets write mode one, performs latch REP MOVSB.
; Out: restores DS; ES=background segment, CX=0, SI/DI advanced; AX,DX clobbered.
; Forces write mode zero afterward; does not restore previous GC mode/selection or set DF.
; END CONTRACT
SaveDrawPageBackground:
    mov dx, 03CEh ; @446F
    mov al, 5 ; @4472
    out dx, al ; @4474
    inc dx ; @4475
    in al, dx ; @4476
    and al, 0FCh ; @4477
    inc al ; @4479
    out dx, al ; @447B
    push ds ; @447C
    lds si, dword ptr cs:[DrawPagePointer] ; @447D
    les di, dword ptr cs:[BackgroundPagePointer] ; @4482
    mov cx, word ptr cs:[VgaPlaneCopyByteCount] ; @4487
    rep movsb ; @448C
    pop ds ; @448E
    mov dx, 03CFh ; @448F
    in al, dx ; @4492
    and al, 0FCh ; @4493
    out dx, al ; @4495
    ret ; @4496
; CONTRACT (tools/apply.py)
; Wait up to CX retraces for a changed raw keyboard scan or any joystick button.
; In: CX retrace count; DS=DGROUP. Samples once first to discard an old keyboard change.
; Out: AX=0039h on timeout/button, else AL=scan and AH=scan XOR previous scan.
; Out: ZF=(remaining CX==0); CX counts down only on the no-input path. DX preserved.
; Clobbers: BX, BP, SI, DI through joystick sampling. CX=0 can wrap to 65535.
; END CONTRACT
WaitForInputOrRetraceTimeout:
    push dx ; @4497
    call PollKeyboardScanChange ; @4498
loc_449B:
    call PollKeyboardScanChange ; @449B
    and ah, ah ; @449E
    jne loc_44B7 ; @44A0
    push cx ; @44A5
    call SampleJoystickAxesAndButtons ; @44A6
    pop cx ; @44A9
    jne loc_44B4 ; @44AA
    call WaitNextVerticalRetrace ; @44AF
    loop loc_449B ; @44B2
loc_44B4:
    mov ax, 039h ; @44B4
loc_44B7:
    and cx, cx ; @44B7
    pop dx ; @44B9
    ret ; @44BA
; CONTRACT (tools/apply.py)
; Wait CX complete vertical-retrace starts; preserve DX.
; Out: CX=0, AL=8; CX=0 on entry waits 65536 times because LOOP decrements first.
; END CONTRACT
WaitRetraceCount:
    push dx ; @44BB
loc_44BC:
    call WaitNextVerticalRetrace ; @44BC
    loop loc_44BC ; @44BF
    pop dx ; @44C1
    ret ; @44C2
; CONTRACT (tools/apply.py)
; Wait until outside vertical retrace, then wait for the next retrace to begin.
; Out: AL=8, DX=03DAh, ZF clear. Falls through to the retrace-active polling entry.
; Effects: unbounded polling of VGA input-status bit 3; no timeout.
; END CONTRACT
WaitNextVerticalRetrace:
    call WaitVerticalRetraceInactive ; @44C3
; CONTRACT (tools/apply.py)
; Poll VGA input status 03DAh bit 3 until vertical retrace is active.
; Out: AL=8, DX=03DAh, ZF clear. Does not require a new rising edge.
; END CONTRACT
WaitVerticalRetraceActive:
    mov dx, 03DAh ; @44C6
loc_44C9:
    in al, dx ; @44C9
    and al, 8 ; @44CA
    je short loc_44C9 ; @44CC
    ret ; @44CE
; CONTRACT (tools/apply.py)
; Wait for vertical retrace to be active, then wait for it to end.
; Out: AL=0, DX=03DAh, ZF set. Unreferenced seed; reachability is not established.
; Effects: falls through to the retrace-inactive polling entry.
; END CONTRACT
WaitThroughVerticalRetrace:
    call WaitVerticalRetraceActive ; @44CF
; CONTRACT (tools/apply.py)
; Poll VGA input status 03DAh bit 3 until vertical retrace is inactive.
; Out: AL=0, DX=03DAh, ZF set; returns immediately if already inactive.
; END CONTRACT
WaitVerticalRetraceInactive:
    mov dx, 03DAh ; @44D2
loc_44D5:
    in al, dx ; @44D5
    and al, 8 ; @44D6
    jne short loc_44D5 ; @44D8
    ret ; @44DA
; CONTRACT (tools/apply.py)
; Discard the current scan change, then poll input once per complete retrace.
; In: DS=DGROUP. Out: AX=nonzero joystick button bits, or AL=scan/AH=scan XOR old.
; Clobbers: BX, CX, DX, BP, SI, DI through sampling; no timeout.
; END CONTRACT
WaitForScanChangeOrJoystickButton:
    call PollKeyboardScanChange ; @44DB
loc_44DE:
    call WaitNextVerticalRetrace ; @44DE
    call SampleJoystickAxesAndButtons ; @44E1
    jne loc_44F0 ; @44E4
    call PollKeyboardScanChange ; @44E9
    and ah, ah ; @44EC
    je short loc_44DE ; @44EE
loc_44F0:
    ret ; @44F0
; CONTRACT (tools/apply.py)
; Snapshot the interrupt's latest raw scan byte and compute its XOR with the old sample.
; In: DS=DGROUP. Out: AL=new scan, AH=new XOR old; stores old/current/change bytes.
; Effects: make/break and prefix bytes are unfiltered; repeated identical scans show no change.
; END CONTRACT
PollKeyboardScanChange:
    mov al, byte ptr ds:[CurrentKeyboardScanCode] ; @44F1
    mov byte ptr ds:[PreviousPolledScanCode], al ; @44F4
    mov al, byte ptr cs:[LatestInterruptScanCode] ; @44F7
    mov byte ptr ds:[CurrentKeyboardScanCode], al ; @44FB
    mov ah, al ; @44FE
    xor ah, byte ptr ds:[PreviousPolledScanCode] ; @4500
    mov byte ptr ds:[KeyboardScanCodeChangeBits], ah ; @4504
    ret ; @4508
; CONTRACT (tools/apply.py)
; Physical one-byte storage for the interrupt scan-code latch.
; END CONTRACT
LatestScanCodeStorage:
    db 00h ; data 4509..450A
; CONTRACT (tools/apply.py)
; Reset scan-sequence candidates, flush the BIOS keyboard queue, and replace INT 09h.
; In: DS=DGROUP; vector at 0097. Out: old vector at 0093, sequence index/state zeroed.
; Effects: DOS AH=35h/25h; ES becomes old vector segment. Ends with STI, not saved IF.
; Effects: no installation guard; callers must restore before reinstalling.
; END CONTRACT
InstallKeyboardSequenceInterrupt:
    xor al, al ; @450A
    mov byte ptr ds:[KeyboardSequenceIndex], al ; @450C
    xor si, si ; @450F
loc_4511:
    cmp byte ptr [si + KeyboardSequenceRecords], 0FFh ; @4511
    je loc_4524 ; @4516
    mov byte ptr [si + KeyboardSequenceCandidateState], al ; @451B
    add si, 6 ; @451F
    jmp short loc_4511 ; @4522
loc_4524:
    cli ; @4524
    mov di, 040h ; @4525
    mov es, di ; @4528
    mov ax, word ptr es:[01Ch] ; @452A
    mov word ptr es:[01Ah], ax ; @452E
    mov ax, 03509h ; @4532
    int 021h ; @4535
    mov word ptr ds:[PreviousKeyboardVector], bx ; @4537
    mov word ptr ds:[PreviousKeyboardVectorSegment], es ; @453B
    push ds ; @453F
    mov ax, 02509h ; @4540
    lds dx, dword ptr ds:[KeyboardHandlerVector] ; @4543
    int 021h ; @4547
    pop ds ; @4549
    sti ; @454A
    ret ; @454B
; CONTRACT (tools/apply.py)
; Restore the saved INT 09h vector, then empty the BIOS keyboard queue.
; In: DS=DGROUP, saved far vector at 0093. DS preserved; ES=0040h on return.
; Effects: DOS AH=25h; queue head becomes tail at 0040:001A/001C. Ends with STI.
; END CONTRACT
RestoreKeyboardInterrupt:
    push ds ; @454C
    mov ax, 02509h ; @454D
    lds dx, dword ptr ds:[PreviousKeyboardVector] ; @4550
    int 021h ; @4554
    pop ds ; @4556
    cli ; @4557
    mov di, 040h ; @4558
    mov es, di ; @455B
    mov ax, word ptr es:[01Ch] ; @455D
    mov word ptr es:[01Ah], ax ; @4561
    sti ; @4565
    ret ; @4566
; CONTRACT (tools/apply.py)
; INT 09h: latch port 60h and match six-byte raw-scan sequence records.
; In: hardware interrupt; loads DGROUP itself. Out: action byte written on completed match.
; Effects: action gated by the sign of the selected player's control word; resets candidates.
; Preserves: AX, BX, SI, DS; sends PIC EOI at 20h and IRETs without chaining old handler.
; Quirks: no BIOS translation/queueing, no port-61h acknowledgement, no E0/E1 special case.
; END CONTRACT
public HandleKeyboardScanInterrupt
HandleKeyboardScanInterrupt:
    push ax ; @4567
    push bx ; @4568
    push si ; @4569
    push ds ; @456A
    mov bx, seg ext_5C09 ; @456B
    mov ds, bx ; @456E
    in al, 060h ; @4570
    mov byte ptr cs:[LatestInterruptScanCode], al ; @4572
    xor bh, bh ; @4576
    xor ah, ah ; @4578
    xor si, si ; @457A
    mov bl, byte ptr ds:[KeyboardSequenceIndex] ; @457C
loc_4580:
    cmp byte ptr [si + KeyboardSequenceCandidateState], 0FFh ; @4580
    je loc_45DF ; @4585
    cmp al, byte ptr [bx + si + KeyboardSequenceRecords] ; @458A
    je loc_459B ; @458E
    mov byte ptr [si + KeyboardSequenceCandidateState], 0FFh ; @4593
    nop ; @4598
    jmp short loc_45DF ; @4599
loc_459B:
    cmp byte ptr [bx + si + KeyboardSequenceNextScan], 0FFh ; @459B
    jne loc_45DD ; @45A0
    mov bl, byte ptr [si + KeyboardSequenceActionIndex] ; @45A5
    and bl, 2 ; @45A9
    test word ptr [bx + PlayerOneControlMode], 0FFFFh ; @45AC
    jns loc_45C3 ; @45B2
    mov bl, byte ptr [si + KeyboardSequenceActionIndex] ; @45B7
    mov al, byte ptr [si + KeyboardSequenceActionValue] ; @45BB
    mov byte ptr [bx + PlayerUpInput], al ; @45BF
loc_45C3:
    xor al, al ; @45C3
    mov byte ptr ds:[KeyboardSequenceIndex], al ; @45C5
    xor si, si ; @45C8
loc_45CA:
    cmp byte ptr [si + KeyboardSequenceRecords], 0FFh ; @45CA
    je loc_45F2 ; @45CF
    mov byte ptr [si + KeyboardSequenceCandidateState], al ; @45D4
    add si, 6 ; @45D8
    jmp short loc_45CA ; @45DB
loc_45DD:
    inc ah ; @45DD
loc_45DF:
    add si, 6 ; @45DF
    cmp byte ptr [si + KeyboardSequenceRecords], 0FFh ; @45E2
    jne short loc_4580 ; @45E7
    test ah, 0FFh ; @45E9
    je short loc_45C3 ; @45EC
    inc byte ptr ds:[KeyboardSequenceIndex] ; @45EE
loc_45F2:
    pop ds ; @45F2
    pop si ; @45F3
    pop bx ; @45F4
    mov al, 020h ; @45F5
    out 020h, al ; @45F7
    pop ax ; @45F9
    iret ; @45FA
byte_data_45FB:
    even ; assembler alignment before CS data
; CONTRACT (tools/apply.py)
; Physical storage starts with sprite/VGA scratch words, followed by far pointers.
; END CONTRACT
VideoScratchAndResourcePointers:
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 0A0h, 00h, 00h, 00h, 0A0h ; data 45FC..460C
    db 00h, 00h, 00h, 0A0h, 00h, 00h, 00h, 0A0h ; data 460C..4614
    dw offset loc_4681
    dw seg GAMESEG
    dw 00h
    dw seg ext_1E1F
    dw 00h
    dw seg ext_37A7
    dw 00h
    dw seg ext_438A
    dw 00h
    dw seg ext_4E83
    dw 00h
    dw seg ext_5B63
    dw 035Ah
    dw seg ext_5B63
    dw 00h
    dw seg ext_0A67
; CONTRACT (tools/apply.py)
; Copy four consecutive indexed pixels into VGA planes 1,2,4,8 at each address.
; In: DS=DGROUP; image pointer 009B; CS draw-page far pointer; plane-byte count at 4602.
; Out: ES:DI advanced in VGA, SI advanced by four times the count; DS preserved.
; Effects: sequencer map mask restored to 0Fh; uses caller's direction flag; CX=0 wraps LOOP.
; END CONTRACT
UploadChunkyImageToVgaPlanes:
    les di, dword ptr cs:[DrawPagePointer] ; @4634
    mov cx, word ptr cs:[VgaPlaneCopyByteCount] ; @4639
    push ds ; @463E
    lds si, dword ptr ds:[DecodedImagePointer] ; @463F
    mov dx, 03C4h ; @4643
    mov al, 2 ; @4646
    out dx, al ; @4648
    inc dx ; @4649
loc_464A:
    mov al, 1 ; @464A
    out dx, al ; @464C
    lodsb ; @464D
    mov byte ptr es:[di], al ; @464E
    mov al, 2 ; @4651
    out dx, al ; @4653
    lodsb ; @4654
    mov byte ptr es:[di], al ; @4655
    mov al, 4 ; @4658
    out dx, al ; @465A
    lodsb ; @465B
    mov byte ptr es:[di], al ; @465C
    mov al, 8 ; @465F
    out dx, al ; @4661
    movsb ; @4662
    loop loc_464A ; @4663
    mov al, 0Fh ; @4665
    out dx, al ; @4667
    pop ds ; @4668
    ret ; @4669
; CONTRACT (tools/apply.py)
; Copy the first 384 palette bytes into both halves of the 768-byte base palette.
; In: DS=DGROUP; source far pointer 00B3 and base destination far pointer 00AB.
; Out: both halves equal source colors 0..127; ES:DI and SI advanced; DS preserved.
; Effects: uses caller's DF; source colors 128..255 are not read.
; END CONTRACT
DuplicateSourcePaletteHalves:
    push ds ; @466A
    les di, dword ptr ds:[BasePalettePointer] ; @466B
    lds si, dword ptr ds:[PaletteSourcePointer] ; @466F
    mov cx, 0C0h ; @4673
loc_4676:
    lodsw ; @4676
    mov word ptr es:[di + 0180h], ax ; @4677
    stosw ; @467C
    loop loc_4676 ; @467D
    pop ds ; @467F
    ret ; @4680
; CONTRACT (tools/apply.py)
; Keep this seed mechanical: 768 zero bytes are the writable base RGB palette.
; Evidence: far pointers at 4614h and DGROUP:00AB, copies at 466Ah/4C81h, reads at 4E39h.
; No call/branch here is established; ADD [BX+SI],AL is a misleading zero-byte disassembly.
; END CONTRACT
public loc_4681
loc_4681:
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4681..4691
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4691..46A1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 46A1..46B1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 46B1..46C1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 46C1..46D1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 46D1..46E1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 46E1..46F1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 46F1..4701
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4701..4711
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4711..4721
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4721..4731
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4731..4741
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4741..4751
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4751..4761
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4761..4771
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4771..4781
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4781..4791
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4791..47A1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 47A1..47B1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 47B1..47C1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 47C1..47D1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 47D1..47E1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 47E1..47F1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 47F1..4801
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4801..4811
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4811..4821
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4821..4831
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4831..4841
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4841..4851
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4851..4861
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4861..4871
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4871..4881
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4881..4891
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4891..48A1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 48A1..48B1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 48B1..48C1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 48C1..48D1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 48D1..48E1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 48E1..48F1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 48F1..4901
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4901..4911
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4911..4921
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4921..4931
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4931..4941
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4941..4951
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4951..4961
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4961..4971
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4971..4981
; CONTRACT (tools/apply.py)
; Keep this seed mechanical: 768 zero bytes are the writable faded RGB palette.
; Evidence: DGROUP:00AF points here and 4E42h writes all 768 scaled components.
; No executable entry is established; do not translate its zero-byte disassembly as a routine.
; END CONTRACT
public loc_4981
loc_4981:
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4981..4991
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4991..49A1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 49A1..49B1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 49B1..49C1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 49C1..49D1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 49D1..49E1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 49E1..49F1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 49F1..4A01
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4A01..4A11
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4A11..4A21
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4A21..4A31
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4A31..4A41
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4A41..4A51
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4A51..4A61
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4A61..4A71
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4A71..4A81
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4A81..4A91
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4A91..4AA1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4AA1..4AB1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4AB1..4AC1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4AC1..4AD1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4AD1..4AE1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4AE1..4AF1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4AF1..4B01
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4B01..4B11
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4B11..4B21
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4B21..4B31
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4B31..4B41
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4B41..4B51
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4B51..4B61
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4B61..4B71
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4B71..4B81
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4B81..4B91
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4B91..4BA1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4BA1..4BB1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4BB1..4BC1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4BC1..4BD1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4BD1..4BE1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4BE1..4BF1
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4BF1..4C01
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4C01..4C11
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4C11..4C21
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4C21..4C31
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4C31..4C41
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4C41..4C51
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4C51..4C61
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4C61..4C71
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h ; data 4C71..4C81
; CONTRACT (tools/apply.py)
; Unpack an ICE picture to the scratch segment, then copy its palette from offset FA00h.
; In: SI=packed resource segment, DS=DGROUP; source starts at offset zero.
; Out: CS base palette receives 768 bytes; scratch retains pixels; DS and CX preserved.
; Effects: leaves ES addressing the palette destination; invalid ICE still copies scratch.
; END CONTRACT
UnpackPictureAndCopyPalette:
    push cx ; @4C81
    push ds ; @4C82
    mov ds, si ; @4C83
    xor si, si ; @4C85
    les di, dword ptr cs:[IceScratchPointer] ; @4C87
    call UnpackIceStream ; @4C8C
    mov si, 0FA00h ; @4C8F
    pop ds ; @4C92
    push ds ; @4C93
    mov cx, es ; @4C94
    les di, dword ptr cs:[PicturePaletteDestination] ; @4C96
    mov ds, cx ; @4C9B
    mov cx, 0180h ; @4C9D
    rep movsw ; @4CA0
    pop ds ; @4CA2
    pop cx ; @4CA3
    ret ; @4CA4
; CONTRACT (tools/apply.py)
; Set ES to the scratch segment and DI=0, then fall through to ICE unpacking.
; In: DS:SI points to ICE header (successful path requires stream based at DS:0000).
; Out: ES=scratch, SI/DI changed by decoder, DF clear; no success status.
; END CONTRACT
UnpackIceToScratch:
    mov di, seg ext_0A67 ; @4CA5
    nop ; @4CA8
    mov es, di ; @4CA9
    xor di, di ; @4CAB
; CONTRACT (tools/apply.py)
; Recognize ICE! and expand the backward byte/bit stream into ES.
; In: DS:SI header, ES destination segment; successful sizes become absolute SI/DI offsets.
; Out: AX/BX/CX/DX/BP/DS/ES preserved, DF clear; SI/DI changed; no success flag.
; Quirks: ignores high size words and supplied DI; packed/unpacked buffers must start at zero.
; Effects: bad magic returns after one/two LODSWs; no length or back-reference validation.
; END CONTRACT
UnpackIceStream:
    push ax ; @4CAD
    push bx ; @4CAE
    push cx ; @4CAF
    push dx ; @4CB0
    push bp ; @4CB1
    push ds ; @4CB2
    push es ; @4CB3
    cld ; @4CB4
    lodsw ; @4CB5
    cmp ax, word ptr 04349h ; @4CB6
    jne loc_4CE0 ; @4CB9
    lodsw ; @4CBE
    cmp ax, word ptr 02145h ; @4CBF
    jne loc_4CE0 ; @4CC2
    add si, 2 ; @4CC7
    lodsw ; @4CCA
    xchg al, ah ; @4CCB
    dec ax ; @4CCD
    push ax ; @4CCE
    add si, 2 ; @4CCF
    lodsw ; @4CD2
    xchg al, ah ; @4CD3
    dec ax ; @4CD5
    mov di, ax ; @4CD6
    pop si ; @4CD8
    std ; @4CD9
    mov ah, byte ptr [si] ; @4CDA
    dec si ; @4CDC
    call DecodeIceLiteralAndMatchStream ; @4CDD
loc_4CE0:
    pop es ; @4CE0
    pop ds ; @4CE1
    pop bp ; @4CE2
    pop dx ; @4CE3
    pop cx ; @4CE4
    pop bx ; @4CE5
    pop ax ; @4CE6
    cld ; @4CE7
    ret ; @4CE8
; CONTRACT (tools/apply.py)
; Decode backward ICE literals and matches until output DI reaches FFFFh.
; In: DS:SI compressed cursor, AH sentinel bit buffer, ES:DI backward output, DF set.
; Effects: body continues at 4D4Bh beyond both bit-helper entries and loops back here.
; Quirks: literal count DX+1; match count BX+2, with overlapping backward copies allowed.
; END CONTRACT
DecodeIceLiteralAndMatchStream:
    call ReadIceBitToCarry ; @4CE9
    jae loc_4D21 ; @4CEC
    xor dx, dx ; @4CF1
    call ReadIceBitToCarry ; @4CF3
    jae loc_4D1D ; @4CF6
    mov bp, offset IceLiteralCodeTablePivot ; @4CFB
    mov bh, 4 ; @4CFE
loc_4D00:
    sub bp, 2 ; @4D00
    mov cx, word ptr cs:[bp] ; @4D03
    call ReadIceBitsToDx ; @4D07
    mov cx, word ptr cs:[bp + 014h] ; @4D0A
    cmp cx, dx ; @4D0E
    jne loc_4D19 ; @4D10
    dec bh ; @4D15
    jns short loc_4D00 ; @4D17
loc_4D19:
    add dx, word ptr cs:[bp + 0Ah] ; @4D19
loc_4D1D:
    movsb ; @4D1D
    dec dx ; @4D1E
    jns short loc_4D1D ; @4D1F
loc_4D21:
    cmp di, -1 ; @4D21
    jne loc_4D4B ; @4D24
    ret ; @4D29
; CONTRACT (tools/apply.py)
; Shift the ICE bit buffer and return the next bit in CF.
; In/Out: AH sentinel buffer; DS:SI points backward; empty buffer refills and decrements SI.
; Preserves: AL, BX, CX, DX, BP, DI, DS, ES. CF is consumed immediately by callers.
; END CONTRACT
ReadIceBitToCarry:
    shl ah, 1 ; @4D2A
    jne loc_4D36 ; @4D2C
    mov ah, byte ptr [si] ; @4D31
    dec si ; @4D33
    rcl ah, 1 ; @4D34
loc_4D36:
    ret ; @4D36
; CONTRACT (tools/apply.py)
; Read CX+1 bits from the backward ICE stream into DX, most significant bit first.
; In/Out: AH sentinel buffer and DS:SI cursor. Out: CX=FFFFh, DX decoded unsigned bits.
; Quirks: signed JNS after DEC means CX=0 reads one bit; normal callers supply 0..14.
; Effects: returns at 4D4Ah; the following match decoder is a different shared body.
; END CONTRACT
ReadIceBitsToDx:
    xor dx, dx ; @4D37
loc_4D39:
    shl ah, 1 ; @4D39
    jne loc_4D45 ; @4D3B
    mov ah, byte ptr [si] ; @4D40
    dec si ; @4D42
    rcl ah, 1 ; @4D43
loc_4D45:
    rcl dx, 1 ; @4D45
    dec cx ; @4D47
    jns short loc_4D39 ; @4D48
    ret ; @4D4A
loc_4D4B:
    mov bp, 3 ; @4D4B
loc_4D4E:
    call ReadIceBitToCarry ; @4D4E
    jae loc_4D59 ; @4D51
    dec bp ; @4D56
    jns short loc_4D4E ; @4D57
loc_4D59:
    xor bx, bx ; @4D59
    xor dx, dx ; @4D5B
    push ax ; @4D5D
    mov al, byte ptr cs:[bp + IceMatchLengthBitCountsMinusOne] ; @4D5E
    cbw ; @4D63
    mov cx, ax ; @4D64
    pop ax ; @4D66
    and cx, 0FFFFh ; @4D67
    js loc_4D72 ; @4D6A
    call ReadIceBitsToDx ; @4D6F
loc_4D72:
    mov bl, byte ptr cs:[bp + IceMatchLengthBiases] ; @4D72
    add bx, dx ; @4D77
    je loc_4DAB ; @4D79
    mov bp, 1 ; @4D7E
loc_4D81:
    call ReadIceBitToCarry ; @4D81
    jae loc_4D8C ; @4D84
    dec bp ; @4D89
    jns short loc_4D81 ; @4D8A
loc_4D8C:
    xor dx, dx ; @4D8C
    push ax ; @4D8E
    mov al, byte ptr cs:[bp + IceMatchOffsetBitCountsMinusOne] ; @4D8F
    cbw ; @4D94
    mov cx, ax ; @4D95
    pop ax ; @4D97
    call ReadIceBitsToDx ; @4D98
    shl bp, 1 ; @4D9B
    add dx, word ptr cs:[bp + IceMatchOffsetBiases] ; @4D9D
    jns loc_4DC6 ; @4DA2
    sub dx, bx ; @4DA7
    jmp short loc_4DC6 ; @4DA9
loc_4DAB:
    xor dx, dx ; @4DAB
    mov cx, 5 ; @4DAD
    mov bp, 0FFFFh ; @4DB0
    call ReadIceBitToCarry ; @4DB3
    jae loc_4DC1 ; @4DB6
    mov cx, 8 ; @4DBB
    mov bp, 03Fh ; @4DBE
loc_4DC1:
    call ReadIceBitsToDx ; @4DC1
    add dx, bp ; @4DC4
loc_4DC6:
    push si ; @4DC6
    lea si, [bx + di + 2] ; @4DC7
    add si, dx ; @4DCA
    mov al, byte ptr es:[si] ; @4DCC
    dec si ; @4DCF
    stosb ; @4DD0
loc_4DD1:
    mov al, byte ptr es:[si] ; @4DD1
    dec si ; @4DD4
    stosb ; @4DD5
    dec bx ; @4DD6
    jns short loc_4DD1 ; @4DD7
    pop si ; @4DD9
    jmp near ptr DecodeIceLiteralAndMatchStream ; @4DDA
; CONTRACT (tools/apply.py)
; Physical literal-code and match-code tables; packed mixed byte/word fields.
; END CONTRACT
IceDecoderTables:
    db 0Eh, 00h, 07h, 00h, 02h, 00h, 01h, 00h, 01h, 00h, 0Dh, 01h, 0Eh, 00h, 07h, 00h ; data 4DDD..4DED
    db 04h, 00h, 01h, 00h, 0FFh, 07Fh, 0FFh, 00h, 07h, 00h, 03h, 00h, 03h, 00h, 00h, 00h ; data 4DED..4DFD
    db 00h, 00h, 00h, 00h, 00h, 00h, 00h, 00h, 09h, 01h, 00h, 0FFh, 0FFh, 08h, 04h, 02h ; data 4DFD..4E0D
    db 01h, 00h, 0Bh, 04h, 07h, 00h, 01Fh, 01h, 0FFh, 0FFh, 01Fh, 00h ; data 4E0D..4E19
; CONTRACT (tools/apply.py)
; Scale/upload the palette at factors 0,4,...,256, one complete retrace per factor.
; In: DS=DGROUP. Out: CX=260; colors 0..216 reach the base palette values.
; Effects: factors use 8.8 multiplication; uploads force interrupts enabled.
; END CONTRACT
FadePaletteIn:
    xor cx, cx ; @4E19
loc_4E1B:
    call ScaleAndUploadFadedPalette ; @4E1B
    add cx, 4 ; @4E1E
    cmp cx, word ptr 0100h ; @4E21
    jbe short loc_4E1B ; @4E25
    ret ; @4E27
; CONTRACT (tools/apply.py)
; Scale/upload the palette at factors 256,252,...,0, one complete retrace per factor.
; In: DS=DGROUP. Preserves CX; colors 0..216 become black; uploads end with STI.
; END CONTRACT
FadePaletteOut:
    push cx ; @4E28
    mov cx, 0100h ; @4E29
loc_4E2C:
    call ScaleAndUploadFadedPalette ; @4E2C
    sub cx, 4 ; @4E2F
    jns short loc_4E2C ; @4E32
    pop cx ; @4E34
    ret ; @4E35
; CONTRACT (tools/apply.py)
; Compute all 768 faded component bytes, then upload colors 0..216 after a retrace.
; In: CX factor (normally 0..256), DS=DGROUP. Stores AH of each unsigned component*CX.
; Out: CX/DS preserved, ES:DI points to faded palette. Tail-jumps to range uploader 4E72h.
; Quirks: no saturation; out-of-range factors wrap through AH. Ends with interrupts enabled.
; END CONTRACT
ScaleAndUploadFadedPalette:
    mov bx, 02FFh ; @4E36
loc_4E39:
    mov al, byte ptr cs:[bx + BaseRgbPalette] ; @4E39
    xor ah, ah ; @4E3E
    mul cx ; @4E40
    mov byte ptr cs:[bx + FadedRgbPalette], ah ; @4E42
    dec bx ; @4E47
    jns short loc_4E39 ; @4E48
    les di, dword ptr ds:[FadedPalettePointer] ; @4E4A
    mov bx, 0D800h ; @4E4E
    call WaitNextVerticalRetrace ; @4E51
    jmp loc_4E72 ; @4E54
; CONTRACT (tools/apply.py)
; INT 24h handler: return DOS critical-error action AL=3 (fail the system call).
; Effects: executes STI before IRET; saved interrupt flags are then restored by IRET.
; END CONTRACT
FailDosCriticalError:
    sti ; @4E57
    mov al, 3 ; @4E58
    iret ; @4E5A
; CONTRACT (tools/apply.py)
; Install CS:4E57h as INT 24h using DOS AH=25h.
; Preserves DS. Old vector is neither saved nor restored by this code.
; END CONTRACT
InstallDosCriticalErrorFailHandler:
    push ds ; @4E5B
    push cs ; @4E5C
    pop ds ; @4E5D
    mov ax, 02524h ; @4E5E
    mov dx, offset FailDosCriticalError ; @4E61
    int 021h ; @4E64
    pop ds ; @4E66
    ret ; @4E67
; CONTRACT (tools/apply.py)
; Wait for a complete retrace and upload all 256 base-palette RGB triples to VGA DAC.
; In: DS=DGROUP, base palette pointer 00AB. Falls through to range uploader 4E72h.
; Effects: DS/CX preserved, SI advanced, ES:DI=base palette; CLI/STI forces IF=1.
; Reachability: unreferenced seed; purpose follows its body, not an identified caller.
; END CONTRACT
UploadBasePalette:
    les di, dword ptr ds:[BasePalettePointer] ; @4E68
    call WaitNextVerticalRetrace ; @4E6C
    mov bx, 0FF00h ; @4E6F
loc_4E72:
    push cx ; @4E72
    push ds ; @4E73
    push es ; @4E74
    pop ds ; @4E75
    push di ; @4E76
    pop si ; @4E77
    xor ah, ah ; @4E78
    xor ch, ch ; @4E7A
    cli ; @4E7C
    mov dx, 03C8h ; @4E7D
    mov al, bl ; @4E80
    out dx, al ; @4E82
    inc dx ; @4E83
    add si, ax ; @4E84
    add si, ax ; @4E86
    add si, ax ; @4E88
    mov cl, bh ; @4E8A
    sub cl, bl ; @4E8C
    inc cx ; @4E8E
loc_4E8F:
    lodsb ; @4E8F
    out dx, al ; @4E90
    lodsb ; @4E91
    out dx, al ; @4E92
    lodsb ; @4E93
    out dx, al ; @4E94
    loop loc_4E8F ; @4E95
    sti ; @4E97
    pop ds ; @4E98
    pop cx ; @4E99
    ret ; @4E9A
; CONTRACT (tools/apply.py)
; Set all 256 VGA DAC colors to black in eight groups of 32 colors.
; Effects: waits a complete retrace per group; CLI/STI around each group forces IF=1.
; Out: CX=0, DX=03C9h; no palette memory is modified.
; END CONTRACT
BlackenVgaPalette:
    mov dx, 03C8h ; @4E9B
    xor al, al ; @4E9E
    out dx, al ; @4EA0
    inc dx ; @4EA1
    mov ch, 8 ; @4EA2
loc_4EA4:
    push dx ; @4EA4
    call WaitNextVerticalRetrace ; @4EA5
    pop dx ; @4EA8
    cli ; @4EA9
    xor al, al ; @4EAA
    mov cl, 020h ; @4EAC
loc_4EAE:
    out dx, al ; @4EAE
    out dx, al ; @4EAF
    out dx, al ; @4EB0
    dec cl ; @4EB1
    jne short loc_4EAE ; @4EB3
    sti ; @4EB5
    dec ch ; @4EB6
    jne short loc_4EA4 ; @4EB8
    ret ; @4EBA
; CONTRACT (tools/apply.py)
; Swap the display/draw page offsets and program the new CRTC start address.
; In: CS words 4608h and 460Ch. Preserves AX, BX, DX.
; Effects: waits for retrace to be inactive, not for a new rising edge; ports 03D4h/03D5h.
; Boundary: returns at 4EE5h; 4EE6h is a separate process-exit target, not a fallthrough.
; END CONTRACT
SwapAndDisplayVgaPage:
    push ax ; @4EBB
    push bx ; @4EBC
    push dx ; @4EBD
    mov bx, word ptr cs:[DisplayedVgaPagePointer] ; @4EBE
    xchg word ptr cs:[DrawPagePointer], bx ; @4EC3
    mov word ptr cs:[DisplayedVgaPagePointer], bx ; @4EC8
    call WaitVerticalRetraceInactive ; @4ECD
    mov dx, 03D4h ; @4ED0
    mov al, 0Ch ; @4ED3
    out dx, al ; @4ED5
    inc dx ; @4ED6
    mov al, bh ; @4ED7
    out dx, al ; @4ED9
    dec dx ; @4EDA
    mov al, 0Dh ; @4EDB
    out dx, al ; @4EDD
    inc dx ; @4EDE
    mov al, bl ; @4EDF
    out dx, al ; @4EE1
    pop dx ; @4EE2
    pop bx ; @4EE3
    pop ax ; @4EE4
    ret ; @4EE5
loc_4EE6:
    call FadeAndShutdownSound ; @4EE6
    xor ah, ah ; @4EE9
    mov al, byte ptr ds:[SavedBiosVideoMode] ; @4EEB
    int 010h ; @4EEE
    call RestoreKeyboardInterrupt ; @4EF0
    mov ah, 04Ch ; @4EF3
    int 021h ; @4EF5
; CONTRACT (tools/apply.py)
; Physical eight-byte storage for four ADD/ADC random-state words.
; END CONTRACT
RandomStateStorage:
    db 03h, 07Fh, 034h, 081h, 0BCh, 048h, 047h, 023h ; data 4EF7..4EFF
; CONTRACT (tools/apply.py)
; Read DOS time AH=2Ch and replace only the high byte of the first random-state word.
; Out: CS:4EF8h=DH (seconds), other random-state bytes unchanged; DOS time registers exposed.
; END CONTRACT
SeedRandomFromDosSeconds:
    mov ah, 02Ch ; @4EFF
    int 021h ; @4F01
    mov byte ptr cs:[RandomSecondsSeedByte], dh ; @4F03
    ret ; @4F08
; CONTRACT (tools/apply.py)
; Advance four 16-bit random-state words and scale the new first word below input AX.
; In: AX=unsigned exclusive upper bound. Out: AX=high word of state0*bound.
; Preserves CX/DX. Bound zero returns zero but still changes state.
; Quirks: ADD/ADC chain uses input AX and exact carries, including final carry into state0.
; END CONTRACT
NextRandomBelowAx:
    push cx ; @4F09
    push dx ; @4F0A
    push ax ; @4F0B
    add ax, word ptr cs:[RandomStateWord0] ; @4F0C
    mov dx, word ptr cs:[RandomStateWord1] ; @4F11
    adc dx, ax ; @4F16
    mov word ptr cs:[RandomStateWord1], dx ; @4F18
    mov cx, word ptr cs:[RandomStateWord2] ; @4F1D
    adc cx, dx ; @4F22
    mov word ptr cs:[RandomStateWord2], cx ; @4F24
    mov dx, word ptr cs:[RandomStateWord3] ; @4F29
    adc dx, cx ; @4F2E
    mov word ptr cs:[RandomStateWord3], dx ; @4F30
    adc ax, dx ; @4F35
    mov word ptr cs:[RandomStateWord0], ax ; @4F37
    pop cx ; @4F3B
    mul cx ; @4F3C
    mov ax, dx ; @4F3E
    pop dx ; @4F40
    pop cx ; @4F41
    ret ; @4F42
; CONTRACT (tools/apply.py)
; Call the C sound initializer with device bits=1 (AdLib only), removing its word argument.
; Out: AX=initializer device mask; initialization can detect no device. Far cdecl call.
; END CONTRACT
InitializeAdLibSound:
    push 1 ; @4F43
    call far ptr _InitializeSoundSystem ; @4F45
    add sp, 2 ; @4F4A
    ret ; @4F4D
; CONTRACT (tools/apply.py)
; Call C main-track stop/fade with 11h, then call C sound shutdown.
; Effects: far cdecl calls; fade can busy-wait for interrupt-driven completion.
; END CONTRACT
FadeAndShutdownSound:
    push 011h ; @4F4E
    call far ptr _StopMusicTrack ; @4F50
    add sp, 2 ; @4F55
    call far ptr _ShutdownSoundSystem ; @4F58
    ret ; @4F5D
; CONTRACT (tools/apply.py)
; Save BIOS video mode, reject 8086-style FLAGS, install fail-on-error, and read scores.
; Effects: seed RNG, BIOS mode 13h, unchain VGA, install keyboard, calibrate sticks, init sound.
; Out: falls through to clear all VGA planes. Requires DS=DGROUP; setup changes many registers.
; Quirks: FLAGS probe clears flags/IF; rejection jumps to shared DOS process-exit path.
; END CONTRACT
InitializeDosVideoInputAndSound:
    mov ah, 0Fh ; @4F5E
    int 010h ; @4F60
    and al, 07Fh ; @4F62
    mov byte ptr ds:[SavedBiosVideoMode], al ; @4F64
    xor ax, ax ; @4F67
    push ax ; @4F69
    popf ; @4F6A
    pushf ; @4F6B
    pop ax ; @4F6C
    and ax, word ptr 0F000h ; @4F6D
    cmp ax, word ptr 0F000h ; @4F70
    jne loc_4F7B ; @4F73
    jmp near ptr loc_4EE6 ; @4F78
loc_4F7B:
    call InstallDosCriticalErrorFailHandler ; @4F7B
    call LoadHighScores ; @4F7E
    call SeedRandomFromDosSeconds ; @4F81
    cld ; @4F84
    mov ax, 013h ; @4F85
    int 010h ; @4F88
    call ConfigureVgaPicturePages ; @4F8A
    call InstallKeyboardSequenceInterrupt ; @4F8D
    call DetectAndCalibrateJoysticks ; @4F90
    call InitializeAdLibSound ; @4F93
; CONTRACT (tools/apply.py)
; Enable all four VGA map-mask bits and clear the 64-KiB A000h aperture with STOSW.
; Out: ES=A000h, AX=0, CX=0, DI wraps to 0 for DF=0; DS preserved.
; Effects: uses caller's DF; all planes receive the writes.
; END CONTRACT
ClearAllVgaPlanes:
    call EnableAllVgaWritePlanes ; @4F96
    mov di, 0A000h ; @4F99
    mov es, di ; @4F9C
    xor di, di ; @4F9E
    mov ax, di ; @4FA0
    mov cx, 08000h ; @4FA2
    rep stosw ; @4FA5
    ret ; @4FA7
; CONTRACT (tools/apply.py)
; Select VGA sequencer map-mask register 2 and write 0Fh to enable all four planes.
; Out: AL=0Fh, DX=03C5h; other general registers untouched.
; END CONTRACT
EnableAllVgaWritePlanes:
    mov dx, 03C4h ; @4FA8
    mov al, 2 ; @4FAB
    out dx, al ; @4FAD
    inc dx ; @4FAE
    mov al, 0Fh ; @4FAF
    out dx, al ; @4FB1
    ret ; @4FB2
; CONTRACT (tools/apply.py)
; Configure unchained byte-addressed VGA with 80 bytes per plane row and line compare 399.
; Out: CS height=200, plane count=3E80h, fixed page=0, display/draw=3E80h/0 after swap.
; Effects: third page=7D00h; blackens DAC, clears all planes, tail-jumps to page flip.
; Quirks: clears chain-4, CRTC doubleword mode; enables byte mode and split-screen panning.
; END CONTRACT
ConfigureVgaPicturePages:
    mov word ptr cs:[PlayfieldHeight], 0C8h ; @4FB3
    mov word ptr cs:[VgaPlaneCopyByteCount], 03E80h ; @4FBA
    call BlackenVgaPalette ; @4FC1
    mov dx, 03C4h ; @4FC4
    mov al, 4 ; @4FC7
    out dx, al ; @4FC9
    inc dx ; @4FCA
    in al, dx ; @4FCB
    and al, 0F7h ; @4FCC
    out dx, al ; @4FCE
    mov dx, 03D4h ; @4FCF
    mov al, 014h ; @4FD2
    out dx, al ; @4FD4
    inc dx ; @4FD5
    in al, dx ; @4FD6
    and al, 0BFh ; @4FD7
    out dx, al ; @4FD9
    dec dx ; @4FDA
    mov al, 017h ; @4FDB
    out dx, al ; @4FDD
    inc dx ; @4FDE
    in al, dx ; @4FDF
    or al, 040h ; @4FE0
    out dx, al ; @4FE2
    dec dx ; @4FE3
    mov al, 013h ; @4FE4
    out dx, al ; @4FE6
    inc dx ; @4FE7
    mov al, 028h ; @4FE8
    out dx, al ; @4FEA
    mov dx, 03D4h ; @4FEB
    mov al, 018h ; @4FEE
    out dx, al ; @4FF0
    inc dx ; @4FF1
    mov al, 08Fh ; @4FF2
    out dx, al ; @4FF4
    dec dx ; @4FF5
    mov al, 7 ; @4FF6
    out dx, al ; @4FF8
    inc dx ; @4FF9
    in al, dx ; @4FFA
    and al, 0EFh ; @4FFB
    or al, 010h ; @4FFD
    out dx, al ; @4FFF
    dec dx ; @5000
    mov al, 9 ; @5001
    out dx, al ; @5003
    inc dx ; @5004
    in al, dx ; @5005
    and al, 0BFh ; @5006
    or al, 0 ; @5008
    out dx, al ; @500A
    call WaitNextVerticalRetrace ; @500B
    mov dx, 03C0h ; @500E
    mov al, 010h ; @5011
    out dx, al ; @5013
    inc dx ; @5014
    in al, dx ; @5015
    or al, 020h ; @5016
    dec dx ; @5018
    out dx, al ; @5019
    mov al, 020h ; @501A
    out dx, al ; @501C
    xor ax, ax ; @501D
    mov word ptr cs:[FixedVgaPagePointer], ax ; @501F
    mov word ptr cs:[DisplayedVgaPagePointer], ax ; @5023
    mov word ptr cs:[DrawPagePointer], 03E80h ; @5027
    mov word ptr cs:[BackgroundPagePointer], 07D00h ; @502E
    call ClearAllVgaPlanes ; @5035
    jmp near ptr SwapAndDisplayVgaPage ; @5038
; CONTRACT (tools/apply.py)
; Configure unchained byte-addressed VGA with 96 bytes per plane row and line compare 383.
; Out: CS height=192, plane count=4800h, fixed page=0, display/draw=5A08h/0A88h after swap.
; Effects: third page=A988h; blackens DAC, clears all planes, tail-jumps to page flip.
; Quirks: page gaps are 4F80h, not the 4800h plane copy count; retain the 0A88h base.
; END CONTRACT
ConfigureVgaGameplayPages:
    mov word ptr cs:[PlayfieldHeight], 0C0h ; @503B
    mov word ptr cs:[VgaPlaneCopyByteCount], 04800h ; @5042
    call BlackenVgaPalette ; @5049
    mov dx, 03C4h ; @504C
    mov al, 4 ; @504F
    out dx, al ; @5051
    inc dx ; @5052
    in al, dx ; @5053
    and al, 0F7h ; @5054
    out dx, al ; @5056
    mov dx, 03D4h ; @5057
    mov al, 014h ; @505A
    out dx, al ; @505C
    inc dx ; @505D
    in al, dx ; @505E
    and al, 0BFh ; @505F
    out dx, al ; @5061
    dec dx ; @5062
    mov al, 017h ; @5063
    out dx, al ; @5065
    inc dx ; @5066
    in al, dx ; @5067
    or al, 040h ; @5068
    out dx, al ; @506A
    dec dx ; @506B
    mov al, 013h ; @506C
    out dx, al ; @506E
    inc dx ; @506F
    mov al, 030h ; @5070
    out dx, al ; @5072
    mov dx, 03D4h ; @5073
    mov al, 018h ; @5076
    out dx, al ; @5078
    inc dx ; @5079
    mov al, 07Fh ; @507A
    out dx, al ; @507C
    dec dx ; @507D
    mov al, 7 ; @507E
    out dx, al ; @5080
    inc dx ; @5081
    in al, dx ; @5082
    and al, 0EFh ; @5083
    or al, 010h ; @5085
    out dx, al ; @5087
    dec dx ; @5088
    mov al, 9 ; @5089
    out dx, al ; @508B
    inc dx ; @508C
    in al, dx ; @508D
    and al, 0BFh ; @508E
    or al, 0 ; @5090
    out dx, al ; @5092
    call WaitNextVerticalRetrace ; @5093
    mov dx, 03C0h ; @5096
    mov al, 010h ; @5099
    out dx, al ; @509B
    inc dx ; @509C
    in al, dx ; @509D
    or al, 020h ; @509E
    dec dx ; @50A0
    out dx, al ; @50A1
    mov al, 020h ; @50A2
    out dx, al ; @50A4
    xor ax, ax ; @50A5
    mov word ptr cs:[FixedVgaPagePointer], ax ; @50A7
    add ax, word ptr 0A88h ; @50AB
    mov word ptr cs:[DisplayedVgaPagePointer], ax ; @50AE
    add ax, word ptr 04F80h ; @50B2
    mov word ptr cs:[DrawPagePointer], ax ; @50B5
    add ax, word ptr 04F80h ; @50B9
    mov word ptr cs:[BackgroundPagePointer], ax ; @50BC
    call ClearAllVgaPlanes ; @50C0
    jmp near ptr SwapAndDisplayVgaPage ; @50C3
; CONTRACT (tools/apply.py)
; Probe port 201h axis pairs after a 1600h-iteration discharge delay and calibrate centers.
; In: DS=DGROUP; sticks must be centered. Out: presence flags, control selectors, axis thresholds.
; Effects: thresholds are ceil(center/2), center+floor(center/2); timeout=max(2*each center).
; Quirks: 16-bit wraps, unsigned max; undetected-stick thresholds can stay stale. Ends with STI.
; END CONTRACT
DetectAndCalibrateJoysticks:
    cli ; @50C6
    sub ax, ax ; @50C7
    mov word ptr ds:[JoystickPresentFlags], ax ; @50C9
    mov word ptr ds:[SecondJoystickPresent], ax ; @50CC
    mov byte ptr ds:[JoystickEnabledAxisMask], al ; @50CF
    mov word ptr ds:[JoystickSampleLoopLimit], 0FFFFh ; @50D2
    mov word ptr ds:[ds_3321], ax ; @50D8
    mov word ptr ds:[ds_3325], ax ; @50DB
    mov word ptr ds:[ds_3323], ax ; @50DE
    mov word ptr ds:[ds_3327], ax ; @50E1
    mov word ptr ds:[FirstJoystickXDoubleCenter], ax ; @50E4
    mov word ptr ds:[FirstJoystickYDoubleCenter], ax ; @50E7
    mov word ptr ds:[SecondJoystickXDoubleCenter], ax ; @50EA
    mov word ptr ds:[SecondJoystickYDoubleCenter], ax ; @50ED
    mov dx, 0201h ; @50F0
    out dx, al ; @50F3
    mov cx, 01600h ; @50F4
loc_50F7:
    dec cx ; @50F7
    je loc_50FF ; @50F8
    jmp short loc_50F7 ; @50FD
loc_50FF:
    mov dx, 0201h ; @50FF
    in al, dx ; @5102
    push ax ; @5103
    test al, 3 ; @5104
    jne loc_515B ; @5106
    mov word ptr ds:[JoystickPresentFlags], 0FFFFh ; @510B
    mov word ptr ds:[PlayerOneControlMode], 0 ; @5111
    or byte ptr ds:[JoystickEnabledAxisMask], 3 ; @5117
    call SampleJoystickAxesAndButtons ; @511C
    mov ax, word ptr ds:[FirstJoystickXCount] ; @511F
    mov bx, word ptr ds:[FirstJoystickYCount] ; @5122
    shl ax, 1 ; @5126
    shl bx, 1 ; @5128
    mov word ptr ds:[FirstJoystickXDoubleCenter], ax ; @512A
    mov word ptr ds:[FirstJoystickYDoubleCenter], bx ; @512D
    mov ax, word ptr ds:[FirstJoystickXCount] ; @5131
    mov bx, ax ; @5134
    shr ax, 1 ; @5136
    sub bx, ax ; @5138
    mov word ptr ds:[JoystickLeftThresholds], bx ; @513A
    add bx, ax ; @513E
    add bx, ax ; @5140
    mov word ptr ds:[JoystickRightThresholds], bx ; @5142
    mov ax, word ptr ds:[FirstJoystickYCount] ; @5146
    mov bx, ax ; @5149
    shr ax, 1 ; @514B
    sub bx, ax ; @514D
    mov word ptr ds:[JoystickUpThresholds], bx ; @514F
    add bx, ax ; @5153
    add bx, ax ; @5155
    mov word ptr ds:[JoystickDownThresholds], bx ; @5157
loc_515B:
    pop ax ; @515B
    test al, 0Ch ; @515C
    jne loc_51C0 ; @515E
    mov word ptr ds:[SecondJoystickPresent], 0FFFFh ; @5163
    mov word ptr ds:[PlayerTwoControlMode], 1 ; @5169
    or byte ptr ds:[JoystickEnabledAxisMask], 0Ch ; @516F
    mov cx, 01600h ; @5174
loc_5177:
    dec cx ; @5177
    je loc_517F ; @5178
    jmp short loc_5177 ; @517D
loc_517F:
    call SampleJoystickAxesAndButtons ; @517F
    mov cx, word ptr ds:[SecondJoystickXCount] ; @5182
    mov dx, word ptr ds:[SecondJoystickYCount] ; @5186
    shl cx, 1 ; @518A
    shl dx, 1 ; @518C
    mov word ptr ds:[SecondJoystickXDoubleCenter], cx ; @518E
    mov word ptr ds:[SecondJoystickYDoubleCenter], dx ; @5192
    mov ax, word ptr ds:[SecondJoystickXCount] ; @5196
    mov bx, ax ; @5199
    shr ax, 1 ; @519B
    sub bx, ax ; @519D
    mov word ptr ds:[SecondJoystickXLowThreshold], bx ; @519F
    add bx, ax ; @51A3
    add bx, ax ; @51A5
    mov word ptr ds:[SecondJoystickXHighThreshold], bx ; @51A7
    mov ax, word ptr ds:[SecondJoystickYCount] ; @51AB
    mov bx, ax ; @51AE
    shr ax, 1 ; @51B0
    sub bx, ax ; @51B2
    mov word ptr ds:[SecondJoystickYLowThreshold], bx ; @51B4
    add bx, ax ; @51B8
    add bx, ax ; @51BA
    mov word ptr ds:[SecondJoystickYHighThreshold], bx ; @51BC
loc_51C0:
    mov ax, word ptr ds:[FirstJoystickXDoubleCenter] ; @51C0
    cmp ax, word ptr ds:[FirstJoystickYDoubleCenter] ; @51C3
    jae loc_51CF ; @51C7
    mov ax, word ptr ds:[FirstJoystickYDoubleCenter] ; @51CC
loc_51CF:
    cmp ax, word ptr ds:[SecondJoystickXDoubleCenter] ; @51CF
    jae loc_51DB ; @51D3
    mov ax, word ptr ds:[SecondJoystickXDoubleCenter] ; @51D8
loc_51DB:
    cmp ax, word ptr ds:[SecondJoystickYDoubleCenter] ; @51DB
    jae loc_51E7 ; @51DF
    mov ax, word ptr ds:[SecondJoystickYDoubleCenter] ; @51E4
loc_51E7:
    mov word ptr ds:[JoystickSampleLoopLimit], ax ; @51E7
    sti ; @51EA
    ret ; @51EB
; CONTRACT (tools/apply.py)
; Trigger port 201h and time enabled falling axis bits using a software countdown.
; In: DS=DGROUP; enabled low-nibble mask and sample-loop limit.
; Out: four axis counts, two active-high button words; AX=button OR, ZF set iff none pressed.
; Clobbers: BX, CX, DX, BP, SI, DI. Saves/restores FLAGS around timing, then changes arithmetic
; flags.
; Quirks: buttons sampled by two separate INs even if no axes enabled; zero limit can wrap LOOP.
; END CONTRACT
SampleJoystickAxesAndButtons:
    pushf ; @51EC
    cli ; @51ED
    mov dx, 0201h ; @51EE
    out dx, al ; @51F1
    sub cx, cx ; @51F2
    mov bx, cx ; @51F4
    mov bp, cx ; @51F6
    mov si, cx ; @51F8
    mov di, cx ; @51FA
    mov cx, word ptr ds:[JoystickSampleLoopLimit] ; @51FC
    in al, dx ; @5200
    not ax ; @5201
    and ax, word ptr 030h ; @5203
    mov word ptr ds:[JoystickButtonBits], ax ; @5206
    in al, dx ; @5209
    not ax ; @520A
    and ax, word ptr 0C0h ; @520C
    mov word ptr ds:[SecondJoystickButtonBits], ax ; @520F
    mov ah, byte ptr ds:[JoystickEnabledAxisMask] ; @5212
    or ah, ah ; @5216
    je loc_522B ; @5218
    not ah ; @521D
loc_521F:
    in al, dx ; @521F
    or al, ah ; @5220
    xor al, 0FFh ; @5222
    jne loc_524F ; @5224
    loop loc_521F ; @5229
loc_522B:
    popf ; @522B
    mov ax, word ptr ds:[JoystickSampleLoopLimit] ; @522C
    mov dx, ax ; @522F
    sub dx, di ; @5231
    mov word ptr ds:[SecondJoystickYCount], dx ; @5233
    mov cx, ax ; @5237
    sub cx, si ; @5239
    mov word ptr ds:[SecondJoystickXCount], cx ; @523B
    mov dx, ax ; @523F
    sub dx, bx ; @5241
    mov word ptr ds:[FirstJoystickXCount], dx ; @5243
    sub ax, bp ; @5247
    mov word ptr ds:[FirstJoystickYCount], ax ; @5249
    jmp loc_5294 ; @524C
loc_524F:
    test al, 1 ; @524F
    jne loc_5288 ; @5251
    test al, 2 ; @5256
    jne loc_527C ; @5258
    test al, 4 ; @525D
    jne loc_5270 ; @525F
    mov di, cx ; @5264
    or ah, 8 ; @5266
    cmp ah, 0FFh ; @5269
    jne short loc_521F ; @526C
    jmp short loc_522B ; @526E
loc_5270:
    mov si, cx ; @5270
    or ah, 4 ; @5272
    cmp ah, 0FFh ; @5275
    jne short loc_521F ; @5278
    jmp short loc_522B ; @527A
loc_527C:
    mov bp, cx ; @527C
    or ah, 2 ; @527E
    cmp ah, 0FFh ; @5281
    jne short loc_521F ; @5284
    jmp short loc_522B ; @5286
loc_5288:
    mov bx, cx ; @5288
    or ah, 1 ; @528A
    cmp ah, 0FFh ; @528D
    jne short loc_521F ; @5290
    jmp short loc_522B ; @5292
loc_5294:
    mov ax, word ptr ds:[JoystickButtonBits] ; @5294
    or ax, word ptr ds:[SecondJoystickButtonBits] ; @5297
    ret ; @529B
game_code_end:
GAMESEG ends
extrn ext_0A67:far
extrn ext_1E1F:far
extrn ext_2BF6:far
extrn ext_2D9A:far
extrn ext_2F9E:far
extrn ext_2FB7:far
extrn ext_325B:far
extrn ext_3260:far
extrn ext_3265:far
extrn ext_326B:far
extrn ext_3274:far
extrn ext_3279:far
extrn ext_3444:far
extrn ext_3632:far
extrn ext_3637:far
extrn ext_37A7:far
extrn ext_438A:far
extrn ext_4E83:far
extrn ext_5B63:far
end