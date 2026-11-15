# Remaining resource ownership (cut 5R, second part)

`resource_world` is registry order 18. It complements the accepted
`resource_catalog`, whose directory and immutable codec-table contract is unchanged.
Keeping the continuation separate avoids widening that first cut's constness claim
and preserves its stable kind/index vocabulary. `metadata/resource-world.json`
lists every allocation, physical observation coordinate, classification, view and
borrower. Native code contains sizes and allocation-relative views only; the
verification bridge contains the historical coordinate mapping.

The continuation moves 359,423 bytes, making 371,853 native observation lanes in
combination with the accepted owners. All newly moved provider bytes remain
mutable or opaque mutable. The review's absence of observed writers proves no
constness. In particular, descriptor fields, terminated lists, animation words,
demo bytecode, packed maps, pictures, ADLX data, passwords, palettes, pixel banks
and retained padding can still be reached through admitted generic byte windows.
The existing 60 codec bytes remain read-only provider views in resource_catalog.

There are 58 disjoint storage regions and 682 version-one view identities. A view
is an allocation number, offset and length. Overlapping sentinels and distinct
consumer interpretations share those cells. Version-one token numbering is fixed
by the manifest, never computed from an encoded descriptor or callback address.
The resource pack uses family 5 plus that view number, sharing existing payload
offsets; scratch is a reservation rather than payload. D3 startup rejection and
the resource_catalog kind/index IDs are unchanged. Raw descriptor and callback
words are compatibility data interpreted only by the accepted adapters. Adding
storage views does not introduce a production code-address dispatcher.

The full 65,536-byte codec window has this allocation map:

| Window offsets | Bytes | Owner / meaning |
|---|---:|---|
| 0000..FCFF | 64,768 | Explicit native codec scratch |
| FD00..FD03 | 4 | Existing native audio flags, borrowed |
| FD04..FD0F | 12 | Retained scratch-tail alignment cells |
| FD10..FFFF | 752 | Prefix of the packed-map provider allocation, borrowed |

The ICE adapters still seed a complete window. Their existing actual-store count
identifies the backward ring of writes, including partial failures and wrapping
output. Publication updates owned cells only when the decoder actually wrote
them. An unchanged seeded tail must not overwrite a live owner mutation between
seeding and publication. No second persistent window or copy of the map prefix or
audio flags is allocated. The generated composition routes ICE, audio, copy and
decimal byte windows through the same physical owners.

Player cycle starts at DGROUP:0CFA and ends at 0CFC are two-word views of three
physical words. GAME:41B8 reads `[bx+PlayerAnimationCycleEnds]` and GAME:41C1
reads `[bx+PlayerAnimationCycleStarts]`, with player byte indices 0 and 2.
Consequently 0CFC is ends[0] and starts[1], once. The three impact words are at
DGROUP:262E..2633; GAME:13CB..13D1 and 1433..1439 shift the live difficulty by
one before reading them. Both tables remain mutable resource-backed player views,
not duplicated per-player runtime arrays. Numeric values are retained, not
reconstructed from sprite IDs or selected difficulty.

The generated bridge composition assigns live consumers explicit codec, render,
player, session, actor, front-end, audio or copy/decimal borrower roles. Its
byte/word routes preserve conditional segments, foreign windows and partial word
aliases, then fall through to the other owners for cells outside this resource
world. Membership is fixed, imported once and sealed with A5. Serialization writes
only the separate observation view; neither serialization nor failed publication
resynchronizes live RAM.

`program-model.json` now records the 184 proposed `storage_extent` entries as
bounded views with their evidence and limitations. A strided field has enumerated
cells, not a contiguous allocation spanning its neighbors. Container-only and
unknown proposals retain a null extent. Scratch's 64 KiB is explicitly an aliasing
window, not a second independent allocation. All model completeness flags remain
unchanged. The independent audio-channel record declaration is thirteen 42-byte
records; its interior aliases are not additional allocations.
