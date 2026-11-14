"""Full RAM/device/ABI C-to-C cases, including unsupported DIV0 prefix."""
import ctypes as C,json,sys
from closure_support import ROOT,receipt,save
from hud_shells import OUT,FILES
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild,contacts_reference

def main():
    contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True)
    build=json.loads((OUT/'build.json').read_text());dll=nbuild.load_l1(build['command'][build['command'].index('-o')+1]);machine=difftest.Machine()
    suite=difftest.load_suite('render');cases=[]
    for digit in range(256):
        def setup(m,digit=digit):
            suite.scene(m);m.ww('DGROUP:HudDigitCursorX',(0xfff9+digit)&65535);m.ww('DGROUP:HudDigitCursorY',194)
        cases.append(difftest.Case('raw glyph '+str(digit),'GAME:DrawHudDigit',setup=setup,regs=dict(DS=suite.DATA_SEG,AX=0xa500|digit)))
    for timer in (0,1,0x7fff,0x8000,0xffff):
        case=suite.hud_case('unchanged',timer,0xffff)
        previous=case.setup
        def setup(m,previous=previous):previous(m);m.ww('DGROUP:TimerBarDivisor',0)
        case.setup=setup;case.title='DIV0 prefix '+str(timer);cases.append(case)
    for path,divisor in [('lives','DecimalTenDivisor'),('fare-one','DecimalThousandDivisor'),('score-low','DecimalTenThousandDivisor')]:
        case=suite.hud_case(path);previous=case.setup
        def setup(m,previous=previous,divisor=divisor):previous(m);m.ww('DGROUP:'+divisor,0)
        case.setup=setup;case.title='decimal failure prefix '+path;cases.append(case)
    for mode in range(4):
      for read_mode in (0,8):
       for mask in (0,5,15):
        for timer,cached in ((7000,11),(7000,1),(0,0x8000),(700,0x8000)):
            case=suite.hud_case('unchanged',timer,cached);previous=case.setup
            def setup(m,previous=previous,mode=mode,read_mode=read_mode,mask=mask):
                previous(m);m.device.map_mask=mask;m.device.gc[5]=mode|read_mode;m.device.gc[0]=9;m.device.gc[1]=5;m.device.gc[3]=0x1b;m.device.gc[8]=0xa5
                m.write(suite.DATA_SEG,m.off('DGROUP:VgaSinglePlaneMasks'),bytes((0,0xff,0xa5,0x5a)))
                m.write(suite.DATA_SEG,m.off('DGROUP:VgaCumulativePlaneMasks'),bytes((0x5a,0xa5,0xff,0)))
            case.setup=setup;case.title=f'bar inherited mode={mode}|{read_mode} map={mask} timer={timer} previous={cached}';cases.append(case)
    rows=[];mem=dll.ugh_memory().contents;dev=dll.ugh_device_state().contents
    for case in cases:
        machine.reset();case.setup(machine);registers=machine.prepare(case.routine,case.regs,case.kind,case.args,case.flags);initial=machine.snapshot();device=machine.device.state();observations=[]
        name=case.routine.split(':')[1]
        for prefix in ('l1_','c_'):
            C.memmove(mem,initial,difftest.MEM_SIZE);dll.ugh_devices_reset();C.memmove(C.addressof(dev),device,len(device))
            r=difftest.Regs(**{k.lower():v for k,v in registers.items()});fn=getattr(dll,prefix+name);fn.argtypes=[C.POINTER(difftest.Regs)];fn.restype=C.c_int
            status=fn(C.byref(r));observations.append((status,bytes(r),bytes(mem),C.string_at(C.addressof(dev),C.sizeof(dev))))
        assert observations[0]==observations[1],case.title
        if case.title.startswith('DIV0'):
            r=difftest.Regs.from_buffer_copy(observations[1][1])
            timer=int(case.title.split()[-1])
            assert (r.sp==((registers['SP']-2)&65535) and status!=0) if timer<0x8000 else (r.sp==registers['SP'] and status==0)
        rows.append(dict(case=case.title,result='PASS',status=observations[1][0]))
    save(OUT/'full-cases.json',receipt(['python','verif/hud_full_cases.py'],[*FILES,ROOT/'verif/hud_full_cases.py',ROOT/'verif/hud_build.py',ROOT/'tests/render.py',ROOT/'c/render.c'],result='PASS',cases=rows,scope='Actual L1 parent and native parent with the same composed accepted/native children; all RAM including stack scratch, full registers/flags, full device state and every IO log byte. Separate integration.json compares L0.'))
    print('PASS',len(rows),'full RAM/device/ABI C pairs, including5 DIV0/negative-timer prefixes',flush=True)
if __name__=='__main__':main()
