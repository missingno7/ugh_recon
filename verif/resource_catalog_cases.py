"""Resource catalog consuming paths, alias windows and immutable guards."""
import ctypes as C,inspect,json,sys

def pair(m,dlls,name,regs=None,actions=()):
 import difftest
 initial=m.prepare('GAME:'+name,{**difftest.POISON,'CS':m.seg('GAME:DrawTransparentSprite'),'DS':m.seg('DGROUP:PlayerCount'),**(regs or {})},'far',(),0x602);memory=m.snapshot();device=m.device.state();result=[]
 for dll in dlls:
  C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device));dll.api_begin()
  r=difftest.Regs(**{k.lower():v for k,v in initial.items()});f=getattr(dll,'api_c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r))
  for target,changes,change_regs in actions:
   dll.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
   for bank,offset,value in changes:dll.api_live_store(bank,offset,value)
   for field,value in change_regs.items():setattr(r,field,value)
   f=getattr(dll,'api_c_'+target);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r))
  result.append((status,bytes(r),bytes(dll.ugh_memory().contents),bytes(dev)))
 return result

TRANSPORT=r'''#include "platform.h"
EXPORT unsigned resource_reads,resource_publishes,resource_read_counts[4],resource_publish_count;
void resource_actual_read(uint8_t*,uint32_t,unsigned);
void resource_actual_publish(uint32_t,const uint8_t*,unsigned,unsigned,size_t);
EXPORT void resource_transport_begin(void){resource_reads=resource_publishes=resource_publish_count=0;for(unsigned i=0;i<4;i++)resource_read_counts[i]=0;}
void audio_workspace_read(uint8_t*d,uint32_t a,unsigned n){if(resource_reads<4)resource_read_counts[resource_reads]=n;resource_reads++;resource_actual_read(d,a,n);}
void audio_workspace_publish(uint32_t a,const uint8_t*s,unsigned n,unsigned extent,size_t written){resource_publishes++;resource_publish_count=n;resource_actual_publish(a,s,n,extent,written);}
'''

def transport_dll(ROOT,OUT,bounded,clipped=False):
 from pathlib import Path
 folder=OUT/('transport-clipped' if clipped else 'transport');folder.mkdir(exist_ok=True)
 cmd=json.loads((OUT/'children/api-resources-composed-compile.json').read_text())['command'];cmd[cmd.index('-o')+1]=str(folder/'api.dll')
 for i,arg in enumerate(cmd):
  if not arg.endswith('.c'):continue
  original=Path(arg);text=original.read_text();changed=False
  if original.name.endswith('audio_world_bridge.c'):
   assert text.count('void audio_workspace_read(')==text.count('void audio_workspace_publish(')==1;text=text.replace('void audio_workspace_read(','void resource_actual_read(',1).replace('void audio_workspace_publish(','void resource_actual_publish(',1);changed=True
  if clipped and original.name in ['ice_bridge.c','native_ice_bridge.c']:
   old='audio_workspace_read(output,destination,sizeof output);';assert text.count(old)==1;text=text.replace(old,'memset(output,0,sizeof output);audio_workspace_read(output,destination,unpacked);');changed=True
  if changed:
   import re
   text=re.sub(r'#include "([^\"]+)"',lambda m:'#include "'+(original.parent/m[1]).resolve().as_posix()+'"' if (original.parent/m[1]).is_file() else m[0],text);new=folder/original.name;new.write_text(text);cmd[i]=str(new)
 helper=folder/'transport.c';helper.write_text(TRANSPORT);cmd.append(str(helper));bounded(cmd,'transport-'+('clipped' if clipped else 'full')+'-compile');return folder/'api.dll'

def seeded_tail(m):
 from dataprobe import ice_encode_tokens
 game=m.seg('GAME:DrawTransparentSprite');table=m.off('GAME:IceDecoderTables');bank=game+(table-512)//16;distance=game*16+table-bank*16-1
 assert 65<=distance<=576
 m.reset();m.write(0x8500,0,ice_encode_tokens(bytes(2),[('match',1,-1)],[distance]));return bank

def run(ROOT,OUT,bounded,save):
 import nbuild,difftest,palette_composition as palette
 dlls=[nbuild.load_l1(OUT/'api/resources'/label/'api.dll') for label in ['reference','composed']];m=difftest.Machine();rows=[];dirseg=m.rw('GAME:SpriteDirectoryPointer',2);game=m.seg('GAME:DrawTransparentSprite');data=m.seg('DGROUP:PlayerCount')
 for x in [0,1,31,32,6144,10239,10240,0x7fff,0x8000,0xffe0,0xffff]:
  for backwards in [0,1]:
   m.reset();m.ww('DGROUP:ActorX32',x);m.write(dirseg,858,b'\x13\x03')
   got=pair(m,dlls,'SetDemoRevealSpriteWidth',dict(BX=0));assert got[0]==got[1],('width',x,backwards)
   # Source/store alias is exactly record214's low dimension byte.
   assert got[1][2][dirseg*16+859]==3
   rows.append(dict(entry='SetDemoRevealSpriteWidth',x=x,stores=1,dir_index=214))
 # Live owner mutation between consumed operations, including a source-word
 # update that cannot be discarded by a frame-start resource snapshot.
 for x in [0,6144,0xffff]:
  m.reset();m.ww('DGROUP:ActorX32',x)
  actions=[('SetDemoRevealSpriteWidth',[(dirseg,858,0x0411),(data,m.off('DGROUP:ActorX32'),0)],{'bx':0})]
  got=pair(m,dlls,'SetDemoRevealSpriteWidth',dict(BX=0),actions);assert got[0]==got[1],('live width',x)
  assert got[1][2][dirseg*16+858:dirseg*16+860]==b'\x7f\x04'
  rows.append(dict(entry='SetDemoRevealSpriteWidth',live_reply=True,stores=2))
 # Full-window ICE with the provider cells in the retained (not written) tail.
 from dataprobe import ice_pack235
 for name in ['UnpackIceStream','UnpackIceToScratch']:
  for length in [1,17,32000,64768,65535,65536]:
   m.reset();payload=(bytes(range(256))*(length//256+1))[:length];stream=ice_pack235(payload);m.write(0x8500,0,stream)
   bank=m.seg('ZERO:IceDecodeWorkspace') if name.endswith('Scratch') else (game-0x400 if length<=32000 else 0x6000)
   print('CODEC',name,length,hex(bank),flush=True)
   got=pair(m,dlls,name,dict(DS=0x8500,ES=bank,SI=0));assert got[0]==got[1],(name,length)
   rows.append(dict(entry=name,length=length,full_window=65536,tail_borrows='codec tables for foreign safe low-output window; native audio flags/map prefix for canonical scratch'))
 # Request-count and seeded-reference witness over the real full-window adapters.
 transport=nbuild.load_l1(transport_dll(ROOT,OUT,bounded));bank=seeded_tail(m);transport.resource_transport_begin()
 got=pair(m,[dlls[0],transport],'UnpackIceStream',dict(DS=0x8500,ES=bank,SI=0));assert got[0]==got[1],'seeded table-tail byte differs'
 assert C.c_uint.in_dll(transport,'resource_reads').value==2 and C.c_uint.in_dll(transport,'resource_publishes').value==1
 assert list((C.c_uint*4).in_dll(transport,'resource_read_counts'))[:2]==[65536,65536] and C.c_uint.in_dll(transport,'resource_publish_count').value==65536
 rows.append(dict(entry='UnpackIceStream',seeded_codec_table_reference=True,read_counts=[65536,65536],publish_count=65536))
 # Generic data-window aliases use mutable directory bytes. Do not extend ICE
 # admission to overwriting decoder tables; the explicit rejection is tested below.
 source=inspect.getsource(palette.borrowers);source=source[:source.index(' # A maximal ICE destination')]
 source=source.replace("OUT/'api'/v/'api.dll'","OUT/'api/resources'/v/'api.dll'")
 source=source.replace("m.seg('GAME:BaseRgbPalette')","m.rw('GAME:SpriteDirectoryPointer',2)").replace("m.off('GAME:BaseRgbPalette')","0").replace("m.off('GAME:FadedRgbPalette')","858")
 source=source.replace('  for dll in dlls:\n','  for dll in dlls:\n   dll.api_begin()\n')
 source=source.replace("pair('UploadBasePalette',regs=", "m.ww('DGROUP:BasePalettePointer',base);m.ww('DGROUP:BasePalettePointer',game,2)\n pair('UploadBasePalette',regs=")
 source+=' save(OUT/"byte-borrowers.json",dict(result="PASS",cases=rows))\n'
 env=dict(palette.__dict__,OUT=OUT,save=save);exec(source,env);env['borrowers']()
 save(OUT/'borrowers.json',dict(result='PASS',cases=rows,byte_window_cases=len(json.loads((OUT/'byte-borrowers.json').read_text())['cases']),scope='Compiled independent L1/composed full returned RAM/Regs/Devices for reveal writes, live post-operation aliases and full65536-byte codec windows. Generic byte-window corpus compares accepted live ABI and RAM outside scratch stack plus ordered ports. Immutable table writes are outside codec admission and fail closed; no broader ICE code/table overlap is credited.'))

def defects(ROOT,OUT,bounded,save,snapshot,previous):
 folder=OUT/'defects';folder.mkdir(exist_ok=True);capture=folder/'capture.py';capture.write_text('import json,subprocess,sys\nr=subprocess.run(sys.argv[1:],capture_output=True,text=True);print(json.dumps(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)))\n');rows=[]
 gcc=previous.timing.common.GCC
 for fault,name in [(1,'stale-reveal-width'),(2,'wrong-token-map'),(3,'missed-serialization')]:
  exe=folder/(name+'.exe');bounded([gcc,'-O2','-std=c11','-DRESOURCE_TEST_FAULT='+str(fault),'-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/resource_catalog_router.c',ROOT/'native/resource_catalog.c',ROOT/'native/bridge/resource_catalog_bridge.c'],'defect-'+name+'-compile')
  result=json.loads(bounded([sys.executable,capture,exe],'defect-'+name+'-run')['stdout']);assert result['returncode']!=0,(name,'survived')
  rows.append(dict(defect=name,result='DETECTED',case='Independent literal numeric layout/token/whole-observation comparator',exit=result['returncode']))
 # Correct immutable barrier must fail closed, not ignore the store.
 result=json.loads(bounded([sys.executable,capture,OUT/'router/router.exe','immutable'],'immutable-store-run')['stdout']);assert result['returncode']==89 and 'immutable' in result['stderr'];rows.append(dict(defect='write-to-immutable',result='REJECTED',exit=89))
 # Removing that policy is a semantic mutant, observed by the same positive oracle.
 p=folder/'mutable-codec.c';text=(ROOT/'native/resource_catalog.c').read_text().replace('#include "resource_catalog.h"','#include "'+(ROOT/'native/resource_catalog.h').as_posix()+'"');old='return lane<view.size?RESOURCE_IMMUTABLE:RESOURCE_INVALID;';assert text.count(old)==1;p.write_text(text.replace(old,'return lane<view.size?RESOURCE_OK:RESOURCE_INVALID;'))
 exe=folder/'immutable-accepted.exe';bounded([gcc,'-O2','-std=c11','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/resource_catalog_router.c',p,ROOT/'native/bridge/resource_catalog_bridge.c'],'defect-immutable-accepted-compile');result=json.loads(bounded([sys.executable,capture,exe],'defect-immutable-accepted-run')['stdout']);assert result['returncode']==13;rows.append(dict(defect='immutable-write-accepted',result='DETECTED',exit=13))
 import difftest,nbuild
 m=difftest.Machine();bank=seeded_tail(m);reference=nbuild.load_l1(OUT/'api/resources/reference/api.dll');clipped=nbuild.load_l1(transport_dll(ROOT,OUT,bounded,True));clipped.resource_transport_begin()
 got=pair(m,[reference,clipped],'UnpackIceStream',dict(DS=0x8500,ES=bank,SI=0));counts=list((C.c_uint*4).in_dll(clipped,'resource_read_counts'))[:2]
 assert counts==[65536,2] and got[0]!=got[1],'clipped retained seed survived'
 rows.append(dict(defect='clipped-workspace-seed',result='DETECTED',case='two-byte first-match references private readonly codec-table seed in retained tail',read_counts=counts))
 target=snapshot()
 for fault,name,scenario in [(1,'stale-reveal-width','reveal'),(2,'wrong-token-map','reveal'),(3,'missed-serialization','gameplay-adlib')]:
  generated=folder/('host-'+name);hostcapture=previous.copy_host(target,generated);p=generated/'tools/hostbuild.py';text=p.read_text();needle="return (['-DUGH_NATIVE_RESOURCES']";assert text.count(needle)==1;p.write_text(text.replace(needle,"return (['-DRESOURCE_TEST_FAULT="+str(fault)+"','-DUGH_NATIVE_RESOURCES']",1))
  bounded([sys.executable,'tools/hostbuild.py'],'defect-host-'+name+'-build',generated)
  import wholegame
  script=target/('tests/scenarios/'+scenario+'.txt');ref=json.loads((target/('build/whole/'+scenario+'.ref.json')).read_text())['frames'];r=json.loads(bounded([sys.executable,hostcapture,generated/'build/host/ugh.exe','--headless',str(wholegame.scenario(script)['frames']),'--script',script,'--timeout','590'],'defect-host-'+name+'-run')['stdout']);got=[json.loads(l) for l in r['stdout'].splitlines()];first=next((i for i,(a,b) in enumerate(zip(got,ref)) if a!=b),None)
  if fault==3:assert r['returncode']==88 and 'missed serialization' in r['stderr']
  else:assert first is not None and r['returncode']==0,(name,r['returncode'],r['stderr'])
  rows.append(dict(defect=name,result='DETECTED',scenario=scenario,frame=first+1 if first is not None else len(got)+1,exit=r['returncode']))
 save(OUT/'defects.json',dict(result='PASS',controls=rows,scope='Three new owner/token/serializer seams plus immutable-store barrier and a policy-removal mutant; whole-host controls consume the real reveal/render paths. Source fixture/expected oracle unchanged.'))
