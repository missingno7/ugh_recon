; Recovered layouts: declarations only, no instances and no emitted bytes.
; Evidence and scope: docs/architecture-model.md. TASM 3.0 MASM mode.
; Fields are globally unique: FIELD:Type.Field in the naming tools, no address ledger IDs.
DemoMotionHeader struc
    DemoHeaderX dw ?                 ; +00 signed initial pixel X
    DemoHeaderY dw ?                 ; +02 signed initial pixel Y
    DemoHeaderPeriod dw ?            ; +04 updates per motion instruction
    DemoHeaderCallback dw ?          ; +06 near GAME callback
DemoMotionHeader ends

PassengerJourneyLeg struc
    JourneyLegPlatform dw ?          ; +00 platform index (FFFF terminates)
    JourneyLegWait dw ?              ; +02 raw wait, scaled by three halves
PassengerJourneyLeg ends

SpriteDirectoryEntry struc
    SpriteEntryBankOffset dw ?       ; +00 offset in the ID-selected pixel bank
    SpriteEntryWidth db ?            ; +02 pixel columns
    SpriteEntryHeight db ?           ; +03 pixel rows; width+height also read as a word
SpriteDirectoryEntry ends

DemoHiddenSprite equ 07FFFh
ItemLandedLifetime equ 0230h
ItemBenefitTimer equ 0
ItemBenefitLives equ 1
