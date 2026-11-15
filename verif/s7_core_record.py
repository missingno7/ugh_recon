"""Test-only startup recorder generator. Never a production dependency.

The baseline is the independent rebuilt image, relocated into a separate
observation buffer. Only owner serialization and explicit service effects
change it. No expected frame record is read by the recorder or core.
"""
from pathlib import Path
import struct,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import cgen

def generate(out):
    mz,symbols=cgen.read_symbols();load=cgen.LOAD*16
    observation=bytearray(0x110000);observation[load:load+len(mz.image)]=mz.image
    for site in mz.sites:
        p=load+site;struct.pack_into('<H',observation,p,(struct.unpack_from('<H',observation,p)[0]+cgen.LOAD)&65535)
    # Independent external startup inputs, identical to startup.txt's fixture.
    struct.pack_into('<HH',observation,0x20,0x100,0xf000)
    # Harness return identity is observer metadata, outside the excluded stack.
    struct.pack_into('<H',observation,0x8fefe,0xfff0)
    (out/'baseline.bin').write_bytes(observation)
    def s(name,module='DGROUP'):return symbols[module+':'+name]
    def addr(name,module='DGROUP'):return load+s(name,module)['linear']
    def off(name,module='GAME'):return s(name,module)['offset']
    def seg(module):return cgen.LOAD+cgen.FRAMES[module]
    lines=[]
    def field(name,expression,width=2,module='DGROUP'):
        lines.append(f'put({addr(name,module)},{expression},{width});')
    for name,member in [('PlayerCount','configuration.players'),('PlayerArrayBytes','configuration.player_bytes'),
      ('PlayerOneControlMode','configuration.control_mode[0]'),('PlayerTwoControlMode','configuration.control_mode[1]'),
      ('SelectedDifficulty','configuration.difficulty')]:field(name,'w->run.'+member)
    for name,member,width in [('LatestInterruptScanCode','latest',1),('PreviousPolledScanCode','previous',1),
      ('CurrentKeyboardScanCode','current_scan_storage',2),('KeyboardScanCodeChangeBits','change',1),
      ('KeyboardSequenceIndex','index',1),('JoystickEnabledAxisMask','enabled_axis_storage',2),('JoystickSampleLoopLimit','loop_limit',2)]:
        field(name,'w->input.'+member,width,'GAME' if name=='LatestInterruptScanCode' else 'DGROUP')
    for name,member,n,module in [('HighScoreRows','front.score_rows',107,'DGROUP'),('KeyboardSequenceRecords','input.sequence',205,'DGROUP'),
      ('BaseRgbPalette','palette.base',768,'GAME'),('FadedRgbPalette','palette.faded',768,'GAME')]:
        lines.append(('#ifndef S7_RECORD_MISS_PALETTE\n' if member=='palette.base' else '')+
          f'memcpy(observation+{addr(name,module)},w->{member},{n});'+
          ('\n#endif' if member=='palette.base' else ''))
    field('SavedBiosVideoMode','w->lifecycle.saved_bios_video_mode',1)
    field('HighScoreFileHandle','w->front.file_handle_bytes[0]|(uint16_t)w->front.file_handle_bytes[1]<<8')
    for i in range(4):lines.append(f'put({addr("RandomStateStorage","GAME")+2*i},w->random.word[{i}],2);')
    lines.append('#ifdef S7_RECORD_STALE_SEED\nput('+str(addr('RandomStateStorage','GAME'))+',3,2);\n#endif')
    for name,member in [('PlayfieldHeight','height'),('VgaPlaneCopyByteCount','plane_copy_bytes'),('DrawPagePointer','draw'),
                        ('DisplayedVgaPagePointer','displayed'),('BackgroundPagePointer','background'),('FixedVgaPagePointer','fixed')]:field(name,'w->pages.'+member,2,'GAME')
    # Scratch's full-window tail aliases other allocations; only its64768-byte
    # picture output is written in this slice, as in the historical decoder.
    lines.append(f'memcpy(observation+{load+cgen.FRAMES["ZERO"]*16},w->scratch,64768);')
    joy=[('JoystickPresentFlags','present'),('FirstJoystickXCount','x'),('FirstJoystickYCount','y'),('JoystickButtonBits','buttons'),
      ('FirstJoystickXDoubleCenter','double_x'),('FirstJoystickYDoubleCenter','double_y'),('JoystickLeftThresholds','left'),
      ('JoystickRightThresholds','right'),('JoystickUpThresholds','up'),('JoystickDownThresholds','down')]
    for name,member in joy:
        for i in range(2):lines.append(f'put({addr(name)+2*i},w->input.joysticks[{i}].{member},2);')
    for i,name in enumerate(['ds_3321','ds_3323','ds_3325','ds_3327']):field(name,f'w->input.calibration_reset_words[{i}]')
    field('SoundSystemInitialized','w->audio_initialized',2,'CDATA')
    lines.append('if(w->audio_attempted){')
    field('AdlibInitAttempted','w->audio_attempted',1,'SOUND')
    field('CalibrationLoopRemainder','w->calibration_remainder',2,'SOUND')
    field('SoundIoDelayMultiplier','w->delay_multiplier',2,'SOUND')
    field('SoundDeviceBits','w->audio_reset.devices',2,'SOUND')
    for name,member,width in [('AdlxPlaybackGuard','playback_guard',2),('AdlxTimerPeriod','timer_period',2),('AdlxTickCount','ticks',4),
      ('MusicTicksPerUnit','ticks_per_unit',2),('MainAdlxTimeOrigin','time_origin',4),('ScannedMusicClockTicks','scanned_ticks',4),
      ('MainAdlxPlaying','playing',2),('MainAdlxSectionLoopEnabled','section_loop_enabled',2),('MusicTrackVolume','track_volume',2),
      ('ReservedAdlibChannelCount','reserved_voices',2),('CurrentAdlxSlot','current_channel',2),
      ('MusicFadeStep','fade.step_count',2),('MusicFadeDuration','fade.duration',2),('MusicFadeStartVolume','fade.start_volume',2),
      ('MusicFadeTargetVolume','fade.target_volume',2),('MusicFadeScheduled','fade.scheduled',2)]:field(name,'w->audio.'+member,width,'SOUND')
    for name,member in [('SampleMixerBusy','mixer_busy'),('DspBasePort','dsp_port'),('DspInterruptVector','interrupt_vector'),
      ('ActiveSampleVoiceCount','sample_count'),('ActiveSampleVoiceMask','sample_mask')]:field(name,'w->audio_reset.'+member,2,'SOUND')
    for name,member in [('SoundBankBase','audio_reset.bank'),('AdlibInstrumentMap','audio_reset.instrument_map'),
                        ('FirstScannedEvent','audio.section_start'),('MainAdlxSectionEnd','audio.section_end')]:
        # No track/bank exists in the admitted startup scenario. Reject an
        # unexpected live binding instead of silently recording a null one.
        lines.append(f'if(w->{member}.window)exit(9);')
        field(name,'w->'+member+'.index',2,'SOUND')
        lines.append(f'put({addr(name,"SOUND")+2},0,2);')
    lines.append(f'put({addr("ActiveSampleVoiceMask","SOUND")+2},w->audio_reset.spare[0],2);')
    lines.append(f'put({addr("CurrentAdlxSlot","SOUND")+2},w->audio_reset.spare[1],2);')
    field('SoundBankLength','w->audio_reset.bank_length',4,'SOUND')
    channel=[(0,'age',4),(4,'repeats',2),(6,'start.index',2),(8,'0',2),(10,'length',2),(12,'sample_mode',2),(14,'sample_rate',2),
      (16,'cursor.index',2),(18,'0',2),(20,'sample_half_length',2),(22,'reserved_word',2),(24,'sample_selector',2),(26,'sample_accumulator',2),
      (28,'volume',2),(30,'deadline',4),(34,'voice_count',2),(36,'first_voice',2),(38,'step_q8',2),(40,'control',2)]
    for i in range(13):
        lines.append(f'if(w->audio.channels[{i}].start.window||w->audio.channels[{i}].cursor.window)exit(9);')
        for offset,member,width in channel:lines.append(f'put({addr("AudioChannelStates","SOUND")+42*i+offset},'+('0' if member=='0' else f'w->audio.channels[{i}].{member}')+f',{width});')
    for name,member in [('AdlibVoiceStates','live'),('SavedAdlibVoiceStates','displaced'),('ScannedAdlibVoiceStates','scanned')]:
        for i in range(9):
            a=addr(name,'SOUND')+20*i;lines.append(f'memcpy(observation+{a},w->audio.{member}[{i}].instrument,12);')
            for j,m in enumerate(['volume','gain','owner','frequency']):lines.append(f'put({a+12+2*j},w->audio.{member}[{i}].{m},2);')
    lines.append('}')
    constants=dict(GAME_SEG=seg('GAME'),SOUND_SEG=seg('SOUND'),
      FAIL=off('FailDosCriticalError'),KEYBOARD=off('HandleKeyboardScanInterrupt'),
      BEGIN=off('BeginSoundDelayMeasurement','SOUND'),FINISH=off('FinishSoundDelayMeasurement','SOUND'),
      WAIT_BEGIN=off('loc_1163','SOUND'),WAIT_FINISH=off('loc_116B','SOUND'),
      CAL_VECTOR=addr('PreviousCalibrationTimerVector','SOUND'),CAL_SEGMENT=addr('PreviousCalibrationTimerSegment','SOUND'),
      RETURN_PICTURE_MODE=off('InitializeDosVideoInputAndSound')+0x2f,
      RETURN_PICTURE=off('ShowPackedPictureAndWait')+10,RETURN_GAMEPLAY=off('RunDosGame')+14)
    source=RECORDER.replace('/* CONSTANTS */','\n'.join('#define REC_'+k+' '+str(v) for k,v in constants.items()))
    source=source.replace('/* OWNER FIELDS */','\n'.join(lines))
    scalar_names=['CurrentLevelIndex','LivesRemaining','ScoreLowWord','ScoreHighWord','PlayerPixelX','PlayerYPixels','ActorPlatformOrScriptDone','ActorX32','ActorY32','ActorSpriteIds','PlayerPlatformIndices','ScreenFadeLevel','PlayerCount','ScreenFadeStep','PlayerImpactMagnitude','LevelTimer','WaterYPixels','PlayerCarriedKinds','RemainingPassengerJourneys']
    scalar_code=[]
    for name in scalar_names:
        a=addr(name);v=f'observation[{a}]' if name in ('LivesRemaining','RemainingPassengerJourneys') else f'(observation[{a}]|observation[{a+1}]<<8)'
        scalar_code.append('printf("\\\"'+name+'\\\":%u,",(unsigned)'+v+');')
    source=source.replace('/* SCALARS */','\n'.join(scalar_code))
    target=out/'recorder.c';target.write_text(source);return target

RECORDER=r'''
#include "native/game_boot.h"
#include "port/test/backend.h"
#include "port/resources.h"
#include "port/hash.h"
#include "c/platform.h" /* observer layout only; no machine objects linked */
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
/* CONSTANTS */
static uint8_t observation[UGH_MEM_SIZE];
static Devices device;
static GameWorld *world;
static GSTestBackend *backend;
static const char *directory;
static unsigned frames;
static void put(unsigned address,uint32_t value,unsigned size){for(unsigned i=0;i<size;i++)observation[address+i]=(uint8_t)(value>>(8*i));}
static void event(unsigned kind,unsigned port,unsigned size,unsigned value){if(device.count>=1080000)exit(9);device.log[device.count++]=(IoEvent){kind,port,size,value};}
static InputScript *script(unsigned port){for(unsigned i=0;i<device.script_count;i++)if(device.scripts[i].port==port)return &device.scripts[i];exit(9);}
static void consume(unsigned port){InputScript *s=script(port);if(++s->used==s->runs[s->cursor].repeat){s->used=0;if(++s->cursor==s->count&&s->cycles_left>1){s->cycles_left--;s->cursor=0;}}}
static void add_script(unsigned port,unsigned first,unsigned second,unsigned repeat,unsigned count){InputScript *s=&device.scripts[device.script_count++];s->port=port;s->count=count;s->cycles=s->cycles_left=UINT32_MAX;s->runs[0]=(ScriptRun){first,repeat};if(count==2)s->runs[1]=(ScriptRun){second,1};}
static void hex(const void *p,size_t size,char text[65]){uint8_t hash[32];gs_sha256(p,size,hash);for(unsigned i=0;i<32;i++)sprintf(text+2*i,"%02x",hash[i]);}
static void output(const char *suffix,const void *data,size_t size){char path[4096];snprintf(path,sizeof path,"%s/frame-%u.%s",directory,frames,suffix);FILE *f=fopen(path,"wb");if(!f||fwrite(data,1,size,f)!=size)exit(9);fclose(f);}
static void frame(void){
 GameWorld *w=world;GSTestBackend *b=backend;
 /* OWNER FIELDS */
 memcpy(device.plane,b->planes,sizeof device.plane);memcpy(device.latch,b->latches,4);
 memcpy(device.seq,b->seq,5);memcpy(device.gc,b->gc,9);memcpy(device.crtc,b->crtc,25);memcpy(device.attr,b->attribute,21);
 memcpy(device.dac,b->dac,768);memcpy(device.opl,b->opl,256);
 device.seq_index=b->seq_index;device.map_mask=b->map_mask;device.gc_index=b->gc_index;device.read_map=b->read_plane;
 device.crtc_index=b->crtc_index;device.attr_index=b->attribute_index;device.attr_phase=b->attribute_phase;
 device.dac_index=b->dac_index;device.dac_component=b->dac_component;device.opl_index=b->opl_index;
 device.video_mode=b->video_mode;device.video_columns=b->video_columns;device.video_page=b->video_page;
 char ram[65],dev[65],log[65];uint8_t *joined=malloc(UGH_MEM_SIZE-(0x8fefe - 0x80000));
 memcpy(joined,observation,0x80000);memcpy(joined+0x80000,observation+0x8fefe,UGH_MEM_SIZE-0x8fefe);
 hex(joined,UGH_MEM_SIZE-(0x8fefe - 0x80000),ram);free(joined);
 hex(&device,offsetof(Devices,count),dev);hex(device.log,device.count*sizeof(IoEvent),log);
 printf("{\"ram\":\"%s\",\"device\":\"%s\",\"log\":\"%s\",\"scalars\":{",ram,dev,log);
 /* SCALARS */
 printf("\"return\":%u}}\n",frames==0?REC_RETURN_PICTURE_MODE:frames==5?REC_RETURN_GAMEPLAY:REC_RETURN_PICTURE);
 output("ram",observation,sizeof observation);output("devices",&device,offsetof(Devices,count));output("io",device.log,device.count*sizeof(IoEvent));frames++;
}
static void effect(void *context,GSTestEffect e){
 (void)context;static const unsigned ports[]={0x3c4,0x3c5,0x3ce,0x3cf,0x3d4,0x3d5,0x3c0,0x3c1,0x3da};
 switch(e.kind){
 case GST_CONTROL_WRITE:event(LOG_OUT,ports[e.a],1,e.b);break;
 case GST_CONTROL_READ:event(LOG_IN,ports[e.a],1,e.b);if(e.a==8)consume(0x3da);break;
 case GST_DAC:event(LOG_OUT,e.a==GS_DAC_SELECT?0x3c8:0x3c9,1,e.b);break;
 case GST_JOYSTICK_START:event(LOG_OUT,0x201,1,e.b);script(0x201)->cursor=script(0x201)->used=0;script(0x201)->cycles_left=script(0x201)->cycles;break;
 case GST_JOYSTICK_SAMPLE:event(LOG_IN,0x201,1,e.b);consume(0x201);break;
 case GST_VIDEO_MODE:event(LOG_DOS,0x10,0,e.a?0xf00:e.b);break;
 case GST_LIFECYCLE_BINDING:event(LOG_DOS,0x21,0,0x2524);put(0x90,REC_FAIL,2);put(0x92,REC_GAME_SEG,2);break;
 case GST_FILE:if(e.a!=0x3d)exit(9);event(LOG_DOS,0x21,0,0x3d00);break;
 case GST_SEED:event(LOG_DOS,0x21,0,0x2c02);consume(0xfffe);break;
 case GST_VECTOR:
   event(LOG_DOS,0x21,0,e.a==GS_VECTOR_CAPTURE?0x3509:0x2509);
   if(e.a==GS_VECTOR_INSTALL){put(0x24,REC_KEYBOARD,2);put(0x26,REC_GAME_SEG,2);}break;
 case GST_CALIBRATION:
   if(e.a==GS_CALIBRATION_BEGIN){event(LOG_DOS,0x21,0,0x3508);put(REC_CAL_VECTOR,0x100,2);put(REC_CAL_SEGMENT,0xf000,2);event(LOG_DOS,0x21,0,0x2508);}
   if(e.a!=GS_CALIBRATION_FINISH){device.clocks+=65536;device.irq_cursor++;event(LOG_IRQ,0,0,65536);event(LOG_OUT,0x20,1,0x20);event(LOG_DOS,0x21,0,0x2508);}
   break;
 case GST_OPL:event(LOG_OUT,e.a==GS_OPL_SELECT?0x388:0x389,1,e.b);break;
 case GST_AUDIO_STATUS:event(LOG_IN,0x388,1,e.b);consume(0x388);break;
 case GST_PRESENT:frame();break;
 case GST_EVENT:case GST_CPU_QUERY:case GST_FLUSH:break;
 default:fprintf(stderr,"unhandled recorder effect %u\n",e.kind);exit(9);
 }
}
int main(int argc,char **argv){
 if(argc!=4)return 2;directory=argv[3];FILE *f=fopen(argv[2],"rb");if(!f||fread(observation,1,sizeof observation,f)!=sizeof observation)return 2;fclose(f);
 GSResourcePack pack;char error[256];if(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)!=GS_OK)return 2;
 world=calloc(1,sizeof *world);backend=calloc(1,sizeof *backend);if(!world||!backend)return 2;
 gs_test_init(backend);gs_test_startup(backend,0);
 backend->calibration_reply.progress=REC_BEGIN;
 GSTestRun retraces[]={{0,1},{8,1}},absent[]={{255,10000}};
 gs_test_stream(&backend->retrace_samples,retraces,2,UINT32_MAX);gs_test_stream(&backend->joystick,absent,1,UINT32_MAX);
 add_script(0x3da,0,8,1,2);add_script(0x201,255,0,10000,1);add_script(0xfffe,0x10203040,0,1,1);add_script(0x388,224,0,1,1);
 device.irq_count=2;device.irqs[0]=(IrqEvent){REC_SOUND_SEG,REC_WAIT_BEGIN,0,0,65536};device.irqs[1]=(IrqEvent){REC_SOUND_SEG,REC_WAIT_FINISH,0,0,65536};
 backend->resources=gs_resources_operations();backend->resource_context=&pack;backend->recorder=effect;
 GameServices services=gs_test_services(backend);if(game_world_construct(world,&services)!=GS_OK)return 3;
 GameBootResult result=game_boot(world,&services);
 fprintf(stderr,"slice kind=%u status=%u action=%u frames=%u\n",result.kind,result.status,result.action,frames);
 free(world);free(backend);gs_resources_close(&pack);return result.kind==GAME_BOOT_SLICE_END&&frames==6?0:4;
}
'''
