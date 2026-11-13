"""Execute every shipped stream to END on compiled independent L1 and L2.

The format decoder supplies only the resource census/byte bounds, never expected
register writes. Each actual compiled interpreter supplies its own ordered log.
"""
import argparse,ctypes as C,hashlib,json,sys,time,struct
from closure_support import ROOT,receipt,save
from adlx_main_build import OUT,build
import contacts_reference
contacts_reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,dataprobe
from emu import LOAD

def events(dll):
    dev=dll.ugh_device_state().contents
    assert not dev.error
    return [(e.kind,e.port,e.size,e.value) for e in dev.log[:dev.count]]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--effects',action='store_true');args=parser.parse_args()
    start=time.perf_counter();plain=contacts_reference.prepare_reference(local=True)
    dataprobe.IMAGE=contacts_reference.expanded_image(local=True);dataprobe.OUT=OUT/'format'
    streams=dataprobe.music(dataprobe.validate())
    candidate=nbuild.load_l1(build());reference=nbuild.load_l1(build(reference=True));m=difftest.Machine()
    suite=difftest.load_suite('adlib');rows=[]
    for stream in streams:
        frame=int(stream['frame'],16)
        if args.effects and stream['track_length']>100:continue
        configurations=[(stream['channels'],8,0,1),(stream['channels'],8,1,1),(stream['channels'],8,1,2)] if args.effects else [(0,12,1,1),(2,12,1,1),(9,12,1,1),(0x10,13,0,1),(0x101,12,1,1),(10,12,1,1),(2,13,0,2)]
        routine='RunEffectAdlxEvents' if args.effects else 'RunMainAdlxEvents'
        for reserved,slot,playing,repeat in configurations:
            m.reset();suite.base(m)
            assert m.read(frame+LOAD,42,stream['track_length'])==bytes.fromhex(''.join(e['raw'] for e in stream['events']))
            for key,value in dict(CurrentAdlxSlot=slot,ReservedAdlibChannelCount=reserved,MainAdlxPlaying=playing,
                    MainAdlxFlags=1,MainAdlxRepeatCount=repeat,MainAdlxStartPointer=42,MainAdlxStartSegment=frame+LOAD,
                    MainAdlxCursor=42,MainAdlxCursorSegment=frame+LOAD,AdlxTickCount=0xfffc,AdlxTickHighWord=0xffff,
                    MainAdlxDeadlineLow=0xfffc,MainAdlxDeadlineHigh=0xffff).items():m.ww('SOUND:'+key,value)
            if args.effects:
                m.ww('SOUND:SoundDeviceBits',1);m.ww('SOUND:MusicVoiceCount',9)
                m.ww('SOUND:AdlxTimerPeriod',0x1843 if playing else 0)
                effect=m.off('SOUND:AudioChannelStates')+8*42
                for field,value in [(4,repeat),(6,42),(8,frame+LOAD),(16,42),(18,frame+LOAD),(28,0xc8),
                        (30,0xfffc),(32,0xffff),(34,stream['channels']),(36,9-reserved),(38,256),(40,5)]:
                    m.write(m.seg('SOUND:AudioChannelStates'),effect+field,struct.pack('<H',value))
            initial=m.prepare('SOUND:'+routine,difftest.POISON,'far',(),0x602)
            for dll in (reference,candidate):
                C.memmove(dll.ugh_memory().contents,m.snapshot(),difftest.MEM_SIZE);dll.ugh_devices_reset()
            states=[difftest.Regs(**{n.lower():v for n,v in initial.items()}) for _ in range(2)]
            s=m.seg('SOUND:MainAdlxFlags');o=m.off('SOUND:MainAdlxFlags');base=s*16
            cursor=m.off('SOUND:MainAdlxCursor');bank=m.off('SOUND:MainAdlxCursorSegment')
            if args.effects:o=effect+40;cursor=effect+16;bank=effect+18
            total_writes=[];batches=0
            while batches<20000:
                batches+=1
                logs=[]
                for dll,r in zip((reference,candidate),states):
                    mem=dll.ugh_memory().contents
                    r.di=mem[base+cursor]|mem[base+cursor+1]<<8;r.es=mem[base+bank]|mem[base+bank+1]<<8
                    assert r.es==frame+LOAD and 42<=r.di<42+stream['track_length']
                    dll.ugh_device_state().contents.count=0
                    fn=getattr(dll,'c_'+routine);fn.argtypes=[C.POINTER(difftest.Regs)];fn.restype=C.c_int
                    assert fn(C.byref(r))==0
                    logs.append(events(dll))
                assert logs[0]==logs[1],(frame,reserved,slot,batches,'ordered writes')
                total_writes.extend((e[1]-0x388,e[3]) for e in logs[0] if e[1] in (0x388,0x389))
                left,right=[bytes(d.ugh_memory().contents) for d in (reference,candidate)]
                # The dedicated stack scratch below the incoming frame is not
                # persistent audio state; same exclusion as difftest.run.
                lo=initial['SS']*16;hi=lo+initial['SP']
                assert left[:lo]==right[:lo] and left[hi:]==right[hi:],(frame,reserved,slot,batches,'RAM')
                for n in ('ax','bx','cx','dx','si','di','bp','ds','es','ss','sp'):
                    assert getattr(states[0],n)==getattr(states[1],n),(frame,reserved,slot,batches,n)
                assert (states[0].flags&0x600)==(states[1].flags&0x600)
                if not left[base+o]&1:break
            else:raise AssertionError('stream failed to reach END within 20000 bursts')
            assert len(total_writes)%2==0
            writes=[(total_writes[i][1],total_writes[i+1][1]) for i in range(0,len(total_writes),2)]
            rows.append(dict(frame=f'{frame:04X}',reserved=reserved,current_channel=slot,playing=playing,passes=repeat,
                bound=20000,batches=batches,register_writes=len(writes),ordered_sha256=hashlib.sha256(bytes(v for pair in writes for v in pair)).hexdigest()))
            print(rows[-1],flush=True)
    audit=(C.c_uint32*32).in_dll(candidate,'adlx_main_audit')
    assert not audit[17] and not audit[18]
    if not args.effects:assert audit[16]==8*sum(len(stream['events']) for stream in streams)
    else:assert len(rows)==24
    save(OUT/('effects-corpus.json' if args.effects else 'corpus.json'),receipt(['python','verif/adlx_main_corpus.py',*sys.argv[1:]],
        [__file__,ROOT/'tools/dataprobe.py',plain,dataprobe.IMAGE,ROOT/'verif/adlx_main_build.py'],
        result='PASS',streams=rows,native_steps=audit[16],fallbacks=list(audit)[17:19],seconds=time.perf_counter()-start))
if __name__=='__main__':main()
