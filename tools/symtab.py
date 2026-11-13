"""Small source/address index shared by the naming tools; no build output is edited.

names.json preserves initial address-based identities. Source comments supply ASM
coordinates, not proof; the existing independent gates remain the authority.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from common import ROOT, BUILD, MZ, load_json, sha256
from fragment import statement

IDENT = re.compile(r'(?<![A-Za-z0-9_?$@])[A-Za-z_?$@][A-Za-z0-9_?$@]*')
DEF = re.compile(r'^([A-Za-z_?$@][\w?$@]*)(?::|\s+(equ|label|proc|db|dw|dd)\b)', re.I)
NAMES = ROOT/'metadata/names.json'
MODULES = {'GAME': (0x13B,8,0x529C), 'SOUND': (0x664,12,0x2143),
           'TIMER': (0xA32,6,0x341), 'C': (0x878,3,0x1BA5)}

def sources():
    return sorted(p for folder in ('asm','data','c') for p in (ROOT/'src'/folder).rglob('*')
                  if p.is_file() and p.suffix.lower() in ('.asm','.inc','.c','.h'))

def read_sources():
    return {p:p.read_bytes().decode('latin1') for p in sources()}

def consumer_sources():
    """Maintained semantic users, excluding caches and generated build output.

    Keep this separate from sources(): these files have no L0 address identities.
    Generated interfaces are included in the transaction and regenerated after proof.
    """
    extensions={'.c','.h','.inc','.py','.json','.md','.txt','.cmake','.in','.yaml','.yml'}
    paths=[]
    for folder in ('c','tests','native','verif'):
        paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts
                     and (p.suffix.lower() in extensions or p.name in ('Makefile','CMakeLists.txt')))
    plan=ROOT/'metadata/translation-plan.json'
    if plan.exists():paths.append(plan)
    paths.extend((ROOT/'metadata/closure').glob('*.json'))
    return sorted(set(paths))

def structure_definitions(texts=None):
    """Non-address STRUC types/fields; never add these to names.json.

    MASM-mode TASM exposes fields as flat identifiers. Require qualified queries
    (FIELD:Type.Field, RECORD:Type), and reject duplicate declarations rather than
    silently assigning a field to the wrong record. No binary layout is inferred.
    """
    out=[]
    for path,text in (read_sources() if texts is None else texts).items():
        owner=None
        for n,line in enumerate(text.splitlines(),1):
            code=statement(line)
            start=re.fullmatch(r'(\w+)\s+struc',code,re.I)
            if start:
                if owner:raise ValueError('nested STRUC is unsupported: '+str(path))
                owner=start[1]
                out.append(dict(module='RECORD',name=owner,kind='record-type',form='struc',path=path,line=n))
            elif owner and re.fullmatch(re.escape(owner)+r'\s+ends',code,re.I):owner=None
            elif owner:
                field=re.match(r'(\w+)\s+(db|dw|dd|df|dq|dt)\b',code,re.I)
                if field:out.append(dict(module='FIELD',owner=owner,name=field[1],kind='record-field',
                                         form='field',path=path,line=n))
    return out

def resolve_structure(query,texts=None):
    fields=structure_definitions(texts)
    if query.upper().startswith('RECORD:'):
        matches=[d for d in fields if d['module']=='RECORD' and d['name'].lower()==query[7:].lower()]
    elif query.upper().startswith('FIELD:') and '.' in query:
        owner,name=query[6:].split('.',1)
        matches=[d for d in fields if d['module']=='FIELD' and d['owner'].lower()==owner.lower()
                 and d['name'].lower()==name.lower()]
    else:raise ValueError(query+': use RECORD:Type or FIELD:Type.Field for STRUC symbols')
    if len(matches)!=1:raise ValueError(query+': unknown or duplicate STRUC symbol')
    d=matches[0]
    # Flat field identifiers must be unique across maintained include files.
    if sum(x['name'].lower()==d['name'].lower() for x in fields)!=1:
        raise ValueError(query+': duplicate flat TASM identifier')
    return query,dict(name=d['name'],kind=d['kind'],evidence='STRUC declaration',
                      spellings=[dict(module=d['module'],name=d['name'],public=True,decorated=False)])

def json_text(obj):
    return json.dumps(obj,indent=2,ensure_ascii=True)+'\n'

def original():
    raw=(BUILD/'oracle/UGH_X.EXE').read_bytes()
    if sha256(raw)!=load_json('oracle.json')['expanded']['file_sha256']:
        raise ValueError('expanded oracle does not match lock; run tools/oracle.py')
    return MZ(raw)

def number(s):
    s=s.strip()
    if re.fullmatch(r'[0-9A-Fa-f]+h',s):return int(s[:-1],16)
    return int(s,0) if s.startswith('0x') else int(s)

def initializers(s,width):
    """Only literal, initialized data; symbolic expressions/fixups are rejected."""
    out=bytearray()
    for part in re.split(r',(?=(?:[^\'\"]|\'[^\']*\'|\"[^\"]*\")*$)',s):
        part=part.strip()
        dup=re.fullmatch(r'(\d+)\s+dup\s*\((.*)\)',part,re.I)
        if dup:out.extend(initializers(dup[2],width)*int(dup[1]));continue
        if len(part)>=2 and part[0] in "'\"" and part[-1]==part[0]:
            if width!=1:raise ValueError('string initializer requires db')
            out.extend(part[1:-1].encode('latin1'));continue
        try:v=number(part)
        except ValueError:raise ValueError('literal data only (no ?, symbols, SEG or OFFSET)')
        if not 0<=v<1<<(8*width):raise ValueError('initializer out of range')
        out.extend(v.to_bytes(width,'little'))
    return bytes(out)

def data_size(s,width):
    # Counting symbolic DWs is safe here; rewriting them is deliberately forbidden.
    parts=re.split(r',(?=(?:[^\'\"]|\'[^\']*\'|\"[^\"]*\")*$)',s)
    total=0
    for p in parts:
        d=re.fullmatch(r'\s*(\d+)\s+dup\s*\((.*)\)\s*',p,re.I)
        if d:total+=int(d[1])*data_size(d[2],width)
        elif p.strip().startswith(("'",'"')):total+=len(p.strip()[1:-1])
        else:total+=width
    return total

def definitions(texts=None):
    texts=read_sources() if texts is None else texts
    known={};known_kind={}
    if NAMES.exists():
        for r in json.loads(NAMES.read_text())['symbols'].values():
            for s in r['spellings']:
                known[s['module'],s['name']]=tuple(int(x,16) for x in r['address'].split(':'))
                known_kind[s['module'],s['name']]=r['kind']
    out=[]
    for path,text in texts.items():
        module=path.stem.upper() if path.suffix.lower()!='.c' else 'C'
        lines=text.splitlines()
        if module=='C':
            for n,line in enumerate(lines):
                m=re.search(r'/\*\s*@([\dA-Fa-f]+):([\dA-Fa-f]+)\s*\*/',line)
                if m:
                    j=n+1
                    # Managed contracts go before the address marker, never between marker and definition.
                    while j<len(lines) and not lines[j].strip():j+=1
                    f=re.search(r'\b(\w+)\s*\(',lines[j])
                    if f:out.append(dict(module='C',name=f[1],frame=int(m[1],16),offset=int(m[2],16),
                                         kind='c-function',path=path,line=j+1,form='function'))
            for n,line in enumerate(lines):
                m=re.match(r'int\s+(\w+)\s*=\s*0\s*;',line)
                if m:
                    # These are the only two initialized C globals; recover offsets from the persistent map later.
                    prior=[x for x in out if x['kind']=='c-global']
                    out.append(dict(module='C',name=m[1],frame=0x1A37,offset=len(prior)*2,
                                    kind='c-global',path=path,line=n+1,form='global'))
            continue
        if module in MODULES:frame,pos,end=MODULES[module]
        elif module=='DGDATA':frame,pos,end=0x5C09,0x92,0x7B7C
        elif module=='ZERO':frame,pos,end=0xA67,0,64768
        elif re.fullmatch('B[0-9A-F]{4}',module):frame,pos,end=int(module[1:],16),0,0x10000
        else:continue
        base=pos
        pending=[]
        def flush(at):
            for x in pending:x['offset']=at
            pending.clear()
        for n,line in enumerate(lines):
            code=statement(line)
            at=re.search(r';\s*@([0-9A-Fa-f]{4})\b',line)
            if at:pos=int(at[1],16);flush(pos)
            d=DEF.match(code)
            if d:
                name,form=d[1],(d[2] or 'label').lower()
                fr,off=frame,pos
                fixed=False
                rhs=code[d.end():].strip()
                if form=='equ':
                    if re.fullmatch(r'[0-9A-Fa-f]+h',rhs):
                        off=number(rhs);fr=0x5C09 if name.lower().startswith('ds_') else frame
                    else:
                        e=re.fullmatch(r'\w+_BASE\s*\+\s*([0-9A-Fa-f]+h)',rhs,re.I)
                        if not e:continue
                        off=base+number(e[1])
                if form in ('label','proc'):
                    mechanical=re.fullmatch(r'(?:loc|sub|byte_data)_([0-9A-Fa-f]{4})',name)
                    if mechanical:off=int(mechanical[1],16);fixed=True
                    elif (module,name) in known:fr,off=known[module,name];fixed=True
                kind='code' if module in MODULES else 'data'
                if fr==0x5C09 or form=='equ' and not name.lower().startswith(('_fn_','_main')):kind='data'
                if name.lower().startswith(('byte','word','dword')):kind='data'
                if (module,name) in known:
                    fr,off=known[module,name];kind=known_kind[module,name];fixed=True
                x=dict(module=module,name=name,frame=fr,offset=off,kind=kind,path=path,line=n+1,form=form)
                out.append(x)
                if form in ('label','proc') and not fixed and module in MODULES and not name.upper().endswith('_BASE') and not name.lower().startswith('ext_'):
                    pending.append(x)
                if form in ('db','dw','dd'):
                    flush(pos);pos+=data_size(rhs,{'db':1,'dw':2,'dd':4}[form])
            data=re.match(r'^(db|dw|dd)\s+(.*)',code,re.I)
            if data:
                flush(pos);pos+=data_size(data[2],{'db':1,'dw':2,'dd':4}[data[1].lower()])
            if re.fullmatch(r'\w+\s+ends',code,re.I):flush(end)
    return out

def bootstrap():
    defs=definitions();records={}
    # Decorated interface equates are paired with a local routine/data alias where one exists.
    for d in defs:
        if d['name'].startswith('_fn_') or d['name'].startswith('_g_'):continue
        key=f"{d['frame']:04X}:{d['offset']:04X}/{d['module']}/{d['name']}"
        # Repeated DGROUP equates represent one symbol used by several ASM modules.
        if d['frame']==0x5C09 and d['form']=='equ':key=f"5C09:{d['offset']:04X}/DGROUP/{d['name']}"
        r=records.setdefault(key,dict(name=d['name'],kind=d['kind'],address=f"{d['frame']:04X}:{d['offset']:04X}",
            evidence='Address and declaration in '+str(d['path'].relative_to(ROOT)).replace('\\','/')+'.',spellings=[]))
        r['spellings'].append(dict(module=d['module'],name=d['name'],decorated=False))
    for d in defs:
        if not (d['name'].startswith('_fn_') or d['name'].startswith('_g_')):continue
        addr=f"{d['frame']:04X}:{d['offset']:04X}"
        choices=[(k,r) for k,r in records.items() if r['address']==addr and any(s['module']==d['module'] for s in r['spellings'])
                 and (r['name'].startswith('loc_') if '_fn_' in d['name'] else r['name'].startswith('byte_') and not r['name'].startswith('byte_data_'))]
        if choices:key,r=choices[0]
        else:
            key=f"{addr}/{d['module']}/{d['name']}"
            r=records.setdefault(key,dict(name=d['name'][1:],kind='code' if '_fn_' in d['name'] else 'data',address=addr,
                evidence='Public interface equate in '+d['path'].name+'.',spellings=[]))
        r['spellings'].append(dict(module=d['module'],name=d['name'],decorated=True,public=True))
        r['spellings'].append(dict(module='C',name=d['name'][1:],decorated=False,public=True))
    # C functions have decorated extern references but no definition in ASM.
    for r in records.values():
        if r['kind']=='c-function':
            for module in MODULES:
                if module!='C':r['spellings'].append(dict(module=module,name='_'+r['name'],decorated=True,public=True))
    return dict(schema=1,limits=dict(tasm_significant=255,tasm_public=63,bcc_significant=32,tlink_significant=63,
                    evidence='build/workers/naming-infra/length-probes.json'),symbols=records)

def names():
    return json.loads(NAMES.read_text()) if NAMES.exists() else bootstrap()


def register_data():
    """Add newly curated data labels without regenerating permanent identities.

    Reuse an existing DGROUP variable identity when its exact spelling/address
    already occurs as an EQU view. Public data spellings are renameable across
    all consumers. Code exports used by data pointers keep their original IDs.
    """
    doc=names(); layout=load_json('data-layout.json')
    from datagen import validate
    validate(layout)
    for m in layout['modules']:
        for l in m['labels']:
            addr=f"{m['frame']:04X}:{l['offset']:04X}"
            hits=[r for r in doc['symbols'].values() if r['address']==addr and
                  any(s['name']==l['name'] for s in r['spellings'])]
            if len(hits)>1:raise ValueError('ambiguous existing data identity '+l['name'])
            if hits:r=hits[0]
            else:
                key=f"{addr}/{m['name']}/{l['name']}"
                r=dict(name=l['name'],kind='data',address=addr,
                       evidence='Curated layout metadata/data-layout.json; '+l.get('comment','')+
                       ' See enclosing object/field comments and docs/data.md.',spellings=[])
                doc['symbols'][key]=r
            spelling=next((s for s in r['spellings'] if s['module']==m['name'] and s['name']==l['name']),None)
            if spelling is None:
                spelling=dict(module=m['name'],name=l['name'],decorated=False);r['spellings'].append(spelling)
            if l.get('public'):
                spelling['public']=True
                for s in r['spellings']:
                    if s['name']==l['name']:s['public']=True
        for e in m['externals']:
            # Register cross-module references as spellings of the exported identity.
            hits=[r for r in doc['symbols'].values() if any(s['name']==e['name'] for s in r['spellings'])]
            if len(hits)!=1:raise ValueError('missing/ambiguous external data binding '+e['name'])
            r=hits[0]
            for s in r['spellings']:
                if s['name']==e['name']:s['public']=True
            if not any(s['module']==m['name'] and s['name']==e['name'] for s in r['spellings']):
                r['spellings'].append(dict(module=m['name'],name=e['name'],decorated=False,public=True))
    NAMES.write_text(json_text(doc))
    print('Registered curated data labels; preserved all existing identity keys')

def resolve_symbol(query,doc=None):
    doc=names() if doc is None else doc
    if query in doc['symbols']:return query,doc['symbols'][query]
    scope=None
    scopes={'DGROUP'}|{s['module'] for r in doc['symbols'].values() for s in r['spellings']}
    if ':' in query and query.split(':',1)[0].upper() in scopes:
        scope,query=query.split(':',1);scope=scope.upper()
    hits=[]
    for key,r in doc['symbols'].items():
        for s in r['spellings']:
            if s['name'].lower()==query.lower() and (scope is None or s['module']==scope or scope=='DGROUP' and r['address'].startswith('5C09:')):
                hits.append((key,r));break
    if len(hits)!=1:raise ValueError(f'{query}: '+('unknown symbol' if not hits else 'ambiguous; use MODULE:'+query))
    return hits[0]

def address(query,module=None):
    try:
        _,r=resolve_symbol(query);a,b=r['address'].split(':');return int(a,16)*16+int(b,16)
    except ValueError as exc:
        if 'ambiguous' in str(exc):raise
    q=query.lower()
    if q.startswith('ds:'):return 0x5C090+int(q[3:],16)
    if q.startswith('cs:'):
        if not module:raise ValueError('cs: requires --module GAME|SOUND|TIMER|C')
        return MODULES[module.upper()][0]*16+int(q[3:],16)
    if ':' in q:
        a,b=q.split(':');return int(a,16)*16+int(b,16)
    return int(q,16)

def locate(linear,defs=None):
    defs=definitions() if defs is None else defs
    candidates=[d for d in defs if d['frame']*16+d['offset']<=linear]
    # A nearest label is meaningful only inside the same owned module/frame.
    owners=[name for name,(f,a,b) in MODULES.items() if f*16+a<=linear<f*16+b]
    if owners:candidates=[d for d in candidates if d['module']==owners[0] and d['frame']==MODULES[owners[0]][0]]
    else:candidates=[d for d in candidates if d['kind'] in ('data','c-global') and 0<=linear-(d['frame']*16+d['offset'])<65536]
    if not candidates:raise ValueError('no maintained source label at this address')
    return max(candidates,key=lambda d:(d['frame']*16+d['offset'],d['form'] not in ('equ',),not d['name'].startswith(('ext_','_'))))

def routines():
    defs=definitions();out=[]
    for m in load_json('asm-map.json')['modules']:
        for e in m['entries']:
            # entries includes branch targets. Only call/seed/vector/callback entries are routines.
            if not any(not re.match(r'^(?:j\w*|loop\w*) at ',v) for v in e['evidence']):continue
            hits=[d for d in defs if d['module']==m['name'] and d['offset']==e['offset'] and d['form'] in ('label','proc') and not d['name'].startswith(('ext_','_')) and not d['name'].endswith('_BASE')]
            if not hits:raise ValueError(f"{m['name']}:{e['offset']:04X}: routine entry has no maintained source label")
            out.append(dict(hits[0]))
    out.extend(dict(d) for d in defs if d['kind']=='c-function')
    for module in MODULES:
        rs=sorted((d for d in out if d['module']==module),key=lambda d:d['offset'])
        lines=(ROOT/('src/c/module.c' if module=='C' else f'src/asm/{module}.ASM')).read_text().splitlines()
        for i,d in enumerate(rs):
            d['end']=rs[i+1]['offset'] if i+1<len(rs) else MODULES[module][2]
            d['end_line']=rs[i+1]['line']-1 if i+1<len(rs) else len(lines)
    return out

def build_regions():
    """Cut nearby routines into bounded regions, favouring fewer cut call edges."""
    from graph import analyse
    rs,graph=analyse();regions=[]
    for module in MODULES:
        pending=sorted((r for r in rs if r['module']==module),key=lambda r:r['line'])
        while pending:
            if pending[-1]['end_line']-pending[0]['line']+1<=2000:cut=len(pending)
            else:
                options=[]
                for j in range(1,len(pending)):
                    size=pending[j-1]['end_line']-pending[0]['line']+1
                    if not 800<=size<=2000:continue
                    left={r['linear'] for r in pending[:j]};right={r['linear'] for r in pending[j:]}
                    edges=sum(len(set(graph[x]['callees']) & right) for x in left)
                    edges+=sum(len(set(graph[x]['callees']) & left) for x in right)
                    options.append((edges+abs(size-1400)/400,j))
                cut=min(options)[1] if options else 1
            chunk,pending=pending[:cut],pending[cut:]
            ports=sorted(set(p for r in chunk for p in graph[r['linear']]['ports']))
            services=sorted(set(p for r in chunk for p in graph[r['linear']]['services']))
            refs=Counter(d for r in chunk for d in graph[r['linear']]['data_symbols'])
            regions.append(dict(id=f'{module.lower()}-{sum(r["module"]==module for r in regions)+1:02}',module=module,
                description=f"{chunk[0]['frame']:04X}:{chunk[0]['offset']:04X}..{chunk[-1]['end']:04X}; ports "+(', '.join(ports) or 'none resolved')+'; INT/AH '+(', '.join(services) or 'none resolved'),
                source_lines=chunk[-1]['end_line']-chunk[0]['line']+1,
                routines=[f"{module}:{r['name']}" for r in chunk],data_labels=sorted(refs)))
    # Assign each referenced data label primarily to its heaviest user region.
    for label in {d for r in regions for d in r['data_labels']}:
        candidates=[r for r in regions if label in r['data_labels']]
        owner=max(candidates,key=lambda reg:sum(graph[r['linear']]['data_symbols'].count(label) for r in rs if f"{r['module']}:{r['name']}" in reg['routines']))
        for r in candidates:
            if r is not owner:r['data_labels'].remove(label)
    doc=dict(schema=1,note='Static call/seed routines, including unreferenced seeds; shared tails stay with their physical interval. Small module/remainder and indivisible large routines may be outside the target size.',regions=regions)
    check_regions(doc,rs)
    return doc

def check_regions(doc,rs=None):
    expected=Counter(f"{r['module']}:{r['name']}" for r in (routines() if rs is None else rs))
    got=Counter(n for r in doc['regions'] for n in r['routines'])
    if got!=expected or any(v!=1 for v in got.values()):raise ValueError('region routine partition is incomplete, duplicated or stale')
    return len(got)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--init',action='store_true');p.add_argument('--regions',action='store_true');p.add_argument('--check',action='store_true')
    p.add_argument('--register-data',action='store_true',help='add curated data labels to the existing ledger')
    a=p.parse_args()
    if a.init:
        if NAMES.exists():raise ValueError('names.json already exists; identities must not be regenerated')
        NAMES.write_text(json_text(bootstrap()))
    if a.regions:(ROOT/'metadata/naming-regions.json').write_text(json_text(build_regions()))
    if a.register_data:register_data()
    if a.check:
        doc=names();defs=definitions()
        for d in defs:
            hits=[r for r in doc['symbols'].values() if any(s['module']==d['module'] and s['name']==d['name'] for s in r['spellings'])]
            if len(hits)!=1 or hits[0]['address']!=f"{d['frame']:04X}:{d['offset']:04X}":raise ValueError('missing/stale identity '+d['module']+':'+d['name'])
        count=check_regions(load_json('naming-regions.json'))
        print(f"{len(doc['symbols'])} address identities; {count} routines partitioned exactly once")

if __name__=='__main__':main()
