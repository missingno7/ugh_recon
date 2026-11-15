"""Independent observation-only recorder for typed front-end scenario inputs."""
from pathlib import Path
import struct
import s7_core_record
import cgen

def generate(out,scenario):
    source=s7_core_record.generate(out)
    mz,symbols=cgen.read_symbols();load=cgen.LOAD*16
    def a(n,mod='DGROUP'):return load+symbols[mod+':'+n]['linear']
    def o(n):return symbols['GAME:'+n]['offset']
    baseline=bytearray((out/'baseline.bin').read_bytes())
    # The scenario's explicit external starting page/input configuration.
    for n,v,mod in [('PlayfieldHeight',192,'GAME'),('VgaPlaneCopyByteCount',0x4800,'GAME'),('DrawPagePointer',0x5a08,'GAME'),('DisplayedVgaPagePointer',0xa88,'GAME'),('BackgroundPagePointer',0xa988,'GAME'),('PlayerCount',1,'DGROUP'),('PlayerArrayBytes',2,'DGROUP'),('PlayerOneControlMode',65535,'DGROUP'),('PlayerTwoControlMode',65535,'DGROUP'),('JoystickSampleLoopLimit',3,'DGROUP'),('WaterYPixels',200,'DGROUP')]:
        struct.pack_into('<H',baseline,a(n,mod),v)
    for n in ['DrawPagePointer','DisplayedVgaPagePointer','BackgroundPagePointer']:struct.pack_into('<H',baseline,a(n,'GAME')+2,0xa000)
    struct.pack_into('<HH',baseline,0x24,o('HandleKeyboardScanInterrupt'),cgen.LOAD+cgen.FRAMES['GAME'])
    baseline[a('JoystickEnabledAxisMask')]=0
    if scenario=='high-score':struct.pack_into('<I',baseline,a('ScoreLowWord'),999999)
    (out/'baseline.bin').write_bytes(baseline)
    s=source.read_text().replace('#include "native/game_boot.h"','#include "native/game_boot.h"\n#include "native/compose_front_end.h"')
    s=s.replace('static unsigned frames;','static unsigned frames;\nstatic int terminal;\nstatic int score_case;')
    owner=[]
    for name,member,n in [('HighScoreNameEntry','front.name_entry',13),('PasswordEditBuffer','front.password',21),('LevelNumberTensCharacter','front.level_characters',2),('DecimalDigitBuffer','front_data.digits',7)]:
        assignment=f'memcpy(observation+{a(name)},w->{member},{n});'
        if name==('HighScoreNameEntry' if scenario=='high-score' else 'PasswordEditBuffer'):
            assignment='#ifndef S7_FRONT_MISS_FIELD\n'+assignment+'\n#endif'
        owner.append(assignment)
    for name,member,n,delta in [('Text_0AE4','front.difficulty_text',6,41),('Text_0AE4','front.players_text',10,53),('Text_0B64','front.control_text[0]',10,15),('Text_0B64','front.control_text[1]',10,41)]:owner.append(f'memcpy(observation+{a(name)+delta},w->{member},{n});')
    for name,member,mod in [('WaterYPixels','run.water_y','DGROUP'),('ScoreLowWord','run.score&65535u','DGROUP'),('ScoreHighWord','run.score>>16','DGROUP'),('RendererScratchWord','front_data.renderer_water','GAME'),('SpritePlaneStateScratch','front_data.renderer_plane','GAME')]:owner.append(f'put({a(name,mod)},w->{member},2);')
    owner+=['memcpy(device.files[0].data,b->scores,8192);device.files[0].exists=b->exists;device.files[0].length=b->length;',
            'if(b->exists)memcpy(device.files[0].name,"UGH!.HI",8);',
            'for(unsigned i=0;i<32;i++){device.handles[i].active=b->handles[i].active;device.handles[i].position=b->handles[i].position;device.handles[i].mode=b->handles[i].mode;}']
    s=s.replace(' memcpy(device.plane', '\n'.join(owner)+'\n memcpy(device.plane')
    ret=f'(terminal?0:score_case?(frames==0?{o("InsertHighScoreAndClearScore")+0xc0}:frames==8?{o("ShowHighScores")+0x1e}:{o("DrawHighScoreNameEntry")+0x1c}):(frames==0?{o("EditLevelPassword")+9}:{o("EditLevelPassword")+0x56}))'
    # DrawMainMenu's tail dispatch sees its caller's return, EditLevelPassword+9.
    old='printf("\\\"return\\\":%u}}\\n",frames==0?REC_RETURN_PICTURE_MODE:frames==5?REC_RETURN_GAMEPLAY:REC_RETURN_PICTURE);'
    new='printf("\\\"return\\\":%u}%s}\\n",'+ret+',terminal?",\\\"terminal\\\":\\\"return\\\"":"");'
    assert old in s;s=s.replace(old,new)
    s=s.replace('case GST_FILE:if(e.a!=0x3d)exit(9);event(LOG_DOS,0x21,0,0x3d00);break;', '''case GST_FILE:event(LOG_DOS,0x21,0,e.a==0x3c?0x3c00:e.a==0x40?(0x4000|e.b):e.a==0x3d?0x3d00:(e.a<<8));break;
 case GST_QUEUE:
#ifndef S7_FRONT_MISS_QUEUE
 event(LOG_DOS,0x16,0,e.a==GS_QUEUE_PEEK?0x100:e.b);
#endif
 if(e.a==GS_QUEUE_TAKE)consume(0xffff);break;''')
    s=s.replace('if(e.a==GS_VECTOR_INSTALL){put(0x24,REC_KEYBOARD,2);put(0x26,REC_GAME_SEG,2);}break;', 'if(e.a==GS_VECTOR_INSTALL){put(0x24,REC_KEYBOARD,2);put(0x26,REC_GAME_SEG,2);}else if(e.a==GS_VECTOR_RESTORE){put(0x24,0,4);}break;')
    s=s[:s.index('int main(int argc,char **argv)')]+r'''
int main(int argc,char **argv){
 if(argc!=4)return 2;directory=argv[3];FILE *f=fopen(argv[2],"rb");if(!f||fread(observation,1,sizeof observation,f)!=sizeof observation)return 2;fclose(f);
 GSResourcePack pack;char error[256];if(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)!=GS_OK)return 2;
 world=calloc(1,sizeof *world);backend=calloc(1,sizeof *backend);if(!world||!backend)return 2;
 gs_test_init(backend);
 GSTestRun retraces[]={{0,1},{8,1}},absent[]={{255,10000}};
 gs_test_stream(&backend->retrace_samples,retraces,2,UINT32_MAX);gs_test_stream(&backend->joystick,absent,1,UINT32_MAX);
 add_script(0x3da,0,8,1,2);add_script(0x201,255,0,10000,1);add_script(0xfffe,0x10203040,0,1,1);add_script(0x388,224,0,1,1);
 device.irqs[0]=(IrqEvent){REC_SOUND_SEG,REC_WAIT_BEGIN,0,0,65536};device.irqs[1]=(IrqEvent){REC_SOUND_SEG,REC_WAIT_FINISH,0,0,65536};
 /* BIOS scenario words are future external deliveries, not a state snapshot. */
 score_case=SCORE_CASE;
 GSTestRun bios_score[]={{0x61,1},{0x62,1},{8,1},{0x63,1},{0x31,1},{13,1}};
 GSTestRun bios_password[]={{0x61,1},{8,1},{0x62,1},{0x31,1},{13,1}};
 GSTestRun *bios=score_case?bios_score:bios_password;unsigned count=score_case?6:5;
 gs_test_stream(&backend->bios,bios,count,1);
 InputScript *bs=&device.scripts[device.script_count++];bs->port=0xffff;bs->count=count;bs->cycles=bs->cycles_left=1;
 for(unsigned i=0;i<count;i++)bs->runs[i]=(ScriptRun){bios[i].value,1};
 backend->keyboard=(GSBinding){2};backend->resources=gs_resources_operations();backend->resource_context=&pack;
 GameServices services=gs_test_services(backend);if(game_world_construct(world,&services)!=GS_OK)return 3;
 world->pages=(VideoPages){.height=192,.plane_copy_bytes=0x4800,.fixed=0,.displayed=0xa88,.draw=0x5a08,.background=0xa988};
 world->run.configuration.players=1;world->run.configuration.player_bytes=2;world->run.configuration.control_mode[0]=world->run.configuration.control_mode[1]=65535;
 world->input.loop_limit=3;world->input.enabled_axis_storage&=65280u;world->run.water_y=200;world->keyboard_saved=(GSBinding){1};
 if(score_case)world->run.score=999999;
 backend->recorder=effect;GSStatus status;
 if(score_case)status=game_front_scores_insert(world,&services).status;else status=game_front_password(world,&services);
 if(status!=GS_OK){fprintf(stderr,"front status=%u frames=%u\n",status,frames);return 4;}
 terminal=1;frame();free(world);free(backend);gs_resources_close(&pack);return 0;
}
'''
    s=s.replace('SCORE_CASE','1' if scenario=='high-score' else '0')
    source.write_text(s);return source

