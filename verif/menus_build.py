"""Strict independent full L1 and native-front-end libraries."""
import os,re
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
from high_scores_build import NAMES as HIGH_NAMES
OUT=ROOT/'build/workers/close-adlx-13'
NAMES=['RunMainMenuAndAttractLoop', 'DrawMainMenu', 'DrawMenuHeaderSprites', 'SelectPlayerControls', 'DrawControlOptions', 'EditLevelPassword', 'CopyIndexedMenuString', 'DrawTextLine', 'DrawTextBlock', 'PrepareAttractMap0', 'PrepareAttractMap90', 'ShowLevelIntroduction', 'ShowCreditsPages']
def build(reference=False):
 folder=OUT/f'{"reference" if reference else "native"}-{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[];inputs=[]
 for p in sorted((ROOT/'c').glob('*.c')):
  source=p.read_text();changed=source
  if not reference:
   for n in [*HIGH_NAMES,*NAMES]:changed=re.sub(r'(EXPORT int )c_'+n+r'(?=\()',r'\1l1_'+n,changed)
  # Both generated variants trace dispatched entries, including IRQ targets.
  # Direct leaf calls may legitimately have no child entry; callers assert that.
  if p.name=='dispatch.c':
   assert changed.count('int status=fn(r);')==2
   changed=changed.replace('int status=fn(r);','platform_trace_entry(segment,offset,r); int status=fn(r);')
  if changed!=source:target=folder/p.name;target.write_text(changed);sources.append(target)
  else:sources.append(p)
  inputs.append(p)
 if not reference:
  for component,names in [('high_scores',HIGH_NAMES),('menus',NAMES)]:
   p=ROOT/f'native/bridge/{component}_bridge.c';text=p.read_text().replace(f'#include "../{component}.h"',f'#include "{(ROOT/f"native/{component}.h").as_posix()}"').replace('#include "front_end_support.h"',f'#include "{(ROOT/"native/bridge/front_end_support.h").as_posix()}"');text=f'#include "platform.h"\nEXPORT uint32_t {component}_audit[{len(names)}];\n'+text
   for i,n in enumerate(names):
    body=function(text,'c_'+n);text=text.replace(body,body.replace('{',f'{{{component}_audit[{i}]++;',1))
   target=folder/p.name;target.write_text(text);sources.append(target);inputs.append(p)
  sources.extend([ROOT/'native/high_scores.c',ROOT/'native/menus.c']);inputs.extend([ROOT/'native/high_scores.c',ROOT/'native/menus.c',ROOT/'native/high_scores.h',ROOT/'native/menus.h',ROOT/'native/front_end.h',ROOT/'native/bridge/front_end_support.h'])
 dll=folder/'menus.dll';r=compile_c(sources,dll,[ROOT/'c',ROOT/'native'],['-shared']);r['maintained_inputs']=hashes([*inputs,*sorted((ROOT/'c').glob('*.h')),Path(__file__)]);save(OUT/('menus-reference-build.json' if reference else 'menus-build.json'),r);return dll
if __name__=='__main__':print(build())
