#include "platform.h"
#include "audio_world_bridge.h"
#include <string.h>
#define MEMBER(member) ((size_t)((uint8_t*)&native_timing_world()->audio.member-(uint8_t*)native_timing_world()))
void audio_world_snapshot(AudioState *view){
 NativeTimingWorld *world=native_timing_world();
 audio_world_borrow(&world->audio,view,world->music.ticks,world->music.origin,world->music.rate,world->music.playing,world->music.section_loop);
}
static unsigned peer_depth;
#if AUDIO_TEST_FAULT == 1 || AUDIO_TEST_FAULT == 3
static unsigned fault_used;
#endif
int audio_peer_active(void){return peer_depth!=0;}
void audio_world_bindings(void){
 for(unsigned i=0;i<AUDIO_CHANNEL_COUNT;i++){
  uint16_t base=(uint16_t)(S(AudioChannelStates)+42u*i);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+0)),MEMBER(channels[i].age),4,0);
 timing_bind_audio_high(lin(SOUND_SEG,(uint16_t)(base+2)),MEMBER(channels[i].age));
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+4)),MEMBER(channels[i].repeats),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+6)),MEMBER(channels[i].start.index),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+8)),MEMBER(channels[i].start.window),8,3);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+10)),MEMBER(channels[i].length),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+12)),MEMBER(channels[i].sample_mode),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+14)),MEMBER(channels[i].sample_rate),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+16)),MEMBER(channels[i].cursor.index),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+18)),MEMBER(channels[i].cursor.window),8,3);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+20)),MEMBER(channels[i].sample_half_length),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+22)),MEMBER(channels[i].reserved_word),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+24)),MEMBER(channels[i].sample_selector),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+26)),MEMBER(channels[i].sample_accumulator),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+28)),MEMBER(channels[i].volume),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+30)),MEMBER(channels[i].deadline),4,0);
 timing_bind_audio_high(lin(SOUND_SEG,(uint16_t)(base+32)),MEMBER(channels[i].deadline));
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+34)),MEMBER(channels[i].voice_count),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+36)),MEMBER(channels[i].first_voice),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+38)),MEMBER(channels[i].step_q8),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+40)),MEMBER(channels[i].control),2,0);
 }
 for(unsigned i=0;i<AUDIO_VOICE_COUNT;i++){
  for(unsigned j=0;j<12;j++){
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(AdlibVoiceStates)+20u*i+j)),MEMBER(live[i].instrument[j]),1,0);
  }
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(AdlibVoiceStates)+20u*i+12)),MEMBER(live[i].volume),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(AdlibVoiceStates)+20u*i+14)),MEMBER(live[i].gain),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(AdlibVoiceStates)+20u*i+16)),MEMBER(live[i].owner),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(AdlibVoiceStates)+20u*i+18)),MEMBER(live[i].frequency),2,0);
  for(unsigned j=0;j<12;j++){
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(SavedAdlibVoiceStates)+20u*i+j)),MEMBER(displaced[i].instrument[j]),1,0);
  }
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(SavedAdlibVoiceStates)+20u*i+12)),MEMBER(displaced[i].volume),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(SavedAdlibVoiceStates)+20u*i+14)),MEMBER(displaced[i].gain),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(SavedAdlibVoiceStates)+20u*i+16)),MEMBER(displaced[i].owner),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(SavedAdlibVoiceStates)+20u*i+18)),MEMBER(displaced[i].frequency),2,0);
  for(unsigned j=0;j<12;j++){
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(ScannedAdlibVoiceStates)+20u*i+j)),MEMBER(scanned[i].instrument[j]),1,0);
  }
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(ScannedAdlibVoiceStates)+20u*i+12)),MEMBER(scanned[i].volume),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(ScannedAdlibVoiceStates)+20u*i+14)),MEMBER(scanned[i].gain),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(ScannedAdlibVoiceStates)+20u*i+16)),MEMBER(scanned[i].owner),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(ScannedAdlibVoiceStates)+20u*i+18)),MEMBER(scanned[i].frequency),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(AdlibOperatorOffsets)+i)),MEMBER(operator_index[i]),1,0);
 }
 timing_bind_audio(lin(SOUND_SEG,S(AdlxPlaybackGuard)),MEMBER(playback_guard),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(ScannedMusicClockTicks)),MEMBER(scanned_ticks),4,0);
 timing_bind_audio_high(lin(SOUND_SEG,(uint16_t)(S(ScannedMusicClockTicks)+2)),MEMBER(scanned_ticks));
 timing_bind_audio(lin(SOUND_SEG,S(FirstScannedEvent)),MEMBER(section_start.index),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(MainAdlxSectionEnd)),MEMBER(section_end.index),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(AdlxTimerPeriod)),MEMBER(timer_period),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(AdlxPlaybackTimerHandle)),MEMBER(playback_timer_handle),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(ReservedAdlibChannelCount)),MEMBER(reserved_voices),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(CurrentAdlxSlot)),MEMBER(current_channel),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(MusicTrackVolume)),MEMBER(track_volume),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(FirstScannedEvent)+2)),MEMBER(section_start.window),8,3);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(MainAdlxSectionEnd)+2)),MEMBER(section_end.window),8,3);
 timing_bind_audio(lin(SOUND_SEG,S(MusicFadeStep)),MEMBER(fade.step_count),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(MusicFadeDuration)),MEMBER(fade.duration),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(MusicFadeStartVolume)),MEMBER(fade.start_volume),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(MusicFadeTargetVolume)),MEMBER(fade.target_volume),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(MusicFadeScheduled)),MEMBER(fade.scheduled),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(MusicFadeTimerHandle)),MEMBER(fade.timer_handle),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(SampleMixerBusy)),MEMBER(reset.mixer_busy),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(DspBasePort)),MEMBER(reset.dsp_port),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(DspInterruptVector)),MEMBER(reset.interrupt_vector),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(SoundDeviceBits)),MEMBER(reset.devices),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(ActiveSampleVoiceCount)),MEMBER(reset.sample_count),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(ActiveSampleVoiceMask)),MEMBER(reset.sample_mask),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(SoundBankBase)),MEMBER(reset.bank.index),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(SoundBankBase)+2)),MEMBER(reset.bank.window),8,3);
 timing_bind_audio(lin(SOUND_SEG,S(AdlibInstrumentMap)),MEMBER(reset.instrument_map.index),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(AdlibInstrumentMap)+2)),MEMBER(reset.instrument_map.window),8,3);
 timing_bind_audio(lin(SOUND_SEG,S(SoundBankLength)),MEMBER(reset.bank_length),4,0);
 timing_bind_audio_high(lin(SOUND_SEG,(uint16_t)(S(SoundBankLength)+2)),MEMBER(reset.bank_length));
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(ActiveSampleVoiceMask)+2)),MEMBER(reset.spare[0]),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(CurrentAdlxSlot)+2)),MEMBER(reset.spare[1]),2,0);
 timing_bind_audio_external(lin(SOUND_SEG,S(PreviousCalibrationTimerVector)),0);
 timing_bind_audio_external(lin(SOUND_SEG,S(PreviousCalibrationTimerSegment)),1);
 timing_bind_audio_external(lin(SOUND_SEG,S(PreviousDspVectorOffset)),2);
 timing_bind_audio_external(lin(SOUND_SEG,S(PreviousDspVectorSegment)),3);
 timing_bind_audio(lin(SOUND_SEG,S(CurrentAdlxRecordOffset)),MEMBER(driver.current_record),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(SampleMixPairsRemaining)),MEMBER(driver.pairs_remaining),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(SampleMixFirstSum)),MEMBER(driver.first_sum),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(SampleMixSecondSum)),MEMBER(driver.second_sum),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(SoundIoDelayMultiplier)),MEMBER(driver.delay_multiplier),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(CalibrationLoopRemainder)),MEMBER(driver.calibration_remainder),2,0);
 timing_bind_audio(lin(SOUND_SEG,S(AdlibInitAttempted)),MEMBER(driver.attempted),1,0);
 timing_bind_audio(lin(SOUND_SEG,S(DspIrqBusy)),MEMBER(driver.interrupt_busy),1,0);
 timing_bind_audio(lin(SOUND_SEG,S(DspProbeIrqSeen)),MEMBER(driver.probe_seen),1,0);
 timing_bind_audio(lin(SOUND_SEG,S(DmaMixBufferSelect)),MEMBER(driver.selection),1,0);
 timing_bind_audio(lin(SOUND_SEG,S(DspPicIrqMask)),MEMBER(driver.interrupt_mask),1,0);
 timing_bind_audio(lin(UGH_S_C_SoundSystemInitialized,UGH_O_C_SoundSystemInitialized),MEMBER(driver.initialized),2,0);
 timing_bind_audio(lin(UGH_S_C_SoundSystemShutdown,UGH_O_C_SoundSystemShutdown),MEMBER(driver.shutdown),2,0);
 for(unsigned i=0;i<2;i++){
  uint16_t base=(uint16_t)(S(DmaMixBufferOneCount)+i*0x40a);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+0)),MEMBER(dma[i].count),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+2)),MEMBER(dma[i].page),1,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+3)),MEMBER(dma[i].retained_high),1,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+4)),MEMBER(dma[i].address),2,0);
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+6)),MEMBER(dma[i].offset),2,0);
  for(unsigned j=0;j<1024;j++){
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+8+j)),MEMBER(dma[i].samples[j]),1,0);
  }
  for(unsigned j=0;j<2;j++){
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(base+1032+j)),MEMBER(dma[i].retained[j]),1,0);
  }
 }
 for(unsigned j=0;j<sizeof native_timing_world()->audio.fallback_reservation;j++){
  timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(DmaMixBufferOneCount)+2u*0x40a+j)),MEMBER(fallback_reservation[j]),1,0);
 }
 for(unsigned j=0;j<2;j++){
 timing_bind_audio(lin(SOUND_SEG,(uint16_t)(S(DmaMixBufferOneCount)+3u*0x40a+j)),MEMBER(retained_dma_tail[j]),1,0);
 }
}

int audio_peer_deliver(AudioPeerRole role,uint16_t binding,Regs *registers){
 uint16_t saved=registers->cs;int result;
#if AUDIO_TEST_FAULT == 1
 if(role==AUDIO_PEER_RunMainAdlxEvents && !fault_used){fault_used=1;return UGH_OK;}
#endif
#if AUDIO_TEST_FAULT == 3
 uint16_t before=native_timing_world()->audio.channels[12].cursor.index;
#endif
 peer_depth++;
 switch(role){
 case AUDIO_PEER_AdvanceGuardedSoundClock:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_AdvanceGuardedSoundClock(registers);break;
 case AUDIO_PEER_AdvanceMusicFade:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_AdvanceMusicFade(registers);break;
 case AUDIO_PEER_ApplyScannedMusicEvents:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_ApplyScannedMusicEvents(registers);break;
 case AUDIO_PEER_BeginSoundDelayMeasurement:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_BeginSoundDelayMeasurement(registers);break;
 case AUDIO_PEER_CalibrateSoundDelay:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_CalibrateSoundDelay(registers);break;
 case AUDIO_PEER_CancelMusicFade:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_CancelMusicFade(registers);break;
 case AUDIO_PEER_ChainSavedTimerInterrupt:if(binding!=TIMER_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=TIMER_SEG;result=c_ChainSavedTimerInterrupt(registers);break;
 case AUDIO_PEER_ClearSoundState:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_ClearSoundState(registers);break;
 case AUDIO_PEER_DelaySoundIo:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_DelaySoundIo(registers);break;
 case AUDIO_PEER_DisableMusicSectionLoop:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_DisableMusicSectionLoop(registers);break;
 case AUDIO_PEER_FinishSoundDelayMeasurement:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_FinishSoundDelayMeasurement(registers);break;
 case AUDIO_PEER_GetElapsedMusicTime:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_GetElapsedMusicTime(registers);break;
 case AUDIO_PEER_GetMusicTrackDuration:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_GetMusicTrackDuration(registers);break;
 case AUDIO_PEER_HandleDspProbeInterrupt:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleDspProbeInterrupt(registers);break;
 case AUDIO_PEER_HandleEffectAdlxControl:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleEffectAdlxControl(registers);break;
 case AUDIO_PEER_HandleEffectAdlxFrequency:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleEffectAdlxFrequency(registers);break;
 case AUDIO_PEER_HandleEffectAdlxGain:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleEffectAdlxGain(registers);break;
 case AUDIO_PEER_HandleEffectAdlxInstrument:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleEffectAdlxInstrument(registers);break;
 case AUDIO_PEER_HandleEffectAdlxKeyOff:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleEffectAdlxKeyOff(registers);break;
 case AUDIO_PEER_HandleEffectAdlxLongWait:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleEffectAdlxLongWait(registers);break;
 case AUDIO_PEER_HandleEffectAdlxNoOp:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleEffectAdlxNoOp(registers);break;
 case AUDIO_PEER_HandleEffectAdlxShortWait:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleEffectAdlxShortWait(registers);break;
 case AUDIO_PEER_HandleEffectAdlxTimerPeriod:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleEffectAdlxTimerPeriod(registers);break;
 case AUDIO_PEER_HandleMainAdlxControl:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleMainAdlxControl(registers);break;
 case AUDIO_PEER_HandleMainAdlxFrequency:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleMainAdlxFrequency(registers);break;
 case AUDIO_PEER_HandleMainAdlxGain:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleMainAdlxGain(registers);break;
 case AUDIO_PEER_HandleMainAdlxInstrument:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleMainAdlxInstrument(registers);break;
 case AUDIO_PEER_HandleMainAdlxKeyOff:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleMainAdlxKeyOff(registers);break;
 case AUDIO_PEER_HandleMainAdlxLongWait:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleMainAdlxLongWait(registers);break;
 case AUDIO_PEER_HandleMainAdlxNoOp:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleMainAdlxNoOp(registers);break;
 case AUDIO_PEER_HandleMainAdlxShortWait:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleMainAdlxShortWait(registers);break;
 case AUDIO_PEER_HandleMainAdlxTimerPeriod:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleMainAdlxTimerPeriod(registers);break;
 case AUDIO_PEER_HandleSampleDmaInterrupt:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_HandleSampleDmaInterrupt(registers);break;
 case AUDIO_PEER_HandleTimerInterrupt:if(binding!=TIMER_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=TIMER_SEG;result=c_HandleTimerInterrupt(registers);break;
 case AUDIO_PEER_InitializeAdlibPlayback:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_InitializeAdlibPlayback(registers);break;
 case AUDIO_PEER_InitializeDspPlayback:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_InitializeDspPlayback(registers);break;
 case AUDIO_PEER_InitializeSoundSystem:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_InitializeSoundSystem(registers);break;
 case AUDIO_PEER_InstallTimerInterrupt:if(binding!=TIMER_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=TIMER_SEG;result=c_InstallTimerInterrupt(registers);break;
 case AUDIO_PEER_KeyOffAdlibChannel:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_KeyOffAdlibChannel(registers);break;
 case AUDIO_PEER_LoadAdlibChannel:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_LoadAdlibChannel(registers);break;
 case AUDIO_PEER_LoadAdlibInstrument:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_LoadAdlibInstrument(registers);break;
 case AUDIO_PEER_LoadAdlibTrackData:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_LoadAdlibTrackData(registers);break;
 case AUDIO_PEER_LoadBankSoundByIndex:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_LoadBankSoundByIndex(registers);break;
 case AUDIO_PEER_LoadIffSample:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_LoadIffSample(registers);break;
 case AUDIO_PEER_LoadSoundBankResource:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_LoadSoundBankResource(registers);break;
 case AUDIO_PEER_LocateDmaMixBuffers:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_LocateDmaMixBuffers(registers);break;
 case AUDIO_PEER_MixSampleVoicePairs:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_MixSampleVoicePairs(registers);break;
 case AUDIO_PEER_PlayAdlibEffect:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_PlayAdlibEffect(registers);break;
 case AUDIO_PEER_PrimeSampleDmaPlayback:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_PrimeSampleDmaPlayback(registers);break;
 case AUDIO_PEER_ProbeSoundBlasterDmaIrq:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_ProbeSoundBlasterDmaIrq(registers);break;
 case AUDIO_PEER_RegisterTimerCallback:if(binding!=TIMER_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=TIMER_SEG;result=c_RegisterTimerCallback(registers);break;
 case AUDIO_PEER_RegisterTimerCallbackFromStack:if(binding!=TIMER_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=TIMER_SEG;result=c_RegisterTimerCallbackFromStack(registers);break;
 case AUDIO_PEER_RemoveTimerCallback:if(binding!=TIMER_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=TIMER_SEG;result=c_RemoveTimerCallback(registers);break;
 case AUDIO_PEER_RemoveTimerCallbackFromStack:if(binding!=TIMER_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=TIMER_SEG;result=c_RemoveTimerCallbackFromStack(registers);break;
 case AUDIO_PEER_ResetAdlibTrackChannelCursor:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_ResetAdlibTrackChannelCursor(registers);break;
 case AUDIO_PEER_ResetSampleVoiceCursor:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_ResetSampleVoiceCursor(registers);break;
 case AUDIO_PEER_ResetSoundBlasterDsp:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_ResetSoundBlasterDsp(registers);break;
 case AUDIO_PEER_RestoreAdlibVoiceAllocation:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_RestoreAdlibVoiceAllocation(registers);break;
 case AUDIO_PEER_RestoreTimerInterrupt:if(binding!=TIMER_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=TIMER_SEG;result=c_RestoreTimerInterrupt(registers);break;
 case AUDIO_PEER_RunEffectAdlxEvents:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_RunEffectAdlxEvents(registers);break;
 case AUDIO_PEER_RunMainAdlxEvents:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_RunMainAdlxEvents(registers);break;
 case AUDIO_PEER_ScanMusicEvents:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_ScanMusicEvents(registers);break;
 case AUDIO_PEER_ScheduleMusicFade:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_ScheduleMusicFade(registers);break;
 case AUDIO_PEER_SetAdlibChannelGain:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_SetAdlibChannelGain(registers);break;
 case AUDIO_PEER_SetAdlibChannelVolume:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_SetAdlibChannelVolume(registers);break;
 case AUDIO_PEER_SetAdlibFrequency:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_SetAdlibFrequency(registers);break;
 case AUDIO_PEER_SetDspSampleRate:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_SetDspSampleRate(registers);break;
 case AUDIO_PEER_SetMusicTrackVolume:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_SetMusicTrackVolume(registers);break;
 case AUDIO_PEER_SetTimerCallbackInterval:if(binding!=TIMER_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=TIMER_SEG;result=c_SetTimerCallbackInterval(registers);break;
 case AUDIO_PEER_ShutdownAdlibPlayback:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_ShutdownAdlibPlayback(registers);break;
 case AUDIO_PEER_ShutdownDspPlayback:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_ShutdownDspPlayback(registers);break;
 case AUDIO_PEER_ShutdownSoundSystem:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_ShutdownSoundSystem(registers);break;
 case AUDIO_PEER_SilenceAdlibOperators:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_SilenceAdlibOperators(registers);break;
 case AUDIO_PEER_StartAdlibTrackChannel:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_StartAdlibTrackChannel(registers);break;
 case AUDIO_PEER_StartDmaSampleBlock:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_StartDmaSampleBlock(registers);break;
 case AUDIO_PEER_StartMusicTrack:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_StartMusicTrack(registers);break;
 case AUDIO_PEER_StartSoundOutputs:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_StartSoundOutputs(registers);break;
 case AUDIO_PEER_StopAdlibTrackChannel:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_StopAdlibTrackChannel(registers);break;
 case AUDIO_PEER_StopMusicTrack:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_StopMusicTrack(registers);break;
 case AUDIO_PEER_StopSoundChannel:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_StopSoundChannel(registers);break;
 case AUDIO_PEER_SwapDwordByteOrder:if(binding!=UGH_SEG_C){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=UGH_SEG_C;result=c_SwapDwordByteOrder(registers);break;
 case AUDIO_PEER_TickAdlxPlayback:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_TickAdlxPlayback(registers);break;
 case AUDIO_PEER_WriteAdlibRegister:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_WriteAdlibRegister(registers);break;
 case AUDIO_PEER_WriteSoundBlasterDsp:if(binding!=SOUND_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=SOUND_SEG;result=c_WriteSoundBlasterDsp(registers);break;
 case AUDIO_PEER_loc_032F:if(binding!=TIMER_SEG){peer_depth--;return UGH_BAD_CALLBACK;}registers->cs=TIMER_SEG;result=c_loc_032F(registers);break;
 default:peer_depth--;return UGH_BAD_CALLBACK;
 }
 peer_depth--;
#if AUDIO_TEST_FAULT == 3
 if(role==AUDIO_PEER_RunMainAdlxEvents && !fault_used){native_timing_world()->audio.channels[12].cursor.index=before;fault_used=1;}
#endif
 if(result!=UGH_CONTROL_TRANSFER && result!=UGH_DOS_EXIT)registers->cs=saved;
 return result;
}

/* Provider coordinates belong to explicit service state, not game pointers.
 * Native code retains an opaque binding identity and role. */
static uint16_t external_words[4];
uint16_t audio_external_read(unsigned index){return external_words[index];}
void audio_external_write(unsigned index,uint16_t value){
 external_words[index]=value;unsigned first=index&~1u;
 AudioExternalBinding binding={external_words[first]==0x100 && external_words[first+1]==0xf000?AUDIO_EXTERNAL_BIOS:AUDIO_EXTERNAL_OTHER,(uint16_t)(1+first/2)};
 if(first)native_timing_world()->audio.driver.dsp_binding=binding;
 else native_timing_world()->audio.driver.calibration_binding=binding;
}
/* ICE's fixed 64-KiB workspace also spans the two C facade flags. Its
 * in/out seed must borrow them; unchanged trailing lanes must not publish a
 * cached flag. The accepted decoder writes a contiguous backward ring and
 * reports every actual store, including partial/wrapping writes. */
void audio_workspace_read(uint8_t *destination,uint32_t address,unsigned count){
 memcpy(destination,ugh_mem+address,count);
 for(unsigned i=0;i<count;i++){
  uint8_t value;if(timing_shared_read(address+i,&value))destination[i]=value;
 }
}
void audio_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t destination=(size_t)window,base=(size_t)ugh_mem;
 if(destination>=base && destination-base<UGH_MEM_SIZE && index<UGH_MEM_SIZE-(destination-base)){
  if(timing_shared_write((uint32_t)(destination-base+index),value))return;
 }
 window[index]=value;
}
void audio_workspace_publish(uint32_t base,const uint8_t *source,unsigned count,unsigned extent,size_t written){
 for(unsigned i=0;i<count;i++){
  uint32_t address=base+i;
  if(timing_is_owned(address)){
   unsigned distance=(extent-1u-i)&65535u;
   if(written>distance)timing_shared_write(address,source[i]);
  }else{
   ugh_mem[address]=source[i];
  }
 }
}
