"""Transactional whole-token symbol rename, including C/ASM interface spellings.

Usage: rename.py [--check] OLD NEW [OLD NEW ...] | --file pairs.txt
Ambiguous local names require MODULE:OLD. All writes run the three proof gates;
--check explicitly requests this default. On failure maintained files are restored.
--dry validates without writing or building.

Consumers in c/, tests/ (recursively), native/ and verif/, the translation plan
and closure certificates are updated in the same transaction. L1 c_Label and
UGH_[OS]_MODULE_Label aliases are recognized. cgen runs after the proof gates;
its generated files roll back too. Ambiguous bare consumer names are refused.
Non-address STRUC targets use RECORD:Type or FIELD:Type.Field; fields must have
unique flat TASM identifiers. L0 quoted data remains immutable.
"""
import argparse
import copy
import json
import re
import subprocess
import sys
from common import ROOT
import symtab as S

# TASM 3 / BCC 3 reserved vocabulary, plus every Capstone x86 mnemonic/register.
# Conservative union: a name must be usable in both maintained languages.
RESERVED=set('''auto break case char const continue default do double else enum extern float for
goto if int long register return short signed sizeof static struct switch typedef union unsigned
void volatile while asm cdecl far huge interrupt near pascal _asm _cdecl _cs _ds _es _far _huge
_interrupt _loadds _near _pascal _saveregs _seg _ss _fastcall __asm __cdecl __far __huge
__interrupt __loadds __near __pascal __saveregs __seg __fastcall class delete friend inline new
operator private protected public template this virtual bool catch throw try namespace using
segment ends group proc endp label equ db dw dd df dq dt dup end org assume align even odd
extrn extern externdef global comm common locals nolocals local arg uses model stack code data
const fardata fardata? data? startup exit dosseg jumps nojumps ideal masm radix title subtitle
name include includelib incbin record struc ends struct union macro endm rept irp irpc exitm
purge catstr substr sizestr instr textequ ifdef ifndef ifb ifnb ifidn ifdif ife if1 if2 elseif
else endif err err1 err2 errb errnb errdef errndef errdif erridn out page list nolist xlist
cref nocref dotname nodotname case atexit mask width type length size sizeptr lengthof sizeof
offset seg ptr byte word dword fword qword tbyte abs nothing at use16 use32 read write execute
para paragraph dword page memory common private public stack not and or xor mod shl shr high
low highword lowword eq ne lt le gt ge moderr emul noemul smart nosmart version ifeif display
warn nowarn assume flat tiny small medium compact large huge cpu flags
eax ebx ecx edx esi edi ebp esp ax bx cx dx si di bp sp al ah bl bh cl ch dl dh
cs ds es ss fs gs st mm0 mm1 mm2 mm3 mm4 mm5 mm6 mm7 cr0 cr2 cr3 cr4 dr0 dr1 dr2 dr3 dr6 dr7
'''.lower().split())
try:
    import capstone.x86_const as X
    RESERVED.update(n[8:].lower() for n in vars(X) if n.startswith('X86_INS_'))
    RESERVED.update(n[8:].lower() for n in vars(X) if n.startswith('X86_REG_'))
except ImportError:pass

def validate_name(new,record,doc):
    if any(s['name'].lower()=='_main' or s['name'].upper().endswith('_BASE') or s['name'].lower().startswith('ext_') for s in record['spellings']):
        raise ValueError('fixed linker/contribution anchor; not a semantic naming target')
    if not re.fullmatch('[A-Za-z][A-Za-z0-9_]*',new):raise ValueError(f'{new}: use an ASCII letter followed by letters, digits or underscores')
    if new.lower() in RESERVED:raise ValueError(f'{new}: reserved TASM/C word, instruction or register')
    c=any(s['module']=='C' for s in record['spellings'])
    limit=doc['limits']['bcc_significant'] if c else min(doc['limits']['tasm_significant'],doc['limits']['tasm_public'],doc['limits']['tlink_significant'])
    if len(new)>limit:raise ValueError(f'{new}: length {len(new)} exceeds significant name limit {limit}'+(' (C interface)' if c else ' (TASM/TLINK)'))

def substitute(text,table,language='asm'):
    """Replace identifiers in source/binding comments, never in quoted literals.

    Contract comments and BIND/OMF lines are included; strings are immutable data.
    C escapes and ASM doubled quotes are consumed by the literal alternatives.
    """
    def tokens(s):return S.IDENT.sub(lambda m:table.get(m[0].lower(),m[0]),s)
    if language=='c':
        pattern=re.compile(r'''/\*.*?\*/|//[^\r\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|'''+S.IDENT.pattern,re.S)
        return pattern.sub(lambda m:tokens(m[0]) if m[0].startswith(('/*','//')) else m[0] if m[0][0] in "'\"" else tokens(m[0]),text)
    out=[]
    for line in text.splitlines(keepends=True):
        # A quote in a prose comment must never swallow subsequent source lines.
        pattern=re.compile(r'''\"(?:[^\"]|\"\")*\"|'(?:[^']|'')*'|;[^\r\n]*|'''+S.IDENT.pattern)
        out.append(pattern.sub(lambda m:tokens(m[0]) if m[0][0] not in "'\"" else m[0],line))
    return ''.join(out)

def replace_json(obj,table):
    if isinstance(obj,str):return S.IDENT.sub(lambda m:table.get(m[0].lower(),m[0]),obj)
    if isinstance(obj,list):return [replace_json(x,table) for x in obj]
    if isinstance(obj,dict):
        out={}
        for k,v in obj.items():
            # Only bindings has symbol-valued keys. Schema keys (frame, target,
            # etc.) must survive even if a routine happens to have that name.
            if k=='bindings':
                bindings={replace_json(name,table):address for name,address in v.items()}
                if len(bindings)!=len(v):raise ValueError('metadata binding key collision')
                out[k]=bindings
            else:out[k]=replace_json(v,table)
        return out
    return obj

def external_bindings(mod,texts):
    """Freeze the gate's existing external bindings before replacing their names.

    Explicit frame/offsets remain independent of the evolving names ledger.
    """
    bindings=dict(mod.get('bindings',{}))
    text=texts[ROOT/f"src/asm/{mod['name']}.ASM"]
    for name in re.findall(r'\bextrn\s+(\w+):',text,re.I):
        up=name.upper()
        if up in bindings:continue
        e=re.fullmatch('EXT_([0-9A-F]{4})',up)
        f=re.fullmatch('_FN_(?:([0-9A-F]{4})_)?([0-9A-F]{4})',up)
        if e:
            frame=int(e[1],16);off=mod.get('external_starts',{}).get(f'{frame:04X}',0)
        elif f:frame=int(f[1],16) if f[1] else 0x878;off=int(f[2],16)
        else:raise ValueError('missing independent ASM binding '+name)
        bindings[up]=[frame,off]
    return bindings

def resolve_target(query,doc=None,texts=None):
    if query.upper().startswith(('FIELD:','RECORD:')):return S.resolve_structure(query,texts)
    return S.resolve_symbol(query,doc)

def consumer_table(doc,tables):
    """Unambiguous bare names plus explicit module macros and L1 adapters.

    A local loc_XXXX may exist in several modules. Its module-qualified reference
    can be renamed, but an unqualified ambiguous consumer must be resolved by a
    human; guessing from its containing filename is unsafe.
    """
    owners={}
    for key,rec in doc['symbols'].items():
        for s in rec['spellings']:owners.setdefault(s['name'].lower(),set()).add(key)
    result={}; ambiguous=set()
    def add(old,new):
        old=old.lower()
        if old in result and result[old]!=new:raise ValueError('ambiguous consumer spelling '+old)
        result[old]=new
    for module,table in tables.items():
        for old,new in table.items():
            if len(owners.get(old,()))<=1:add(old,new)
            else:ambiguous.add(old)
            for prefix in (f'UGH_O_{module}_',f'UGH_S_{module}_'):
                add(prefix+old,prefix+new)
            if not old.startswith('_'):
                if len(owners.get(old,()))<=1:add('c_'+old,'c_'+new)
                else:ambiguous.add('c_'+old)
    return result,ambiguous

def consumer_substitute(text,table,tables,ambiguous):
    # Qualified identities also occur in Python/JSON strings and C TRANSLATES comments.
    protected={}
    def qualified(m):
        module,old=m[1].upper(),m[2]
        new=tables.get(module,{}).get(old.lower())
        if new is None:return m[0]
        marker=f'__RENAME_QUALIFIED_{len(protected)}__'
        protected[marker]=m[1]+':'+new
        return marker
    text=re.sub(r'\b([A-Za-z][A-Za-z0-9_]*)\s*:\s*('+S.IDENT.pattern+r')',qualified,text)
    for token in S.IDENT.findall(text):
        if token.lower() in ambiguous and token.lower() not in table:
            raise ValueError('ambiguous consumer token '+token+'; qualify its module before renaming')
    text=S.IDENT.sub(lambda m:table.get(m[0].lower(),m[0]),text)
    for marker,value in protected.items():text=text.replace(marker,value)
    return text

def source_result(path,text,tables):
    module='C' if path.suffix.lower() in ('.c','.h') else path.stem.upper()
    table=dict(tables.get(module,{}))
    # Include declarations and their users share TASM's flat type/field namespace.
    table.update(tables.get('FIELD',{}));table.update(tables.get('RECORD',{}))
    return substitute(text,table,'c' if module=='C' else 'asm')

def prepare(pairs,evidence=None):
    """Return path -> complete bytes and old/new lookup; no disk mutation."""
    texts=S.read_sources();doc=copy.deepcopy(S.names());tables={};taken={};resolved=[]
    consumers={p:p.read_bytes().decode('utf-8') for p in S.consumer_sources()}
    all_tokens={m[0].lower() for t in (*texts.values(),*consumers.values()) for m in S.IDENT.finditer(t)}
    for old,new in pairs:
        key,r=resolve_target(old,doc,texts)
        if key in taken:raise ValueError(f'{old}: symbol renamed twice in one transaction')
        validate_name(new,r,doc)
        existing={s['name'].lower() for s in r['spellings']}
        # Collisions are refused even if the existing symbol is renamed away.
        targets={('_' if s.get('decorated') else '')+new for s in r['spellings']}
        targets.update('c_'+new for s in r['spellings'] if not s.get('decorated'))
        targets.update(prefix+s['module']+'_'+new for s in r['spellings']
                       for prefix in ('UGH_O_','UGH_S_'))
        existing.update('c_'+s['name'].lower() for s in r['spellings'] if not s.get('decorated'))
        existing.update((prefix+s['module']+'_'+s['name']).lower() for s in r['spellings']
                        for prefix in ('UGH_O_','UGH_S_'))
        for target in targets:
            if target.lower() in all_tokens and target.lower() not in existing:raise ValueError(f'{new}: collision with existing token {target}')
            if target.lower() in taken:raise ValueError(f'{new}: collision between proposed names')
        taken[key]=True
        for target in targets:taken[target.lower()]=True
        for s in r['spellings']:
            target=('_' if s.get('decorated') else '')+new
            if s.get('public'):
                # All users of a public spelling share that binding, including ASM EXTRNs.
                for module in (*S.MODULES,*(p.stem.upper() for p in texts),s['module']):
                    tables.setdefault(module,{})[s['name'].lower()]=target
            else:tables.setdefault(s['module'],{})[s['name'].lower()]=target
        if 'address' in r:
            # cgen adds a frame-owner alias as well as source spellings. DGROUP,
            # ZERO and CDATA often have no same-named source module.
            frame=int(r['address'].split(':')[0],16)
            owners={0x13B:'GAME',0x664:'SOUND',0x878:'C',0xA32:'TIMER',
                    0x5C09:'DGROUP',0xA67:'ZERO',0x1A37:'CDATA'}
            owner=owners.get(frame,f'B{frame:04X}')
            tables.setdefault(owner,{})[r['name'].lower()]=new
        resolved.append((key,old,new))
    updates={}
    for path,text in texts.items():
        result=source_result(path,text,tables)
        if result!=text:updates[path]=result.encode('latin1')
    table,ambiguous=consumer_table(doc,tables)
    for path,text in consumers.items():
        result=consumer_substitute(text,table,tables,ambiguous)
        if result!=text:updates[path]=result.encode('utf-8')
    for key,old,new in resolved:
        if key not in doc['symbols']:continue # STRUC symbols have no address identity.
        r=doc['symbols'][key];r['name']=new
        r['evidence']=(evidence or {}).get(old,r['evidence'])
        for s in r['spellings']:s['name']=tables.get(s['module'],{}).get(s['name'].lower(),s['name'])
    updates[S.NAMES]=S.json_text(doc).encode()
    layout=S.load_json('reloc-layout.json')
    # Stable dictionary KEYS and their uses are deliberately untouched.
    for key,value in layout['labels'].items():
        module='GAME' if key.startswith('game_') else 'SOUND' if key.startswith('sound_') else 'TIMER'
        layout['labels'][key]=tables.get(module,{}).get(value.lower(),value)
    updates[ROOT/'metadata/reloc-layout.json']=S.json_text(layout).encode()
    amap=S.load_json('asm-map.json')
    for i,m in enumerate(amap['modules']):
        m['bindings']=external_bindings(m,texts)
        amap['modules'][i]=replace_json(m,tables.get(m['name'],{}))
        amap['modules'][i]['name']=m['name']
        amap['modules'][i]['bindings']={k.upper():v for k,v in amap['modules'][i]['bindings'].items()}
    updates[ROOT/'metadata/asm-map.json']=S.json_text(amap).encode()
    data_layout=ROOT/'metadata/data-layout.json'
    if data_layout.exists():
        data=json.loads(data_layout.read_text())
        # Public tokens have one binding across every generated data module.
        # Apply each module's substitutions to its curated names/expressions too.
        for i,m in enumerate(data['modules']):
            data['modules'][i]=replace_json(m,tables.get(m['name'],{}))
            data['modules'][i]['name']=m['name']
        updates[data_layout]=S.json_text(data).encode()
    inv=ROOT/'src/c/inventory.json'
    updates[inv]=S.json_text(replace_json(json.loads(inv.read_text()),tables.get('C',{}))).encode()
    regions=ROOT/'metadata/naming-regions.json'
    if regions.exists():
        reg=json.loads(regions.read_text())
        for region in reg['regions']:
            region['routines']=[n.split(':',1)[0]+':'+replace_json(n.split(':',1)[1],tables.get(region['module'],{})) for n in region['routines']]
            region['data_labels']=[n.split(':',1)[0]+':'+replace_json(n.split(':',1)[1],tables.get(n.split(':')[0],{})) for n in region['data_labels']]
        updates[regions]=S.json_text(reg).encode()
    return {p:b for p,b in updates.items() if not p.exists() or p.read_bytes()!=b},tables

def gates(logdir):
    logdir.mkdir(parents=True,exist_ok=True)
    for tool in ('asmverify','cjudge','verify'):
        p=subprocess.run([sys.executable,str(ROOT/f'tools/{tool}.py')],cwd=ROOT,capture_output=True,text=True)
        (logdir/f'{tool}.txt').write_text(p.stdout+p.stderr)
        print(f'{tool}.py -> {p.returncode}',flush=True)
        if p.returncode:raise ValueError(f'{tool}.py failed; see {logdir/tool}.txt')

def commit(updates,check=False,logdir=None):
    before={p:p.read_bytes() if p.exists() else None for p in updates}
    # cgen runs only after the fresh proof build. Its derived outputs belong to
    # this same rollback boundary, including headers it might create for a package.
    generated=set()
    if check and (ROOT/'c').is_dir():
        generated={ROOT/'c/ugh_sym.h',ROOT/'c/ugh_adapters.h',ROOT/'c/dispatch_table.inc',
                   ROOT/'build/c/symbols.json'}|{p.with_suffix('.h') for p in (ROOT/'c').glob('*.c')}
        for p in generated:before.setdefault(p,p.read_bytes() if p.exists() else None)
    try:
        for p,b in updates.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        if check:gates(logdir or ROOT/'build/workers/naming-infra/rename-check')
        if generated:
            p=subprocess.run([sys.executable,str(ROOT/'tools/cgen.py')],cwd=ROOT,capture_output=True,text=True)
            out=logdir or ROOT/'build/workers/naming-infra/rename-check'
            (out/'cgen.txt').write_text(p.stdout+p.stderr)
            print(f'cgen.py -> {p.returncode}',flush=True)
            if p.returncode:raise ValueError('cgen.py failed; see '+str(out/'cgen.txt'))
    except BaseException:
        for p,b in before.items():
            if b is None:p.unlink(missing_ok=True)
            else:p.write_bytes(b)
        print('Transaction restored all maintained files.',file=sys.stderr)
        raise
    for p in sorted(set(updates)|generated):
        if p.exists() and p.read_bytes()!=before.get(p):print('touched '+str(p.relative_to(ROOT)).replace('\\','/'))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pairs',nargs='*');p.add_argument('--file',type=S.Path);p.add_argument('--check',action='store_true',help='run all three gates (also the default)');p.add_argument('--dry',action='store_true')
    a=p.parse_args();pairs=[]
    if len(a.pairs)%2:p.error('OLD NEW pairs required')
    pairs.extend(zip(a.pairs[::2],a.pairs[1::2]))
    if a.file:
        for n,line in enumerate(a.file.read_text().splitlines(),1):
            words=line.split('#',1)[0].split()
            if not words:continue
            if len(words)!=2:p.error(f'{a.file}:{n}: expected OLD NEW')
            pairs.append(tuple(words))
    if not pairs:p.error('supply at least one OLD NEW pair')
    try:
        updates,_=prepare(pairs)
        if a.dry:
            for path in updates:print('would touch '+str(path.relative_to(ROOT)))
        else:commit(updates,True)
    except ValueError as e:p.exit(1,str(e)+'\n')

if __name__=='__main__':main()
