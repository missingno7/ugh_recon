"""Actual C start/stop orchestration versus native requests under peer contracts.

Output profile leaves arithmetic and original control intact. Timer delivery
clears the word on the second poll; all API results and selected state changes
are shared arbitrary replies. Frame/dependence cover one admitted native resume.
"""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_music_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependence']);p.add_argument('--negative',action='store_true');p.add_argument('--timeout',type=int,default=180);a=p.parse_args();assert 0<a.timeout<=600
    folder=OUT/f'proof-flow-{a.mode}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
    native=(ROOT/'native/adlx_music.c').read_text();literal=(ROOT/'c/sound_api.c').read_text()
    code='''#include "platform.h"
#include "adlx_music.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];AudioState nondet_audio(void);AudioMusicWork nondet_work(void);uint16_t nondet_u16(void);uint8_t nondet_u8(void);
static AudioState reference;static uint8_t stack[1024],resource;
static uint16_t devices,replies[12],changes[12][6];static unsigned count,polls;
typedef struct Probe {uint16_t action,channel,volume,resource_index,playing,current,track,start,target,step,duration,scheduled;uint32_t origin,ticks;} Probe;
static Probe expected[12];
static Probe probe(const AudioState *s,AudioMusicRequest q) {
 Probe p={(uint16_t)q.action,q.channel,q.volume,q.action==AUDIO_MUSIC_LOAD ? q.resource.index : 0,s->playing,s->current_channel,s->track_volume,s->fade.start_volume,s->fade.target_volume,s->fade.step_count,s->fade.duration,s->fade.scheduled,s->time_origin,s->ticks};return p;
}
static void contract(AudioState *s,unsigned i) {
 s->playing=changes[i][0];s->current_channel=changes[i][1];s->track_volume=changes[i][2];s->ticks=(uint32_t)changes[i][3]*65536u+changes[i][4];s->fade.scheduled=changes[i][5];
}
uint8_t ugh_read(uint32_t address) {
 unsigned p=address-(unsigned)SOUND_SEG*16u;uint16_t v;
 if((p&65534u)==S(SoundDeviceBits)) v=devices;
 else if((p&65534u)==S(MainAdlxPlaying)) v=reference.playing;
 else if((p&65534u)==S(CurrentAdlxSlot)) v=reference.current_channel;
 else if((p&65534u)==S(MusicTrackVolume)) v=reference.track_volume;
 else if((p&65534u)==S(MusicFadeStartVolume)) v=reference.fade.start_volume;
 else if((p&65534u)==S(MusicFadeTargetVolume)) v=reference.fade.target_volume;
 else if((p&65534u)==S(MusicFadeStep)) v=reference.fade.step_count;
 else if((p&65534u)==S(MusicFadeDuration)) v=reference.fade.duration;
 else if((p&65534u)==S(MusicFadeScheduled)) v=reference.fade.scheduled;
 else if(p>=S(AdlxTickCount) && p<S(AdlxTickCount)+4) return (uint8_t)(reference.ticks>>(8*(p-S(AdlxTickCount))));
 else {CHECK(address>=0x80000 && address<0x80400,"flow stack read");return stack[address-0x80000];}
 return (uint8_t)(v>>(8*(p&1u)));
}
void ugh_write(uint32_t address,uint8_t value) {
 unsigned p=address-(unsigned)SOUND_SEG*16u;uint16_t *v=0;
 if((p&65534u)==S(MainAdlxPlaying)) v=&reference.playing;
 else if((p&65534u)==S(CurrentAdlxSlot)) v=&reference.current_channel;
 else if((p&65534u)==S(MusicTrackVolume)) v=&reference.track_volume;
 else if((p&65534u)==S(MusicFadeStartVolume)) v=&reference.fade.start_volume;
 else if((p&65534u)==S(MusicFadeTargetVolume)) v=&reference.fade.target_volume;
 else if((p&65534u)==S(MusicFadeStep)) v=&reference.fade.step_count;
 else if((p&65534u)==S(MusicFadeDuration)) v=&reference.fade.duration;
 else if(p>=S(MainAdlxTimeOrigin) && p<S(MainAdlxTimeOrigin)+4) {unsigned shift=8*(p-S(MainAdlxTimeOrigin));reference.time_origin=(reference.time_origin&~((uint32_t)255<<shift))|((uint32_t)value<<shift);return;}
 else {CHECK(address>=0x80000 && address<0x80400,"flow stack write");stack[address-0x80000]=value;return;}
 unsigned shift=8*(p&1u);*v=(uint16_t)((*v&~(255u<<shift))|((unsigned)value<<shift));
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {
 AudioMusicRequest q={AUDIO_MUSIC_DONE,{&resource,0},0,0};
 if(bank==SOUND_SEG) {
  if(target==S(CancelMusicFade)) q.action=AUDIO_MUSIC_CANCEL;
  else if(target==S(ScheduleMusicFade)) q.action=AUDIO_MUSIC_SCHEDULE;
  else {CHECK(target==S(SilenceAdlibOperators),"flow sound peer set");q.action=AUDIO_MUSIC_SILENCE;}
 } else {
  CHECK(bank==UGH_SEG_C,"flow C peer bank");
  if(target==UGH_O_C_LoadAdlibTrackData) {q.action=AUDIO_MUSIC_LOAD;q.channel=arg16(r,0);CHECK(arg16(r,4)==0x6000 && !arg16(r,6),"resource bank and repeat args");q.resource.index=arg16(r,2);}
  else if(target==UGH_O_C_StartAdlibTrackChannel) {q.action=AUDIO_MUSIC_START_CHANNEL;q.channel=arg16(r,0);q.volume=arg16(r,2);}
  else if(target==UGH_O_C_SetMusicTrackVolume) {q.action=AUDIO_MUSIC_SET_VOLUME;q.volume=arg16(r,0);}
  else {CHECK(target==UGH_O_C_StopAdlibTrackChannel,"flow C peer set");q.action=AUDIO_MUSIC_STOP_CHANNEL;q.channel=arg16(r,0);}
 }
 CHECK(count<12,"flow journal bound");expected[count]=probe(&reference,q);r->ax=replies[count];contract(&reference,count++);return 0;
}
int platform_service_point_at(ServicePoint kind,uint16_t bank,uint16_t target,Regs *r) {
 (void)r;CHECK(kind==SERVICE_TIMER_WAIT && bank==UGH_SEG_C && target==UGH_O_C_StopMusicTrack+0x95,"flow wait site");
 AudioMusicRequest q={AUDIO_MUSIC_TIMER_WAIT,{&resource,0},0,0};CHECK(count<12,"flow wait journal bound");expected[count++]=probe(&reference,q);
 reference.fade.scheduled=++polls==2 ? 0 : 2;return 0;
}
'''
    code+=literal[literal.index('#define CSEG'):literal.index('/* Word device mask;')]
    code+=function(literal,'c_StartMusicTrack')+function(literal,'c_StopMusicTrack')
    for name in ['audio_music_begin','audio_music_request','audio_music_wait','audio_music_next']:
        f=function(native,name)
        if a.negative and name=='audio_music_next':f=f.replace('if(state->fade.scheduled) return audio_music_wait(work);','if(state->fade.scheduled&1u) return audio_music_wait(work);')
        code+=f
    if a.mode=='outputs':
        code+='''int main(void) {
 reference=nondet_audio();AudioState native=reference;devices=nondet_u16();uint16_t duration=nondet_u16(),volume=nondet_u16(),offset=nondet_u16();AudioMusicOperation operation=nondet_u8()&1 ? AUDIO_MUSIC_START : AUDIO_MUSIC_STOP;
 for(unsigned i=0;i<12;i++) {replies[i]=nondet_u16();for(unsigned j=0;j<6;j++) changes[i][j]=nondet_u16();}
 Regs r={0};r.cs=UGH_SEG_C;r.ss=0x8000;r.sp=0x200;r.flags=0x202;
 wr16(r.ss,0x204,operation==AUDIO_MUSIC_START ? offset : duration);wr16(r.ss,0x206,0x6000);wr16(r.ss,0x208,duration);wr16(r.ss,0x20a,volume);
 if(operation==AUDIO_MUSIC_START) c_StartMusicTrack(&r);else c_StopMusicTrack(&r);
 AudioCursor source={&resource,offset};AudioMusicWork work=audio_music_begin(operation,source,duration,volume,devices);unsigned actual=0,delivered=0;uint16_t reply=65535;
 for(unsigned iteration=0;iteration<13;iteration++) {
  AudioMusicRequest q=audio_music_next(&native,&work,reply);if(q.action==AUDIO_MUSIC_DONE) break;
  CHECK(actual<count,"same service count prefix");Probe x=probe(&native,q),y=expected[actual];
  CHECK(x.action==y.action && x.channel==y.channel && x.volume==y.volume && x.resource_index==y.resource_index,"ordered peer request arguments");
  if(q.action==AUDIO_MUSIC_LOAD) CHECK(q.resource.window==source.window,"resource identity passed to loader");
  CHECK(x.playing==y.playing && x.current==y.current && x.track==y.track && x.start==y.start && x.target==y.target && x.step==y.step && x.duration==y.duration && x.scheduled==y.scheduled && x.origin==y.origin && x.ticks==y.ticks,"state visible at each service boundary");
  if(q.action==AUDIO_MUSIC_TIMER_WAIT) native.fade.scheduled=++delivered==2 ? 0 : 2;
  else {reply=replies[actual];contract(&native,actual);}actual++;
 }
 CHECK(work.stage==100 && actual==count && r.ax==work.result,"final result and service count");
 CHECK(native.playing==reference.playing && native.current_channel==reference.current_channel && native.track_volume==reference.track_volume && native.time_origin==reference.time_origin,"final music policy");
 CHECK(native.fade.start_volume==reference.fade.start_volume && native.fade.target_volume==reference.fade.target_volume && native.fade.step_count==reference.fade.step_count && native.fade.duration==reference.fade.duration,"final fade setup");return 0;}
'''
    else:
        code+='''static int within(uint8_t *p,void *f,unsigned n) {return p>=(uint8_t *)f && p<(uint8_t *)f+n;}
int main(void) {
 AudioState state=nondet_audio();AudioMusicWork work=nondet_work();work.operation=nondet_u8()&1 ? AUDIO_MUSIC_START : AUDIO_MUSIC_STOP;__CPROVER_assume(work.stage<=6 || work.stage==100);uint16_t reply=nondet_u16();
'''
        if a.mode=='frame':
            code+='''unsigned i=nondet_u16();__CPROVER_assume(i<sizeof(state));uint8_t *p=(uint8_t *)&state+i,old=*p;
 __CPROVER_assume(!within(p,&state.playing,2) && !within(p,&state.current_channel,2) && !within(p,&state.track_volume,2) && !within(p,&state.time_origin,4) && !within(p,&state.fade.start_volume,2) && !within(p,&state.fade.target_volume,2) && !within(p,&state.fade.step_count,2) && !within(p,&state.fade.duration,2));
 audio_music_next(&state,&work,reply);CHECK(*p==old,"all other resume state bytes unchanged");
'''
        else:
            code+='''AudioState other=nondet_audio();other.playing=state.playing;other.current_channel=state.current_channel;other.track_volume=state.track_volume;other.time_origin=state.time_origin;other.ticks=state.ticks;other.fade=state.fade;AudioMusicWork second=work;
 AudioMusicRequest x=audio_music_next(&state,&work,reply),y=audio_music_next(&other,&second,reply);
 CHECK(x.action==y.action && x.channel==y.channel && x.volume==y.volume && work.stage==second.stage && work.result==second.result && work.channel==second.channel && work.wait_budget==second.wait_budget,"resume read dependence");
 CHECK(state.playing==other.playing && state.current_channel==other.current_channel && state.track_volume==other.track_volume && state.time_origin==other.time_origin && state.fade.start_volume==other.fade.start_volume && state.fade.target_volume==other.fade.target_volume && state.fade.step_count==other.fade.step_count && state.fade.duration==other.fade.duration,"no omitted policy input");
'''
        code+='return 0;}\n'
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_music.c',ROOT/'native/adlx_music.h',ROOT/'native/audio.h',ROOT/'c/sound_api.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=15,timeout=a.timeout,extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
