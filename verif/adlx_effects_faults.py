"""Real L0 DIV exceptions vs the existing L1/native unsupported status class."""
import ctypes as C,sys
from closure_support import ROOT,receipt,save
from adlx_effects_build import OUT,build
import contacts_reference
contacts_reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild

def main():
    contacts_reference.prepare_reference(local=True);dll=nbuild.load_l1(build());rows=[]
    for playing,period,request in [(1,0,0x100),(1,1,0xffff),(0,1,0x100),(1,0,0)]:
        m=difftest.Machine();m.reset();difftest.load_suite('adlib').base(m)
        m.ww('SOUND:MainAdlxPlaying',playing);m.ww('SOUND:AdlxTimerPeriod',period)
        m.write(0x6000,0x100,request.to_bytes(2,'big')+b'\x81')
        initial=m.prepare('SOUND:HandleEffectAdlxTimerPeriod',dict(difftest.POISON,AX=0xa560,ES=0x6000,DI=0x100),'far',(),0x602)
        snapshot=m.snapshot()
        try:m.run()
        except RuntimeError as error:
            assert 'unsupported INT 00' in str(error),error
            diagnostic=str(error)
        else:raise AssertionError('L0 DIV unexpectedly returned')
        C.memmove(dll.ugh_memory().contents,snapshot,difftest.MEM_SIZE);dll.ugh_devices_reset()
        r=difftest.Regs(**{n.lower():v for n,v in initial.items()})
        fn=dll.c_HandleEffectAdlxTimerPeriod;fn.argtypes=[C.POINTER(difftest.Regs)]
        assert fn(C.byref(r))==1
        assert bytes(dll.ugh_memory().contents)==snapshot
        assert r.sp==(initial['SP']-4)&65535 and r.di==initial['DI'] and r.bx==period
        rows.append(dict(playing=playing,period=period,request=request,L0=diagnostic,bridge='UGH_UNSUPPORTED, RAM unchanged; L1 partial SP/DI/BX retained'))
    save(OUT/'faults.json',receipt(['python','verif/adlx_effects_faults.py'],[__file__,ROOT/'c/adlib.c',ROOT/'native/adlx_effects.c',ROOT/'native/bridge/adlx_effects_bridge.c'],result='PASS',cases=rows))
    print('PASS4 original DIV0/overflow -> L1/native fault outcomes; exception-handler register continuation is outside contract')
if __name__=='__main__':main()
