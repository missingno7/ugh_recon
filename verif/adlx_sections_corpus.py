"""Scan every shipped resource at successive unit boundaries until C rejects.

Apply each accepted snapshot, then run the actual Tick/main handoff until the
first recurring section application. Decoder supplies inventory only.
"""
import ctypes as C,sys,json,hashlib,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_sections_build import OUT,build
from adlx_loader_corpus import compare,invoke,begin
import contacts_reference
contacts_reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,dataprobe
from emu import LOAD

def put(dll,bank,offset,value,words=1):
    m=dll.ugh_memory().contents
    for i in range(words*2):m[bank*16+offset+i]=(value>>(i*8))&255
def get(dll,bank,offset,words=1):
    m=dll.ugh_memory().contents;return sum(m[bank*16+offset+i]<<(8*i) for i in range(words*2))
def setargs(dlls,states,*args):
    for dll,r in zip(dlls,states):
        r.cs=UGH_C
        for i,value in enumerate(args):put(dll,r.ss,(r.sp+4+i*2)&65535,value)
UGH_C=LOAD+0x878
def main():
    started=time.perf_counter();plain=contacts_reference.prepare_reference(local=True)
    dataprobe.IMAGE=contacts_reference.expanded_image(local=True);dataprobe.OUT=OUT/'format'
    streams=dataprobe.music(dataprobe.validate());dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())]
    machine=difftest.Machine();base=difftest.load_suite('adlib').base;api=difftest.load_suite('sound_api');rows=[];limits=[]
    audit=(C.c_uint32*16).in_dll(dlls[1],'adlx_sections_audit')
    for stream in streams:
        frame=int(stream['frame'],16);accepted=0
        for unit in range(65536):
            rejected=False
            for reserved in [0,1,9]:
                machine.reset();base(machine);api.base(machine,1)
                initial,states=begin(machine,dlls,'LoadAdlibTrackData',(12,0,frame+LOAD,0),True)
                invoke(dlls,states,'LoadAdlibTrackData');compare(dlls,states,initial,(frame,unit,'load'))
                bank=machine.seg('SOUND:AudioChannelStates')
                for dll in dlls:
                    for n,v in dict(MainAdlxPlaying=1,ReservedAdlibChannelCount=reserved,MusicTrackVolume=200,CurrentAdlxSlot=12,
                        MainAdlxSectionLoopEnabled=0,MainAdlxDeadlineLow=0,MainAdlxDeadlineHigh=0,AdlxTickCount=0,AdlxTickHighWord=0,AdlxPlaybackGuard=0).items():put(dll,bank,machine.off('SOUND:'+n),v)
                setargs(dlls,states,unit,min(unit+1,65535));before=list(audit)
                invoke(dlls,states,'ScanMusicEvents');memory=compare(dlls,states,initial,(frame,unit,reserved,'scan'))
                if states[0].ax==65535:
                    limits.append(dict(frame=f'{frame:04X}',first_rejected_unit=unit,scanned_native=audit[3]-before[3],literal=audit[4]-before[4]))
                    rejected=True;break
                assert states[0].ax==1
                start=get(dlls[0],bank,machine.off('SOUND:FirstScannedEvent'))
                end=get(dlls[0],bank,machine.off('SOUND:MainAdlxSectionEnd'))
                delta=get(dlls[0],bank,machine.off('SOUND:ScannedMusicClockTicks'),2)
                for r in states:r.cs=UGH_C
                invoke(dlls,states,'ApplyScannedMusicEvents');compare(dlls,states,initial,(frame,unit,reserved,'initial apply'))
                boundary_before=audit[8];ticks=0;ports=[]
                while audit[8]==boundary_before:
                    ticks+=1;assert ticks<20000,(frame,unit,'handoff bound')
                    # Advance directly to the next due event. Both actual
                    # schedulers still increment/read/retest their own clocks.
                    for dll,r in zip(dlls,states):
                        deadline=get(dll,bank,machine.off('SOUND:MainAdlxDeadlineLow'),2)
                        put(dll,bank,machine.off('SOUND:AdlxTickCount'),(deadline-1)&0xffffffff,2);r.cs=bank
                    invoke(dlls,states,'TickAdlxPlayback');compare(dlls,states,initial,(frame,unit,reserved,ticks))
                    dev=dlls[1].ugh_device_state().contents;ports.extend((e.port,e.value) for e in dev.log[:dev.count])
                packed=bytes(v for p,v in ports if p in [0x388,0x389]);assert len(packed)%2==0
                rows.append(dict(frame=f'{frame:04X}',unit=unit,reserved=reserved,start=start,end=end,duration=delta,ticks=ticks,
                    register_writes=len(packed)//2,ordered_sha256=hashlib.sha256(packed).hexdigest(),native_scan=audit[3]-before[3],scan_literal=audit[4]-before[4]))
                accepted+=1
            if rejected:break
        else:raise AssertionError('no finite scan rejection in the entire unit-word domain')
        print(f'{frame:04X}: {accepted} scan/apply/handoff configurations; first rejection {unit}',flush=True)
    save(OUT/'corpus.json',receipt([sys.executable,'verif/adlx_sections_corpus.py'],[Path(__file__),ROOT/'verif/adlx_sections_build.py',ROOT/'verif/adlx_loader_corpus.py',ROOT/'tools/dataprobe.py',plain,dataprobe.IMAGE],
        result='PASS',resources=len(streams),sections=rows,limits=limits,sections_audit=list(audit),seconds=time.perf_counter()-started))
    print('sections',len(rows),'audit',list(audit),flush=True)
if __name__=='__main__':main()
