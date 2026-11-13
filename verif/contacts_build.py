"""Isolated contact/level-view variant; locked historical builders stay unchanged."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
sys.path.insert(0,str(ROOT/'tools'))
import nbuild
OUT=ROOT/'build/workers/close-contacts'
NAMES=['FindPlayerTouchingFallingItem','FindPlayerTouchingActor','FindPlayerTouchingEnemy','FindThrownStoneHittingEnemy']
NATIVE=[ROOT/'native/contacts.c',ROOT/'native/level_view.c',ROOT/'native/bridge/level_view_bridge.c',ROOT/'native/bridge/contacts_bridge.c']

def build():
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True)
    sources=[];inputs=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        inputs.append(path)
        if path.name=='actors.c':
            text=path.read_text()
            # Rename definitions only: calls within actors.c must use bridges too.
            for name in NAMES:
                text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text)
                assert n==1,name
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    sources+=NATIVE[:-1]
    text=NATIVE[-1].read_text()
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name)
        text=text.replace(body,body.replace('{',f'{{ contacts_audit[{i}]++;',1))
    text=text.replace('return l1_FindThrownStoneHittingEnemy(r);','return contacts_audit[4]++, l1_FindThrownStoneHittingEnemy(r);')
    text=text.replace('#include "../contacts.h"','#include "'+(ROOT/'native/contacts.h').as_posix()+'"')
    text=text.replace('int l1_FindThrownStoneHittingEnemy','EXPORT uint32_t contacts_audit[5];\nint l1_FindThrownStoneHittingEnemy',1)
    generated=folder/'contacts_bridge.c';generated.write_text(text);sources.append(generated)
    dll=folder/'contacts.dll'
    result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared'])
    result['maintained_inputs']=hashes([*inputs,*NATIVE,*sorted((ROOT/'native').glob('*.h')),
        ROOT/'native/bridge/level_projection.h',Path(__file__),
        *sorted((ROOT/'c').glob('*.h')),*sorted((ROOT/'c').glob('*.inc'))])
    save(OUT/'build.json',result);return dll

def pair(folder,bridges=False,word_memory=False):
    folder.mkdir(parents=True,exist_ok=True)
    raw=(ROOT/'c/actors.c').read_text()
    prefix='\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\n'
    text=f'#include "{(ROOT/"c/ugh.h").as_posix()}"\n'+prefix
    if word_memory:text+='uint16_t contacts_read_word(uint16_t,uint16_t);\n#define rd16 contacts_read_word\n'
    for name in ['shl','less','greater','contact',*['c_'+n for n in NAMES]]:
        text+=function(raw,name)
    for name in NAMES:text=re.sub(r'\bc_'+name+r'\b','l1_'+name,text)
    paths=[ROOT/'c/actors.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'native/geometry.h',ROOT/'native/level.h',ROOT/'native/contacts.h',*NATIVE[:2]]
    for p in NATIVE[:2]:text+=f'#include "{p.as_posix()}"\n'
    if bridges:
        for p in NATIVE[2:]:text+=f'#include "{p.as_posix()}"\n';paths.append(p)
        paths.append(ROOT/'native/bridge/level_projection.h')
    target=folder/'pair.inc';target.write_text(text)
    return paths

if __name__=='__main__':print(build())
