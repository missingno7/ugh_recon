"""Translation, test declaration, entry execution and instruction coverage are separate.

Run python tools/difftest.py --coverage, then python tools/coverage.py.
Uses the rebuilt image and curated routine census. Indirect tails are explicitly
unresolved in this static reachable-body diagnostic, never counted as full proof.
"""
import json
import re
from collections import Counter
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
from capstone.x86_const import X86_OP_IMM
from common import ROOT, load_json, sha256
import cgen
import symtab


def inventory():
    return sorted(symtab.routines(),key=lambda r:(r['frame'],r['offset']))


def translations():
    out={}
    for p in sorted((ROOT/'c').glob('*.c')):
        text=p.read_text()
        for m in re.finditer(r'/\* TRANSLATES (\w+:\w+).*?\*/\s*EXPORT int (c_\w+)\(',text,re.S):
            if m[1] in out: raise ValueError('duplicate translation: '+m[1])
            out[m[1]]=dict(file=str(p.relative_to(ROOT)),adapter=m[2])
    return out


def instructions(mz):
    cs=Cs(CS_ARCH_X86,CS_MODE_16); cs.detail=True
    ins={}
    for mod in load_json('asm-map.json')['modules']:
        base=int(mod['frame'],16)*16 if isinstance(mod['frame'],str) else mod['frame']*16
        for span in mod['spans']:
            if span['kind']=='code':
                for i in cs.disasm(mz.image[base+span['start']:base+span['end']],base+span['start']):
                    ins[i.address]=i
    inv=json.loads((ROOT/'src/c/inventory.json').read_text())
    for f in inv['functions']:
        frame,offset=(int(x,16) for x in f['address'].split(':')); a=frame*16+offset
        for i in cs.disasm(mz.image[a:a+f['instruction_length']],a): ins[i.address]=i
    return ins


def body(ins,entry):
    seen=set(); work=[entry]; indirect=[]
    while work:
        p=work.pop()
        while p in ins and p not in seen:
            seen.add(p); i=ins[p]; m=i.mnemonic
            if m in ('ret','retf','iret','hlt'): break
            if m=='jmp' or m.startswith(('j','loop')):
                target=i.operands[0].imm if len(i.operands)==1 and i.operands[0].type==X86_OP_IMM else None
                if target is not None: work.append(target)
                else: indirect.append(p)
                if m=='jmp': break
            if m=='ljmp': indirect.append(p); break
            p+=i.size
    return seen,indirect


def main():
    mz,_=cgen.read_symbols(); rs=inventory(); translated=translations(); ins=instructions(mz)
    path=ROOT/'build/c/executed.json'
    cov=json.loads(path.read_text()) if path.exists() else None
    if cov:
        for p,digest in cov['inputs'].items():
            if sha256((ROOT/p).read_bytes())!=digest: raise ValueError('stale coverage: '+p+'; rerun difftest --coverage')
        if cov['passed']!=cov['total']: raise ValueError('coverage run has failures; no acceptance evidence')
    # Test existence is independent of the selected suites in the last execution run.
    from difftest import load_suite
    declared={}
    for p in sorted((ROOT/'tests').glob('*.py')):
        if not p.stem.startswith('_'):
            for case in load_suite(p.stem).CASES:
                declared.setdefault(case.routine,set()).add(p.stem)
    tested=set(declared)
    executed=set(cov['executed']) if cov else set()
    expected={r['module']+':'+r['name'] for r in rs}
    plan=load_json('translation-plan.json')
    assigned=Counter(row['routine'] for row in plan['routines'])
    if set(assigned)!=expected or any(n!=1 for n in assigned.values()):
        raise ValueError('translation plan must cover every curated routine exactly once')
    if plan['schema']!=2: raise ValueError('translation table schema drift')
    for row in plan['routines']:
        name=row['routine']; status=row['status']; path=ROOT/row['file']; suite=ROOT/row['suite']
        if not path.is_file() or not suite.is_file(): raise ValueError('missing translation table path: '+name)
        if status=='translated':
            if name not in translated or translated[name]['file'].replace('\\','/')!=row['file']:
                raise ValueError('translation table/source drift: '+name)
            if suite.stem not in declared.get(name,set()): raise ValueError('table suite does not test '+name)
        elif status=='control_prefix':
            if name in translated or '/* CONTROL_PREFIX '+name+' */' not in path.read_text():
                raise ValueError('abnormal control prefix/source drift: '+name)
        elif status=='inline_only':
            if name not in {'GAME:DecodeIceLiteralAndMatchStream','GAME:ReadIceBitToCarry','GAME:ReadIceBitsToDx'} or path.name!='ice.c':
                raise ValueError('only the three established ICE entries are inline-only')
        else: raise ValueError('unknown translation table status: '+status)
    if set(translated)-expected: raise ValueError('translation marker not in routine census')
    rows=[]
    for r in rs:
        name=r['module']+':'+r['name']; entry=r['frame']*16+r['offset']
        reachable,indirect=body(ins,entry)
        ran=reachable&executed
        rows.append(dict(routine=name,address=f'{r["frame"]:04X}:{r["offset"]:04X}',
                         translation=translated.get(name),test=name in tested,test_suites=sorted(declared.get(name,())),
                         entry_executed=entry in executed,
                         instructions=len(reachable),executed=len(ran),
                         missing=sorted(reachable-executed),indirect_tails=indirect))
    inline=sum(row['status']=='inline_only' for row in plan['routines'])
    counts=dict(routines=len(rows),translations=len(translated),inline_only=inline,
                remaining=len(rows)-len(translated)-inline,
                control_prefixes=sum(row['status']=='control_prefix' for row in plan['routines']),directly_tested=len(tested),
                entries_executed=sum(r['entry_executed'] for r in rows))
    report=dict(counts=counts,notes='Reachable-body instruction counts can overlap at shared tails. '
                'Calls excluded; computed jumps unresolved. Execution is behavioural evidence only.',routines=rows)
    (ROOT/'build/c/coverage.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Translation coverage', '', str(counts), '',report['notes'],'',
           '| Routine | C | Direct test | Entry ran | Instructions ran/body | Missing (image) |',
           '|---|---|---|---|---|---|']
    for r in rows:
        t=r['translation']
        lines.append(f'| {r["routine"]} | {t["file"] if t else "-"} | {r["test"]} | '
                     f'{r["entry_executed"]} | {r["executed"]}/{r["instructions"]} | '+
                     ' '.join(f'{n:05X}' for n in r['missing'][:8])+(' ...' if len(r['missing'])>8 else '')+' |')
    (ROOT/'build/c/coverage.md').write_text('\n'.join(lines)+'\n')
    print(counts); print('build/c/coverage.md (execution is not a byte-match claim)')


if __name__=='__main__': main()
