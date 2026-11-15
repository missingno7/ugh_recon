"""Second audio/timer ownership cut; serial bounded generated-copy evidence."""
import argparse,hashlib,inspect,json,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-adlx-23'
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

def relock(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'relock',locals())

def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

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
 source=source.replace("prefix+=body+", "prefix+='static uint16_t audio_external_read(unsigned i){(void)i;assert(0);return 0;}\\nstatic void audio_external_write(unsigned i,uint16_t v){(void)i;(void)v;assert(0); }\\n'\n prefix+=body+")
 source=source.replace("'-E','-P','-nostdinc'","'-E','-P','-DUGH_NATIVE_AUDIO','-nostdinc'")
 source=source.replace('__CPROVER_assume(wide<2)','__CPROVER_assume(wide<3)')
 source=source.replace('if(!wide)half=0;','if(wide!=1)half=0;if(wide==2)address=0;')
 source=source.replace('w->music.ticks=old;w->music.rate=(uint16_t)old;','w->music.ticks=old;w->music.rate=(uint16_t)old;w->audio.driver.attempted=(uint8_t)old;')
 source=source.replace('wide?(size_t)((uint8_t*)&w->music.ticks-(uint8_t*)w):(size_t)((uint8_t*)&w->music.rate-(uint8_t*)w),wide?4:2', 'wide==1?(size_t)((uint8_t*)&w->music.ticks-(uint8_t*)w):wide==2?(size_t)((uint8_t*)&w->audio.driver.attempted-(uint8_t*)w):(size_t)((uint8_t*)&w->music.rate-(uint8_t*)w),wide==1?4:wide==2?1:2')
 source=source.replace('uint32_t expected=wide?old:(uint16_t)old;', 'uint32_t expected=wide==1?old:wide==2?(uint8_t)old:(uint16_t)old;')
 source=source.replace('if(wide){assert(w->music.ticks', 'if(wide==2){assert(w->audio.driver.attempted==(uint8_t)expected);assert(w->music.ticks==initial_ticks && w->music.rate==initial_rate);}\n else if(wide){assert(w->music.ticks')
 source=source.replace('numeric 16/32-bit fields','numeric 8/16/32-bit fields')
 env=dict(prior.__dict__);exec(source,env);env['proof']()

def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())

def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())

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

def levels(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'levels',locals())

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

def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())

def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())
# Scheduled by world_gate; no private CLI.
