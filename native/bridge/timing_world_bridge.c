#include "platform.h"
#include "timing_world_bridge.h"
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct TimingBinding {uint32_t address;size_t member;unsigned size,shift,kind,index;} TimingBinding;
static TimingBinding bindings[180];static unsigned count,active;
static uint16_t at[UGH_MEM_SIZE],open_words[32],previous[2];
static unsigned long long shared_reads,shared_writes;
static uint8_t seal=0xa5;
static unsigned audio_depth;
#if TIMING_TEST_FAULT == 1 || TIMING_TEST_FAULT == 3
static unsigned fault_used;
#endif
static void require(int yes){if(!yes){fputs("timing: invariant or sealed RAM violation\n",stderr);abort();}}
static uint16_t word_token(uint16_t word,unsigned position){
 if(!word)return TIMER_ZERO;
 if(word==T(ChainSavedTimerInterrupt))return TIMER_ENTRY_CHAIN;
 if(word==S(AdvanceMusicFade))return TIMER_ENTRY_FADE;
 if(word==S(TickAdlxPlayback))return TIMER_ENTRY_PLAYBACK;
 if(word==S(ClearSoundState))return TIMER_ENTRY_CLEAR;
 if(word==T(HandleTimerInterrupt))return TIMER_ENTRY_IRQ;
 if(word==TIMER_SEG)return TIMER_GROUP_TIMER;
 if(word==SOUND_SEG)return TIMER_GROUP_SOUND;
 return (uint16_t)(32+position);
}
static uint16_t token_word(uint16_t token,const uint16_t *words){
 switch(token){
 case TIMER_ZERO:return 0;
 case TIMER_ENTRY_CHAIN:return T(ChainSavedTimerInterrupt);
 case TIMER_ENTRY_FADE:return S(AdvanceMusicFade);
 case TIMER_ENTRY_PLAYBACK:return S(TickAdlxPlayback);
 case TIMER_ENTRY_CLEAR:return S(ClearSoundState);
 case TIMER_ENTRY_IRQ:return T(HandleTimerInterrupt);
 case TIMER_GROUP_TIMER:return TIMER_SEG;
 case TIMER_GROUP_SOUND:return SOUND_SEG;
 default:require(token>=32 && token<64);return words[token-32];
 }
}
static void bind_word(uint32_t address,size_t member,unsigned size,unsigned shift,unsigned kind,unsigned index){
 require(count<180);TimingBinding b={address,member,size,shift,kind,index};bindings[count]=b;
 for(unsigned j=0;j<2;j++){require(address+j<UGH_MEM_SIZE && !at[address+j]);at[address+j]=(uint16_t)(count+1);}count++;
}
#define WORLD_MEMBER(member) ((size_t)((uint8_t*)&native_timing_world()->member-(uint8_t*)native_timing_world()))
static void define_bindings(void){
 if(count)return;
 bind_word(lin(DATA_SEG,D(LastActiveTimerSlotOffset)),WORLD_MEMBER(last_offset),2,0,0,0);
 bind_word(lin(DATA_SEG,D(NextPitQuantumLow)),WORLD_MEMBER(timer.quantum),4,0,0,0);
 bind_word(lin(DATA_SEG,D(NextPitQuantumHigh)),WORLD_MEMBER(timer.quantum),4,16,0,0);
 bind_word(lin(DATA_SEG,D(EarliestTimerIntervalLow)),WORLD_MEMBER(timer.earliest),4,0,0,0);
 bind_word(lin(DATA_SEG,D(EarliestTimerIntervalHigh)),WORLD_MEMBER(timer.earliest),4,16,0,0);
 bind_word(lin(DATA_SEG,D(ProgrammedPitDivisor)),WORLD_MEMBER(timer.programmed_divisor),2,0,0,0);
 bind_word(lin(TIMER_SEG,T(TimerInterruptInstalled)),WORLD_MEMBER(timer.installed),2,0,0,0);
 bind_word(lin(DATA_SEG,D(PreviousInt08Offset)),0,2,0,2,0);
 bind_word(lin(DATA_SEG,D(PreviousInt08Segment)),0,2,0,2,1);
 for(unsigned i=0;i<TIMER_CAPACITY;i++){
  bind_word(lin(DATA_SEG,(uint16_t)(D(TimerIntervalLowBySlot)+i*2)),WORLD_MEMBER(timer.slots[i].interval),4,0,0,0);
  bind_word(lin(DATA_SEG,(uint16_t)(D(TimerIntervalHighBySlot)+i*2)),WORLD_MEMBER(timer.slots[i].interval),4,16,0,0);
  bind_word(lin(DATA_SEG,(uint16_t)(D(TimerRemainingLowBySlot)+i*2)),WORLD_MEMBER(timer.slots[i].remaining),4,0,0,0);
  bind_word(lin(DATA_SEG,(uint16_t)(D(TimerRemainingHighBySlot)+i*2)),WORLD_MEMBER(timer.slots[i].remaining),4,16,0,0);
  bind_word(lin(DATA_SEG,(uint16_t)(D(TimerCallbackDueBySlot)+i*2)),WORLD_MEMBER(timer.slots[i].due),2,0,0,0);
  bind_word(lin(DATA_SEG,(uint16_t)(D(TimerHandleBySlot)+i*2)),WORLD_MEMBER(timer.slots[i].handle),2,0,0,0);
  bind_word(lin(DATA_SEG,(uint16_t)(D(TimerSlotOffsetByHandle)+i*2)),WORLD_MEMBER(timer.by_handle[i]),2,0,0,0);
  bind_word(lin(DATA_SEG,(uint16_t)(D(TimerCallbackOffsetBySlot)+i*4)),WORLD_MEMBER(timer.slots[i].target.first),2,0,1,i*2);
  bind_word(lin(DATA_SEG,(uint16_t)(D(TimerCallbackSegmentBySlot)+i*4)),WORLD_MEMBER(timer.slots[i].target.second),2,0,1,i*2+1);
 }
 bind_word(lin(SOUND_SEG,S(AdlxTickCount)),WORLD_MEMBER(music.ticks),4,0,0,0);
 bind_word(lin(SOUND_SEG,S(AdlxTickHighWord)),WORLD_MEMBER(music.ticks),4,16,0,0);
 bind_word(lin(SOUND_SEG,S(MainAdlxTimeOrigin)),WORLD_MEMBER(music.origin),4,0,0,0);
 bind_word(lin(SOUND_SEG,S(MainAdlxTimeOriginHigh)),WORLD_MEMBER(music.origin),4,16,0,0);
 bind_word(lin(SOUND_SEG,S(MusicTicksPerUnit)),WORLD_MEMBER(music.rate),2,0,0,0);
 bind_word(lin(SOUND_SEG,S(MainAdlxPlaying)),WORLD_MEMBER(music.playing),2,0,0,0);
 bind_word(lin(SOUND_SEG,S(MainAdlxSectionLoopEnabled)),WORLD_MEMBER(music.section_loop),2,0,0,0);
}
static uint16_t get(const TimingBinding *b){
 if(b->kind==2)return previous[b->index];
 const uint8_t *p=(const uint8_t*)native_timing_world()+b->member;uint32_t value=0;
 if(b->size==2){uint16_t half;memcpy(&half,p,2);value=half;}else memcpy(&value,p,4);
 if(b->kind==1)return token_word((uint16_t)value,open_words);
 return (uint16_t)(value>>b->shift);
}
static void put(const TimingBinding *b,uint16_t value){
 NativeTimingWorld *world=native_timing_world();
 if(b->kind==2){previous[b->index]=value;world->lifetime.saved=(TimerExternalBinding){previous[0]==0x100 && previous[1]==0xf000?TIMER_EXTERNAL_BIOS:TIMER_EXTERNAL_OTHER,1};return;}
 uint8_t *p=(uint8_t*)world+b->member;
 if(b->kind==1){
  uint16_t token=word_token(value,b->index);
  /* Known identities serialize from immutable bindings; retain payload only
   * for genuinely open fragments, never a second copy of a known target. */
  open_words[b->index]=token>=32?value:0;value=token;
 }
 if(b->size==2)memcpy(p,&value,2);
 else {uint32_t full;memcpy(&full,p,4);full=(full&~(65535u<<b->shift))|((uint32_t)value<<b->shift);memcpy(p,&full,4);}
 world->timer.count=world->last_offset/2+1;
}
int timing_is_owned(uint32_t address){return active && address<UGH_MEM_SIZE && at[address];}
int timing_shared_read(uint32_t address,uint8_t *value){
 if(!timing_is_owned(address))return 0;
 const TimingBinding *b=&bindings[at[address]-1];*value=(uint8_t)(get(b)>>(8*(address-b->address)));shared_reads++;return 1;
}
int timing_shared_write(uint32_t address,uint8_t value){
 if(!timing_is_owned(address))return 0;
 const TimingBinding *b=&bindings[at[address]-1];unsigned shift=8*(address-b->address);
 uint16_t old=get(b);put(b,(uint16_t)((old&~(255u<<shift))|((uint16_t)value<<shift)));shared_writes++;return 1;
}
uint8_t audio_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t source=(size_t)window,base=(size_t)ugh_mem;
 if(source>=base && source-base+index<UGH_MEM_SIZE){
  uint8_t value;if(timing_shared_read((uint32_t)(source-base+index),&value))return value;
 }
 return window[index];
}
void timing_cold_import(uint8_t *memory){
 active=0;define_bindings();native_timing_reset();memset(open_words,0,sizeof open_words);memset(previous,0,sizeof previous);
 for(unsigned i=0;i<count;i++){const TimingBinding *b=&bindings[i];put(b,(uint16_t)(memory[b->address]|(uint16_t)memory[b->address+1]*256u));}
 for(unsigned i=0;i<count;i++){memory[bindings[i].address]=seal;memory[bindings[i].address+1]=seal;}active=1;
}
void timing_require_seal(const uint8_t *memory){
 if(!active)return;
 for(unsigned i=0;i<count;i++)require(memory[bindings[i].address]==seal && memory[bindings[i].address+1]==seal);
}
void timing_serialize(uint8_t *output){
 if(!active)return;
 /* A moved field can never silently fall back to a baseline/journal byte.
  * The independent canonical-view checker detects a missed publication even
  * when its legitimate value is still the cold value. */
 for(unsigned i=0;i<count;i++){output[bindings[i].address]=seal;output[bindings[i].address+1]=seal;}
 unsigned emitted=0;
 for(unsigned i=0;i<count;i++){const TimingBinding *b=&bindings[i];
#if TIMING_TEST_FAULT == 4
  if(b->member==WORLD_MEMBER(music.ticks) && b->kind==0)continue;
#endif
  uint16_t word=get(b);output[b->address]=(uint8_t)word;output[b->address+1]=(uint8_t)(word>>8);emitted+=2;}
 if(emitted!=count*2){fputs("timing: missed owned serialization\n",stderr);exit(88);}
}
unsigned timing_owned_bytes(void){return active?count*2:0;}
uint32_t timing_check_serialization(const uint8_t *observation){
 if(!active)return UINT32_MAX;
 for(unsigned i=0;i<count;i++){
  uint16_t word=get(&bindings[i]);uint32_t a=bindings[i].address;
  if(observation[a]!=(uint8_t)word)return a;
  if(observation[a+1]!=(uint8_t)(word>>8))return a+1;
 }
 return UINT32_MAX;
}
int timing_audio_callback_active(void){return audio_depth!=0;}
void timing_saved_words(uint16_t *offset,uint16_t *segment){*offset=previous[0];*segment=previous[1];}
void timing_save_binding(uint16_t offset,uint16_t segment){
 previous[0]=offset;previous[1]=segment;
 native_timing_world()->lifetime.saved=(TimerExternalBinding){offset==0x100 && segment==0xf000?TIMER_EXTERNAL_BIOS:TIMER_EXTERNAL_OTHER,1};
}
int timing_snapshot(TimerState *state,uint16_t *words){
 *state=native_timing_world()->timer;state->count=native_timing_world()->last_offset/2+1;
 for(unsigned i=0;i<16;i++){
  words[i*2]=token_word(state->slots[i].target.first,open_words);
  words[i*2+1]=token_word(state->slots[i].target.second,open_words);
  state->slots[i].target.first=word_token(words[i*2],i*2);state->slots[i].target.second=word_token(words[i*2+1],i*2+1);
 }
 return !(native_timing_world()->last_offset&1) && native_timing_world()->last_offset<=30;
}
void timing_commit(const TimerState *state,const uint16_t *words){
 uint16_t raw[32];for(unsigned i=0;i<16;i++){raw[i*2]=token_word(state->slots[i].target.first,words);raw[i*2+1]=token_word(state->slots[i].target.second,words);}
 /* The old publish cuts do not write the installed word. Lifetime entries
  * write it explicitly through their live code view; a foreign-CS view must
  * not acquire a second, unintended write to the canonical timer flag. */
 uint16_t installed=native_timing_world()->timer.installed;
 native_timing_world()->timer=*state;native_timing_world()->timer.installed=installed;
 native_timing_world()->last_offset=(uint16_t)((state->count-1)*2);
 for(unsigned i=0;i<16;i++){
  TimerTarget target={word_token(raw[i*2],i*2),word_token(raw[i*2+1],i*2+1)};
  open_words[i*2]=target.first>=32?raw[i*2]:0;
  open_words[i*2+1]=target.second>=32?raw[i*2+1]:0;
  native_timing_world()->timer.slots[i].target=target;
 }
}
int timing_deliver(TimerCallback callback,Regs *r){
 uint16_t saved=r->cs;int status;
#if TIMING_TEST_FAULT == 3
 uint32_t before=native_timing_world()->music.ticks;
#endif
 audio_depth++;
 r->cs=callback==TIMER_BIOS_CHAIN || callback==TIMER_FIXTURE_IRQ?TIMER_SEG:SOUND_SEG;
 switch(callback){
 case TIMER_BIOS_CHAIN:status=c_ChainSavedTimerInterrupt(r);break;
 case TIMER_MUSIC_FADE:status=c_AdvanceMusicFade(r);break;
 case TIMER_ADLX_PLAYBACK:
#if TIMING_TEST_FAULT == 1
  if(!fault_used){fault_used=1;status=UGH_OK;}else status=c_TickAdlxPlayback(r);
#else
  status=c_TickAdlxPlayback(r);
#endif
  break;
 case TIMER_FIXTURE_CLEAR:status=c_ClearSoundState(r);break;
 case TIMER_FIXTURE_IRQ:status=c_HandleTimerInterrupt(r);break;
 default:status=UGH_BAD_CALLBACK;break;
 }
 audio_depth--;
#if TIMING_TEST_FAULT == 3
 if(callback==TIMER_ADLX_PLAYBACK && !fault_used){native_timing_world()->music.ticks=before;fault_used=1;}
#endif
 if(status!=UGH_CONTROL_TRANSFER && status!=UGH_DOS_EXIT)r->cs=saved;
 return status;
}
