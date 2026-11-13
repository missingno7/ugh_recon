"""Seed retained-quirk defects in scratch code; require compiled tests to fail."""
import argparse,ctypes as C,json,subprocess,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from demo_build import OUT
MUTANTS={
    'unsigned-delta':('demo_core.c','value<128 ? (int)value : (int)value-256','(int)value','demo_word_cases'),
    'zero-period':('demo_core.c','slot->countdown=slot->script->period;','slot->countdown=slot->script->period ? slot->script->period : 1;','demo_word_cases'),
    'stop-unpinned':('demo_core.c','slot->cursor-=2;','slot->cursor+=0;','demo_word_cases'),
    'history-cleared':('demo_core.c','scene->slots[i].sprite=ACTOR_HIDDEN_SPRITE;',
        'render->slots[i].pixel_x=render->slots[i].pixel_y=0; scene->slots[i].sprite=ACTOR_HIDDEN_SPRITE;','demo_cross_mode'),
    'all-aliases-live':('actor_resources.c','valid[phase] : 0','(valid[phase] | 63u) : 0','demo_alias_checks')}
def child(name):
    import demo_build,contacts_reference
    contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True)
    folder=OUT/'mutants'/name;folder.mkdir(parents=True,exist_ok=True)
    filename,old,new,test=MUTANTS[name];source=ROOT/'native'/filename;raw=source.read_text();assert raw.count(old)==1
    changed=folder/filename;changed.write_text(raw.replace(old,new));demo_build.OUT=folder
    demo_build.SOURCES=[changed if p==source else p for p in demo_build.SOURCES]
    sys.path.insert(0,str(ROOT/'tools'));import difftest,nbuild
    dll=nbuild.load_l1(demo_build.build());machine=difftest.Machine();machine.reset()
    difftest.load_suite('menu').composition_fixture(machine)
    C.memmove(dll.ugh_memory().contents,machine.snapshot(),len(dll.ugh_memory().contents));dll.ugh_devices_reset()
    result=getattr(dll,test)();assert result<0,(name,result)
    save(folder/'result.json',receipt([sys.executable,'verif/demo_mutants.py','--case',name],
        [Path(__file__),source,changed,ROOT/'verif/demo_harness.c'],result='DETECTED',test=test,returncode=result,
        build=json.loads((folder/'build.json').read_text())))
    print(name,'DETECTED',test,result,flush=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=list(MUTANTS));a=p.parse_args()
    if a.case:return child(a.case)
    results=[]
    for name in MUTANTS:
        command=[sys.executable,str(Path(__file__)),'--case',name];run=subprocess.run(command,capture_output=True,text=True)
        print(run.stdout+run.stderr,flush=True);assert run.returncode==0
        results.append(json.loads((OUT/'mutants'/name/'result.json').read_text()))
    save(OUT/'mutants.json',dict(result='PASS',mutants=results))
if __name__=='__main__':main()
