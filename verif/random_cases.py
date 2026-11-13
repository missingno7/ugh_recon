"""Extra independent L0 recurrence/seed/sequence cases using maintained cases."""
from difftest import Case
from dos_input import rng_case,GENERAL

CASES=[]
for word in range(4):
    for bound in (0,1,2,320,32768,65535):
        for value in (0,1,32767,32768,65534,65535):
            state=[65535]*4;state[word]=value
            CASES.append(rng_case(bound,tuple(state)))
for seconds in (0,1,59,60,127,255):
    for state in ((0,0,0,0),(65535,65535,65535,65535),(0x1234,0x5678,0x9abc,0xdef0)):
        def setup(m,seconds=seconds,state=state):
            for i,v in enumerate(state):m.ww(f'GAME:RandomStateWord{i}',v)
            m.device.script(0xfffe,[(12<<24)|(34<<16)|(seconds<<8)|56])
        def check(m,r,seconds=seconds,state=state):
            expected=((state[0]&255)|(seconds<<8),*state[1:])
            assert tuple(m.rw(f'GAME:RandomStateWord{i}') for i in range(4))==expected
            assert r['CX']==0x0c22 and r['DX']==seconds*256+56
        CASES.append(Case(f'partial seed {seconds} {state}','GAME:SeedRandomFromDosSeconds',
            setup=setup,check=check,out_regs=GENERAL+('IF','DF')))
