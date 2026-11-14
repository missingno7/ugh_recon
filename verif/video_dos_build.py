"""Strict independent full L1 and twenty-entry native-video/DOS libraries."""
import os,re
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
OUT=ROOT/'build/workers/close-adlx-12'
NAMES=['BlackenVgaPalette', 'UploadBasePalette', 'DuplicateSourcePaletteHalves', 'ScaleAndUploadFadedPalette', 'FadePaletteIn', 'FadePaletteOut', 'ClearAllVgaPlanes', 'EnableAllVgaWritePlanes', 'ConfigureVgaGameplayPages', 'ConfigureVgaPicturePages', 'SwapAndDisplayVgaPage', 'UploadChunkyImageToVgaPlanes', 'WaitNextVerticalRetrace', 'WaitRetraceCount', 'WaitThroughVerticalRetrace', 'WaitVerticalRetraceActive', 'WaitVerticalRetraceInactive', 'WaitForInputOrRetraceTimeout', 'InstallDosCriticalErrorFailHandler', 'FailDosCriticalError']
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
  p=ROOT/'native/bridge/video_dos_bridge.c';text=p.read_text().replace('#include "../video_dos.h"',f'#include "{(ROOT/"native/video_dos.h").as_posix()}"');text=text.replace('static void push','EXPORT uint32_t video_dos_audit[20];\nstatic void push',1)
  for i,n in enumerate(NAMES):
   body=function(text,'c_'+n);text=text.replace(body,body.replace('{',f'{{video_dos_audit[{i}]++;',1))
  target=folder/p.name;target.write_text(text);sources.extend([target,ROOT/'native/video_dos.c']);inputs.extend([p,ROOT/'native/video_dos.c',ROOT/'native/video_dos.h'])
 dll=folder/'video_dos.dll';r=compile_c(sources,dll,[ROOT/'c',ROOT/'native'],['-shared']);r['maintained_inputs']=hashes([*inputs,*sorted((ROOT/'c').glob('*.h')),Path(__file__)]);save(OUT/('reference-build.json' if reference else 'build.json'),r);return dll
if __name__=='__main__':print(build())
