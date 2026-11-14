# Optional level coverage

This suite is separate from the default twenty scenarios. It covers all 69
one-player positions, followed by the 12 two-player positions whose physical
records are absent from the one-player order (12,18,...,78). Passwords and
record identities come from the freshly reconstructed resource tables.

Run `python tools/build.py`, then `python verif/level_suite.py --all`.
`--generate` deterministically regenerates these input-only scripts. References
are generated with the maintained reconstructed-ASM runner into `build/levels`;
neither native nor literal host output is used as an expected result. The driver
then compares both hosts, preserving the maintained RAM/device/ordered-log and
scalar observation model. No default tool directory or behavior is changed.

Each 160-boundary script supplies a password through the existing session path,
skips presentations with Enter, then supplies short keyboard thrust/direction
and action bursts. Two-player extras also move player two. Coverage reports
successful loader returns and actual routine-entry counts (including presentation
calls). Gameplay requirements establish that the selected record was drawn and
simulated; a listed password alone is not credited as level coverage.

The optional extensions have separate commands:

- `python verif/level_suite.py --group audio --all` enables AdLib on selected
  openings; see `tests/levels-audio/README.md`.
- `python verif/level_suite.py --group deep --all` runs longer measured gameplay
  witnesses; see `tests/levels-deep/README.md`.

They use separate caches and receipts. The default twenty-scenario gate is
unchanged. The driver also reports positive and zero actor/hazard entry counts
for the extensions and checks their explicit `coverage.json` obligations.
