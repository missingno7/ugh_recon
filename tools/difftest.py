"""Differential routine suites, rebuilt ASM/C oracle versus portable C.

python tools/difftest.py [suite ...] [--poison] [--coverage]
No assets/original EXE is required after the plain build exists. Full RAM except
dedicated stack scratch, declared buffers, DS/ES/SS/SP, contract registers/flags,
VGA state and every port/DOS transaction are compared. First differences fail.
"""
import argparse
import ctypes as C
import importlib.util
import json
import os
import sys
from dataclasses import dataclass, field
from common import ROOT, sha256
import cbuild
from emu import Machine, REG_NAMES, FLAGS, MEM_SIZE, STACK_SEG, STACK_TOP

# Suites import this module by its stable name even when run as a script.
sys.modules.setdefault('difftest',sys.modules[__name__])


class Regs(C.Structure):
    _fields_=[(n.lower(),C.c_uint16) for n in REG_NAMES]


class IoEvent(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('kind','port','size','value')]


class DeviceState(C.Structure):
    _fields_=[('planes',C.c_uint8*(4*65536)),('latch',C.c_uint8*4),
              ('seq_index',C.c_uint8),('map_mask',C.c_uint8),('gc_index',C.c_uint8),('read_map',C.c_uint8),
              ('count',C.c_uint32),('error',C.c_uint32),('log',IoEvent*270000)]


@dataclass
class Case:
    title: str
    routine: str
    setup: object = None
    regs: dict = field(default_factory=dict)
    out_regs: tuple = ()
    ranges: tuple = ()
    args: tuple = ()
    kind: str = 'near'
    flags: int = 0x202
    flag_inputs: tuple = ()  # arithmetic flags explicitly specified by the entry contract
    budget: int = 5_000_000
    check: object = None  # independent expected-value assertion, called on oracle result
    cfunc: str = ''


def load_dll():
    # Process-specific copy avoids loaded-DLL file locks without deleting other workers' files.
    path=cbuild.build(ROOT/f'build/c/ughcore_{os.getpid()}.dll')
    dll=C.CDLL(str(path))
    dll.ugh_memory.restype=C.POINTER(C.c_uint8*MEM_SIZE)
    dll.ugh_device_state.restype=C.POINTER(DeviceState)
    dll.ugh_device_size.restype=C.c_uint32
    if dll.ugh_device_size()!=C.sizeof(DeviceState): raise RuntimeError('device ctypes layout drift')
    return dll


POISON=dict(AX=0xA5C3,BX=0x5A3C,CX=0x3C5A,DX=0xC3A5,SI=0x6996,DI=0x9669,
            BP=0x7E81,DS=0x7340,ES=0x7C20)


def run(case,m,dll,poison=False):
    m.reset()
    if case.setup: case.setup(m)
    regs=dict(POISON if poison else {})
    regs.update(case.regs(m) if callable(case.regs) else case.regs)
    # Poison arithmetic flags, preserve the case's explicit direction/interrupt state.
    specified=sum(FLAGS[name] for name in set(case.flag_inputs))
    flags=case.flags | ((0x8D5 & ~specified) if poison else 0)
    args=case.args(m) if callable(case.args) else case.args
    initial_regs=m.prepare(case.routine,regs,case.kind,args,flags)
    initial=m.snapshot()
    device_initial=m.device.state()
    result=m.run(case.budget)
    asm=m.snapshot()
    if case.check: case.check(m,result)
    mem=dll.ugh_memory().contents
    C.memmove(mem,initial,MEM_SIZE)
    dll.ugh_devices_reset()
    dev=dll.ugh_device_state().contents
    C.memmove(C.addressof(dev),device_initial,len(device_initial))
    r=Regs(**{n.lower():v for n,v in initial_regs.items()})
    fn=getattr(dll,case.cfunc or 'c_'+case.routine.split(':')[1])
    fn.argtypes=[C.POINTER(Regs)]; fn.restype=C.c_int
    status=fn(C.byref(r))
    if case.kind=='iret':
        # The adapter models the handler body; the declared IRET pops saved FLAGS.
        a=r.ss*16+((r.sp+4)&65535)
        r.flags=mem[a] | (mem[a+1]<<8)
    r.sp=(r.sp+m.return_size)&65535; r.ip=0xfff0
    got=bytes(mem)
    problems=[]
    if status: problems.append(f'C returned status {status}')
    if dev.error: problems.append('C requested unsupported hardware or overflowed its log')
    # Stack scratch below the entry return frame is the sole excluded memory span.
    # Incoming frame and all cdecl arguments remain compared. All other RAM is checked,
    # including code variables, the 23 far frames and writes outside declared outputs.
    exclude_start=STACK_SEG*16
    exclude_end=exclude_start+initial_regs['SP']
    for a,b in ((0,exclude_start),(exclude_end,MEM_SIZE)):
        if asm[a:b]!=got[a:b]:
            i=next(i for i in range(a,b) if asm[i]!=got[i])
            problems.append(f'RAM linear {i:05X}: asm {asm[i]:02X}, C {got[i]:02X}')
            break
    for seg,off,n in case.ranges:
        a=seg*16+off
        if asm[a:a+n]!=got[a:a+n]: problems.append(f'declared buffer {seg:04X}:{off:04X}+{n:X} differs')
    for name in dict.fromkeys(('CS','DS','ES','SS','SP')+tuple(case.out_regs)):
        if name in FLAGS:
            a,b=bool(result['FLAGS']&FLAGS[name]),bool(r.flags&FLAGS[name])
        else: a,b=result[name],getattr(r,name.lower())
        if a!=b: problems.append(f'{name}: asm {int(a):04X}, C {int(b):04X}')
    cdevice=C.string_at(C.addressof(dev),len(device_initial))
    adevice=m.device.state()
    if cdevice!=adevice:
        i=next(i for i in range(len(adevice)) if cdevice[i]!=adevice[i])
        problems.append(f'VGA state byte {i:05X}: asm {adevice[i]:02X}, C {cdevice[i]:02X}')
    clog=[(e.kind,e.port,e.size,e.value) for e in dev.log[:dev.count]]
    if m.device.log!=clog:
        i=next((i for i,(a,b) in enumerate(zip(m.device.log,clog)) if a!=b),min(len(m.device.log),len(clog)))
        problems.append(f'port/DOS log event {i}: asm {m.device.log[i:i+1]}, C {clog[i:i+1]} '
                        f'(lengths {len(m.device.log)}/{len(clog)})')
    return problems


def load_suite(name):
    path=ROOT/'tests'/f'{name}.py'
    spec=importlib.util.spec_from_file_location('ugh_test_'+name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('suites',nargs='*'); p.add_argument('--poison',action='store_true')
    p.add_argument('--coverage',action='store_true')
    a=p.parse_args()
    suites=a.suites or sorted(f.stem for f in (ROOT/'tests').glob('*.py') if not f.stem.startswith('_'))
    d=load_dll(); m=Machine(coverage=a.coverage)
    total=failed=0; rows=[]
    for name in suites:
        cases=load_suite(name).CASES; bad=0
        for case in cases:
            total+=1
            try: problems=run(case,m,d,a.poison or bool(os.environ.get('UGH_POISON')))
            except Exception as e: problems=[f'{type(e).__name__}: {e}']
            rows.append(dict(suite=name,title=case.title,routine=case.routine,passed=not problems,steps=m.steps))
            if problems:
                failed+=1; bad+=1; print(f'FAIL {name}: {case.title}')
                for problem in problems: print('  '+problem)
        print(f'{"PASS" if not bad else "FAIL"} {name}: {len(cases)-bad}/{len(cases)} cases')
    inputs={str(f.relative_to(ROOT)):sha256(f.read_bytes()) for folder in ('c','tests')
            for f in (ROOT/folder).glob('*') if f.suffix in ('.c','.h','.py')}
    for name in ('emu','cgen','cbuild','difftest'):
        f=ROOT/'tools'/f'{name}.py'; inputs[str(f.relative_to(ROOT))]=sha256(f.read_bytes())
    report=dict(suites=suites,poison=a.poison or bool(os.environ.get('UGH_POISON')),cases=rows,
                passed=total-failed,total=total,inputs=inputs,
                image_sha256=sha256(m.raw_image))
    target=ROOT/'build/c/difftest.json'; target.write_text(json.dumps(report,indent=2)+'\n')
    if a.coverage:
        report['executed']=sorted(m.executed)
        (ROOT/'build/c/executed.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'{total-failed}/{total} cases equal'+(' (poison)' if report['poison'] else ''))
    return 1 if failed or not total else 0


if __name__=='__main__':
    raise SystemExit(main())
