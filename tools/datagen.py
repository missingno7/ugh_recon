"""Bootstrap RAW data source from the locked expanded image; never used by build.py.

Only data intervals are copied. Runtime DGROUP data comes from C0H/CH.LIB and
the four C globals' bytes come from module.c. All relocated words are symbolic.
"""
import json
from common import ROOT, BUILD, MZ, load_json, sha256

FRAMES = [0x1a38,0x1e1f,0x2bc6,0x2bf6,0x2d9a,0x2f9e,0x2fb7,
          0x325b,0x3260,0x3265,0x326b,0x3274,0x3279,0x3444,0x3629,
          0x3632,0x3637,0x37a7,0x438a,0x4e83,0x5b63,0x5c09]

def emit(mz, start, end):
    out=[]; p=start; sites=set(mz.sites)
    while p<end:
        if p in sites:
            out.append(f'    dw seg ext_{mz.word(p):04X} ; image {p:06X}')
            p+=2; continue
        stop=min([end]+[s for s in sites if s>p])
        run=p+1
        while run<stop and mz.image[run]==mz.image[p]:run+=1
        if run-p>=8:
            out.append(f'    db {run-p} dup (0{mz.image[p]:02X}h)');p=run;continue
        q=p
        while q<min(stop,p+64) and 32<=mz.image[q]<127 and mz.image[q]!=39:q+=1
        if q-p>=4:
            out.append("    db '"+mz.image[p:q].decode('ascii')+"'");p=q;continue
        q=min(stop,p+16)
        # Stop before a useful run or string so these remain legible.
        for i in range(p+1,q):
            if i+8<=stop and len(set(mz.image[i:i+8]))==1:q=i;break
            if i+4<=stop and all(32<=b<127 and b!=39 for b in mz.image[i:i+4]):q=i;break
        out.append('    db '+', '.join(f'0{b:02X}h' for b in mz.image[p:q]));p=q
    return out

def write(name, lines):
    (ROOT/'src/data'/name).write_bytes(('\r\n'.join(lines)+'\r\n').encode('ascii'))

def main():
    raw=(BUILD/'oracle/UGH_X.EXE').read_bytes()
    if sha256(raw)!=load_json('oracle.json')['expanded']['file_sha256']:raise ValueError('unlocked oracle')
    mz=MZ(raw);(ROOT/'src/data').mkdir(exist_ok=True)
    note=['; RAW data debt. Bootstrap: tools/datagen.py; edit this source thereafter.', '.286']
    write('ZERO.ASM',note+["ZERODATA segment para public 'FAR_DATA'",'public ext_0A67','ext_0A67 label far',
                         '    db 64768 dup (0)','ZERODATA ends','end'])
    for a,b in zip(FRAMES,FRAMES[1:]):
        lines = note+[f"BANK_{a:04X} segment para public 'FAR_DATA'",f'public ext_{a:04X}',f'ext_{a:04X} label far']
        lines += emit(mz,a*16,b*16)+[f'BANK_{a:04X} ends']
        write(f'B{a:04X}.ASM',lines+['end'])
    a=0x5c090+0x92;b=0x5c090+0x7b7c
    frames=sorted({mz.word(p) for p in mz.sites if a<=p<b}-{0x5c09})
    lines=note+['; Menu option/string offset table at DGROUP:00DA..00EC.',
                '; GAME:0652 indexes the option entries and copies the selected DS string.',
                'extrn ext_013B:far']
    lines+=[f'extrn ext_{f:04X}:far' for f in frames if f!=0x13b]
    lines+=["_DATA segment word public 'DATA'",'public ext_5C09','ext_5C09 label far']
    lines+=emit(mz,a,0x5c090+0xda)
    labels={}
    for off in range(0xda,0xee,2):
        target=0x5c090+mz.word(0x5c090+off);symbol=f'dg_text_{target-0x5c090:04X}'
        labels[target]=symbol;lines.append('    dw offset '+symbol)
    p=0x5c090+0xee
    for target,symbol in sorted(labels.items()):
        lines+=emit(mz,p,target)+[symbol+' label byte'];p=target
    lines+=emit(mz,p,b)+['_DATA ends','DGROUP group _DATA']
    lines+=['end']
    write('DGDATA.ASM',lines)
    print('RAW data sources:',b-a+64768+(FRAMES[-1]-FRAMES[0])*16,'bytes')

if __name__=='__main__':main()
