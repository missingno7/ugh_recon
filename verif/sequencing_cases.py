"""Compiled actual-C scalar slices, complete record pairs and full-RAM parents."""
import ctypes as C,json,subprocess,sys
from closure_support import ROOT,compile_c,receipt,save
from sequencing_build import OUT
from sequencing_proof import common,body
from session_record_proof import KEYS,source

PREFIX='''#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static unsigned domain,axis;static unsigned long long comparisons;
static unsigned random_state=0x925731ab;
static uint16_t random_word(void){random_state^=random_state<<13;random_state^=random_state>>17;random_state^=random_state<<5;return (uint16_t)random_state;}
static void fill(void *p,size_t n){unsigned char *a=p;while(n--)*a++=(unsigned char)random_word();}
#define __CPROVER_assume(c) do{if(!(c))return;}while(0)
'''
CHECK='#define CHECK(c,m) do{if(!(c)){fprintf(stderr,"FAIL %s domain=%u axis=%u\\n",m,domain,axis);exit(3);}}while(0)'
def executable(folder,name,code,inputs):
    f=folder/(name+'.c');f.write_text(code);exe=folder/(name+'.exe');r=compile_c([f],exe,[ROOT/'c',ROOT/'native'],['-Wno-unused-function','-Wno-unused-variable','-Wno-unused-but-set-variable']);run=subprocess.run([str(exe)],capture_output=True,text=True);assert run.returncode==0,run.stdout+run.stderr
    r['maintained_inputs']=receipt([],inputs)['inputs'];r['stdout']=run.stdout;save(folder/(name+'.json'),r);print(run.stdout.strip(),flush=True);return r
def scalars(folder):
    keys=['loader-scalar','display-byte','display-score','password'];c=PREFIX+common().replace('#define CHECK(c,m) __CPROVER_assert((c),(m))',CHECK)
    for key in keys:
        b=body(key).replace('int main(void)','static void case_'+key.replace('-','_')+'(void)').replace('return 0;}','comparisons++;return;}')
        b=b.replace('uint16_t v,repeated;','uint16_t v=(uint16_t)domain,repeated=random_word();').replace('uint8_t input;','uint8_t input=(uint8_t)domain;').replace('uint32_t input;','uint32_t input=axis?((uint32_t)domain<<16)|random_word():((uint32_t)random_word()<<16)|domain;')
        b=b.replace('uint8_t candidate,editor;uint16_t length,misses,level;','uint8_t candidate=(uint8_t)domain,editor=(uint8_t)(domain>>8);uint16_t length=(uint16_t)domain,misses=(uint16_t)domain,level=(uint16_t)domain;')
        b=b.replace('uint16_t players;','uint16_t players=(uint16_t)domain;')
        b=b.replace('Regs regs,*r=&regs;','Regs regs={0},*r=&regs;');c+=b
    c+='int main(void){for(axis=0;axis<2;axis++)for(domain=0;domain<65536;domain++){case_loader_scalar();case_display_score();if(!axis){case_password();if(domain<256)case_display_byte();}}printf("PASS %llu actual-C scalar comparisons; all word slices, every byte pair and all cached bytes\\n",comparisons);return 0;}'
    return executable(folder,'scalars',c,[ROOT/'native/session.c',ROOT/'native/session.h',ROOT/'native/lifecycle.c',ROOT/'native/lifecycle.h',ROOT/'c/render.c',ROOT/'c/scene.c',ROOT/'verif/sequencing_cases.py',ROOT/'verif/sequencing_proof.py'])
def records(folder):
    rows=[]
    for key in KEYS:
        c=source(key,'output').replace('#define CHECK(c,m) __CPROVER_assert((c),(m))',CHECK)
        c=c.replace('int main(void)','static void compare_record(void)').replace('Memory initial;','Memory initial;fill(&initial,sizeof(initial));if(axis<sizeof(initial)/2){uint16_t v=(uint16_t)domain;memcpy((unsigned char *)&initial+axis*2,&v,2);}')
        c=c.replace('Regs r;r.di=0;','Regs r;fill(&r,sizeof(r));r.di=0;')
        # Fixed-kind profiles still enumerate every payload word. The actor
        # profile additionally admits all descriptor identities and sentinels.
        forced=dict(tree='Data_76E4',bird='Data_7630',dino='Data_76A8').get(key)
        if forced:c=c.replace('memory=initial;',f'initial.words[0]=D({forced});memory=initial;',1)
        if key=='actor':c=c.replace('memory=initial;','if(axis!=27 && !(domain&3u))initial.words[0]=D(Data_78DC);memory=initial;',1)
        c=c.replace('return 0;}\n','comparisons++;return;}\n') if False else c
        pos=c.rindex('return 0;}');c=c[:pos]+c[pos:].replace('return 0;}','comparisons++;return;}',1)
        c=PREFIX+c+'int main(void){for(axis=0;axis<sizeof(Memory)/2;axis++)for(domain=0;domain<65536;domain++)compare_record();printf("PASS %llu '+key+' actual-C record scalar slices\\n",comparisons);return 0;}'
        rows.append(executable(folder,key,c,[ROOT/'native/session.c',ROOT/'native/session.h',ROOT/'native/bridge/session_bridge.c',ROOT/'verif/session_record_proof.py',ROOT/'verif/session_loader.py',ROOT/'c/render.c',ROOT/'verif/sequencing_cases.py']))
    return rows
def parents():
    sys.path.insert(0,str(ROOT/'tools'));import difftest,nbuild,contacts_reference
    from emu import DATA_SEG
    contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True)
    j=json.loads((OUT/'build.json').read_text());dll=nbuild.load_l1(j['command'][j['command'].index('-o')+1]);m=difftest.Machine();mem=dll.ugh_memory().contents;dev=dll.ugh_device_state().contents
    names=set(j['entries']);cases=[]
    for suite in ['menu','video','render','scene','items_water']:
        cases += [case for case in difftest.load_suite(suite).CASES if case.routine.split(':')[1] in names]
    for high_icon in [0,0x8000]:
        base=difftest.load_suite('render').synthetic_level(0)
        def pool(m,base=base,high_icon=high_icon):
            base.setup(m)
            def put(at,words):m.write(DATA_SEG,at,b''.join((v&65535).to_bytes(2,'little') for v in words))
            platforms=[];actors=[];enemies=[]
            kinds=[m.off('DGROUP:'+n) for n in ['Data_76E4','Data_7630','Data_76A8']]
            for i in range(15):
                platforms += [i,319-i,(i*0x1001)&65535,0xff00+i,0x7ff0+i,32+i,high_icon+i,0xa55a]
                actors += [m.off('DGROUP:Data_78DC') if i&1 else 0x7400,i,0x7ff0+i]
                if i%4==0:enemies += [kinds[0],i,0x8000+i]
                elif i%4==1:enemies += [kinds[1],0xa55a,0x8000+i,0xffff-i]
                elif i%4==2:enemies += [kinds[2],0xffff-i,0x8000+i,0xa55a,0x5aa5]
                else:enemies += [0x7400,i,0xa55a,0x8000+i]
            put(0x7100,platforms+[0x8000]);put(0x7200,actors+[0xffff]);put(0x7300,enemies+[0xffff])
        cases.append(difftest.Case(f'full15-platform/actor/enemy prefixes icon high={high_icon:04x}','GAME:LoadCurrentLevelState',setup=pool,regs=dict(DS=DATA_SEG),flags=0x602))
    for name in ['InitializeAdLibSound','FadeAndShutdownSound']:
        for bits in [0,1,2,3]:
            for initialized in [0,1,0xffff]:
                def setup(m,bits=bits,initialized=initialized):
                    m.ww('SOUND:SoundDeviceBits',bits);m.ww('C:SoundSystemInitialized',initialized);m.wb('SOUND:AdlibInitAttempted',1)
                cases.append(difftest.Case(f'{name} retained device bits={bits} initialized={initialized}', 'GAME:'+name,setup=setup,regs=dict(DS=DATA_SEG)))
    rows=[];observer_type=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs));dll.ugh_set_entry_observer.argtypes=[observer_type]
    for case in cases:
        m.reset()
        if case.setup:case.setup(m)
        registers=m.prepare(case.routine,case.regs,case.kind,case.args,case.flags);initial=m.snapshot();device=m.device.state();observations=[]
        for prefix in ['l1_','c_']:
            C.memmove(mem,initial,difftest.MEM_SIZE);dll.ugh_devices_reset();C.memmove(C.addressof(dev),device,len(device));stream=[]
            @observer_type
            def observe(seg,off,regs):
                r=regs.contents;address=((r.ss<<4)+r.sp)&0xfffff
                stream.append((seg,off,bytes(r),bytes(mem[address:address+4])))
            dll.ugh_set_entry_observer(observe)
            r=difftest.Regs(**{k.lower():v for k,v in registers.items()});f=getattr(dll,prefix+case.routine.split(':')[1]);f.argtypes=[C.POINTER(difftest.Regs)];f.restype=C.c_int;status=f(C.byref(r))
            observations.append((status,bytes(r),bytes(mem),C.string_at(C.addressof(dev),C.sizeof(dev)),stream))
        assert observations[0]==observations[1],case.title
        entries=observations[1][4];counts={}
        for name in ['RespawnRainParticle','AdvanceRainParticles','NextRandomBelowAx']:
            segment,offset=m.seg('GAME:'+name),m.off('GAME:'+name);counts[name]=sum(seg==segment and off==offset for seg,off,regs,stack in entries)
        loader=m.off('GAME:LoadCurrentLevelState')
        counts['direct_loader_respawns']=sum(seg==m.seg('GAME:RespawnRainParticle') and off==m.off('GAME:RespawnRainParticle') and int.from_bytes(stack[:2],'little')==(loader+0x2b0)&65535 for seg,off,regs,stack in entries)
        counts['direct_loader_prewarm']=sum(seg==m.seg('GAME:AdvanceRainParticles') and off==m.off('GAME:AdvanceRainParticles') and int.from_bytes(stack[:2],'little')==(loader+0x2bb)&65535 for seg,off,regs,stack in entries)
        if case.routine=='GAME:LoadCurrentLevelState' and counts['direct_loader_prewarm']:assert counts['direct_loader_respawns']==193 and counts['direct_loader_prewarm']==577
        rows.append(dict(case=case.title,entry=case.routine,result='PASS',status=observations[1][0],service_entries=len(entries),rain_counts=counts))
    dll.ugh_set_entry_observer(observer_type());print('PASS',len(rows),'complete RAM/register/device/ordered-service parent pairs',flush=True);return rows,j
def main():
    folder=OUT/'cases';folder.mkdir(parents=True,exist_ok=True);a=scalars(folder);b=records(folder);pairs,build=parents()
    save(OUT/'cases.json',receipt(['python','verif/sequencing_cases.py'],[__file__],result='PASS',scalars=a,records=b,parents=pairs,build=build))
if __name__=='__main__':main()
