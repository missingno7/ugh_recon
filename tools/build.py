"""Fresh plain and derived proof builds. No oracle input or output rewriting."""
import json, shutil
from common import ROOT, BUILD, TOOLS, load_json, sha256
from dos import dos

WORK=BUILD/'link'
OBJECTS=['C0H','DGDATA','GAME','SOUND','ZERO','MODULE','TIMER',
         'B1A38','B1E1F','B2BC6','B2BF6','B2D9A','B2F9E','B2FB7',
         'B325B','B3260','B3265','B326B','B3274','B3279','B3444',
         'B3629','B3632','B3637','B37A7','B438A','B4E83','B5B63','RESERVE']

def build_variant(variant):
    from fragment import write_variant
    from omf import parse
    directory=WORK/variant
    directory.mkdir(parents=True,exist_ok=True)
    # Remove only known generated files in the explicitly named build directory.
    for pattern in ('*.OBJ','*.EXE','*.MAP','*.LST','*.log','*.BAK'):
        for p in directory.glob(pattern):p.unlink()
    layout=load_json('reloc-layout.json')
    objects=OBJECTS.copy()
    if variant=='proof':
        write_variant(ROOT/'src/asm',ROOT/'metadata/reloc-layout.json',directory)
        objects.insert(1,'LAYOUT')
    for name,entry in load_json('toolchain-lock.json')['libraries'].items():
        data=(TOOLS/entry['path']).read_bytes()
        if sha256(data)!=entry['sha256']:raise ValueError('library hash mismatch: '+name)
        (directory/name).write_bytes(data)
    from asmverify import validate_map, source_audit
    asm_map=load_json('asm-map.json');validate_map(asm_map)
    mapped={m['name']:m for m in asm_map['modules']}
    includes=sorted((ROOT/'src/asm').glob('*.INC'))
    for include in includes:shutil.copyfile(include,directory/include.name)
    sources=list((ROOT/'src/asm').glob('*.ASM'))+list((ROOT/'src/data').glob('*.ASM'))
    if {p.stem for p in sources}!=set(OBJECTS)-{'C0H','MODULE'}:
        raise ValueError('missing or unlisted assembly/data source')
    for folder in ('asm','data'):
        for p in sorted((ROOT/'src'/folder).glob('*.ASM')):
            derived=folder=='asm' or p.stem in layout['deferred_data_externals']
            if not derived or variant=='plain':shutil.copyfile(p,directory/p.name)
            generated=directory/p.name
            log=dos('TASM',['/kh8192',f'{p.name},{p.stem}.OBJ,{p.stem}.LST'],directory)
            (directory/(p.stem+'.log')).write_text(log)
            if folder=='asm':
                mod=mapped[p.stem]
                if variant=='proof' and p.stem in ('GAME','SOUND'):
                    # Audit generated listing data directives against the same independent
                    # classification. Placement is diagnostic only, never linker input.
                    rule=next(m for m in layout['modules'] if m['name']==p.stem)
                    names=([rule['segment']] if rule['resident_prefix'] else [])+rule['piece_names']
                    sizes={s['name']:s['size'] for s in parse((directory/(p.stem+'.OBJ')).read_bytes()).segments}
                    at=mod['start'];pieces=[]
                    for name in names:
                        end=at+sizes[name]
                        pieces.append({'segment':name,'start':at,'end':end})
                        at=end
                    if at!=mod['end']:raise ValueError(p.stem+': generated extent changed')
                    mod=dict(mod,pieces=pieces)
                source_audit(generated,directory/(p.stem+'.LST'),mod,mod['end']-mod['start'])
            else:
                obj=parse((directory/(p.stem+'.OBJ')).read_bytes())
                if any(s['class_name']=='CODE' for s in obj.segments):
                    raise ValueError('code segment in a data-only source')
    if variant=='proof':
        (directory/'LAYOUT.log').write_text(dos('TASM',['/kh8192','LAYOUT.ASM,LAYOUT.OBJ,LAYOUT.LST'],directory))
        obj=parse((directory/'LAYOUT.OBJ').read_bytes())
        if any(s['size'] for s in obj.segments) or obj.data or obj.fixups or obj.publics:
            raise ValueError('LAYOUT must contain empty segment declarations only')
    shutil.copyfile(ROOT/'src/c/module.c',directory/'MODULE.C')
    (directory/'MODULE.log').write_text(dos('BCC',['-c','-mh','-2','-n.','MODULE.C'],directory))
    command='/m /s '+'+'.join(n+'.OBJ' for n in objects)+',UGH.EXE,UGH.MAP,CH.LIB'
    (directory/'LINK.RSP').write_bytes((command+'\r\n').encode('ascii'))
    log=dos('TLINK',['@LINK.RSP'],directory)
    (directory/'TLINK.log').write_text(log)
    sources.extend(includes)
    sources.append(ROOT/'src/c/module.c')
    sources.extend([ROOT/'tools/fragment.py',ROOT/'metadata/reloc-layout.json'])
    (directory/'build.json').write_text(json.dumps({'variant':variant,'objects':objects,'tlink':command,
        'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()) for p in sources}},indent=2)+'\n')
    return directory/'UGH.EXE'

def build():
    return {variant:build_variant(variant) for variant in ('plain','proof')}

if __name__=='__main__':
    for variant,p in build().items():print(variant+' build:',p,p.stat().st_size,'bytes')
