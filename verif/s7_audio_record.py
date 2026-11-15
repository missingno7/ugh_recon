"""Observation-only AdLib boot recorder; no recorder input enters GameWorld."""
import struct,re
import s7_core_record,cgen

def generate(out,frontend=None):
    if frontend:
        import s7_frontend_record
        source=s7_frontend_record.generate(out,'high-score')
    else:source=s7_core_record.generate(out)
    s=source.read_text();_,sy=cgen.read_symbols();load=cgen.LOAD*16
    def addr(n,m='SOUND'):return load+sy[m+':'+n]['linear']
    def off(n,m='GAME'):return sy[m+':'+n]['offset']
    def seg(m):return cgen.LOAD+cgen.FRAMES[m]
    # Resource bindings are observation metadata, never a production resolver.
    import respack
    mz,_=cgen.read_symbols();rows=respack.inventory(mz.image,sy)[0]
    headers=sorted([r for r in rows if r['name'].startswith('data.') and mz.image[r['image_start']:r['image_start']+4]==b'ADLX'],key=lambda r:r['image_start'])
    bindings='static unsigned cursor_segment(AudioCursor c){if(!c.window)return 0;'
    for i,r in enumerate(headers):bindings+=f'if(c.window==world->audio_data[{i}].data)return {cgen.LOAD+r["image_start"]//16};'
    bindings+='exit(9);}\n'
    s=re.sub(r'if\(w->[^;\n]*\.window[^;\n]*\)exit\(9\);','',s)
    s=s.replace('if(w->audio_attempted){','if(w->audio_initialized){')
    lines=[]
    pointers=[('SoundBankBase','audio_reset.bank'),('AdlibInstrumentMap','audio_reset.instrument_map'),('FirstScannedEvent','audio.section_start'),('MainAdlxSectionEnd','audio.section_end')]
    for n,member in pointers:lines.append(f'put({addr(n)+2},cursor_segment(w->{member}),2);')
    for i in range(13):
        for delta,member in [(8,'start'),(18,'cursor')]:lines.append(f'put({addr("AudioChannelStates")+42*i+delta},cursor_segment(w->audio.channels[{i}].{member}),2);')
    lines.append(f'if(w->audio_record)put({addr("CurrentAdlxRecordOffset")},{sy["SOUND:AudioChannelStates"]["offset"]}+42*w->audio_record,2);')
    lines.append(f'put({addr("SoundSystemShutdown","CDATA")},w->audio_shutdown,2);')
    lines.append(f'if(w->terminal_audio_latch)put({load+cgen.FRAMES["DGROUP"]*16+2},1,2);')
    for n,member in [('AdlxPlaybackTimerHandle','audio.playback_timer_handle'),('MusicFadeTimerHandle','audio.fade.timer_handle'),('TimerInterruptInstalled','timer.installed')]:
        lines.append(f'put({addr(n,"TIMER" if n=="TimerInterruptInstalled" else "SOUND")},w->{member},2);')
    lines += [f'put({addr("LastActiveTimerSlotOffset","DGROUP")},(w->timer.count-1)*2,2);',
              f'put({addr("PreviousInt08Offset","DGROUP")},256,2);',f'put({addr("PreviousInt08Segment","DGROUP")},61440,2);']
    for n,member in [('NextPitQuantumLow','quantum'),('EarliestTimerIntervalLow','earliest')]:
        # The table labels are independently resolved from the rebuilt source.
        lines.append(f'put({addr(n,"DGROUP")},w->timer.{member},4);')
    # The historical dwords are split parallel low/high arrays, unlike the
    # ordinary native TimerSlot; serialize each word explicitly.
    fields=[('TimerIntervalLowBySlot','TimerIntervalHighBySlot','interval'),('TimerRemainingLowBySlot','TimerRemainingHighBySlot','remaining')]
    for i in range(16):
        for low,high,member in fields:
            lines += [f'put({addr(low,"DGROUP")+2*i},w->timer.slots[{i}].{member},2);',f'put({addr(high,"DGROUP")+2*i},w->timer.slots[{i}].{member}>>16,2);']
        for n,member in [('TimerCallbackDueBySlot','due'),('TimerHandleBySlot','handle')]:lines.append(f'put({addr(n,"DGROUP")+2*i},w->timer.slots[{i}].{member},2);')
        lines.append(f'put({addr("TimerSlotOffsetByHandle","DGROUP")+2*i},w->timer.by_handle[{i}],2);')
        # Fragment decoding is observer metadata only, preserving mixed pairs.
        lines += [f'put({addr("TimerCallbackOffsetBySlot","DGROUP")+4*i},fragment(w->timer.slots[{i}].target.first),2);',f'put({addr("TimerCallbackSegmentBySlot","DGROUP")+4*i},fragment(w->timer.slots[{i}].target.second),2);']
    lines.append(f'put({addr("ProgrammedPitDivisor","DGROUP")},w->timer.programmed_divisor,2);')
    s=s.replace(' memcpy(device.plane','if(w->timer.count){\n'+'\n'.join(lines)+'\n}\n memcpy(device.plane')
    helper=f'''static unsigned fragment(unsigned f){{switch(f){{case TIMER_ENTRY_CHAIN:return {off('ChainSavedTimerInterrupt','TIMER')};case TIMER_ENTRY_FADE:return {off('AdvanceMusicFade','SOUND')};case TIMER_ENTRY_PLAYBACK:return {off('TickAdlxPlayback','SOUND')};case TIMER_GROUP_TIMER:return {seg('TIMER')};case TIMER_GROUP_SOUND:return {seg('SOUND')};default:return 0;}}}}
static GSStatus pump(void *context,GSInputPollCut cut){{
 GSTestBackend *b=context;static unsigned delivered=0;
 if(cut==GS_INPUT_SCAN&&frames>=1&&delivered<2){{
 unsigned scan=delivered++?129:1;GSTestRun run={{scan,1}};gs_test_stream(&b->scans,&run,1,1);
 InputScript *p=NULL;for(unsigned i=0;i<device.script_count;i++)if(device.scripts[i].port==0x60)p=&device.scripts[i];
 if(!p){{p=&device.scripts[device.script_count++];p->port=0x60;}}p->count=1;p->cursor=p->used=0;p->cycles=p->cycles_left=1;p->runs[0]=(ScriptRun){{scan,1}};
 device.irq_count=1;device.irq_cursor=0;device.irqs[0]=(IrqEvent){{{seg('GAME')},{off('PollKeyboardScanChange')},0,1,0}};
 }}return GS_OK;
}}
'''
    s=s.replace('static void frame(void){',bindings+helper+'static void frame(void){')
    effects=f'''case GST_IRQ:device.clocks+=e.b;device.irq_count=1;device.irq_cursor=1;device.irqs[0]=(IrqEvent){{world->audio.fade.scheduled&&world->audio.fade.target_volume==0?{seg('C')}:{seg('GAME')},world->audio.fade.scheduled&&world->audio.fade.target_volume==0?{off('StopMusicTrack','C')+0x95}:{off('WaitVerticalRetraceActive')},0,0,e.b}};event(LOG_IRQ,e.a,0,e.b);break;
 case GST_ACK:event(LOG_OUT,0x20,1,0x20);break;
 case GST_CLOCK:{{unsigned ticks=observation[0x46c]|observation[0x46d]<<8|observation[0x46e]<<16|observation[0x46f]<<24;ticks++;if(ticks>=0x1800b0){{ticks=0;observation[0x470]++;}}put(0x46c,ticks,4);event(LOG_OUT,0x20,1,0x20);break;}}
 case GST_SCAN:device.irq_cursor++;event(LOG_IRQ,1,0,0);event(LOG_IN,0x60,1,e.b);consume(0x60);break;
 case GST_PIT_COMMAND:device.pit_command=e.b;device.pit_phase=0;event(LOG_OUT,0x43,1,e.b);break;
 case GST_PIT_COUNTER:device.pit_divisor=backend->pit_divisor;device.pit_phase=backend->pit_phase;event(LOG_OUT,0x40,1,e.b);break;
 case GST_TIMER_LIFETIME:
  if(e.a==GS_TIMER_READ_BINDING)event(LOG_DOS,0x21,0,0x3508);
  else{{event(LOG_DOS,0x21,0,0x2508);put(0x20,e.a==GS_TIMER_BIND_HANDLER?{off('HandleTimerInterrupt','TIMER')}:256,2);put(0x22,e.a==GS_TIMER_BIND_HANDLER?{seg('TIMER')}:61440,2);}}break;
 '''
    s=s.replace('case GST_PRESENT:frame();break;',effects+'case GST_PRESENT:frame();break;')
    s=s.replace('gs_test_startup(backend,0)','gs_test_startup(backend,1)')
    if frontend:s=s.replace('gs_test_init(backend);','gs_test_init(backend);gs_test_startup(backend,1);')
    s=s.replace('add_script(0x388,224,0,1,1);','add_script(0x388,0,192,1,2);script(0x388)->count=3;script(0x388)->runs[2]=(ScriptRun){0,64};')
    if not frontend:
        s=s.replace('GameServices services=gs_test_services(backend);','GameServices services=gs_test_services(backend);services.input.pump=pump;')
        s=s.replace('frames==5?REC_RETURN_GAMEPLAY','frames==2?REC_RETURN_GAMEPLAY').replace('frames==6?0:4','frames==3?0:4')
    else:
        s=s.replace('backend->recorder=effect;GSStatus status;','backend->recorder=effect;device.irq_count=2;backend->calibration_reply.progress=REC_BEGIN;if(game_audio_init(world,&services,1)!=GS_OK)return 3;GSStatus status;')
        # The score editor uses the BIOS stream; pump is unused in this profile.
        s=s.replace('GameServices services=gs_test_services(backend);','GameServices services=gs_test_services(backend);(void)pump;')
        s=s.replace('(terminal?0:', '(terminal?1:')
        baseline=bytearray((out/'baseline.bin').read_bytes());struct.pack_into('<H',baseline,0x8ff00,1);(out/'baseline.bin').write_bytes(baseline)
    s=s.replace('#include "native/game_boot.h"','#include "native/game_boot.h"\n#include "native/compose_audio.h"')
    source.write_text(s);return source
