"""Actual fade C outputs, plus separate native whole-state frame/dependence."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_music_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependence','timer','timer-frame','timer-dependence']);p.add_argument('--word-memory',action='store_true');p.add_argument('--negative',action='store_true');p.add_argument('--timeout',type=int,default=180);a=p.parse_args();assert 0<a.timeout<=600
    folder=OUT/f'proof-fade-{a.mode}{"-word" if a.word_memory else ""}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
    native=(ROOT/'native/adlx_music.c').read_text();literal=(ROOT/'c/adlib.c').read_text()
    code='''#include "ugh.h"
#include "adlx_music.h"
#ifndef INT32_MIN
#define INT32_MIN (-2147483647-1)
#endif
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];AudioState nondet_audio(void);uint16_t nondet_u16(void);uint8_t nondet_u8(void);
static AudioState reference;static uint8_t stack[1024];static uint16_t event,argument,remainder,handle,reply,status;
uint8_t ugh_read(uint32_t address) {
 unsigned p=address-(unsigned)SOUND_SEG*16u;uint16_t v;
 if((p&65534u)==S(MusicFadeStep)) v=reference.fade.step_count;
 else if((p&65534u)==S(MusicFadeDuration)) v=reference.fade.duration;
 else if((p&65534u)==S(MusicFadeStartVolume)) v=reference.fade.start_volume;
 else if((p&65534u)==S(MusicFadeTargetVolume)) v=reference.fade.target_volume;
 else if((p&65534u)==S(MusicFadeTimerHandle)) v=reference.fade.timer_handle;
 else if((p&65534u)==S(MusicFadeScheduled)) v=reference.fade.scheduled;
 else {CHECK(address>=0x80000 && address<0x80400,"fade stack read");return stack[address-0x80000];}
 return (uint8_t)(v>>(8*(p&1u)));
}
void ugh_write(uint32_t address,uint8_t value) {
 unsigned p=address-(unsigned)SOUND_SEG*16u;uint16_t *v=0;
 if((p&65534u)==S(MusicFadeStep)) v=&reference.fade.step_count;
 else if((p&65534u)==S(MusicFadeTimerHandle)) v=&reference.fade.timer_handle;
 else if((p&65534u)==S(MusicFadeScheduled)) v=&reference.fade.scheduled;
 else {CHECK(address>=0x80000 && address<0x80400,"fade stack write");stack[address-0x80000]=value;return;}
 unsigned shift=8*(p&1u);*v=(uint16_t)((*v&~(255u<<shift))|((unsigned)value<<shift));
}
int ugh_dispatch(uint16_t b,uint16_t t,Regs *r) {
 CHECK(!event,"one fade service");
 if(b==TIMER_SEG && t==T(RemoveTimerCallback)) {event=1;handle=r->ax;}
 else if(b==UGH_SEG_C && t==UGH_O_C_SetMusicTrackVolume) {event=2;argument=arg16(r,0);remainder=r->dx;}
 else {CHECK(b==TIMER_SEG && t==T(RegisterTimerCallback),"exact fade callback set");event=3;CHECK(r->ax==S(AdvanceMusicFade) && r->dx==SOUND_SEG && r->cx==1 && r->bx==0xd1eb,"fade registration ABI interval and target");}
 r->ax=reply;return status;
}
'''
    if a.word_memory:
        code+='''static uint16_t fade_read_word(uint16_t bank,uint16_t offset) {
 if(bank==SOUND_SEG) {
  if(offset==S(MusicFadeStep)) return reference.fade.step_count;
  if(offset==S(MusicFadeDuration)) return reference.fade.duration;
  if(offset==S(MusicFadeStartVolume)) return reference.fade.start_volume;
  if(offset==S(MusicFadeTargetVolume)) return reference.fade.target_volume;
  if(offset==S(MusicFadeScheduled)) return reference.fade.scheduled;
  if(offset==S(MusicFadeTimerHandle)) return reference.fade.timer_handle;
 }
 CHECK(bank==0x8000 && offset<1023 && !(offset&1),"aligned ordinary stack word");return (uint16_t)(stack[offset]|(unsigned)stack[offset+1]*256u);
}
static void fade_write_word(uint16_t bank,uint16_t offset,uint16_t value) {
 if(bank==SOUND_SEG) {
  if(offset==S(MusicFadeStep)) {reference.fade.step_count=value;return;}
  if(offset==S(MusicFadeScheduled)) {reference.fade.scheduled=value;return;}
  if(offset==S(MusicFadeTimerHandle)) {reference.fade.timer_handle=value;return;}
 }
 CHECK(bank==0x8000 && offset<1023 && !(offset&1),"aligned ordinary stack store");stack[offset]=(uint8_t)value;stack[offset+1]=(uint8_t)(value>>8);
}
#define rd16 fade_read_word
#define wr16 fade_write_word
'''
    for name in ['push','call','inc','c_CancelMusicFade','c_ScheduleMusicFade','c_AdvanceMusicFade']:code+=function(literal,name)
    for name in ['audio_music_fade_step','audio_music_schedule','audio_music_cancel','audio_music_registered','audio_music_cancelled']:
        f=function(native,name)
        if a.negative and name=='audio_music_fade_step':f=f.replace('state->fade.step_count>state->fade.duration','(int16_t)state->fade.step_count>(int16_t)state->fade.duration')
        code+=f
    if a.mode=='outputs':
        code+='''int main(void) {
 reference=nondet_audio();AudioState native=reference;Regs r={0};r.cs=SOUND_SEG;r.ss=0x8000;r.sp=0x200;r.flags=nondet_u16();reply=nondet_u16();status=nondet_u16();__CPROVER_assume(status<=1);
 int rc=c_AdvanceMusicFade(&r);AudioFadeRequest q=audio_music_fade_step(&native);
 CHECK(reference.fade.step_count==native.fade.step_count,"wrapping step output");
 if(q.action==AUDIO_FADE_FAULT) CHECK(rc==UGH_UNSUPPORTED && !event,"actual signed divide fault");
 else if(q.action==AUDIO_FADE_REMOVE) {CHECK(event==1 && handle==q.handle && rc==status,"unsigned completion requests removal");if(!status) audio_music_cancelled(&native);}
 else CHECK(q.action==AUDIO_FADE_VOLUME && event==2 && argument==q.volume && remainder==q.remainder && rc==status,"signed IMUL/IDIV interpolated word and remainder");
 CHECK(reference.fade.scheduled==native.fade.scheduled,"clear scheduled only after successful remover");return 0;}
'''
    elif a.mode=='timer':
        code+='''int main(void) {
 reference=nondet_audio();AudioState native=reference;Regs r={0};r.cs=SOUND_SEG;r.ss=0x8000;r.sp=0x200;reply=nondet_u16();status=nondet_u16();__CPROVER_assume(status<=1);
 if(nondet_u8()&1) {
  int rc=c_ScheduleMusicFade(&r);AudioFadeRequest q=audio_music_schedule(&native);
  CHECK((q.action==AUDIO_FADE_REGISTER)==(event==3),"bit-zero schedule gate");
  CHECK(q.interval==119275,"fade interval clocks");if(event && !status) audio_music_registered(&native,reply);
  CHECK(rc==(event ? status : 0),"schedule peer status");
 } else {
  int rc=c_CancelMusicFade(&r);AudioFadeRequest q=audio_music_cancel(&native);
  CHECK((q.action==AUDIO_FADE_REMOVE)==(event==1),"bit-zero cancel gate");
  if(event) {CHECK(handle==q.handle,"unchecked stale handle retained");if(!status) audio_music_cancelled(&native);}
  CHECK(rc==(event ? status : 0),"cancel peer status");
 }
 CHECK(reference.fade.scheduled==native.fade.scheduled && reference.fade.timer_handle==native.fade.timer_handle,"timer completion owned words");return 0;}
'''
    elif a.mode=='timer-frame':
        code+='''int main(void) {
 AudioState s=nondet_audio();unsigned i=nondet_u16();__CPROVER_assume(i<sizeof(s));uint8_t *p=(uint8_t *)&s+i,*f=(uint8_t *)&s.fade.scheduled,*h=(uint8_t *)&s.fade.timer_handle;__CPROVER_assume((p<f || p>=f+2) && (p<h || p>=h+2));uint8_t old=*p;
 audio_music_schedule(&s);audio_music_cancel(&s);audio_music_registered(&s,nondet_u16());audio_music_cancelled(&s);CHECK(*p==old,"timer completion frame");return 0;}
'''
    elif a.mode=='timer-dependence':
        code+='''int main(void) {
 AudioState a=nondet_audio(),b=nondet_audio();b.fade.scheduled=a.fade.scheduled;b.fade.timer_handle=a.fade.timer_handle;AudioFadeRequest x=audio_music_schedule(&a),y=audio_music_schedule(&b);CHECK(x.action==y.action && x.interval==y.interval,"registration dependence");x=audio_music_cancel(&a);y=audio_music_cancel(&b);CHECK(x.action==y.action && x.handle==y.handle,"removal dependence");uint16_t h=nondet_u16();audio_music_registered(&a,h);audio_music_registered(&b,h);CHECK(a.fade.scheduled==b.fade.scheduled && a.fade.timer_handle==b.fade.timer_handle,"completion dependence");return 0;}
'''
    elif a.mode=='frame':
        code+='''int main(void) {
 AudioState state=nondet_audio();unsigned i=nondet_u16();__CPROVER_assume(i<sizeof(state));uint8_t *p=(uint8_t *)&state+i,*s=(uint8_t *)&state.fade.step_count;__CPROVER_assume(p<s || p>=s+2);uint8_t old=*p;
 audio_music_fade_step(&state);CHECK(*p==old,"every other fade-step state byte unchanged");return 0;}
'''
    else:
        code+='''int main(void) {
 AudioState a=nondet_audio(),b=nondet_audio();b.fade=a.fade;AudioFadeRequest x=audio_music_fade_step(&a),y=audio_music_fade_step(&b);
 CHECK(a.fade.step_count==b.fade.step_count && x.action==y.action,"fade read dependence");
 CHECK(x.handle==y.handle && x.volume==y.volume && x.remainder==y.remainder,"no omitted fade output input");return 0;}
'''
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_music.c',ROOT/'native/adlx_music.h',ROOT/'native/audio.h',ROOT/'c/adlib.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=15,timeout=a.timeout,extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
