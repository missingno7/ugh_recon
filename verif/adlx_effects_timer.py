"""Separate actual-C timer output and frame obligations to avoid array/division
coupling. Outputs admit every playing/period/request/old-scale/handle word; all
other state is unused by this opcode. Frame admits the full arbitrary state and
omits only the two cells covered by the output profile. No arithmetic model.
"""
import argparse,sys
from pathlib import Path
from closure_support import ROOT,cbmc as run_cbmc
from adlx_effects_build import OUT
import adlx_effects_word as word

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame']);p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
    word.OUT=OUT/('timer-'+a.mode)
    def split(harness,folder,inputs,**options):
        harness=Path(harness);text=harness.read_text()
        if a.mode=='outputs':
            text=text.replace('reference_state=nondet_audio();','''reference_state=(AudioState){0};
reference_state.playing=N16();reference_state.timer_period=N16();
reference_state.playback_timer_handle=N16();reference_state.channels[8].step_q8=N16();
reference_state.channels[8].first_voice=N16();''')
            text=text.replace('compare_state(&native,&reference_state);','''
CHECK(native.timer_period==reference_state.timer_period,"timer period output");
CHECK(native.channels[selected].step_q8==reference_state.channels[selected].step_q8,"timer scale output");
CHECK(native.playing==reference_state.playing && native.playback_timer_handle==reference_state.playback_timer_handle,"timer control inputs retained");''')
        else:
            text=text.replace('compare_state(&native,&reference_state);','''
native.timer_period=reference_state.timer_period;
native.channels[selected].step_q8=reference_state.channels[selected].step_q8;
compare_state(&native,&reference_state);''')
            text=text.replace('CHECK(r.di==cursor.index,"event consumption");','')
            text=text.replace('CHECK(result==(output.exit==AUDIO_EFFECTS_DIVIDE_FAULT ? UGH_UNSUPPORTED : UGH_OK),"step status");','')
        harness.write_text(text)
        return run_cbmc(harness,folder,[*inputs,Path(__file__)],**options)
    word.cbmc=split
    sys.argv=['adlx_effects_word.py','--op','6','--record','8','--timeout',str(a.timeout)]
    word.main()
if __name__=='__main__':main()
