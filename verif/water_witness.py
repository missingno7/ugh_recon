"""Probe an input-only timer-trace extension; independently verify any witness."""
import argparse,ctypes as C,json,sys
from closure_support import ROOT,save,receipt
from water_build import OUT,build
import contacts_reference as reference
reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import wholegame as w,nbuild
from difftest import Regs
from emu import MEM_SIZE,NativeVga
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['probe','verify']);p.add_argument('--frames',type=int,default=2400);p.add_argument('--policy',choices=['extend','rescue','question'],default='extend');a=p.parse_args()
    reference.prepare_reference(local=True);dll=nbuild.load_l1(build());audit=(C.c_uint32*20).in_dll(dll,'water_audit');path=ROOT/('verif/water_witness'+('' if a.policy=='extend' else '_'+a.policy)+'.txt')
    if a.mode=='probe':
        lines=(ROOT/'tests/scenarios/items-timer.txt').read_text().splitlines();lines=[l for l in lines if not l.startswith(('frames ','expect ','requires '))];lines.insert(0,'frames '+str(a.frames));s=w.scenario(ROOT/'tests/scenarios/items-timer.txt');s['frames']=a.frames;s['requires']=[];s['expects']={}
        machine,initial=w.fixture(s);mem=dll.ugh_memory().contents;dev=dll.ugh_device_state().contents;C.memmove(mem,machine.snapshot(),MEM_SIZE);dll.ugh_devices_reset();state=machine.device.state();C.memmove(C.addressof(dev),state,len(state));clock=w.Clock(s,machine)
        FRAME=C.CFUNCTYPE(C.c_int,C.POINTER(Regs));SERVICE=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(Regs))
        samples=[];last=[None];events={};finish=[0];stage=[0];throw_at=[0]
        def value(name,index=0):
            seg,off=machine.address('DGROUP:'+name);return int.from_bytes(bytes(mem[seg*16+off+2*index:seg*16+off+2*index+2]),'little')
        def signed(v):return v-65536 if v&32768 else v
        def boundary(rp):
            clock.frame+=1;f=clock.frame;dev.count=0
            if f in (850,1000,1300,1600):samples.append(dict(frame=f,x=value('PlayerPixelX'),y=value('PlayerYPixels'),vy=value('PlayerVerticalVelocities'),carry=value('PlayerCarriedKinds'),water=value('WaterYPixels')))
            if a.policy!='extend' and f>813:
                found=[i for i in range(15) if value('ActorDescriptors',i) in (0x776a,0x7892)]
                x=signed(value('PlayerX32'))/32;y=signed(value('PlayerY32'))/32;vx=signed(value('PlayerHorizontalVelocities'));vy=signed(value('PlayerVerticalVelocities'));surface=value('WaterYPixels')
                if stage[0]==0 and abs(x+8)<5 and abs(vx)<250 and y<48:stage[0]=1
                tx=-8;ty=40 if stage[0]==0 else surface-17
                dx=max(-1200,min(1200,(tx-x)*160));dy=max(-1000,min(1000,(ty-y)*150));ax=1 if vx<dx-80 else -1 if vx>dx+80 else 0;ay=1 if vy<dy-60 else -1 if vy>dy+60 else 0
                if value('PlayerYPixels')+18==surface and not vy:ay=0
                if value('PlayerPlatformIndices')!=65535:ay=-1
                if a.policy=='question' and audit[6]:ay=-1
                if not throw_at[0] and value('PlayerPlatformIndices')==65535 and f>820:throw_at[0]=f+2
                button=throw_at[0]<=f<throw_at[0]+8 if throw_at[0] else False
                control=(ax,ay,button)
                if control!=last[0]:events[f]=control;last[0]=control
                wave=w.joystick_wave(ax,ay);s['joy_events'][f]=[v&239 for v in wave] if button else wave
                if not finish[0] and (audit[8] if a.policy=='rescue' else audit[7]):finish[0]=f+160
            return 2 if f>=a.frames or (finish[0] and f>=finish[0]) else 0
        def service(seg,off,rp):clock.service(dev,seg,off,rp.contents.flags,lambda s,o,n:bytes(mem[s*16+o:s*16+o+n]));return 0
        cb=FRAME(boundary);scb=SERVICE(service);dll.ugh_set_frame_observer.argtypes=[FRAME];dll.ugh_set_frame_observer(cb);dll.ugh_set_service_observer.argtypes=[SERVICE];dll.ugh_set_service_observer(scb)
        r=Regs(**{k.lower():v for k,v in initial.items()});status=dll.c_RunDosGame(C.byref(r));dll.ugh_set_frame_observer(FRAME());dll.ugh_set_service_observer(SERVICE())
        result=receipt(['python','verif/water_witness.py','probe','--frames',str(a.frames),'--policy',a.policy],[__file__,ROOT/'tests/scenarios/items-timer.txt'],result='PROBE',status=status,frames=clock.frame,entries=list(audit[:10]),fallbacks=list(audit[10:]),device_error=dev.error,samples=samples)
        save(OUT/('witness-probe-'+a.policy+'-'+str(a.frames)+'.json'),result);print(result['entries'],status,clock.frame,dev.error,samples)
        worth=any(audit[i] for i in [2,3,4,5,6,7,8]) if a.policy=='extend' else bool(audit[8] if a.policy=='rescue' else audit[7])
        if worth:
            lines[0]='frames '+str(clock.frame)
            for f,(ax,ay,button) in events.items():lines.append(f'{f}: joy='+','.join(f'{v&239:02x}' for v in w.joystick_wave(ax,ay)) if button else f'{f}: stick={ax},{ay}')
            reached=[n for i,n in enumerate(__import__('water_shells').NAMES) if audit[i]];lines.append('requires '+' '.join('GAME:'+n for n in reached));path.write_text('\n'.join(lines)+'\n');print('recorded candidate',path)
        return
    s=w.scenario(path);folder=OUT/('witness-'+a.policy);folder.mkdir(parents=True,exist_ok=True);accelerator=NativeVga(folder);w.VGA_ACCELERATOR=accelerator
    try:
        machine,initial=w.fixture(s);frames,cov,_=w.original(s,machine,initial);machine,initial=w.fixture(s);failure=w.native(s,machine,initial,dll,frames)
    finally:accelerator.close();w.VGA_ACCELERATOR=None
    assert not failure and set(s['requires'])<=set(cov['routines'])
    save(folder/'reference.json',dict(frames=frames,coverage=cov));save(folder/'result.json',receipt(['python','verif/water_witness.py','verify'],[__file__,path],result='PASS',frames=len(frames),entries=list(audit[:10]),fallbacks=list(audit[10:])))
    print('PASS input-only witness',len(frames),'frames',list(audit[:10]))
if __name__=='__main__':main()
