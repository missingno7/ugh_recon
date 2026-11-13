"""Reproduce demo enumeration, resource projection and actual-C proofs."""
import argparse,ctypes as C,json,struct,sys,time
from pathlib import Path
from closure_support import ROOT,receipt,save,cbmc,function
from demo_build import OUT,build,SOURCES
import contacts_reference
contacts_reference.OUT=OUT/'reference'
from contacts_reference import prepare_reference,expanded_image
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,dataprobe
from common import MZ

def enumerate_cases(local=False):
    plain=prepare_reference(local=local);image=expanded_image(local=local)
    dll=nbuild.load_l1(build());machine=difftest.Machine();machine.reset()
    memory=dll.ugh_memory().contents;C.memmove(memory,machine.snapshot(),len(memory));dll.ugh_devices_reset()
    start=time.perf_counter();checks=dll.demo_alias_checks();assert checks==126,checks
    C.memmove(memory,machine.snapshot(),len(memory))
    mz=MZ(image.read_bytes());_,orders=dataprobe.levels(mz);d=mz.image[0x5c090:];placements=0
    for entry in orders:
        table=0x3349 if entry['players']==1 else 0x33d5
        record=struct.unpack_from('<H',d,table+2*(entry['number']-1))[0]
        before=bytes(memory);n=dll.demo_resource_checks(record,len(entry['actors']))
        assert n==len(entry['actors']),(entry['number'],n)
        assert bytes(memory)==before;placements+=n
    composition=difftest.load_suite('menu').composition_fixture
    machine.reset();composition(machine);C.memmove(memory,machine.snapshot(),len(memory))
    dll.ugh_devices_reset();cross=dll.demo_cross_mode();assert cross==1,cross
    C.memmove(memory,machine.snapshot(),len(memory))
    words=dll.demo_word_cases();assert words==262400,words
    C.memmove(memory,machine.snapshot(),len(memory))
    steps=dll.demo_enumerate_scripts();assert steps>0,steps
    facts=resource_facts(image)
    save(OUT/'enumeration.json',receipt(['python','verif/demo_evidence.py','enumerate'],
        [*SOURCES,ROOT/'verif/demo_harness.c',Path(__file__),plain,image],result='PASS',
        alias_checks=checks,level_entries=len(orders),placements=placements,cross_mode=cross,word_cases=words,script_ticks=steps,resources=facts,seconds=time.perf_counter()-start,
        audit=list((C.c_uint32*6).in_dll(dll,'demo_audit')),build=json.loads((OUT/'build.json').read_text())))
    print('PASS scripts',len(facts['scripts']),'ticks',steps,'alias checks',checks,flush=True)

def resource_facts(image):
    mz=MZ(image.read_bytes());d=mz.image[0x5c090:]
    def w(p):return struct.unpack_from('<H',d,p)[0]
    scripts=[];vectors=[]
    for table,limit in zip([0x1020,0x1792,0x1e40,0x24de],[0x1792,0x1e40,0x24de,0x2614]):
        starts=[];p=table
        while w(p)!=65535:starts.append(w(p));p+=2
        vectors.append(dict(vector=f'{table:04X}',headers=[f'{p:04X}' for p in starts]))
        for base,end in zip(sorted(starts),sorted(starts)[1:]+[limit]):
            p=base+8;ops=[]
            while p<end:
                op=w(p);ops.append(dict(offset=p-base-8,word=op));p+=4 if op<32768 else 2
            assert p==end and w(end-2)==32768
            scripts.append(dict(header=f'{base:04X}',initial=list(struct.unpack_from('<hh',d,base)),period=w(base+4),callback=f'{w(base+6):04X}',code_bytes=end-base-8,instructions=ops))
    assert len(scripts)==28
    save(OUT/'shipped-scripts.json',dict(vectors=vectors,scripts=scripts))
    return dict(vectors=vectors,scripts=scripts)

def prove(mode,timeout=60,negative=False):
    folder=OUT/('cbmc_'+mode+('_negative' if negative else ''));folder.mkdir(parents=True,exist_ok=True)
    native=ROOT/'native/demo_core.c';text=f'#include "{(ROOT/"c/ugh.h").as_posix()}"\n'
    # Actual L1 interpreter, with its ordinary RAM and callback boundaries
    # replaced only by the harness's normalized read/write/observation shim.
    raw=(ROOT/'c/demo_scripts.c').read_text()
    text+='uint16_t demo_read16(uint16_t,uint16_t); uint8_t demo_read8(uint16_t,uint16_t); void demo_write16(uint16_t,uint16_t,uint16_t);\n'
    text+='#define rd16 demo_read16\n#define rd8 demo_read8\n#define wr16 demo_write16\n'
    text+='int demo_callback(Regs *,uint16_t);\n'
    text+=function(raw,'c_AdvanceDemoScripts').replace('c_AdvanceDemoScripts','l1_AdvanceDemoScripts')
    # These are actual maintained L1 statements, not a separately restated
    # arithmetic specification. Fail if the source spelling/shape changes.
    body=function(raw,'c_AdvanceDemoScripts')
    delta_read='int16_t delta=(int8_t)rd8(r->ds,r->si);'
    delta_shift='r->ax=(uint16_t)((uint16_t)delta<<2);'
    assert body.count(delta_read)==body.count(delta_shift)==1
    text+='static uint16_t reference_delta_value(Regs *r) { '+delta_read+delta_shift+'return r->ax; }\n'
    scene=function((ROOT/'c/scene.c').read_text(),'c_InitializeDemoScripts')
    seed='r->ax=(uint16_t)(r->ax<<5);';assert scene.count(seed)==2
    text+='static uint16_t reference_pixel_value(Regs *r) { '+seed+'return r->ax; }\n'
    text+=f'#include "{native.as_posix()}"\n'
    if mode=='instruction':
        # Cut one real L1 inner-loop iteration at its natural yield/continue
        # boundary. Retain the exact production statements, including both
        # continue sites and the repeat/stop branches, without a second model.
        body=function(raw,'c_AdvanceDemoScripts')
        begin=body.index('                r->ax=rd16(r->ds,r->si);')
        end=body.index('            wr16(r->ds,(uint16_t)(D(ActorUpdateOrScriptCursor)')
        fragment=body[begin:end]
        assert fragment.rstrip().endswith('}')
        fragment=fragment.rstrip()[:-1] # closing production for(;;)
        text+='static int reference_instruction(Regs *r) { for(unsigned once=0;once<1;once++) {\n'+fragment+'\n} return 0; }\n'
    h=folder/'harness.c';h.write_text(text+'\n'+(ROOT/'verif/demo_cbmc.c').read_text())
    result=cbmc(h,folder,[native,ROOT/'native/demo_core.h',ROOT/'native/actors.h',ROOT/'verif/demo_cbmc.c',ROOT/'c/demo_scripts.c',ROOT/'c/scene.c',Path(__file__)],
        unwind=1 if negative else 20,timeout=timeout,defines=[f'-DDEMO_PROOF_{mode.upper()}','-DUINT16_MAX=65535u'])
    print(json.dumps({k:result[k] for k in ['result','seconds','failures']}),flush=True)
    if negative:assert result['result']=='FAIL' and any('unwind' in r[0] for r in result['failures'])
    else:assert result['result']=='PASS'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['enumerate','instruction','tick','arithmetic'])
    p.add_argument('--timeout',type=int,default=60);p.add_argument('--negative',action='store_true');p.add_argument('--local-reference',action='store_true');a=p.parse_args()
    if a.mode=='enumerate':enumerate_cases(a.local_reference)
    else:prove(a.mode,a.timeout,a.negative)
