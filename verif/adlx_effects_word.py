"""Actual-C native-step proof on a typed, word-backed ordinary-RAM binding."""
import argparse,json
from pathlib import Path
from closure_support import ROOT,cbmc
from adlx_effects_build import OUT
from adlx_effects_evidence import pair

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--op',type=int,choices=range(9));p.add_argument('--channels',action='store_true');p.add_argument('--negative',action='store_true');p.add_argument('--record',type=int,choices=[8,9,10,11]);p.add_argument('--timeout',type=int,default=90);p.add_argument('--sat',action='store_true');p.add_argument('--contracts',action='store_true');a=p.parse_args()
    for op in range(9) if a.op is None else [a.op]:
      for channel in range(11) if a.channels else [-1]:
        record=a.record if a.record is not None else -1
        folder=OUT/f'final_{"contract" if a.contracts else "probe"}_{op}_r{record}_c{channel}_{"sat" if a.sat else "smt"}{"_negative" if a.negative else ""}'
        _,inputs=pair(folder,op,a.negative)
        inc=folder/'pair.inc';text=inc.read_text().replace('static void initialize(void);','').replace('static void compare_memory(void);','')
        cut=text.index('/* All entries RETF.')
        text=text[:cut]+'static uint16_t native_raw,native_divisor;\nstatic uint32_t native_numerator,native_quotient;\nstatic uint8_t native_channel;\nstatic uint16_t word_read(uint16_t bank,uint16_t offset);\nstatic void word_write(uint16_t bank,uint16_t offset,uint16_t value);\n#define rd16 word_read\n#define wr16 word_write\n'+text[cut:]
        # Ghost-only observation in actual native code. The reference then
        # asserts equality BEFORE sharing the term. No equality is assumed;
        # each bind is an independently checked expression lemma in the proof.
        native=folder/'native_observed.c'
        code=(ROOT/'native/adlx_effects.c').read_text().replace('#include "adlx_effects.h"','#include "'+(ROOT/'native/adlx_effects.h').as_posix()+'"')
        if a.negative:code=code.replace('channel<=9','channel<9')
        code=code.replace('result.channel=channel;','''
#if CHANNEL >= 0 && CHANNEL < 10
CHECK(channel==CHANNEL,"finite channel identity lemma");channel=CHANNEL;
#endif
native_channel=channel;result.channel=channel;''')
        code=code.replace('result.wait_delta=((uint32_t)raw*track->step_q8)>>8;','native_raw=raw;result.wait_delta=((uint32_t)raw*track->step_q8)>>8;')
        code=code.replace('uint32_t numerator=(uint32_t)requested*256u;','uint32_t numerator=(uint32_t)requested*256u;native_numerator=numerator;native_divisor=state->timer_period;native_quotient=native_divisor ? numerator/native_divisor : 0;')
        native.write_text(code)
        old_native=(folder/'mutant.c') if a.negative else ROOT/'native/adlx_effects.c'
        text=text.replace('#include "'+old_native.as_posix()+'"','#include "'+native.as_posix()+'"')
        if a.contracts:text=text.replace('#include "'+(ROOT/'native/adlx_main.c').as_posix()+'"','')
        needle='uint16_t delta=(uint16_t)((((r->ax&15u)<<8)|rd8(r->es,r->di))<<7);'
        text=text.replace(needle,needle+'CHECK(delta==native_raw,"long raw expression lemma");delta=native_raw;')
        needle='uint32_t numerator=((uint32_t)(uint8_t)v<<16)|(v&0xff00);'
        text=text.replace(needle,needle+'CHECK(numerator==native_numerator,"timer numerator expression lemma");numerator=native_numerator;')
        needle='if(!r->bx || numerator/r->bx>65535) return UGH_UNSUPPORTED;'
        text=text.replace(needle,'CHECK(r->bx==native_divisor,"timer divisor expression lemma");r->bx=native_divisor;\nif(r->bx) CHECK(numerator/r->bx==native_quotient,"timer quotient expression lemma");\nif(!r->bx || native_quotient>65535) return UGH_UNSUPPORTED;')
        text=text.replace('r->ax=(uint16_t)(numerator/r->bx);','r->ax=(uint16_t)native_quotient;')
        needle='al(r,(uint8_t)((uint8_t)r->ax+rd8(r->cs,(uint16_t)(r->bx+0x24))));'
        text=text.replace(needle,needle+'CHECK((uint8_t)r->ax==native_channel,"effective channel expression lemma");al(r,native_channel);')
        inc.write_text(text)
        support=(ROOT/'verif/adlx_effects_harness.c').read_text().split('#ifdef SEMANTIC\nstatic void compare_voice')[1].split('\n#endif\n\nstatic void one_case')[0]
        support='static void compare_voice'+support
        support=support.replace('for(unsigned i=0;i<12;i++) CHECK', 'unsigned i=N8();__CPROVER_assume(i<12);CHECK')
        support=support.replace('for(unsigned i=0;i<13;i++) {', '{ unsigned i=N8();__CPROVER_assume(i<13);')
        support=support.replace('for(unsigned i=0;i<9;i++) {', '{ unsigned i=N8();__CPROVER_assume(i<9);')
        source=(ROOT/'verif/adlx_effects_word.c').read_text().replace('/* COMPARE_HELPERS */',support)
        source=source.replace('#include "adlx_effects_voice_contract.h"','#include "'+(ROOT/'verif/adlx_effects_voice_contract.h').as_posix()+'"')
        harness=folder/'harness.c';harness.write_text(source)
        extra=['--arrays-uf-never']
        if not a.sat:extra+=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe']
        result=cbmc(harness,folder,[*inputs,Path(__file__),ROOT/'verif/adlx_effects_word.c',ROOT/'verif/adlx_effects_voice_contract.h'],unwind=15,timeout=a.timeout,
            defines=['-D__CPROVER__',f'-DOP={op}',f'-DCHANNEL={channel}',f'-DRECORD={record}',*(['-DVOICE_CONTRACT'] if a.contracts else [])],extra=extra)
        print(op,channel,result['result'],result['seconds'],result['failures'],flush=True)
        assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
