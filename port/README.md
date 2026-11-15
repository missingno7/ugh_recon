# Standalone service groundwork

The deterministic backend for step 7.2 is `test/backend.c`. It implements the
same synchronous `GameServices` table using only C runtime storage. Run:

```
python verif/s7_services.py --all
```

See [test/README.md](test/README.md) for fixture delivery, coverage, comparison
boundaries and the operations deliberately left Unsupported for step 7.3.

This target links no game units. `services.h` is the engine-facing synchronous
capability table; `sdl/backend.h` holds provider state. Run its headless tests with:

```
python verif/port_services.py --all
```

The driver uses the existing pinned MinGW compiler, SDL3 and Nuked-OPL3. It sets
SDL's dummy video/audio drivers, builds only these providers and test oracles, and
records bounded child commands under `build/workers/close-stones-26/`.
The embedding application initializes SDL video/audio/events/gamepad subsystems
before using the live device operations; lifecycle wiring remains step7 work.

To extract the pack separately:

```
python tools/respack.py --output build/port/ugh.res --header build/port/resource_manifest.h
python tools/respack.py --output build/port/ugh.res --verify
```

Compile the generated admission header into the eventual executable. Pass its
required-resource array to `gs_resources_open` before any engine initialization.
A missing, wrong-version, damaged, incomplete, detached-alias or foreign-content
pack is rejected, with no partially published pack. The runtime reader opens no
executable. Mutability permits live updates after admission; hashes validate initial
content, not a later mutable resource's gameplay value.

The build manifest has original extraction coordinates for audit. The pack and its
compiled admission header have IDs, classes, file-relative views, lengths and
digests. Individual initialized data records are templates for future owner
initializers, never a memory image to restore. The zero codec reservation and
library runtime data are explicitly excluded. Workspace allocation and its owner
aliases still require the step7 engine adapter.

The extractor reserves catalog families 1 (662 sprite records), 2 (five codec
views) and 3 (three semantic demo effects with no code payload). Family4 names are
checked CRC32 keys over curated symbolic data-object names. Collisions fail the
build. Renaming/repartitioning a registered name is an admission-schema change,
not permission to reuse its ID for a different object. Generated symbolic macros
let consumers name IDs without historical coordinates. Reserved/unknown data is
`opaque_mutable`, not silently frozen or discarded.

Time delivery is requested at explicit cuts. Active-retrace and timer opportunities
use independent exact integer 1/70-second timelines; pacing uses their maximum,
following the existing host's two-timeline pattern. Status/input reads never advance
either timeline. Timer accounting/quantum decisions stay in the engine; opportunities
preserve caller order. Wall time only delays presentation. Host
suspension freezes virtual events and shifts the pacing epoch on resume, with no
catch-up tick. Game pause is separate: its input polling continues. No SDL vsync or
audio callback runs engine code.

Gamepad counts use neutral1000, negative endpoint250 and positive endpoint1750 in
common virtual discharge units, with 16-bit limit/latched replies. Native input
still computes its own thresholds/directions. Two independent devices and button
groups are supported. Scans are ordered set1 bytes; editor keys use a separate
queue. Install/restore flushes both recipients and suppresses stale releases.

Pending step7 bindings deliberately return Unsupported: noncanonical pixel
continuations/external controls, legacy audio capability/calibration and timer
lifetime prefixes, and lifecycle/terminal orchestration. Logical clock delivery
calls an explicitly supplied synchronous receiver, otherwise Unsupported. The four
unexplained hooks are not implemented. No service facade is wired to native worlds
or a game loop by this groundwork.

`files.c` follows the current Windows host's atomic-replace policy. A disk flush
does not manufacture a logical close. SDL presentation and stream consumers are
tested headlessly; physical device/backend-driver combinations still need live
integration testing. See the worker report for the exact request correspondence
and test limits.
