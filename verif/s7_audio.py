"""Production AdLib composition: independent recorder and 143-stream replay."""
from pathlib import Path
import argparse,ctypes as C,hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from job_pool import run,save
from cbuild import GCC
import nativebuild,s7_audio_record

def objects(prod):
    m=json.loads((ROOT/'metadata/native-manifest.json').read_text())
    return [prod/('object-%02d.o'%i) for i,s in enumerate(m['core']+m['backends']['test']) if s!='port/test/main.c']

def executable(source,folder,prod,replacements=None):
    obj=folder/'observer.o';exe=folder/'observer.exe'
    run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT,'-I',ROOT/'port','-I',prod,'-c',source,'-o',obj],ROOT,folder,'compile')
    inputs=[(replacements or {}).get(p,p) for p in objects(prod)]
    run([GCC,*inputs,obj,'-o',exe],ROOT,folder,'link');return exe

def cases(out,prod):
    folder=out/'cases';folder.mkdir(exist_ok=True);exe=executable(ROOT/'verif/s7_audio_cases.c',folder,prod)
    print(run([exe,prod/'ugh.res'],ROOT,folder,'run')['stdout'].strip(),flush=True)
    return dict(result='PASS')

def boot(out,prod):
    folder=out/'boot';folder.mkdir(exist_ok=True);source=s7_audio_record.generate(folder)
    exe=executable(source,folder,prod);r=run([exe,prod/'ugh.res',folder/'baseline.bin',folder],ROOT,folder,'record')
    got=[json.loads(x) for x in r['stdout'].splitlines()]
    # The original scenario uses no card. The AdLib scenario skips the last
    # pictures after Escape and has exactly three records before main menu.
    want=json.loads((ROOT/'build/whole/adlib.ref.json').read_text())['frames'][:3]
    diffs=[dict(frame=i,field=k,actual=a[k],expected=b[k]) for i,(a,b) in enumerate(zip(got,want)) for k in a if a[k]!=b[k]]
    if len(got)!=3:diffs.append(dict(field='count',actual=len(got),expected=3))
    save(folder/'actual.json',got);save(folder/'differences.json',diffs)
    assert not diffs,[(d.get('frame'),d['field']) for d in diffs]
    print('PASS AdLib boot 3/3 complete records',flush=True)
    return dict(result='PASS',reference='adlib boot prefix',records=3)

def reference(folder):
    """Existing accepted corpus configurations, independently executed L1.

    Expected state never enters the production process. This adapter has the
    entire machine environment solely to execute the historical comparator.
    """
    import difftest,dataprobe,cgen
    from emu import LOAD
    dll=difftest.load_dll(folder/'literal.dll');m=difftest.Machine();base=difftest.load_suite('adlib').base
    mz,_=cgen.read_symbols();streams=dataprobe.music(mz);rows=[];row=0
    fns={name:getattr(dll,'c_'+name) for name in ['RunMainAdlxEvents','RunEffectAdlxEvents']}
    for f in fns.values():f.argtypes=[C.POINTER(difftest.Regs)];f.restype=C.c_int
    for effects in [False,True]:
      for resource,stream in enumerate(streams):
       frame=int(stream['frame'],16)
       configs=[(stream['channels'],8,0,1),(stream['channels'],9,1,1),(stream['channels'],10,1,2),(stream['channels'],11,0,1),(stream['channels'],8,1,1),(stream['channels'],11,1,0)] if effects else [(0,12,1,1),(2,12,1,1),(9,12,1,1),(16,13,0,1),(257,12,1,1),(10,12,1,1),(2,13,0,2)]
       for reserved,slot,playing,repeat in configs:
        m.reset();base(m)
        for key,v in dict(CurrentAdlxSlot=slot,ReservedAdlibChannelCount=reserved,MainAdlxPlaying=playing,MainAdlxFlags=1,MainAdlxRepeatCount=repeat,MainAdlxStartPointer=42,MainAdlxStartSegment=frame+LOAD,MainAdlxCursor=42,MainAdlxCursorSegment=frame+LOAD,AdlxTickCount=0xfffc,AdlxTickHighWord=0xffff,MainAdlxDeadlineLow=0xfffc,MainAdlxDeadlineHigh=0xffff).items():m.ww('SOUND:'+key,v)
        selected=12
        if effects:
            selected=slot;m.ww('SOUND:SoundDeviceBits',1);m.ww('SOUND:MusicVoiceCount',9)
            m.ww('SOUND:AdlxTimerPeriod',0x7fff if slot==11 else 100 if slot==8 and playing else 0x1843 if playing else 0)
            effect=m.off('SOUND:AudioChannelStates')+slot*42;m.ww('SOUND:CurrentAdlxRecordOffset',effect)
            for field,v in [(4,repeat),(6,42),(8,frame+LOAD),(16,42),(18,frame+LOAD),(28,200),(30,0xfffc),(32,0xffff),(34,stream['channels']),(36,9-reserved),(38,256),(40,5 if repeat else 7)]:m.write(m.seg('SOUND:AudioChannelStates'),effect+field,struct.pack('<H',v))
        routine='RunEffectAdlxEvents' if effects else 'RunMainAdlxEvents'
        initial=m.prepare('SOUND:'+routine,difftest.POISON,'far',(),0x602);memory=dll.ugh_memory().contents
        C.memmove(memory,m.snapshot(),difftest.MEM_SIZE);dll.ugh_devices_reset();dev=dll.ugh_device_state().contents
        r=difftest.Regs(**{n.lower():v for n,v in initial.items()});sound=m.seg('SOUND:AudioChannelStates')*16;track=m.off('SOUND:AudioChannelStates')+42*selected
        def value(name,n=2):
            at=sound+m.off('SOUND:'+name);return int.from_bytes(memory[at:at+n],'little')
        def cell(delta,n=2):return int.from_bytes(memory[sound+track+delta:sound+track+delta+n],'little')
        ordered=hashlib.sha256();clock=bytearray();passes=0;writes=0
        for burst in range(1,20001):
            r.di=cell(16);r.es=cell(18);dev.count=0
            assert fns[routine](C.byref(r))==0,(frame,effects,slot,burst)
            raw=bytearray(e.value for e in dev.log[:dev.count] if e.port in (0x388,0x389));ordered.update(raw);writes+=len(raw)//2
            clock+=struct.pack('<12I',value('AdlxTickCount',4),value('MainAdlxTimeOrigin',4),value('MusicTicksPerUnit'),value('MainAdlxPlaying'),value('MainAdlxSectionLoopEnabled'),cell(30,4),cell(16),cell(40),value('AdlxTimerPeriod'),cell(38),value('CurrentAdlxSlot'),value('ReservedAdlibChannelCount'))
            if effects and cell(16)==42:passes+=1
            if not cell(40)&1 or effects and not repeat and passes==2:break
        else:raise AssertionError('corpus burst bound')
        (folder/f'clock-{row}.bin').write_bytes(clock)
        rows.append(dict(row=row,resource=resource,effects=int(effects),reserved=reserved,slot=slot,playing=playing,repeat=repeat,bursts=burst,writes=writes,opl=ordered.hexdigest()));row+=1
    save(folder/'records.json',rows)

def corpus(out,prod):
    folder=out/'corpus';folder.mkdir(exist_ok=True);literal=folder/'reference';literal.mkdir(exist_ok=True)
    exe=executable(ROOT/'verif/s7_audio_corpus.c',folder,prod)
    row=run([exe,prod/'ugh.res',folder],ROOT,folder,'production')
    got=[json.loads(x) for x in row['stdout'].splitlines()]
    run([sys.executable,__file__,'--reference-worker',literal],ROOT,folder,'reference')
    want=json.loads((literal/'records.json').read_text());assert len(got)==len(want)==143
    diffs=[]
    for a,b in zip(got,want):
        if a!=b:diffs.append(dict(row=a['row'],actual=a,expected=b))
        x=(folder/f'clock-{a["row"]}.bin').read_bytes();y=(literal/f'clock-{a["row"]}.bin').read_bytes()
        if x!=y:diffs.append(dict(row=a['row'],field='clock',first_byte=next((i for i,(p,q) in enumerate(zip(x,y)) if p!=q),min(len(x),len(y)))))
    save(folder/'actual.json',got);save(folder/'differences.json',diffs);assert not diffs,diffs[:5]
    print('PASS 11 ADLX resources / 143 configurations: ordered OPL and every burst clock',flush=True)
    return dict(result='PASS',resources=11,configurations=143,bursts=sum(r['bursts'] for r in got),register_writes=sum(r['writes'] for r in got))

def negative(out,prod):
    """Compile mutations only in scratch, replacing one production object."""
    m=json.loads((ROOT/'metadata/native-manifest.json').read_text());index=m['core'].index('native/compose_audio.c')
    original=(ROOT/'native/compose_audio.c').read_text();controls=[]
    for name,old,new,recorder in [
        ('dropped-clock','if(!audio_section_tick_begin(&w->audio))return GS_OK;',
         'if(!audio_section_tick_begin(&w->audio))return GS_OK;w->audio.ticks--;','boot'),
        ('opl-register','(GSRegisterWrite){writes[i].reg,writes[i].value}',
         '(GSRegisterWrite){writes[i].reg^1u,writes[i].value}','corpus')]:
        assert original.count(old)==1
        folder=out/('defect-'+name);folder.mkdir(exist_ok=True);copy=folder/'compose_audio.c';copy.write_text(original.replace(old,new));obj=folder/'audio.o'
        run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT,'-I',ROOT/'native','-I',prod,'-c',copy,'-o',obj],ROOT,folder,'mutant')
        source=s7_audio_record.generate(folder) if recorder=='boot' else ROOT/'verif/s7_audio_corpus.c'
        exe=executable(source,folder,prod,{prod/('object-%02d.o'%index):obj})
        args=[exe,prod/'ugh.res',folder/'baseline.bin',folder] if recorder=='boot' else [exe,prod/'ugh.res',folder]
        r=run(args,ROOT,folder,'run');got=[json.loads(x) for x in r['stdout'].splitlines()]
        if recorder=='boot':
            want=json.loads((ROOT/'build/whole/adlib.ref.json').read_text())['frames'][:3]
            caught=[i for i,(a,b) in enumerate(zip(got,want)) if a['ram']!=b['ram']]
        else:
            want=json.loads((out/'corpus/reference/records.json').read_text())
            caught=[i for i,(a,b) in enumerate(zip(got,want)) if a['opl']!=b['opl']]
        assert caught,name+' escaped';controls.append(dict(defect=name,detected=caught))
    save(out/'negative.json',dict(result='PASS',controls=controls));print('PASS audio negative controls 2/2',flush=True)
    return dict(result='PASS',controls=2)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=ROOT/'build/workers/s7-audio');p.add_argument('--no-build',action='store_true');p.add_argument('--reference-worker',type=Path);p.add_argument('--boot-only',action='store_true');a=p.parse_args()
    if a.reference_worker:return reference(a.reference_worker)
    out=a.out.resolve();out.mkdir(exist_ok=True,parents=True);prod=out/'production'
    (out/'receipt.json').unlink(missing_ok=True)
    if not a.no_build:nativebuild.build('test',prod)
    audited=json.loads((prod/'nativebuild.json').read_text())
    assert audited['result']=='PASS' and audited['backend']=='test'
    assert audited['manifest']==nativebuild.sha(ROOT/'metadata/native-manifest.json')
    for name,digest in audited['inputs'].items():assert nativebuild.sha(ROOT/name)==digest,'stale production input: '+name
    results=dict(boot=boot(out,prod))
    if not a.boot_only:
        results['cases']=cases(out,prod);results['corpus']=corpus(out,prod)
        import s7_audio_front
        results['front']=s7_audio_front.verify(out,prod)
        results['negative']=negative(out,prod)
    inputs=['verif/s7_audio.py','verif/s7_audio_front.py','verif/s7_audio_record.py','verif/s7_audio_corpus.c','verif/s7_audio_cases.c','tools/audio_data.py']
    save(out/'receipt.json',dict(result='PASS',production_receipt_sha256=nativebuild.sha(prod/'nativebuild.json'),verification_inputs={n:nativebuild.sha(ROOT/n) for n in inputs},**results))
if __name__=='__main__':main()
