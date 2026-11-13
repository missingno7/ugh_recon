"""Every shipped container: byte-exact load/reset and complete native playback."""
import ctypes as C,hashlib,json,sys,struct,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_loader_build import OUT,build
import contacts_reference
contacts_reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,dataprobe
from emu import LOAD

def log(dll):
    d=dll.ugh_device_state().contents;assert not d.error
    return [(e.kind,e.port,e.size,e.value) for e in d.log[:d.count]]
def compare(dlls,states,initial,title):
    memories=[bytes(d.ugh_memory().contents) for d in dlls];lo=initial['SS']*16;hi=lo+initial['SP']
    assert memories[0][:lo]==memories[1][:lo] and memories[0][hi:]==memories[1][hi:],(title,'persistent RAM')
    for n in ('ax','bx','cx','dx','si','di','bp','ds','es','ss','sp','flags'):
        assert getattr(states[0],n)==getattr(states[1],n),(title,n,getattr(states[0],n),getattr(states[1],n))
    assert log(dlls[0])==log(dlls[1]),(title,'ordered writes')
    return memories[0]
def invoke(dlls,states,routine):
    for dll,r in zip(dlls,states):
        dll.ugh_device_state().contents.count=0
        f=getattr(dll,'c_'+routine);f.argtypes=[C.POINTER(difftest.Regs)];f.restype=C.c_int
        assert f(C.byref(r))==0,routine
def begin(m,dlls,routine,args,poison=False):
    initial=m.prepare('C:'+routine,difftest.POISON if poison else {},'far',args,0x202)
    for dll in dlls:C.memmove(dll.ugh_memory().contents,m.snapshot(),difftest.MEM_SIZE);dll.ugh_devices_reset()
    return initial,[difftest.Regs(**{n.lower():v for n,v in initial.items()}) for _ in dlls]
def main():
    started=time.perf_counter();plain=contacts_reference.prepare_reference(local=True)
    dataprobe.IMAGE=contacts_reference.expanded_image(local=True);dataprobe.OUT=OUT/'format'
    streams=dataprobe.music(dataprobe.validate());image=dataprobe.validate().image
    dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine()
    base=difftest.load_suite('adlib').base;api=difftest.load_suite('sound_api');matrix=[];pipelines=[]
    for stream in streams:
        frame=int(stream['frame'],16);raw=image[frame*16:frame*16+stream['root_size']+8]
        for slot in range(8,13):
         for reserved in [0,9,10,0xffff]:
          for repeats in [0,1,0xffff]:
           for offset in [0,0xfff9]:
            for poison in [False,True]:
             for routine in ['LoadAdlibTrackData','LoadAdlibChannel']:
                m.reset();base(m);api.base(m,1);m.ww('SOUND:ReservedAdlibChannelCount',reserved)
                m.write(0x6000,0,bytes([0xa5])*65537)
                for i,value in enumerate(raw):m.write(0x6000,(offset+i)&65535,bytes([value]))
                m.ww('SOUND:AudioChannelStates',0xfedc,slot*42+4)
                args=(slot,offset,0x6000,repeats) if routine=='LoadAdlibTrackData' else (slot,offset,0x6000,0x7654,repeats)
                initial,states=begin(m,dlls,routine,args,poison);invoke(dlls,states,routine)
                memory=compare(dlls,states,initial,(frame,slot,reserved,repeats,offset,poison,routine))
                s=m.seg('SOUND:AudioChannelStates')*16;p=m.off('SOUND:AudioChannelStates')+slot*42
                # Store exact loaded record/map bytes, not expected data from decoder.
                material=memory[s+p:s+p+42]+memory[s+m.off('SOUND:AdlibInstrumentMap'):s+m.off('SOUND:AdlibInstrumentMap')+4]
                matrix.append(dict(frame=f'{frame:04X}',slot=slot,reserved=reserved,repeats=repeats,offset=offset,poison=poison,routine=routine,
                    result=states[1].ax,loaded_sha256=hashlib.sha256(material).hexdigest()))
                invoke(dlls,states,'ResetAdlibTrackChannelCursor')
                reset=compare(dlls,states,initial,(frame,slot,reserved,repeats,offset,poison,routine,'reset'))
                matrix[-1]['reset_result']=states[1].ax
                matrix[-1]['reset_sha256']=hashlib.sha256(reset[s+p:s+p+42]).hexdigest()
        for main in [False,True]:
            m.reset();base(m);api.base(m,1)
            m.ww('SOUND:MusicVoiceCount',9);m.ww('SOUND:MainAdlxPlaying',int(not main));m.ww('SOUND:MusicTrackVolume',200)
            m.ww('SOUND:AudioChannelStates',0,12*42+36)
            m.ww('SOUND:AdlxTimerPeriod',0x1843)
            slot=12 if main else 8
            routine='LoadAdlibTrackData' if main else 'PlayAdlibEffect'
            args=(12,0,frame+LOAD,1) if main else (0,frame+LOAD,200,1)
            initial,states=begin(m,dlls,routine,args,True);invoke(dlls,states,routine)
            memory=compare(dlls,states,initial,(frame,main,'load'))
            if main:
                for dll,r in zip(dlls,states):
                    mem=dll.ugh_memory().contents;s=m.seg('SOUND:MainAdlxPlaying');p=m.off('SOUND:MainAdlxPlaying');mem[s*16+p]=1;mem[s*16+p+1]=0
                    for delta,value in [(4,12),(6,200)]:
                        mem[r.ss*16+((r.sp+delta)&65535)]=value&255;mem[r.ss*16+((r.sp+delta+1)&65535)]=value>>8
                invoke(dlls,states,'StartAdlibTrackChannel');memory=compare(dlls,states,initial,(frame,main,'start'))
            else:assert states[1].ax==8
            bank=m.seg('SOUND:AudioChannelStates');p=m.off('SOUND:AudioChannelStates')+slot*42;writes=[];bursts=0
            event='RunMainAdlxEvents' if main else 'RunEffectAdlxEvents'
            while memory[bank*16+p+40]&1:
                bursts+=1;assert bursts<=20000
                for dll,r in zip(dlls,states):
                    mem=dll.ugh_memory().contents;r.cs=bank
                    r.di=mem[bank*16+p+16]|mem[bank*16+p+17]<<8;r.es=mem[bank*16+p+18]|mem[bank*16+p+19]<<8
                    if not main:
                        at=bank*16+m.off('SOUND:CurrentAdlxRecordOffset');mem[at]=p&255;mem[at+1]=p>>8
                invoke(dlls,states,event);memory=compare(dlls,states,initial,(frame,main,bursts))
                writes.extend(log(dlls[1]))
            registers=[e[3] for e in writes if e[1] in [0x388,0x389]]
            pipelines.append(dict(frame=f'{frame:04X}',main=main,bursts=bursts,outcome='END',register_writes=len(registers)//2,ordered_sha256=hashlib.sha256(bytes(registers)).hexdigest()))
            print(pipelines[-1],flush=True)
    audit=list((C.c_uint32*16).in_dll(dlls[1],'adlx_loader_audit'));assert not audit[2],audit
    allocation=list((C.c_uint32*16).in_dll(dlls[1],'adlx_allocation_audit'));assert not sum(allocation[8:11]),allocation
    save(OUT/'corpus.json',receipt([sys.executable,'verif/adlx_loader_corpus.py'],[Path(__file__),ROOT/'verif/adlx_loader_build.py',ROOT/'tools/dataprobe.py',plain,dataprobe.IMAGE],
        result='PASS',resources=len(streams),loaded_cases=matrix,pipelines=pipelines,loader_audit=audit,allocation_audit=allocation,seconds=time.perf_counter()-started))
    print('loaded cases',len(matrix),'loader',audit,'allocation',allocation,flush=True)
if __name__=='__main__':main()
