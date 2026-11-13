"""Two real DLLs and actual pixel services across demo -> first stone pages."""
import ctypes as C,json,os,sys
from closure_support import ROOT,compile_c,function,receipt,save
from render_history_build import OUT,build
from render_history_shells import gameplay_cuts
import contacts_reference
contacts_reference.OUT=OUT/'reference'
from contacts_reference import prepare_reference
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,cgen
DATA=cgen.LOAD+cgen.FRAMES['DGROUP'];GAME=cgen.LOAD+cgen.FRAMES['GAME']

def literal():
    folder=OUT/f'literal-{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);raw=(ROOT/'c/scene.c').read_text()
    text='#include "platform.h"\n'+'\n'.join(s for s in raw.splitlines() if s.startswith('#define '))+'\n'+function(raw,'sar')+gameplay_cuts()
    path=folder/'cuts.c';path.write_text(text);sources=[*sorted((ROOT/'c').glob('*.c')),path];dll=folder/'literal.dll';result=compile_c(sources,dll,[ROOT/'c'],['-shared']);return dll,result

def main():
    plain=prepare_reference(local=True);native_path=build();left_path,left_build=literal();native=nbuild.load_l1(native_path);left=nbuild.load_l1(left_path);machine=difftest.Machine();machine.reset();difftest.load_suite('menu').composition_fixture(machine)
    initial=machine.snapshot();rows=[]
    device_initial=machine.device.state()
    for dll in [left,native]:
        C.memmove(dll.ugh_memory().contents,initial,len(initial));dll.ugh_devices_reset()
        C.memmove(C.addressof(dll.ugh_device_state().contents),device_initial,len(device_initial))
    def word(dll,base,slot=0):
        memory=dll.ugh_memory().contents;p=DATA*16+base+2*slot;return memory[p]|(memory[p+1]<<8)
    def write(base,value):
        for dll in [left,native]:
            memory=dll.ugh_memory().contents;p=DATA*16+base;memory[p]=value&255;memory[p+1]=value>>8
    # Symbol names are read from the checked rebuilt symbol table.
    _,symbols=cgen.read_symbols();sym=lambda n:symbols['DGROUP:'+n]['offset']
    registers=[difftest.Regs(ds=DATA,cs=GAME,ss=0x9000,sp=0x1000,flags=0x202,ax=0x1357,cx=0x2468,di=0x3579,es=0x7500) for _ in range(2)]
    def call(name,**inputs):
        for r in registers:
            for n,v in inputs.items():setattr(r,n,v)
        status=[]
        for dll,r in zip([left,native],registers):
            fn=getattr(dll,name);fn.argtypes=[C.POINTER(difftest.Regs)];fn.restype=C.c_int;status.append(fn(C.byref(r)))
        assert status==[0,0],(name,status)
        assert bytes(registers[0])==bytes(registers[1]),(name,'registers')
        l=bytes(left.ugh_memory().contents);r=bytes(native.ugh_memory().contents)
        assert l==r,(name,'RAM',next((i for i,(a,b) in enumerate(zip(l,r)) if a!=b),None))
        assert bytes(left.ugh_device_state().contents)==bytes(native.ugh_device_state().contents),(name,'devices')
        rows.append(dict(call=name,slot2=[word(native,sym(n),2) for n in ['ActorPixelX','ActorPixelY','ActorPreviousDrawX','ActorPreviousDrawY','ActorEraseSprite','ActorEraseOverlaySprite']]))
    call('c_InitializeDemoScripts',si=0x1792)
    assert rows[-1]['slot2'][:4]==[320,106,320,106]
    write(sym('PlayerCount'),1);write(sym('CurrentLevelIndex'),0)
    call('c_LoadCurrentLevelState');call('c_DispatchActorUpdates');call('c_ResetSpriteEraseState')
    assert rows[-1]['slot2'][:4]==[320,106,320,106]
    call('c_UpdateStonePickupWait',bx=4);call('render_history_GAME_DRAW')
    assert rows[-1]['slot2'][2:4]==[320,106] and rows[-1]['slot2'][:2]!=[320,106]
    for _ in range(4):
        call('render_history_GAME_OVERLAY');call('c_SwapAndDisplayVgaPage');call('render_history_GAME_ERASE');call('c_DispatchActorUpdates');call('render_history_GAME_DRAW')
    audit=list((C.c_uint32*12).in_dll(native,'render_history_audit'));assert not any(audit[6:]),audit
    save(OUT/'cross-mode.json',receipt(['python','verif/render_history_cross_mode.py'],[__file__,ROOT/'verif/render_history_build.py',ROOT/'verif/render_history_shells.py',ROOT/'native/actor_render.c',ROOT/'native/actor_render.h',ROOT/'native/bridge/actor_render_bridge.c',plain],result='PASS',rows=rows,native_audit=audit,literal_build=left_build,native_build=json.loads((OUT/'build.json').read_text())))
    print('PASS actual native/literal cross-mode and four page cycles:',len(rows),'boundaries',audit,flush=True)
if __name__=='__main__':main()
