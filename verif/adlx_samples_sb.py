"""SB protocol and sample/DMA API evidence; input-only gameplay reach audit."""
import ctypes as C,copy,sys,struct,json,time,tempfile,hashlib
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_samples_build import OUT,build
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,wholegame
from emu import SoundBlaster,Devices,NativeVga
from adlx_samples_cases import sample
def main():
    import contacts_reference
    contacts_reference.OUT=OUT/'reference';plain=contacts_reference.prepare_reference(local=True)
    ledger=OUT/'sb-prior-edges.json';ledger.write_text('[]\n')
    class ReadRoot(type(ROOT)):
        def __truediv__(self,value):
            if str(value)=='build/workers/c-close/call-edges.json':return ledger
            if str(value)=='build/link/plain/UGH.EXE':return plain
            return super().__truediv__(value)
    wholegame.ROOT=ReadRoot(ROOT)
    start=time.perf_counter();dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine();difftest.load_suite('sound_api').base(m,2)
    sound=m.seg('SOUND:AudioChannelStates');m.ww('SOUND:DspBasePort',0x220);m.wb('SOUND:DspPicIrqMask',128)
    m.ww('SOUND:ActiveSampleVoiceCount',0);m.ww('SOUND:ActiveSampleVoiceMask',0);m.ww('SOUND:SampleMixerBusy',0);m.ww('SOUND:AudioChannelStates',0,40)
    m.device.sb=SoundBlaster();m.device.sb.install(m.device);m.write(0,4*15,struct.pack('<HH',m.off('SOUND:HandleSampleDmaInterrupt'),sound));m.write(0x7100,0x100,sample(64))
    models=[copy.deepcopy(m.device.sb) for _ in dlls];states=[difftest.Regs(ax=0xa5c3,bx=0,cx=0,dx=0,si=0x6996,di=0x9669,bp=0x7e81,sp=0x1000,cs=sound,ds=0x7340,es=0x7c20,ss=0x8000,flags=0x202) for _ in dlls]
    callbacks=[];clocks=[];s=dict(card='sb',events={},frames=1)
    for dll,model in zip(dlls,models):
        C.memmove(dll.ugh_memory().contents,m.snapshot(),difftest.MEM_SIZE);dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;initial=m.device.state();C.memmove(C.addressof(dev),initial,len(initial))
        clock=wholegame.Clock(s,m);clock.sb=model;clock.timer_sites.append(m.address('SOUND:loc_1FEA'));clocks.append(clock)
        output_type=C.CFUNCTYPE(None,C.c_uint16,C.c_uint,C.c_uint32);service_type=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs))
        def output(port,size,value,dev=dev,model=model):model.sync(dev,[(e.kind,e.port,e.size,e.value) for e in dev.log[:dev.count]])
        def service(seg,off,rp,dev=dev,clock=clock,dll=dll):
            clock.service(dev,seg,off,rp.contents.flags,lambda bank,at,n:bytes(dll.ugh_memory().contents[bank*16+at:bank*16+at+n]));return 0
        ocb=output_type(output);scb=service_type(service);callbacks.extend([ocb,scb]);dll.ugh_set_output_observer.argtypes=[output_type];dll.ugh_set_output_observer(ocb);dll.ugh_set_service_observer.argtypes=[service_type];dll.ugh_set_service_observer(scb)
    rows=[]
    def compare(title):
        memories=[];logs=[]
        for dll,model in zip(dlls,models):
            dev=dll.ugh_device_state().contents;events=[(e.kind,e.port,e.size,e.value) for e in dev.log[:dev.count]];model.sync(dev,events)
            assert not dev.error,(title,'device error');memories.append(bytes(dll.ugh_memory().contents));logs.append(events)
        assert memories[0][:0x80000]==memories[1][:0x80000] and memories[0][0x81000:]==memories[1][0x81000:],(title,'RAM')
        assert bytes(states[0])==bytes(states[1]) and logs[0]==logs[1] and models[0].state()==models[1].state(),(title,'ABI/log/model')
        rows.append(dict(title=title,events=len(logs[0]),pcm=len(models[0].pcm),state_sha256=hashlib.sha256(models[0].state()).hexdigest()))
    def pair(name,bank,args=()):
        for dll,r in zip(dlls,states):
            r.cs=bank
            for i,value in enumerate(args):C.memmove(C.addressof(dll.ugh_memory().contents)+r.ss*16+r.sp+4+2*i,struct.pack('<H',value),2)
            f=getattr(dll,'c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];assert f(C.byref(r))==0,name
        compare(name)
    pair('ResetSoundBlasterDsp',sound);assert states[0].ax==0xaa
    pair('SetDspSampleRate',sound,(8000,));pair('LocateDmaMixBuffers',sound)
    pair('LoadIffSample',m.seg('C:LoadIffSample'),(0,0x100,0x7100,255,2,256));assert states[0].ax==1
    pair('PrimeSampleDmaPlayback',sound)
    for i in range(24):
        for dll,r in zip(dlls,states):
            r.cs=sound;r.flags|=512;f=dll.platform_service_point_at;f.argtypes=[C.c_int,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs)];assert f(1,sound,m.off('SOUND:loc_1FEA'),C.byref(r))==0
        compare('DMA poll '+str(i))
        if models[0].blocks and not models[0].remaining:break
    assert models[0].pcm and models[0].blocks
    save(OUT/'sb-api.json',receipt([sys.executable,'verif/adlx_samples_sb.py'],[Path(__file__),ROOT/'tools/emu.py',ROOT/'tools/wholegame.py',ROOT/'verif/adlx_samples_build.py',ROOT/'verif/adlx_samples_cases.py'],result='PASS',scope='API-level generated resource and explicit driver installation fixture, not whole-game reachability',rows=rows,pcm_bytes=len(models[0].pcm),pcm_sha256=hashlib.sha256(models[0].pcm).hexdigest()))
    print('PASS SB API sample/DMA chain',rows[-1],flush=True)
    # Fresh input-only witness, with no game-state patch or repaired hook.
    scenario=wholegame.scenario(ROOT/'verif/sb_gameplay.txt');folder=OUT/'sb-whole';folder.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='vga-',dir=OUT) as temp:
        accelerator=NativeVga(Path(temp));wholegame.VGA_ACCELERATOR=accelerator
        try:
            original,initial=wholegame.fixture(scenario);frames,coverage,_=wholegame.original(scenario,original,initial)
            assert set(scenario['requires'])<=set(coverage['routines']),scenario['requires']
            candidate,initial=wholegame.fixture(scenario);failure=wholegame.native(scenario,candidate,initial,dlls[1],frames);assert not failure,failure
        finally:accelerator.close();wholegame.VGA_ACCELERATOR=None
    audio=[name for name in coverage['routines'] if name.startswith(('SOUND:','C:'))];targets=['C:LoadIffSample','SOUND:ResetSampleVoiceCursor','SOUND:MixSampleVoicePairs']
    assert not set(targets)&set(audio)
    save(OUT/'sb-gameplay.json',receipt([sys.executable,'verif/adlx_samples_sb.py'],[Path(__file__),ROOT/'tools/emu.py',ROOT/'tools/wholegame.py',ROOT/'verif/sb_gameplay.txt'],result='PASS',frames=len(frames),audio_routines=audio,unreached_samples=targets,scope='SB-equipped input-only gameplay; original requests AdLib only. This cannot meet the requested sample-reaching witness.',seconds=time.perf_counter()-start))
    print('PASS SB-equipped gameplay',len(frames),'frames; samples not reached',flush=True)
if __name__=='__main__':main()
