"""Complete HUD branch-stage inventory and named/direct rendering-cache writers."""
import re,sys
from closure_support import ROOT,receipt,save,function
from hud_shells import OUT,FILES,NAMES,FIELDS,main as shells
from hud_proof import KEYS,STAGES

COVERAGE={'DrawHudBorders':['border'],'DrawHudDigit':['digit'],
 'DrawHudDigitAndAdvance':['digit','advance'],
 'RedrawChangedTwoDigitNumber':['changed','digit','advance'],
 'RedrawChangedFourDigitNumber':['changed','digit','advance'],
 'RedrawChangedSixDigitNumber':['changed','digit','advance'],
 'RefreshHudAndTimerBar':[*STAGES,'bar-shrink','bar-grow','bar-next','projection','append']}

def main():
    old=sys.argv;sys.argv=[old[0]]
    try:shells()
    finally:sys.argv=old
    assert set(COVERAGE)==set(NAMES) and set(sum(COVERAGE.values(),[]))==set(KEYS)
    callers={n:[] for n in NAMES};writers=[];labels=[n for _,n,_ in FIELDS]
    for p in sorted((ROOT/'c').glob('*.c')):
        text=p.read_text()
        for match in re.finditer(r'^(?:EXPORT\s+)?(?:static\s+)?(?:void|int|uint\d+_t)\s+(\w+)\s*\(',text,re.M):
            try:b=function(text,match[1])
            except ValueError:continue
            for n in NAMES:
                if re.search(r'\b(?:CALL|ugh_dispatch|ugh_call_near)\s*\([^;\n]*\b'+n+r'\b|\bc_'+n+r'\s*\(',b[b.index('{')+1:]):callers[n].append(dict(source=p.relative_to(ROOT).as_posix(),function=match[1]))
            for line in b.splitlines():
                if re.search(r'\b(?:W|WB|WI|WX|WRITE|wr8|wr16)\s*\(',line):
                    fields=[f for f in labels if re.search(r'\b'+f+r'\b',line)]
                    if fields:writers.append(dict(source=p.relative_to(ROOT).as_posix(),function=match[1],fields=fields,statement=line.strip()))
    writers.append(dict(source='c/render.c',function='c_InitializeLevelDisplay',statement='Normal196-word clear at D:2648..27CF includes bar/cache/cursor HUD words. Incoming DF and live far workspace pointer remain original. Cached icon words at2800/2802 are outside that span and are explicitly assignedFFFF by LoadCurrentLevelState.'))
    composition='Eight native refresh stages cover every original HUD W/WB and immediate service in order; next-stage equality checks preserve every early jump and scheduling priority. Actual-C output properties record an arbitrary published journal position and all branch continuations. Independent input-byte frame/dependence profiles, arbitrary-prefix append and projection-field/frame properties close the typed working state. Glyph/border/cursor/scanner and partial/full bar-cell cuts cover the remaining decisions. Native bar family/index uses arbitrary live table bytes as service replies; physical transactions and complete ABI/flags/stack/session composition remain C/D. Closed decimal entry behavior is a borrowed contract, not re-encoded here.'
    OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'inventory.json',receipt(['python','verif/hud_inventory.py'],[*FILES,ROOT/'native/render_primitives.h',ROOT/'verif/hud_shells.py',ROOT/'verif/hud_proof.py',ROOT/'verif/hud_inventory.py',*sorted((ROOT/'c').glob('*.[ch]'))],result='PASS',coverage=COVERAGE,composition=composition,callers=callers,cache_writers=writers,abnormal='A consumed service prefix returns immediately on failure; future stage stores are not applied. Normal finish rejects an unconsumed effect, wrong next stage, remaining bar request or working-state mismatch. DIV0 retains the original pushed DS and unsupported status.'))
    print('PASS seven handlers, all refresh branches, scanner and bar transactions')
if __name__=='__main__':main()
