"""Strict independent full L1 and native-front-end libraries."""
import os,re
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
OUT=ROOT/'build/workers/close-adlx-13'
NAMES=['LoadHighScores', 'SaveHighScores', 'ComplementHighScoreTable', 'GetHighScoreRow', 'GetHighScoreDigits', 'CopyHighScoreRowDown', 'TestHighScoreQualification', 'InsertHighScoreAndClearScore', 'ShowHighScores', 'DrawHighScoreNameEntry']
def build(reference=False):
 folder=OUT/f'{"reference" if reference else "native"}-{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[];inputs=[]
 for p in sorted((ROOT/'c').glob('*.c')):
  source=p.read_text();changed=source
  if not reference:
   for n in NAMES:changed=re.sub(r'(EXPORT int )c_'+n+r'(?=\()',r'\1l1_'+n,changed)
  if changed!=source:target=folder/p.name;target.write_text(changed);sources.append(target)
  else:sources.append(p)
  inputs.append(p)
 if not reference:
  p=ROOT/'native/bridge/high_scores_bridge.c';text=p.read_text().replace('#include "../high_scores.h"',f'#include "{(ROOT/"native/high_scores.h").as_posix()}"').replace('#include "front_end_support.h"',f'#include "{(ROOT/"native/bridge/front_end_support.h").as_posix()}"');text='#include "platform.h"\nEXPORT uint32_t high_scores_audit[10];\n'+text
  for i,n in enumerate(NAMES):
   body=function(text,'c_'+n);text=text.replace(body,body.replace('{',f'{{high_scores_audit[{i}]++;',1))
  target=folder/p.name;target.write_text(text);sources.extend([target,ROOT/'native/high_scores.c']);inputs.extend([p,ROOT/'native/high_scores.c',ROOT/'native/high_scores.h',ROOT/'native/front_end.h',ROOT/'native/bridge/front_end_support.h'])
 dll=folder/'high_scores.dll';r=compile_c(sources,dll,[ROOT/'c',ROOT/'native'],['-shared']);r['maintained_inputs']=hashes([*inputs,*sorted((ROOT/'c').glob('*.h')),Path(__file__)]);save(OUT/('high-reference-build.json' if reference else 'high-build.json'),r);return dll
if __name__=='__main__':print(build())
