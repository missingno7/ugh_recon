"""Write only this work order's review certificates; never promote status."""
import hashlib,json,sys
from pathlib import Path
from closure_support import ROOT,save
sys.path.insert(0,str(ROOT/'tools'))
from closure import actual_dependencies
OUT=ROOT/'build/workers/close-demo'
DATE='2026-11-13'
ACTOR=['native/actors.h','native/actor_resources.h','native/actor_resources.c',
       'native/bridge/actor_projection.h','native/bridge/actor_resources_bridge.c']
DEMO=['native/demo_core.h','native/demo_core.c','native/bridge/demo_core_bridge.c']
def evidence(prop,level,method,command,result):
    return dict(property=prop,level=level,method=method,command=command,result=result,date=DATE)
def main():
    enumeration=json.loads((OUT/'enumeration.json').read_text())
    integration=json.loads((OUT/'integration.json').read_text())
    assert enumeration['result']==integration['result']=='PASS'
    common=dict(status='unanalyzed',status_reason='Only the supervisor sets an accepted status; this work order proposes review statuses.',
        assumptions=['Serialized ordinary RAM and stack; no device aliases, asynchronous mutation or self-modifying resources.',
          'Locked shipped resource bank, accessible initialized native storage, disjoint outputs and inputs, valid resource lifetimes.',
          'L0 is untouched. Actual-C A/B properties concern L1 -> L2 only; L0 -> L1 remains C/D differential evidence.'],
        amiga={'classification':'similar purpose with different implementation; script correspondence unresolved',
          'finding':'docs/actor-storage.md and docs/architecture-model.md give actor/journey and paired land/water meaning. No Amiga field offsets, capacities, bytecode or cache lifetimes are imported.'},
        observation_chain='L0 remains byte-exact under its existing gates; no L0 source was changed. This is a behavioural native closure, not an exact ASM/C contribution.')
    actors=dict(common,component='actor_types',proposed_status='verified-within-contract',
        proposed_status_reason='Finite shipped immutable descriptors/animations/itineraries/scripts and complete 21-phase x 6-alias table are enumerated on actual compiled code. No passenger implementation, generalized corrupt reference graph or alias-disjoint lifetime theorem is claimed.',
        original={'L0':['DGROUP descriptors 5C09:7720..7970, animation/journey references in all 81 level records',
          'DGROUP four demo vectors 5C09:1020/1792/1E40/24DE and 28 headers',
          'GAME:InitializeDemoScripts 013B:0AEB resource readers, GAME passenger/stone readers 013B:149C..2195'],
          'L1':['c/scene.c:c_InitializeDemoScripts','c/actors.c and c/actors_states.c phase-specific alias readers; remain L1'],
          'static_evidence':['docs/actor-storage.md completely, including accepted design and supervisor condition','docs/architecture-model.md','src/asm/GAME.ASM and src/data/DGDATA.ASM']},
        native={'files':ACTOR,'header':'native/actors.h; native/actor_resources.h',
          'functions':['actor_phase_aliases','actor_alias_value','actor_type_resource','demo_script_boundary'],
          'bridge':['actor_bridge_resources','actor_bridge_type','actor_bridge_journey','actor_bridge_level','actor_bridge_scripts','actor_bridge_script_cursor','actor_bridge_demo_project','actor_bridge_render_project','actor_bridge_alias_project','actor_bridge_alias_read'],
          'build':'python verif/demo_build.py'},
        purpose='Adopt only the accepted actor-specific shared vocabulary. Resolve immutable actor descriptors, animations, journeys and demo scripts over the existing level view. Keep gameplay and demo simulation separate and renderer history persistent; mechanically gate semantic aliases by phase.',
        interface={'inputs':['Eight exact descriptor identities, six sentinel-terminated animations per descriptor, paired identities; all shipped passenger journeys and placements, 28 script headers/code spans.',
          'Existing LevelDescription actor_count and the same source record for the additive ActorLevelStorage companion.',
          'A known phase and in-range actor index for narrow semantic-alias projection; renderer history imports every word for all sixteen physical slots.'],
          'outputs':['ActorType stable identity/geometry/animations/known tail scalars/pair, PassengerJourney legs/count; ActorLevelEntry type/platform/typed itinerary, leaving stone opaque tail in existing level view.',
            'DemoMotionScript ordinary code pointer/size/header scalars/effect, script-relative instruction offsets; DemoMotionScene active prefix with validated period and stored callback identity.',
            'Per-phase valid alias mask and checked accessor; invalid alias reads return zero without touching output. Invalid fields are poisoned in debug or ACTOR_VERIFY builds. Carrier 1 requires PlayerCount==2.'],
          'effects':['Read-only RAM projection; writes only caller-owned storage. Failures can leave partial private storage but publish no scene to the demo bridge.',
            'No level.h or level_projection.h change. New actor_projection.h is additive; actor_bridge_level enriches the same source level without altering its generic raw placement representation.'],
          'preconditions':['Contract is the finite shipped resource domain; no arbitrary synthetic pointer graphs. Bounded parser extensions reject unknown/capacity/malformed input.',
            'Original active prefix reserves an in-array sentinel, count<=15. Cursor must be an instruction boundary in its registered script; nonzero repeats require a same-script valid restart. Zero repeats leave the stale loop pointer unprojected.',
            'Copied demo period must equal header period; callback must match that header. Completion is 0/FFFF. Caller supplies the entry-known mode/phase, never infers one from sprite visibility.'],
          'alias_table':{'ACTOR_WAIT_FOR_PLATFORM':['journey_wait'],'ACTOR_PLATFORM_WAIT':['waiting_pose'],
            'ACTOR_DESTINATION_REQUEST':['request_ticks'],'ACTOR_QUESTION':['request_ticks'],
            'ACTOR_CARRIED_PASSENGER':['carrier'],'ACTOR_CARRIED_STONE':['carrier'],
            'ACTOR_THROWN_STONE':['horizontal_step'],'ACTOR_FLOATING':['floating_ticks'],
            'ACTOR_FLOATING_DESTINATION_REQUEST':['request_ticks'],'ACTOR_FLOATING_QUESTION':['request_ticks'],
            'all_other_phases':[]},
          'alias_enforcement':'actor_bridge_alias_project reads only members in actor_phase_aliases; debug/verification poisons the rest. actor_bridge_alias_read -> actor_alias_value validates before reading. Future passenger bridge readers must use this accessor. There is no passenger implementation in this unit.'},
        callers=['Demo core bridge imports scripts, typed scene and persistent renderer history.','Following passenger/stone closures can use the additive typed resource companion and checked alias projection.'],
        callees={'native':['level_object_geometry; local decoding/mask helpers'], 'bridge':['rd8/rd16; resource/type/boundary helpers; no machine callbacks executed']},
        indirect={'sites':[],'classification':'Stored descriptor code words deliberately remain in L1, outside ActorType. Demo callback identities map only to the complete three-valued effect enum, never one universal callback type.'},
        memory={'read':['Shipped descriptor data and referenced terminated animations; source level placements and passenger journeys; all 28 script headers/code bytes.',
          'Mode-specific active cursor/control/position/sprite arrays; renderer cache arrays D:2B2D/2B4D/2B6D/2B8D/2C0D/2C4D for every physical slot.',
          'Alias projection reads D:2A2D or D:2ACD only where phase-valid, plus PlayerCount for second carrier.'],
          'write':['Caller-owned projection storage only; no L1 RAM or devices.'],
          'owners':['Resources borrow immutable level ownership. ActorRenderStorage owns persistent history independent of GameplayActors and DemoMotionScene.'],
          'aliases':'Separate named gameplay scratch capacities are semantic aliases of retained cells. No whole-struct serialization. No union, mode reset or derived pixel-cache projection.'},
        eliminated=[{'detail':'Encoded pointers/code identities inside ordinary native types','evidence':'Only the bridge resolves machine identities; native APIs have pointers, resource indices and enums.'},
          {'detail':'Universal actor/demo record or union lifetime assumption','evidence':'Accepted three-object design, with cross-mode cached-pixel read tested on actual L1 gameplay draw.'}],
        retained=[{'detail':'Eight descriptor identities, including primary versus alternate stone and exact land/water pairs','reason':'Only primary stone participates in hazard queries; no family normalization.'},
          {'detail':'Animation words, journey waits, header periods and stale renderer history','reason':'Byte offsets/countdowns and old pixel values are observed by subsequent transitions/draw.'},
          {'detail':'Unknown descriptor +3A/+3C and placement tails','reason':'No established native meaning; skipped here and retained in existing immutable/raw level representation.'}],
        evidence=[evidence('Complete shipped resource projection','A','Actual compiled bridge/native; compare every type geometry/tail/pair/animation word and sentinel; all 150 ordered records, 493 placements and their complete passenger journeys; source RAM remains unchanged.',
          'python verif/demo_evidence.py enumerate --local-reference','PASS: 150 entries / 493 placements / eight descriptors and all their animations; 28 scripts fully enumerated in shipped-scripts.json.'),
          evidence('Complete phase/member validity table','A','Actual compiled projection/accessor, independently tabulated expected masks for all 21 phases x six members; invalid output remains untouched and invalid carrier rejected.',
          'python verif/demo_evidence.py enumerate --local-reference','PASS: 126 phase/member checks plus invalid carrier control.'),
          evidence('Persistent render history across normal mode switch','C','Native pre-game initialization, actual L1 first level load/bootstrap/reset/stone update, then verbatim extracted inline gameplay actor draw. Check slot 2 demo cache survives and becomes previous history before new stone pixels.',
          'python verif/demo_evidence.py enumerate --local-reference','PASS: slot 2 (320,106) persists through loader/bootstrap and is consumed by first gameplay draw; current cache then changes to stone position.'),
          evidence('Demo integration uses the resource projection','D','All maintained whole-game scenarios with bridged L1, full observation model and no fallback counters in reaching scenarios.',
          'python verif/demo_integration.py --whole --local-reference','PASS: 16 scenarios, native calls initialize/advance/completion = 22/574/568, fallback 0/0/0.')],
        uncertainty=['This introduces shared types, not a complete gameplay state projection or any passenger transition implementation. Phase input belongs to the eventual entry-specific bridge.',
          'Projection rejection extensions and arbitrary malformed resource graphs are outside the finite shipped-domain A claim. No source layout is inferred from the reproducing linker layout.'])
    demo=dict(common,component='demo_core',proposed_status='migrated',
        proposed_status_reason='Actual-C instruction-step and arithmetic proofs, full shipped-script enumeration, bounded full-tick proof, and C/D bridge integration. Full arbitrary-scene/initializer/shell equivalence is not mechanically proved, so no stronger whole-contract status is proposed.',
        original={'L0':['GAME:InitializeDemoScripts 013B:0AEB','GAME:AdvanceDemoScripts 013B:09D7','GAME:TestAllDemoScriptsFinished 013B:09BC'],
          'L1':['c/scene.c:c_InitializeDemoScripts','c/demo_scripts.c:c_AdvanceDemoScripts','c/game_services.c:c_TestAllDemoScriptsFinished'],
          'static_evidence':['docs/actor-storage.md closure unit 7 and complete callback table','src/asm/GAME.ASM actual entry/return sites and instruction readers/writers']},
        native={'files':DEMO,'header':'native/demo_core.h, shared native/actors.h','functions':['demo_initialize','demo_instruction','demo_advance_slot','demo_all_finished','demo_delta','demo_pixel_position'],
          'bridge':['c_InitializeDemoScripts','c_AdvanceDemoScripts','c_TestAllDemoScriptsFinished'],'build':'python verif/demo_build.py'},
        purpose='Initialize a motion scene, advance the demo bytecode interpreter and test sticky per-slot completion as one coherent core. Keep synchronous stored callback effects at their existing presentation boundary.',
        interface={'inputs':['Immutable registered script header/code resources, active prefix<=15, valid cursor/restart instruction boundaries, any repeat/countdown/position/sprite word and sticky completion bool.',
          'Separate ActorRenderStorage supplied at initialization; it is imported from persistent RAM and never reconstructed from positions.',
          'Bridge admits DS=DGROUP, CS=GAME, DF=0 and the registered reveal-width reference. Dynamic segments/reverse streams/unregistered resources/aliases/mutated periods use explicit L1 compatibility before publishing native state.'],
          'outputs':['Updated logical cursor/restart/repeat/countdown/completion/position/sprite and narrow DemoStep write/effect indicators.',
            'Completion boolean; bridge preserves actual CF result and deterministic full L1 flag/register shell. Initialize immediately resets sprites then steps before its runner clears fade/exit values.'],
          'effects':['Initialize seeds active current/previous pixel caches through ActorRenderStorage, fixed positions/header controls; leaves loop-start word stale. Reset touches all sixteen actor current/erase sprite words, not overlay/pixel history. Enemy/item reset contributions remain the actual L1 reset service.',
            'A due motion writes sprite, X, Y, invokes exactly its stored callback with original near return frame, then stores the cursor. Repeat/restart/done words are published only on paths that actually write them.',
            'Callbacks retain width-byte writes and fade effects in original slot order. Native computes private slot results first; known callbacks cannot mutate later interpreter inputs under the registered-width contract.'],
          'preconditions':['Ordinary nonaliasing stable RAM/stack and immutable registered resource bank; native object storage accessible and separate from code.',
            'Control walk must yield motion or stop within code_size+1 instructions; native rejects an overlong/out-of-range walk in private storage before bridge publication. Malformed/corrupt states outside this domain use retained L1.',
            'No assumption that repeat_count is negative or countdown/period is positive. Bridge validates completed word as 0/FFFF; completion scan also supports arbitrary nonzero raw completion for compatibility.',
            'demo_instruction is one bytecode transition, with accessible opcode/delta bytes; cursor/restart offsets are ordinary bounded buffer offsets. Its relational symbolic proof is independent of initialized/reachable script states.']},
        callers={'initialize':'RunScriptedDemo G:08D5, near call; callback effects occur before G:08D8 clears exit/fade.',
          'advance':'InitializeDemoScripts tail at G:0B4B and RunScriptedDemo G:0922 (erase -> interpret -> draw).',
          'finished':'RunScriptedDemo G:092B consumes CF; no AX boolean is invented.',
          'observations':'Advance/initialize: AX and callback CX/ES/DI flow through; BX=sentinel byte index, SI=FFFF, flags from final CMP. DX/BP/DS/CS/SS:SP and IF/DF survive admitted callbacks. Completion changes BX/CF/arith flags only. Routine suites compare full declared shell, including poisoned initial values.'},
        callees={'native':['demo_instruction','demo_delta','demo_pixel_position'],
          'bridge':['actor projection and resources','ugh_call_near for actual reset and three actual stored callbacks','retained l1_* compatibility endpoints']},
        indirect={'site':'GAME 013B:0A15, near stored demo callback',
          'targets':['GAME:StartDemoFadeWhenSpriteHidden 013B:0989 -> DEMO_EFFECT_FADE_ON_HIDDEN',
            'GAME:SetDemoRevealSpriteWidth 013B:099F -> DEMO_EFFECT_REVEAL_WIDTH','GAME:IgnoreActorState 013B:1C0E -> DEMO_EFFECT_NONE'],
          'classification':'Complete set from all 28 shipped headers. loc_0B4E is not a callback substitute; no new callback address is admitted. Actual handlers remain L1 presentation services, with the stored identity checked against header.'},
        memory={'read':['Cursor sentinel D:2A0D, countdown D:2BCD, copied period D:2C6D, repeat D:2ACD and live restart D:2A2D; position D:2AED/2B0D, sprite D:2BED, callback D:2C2D, completion D:2A4D.',
          'Initialize reads header vector and header/code resources, imports all sixteen render histories; completion scan biased D:2A4B after BX+=2 is this slot D:2A4D.'],
          'write':['Initialize active X/Y caches and previous caches D:2B2D/2B4D/2B6D/2B8D; fixed position, period, callback, cursor, countdown=1, repeat=0, done=0; cursor sentinel only at first unused slot.',
            'All sixteen current/erase sprites via reset; other histories untouched. Due step writes only described controls/position/sprite; callbacks may write ScreenFadeStep/Level or registered sprite-214 directory width byte, plus near-call stack scratch.'],
          'owners':['DemoMotionScene owns mode controls and sprite output; ActorRenderStorage owns persistent caches/erase words. Existing renderer/presentation owns width byte and fade. Gameplay view never flushes demo controls.'],
          'aliases':'No full slot dump. Inactive gameplay cells and dormant loop pointers stay unchanged; descriptor/itinerary/destination/platform indices, gameplay animation offset, quick timer and overlay erase are not demo outputs.'},
        eliminated=[{'detail':'Register model, segment pointers and code dispatch in native interpreter','evidence':'Ordinary resources, typed slots and returned DemoStep effects; only bridge binds original ABI and handlers.'},
          {'detail':'Array sentinel from ordinary core iteration','evidence':'Scene has explicit count; bridge separately validates and emits original in-array sentinel.'}],
        retained=[{'detail':'Predecrement countdown and period zero','reason':'Zero wraps to FFFF; a zero period reload is retained, not disabled.'},
          {'detail':'Signed-byte deltas x4 and word-shift initialization','reason':'Each position operation truncates to sixteen bits; negative odd/high-bound values are not normalized.'},
          {'detail':'Negative declaration, incrementing repeat encoding and sticky pinned stop','reason':'8000 increments nonzero repeat; zero repeats mark finished without removing the slot. Stopped slots still run cadence, and completion never means invisible.'},
          {'detail':'Callback order and actual near frame, width low byte/fade effects','reason':'Effects are synchronous after new sprite/position and before cursor store; reveal wrapper cleanup remains L1.'}],
        evidence=[evidence('Complete initialized trajectories of all shipped scripts','A','Actual compiled L1 and bridged native code for each of the 28 scripts, from header state with poisoned dormant loop pointer, through first completion and five extra ticks. Full RAM and complete register shell compared every tick.',
          'python verif/demo_evidence.py enumerate --local-reference',f'PASS: {enumeration["script_ticks"]} ticks across 28 scripts; complete header/opcode inventory in shipped-scripts.json. A only for this finite initialized trajectory domain, not every possible slot state.'),
          evidence('Complete countdown/period/repeat scalar slices and helpers','A','Actual L1/native compiled code over all 65536 countdowns, all 65536 periods including zero, all 65536 repeat encodings (including positive/8000/FFFF); all 65536 pixel seeds and 256 signed-byte deltas.',
          'python verif/demo_evidence.py enumerate --local-reference',f'PASS: {enumeration["word_cases"]} scalar/helper comparisons. Other inputs fixed as stated in demo_word_cases; not a full Cartesian word-state enumeration.'),
          evidence('Any admitted one-instruction slot transition','B','CBMC 6.11 actual production demo_instruction versus a verbatim extracted one-iteration L1 inner loop. Arbitrary opcode word, delta bytes, position/sprite/repeat words, sticky completion, restart offset; no initialized-state restriction. Normalized disjoint RAM and callback observation cut. Pointer/bounds/overflow/unwinding checks enabled.',
          'python verif/demo_evidence.py instruction --timeout 45','PASS: all properties. One instruction is the inductive loop transition; this is not a monolithic arbitrary-bytecode termination proof.'),
          evidence('Countdown gate and complete tick in a bounded control window','B','CBMC actual full L1 AdvanceDemoScripts and actual demo_advance_slot; all scalar slot states/periods, arbitrary first instruction, with accessible motion at fallthrough/restart. Full control walk bounded by structural window, not reachable initial states.',
          'python verif/demo_evidence.py tick --timeout 60','PASS: all properties under the documented 16-byte canonical control-window assumption. General-script composition relies on the separately proved instruction transition plus finite/script C/A evidence.'),
          evidence('Small arithmetic for all bit patterns','A','CBMC actual demo_delta and demo_pixel_position against exact L1 byte-sign-extension/shift expressions, arbitrary byte/word inputs, no range assumptions.',
          'python verif/demo_evidence.py arithmetic --timeout 30','PASS: all properties; compiled enumeration separately covers their complete finite domains.'),
          evidence('Insufficient unwinding negative control','C','Run the tick harness with unwind one; the real setup loop is intentionally under-unwound and must fail.',
          'python verif/demo_evidence.py tick --negative --timeout 30','PASS control: expected FAIL main.unwind.0, never a silently truncated success.'),
          evidence('L0 -> bridged L1 demo/caller regression','C','Maintained demo_scripts, scene and game_services suites with ordinary and poisoned register/flag inputs. Full memory/device/log observation model; synthetic/nonadmitted states use explicit L1 compatibility.',
          'python verif/demo_integration.py --whole --local-reference','PASS: demo_scripts 260/260, scene 484/484, game_services 44/44. Routine native endpoint calls [48,130,36], compatibility counts [30,78,8]; this includes intentionally synthetic/DF/dynamic-segment/alias fixtures.'),
          evidence('Whole-game composition and reaching demos','D','Actual wholegame.main with separately held bridged DLL reference, unchanged scenario fixtures/cached rebuilt-L0 observations and audited entry/fallback counts.',
          'python verif/demo_integration.py --whole --local-reference','PASS: all 16 scenarios; initialize/advance/completion calls [22,574,568], fallbacks [0,0,0]. Attract/reveal/pregame reach this closure; completion also reaches it.'),
          evidence('Explicit native-to-gameplay history handoff','C','Real L1 loader/bootstrap/reset/stone update and verbatim inline gameplay actor draw after native pre-game initialization, with renderer projection checks.',
          'python verif/demo_evidence.py enumerate --local-reference','PASS: pre-game slot 2 (320,106) survives into first stone draw and becomes previous history before current cache replacement.')],
        uncertainty=['A/B proof levels are property-specific. Full arbitrary-script tick termination, arbitrary active-scene composition, bridge register shell and initializer are not monolithic CBMC proofs; their general integration evidence remains C/D.',
          'Compatibility fallback is explicit for unregistered/malformed/corrupt streams, DF=1, dynamic segments, copied-period/callback mismatches and unregistered width references. No native proof is claimed for those paths.',
          'Presentation wrappers/draw/erase/reset and callback implementations remain L1. Their established ordering is retained; this does not close closure unit 8 or all render_hud.'])
    if (OUT/'mutants.json').exists():
        mutants=json.loads((OUT/'mutants.json').read_text());assert mutants['result']=='PASS'
        for cert in [actors,demo]:cert['evidence'].append(evidence('Seeded retained-semantics defects','C',
          'Compile scratch native mutations and run the actual scalar, cross-mode and alias-table tests; maintained native/L1 inputs remain unchanged.',
          'python verif/demo_mutants.py','PASS: unsigned delta, period-zero normalization, unpinned stop, cleared render history and all-aliases-live mutants all detected by compiled checks.'))
    if (OUT/'host.json').exists():
        host=json.loads((OUT/'host.json').read_text());assert host['result']=='PASS'
        for cert in [actors,demo]:cert['evidence'].append(evidence('Host review with scratch certificate promotion','D','Copy maintained sources and checked plain build under worker scratch, set only scratch actor_types/demo_core status=migrated; run unchanged CLI commands without selection/generation monkeypatches.',
          'python verif/demo_host.py -> python tools/hostbuild.py; python host/check.py --variant native','PASS: real native host build and unchanged host check in scratch; maintained status remains unanalyzed.'))
    inputs=[*ACTOR,*DEMO,'c/scene.c','c/demo_scripts.c','c/game_services.c','c/ugh.h','c/ugh_sym.h',
      'c/actors.c','c/abi.c','c/memory.c','c/dispatch.c','c/dispatch_table.inc','c/ugh_adapters.h','c/platform.c','c/platform.h',
      'native/level.h','native/level_view.c','native/geometry.h','native/bridge/level_projection.h','native/bridge/level_view_bridge.c',
      'metadata/oracle.json','metadata/verif-tools.json','src/asm/GAME.ASM','src/data/DGDATA.ASM',
      'verif/closure_support.py','verif/windows_job.py','verif/contacts_reference.py',
      'tools/difftest.py','tools/wholegame.py','tools/hostbuild.py','host/check.py',
      *[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'verif').glob('demo_*')) if p.suffix in ('.py','.c')]]
    for cert,owned in [(actors,ACTOR),(demo,DEMO)]:
        cert['dependencies']={name:actual_dependencies(ROOT/name) for name in owned}
        cert['verification_input_hashing']='sha256-lf-text'
        cert['verification_inputs']={name:hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in sorted(set(inputs))}
        path=ROOT/f'metadata/closure/{cert["component"]}.json'
        if path.exists():cert['status']=json.loads(path.read_text())['status']
        save(path,cert)
if __name__=='__main__':main()
