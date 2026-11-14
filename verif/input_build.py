"""Strict independent full L1 and eight-entry native-input libraries."""
import os,re
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
OUT=ROOT/'build/workers/close-adlx-11'
NAMES=['DetectAndCalibrateJoysticks','SampleJoystickAxesAndButtons','HandleKeyboardScanInterrupt','InstallKeyboardSequenceInterrupt','RestoreKeyboardInterrupt','PollKeyboardScanChange','WaitForScanChangeOrJoystickButton','PollPlayerControls']
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
  p=ROOT/'native/bridge/input_bridge.c';text=p.read_text().replace('#include "../input.h"',f'#include "{(ROOT/"native/input.h").as_posix()}"');text=text.replace('static void push','EXPORT uint32_t input_audit[16];\nstatic void push',1)
  for i,n in enumerate(NAMES):
   body=function(text,'c_'+n);text=text.replace(body,body.replace('{',f'{{input_audit[{i}]++;',1))
  text=text.replace('r->si=source.position;logic(r,r->si,16);','r->si=source.position;logic(r,r->si,16);unsigned kind=!source.joystick ? 0 : source.position==0 ? 1 : source.position==2 ? 2 : 3;if(kind<3 && r->bx<=2) input_audit[8+3u*(r->bx/2u)+kind]++;',1)
  text=text.replace('case INPUT_KEY_WRITE_ACTION:wr8','case INPUT_KEY_WRITE_ACTION:input_audit[14]++;wr8',1)
  target=folder/p.name;target.write_text(text);sources.extend([target,ROOT/'native/input.c']);inputs.extend([p,ROOT/'native/input.c',ROOT/'native/input.h'])
 dll=folder/'input.dll';r=compile_c(sources,dll,[ROOT/'c',ROOT/'native'],['-shared']);r['maintained_inputs']=hashes([*inputs,*sorted((ROOT/'c').glob('*.h')),Path(__file__)]);save(OUT/('reference-build.json' if reference else 'build.json'),r);return dll
if __name__=='__main__':print(build())
