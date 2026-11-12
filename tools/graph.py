"""Static original-byte call and hardware summary. Indirect targets remain unresolved.

graph.py SYMBOL|ADDR [--module GAME|SOUND|TIMER|C] [--tree N]
For data addresses, list referencing routines. Memory offsets with an unknown
segment remain explicitly unresolved; indexed displacements are not exact cells.
"""
import argparse
import re
import symtab as S
from where import describe
from capstone import Cs, CS_ARCH_X86, CS_MODE_16, CS_AC_READ, CS_AC_WRITE
from capstone.x86_const import X86_OP_REG, X86_OP_IMM, X86_OP_MEM

def analyse():
    mz=S.original();rs=S.routines();defs=S.definitions();cs=Cs(CS_ARCH_X86,CS_MODE_16);cs.detail=True
    amap={m['name']:m for m in S.load_json('asm-map.json')['modules']}
    inv={
        int(f['address'].split(':')[1],16):f for f in __import__('json').loads((S.ROOT/'src/c/inventory.json').read_text())['functions']}
    graph={};name_doc=S.names()
    for r in rs:
        start=r['frame']*16+r['offset'];r['linear']=start
        g=dict(callers=[],callees=[],ports=[],interrupts=[],services=[],reads=[],writes=[],data_symbols=[],memory=[],indirect=[])
        graph[start]=g;regs={};stack=[]
        lines=r['path'].read_text().splitlines()[r['line']-1:r['end_line']]
        # Source symbols expose offset constants without claiming that DS has a proven value.
        text='\n'.join(lines)
        # BIND aliases are declarations, not local C definitions.
        for rec in name_doc['symbols'].values():
            for spelling in rec['spellings']:
                if spelling['module']==r['module'] and rec['kind'] in ('data','c-global'):
                    if re.search(r'(?<![\w])'+re.escape(spelling['name'])+r'(?![\w])',text):
                        g['data_symbols'].append(f"{r['module']}:{spelling['name']}")
        end=r['end']
        if r['module']=='C':end=min(end,r['offset']+inv[r['offset']]['instruction_length'])
        instructions=[]
        # Skip independently classified embedded ASM data.
        spans=amap.get(r['module'],{}).get('spans',[dict(start=r['offset'],end=end,kind='code')])
        for sp in spans:
            a,b=max(r['offset'],sp['start']),min(end,sp['end'])
            if sp['kind']=='code' and a<b:instructions.extend(cs.disasm(mz.image[r['frame']*16+a:r['frame']*16+b],a))
        # Conservative straight-line register constants: reset at every branch target,
        # call, interrupt and control-flow break. No inferred interprocedural ABI.
        targets={i.operands[0].imm for i in instructions if (i.mnemonic.startswith('j') or i.mnemonic.startswith('loop')) and i.operands and i.operands[0].type==X86_OP_IMM}
        for i in instructions:
            if i.address in targets:regs={};stack=[]
            ops=i.operands;m=i.mnemonic
            if m in ('call','lcall','jmp','ljmp'):
                target=None
                if len(ops)==2 and all(o.type==X86_OP_IMM for o in ops):target=(ops[0].imm&65535)*16+(ops[1].imm&65535)
                elif len(ops)==1 and ops[0].type==X86_OP_IMM:target=r['frame']*16+(ops[0].imm&65535)
                else:g['indirect'].append(f'{i.address:04X}: {m} {i.op_str}')
                if target is not None and (m in ('call','lcall') or target<start or target>=r['frame']*16+r['end']):g['callees'].append(target)
            if m in ('in','out'):
                op=ops[1] if m=='in' else ops[0]
                value=op.imm if op.type==X86_OP_IMM else regs.get(i.reg_name(op.reg))
                g['ports'].append(f'{value:04X}' if value is not None else 'DX unresolved')
            if m=='int' and ops:
                g['interrupts'].append(f'{ops[0].imm:02X}')
                ah=regs.get('ah',regs.get('ax',-256)>>8)
                g['services'].append(f'{ops[0].imm:02X}/AH={ah:02X}' if ah>=0 else f'{ops[0].imm:02X}/AH unknown')
            for op in ops:
                if op.type!=X86_OP_MEM:continue
                mem=op.mem;seg=i.reg_name(mem.segment) if mem.segment else ('ss' if i.reg_name(mem.base)=='bp' else 'ds')
                fr=r['frame'] if seg=='cs' else regs.get(seg)
                # Stack-relative accesses are not globals.
                if seg=='ss':continue
                off=mem.disp&65535;indexed=bool(mem.base or mem.index)
                base=regs.get(i.reg_name(mem.base)) if mem.base else 0
                index=regs.get(i.reg_name(mem.index)) if mem.index else 0
                initial=indexed and base is not None and index is not None
                if initial:off=(off+base+index*mem.scale)&65535
                desc=f'{fr:04X}:{off:04X}' if fr is not None else f'{seg.upper()}?:{off:04X}'
                if indexed:desc+=' (initial indexed offset)' if initial else ' (indexed displacement)'
                access=op.access
                if not access:access=CS_AC_READ  # Capstone's missing access is an explicitly conservative read.
                for key,flag in (('reads',CS_AC_READ),('writes',CS_AC_WRITE)):
                    if access&flag:g[key].append(desc)
                g['memory'].append((fr,off,indexed,access))
            # Constant propagation for segment loads and DX ports; arithmetic invalidates.
            def value(op):
                if op.type==X86_OP_IMM:return op.imm&65535
                if op.type==X86_OP_REG:return r['frame'] if i.reg_name(op.reg)=='cs' else regs.get(i.reg_name(op.reg))
            val=value(ops[1]) if m=='mov' and len(ops)==2 else None
            zero=m in ('xor','sub') and len(ops)==2 and ops[0].type==ops[1].type==X86_OP_REG and ops[0].reg==ops[1].reg
            arith=(regs.get(i.reg_name(ops[0].reg)) if len(ops)==1 and ops[0].type==X86_OP_REG and m in ('inc','dec') else None)
            pushed=value(ops[0]) if m=='push' and ops else None
            popped=stack.pop() if m=='pop' and stack else None
            _,written=i.regs_access()
            for reg in written:
                name=i.reg_name(reg);regs.pop(name,None)
                if name in ('al','ah'):regs.pop('ax',None)
                if name in ('dl','dh'):regs.pop('dx',None)
            if m=='mov' and len(ops)==2 and ops[0].type==X86_OP_REG and val is not None:regs[i.reg_name(ops[0].reg)]=val
            if zero:regs[i.reg_name(ops[0].reg)]=0
            if arith is not None:regs[i.reg_name(ops[0].reg)]=(arith+(1 if m=='inc' else -1))&65535
            if m=='push':stack.append(pushed)
            if m=='pop' and ops and ops[0].type==X86_OP_REG and popped is not None:regs[i.reg_name(ops[0].reg)]=popped
            if m in ('call','lcall','int','jmp','ljmp','ret','retf','iret'):regs={};stack=[]
        for key in ('callees','ports','interrupts','services','reads','writes','indirect'):g[key]=sorted(set(g[key]))
    for addr,g in graph.items():
        for callee in g['callees']:
            if callee in graph:graph[callee]['callers'].append(addr)
    return rs,graph

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('symbol');p.add_argument('--module',choices=S.MODULES);p.add_argument('--tree',type=int,default=0)
    a=p.parse_args()
    try:
        if not 0<=a.tree<=20:raise ValueError('--tree must be 0..20')
        addr=S.address(a.symbol,a.module);rs,g=analyse();defs=S.definitions();name_doc=S.names()
        def label(x):
            try:return describe(x,defs)
            except ValueError:return f'image {x:05X} (runtime/unowned)'
        print(label(addr))
        matches=[r for r in rs if r['linear']<=addr<r['frame']*16+r['end']]
        is_data=S.locate(addr,defs)['kind'] in ('data','c-global')
        if is_data or not matches:
            print('Referencing routines (exact resolved cells or symbolic source offsets; indexed uses marked):')
            hit=False
            for r in rs:
                rec=g[r['linear']]
                symbolic=[]
                for s in rec['data_symbols']:
                    try:
                        _,record=S.resolve_symbol(s,name_doc)
                        fr,off=(int(x,16) for x in record['address'].split(':'))
                        if fr*16+off==addr:symbolic.append(s)
                    except ValueError:pass
                memory=[('R' if ac&CS_AC_READ else '')+('W' if ac&CS_AC_WRITE else '')+(' indexed' if ix else '') for fr,off,ix,ac in rec['memory'] if fr is not None and fr*16+off==addr]
                if symbolic or memory:print('  '+label(r['linear'])+'  '+', '.join(memory+['symbolic '+s for s in symbolic]));hit=True
            if not hit:print('  none resolved; indirect/register-based accesses may be missing')
            return
        r=matches[-1];rec=g[r['linear']]
        for key in ('callers','callees'):
            print(key+':')
            for target in rec[key]:
                cross=' [cross-module]' if any(q['linear']==target and q['module']!=r['module'] for q in rs) else ''
                print('  '+label(target)+cross)
        for key in ('ports','interrupts','services','reads','writes','indirect','data_symbols'):
            print(key+': '+(', '.join(rec[key]) or 'none resolved'))
        print('Static summary: DS?/ES? segments unknown; indexed displacements are bases; indirect edges and call side effects are incomplete.')
        if a.tree:
            def tree(x,depth,path):
                print('  '*(a.tree-depth)+label(x)+(' [cycle]' if x in path else ''))
                if depth and x not in path:
                    for t in g.get(x,{}).get('callees',[]):tree(t,depth-1,path|{x})
            tree(r['linear'],a.tree,set())
    except (ValueError,FileNotFoundError) as e:p.exit(1,str(e)+'\n')

if __name__=='__main__':main()
