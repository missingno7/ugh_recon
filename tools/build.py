"""Fresh natural Borland build. No oracle input and no output rewriting."""
import json, shutil
from common import ROOT, BUILD, TOOLS, load_json, sha256
from dos import dos

WORK=BUILD/'link'
OBJECTS=['C0H','LAYOUT','DGDATA','GAME','SOUND','ZERO','MODULE','TIMER',
         'B1A38','B1E1F','B2BC6','B2BF6','B2D9A','B2F9E','B2FB7',
         'B325B','B3260','B3265','B326B','B3274','B3279','B3444',
         'B3629','B3632','B3637','B37A7','B438A','B4E83','B5B63','RESERVE']

def build():
    WORK.mkdir(parents=True,exist_ok=True)
    # Remove only known generated files in the explicitly named build directory.
    for pattern in ('*.OBJ','*.EXE','*.MAP','*.LST','*.log','*.BAK'):
        for p in WORK.glob(pattern):p.unlink()
    for name,entry in load_json('toolchain-lock.json')['libraries'].items():
        data=(TOOLS/entry['path']).read_bytes()
        if sha256(data)!=entry['sha256']:raise ValueError('library hash mismatch: '+name)
        (WORK/name).write_bytes(data)
    from asmverify import validate_map, source_audit
    asm_map=load_json('asm-map.json');validate_map(asm_map)
    mapped={m['name']:m for m in asm_map['modules']}
    sources=list((ROOT/'src/asm').glob('*.ASM'))+list((ROOT/'src/data').glob('*.ASM'))
    if {p.stem for p in sources}!=set(OBJECTS)-{'C0H','MODULE'}:
        raise ValueError('missing or unlisted assembly/data source')
    for folder in ('asm','data'):
        for p in sorted((ROOT/'src'/folder).glob('*.ASM')):
            shutil.copyfile(p,WORK/p.name)
            log=dos('TASM',['/kh8192',f'{p.name},{p.stem}.OBJ,{p.stem}.LST'],WORK)
            (WORK/(p.stem+'.log')).write_text(log)
            if folder=='asm':
                mod=mapped[p.stem]
                source_audit(p,WORK/(p.stem+'.LST'),mod,mod['end']-mod['start'])
            else:
                from omf import parse
                obj=parse((WORK/(p.stem+'.OBJ')).read_bytes())
                if p.stem=='LAYOUT':
                    if any(s['size'] for s in obj.segments) or obj.data or obj.fixups or obj.publics:
                        raise ValueError('LAYOUT must contain empty segment declarations only')
                elif any(s['class_name']=='CODE' for s in obj.segments):
                    raise ValueError('code segment in a data-only source')
    shutil.copyfile(ROOT/'src/c/module.c',WORK/'MODULE.C')
    (WORK/'MODULE.log').write_text(dos('BCC',['-c','-mh','-2','-n.','MODULE.C'],WORK))
    command='/m /s '+'+'.join(n+'.OBJ' for n in OBJECTS)+',UGH.EXE,UGH.MAP,CH.LIB'
    (WORK/'LINK.RSP').write_bytes((command+'\r\n').encode('ascii'))
    log=dos('TLINK',['@LINK.RSP'],WORK)
    (WORK/'TLINK.log').write_text(log)
    sources.append(ROOT/'src/c/module.c')
    (WORK/'build.json').write_text(json.dumps({'objects':OBJECTS,'tlink':command,
        'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()) for p in sources}},indent=2)+'\n')
    return WORK/'UGH.EXE'

if __name__=='__main__':
    p=build();print('natural build:',p, p.stat().st_size,'bytes')
