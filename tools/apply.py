"""Validate an entire naming proposal, apply atomically with rollback, then run gates.

rename OLD NEW
comment LABEL
; Purpose / In / Out / hardware and original quirks (until a blank line).

data LABEL byte|word|dword|string [count]
note free text (report only)

--dry validates every directive without writing. Labels may use old or new names.
"""
import argparse
import json
import re
import sys
from pathlib import Path
import symtab as S
import rename as R

def parse(text):
    lines=text.splitlines();ops=[];errors=[];i=0
    while i<len(lines):
        n=i+1;line=lines[i].strip();i+=1
        if not line or line.startswith('#'):continue
        words=line.split();op=words[0]
        if op=='comment' and len(words)==2:
            block=[]
            while i<len(lines) and lines[i].strip():
                if not lines[i].startswith(';'):errors.append(f'line {i+1}: comment block requires ; lines followed by a blank line')
                else:block.append(lines[i])
                i+=1
            if not block:errors.append(f'line {n}: empty contract comment')
            elif any(len(b)>100 for b in block):errors.append(f'line {n}: contract lines must be at most 100 characters')
            ops.append(dict(op=op,line=n,label=words[1],block=block))
        elif op=='rename' and len(words)==3:ops.append(dict(op=op,line=n,old=words[1],new=words[2]))
        elif op=='data' and len(words) in (3,4):
            count=None
            if len(words)==4:
                try:
                    count=int(words[3],0)
                    if count<=0:raise ValueError()
                except ValueError:errors.append(f'line {n}: count must be a positive integer')
            ops.append(dict(op=op,line=n,label=words[1],kind=words[2],count=count))
        elif op=='note' and len(words)>1:ops.append(dict(op=op,line=n,text=line[5:]))
        else:errors.append(f'line {n}: invalid directive {line!r}')
    if errors:raise ValueError('\n'.join(errors))
    return ops

def target(label,ops,doc,defs):
    try:key,rec=S.resolve_symbol(label,doc)
    except ValueError as first:
        # NEW can refer to a rename within this proposal.
        hits=[o for o in ops if o['op']=='rename' and o['new'].lower()==label.split(':')[-1].lower()]
        if len(hits)!=1:raise first
        key,rec=S.resolve_symbol(hits[0]['old'],doc)
    matches=[d for d in defs if any(s['module']==d['module'] and s['name']==d['name'] for s in rec['spellings'])]
    # Prefer the physical local label, then a C definition, then an EQU constant.
    rank=lambda d:(d['form'] not in ('equ',),d['name']==rec['name'],not d['name'].startswith('_'))
    if not matches:raise ValueError(label+': no maintained definition')
    d=max(matches,key=rank)
    return key,rec,d

def contract(text,d,block):
    lines=text.splitlines(keepends=True);n=d['line']-1;newline='\r\n' if '\r\n' in text else '\n'
    c=d['module']=='C'
    # cjudge requires the address marker to remain immediately before its function.
    if c and d['form']=='function':
        while n>0 and not re.search(r'/\*\s*@[\dA-Fa-f]+:',lines[n]):n-=1
    begin='/* CONTRACT (tools/apply.py)' if c else '; CONTRACT (tools/apply.py)'
    end=' * END CONTRACT */' if c else '; END CONTRACT'
    k=n
    if k>0 and lines[k-1].strip()==end.strip():
        k-=1
        while k>0 and lines[k].strip()!=begin:k-=1
        if lines[k].strip()!=begin:raise ValueError('unbalanced managed contract block')
    elif not c:
        # Replace a directly adjacent plain contract, preserving bootstrap/evidence comments.
        while k>0 and lines[k-1].lstrip().startswith(';'):
            if re.match(r'\s*;\s*(?:UNKNOWN|DATA:|Maintained|Image contribution|RAW|PROC/ARG)',lines[k-1]):break
            k-=1
    body=[begin]+[(' * '+b[1:].lstrip()) if c else b for b in block]+[end]
    lines[k:n]=[b+newline for b in body]
    return ''.join(lines)

def typed_data(text,d,kind,count):
    kinds={'byte':1,'db':1,'word':2,'dw':2,'dword':4,'dd':4,'string':1}
    if kind not in kinds:raise ValueError('data kind must be byte, word, dword or string')
    if d['kind'] not in ('data',) or d['form'] not in ('label','db','dw','dd'):
        raise ValueError('typed data requires a physical ASM data label (not code, C or EQU)')
    lines=text.splitlines(keepends=True);n=d['line']-1;first=n
    declaration=S.statement(lines[n]);match=S.DEF.match(declaration)
    if not match:raise ValueError('missing data label')
    inline=(match[2] or '').lower() in ('db','dw','dd')
    if inline:
        if match[2].lower()!='db':raise ValueError('only literal DB runs can be retyped')
    else:first+=1
    j=first;raw=bytearray();selected=[]
    while j<len(lines):
        code=S.statement(lines[j])
        if j==n and inline:code='db '+declaration[match.end():].strip()
        m=re.fullmatch(r'db\s+(.+)',code,re.I)
        if not m:break
        try:raw.extend(S.initializers(m[1],1))
        except ValueError as e:raise ValueError(f'literal DB run required: {e}')
        selected.append(j);j+=1
    if not raw:raise ValueError('no consecutive initialized literal DB run immediately after label')
    width=kinds[kind]
    if len(raw)%width:raise ValueError(f'{len(raw)} bytes cannot be represented by {width}-byte elements')
    if count is not None and count!=len(raw)//width:raise ValueError(f'count {count} differs from complete DB run ({len(raw)//width} elements)')
    linear=d['frame']*16+d['offset'];mz=S.original()
    if raw!=mz.image[linear:linear+len(raw)]:raise ValueError('literal run differs from original at label address')
    if any(linear<=p<linear+len(raw) for p in mz.sites):raise ValueError('typed run overlaps a relocation; symbolic initializer required')
    if d['module'] in S.MODULES:
        mod=next(m for m in S.load_json('asm-map.json')['modules'] if m['name']==d['module'])
        if not any(s['kind']=='data' and s['start']<=d['offset'] and d['offset']+len(raw)<=s['end'] for s in mod['spans']):
            raise ValueError('typed run is outside independently classified ASM data')
    newline='\r\n' if '\r\n' in text else '\n'
    if kind=='string':
        if any(b<32 or b>126 or b==39 for b in raw):raise ValueError('string requires printable ASCII without apostrophes; include terminators in a separate run')
        output=["    db '"+raw.decode('ascii')+"'"]
    else:
        values=[int.from_bytes(raw[i:i+width],'little') for i in range(0,len(raw),width)]
        directive={1:'db',2:'dw',4:'dd'}[width]
        output=['    '+directive+' '+', '.join(f'0{v:0{width*2}X}h' for v in values[i:i+8]) for i in range(0,len(values),8)]
    if inline:output.insert(0,d['name']+':')
    lines[first:j]=[line+newline for line in output]
    return ''.join(lines)

def prepare(ops):
    errors=[];doc=S.names();defs=S.definitions();pairs=[(o['old'],o['new']) for o in ops if o['op']=='rename']
    evidence={}
    for o in ops:
        try:
            if o['op']=='rename':R.prepare([(o['old'],o['new'])])
            elif o['op'] in ('comment','data'):target(o['label'],ops,doc,defs)
        except ValueError as e:errors.append(f"line {o['line']}: {e}")
    if errors:raise ValueError('\n'.join(errors))
    try:updates,tables=R.prepare(pairs) if pairs else ({},{})
    except ValueError as e:
        lines=', '.join(str(o['line']) for o in ops if o['op']=='rename')
        raise ValueError(f'line {lines}: {e}')
    texts=S.read_sources();seen=set()
    # Process against the original index; recalculate source line locations after every insertion.
    for o in ops:
        if o['op'] not in ('comment','data'):continue
        try:
            key,rec,d=target(o['label'],ops,doc,defs)
            marker=(key,o['op'])
            if marker in seen:raise ValueError('duplicate '+o['op']+' for the same identity')
            seen.add(marker)
            current_defs=S.definitions(texts)
            d=next(x for x in current_defs if x['path']==d['path'] and x['name']==d['name'])
            if o['op']=='comment':
                texts[d['path']]=contract(texts[d['path']],d,o['block'])
                for rename in ops:
                    if rename['op']=='rename' and S.resolve_symbol(rename['old'],doc)[0]==key:
                        evidence[rename['old']]=o['block'][0].lstrip('; ')
            else:texts[d['path']]=typed_data(texts[d['path']],d,o['kind'],o['count'])
        except (ValueError,StopIteration) as e:errors.append(f"line {o['line']}: {e}")
    if errors:raise ValueError('\n'.join(errors))
    # Re-run the rename planner with contract evidence, then combine the edited source texts.
    if pairs:updates,tables=R.prepare(pairs,evidence)
    for path,text in texts.items():
        module='C' if path.suffix.lower() in ('.c','.h') else path.stem.upper()
        new=R.substitute(text,tables.get(module,{}),'c' if module=='C' else 'asm').encode('latin1')
        if new!=path.read_bytes():updates[path]=new
    return updates

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('proposal',type=Path);p.add_argument('--dry',action='store_true')
    a=p.parse_args()
    try:
        ops=parse(a.proposal.read_text());updates=prepare(ops)
        report=S.ROOT/'build/workers/naming-infra/apply'/a.proposal.stem
        if a.dry:
            print(f'Validated {len(ops)} directives; {len(updates)} files would change. No files written.')
            return
        R.commit(updates,True,report)
        report.mkdir(parents=True,exist_ok=True)
        (report/'report.json').write_text(S.json_text(dict(proposal=str(a.proposal),result='all three gates passed',
            notes=[dict(line=o['line'],text=o['text']) for o in ops if o['op']=='note'],touched=[str(p.relative_to(S.ROOT)) for p in updates])))
        print(f'Applied {len(ops)} directives; notes/report: {report / "report.json"}')
    except (ValueError,FileNotFoundError,UnicodeError) as e:p.exit(1,f'{a.proposal}: {e}\n')

if __name__=='__main__':main()
