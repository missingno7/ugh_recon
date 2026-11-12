"""DGROUP logic, carry result, CS latch, and far-stack copy with DS/ES changes."""
from difftest import Case
from emu import DATA_SEG

ARITH=('CF','PF','ZF','SF','OF')
GENERAL=('AX','BX','CX','DX','SI','DI','BP')
CASES=[]


for seed in (None,0,0x55,0xFF):
    def setup(m,seed=seed):
        if seed is not None:
            s,o=m.address('DGROUP:HighScoreRows')
            m.write(s,o,bytes((seed+i*31)&255 for i in range(107)))
    CASES.append(Case(f'complement score bytes {seed}', 'GAME:ComplementHighScoreTable',
                      setup=setup,regs=dict(DS=DATA_SEG),out_regs=GENERAL+ARITH))

for size,zero in ((0,None),(1,None),(16,None),(16,0),(16,7),(16,15)):
    def setup(m,size=size,zero=zero):
        for i in range(size):
            m.ww('DGROUP:ActorUpdateOrScriptCursor',0x1234,i*2)
            m.ww('DGROUP:DemoCompletionScanBiasedBase',0 if i==zero else (0x8000+i),2+i*2)
        m.ww('DGROUP:ActorUpdateOrScriptCursor',65535,size*2)
    CASES.append(Case(f'finished size={size}, zero={zero}', 'GAME:TestAllDemoScriptsFinished',
                      setup=setup,regs=dict(DS=DATA_SEG),out_regs=GENERAL+ARITH))

for old,new in ((0,0),(0,0xE0),(0xE0,0xE0),(0x1C,0x9C),(255,0),(0,255)):
    def setup(m,old=old,new=new):
        m.wb('DGROUP:CurrentKeyboardScanCode',old)
        m.wb('GAME:LatestInterruptScanCode',new)
    CASES.append(Case(f'scan {old:02X}->{new:02X}', 'GAME:PollKeyboardScanChange',
                      setup=setup,regs=dict(DS=DATA_SEG),out_regs=GENERAL+ARITH))


def copy_case(count,source,dest,reverse=False,overlap=False):
    ss,es=0x7500,(0x7500 if overlap else 0x7700)
    def setup(m):
        for i in range(256): m.write(ss,i,bytes(((i*29+7)&255,)))
        for i in range(64): m.write(ss,(source+i)&65535,bytes(((i*13+19)&255,)))
    return Case(f'copy n={count}, {source:04X}->{dest:04X}, DF={reverse}, alias={overlap}',
                'GAME:CopyFarBytes',setup=setup,args=(count,0xFEED,source,ss,dest,es),
                kind='far',flags=0x602 if reverse else 0x202,out_regs=GENERAL+ARITH+('DF',))


CASES += [copy_case(0,16,32),copy_case(1,16,32),copy_case(32,0xFFF0,0xFFF8),
          copy_case(32,31,40,True),copy_case(64,0,1,False,True),copy_case(32,32,31,True,True)]
