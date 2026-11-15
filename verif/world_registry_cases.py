"""Registry admission/overlap controls and an unmaintained toy world."""
import copy,json,os,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from job_pool import run,save

def toy(out):
 from world_gate import freeze
 out=Path(out);root=freeze(out);folder=root/'native';bridge=folder/'bridge';name='toy_world'
 (folder/(name+'.h')).write_text('#include <stdint.h>\nuint8_t *native_toy_world(void);\n')
 (folder/(name+'.c')).write_text('#include "toy_world.h"\nstatic uint8_t value;uint8_t *native_toy_world(void){return &value;}\n')
 (bridge/(name+'_bridge.h')).write_text('''#include "ugh.h"
void toy_cold_import(uint8_t*);void toy_require_seal(const uint8_t*);void toy_serialize(uint8_t*);
unsigned toy_owned_bytes(void);int toy_is_owned(uint32_t);int toy_shared_read(uint32_t,uint8_t*);int toy_shared_write(uint32_t,uint8_t);uint32_t toy_check_serialization(const uint8_t*);
uint8_t toy_borrowed_byte(const uint8_t*,uint32_t);void toy_borrowed_store(uint8_t*,uint32_t,uint8_t);
''')
 (bridge/(name+'_bridge.c')).write_text('''#include "platform.h"
#include "toy_world_bridge.h"
#include "../toy_world.h"
#include <stdlib.h>
#define TOY_ADDRESS 0x105000u
static unsigned active;
void toy_cold_import(uint8_t*m){active=0;*native_toy_world()=m[TOY_ADDRESS];m[TOY_ADDRESS]=0xa5;active=1;}
void toy_require_seal(const uint8_t*m){if(active&&m[TOY_ADDRESS]!=0xa5)exit(88);}
unsigned toy_owned_bytes(void){return active;}
int toy_is_owned(uint32_t a){return active&&a==TOY_ADDRESS;}
int toy_shared_read(uint32_t a,uint8_t*v){if(!toy_is_owned(a))return 0;*v=*native_toy_world();return 1;}
int toy_shared_write(uint32_t a,uint8_t v){if(!toy_is_owned(a))return 0;*native_toy_world()=v;return 1;}
void toy_serialize(uint8_t*m){if(active)m[TOY_ADDRESS]=*native_toy_world();}
uint32_t toy_check_serialization(const uint8_t*m){return active&&m[TOY_ADDRESS]!=*native_toy_world()?TOY_ADDRESS:UINT32_MAX;}
uint8_t toy_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void toy_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
''')
 row=json.loads((root/'metadata/worlds/enemy_world.json').read_text());row.update(component=name,flag='UGH_NATIVE_TOY',order=99,header='native/bridge/toy_world_bridge.h',bridge='native/bridge/toy_world_bridge.c',compile_flags=[],platform_provider=None)
 for key in ['cold_import','seal','read','write','serialize','check','owned_bytes','borrowed_byte','borrowed_store']:
  row[key]=row[key].replace('enemies','toy')
 row['lanes']=dict(predicate='toy_is_owned',bytes=1,stability='one fixed toy lane');row['gate']={'cases':'not a maintained toy case'}
 save(root/'metadata/worlds/toy_world.json',row)
 c=dict(status='migrated',component=name,purpose='Scratch-only build admission fixture; no game/evidence claim',native=dict(files=['native/toy_world.h','native/toy_world.c','native/bridge/toy_world_bridge.h','native/bridge/toy_world_bridge.c'],functions=['native_toy_world'],bridge='Uncommitted toy admission control'))
 save(root/'metadata/closure/toy_world.json',c)
 # This is the only admission: own files/certificate plus one registry entry.
 shared=['tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h','verif/projector/publications.py','verif/projector_evidence.py']
 import hashlib
 before={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in shared}
 run([sys.executable,'tools/hostbuild.py','--out',out/'host','--no-generate'],root,out,'toy-build')
 run([sys.executable,'host/check.py','--out',out/'host','--receipt-dir',out,'--variant','native'],root,out,'toy-check')
 assert before=={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in shared}
 # Overlap is a real generated-table failure, not a substituted expected result.
 p=bridge/'toy_world_bridge.c';p.write_text(p.read_text().replace('#define TOY_ADDRESS 0x105000u','#define TOY_ADDRESS (((uint32_t)DATA_SEG<<4)+D(EnemyDescriptors))'))
 run([sys.executable,'tools/hostbuild.py','--out',out/'overlap','--no-generate'],root,out,'overlap-build')
 result=run([out/'overlap/ugh.exe','--headless','1','--smoke','1','--timeout','30'],root,out,'overlap-run',allowed=(88,));assert 'world registry overlap' in result['stderr']
 save(out/'receipt.json',dict(result='PASS',toy='unmaintained scratch entry',shared_files_unchanged=shared,toy_host='21/21',overlap='exit88 detected',source_admission='own native/bridge files and certificate plus one registry entry; no shared-file edit'))
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'build/workers/close-adlx-29/toy');a=p.parse_args();toy(a.out)
