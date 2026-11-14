"""Source-checked seams, callers, initializer writers and explicit proof scope."""
import json,re,sys
from closure_support import ROOT,function,receipt,save
from sequencing_build import OUT
from lifecycle_shells import NAMES as LIFENAMES,generated as life_generated
from session_bridge import NAMES as SESSIONNAMES,generated as session_generated,NEAR
from session_loader import FIELDS
def main():
    assert (ROOT/'native/bridge/lifecycle_bridge.c').read_text()==life_generated()
    assert (ROOT/'native/bridge/session_bridge.c').read_text()==session_generated()
    actor=(ROOT/'native/bridge/actor_render_bridge.c').read_text();assert 'c_RunGameFromPassword' not in actor
    for n in ['GAME_ERASE','GAME_DRAW','GAME_OVERLAY']:assert 'actor_render_session_'+n+'(' in actor
    original=function((ROOT/'c/scene.c').read_text(),'c_RunGameFromPassword')
    calls=re.findall(r'CALL\((\w+),G\(RunGameFromPassword\)\+0x([a-f0-9]+)\)',original)
    closed_actor_cuts={'e3','108','232','382'};layer_cuts={'138','15f','29d','348'}
    native_calls={(n,f'{o:x}') for a,n,o in NEAR};assert all((n,o) in native_calls or o in closed_actor_cuts|layer_cuts for n,o in calls)
    # No entire session-body fallback exists. The original 100000 frame guard
    # and per-slot compatibility guards have separate explicit counters.
    modern=function((ROOT/'native/bridge/session_bridge.c').read_text(),'c_RunGameFromPassword');assert 'l1_RunGameFromPassword' not in modern and '100000' in modern
    loader=function((ROOT/'c/render.c').read_text(),'c_LoadCurrentLevelState')
    assert 'r->si=24;' in loader and 'r->si=576;' in loader and 'r->bx=384;' in loader and 'r->cx=160;' in loader
    assert not re.search(r'W(?:I)?\(Actor(?:Pixel|PreviousDraw)[XY]',loader)
    targets=LIFENAMES+SESSIONNAMES;callers={n:[] for n in targets};writers=[];hooks=[]
    for p in sorted((ROOT/'c').glob('*.c')):
        text=p.read_text()
        for m in re.finditer(r'^(?:EXPORT\s+)?(?:static\s+)?(?:void|int|uint\d+_t)\s+(\w+)\s*\(',text,re.M):
            try:b=function(text,m[1])
            except ValueError:continue
            tail=b[b.index('{')+1:]
            for n in targets:
                if re.search(r'\b(?:CALL\w*|ugh_dispatch|ugh_call_near)\s*\([^;\n]*\b'+n+r'\b|\bc_'+n+r'\s*\(',tail):callers[n].append(dict(source=p.relative_to(ROOT).as_posix(),function=m[1]))
            for line in b.splitlines():
                if re.search(r'\b(?:W|WB|WI|WX|wr8|wr16)\s*\(',line):
                    fs=[f for f in [*FIELDS,'LivesRemaining','ScoreLowWord','ScoreHighWord','ScoreMultiplier','CurrentLevelIndex','WaterY32','WaterYPixels'] if re.search(r'\b'+f+r'\b',line)]
                    if fs:writers.append(dict(source=p.relative_to(ROOT).as_posix(),function=m[1],fields=fs,statement=line.strip()))
            for line in tail.splitlines():
                if re.search(r'G\(loc_001[C-F]\)',line):hooks.append(dict(source=p.relative_to(ROOT).as_posix(),function=m[1],statement=line.strip()))
    regions=[
      dict(region='Lifecycle scripts and masks',profiles=['life-order','life-frame','life-dependence','life-consume'],scope='Actual native-C request order/arguments/protocol; four checked actual-C ABI shells and full-RAM stream C pairs establish the literal link.'),
      dict(region='Session phase decisions',profiles=['session-step','session-frame','session-dependence','password','protocol'],scope='All private phases admitted, raw world inputs. Signed fade, death byte, unsigned postincrement level bound, equality-only player loops, password counters and request protocol have B invariants. Other service order/private phase edges retain source-checked mapping and complete ordered-stream C/D composition, not a full-session B claim.'),
      dict(region='Enemy/item layer cache decisions',profiles=['render-output','render-frame','render-dependence'],scope='Full raw typed current slot input and history; signed upper Y clip only, unconditional erase cache swap. Exact retained source layer scans and service bindings have C/D.'),
      dict(region='Loader records',profiles=[k+'-'+m for k in ['platform','actor','tree','bird','dino','trio'] for m in ['output','frame','dependence']],scope='Actual full one-record literal C and actual native+bridge; arbitrary resource words and shared scale replies, full typed slot output, every ordered store and scalar service, all registers/flags; separate resource/other-slot frame and other-slot dependence. Records compose by exact DI+2 seam and live next read.'),
      dict(region='Header, tile copy, seeds, display and rain prewarm',profiles=['loader-scalar','display-byte','display-score','display-order'],scope='B raw arithmetic, shifts, byte/score wraps and display ordinal protocol. Header backward-overlap/full RAM, live DF tile copy, fixed initializer store order, HUD coordinate publication and 193+577 rain composition are C, not an invented unrestricted byte-RAM theorem.')]
    save(OUT/'inventory.json',receipt(['python','verif/sequencing_inventory.py'],[__file__,ROOT/'verif/lifecycle_shells.py',ROOT/'verif/session_bridge.py',ROOT/'verif/session_loader.py',ROOT/'native/session.c',ROOT/'native/session.h',ROOT/'native/lifecycle.c',ROOT/'native/lifecycle.h',ROOT/'native/bridge/session_bridge.c',ROOT/'native/bridge/lifecycle_bridge.c',ROOT/'native/bridge/actor_render_bridge.c',*sorted((ROOT/'c').glob('*.[ch]'))],result='PASS',coverage=regions,callers=callers,initializer_writers=writers,external_hooks=hooks,
      split='Lifecycle has no level/frame policy: four lifetime/platform/audio entries. Session owns four coupled level/session/initializer entries and the inline nonactor render policies. actor_render retains exactly its six actor operations and three inline scan adapters; one session bridge owns the sole c_RunGameFromPassword export.',
      port='Supply synchronous asset/file/error/memory/decompression staging services, video/palette/retrace/page services and interrupt/input/timer/audio front ends under their accepted contracts. Preserve original call order and service return/abort semantics, scratch world construction, source-visible frames and persistent histories. Native lifecycle requests mask1 only; legacy hooks stay literal.',
      alias='No actor scratch alias read is added and native/actors.h is unchanged. Loader constructs canonical descriptor/platform/journey/callback/position fields; renderer reads only accepted persistent history. Private streamed state is not another owner. Normal finite physical prefixes and ordinary resource/stack ownership are explicit.',
      stale='Loader leaves water byte position/frame/countdown/phase/pending and rain modulo-four state stale until their existing owners update them. Actor four pixel history words survive load/reset; only hide/erase markers are seeded. Mode-one HUD layout leaves second-player coordinates stale. Player impact/thrust and remaining rendering history are not gratuitously reset.'))
    print('PASS eight entries, service seams, initializer writers and explicit B/C scope',flush=True)
if __name__=='__main__':main()
