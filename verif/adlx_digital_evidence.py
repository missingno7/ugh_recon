"""Generated digital API cases, full RAM/ABI/ordered ports; no game reach claim."""
import ctypes as C,random,struct,sys,time,hashlib
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_digital_build import OUT,build,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest,nbuild
from adlx_samples_cases import sample
contacts_reference.OUT=OUT/'reference'

def main():
 start=time.perf_counter();plain=contacts_reference.prepare_reference(local=True);dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine();rng=random.Random(10407);api=difftest.load_suite('sound_api');dsps=difftest.load_suite('dsp');rows=[]
 def pair(name,args=(),regs=None):
  bank='C:' if name in NAMES[:3] else 'SOUND:';initial=m.prepare(bank+name,{**difftest.POISON,**(regs or {})},'far' if name not in ['HandleSampleDmaInterrupt','HandleDspProbeInterrupt'] else 'iret',args,rng.choice([0x202,0x602,0xed7]));memory=m.snapshot();device=m.device.state();outputs=[];states=[];events=[];statuses=[];errors=[]
  for dll in dlls:
   C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device));r=difftest.Regs(**{n.lower():v for n,v in initial.items()});f=getattr(dll,'c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];statuses.append(f(C.byref(r)));outputs.append(bytes(dll.ugh_memory().contents));states.append(bytes(r));events.append([(e.kind,e.port,e.size,e.value) for e in dev.log[:dev.count]]);errors.append(dev.error)
  assert statuses[0]==statuses[1] and errors[0]==errors[1],(name,len(rows),'status',statuses,errors)
  assert states[0]==states[1],(name,len(rows),'ABI',struct.unpack('<14H',states[0]),struct.unpack('<14H',states[1]))
  lo=initial['SS']*16;hi=lo+initial['SP'];assert outputs[0][:lo]==outputs[1][:lo] and outputs[0][hi:]==outputs[1][hi:],(name,len(rows),'RAM',next((i for i,(a,b) in enumerate(zip(*outputs)) if a!=b and not lo<=i<hi),None))
  assert events[0]==events[1],(name,len(rows),'ports');rows.append(dict(name=name,status=statuses[0],error=errors[0],events=len(events[0]),state_sha256=hashlib.sha256(outputs[1]).hexdigest()))
 for name in NAMES:
  for i in range(120):
   m.reset();api.base(m,rng.choice([0,1,2,3,0xfffd,0xffff]));dsps.dsp(m,base=0x220,status=[0x80]*(i%7)+[i%128]*4,reads=[0x7f]*(i%9)+[0x80]);m.device.script(0x22a,[rng.randrange(256)]);m.ww('SOUND:SoundIoDelayMultiplier',0);m.ww('SOUND:SampleMixerBusy',0);m.ww('SOUND:ActiveSampleVoiceCount',0);m.ww('SOUND:ActiveSampleVoiceMask',rng.randrange(65536));m.wb('SOUND:DspIrqBusy',rng.randrange(256));m.wb('SOUND:DmaMixBufferSelect',rng.randrange(256));m.wb('SOUND:DspPicIrqMask',rng.randrange(256));m.write(0,0x20,struct.pack('<HH',0x100,0xf000))
   for site in ['loc_1163','loc_116B']:m.device.schedule(m.seg('SOUND:'+site),m.off('SOUND:'+site),clocks=65536)
   args=();regs=None
   if name=='StopSoundChannel':args=(rng.choice([0,1,7,8,11,12,13,0xffff]),)
   elif name=='LoadSoundBankResource':args=tuple(rng.randrange(65536) for _ in range(6))
   elif name=='LoadBankSoundByIndex':
    base=0x71000;index=rng.choice([0,1,5461,5462,65535]);entry=(base+16+(index*12&65535)+8)&1048575;source=(base+0x300)&1048575;m.ww('SOUND:SoundBankBase',0);m.ww('SOUND:SoundBankBase',0x7100,2);m.ww('SOUND:SoundBankLength',rng.choice([0,0x4000,0xffff]));m.ww('SOUND:SoundBankLength',0,2);m.write(0x7100,0,struct.pack('<I',16));m.write(entry>>4,entry&15,struct.pack('<I',0x300));fixture=sample(64)
    if i%3==1:fixture=b'ADLX'+bytes(4)+b'AHDR'+bytes(64)
    elif i%3==2:fixture=rng.randbytes(90)
    m.write(source>>4,source&15,fixture);args=(rng.choice([0,7,8,11,12,65535]),index,255,1,256)
   elif name=='SetDspSampleRate':args=(rng.choice([0,1,999,1000,1001,3906,3907,8000,65535]),)
   elif name=='StartDmaSampleBlock':regs=dict(BX=rng.randrange(65536),DX=rng.randrange(65536),CX=rng.randrange(65536))
   elif name=='HandleSampleDmaInterrupt':
    dsps.buffers(m,counts=(rng.choice([0,39,40,1024,65535]),rng.choice([0,39,40,1024,65535])));dsps.voice(m,rng.choice(['none','silent','sample','expire']));m.wb('SOUND:DspIrqBusy',rng.choice([0,2,3,254,255]))
   elif name=='PrimeSampleDmaPlayback':
    dsps.buffers(m,counts=(0,0));dsps.voice(m,rng.choice(['none','silent','sample','expire']));m.ww('SOUND:SampleMixerBusy',0);m.wb('SOUND:DspIrqBusy',0)
   pair(name,args,regs)
 for i in range(300):
  m.reset();api.base(m,2);bank=rng.choice([0x7100,0xfff0,0xffff,0x4000]);offset=rng.choice([0,15,0xfffe,0xffff]);base=bank*16+offset;index=rng.randrange(65536);directory=rng.randrange(1<<32);length=rng.randrange(1<<32);entry=(base+directory+(index*12&65535)+8)&1048575;displacement=rng.randrange(1<<32);source=(base+displacement)&1048575
  m.ww('SOUND:SoundBankBase',offset);m.ww('SOUND:SoundBankBase',bank,2);m.ww('SOUND:SoundBankLength',length&65535);m.ww('SOUND:SoundBankLength',length>>16,2)
  m.write(bank,offset,struct.pack('<H',directory&65535));m.write(bank,(offset+2)&65535,struct.pack('<H',directory>>16));m.write(entry>>4,entry&15,struct.pack('<I',displacement));m.write(source>>4,source&15,b'X'+rng.randbytes(12))
  pair('LoadBankSoundByIndex',(rng.choice([0,7,8,11,12,65535]),index,65535,0,256))
 save(OUT/'digital-cases.json',receipt([sys.executable,'verif/adlx_digital_evidence.py'],[Path(__file__),ROOT/'verif/adlx_digital_build.py',ROOT/'native/adlx_digital.c',ROOT/'native/adlx_digital.h',ROOT/'native/bridge/adlx_digital_bridge.c',ROOT/'c/dsp.c',ROOT/'c/sound_api.c',ROOT/'c/sound_engine.c',plain],result='PASS',scope='unreachable in the shipped program; API-only compiled fixture',cases=rows,seconds=time.perf_counter()-start));print('PASS',len(rows),'digital API pairs',flush=True)
if __name__=='__main__':main()
