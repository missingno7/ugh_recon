"""Actual one-record C/bridge pairs, fixed slot plus arbitrary-other-slot frame.

Resource reads and scale returns are arbitrary at their matching cuts. Resource,
slot, platform and stack objects are disjoint; aliasing within the 26-byte header
copy is a different obligation. No world prefix or other slot is symbolic here.
"""
import argparse
from closure_support import ROOT,function
from sequencing_build import OUT
from sequencing_limits import cbmc
from session_loader import FIELDS,lists
from sequencing_proof import check

KEYS=['platform','actor','tree','bird','dino','trio']
def literal(key):
    b=function((ROOT/'c/render.c').read_text(),'c_LoadCurrentLevelState')
    starts=['    r->si=R(LevelPlatformList);','    r->si=R(LevelActorList);','    r->si=R(LevelEnemyList);','    r->bx=384;']
    i=0 if key=='platform' else 1 if key=='actor' else 2
    b=b[b.index(starts[i]):b.index(starts[i+1])];b=b[b.index('    for(;;) {')+len('    for(;;) {'):b.rfind('    }')]
    # A branch break is the end of this single record; retain every other byte.
    return b.replace('break;','return UGH_OK;')+'return UGH_OK;'
def source(key,mode):
    s='#include "ugh.h"\n#include "'+(ROOT/'native/session.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\n'
    scene=(ROOT/'c/scene.c').read_text()
    s+=function(scene,'sar')+'''static void sq_require(int c){CHECK(c,"BRIDGE_REJECTED");}
static uint16_t sq_word(uint16_t a,uint16_t b){CHECK(a==b,"selected value consumed by bridge");return a;}
static int sq_bool(int a,int b){CHECK(!!a==!!b,"selected branch consumed by bridge");return !!a;}
typedef struct Memory {uint16_t fields[27],words[8],spawn,height,callback8,callback16,repeated,scaled;uint16_t other_slot;} Memory;
static Memory memory;
static uint16_t journal_fields[16],journal_values[16],service_target,service_arg,service_ret;
static unsigned journal_count,word_cursor,service_count;
static unsigned field_index(uint16_t at){switch(at){
'''
    for i,f in enumerate(FIELDS):s+=f'case D({f}):return {i};\n'
    s+='default:CHECK(0,"declared current slot writes only");return 0;}}\n'
    s+='static void store(uint16_t at,uint16_t v){unsigned f=field_index(at);CHECK(journal_count<16,"record journal bound");journal_fields[journal_count]=(uint16_t)f;journal_values[journal_count++]=v;memory.fields[f]=v;}\n'
    s+='''static uint16_t indexed(uint16_t base,uint16_t index){(void)index;
 if(base==D(ActorInitialPlatformIndices))return memory.fields[9];
 if(base==D(PlatformSpawnX))return memory.spawn;
 if(base==D(PlatformHeights))return memory.height;
 CHECK(0,"complete indexed read vocabulary");return 0;}
static uint16_t sample(uint16_t segment,uint16_t at){(void)segment;
 if(at==(uint16_t)(memory.words[0]+8u))return memory.callback8;
 if(at==(uint16_t)(memory.words[0]+16u))return memory.callback16;
 CHECK(0,"complete descriptor read vocabulary");return 0;}
static uint16_t repeat_sample(uint16_t segment,uint16_t at){(void)segment;(void)at;return memory.repeated;}
static void list_word(Regs *r){CHECK(word_cursor<8,"small record input bound");r->ax=memory.words[word_cursor++];r->si=(uint16_t)(r->si+2*step(r));}
static int service(uint16_t target,uint16_t ret,Regs *r){CHECK(!service_count,"one record scaler");service_count++;service_target=target;service_arg=r->ax;service_ret=ret;r->ax=memory.scaled;return 0;}
#define RI(n,i) indexed(D(n),(i))
#define WI(n,i,v) do{CHECK((i)==0,"fixed physical slot");store(D(n),(uint16_t)(v));}while(0)
#define rd16 sample
#define wr16(seg,at,v) store((at),(v))
#define lodsw list_word
#define ugh_call_near service
#define CALL(n,o,ret) do{int st=service(G(n),(uint16_t)(G(o)+(ret)),r);if(st)return st;}while(0)
'''
    native=lists();native=native.replace('r->di=(uint16_t)(r->di+2);break;','r->di=(uint16_t)(r->di+2);return UGH_OK;')
    code=native+'\nstatic int reference(Regs *r){r->di=logic(r,0,16);'+literal(key)+'}\n'
    code=code.replace('rd16(r->ds,(uint16_t)(r->si-2))','repeat_sample(r->ds,(uint16_t)(r->si-2))')
    s+=code
    s+='int main(void){Memory initial;memory=initial;Regs r;r.di=0;Regs original=r;'
    # The primary identity and all unknown default identities remain distinct.
    if key in ['tree','bird','dino']:s+='__CPROVER_assume(initial.words[0]==D('+dict(tree='Data_76E4',bird='Data_7630',dino='Data_76A8')[key]+'));'
    elif key=='trio':s+='__CPROVER_assume(initial.words[0]!=D(Data_76E4) && initial.words[0]!=D(Data_7630) && initial.words[0]!=D(Data_76A8));'
    s+='journal_count=word_cursor=service_count=0;int a=reference(&r);Memory expected=memory;Regs expected_regs=r;uint16_t jf[16],jv[16];unsigned count=journal_count,reads=word_cursor,calls=service_count;uint16_t target=service_target,arg=service_arg,ret=service_ret;for(unsigned i=0;i<16;i++){jf[i]=journal_fields[i];jv[i]=journal_values[i];}'
    s+='memory=initial;r=original;journal_count=word_cursor=service_count=0;int b=sq_load_lists(&r,'+('LOAD_PLATFORMS' if key=='platform' else 'LOAD_ACTORS' if key=='actor' else 'LOAD_ENEMIES')+');'
    if mode=='output':
        s+=check('a==b && journal_count==count && word_cursor==reads && service_count==calls','complete record store/read/service counts')
        s+='for(unsigned i=0;i<16;i++){if(i<count){'+check('jf[i]==journal_fields[i] && jv[i]==journal_values[i]','all record stores in original order')+'}}'
        s+='if(calls){'+check('service_target==target && service_arg==arg && service_ret==ret','scale request and exact ABI continuation')+'}'
        for f in ['ax','bx','cx','dx','si','di','bp','sp','cs','ds','es','ss','ip','flags']:s+=check('r.'+f+'==expected_regs.'+f,'all record registers and flags')
        s+='for(unsigned i=0;i<27;i++){'+check('memory.fields[i]==expected.fields[i]','entire typed working slot at record boundary')+'}'
    elif mode=='frame':
        s+=check('memory.other_slot==initial.other_slot','arbitrary other physical slot framed')
        for f in ['spawn','height','callback8','callback16','repeated','scaled']:s+=check('memory.'+f+'==initial.'+f,'every resource field framed')
        s+='for(unsigned i=0;i<8;i++){'+check('memory.words[i]==initial.words[i]','all list inputs framed')+'}'
    else:
        # Output comparison already admits every previous field independently;
        # an additional run varies the arbitrary other physical slot.
        s+='uint16_t other;memory=initial;memory.other_slot=other;r=original;journal_count=word_cursor=service_count=0;sq_load_lists(&r,'+('LOAD_PLATFORMS' if key=='platform' else 'LOAD_ACTORS' if key=='actor' else 'LOAD_ENEMIES')+');'
        s+=check('journal_count==count','other slot cannot change operation count')
        s+='for(unsigned i=0;i<16;i++){if(i<count){'+check('jf[i]==journal_fields[i] && jv[i]==journal_values[i]','no other slot dependence')+'}}'
    return s+'return 0;}\n'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('key',choices=KEYS);ap.add_argument('mode',choices=['output','frame','dependence']);ap.add_argument('--reachability',action='store_true');a=ap.parse_args()
    folder=OUT/('record-reach' if a.reachability else 'record-proofs')/(a.key+'-'+a.mode);folder.mkdir(parents=True,exist_ok=True);code=source(a.key,a.mode)
    if a.reachability:
        pos=code.rindex('return 0;}');code=code[:pos]+'CHECK(0,"REACHED_FINAL_COMPARISON");'+code[pos:]
    h=folder/'harness.c';h.write_text(code)
    r=cbmc(h,folder,[ROOT/'native/session.c',ROOT/'native/session.h',ROOT/'native/bridge/session_bridge.c',ROOT/'verif/session_record_proof.py',ROOT/'verif/sequencing_proof.py',ROOT/'verif/session_loader.py',ROOT/'c/render.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=32,timeout=600)
    print(a.key,a.mode,r['result'],r['seconds'],flush=True)
    if a.reachability:assert r['result']=='FAIL' and r['failures'] and all('REACHED_FINAL_COMPARISON' in str(f) for f in r['failures'])
    else:assert r['result']=='PASS',r.get('failures')
if __name__=='__main__':main()
