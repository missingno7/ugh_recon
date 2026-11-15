"""Observation-only recording of the production demo objects.

Historical words below serialize typed state into an independent observation
buffer. They are never inputs to a constructor, resource owner or service.
"""
import struct
import cgen
import s7_frontend_record

KINDS={'attract':'ATTRACT','pregame':'PREGAME','completion':'COMPLETION','reveal':'REVEAL'}
LIMITS={'attract':96,'pregame':160,'completion':160,'reveal':128}

def generate(out,scenario,limit=None):
    limit=limit or LIMITS[scenario]
    source=s7_frontend_record.generate(out,'password')
    mz,symbols=cgen.read_symbols();load=cgen.LOAD*16
    def a(n,mod='DGROUP'):return load+symbols[mod+':'+n]['linear']
    def o(n):return symbols['GAME:'+n]['offset']
    s=source.read_text().replace('#include "native/compose_front_end.h"','#include "native/compose_front_end.h"\n#include "native/compose_demo.h"')
    # Reuse only startup's observer, plus the front-end's renderer publication.
    # Its BIOS/editor setup is replaced completely by this scenario's fixture.
    import json
    graph=json.loads((cgen.ROOT/'metadata/object-identities.json').read_text())
    entries=[r for r in graph['resources'] if r['kind']=='OBJECT_SCRIPT']
    mapping='\n'.join('case %d:return %d;'%(r['view'],r['word']) for r in entries)
    helper='''#ifndef S7_DEMO_MISS_ACTOR
static uint16_t script_origin(ObjectResourceIdentity id){
 if(id.kind==OBJECT_RESOURCE_UNSUPPORTED)return 0;
 if(id.kind!=OBJECT_SCRIPT)exit(9);switch(id.view.index){MAPPING default:exit(9);}}
static uint16_t effect_word(ObjectCallbackIdentity id){
 if(id.kind==OBJECT_CALLBACK_UNSUPPORTED)return 0;
 if(id.kind!=OBJECT_CALLBACK_DEMO_EFFECT||id.effect.kind!=RESOURCE_DEMO_EFFECT)exit(9);
 switch(id.effect.index){case 0:return NONE;case 1:return FADE;case 2:return WIDTH;default:exit(9);}}
#endif
'''.replace('MAPPING',mapping).replace('NONE',str(o('IgnoreActorState'))).replace('FADE',str(o('StartDemoFadeWhenSpriteHidden'))).replace('WIDTH',str(o('SetDemoRevealSpriteWidth')))
    s=s.replace('static void frame(void){',helper+'\nstatic void frame(void){')
    fields=[]
    actor=[('ActorInitialPlatformIndices','initial_platform'),('ActorPlatformOrScriptDone','source_or_done'),('ActorDestinationPlatforms','destination_platform'),('ActorSourcePlatformByteIndices','source_byte_index'),('ActorDestinationPlatformByteIndices','destination_byte_index'),('ActorMotionWaitOrDemoRepeats','delay_or_repeat_word'),('ActorX32','position.x32'),('ActorY32','position.y32'),('ActorPixelX','history.pixel_x'),('ActorPreviousDrawX','history.previous_x'),('ActorPixelY','history.pixel_y'),('ActorPreviousDrawY','history.previous_y'),('ActorAnimationByteOffsets','animation.byte_offset'),('ActorAnimationCountdowns','animation.countdown'),('ActorSpriteIds','sprite'),('ActorEraseSprite','history.erase_sprite'),('ActorEraseOverlaySprite','history.erase_overlay_sprite'),('ActorVerticalOrDemoPeriod','motion_or_period_word'),('PassengerQuickDeliveryCountdowns','quick_delivery_ticks')]
    for name,member in actor:fields.append(f'for(unsigned i=0;i<16;i++)put({a(name)}+2*i,w->actors.slot[i].{member},2);')
    fields.append(f'''for(unsigned i=0;i<16;i++){{GameActorSlot *actor=w->actors.slot+i;
 put({a('ActorUpdateOrScriptCursor')}+2*i,actor->cursor==65535?65535:actor->demo?script_origin(actor->script)+8+actor->cursor:actor->cursor,2);
 put({a('ActorPhaseOrDemoLoopCursor')}+2*i,actor->loop_script.kind==OBJECT_RESOURCE_UNSUPPORTED?actor->loop_cursor:script_origin(actor->loop_script)+8+actor->loop_cursor,2);
 put({a('ActorOverlayOrScriptCallbacks')}+2*i,actor->demo?effect_word(actor->callback):actor->overlay_sprite,2);
 }}''')
    for name,member in [('EnemySpriteIds','sprite'),('EnemyEraseSprite','erase_sprite')]:fields.append(f'for(unsigned i=0;i<5;i++)put({a(name)}+2*i,w->enemies.slot[i].{member},2);')
    for name,member in [('FallingItemSprites','sprite'),('FallingItemEraseSprite','erase_sprite')]:fields.append(f'for(unsigned i=0;i<12;i++)put({a(name)}+2*i,w->items.slot[i].{member},2);')
    for name,member,width in [('DemoExitCode','demo_exit',2),('ScreenFadeLevel','run.fade_level',2),('ScreenFadeStep','run.fade_step',2),('WaterSurfaceFrame','presentation.weather.frame',2),('WaterSurfaceFrameCountdown','presentation.weather.countdown',1),('WaterSurfaceByteOffset','presentation.weather.byte_offset',2)]:fields.append(f'put({a(name)},w->{member},{width});')
    fields.append(f'memcpy(observation+{a("Data_264C")},w->run.tiles,320);')
    sprite=symbols['B5B63:SpriteDirectory_000']['linear']+load
    fields.append(f'''for(unsigned i=0;i<662;i++){{put({sprite}+4*i,w->sprite_catalog.sprites[i].source_offset,2);
#ifndef S7_DEMO_MISS_WIDTH
 put({sprite}+4*i+2,w->sprite_catalog.sprites[i].dimensions,2);
#endif
 }}''')
    fields=['#ifndef S7_DEMO_MISS_ACTOR\n'+'\n'.join(fields[:len(actor)+1])+'\n#endif']+fields[len(actor)+1:]
    s=s.replace(' memcpy(device.plane','\n'.join(fields)+'\n memcpy(device.plane')
    # Historical return observations are observer metadata at these page cuts.
    ret=f'(frames==0?{o("PrepareAttractMap0")+0x42}:frames==1?{o("PlayAttractDemo" if scenario=="attract" else "PlayPreGameDemo" if scenario=="pregame" else "PlayGameCompletionDemo" if scenario=="completion" else "PlaySpriteRevealDemo")+3}:{o("RunScriptedDemo")+0x56})'
    start=s.index(' printf("\\\"return\\\":')
    end=s.index('\n',start)
    s=s[:start]+' printf("\\\"return\\\":%u}}\\n",'+ret+');'+s[end:]
    s=s.replace('frames++;\n}',f'frames++;if(frames=={limit})exit(0);\n}}')
    s=s.replace('static int terminal;\nstatic int score_case;','')
    s=s[:s.index('int main(int argc,char **argv)')]+r'''
int main(int argc,char **argv){
 if(argc!=4)return 2;directory=argv[3];FILE *f=fopen(argv[2],"rb");if(!f||fread(observation,1,sizeof observation,f)!=sizeof observation)return 2;fclose(f);
 GSResourcePack pack;char error[256];if(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)!=GS_OK)return 2;
 world=calloc(1,sizeof *world);backend=calloc(1,sizeof *backend);if(!world||!backend)return 2;
 gs_test_init(backend);GSTestRun retraces[]={{0,1},{8,1}},absent[]={{255,10000}};
 gs_test_stream(&backend->retrace_samples,retraces,2,UINT32_MAX);gs_test_stream(&backend->joystick,absent,1,UINT32_MAX);
 add_script(0x3da,0,8,1,2);add_script(0x201,255,0,10000,1);add_script(0xfffe,0x10203040,0,1,1);add_script(0x388,224,0,1,1);
 device.irqs[0]=(IrqEvent){REC_SOUND_SEG,REC_WAIT_BEGIN,0,0,65536};device.irqs[1]=(IrqEvent){REC_SOUND_SEG,REC_WAIT_FINISH,0,0,65536};
 backend->keyboard=(GSBinding){2};backend->resources=gs_resources_operations();backend->resource_context=&pack;
 GameServices services=gs_test_services(backend);if(game_world_construct(world,&services)!=GS_OK)return 3;
 world->pages=(VideoPages){.height=192,.plane_copy_bytes=0x4800,.fixed=0,.displayed=0xa88,.draw=0x5a08,.background=0xa988};
 world->run.configuration.players=1;world->run.configuration.player_bytes=2;world->run.configuration.control_mode[0]=world->run.configuration.control_mode[1]=65535;
 world->input.loop_limit=3;world->input.enabled_axis_storage&=65280u;world->run.water_y=200;world->keyboard_saved=(GSBinding){1};
 backend->recorder=effect;GameDemoResult result=game_demo_play(world,&services,DEMO_PRESENT_KIND);
 fprintf(stderr,"demo status=%u selection=%d frames=%u\n",result.status,result.selection,frames);
 free(world);free(backend);gs_resources_close(&pack);return 4;
}
'''.replace('DEMO_PRESENT_KIND','DEMO_PRESENT_'+KINDS[scenario])
    source.write_text(s);return source
