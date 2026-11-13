"""Isolated falling-item variant and actual-C relational pair generation."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
sys.path.insert(0,str(ROOT/'tools'))
OUT=ROOT/'build/workers/close-items'
REPLACE={'items_water.c':['SpawnFallingItem','LandFallingItem','AdvanceFallingItem','DispatchFallingItems'],
         'actors_states.c':['ExpireOrCollectFallingItem']}
NAMES=[n for names in REPLACE.values() for n in names]
NATIVE=[ROOT/'native/items.c',ROOT/'native/contacts.c',ROOT/'native/bridge/items_bridge.c']

def build():
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True)
    sources=[];inputs=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        inputs.append(path)
        if path.name in REPLACE:
            text=path.read_text()
            for name in REPLACE[path.name]:
                text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text)
                assert n==1,name
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    bridge=NATIVE[-1];text=bridge.read_text()
    text=text.replace('#include "../items.h"','#include "'+(ROOT/'native/items.h').as_posix()+'"')
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name)
        body2=body.replace('{',f'{{ items_audit[{i}]++;',1)
        body2=body2.replace('return l1_'+name+'(r);',f'return items_audit[{i+5}]++, l1_{name}(r);')
        text=text.replace(body,body2)
    text=text.replace('int l1_SpawnFallingItem','EXPORT uint32_t items_audit[10];\nint l1_SpawnFallingItem',1)
    generated=folder/'items_bridge.c';generated.write_text(text)
    sources+=NATIVE[:-1]+[generated]
    dll=folder/'items.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native'],['-shared'])
    result['maintained_inputs']=hashes([*inputs,*NATIVE,Path(__file__),*sorted((ROOT/'native').glob('*.h')),
        *sorted((ROOT/'c').glob('*.h')),*sorted((ROOT/'c').glob('*.inc'))])
    save(OUT/'build.json',result);return dll

def pair(folder):
    folder.mkdir(parents=True,exist_ok=True)
    text=f'#include "{(ROOT/"c/ugh.h").as_posix()}"\n'
    # A normalized word RAM shim retains all maintained L1 arithmetic and control
    # flow, while avoiding bit-blasted 1-MiB byte-array multiplexer circuits.
    text+='uint16_t items_rd16(uint16_t,uint16_t);\nvoid items_wr16(uint16_t,uint16_t,uint16_t);\nuint8_t items_rd8(uint16_t,uint16_t);\nvoid items_wr8(uint16_t,uint16_t,uint8_t);\n'
    text+='#define rd16 items_rd16\n#define wr16 items_wr16\n#define rd8 items_rd8\n#define wr8 items_wr8\n'
    raw=(ROOT/'c/items_water.c').read_text()
    for name in ['cell','sar5','shl5','c_IgnoreExhaustedTree',*['c_'+n for n in REPLACE['items_water.c']]]:
        text+=function(raw,name)
    raw=(ROOT/'c/actors_states.c').read_text()
    text+='\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\n'
    for name in ['shift','byte_add','byte_sub','c_ExpireOrCollectFallingItem']:text+=function(raw,name)
    for name in NAMES:text=re.sub(r'\bc_'+name+r'\b','l1_'+name,text)
    for name in NATIVE[:2]:text+=f'#include "{name.as_posix()}"\n'
    # Actual reference contact, independent of native contacts.
    raw=(ROOT/'c/actors.c').read_text()
    text+='#define READ(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))\n#define DESC(n) rd16(r->ds,(uint16_t)(r->si+(n)))\n'
    for name in ['shl','less','greater','contact','c_FindPlayerTouchingFallingItem']:text+=function(raw,name)
    text+='#undef A\n#undef B\n#undef F\n#undef R\n#undef W\n'
    text+=f'#include "{NATIVE[-1].as_posix()}"\n'
    target=folder/'pair.inc';target.write_text(text)
    return [ROOT/'c/items_water.c',ROOT/'c/actors_states.c',ROOT/'c/actors.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',
        *NATIVE[:2],ROOT/'native/items.h',ROOT/'native/contacts.h',ROOT/'native/geometry.h',ROOT/'native/level.h']

if __name__=='__main__':print(build())
