"""Strict independent full L1 and native-picture libraries."""
import os,re
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
OUT=ROOT/'build/workers/close-adlx-14'
NAMES=['UnpackPictureAndCopyPalette','ShowPackedPictureAndWait','ShowStartupPictures']
def build(reference=False,ice=False):
 folder=OUT/f'{"reference" if reference else "native"}-{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[];inputs=[]
 for p in sorted((ROOT/'c').glob('*.c')):
  source=p.read_text();changed=source
  if not reference:
   for n in [*NAMES,*(['UnpackIceStream'] if ice else [])]:changed=re.sub(r'(EXPORT int )c_'+n+r'(?=\()',r'\1l1_'+n,changed)
  # The maintained literal dispatcher has no trace hook. Enable the existing
  # read-only observer in generated copies on BOTH sides, never in c/.
  if p.name=='dispatch.c':
   assert changed.count('int status=fn(r);')==2
   changed=changed.replace('int status=fn(r);','platform_trace_entry(segment,offset,r); int status=fn(r);')
  if changed!=source:target=folder/p.name;target.write_text(changed);sources.append(target)
  else:sources.append(p)
  inputs.append(p)
 if not reference:
  p=ROOT/'native/bridge/pictures_bridge.c';text=p.read_text().replace('#include "../pictures.h"',f'#include "{(ROOT/"native/pictures.h").as_posix()}"');text='#include "platform.h"\nEXPORT uint32_t pictures_audit[3];\n'+text
  for i,n in enumerate(NAMES):
   body=function(text,'c_'+n);text=text.replace(body,body.replace('{',f'{{pictures_audit[{i}]++;',1))
  target=folder/p.name;target.write_text(text);sources.extend([target,ROOT/'native/pictures.c']);inputs.extend([p,ROOT/'native/pictures.c',ROOT/'native/pictures.h'])
 if not reference and ice:
  sources.extend([ROOT/'native/ice.c',ROOT/'native/bridge/ice_bridge.c']);inputs.extend([ROOT/'native/ice.c',ROOT/'native/ice.h',ROOT/'native/bridge/ice_bridge.c'])
 dll=folder/'pictures.dll';r=compile_c(sources,dll,[ROOT/'c',ROOT/'native'],['-shared']);r['maintained_inputs']=hashes([*inputs,*sorted((ROOT/'c').glob('*.h')),Path(__file__)]);save(OUT/('pictures-reference-build.json' if reference else 'pictures-ice-build.json' if ice else 'pictures-build.json'),r);return dll
if __name__=='__main__':print(build())
