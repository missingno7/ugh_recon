"""All shipped resources through real calibration, probe, play/fade/stop/shutdown."""
import ctypes as C,sys,time,hashlib,json,struct
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_lifetime_build import OUT,build
from adlx_loader_corpus import compare,log
from adlx_music_corpus import call
from adlx_sections_corpus import put,get
import contacts_reference
contacts_reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,dataprobe
from emu import LOAD
def main():
    start=time.perf_counter();plain=contacts_reference.prepare_reference(local=True)
    dataprobe.IMAGE=contacts_reference.expanded_image(local=True);dataprobe.OUT=OUT/'format';streams=dataprobe.music(dataprobe.validate())
    dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine();base=difftest.load_suite('adlib').base;api=difftest.load_suite('sound_api')
    sound=m.seg('SOUND:AudioChannelStates');cseg=LOAD+0x878;rows=[];deliveries=[0,0];observers=[]
    observer_type=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs))
    for index,dll in enumerate(dlls):
        def deliver(segment,offset,p,index=index,dll=dll):
            if segment==sound:
                assert offset in [m.off('SOUND:loc_1163'),m.off('SOUND:loc_116B')];return 0
            assert segment==cseg and offset==m.off('C:StopMusicTrack')+0x95
            deliveries[index]+=1;callback=difftest.Regs.from_buffer_copy(p.contents)
            status=call(dll,callback,'AdvanceMusicFade',sound,clear=False)
            return status or call(dll,callback,'TickAdlxPlayback',sound,clear=False)
        observers.append(observer_type(deliver));dll.ugh_set_service_observer.argtypes=[observer_type];dll.ugh_set_service_observer(observers[-1])
    for stream in streams:
      for duration in [0,1,2,17]:
       for second in [0,65537]:
        m.reset();base(m);api.base(m,1);m.ww('SOUND:AdlibInitAttempted',0)
        m.write(0,0x20,struct.pack('<HH',0x2468,0x1357));m.device.script(0x388,[0x1f,0x20])
        m.device.schedule(sound,m.off('SOUND:loc_1163'),skip=1,clocks=65536)
        m.device.schedule(sound,m.off('SOUND:loc_116B'),skip=second,clocks=65536)
        initial=m.prepare('SOUND:InitializeAdlibPlayback',difftest.POISON,'far',(),0x602)
        states=[difftest.Regs(**{n.lower():v for n,v in initial.items()}) for _ in dlls];device=m.device.state()
        for dll in dlls:
            C.memmove(dll.ugh_memory().contents,m.snapshot(),difftest.MEM_SIZE);dll.ugh_devices_reset();C.memmove(C.addressof(dll.ugh_device_state().contents),device,len(device))
        ordered=[];steps=0
        def pair(name,bank,args=()):
            for dll,r in zip(dlls,states):assert call(dll,r,name,bank,args)==0,(stream['frame'],name)
            compare(dlls,states,initial,(stream['frame'],duration,second,name,steps));ordered.extend(log(dlls[1]))
        pair('ClearSoundState',sound)
        # The top-level device selector (outside this unit) chooses AdLib after
        # clearing the shared state. This is an explicit corpus input.
        for dll in dlls:put(dll,sound,m.off('SOUND:SoundDeviceBits'),1)
        pair('InitializeAdlibPlayback',sound);assert states[0].ax==1
        pair('StartMusicTrack',cseg,(0,int(stream['frame'],16)+LOAD,duration,201));assert states[0].ax==1
        if duration:
            while get(dlls[0],sound,m.off('SOUND:MusicFadeScheduled')):
                steps+=1;assert steps<=duration+1;pair('AdvanceMusicFade',sound);pair('TickAdlxPlayback',sound)
        pair('SetMusicTrackVolume',cseg,(37,));before=list(deliveries)
        pair('StopMusicTrack',cseg,(2 if duration else 0,));pair('ShutdownAdlibPlayback',sound)
        assert get(dlls[0],sound,m.off('SOUND:AdlibInitAttempted'))&255==0
        assert deliveries[0]-before[0]==deliveries[1]-before[1]
        rows.append(dict(frame=stream['frame'],duration=duration,second_skip=second,steps=steps,events=len(ordered),ordered_sha256=hashlib.sha256(json.dumps(ordered).encode()).hexdigest()))
      print(stream['frame'],'PASS startup/fade/stop/shutdown',flush=True)
    audit=list((C.c_uint32*16).in_dll(dlls[1],'adlx_lifetime_audit'));assert audit[:6]==[len(rows)]*6,audit
    save(OUT/'corpus.json',receipt([sys.executable,'verif/adlx_lifetime_corpus.py'],[Path(__file__),ROOT/'verif/adlx_lifetime_build.py',ROOT/'verif/adlx_loader_corpus.py',ROOT/'verif/adlx_music_corpus.py',ROOT/'verif/adlx_sections_corpus.py',ROOT/'tools/dataprobe.py',plain,dataprobe.IMAGE],result='PASS',resources=len(streams),cases=rows,deliveries=deliveries,lifetime_audit=audit,seconds=time.perf_counter()-start))
    print('PASS',len(rows),'pipelines; deliveries',deliveries,'audit',audit,flush=True)
if __name__=='__main__':main()
