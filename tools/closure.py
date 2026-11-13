"""Validate semantic-closure certificates and the native source boundary.

This is a source rule checker, not a C verifier. pycparser enumerates actual
direct calls (including static helpers); includes are checked literally. Unknown
syntax/indirect calls fail closed. Comments and strings do not trigger bans.
"""
import argparse,json,re,sys
from pathlib import Path
from pycparser import c_ast,c_parser
ROOT=Path(__file__).resolve().parents[1]
FIELDS=set('component status original native purpose interface callers callees indirect memory assumptions eliminated retained evidence amiga uncertainty dependencies'.split())
STATUSES='unanalyzed analyzed boundary-established migrated verified-under-assumptions verified-within-contract integration-validated blocked'.split()
FORBIDDEN=r'\b(?:Regs|ugh_\w+|UGH_\w+|rd(?:8|16|32)(?:_linear)?|wr(?:8|16|32)|flag|szp|logic|sub16|add16|dec16|arg16|push|pop|lin|step|set_al|set_ah|GAME_SEG|DATA_SEG|SOUND_SEG|TIMER_SEG|ax|bx|cx|dx|si|di|bp|sp|cs|ds|es|ss|ip|CF|PF|AF|ZF|SF|IF|DF|OF)\b|(?:->|\.)\s*flags\b'

def clean(text):
    return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                  lambda m:' '*(len(m[0])) if m[0].startswith(('/', '"', "'")) else m[0],text,flags=re.S)

def stripped(text):
    return re.sub(r'^\s*#.*$','',re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S),flags=re.M)

PREAMBLE='''typedef unsigned char uint8_t; typedef signed char int8_t;
typedef unsigned short uint16_t; typedef short int16_t;
typedef unsigned int uint32_t; typedef int int32_t;
typedef unsigned long long uint64_t; typedef long long int64_t;
typedef unsigned long long size_t;
typedef struct Regs { uint16_t ax,bx,cx,dx,si,di,bp,sp,cs,ds,es,ss,ip,flags; } Regs;
'''

def actual_dependencies(path):
    text=path.read_text()
    includes=re.findall(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]',text,re.M)
    # Expand project headers for types; system/L1 headers contribute no calls to
    # this translation unit's maintained text. No macro-generated control flow is
    # accepted by this deliberately small native dialect.
    seen=set()
    def expand(p):
        if p in seen:return ''
        seen.add(p);t=p.read_text();prefix=''
        for inc in re.findall(r'^\s*#\s*include\s*"([^"]+)"',t,re.M):
            child=(p.parent/inc).resolve()
            if child.is_relative_to((ROOT/'native').resolve()) and child.exists():prefix+=expand(child)
        return prefix+stripped(t)+'\n'
    code=expand(path)
    code=re.sub(r'\bEXPORT\b','',code)
    tree=c_parser.CParser().parse(PREAMBLE+code,filename=str(path))
    calls=set()
    class Calls(c_ast.NodeVisitor):
        def visit_FuncCall(self,node):
            if not isinstance(node.name,c_ast.ID):raise ValueError(f'{path}: indirect call requires an explicit checker extension')
            calls.add(node.name.name);self.generic_visit(node)
    Calls().visit(tree)
    return dict(includes=sorted(set(includes)),calls=sorted(calls))

def validate():
    errors=[];owners={};count=0;original_offsets=set()
    for path in sorted((ROOT/'metadata/closure').glob('*.json')):
        count+=1
        try:
            cert=json.loads(path.read_text());missing=FIELDS-set(cert)
            if missing:raise ValueError('missing fields: '+', '.join(sorted(missing)))
            if cert['status'] not in STATUSES:raise ValueError('invalid status')
            if cert['component']!=path.stem:raise ValueError('component differs from filename')
            original_offsets.update(int(x,16) for x in re.findall(r'\b[0-9A-Fa-f]{4}:([0-9A-Fa-f]{4})\b',json.dumps(cert['original'])) if int(x,16)>=256)
            for key in FIELDS-{'uncertainty'}:
                if not cert[key]:raise ValueError(f'empty field: {key}')
            if cert['status']=='blocked' and not cert['uncertainty']:raise ValueError('blocked status needs reason')
            for evidence in cert['evidence']:
                for key in ('property','level','method','command','result','date'):
                    if not evidence.get(key):raise ValueError(f'evidence missing {key}')
                if evidence['level'] not in ('A','B','C','D'):raise ValueError('invalid evidence level')
            earned={e['level'] for e in cert['evidence'] if not str(e['result']).lower().startswith(('pending','blocked','not run'))}
            needs={'verified-under-assumptions':'B','verified-within-contract':'A','integration-validated':'D'}
            if cert['status'] in needs and needs[cert['status']] not in earned:raise ValueError('status has no supporting evidence level')
            for name,declared in cert['dependencies'].items():
                p=(ROOT/name).resolve()
                if not p.is_relative_to((ROOT/'native').resolve()) or not p.is_file():raise ValueError(f'invalid native path {name}')
                if name in owners:raise ValueError(f'duplicate ownership {name}')
                owners[name]=path.name
                actual=actual_dependencies(p)
                if actual!={k:sorted(set(v)) for k,v in declared.items()}:raise ValueError(f'{name}: declared dependencies differ: actual={actual}')
        except Exception as exc:errors.append(f'{path.relative_to(ROOT)}: {exc}')
    if not count:errors.append('no closure certificates')
    for path in sorted((ROOT/'native').rglob('*')):
        if path.suffix not in ('.c','.h'):continue
        name=path.relative_to(ROOT).as_posix()
        if name not in owners:errors.append(f'unowned native file: {name}')
        if 'bridge' in path.relative_to(ROOT/'native').parts:continue
        source=path.read_text();match=re.search(FORBIDDEN,clean(source))
        if match:errors.append(f'{name}: forbidden identifier {match[0]}')
        if re.search(r'#\s*include\s*[<"](?:.*[/\\])?ugh\w*\.h',source):errors.append(f'{name}: L1 header dependency')
        for token in re.findall(r'\b(?:0[xX][0-9a-fA-F]+|[0-9]+)[uUlL]*\b',clean(source)):
            value=re.sub(r'[uUlL]+$','',token)
            number=int(value,16 if value.lower().startswith('0x') else 10)
            if number in original_offsets:errors.append(f'{name}: original code offset literal {token}')
    return count,errors

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--inventory',action='store_true');args=parser.parse_args()
    if args.inventory:
        print(json.dumps({p.relative_to(ROOT).as_posix():actual_dependencies(p) for p in sorted((ROOT/'native').rglob('*')) if p.suffix in ('.c','.h')},indent=2))
    else:
        count,errors=validate()
        for error in errors:print('FAIL '+error)
        print(f'{count} certificate(s), {len(errors)} error(s)');raise SystemExit(bool(errors))
