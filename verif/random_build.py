"""Build the RNG substitution in an isolated worker directory."""
import os,re,sys
from closure_support import ROOT,compile_c,function,hashes,save
from random_evidence import OUT,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import nbuild

def build():
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True)
    sources=[];inputs=[]
    for p in sorted((ROOT/'c').glob('*.c')):
        inputs.append(p)
        if p.name=='dos_input.c':
            text=p.read_text()
            # Rename definitions only; all callers continue to enter bridges.
            for name in NAMES:
                text=re.sub(r'EXPORT int c_'+name+r'\(',r'EXPORT int l1_'+name+'(',text)
            generated=folder/p.name;generated.write_text(text);sources.append(generated)
        else:sources.append(p)
    bridge=ROOT/'native/bridge/random_bridge.c';text=bridge.read_text()
    text=text.replace('#include "../random.h"','#include "'+(ROOT/'native/random.h').as_posix()+'"')
    # Add audit entries without modifying maintained bridge code.
    text=text.replace('EXPORT int c_NextRandomBelowAx','EXPORT uint32_t random_audit[2];\nEXPORT int c_NextRandomBelowAx',1)
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name)
        text=text.replace(body,body.replace('{',f'{{ random_audit[{i}]++;',1))
    generated=folder/'random_bridge.c';generated.write_text(text)
    sources += [ROOT/'native/random.c',generated]
    dll=folder/'random.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native'],['-shared'])
    result['maintained_inputs']=hashes([*inputs,bridge,ROOT/'native/random.c',ROOT/'native/random.h',
        ROOT/'verif/random_build.py',*sorted((ROOT/'c').glob('*.h')),*sorted((ROOT/'c').glob('*.inc'))])
    save(OUT/'build.json',result)
    return dll

if __name__=='__main__':print(build())
