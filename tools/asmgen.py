"""Bootstrap recursive-descent map and mnemonic TASM source. Maintained ASM is independent.

No linear sweep: only entries justified by control flow or the explicit evidence list below.
Run --map to rediscover into scratch; --emit uses the curated map and overwrites source.
"""
import argparse, json, struct, re
from collections import defaultdict, deque
from capstone import Cs, CS_ARCH_X86, CS_MODE_16, CS_GRP_CALL, CS_GRP_JUMP, CS_GRP_RET, CS_GRP_IRET
from capstone.x86 import X86_OP_IMM, X86_OP_MEM
from common import ROOT, BUILD, MZ, sha256

MAP = ROOT/'metadata/asm-map.json'
FRAMES = [('GAME',0x13b,8,0x529c), ('SOUND',0x664,0xc,0x2143), ('TIMER',0xa32,6,0x341)]
CS = Cs(CS_ARCH_X86, CS_MODE_16); CS.detail = True

def oracle():
    m = MZ((BUILD/'oracle/UGH_X.EXE').read_bytes())
    lock = json.loads((ROOT/'metadata/oracle.json').read_text())
    if m.identity()!=lock['expanded']:raise ValueError('expanded oracle differs from lock')
    return m

def decode(m, frame, off):
    return next(CS.disasm(m.image[frame*16+off:frame*16+off+15],off,count=1),None)

def discover(m):
    result = {'schema':1,'oracle_sha256':sha256(m.data),'modules':[], 'encoding_exceptions':[]}
    for name,frame,start,end in FRAMES:
        entries = defaultdict(list)
        def entry(off, why):
            if start <= off < end and why not in entries[off]: entries[off].append(why)
        if name == 'GAME': entry(8,'startup far call at image 0137')
        seeds={
          'GAME': {0x4e57:'DOS int 24 vector installed at 4E5E/4E61',
                   0x4eff:'call target from 4F5E; follows CS variables at 4EF7..4EFE',
                   0x989:'unreferenced routine, matching 0965 variant; bounded by RET at 0988/099E',
                   0xb4e:'unreferenced RET between routines',0x3ea1:'unreferenced CALL/ADD/RET wrapper around 3EAA',
                   0x43d7:'unreferenced entry with fallthrough into 43EA',0x44cf:'unreferenced CALL 44C6 with fallthrough into 44D2',
                   0x4e68:'unreferenced LES/CALL/MOV entry with fallthrough into 4E72'},
          'SOUND':{0x1179:'DOS int 08 vector installed at 1159',0x1193:'DOS int 08 vector installed at 1184',
                   0x12e5:'callback AX:DX passed to TIMER at 1360',0x1939:'callback AX:DX passed to TIMER at 1B1E',
                   0x1ef5:'DOS interrupt vector installed at 1FA7',0x1e04:'DOS interrupt vector installed at 2086',
                   0x11c3:'unreferenced callback matching 1939 counter increment and call',
                   0x1571:'unreferenced ENTER/far-return procedure before dispatch at 15D3',
                   0x1b3a:'unreferenced register-save/far-return procedure between 1B39 and 1B4D'},
          'TIMER':{0x99:'callback saved in DGROUP 7B2E at 002E',0xd2:'DOS int 08 vector installed at 008F',
                   0x30e:'unreferenced far wrapper: BP prologue and PUSH CS/CALL 01AA',
                   0x323:'unreferenced far wrapper: BP prologue and PUSH CS/CALL 021B',
                   0x32f:'unreferenced far wrapper: BP prologue and PUSH CS/CALL 021B'}
        }
        for off,why in seeds[name].items():entry(off,why)
        if name=='GAME':
            for p in range(0x2db3,0x2db9,2):entry(m.word(frame*16+p),f'CS jump table word at {p:04X}, indexed at 2DFE')
            for a,b in [(0x7638,0x7652),(0x7674,0x768e),(0x76b0,0x76ca),(0x76ec,0x7706),
                        (0x7728,0x774e),(0x7772,0x7798),(0x78e4,0x790a),(0x7974,0x797c)]:
                for p in range(a,b,2):
                    t=m.word(0x5c090+p)
                    if t:entry(t,f'DGROUP descriptor callback word at {p:04X}; dispatch 1492/236F/2B8C')
        if name=='SOUND':
            for a,b,at in [(0x174b,0x176b,0x15e5),(0x1919,0x1939,0x177d)]:
                for p in range(a,b,2):entry(m.word(frame*16+p),f'CS opcode dispatch table word at {p:04X}, indexed at {at:04X}')
        # Explicit far calls and data pointers from relocation sites, not arbitrary word scanning.
        for s in m.sites:
            if m.word(s) != frame: continue
            if m.image[s-3] in (0x9a,0xea): entry(m.word(s-2),f'far transfer at image {s-3:05X}')
            if s >= 0x5c090: entry(m.word(s-2),f'DGROUP far pointer at image {s-2:05X}')
        todo=deque(entries); ins={}; occupied={}; conflicts=[]; indirect=[]
        while todo:
            off=todo.popleft()
            while start<=off<end:
                if off in ins: break
                if off in occupied:
                    conflicts.append([off,occupied[off]]); break
                i=decode(m,frame,off)
                if i is None or off+i.size>end: break
                if any(j in occupied for j in range(off,off+i.size)):
                    conflicts.append([off,'overlap']);break
                ins[off]=i
                for j in range(off,off+i.size): occupied[j]=off
                isjump=i.group(CS_GRP_JUMP) or i.mnemonic.startswith('loop') or i.mnemonic=='jcxz'; iscall=i.group(CS_GRP_CALL)
                if name=='GAME' and i.mnemonic=='mov' and len(i.operands)==2 and i.operands[0].type==X86_OP_MEM and i.operands[1].type==X86_OP_IMM:
                    if i.operands[0].mem.disp in (0x2a0d,0x2cf3,0x2d83):
                        t=i.operands[1].imm&0xffff;entry(t,f'function pointer stored by {off:04X}');todo.append(t)
                if isjump or iscall:
                    if i.operands and i.operands[0].type==X86_OP_IMM and i.mnemonic not in ('lcall','ljmp'):
                        target=i.operands[0].imm&0xffff
                        entry(target,f'{i.mnemonic} at {off:04X}'); todo.append(target)
                    elif i.mnemonic not in ('lcall','ljmp'):
                        indirect.append({'at':off,'instruction':i.mnemonic+' '+i.op_str})
                if i.mnemonic=='jmp':
                    # TASM's reserved forward jump / far-call space, unreachable but code padding.
                    p=off+i.size
                    while p<end and m.image[frame*16+p]==0x90 and p not in occupied:
                        ni=decode(m,frame,p);ins[p]=ni;occupied[p]=p;p+=1
                if i.group(CS_GRP_RET) or i.group(CS_GRP_IRET) or i.mnemonic in ('jmp','ljmp','hlt') or (name=='GAME' and off==0x4ef5): break
                off+=i.size
        spans=[]; p=start
        while p<end:
            if p in ins:
                q=p+ins[p].size
                while q in ins:q+=ins[q].size
                spans.append({'start':p,'end':q,'kind':'code'});p=q
            else:
                q=p+1
                while q<end and q not in ins:q+=1
                spans.append({'start':p,'end':q,'kind':'UNKNOWN'});p=q
        result['modules'].append({'name':name,'frame':frame,'start':start,'end':end,
            'entries':[{'offset':k,'evidence':v} for k,v in sorted(entries.items())],
            'spans':spans,'indirect':indirect,'conflicts':conflicts})
        print(name, 'code',len(occupied),'unknown',end-start-len(occupied),'indirect',len(indirect),'conflicts',conflicts)
    return result

def hx(n):
    return ('-' + hx(-n)) if n<0 else f'0{n:X}h'

def emit(m, doc):
    if sha256(m.data)!=doc['oracle_sha256']:raise ValueError('map oracle binding changed')
    for mod in doc['modules']:
        name,frame,start,end=(mod[k] for k in ('name','frame','start','end'))
        base=frame*16; image=m.image[base:base+end]
        bindings=doc.get('external_starts',{})
        reloc_offsets={s-base for s in m.sites if base+start<=s<base+end}
        code={};data={};ds=set();cs=set();extern=set();overrides=mod.get('source_overrides',{})
        for sp in mod['spans']:
            if sp['kind']=='code':
                p=sp['start']
                while p<sp['end']:
                    i=decode(m,frame,p);assert i and p+i.size<=sp['end'];code[p]=i;p+=i.size
            elif sp['kind'] in ('data','padding'):data.update({p:sp for p in range(sp['start'],sp['end'])})
            else:raise ValueError(f'{name}: UNKNOWN {sp}')
        code_bytes={p for a,i in code.items() for p in range(a,a+i.size)}
        labels={e['offset'] for e in mod['entries']}
        for addr in mod.get('address_operands',[]):
            if addr['kind']=='code':labels.add(addr['target'])
        for i in code.values():
            if (i.group(CS_GRP_JUMP) or i.group(CS_GRP_CALL) or i.mnemonic.startswith('loop') or i.mnemonic=='jcxz') and i.operands[0].type==X86_OP_IMM:
                if i.mnemonic in ('lcall','ljmp'):
                    if i.operands[0].imm==frame:labels.add(i.operands[1].imm)
                else:labels.add(i.operands[0].imm&0xffff)
        def ext(fr):
            if fr==frame:return name+'SEG'
            extern.add(fr);return f'ext_{fr:04X}'
        def memname(seg,disp):
            if seg=='cs':
                cs.add(disp&0xffff);return f'byte_{disp&0xffff:04X}'
            ds.add(disp&0xffff);return f'ds_{disp&0xffff:04X}'
        lines=[];skip=set()
        for off in range(start,end):
            if off in skip:continue
            if name=='GAME' and off==0x20:
                lines += ['; PROC/ARG/USES reproduces the entire 0020..0038 routine.',
                          '; The unused word at BP+8 has no established meaning.',
                          'loc_0020 proc C far uses ds es si di',
                          '    arg arg_0006:word, arg_0008:word, arg_000A:dword, arg_000E:dword',
                          '    lds si, arg_000A ; @0028',
                          '    les di, arg_000E ; @002B',
                          '    mov cx, arg_0006 ; @002E',
                          '    rep movsb ; @0031',
                          '    ret ; @0033 automatic USES restore, LEAVE and far return',
                          'loc_0020 endp']
                skip.update(range(0x21,0x39));continue
            if off in code:
                i=code[off];mn=i.mnemonic;op=i.op_str
                if mn=='push' and op=='cs' and off+1 in code and code[off+1].bytes[0]==0xe8 and off+1 not in labels:
                    target=code[off+1].operands[0].imm&0xffff
                    padded=target>off and off+4 in code and image[off+4]==0x90 and off+4 not in labels
                    if target<off or padded:
                        lines += ([f'loc_{off:04X}:'] if off in labels else [])+[f'    call far ptr loc_{target:04X} ; @{off:04X} same-segment far call']
                        skip.add(off+1)
                        if padded:skip.add(off+4)
                        continue
                if str(off) in overrides:
                    lines += [f'loc_{off:04X}:', '    '+overrides[str(off)]];continue
                if mn in ('lcall','ljmp') and i.operands[0].type==X86_OP_IMM:
                    fr,t=i.operands[0].imm,i.operands[1].imm
                    target=(f'loc_{t:04X}' if fr==frame else ext(fr)+'+'+hx(t-bindings.get(f'{fr:04X}',0)))
                    text=('call' if mn=='lcall' else 'jmp')+' far ptr '+target
                elif (i.group(CS_GRP_JUMP) or i.group(CS_GRP_CALL) or mn.startswith('loop') or mn=='jcxz') and i.operands[0].type==X86_OP_IMM:
                    target=i.operands[0].imm&0xffff;qual=''
                    inverse={'jo':'jno','jno':'jo','jb':'jae','jae':'jb','je':'jne','jne':'je',
                             'jbe':'ja','ja':'jbe','js':'jns','jns':'js','jp':'jnp','jnp':'jp',
                             'jl':'jge','jge':'jl','jle':'jg','jg':'jle'}
                    if mn in inverse and target==off+5 and off+2 in code and off+2 not in labels and image[off+2]==0xe9:
                        far=code[off+2].operands[0].imm&0xffff
                        if not -128<=far-(off+2)<=127:
                            mn=inverse[mn];target=far;skip.add(off+2)
                            lines += ([f'loc_{off:04X}:'] if off in labels else [])+[f'    {mn} loc_{target:04X} ; @{off:04X} JUMPS expansion']
                            continue
                    if mn=='jmp':
                        if i.bytes[0]==0xeb:
                            if off+2 in code and image[off+2]==0x90 and target>off:
                                skip.add(off+2)
                            else:qual='short '
                        else:qual='near ptr '
                    elif mn.startswith('j') and mn!='jcxz':
                        if image[off+2:off+5]==b'\x90'*3 and target>off:
                            skip.update(range(off+2,off+5))
                        else:qual='short '
                    text=mn+' '+qual+f'loc_{target:04X}'
                else:
                    mn={'cwde':'cbw','cdq':'cwd','pushaw':'pusha','popaw':'popa'}.get(mn,mn)
                    if mn in ('lcall','ljmp'):
                        mn={'lcall':'call','ljmp':'jmp'}[mn];op='dword ptr '+op
                    # String operands in Capstone are explanatory, not Intel/TASM source syntax.
                    stem=mn.split()[-1]
                    if stem in ('movsb','movsw','stosb','stosw','lodsb','lodsw','scasb','scasw','cmpsb','cmpsw','insb','insw','outsb','outsw'):
                        segprefix=next((b for b in i.prefix if b in (0x26,0x2e,0x36,0x3e)),0)
                        if segprefix: mn={0x26:'es',0x2e:'cs',0x36:'ss',0x3e:'ds'}[segprefix]+': '+mn
                        op=''
                    else:
                        # Replace only displacements in memory operands, keeping register/struct forms.
                        for operand in i.operands:
                            if operand.type==X86_OP_MEM:
                                mm=operand.mem;seg=i.reg_name(mm.segment) if mm.segment else ''
                                disp=mm.disp
                                if disp and ((seg=='cs' and (not mm.base or abs(disp)>0xff or i.disp_size==2)) or (not seg and (disp>0xff or not mm.base and not mm.index))):
                                    sym=memname(seg,disp)
                                    token=('0x'+format(abs(disp),'x')) if abs(disp)>=10 else str(abs(disp))
                                    op=re.sub(r'(?<![\w])'+re.escape(token)+r'(?![\w])',sym,op,count=1)
                        op=op.replace(', ptr ', ', dword ptr ')
                        if any(o.type==X86_OP_MEM and not o.mem.base and not o.mem.index and not o.mem.segment for o in i.operands):
                            op=re.sub(r'(?<!:)\[','ds:[',op)
                        if mn=='xchg' and i.bytes[0]==0x86 and i.modrm>>6==3:
                            op=', '.join(reversed(op.split(', ')))
                        # An image segment word is always symbolic, with an OMF base fixup.
                        sites=[p for p in range(off,off+i.size) if p in reloc_offsets]
                        if sites:
                            assert len(sites)==1
                            fr=m.word(base+sites[0]);sym=ext(fr)
                            old=i.operands[-1].imm
                            op=op.rsplit(',',1)[0]+', seg '+sym if ',' in op else 'seg '+sym
                        elif mn=='push' and i.bytes[0]==0x68:
                            op='word ptr '+hx(i.operands[0].imm&0xffff)
                        elif len(i.operands)>=2 and i.operands[-1].type==X86_OP_IMM:
                            # Preserve full-width immediates where sign-extension offers a shorter form.
                            opcode=next((b for b in i.bytes if b not in (0x26,0x2e,0x36,0x3e,0xf0,0xf2,0xf3)),0)
                            if opcode==0x81 or (opcode in (0x05,0x0d,0x15,0x1d,0x25,0x2d,0x35,0x3d)):
                                op=op.rsplit(',',1)[0]+', word ptr '+hx(i.operands[-1].imm&0xffff)
                        address=next((x for x in mod.get('address_operands',[]) if x['at']==off),None)
                        if address:
                            target=address['target']
                            sym=f'loc_{target:04X}' if address['kind']=='code' else memname('cs',target)
                            op=op.rsplit(',',1)[0]+', offset '+sym
                    text=mn+(' '+op if op else '')
                text=re.sub(r'0x([0-9a-fA-F]+)',lambda m:hx(int(m.group(1),16)),text)
                lines += ([f'loc_{off:04X}:'] if off in labels else [])+[f'    {text} ; @{off:04X}']
            elif off in data:
                sp=data[off]
                if off==sp['start']:lines += [f'byte_data_{off:04X}:']
                if off in reloc_offsets:
                    lines += ['    dw seg '+ext(m.word(base+off))];skip.add(off+1)
                elif base+off+2 in m.sites:
                    fr=m.word(base+off+2);t=m.word(base+off)
                    target='offset '+f'loc_{t:04X}' if fr==frame else hx(t-bindings.get(f'{fr:04X}',0))
                    lines += ['    dw '+target];skip.add(off+1)
                elif any(a<=off<b and (off-a)%2==0 for a,b in mod.get('pointer_tables',[])):
                    lines += [f'    dw offset loc_{m.word(base+off):04X}'];skip.add(off+1)
                elif sp['kind']=='padding' and image[off]==0x90:lines+=['    even ; assembler alignment before CS data']
                else:
                    q=off+1
                    while q<min(off+16,sp['end']) and q not in reloc_offsets and q-1 not in reloc_offsets and q-2 not in reloc_offsets and base+q+2 not in m.sites:
                        if any(a<=q<b for a,b in mod.get('pointer_tables',[])):break
                        q+=1
                    values=image[off:q]
                    # Plain initializers keep this bootstrap on LEDATA (shared OMF reader).
                    text=', '.join(hx(x) for x in values)
                    lines += ['    db '+text+f' ; data {off:04X}..{q:04X}']
                    skip.update(range(off+1,q))
            else:assert off in code_bytes,hex(off)
        prolog=['; Maintained reconstruction; asmgen.py is the bootstrap, asmverify.py is the gate.',
                f'; Image contribution {base+start:05X}..{base+end:05X} (end exclusive).',
                '.286','JUMPS']
        prolog += [f'extrn ext_{fr:04X}:far' for fr in sorted(extern)]
        prolog += [f"{name}SEG segment {mod.get('alignment','word')} public 'CODE'",f'assume cs:{name}SEG',
                   f'public ext_{frame:04X}',f'ext_{frame:04X} label far',f'{name}_BASE label byte']
        prolog += [f'ds_{p:04X} equ {hx(p)}' for p in sorted(ds)]
        prolog += [f'byte_{p:04X} equ {name}_BASE+{hx(p-start)}' for p in sorted(cs)]
        out='\r\n'.join(prolog+lines+[f'{name}SEG ends','end',''])
        (ROOT/'src/asm'/f'{name}.ASM').write_bytes(out.encode('ascii'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--map',action='store_true');ap.add_argument('--emit',action='store_true');args=ap.parse_args()
    m=oracle()
    if args.map:
        scratch=BUILD/'workers/asm/discovered-map.json'
        scratch.parent.mkdir(parents=True,exist_ok=True)
        scratch.write_text(json.dumps(discover(m),indent=2)+'\n')
        print('Discovery only:',scratch,'(curated metadata unchanged)')
    if args.emit: emit(m,json.loads(MAP.read_text()))

if __name__=='__main__':main()
