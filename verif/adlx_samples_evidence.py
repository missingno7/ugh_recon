"""Full compiled L1/native sample output/RAM comparisons, generated fixtures."""
import ctypes as C,random,struct,time,sys,hashlib
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_samples_build import OUT,build
sys.path.insert(0,str(ROOT/'tools'))
from adlx_samples_cases import sample
import difftest,nbuild,dataprobe
import contacts_reference
contacts_reference.OUT=OUT/'reference'
def main():
    start=time.perf_counter();plain=contacts_reference.prepare_reference(local=True)
    dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine();rng=random.Random(913771);initial=bytearray(m.snapshot());sound=m.seg('SOUND:AudioChannelStates');base=sound*16
    cases=[];stackbase=0x80000
    def word(memory,label,value,delta=0):struct.pack_into('<H',memory,base+m.off('SOUND:'+label)+delta,value&65535)
    def run(name,memory,args=(),registers=None):
        frames=[];statuses=[];outputs=[];logs=[]
        for dll in dlls:
            C.memmove(dll.ugh_memory().contents,bytes(memory),len(memory));dll.ugh_devices_reset()
            r=difftest.Regs(ax=0xa5c3,bx=0x5a3c,cx=0xc35a,dx=0x5ac3,si=0x6996,di=0x9669,bp=0x7e81,sp=0x1000,cs=0x1888 if name=='LoadIffSample' else sound,ds=0x7340,es=0x7c20,ss=0x8000,flags=rng_flags)
            for key,value in (registers or {}).items():setattr(r,key,value)
            mem=dll.ugh_memory().contents
            for i,value in enumerate(args):C.memmove(C.addressof(mem)+stackbase+0x1004+2*i,struct.pack('<H',value),2)
            f=getattr(dll,'c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r));statuses.append(status);frames.append(bytes(r));outputs.append(bytes(mem))
            d=dll.ugh_device_state().contents;assert not d.error;logs.append([(e.kind,e.port,e.size,e.value) for e in d.log[:d.count]])
        assert statuses[0]==statuses[1],(name,len(cases),'status',statuses)
        assert frames[0]==frames[1],(name,len(cases),'registers')
        # Scratch below the calling frame has the established L1 ABI lifetime.
        assert outputs[0][:stackbase]==outputs[1][:stackbase] and outputs[0][stackbase+0x1000:]==outputs[1][stackbase+0x1000:],(name,len(cases),'RAM',next((i for i,(x,y) in enumerate(zip(*outputs)) if x!=y),None))
        assert logs[0]==logs[1],(name,len(cases),'ports')
        cases.append(dict(name=name,status=statuses[0],output_sha256=hashlib.sha256(outputs[1][base:base+65537]).hexdigest()))
    for i in range(1200):
        memory=bytearray(initial);memory[base:base+65537]=rng.randbytes(65537);rng_flags=rng.randrange(65536)
        count=rng.choice([0,1,2,8,0x8000,65535]);mask=rng.randrange(256)|0xa500
        word(memory,'ActiveSampleVoiceCount',count);word(memory,'ActiveSampleVoiceMask',mask)
        for voice in range(8):
            d=42*voice;sourcebank=0x7100;source=rng.choice([0,1,0xfffe,0xffff])
            if i%5==0:sourcebank=sound;source=rng.choice([m.off('SOUND:SampleMixFirstSum'),m.off('SOUND:ActiveSampleVoiceCount'),m.off('SOUND:SampleVoicePairCursor')+d,0x600])
            else:memory[sourcebank*16:sourcebank*16+65537]=bytes(range(256))*256+b'\x7f'
            for label,value in [('SampleVoicePairCursor',rng.choice([0,1,65535,32768])),('SampleVoiceByteLength',rng.choice([0,1,2,8,65535])),('SampleVoiceStepQ8',rng.choice([0,1,255,256,512,65535])),('SampleVoiceRepeatCount',rng.choice([0,1,2,0x8000,65535])),('SampleVoiceFlags',rng.choice([0,2,0xffff])),('SampleVoiceVolume',rng.randrange(65536)),('SampleVoiceDataPointer',source)]:word(memory,label,value,d)
            word(memory,'SampleVoiceDataPointer',sourcebank,d+2)
        destination=rng.choice([0x600,0xffff,m.off('SOUND:ActiveSampleVoiceCount'),m.off('SOUND:SampleMixFirstSum'),m.off('SOUND:AudioChannelStates')+16])
        run('MixSampleVoicePairs',memory,registers=dict(bx=rng.choice([0,1,2,3,4,7,16,31]),dx=destination))
    for i in range(600):
        memory=bytearray(initial);rng_flags=rng.randrange(65536);word(memory,'SoundDeviceBits',rng.choice([0,1,2,3]));word(memory,'SampleMixerBusy',0)
        bank,offset=rng.choice([(0x7100,0x100),(0xf000,0xfff9),(0xffff,15),(0xffff,0xffff)])
        raw=bytearray(sample(rng.choice([0,1,7,64000,64001,65536,0xffffffff]),rng.randrange(256),root=rng.choice([0,64,128,0xfffffff0])))
        if i%3==0:raw[rng.randrange(min(len(raw),48))]=rng.randrange(256)
        origin=bank*16+offset
        for j,value in enumerate(raw):memory[(origin+j)&0xfffff]=value
        if origin>=0x100000:memory[origin]=raw[0] # initial non-normalized read
        run('LoadIffSample',memory,(rng.choice([0,7,8,65535]),offset,bank,rng.randrange(65536),rng.choice([0,1,2,65535]),rng.randrange(65536)))
    for index in range(65536):
        # Complete reset-word domain; compare just the independently compiled
        # result, both physical store bytes and register/flag frame.
        memory=bytearray(initial);rng_flags=(index*17)&65535;run('ResetSampleVoiceCursor',memory,registers=dict(ax=index))
    dataprobe.IMAGE=contacts_reference.expanded_image(local=True);dataprobe.OUT=OUT/'format';inventory=dataprobe.music(dataprobe.validate())
    image=dataprobe.validate().image;hits=[];position=0
    while True:
        position=image.find(b'FORM',position)
        if position<0:break
        hits.append(dict(offset=position,type=image[position+8:position+12].hex(),sample=image[position+8:position+12]==b'8SVX'));position+=1
    assert not any(row['sample'] for row in hits)
    save(OUT/'samples.json',receipt([sys.executable,'verif/adlx_samples_evidence.py'],[Path(__file__),ROOT/'verif/adlx_samples_cases.py',ROOT/'verif/adlx_samples_build.py',ROOT/'native/adlx_samples.c',ROOT/'native/adlx_samples.h',ROOT/'native/bridge/adlx_samples_bridge.c',ROOT/'native/audio.h',ROOT/'c/sound_engine.c',ROOT/'c/sound_api.c',ROOT/'tools/dataprobe.py',plain,dataprobe.IMAGE],result='PASS',cases=cases,shipped_samples=0,raw_FORM_hits=hits,adlx_resources=len(inventory),seconds=time.perf_counter()-start))
    print('PASS',len(cases),'compiled cases;1200 mixer,600 importer,65536 reset words; shipped samples0',flush=True)
if __name__=='__main__':main()
