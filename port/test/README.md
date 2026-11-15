# Deterministic test services

`gs_test_init` creates explicit backend storage; `gs_test_services` returns its
capability table. The implementation includes only `backend.h`, `services.h` and
standard C headers. It has no emulator, SDL, resource-image loader or game units.
The state occupies four 64-Ki-cell planes plus bounded service/fixture storage.
There are no game callbacks or background threads.

| Capability | Behaviour |
|---|---|
| Indexed video | All four inherited GC write modes, rotate/logic/set-reset/masks, compare/care reads, live latches, hidden cells, ordered copies, collision reads, water read/write, CRTC/attribute transactions |
| DAC | Six-bit components, partial triples, persistent cursor and index wrap |
| Input | Ordered raw set-1 bytes, separate BIOS delivery stream with peek/take, queue-flush witness, captured/native keyboard tokens, two sticks and independent buttons |
| Joystick | Synthetic 250/1000/1750 endpoint/neutral units or explicitly scripted raw samples; prioritized axis detection without decrement, full zero-limit wrap |
| Time | Independent retrace/timer 70-Hz integer timelines, explicit cuts, suspension without catch-up, PIT low/high phase, PIC mask/EOI and explicit IRQ opportunities |
| OPL | Ordered atomic writes and partial register-selection/data transactions; advance records virtual audio time without synthesizing engine ticks |
| Scores | Logical handles, raw encoded bytes, retained short-read tails, DOS error/value replies, short I/O limits, one-shot injected errors, in-memory persistence without implicit close |
| Lifecycle/seed | Primitive video query/set and terminal exit; fixed replay DOS-time reply, initially 10:20:30:40 in hexadecimal |
| Resources | Optional delegation to an admitted `GSResourceOps`/context; no second resource owner or extractor |

`GSTestRun` fixtures schedule future external deliveries at service reads. They
can repeat, cycle, or end. They are not a physical held-key state. BIOS peek does
not consume a delivery; take does. Queue flush returns the live `flush_reply`
witness and does not erase future scripted deliveries, matching the current
platform model's BDA-head flush and independent INT16 script. This differs from
flushing already queued physical events in the SDL backend. Raw scripted
joystick samples use the same priority/decrement algorithm as the current model;
without a script, both sticks use the configured synthetic discharge counts.

Install/restore accepts the closed keyboard roles 1 (saved external recipient)
and 2 (native scan recipient). It does not interpret a token as a code address.
The engine still requests queue flushing at its existing separate cuts. The
verification adapter translates historical coordinates only on the oracle side.

An exhausted scan or queue fixture returns Empty; malformed routes/arguments return Invalid or
Unsupported. A counts stream that ends mid-measurement returns Unsupported with
the consumed count/latch prefix. A word store at the final cell consumes its low
byte then returns Unsupported: its contiguous high byte has no indexed-store
binding. Masks with enabled joystick bits outside the four axes are Unsupported.
These are explicit boundaries, not an all-state literal compatibility claim.

All callbacks marked `step 7: pending` remain Unsupported: pixel compatibility,
audio status/clock/calibration/timer lifetime, and lifecycle orchestration/critical
binding. Primitive operations added after those callbacks do not execute an
engine continuation. The SDL tables leave these newly optional primitives null;
this task does not bind the production loop.

`GSTestRecorder` sees synchronous ordered effects, including raw DAC/OPL stream
transactions. It is diagnostic and cannot reject or run game work. Presentation
counts a boundary, persistence clears dirty state, and pacing is a deterministic
no-op. The replay backend performs no disk I/O or audio synthesis.

`verif/s7_services.py --all` compiles the backend as a separate object with a
checked dependency file, links a backend-only executable, compares synthetic
edge streams with unmodified platform/memory implementations, and instruments
generated composed-host copies for all twenty maintained scenarios plus smoke.
Every supported input/output reply and normalized ordered I/O effect is compared.
Each aperture write checks all four destination bytes; each read checks all
latches. Full planes, latches, controls, DAC/OPL, PIT/PIC/clocks, score bytes and
handles, mode and exit state are compared at every frame/terminal boundary.
The original host records must also equal the maintained references.

External scripts are shared stimuli, copied only when the host replaces a
fixture; their cursor/used/cycle consumption is independently checked. Backend
storage is imported once, never refreshed from a later model boundary. Unserved
OPL status probes and external/timer vector operations are counted separately
and checked for Unsupported in the backend while the verification model retains
its literal behaviour. Those exclusions are not counted as equivalent replies.
The runner also records the existing D5 inventory check without relocking it;
inventory drift is separate from the service comparison result.

All test/build children run serially in jobs capped at 600 seconds and 8 GiB.
Receipts, generated sources, defect binaries and the handoff report are under
`build/workers/s7-services/`. Neither oracle assets nor maintained host/native
sources are changed.
