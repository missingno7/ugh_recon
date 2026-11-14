# Optional AdLib level openings

Run `python verif/level_suite.py --group audio --all`. Seven real program-entry
traces initialize AdLib, enter shipped passwords and run 360 page-flip boundaries.
The selected one-player positions are 1, 2, 4, 5, 31, 43 and 64: tree, bird,
dino, Triopterus, low water, and both rain modes. The session selects the same
`3444:0000` music resource for every level; it does not select a section loop.

References come only from the rebuilt reconstructed ASM, in `build/levels-audio`.
Both hosts compare every frame. `coverage.json` additionally requires an active
AdLib gameplay-track request and level-start effect in every reference trace.
Receipts and per-entry counts (including zeros) are under
`build/workers/close-stones-17/audio/`. `BRANCHES.md` lists ordered API request
identities and counts; each reference retains their full order. Input timing
accounts for the password editor drawing one frame per character. These scripts
pin LF locally because reference identities hash raw script bytes.

This is separate from the default twenty-scenario gate and the 81 short openings.
