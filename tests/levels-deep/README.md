# Optional deeper gameplay

Run `python verif/level_suite.py --group deep --all`. This group has its own flag
so longer traces do not slow the 81-record opening suite or the default gate.
References in `build/levels-deep` come only from reconstructed ASM. Both hosts
compare full frame records; no gameplay state is injected or expected from a host.

The departure, water, bird and tree inputs extend or adapt maintained traces,
with AdLib enabled. Stone, dino and completion inputs were found using a read-only
feedback controller against L1 and then frozen as ordinary input-only scripts.
Only ASM entry counts earn branch coverage. `coverage.json` enforces the extra
entry, active-audio and next-level obligations on generated and cached references.
`BRANCHES.md` in the worker receipts reports every actor/hazard entry, including
zeros, and audio request counts. The complete request order remains in each
reference's inventory. All frame numbers there count completed page flips.

`completion-next` remains silent so the extended natural playthrough complements
the active-AdLib witnesses. It must load levels 1 and 2, board and deliver three
times, and finish with level index 1 and three lives. It does not simulate the
remaining game to final victory. Each child's limits are 600 seconds and 8 GiB;
children run serially. Cold reference generation costs more than cached replay.

The dino trace additionally counts the original `GAME:loc_2A36` velocity ADD,
with an instruction-shape check and signed addend counts. This distinguishes
player-force publication from animation-only calls to `UpdateDinoForce`.
