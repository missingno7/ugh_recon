"""Independent object-boundary recordings, not a gameplay frame certificate.

Only semantic case inputs configure the two executions. Native recordings exit
before the independent literal worker runs or any expected bytes are read.
"""
import argparse
import ctypes as C
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'verif')]
import cgen
import nativebuild
import s7_audio
import s7_session_record
from job_pool import run, save
from cbuild import GCC


def roles():
    text = (ROOT/'native/actor_pass.h').read_text()
    return re.findall(r'^    ACTOR_CALLBACK_(\w+),', text, re.M)


def cases():
    result = []
    for ordinal, role in enumerate(roles(), 1):
        if role in ('BoardWaterbornePassenger',) or ordinal >= 27:
            types = [1, 3, 5]
        elif 21 <= ordinal <= 26:
            types = [6, 7]
        else:
            types = [0, 2, 4]
        for kind in types:
            for variant in range(4):
                result.append(dict(role=role, ordinal=ordinal, kind=kind, variant=variant))
    return result


def projection():
    helpers, fields, ranges = s7_session_record.projection()
    _, symbols = cgen.read_symbols()
    # Some registered direct roles are deliberately absent from shipped
    # descriptor links. They still have independent observation identities.
    for role in roles():
        if 'case ACTOR_CALLBACK_'+role+':' not in helpers:
            helpers=helpers.replace('switch(id.actor){','switch(id.actor){case ACTOR_CALLBACK_%s:return %d;' % (role,symbols['GAME:'+role]['offset']))
    def a(name):
        return cgen.LOAD*16+symbols['DGROUP:'+name]['linear']
    extras = [('CurrentLevelIndex', 'w->run.level', 2), ('ScoreLowWord', 'w->run.score', 4),
              ('LivesRemaining', 'w->run.lives', 1), ('ScoreMultiplier', 'w->run.multiplier', 1),
              ('LevelTimer', 'w->run.timer', 2), ('LevelCompletionMarker', 'w->run.completion', 1),
              ('ScreenFadeStep', 'w->run.fade_step', 2), ('ScreenFadeLevel', 'w->run.fade_level', 2)]
    for name, expr, size in extras:
        fields += '\nput(%d,%s,%d);' % (a(name), expr, size)
        ranges.append((a(name), size, name))
    # Bindings below are observation metadata, independent of constructors.
    bridge=(ROOT/'native/bridge/item_world_bridge.c').read_text()
    item_names = re.findall(r' WORD\((\w+),(\w+)\)', bridge)
    for name, member in item_names:
        if name=='n' or member in ('descriptor_word','callback_word'):
            continue
        for i in range(12):
            fields += '\nput(%d,w->items.slot[%d].%s,2);' % (a(name)+2*i, i, member)
            ranges.append((a(name)+2*i, 2, name+str(i)))
    for i in range(12):
        for name, expr in [('FallingItemDescriptors', 'origin(w->session.item_descriptor[%d])' % i),
                           ('FallingItemCallbacks', 'item_callback(w->session.item_callback[%d])' % i)]:
            fields += '\nput(%d,%s,2);' % (a(name)+2*i, expr)
            ranges.append((a(name)+2*i, 2, name+str(i)))
    graph=json.loads((ROOT/'metadata/object-identities.json').read_text())
    callbacks={l['callback']['role']:l['word'] for l in graph['links'] if l['kind']=='callback' and l['callback']['family']=='item'}
    helpers += '''static uint16_t item_callback(ObjectCallbackIdentity id){
 if(id.kind==OBJECT_CALLBACK_UNSUPPORTED)return 0;
 if(id.kind!=OBJECT_CALLBACK_ITEM)exit(9);
 switch(id.item){%s default:exit(9);}}
''' % ''.join('case %s:return %d;' % pair for pair in callbacks.items())
    return helpers,fields,ranges


def actor_setup(row):
    """Semantic external test inputs, shared by two independent constructors."""
    v=row['variant']
    alias = 2 if row['role'] in ('UpdateCarriedPassenger','DeliverPassenger','WaitForStoneRelease','ThrowCarriedStone') else [65535,0,32768,1][v]
    values=dict(position_x=1024, position_y=1024, pixel_x=32, pixel_y=32,
                source=0, destination=1, animation_offset=65534 if v==0 else 0,
                countdown=[1,0,2,1][v], alias=alias, repeat=[0,1,65535,2][v],
                vertical=[0,65535,32768,100][v], sprite=123, overlay=65535,
                quick=[0,1,32768,200][v], water=20 if v==3 else 160,
                fare=1234, floor=100, score=4294967280,
                remaining=[0,1,128,2][v], action=[0,128,32768,128][v])
    if row['role']=='UpdateThrownStone':
        if v==0:values['vertical']=65530
        if v==1:values['position_x']=65023
        if v==2:values.update(position_y=6144,vertical=0)
    if row['role']=='UpdatePassengerSinking' and v==3:
        values.update(position_y=6144,vertical=0)
    return values


def direct_extra(row):
    if row['role']=='ReadPassengerJourneyLeg' and row['variant']!=3:
        return 'GSBytes journey;if(game_object_resource(&s,a->journey,&journey)!=GS_OK)exit(3);a->journey.position=(uint16_t)(a->journey.position+journey.size-6);'
    if row['role']=='AnimatePassengerDeparture' and row['variant']==3:
        return 'ObjectGraphLink link;GSBytes animation;if(game_object_link(a->descriptor,56,&link)!=GS_OK||game_object_resource(&s,link.resource,&animation)!=GS_OK)exit(3);a->animation.byte_offset=(uint16_t)(animation.size-6);'
    if row['role']=='UpdateThrownStone' and row['variant']==3:
        return 'uint16_t ax,ay;if(game_object_word(&s,a->descriptor,0,&ax)!=GS_OK||game_object_word(&s,a->descriptor,2,&ay)!=GS_OK)exit(3);a->position.x32=(uint16_t)((w->session.platforms.slot[0].left-ax+1u)*32u);a->position.y32=(uint16_t)((w->session.platforms.slot[0].height-ay)*32u);a->delay_or_repeat_word=0;a->motion_or_period_word=0;'
    return ''


def item_resources():
    graph=json.loads((ROOT/'metadata/object-identities.json').read_text())
    return sorted((r for r in graph['resources'] if r['kind']=='OBJECT_ITEM_DESCRIPTOR'),key=lambda r:r['word'])


def items_body():
    ids=','.join('{OBJECT_ITEM_DESCRIPTOR,{%d},0}' % r['view'] for r in item_resources())
    return '''
 static const ObjectResourceIdentity descriptors[]={IDS};
 for(unsigned type=0;type<11;type++)for(unsigned operation=0;operation<4;operation++)for(unsigned variant=0;variant<8;variant++){
  if(game_world_construct(w,&s)!=GS_OK)exit(3);
  w->run.configuration.players=2;w->run.configuration.player_bytes=4;w->run.level=0;w->run.water_y=200;
  if(game_session_load(w,&s)!=GS_OK)exit(3);
  w->run.timer=65530;w->run.lives=255;w->run.multiplier=2;
  ObjectResourceIdentity id=descriptors[type];
  for(unsigned j=0;j<12;j++)w->items.slot[j].sprite=65535;
  w->session.item_descriptor[0]=id;
  w->session.item_callback[0]=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ITEM,.item=ITEM_CALLBACK_ADVANCE};
  NativeItemSlot *a=w->items.slot;
  a->sprite=400;a->x32=1024;a->y32=1024;a->vertical_step=variant==0?65530:0;
  a->motion_or_lifetime=variant==1?1:variant==2?0:560;
  a->erase_sprite=123;a->draw_x=12;a->draw_y=13;a->previous_x=14;a->previous_y=15;
  if(operation==1){
   a->motion_or_lifetime=0;
   if(variant==1)a->x32=65024;
   if(variant==2)a->x32=10240;
   if(variant==3)a->y32=6144;
   if(variant>=4){
    uint16_t ax,ay;if(game_object_word(&s,id,0,&ax)!=GS_OK||game_object_word(&s,id,2,&ay)!=GS_OK)exit(3);
    a->x32=(uint16_t)((w->session.platforms.slot[0].left-ax+(variant&1))*32u);
    a->y32=(uint16_t)((w->session.platforms.slot[0].height-ay-1u)*32u);a->vertical_step=32;
   }
  }
  for(unsigned j=0;j<2;j++){NativePlayer *p=w->session.players.player+j;
   p->fixed_x=4096;p->fixed_y=4096;
   if(variant>=3&&j==(variant&1u)){uint16_t ax,ay;if(game_object_word(&s,id,0,&ax)!=GS_OK||game_object_word(&s,id,2,&ay)!=GS_OK)exit(3);
    p->fixed_x=(uint16_t)(a->x32+(ax-10u)*32u);p->fixed_y=(uint16_t)(a->y32+ay*32u-100u);}
  }
  GSStatus status=GS_OK;
  if(operation==0){
   for(unsigned j=0;j<12;j++)w->items.slot[j].sprite=variant==1?400:65535;
   if(variant==2)w->items.slot[11].sprite=65534;
   GameItemSpawn r=game_item_spawn(w,&s,id,(ObjectPosition){1024,2048},65520,123);
   status=r.status;if((r.allocation.status==ITEM_POOL_FULL)!=(variant==1))exit(3);
  }else if(operation==1)status=game_item_call(w,&s,0,ITEM_CALLBACK_ADVANCE);
  else if(operation==2)status=game_item_call(w,&s,0,ITEM_CALLBACK_LAND);
  else status=game_item_call(w,&s,0,ITEM_CALLBACK_COLLECT);
  if(status!=GS_OK){fprintf(stderr,"item %u %u %u status %u\\n",type,operation,variant,status);exit(3);}
  record(w,f);case_index++;
 }
'''.replace('IDS',ids)


def source(out, mode):
    helpers,fields,ranges=projection()
    records='\n'.join('if(fwrite(observation+%d,1,%d,f)!=%d)exit(9);' % (at,n,n) for at,n,_ in ranges)
    setup=[]
    for row in cases():
        q=actor_setup(row)
        setup.append('''{
 if(game_world_construct(w,&s)!=GS_OK)exit(3);
 w->run.configuration.players=2;w->run.configuration.player_bytes=4;w->run.level=0;w->run.water_y=200;
 if(game_session_load(w,&s)!=GS_OK)exit(3);
 GameActorSlot *a=w->actors.slot;ObjectResourceIdentity descriptor;
 if(game_object_actor_type((ActorTypeId)KIND,&descriptor)!=GS_OK)exit(3);a->descriptor=descriptor;
 a->callback=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ACTOR,.actor=ACTOR_CALLBACK_ROLE};
 a->position=(ObjectPosition){PX,PY};a->history.pixel_x=HX;a->history.pixel_y=HY;
 a->source_or_done=SRC;a->source_byte_index=2*SRC;a->destination_platform=DST;a->destination_byte_index=2*DST;
 a->animation=(ActorAnimationState){OFF,TICK};a->loop_cursor=ALIAS;a->delay_or_repeat_word=REPEAT;
 a->motion_or_period_word=VERTICAL;a->sprite=SPRITE;a->overlay_sprite=OVERLAY;a->quick_delivery_ticks=QUICK;
 w->run.water_y=WATER;w->run.record.water_fixed=WATER*32;w->run.score=SCORE;
 w->run.multiplier=2;w->run.lives=255;w->run.timer=65530;w->run.fade_step=2;w->run.fade_level=256;w->run.record.journeys=REMAINING;
 for(size_t j=0;j<2;j++){NativePlayer *p=w->session.players.player+j;
 p->fare=FARE;p->minimum_fare=FLOOR;p->fixed_x=4096;p->fixed_y=4096;p->pixel_x=128;p->pixel_y=128;
 p->velocity_x=65500;p->velocity_y=120;p->platform=65535;p->carried=0;p->action=ACTION;}
 for(size_t j=0;j<12;j++)w->items.slot[j].sprite=65535;
 if(VARIANT==3){
  w->session.players.player[1].platform=0;w->session.players.player[1].pixel_x=(uint16_t)(32+8-16);
  w->session.players.player[1].pixel_y=(uint16_t)(WATER-18);w->session.players.player[1].velocity_y=0;
 }
 EXTRA
 uint16_t cursor=0;GSStatus status=game_actor_call(w,&s,&cursor,a->callback,0);
 if(status!=GS_OK){fprintf(stderr,"actor case %u ROLE type KIND variant VARIANT status %u\\n",case_index,status);exit(3);}
 record(w,f);if(fwrite(&cursor,2,1,f)!=1)exit(9);case_index++;
}'''.replace('KIND',str(row['kind'])).replace('ROLE',row['role']).replace('VARIANT',str(row['variant']))
            .replace('PX',str(q['position_x'])).replace('PY',str(q['position_y'])).replace('HX',str(q['pixel_x'])).replace('HY',str(q['pixel_y']))
            .replace('SRC',str(q['source'])).replace('DST',str(q['destination'])).replace('OFF',str(q['animation_offset'])).replace('TICK',str(q['countdown']))
            .replace('ALIAS',str(q['alias'])).replace('REPEAT',str(q['repeat'])).replace('VERTICAL',str(q['vertical'])).replace('SPRITE',str(q['sprite']))
            .replace('OVERLAY',str(q['overlay'])).replace('QUICK',str(q['quick'])).replace('WATER',str(q['water'])).replace('SCORE',str(q['score'])+'u')
            .replace('FARE',str(q['fare'])).replace('FLOOR',str(q['floor'])).replace('REMAINING',str(q['remaining'])).replace('ACTION',str(q['action'])).replace('EXTRA',direct_extra(row)))
    if mode=='passes':
        body='''
 w->run.water_y=200;
 for(unsigned players=1;players<=2;players++)for(unsigned level=0;level<(players==1?69u:81u);level++){
  w->run.configuration.players=(uint16_t)players;w->run.configuration.player_bytes=(uint16_t)(players*2);w->run.level=(uint16_t)level;
  if(game_session_load(w,&s)!=GS_OK)exit(3);
  for(unsigned iteration=0;iteration<320;iteration++){
   GSStatus status=game_actors_update(w,&s);
   if(status!=GS_OK){fprintf(stderr,"pass %u %u %u status %u\\n",players,level,iteration,status);exit(3);}
   record(w,f);case_index++;
  }
 }
'''
    elif mode=='items':
        body=items_body()
    else:
        body='\n'.join(setup)
    text=r'''
#include "native/compose_session.h"
#include "native/compose_objects.h"
#include "native/game_object_data.h"
#include "port/resources.h"
#include "port/test/backend.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t observation[0x110000];
static void put(unsigned at,unsigned value,unsigned n){for(unsigned i=0;i<n;i++)observation[at+i]=(uint8_t)(value>>(8*i));}
HELPERS
static void record(GameWorld *w,FILE *f){FIELDS
#ifdef S7_OBJECT_MISS_ALIAS
 put(ALIAS_ADDRESS,0,2);
#endif
RECORDS
}
int main(int argc,char **argv){
 if(argc!=3)return 2;GSResourcePack pack;char error[256];
 if(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)!=GS_OK)return 2;
 GameWorld *w=calloc(1,sizeof *w);GSTestBackend *b=calloc(1,sizeof *b);if(!w||!b)return 2;
 gs_test_init(b);b->resources=gs_resources_operations();b->resource_context=&pack;GameServices s=gs_test_services(b);
 if(game_world_construct(w,&s)!=GS_OK)return 3;
 FILE *f=fopen(argv[2],"wb");if(!f)return 2;unsigned case_index=0;
 BODY
 fclose(f);free(w);free(b);gs_resources_close(&pack);printf("object records %u\n",case_index);return 0;
}
'''
    _,symbols=cgen.read_symbols()
    alias=cgen.LOAD*16+symbols['DGROUP:ActorPhaseOrDemoLoopCursor']['linear']
    path=out/(mode+'.c');path.write_text(text.replace('HELPERS',helpers).replace('FIELDS',fields).replace('RECORDS',records).replace('BODY',body).replace('ALIAS_ADDRESS',str(alias)))
    return path,ranges


def literal(out,mode):
    import wholegame
    from difftest import load_dll,Regs
    from emu import MEM_SIZE
    dll=load_dll(out/'literal.dll');scenario=wholegame.scenario(ROOT/'tests/levels/one-01.txt')
    m,initial=wholegame.fixture(scenario);baseline=m.snapshot();memory=dll.ugh_memory().contents
    device=dll.ugh_device_state().contents;dev=m.device.state()
    def reset():
        C.memmove(memory,baseline,MEM_SIZE);dll.ugh_devices_reset();C.memmove(C.addressof(device),dev,len(dev))
    def set_value(name,value,width=2,index=0,module='DGROUP'):
        seg,off=m.address(module+':'+name);at=seg*16+off+index
        for i in range(width):memory[at+i]=(value>>(8*i))&255
    def get_word(name,index=0):
        seg,off=m.address('DGROUP:'+name);at=seg*16+off+index
        return memory[at]|memory[at+1]<<8
    def registers():return Regs(**{k.lower():v for k,v in initial.items()})
    def call(name,r=None):
        r=r or registers();status=getattr(dll,'c_'+name)(C.byref(r))
        if status:raise RuntimeError((name,status))
        return r
    def load(players,level):
        set_value('PlayerCount',players);set_value('PlayerArrayBytes',players*2);set_value('CurrentLevelIndex',level)
        call('LoadCurrentLevelState')
    _,_,ranges=projection();count=0
    with (out/(mode+'-literal.bin')).open('wb') as f:
        def record():
            for at,n,_ in ranges:f.write(bytes(memory[at:at+n]))
        reset()
        if mode=='passes':
            for players,levels in [(1,69),(2,81)]:
                for level in range(levels):
                    load(players,level)
                    for iteration in range(320):call('DispatchActorUpdates');record();count+=1
        elif mode=='items':
            _,symbols=cgen.read_symbols()
            for resource in item_resources():
                for operation,name in enumerate(['SpawnFallingItem','AdvanceFallingItem','LandFallingItem','ExpireOrCollectFallingItem']):
                    for variant in range(8):
                        reset();load(2,0);set_value('LevelTimer',65530);set_value('LivesRemaining',255,1);set_value('ScoreMultiplier',2,1)
                        for j in range(12):set_value('FallingItemSprites',65535,index=2*j)
                        set_value('FallingItemDescriptors',resource['word']);set_value('FallingItemCallbacks',symbols['GAME:AdvanceFallingItem']['offset'])
                        x,y,vertical,motion=1024,1024,65530 if variant==0 else 0,1 if variant==1 else 0 if variant==2 else 560
                        seg,off=m.address('DGROUP:Data_7720');base=seg*16
                        ax=memory[base+resource['word']]|memory[base+resource['word']+1]<<8
                        ay=memory[base+resource['word']+2]|memory[base+resource['word']+3]<<8
                        if operation==1:
                            motion=0
                            if variant==1:x=65024
                            if variant==2:x=10240
                            if variant==3:y=6144
                            if variant>=4:
                                x=((get_word('PlatformLeftEdges')-ax+(variant&1))*32)&65535
                                y=((get_word('PlatformHeights')-ay-1)*32)&65535;vertical=32
                        for field,value in [('FallingItemSprites',400),('FallingItemX',x),('FallingItemY',y),('FallingItemVerticalStep',vertical),
                                            ('FallingItemMotionOrLifetime',motion),('FallingItemEraseSprite',123),('FallingItemDrawX',12),
                                            ('FallingItemDrawY',13),('FallingItemPreviousDrawX',14),('FallingItemPreviousDrawY',15)]:set_value(field,value)
                        for j in range(2):
                            px,py=4096,4096
                            if variant>=3 and j==(variant&1):px=(x+(ax-10)*32)&65535;py=(y+ay*32-100)&65535
                            set_value('PlayerX32',px,index=2*j);set_value('PlayerY32',py,index=2*j)
                        r=registers();r.bx=0
                        if operation==0:
                            for j in range(12):set_value('FallingItemSprites',400 if variant==1 else 65535,index=2*j)
                            if variant==2:set_value('FallingItemSprites',65534,index=22)
                            r.bx=symbols['GAME:IgnoreExhaustedTree']['offset'];r.si=resource['word'];r.ax=1024;r.bp=2048;r.cx=65520;r.dx=123
                        call(name,r);record();count+=1
        else:
            _,symbols=cgen.read_symbols()
            for row in cases():
                reset();load(2,0);q=actor_setup(row)
                set_value('ActorDescriptors',symbols['DGROUP:Data_7720']['offset']+74*row['kind'])
                set_value('ActorUpdateOrScriptCursor',symbols['GAME:'+row['role']]['offset'])
                fields={'ActorX32':'position_x','ActorY32':'position_y','ActorPixelX':'pixel_x','ActorPixelY':'pixel_y',
                        'ActorPlatformOrScriptDone':'source','ActorDestinationPlatforms':'destination','ActorAnimationByteOffsets':'animation_offset',
                        'ActorAnimationCountdowns':'countdown','ActorPhaseOrDemoLoopCursor':'alias','ActorMotionWaitOrDemoRepeats':'repeat',
                        'ActorVerticalOrDemoPeriod':'vertical','ActorSpriteIds':'sprite','ActorOverlayOrScriptCallbacks':'overlay',
                        'PassengerQuickDeliveryCountdowns':'quick'}
                for name,key in fields.items():set_value(name,q[key])
                set_value('ActorSourcePlatformByteIndices',2*q['source']);set_value('ActorDestinationPlatformByteIndices',2*q['destination'])
                for name,value,width in [('WaterYPixels',q['water'],2),('WaterY32',q['water']*32,2),('ScoreLowWord',q['score'],4),
                                         ('ScoreMultiplier',2,1),('LivesRemaining',255,1),('LevelTimer',65530,2),('ScreenFadeStep',2,2),
                                         ('ScreenFadeLevel',256,2),('RemainingPassengerJourneys',q['remaining'],1)]:set_value(name,value,width)
                for j in range(2):
                    for name,value in [('PlayerPassengerFares',q['fare']),('PlayerMinimumFares',q['floor']),('PlayerX32',4096),('PlayerY32',4096),
                                       ('PlayerPixelX',128),('PlayerYPixels',128),('PlayerHorizontalVelocities',65500),('PlayerVerticalVelocities',120),
                                       ('PlayerPlatformIndices',65535),('PlayerCarriedKinds',0),('PlayerActionInput',q['action'])]:set_value(name,value,index=2*j)
                for j in range(12):set_value('FallingItemSprites',65535,index=2*j)
                if row['variant']==3:
                    for name,value in [('PlayerPlatformIndices',0),('PlayerPixelX',24),('PlayerYPixels',(q['water']-18)&65535),('PlayerVerticalVelocities',0)]:set_value(name,value,index=2)
                if row['role']=='ReadPassengerJourneyLeg' and row['variant']!=3:
                    cursor=get_word('ActorJourneyCursors')
                    graph=json.loads((ROOT/'metadata/object-identities.json').read_text())
                    resource=next(r for r in graph['resources'] if r['kind']=='OBJECT_JOURNEY' and r['word']<=cursor<r['word']+r['size'])
                    set_value('ActorJourneyCursors',resource['word']+resource['size']-6)
                if row['role']=='AnimatePassengerDeparture' and row['variant']==3:
                    seg,_=m.address('DGROUP:Data_7720');base=seg*16;descriptor=get_word('ActorDescriptors')
                    pointer=memory[base+descriptor+56]|memory[base+descriptor+57]<<8;frame_count=0
                    while (memory[base+pointer+2*frame_count]|memory[base+pointer+2*frame_count+1]<<8)!=65535:frame_count+=1
                    set_value('ActorAnimationByteOffsets',(2*frame_count-4)&65535)
                if row['role']=='UpdateThrownStone' and row['variant']==3:
                    seg,_=m.address('DGROUP:Data_7720');base=seg*16;descriptor=get_word('ActorDescriptors')
                    ax=memory[base+descriptor]|memory[base+descriptor+1]<<8;ay=memory[base+descriptor+2]|memory[base+descriptor+3]<<8
                    set_value('ActorX32',((get_word('PlatformLeftEdges')-ax+1)*32)&65535)
                    set_value('ActorY32',((get_word('PlatformHeights')-ay)*32)&65535)
                    set_value('ActorMotionWaitOrDemoRepeats',0);set_value('ActorVerticalOrDemoPeriod',0)
                r=registers();r.bx=0;r.di=0
                try:call(row['role'],r)
                except Exception as e:raise RuntimeError((row,e)) from e
                record();f.write(r.bx.to_bytes(2,'little'));count+=1
    required={'direct':len(cases()),'passes':48000,'items':352}[mode]
    assert count==required,(mode,count,required)
    print('literal object records',count,flush=True)


def verify(out,build=True):
    out.mkdir(parents=True,exist_ok=True);prod=out/'production'
    if build:nativebuild.build('test',prod)
    audited=json.loads((prod/'nativebuild.json').read_text())
    assert audited['manifest']==nativebuild.sha(ROOT/'metadata/native-manifest.json')
    for name,digest in audited['inputs'].items():assert nativebuild.sha(ROOT/name)==digest,'stale production source '+name
    results={}
    for mode in ['direct','passes','items']:
        folder=out/mode;folder.mkdir(exist_ok=True);code,ranges=source(folder,mode)
        exe=s7_audio.executable(code,folder,prod)
        print(run([exe,prod/'ugh.res',folder/'native.bin'],ROOT,folder,'record')['stdout'].strip(),flush=True)
        # No expected bytes or literal execution exist before this exit.
        print(run([sys.executable,__file__,'--literal',folder,'--mode',mode],ROOT,folder,'literal')['stdout'].strip(),flush=True)
        actual=(folder/'native.bin').read_bytes();expected=(folder/(mode+'-literal.bin')).read_bytes()
        size=sum(n for _,n,_ in ranges)+(2 if mode=='direct' else 0);diffs=[]
        required={'direct':len(cases()),'passes':48000,'items':352}[mode]
        if len(actual)!=required*size:diffs.append(dict(field='required_records',actual=len(actual)//size,expected=required))
        if len(actual)!=len(expected):diffs.append(dict(field='length',actual=len(actual),expected=len(expected)))
        for i in range(min(len(actual),len(expected))//size):
            at=i*size
            for address,n,name in ranges+([(0,2,'returned_actor_cursor')] if mode=='direct' else []):
                if actual[at:at+n]!=expected[at:at+n]:diffs.append(dict(record=i,case=cases()[i] if mode=='direct' else None,field=name,actual=actual[at:at+n].hex(),expected=expected[at:at+n].hex()))
                at+=n
        save(folder/'differences.json',diffs)
        results[mode]=dict(result='FAIL' if diffs else 'PASS',records=len(actual)//size,bytes_per_record=size,differences=len(diffs),first=diffs[:8])
        print(mode,results[mode],flush=True)
        if diffs:break
    if all(r['result']=='PASS' for r in results.values()):
        folder=out/'cases';folder.mkdir(exist_ok=True)
        exe=s7_audio.executable(ROOT/'verif/s7_gameplay_cases.c',folder,prod)
        print(run([exe,prod/'ugh.res'],ROOT,folder,'run')['stdout'].strip(),flush=True)
        results['focused']=dict(result='PASS')
        folder=out/'controls';folder.mkdir(exist_ok=True)
        # Observation and actual-composition defects are independent controls.
        direct=(out/'direct/direct.c').read_text()
        observer=folder/'miss-alias.c';observer.write_text('#define S7_OBJECT_MISS_ALIAS\n'+direct)
        exe=s7_audio.executable(observer,folder,prod)
        run([exe,prod/'ugh.res',folder/'miss-alias.bin'],ROOT,folder,'miss-alias')
        expected=(out/'direct/direct-literal.bin').read_bytes()
        assert (folder/'miss-alias.bin').read_bytes()!=expected,'missing alias observer escaped'
        mutant=folder/'wrong-water-motion.c'
        text=(ROOT/'native/compose_actors.c').read_text()
        anchor='case PW_VELOCITY:a->motion_or_period_word=v;break;'
        assert anchor in text
        mutant.write_text(text.replace(anchor,'case PW_VELOCITY:a->motion_or_period_word=(uint16_t)(v^1u);break;'))
        obj=folder/'mutant.o'
        run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT/'native','-I',prod,'-c',mutant,'-o',obj],ROOT,folder,'mutant-compile')
        manifest=json.loads((ROOT/'metadata/native-manifest.json').read_text())
        original=prod/('object-%02d.o'%manifest['core'].index('native/compose_actors.c'))
        sourcefile=folder/'direct.c';sourcefile.write_text(direct)
        exe=s7_audio.executable(sourcefile,folder,prod,{original:obj})
        run([exe,prod/'ugh.res',folder/'wrong-motion.bin'],ROOT,folder,'wrong-motion')
        assert (folder/'wrong-motion.bin').read_bytes()!=expected,'wrong composition water motion escaped'
        results['controls']=dict(result='PASS',detected=['missed alias publication','changed water velocity composition'])
        print('PASS 2/2 object recorder/composition controls',flush=True)
    save(out/'objects-receipt.json',dict(result='PASS' if all(r['result']=='PASS' for r in results.values()) else 'FAIL',
        scope='object-boundary owner projections; zero gameplay frame/device claim',results=results))
    return all(r['result']=='PASS' for r in results.values())


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=ROOT/'build/workers/s7-gameplay');p.add_argument('--no-build',action='store_true')
    p.add_argument('--literal',type=Path);p.add_argument('--mode',choices=['direct','passes','items'],default='direct');args=p.parse_args()
    if args.literal:literal(args.literal,args.mode)
    else:raise SystemExit(0 if verify(args.out,not args.no_build) else 1)
