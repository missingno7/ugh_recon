"""Data-driven verification-host composition; no game logic or ownership guesses."""
import json,os,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def entries(root=None,components=None):
 root=Path(root or ROOT);folder=Path(os.environ.get('UGH_WORLD_REGISTRY',str(root/'metadata/worlds')))
 rows=[json.loads(p.read_text(encoding='utf-8'))|{'registry_file':p} for p in sorted(folder.glob('*.json')) if components is None or p.stem in components]
 seen=set()
 for row in rows:
  if row['registry_file'].stem!=row['component']:raise ValueError('registry filename must name its component')
  if row['component'] in seen:raise ValueError('duplicate world '+row['component'])
  seen.add(row['component'])
  for k in ['header','bridge']:
   if not (root/row[k]).is_file():raise ValueError('missing world '+k+': '+row[k])
 return sorted(rows,key=lambda x:(x['order'],x['component']))

def selected(units,root=None):
 names={u['component'] for u in units};rows=entries(root,components=names)
 for row in rows:
  if row.get('storage_owner') and row['storage_owner'] not in names:raise ValueError('missing storage owner '+row['storage_owner'])
 if len(rows)>254:raise ValueError('world owner table exceeds byte identity capacity')
 return rows

def header(rows):
 includes=''.join('#include "'+(ROOT/r['header']).as_posix()+'"\n' for r in rows)
 return '''/* Generated world registry. Do not edit. */
#ifndef UGH_GENERATED_WORLD_REGISTRY_H
#define UGH_GENERATED_WORLD_REGISTRY_H
#include "ugh.h"
'''+includes+'''
int world_registry_read(uint32_t address,uint8_t *value);
int world_registry_write(uint32_t address,uint8_t value);
int world_registry_is_owned(uint32_t address);
void world_registry_cold_import(uint8_t *memory);
void world_registry_invalidate(void);
void world_registry_require_seal(const uint8_t *memory);
void world_registry_serialize(uint8_t *output);
uint32_t world_registry_check(const uint8_t *output);
unsigned world_registry_owned_bytes(void);
uint8_t world_borrowed_byte(const uint8_t *window,uint32_t index);
void world_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
#endif
'''

def generate(units,folder=None):
 rows=selected(units);folder=Path(folder or ROOT/'build/host/registry');folder.mkdir(parents=True,exist_ok=True)
 p=folder/'world_registry_generated.h';content=header(rows)
 if not p.exists() or p.read_text()!=content:p.write_text(content,encoding='utf-8')
 return folder

def options(units,base=None):
 rows=selected(units)
 if not rows:return []
 folder=generate(units,base)
 return ['-DUGH_WORLD_REGISTRY',*[f'-D{r["flag"]}' for r in rows],*[f for r in rows for f in r['compile_flags']],'-I',str(folder),'-I',str(ROOT/'native/bridge'),'-I',str(ROOT/'verif/projector')]

def implementation(rows):
 owners=[r for r in rows if r['cold_import']]
 table=''.join('{'+','.join([json.dumps(r['component']),r['lanes']['predicate'],r['read'],r['write'],r['cold_import'],r['seal'],r['serialize'],r['check'],r['owned_bytes']])+'},\n' for r in owners)
 return '''
/* Generated single owner table. Membership is disjoint, never precedence. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
typedef struct WorldOwner {
 const char *name;int (*owns)(uint32_t);int (*read)(uint32_t,uint8_t*);int (*write)(uint32_t,uint8_t);
 void (*import)(uint8_t*);void (*seal)(const uint8_t*);void (*serialize)(uint8_t*);
 uint32_t (*check)(const uint8_t*);unsigned (*bytes)(void);
} WorldOwner;
static const WorldOwner world_owners[]={
'''+table+'''};
#define WORLD_COUNT (sizeof world_owners/sizeof world_owners[0])
static uint8_t world_lane_owner[UGH_MEM_SIZE];
static uint32_t world_lane_epoch[UGH_MEM_SIZE],world_epoch=1;
static unsigned world_topology_checked;
void world_registry_invalidate(void){if(!++world_epoch){memset(world_lane_epoch,0,sizeof world_lane_epoch);world_epoch=1;}}
static unsigned world_owner(uint32_t address){
 if(address>=UGH_MEM_SIZE)return 0;
 if(world_lane_epoch[address]!=world_epoch){
  unsigned found=0;
  for(unsigned i=0;i<WORLD_COUNT;i++)if(world_owners[i].owns(address)){
   if(found){fprintf(stderr,"world registry overlap at %05X: %s / %s\\n",address,world_owners[found-1].name,world_owners[i].name);exit(88);}
   found=i+1;
  }
  world_lane_owner[address]=(uint8_t)found;world_lane_epoch[address]=world_epoch;
 }
 return world_lane_owner[address];
}
int world_registry_is_owned(uint32_t address){return world_owner(address)!=0;}
int world_registry_read(uint32_t address,uint8_t *value){unsigned n=world_owner(address);if(!n)return 0;if(!world_owners[n-1].read(address,value)){fputs("world registry stale owner\\n",stderr);exit(88);}return 1;}
int world_registry_write(uint32_t address,uint8_t value){unsigned n=world_owner(address);if(!n)return 0;if(!world_owners[n-1].write(address,value)){fputs("world registry stale owner\\n",stderr);exit(88);}return 1;}
void world_registry_cold_import(uint8_t *memory){
 world_registry_invalidate();for(unsigned i=0;i<WORLD_COUNT;i++)world_owners[i].import(memory);world_registry_invalidate();
 if(!world_topology_checked){unsigned lanes=0;for(uint32_t a=0;a<UGH_MEM_SIZE;a++)lanes+=world_owner(a)!=0;
 if(lanes!=world_registry_owned_bytes()){fputs("world registry lane count mismatch\\n",stderr);exit(88);}world_topology_checked=1;}
}
void world_registry_require_seal(const uint8_t *memory){for(unsigned i=0;i<WORLD_COUNT;i++)world_owners[i].seal(memory);}
void world_registry_serialize(uint8_t *output){for(unsigned i=0;i<WORLD_COUNT;i++)world_owners[i].serialize(output);}
uint32_t world_registry_check(const uint8_t *output){for(unsigned i=0;i<WORLD_COUNT;i++){uint32_t at=world_owners[i].check(output);if(at!=UINT32_MAX)return at;}return UINT32_MAX;}
unsigned world_registry_owned_bytes(void){unsigned n=0;for(unsigned i=0;i<WORLD_COUNT;i++)n+=world_owners[i].bytes();return n;}
uint8_t world_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(world_registry_read((uint32_t)(p-base+index),&value))return value;}
 return window[index];
}
void world_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && world_registry_write((uint32_t)(p-base+index),value))return;
 window[index]=value;
}
'''

def function_span(text,name):
 m=re.search(r'\b(?:uint8_t|void)\s+'+re.escape(name)+r'\s*\([^;{}]*\)\s*\{',text)
 if not m:return None
 b=text.index('{',m.start());depth=1;i=b+1
 while depth:
  if text[i]=='{':depth+=1
  elif text[i]=='}':depth-=1
  i+=1
 return m.start(),b,i

def compose(relative,text,units):
 rows=selected(units)
 if not rows:return text
 h='#include "world_registry_generated.h"\n'
 if relative=='c/memory.c':
  text=text.replace('uint8_t ugh_read(uint32_t a) {','uint8_t ugh_read(uint32_t a) { uint8_t owned; if(world_registry_read(a,&owned))return owned;')
  text=text.replace('void ugh_write(uint32_t a, uint8_t v) {','void ugh_write(uint32_t a, uint8_t v) { if(world_registry_write(a,v))return;')
  return h+text+implementation(rows)
 if relative=='c/platform.c':return h+text+'\n'+''.join((ROOT/r['platform_provider']).read_text()+'\n' for r in rows if r['platform_provider'])
 if relative in ('native/far_copy.c','native/decimal.c'):
  name='far_copy.h' if relative.endswith('far_copy.c') else 'decimal.h';text=text.replace('#include "'+name+'"','#include "'+(ROOT/'native'/name).as_posix()+'"')
  if relative.endswith('far_copy.c'):
   old='destination[destination_cursor]=source[source_cursor];';assert text.count(old)==1
   text=text.replace(old,'world_borrowed_store(destination,destination_cursor,world_borrowed_byte(source,source_cursor));')
  else:
   for v in ['digit','255']:text=text.replace('output->bytes[output->cursor]='+v+';','world_borrowed_store(output->bytes,output->cursor,'+v+');')
   text=text.replace('bytes[0]+(uint16_t)bytes[1]*256u','world_borrowed_byte(bytes,0)+(uint16_t)world_borrowed_byte(bytes,1)*256u')
   for v in ['ten','hundred']:text=text.replace('*divisors.'+v,'world_borrowed_byte(divisors.'+v+',0)')
  return h+text
 names={r['component'] for r in rows}
 if relative in ('native/bridge/ice_bridge.c','native/bridge/ice_scratch_bridge.c') and 'audio_world' in names:
  name='ice_scratch.h' if 'ice_scratch_bridge' in relative else 'ice.h'
  text=text.replace('#include "../'+name+'"','#include "'+(ROOT/'native'/name).as_posix()+'"\n#include "audio_world_bridge.h"')
  written='result.decoder.bytes_written' if 'ice_scratch_bridge' in relative else 'result.bytes_written'
  return text.replace('memcpy(input,ugh_mem+source,sizeof input);','audio_workspace_read(input,source,sizeof input);').replace('memcpy(output,ugh_mem+destination,sizeof output);','audio_workspace_read(output,destination,sizeof output);').replace('memcpy(ugh_mem+destination,output,sizeof output);','audio_workspace_publish(destination,output,sizeof output,unpacked,'+written+');')
 if relative in ('native/bridge/menus_bridge.c','native/bridge/high_scores_bridge.c') and 'input_world' in names:return h+text.replace('platform_interrupt(0x16,r)','input_editor_queue(r)')
 if relative in {r['bridge'] for r in rows}:
  for r in rows:
   for key,target in [('borrowed_byte','world_borrowed_byte'),('borrowed_store','world_borrowed_store')]:
    f=function_span(text,r[key])
    if f:
     a,b,z=f;signature=text[a:b];parameters=signature[signature.index('(')+1:signature.rfind(')')];arguments=[re.findall(r'[A-Za-z_]\w*',v)[-1] for v in parameters.split(',')];assert len(arguments)==(2 if key=='borrowed_byte' else 3)
     text=text[:b+1]+'\n '+('return ' if key=='borrowed_byte' else '')+target+'('+','.join(arguments)+');\n'+text[z-1:]
  local=next(r for r in rows if r['bridge']==relative)
  if local['cold_import']:
   name=local['cold_import'];f=function_span(text,name);assert f,name
   a,b,z=f;text=text[:a]+text[a:z].replace(name+'(','world_private_'+name+'(',1)+text[z:]
   text+='\nvoid '+name+'(uint8_t *memory){world_registry_invalidate();world_private_'+name+'(memory);world_registry_invalidate();}\n'
  if relative=='native/bridge/audio_world_bridge.c':
   text=text.replace('timing_shared_read(address+i,&value)','world_registry_read(address+i,&value)').replace('timing_is_owned(address)','world_registry_is_owned(address)').replace('timing_shared_write(address,source[i])','world_registry_write(address,source[i])')
  return h+text
 return text
