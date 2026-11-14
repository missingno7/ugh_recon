"""Real compiled facade peers; full persistent RAM, registers and ordered I/O."""
import ctypes as C,random,struct,sys,time,hashlib
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_facade_build import OUT,build,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest,nbuild,dataprobe
from common import MZ,load_json
contacts_reference.OUT=OUT/'reference'
def main():
    start=time.perf_counter();plain=contacts_reference.prepare_reference(local=True);dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine();api=difftest.load_suite('sound_api');adlib=difftest.load_suite('adlib');rng=random.Random(10071);rows=[]
    def pair(name,args=(),regs=None):
        initial=m.prepare('C:'+name,{**difftest.POISON,**(regs or {})},'far',args,rng.choice([0x202,0x602,0xed7]));memory=m.snapshot();device=m.device.state();outputs=[];states=[];events=[];statuses=[];errors=[]
        for dll in dlls:
            C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();d=dll.ugh_device_state().contents;C.memmove(C.addressof(d),device,len(device));r=difftest.Regs(**{n.lower():v for n,v in initial.items()});f=getattr(dll,'c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];statuses.append(f(C.byref(r)));outputs.append(bytes(dll.ugh_memory().contents));states.append(bytes(r));events.append([(e.kind,e.port,e.size,e.value) for e in d.log[:d.count]]);errors.append(d.error)
        assert statuses[0]==statuses[1] and errors[0]==errors[1],(name,len(rows),'status',statuses,errors)
        assert states[0]==states[1],(name,len(rows),'ABI',list(struct.unpack('<14H',states[0])),list(struct.unpack('<14H',states[1])))
        lo=initial['SS']*16;hi=lo+initial['SP'];assert outputs[0][:lo]==outputs[1][:lo] and outputs[0][hi:]==outputs[1][hi:],(name,len(rows),'RAM',next((i for i,(a,b) in enumerate(zip(*outputs)) if a!=b and not lo<=i<hi),None))
        assert events[0]==events[1],(name,len(rows),'ordered events');rows.append(dict(name=name,status=statuses[0],events=len(events[0]),state_sha256=hashlib.sha256(outputs[1]).hexdigest()))
    for name in NAMES[:3]:
      for i in range(350):
        m.reset();adlib.base(m);api.base(m,rng.choice([0,1,2,3,0xfffd]));m.write(0,0x20,struct.pack('<HH',0x100,0xf000))
        m.ww('C:SoundSystemInitialized',rng.choice([0,1,0xffff]));m.ww('C:SoundSystemShutdown',rng.choice([0,1,0xffff]));m.ww('SOUND:MusicFadeScheduled',0)
        m.wb('SOUND:AdlibInitAttempted',rng.choice([0,1,0xff]));m.device.script(0x388,rng.choice([[0xe0],[0,0],[0,0x20]]),cycles=0xffffffff)
        for site in ['loc_1163','loc_116B']:m.device.schedule(m.seg('SOUND:'+site),m.off('SOUND:'+site),clocks=65536)
        m.ww('SOUND:ActiveSampleVoiceCount',0)
        for slot in range(8,12):m.ww('SOUND:AudioChannelStates',rng.randrange(65536),42*slot+28)
        pair(name,(rng.choice([0,1,2,3,0xffff]),) if name=='InitializeSoundSystem' else ())
    targets=['DurationLongWait','DurationFrequency','DurationKeyOff','DurationVolume','DurationInstrument','DurationTimer','DurationExtension','DurationDefault']
    # Resolve constants from the same published compiler-position interface.
    start_off=m.off('C:GetMusicTrackDuration');positions=[0x92,0xae,0xb4,0xb6,0xb8,0xbe,0xc0,0xd0]
    for i in range(1800):
        m.reset();api.base(m,rng.choice([0,1,3]));m.ww('SOUND:MainAdlxPlaying',rng.choice([0,1,0xffff]));m.ww('SOUND:MusicTicksPerUnit',rng.choice([0,1,420,65535]))
        offset=rng.choice([0x100,0xffe0]);length=rng.choice([0,1,2,17,31,128]);m.ww('SOUND:MainAdlxStartPointer',offset);m.ww('SOUND:MainAdlxStartPointer',0x7100,2);m.ww('SOUND:MusicEventStreamLength',length)
        m.write(0x7100,0,rng.randbytes(65537))
        if i%2:
            for slot in range(8):m.write(m.seg('C:GetMusicTrackDuration'),start_off+0x107+2*slot,struct.pack('<H',start_off+rng.choice(positions) if i%5 else 0xbeef))
        pair('GetMusicTrackDuration')
    rebuilt=MZ(plain.read_bytes());assert rebuilt.identity()['image_sha256']==load_json('oracle.json')['expanded']['image_sha256'];dataprobe.OUT=OUT/'format';streams=dataprobe.music(rebuilt)
    for stream in streams:
      for rate in [1,420,65535]:
        m.reset();api.base(m,1);m.ww('SOUND:MainAdlxPlaying',1);m.ww('SOUND:MusicTicksPerUnit',rate);m.ww('SOUND:MainAdlxStartPointer',42);m.ww('SOUND:MainAdlxStartPointer',int(stream['frame'],16)+0x1010,2);m.ww('SOUND:MusicEventStreamLength',stream['track_length']);pair('GetMusicTrackDuration')
    save(OUT/'facade-cases.json',receipt([sys.executable,'verif/adlx_facade_evidence.py'],[Path(__file__),ROOT/'verif/adlx_facade_build.py',ROOT/'native/adlx_facade.c',ROOT/'native/adlx_facade.h',ROOT/'native/bridge/adlx_facade_bridge.c',ROOT/'c/sound_api.c',ROOT/'c/music_analysis.c',plain,ROOT/'metadata/oracle.json'],result='PASS',cases=rows,resources=len(streams),seconds=time.perf_counter()-start));print('PASS',len(rows),'real compiled facade cases;11 resources',flush=True)
if __name__=='__main__':main()

