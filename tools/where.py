"""Locate SYMBOL, frame:offset, ds:offset, image-linear hex, or cs:offset --module NAME."""
import argparse
import re
import symtab as S
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

def mnemonic(i):
    # Capstone incorrectly calls unprefixed 16-bit 98/99 cwde/cdq.
    if i.mnemonic=='cwde' and 0x66 not in i.bytes[:-1]:return 'cbw'
    if i.mnemonic=='cdq' and 0x66 not in i.bytes[:-1]:return 'cwd'
    return i.mnemonic

def describe(linear,defs=None):
    d=S.locate(linear,defs);delta=linear-d['frame']*16-d['offset']
    line=d['line']
    if delta and d['kind']=='code' and d['module'] in S.MODULES and d['module']!='C':
        target=linear-d['frame']*16;rows=[]
        for n,text in enumerate(d['path'].read_text().splitlines(),1):
            at=re.search(r';\s*@([0-9A-Fa-f]{4})\b',text)
            if at and d['offset']<=int(at[1],16)<=target:rows.append((int(at[1],16),n))
        if rows:line=max(rows)[1]
    return f"{d['module']} {d['frame']:04X}:{d['offset']:04X} {d['name']}"+(f'+{delta:X}' if delta else '')+f"  {d['path'].relative_to(S.ROOT)}:{line}"+(f" (label line {d['line']})" if line!=d['line'] else '')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('address');p.add_argument('--module',choices=S.MODULES);p.add_argument('--disasm',type=int,default=0)
    a=p.parse_args()
    try:
        linear=S.address(a.address,a.module);mz=S.original()
        if not 0<=linear<len(mz.image):raise ValueError('address outside original load image')
        print(f'image {linear:05X}: '+describe(linear))
        if not 0<=a.disasm<=10000:raise ValueError('--disasm must be 0..10000 instructions')
        if a.disasm:
            d=S.locate(linear);base=d['frame']*16
            print('Original bytes (data addresses may decode as meaningless instructions):')
            for j,i in enumerate(Cs(CS_ARCH_X86,CS_MODE_16).disasm(mz.image[linear:linear+16*a.disasm],linear-base)):
                if j>=a.disasm:break
                print(f'{d["frame"]:04X}:{i.address:04X} {i.bytes.hex():24} {mnemonic(i)} {i.op_str}')
    except (ValueError,FileNotFoundError) as e:p.exit(1,str(e)+'\n')

if __name__=='__main__':main()
