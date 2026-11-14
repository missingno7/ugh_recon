"""Standards-shaped generated IFF fixtures through actual import/reset/mix."""
import ctypes as C,struct,sys,hashlib,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_samples_build import OUT,build
from adlx_loader_corpus import begin,compare
from adlx_music_corpus import call
import contacts_reference
contacts_reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,dataprobe
def fixture(length,compression):
    header=struct.pack('>IIIHBBI',length,0,0,8000,1,compression,65536)
    payload=bytes((i*67+139)&255 for i in range(length))
    chunks=b'VHDR'+struct.pack('>I',20)+header+b'BODY'+struct.pack('>I',length)+payload+(b'\0' if length&1 else b'')
    return b'FORM'+struct.pack('>I',4+len(chunks))+b'8SVX'+chunks
def main():
    started=time.perf_counter();plain=contacts_reference.prepare_reference(local=True);dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine();rows=[]
    for length in [0,1,2,7,32,128,63999,64000]:
      for compression in [0,1,2,255]:
       raw=fixture(length,compression);description=dataprobe.parse_form(raw) # Inventory/bounds only.
       for slot in [0,7]:
        for scale in [0,256,512,65535]:
          m.reset();difftest.load_suite('sound_api').base(m,2);m.ww('SOUND:SampleMixerBusy',0);m.ww('SOUND:ActiveSampleVoiceCount',0);m.ww('SOUND:ActiveSampleVoiceMask',0)
          m.ww('SOUND:AudioChannelStates',0,slot*42+40);m.ww('SOUND:AudioChannelStates',0x8000,slot*42+4)
          m.write(0x7100,0x100,raw);args=(slot,0x100,0x7100,255,0 if scale==0 else 2,scale)
          initial,states=begin(m,dlls,'LoadIffSample',args,True)
          for dll,r in zip(dlls,states):assert call(dll,r,'LoadIffSample',m.seg('C:LoadIffSample'),args)==0
          compare(dlls,states,initial,(length,compression,slot,scale,'load'));assert states[0].ax==1
          for dll,r in zip(dlls,states):r.ax=slot;assert call(dll,r,'ResetSampleVoiceCursor',m.seg('SOUND:ResetSampleVoiceCursor'))==0
          compare(dlls,states,initial,(length,compression,slot,scale,'cursor'))
          for dll,r in zip(dlls,states):r.bx=31;r.dx=0x600;assert call(dll,r,'MixSampleVoicePairs',m.seg('SOUND:MixSampleVoicePairs'))==0
          memory=compare(dlls,states,initial,(length,compression,slot,scale,'mix'))
          rows.append(dict(length=length,compression=compression,slot=slot,scale=scale,returned=states[0].ax,output_sha256=hashlib.sha256(memory[m.seg('SOUND:MixSampleVoicePairs')*16+0x600:m.seg('SOUND:MixSampleVoicePairs')*16+0x620]).hexdigest()))
    save(OUT/'corpus.json',receipt([sys.executable,'verif/adlx_samples_corpus.py'],[Path(__file__),ROOT/'verif/adlx_samples_build.py',ROOT/'tools/dataprobe.py',ROOT/'native/adlx_samples.c',ROOT/'native/adlx_samples.h',ROOT/'native/bridge/adlx_samples_bridge.c',plain],result='PASS',generated_cases=len(rows),shipped_samples=0,cases=rows,seconds=time.perf_counter()-started))
    print('PASS',len(rows),'valid IFF import/reset/mix pipelines; shipped samples0',flush=True)
if __name__=='__main__':main()
