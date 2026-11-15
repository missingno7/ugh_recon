"""D5 inventory, not a runtime admission implementation or a new proof of reachability.

Only --generate writes metadata/admission.json.  --check reconstructs the inventory
from certificates and source, using content-addressed receipt snapshots if the
untracked worker receipts are absent.  Neither command rewrites a certificate.
Run: python verif/admission.py --all
"""
from __future__ import annotations

import argparse
import collections
import functools
import hashlib
import json
import re
import sys
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/workers/close-stones-27"
MANIFEST = ROOT / "metadata/admission.json"
sys.path[:0] = [str(ROOT / "verif"), str(ROOT / "tools")]

# Receipt snapshots are data, not game code. Pins are filled from the accepted
# receipts, independently of the generated manifest. Missing receipts must never
# turn --check into an unchecked comparison of a manifest with itself.
PINS = {'audio': 'dc50cfb50119d00c94062dd47b056c01ee334a9f646476139055545a88479101', 'timing': 'd1d1272ff929a38e2f81427053c37f18a0eae212812e36ae9c476ed6288f18b9', 'audio_summary': '0b0d19e49187afcc1c10bf5dcd9e527903ac8236e803e4dce23913df0a4ff479', 'timing_summary': '0871ae4306290dde454e4e0cd641537e95450349a2a22332ec031dafcdb94758', 'pack': '1e889cc5d20d50b3b775fab041e3ed76024e640434c0c6e65c064619fefb10af', 'prefix_replay': '0b5658d853aa1077cc95d9ef9a1bf0e5664d9207f5d4fffb2f18782dda33911e'}
RECEIPTS = {
    "audio": "build/workers/close-adlx-23/api.json",
    "timing": "build/workers/close-adlx-22/api.json",
    "audio_summary": "build/workers/close-adlx-23/verification-receipt.json",
    "timing_summary": "build/workers/close-adlx-22/verification-receipt.json",
    "pack": "build/workers/close-stones-26/ugh.manifest.json",
}
VOLATILE = {"dependencies", "verification_inputs", "verification_input_hashing", "evidence_refreshed"}
USE_SNAPSHOT = False


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def text_hash(path):
    return hashlib.sha256(Path(path).read_text(encoding="utf-8-sig").replace("\r\n", "\n").encode()).hexdigest()


def leaves(value, pointer=""):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, pointer + "/" + key.replace("~", "~0").replace("/", "~1"))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from leaves(item, pointer + "/" + str(i))
    else:
        yield pointer, value


def source(path, pointer=None):
    result = {"path": path}
    if pointer is not None:
        result["pointer"] = pointer
    return result


def certs():
    return {p.stem: read(p) for p in sorted((ROOT / "metadata/closure").glob("*.json"))}


def receipt_selection(kind, data):
    if kind in ("audio", "timing"):
        declines = data["explicit_out_of_domain"]
        observed = [r for r in data["profiles"]["composed"]["cases"] if r["status"] != 0]
        if declines != observed:
            raise ValueError(kind + " receipt rejection list disagrees with composed results")
        return {"result": data["result"], "rejections": declines,
                "legacy_matching": data["legacy_matching"], "composed_matching": data["composed_matching"]}
    if kind == "pack":
        return {k: data[k] for k in ("schema", "image_sha256", "resources", "model_bindings", "classification_policy")}
    return {"result": data["result"], "api": data["api"]}


def evidence(previous=None):
    result = {}
    for kind, path in RECEIPTS.items():
        p = ROOT / path
        if p.exists() and not USE_SNAPSHOT:
            payload = receipt_selection(kind, read(p))
        elif previous and kind in previous:
            payload = previous[kind]["snapshot"]
        else:
            raise ValueError("required receipt unavailable: " + path + "; use the committed manifest's pinned snapshot")
        if digest(payload) != PINS.get(kind):
            raise ValueError("receipt content does not match accepted pin: " + path)
        result[kind] = {"source": path, "sha256_canonical_selection": digest(payload), "snapshot": payload}
    return result


@functools.lru_cache(maxsize=None)
def header_text(path):
    return Path(path).read_text()


def enum_views(paths):
    from standalone_census import masked
    rows = []
    todo = list(paths); visited = set()
    while todo:
        name = todo.pop()
        if name in visited:
            continue
        visited.add(name)
        p = ROOT / name
        if p.suffix != ".h" or not p.exists():
            continue
        raw = header_text(p); t = masked(raw)
        for dependency in re.findall(r'^\s*#include\s+"([^"]+)"', raw, re.M):
            candidates = [p.parent / dependency, ROOT / "native" / dependency, ROOT / "native/bridge" / dependency]
            for candidate in candidates:
                candidate = candidate.resolve()
                if candidate.is_relative_to(ROOT / "native") and candidate.is_file():
                    todo.append(candidate.relative_to(ROOT).as_posix())
                    break
        for match in re.finditer(r"typedef\s+enum\s*(\w+)?\s*\{([^{}]*)\}\s*(\w+)\s*;", t, re.S):
            values = [x.strip() for x in match[2].split(",") if x.strip()]
            rows.append({"type": match[3], "declarations": values, "source": source(name),
                         "scope": "Declared typed vocabulary; not permission to invoke every role or enum value from arbitrary state."})
    return sorted(rows, key=lambda r: (r["source"]["path"], r["type"]))


@functools.lru_cache(maxsize=None)
def function_hash(path, name):
    return raw_function_hash(Path(path).read_text(), name)


def raw_function_hash(raw, name):
    from standalone_census import bodies, masked
    entry = next((x for x in bodies(raw) if x[3] == name), None)
    if entry is None:
        raise ValueError("source checkpoint function missing: " + name)
    a, b, e, _ = entry
    return digest(re.sub(r"\s+", "", masked(raw[a:e + 1])))


def fallback_sites():
    """Inventory executable references, including branch-inactive verifier guards.

    Also reject l1 identifiers in preprocessor bodies: no declaration or macro
    escape can silently disappear from the executable-site classification.
    """
    from standalone_census import bodies, masked
    rows = []
    for p in sorted((ROOT / "native").rglob("*")):
        if p.suffix not in (".c", ".h"):
            continue
        raw = p.read_text(); clean = masked(raw); functions = bodies(raw)
        ordinals = collections.Counter()
        for match in re.finditer(r"\bl1_\w+\b", clean):
            function = next((n for a, b, e, n in functions if b < match.start() < e), None)
            line_start = clean.rfind("\n", 0, match.start()) + 1
            line_end = clean.find("\n", match.end())
            if line_end < 0:
                line_end = len(clean)
            line = clean[line_start:line_end].strip()
            if function is None:
                # Function declarations are not transfers. Everything else is
                # classified, including aliases/macros that could hide a transfer.
                if re.fullmatch(r"(?:extern\s+)?(?:EXPORT\s+)?int\s+l1_\w+\s*\([^;{}]*\)\s*;", line):
                    continue
                function = "<file-scope-or-macro>"
            path = p.relative_to(ROOT).as_posix()
            key = (function, match[0]); ordinals[key] += 1
            checkpoint = ":".join((path, function, match[0], str(ordinals[key])))
            prefix = {"checkpoint": checkpoint, "source": source(path), "function": function,
                      "line_hint": raw.count("\n", 0, match.start()) + 1,
                      "expression": raw[line_start:line_end].strip(),
                      "semantics": "Stop at this selected literal-transfer expression, before invoking its target. Preserve all preceding stores, register effects and delivered services. Execute neither the literal body nor its following tail; no rollback."}
            if function != "<file-scope-or-macro>":
                prefix["source_function_sha256_normalized_tokens"] = function_hash(p, function)
            rows.append({"id": "fallback:" + checkpoint, "kind": "dormant_l1_guard", "target": match[0],
                         "policy": "Unsupported", "prefix": prefix,
                         "verification_behavior": "Retained full compatibility fallback or composed Unsupported branch; census nonexecution is observation, not proof of unreachability."})
    return rows


def explicit_unsupported_sites():
    """Also inventory existing status-1 cuts that have no literal alternative."""
    from standalone_census import bodies, masked
    rows = []
    for path in sorted((ROOT / "native").rglob("*")):
        if path.suffix not in (".c", ".h"):
            continue
        raw = path.read_text(); functions = bodies(raw); clean = masked(raw)
        counts = collections.Counter()
        for match in re.finditer(r"\bUGH_UNSUPPORTED\b", clean):
            function = next((n for a, b, e, n in functions if b < match.start() < e), "<macro>")
            counts[function] += 1
            relative = path.relative_to(ROOT).as_posix()
            checkpoint = f"{relative}:{function}:Unsupported:{counts[function]}"
            start = raw.rfind("\n", 0, match.start()) + 1
            end = raw.find("\n", match.end())
            if end < 0:
                end = len(raw)
            prefix = {"checkpoint": checkpoint, "source": source(relative), "function": function,
                      "line_hint": raw.count("\n", 0, match.start()) + 1, "expression": raw[start:end].strip(),
                      "semantics": "Produce Unsupported at this selected status expression (macro expands at its caller). Preserve preceding writes/services and the documented caller unwind. Do not resume normal gameplay or invoke a literal fallback; no rollback."}
            if function != "<macro>":
                prefix["source_function_sha256_normalized_tokens"] = function_hash(path, function)
            rows.append({"id": "existing-unsupported:" + checkpoint, "kind": "existing_unsupported_cut", "policy": "Unsupported", "prefix": prefix,
                         "scope": "Source cut inventory, not an additional fixture decline. A cut may also serve one of the 188 replayed declines or a classified literal guard."})
    return rows


def fixture_map():
    from difftest import load_suite
    result = {}
    for suite in ("timer_system", "sound_api", "sound_engine"):
        for case in load_suite(suite).CASES:
            key = (suite, case.title)
            item = {"routine": case.routine, "kind": case.kind, "source": "tests/" + suite + ".py"}
            if key in result and result[key] != item:
                raise ValueError("ambiguous fixture entry role " + str(key))
            result[key] = item
    return result


def rejection_edges(ev, trace=None):
    fixtures = fixture_map()
    timing_keys = {(r["suite"], r["case"], r["poison"]) for r in ev["timing"]["snapshot"]["rejections"]}
    audio_rows = ev["audio"]["snapshot"]["rejections"]
    if len(audio_rows) != 188 or len(timing_keys) != 32:
        raise ValueError("rejection count: expected 188 including 32 timing")
    edges = []
    for row in audio_rows:
        key = (row["suite"], row["case"], row["poison"])
        fixture = fixtures[(row["suite"], row["case"])]
        identity = digest([*key])[:20]
        prefix = {"checkpoint": "composed-api-rejection:" + identity,
                  "source": source(RECEIPTS["audio"], "/explicit_out_of_domain"),
                  "entry": fixture["routine"],
                  "semantics": "At the first composed adapter admission decline, return status 1; preserve the adapter's actual prefix. Not a pre-entry rejection or rollback. The receipt's RAM/register differences document the stopped execution, not a successful L1 match.",
                  "precision": "Recorded composed API decline; fixture and poison identity are exact. Source checkpoint replay is required before runtime policy lowering."}
        if trace and identity in trace:
            prefix = trace[identity]
        edges.append({"id": "audio-decline:" + identity, "kind": "audio_api_decline", "policy": "Unsupported",
                      "unit": "audio_world", "also_timing": key in timing_keys, "fixture": {**row, **fixture},
                      "source": source(RECEIPTS["audio"], "/explicit_out_of_domain"), "prefix": prefix})
    if not timing_keys <= {(r["suite"], r["case"], r["poison"]) for r in audio_rows}:
        raise ValueError("timing declines are not a subset of audio declines")
    return edges


def edge(name, kind, path, checkpoint, semantics, **extra):
    return {"id": name, "kind": kind, "policy": "Unsupported", "source": source(path),
            "prefix": {"source": source(path), "checkpoint": checkpoint, "semantics": semantics}, **extra}


def other_edges():
    edges = []
    for operation in ("pixel_service_continuation", "pixel_service_compatibility_write"):
        edges.append(edge("pixel-opaque:" + operation, "opaque_compatibility_service", "native/pixel_world.h", operation,
                          "Immediately before delivery to the opaque verification provider. Preserve already delivered pixel/control effects and operation journals. Do not dispatch the opaque binding.",
                          unit="pixel_world", operation=operation))
    # Descriptor/callback/script/journey/animation/drop identities now have a
    # finite generated vocabulary. Their raw words live only in verification.
    # Sound handles belong to the independent audio continuation.
    raw = {"enemy_world": ["sound-handle"]}
    for unit, fields in raw.items():
        for field in fields:
            edges.append(edge("raw-identity:" + unit + ":" + field, "raw_identity_interpretation",
                              "metadata/closure/" + unit + ".json", unit + "/decode/" + field,
                              "Reject before interpreting an unregistered raw transport word as a descriptor, callback, journey, animation, drop-list or sound role. Merely storing/serializing the word is allowed. Already recognized shipped bindings must be decoded by an explicit registry; word-to-token equality is not an admission rule.",
                              unit=unit, field=field, runtime_enforcement="pending typed identity/continuation cut"))
    for family in ("actor descriptor", "enemy descriptor", "falling-item descriptor",
                   "passenger itinerary", "motion script", "animation", "tree reward list"):
        edges.append(edge("typed-object-resource:" + family, "typed_identity_admission",
                          "native/object_identities.c", "object_resource_identity/" + family,
                          "Before interpreting the view or cursor: reject an unregistered family, view or position with Unsupported. No raw compatibility fallback in the native constructor.",
                          runtime_enforcement="object_resource_identity; full-word verifier round trips and actual C bounds properties"))
    edges.append(edge("typed-object-callback", "typed_identity_admission", "native/object_identities.c",
                      "object_callback_identity/role",
                      "Before using the role: reject unknown actor/enemy/item/effect enums with Unsupported. Empty/zero resource members are explicit identities, never permission to execute a callback.",
                      runtime_enforcement="object_callback_identity; direct callback invocation is a separate outstanding continuation"))
    edges.append(edge("audio:sb-digital", "unreachable_shipped_path", "metadata/closure/adlx_digital.json", "select-audio-backend/SB-or-digital",
                      "Before accepting an SB/digital backend or submitting its first service. Startup selects AdLib only; preserve any earlier lifecycle effects. Verification API contracts remain available.",
                      source_also=[source("metadata/closure/lifecycle.json"), source("metadata/closure/adlx_samples.json")]))
    for name in ("loc_001C", "loc_001D", "loc_001E", "loc_001F"):
        edges.append(edge("external-hook:" + name, "external_hook", "src/asm/GAME.ASM", "external-transfer/" + name,
                          "Before the transfer into this retained unexplained near RET hook. Deliver no invented replacement service. Preserve all caller prefix effects; do not repair the broken far-call/near-return shell.",
                          role=name, source_also=[source("docs/standalone-plan.md")]))
    # D5's full VGA compatibility domain is wider than the shipped admission.
    edges.append(edge("video:outside-shipped-controls", "nonshipped_video_domain", "docs/port-contract.md", "pixel-service/admit-controls",
                      "Before accepting the first pixel/copy request whose inherited controls or binding is outside the shipped-state predicates. Keep earlier requests. Full compatibility remains in verification; the census alone is C/D observation, not a universal proof.",
                      predicates="The per-service states and address examples in the accepted VGA census remain the evidence, not blanket clipping or zero/default initialization."))
    edges.append(edge("resources:invalid-pack", "startup_resource_error", "port/resources.c", "gs_resources_load/validation",
                      "Before publishing any pack resource view: reject wrong version/hash, duplicate/missing required identity, malformed range or missing pack. Error is explicit; do not synthesize missing resources."))
    return edges


def receipt_checks(cs, ev):
    for unit, kind, total in (("audio_world", "audio", 188), ("timing_world", "timing", 32)):
        summary_kind = kind + "_summary"
        p = RECEIPTS[summary_kind]
        expected = cs[unit].get("receipts", {}).get(p)
        if not expected:
            raise ValueError("certificate rejection receipt anchor absent: " + unit)
        # Certificate uses a normalized-text digest of the full receipt, whereas
        # the compact snapshot has an independent canonical-data digest.
        if p in FULL_RECEIPT_PINS and expected != FULL_RECEIPT_PINS[p]:
            raise ValueError("certificate rejection receipt changed: " + unit)
        if (ROOT / p).exists() and text_hash(ROOT / p) != expected:
            raise ValueError("certificate rejection receipt hash mismatch: " + unit)
        counts = ev[summary_kind]["snapshot"]["api"]
        count = counts.get("declines", counts.get("explicit_rejections"))
        if count != total or len(ev[kind]["snapshot"]["rejections"]) != total:
            raise ValueError("certificate rejection list disagrees with manifest: " + unit)
        assertions = [str(v) for ptr, v in leaves(cs[unit]) if ptr.startswith(("/evidence", "/uncertainty"))]
        if not any(re.search(r"\b" + str(total) + r"\b", v) and re.search(r"reject|declin", v, re.I) for v in assertions):
            raise ValueError("certificate no longer declares the recorded rejections: " + unit)


FULL_RECEIPT_PINS = {
    RECEIPTS["audio_summary"]: "12e333f7e7a193c1388d1b9a7b8a09496873bdd1c0c07974d7b6dbd10a6bb18c",
    RECEIPTS["timing_summary"]: "558a2be17d961b1fb36c8f303b2885a4d088dde963b7b22af991b86938a62b06",
}


def unit_domains(cs, pack):
    model = read(ROOT / "metadata/program-model.json")
    token_by_name = {r["name"]: r["id"] for r in pack["resources"]}
    token_by_model = {r["name"]: token_by_name[r["resource"]] for r in pack["model_bindings"] if r["resource"] is not None}
    groups = resource_groups(pack)
    consumers = {
        "resource_catalog": list(groups),
        "actor_types": ["descriptor_tables", "itineraries", "animations", "demo_tables"],
        "actor_world": [], "enemy_world": [],
        "actor_pass": ["descriptor_tables"], "actor_render": ["sprite_metadata", "sprite_pixels"],
        "demo_core": ["demo_tables", "demo_effects", "animations"],
        "demo_presentation": ["demo_tables", "demo_effects", "sprite_metadata"],
        "hazards": ["descriptor_tables", "animations"], "stones": ["descriptor_tables", "animations"],
        "passenger_itinerary": ["descriptor_tables", "itineraries", "animations"],
        "passenger_delivery": ["descriptor_tables", "itineraries", "animations"],
        "passenger_water": ["descriptor_tables", "itineraries", "animations"],
        "adlx_loader": ["adlx"], "adlx_sections": ["adlx"], "adlx_main": ["adlx"],
        "adlx_effects": ["adlx"], "adlx_voice": ["adlx"], "adlx_music": ["adlx"],
        "audio_world": ["adlx"], "music_clock": ["adlx"],
        "ice": ["codec_tables", "packed_streams"], "ice_scratch": ["codec_tables", "packed_streams"],
        "pictures": ["packed_streams"], "render_primitives": ["sprite_metadata", "sprite_pixels"],
        "hud": ["sprite_metadata", "sprite_pixels"], "water_weather": ["sprite_metadata"],
        "session": ["packed_streams", "descriptor_tables", "itineraries"],
        "menus": ["packed_streams", "demo_tables"],
        "level_view": ["descriptor_tables", "itineraries"],
    }
    units = []
    for unit, cert in cs.items():
        path = "metadata/closure/" + unit + ".json"
        files = cert.get("native", {}).get("files", [])
        original = cert.get("original", {})
        routines = set(re.findall(r"(?:GAME|SOUND|TIMER|C):[A-Za-z_]\w*", json.dumps(original)))
        routines.update("GAME:" + x for x in re.findall(r"\bc_(\w+)", json.dumps(original)))
        referenced = set()
        for name, var in model["variables"].items():
            if routines.intersection(var.get("readers", []) + var.get("writers", [])):
                if name in token_by_model:
                    referenced.add(token_by_model[name])
        contract = {k: cert[k] for k in ("interface", "assumptions", "indirect") if k in cert}
        enums = enum_views(files)
        roles = [r for r in enums if re.search("Callback|Role|Effect|Phase|Mode|Kind|Status|Error|Id$", r["type"])]
        callable_roles = []
        for row in roles:
            if not re.search(r"Callback$|CallbackRole$|PeerRole$|MotionEffect$", row["type"]):
                continue
            names = [x.split("=", 1)[0].strip() for x in row["declarations"]]
            excluded = [x for x in names if re.search(r"(?:^|_)(?:OPEN|UNKNOWN|UNSUPPORTED|INVALID|OTHER|COUNT|CAPACITY|FIXTURE)(?:_|$)", x)
                        or row["type"] == "AudioPeerRole" and re.search(r"Dsp|Dma|Sample", x)]
            callable_roles.append({"type": row["type"], "registered_roles": [x for x in names if x not in excluded],
                                   "excluded_open_roles": excluded, "source": row["source"],
                                   "scope": "Registry vocabulary subject to the unit contract and global SB/hooks/raw-identity exclusions; not arbitrary mixed fragments or host pointers."})
        units.append({"unit": unit, "source": source(path), "certificate_status": cert["status"],
                      "contract": contract, "entry_roles": original,
                      "production_entry": "not admitted: SB/digital API only" if unit in ("adlx_digital", "adlx_samples") else "internal shipped caller roles only, never arbitrary ABI entry",
                      "resource_tokens": sorted(referenced),
                      "indirect_resource_groups": consumers.get(unit, []),
                      "resource_scope": "Exact model reader/writer links to stable pack IDs; not an exhaustive indirect resource allowlist. Registry tokens below plus the certificate's list/descriptor contract constrain indirect resources.",
                      "typed_vocabulary": roles,
                      "callback_roles": callable_roles,
                      "error_replies": {"declared_status_types": [r for r in enums if re.search("Status|Error|Result", r["type"])],
                                        "contract_outputs": cert.get("interface", {}).get("outputs"),
                                        "production_admission_failure": "Unsupported at the edge's prefix; ordinary documented game errors retain their own result and partial effects."},
                      "modes": {"production_audio": ["none", "adlib"], "players": [1, 2],
                                "source": source("docs/port-contract.md"), "unit_constraints": cert.get("assumptions", [])},
                      "interpretation": "Conjunction of this contract, registered identities, the shipped entry graph and explicit exclusions. Migrated does not mean arbitrary ABI states are admitted. Vocabulary enum members do not independently grant entry permission."})
    return units


def resource_groups(pack):
    """Closed data-token lists, not inferred callback identities or allocations.

    Operations still select subresources through their accepted contracts: e.g.
    a glyph call does not thereby admit a caller-chosen arbitrary sprite.
    """
    selectors = {
        "sprite_metadata": r"^catalog\.sprite\.",
        "sprite_pixels": r"^data\.B\w+\.Sprite_\d+$",
        "codec_tables": r"^catalog\.codec\.",
        "demo_effects": r"^catalog\.demo_effect\.",
        "demo_tables": r"^data\.DGDATA\.DemoTable_",
        "descriptor_tables": r"^data\.DGDATA\.(?:ActorDescriptors|EnemyDescriptors|FallingItemDescriptors|FallingDescriptor_\w+)$",
        "itineraries": r"^data\.DGDATA\.Passengeritinerary_",
        "animations": r"^data\.DGDATA\.Animation_",
        "adlx": r"^data\.B\w+\.Adlx(?:Header|Events)_",
        "packed_streams": r"^data\.B\w+\.IceStream_",
    }
    return {name: {"token_ids": [r["id"] for r in pack["resources"] if re.search(pattern, r["name"])],
                   "selector": pattern, "source": source(RECEIPTS["pack"], "/resources"),
                   "scope": "Registered data availability, constrained further by each consumer contract. No code bytes or raw word-to-callback mapping."}
            for name, pattern in selectors.items()}


def quirks(cs):
    rows = []
    pattern = re.compile(r"bug|quirk|stale|wrap|wrong.stride|alias|sentinel|unclipp|underflow|overflow|partial|typo|infinite|unbounded|unsigned|high.byte|retained tail|lookahead|look.ahead", re.I)
    for unit, cert in cs.items():
        for pointer, value in leaves(cert):
            if not isinstance(value, str):
                continue
            retained = pointer.startswith(("/retained", "/quirks", "/bugs"))
            supplemental = pointer.startswith(("/interface", "/memory", "/purpose")) and pattern.search(value)
            if retained or supplemental:
                rows.append({"id": unit + pointer, "unit": unit, "source": source("metadata/closure/" + unit + ".json", pointer),
                             "assertion": value, "kind": "retained_assertion" if retained else "contract_edge_assertion",
                             "rule": "Preserve the entire source assertion, including each clause; production admission is not permission to fix it."})
    return rows


def semantic_certificate_hash(cert):
    return digest({k: v for k, v in cert.items() if k not in VOLATILE})


def object_identity_domains():
    graph = read(ROOT / "metadata/object-identities.json")
    return {"source": source("metadata/object-identities.json"),
            "native": source("native/object_identities.h"),
            "resources": [{k: r[k] for k in ("kind", "view", "positions")} for r in graph["resources"]],
            "callback_roles": [{k: r[k] for k in ("family", "role")} for r in graph["callbacks"]],
            "graph_links": [{k: v for k, v in r.items() if k != "word"} for r in graph["links"]],
            "scope": "Stable resource views, relative admitted positions and enum roles only. Historical words occur only in the verification bindings. A registered role is not permission to invoke it in arbitrary state; direct callback transport remains outstanding."}


def assemble(previous=None):
    cs = certs(); ev = evidence(previous.get("evidence_snapshots") if previous else None)
    receipt_checks(cs, ev)
    if previous and previous.get("prefix_replay"):
        trace = previous["prefix_replay"]
    elif (OUT / "prefix-replay.json").exists():
        trace = read(OUT / "prefix-replay.json")["prefix_replay"]
    else:
        raise ValueError("prefix evidence absent: use the committed manifest snapshot or run --prefix-replay")
    if digest(trace) != PINS.get("prefix_replay"):
        raise ValueError("prefix replay snapshot pin mismatch")
    for cut in trace.values():
        if function_hash(ROOT / cut["source"]["path"], cut["function"]) != cut["source_function_sha256_normalized_tokens"]:
            raise ValueError("rejection source checkpoint changed: " + cut["checkpoint"])
    pack = ev["pack"]["snapshot"]
    fallbacks = fallback_sites()
    return {
        "schema": 1, "decision": "D5", "generator": "python verif/admission.py --generate",
        "scope": "Machine-checked admission inventory and source checkpoints. Does not implement runtime guards or prove the shipped entry graph complete. Full compatibility verifier contracts are retained.",
        "policy": {"production": "shipped-domain-only", "else": "Unsupported at the documented prefix, not implicit fallback or rollback",
                   "registry_rule": "Stable data IDs are distinct from callable roles. Preserved raw words are never implicitly tokens.",
                   "D1": "deterministic virtual 70 Hz", "D2": "synthetic calibrated counts", "D3": "validated data-only pack",
                   "D4": "seconds replaces only RNG word zero high byte; fixed replay option",
                   "runtime_enforcement": "Step 7 continuation: implement and test these gates; this manifest does not remove verifier services."},
        "certificate_inputs": {n: {"source": "metadata/closure/" + n + ".json", "semantic_sha256": semantic_certificate_hash(c)} for n, c in cs.items()},
        "policy_inputs": {path: text_hash(ROOT / path) for path in (
            "docs/port-contract.md", "docs/standalone-plan.md", "src/asm/GAME.ASM",
            "native/pixel_world.h", "native/actor_world.h", "native/enemy_world.h",
            "native/resource_catalog.c", "native/resource_world.h", "native/resource_world.c",
            "metadata/resource-world.json", "metadata/program-model.json", "port/resources.c",
            "native/object_identities.h", "native/object_identities.c", "native/object_identities.inc",
            "native/bridge/object_identities_bridge.c", "native/bridge/object_identity_bindings.inc",
            "metadata/object-identities.json", "tools/object_identities.py")},
        "model_storage_extents": {n: v["storage_extent"] for n, v in read(ROOT / "metadata/program-model.json")["variables"].items() if "storage_extent" in v},
        "evidence_snapshots": ev,
        "registry": {"resource_catalog": {"sprite": {"kind": 1, "indices": [0, 661]}, "codec": {"kind": 2, "indices": [0, 4]},
                                          "demo_effect": {"kind": 3, "indices": [0, 2]}, "source": source("native/resource_catalog.c")},
                     "resource_world": {"source": source("metadata/resource-world.json"),
                                        "schema": 1, "pack_family": 5,
                                        "views": read(ROOT / "metadata/resource-world.json")["views"],
                                        "workspace": read(ROOT / "metadata/resource-world.json")["workspace"]},
                     "pack_resources": pack["resources"],
                     "resource_groups": resource_groups(pack),
                     "object_identities": object_identity_domains(),
                     "storage_only_units": {"actor_world": "Verification retains raw transports; descriptor, callback, script and journey interpretation uses the object identity vocabulary. Callback execution transport remains a separate continuation.",
                                            "enemy_world": "Verification retains raw transports; descriptor, callback, animation and drop-list identities have the generated vocabulary. Sound-handle interpretation remains with the audio continuation.",
                                            "item_world": "Verification retains raw transports; item descriptors and callback roles have the generated vocabulary. Invocation through direct native services remains outstanding."},
                     "pack_scope": "Data availability, not code/callback permission; opaque_mutable resources stay mutable. No original words are production IDs.",
                     "unknown_model_extents": [r["name"] for r in pack["model_bindings"] if r["resource"] is None]},
        "units": unit_domains(cs, pack),
        "rejection_declarations": [{"unit": n, "source": source("metadata/closure/" + n + ".json", ptr), "declaration": v}
                                    for n, c in cs.items() for ptr, v in leaves(c)
                                    if not any(ptr.startswith("/" + x) for x in VOLATILE)
                                    and (re.search(r"reject|declin|unsupported|out.of.domain|out.of.contract", ptr, re.I)
                                         or isinstance(v, str) and re.search(r"reject|declin|unsupported|out.of.domain|out.of.contract", v, re.I))],
        "unsupported": rejection_edges(ev, trace) + fallbacks + explicit_unsupported_sites() + other_edges(),
        "retained_quirks": quirks(cs), "prefix_replay": trace,
        "counts": {"units": len(cs), "audio_declines": 188, "included_timing_declines": 32,
                   "literal_transfer_sites": len(fallbacks), "pixel_opaque_services": 2,
                   "existing_status_cuts": len(explicit_unsupported_sites()),
                   "pack_data_ids": len(pack["resources"]), "unresolved_allocation_names": 184},
    }


def check(manifest):
    errors = []
    registry = manifest.get("registry", {})
    resources = registry.get("pack_resources", [])
    tokens = {r["id"] for r in resources}
    if len(tokens) != len(resources):
        errors.append("duplicate resource token")
    groups = registry.get("resource_groups", {})
    for name, group in groups.items():
        if not group.get("token_ids") or not set(group["token_ids"]) <= tokens:
            errors.append("resource group has absent or invalid IDs: " + name)
    for unit in manifest.get("units", []):
        if not set(unit.get("resource_tokens", [])) <= tokens:
            errors.append("unit references unregistered resource token: " + unit["unit"])
        if not set(unit.get("indirect_resource_groups", [])) <= set(groups):
            errors.append("unit references unknown resource group: " + unit["unit"])
    ids = [x.get("id") for x in manifest.get("unsupported", [])]
    if len(ids) != len(set(ids)):
        errors.append("duplicate Unsupported identity")
    for row in manifest.get("unsupported", []):
        prefix = row.get("prefix")
        if not isinstance(prefix, dict) or not all(prefix.get(k) for k in ("checkpoint", "source", "semantics")):
            errors.append("Unsupported edge has no prefix: " + str(row.get("id")))
    wanted = assemble(manifest)
    actual_fallback = {r["id"] for r in manifest.get("unsupported", []) if r.get("kind") == "dormant_l1_guard"}
    expected_fallback = {r["id"] for r in wanted["unsupported"] if r["kind"] == "dormant_l1_guard"}
    if actual_fallback != expected_fallback:
        errors.append("unclassified fallback site: " + str(sorted(expected_fallback - actual_fallback)) + "; obsolete: " + str(sorted(actual_fallback - expected_fallback)))
    actual_rejections = [r for r in manifest.get("unsupported", []) if r.get("kind") == "audio_api_decline"]
    expected_rejections = [r for r in wanted["unsupported"] if r["kind"] == "audio_api_decline"]
    if actual_rejections != expected_rejections:
        errors.append("certificate rejection list and manifest disagree")
    # This also catches lost quirks, altered source expressions, domains and
    # receipt snapshots, not just the three required negative controls.
    for key in wanted:
        if key == "unsupported":
            remaining = lambda rows: [r for r in rows if r.get("kind") not in ("audio_api_decline", "dormant_l1_guard")]
            if remaining(manifest.get(key, [])) != remaining(wanted[key]):
                errors.append("other Unsupported policy inventory differs")
        elif manifest.get(key) != wanted[key]:
            errors.append("inventory differs: " + key)
    # Compare fallback contents too, so a newly empty predicate cannot pass.
    if [r for r in manifest.get("unsupported", []) if r.get("kind") == "dormant_l1_guard"] != [r for r in wanted["unsupported"] if r["kind"] == "dormant_l1_guard"]:
        errors.append("fallback source checkpoints differ")
    if errors:
        raise ValueError("\n".join(errors))
    return wanted["counts"]


def negatives(manifest):
    rows = []
    for name, mutate, required in (
        ("rejection-disagreement", lambda m: m["unsupported"].pop(0), "certificate rejection list"),
        ("unclassified-fallback", lambda m: m["unsupported"].remove(next(r for r in m["unsupported"] if r["kind"] == "dormant_l1_guard")), "unclassified fallback"),
        ("missing-prefix", lambda m: m["unsupported"][0].pop("prefix"), "has no prefix"),
        ("lost-quirk", lambda m: m["retained_quirks"].pop(), "retained_quirks"),
        ("changed-receipt-list", lambda m: m["evidence_snapshots"]["audio"]["snapshot"]["rejections"].pop(), ("evidence_snapshots", "receipt content")),
    ):
        bad = json.loads(json.dumps(manifest)); mutate(bad)
        save(OUT / "negative" / (name + ".json"), bad)
        try:
            check(bad)
        except ValueError as error:
            detail = str(error)
            choices = (required,) if isinstance(required, str) else required
            if not any(x in detail for x in choices):
                raise AssertionError((name, detail)) from error
            rows.append({"control": name, "result": "DETECTED", "diagnostic": detail})
        else:
            raise AssertionError("negative control survived: " + name)
    save(OUT / "negative-controls.json", {"result": "PASS", "controls": rows})
    return len(rows)


def bounded(command, label):
    """Serial child, 600 s and 8 GiB job limit; closing job kills descendants."""
    import ctypes as C
    from windows_job import WindowsJob, ExtendedLimits
    start = time.monotonic()
    with WindowsJob() as job:
        limits = ExtendedLimits()
        limits.basic.flags = 0x2000 | 0x100 | 0x200
        limits.process_memory = limits.job_memory = 8 * 1024 ** 3
        if not job.kernel.SetInformationJobObject(job.handle, 9, C.byref(limits), C.sizeof(limits)):
            raise C.WinError(C.get_last_error())
        proc = subprocess.Popen([str(x) for x in command], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        job.assign(proc)
        try:
            output = proc.communicate(timeout=600)[0].decode(errors="replace")
            result = "PASS" if proc.returncode == 0 else "FAIL_OR_MEMORY_CAP"
        except subprocess.TimeoutExpired:
            job.terminate(); output = proc.communicate()[0].decode(errors="replace"); result = "TIME_CAP"
        receipt = {"command": [str(x) for x in command], "result": result, "exit_code": proc.returncode,
                   "seconds": round(time.monotonic() - start, 3), "memory_limit_bytes": 8 * 1024 ** 3,
                   "wall_limit_seconds": 600, "output": output}
        save(OUT / (label + ".json"), receipt)
        if result != "PASS":
            raise ValueError(label + ": " + result + "\n" + output[-6000:])
        return receipt


def prefix_worker():
    """Replay accepted audio API declines, adding side-channel checkpoints only.

    Historical sources are intentionally frozen: no mixed process-refactor build
    and no maintained source edits. This identifies the *first* rejecting cut,
    and verifies the full recorded differential diagnostics are unchanged.
    """
    import ctypes as C
    import io
    import shutil
    import zipfile
    import difftest
    import nbuild
    from emu import Machine
    folder = OUT / "prefix-replay"; folder.mkdir(exist_ok=True)
    tree = folder / "accepted"
    archive = subprocess.check_output(["git", "archive", "--format=zip", "5107c51", "native", "c", "verif/projector"], cwd=ROOT)
    # Archive paths are repository-controlled. Extract only the named roots and
    # verify every resolved destination remains in this worker's private tree.
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for entry in z.infolist():
            target = (tree / entry.filename).resolve()
            if not target.is_relative_to(tree.resolve()):
                raise ValueError("unsafe archive path")
        z.extractall(tree)
    original_folder = ROOT / "build/workers/close-adlx-23/api/composed"
    generated = folder / "generated"; generated.mkdir(exist_ok=True)
    for path in original_folder.iterdir():
        if path.suffix in (".c", ".h"):
            shutil.copyfile(path, generated / path.name)
    api = read(ROOT / RECEIPTS["audio"])
    command_receipt = read(ROOT / "build/workers/close-adlx-23/children/api-composed-compile.json")
    def remap(value):
        # Old receipts escaped Windows separators twice; Path normalizes them.
        normalized = Path(value)
        if normalized.is_relative_to(original_folder):
            return str(generated / normalized.relative_to(original_folder))
        if normalized.is_relative_to(ROOT):
            return str(tree / normalized.relative_to(ROOT))
        return value
    command = [remap(x) for x in command_receipt["command"]]
    command[command.index("-o") + 1] = str(folder / "api.dll")
    verified_inputs = []
    for name, expected in api["profiles"]["composed"]["inputs"].items():
        original = ROOT / name
        target = Path(remap(str(original)))
        if target.exists() and target.suffix == ".c":
            actual = text_hash(target)
            if actual != expected:
                frozen = ROOT / "build/workers/close-adlx-23/projector/frozen" / name
                if frozen.exists() and text_hash(frozen) == expected:
                    shutil.copyfile(frozen, target)
                    actual = text_hash(target)
                else:
                    raise ValueError("historical source lock differs from accepted receipt: " + name)
            verified_inputs.append({"source": name, "sha256": actual})
    checkpoints = []
    for path in sorted((tree / "native").rglob("*")):
        if path.suffix not in (".c", ".h"):
            continue
        raw = path.read_text()
        if path.name == "audio_composition_api.h":
            raw = raw.replace("((void)(registers),UGH_UNSUPPORTED)",
                              "((void)(registers),admission_record(__FILE__,__LINE__,__func__,#name))")
        else:
            raw = re.sub(r"return\s+UGH_UNSUPPORTED\s*;", r'return admission_record(__FILE__,__LINE__,__func__,"Unsupported");', raw)
        path.write_text(raw, encoding="utf-8", newline="\n")
    header = folder / "trace.h"
    header.write_text("int admission_record(const char *,unsigned,const char *,const char *);\n", encoding="utf-8")
    trace_c = folder / "trace.c"
    trace_c.write_text('''#include <string.h>
static unsigned calls,line_number;
static char file_name[1024],function_name[128],reason[128];
__declspec(dllexport) void admission_trace_reset(void){calls=0;line_number=0;file_name[0]=function_name[0]=reason[0]=0;}
int admission_record(const char *file,unsigned line,const char *function,const char *why){
 if(!calls){strncpy(file_name,file,sizeof(file_name)-1);strncpy(function_name,function,sizeof(function_name)-1);strncpy(reason,why,sizeof(reason)-1);line_number=line;}calls++;return 1;
}
__declspec(dllexport) unsigned admission_trace_count(void){return calls;}
__declspec(dllexport) unsigned admission_trace_line(void){return line_number;}
__declspec(dllexport) const char *admission_trace_file(void){return file_name;}
__declspec(dllexport) const char *admission_trace_function(void){return function_name;}
__declspec(dllexport) const char *admission_trace_reason(void){return reason;}
''', encoding="utf-8", newline="\n")
    command += ["-include", str(header), str(trace_c)]
    bounded(command, "prefix-compile")
    dll = nbuild.load_l1(folder / "api.dll")
    for name in ("file", "function", "reason"):
        getattr(dll, "admission_trace_" + name).restype = C.c_char_p
    machine = Machine()
    cases = {(suite, case.title): case for suite in ("timer_system", "sound_api", "sound_engine") for case in difftest.load_suite(suite).CASES}
    traces = {}; results = []
    for row in api["explicit_out_of_domain"]:
        case = cases[(row["suite"], row["case"])]
        old_name = case.cfunc
        case.cfunc = "api_" + (old_name or "c_" + case.routine.split(":")[1])
        dll.admission_trace_reset()
        problems = difftest.run(case, machine, dll, row["poison"])
        case.cfunc = old_name
        if problems != row["problems"] or C.c_int.in_dll(dll, "api_status").value != row["status"]:
            raise ValueError("prefix instrumentation changed accepted differential: " + row["case"] + str(problems))
        count = dll.admission_trace_count()
        if count == 0:
            raise ValueError("unlocated rejection checkpoint: " + row["case"])
        path = Path(dll.admission_trace_file().decode()).relative_to(tree).as_posix()
        line = dll.admission_trace_line(); function = dll.admission_trace_function().decode()
        why = dll.admission_trace_reason().decode()
        original_text = subprocess.check_output(["git", "show", "5107c51:" + path], cwd=ROOT).decode()
        original_line = original_text.splitlines()[line - 1].strip()
        identity = digest([row["suite"], row["case"], row["poison"]])[:20]
        checkpoint = {"checkpoint": path + ":" + function + ":" + str(line), "source": source(path),
                      "revision": "5107c51", "line_hint": line, "expression": original_line,
                      "function": function, "reason": why, "first_of_reject_count": count,
                      "semantics": "Return Unsupported at this first rejecting composed adapter expression. Keep all prefix stores, register effects and services; no literal call, following tail or rollback.",
                      "precision": "Compiled checkpoint replay of the exact accepted fixture+poison; complete RAM/register/device differential diagnostics unchanged."}
        checkpoint["source_function_sha256_normalized_tokens"] = raw_function_hash(original_text, function)
        traces[identity] = checkpoint
        results.append({"suite": row["suite"], "case": row["case"], "poison": row["poison"],
                        "checkpoint": checkpoint, "status": row["status"], "differential_diagnostics": problems})
    result = {"result": "PASS", "revision": "5107c51", "count": len(results), "verified_c_inputs": verified_inputs,
              "instrumentation": "Only return-1 expression and AUDIO_LITERAL side-channel logging; first checkpoint captured. No game-state/device/log writes.",
              "prefix_replay": traces, "cases": results}
    save(OUT / "prefix-replay.json", result)
    print("PREFIX PASS", len(results), "cases,", len({r["checkpoint"]["checkpoint"] for r in results}), "source cuts")


def extents(manifest):
    """Proposal only: exact access views are not independent allocations."""
    model = read(ROOT / "metadata/program-model.json")
    layout = read(ROOT / "metadata/data-layout.json")
    ledger_path = "build/workers/close-adlx-24/cut-cells.json"
    schema_path = "build/workers/close-stones-25/projector/instrumented/schema.json"
    review_path = "build/workers/close-stones-24/provider-review.json"
    ledger = read(ROOT / ledger_path); schema = read(ROOT / schema_path); review = read(ROOT / review_path)
    cells = {row["name"]: row for group in ledger.values() for row in group}
    bindings = schema["bindings"]
    # Static symbols supplement the old cut ledger (which intentionally omitted
    # many code-segment variables). No candidate generation or shared writes.
    from cgen import read_symbols
    _, symbols = read_symbols()
    review_named = {r["name"]: r for r in review["named"]}
    load = 0x10100
    fields = []
    for module in layout["modules"]:
        base = load + module["frame"] * 16
        for obj in module["objects"]:
            for field in obj.get("fields", []):
                fields.append((base + field["start"], base + field["end"], module["name"], field))
    proposals = []
    for name in manifest["registry"]["unknown_model_extents"]:
        var = model["variables"].get(name, {})
        cell = cells.get(name, {})
        addresses = sorted(set(cell.get("addresses", [])) | {
            0x10100 + row["linear"] for symbol, row in symbols.items()
            if symbol.split(":")[-1] == name})
        accesses = []
        for sid in var.get("sites", []):
            site = model["sites"][sid]
            for memory in site.get("memory", []):
                if name in memory.get("symbols", []):
                    # For a nearest-label annotation use the actual operand,
                    # never a guessed distance to the next model name.
                    for expression in memory.get("segment_expressions", []):
                        frame = re.fullmatch(r"frame:([0-9A-Fa-f]+)", expression)
                        if frame and not memory.get("indexed"):
                            a = load + int(frame[1], 16) * 16 + int(memory["displacement"], 16)
                            if a not in addresses:
                                addresses.append(a)
                    accesses.append({"site": sid, "width": memory.get("width"), "indexed": memory.get("indexed"),
                                     "operand": memory.get("operand"), "segment_values": memory.get("segment_values", []),
                                     "displacement": memory.get("displacement"), "segment_expressions": memory.get("segment_expressions", []),
                                     "source_offset_hints": memory.get("source_offset_hints", [])})
        exact = [b for b in bindings if b["address"] in addresses]
        containing = [b for b in bindings if any(b["address"] <= a < b["address"] + b["width"] for a in addresses)]
        classified = review_named.get(name)
        proposal = {"name": name, "addresses": addresses, "model_readers": var.get("readers", []),
                    "model_writers": var.get("writers", []), "model_complete": var.get("complete", False),
                    "static_accesses": accesses, "conditional_segment_sites": var.get("conditional_segment_sites", []),
                    "source": [ledger_path, schema_path, "metadata/data-layout.json", "metadata/program-model.json"],
                    "kind": "unknown", "extent": None,
                    "reason": "No independent allocation proved. Conditional segments or indexed use must not be converted into a nearest-label bound."}
        if classified:
            proposal.update(kind="reviewed_view", extent=classified.get("size"),
                            reason=classified.get("reason", "Accepted provider view, not necessarily a disjoint allocation."),
                            classification=classified.get("classification"),
                            census=classified.get("observed_writes", []))
            proposal["source"].append(review_path)
        elif exact:
            b = exact[0]
            proposal.update(kind="typed_field_view", extent=b["width"],
                            reason="Typed field access view " + b["field"] + "; this is an interior/alias view, not a new independent allocation.",
                            typed_views=[{k: b[k] for k in ("field", "address", "width")} for b in exact])
            # A strided alias is not one contiguous allocation. Keep the exact
            # cells rather than granting the bounding hull to this model name.
            if "[" in b["field"]:
                family = re.sub(r"\[\d+\]", "[*]", b["field"], count=1)
                siblings = [v for v in bindings if re.sub(r"\[\d+\]", "[*]", v["field"], count=1) == family]
                if len(siblings) > 1:
                    proposal["view_shape"] = {"field_pattern": family, "elements": len(siblings),
                                              "cells": [[v["address"], v["width"]] for v in siblings],
                                              "meaning": "Exact noncontiguous field cells, not intervening bytes or a new allocation."}
        elif containing and accesses and all(not x["indexed"] for x in accesses):
            width = max(x["width"] for x in accesses)
            if any(b["address"] <= addresses[0] and addresses[0] + width <= b["address"] + b["width"] for b in containing):
                proposal.update(kind="typed_interior_access_view", extent=width,
                                reason="Static operand width inside typed field " + containing[0]["field"] + "; no independent allocation or remaining-tail extent inferred.",
                                typed_views=[{k: b[k] for k in ("field", "address", "width")} for b in containing])
        elif len(addresses) == 1:
            match = [r for r in fields if r[0] <= addresses[0] < r[1]]
            if match:
                a, b, module, field = min(match, key=lambda r: r[1] - r[0])
                # A multi-element declaration only proves the containing object;
                # we never grant its remaining bytes to an interior scalar label.
                proposal.update(kind="declared_container_only", extent=None,
                                container={"module": module, "start": a, "end": b, "declaration": field},
                                reason="Static declaration bounds the containing field, not this model name's independent allocation. Access width is reported separately; no tail extent guessed.")
            if accesses and all(not x["indexed"] for x in accesses):
                proposal.update(kind="static_operand_view", extent=max(x["width"] for x in accesses),
                                reason="Exact scalar access address and maximum actual operand width; a bounded access view only, not an independently allocated object. Any declaration container remains separately recorded.")
        if name in ("IceDecodeWorkspace", "ext_0A67"):
            proposal.update(kind="overlapping_scratch_window", extent=65536,
                            reason="Static ZERO reservation is 64768 bytes. Accepted full-window ICE borrow is 65536 bytes, including four seeded audio bytes, twelve padding bytes and the first 752 packed-map bytes. The 64 KiB borrow is not a disjoint allocation.",
                            nominal_allocation=64768,
                            source=proposal["source"] + ["metadata/closure/ice_scratch.json", "metadata/closure/resource_catalog.json"])
        if name == "PlayerAnimationCycleEnds":
            proposal.update(kind="overlapping_animation_view", extent=4,
                            reason="Two-word end view at 0CFC overlaps player two's start. Three physical boundary words total; do not allocate separate start/end arrays.",
                            source=proposal["source"] + ["native/bridge/player_world_bridge.c", "metadata/closure/player_world.json"])
        if name == "AudioChannelStates":
            proposal.update(kind="declared_record_array", extent=13 * 42,
                            reason="Thirteen 42-byte physical channel records, including main record 12. Native AudioChannel pointers do not determine the transport stride. Interior MainAdlx aliases share this one array; do not allocate them again.",
                            source=proposal["source"] + ["native/audio.h", "native/bridge/audio_projection.h", "src/asm/SOUND.ASM"])
        if name.startswith("IceMatch"):
            suffix = {"IceMatchLengthBitCountsMinusOne": (40, 5, 1), "IceMatchLengthBiases": (45, 5, 1),
                      "IceMatchOffsetBitCountsMinusOne": (50, 3, 1), "IceMatchOffsetBiases": (54, 6, 2)}[name]
            proposal.update(kind="biased_codec_subview", extent=suffix[1],
                            reason=f"Registered codec subview: offset {suffix[0]} in 60-byte block, first logical index -1, entry width {suffix[2]}; the symbol anchor is not an independent allocation.",
                            source=proposal["source"] + ["native/resource_catalog.c"])
        proposals.append(proposal)
    if len(proposals) != 184 or len({r["name"] for r in proposals}) != 184:
        raise ValueError("extent inventory is not exactly 184 unique names")
    save(OUT / "extents.json", {"result": "PROPOSAL_ONLY", "count": len(proposals), "proposals": proposals})
    lines = ["# Allocation extent proposals (not applied)", "", "All 184 unresolved model names from the accepted pack audit are listed once. Hex addresses below are verification linear coordinates, not proposed port identities.", "",
             "A scalar or strided field view does not establish an independent allocation. `unknown` and container-only rows deliberately do not claim an extent. Census writer sets are lower bounds from the 20 maintained scenarios, 81 openings, seven audio and eight deep runs; absence of an observed writer proves neither constness nor extent. Static model `complete=false` remains explicit.", "",
             "The full static access sites, conditional segments, writer/reader sets, typed field identities, review classifications and available census records are in `extents.json`. Provider review and old projector coordinates are evidence, not a claim about current ownership.", "",
             "| Name | Proposed view bytes | Classification | Evidence and limitation |", "|---|---:|---|---|"]
    for row in proposals:
        detail = row["reason"].replace("|", "\\|")
        if row.get("view_shape"):
            shape = row["view_shape"]
            detail += f" Strided field: {shape['elements']} elements of {row['extent']} bytes; only the enumerated cells are proposed."
        coords = ",".join(f"{a:05X}" for a in row["addresses"]) or "unresolved segment/address"
        lines.append(f"| `{row['name']}` | {row['extent'] if row['extent'] is not None else 'unknown'} | {row['kind']} | {coords}: {detail} |")
    lines += ["", "Counts: " + ", ".join(f"{k}={v}" for k, v in sorted(collections.Counter(r["kind"] for r in proposals).items())), "",
              "Proposal: retain aliases as views of their canonical allocation; do not append 184 guessed allocation records. Resolve remaining unknowns only with an exact declaration or a proven bounded access contract. No program-model edit is included.", ""]
    (OUT / "EXTENTS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return collections.Counter(r["kind"] for r in proposals)


def main():
    global USE_SNAPSHOT
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("generate", "check", "negative", "extents", "all", "prefix-replay", "prefix-worker"):
        parser.add_argument("--" + flag, action="store_true")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--receipt-mode", choices=("available", "snapshot"), default="available",
                        help="snapshot tests the self-contained clean-checkout evidence path")
    args = parser.parse_args()
    USE_SNAPSHOT = args.receipt_mode == "snapshot"
    if args.prefix_worker:
        prefix_worker()
        return 0
    if args.prefix_replay:
        bounded([sys.executable, Path(__file__), "--prefix-worker"], "prefix-worker")
        return 0
    if not any((args.generate, args.check, args.negative, args.extents, args.all)):
        args.check = True
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        prior = read(args.manifest) if args.manifest.exists() else None
        if args.generate or args.all:
            value = assemble(prior); save(args.manifest, value)
        else:
            value = prior
        if value is None:
            raise ValueError("manifest absent: run --generate with accepted receipts present")
        receipt = {"result": "PASS", "command": "python verif/admission.py " + " ".join(sys.argv[1:]), "counts": check(value)}
        if args.negative or args.all:
            receipt["negative_controls"] = negatives(value)
        if args.extents or args.all:
            receipt["extent_proposals"] = dict(extents(value))
        save(OUT / "check.json", receipt)
        print(json.dumps(receipt, sort_keys=True))
    except (ValueError, KeyError, AssertionError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
