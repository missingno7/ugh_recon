"""Four exact ABI shells consuming the native lifecycle request sequence."""
import argparse
from closure_support import ROOT,function
OUT=ROOT/'build/workers/close-stones-12/lifecycle'
BRIDGE=ROOT/'native/bridge/lifecycle_bridge.c'
NAMES=['RunDosGame','InitializeDosVideoInputAndSound','InitializeAdLibSound','FadeAndShutdownSound']
FILES=[ROOT/'native/lifecycle.h',ROOT/'native/lifecycle.c',BRIDGE]

def replace(text,old,new):assert text.count(old)==1,(old,text.count(old));return text.replace(old,new)
def generated():
    video=(ROOT/'c/video.c').read_text();menu=(ROOT/'c/menu.c').read_text()
    s='''#include "platform.h"
#include "../lifecycle.h"
#include <stdlib.h>
static void lc_require(int condition){if(!condition)abort();}
static uint16_t lc_word(uint16_t native_value,uint16_t literal){lc_require(native_value==literal);return native_value;}
static LifecycleRequest lc_take(LifecycleProcess *p,LifecycleAction expected){LifecycleRequest e=lifecycle_next(p);lc_require(e.action==expected && lifecycle_consume(p,e.action));return e;}
static void lc_finish(LifecycleProcess *p){lc_require(lifecycle_complete(p));}
'''
    for n in ['push','pop','video_far_call']:s+=function(video,n)+'\n'
    s+='''static int lc_call(Regs *r,LifecycleProcess *p,uint16_t target,uint16_t ret){
 LifecycleAction action;
 if(target==G(InitializeDosVideoInputAndSound))action=LIFE_INITIALIZE_PLATFORM;
 else if(target==G(ShowStartupPictures))action=LIFE_STARTUP_PICTURES;
 else if(target==G(ConfigureVgaGameplayPages))action=LIFE_GAMEPLAY_VIDEO;
 else if(target==G(RunMainMenuAndAttractLoop))action=LIFE_MAIN_MENU;
 else if(target==G(InstallDosCriticalErrorFailHandler))action=LIFE_INSTALL_ERROR_HANDLER;
 else if(target==G(LoadHighScores))action=LIFE_LOAD_SCORES;
 else if(target==G(SeedRandomFromDosSeconds))action=LIFE_SEED_RANDOM;
 else if(target==G(ConfigureVgaPicturePages))action=LIFE_PICTURE_VIDEO;
 else if(target==G(InstallKeyboardSequenceInterrupt))action=LIFE_INSTALL_KEYBOARD;
 else if(target==G(DetectAndCalibrateJoysticks))action=LIFE_CALIBRATE_CONTROLS;
 else {lc_require(target==G(InitializeAdLibSound));action=LIFE_INITIALIZE_AUDIO;}
 lc_take(p,action);return ugh_call_near(target,ret,r);
}
#define MCALL(n,ret) do{int status=lc_call(r,&plan,G(n),ret);if(status)return status;}while(0)
'''
    b=function(menu,'c_RunDosGame');b=replace(b,'    r->dx=DATA_SEG;','    LifecycleProcess plan;lifecycle_begin(&plan,LIFE_PROGRAM);lc_take(&plan,LIFE_BIND_WORLD);\n    r->dx=DATA_SEG;')
    b=replace(b,'    return ugh_dispatch','    lc_take(&plan,LIFE_SHUTDOWN_PLATFORM);lc_finish(&plan);return ugh_dispatch');s+=b+'\n'
    b=function(video,'c_InitializeDosVideoInputAndSound');b=replace(b,'    set_ah(r,15);','    LifecycleProcess plan;lifecycle_begin(&plan,LIFE_PLATFORM_INIT);lc_take(&plan,LIFE_QUERY_VIDEO);\n    set_ah(r,15);')
    b=replace(b,'    set_al(r,(uint8_t)logic','    lifecycle_video_reply(&plan,r->ax);LifecycleRequest mode=lc_take(&plan,LIFE_SAVE_VIDEO);\n    set_al(r,(uint8_t)logic')
    b=replace(b,'wr8(r->ds,D(SavedBiosVideoMode),(uint8_t)r->ax);','wr8(r->ds,D(SavedBiosVideoMode),(uint8_t)lc_word(mode.argument,(uint8_t)r->ax));lc_take(&plan,LIFE_CPU_PROBE);')
    b=b.replace('call(r,','lc_call(r,&plan,')
    b=replace(b,'    flag(r,DF,0); r->ax=0x13;','    LifecycleRequest video_mode=lc_take(&plan,LIFE_SET_VIDEO);\n    flag(r,DF,0); r->ax=lc_word(video_mode.argument,0x13);')
    b=replace(b,'    return c_ClearAllVgaPlanes(r);','    lc_take(&plan,LIFE_CLEAR_VIDEO);lc_finish(&plan);return c_ClearAllVgaPlanes(r);');s+=b+'\n'
    b=function(video,'c_InitializeAdLibSound');b=replace(b,'    push(r,1);','    LifecycleProcess plan;lifecycle_begin(&plan,LIFE_ADLIB_INIT);LifecycleRequest e=lc_take(&plan,LIFE_SOUND_INITIALIZE_ADLIB);\n    push(r,lc_word(e.argument,1));')
    b=replace(b,'r->sp=add16(r,r->sp,2,0); return UGH_OK;','r->sp=add16(r,r->sp,2,0);lc_finish(&plan);return UGH_OK;');s+=b+'\n'
    b=function(video,'c_FadeAndShutdownSound');b=replace(b,'    push(r,0x11);','    LifecycleProcess plan;lifecycle_begin(&plan,LIFE_SOUND_SHUTDOWN);LifecycleRequest e=lc_take(&plan,LIFE_STOP_MUSIC);\n    push(r,lc_word(e.argument,0x11));')
    b=replace(b,'    return video_far_call','    lc_take(&plan,LIFE_SOUND_STOP);lc_finish(&plan);return video_far_call');s+=b+'\n'
    return s
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();s=generated()
    if a.write:BRIDGE.write_text(s)
    assert BRIDGE.read_text()==s;print('PASS four lifecycle ABI shells and exact request cuts')
if __name__=='__main__':main()
