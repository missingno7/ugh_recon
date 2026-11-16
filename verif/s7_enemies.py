"""Independent compiled-L1 enemy boundary recordings, not a frame certificate."""
import argparse, ctypes as C, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import cgen,nativebuild,s7_audio,s7_gameplay_objects,dataprobe
from cbuild import GCC
from job_pool import run,save

def role_names():
    return dict(re.findall(r'case (H_\w+):return G\((\w+)\);',(ROOT/'native/bridge/hazards_bridge.c').read_text()))

def cases():
    _,levels=dataprobe.levels(cgen.read_symbols()[0]);g=json.loads((ROOT/'metadata/object-identities.json').read_text())
    descriptors=sorted((r for r in g['resources'] if r['kind']=='OBJECT_ENEMY_DESCRIPTOR'),key=lambda r:r['word']);result=[]
    for level in levels:
        if level['players']!=2:continue
        for slot,enemy in enumerate(level['enemies']):
            kind=next(i for i,r in enumerate(descriptors) if r['word']==enemy[0]);view=descriptors[kind]['view']
            roles=list(dict.fromkeys(l['callback']['role'] for l in g['links'] if l['source']==view and l['kind']=='callback' and l['callback']['role']!='H_ZERO'))
            if kind==0:roles.append('H_BIRD_STOP')
            for role in roles:
                for variant in range(8):result.append(dict(level=level['number']-1,slot=slot,kind=kind,role=role,variant=variant))
    return result

def projection(audio=False):
    h,f,r=s7_gameplay_objects.projection();_,symbols=cgen.read_symbols()
    for role,name in role_names().items():
        if 'case '+role+':' not in h:h=h.replace('switch(id.enemy){','switch(id.enemy){case %s:return %d;'%(role,symbols['GAME:'+name]['offset']))
    if audio:
        def field(name,expr,width=2,delta=0):
            nonlocal f
            at=cgen.LOAD*16+symbols['SOUND:'+name]['linear']+delta
            f+='\nput(%d,%s,%d);'%(at,expr,width);r.append((at,width,name+str(delta)))
        import respack
        mz,_=cgen.read_symbols();rows=respack.inventory(mz.image,symbols)[0]
        headers=sorted((row for row in rows if row['name'].startswith('data.') and mz.image[row['image_start']:row['image_start']+4]==b'ADLX'),key=lambda row:row['image_start'])
        h+='static unsigned audio_segment(GameWorld *w,AudioCursor c){if(!c.window)return 0;'+''.join('if(c.window==w->audio_data[%d].data)return %d;'%(i,cgen.LOAD+row['image_start']//16) for i,row in enumerate(headers))+'exit(9);}\n'
        channel=[(0,'age',4),(4,'repeats',2),(6,'start.index',2),(8,'start',0),(10,'length',2),(12,'sample_mode',2),(14,'sample_rate',2),
          (16,'cursor.index',2),(18,'cursor',0),(20,'sample_half_length',2),(22,'reserved_word',2),(24,'sample_selector',2),(26,'sample_accumulator',2),
          (28,'volume',2),(30,'deadline',4),(34,'voice_count',2),(36,'first_voice',2),(38,'step_q8',2),(40,'control',2)]
        for i in range(13):
            for offset,member,width in channel:
                expr='w->audio.channels[%d].%s'%(i,member)
                field('AudioChannelStates',expr if width else 'audio_segment(w,%s)'%expr,width or 2,42*i+offset)
        for name,member in [('AdlibVoiceStates','live'),('SavedAdlibVoiceStates','displaced'),('ScannedAdlibVoiceStates','scanned')]:
            for i in range(9):
                for j in range(12):field(name,'w->audio.%s[%d].instrument[%d]'%(member,i,j),1,20*i+j)
                for j,m in enumerate(['volume','gain','owner','frequency']):field(name,'w->audio.%s[%d].%s'%(member,i,m),2,20*i+12+2*j)
        for name,member,width in [('AdlxPlaybackGuard','playback_guard',2),('AdlxTimerPeriod','timer_period',2),('AdlxTickCount','ticks',4),('MusicTicksPerUnit','ticks_per_unit',2),('MainAdlxTimeOrigin','time_origin',4),('ScannedMusicClockTicks','scanned_ticks',4),('MainAdlxPlaying','playing',2),('MainAdlxSectionLoopEnabled','section_loop_enabled',2),('MusicTrackVolume','track_volume',2),('ReservedAdlibChannelCount','reserved_voices',2),('CurrentAdlxSlot','current_channel',2)]:field(name,'w->audio.'+member,width)
        field('SoundDeviceBits','w->audio_reset.devices')
    return h,f,r

def setup(row):
    v=row['variant']
    result=dict(x32=65024 if v==2 else 1024,y32=6140 if v==3 else 1024,platform=0,
      speed=[24,65512,32768,0,24,65512,24,0][v],initial_delay=7,counter=[1,0,32768,2,1,2,350,65535][v],
      animation_offset=[65534,0,4,1,0,0,0,65534][v],countdown=[1,0,32768,1,1,1,1,32768][v],
      sprite=123,erase_sprite=456,draw_x=12,draw_y=13,previous_x=14,previous_y=15,
      direction_or_target_word=(v&1)*(1 if row['kind']==0 else 2),sound_handle_word=65535)
    if row['role']=='H_DINO_FORCE' and v==3:result['animation_offset']=4
    if row['kind']==0 and v==7:result['direction_or_target_word']=32768
    if row['kind']==1 and v==4:result['platform']=32768
    return result

DIRECT=r'''
static const struct Case {unsigned level,slot,kind;HazardEntry role;unsigned variant;} cases[]={CASES};
for(unsigned ci=0;ci<sizeof cases/sizeof *cases;ci++){
 const struct Case *c=cases+ci;unsigned v=c->variant,n=c->slot;
 reset(w,&s);w->run.level=c->level;if(game_session_load(w,&s)!=GS_OK)exit(3);
 NativeEnemySlot *a=w->enemies.slot+n;
 static const uint16_t speeds[]={24,65512,32768,0,24,65512,24,0},counters[]={1,0,32768,2,1,2,350,65535},cursors[]={65534,0,4,1,0,0,0,65534},ticks[]={1,0,32768,1,1,1,1,32768};
 a->x32=v==2?65024:1024;a->y32=v==3?6140:1024;a->platform=0;a->speed=speeds[v];a->initial_delay=7;
 a->counter=counters[v];a->animation_offset=cursors[v];a->countdown=ticks[v];a->sprite=123;a->erase_sprite=456;
 a->draw_x=12;a->draw_y=13;a->previous_x=14;a->previous_y=15;a->direction_or_target_word=(v&1)*(c->kind==0?1:2);a->sound_handle_word=65535;
 if(c->role==H_DINO_FORCE&&v==3)a->animation_offset=4;
 if(c->kind==0&&v==7)a->direction_or_target_word=32768;
 if(c->kind==1&&v==4)a->platform=32768;
 w->session.enemy_callback[n]=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ENEMY,.enemy=c->role};
 if(c->kind==0){ObjectGraphLink l;if(game_object_link(w->session.enemy_descriptor[n],34,&l)!=GS_OK)exit(3);w->session.enemy_list[n]=l.resource;}
 if(c->kind==3&&v==6)w->session.enemy_list[n].position=c->role==H_TREE_RELEASE?16:18;
 if(v==6&&c->kind!=3){ObjectGraphLink l;unsigned member=c->role==H_BIRD_FLIGHT?34:c->role==H_TRIO_IMPACT?50+a->direction_or_target_word:c->role==H_TRIO_RECOVER?42+a->direction_or_target_word:34;
 if(game_object_link(w->session.enemy_descriptor[n],member,&l)==GS_OK&&l.kind==OBJECT_LINK_RESOURCE){GSBytes b;if(game_object_resource(&s,l.resource,&b)!=GS_OK)exit(3);a->animation_offset=(uint16_t)(b.size-4);}}
 w->run.score=4294967280u;w->run.fade_step=2;w->run.fade_level=256;w->run.water_y=200;w->run.record.water_fixed=6400;
 w->session.actor_end[0]=0;w->session.actor_end[1]=1;GameActorSlot *stone=w->actors.slot;
 if(game_object_actor_type(ACTOR_STONE,&stone->descriptor)!=GS_OK)exit(3);stone->callback=(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ACTOR,.actor=ACTOR_CALLBACK_UpdateThrownStone};
 stone->position=(ObjectPosition){v==4?a->x32:4096,v==4?a->y32:4096};stone->motion_or_period_word=v==7?32768:64;stone->delay_or_repeat_word=65520;
 if(c->kind==3&&v==7){w->actors.slot[15].position=(ObjectPosition){777,888};w->actors.slot[15].motion_or_period_word=32771;w->actors.slot[15].delay_or_repeat_word=48879;}
 for(unsigned j=0;j<2;j++){NativePlayer *p=w->session.players.player+j;p->fixed_x=v==5?a->x32:4096;p->fixed_y=v==5?a->y32:4096;p->platform=v>=5?0:65535;p->velocity_x=65495;p->velocity_y=128;}
 for(unsigned j=0;j<12;j++)w->items.slot[j].sprite=65535;
 GSStatus status=game_enemy_call(w,&s,n,(ObjectCallbackIdentity){.kind=OBJECT_CALLBACK_ENEMY,.enemy=c->role},c->kind==3&&v==7?15:0);
 if(status!=GS_OK){fprintf(stderr,"case %u role %u status %u\n",ci,c->role,status);exit(3);}record(w,f);case_index++;
}
'''
PASSES='''reset(w,&s);for(unsigned level=0;level<81;level++){w->run.level=level;if(game_session_load(w,&s)!=GS_OK)exit(3);
for(unsigned j=0;j<800;j++){GSStatus status=game_enemies_update(w,&s);if(status!=GS_OK){fprintf(stderr,"pass %u %u status %u\\n",level,j,status);exit(3);}record(w,f);case_index++;}}'''
RENDER='''for(unsigned level=0;level<81;level++)for(unsigned variant=0;variant<4;variant++)for(unsigned operation=0;operation<3;operation++){
reset(w,&s);w->run.level=level;if(game_session_load(w,&s)!=GS_OK)exit(3);
w->pages.height=192;w->pages.draw=0;w->pages.fixed=14400;w->pages.background=28800;
for(unsigned j=0;j<5;j++){NativeEnemySlot *a=w->enemies.slot+j;a->sprite=variant==0?65535:variant==1?232:123;a->erase_sprite=variant==0?65535:232;
a->x32=variant==2?65504:1024;a->y32=variant==2?65504:variant==3?6144:1024;a->draw_x=12;a->draw_y=13;a->previous_x=14;a->previous_y=15;}
GSStatus status=operation==0?game_enemies_erase(w,&s):operation==1?game_enemies_draw_back(w,&s):game_enemies_draw_front(w,&s);
if(status!=GS_OK)exit(3);record(w,f);case_index++;}'''

def source(out,mode):
    h,f,r=projection(mode=='audio');records='\n'.join('if(fwrite(observation+%d,1,%d,f)!=%d)exit(9);'%(at,n,n) for at,n,_ in r)
    body={'direct':DIRECT,'audio':DIRECT,'passes':PASSES,'render':RENDER}[mode]
    if mode in ('direct','audio'):body=body.replace('CASES',','.join('{%d,%d,%d,%s,%d}'%(c['level'],c['slot'],c['kind'],c['role'],c['variant']) for c in cases()))
    if mode=='audio':body=body.replace('GSStatus status=game_enemy_call','w->audio_reset.devices=1;GSStatus status=game_enemy_call')
    text=r'''
#include "native/compose_enemies.h"
#include "native/compose_session.h"
#include "native/game_object_data.h"
#include "port/resources.h"
#include "port/test/backend.h"
#include "resource_manifest.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t observation[0x110000];
static void put(unsigned at,unsigned v,unsigned n){for(unsigned i=0;i<n;i++)observation[at+i]=(uint8_t)(v>>(8*i));}
HELPERS
static void record(GameWorld *w,FILE *f){FIELDS
#ifdef S7_ENEMY_MISS_COUNTER
put(COUNTER_ADDRESS,0,2);
#endif
RECORDS
}
static void reset(GameWorld *w,GameServices *s){if(game_world_construct(w,s)!=GS_OK)exit(3);w->run.configuration.players=2;w->run.configuration.player_bytes=4;}
int main(int argc,char **argv){if(argc!=3)return 2;GSResourcePack pack;char error[256];
if(gs_resources_open(&pack,argv[1],port_required_resources,PORT_REQUIRED_COUNT,error,sizeof error)!=GS_OK)return 2;
GameWorld *w=calloc(1,sizeof *w);GSTestBackend *b=calloc(1,sizeof *b);if(!w||!b)return 2;
gs_test_init(b);b->resources=gs_resources_operations();b->resource_context=&pack;GameServices s=gs_test_services(b);
FILE *f=fopen(argv[2],"wb");if(!f)return 2;unsigned case_index=0;
BODY
fclose(f);free(w);free(b);gs_resources_close(&pack);printf("enemy records %u\n",case_index);return 0;}
'''
    _,symbols=cgen.read_symbols();address=cgen.LOAD*16+symbols['DGROUP:EnemyStateCounters']['linear']
    p=out/(mode+'.c');p.write_text(text.replace('HELPERS',h).replace('FIELDS',f).replace('RECORDS',records).replace('BODY',body).replace('COUNTER_ADDRESS',str(address)));return p,r

def literal_library(out):
    cgen.generate();scene=(ROOT/'c/scene.c').read_text()
    at=scene.index('r->ax=RX(EnemySpriteIds',scene.index('EXPORT int c_RunGameFromPassword'))
    start=scene.rfind('        r->si=logic(r,0,16);',0,at);stop=scene.index('        r->si=22;',at)
    extra='\nEXPORT int s7_enemy_erase(Regs *r){\n'+scene[start:stop]+'return UGH_OK;}\nEXPORT int s7_enemy_back(Regs *r){return draw_enemy_layer(r,0);}\nEXPORT int s7_enemy_front(Regs *r){return draw_enemy_layer(r,1);}\n'
    copy=out/'scene.c';copy.write_text(scene+extra);sources=[p for p in sorted((ROOT/'c').glob('*.c')) if p.name!='scene.c']+[copy]
    dllpath=out/'literal.dll';run([GCC,'-shared','-O2','-std=c11','-Wall','-Wextra','-Werror','-fwrapv','-I',ROOT/'c','-o',dllpath,*sources],ROOT,out,'literal-compile')
    from emu import MEM_SIZE
    from difftest import DeviceState
    dll=C.CDLL(str(dllpath));dll.ugh_memory.restype=C.POINTER(C.c_uint8*MEM_SIZE);dll.ugh_device_state.restype=C.POINTER(DeviceState);return dll

def literal(out,mode):
    import wholegame
    from difftest import Regs
    from emu import MEM_SIZE
    dll=literal_library(out);m,initial=wholegame.fixture(wholegame.scenario(ROOT/'tests/levels/one-01.txt'))
    memory=dll.ugh_memory().contents;device=dll.ugh_device_state().contents;baseline=m.snapshot();dev=m.device.state()
    def reset():C.memmove(memory,baseline,MEM_SIZE);dll.ugh_devices_reset();C.memmove(C.addressof(device),dev,len(dev))
    def setv(name,value,width=2,index=0,module='DGROUP'):
        seg,off=m.address(module+':'+name);at=seg*16+off+index
        for i in range(width):memory[at+i]=(value>>(8*i))&255
    def getv(name,index=0):
        seg,off=m.address('DGROUP:'+name);at=seg*16+off+index;return memory[at]|memory[at+1]<<8
    def reg():return Regs(**{k.lower():v for k,v in initial.items()})
    def call(name,r=None):
        status=getattr(dll,name)(C.byref(r or reg()))
        if status:raise RuntimeError((name,status))
    def load(level):setv('PlayerCount',2);setv('PlayerArrayBytes',4);setv('CurrentLevelIndex',level);call('c_LoadCurrentLevelState')
    _,_,ranges=projection(mode=='audio');_,symbols=cgen.read_symbols();graph=json.loads((ROOT/'metadata/object-identities.json').read_text());count=0
    with (out/'literal.bin').open('wb') as f:
        def record():
            for at,n,_ in ranges:f.write(bytes(memory[at:at+n]))
        if mode=='passes':
            reset()
            for level in range(81):
                load(level)
                for j in range(800):call('c_DispatchEnemyStates');record();count+=1
        elif mode=='render':
            for level in range(81):
                for variant in range(4):
                    for op in range(3):
                        reset();load(level)
                        for name,value in [('PlayfieldHeight',192),('DrawPagePointer',0),('FixedVgaPagePointer',14400),('BackgroundPagePointer',28800)]:setv(name,value,module='GAME')
                        for j in range(5):
                            for name,value in [('EnemySpriteIds',65535 if variant==0 else 232 if variant==1 else 123),('EnemyEraseSprite',65535 if variant==0 else 232),('EnemyX32',65504 if variant==2 else 1024),('EnemyY32',65504 if variant==2 else 6144 if variant==3 else 1024),('EnemyDrawX',12),('EnemyDrawY',13),('EnemyPreviousDrawX',14),('EnemyPreviousDrawY',15)]:setv(name,value,index=2*j)
                        call(['s7_enemy_erase','s7_enemy_back','s7_enemy_front'][op]);record();count+=1
        else:
            fields=dict(platform='EnemyPlatformIndices',x32='EnemyX32',y32='EnemyY32',initial_delay='EnemyInitialDelays',speed='EnemyHorizontalSpeeds',counter='EnemyStateCounters',animation_offset='EnemyAnimationByteOffsets',countdown='EnemyAnimationCountdowns',sprite='EnemySpriteIds',erase_sprite='EnemyEraseSprite',draw_x='EnemyDrawX',draw_y='EnemyDrawY',previous_x='EnemyPreviousDrawX',previous_y='EnemyPreviousDrawY',direction_or_target_word='EnemyDirectionOrTargetPlayer',sound_handle_word='EnemyFlightSoundHandles')
            for i,row in enumerate(cases()):
                reset();load(row['level']);q=setup(row);v=row['variant'];n=row['slot'];kind=row['kind']
                for field,val in q.items():setv(fields[field],val,index=2*n)
                setv('EnemyStateCallbacks',symbols['GAME:'+role_names()[row['role']]]['offset'],index=2*n)
                desc=getv('EnemyDescriptors',2*n);seg,_=m.address('DGROUP:Data_7630');base=seg*16
                def word(at):return memory[base+at]|memory[base+at+1]<<8
                if kind==0:setv('EnemyAnimationOrDropLists',word(desc+34),index=2*n)
                if kind==3 and v==6:setv('EnemyAnimationOrDropLists',getv('EnemyAnimationOrDropLists',2*n)+(16 if row['role']=='H_TREE_RELEASE' else 18),index=2*n)
                if v==6 and kind!=3:
                    member=34 if row['role']=='H_BIRD_FLIGHT' else 50+q['direction_or_target_word'] if row['role']=='H_TRIO_IMPACT' else 42+q['direction_or_target_word'] if row['role']=='H_TRIO_RECOVER' else 34
                    resource=next((r for r in graph['resources'] if r['word']==word(desc+member) and r['kind']=='OBJECT_ANIMATION'),None)
                    if resource:setv('EnemyAnimationByteOffsets',resource['size']-4,index=2*n)
                for name,value,width in [('ScoreLowWord',4294967280,4),('ScreenFadeStep',2,2),('ScreenFadeLevel',256,2),('WaterYPixels',200,2),('WaterY32',6400,2)]:setv(name,value,width)
                setv('ActorDescriptors',symbols['DGROUP:Data_78DC']['offset']);setv('ActorDescriptors',65535,index=2);setv('ActorUpdateOrScriptCursor',symbols['GAME:UpdateThrownStone']['offset'])
                for name,value in [('ActorX32',q['x32'] if v==4 else 4096),('ActorY32',q['y32'] if v==4 else 4096),('ActorVerticalOrDemoPeriod',32768 if v==7 else 64),('ActorMotionWaitOrDemoRepeats',65520)]:setv(name,value)
                if kind==3 and v==7:
                    for name,value in [('ActorX32',777),('ActorY32',888),('ActorVerticalOrDemoPeriod',32771),('ActorMotionWaitOrDemoRepeats',48879)]:setv(name,value,index=30)
                for j in range(2):
                    for name,value in [('PlayerX32',q['x32'] if v==5 else 4096),('PlayerY32',q['y32'] if v==5 else 4096),('PlayerPlatformIndices',0 if v>=5 else 65535),('PlayerHorizontalVelocities',65495),('PlayerVerticalVelocities',128)]:setv(name,value,index=2*j)
                for j in range(12):setv('FallingItemSprites',65535,index=2*j)
                if mode=='audio':setv('SoundDeviceBits',1,module='SOUND')
                r=reg();r.bx=2*n;r.di=30 if kind==3 and v==7 else 0;r.si=desc
                try:call('c_'+role_names()[row['role']],r)
                except Exception as e:raise RuntimeError((i,row,e)) from e
                record();count+=1
    print('literal enemy records',count,flush=True)

def verify(out,build=True):
    out.mkdir(parents=True,exist_ok=True);prod=out/'production'
    if build:nativebuild.build('test',prod)
    audited=json.loads((prod/'nativebuild.json').read_text());assert audited['manifest']==nativebuild.sha(ROOT/'metadata/native-manifest.json')
    for name,digest in audited['inputs'].items():assert nativebuild.sha(ROOT/name)==digest,'stale source '+name
    results={};direct_cases=cases()
    for mode in ['direct','passes','render','audio']:
        folder=out/mode;folder.mkdir(exist_ok=True);code,ranges=source(folder,mode);exe=s7_audio.executable(code,folder,prod)
        print(run([exe,prod/'ugh.res',folder/'native.bin'],ROOT,folder,'record')['stdout'].strip(),flush=True)
        print(run([sys.executable,__file__,'--literal',folder,'--mode',mode],ROOT,folder,'literal')['stdout'].strip(),flush=True)
        actual=(folder/'native.bin').read_bytes();expected=(folder/'literal.bin').read_bytes();size=sum(n for _,n,_ in ranges);diffs=[]
        required={'direct':len(direct_cases),'audio':len(direct_cases),'passes':81*800,'render':81*4*3}[mode]
        if len(actual)!=required*size or len(actual)!=len(expected):diffs.append(dict(field='length',actual=len(actual),expected=len(expected),required=required*size))
        for i in range(min(len(actual),len(expected))//size):
            at=i*size
            if actual[at:at+size]==expected[at:at+size]:continue
            for address,n,name in ranges:
                if actual[at:at+n]!=expected[at:at+n] and len(diffs)<1000:diffs.append(dict(record=i,case=direct_cases[i] if mode in ('direct','audio') else None,field=name,actual=actual[at:at+n].hex(),expected=expected[at:at+n].hex()))
                at+=n
        save(folder/'differences.json',diffs);results[mode]=dict(result='FAIL' if diffs else 'PASS',records=len(actual)//size,bytes_per_record=size,differences=len(diffs),first=diffs[:8]);print(mode,results[mode],flush=True)
        if diffs:break
    if all(r['result']=='PASS' for r in results.values()):
        folder=out/'cases';folder.mkdir(exist_ok=True);exe=s7_audio.executable(ROOT/'verif/s7_enemies_cases.c',folder,prod)
        print(run([exe,prod/'ugh.res'],ROOT,folder,'run')['stdout'].strip(),flush=True);results['focused']=dict(result='PASS')
        folder=out/'controls';folder.mkdir(exist_ok=True);direct=(out/'direct/direct.c').read_text();p=folder/'miss-counter.c';p.write_text('#define S7_ENEMY_MISS_COUNTER\n'+direct)
        exe=s7_audio.executable(p,folder,prod);run([exe,prod/'ugh.res',folder/'miss.bin'],ROOT,folder,'miss-counter');expected=(out/'direct/literal.bin').read_bytes();assert (folder/'miss.bin').read_bytes()!=expected
        mutant=folder/'wrong-enemy.c';text=(ROOT/'native/compose_enemies.c').read_text();anchor='case HW_COUNTER:a->counter=v;break;';assert anchor in text
        mutant.write_text(text.replace(anchor,'case HW_COUNTER:a->counter=(uint16_t)(v^1u);break;'));obj=folder/'mutant.o'
        run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT/'native','-I',prod,'-c',mutant,'-o',obj],ROOT,folder,'mutant-compile')
        manifest=json.loads((ROOT/'metadata/native-manifest.json').read_text());original=prod/('object-%02d.o'%manifest['core'].index('native/compose_enemies.c'))
        p=folder/'direct.c';p.write_text(direct);exe=s7_audio.executable(p,folder,prod,{original:obj});run([exe,prod/'ugh.res',folder/'wrong.bin'],ROOT,folder,'wrong-counter');assert (folder/'wrong.bin').read_bytes()!=expected
        results['controls']=dict(result='PASS',detected=['missing counter observer','changed enemy counter publication'])
    save(out/'enemies-receipt.json',dict(result='PASS' if all(r['result']=='PASS' for r in results.values()) else 'FAIL',scope='enemy boundary owner projections; zero complete gameplay frame claim',results=results))
    return all(r['result']=='PASS' for r in results.values())

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=ROOT/'build/workers/s7-enemies');p.add_argument('--no-build',action='store_true');p.add_argument('--literal',type=Path);p.add_argument('--mode',choices=['direct','passes','render','audio'],default='direct');a=p.parse_args()
    if a.literal:literal(a.literal,a.mode)
    else:raise SystemExit(0 if verify(a.out,not a.no_build) else 1)
