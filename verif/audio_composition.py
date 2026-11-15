"""Second audio/timer ownership cut; serial bounded generated-copy evidence."""
import argparse,hashlib,inspect,json,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-adlx-23'
sys.path.insert(0,str(ROOT/'tools'))
import timing_composition as prior
prior.OUT=OUT;prior.common.OUT=OUT
bounded=prior.bounded;save=prior.save;sha=prior.sha
NEW_FILES=['native/audio_world.h','native/audio_world.c','native/bridge/audio_world_bridge.h','native/bridge/audio_world_bridge.c','native/bridge/audio_composition_api.h']
BASE_FILES=[*NEW_FILES,'native/timing_world.h','native/audio_bytes.h','native/bridge/timing_world_bridge.c','native/bridge/timing_world_bridge.h','native/bridge/audio_projection.h','tools/hostbuild.py','verif/audio_composition.py','verif/timing_composition.py','verif/standalone_census.py','verif/projector_evidence.py','verif/projector/observer.c','verif/projector/publications.py',*[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'native/bridge').glob('adlx_*_bridge.c'))]]
prior.BASE_FILES=BASE_FILES

def files():
 changed=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
 allowed=[f for f in changed if f.startswith('metadata/closure/') or f in BASE_FILES or f.startswith('verif/projector/') or f in ['host/main.c','host/digest.c','verif/standalone_census.py','verif/projector_evidence.py']]
 return sorted(set(BASE_FILES+allowed+['metadata/closure/audio_world.json']))
prior.files=files
_original_snapshot=prior.snapshot

def snapshot():
 target=_original_snapshot()
 p=target/'metadata/closure/audio_world.json';c=json.loads(p.read_text());c['status']='migrated';save(p,c)
 for bank in ['levels','levels-audio','levels-deep']:
  src=ROOT/'build'/bank
  if src.exists():
   dest=target/'build'/bank;dest.mkdir(parents=True,exist_ok=True)
   for p in src.glob('*.ref.json'):shutil.copyfile(p,dest/p.name)
 return target
prior.snapshot=snapshot

def relock(final=False):
 import closure
 p=ROOT/'metadata/closure/audio_world.json'
 if not p.exists():
  cert=dict(component='audio_world',status='unanalyzed',original=dict(owned=[],composes=['timing_world','audio']),native=dict(files=NEW_FILES,functions=['audio_world_borrow'],bridge='native owner and typed peer interop'),purpose='Rest of the audio owner, sealed RAM and direct peer services',interface=dict(inputs='Cold fixture; borrowed resources; synchronous ordered services',outputs='Native audio ownership and a separate observation serialization'),callers=['Existing external entry ABI; typed timer callback delivery'],callees=['Accepted audio/timer pure kernels and native peer adapters; platform services'],indirect=['Typed AudioPeerRole; open peer targets fail closed. Broken external hooks remain explicit services.'],memory=dict(owner='NativeTimingWorld.audio; clock words remain in NativeTimingWorld.music',aliases='One physical binding per byte; record12 and channel9 use existing channel/saved voice records',observations='Cold import only; sealed machine lanes, native serializer, no RAM write-back or journal for moved fields'),assumptions=['Current deterministic backend; legacy literal/API profile unchanged','Admitted contracts of accepted audio/timer kernels; unsupported requests fail closed'],eliminated=['RAM ownership/projection of audio state in composed profile; audio/timer peer dispatcher hops'],retained=['Original aliases, raw current record/slot, fades, PCM and DMA stale storage; resource and external IRQ bindings','Unreachable shipped SB path and all broken external hook transfers remain unchanged'],evidence=[dict(property='Composition integration',level='D',method='Bounded generated copies and independent compiled references',command='python verif/audio_composition.py --gate',result='not run',date='2026-11-14')],amiga=dict(classification='not-used',finding='DOS composition only'),uncertainty=['No production standalone executable yet; platform machine services remain'],dependencies={},verification_inputs={},verification_input_hashing='sha256-lf-text')
  save(p,cert)
 for p in sorted((ROOT/'metadata/closure').glob('*.json')):
  c=json.loads(p.read_text())
  if p.stem=='audio_world':c['dependencies']={f:closure.actual_dependencies(ROOT/f) for f in NEW_FILES};c['verification_inputs']={f:sha(ROOT/f) for f in BASE_FILES}
  else:
   for f in c['dependencies']:
    if f in BASE_FILES:c['dependencies'][f]=closure.actual_dependencies(ROOT/f)
  save(p,c)
 changed=set()
 for iteration in range(100):
  dirty=False
  for p in sorted((ROOT/'metadata/closure').glob('*.json')):
   c=json.loads(p.read_text());updates=[]
   for f,h in c.get('verification_inputs',{}).items():
    raw=(ROOT/f).read_bytes();raw=raw.replace(b'\r\n',b'\n') if c.get('verification_input_hashing')=='sha256-lf-text' else raw
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=h:c['verification_inputs'][f]=actual;updates.append(f)
   if updates:
    if p.name not in changed:
     c.setdefault('evidence_refreshed',[]).append(dict(date='2026-11-14',reason='Audio ownership/peer composition profile; accepted claims/status unchanged' if any(not f.startswith('metadata/closure/') for f in updates) else 'Only a locked certificate composition note/source-lock wording changed; claims unchanged',commands=['python verif/audio_composition.py --gate'],results='PASS' if final else 'Pending composition replay',inputs=updates));changed.add(p.name)
    save(p,c);dirty=True
  if not dirty:break
 else:raise RuntimeError('lock cycle')
 save(OUT/'relocks.json',dict(certificates=sorted(changed)))

def api():
 source=inspect.getsource(prior.api)
 source=source.replace("'sound_api','music_analysis']","'sound_api','music_analysis','dsp']")
 source=source.replace('profiles={}', 'n_cases=2*len(cases)\n profiles={}',1)
 source=source.replace("units.append(dict(component='timing_world',native=ROOT/'native/timing_world.c',bridge=ROOT/'native/bridge/timing_world_bridge.c',exports=[]))", "units.extend([dict(component='timing_world',native=ROOT/'native/timing_world.c',bridge=ROOT/'native/bridge/timing_world_bridge.c',exports=[]),dict(component='audio_world',native=ROOT/'native/audio_world.c',bridge=ROOT/'native/bridge/audio_world_bridge.c',exports=[])])")
 # Instrument every original entry body, including direct calls/fallbacks.
 source=source.replace("for n in ['RegisterTimerCallback','RemoveTimerCallback','SetTimerCallbackInterval','HandleTimerInterrupt']:","for n in [x[2:] for x in exports]:")
 source=source.replace("assert len(declines)==32", "assert len(profiles['legacy']['cases'])==n_cases")
 source=source.replace('legacy_matching=2202','legacy_matching=n_cases')
 source=source.replace('composed_matching=2202-len(declines)',"composed_matching=len(profiles['composed']['cases'])-len(declines)")
 source=source.replace("16 fixture states (two poison modes each) are beyond the already admitted typed timer domain", "Listed fixture states are outside accepted typed admissions; any decline must have executed an L1 game body in the legacy profile")
 source=source.replace("print('API PASS legacy 2202; composed 2170 matches + 32 explicit domain rejections',flush=True)","print('API PASS',len(declines),'explicit declines',flush=True)")
 observe='EXPORT uint8_t *api_observe(void){\n#ifdef UGH_NATIVE_TIMING\n timing_require_seal(ugh_mem);\n#endif\n memcpy(timing_api_observation,ugh_mem,UGH_MEM_SIZE);\n#ifdef UGH_NATIVE_TIMING\n timing_serialize(timing_api_observation);\n#endif\n return timing_api_observation; }\n'
 source=source.replace('EXPORT uint16_t api_live_word',observe.replace('\n','\\n')+'EXPORT uint16_t api_live_word')
 bridge_loop="""sources += [fixture]
  for original in [u['native'] for u in units]+[u['bridge'] for u in units]:
   rel=original.relative_to(ROOT).as_posix();text=original.read_text();composed_text=hostbuild.composition_source(rel,text,units)
   if text!=composed_text:
    path=folder/('native_'+original.name);path.write_text(composed_text);sources.append(path)
   else:sources.append(original)"""
 source=source.replace("sources += [u['native'] for u in units]+[u['bridge'] for u in units]+[fixture]",bridge_loop)
 env=dict(prior.__dict__);exec(source,env);env['api']()

def corpus():prior.corpus()
def lifetime():prior.lifetime()

def ice_borrow():
 import ctypes as C,random
 import difftest,nbuild
 from ice_fuzz import corpus
 from dataprobe import ice_pack235
 dlls=[nbuild.load_l1(OUT/'api'/label/'api.dll') for label in ['reference','composed']]
 m=difftest.Machine();rng=random.Random(2309);base=m.snapshot();scratch=m.seg('ZERO:IceDecodeWorkspace')*16;rows=[]
 def pair(title,memory,bank=0x7500):
  for entry in ['UnpackIceToScratch','UnpackIceStream']:compare_entry(title,memory,bank,entry)
 def compare_entry(title,memory,bank,entry):
  results=[]
  for dll in dlls:
   C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset()
   r=difftest.Regs(ax=0xa1,bx=0xb2,cx=0xc3,dx=0xd4,bp=0xe5,si=0,di=0xbeef,ds=bank,es=0xdead if entry=='UnpackIceToScratch' else m.seg('ZERO:IceDecodeWorkspace'),ss=0x9000,sp=0x100,flags=0xed7)
   f=getattr(dll,'api_c_'+entry);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r))
   results.append((status,bytes(r),bytes(dll.ugh_memory().contents),bytes(dll.ugh_device_state().contents)))
  assert results[0]==results[1],(title,next((i for i,(a,b) in enumerate(zip(results[0][2],results[1][2])) if a!=b),None))
  rows.append(dict(case=title,entry=entry,status=results[0][0],sha256=hashlib.sha256(results[0][2]).hexdigest()))
 for kind,stream,data in corpus(120,m):
  initial=bytearray(base);initial[0x75000:0x85000]=stream.ljust(65536,b'\0')[:65536];initial[scratch:scratch+65536]=rng.randbytes(65536)
  pair(kind,bytes(initial))
 for frame in [0x1a38,0x2bf6,0x2d9a,0x2f9e,0x2fb7]:
  pair('shipped '+hex(frame),base,m.seg('B'+f'{frame:04X}'+':IceStream_'+f'{frame:04X}'))
 for length in [1,32768,64768,65024,65535,65536]:
  data=(bytes(range(256))*(length//256+1))[:length];stream=ice_pack235(data)
  initial=bytearray(base);initial[0x75000:0x75000+len(stream)]=stream
  pair('crossing facade flags '+str(length),bytes(initial))
 save(OUT/'ice-borrow.json',dict(result='PASS',cases=rows,scope='Independent compiled L1 vs composed ICE scratch, full RAM/ABI/devices including facade-flag overlap, real wrapped/partial writes and seeded retained tail. Codec algorithms and maintained ICE bridge source unchanged.'))

def borrowers():
 import ctypes as C,struct,random
 import difftest,nbuild
 dlls=[nbuild.load_l1(OUT/'api'/label/'api.dll') for label in ['reference','composed']]
 m=difftest.Machine();rng=random.Random(2311);rows=[]
 def pair(name,args=(),regs=None):
  initial=m.prepare('GAME:'+name,{**difftest.POISON,**(regs or {})},'far',args,0x602 if len(rows)&1 else 0x202);memory=m.snapshot();results=[]
  for dll in dlls:
   C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset()
   r=difftest.Regs(**{n.lower():v for n,v in initial.items()});f=getattr(dll,'api_c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r))
   # These existing entries promise live GP/segments/IF/DF, not incidental arithmetic flags.
   live=tuple(getattr(r,n) for n in ['ax','bx','cx','dx','si','di','bp','sp','cs','ds','es','ss','ip'])+(r.flags&0x600,)
   data=bytes(dll.ugh_memory().contents);lo=initial['SS']*16;hi=lo+initial['SP']
   results.append((status,live,data[:lo]+data[hi:],bytes(dll.ugh_device_state().contents)))
  assert results[0]==results[1],(name,len(rows),'borrower mismatch')
  rows.append(dict(name=name,args=args,registers=regs,result=results[0][0]))
 for offset in [m.off('SOUND:AudioChannelStates'),m.off('SOUND:AdlibVoiceStates'),m.off('SOUND:SavedAdlibVoiceStates'),m.off('SOUND:MainAdlxCursor'),m.off('SOUND:DmaMixBufferOneCount')]:
  for delta in [-4,-1,0,1,4]:
   for count in [0,1,2,12,42,255]:
    m.reset();sound=m.seg('SOUND:AudioChannelStates')
    pair('CopyFarBytes',(count,0,offset,sound,(offset+delta)&65535,sound))
 for value in [0,1,99,100,65535,0xffffffff]:
  for label in ['AudioChannelStates','AdlibVoiceStates','MainAdlxCursor','DmaMixBufferOneCount']:
   for name in ['EncodeTwoDecimalDigits','EncodeFourDecimalDigits','EncodeSixDecimalDigits']:
    m.reset();sound=m.seg('SOUND:AudioChannelStates')
    for label_div,word in [('DecimalTenDivisor',10),('DecimalHundredDivisor',100),('DecimalThousandDivisor',1000),('DecimalTenThousandDivisor',10000)]:m.write(sound,m.off('DGROUP:'+label_div),struct.pack('<H',word))
    pair(name,regs=dict(DS=sound,SI=m.off('SOUND:'+label),AX=value&65535,DX=value>>16))
 # Exercise the live-DS shutdown write to a foreign view, without assigning
 # an invented audio owner to DGROUP:0002.
 api=difftest.load_suite('sound_api');adlib=difftest.load_suite('adlib');leaks=[]
 for flag in [0,0xffff]:
  for direction in [0,0x400]:
   m.reset();adlib.base(m);api.base(m,1);api.timer_state(m,2)
   m.ww('C:SoundSystemInitialized',1);m.ww('C:SoundSystemShutdown',flag);m.ww('SOUND:MusicFadeScheduled',0)
   m.wb('SOUND:AdlibInitAttempted',1);m.ww('SOUND:AdlxPlaybackTimerHandle',2);m.ww('TIMER:TimerInterruptInstalled',1)
   m.ww('DGROUP:PreviousInt08Offset',0x100);m.ww('DGROUP:PreviousInt08Segment',0xf000)
   memory=m.snapshot();observations=[]
   for dll in dlls:
    C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset()
    r=difftest.Regs(cs=m.seg('C:ShutdownSoundSystem'),ds=0x7340,ss=0x9000,sp=0x100,flags=0x202|direction)
    f=dll.api_c_ShutdownSoundSystem;f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r));assert status==0
    result=bytes(dll.ugh_memory().contents);canonical=m.seg('C:SoundSystemShutdown')*16+m.off('C:SoundSystemShutdown');foreign=m.seg('DGROUP:PreviousInt08Offset')*16+m.off('C:SoundSystemShutdown')
    assert int.from_bytes(result[canonical:canonical+2],'little')==flag
    assert int.from_bytes(result[foreign:foreign+2],'little')==1
    observations.append((result[:0x90000]+result[0x90100:],bytes(dll.ugh_device_state().contents)))
   assert observations[0]==observations[1]
   leaks.append(dict(flag=flag,direction=direction,physical_target=foreign,canonical_unchanged=True))
 save(OUT/'borrowers.json',dict(result='PASS',cases=rows,shutdown_live_view=leaks,scope='Independent compiled L1; ordered copy overlap/wrap and decimal writes into moved storage; original foreign live-DS latch retained as an unowned raw view.'))

def sb_api():
 import ctypes as C,copy,struct
 import difftest,nbuild,wholegame,contacts_reference
 from emu import SoundBlaster
 from adlx_samples_cases import sample
 contacts_reference.OUT=OUT/'sb-reference';contacts_reference.prepare_reference(local=True)
 dlls=[nbuild.load_l1(OUT/'api'/label/'api.dll') for label in ['reference','composed']]
 m=difftest.Machine();difftest.load_suite('sound_api').base(m,2)
 sound=m.seg('SOUND:AudioChannelStates');m.ww('SOUND:DspBasePort',0x220);m.wb('SOUND:DspPicIrqMask',128)
 m.ww('SOUND:ActiveSampleVoiceCount',0);m.ww('SOUND:ActiveSampleVoiceMask',0);m.ww('SOUND:SampleMixerBusy',0);m.ww('SOUND:AudioChannelStates',0,40)
 m.device.sb=SoundBlaster();m.device.sb.install(m.device)
 m.write(0,4*15,struct.pack('<HH',m.off('SOUND:HandleSampleDmaInterrupt'),sound));m.write(0x7100,0x100,sample(64))
 models=[copy.deepcopy(m.device.sb) for _ in dlls]
 states=[difftest.Regs(ax=0xa5c3,si=0x6996,di=0x9669,bp=0x7e81,sp=0x1000,cs=sound,ds=0x7340,es=0x7c20,ss=0x8000,flags=0x202) for _ in dlls]
 callbacks=[];rows=[]
 for dll,model in zip(dlls,models):
  C.memmove(dll.ugh_memory().contents,m.snapshot(),difftest.MEM_SIZE);dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;initial=m.device.state();C.memmove(C.addressof(dev),initial,len(initial))
  dll.api_begin();dll.api_observe.restype=C.POINTER(C.c_uint8*difftest.MEM_SIZE)
  dll.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
  clock=wholegame.Clock(dict(card='sb',events={},frames=1),m);clock.sb=model;clock.timer_sites.append(m.address('SOUND:loc_1FEA'))
  output_type=C.CFUNCTYPE(None,C.c_uint16,C.c_uint,C.c_uint32);service_type=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs))
  def output(port,size,value,dev=dev,model=model):model.sync(dev,[(e.kind,e.port,e.size,e.value) for e in dev.log[:dev.count]])
  def service(seg,off,rp,dev=dev,clock=clock,dll=dll):
   clock.service(dev,seg,off,rp.contents.flags,lambda bank,at,n:bytes(dll.api_observe().contents[bank*16+at:bank*16+at+n]));return 0
  ocb=output_type(output);scb=service_type(service);callbacks.extend([ocb,scb]);dll.ugh_set_output_observer.argtypes=[output_type];dll.ugh_set_output_observer(ocb);dll.ugh_set_service_observer.argtypes=[service_type];dll.ugh_set_service_observer(scb)
 def compare(title):
  memories=[];logs=[]
  for dll,model in zip(dlls,models):
   dev=dll.ugh_device_state().contents;events=[(e.kind,e.port,e.size,e.value) for e in dev.log[:dev.count]];model.sync(dev,events)
   assert not dev.error,(title,'device error');memories.append(bytes(dll.api_observe().contents));logs.append(events)
  assert memories[0][:0x80000]==memories[1][:0x80000] and memories[0][0x81000:]==memories[1][0x81000:],(title,'RAM')
  assert bytes(states[0])==bytes(states[1]) and logs[0]==logs[1] and models[0].state()==models[1].state(),(title,'ABI/log/model')
  rows.append(dict(title=title,events=len(logs[0]),pcm=len(models[0].pcm)))
 def pair(name,bank,args=()):
  for dll,r in zip(dlls,states):
   r.cs=bank
   for i,value in enumerate(args):dll.api_live_store(r.ss,r.sp+4+2*i,value)
   f=getattr(dll,'api_c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];assert f(C.byref(r))==0,name
  compare(name)
 pair('ResetSoundBlasterDsp',sound);assert states[0].ax==0xaa
 pair('SetDspSampleRate',sound,(8000,));pair('LocateDmaMixBuffers',sound)
 pair('LoadIffSample',m.seg('C:LoadIffSample'),(0,0x100,0x7100,255,2,256));assert states[0].ax==1
 initial_buffer=bytes(dlls[0].api_observe().contents);pair('PrimeSampleDmaPlayback',sound)
 for i in range(24):
  for dll,r in zip(dlls,states):
   r.cs=sound;r.flags|=512;f=dll.platform_service_point_at;f.argtypes=[C.c_int,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs)];assert f(1,sound,m.off('SOUND:loc_1FEA'),C.byref(r))==0
  compare('DMA poll '+str(i))
  if models[0].blocks and not models[0].remaining:break
 memory=bytes(dlls[0].api_observe().contents)
 def word(name):
  at=sound*16+m.off('SOUND:'+name);return int.from_bytes(memory[at:at+2],'little')
 produced=2*(512-word('SampleMixPairsRemaining'));buffer=word('DmaMixBufferOneOffset');pcm=bytes(models[0].pcm)
 assert len(pcm)==641 and produced==258 and models[0].blocks==1
 assert pcm[produced:]==initial_buffer[sound*16+buffer+produced:sound*16+buffer+len(pcm)]
 save(OUT/'sb-api.json',dict(result='PASS',scope='Unreachable in the shipped program; generated API fixture against the committed SB model, native owner persistent throughout; no hook repair',rows=rows,captured_bytes=len(pcm),fresh_bytes=produced,stale_tail_bytes=len(pcm)-produced,pcm_sha256=hashlib.sha256(pcm).hexdigest()))

def router():
 prior.router()
 shutil.copyfile(OUT/'router.json',OUT/'timer-router.json')
 from closure_support import function
 folder=OUT/'router';folder.mkdir(exist_ok=True)
 # Independent committed projection reads the fixture, not the native owner.
 original=subprocess.check_output(['git','show','HEAD:native/bridge/audio_projection.h'],cwd=ROOT,text=True)
 legacy=''.join(function(original,n) for n in ['audio_bridge_cursor','audio_bridge_pointer','audio_bridge_voice','audio_bridge_project'])
 legacy=re.sub(r'\brd(8|16|32)\(',r'fixture_read\1(',legacy)
 roles=re.findall(r'result=c_(\w+)\(registers\)',(ROOT/'native/bridge/audio_world_bridge.c').read_text())
 stubs=''.join('int c_'+n+'(Regs *r){(void)r;return 0;}\n' for n in roles)
 source=folder/'router.c'
 text=r'''#include "audio_world_bridge.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
static uint8_t fixture[UGH_MEM_SIZE],output[UGH_MEM_SIZE];
static uint8_t fixture_read8(uint16_t bank,uint16_t offset){return fixture[lin(bank,offset)];}
static uint16_t fixture_read16(uint16_t bank,uint16_t offset){unsigned a=lin(bank,offset);return (uint16_t)(fixture[a]|fixture[a+1]*256u);}
static uint32_t fixture_read32(uint16_t bank,uint16_t offset){unsigned a=lin(bank,offset);uint32_t result=0;for(unsigned i=0;i<4;i++)result|=(uint32_t)fixture[a+i]<<(8*i);return result;}
'''+legacy+stubs+r'''
int main(void){
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 ugh_mem[lin(DATA_SEG,D(LastActiveTimerSlotOffset))]=30;ugh_mem[lin(DATA_SEG,D(LastActiveTimerSlotOffset))+1]=0;
 memcpy(fixture,ugh_mem,sizeof fixture);timing_cold_import(ugh_mem);
 unsigned addresses[8192],n=0;for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(timing_is_owned(a))addresses[n++]=a;
 if(n!=timing_owned_bytes() || n<=4000)return 1;
 memcpy(output,ugh_mem,sizeof output);timing_serialize(output);if(memcmp(output,fixture,sizeof output))return 2;
 AudioState expected={0},actual={0};audio_bridge_project(SOUND_SEG,&expected);audio_world_snapshot(&actual);
 if(memcmp(&expected,&actual,sizeof actual))return 3;
 unsigned writes=0;
 for(unsigned i=0;i<n;i++){
  unsigned address=addresses[i];
  for(unsigned value=0;value<256;value++){
   if(value&1)audio_borrowed_store(ugh_mem+(address&~15u),address&15u,(uint8_t)value);
   else if(!timing_shared_write(address,(uint8_t)value))return 4;
   fixture[address]=(uint8_t)value;
   uint8_t read;if(!timing_shared_read(address,&read) || read!=value)return 5;
   if(audio_borrowed_byte(ugh_mem,address)!=value || audio_borrowed_byte(ugh_mem+(address&~15u),address&15u)!=value)return 6;
   if(i){timing_shared_read(addresses[i-1],&read);if(read!=fixture[addresses[i-1]])return 13;}
   if(i+1<n){timing_shared_read(addresses[i+1],&read);if(read!=fixture[addresses[i+1]])return 14;}
   writes++;
  }
  timing_serialize(output);
  for(unsigned j=0;j<n;j++)if(output[addresses[j]]!=fixture[addresses[j]])return 7;
  if(timing_check_serialization(output)!=UINT32_MAX)return 8;
  timing_require_seal(ugh_mem);
 }
 /* Channel 9 owner aliases saved voice zero, and record12 has no duplicate. */
 unsigned alias=lin(SOUND_SEG,S(AdlibVoiceStates)+9*20+16);
 timing_shared_write(alias,0x12);timing_shared_write(alias+1,0x6b);
 if(native_timing_world()->audio.displaced[0].owner!=0x6b12)return 9;
 unsigned record=lin(SOUND_SEG,S(MainAdlxCursor));timing_shared_write(record,0x87);timing_shared_write(record+1,0xa4);
 if(native_timing_world()->audio.channels[12].cursor.index!=0xa487)return 10;
 /* Output corruption must stop comparing; the comparator cannot resync. */
 timing_serialize(output);output[addresses[n/2]]^=1;if(timing_check_serialization(output)!=addresses[n/2])return 11;
 unsigned bank_addresses[30],banks=0,identities=0;
 for(unsigned i=0;i<13;i++){bank_addresses[banks++]=lin(SOUND_SEG,S(AudioChannelStates)+42*i+8);bank_addresses[banks++]=lin(SOUND_SEG,S(AudioChannelStates)+42*i+18);}
 bank_addresses[banks++]=lin(SOUND_SEG,S(FirstScannedEvent)+2);bank_addresses[banks++]=lin(SOUND_SEG,S(MainAdlxSectionEnd)+2);
 bank_addresses[banks++]=lin(SOUND_SEG,S(SoundBankBase)+2);bank_addresses[banks++]=lin(SOUND_SEG,S(AdlibInstrumentMap)+2);
 for(unsigned i=0;i<banks;i++)for(unsigned word=0;word<65536;word++){
  timing_shared_write(bank_addresses[i],(uint8_t)word);timing_shared_write(bank_addresses[i]+1,(uint8_t)(word>>8));
  uint8_t low,high;timing_shared_read(bank_addresses[i],&low);timing_shared_read(bank_addresses[i]+1,&high);
  if((unsigned)(low|high*256u)!=word)return 12;
  identities++;
 }
 timing_require_seal(ugh_mem);
 uint8_t workspace[65536];unsigned base=lin(UGH_S_ZERO_IceDecodeWorkspace,0);
 unsigned flag=lin(UGH_S_C_SoundSystemInitialized,UGH_O_C_SoundSystemInitialized),at=flag-base;
 native_timing_world()->audio.driver.initialized=0x1234;native_timing_world()->audio.driver.shutdown=0x5678;
 audio_workspace_read(workspace,base,sizeof workspace);
 if(workspace[at]!=0x34 || workspace[at+1]!=0x12 || workspace[at+2]!=0x78 || workspace[at+3]!=0x56)return 15;
 native_timing_world()->audio.driver.initialized=0x9abc;
 audio_workspace_publish(base,workspace,sizeof workspace,32,32);
 if(native_timing_world()->audio.driver.initialized!=0x9abc)return 16;
 workspace[at]=0x12;workspace[at+1]=0x6b;workspace[at+2]=0x34;workspace[at+3]=0x5a;
 audio_workspace_publish(base,workspace,sizeof workspace,65536,65536-at);
 if(native_timing_world()->audio.driver.initialized!=0x6b12 || native_timing_world()->audio.driver.shutdown!=0x5a34)return 17;
 timing_require_seal(ugh_mem);
 printf("{\"owned_bytes\":%u,\"audio_bytes\":%u,\"byte_writes\":%u,\"resource_identity_words\":%u,\"workspace_overlap_offset\":%u,\"aliases\":2,\"canonical_control\":true}\n",n,timing_audio_owned_bytes(),writes,identities,at);
 return 0;
}
'''
 source.write_text(text)
 exe=folder/'router.exe';bounded([prior.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-fwrapv','-DUGH_NATIVE_AUDIO','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,source,ROOT/'native/timing_world.c',ROOT/'native/audio_world.c',ROOT/'native/bridge/timing_world_bridge.c',ROOT/'native/bridge/audio_world_bridge.c'],'router-compile')
 row=bounded([exe],'router');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='All byte values through all canonical lanes; independent committed AudioState snapshot and literal fixture; full frame comparison after each byte slice, record12/channel9 alias checks.'))

def reuse():
 folder=OUT/'reuse';folder.mkdir(exist_ok=True);rows=[]
 for rel in [f for f in BASE_FILES if '/adlx_' in f and f.endswith('.c')]:
  before=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,text=True);tokens=[]
  for i,source in enumerate([before,(ROOT/rel).read_text()]):
   source=re.sub(r'#include "([^"]+)"',lambda m:'#include "'+str((ROOT/rel).parent.joinpath(m[1]).resolve()).replace('\\','/')+'"' if (ROOT/rel).parent.joinpath(m[1]).is_file() else m[0],source)
   p=folder/(str(i)+'-'+Path(rel).name);p.write_text(source);out=p.with_suffix('.i')
   bounded([prior.common.GCC,'-E','-P','-I',ROOT/'c',p,'-o',out],'reuse-'+str(i)+'-'+Path(rel).stem)
   normalized=out.read_text().replace('typedef uint16_t AudioPeerBinding;','').replace('AudioPeerBinding','uint16_t')
   tokens.append(re.findall(r'"(?:\\.|[^"\\])*"|\w+|[^\s]',normalized))
  assert tokens[0]==tokens[1],rel
  rows.append(dict(file=rel,default_tokens_identical_after_u16_typedef_elision=True))
 pure=[]
 for p in sorted((ROOT/'native').glob('*.c')):
  if p.name.startswith(('adlx_','music_clock','timer.','timer_')) or p.name in ['ice.c','ice_scratch.c','far_copy.c','decimal.c']:
   assert subprocess.check_output(['git','show','HEAD:'+p.relative_to(ROOT).as_posix()],cwd=ROOT).replace(b'\r\n',b'\n')==p.read_bytes().replace(b'\r\n',b'\n'),p
   pure.append(p.relative_to(ROOT).as_posix())
 save(OUT/'reuse.json',dict(result='PASS',bridges=rows,pure_sources_unchanged=pure,scope='Accepted algorithm theorems unchanged; legacy ABI tokens identical after eliding the AudioPeerBinding typedef, which is uint16_t in that profile. New ownership/peer seams have independent evidence.'))

def proof():
 source=inspect.getsource(prior.proof)
 source=source.replace("prefix+=body+", "prefix+='static uint8_t ugh_mem[1];\\nstatic uint16_t audio_external_read(unsigned i){(void)i;assert(0);return 0;}\\nstatic void audio_external_write(unsigned i,uint16_t v){(void)i;(void)v;assert(0); }\\n'\n prefix+=body+")
 source=source.replace("'-E','-P','-nostdinc'","'-E','-P','-DUGH_NATIVE_AUDIO','-nostdinc'")
 source=source.replace('__CPROVER_assume(wide<2)','__CPROVER_assume(wide<3)')
 source=source.replace('if(!wide)half=0;','if(wide!=1)half=0;if(wide==2)address=0;')
 source=source.replace('w->music.ticks=old;w->music.rate=(uint16_t)old;','w->music.ticks=old;w->music.rate=(uint16_t)old;w->audio.driver.attempted=(uint8_t)old;')
 source=source.replace('wide?(size_t)((uint8_t*)&w->music.ticks-(uint8_t*)w):(size_t)((uint8_t*)&w->music.rate-(uint8_t*)w),wide?4:2', 'wide==1?(size_t)((uint8_t*)&w->music.ticks-(uint8_t*)w):wide==2?(size_t)((uint8_t*)&w->audio.driver.attempted-(uint8_t*)w):(size_t)((uint8_t*)&w->music.rate-(uint8_t*)w),wide==1?4:wide==2?1:2')
 source=source.replace('uint32_t expected=wide?old:(uint16_t)old;', 'uint32_t expected=wide==1?old:wide==2?(uint8_t)old:(uint16_t)old;')
 source=source.replace('if(wide){assert(w->music.ticks', 'if(wide==2){assert(w->audio.driver.attempted==(uint8_t)expected);assert(w->music.ticks==initial_ticks && w->music.rate==initial_rate);}\n else if(wide){assert(w->music.ticks')
 source=source.replace('numeric 16/32-bit fields','numeric 8/16/32-bit fields')
 env=dict(prior.__dict__);exec(source,env);env['proof']()

def projector():
 import projector_evidence as pe
 pe.OUT=OUT/'projector';pe.OUT.mkdir(exist_ok=True);frozen=pe.OUT/'frozen';target=snapshot()
 for top in ['c','native','host','metadata','tests','tools','src']:shutil.copytree(target/top,frozen/top,dirs_exist_ok=True)
 revision=json.loads((OUT/'baseline.json').read_text())['revision']
 save(pe.OUT/'baseline.json',dict(commit=revision,scope='Committed HEAD plus only audio composition; scratch promotion'))
 pe.build(False,revision);pe.build(True,revision)
 for path in sorted((frozen/'tests/scenarios').glob('*.txt')):pe.one(path.stem,path.stem=='gameplay')
 pe.one('smoke');pe.summarize()
 runs=[json.loads(p.read_text()) for p in (pe.OUT/'runs').glob('*.json')]
 expected=json.loads((OUT/'router.json').read_text())['counts']['owned_bytes']
 assert all(r['canonical_native_owned_bytes']==expected and r['native_owned_journal_publications']==0 for r in runs)

def census():
 target=snapshot();bounded([sys.executable,'verif/standalone_census.py','--all'],'census',target)
 census_result()

def census_result():
 target=OUT/'baseline/build/workers/close-adlx-19'
 j=json.loads((target/'census.json').read_text());assert all(not s['fallback_calls'] and not s['l1_body_calls'] for s in j['scenarios'])
 owners={p.stem for p in (ROOT/'metadata/closure').glob('adlx_*.json')}|{'timer','timer_lifetime','music_clock','timing_world','audio_world'}
 paths={'native/bridge/'+n+'_bridge.c' for n in owners}
 internal=[];services=[]
 details=sorted((target/'detail').glob('*.json'))
 assert len(details)==len(j['scenarios'])==21,'Incomplete census edge details'
 assert {p.stem for p in details}=={s['scenario'] for s in j['scenarios']}
 for p in details:
  run=json.loads(p.read_text())
  for e in run['machine_edges']:
   if e['kind'] in ['ABI-entry','interrupt-delivery']:continue
   if e['bridge']['path'] not in paths:continue
   row=dict(scenario=run['scenario'],**e)
   (internal if e['target'].get('owner') in owners|paths else services).append(row)
 assert not internal,internal[:3]
 assert any(f['name']=='c_TickAdlxPlayback' and f['count'] for f in j['functions'])
 save(OUT/'census.json',dict(result='PASS',summary=j,internal_island_machine_edges=internal,outgoing_services=services))

def levels():
 target=OUT/'baseline';assert target.is_dir()
 bounded([sys.executable,'tools/hostbuild.py'],'levels-build-native',target)
 groups=[];raw_inputs={}
 # The supplied caches predate LF normalization. Reconstruct only the LF or
 # CRLF representation of committed text, selected by independent provenance
 # and full input identity. This also works from an entirely LF checkout.
 # No cache key, expected frame or oracle-side program text is edited.
 for relative in ['tools/emu.py','tools/wholegame.py']:
  destination=target/relative;normal=destination.read_bytes().replace(b'\r\n',b'\n')
  expected={json.loads(p.read_text())['provenance']['tools'][relative] for bank in ['levels','levels-audio','levels-deep'] for p in (target/'build'/bank).glob('*.ref.json')}
  assert len(expected)==1,(relative,'mixed oracle cache provenance')
  candidates={raw for raw in [normal,normal.replace(b'\n',b'\r\n')] if hashlib.sha256(raw).hexdigest() in expected}
  assert len(candidates)==1,(relative,'cache tool text differs from HEAD')
  raw=candidates.pop();destination.write_bytes(raw);raw_inputs[relative]=hashlib.sha256(raw).hexdigest()
 import wholegame,cgen
 from types import SimpleNamespace
 mz,_=cgen.read_symbols();previous_root=wholegame.ROOT;wholegame.ROOT=target
 for group,suffix in [('openings',''),('audio','-audio'),('deep','-deep')]:
  suite=target/('tests/levels'+suffix)
  if not suite.is_dir():continue
  names=[p.stem for p in sorted(suite.glob('*.txt'))];assert len(names)=={'openings':81,'audio':7,'deep':8}[group]
  for name in names:
   relative='tests/levels'+suffix+'/'+name+'.txt';destination=target/relative;normal=destination.read_bytes().replace(b'\r\n',b'\n')
   reference=json.loads((target/('build/levels'+suffix)/(name+'.ref.json')).read_text())
   candidates=[]
   for raw in set([normal,normal.replace(b'\n',b'\r\n')]):
    destination.write_bytes(raw)
    if wholegame.identity(destination,SimpleNamespace(raw_image=mz.image))==reference['key']:candidates.append(raw)
   assert len(candidates)==1,(name,'cache script text differs from HEAD')
   raw=candidates[0];destination.write_bytes(raw);raw_inputs[relative]=hashlib.sha256(raw).hexdigest()
   for relative in ['tools/emu.py','tools/wholegame.py']:
    assert reference['provenance']['tools'][relative]==raw_inputs[relative],(name,relative,'cache oracle provenance differs')
  args=(['--group',group] if '--group' in (target/'verif/level_suite.py').read_text() else [])
  bounded([sys.executable,'verif/level_suite.py',*args,'--check','native',*names,'--internal'],'levels-native-'+group,target)
  groups.append(dict(group=group,count=len(names),names=names))
 wholegame.ROOT=previous_root
 save(OUT/'levels.json',dict(result='PASS',groups=groups,raw_reference_inputs=raw_inputs,scope='Committed suite text; original cache input line endings in generated copy only, provenance and complete identity checked; no expected result or cache key changed'))

def defects():
 target=snapshot();rows=[]
 for fault,label in [(1,'dropped-peer'),(2,'opl-order'),(3,'stale-audio-state'),(4,'missed-audio-serialization')]:
  folder=OUT/'defects'/label
  for top in ['c','native','host','metadata','tools','verif','src']:shutil.copytree(target/top,folder/top,dirs_exist_ok=True)
  shutil.copytree(target/'build/link',folder/'build/link',dirs_exist_ok=True)
  for rel in ['native/bridge/audio_world_bridge.c','native/bridge/timing_world_bridge.c']:
   (folder/rel).write_text('#define AUDIO_TEST_FAULT '+str(fault)+'\n'+(target/rel).read_text())
  if fault==2:
   p=folder/'c/platform.c';text=(target/'c/platform.c').read_text();assert text.count('void platform_out(')==1
   text=text.replace('void platform_out(','void platform_device_out(',1)+r'''
extern int audio_peer_active(void);
void platform_out(uint16_t port,unsigned size,uint32_t value){
 static unsigned pending,done,saved_size;static uint16_t saved_port;static uint32_t saved_value;
 if(!done && audio_peer_active() && (port==0x388 || port==0x389)){
  if(!pending){pending=1;saved_port=port;saved_size=size;saved_value=value;return;}
  platform_device_out(port,size,value);platform_device_out(saved_port,saved_size,saved_value);done=1;pending=0;return;
 }
 platform_device_out(port,size,value);
}
'''
   p.write_text(text)
  bounded([sys.executable,'tools/hostbuild.py'],'defect-build-'+label,folder)
  command=[folder/'build/host/ugh.exe','--headless','48','--script',target/'tests/scenarios/gameplay-adlib.txt','--timeout','590']
  if fault==4:
   checker=OUT/'defects/capture.py';checker.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
   result=bounded([sys.executable,checker,*command],'defect-run-'+label);failed=json.loads(result['stdout'])
   assert failed['returncode']==88 and 'missed owned serialization' in failed['stderr']
   rows.append(dict(defect=label,result='DETECTED',failure=failed));continue
  result=bounded(command,'defect-run-'+label);actual=[json.loads(l) for l in result['stdout'].splitlines()]
  expected=json.loads((ROOT/'build/whole/gameplay-adlib.ref.json').read_text())['frames']
  mismatch=next((i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),None);assert mismatch is not None
  rows.append(dict(defect=label,result='DETECTED',scenario='gameplay-adlib',frame=mismatch))
 save(OUT/'defects.json',dict(result='PASS',controls=rows))

def audit():
 import cgen
 _,symbols=cgen.read_symbols();model=json.loads((ROOT/'metadata/program-model.json').read_text());audio=model['components']['audio']
 rows=[]
 for name in sorted(set(audio['written_only_here'])|set(audio['shared_written_state'])):
  base=name.split('+')[0];delta=2 if '+2' in name else 0
  candidates=[(prefix+':'+base,symbols[prefix+':'+base]) for prefix in ['SOUND','C','DGROUP'] if prefix+':'+base in symbols]
  row=dict(name=name,model=model['variables'].get(base),raw_alias_expression=name)
  if candidates:
   label,symbol=candidates[0];row.update(symbol=label,physical=(cgen.LOAD+symbol['frame'])*16+symbol['offset']+delta)
  rows.append(row)
 static=OUT/'baseline/build/workers/close-adlx-19/static.json'
 save(OUT/'ownership.json',dict(result='PASS',before=dict(total_native_bytes=320,audio_bytes=14,timer_bytes=306),after=dict(total_native_bytes=4612,audio_bytes=4306,timer_bytes=306,new_audio_bytes=4292,native_owned_baseline_bytes=0,native_owned_journal_bytes=0),
  model_complete=False,model_cells=rows,census_inventory_sha256=sha(static),
  borrowers=[dict(service='audio_workspace_read / audio_workspace_publish',callers=['ice_bridge','ice_scratch_bridge'],shape='byte pointer, uint32 address, unsigned capacity; publication adds unsigned extent and size_t actual writes',rule='64KiB seeded in/out window, backward-ring actual writes; native flags at workspace+FD00..FD03, no retained-value write-back'),
    dict(service='audio_borrowed_byte / audio_borrowed_store',callers=['far_copy','decimal','ADLX loader/sections'],shape='borrowed byte pointer, uint32 index; uint8 read/write value',rule='Ordered aliasing and wrapping remain in the accepted kernel; provider resolves owned bytes directly, otherwise ordinary borrowed buffer'),
    dict(service='existing memory typed view',callers=['outside entry ABI / c infrastructure'],shape='uint32 physical compatibility byte address, uint8 value',rule='Canonical state routes to native fields. Hardware delivery stays platform-owned.'),
    dict(service='live DS shutdown latch',callers=['adlx_facade'],shape='raw expression wr16(live DS, C:SoundSystemShutdown, 1)',rule='After TIMER removal this is DGROUP:0002, not the C flag. No invented owner; four compiled cases retain this foreign view. Canonical flag remains native.')],
  references='AudioCursor holds a typed borrowed resource window and wrapping byte index; only bridge/provider code maps historical bank words. Calibration/DSP IRQ bindings are opaque native identities with explicit provider coordinates.',
  unknowns='Unlabelled gaps and foreign views stay unknown; no broad region or third DMA queue descriptor is invented. Fallback reservation retains opaque prefix/tail bytes.'))

def finalize():
 import closure
 census_result();audit()
 names=['api','router','timer-router','proof','reuse','corpus','lifetime','sb-api','ice-borrow','borrowers','census','levels','defects']
 results={n:json.loads((OUT/(n+'.json')).read_text()) for n in names};assert all(j['result']=='PASS' for j in results.values())
 assert all(not row['timer_fallbacks'] for row in results['api']['profiles']['composed']['cases']),'API executed an L1 body'
 projection=json.loads((OUT/'projector/summary.json').read_text());assert projection['result']=='PASS'
 boundaries=sum(s['serialized_records'] for s in projection['scenarios']);assert boundaries==17955
 assert results['router']['counts']['owned_bytes']==4612
 assert {g['group']:g['count'] for g in results['levels']['groups']}=={'openings':81,'audio':7,'deep':8}
 receipt=dict(result='PASS',date='2026-11-15',revision=json.loads((OUT/'baseline.json').read_text())['revision'],inputs={f:sha(ROOT/f) for f in BASE_FILES},
  api=dict(legacy=results['api']['legacy_matching'],composed=results['api']['composed_matching'],declines=len(results['api']['explicit_out_of_domain'])),
  router=results['router'],timer_router=results['timer-router'],proof=results['proof'],reuse=results['reuse'],
  corpus=dict(resources=results['corpus']['streams'],configurations=len(results['corpus']['configurations'])),lifetime=len(results['lifetime']['cases']),
  digital=results['sb-api'],ice_borrow_cases=len(results['ice-borrow']['cases']),external_borrower_cases=len(results['borrowers']['cases']),shutdown_aliases=results['borrowers']['shutdown_live_view'],
  projector=dict(boundaries=boundaries,native_owned_bytes=4612,new_audio_bytes=4292,native_owned_journal_publications=0,controls=projection['controls']),
  census=dict(scenarios=21,l1_game_bodies=0,fallbacks=0,internal_island_machine_edges=0),levels=results['levels'],defects=results['defects'],
  gate=[dict(command=json.loads((OUT/'children'/('build-'+str(i)+'.json')).read_text())['command'],returncode=0) for i in range(6)])
 save(OUT/'verification-receipt.json',receipt)
 p=ROOT/'metadata/closure/audio_world.json';c=json.loads(p.read_text())
 c['original']['composes']=['timing_world',*[q.stem for q in sorted((ROOT/'metadata/closure').glob('adlx_*.json'))]]
 c['purpose']='Remaining audio state leaves the machine: one native owner, address-free typed peer identities and explicit borrowed byte/workspace services'
 c['memory'].update(native_bytes='4292 newly owned audio bytes plus the earlier 14 clock bytes; timer remains 306 bytes',service_state='Opaque calibration/DSP IRQ bindings retain 8 serialized provider bytes; no DOS vector words in game state',shared_views='Both ICE windows, ordered copy and decimal buffers use explicit typed borrows; live-DS shutdown writes the original foreign DGROUP:0002 view without inventing ownership')
 c['assumptions']+=['Compatibility register/stack shells remain at the current verification ABI. This is state/direct-call composition, not yet a standalone production executable.'] if len(c['assumptions'])==2 else []
 specs=[('Owned layout, byte lanes and resource identities','C','Independent committed AudioState projection, full byte-domain reads/writes, native output/frame checks and direct alias cases','--router','PASS: 4612 owned bytes x256, 1966080 resource words, 2097152 original timer callback-word checks; record12/channel9 aliases; no RAM resynchronization'),
  ('Numeric byte-view output/frame/dependence','B',results['proof']['scope'],'--proof','PASS on actual C, 8/16/32-bit fields and arbitrary values/byte lanes; no whole asynchronous machine theorem'),
  ('L1/Unicorn API and persistent native corpus','C','Independent compiled reference plus Unicorn; full RAM, live ABI, device/ordered ports; explicit admission failures','--api --corpus --lifetime --sb-api --ice-borrow --borrowers',f"PASS: {receipt['api']['legacy']} legacy cases; {receipt['api']['composed']} composed matches, {receipt['api']['declines']} explicit out-of-contract rejections; all 11 ADLX resources/143 configurations, 24 lifetime cases; 641 DMA bytes=258 fresh+383 stale; both ICE borrowers and foreign shutdown view"),
  ('Clean integration, observation projector and machine-edge census','D','Committed HEAD archive plus only this overlay, scratch promotion; native and pure literal hosts; no expected records used as state','--build --projector --census --levels','PASS: closure 47/0; hosts 21/21 each; 17955 equal boundaries, 4612 native bytes/zero owned journal publications; zero island machine edges/fallbacks/L1 game bodies; 81/81 openings; 7/7 audio and 8/8 deep groups'),
  ('New composition seam defects','C','Generated-copy dropped peer, reordered real OPL writes, stale native cursor and missing audio serialization','--defects','PASS: all four detected; missed serialization stops with no resynchronization'),
  ('Accepted kernel evidence reused within original domains','B',results['reuse']['scope'],'--reuse','PASS: pure kernels unchanged; default bridge tokens identical after the exact uint16_t typedef elision; new composition has separate B/C/D evidence')]
 c['evidence']=[dict(property=prop,level=level,method=method,command='python verif/audio_composition.py '+command,result=result,date='2026-11-15') for prop,level,method,command,result in specs]
 c['uncertainty']=['Compatibility ABI shells and resource/port/IRQ machine services remain; this work does not remove the whole machine from the production link.',
  '188 API fixtures outside the existing typed admissions fail closed; exact cases and poison modes are in the receipt. No all-state equivalence is inferred from scenarios.',
  'Unreachable in the shipped program: startup requests AdLib only; no shipped sample resource and bank/delay hooks are near RET stubs; the DSP probe far CALL returns through a near RET. No hook is repaired or given invented intent.']
 peers=[q for q in (ROOT/'metadata/closure').glob('*.json') if q.stem.startswith('adlx_') or q.stem in {'timer','timer_lifetime','music_clock','timing_world','ice','ice_scratch','far_copy','decimal'}]
 peer_files={f for q in peers for f in json.loads(q.read_text())['native']['files']}
 inputs=set(BASE_FILES)|peer_files|{q.relative_to(ROOT).as_posix() for q in peers}|{'c/memory.c','c/platform.c','c/dispatch.c','c/ugh.h','c/ugh_sym.h','metadata/program-model.json','verif/entry_retirement.py','verif/windows_job.py','verif/closure_support.py','verif/timer_callbacks.py',*[f'tests/{s}.py' for s in ['timer','timer_system','timer_stack','music_clock','adlib','sound_engine','sound_api','music_analysis','dsp']]}
 c['verification_inputs']={f:sha(ROOT/f) for f in sorted(inputs)};c['dependencies']={f:closure.actual_dependencies(ROOT/f) for f in NEW_FILES}
 c['receipts']={'build/workers/close-adlx-23/verification-receipt.json':sha(OUT/'verification-receipt.json')}
 c['evidence_refreshed']=[dict(date='2026-11-15',reason='New audio ownership and peer composition evidence; status left for supervisor review',commands=['python verif/audio_composition.py --gate'],results='PASS within the stated contracts',inputs=BASE_FILES)]
 save(p,c)
 old={};changed=set()
 for p in sorted((ROOT/'metadata/closure').glob('*.json')):
  if p.stem=='audio_world':continue
  original=json.loads(subprocess.check_output(['git','show','HEAD:'+p.relative_to(ROOT).as_posix()],cwd=ROOT,text=True));old[p.name]=original;current=json.loads(p.read_text())
  for key in set(original)-{'dependencies','verification_inputs','evidence_refreshed'}:assert current[key]==original[key],(p.name,key,'accepted claim changed')
  if 'evidence_refreshed' in original:current['evidence_refreshed']=original['evidence_refreshed']
  else:current.pop('evidence_refreshed',None)
  for f in current['dependencies']:
   if f in BASE_FILES:current['dependencies'][f]=closure.actual_dependencies(ROOT/f)
  save(p,current)
 for iteration in range(100):
  dirty=[]
  for p in sorted((ROOT/'metadata/closure').glob('*.json')):
   item=json.loads(p.read_text())
   for f,h in item.get('verification_inputs',{}).items():
    raw=(ROOT/f).read_bytes();raw=raw.replace(b'\r\n',b'\n') if item.get('verification_input_hashing')=='sha256-lf-text' else raw
    item['verification_inputs'][f]=hashlib.sha256(raw).hexdigest()
   if p.name in old:
    updates=[f for f,h in item.get('verification_inputs',{}).items() if old[p.name].get('verification_inputs',{}).get(f)!=h]
    if updates:
     direct=any(not f.startswith('metadata/closure/') for f in updates)
     item['evidence_refreshed']=old[p.name].get('evidence_refreshed',[])+[dict(date='2026-11-15',reason='Audio ownership/peer/shared-buffer composition profile; accepted claims and statuses unchanged' if direct else 'Only the locked certificate composition note/source-lock wording changed; claims unchanged',commands=['python verif/audio_composition.py --gate'],results='PASS: default ABI typedef equivalence and unchanged kernels; composition B/C/D replay, hosts and 81 openings, 7 audio and 8 deep scenarios. No old proof domain widened.' if direct else 'Fixed-point SHA256 cascade relock only; no claim/result/status changed.',inputs=updates)];changed.add(p.name)
   before=p.read_text();save(p,item)
   if p.read_text()!=before:dirty.append(p.name)
  if not dirty:break
 else:raise RuntimeError('final lock cycle')
 save(OUT/'relocks.json',dict(certificates=sorted(changed)))
 target=snapshot();bounded([sys.executable,'tools/closure.py'],'final-closure',target)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['relock','build','api','router','proof','reuse','corpus','lifetime','sb-api','ice-borrow','borrowers','projector','census','levels','defects','finalize','gate','internal']:p.add_argument('--'+name,action='store_true')
 a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if a.gate:
  relock();prior.build()
  for name in ['api','router','proof','reuse','corpus','lifetime','sb_api','ice_borrow','borrowers','projector','census','levels','defects']:
   bounded([sys.executable,__file__,'--'+name.replace('_','-'),'--internal'],name+'-child')
  finalize();return
 if a.relock:relock()
 if a.build:prior.build()
 for name in ['api','router','proof','reuse','corpus','lifetime','sb_api','ice_borrow','borrowers','projector','census','levels','defects','finalize']:
  if getattr(a,name):
   if a.internal:globals()[name]()
   else:bounded([sys.executable,__file__,'--'+name.replace('_','-'),'--internal'],name+'-child')
if __name__=='__main__':main()
