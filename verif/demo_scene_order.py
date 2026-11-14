"""Real L0/native callbacks and returns; observers only, no runtime RAM hooks."""
import ctypes as C,dataclasses,json,struct,sys
from closure_support import ROOT,receipt,save
from demo_scene_build import OUT,build,FILES
import contacts_reference
contacts_reference.OUT=OUT/'reference'
from contacts_reference import prepare_reference
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,cgen
from emu import DATA_SEG

def main():
    plain=prepare_reference(local=True);dll=nbuild.load_l1(build());machine=difftest.Machine();scene=difftest.load_suite('scene');composition=difftest.load_suite('menu').composition_fixture
    cases=[];expected_flags={}
    def setup(m,scan=None,empty=False):
        composition(m)
        for name,value in [('ScreenFadeLevel',0x1234),('ScreenFadeStep',0x1357),('DemoExitCode',0x5678)]:m.ww('DGROUP:'+name,value)
        if empty:m.write(DATA_SEG,0x6000,b'\xff\xff')
        if scan is not None:
            buttons=m.device._script(0x201);buttons.count=1;buttons.cursor=buttons.used=0;buttons.cycles=buttons.cycles_left=1000;buttons.runs[0].value=255;buttons.runs[0].repeat=1
            s,o=m.address('GAME:HandleKeyboardScanInterrupt');m.write(0,0x24,struct.pack('<HH',o,s));m.device.script(0x60,[scan])
            m.device.schedule(m.seg('GAME:PollKeyboardScanChange'),m.off('GAME:PollKeyboardScanChange'),irq=1,skip=1)
    out=scene.GENERAL+('CF','PF','ZF','SF','OF','IF','DF')
    for name,scan,empty,exit_word in [('early-callback-button',None,False,0),('interrupted-Q',16,False,65535),('interrupted-Escape',1,False,1),('completed-empty',None,True,0)]:
        def check(m,r,name=name,exit_word=exit_word):
            assert m.rw('DGROUP:DemoExitCode')==exit_word,(name,'exit word')
            assert bool(r['FLAGS']&0x80)==bool(exit_word&0x8000) and bool(r['FLAGS']&0x40)==(exit_word==0),(name,'SF/ZF')
            expected_flags[name]=r['FLAGS']
        cases.append(difftest.Case(name,'GAME:RunScriptedDemo',setup=lambda m,scan=scan,empty=empty:setup(m,scan,empty),regs=lambda m,empty=empty:dict(DS=DATA_SEG,SI=0x6000 if empty else m.off('DGROUP:DemoTable_1792')),check=check,out_regs=out,budget=30000000))
    for entry in ['PlaySpriteRevealDemo','PlayPreGameDemo','PlayAttractDemo','PlayGameCompletionDemo']:
        template=next(c for c in scene.CASES if c.routine=='GAME:'+entry and 'real tables button exit' in c.title)
        def check(m,r,entry=entry):
            expected_flags[entry]=r['FLAGS']
            if entry=='PlaySpriteRevealDemo':
                assert m.rw('DGROUP:ActorX32')==0
                address=m.rw('GAME:DemoRevealWidthPointer');bank=m.rw('GAME:DemoRevealWidthPointer',2);assert m.read(bank,address,1)==b'\x7f'
        cases.append(dataclasses.replace(template,title=entry,setup=lambda m:setup(m),check=check))
    _,symbols=cgen.read_symbols();names=['InitializeDemoScripts','AdvanceDemoScripts','StartDemoFadeWhenSpriteHidden','SetDemoRevealSpriteWidth','IgnoreActorState','PollKeyboardScanChange','SampleJoystickAxesAndButtons','TestAllDemoScriptsFinished','RunScriptedDemo']
    addresses={(cgen.LOAD+symbols['GAME:'+n]['frame'],symbols['GAME:'+n]['offset']):n for n in names};memory=dll.ugh_memory().contents
    def word(bank,address):p=bank*16+address;return memory[p]|(memory[p+1]<<8)
    bases=[symbols['DGROUP:'+n]['offset'] for n in ['ScreenFadeLevel','ScreenFadeStep','DemoExitCode']];entry_log=[]
    callback_type=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs))
    def observe(bank,address,rp):
        name=addresses.get((bank,address))
        if name is None:return
        r=rp.contents;row=dict(entry=name,globals=[word(DATA_SEG,n) for n in bases],index=r.bx,handler_return=word(r.ss,r.sp),flags=r.flags)
        if name=='SetDemoRevealSpriteWidth' and row['handler_return']==symbols['GAME:PlaySpriteRevealDemo']['offset']+0x13:row['cleanup_saved_flags']=word(r.ss,(r.sp+2)&65535)
        entry_log.append(row)
    callback=callback_type(observe);dll.ugh_set_entry_observer.argtypes=[callback_type];rows=[]
    try:
        dll.ugh_set_entry_observer(callback)
        for case in cases:
            for poison in [False,True]:
                entry_log.clear();problems=difftest.run(case,machine,dll,poison);assert not problems,(case.title,poison,problems)
                copied=[dict(r) for r in entry_log]
                if case.title in ['early-callback-button','interrupted-Q','interrupted-Escape']:
                    first=next(i for i,r in enumerate(copied) if r['entry'] in ['StartDemoFadeWhenSpriteHidden','SetDemoRevealSpriteWidth','IgnoreActorState'])
                    poll=next(i for i,r in enumerate(copied) if r['entry']=='PollKeyboardScanChange');assert first<poll and copied[first]['globals']==[0x1234,0x1357,0x5678],case.title
                    assert copied[poll]['globals']==[0,4,0],case.title
                if case.title=='completed-empty':assert not any(r['entry']=='SampleJoystickAxesAndButtons' for r in copied)
                if case.title=='PlaySpriteRevealDemo':
                    cleanup=[r for r in copied if 'cleanup_saved_flags' in r];assert len(cleanup)==1
                    assert cleanup[0]['cleanup_saved_flags']&0xec5==expected_flags[case.title]&0xec5,'returned flags survive cleanup'
                rows.append(dict(case=case.title,poison=poison,result='PASS',entries=copied,return_flags=expected_flags[case.title]));print('PASS',case.title,poison,flush=True)
    finally:dll.ugh_set_entry_observer(callback_type())
    save(OUT/'order.json',receipt(['python','verif/demo_scene_order.py'],[__file__,*FILES,ROOT/'verif/demo_scene_build.py',ROOT/'tests/scene.py',ROOT/'tests/menu.py',ROOT/'tools/difftest.py',plain],result='PASS',cases=rows,build=json.loads((OUT/'build.json').read_text()),scope='Sixteen L0/native cases with observer-only actual callbacks/services; Q/Escape are IRQ keyboard inputs, completed empty uses an accessible empty vector and explicit child-core compatibility. No runtime simulation-memory patches.'))
if __name__=='__main__':main()
