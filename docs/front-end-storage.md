# Front-end allocation and service boundary (cut 6B)

`front_end_world` owns 182 historical observation bytes. Each allocation is cold
imported once; its live RAM lanes are A5. The serializer writes only the separate
observation view. The native owner has no file-content cache or password lookup.

| DGROUP offset | Bytes | Native field | Consumers / writers |
|---|---:|---|---|
| 00BB | 2 | file_handle_bytes | Load/save; stale after failures and close |
| 00C7 | 1 | row_stride | Unsigned CL multiplication in row/digit selection |
| 0B0D | 6 | difficulty_text | Indexed menu copy; text reader |
| 0B19 | 10 | players_text | Indexed menu copy; text reader |
| 0B4E | 21 | password | Twenty edit bytes plus the existing NUL; session reads |
| 0B73 | 10 | control_text[0] | Indexed control-label copy; text reader |
| 0B8D | 10 | control_text[1] | Indexed control-label copy; text reader |
| 0BFD | 2 | level_characters | Decimal introduction writes; centered text reads |
| 0C6D | 13 | name_entry | Twelve edit bytes plus NUL; name rendering/insertion |
| 0C86 | 107 | score_rows | File service, complement, shift, qualification, insertion, text |

The four indexed destinations are established by `menus_label` and the ASM
callers. They are embedded mutable text, not an additional temporary string
buffer. Indexed copy omits NUL; bytes after a shorter copy remain live. The
password comparison anchor at 0B4D is a biased view, with the first comparison at
anchor+1; its preceding CR is outside this allocation. Word aliases at password+2
and name+2/+4/+6/+8 share these fields. Each score row remains 21 bytes: fourteen
name bytes, six digits, CR. Editing copies twelve name bytes into a row, retaining
the last two name bytes. The trailing NUL/FF bytes are part of the 107-byte table
and its XOR-FF transform. The owner does not clip raw windows at field boundaries.

The menus, scores and session adapters have explicit borrower roles; the shared
character loader uses the calling role. Generic copy/decimal/codec windows use
the accepted registry byte borrower. DOS reads/writes remain file services over
the live routed byte span: reads publish only the returned prefix; they never
clear or replace the unreturned tail. `HighFileFlow` preserves all original
open/read/write/close actions, including failed-read/failed-close prefixes and
the unclosed save binding. Device files and positions are service state, never
another authoritative high-score table.

`NativeFrontEditor` carries each invocation's position and full blink word.
`NativeFrontTextCursor` carries the line position and X/Y cursor, accepting live glyph-service
replies at the original cuts. The existing `MenusMain`, `MenusStringCopy` and
`HighFileFlow` are already native invocation continuations. These have no
historical RAM allocation and add no observation bytes. The bridge projects
register arguments for services and accepts their live replies; it never
resynchronizes an owned RAM lane. The composition registry routes both editors'
BIOS queue calls through `input_editor_queue` in `input_world`.

Session retains the actual 69/81-entry password selection and the unknown/empty
default to level zero. Run/configuration/water and decimal buffers remain live
borrowers of their accepted owners. No resource, callback or descriptor identity
is retyped by this cut. Broader string/editor windows retain the existing
deterministic compatibility domain and budgets; no port policy is added here.
