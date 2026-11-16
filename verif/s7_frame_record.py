"""Observation-only native gameplay recorder. Expected records never feed state."""
import json
import re
import struct
import cgen
import wholegame
import s7_menu_record
import s7_session_record
import s7_gameplay_objects
import s7_enemies


WRAPS=['game_frame_execute','game_demo_play','game_front_introduction','game_enemies_update']

def wraps(path):
    return [] if wholegame.scenario(path)['entry']=='GAME:PlayGameCompletionDemo' else WRAPS


def generate(out,scenario,dump=-1):
    fixture=wholegame.scenario(scenario)
    if fixture['entry']=='GAME:PlayGameCompletionDemo':
        import s7_demo_record
        source=s7_demo_record.generate(out,'completion',fixture['frames'])
        text=source.read_text();calls='output("ram",observation,sizeof observation);output("devices",&device,offsetof(Devices,count));output("io",device.log,device.count*sizeof(IoEvent));'
        text=text.replace(calls,'if(frames==%s){%s}'%(dump if dump>=0 else 'UINT32_MAX',calls))
        source.write_text(text);return source
    # Reuse the independently maintained boot/menu/audio service observer.
    source=s7_menu_record.generate(out,'gameplay-adlib',sessions=True)
    s=source.read_text().replace('#include "native/compose_menu.h"','#include "native/compose_menu.h"\n#include "native/compose_frame.h"')
    mz,sy=cgen.read_symbols();load=cgen.LOAD*16
    def a(n):return load+sy['DGROUP:'+n]['linear']
    def o(n):return sy['GAME:'+n]['offset']
    helpers,fields,_=s7_session_record.projection(full=True)
    # Complete direct actor role and falling-item identities, including stale
    # payload behind sentinels; these mappings are output metadata only.
    objhelpers,objfields,_=s7_gameplay_objects.projection()
    actor_switch=re.search(r'switch\(id.actor\)\{(.*?)default:exit\(9\);',objhelpers,re.S)[1]
    helpers=re.sub(r'(switch\(id.actor\)\{).*?(default:exit\(9\);)',lambda m:m[1]+actor_switch+m[2],helpers,flags=re.S)
    enemy_switch=''.join('case %s:return %d;'%(role,o(name)) for role,name in s7_enemies.role_names().items())
    helpers=re.sub(r'(switch\(id.enemy\)\{).*?(default:exit\(9\);)',lambda m:m[1]+enemy_switch+m[2],helpers,flags=re.S)
    helpers+=objhelpers[objhelpers.index('static uint16_t item_callback'):]
    # Select explicit item publications (the other object projection overlaps).
    fields+='\n'+'\n'.join(line for line in objfields.splitlines() if 'w->items.' in line or 'w->session.item_' in line)
    fields+='\nmemcpy(observation+%d,w->presentation.hud.digits[1],7);'%(a('DecimalDigitBuffer')+7)
    # Shutdown is observable even when no audio timer was ever installed.
    fields+='\nput(%d,w->audio_shutdown,2);if(w->terminal_audio_latch)put(%d,1,2);'%(load+sy['CDATA:SoundSystemShutdown']['linear'],load+cgen.FRAMES['DGROUP']*16+2)
    fields+='\n#ifdef S7_FRAME_MISS_TIMER\nput(%d,0,2);\n#endif'%a('LevelTimer')
    fields+='\n#ifdef S7_FRAME_MISS_ENEMY_ROLE\nif(w->session.enemy_callback[0].kind==OBJECT_CALLBACK_ENEMY&&w->session.enemy_callback[0].enemy==H_TREE_ANIMATE)put(%d,0,2);\n#endif'%a('EnemyStateCallbacks')
    wrappers=f'''
static unsigned boundary,demopage;
static unsigned level_frames;
GSStatus __real_game_frame_execute(GameWorld *,GameServices *,SessionRequest,uint16_t *);
GSStatus __real_game_enemies_update(GameWorld *,GameServices *);
GSStatus __wrap_game_enemies_update(GameWorld *w,GameServices *s){{
 GSStatus r=__real_game_enemies_update(w,s);if(r!=GS_OK)fprintf(stderr,"enemy update status=%u level=%u players=%u\\n",r,w->run.level,w->run.configuration.players);return r;
}}
GSStatus __wrap_game_frame_execute(GameWorld *w,GameServices *s,SessionRequest e,uint16_t *p){{
 unsigned saved=boundary;if(e.action==SESSION_SWAP_PAGE){{boundary={o('RunGameFromPassword')+0x39d};if(++level_frames==100000){{fprintf(stderr,"diagnostic per-level frame bound\\n");exit(8);}}}}
 GSStatus result=__real_game_frame_execute(w,s,e,p);boundary=saved;return result;
}}
GameDemoResult __real_game_demo_play(GameWorld *,GameServices *,DemoPresentationKind);
GameDemoResult __wrap_game_demo_play(GameWorld *w,GameServices *s,DemoPresentationKind kind){{
 unsigned saved=boundary,savedpage=demopage;
 if(kind==DEMO_PRESENT_PREGAME){{boundary=1;demopage=0;}}
 GameDemoResult r=__real_game_demo_play(w,s,kind);boundary=saved;demopage=savedpage;return r;
}}
GSStatus __real_game_front_introduction(GameWorld *,GameServices *,GSBytes,GSBytes);
GSStatus __wrap_game_front_introduction(GameWorld *w,GameServices *s,GSBytes text,GSBytes password){{
 unsigned saved=boundary;level_frames=0;boundary={o('ShowLevelIntroduction')+0x69};
 GSStatus r=__real_game_front_introduction(w,s,text,password);boundary=saved;return r;
}}
'''
    s=s.replace('static unsigned return_word(void){',helpers+wrappers+'static unsigned return_word(void){\n'
        f' if(boundary==1)return demopage++==0?{o("PrepareAttractMap0")+0x42}:demopage==2?{o("PlayPreGameDemo")+3}:{o("RunScriptedDemo")+0x56};\n'
        ' if(boundary)return boundary;\n')
    s=s.replace('default:fprintf(stderr,"unknown observation boundary',f'case MENUS_MAIN_SESSION:return {o("InitializeLevelDisplay")+0x104};\n'
        f'case MENUS_MAIN_PASSWORD:return page==0?{o("EditLevelPassword")+9}:{o("EditLevelPassword")+0x56};\n'
        f'case MENUS_MAIN_GAME_OVER:return {o("RunMainMenuAndAttractLoop")+0x11a};\n'
        f'case MENUS_MAIN_SCORES:return {o("ShowHighScores")+0x1e};\n'
        f'case MENUS_MAIN_INSERT_SCORES:return page==0?{o("InsertHighScoreAndClearScore")+0xc0}:page==8?{o("ShowHighScores")+0x1e}:{o("DrawHighScoreNameEntry")+0x1c};\n'
        'default:fprintf(stderr,"unknown observation boundary')
    s=s.replace(' memcpy(device.plane',fields+'\n memcpy(device.plane')
    # Bounded, incremental cumulative event digest. Raw files are opt-in for a
    # selected diagnostic frame, never retained for a passing deep run.
    hash_helpers='''
#define gs_sha256 recorder_full_hash
#include "port/hash.c"
#undef gs_sha256
static uint32_t rolling_state[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static uint8_t rolling_tail[64];static uint64_t rolling_length;static unsigned rolling_used;
static void rolling_hex(const void *bytes,size_t size,char text[65]){
 const uint8_t *data=bytes;rolling_length+=size;
 while(size){unsigned n=64-rolling_used;if(n>size)n=(unsigned)size;memcpy(rolling_tail+rolling_used,data,n);data+=n;size-=n;rolling_used+=n;if(rolling_used==64){block(rolling_state,rolling_tail);rolling_used=0;}}
 uint32_t state[8];memcpy(state,rolling_state,sizeof state);uint8_t tail[128]={0};memcpy(tail,rolling_tail,rolling_used);tail[rolling_used]=128;
 unsigned end=rolling_used<56?64:128;uint64_t bits=rolling_length*8;for(unsigned i=0;i<8;i++)tail[end-1-i]=(uint8_t)(bits>>(8*i));block(state,tail);if(end==128)block(state,tail+64);
 for(unsigned i=0;i<8;i++)for(unsigned j=0;j<4;j++)sprintf(text+8*i+2*j,"%02x",(uint8_t)(state[i]>>(24-8*j)));
}
'''
    s=s.replace('static void frame(void){',hash_helpers+'static void frame(void){')
    s=s.replace('hex(device.log,device.count*sizeof(IoEvent),log);','rolling_hex(device.log,device.count*sizeof(IoEvent),log);')
    s=s.replace('output("ram",observation,sizeof observation);output("devices",&device,offsetof(Devices,count));output("io",device.log,device.count*sizeof(IoEvent));',
        f'if(frames=={dump if dump>=0 else "UINT32_MAX"}){{output("ram",observation,sizeof observation);output("devices",&device,offsetof(Devices,count));output("io",device.log,device.count*sizeof(IoEvent));}}device.count=0;')
    s=s.replace('if(frames==979)exit(0);',f'if(frames=={fixture["frames"]})exit(0);')
    # Scripted future deliveries use the same queue/cycle rules as Clock.
    def rows(values):return ','.join('{%d,%d}'%x for x in values) or '{UINT32_MAX,0}'
    events=[(f,v) for f,scans in sorted(fixture['events'].items()) for v in scans]
    cycles=[];cycle_changes=[]
    for f,scans in sorted(fixture['cycles'].items()):
        cycle_changes.append('{%d,%d,%d}'%(f,len(cycles),len(scans)));cycles+=scans
    waves=[];joy_changes=[]
    # Translate only external waveform prescriptions, never observed counts.
    joy_cycle=[];joy_start=0
    for f in range(fixture['frames']+1):
        if f in fixture['joy_cycles']:joy_cycle=fixture['joy_cycles'][f];joy_start=f
        wave=fixture['joy_events'].get(f)
        if wave is None and joy_cycle:wave=joy_cycle[(f-joy_start)%len(joy_cycle)]
        if wave is not None:joy_changes.append('{%d,%d,%d}'%(f,len(waves),len(wave)));waves+=wave
    pump='''static GSStatus pump(void *context,GSInputPollCut cut){
 GSTestBackend *b=context;static unsigned next,changed,cycle_at,cycle_count,cycle_cursor,joy;
 static const unsigned events[][2]={EVENTS},changes[][3]={CHANGES},joysticks[][3]={JOY};
 static const unsigned cycle[]={CYCLE},waves[]={WAVES};
 if(cut!=GS_INPUT_SCAN)return GS_OK;
 while(changed<sizeof changes/sizeof *changes&&changes[changed][0]<=frames){cycle_at=changes[changed][1];cycle_count=changes[changed][2];cycle_cursor=0;changed++;}
 while(joy<sizeof joysticks/sizeof *joysticks&&joysticks[joy][0]<=frames){
 unsigned start=joysticks[joy][1],count=joysticks[joy++][2];GSTestRun runs[128];InputScript *p=script(0x201);p->count=count;p->cursor=p->used=0;p->cycles=p->cycles_left=UINT32_MAX;
 for(unsigned i=0;i<count;i++){runs[i]=(GSTestRun){waves[start+i],1};p->runs[i]=(ScriptRun){waves[start+i],1};}gs_test_stream(&b->joystick,runs,count,UINT32_MAX);
 }
 unsigned scan;
 if(next<sizeof events/sizeof *events&&events[next][0]<=frames)scan=events[next++][1];
 else if(cycle_count){scan=cycle[cycle_at+cycle_cursor];cycle_cursor=(cycle_cursor+1)%cycle_count;}
 else return GS_OK;
 GSTestRun delivery={scan,1};gs_test_stream(&b->scans,&delivery,1,1);
 InputScript *p=NULL;for(unsigned i=0;i<device.script_count;i++)if(device.scripts[i].port==0x60)p=&device.scripts[i];
 if(!p){p=&device.scripts[device.script_count++];p->port=0x60;}p->count=1;p->cursor=p->used=0;p->cycles=p->cycles_left=1;p->runs[0]=(ScriptRun){scan,1};
 device.irq_count=1;device.irq_cursor=0;device.irqs[0]=(IrqEvent){REC_GAME_SEG,POLL,0,1,0};return GS_OK;
}
'''
    pump=pump.replace('EVENTS',rows(events)).replace('CHANGES',','.join(cycle_changes) or '{UINT32_MAX,0,0}').replace('JOY',','.join(joy_changes) or '{UINT32_MAX,0,0}').replace('CYCLE',','.join(map(str,cycles)) or '0').replace('WAVES',','.join(map(str,waves)) or '0').replace('POLL',str(o('PollKeyboardScanChange')))
    start=s.index('static GSStatus pump(');end=s.index('#define gs_sha256',start)
    s=s[:start]+pump+s[end:]
    # Explicit constructor configuration is derived solely from the scenario.
    if fixture['card']=='none':
        s=s.replace('gs_test_startup(backend,1)','gs_test_startup(backend,0)')
        s=s.replace('add_script(0x388,0,192,1,2);script(0x388)->count=3;script(0x388)->runs[2]=(ScriptRun){0,64};','add_script(0x388,224,0,1,1);')
    if fixture.get('scores')!='blank':s=s.replace('event(LOG_DOS,0x21,0,0x2c00)','event(LOG_DOS,0x21,0,0x2c02)')
    start=s.index('for(unsigned i=0;i<107;i++)backend->scores[i]=world->front.score_rows[i];',s.index('int main('))
    end=s.index('GameMenuResult result=game_main',start)
    setup=''
    if fixture.get('scores')=='blank':
        setup+='for(unsigned i=0;i<107;i++)backend->scores[i]=world->front.score_rows[i];for(unsigned row=0;row<5;row++)for(unsigned i=0;i<6;i++)backend->scores[14+21*row+i]=32;for(unsigned i=0;i<107;i++)backend->scores[i]^=255;backend->exists=1;backend->length=107;\n'
    if fixture.get('bios'):
        values=[int(v,16) for v in fixture['bios'].split()]
        packed=[]
        for value in values:
            if packed and packed[-1][0]==value:packed[-1][1]+=1
            else:packed.append([value,1])
        setup+='GSTestRun bios[]={%s};gs_test_stream(&backend->bios,bios,%d,1);InputScript *bs=&device.scripts[device.script_count++];bs->port=0xffff;bs->count=%d;bs->cycles=bs->cycles_left=1;for(unsigned i=0;i<%d;i++)bs->runs[i]=(ScriptRun){bios[i].value,bios[i].repeat};\n'%(','.join('{%d,%d}'%tuple(v) for v in packed),len(packed),len(packed),len(packed))
    s=s[:start]+setup+s[end:]
    if fixture.get('password'):
        password=fixture['password'];setup='memset(world->front.password,32,20);memcpy(world->front.password,"%s",%d);'%(password,len(password))
        s=s.replace('GameMenuResult result=game_main',setup+'GameMenuResult result=game_main')
        baseline=bytearray((out/'baseline.bin').read_bytes());baseline[a('PasswordEditBuffer'):a('PasswordEditBuffer')+20]=password.encode().ljust(20,b' ');(out/'baseline.bin').write_bytes(baseline)
    if fixture.get('joystick'):
        values=[int(v,16) for v in fixture['joystick'].split()]
        packed=[]
        for value in values:
            if packed and packed[-1][0]==value:packed[-1][1]+=1
            else:packed.append([value,1])
        s=s.replace('add_script(0x201,255,0,10000,1);',
            'add_script(0x201,255,0,1,1);{GSTestRun initial[]={%s};gs_test_stream(&backend->joystick,initial,%d,UINT32_MAX);InputScript *p=script(0x201);p->count=%d;for(unsigned i=0;i<%d;i++)p->runs[i]=(ScriptRun){initial[i].value,initial[i].repeat};}'%(','.join('{%d,%d}'%tuple(v) for v in packed),len(packed),len(packed),len(packed)))
    # Component entries reproduce only explicit cold fixture inputs.
    if fixture['entry']=='GAME:RunGameFromPassword':
        cold=out/'component';cold.mkdir(exist_ok=True)
        import s7_demo_record
        s7_demo_record.generate(cold,'pregame')
        baseline=bytearray((cold/'baseline.bin').read_bytes())
        players=fixture.get('players',1);password=fixture.get('password','')
        struct.pack_into('<HH',baseline,a('PlayerCount'),players,2*players)
        baseline[a('PasswordEditBuffer'):a('PasswordEditBuffer')+20]=password.encode().ljust(20,b' ')
        (out/'baseline.bin').write_bytes(baseline)
        setup='world->pages=(VideoPages){.height=192,.plane_copy_bytes=0x4800,.fixed=0,.displayed=0xa88,.draw=0x5a08,.background=0xa988};world->run.configuration.players=%d;world->run.configuration.player_bytes=%d;world->run.configuration.control_mode[0]=world->run.configuration.control_mode[1]=65535;world->input.loop_limit=3;world->input.enabled_axis_storage&=65280u;world->run.water_y=200;world->keyboard_saved=(GSBinding){1};backend->keyboard=(GSBinding){2};memset(world->front.password,32,20);memcpy(world->front.password,"%s",%d);'%(players,2*players,password,len(password))
        if fixture['card']=='adlib':setup+='device.irq_count=2;backend->calibration_reply.progress=REC_BEGIN;if(game_audio_init(world,&services,1)!=GS_OK)return 3;'
        else:setup+='device.irq_count=0;'
        # Recording begins after the component fixture is configured, before any
        # game operation. A menu action names the output-only display boundary.
        s=s.replace('GameMenuResult result=game_main(world,&services,&menu);',setup+'menu.process.last=MENUS_MAIN_SESSION;GameSessionResult session=game_session_run(world,&services,GAME_SESSION_PASSWORD);GameMenuResult result={GAME_MENU_SESSION_ENTRY,session.status,MENUS_MAIN_SESSION};')
        s=s.replace('backend->recorder=effect;','backend->recorder=NULL;')
        s=s.replace('menu.process.last=MENUS_MAIN_SESSION;','backend->recorder=effect;menu.process.last=MENUS_MAIN_SESSION;')
        if fixture.get('end')=='return':
            s=s.replace('if(terminal)return 65520;','if(terminal)return 0;')
            s=s.replace('if(result.kind==GAME_MENU_EXIT){terminal=1;frame();return 0;}','if(result.status==GS_OK){terminal=1;frame();return 0;}')
            s=s.replace('terminal?",\\\"terminal\\\":\\\"exit\\\""','terminal?",\\\"terminal\\\":\\\"return\\\""')
    source.write_text(s)
    return source
