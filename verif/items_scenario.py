"""Author a fixed input-only pickup trace, or verify its L0/bridged boundaries.

Only keyboard/gameport fixtures are driven. No simulation RAM is patched.
The life descriptor has no shipped producer; see items_capacity.py.
"""
import argparse,ctypes as C,json,sys
from pathlib import Path
from closure_support import ROOT,save,receipt
from items_build import OUT,build
import contacts_reference
contacts_reference.OUT=OUT/'reference'
from contacts_reference import prepare_reference
sys.path.insert(0,str(ROOT/'tools'))
import wholegame as w,nbuild
from difftest import Regs
from emu import MEM_SIZE,NativeVga

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['author','verify']);p.add_argument('--kind',choices=['multiplier','timer'],default='multiplier');a=p.parse_args()
    prepare_reference();dll=nbuild.load_l1(build());path=OUT/f'items-{a.kind}.txt'
    if a.mode=='verify':
        s=w.scenario(path);folder=OUT/f'pickup-{a.kind}';folder.mkdir(exist_ok=True)
        accelerator=NativeVga(folder);w.VGA_ACCELERATOR=accelerator
        try:
            machine,initial=w.fixture(s);frames,coverage,_=w.original(s,machine,initial)
            machine,initial=w.fixture(s);failure=w.native(s,machine,initial,dll,frames)
        finally:accelerator.close();w.VGA_ACCELERATOR=None
        assert not failure,failure
        assert set(s['requires'])<=set(coverage['routines'])
        audit=list((C.c_uint32*10).in_dll(dll,'items_audit'))
        # Flight calls native item_land directly; no bridge wrapper entry is
        # required for the original landing tail, which coverage checks below.
        assert all(audit[i]>0 for i in [0,2,3,4]) and not any(audit[5:]),audit
        save(folder/'reference.json',dict(frames=frames,coverage=coverage))
        save(folder/'result.json',receipt(['python','verif/items_scenario.py','verify'],[__file__,path,ROOT/'verif/items_build.py',ROOT/'tools/wholegame.py'],result='PASS',frames=len(frames),audit=audit))
        print('PASS pickup',len(frames),'frames; audit',audit);return
    # Use the already established real-entry/password editor fixture. A source
    # itinerary at level 59 has a same-platform first leg, permitting a quick
    # delivery and bonus collection without an artificial simulation fixture.
    s=w.scenario(ROOT/'tests/scenarios/enemy.txt')
    s['events']={f:v for f,v in s['events'].items() if v};s['joy_events']={};s['joy_cycles']={}
    s['requires']=[];s['expects']={};s.pop('death',None)
    password='OMEGADAWN';s['bios']='0020 '*5+' '.join(f'{ord(c):04x}' for c in password)+' 000d'
    if a.kind=='timer':
        s=w.scenario(ROOT/'tests/scenarios/passenger.txt');s['events']={f:v for f,v in s['events'].items() if v}
        s['joy_events']={};s['joy_cycles']={};s['requires']=[];s['expects']={}
    machine,initial=w.fixture(s);mem=dll.ugh_memory().contents;dev=dll.ugh_device_state().contents
    C.memmove(mem,machine.snapshot(),MEM_SIZE);dll.ugh_devices_reset();state=machine.device.state();C.memmove(C.addressof(dev),state,len(state))
    clock=w.Clock(s,machine);events={};last=[None];finish=[0];stage=[0];released=[0];last_timer=[0]
    def read(seg,off,n):return bytes(mem[seg*16+off:seg*16+off+n])
    def value(name,size=2,delta=0):
        seg,off=machine.address('DGROUP:'+name);return int.from_bytes(read(seg,off+delta,size),'little')
    def signed(v):return v-65536 if v>=32768 else v
    FRAME=C.CFUNCTYPE(C.c_int,C.POINTER(Regs));SERVICE=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(Regs))
    def boundary(rp):
        clock.frame+=1;f=clock.frame;dev.count=0
        x=signed(value('PlayerX32'))/32;y=signed(value('PlayerY32'))/32
        vx=signed(value('PlayerHorizontalVelocities'));vy=signed(value('PlayerVerticalVelocities'))
        if f>130:
            tx,ty=32,15 if x>85 else 40
            button=False
            if a.kind=='timer':
                old_stage=stage[0]
                if stage[0]==0 and value('PlayerCarriedKinds')==4:stage[0]=1
                if stage[0]==1 and x>136 and abs(vx)<500:stage[0]=2
                if stage[0]==2 and y<34 and abs(vy)<500:stage[0]=3
                if stage[0]==3 and x<70 and abs(vx)<400:stage[0]=4;released[0]=f
                tx,ty=[(80,152),(144,118),(144,30),(64,30),(64,90)][stage[0]]
                if stage[0]==4:
                    for slot in range(12):
                        if value('FallingItemSprites',delta=2*slot)!=65535:
                            tx=signed(value('FallingItemX',delta=2*slot))/32-8
                            ty=45 if abs(tx-x)>3 else 90
                            break
                button=stage[0]==4 and f<released[0]+8
                if old_stage!=stage[0]:print('stage',stage[0],f,'carry',value('PlayerCarriedKinds'),flush=True)
            dx=max(-1600,min(1600,(tx-x)*180));dy=max(-1000,min(1000,(ty-y)*170))
            ax=1 if vx<dx-80 else -1 if vx>dx+80 else 0
            ay=1 if vy<dy-60 else -1 if vy>dy+60 else 0
            if a.kind=='multiplier' and value('PlayerPlatformIndices')==0:ax=ay=0
            if a.kind=='timer' and stage[0]==0 and value('PlayerPlatformIndices')==2:ax=ay=0
            if a.kind=='timer' and stage[0]==4 and value('PlayerPlatformIndices')==1 and abs(tx-x)<3:ax=ay=0
            if (ax,ay,button)!=last[0]:events[f]=(ax,ay,button);last[0]=(ax,ay,button)
            raw=w.joystick_wave(ax,ay);s['joy_events'][f]=[v&239 for v in raw] if button else raw
        if f%250==0:print(f,'xy',x,y,'pad',value('PlayerPlatformIndices'),'carry',value('PlayerCarriedKinds'),'score',value('ScoreLowWord'),'multiplier',value('ScoreMultiplier'),flush=True)
        collected=value('ScoreMultiplier')>1 if a.kind=='multiplier' else stage[0]==4 and value('LevelTimer')>last_timer[0]+1000
        if collected and not finish[0]:finish[0]=f+20
        last_timer[0]=value('LevelTimer')
        return 2 if f==finish[0] or f>=2400 else 0
    def service(seg,off,rp):clock.service(dev,seg,off,rp.contents.flags,read);return 0
    cb=FRAME(boundary);scb=SERVICE(service);dll.ugh_set_frame_observer.argtypes=[FRAME];dll.ugh_set_frame_observer(cb)
    dll.ugh_set_service_observer.argtypes=[SERVICE];dll.ugh_set_service_observer(scb)
    registers=Regs(**{k.lower():v for k,v in initial.items()});status=dll.c_RunDosGame(C.byref(registers))
    print('author status',status,'frame',clock.frame,'device error',dev.error,'level',value('CurrentLevelIndex'),flush=True)
    print('audit',list((C.c_uint32*10).in_dll(dll,'items_audit')),flush=True)
    if dev.error:
        print('tail',[(e.kind,e.port,e.size,e.value) for e in dev.log[max(0,dev.count-6):dev.count]],
              'scripts',[(dev.scripts[i].port,dev.scripts[i].cursor,dev.scripts[i].count) for i in range(dev.script_count)],flush=True)
    assert finish[0] and status==2,'no input-only pickup found'
    lines=['timing pit-quantum-at-polls','# Fixed input-only trace, authored on C; verify independently on L0.',f'frames {finish[0]}','card none','joystick '+s['joystick']]
    if a.kind=='multiplier':lines+=['bios '+s['bios'],'1: esc -esc','4: esc -esc','9: f2 -f2','26: f1 -f1','29: enter -enter','31: cycle=enter,-enter']
    else:lines+=['1: esc -esc','4: esc -esc','9: f1 -f1','12: enter -enter','14: cycle=enter,-enter']
    for f,(x,y,button) in events.items():
        if f>finish[0]:continue
        lines.append(f'{f}: joy='+','.join(f'{v&239:02x}' for v in w.joystick_wave(x,y)) if button else f'{f}: stick={x},{y}')
    lines += ['requires GAME:SpawnFallingItem GAME:AdvanceFallingItem GAME:LandFallingItem GAME:ExpireOrCollectFallingItem GAME:FindPlayerTouchingFallingItem',
        'requires GAME:EditLevelPassword GAME:RunGameFromPassword GAME:DeliverPassenger' if a.kind=='multiplier' else 'requires GAME:ReleaseTreeReward GAME:ThrowCarriedStone',f'expect ScoreLowWord {value("ScoreLowWord")}', 'expect CurrentLevelIndex 58' if a.kind=='multiplier' else 'expect CurrentLevelIndex 0']
    path.write_text('\n'.join(lines)+'\n');print(path,'multiplier',value('ScoreMultiplier'))

if __name__=='__main__':main()
