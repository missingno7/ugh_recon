"""Split actual-C lifetime, handler, calibration and reset properties."""
import argparse,re
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_lifetime_build import OUT
from adlx_lifetime_evidence import pair_code
SOLVER=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe']
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('entry',choices=['reset','initialize','shutdown','begin','finish','calibrate']);p.add_argument('mode',choices=['outputs','frame','dependence']);p.add_argument('--negative',action='store_true');p.add_argument('--wide',action='store_true');p.add_argument('--literal-peers',action='store_true');p.add_argument('--timeout',type=int,default=180);a=p.parse_args()
    folder=OUT/f'proof-{a.entry}-{a.mode}{"-wide" if a.wide else "-literal" if a.literal_peers else "-contract"}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
    code=pair_code('measure' if a.entry in ['begin','finish','calibrate'] else 'reset' if a.entry=='reset' else 'probe' if a.negative else None) if a.negative else pair_code()
    code=code[:code.index('static unsigned case_number,operation;')]+code[code.index('static unsigned case_number,operation;')+len('static unsigned case_number,operation;\n'):]
    code=re.sub(r'#define CHECK\(c,m\).*?\n','#define CHECK(c,m) __CPROVER_assert(c,m)\n',code,count=1)
    for header in ['stdio.h','stdlib.h','string.h']:code=code.replace('#include <'+header+'>\n','')
    code=code.replace('#include "audio_projection.h"',f'#include "{(ROOT/"native/bridge/audio_projection.h").as_posix()}"')
    # The accepted compiled 65536-byte-pair enumeration discharges CPU LOOP;
    # no device/state operation occurs inside it. No calibration loop is cut.
    loop='    uint16_t remaining=product;\n    do { remaining=(uint16_t)(remaining-1); } while(remaining);\n'
    assert loop in code;code=code.replace(loop,'/* Accepted finite DelaySoundIo state contract. */\n')
    if not a.literal_peers and a.entry in ['initialize','shutdown']:
        # Relational child contract: same operator/calibration input and same
        # arbitrary returned BX imply the same ordered child program. Actual
        # silence C/bridge has its independent accepted certificate. No
        # lifetime branch, probe or TIMER interaction is substituted here.
        body=function(code,'c_SilenceAdlibOperators')
        code=code.replace(body,'int lifetime_silence_contract(Regs *r);\nEXPORT int c_SilenceAdlibOperators(Regs *r) {return lifetime_silence_contract(r);}\n')
    code+='\n'+(ROOT/'verif/adlx_lifetime_symbolic.c').read_text()
    entries={'reset':('reference_ClearSoundState','c_ClearSoundState'),'initialize':('reference_InitializeAdlibPlayback','c_InitializeAdlibPlayback'),'shutdown':('reference_ShutdownAdlibPlayback','c_ShutdownAdlibPlayback'),'begin':('reference_BeginSoundDelayMeasurement','c_BeginSoundDelayMeasurement'),'finish':('reference_FinishSoundDelayMeasurement','c_FinishSoundDelayMeasurement'),'calibrate':('reference_CalibrateSoundDelay','c_CalibrateSoundDelay')}
    left,right=entries[a.entry]
    code=code.replace('ENTRY_REFERENCE',left).replace('ENTRY_NATIVE',right).replace('CALIBRATING','1' if a.entry=='calibrate' else '0').replace('RESETTING','1' if a.entry=='reset' else '0')
    code=code.replace('OUTPUTS','1' if a.mode=='outputs' else '0').replace('FRAME','1' if a.mode=='frame' else '0').replace('DEPENDENCE','1' if a.mode=='dependence' else '0')
    harness=folder/'harness.c';harness.write_text(code)
    extra=SOLVER if a.wide else [*SOLVER,'--unwindset','lifetime_run.0:23,reference_CalibrateSoundDelay.0:3,reference_CalibrateSoundDelay.1:3,reference_CalibrateSoundDelay.2:2,c_CalibrateSoundDelay.0:5']
    result=cbmc(harness,folder,[Path(__file__),ROOT/'verif/adlx_lifetime_symbolic.c',ROOT/'verif/adlx_lifetime_evidence.py',ROOT/'native/adlx_lifetime.c',ROOT/'native/adlx_lifetime.h',ROOT/'native/bridge/adlx_lifetime_bridge.c',ROOT/'native/audio.h',ROOT/'native/bridge/audio_projection.h',ROOT/'c/adlib.c',ROOT/'c/sound_engine.c',ROOT/'c/sound_state.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'c/platform.h'],unwind=1165 if a.entry=='reset' else 130,timeout=a.timeout,extra=extra)
    print(a.entry,a.mode,result['result'],result['seconds'],result['failures'],flush=True)
    assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
