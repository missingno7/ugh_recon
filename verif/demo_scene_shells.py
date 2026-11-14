"""Exact checked L1 presentation shells; no changes to accepted render bridge."""
import re,sys
from closure_support import ROOT,function
BRIDGE=ROOT/'native/bridge/demo_presentation_bridge.c'
NAMES=['StartDemoFadeWhenSpriteHidden','SetDemoRevealSpriteWidth','RunScriptedDemo','PlaySpriteRevealDemo','PlayPreGameDemo','PlayAttractDemo','PlayGameCompletionDemo']
KINDS=['DEMO_PRESENT_RUN','DEMO_PRESENT_REVEAL','DEMO_PRESENT_PREGAME','DEMO_PRESENT_ATTRACT','DEMO_PRESENT_COMPLETION']
def generated():
    scene=(ROOT/'c/scene.c').read_text();effects=(ROOT/'c/demo_scripts.c').read_text();out=''
    for helper in ['push','pop','scene_far_call']:
        text=function(scene,helper)
        if helper=='scene_far_call':
            text=text.replace('Regs *r,uint16_t seg','Regs *r,DemoScenePlan *plan,uint16_t seg')
            text=text.replace('    push(r,r->cs);','    if(plan->active) dp_require(plan->pending && (plan->pending_action.service==DP_SERVICE_MUSIC_STOP || plan->pending_action.service==DP_SERVICE_MUSIC_START));\n    push(r,r->cs);')
            text=text.replace('return st;','dp_resume(r,plan);return st;')
        out+=text+'\n'
    for n,kind in zip(NAMES[2:],KINDS):
        text=function(scene,'c_'+n).replace('{','{ DemoScenePlan plan;dp_open(r,&plan,'+kind+');',1)
        text=re.sub(r'r->si=D\((DemoTable_\w+)\);',r'r->si=dp_vector(r,&plan,D(\1));',text)
        text=text.replace('scene_far_call(r,','scene_far_call(r,&plan,')
        text=text.replace('push(r,0x11);','push(r,dp_music_value(r,&plan,DP_SERVICE_MUSIC_STOP,0x11));')
        text=text.replace('push(r,0xa5);','push(r,dp_music_value(r,&plan,DP_SERVICE_MUSIC_START,0xa5));')
        text=text.replace('return c_RunScriptedDemo(r);','return dp_tail(r,&plan,1);')
        text=text.replace('return ugh_dispatch(r->cs,G(RunScriptedDemo),r);','return dp_tail(r,&plan,0);')
        if n=='RunScriptedDemo':
            text=text.replace('continue;','{dp_repeat(r,&plan);continue;}')
            line='r->ax=0xfffc; W(ScreenFadeStep,r->ax); W(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0));'
            assert text.count(line)==1;text=text.replace(line,line+' dp_repeat(r,&plan);')
        text=text.replace('return UGH_OK;','dp_finish(r,&plan);return UGH_OK;')
        out+=text+'\n'
    for n in NAMES[:2]:
        text=function(effects,'c_'+n).replace('{','{ DemoEffectPlan plan=dp_effect(r,'+('1' if n==NAMES[1] else '0')+');',1)
        if n==NAMES[0]:
            text=text.replace('    if(sprite==0x7fff)', '    if(plan.active) dp_require(plan.fade.triggered==(sprite==0x7fff));\n    if(sprite==0x7fff)')
            text=text.replace('wr16(r->ds,D(ScreenFadeStep),r->ax);','dp_effect_write(r,&plan,D(ScreenFadeStep),r->ax);')
            text=text.replace('wr16(r->ds,D(ScreenFadeLevel),','dp_effect_write(r,&plan,D(ScreenFadeLevel),')
        else:text=text.replace('wr8(r->es,r->di,(uint8_t)r->ax);','wr8(r->es,r->di,dp_width_byte(r,&plan));')
        out+=text+'\n'
    return out
def main():
    marker='/* BEGIN CHECKED DEMO SHELLS */\n';prefix=BRIDGE.read_text().split(marker)[0];text=prefix+marker+generated()
    if '--write' in sys.argv:BRIDGE.write_text(text)
    else:assert BRIDGE.read_text()==text,'demo presentation shell drift'
    print('PASS seven retained presentation shells and original near/far frames')
if __name__=='__main__':main()
