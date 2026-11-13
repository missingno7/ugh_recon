"""Write this worker's review candidate; never promote administrative status."""
import json,sys
from pathlib import Path
from closure_support import ROOT
sys.path.insert(0,str(ROOT/'tools'))
import closure
from hazards_build import NAMES,OUT

def main():
    model=json.loads((ROOT/'metadata/program-model.json').read_text())
    native=['native/hazards.h','native/hazards.c','native/bridge/hazards_bridge.c']
    original=[dict(identity='GAME:'+n,address=model['routines']['GAME:'+n]['address'],l1='c_'+n) for n in NAMES]
    cert=dict(component='hazards',status='unanalyzed',proposed_status='boundary-established',
        original=original,native=dict(files=native,header='native/hazards.h',functions=['hazard_step','hazards_next']),
        purpose='Five-slot bird, Triopterus, Dino and finite reward-tree state machines; a single typed slot and ordered semantic effect projection.',
        interface=dict(inputs=['HazardEntry, HazardSlot, immutable HazardType geometry/handler identities and animation windows at the incoming cursor',
            'HazardWorld: two craft views, up to sixteen stone views, ten borrowed LevelPlatform records, player counts, water, score and fade',
            'Release entry receives a valid incoming stone index; audio completion supplies its opaque channel handle'],
            outputs=['Updated typed slot/shared state plus ordered semantic stores, typed tail, audio request and items_spawn arguments'],
            effects=['Score adds the unsigned descriptor score to a wrapping 32-bit score without multiplier',
                'Stone vertical reflection and optional sprite; selected craft kill fade, signed wrapped kick or force',
                'Tree release invokes the already-native item allocator through its bridge; audio stays an open L1 service'],
            preconditions=['Ordinary stable RAM; disjoint stack, immutable resources and mutable output spans; accessible operands',
                'Five aligned slots and descriptor sentinel at or before the sixth word; immutable descriptor list during a dispatch',
                'PlayerCount 0..2, PlayerArrayBytes 2 or 4; animation direction 0/2, launch target 0/1',
                'At most sixteen sentinel-terminated actors; patrol platform <10; finite animations have non-FFFF first frame',
                'Unknown descriptors/targets, output aliases, invalid indices and malformed sentinel walks use independent L1 compatibility']),
        callers=model['components']['hazards']['calls_in'],callees=['native contacts: contact_players/contact_stones','native falling items: items_spawn via c_SpawnFallingItem bridge',
            'open L1 audio: C:PlayAdlibEffect and C:StopAdlibTrackChannel'],
        indirect=dict(dispatch_site='013B:236F',classification='complete under immutable descriptor identities and bounded slot-list contract',
            targets=model['indirect_sites']['013B:236F']['targets'],
            note='Descriptor handler fields +08..20 all remain explicit, including zero and no-op entries. H_TRIO_IMPACT is callable but bypassed by the shipped impact initializer.'),
        memory=dict(owned='Enemy counters/cadence/animation cursor/state and five-slot hazard simulation projection; descriptor, resource and placement storage borrowed',
            shared='Actor stone motion/sprite, craft position/velocity/platform, score and fade are shared views. Rendering owns draw caches; tree initializer writes through the projection.',
            retained='Unwritten stale fields, flight sound handle, and bird-list/tree-reward-list phase union remain explicit in the bridge. No lives write occurs in any hazard routine.'),
        assumptions=['No arbitrary interrupt interleaving during one semantic step; audio and item APIs obey their existing boundaries.',
            'Animation windows describe the actual immutable first/next operands; coincident sample addresses must agree.',
            'Bridge computes native stores once and consumes them in order. Instruction expressions reconstruct the complete register/flag shell and never supply persistent store values (except the external audio return).'],
        eliminated=['Machine addresses and register/flag state from the ordinary native module; typed handler enum replaces near addresses.',
            'Parallel-array layout becomes one shared HazardSlot; contact predicates and level/geometry types are reused without extensions.'],
        retained=['Equality-only predecrement timers wrap zero; DOS constants warning70, alert140, stun350, tree210, cadence4/5/6/15.',
            'Triopterus impact initializes ordinary recovery, preserving the DOS routing difference.',
            'Bird contact only on tick expiry, target toggle/clamps and signed wrapped boundaries; falling counter saturates only under signed <40.',
            'Patrol tick-only movement, unclipped reversal; charge acceleration direction-1, wrapped SHL5/SHL4 kick and platform detachment.',
            'Dino retries on byte-index equality to PlayerCount, origin-adjusted rectangle, +/-41 raw force and direction from animation cursor <5.',
            'Tree cached-coordinate SHL5 bug, sixth-update contact, NEG/SAR reflection, stone-origin launch, reward advancement after successful allocation, delayed exhaustion.'],
        evidence=[dict(property='Boundary inventory',level='C',method='Maintained source and program-model review; mechanical include/call inventory',
            command='python tools/closure.py',result='Pending final review',date='2026-11-13')],
        amiga=dict(classification='Shared design with confirmed DOS differences; no DOS byte proof',
            findings='Bird/Triopterus/Dino scores 2500/1400/800 and finite tree order correspond. DOS timers and flight/force/kick algorithms prevail; docs/amiga.md earlier 150-delay summary is contradicted by its later source correction and the actual 70/140 constants.'),
        uncertainty=['Administrative status belongs to the supervisor. Symbolic proof and host review results are added after execution; no promotion is made by this generator.',
            'Malformed/aliased machine states remain compatibility paths; native C does not claim to replace those unbounded memory walks.'],
        dependencies={name:closure.actual_dependencies(ROOT/name) for name in native})
    (ROOT/'metadata/closure/hazards.json').write_text(json.dumps(cert,indent=2)+'\n')
if __name__=='__main__':main()
