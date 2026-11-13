"""Every shipped ADLX resource through real load/start, fades, Tick and stop.

TIMER allocation/removal are real C peers. At the explicit wait service point,
the delivery contract invokes the actual fade callback and Tick with isolated
interrupt registers; it does not invent fade state or expected output.
"""
import ctypes as C,sys,json,time,hashlib
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_music_build import OUT,build
from adlx_loader_corpus import compare,begin,log
from adlx_sections_corpus import put,get
import contacts_reference
contacts_reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,dataprobe
from emu import LOAD

def call(dll,r,name,bank,args=(),clear=True):
    r.cs=bank
    for i,value in enumerate(args):put(dll,r.ss,(r.sp+4+i*2)&65535,value)
    if clear:dll.ugh_device_state().contents.count=0
    f=getattr(dll,'c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];f.restype=C.c_int
    return f(C.byref(r))

def main():
    started=time.perf_counter();plain=contacts_reference.prepare_reference(local=True)
    dataprobe.IMAGE=contacts_reference.expanded_image(local=True);dataprobe.OUT=OUT/'format'
    streams=dataprobe.music(dataprobe.validate());dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())]
    m=difftest.Machine();base=difftest.load_suite('adlib').base;api=difftest.load_suite('sound_api');rows=[]
    sound=m.seg('SOUND:AudioChannelStates');cseg=LOAD+0x878;deliveries=[0,0]
    observer_type=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs));observers=[]
    for index,dll in enumerate(dlls):
        def deliver(segment,offset,p,index=index,dll=dll):
            assert segment==cseg and offset==m.off('C:StopMusicTrack')+0x95
            deliveries[index]+=1
            callback=difftest.Regs.from_buffer_copy(p.contents)
            status=call(dll,callback,'AdvanceMusicFade',sound,clear=False)
            if status:return status
            # Timer interrupt registers are independent of the blocked caller.
            return call(dll,callback,'TickAdlxPlayback',sound,clear=False)
        observers.append(observer_type(deliver));dll.ugh_set_service_observer.argtypes=[observer_type];dll.ugh_set_service_observer(observers[-1])
    for stream in streams:
      frame=int(stream['frame'],16)
      for duration in [0,1,2,17]:
       for reserved in [0,1,9]:
        for clock in [0,0xfffffffe]:
          m.reset();base(m);api.base(m,1)
          for n,v in dict(MainAdlxPlaying=0,MusicFadeScheduled=0,ReservedAdlibChannelCount=reserved,AdlxPlaybackGuard=0).items():m.ww('SOUND:'+n,v)
          initial,states=begin(m,dlls,'StartMusicTrack',(0,frame+LOAD,duration,201),True)
          for dll in dlls:put(dll,sound,m.off('SOUND:AdlxTickCount'),clock,2)
          ordered=[];steps=0
          def pair(name,bank,args=()):
            for dll,r in zip(dlls,states):assert call(dll,r,name,bank,args)==0,(frame,name)
            compare(dlls,states,initial,(frame,duration,reserved,clock,name,steps))
            ordered.extend(log(dlls[1]))
          pair('StartMusicTrack',cseg,(0,frame+LOAD,duration,201));assert states[0].ax==1
          if duration:
            while get(dlls[0],sound,m.off('SOUND:MusicFadeScheduled')):
                steps+=1;assert steps<=duration+1
                pair('AdvanceMusicFade',sound);pair('TickAdlxPlayback',sound)
          pair('SetMusicTrackVolume',cseg,(37,))
          before=list(deliveries);pair('StopMusicTrack',cseg,(2 if duration else 0,))
          assert deliveries[0]-before[0]==deliveries[1]-before[1]
          assert get(dlls[0],sound,m.off('SOUND:MainAdlxPlaying'))==0
          rows.append(dict(frame=stream['frame'],duration=duration,reserved=reserved,clock=clock,fade_callbacks=steps,stop_deliveries=deliveries[0]-before[0],events=len(ordered),ordered_sha256=hashlib.sha256(json.dumps(ordered).encode()).hexdigest()))
      print(stream['frame'],'PASS',flush=True)
    save(OUT/'corpus.json',receipt([sys.executable,'verif/adlx_music_corpus.py'],[Path(__file__),ROOT/'verif/adlx_music_build.py',ROOT/'verif/adlx_loader_corpus.py',ROOT/'verif/adlx_sections_corpus.py',ROOT/'tools/dataprobe.py',plain,dataprobe.IMAGE],result='PASS',resources=len(streams),cases=rows,deliveries=deliveries,seconds=time.perf_counter()-started))
    print('PASS',len(rows),'pipelines, delivery contract calls',deliveries,flush=True)
if __name__=='__main__':main()
