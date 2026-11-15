# Falling item storage (cut 5G)

`NativeItemWorld.slot[12]` is the only persistent item store. The observation
allocation is DGROUP:2D6B..2E8B (end exclusive), 288 bytes. Each historical array
has twelve words; the bridge maps it to one member of each native record.

| Observation array | Offset | Record member |
|---|---|---|
| FallingItemDescriptors | 2D6B | descriptor_word |
| FallingItemCallbacks | 2D83 | callback_word |
| FallingItemSprites | 2D9B | sprite |
| FallingItemEraseSprite | 2DB3 | erase_sprite |
| FallingItemX | 2DCB | x32 |
| FallingItemY | 2DE3 | y32 |
| FallingItemDrawX | 2DFB | draw_x |
| FallingItemPreviousDrawX | 2E13 | previous_x |
| FallingItemDrawY | 2E2B | draw_y |
| FallingItemPreviousDrawY | 2E43 | previous_y |
| FallingItemMotionOrLifetime | 2E5B | motion_or_lifetime |
| FallingItemVerticalStep | 2E73 | vertical_step |

The words identifying descriptors and callbacks stay compatibility data. The
descriptor contents, including geometry, impulses, reward amounts, kind, sprite
and handler words, stay live resource views under resource_catalog's mutable
provider classification. `FallingItemType` and `FallingItem` in the accepted item
adapter are temporary per-call projections. They own no additional allocation.

Simulation coordinates, current draw coordinates and previous erase coordinates
are independent. Landing overwrites the horizontal-motion word with lifetime
560. Expiry and collection retire the sprite alone; inactive payload and erase
history remain stale. Allocation accepts any sign-set sprite, whereas dispatch
skips only FFFF. Both passes retain descending slot order.

Physical indexed views are retained: descriptor index 12 aliases callback[0],
and the demo's raw 16-index EnemyEraseSprite reset reaches descriptor[0] at
2D6B. The existing literal/raw demo route passes through the world registry;
neither the enemy owner nor the item owner claims a sixth enemy slot.

Session loader/reset/render, tree reward release, quick-delivery spawn,
contacts/physics and item transitions name explicit borrower roles. The timer,
lives and multiplier effects use the live run owner. Generic copy, decimal and
ICE windows use the registry's byte borrower. The manifest and model reader/writer
inventory are emitted by the world gate's inventory stage, including nonmodel
bulk and indirect routes. No algorithm or admission domain is widened.

Cold import copies the fixture once, then seals all 288 RAM lanes with A5.
Serialization writes only the separate observation buffer, checks its exact
emission count and never resynchronizes. The independent literal router checks
membership, all byte values, all word values, partial writes, neighboring
frames, paragraph aliases, resource exclusion and the demo reset alias.

L1 independently checks boundary RAM, device state and common ordered service
entries. The accepted item adapter publishes atomic per-call results, so its
internal byte-store order is compared between the legacy native adapter and the
composed adapter. This is not a claim of equality to L1 instruction store order.
