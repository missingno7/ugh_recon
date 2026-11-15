"""Build/test standalone service groundwork; never compiles or links game code.

Generated host/OPL presentation oracles are independent of port implementations.
Children are serially bounded to600s/8GiB; all maintained sources stay untouched.
"""
import argparse,ctypes as C,hashlib,json,os,shutil,struct,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-stones-26'
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from windows_job import WindowsJob,ExtendedLimits
from cbuild import GCC
SDL=Path('C:/tools/sdl3-3.4.16-mingw/SDL3-3.4.16/x86_64-w64-mingw32')
OPL=Path('C:/tools/nuked-opl3-765ec962e473')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def textsha(path):return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def save(path,value):Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps(value,indent=2)+'\n')
def bounded(command,name,env=None):
 command=list(map(str,command));start=time.perf_counter()
 environment=dict(os.environ,PATH=str(GCC.parent)+os.pathsep+str(SDL/'bin')+os.pathsep+os.environ.get('PATH',''),SDL_AUDIO_DRIVER='dummy',SDL_VIDEO_DRIVER='dummy')
 if env:environment.update(env)
 with WindowsJob() as job:
  limits=ExtendedLimits();limits.basic.flags=0x2000|0x100|0x200;limits.process_memory=limits.job_memory=8*1024**3
  if not job.kernel.SetInformationJobObject(job.handle,9,C.byref(limits),C.sizeof(limits)):raise C.WinError(C.get_last_error())
  p=subprocess.Popen(command,cwd=ROOT,env=environment,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);job.assign(p)
  try:stdout,stderr=p.communicate(timeout=600)
  except subprocess.TimeoutExpired:
   job.terminate();stdout,stderr=p.communicate();save(OUT/'negative'/(name+'-timeout.json'),dict(result='TIMEOUT',command=command,stdout=stdout,stderr=stderr));raise
 row=dict(command=command,returncode=p.returncode,stdout=stdout,stderr=stderr,seconds=time.perf_counter()-start,timeout_seconds=600,memory_limit_bytes=8589934592)
 save(OUT/'children'/(name+'.json'),row)
 if p.returncode:save(OUT/'negative'/(name+'-'+str(time.time_ns())+'.json'),row);raise RuntimeError(name+': '+stderr[-5000:]+stdout[-1000:])
 print(name,'PASS',round(row['seconds'],2),'s',flush=True);return row
def compiler(output,sources,extra=()):
 return [GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'port','-I',ROOT/'tests/port','-I',OUT,'-I',SDL/'include','-I',OPL,*extra,'-o',output,*sources,'-L',SDL/'lib','-lSDL3']
def build():
 OUT.mkdir(parents=True,exist_ok=True)
 pins=json.loads((ROOT/'tests/port/toolchain.json').read_text())
 for name,pin in pins.items():assert sha(pin['path'])==pin['sha256'],'installed tool drift: '+name
 bounded([sys.executable,ROOT/'tools/respack.py','--output',OUT/'ugh.res','--header',OUT/'resource_manifest.h'],'pack-extract')
 sources=[ROOT/'tests/port/services.c',ROOT/'port/hash.c',ROOT/'port/resources.c',*sorted((ROOT/'port/sdl').glob('*.c')),OPL/'opl3.c']
 bounded(compiler(OUT/'services.exe',sources),'build-services')
 bounded(compiler(OUT/'oracle-opl.exe',[ROOT/'tests/port/oracle_opl.c',OPL/'opl3.c']),'build-opl-oracle')
 bounded([OUT/'oracle-opl.exe',OUT/'opl.golden.pcm'],'opl-oracle')
 for path in [SDL/'bin/SDL3.dll',GCC.parent/'libwinpthread-1.dll']:
  if path.exists():shutil.copy2(path,OUT/path.name)
 inputs=[p for p in (ROOT/'port').rglob('*') if p.is_file()]+[p for p in (ROOT/'tests/port').rglob('*') if p.is_file()]+[ROOT/'tools/respack.py',Path(__file__)]
 save(OUT/'build.json',dict(result='PASS',compiler=str(GCC),compiler_sha256=sha(GCC),sdl_sha256=sha(SDL/'bin/SDL3.dll'),sdl_provenance=json.loads((SDL.parents[1]/'provenance.json').read_text()),opl_commit='765ec962e473aeb767e4cba74ffdc8f588ffbfe8',opl_inputs={p.name:sha(p) for p in [OPL/'opl3.c',OPL/'opl3.h']},inputs={p.relative_to(ROOT).as_posix():sha(p) for p in inputs},linked_sources=[str(p) for p in sources],game_code_linked=False))
def unit():
 bounded([OUT/'services.exe','unit',OUT/'scores.test'],'unit')
 bounded([OUT/'services.exe','audio',OUT/'opl.golden.pcm'],'audio')
 record=dict(sequence_sha256=textsha(ROOT/'tests/port/opl_sequence.h'),pcm_sha256=sha(OUT/'opl.golden.pcm'),frames=4800,provider='independent direct pinned OPL3 oracle; host buffered write/generate convention')
 golden=ROOT/'tests/port/audio_golden.json'
 assert golden.exists() and record==json.loads(golden.read_text()),'missing or changed OPL golden'
 save(OUT/'unit.json',dict(result='PASS',audio=record,keyboard='recorded set1 make/break/E0 + editor transitions/overflow',gamepad='recorded endpoints/center, both sticks, full65536 axis domain, wrapped limit0 and presence/buttons',time='7000 ticks=100 rational seconds; suspended delivery empty and no resume catchup',files='raw107-byte roundtrip, stale short tail, live truncation, logical handle retained after atomic persistence'))
def pack():
 import respack
 bounded([OUT/'services.exe','pack',OUT/'ugh.res'],'pack-c-reader')
 m=OUT/'ugh.manifest.json';result=respack.verify(OUT/'ugh.res',m)
 base=(OUT/'ugh.res').read_bytes();rows=[];folder=OUT/'pack-controls';folder.mkdir(exist_ok=True)
 for name in ['missing-file','short','version','table-hash','payload-hash','required-id','missing-id','required-content','overflow','duplicate-id','class-changed','unreferenced-tail','detached-alias']:
  path=folder/(name+'.res');data=bytearray(base)
  if name=='missing-file':
   if path.exists():path.unlink()
  else:
   if name=='short':data=data[:20]
   elif name=='version':data[8]^=1
   elif name=='table-hash':data[140]^=1
   elif name=='payload-hash':data[-1]^=1
   else:
    count=struct.unpack_from('<I',data,16)[0];payload=128+64*count
    if name=='required-id':struct.pack_into('<Q',data,128,0x100000000-1)
    elif name=='missing-id':
     del data[128:192];count-=1;payload-=64;struct.pack_into('<I',data,16,count);struct.pack_into('<Q',data,32,payload);struct.pack_into('<Q',data,40,len(data))
    elif name=='required-content':
     offset,size=struct.unpack_from('<QQ',data,144);data[payload+offset]^=1;data[160:192]=hashlib.sha256(data[payload+offset:payload+offset+size]).digest();data[80:112]=hashlib.sha256(data[payload:]).digest()
    elif name=='overflow':struct.pack_into('<Q',data,144,0xffffffffffffffff)
    elif name=='duplicate-id':data[192:200]=data[128:136]
    elif name=='class-changed':struct.pack_into('<I',data,136,1)
    elif name in ['unreferenced-tail','detached-alias']:
     offset,size=struct.unpack_from('<QQ',data,144)
     if name=='detached-alias':struct.pack_into('<Q',data,144,len(data)-payload)
     data+=data[payload+offset:payload+offset+size] if name=='detached-alias' else b'UNREGISTERED'
     struct.pack_into('<Q',data,40,len(data));data[80:112]=hashlib.sha256(data[payload:]).digest()
    data[48:80]=hashlib.sha256(data[128:payload]).digest()
   path.write_bytes(data)
  row=bounded([OUT/'services.exe','reject',path],'pack-control-'+name);assert 'REJECTED resource pack:' in row['stdout'];rows.append(dict(control=name,result='REJECTED',diagnostic=row['stdout'].strip()))
 save(OUT/'pack.json',dict(**result,controls=rows,pack_sha256=sha(OUT/'ugh.res'),aliases='Catalog views and named mutable records share payload; immutable/mutable overlap rejected',scope='Every selected data declaration byte roundtrips; no instruction or executable header is extracted. Manifest records excluded zero scratch separately. Initializer objects are identified seeds, not a runtime address image.'))

def capture_picture():
 import wholegame
 from emu import NativeVga,DeviceState
 folder=OUT/'picture';folder.mkdir(exist_ok=True)
 (folder/'accelerator').mkdir(exist_ok=True)
 wholegame.VGA_ACCELERATOR=NativeVga(folder/'accelerator')
 path=ROOT/'tests/scenarios/startup.txt';scenario=wholegame.scenario(path);machine,initial=wholegame.fixture(scenario);trace={}
 records,*_=wholegame.original(scenario,machine,initial,stop=12,trace=trace)
 reference=json.loads((ROOT/'build/whole/startup.ref.json').read_text())['frames'];assert records==reference[:12],'picture source frame diverged from maintained ASM reference'
 device=DeviceState();C.memmove(C.addressof(device),trace['final_device'],len(trace['final_device']))
 raw=bytes(device.planes)+bytes(device.dac)+bytes(device.crtc)
 (folder/'picture.state').write_bytes(raw)
 reference_hash=hashlib.sha256(json.dumps(reference[:12],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 save(folder/'source.json',dict(result='PASS',scenario='startup',frame=12,reference_frames_sha256=reference_hash,script_sha256=textsha(path),state_sha256=hashlib.sha256(raw).hexdigest(),source='reconstructed ASM under Unicorn, all12 frames equal maintained reference'))

def video():
 bounded([sys.executable,__file__,'--capture-picture'],'picture-capture')
 folder=OUT/'picture';shim=folder/'oracle.h'
 shim.write_text('#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <SDL3/SDL.h>\ntypedef struct {uint8_t plane[4][65536],dac[768],crtc[25];} Devices;\nextern Devices ugh_devices;\nstatic inline void host_fail(const char *s){fputs(s,stderr);exit(3);}\n')
 source=(ROOT/'host/video.c').read_text().replace('#include "host.h"','#include "oracle.h"')
 (folder/'host_video.c').write_text(source)
 bounded(compiler(folder/'video.exe',[ROOT/'tests/port/video.c',folder/'host_video.c',ROOT/'port/sdl/video.c'],['-I',folder]),'build-video-oracle')
 bounded([folder/'video.exe',folder/'picture.state',folder/'picture.rgb'],'video-picture')
 source=json.loads((folder/'source.json').read_text());source.update(rgb_sha256=sha(folder/'picture.rgb'),host_video_sha256=textsha(ROOT/'host/video.c'))
 golden=ROOT/'tests/port/video_golden.json'
 assert golden.exists() and source==json.loads(golden.read_text()),'missing or changed picture golden'
 save(OUT/'video.json',dict(result='PASS',golden=source,scope='Original reference picture -> typed four-lane store; every RGB pixel equals the current host_render on the identical planes/DAC/CRTC. Additional synthetic page/pitch/split/hidden offsets checked by same independent host presentation.'))
def finish():
 required=['unit','pack','video'];rows={n:json.loads((OUT/(n+'.json')).read_text()) for n in required};assert all(r['result']=='PASS' for r in rows.values())
 text=(ROOT/'port/services.h').read_text();assert not any(x in text for x in ['Regs','ugh_mem','0xa000','0xA000','seg:off'])
 build=json.loads((OUT/'build.json').read_text())
 for name,expected in build['inputs'].items():assert sha(ROOT/name)==expected,'built input changed: '+name
 save(OUT/'receipt.json',dict(result='PASS',scope='Step8 groundwork only; no game linkage or certificate/status change',build_sha256=sha(OUT/'build.json'),evidence={n:sha(OUT/(n+'.json')) for n in required},interface_sha256=sha(ROOT/'port/services.h')))
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['build','unit','pack','video','capture-picture','finish','all']:p.add_argument('--'+n,action='store_true')
 a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if a.all:
  for n in ['build','unit','pack','video']:bounded([sys.executable,__file__,'--'+n],n+'-child')
  finish();return
 for n in ['build','unit','pack','capture_picture','video','finish']:
  if getattr(a,n):globals()[n]()
if __name__=='__main__':main()
