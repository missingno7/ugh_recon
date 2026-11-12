; RAW virtual data debt. The locked MZ requires eight more allocation paragraphs
; than the initialized image plus C0H's stack. Ownership and use are unknown.
; A paragraph-aligned trailing reservation is a reproducing declaration only.
.286
TAIL_RESERVE segment para public 'RESERVE'
    db 128 dup (?)
TAIL_RESERVE ends
end
