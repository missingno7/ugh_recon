"""Independent menu recorder; scenario events are future service deliveries only."""
import cgen,s7_core_record,s7_demo_record,s7_audio_record

def generate(out,scenario):
    import wholegame
    fixture=wholegame.scenario(cgen.ROOT/'tests/scenarios'/f'{scenario}.txt')
    limit=int(fixture['frames'])
    source=s7_demo_record.generate(out,'reveal',limit)
    # Keep the demo owner serializer, but start from the program's cold baseline.
    cold=out/'cold';cold.mkdir(exist_ok=True);s7_core_record.generate(cold)
    (out/'baseline.bin').write_bytes((cold/'baseline.bin').read_bytes())
    s=source.read_text().replace('#include "native/compose_demo.h"','#include "native/compose_demo.h"\n#include "native/compose_menu.h"')
    s=s.replace('static unsigned frames;','static unsigned frames;\nstatic GameMenu menu;\nstatic int terminal;')
    _,sy=cgen.read_symbols()
    def o(n):return sy['GAME:'+n]['offset']
    def seg(n):return cgen.LOAD+cgen.FRAMES[n]
    bootframes=6 if scenario=='startup' else 3
    ret=f'''static unsigned return_word(void){{
 if(terminal)return 65520;
 if(frames<{bootframes})return frames==0?REC_RETURN_PICTURE_MODE:frames=={bootframes-1}?REC_RETURN_GAMEPLAY:REC_RETURN_PICTURE;
 static MenusMainAction previous=MENUS_MAIN_BOUND;static unsigned page;
 MenusMainAction action=menu.process.last;if(action!=previous){{page=0;previous=action;}}else page++;
 switch(action){{
 case MENUS_MAIN_REVEAL:return page==0?{o('PrepareAttractMap0')+0x42}:page==1?{o('PlaySpriteRevealDemo')+3}:{o('RunScriptedDemo')+0x56};
 case MENUS_MAIN_ATTRACT:return page==0?{o('PrepareAttractMap0')+0x42}:page==1?{o('PlayAttractDemo')+3}:{o('RunScriptedDemo')+0x56};
 case MENUS_MAIN_PREPARE_SCREEN:return page==0?{o('RunMainMenuAndAttractLoop')+0x67}:{o('RunMainMenuAndAttractLoop')+0x6d};
 case MENUS_MAIN_REDRAW:return {o('RunMainMenuAndAttractLoop')+0x75};
 case MENUS_MAIN_CONTROLS:return page==0?{o('SelectPlayerControls')+0xf}:{o('SelectPlayerControls')+0x17};
 case MENUS_MAIN_CREDITS:return page%2?{o('ShowCreditsPages')+0x5c}:{o('ShowCreditsPages')+0x1f};
 default:fprintf(stderr,"unknown observation boundary %u\\n",action);exit(9);
 }}
}}
'''
    s=s.replace('static void frame(void){',ret+'static void frame(void){')
    start=s.index(' printf("\\\"return\\\":');end=s.index('\n',start)
    s=s[:start]+r' printf("\"return\":%u}%s}\n",return_word(),terminal?",\"terminal\":\"exit\"":"");'+s[end:]
    # Reuse the startup fixture setup, replacing only the typed entry.
    main=s7_core_record.RECORDER[s7_core_record.RECORDER.index('int main(int argc,char **argv)'):]
    main=main.replace('GameBootResult result=game_boot(world,&services);','GameMenuResult result=game_main(world,&services,&menu);')
    if scenario=='gameplay-adlib':
        setup=r'''for(unsigned i=0;i<107;i++)backend->scores[i]=world->front.score_rows[i];
 for(unsigned row=0;row<5;row++)for(unsigned i=0;i<6;i++)backend->scores[14+21*row+i]=32;
 for(unsigned i=0;i<107;i++)backend->scores[i]^=255;backend->exists=1;backend->length=107;
 GSTestRun bios[]={{0x57,1},{0x48,1},{0x4f,1},{0x4c,1},{0x45,1},{13,1}};gs_test_stream(&backend->bios,bios,6,1);
 InputScript *bs=&device.scripts[device.script_count++];bs->port=0xffff;bs->count=6;bs->cycles=bs->cycles_left=1;
 for(unsigned i=0;i<6;i++)bs->runs[i]=(ScriptRun){bios[i].value,1};
 '''
        main=main.replace('GameMenuResult result=game_main',setup+'GameMenuResult result=game_main')
    main=main.replace('free(world);free(backend);gs_resources_close(&pack);return result.kind==GAME_BOOT_SLICE_END&&frames==6?0:4;','if(result.kind==GAME_MENU_EXIT){terminal=1;frame();return 0;}return result.kind==GAME_MENU_SESSION_ENTRY?0:4;')
    main=main.replace('GameServices services=gs_test_services(backend);','GameServices services=gs_test_services(backend);services.input.pump=pump;')
    s=s[:s.index('int main(int argc,char **argv)')]+main
    source.write_text(s)
    # Active serializer and service effects also work with an absent card. Its
    # cursor mapping is observation-only, never a runtime resource resolver.
    source=s7_audio_record.generate(out,frontend='menu',source=source);s=source.read_text()
    (out/'baseline.bin').write_bytes((cold/'baseline.bin').read_bytes())
    # Replace the supplemental intro pump with this scenario's frame deliveries.
    events=[(f,v) for f,scans in sorted(fixture['events'].items()) for v in scans]
    eventrows=','.join('{%d,%d}'%e for e in events) or '{4294967295u,0}'
    pump=f'''static GSStatus pump(void *context,GSInputPollCut cut){{
 GSTestBackend *b=context;static unsigned next;static const unsigned events[][2]={{{eventrows}}};
 if(cut==GS_INPUT_SCAN&&next<sizeof events/sizeof *events&&events[next][0]<=frames){{
 unsigned scan=events[next++][1];GSTestRun delivery={{scan,1}};gs_test_stream(&b->scans,&delivery,1,1);
 InputScript *p=NULL;for(unsigned i=0;i<device.script_count;i++)if(device.scripts[i].port==0x60)p=&device.scripts[i];
 if(!p){{p=&device.scripts[device.script_count++];p->port=0x60;}}p->count=1;p->cursor=p->used=0;p->cycles=p->cycles_left=1;p->runs[0]=(ScriptRun){{scan,1}};
 device.irq_count=1;device.irq_cursor=0;device.irqs[0]=(IrqEvent){{{seg('GAME')},{o('PollKeyboardScanChange')},0,1,0}};
 }}return GS_OK;
}}
'''
    start=s.index('static GSStatus pump(');end=s.index('static void frame',start);s=s[:start]+pump+s[end:]
    if fixture['card']!='adlib':
        s=s.replace('gs_test_startup(backend,1)','gs_test_startup(backend,0)')
        s=s.replace('add_script(0x388,0,192,1,2);script(0x388)->count=3;script(0x388)->runs[2]=(ScriptRun){0,64};','add_script(0x388,224,0,1,1);')
    s=s.replace('case GST_EVENT:case GST_CPU_QUERY:case GST_FLUSH:break;','case GST_EVENT:case GST_CPU_QUERY:break;\n case GST_FLUSH:put(0x41a,e.b,2);break;\n case GST_TERMINAL:device.exited=1;device.exit_code=e.b;event(LOG_DOS,0x21,0,0x4c00|e.b);break;')
    # The fixture BDA queue is initially empty; its live tail reply is zero.
    s=s.replace('if(e.a==GS_VECTOR_RESTORE){put(0x24,0,4);}','if(e.a==GS_VECTOR_RESTORE){put(0x24,0,4);}')
    if scenario=='gameplay-adlib':
        s=s.replace('e.a==0x3d?0x3d00:(e.a<<8)', 'e.a==0x3d?0x3d00:e.a==0x3f?(0x3f00|e.b):e.a==0x3e?(0x3e00|107):(e.a<<8)')
        s=s.replace('event(LOG_DOS,0x21,0,0x2c02)', 'event(LOG_DOS,0x21,0,0x2c00)')
    player_lane=f'put({cgen.LOAD*16+sy["DGROUP:PlayerCount"]["linear"]},w->run.configuration.players,2);'
    s=s.replace(player_lane,'#ifndef S7_MENU_MISS_PLAYERS\n'+player_lane+'\n#endif')
    s=s.replace('device.exited=1;device.exit_code=e.b;', '\n#ifndef S7_MENU_MISS_EXIT\n device.exited=1;device.exit_code=e.b;\n#endif\n')
    source.write_text(s);return source
