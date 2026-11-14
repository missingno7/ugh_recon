"""Compile private controller/effect/protocol defects; detect actual behavior."""
from closure_support import ROOT,save
from demo_scene_build import OUT
from demo_scene_cases import run
def main():
    text=(ROOT/'native/demo_presentation.c').read_text();changes={
     'clear-before-initialization':('kind==DEMO_PRESENT_RUN?DP_INITIALIZE:DP_PREPARE','kind==DEMO_PRESENT_RUN?DP_CLEAR_EXIT:DP_PREPARE'),
     'wrong-initial-fade':('presentation_value(DP_ACTION_STEP,4)','presentation_value(DP_ACTION_STEP,0)'),
     'lost-negative-fade-test':('presentation_signed(input->fade_level)<0','0'),
     'palette-old-level':('input->palette_work+input->fade_step','input->fade_level+input->fade_step'),
     'water-equality':('presentation_signed(input->water_y)<192','presentation_signed(input->water_y)<=192'),
     'completion-carry-polarity':('if(input->finished)','if(!input->finished)'),
     'joystick-zero-polarity':('if(input->joystick_idle)','if(!input->joystick_idle)'),
     'key-high-byte':('if(!(input->key_word>>8))','if(!(input->key_word&255u))'),
     'key-break-mask':('input->key_word&127u','input->key_word&255u'),
     'quit-exit-code':('key==16?65535u:key==1?1u:0u','key==16?0u:key==1?1u:0u'),
     'zero-step-normalized':('presentation_signed(input->fade_step)<0','presentation_signed(input->fade_step)<=0'),
     'wrong-fade-wrap':('(input->fade_level-4u)','(input->fade_level-3u)'),
     'wrong-wrapper-map':('cursor->kind==DEMO_PRESENT_ATTRACT?DP_SERVICE_PREPARE_NINETY:DP_SERVICE_PREPARE_ZERO','cursor->kind==DEMO_PRESENT_ATTRACT?DP_SERVICE_PREPARE_ZERO:DP_SERVICE_PREPARE_NINETY'),
     'wrong-reveal-vector':('(uint16_t)cursor->kind','(uint16_t)DEMO_PRESENT_PREGAME'),
     'omit-reveal-cleanup':('cursor->kind==DEMO_PRESENT_REVEAL?DP_REVEAL_X:DP_WRAPPER_DONE','DP_WRAPPER_DONE'),
     'wrong-music-reason':('action.value=17','action.value=16'),
     'fade-trigger-hidden':('sprite==32767u','sprite==65535u'),
     'width-logical-sar':('((position_x32&32768u)?63488u:0)','0'),
     'width-cleared-high-byte':('((width.width_word&65280u)|127u)','127u'),
     'private-next-cut-only':('cursor->phase=DP_DRAW;return presentation_service(DP_SERVICE_ADVANCE)','cursor->phase=DP_SWAP;return presentation_service(DP_SERVICE_ADVANCE)'),
    }
    rows=[]
    for name,(old,new) in changes.items():
        assert old in text,name;folder=OUT/'mutants'/name;folder.mkdir(parents=True,exist_ok=True);path=folder/'demo_presentation.c';path.write_text(text.replace(old,new));value,result=run(folder,mutant=path)
        assert value.returncode==23,(name,value.returncode,value.stderr);result.update(result='DETECTED',mutant=name);save(folder/'result.json',result);rows.append(result);print(name+' DETECTED',flush=True)
    for name,change in {
      'captured-palette-only':('plan->observed.palette_work=r->cx;','plan->observed.palette_work=0;'),
      'captured-completion-only':('plan->observed.finished=(r->flags&CF)!=0;','plan->observed.finished=(r->flags&CF)==0;'),
      'unconsumed-parent-finish':('if(!status) dp_finish(r,plan);',''),
      'native-service-only':('dp_require(action.service==service);','action.service=DP_SERVICE_SWAP;dp_require(action.service==service);'),
    }.items():
        folder=OUT/'mutants'/name;folder.mkdir(parents=True,exist_ok=True);value,result=run(folder,bridge_mutant=change);assert value.returncode==23,(name,value.returncode,value.stderr);result.update(result='DETECTED',mutant=name);save(folder/'result.json',result);rows.append(result);print(name+' DETECTED',flush=True)
    save(OUT/'mutants.json',rows)
if __name__=='__main__':main()
