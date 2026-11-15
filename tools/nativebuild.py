"""Positive-manifest, machine-free production build (and independent audit).

Run tools/build.py once before extracting the data pack. Build-time extraction
reads rebuilt DATA declarations only; the resulting executable opens only its
admitted pack. Objects, preprocessed token/include closure and link map are all
checked even when an unreferenced dependency would disappear at link time.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path
from common import ROOT
from cbuild import GCC
import respack

SDL_ROOT=Path('C:/tools/sdl3-3.4.16-mingw')
SDL=SDL_ROOT/'SDL3-3.4.16/x86_64-w64-mingw32'
OPL=Path('C:/tools/nuked-opl3-765ec962e473')
BANNED=re.compile(r'\b(?:l1_\w*|c_\w*|ugh_\w*|Regs|UghAdapter|dispatch_table|'
    r'lin|rd(?:8|16|32)|wr(?:8|16|32)|(?:add|sub|logic|szp|flag)(?:8|16|32)?|'
    r'set_[abcd][lh]|arg16|UGH_[SO]_\w*|'
    r'\w+_(?:cold_import|require_seal|shared_read|shared_write|serialize|check_serialization)|'
    r'project_timing_observation|(?:pr|sc|api)_\w*|host_digest|host_symbol|'
    r'scenario_fixture|scenario_defaults|\w*projector\w*|\w*serializer\w*|project_\w+|'
    r'pixel_service_continuation|pixel_service_compatibility_write)\b')
FORBIDDEN=('c/','host/','verif/','native/bridge/')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):Path(p).write_text(json.dumps(obj,indent=2)+'\n')
def production_owners(certified=()):
    """Ownership only, not a migration certificate or an earned proof level.

    The closure gate still checks every certified source with its existing
    dependency parser. Only explicitly listed new production composition gets
    this second source owner; it cannot replace a certified file's checker.
    """
    manifest=json.loads((ROOT/'metadata/native-manifest.json').read_text())
    admitted=set(manifest['core'])|set(manifest['headers']);result=set()
    for name in manifest['composition']:
        path=(ROOT/name).resolve()
        if name in certified:raise ValueError('production composition shadows certified source: '+name)
        if name in result or name not in admitted or not name.startswith('native/') or '/bridge/' in name:
            raise ValueError('invalid production composition owner: '+name)
        if not path.is_relative_to(ROOT/'native') or local(path)!=name or not path.is_file() or path.suffix not in ('.c','.h'):
            raise ValueError('invalid production composition path: '+name)
        result.add(name)
    return result
def run(command,out,name):
    # The shared bounded runner assigns every child to a Windows job (8 GiB,
    # 600 seconds). It is build tooling, never a linked game dependency.
    sys.path.insert(0,str(ROOT/'verif'))
    from job_pool import run as bounded
    row=bounded(list(map(str,command)),ROOT,out,name)
    return row['stdout']
def local(path):
    p=Path(path).resolve()
    try:return p.relative_to(ROOT).as_posix()
    except ValueError:return None
def check_text(text,where):
    match=BANNED.search(text)
    if match:raise ValueError(f'banned dependency {match[0]} in {where}')
def check_closure(preprocessed,manifest,out,extra_headers=()):
    headers=set(manifest['headers'])|set(extra_headers)
    generated={str((out/n).resolve()).lower() for n in ['resource_manifest.h','boot_data.h','audio_data.h','demo_data.h','session_data_generated.h']}
    # A prior SDL distribution includes the LGPL relink header beside the
    # executable. -I out can select it on a repeat build; admit only its pinned
    # original content, never arbitrary output-directory headers.
    bundled_opl=out/'opl3.h'
    if bundled_opl.exists():
        if sha(bundled_opl)!=manifest['toolchain']['opl_h']['sha256']:
            raise ValueError('bundled OPL header differs from pinned source')
        generated.add(str(bundled_opl.resolve()).lower())
    paths=[];ours=[];current=None;cache={}
    for line in preprocessed.splitlines():
        marker=re.match(r'#\s+\d+\s+"([^"]+)"',line)
        if marker:
            name=marker[1].replace('\\\\','/');current=None
            if name.startswith('<'):continue
            if name in cache:
                current=cache[name]
                continue
            p=Path(name).resolve();relative=local(p)
            if not p.is_file():cache[name]=None;continue
            if relative is not None:
                if relative.startswith(FORBIDDEN):raise ValueError('banned include/source: '+relative)
                admitted_sources=set(manifest['core'])|{p for group in manifest['backends'].values() for p in group}
                if p.suffix.lower()=='.c' and relative not in admitted_sources:
                    raise ValueError('included source absent from positive manifest: '+relative)
                if p.suffix.lower() in ('.h','.inc') and relative not in headers and str(p).lower() not in generated:
                    raise ValueError('include absent from positive manifest: '+relative)
                current=relative;paths.append(relative)
            cache[name]=current
            continue
        if current is not None:ours.append(line)
    check_text('\n'.join(ours),'preprocessed project tokens')
    return sorted(set(paths))
def audit_symbols(text,where):
    # nm's MinGW import decorations are stripped before checking namespaces.
    words=[]
    for line in text.splitlines():
        parts=line.split()
        if parts:words.append(re.sub(r'^__imp_','',parts[-1]))
    check_text('\n'.join(words),where)
def data_header(manifest,out):
    _,symbols=respack.cgen.read_symbols();rows=manifest['resources']
    # Exact byte extents of constructor fields; names resolve ONLY at build
    # time. Each runtime part is an admitted ID + offset within that object.
    fields=[('RANDOM','GAME:RandomStateStorage',8),('SCORES','DGROUP:HighScoreRows',107),
      ('SEQUENCE','DGROUP:KeyboardSequenceRecords',205),('BASE_PALETTE','GAME:BaseRgbPalette',768),
      ('FADED_PALETTE','GAME:FadedRgbPalette',768),('PLAYERS','DGROUP:PlayerCount',2),
      ('PLAYER_BYTES','DGROUP:PlayerArrayBytes',2),('CONTROL_ONE','DGROUP:PlayerOneControlMode',2),
      ('CONTROL_TWO','DGROUP:PlayerTwoControlMode',2),('DIFFICULTY','DGROUP:SelectedDifficulty',2),
      ('LATEST','GAME:LatestInterruptScanCode',1),('PREVIOUS','DGROUP:PreviousPolledScanCode',1),
      ('SCAN','DGROUP:CurrentKeyboardScanCode',2),('CHANGE','DGROUP:KeyboardScanCodeChangeBits',1),
      ('INDEX','DGROUP:KeyboardSequenceIndex',1),('AXES','DGROUP:JoystickEnabledAxisMask',2),
      ('LIMIT','DGROUP:JoystickSampleLoopLimit',2),('ROW_STRIDE','DGROUP:HighScoreRowStride',1),
      ('FILE_HANDLE','DGROUP:HighScoreFileHandle',2),('OPERATOR_INDEX','SOUND:AdlibOperatorOffsets',9),
      ('SAVED_MODE','DGROUP:SavedBiosVideoMode',1),
      ('NAME','DGROUP:HighScoreNameEntry',13),('PASSWORD','DGROUP:PasswordEditBuffer',21),
      ('LEVEL_CHARS','DGROUP:LevelNumberTensCharacter',2),('DIFFICULTY_TEXT','DGROUP:Text_0AE4',6,41),
      ('PLAYERS_TEXT','DGROUP:Text_0AE4',10,53),('CONTROL_TEXT_ONE','DGROUP:Text_0B64',10,15),('CONTROL_TEXT_TWO','DGROUP:Text_0B64',10,41),
      ('DIGITS','DGROUP:DecimalDigitBuffer',7),('DIVISORS','DGROUP:DecimalTenDivisor',6),
      ('CREDITS','DGROUP:Text_091F',453),('MENU_TEXT','DGROUP:Text_0AE4',128),
      ('SCORE_PROMPT','DGROUP:Text_0C23',74),('SCORE_TITLE','DGROUP:Text_0C7B',11),
      ('LEVEL_TITLE','DGROUP:Text_0BF6',10),('PASSWORD_TITLE','DGROUP:Text_0C00',12),
      ('SOURCE_PALETTE','B2BC6:GameSourcePalette',384)]
    lines=['/* Generated admitted constructor data views; no image coordinates. */',
           'static const size_t game_default_sizes[]={'+','.join(str(field[2]) for field in fields)+'};',
           'static const GameDefaultSpec game_default_specs[]={']
    receipt=[]
    for entry in fields:
        field,symbol,size=entry[:3];delta=entry[3] if len(entry)>3 else 0
        if symbol not in symbols:raise ValueError('constructor symbol missing: '+symbol)
        start=symbols[symbol]['linear']+delta;cursor=start
        while cursor<start+size:
            choices=[r for r in rows if r['image_start']<=cursor<r['image_start']+r['size']]
            if not choices:raise ValueError('constructor field outside admitted data: '+field)
            row=max(choices,key=lambda r:r['image_start']+r['size'])
            count=min(start+size,row['image_start']+row['size'])-cursor
            lines.append('{UINT64_C(%d),%d,%d,%d,GD_%s},'%(row['id'],cursor-row['image_start'],count,cursor-start,field))
            receipt.append(dict(field=field,resource=row['name'],offset=cursor-row['image_start'],size=count,destination=cursor-start))
            cursor+=count
    ids=[]
    for name in ['B2D9A','B2BF6','B2F9E','B2FB7']:
        ids.append(next(r['id'] for r in rows if r['name']=='world.allocation.'+name))
    lines+=['};','static const GSResourceId game_picture_ids[]={'+','.join('UINT64_C(%d)'%n for n in ids)+'};']
    # Build-time pointer evidence becomes data-resource identities and offsets.
    # No historical pointer words survive into the production API.
    import frontend_data,demo_data
    (out/'demo_data.h').write_text('\n'.join(demo_data.generate(rows,symbols))+'\n')
    lines+=frontend_data.generate(rows,symbols)
    (out/'boot_data.h').write_text('\n'.join(lines)+'\n');save(out/'constructors.json',receipt)
    import audio_data
    (out/'audio_data.h').write_text('\n'.join(audio_data.generate(rows,symbols))+'\n')
    import session_data
    (out/'session_data_generated.h').write_text('\n'.join(session_data.generate(rows,symbols))+'\n')
def build(backend='test',out=None,negative_control=False):
    out=Path(out or ROOT/'build/native').resolve();out.mkdir(parents=True,exist_ok=True)
    # Never leave a stale successful executable/receipt after a failed audit.
    exe=out/'ugh-native.exe';exe.unlink(missing_ok=True);(out/'nativebuild.json').unlink(missing_ok=True)
    manifest=json.loads((ROOT/'metadata/native-manifest.json').read_text())
    for name,pin in manifest['toolchain'].items():
        if name!='gcc' and backend!='sdl':continue
        if sha(pin['path'])!=pin['sha256']:raise ValueError('pinned toolchain changed: '+name)
    if backend not in manifest['backends']:raise ValueError('unknown backend')
    sources=manifest['core']+manifest['backends'][backend]
    for relative in sources:
        if relative.startswith(FORBIDDEN) or relative not in manifest['core']+manifest['backends'][backend]:raise ValueError('banned source: '+relative)
        if not (relative.startswith('native/') or relative.startswith('port/')) or not relative.endswith('.c'):raise ValueError('invalid production source: '+relative)
    pack=respack.extract(out/'ugh.res',header_path=out/'resource_manifest.h');data_header(pack,out)
    includes=['-I',ROOT,'-I',ROOT/'native','-I',ROOT/'port','-I',out]
    vendor=[];libs=[]
    if backend=='sdl':
        includes+=['-I',SDL/'include','-I',OPL];vendor=[OPL/'opl3.c'];libs=['-L',SDL/'lib','-lSDL3']
    if list(map(str,vendor))!=[str(Path(p)) for p in manifest['vendor'].get(backend,[])]:raise ValueError('vendor source manifest differs')
    flags=['-O2','-g','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fwrapv','-DUGH_PRODUCTION_MAIN']
    if negative_control:
        (out/'negative_include.h').write_text('#include "c/ugh.h"\n')
        includes+=['-include',out/'negative_include.h']
    objects=[];inputs={};closures={}
    for i,source in enumerate([ROOT/p for p in sources]+vendor):
        label='object-%02d'%i;obj=out/(label+'.o')
        pp=run([GCC,*flags,*includes,'-E',source],out,label+'-preprocess')
        closures[str(source)]=check_closure(pp,manifest,out,
            [local(out/'negative_include.h')] if negative_control else [])
        for relative in closures[str(source)]:inputs[relative]=sha(ROOT/relative)
        run([GCC,*flags,*includes,'-c',source,'-o',obj],out,label+'-compile')
        nm=run([GCC.parent/'nm.exe','-a',obj],out,label+'-symbols');audit_symbols(nm,str(obj))
        objects.append(obj)
    mapfile=out/'ugh-native.map'
    run([GCC,*map(str,objects),*libs,'-Wl,-Map,'+str(mapfile),'-o',exe],out,'link')
    linked=run([GCC.parent/'nm.exe','-a',exe],out,'linked-symbols')
    audit_symbols(linked,'executable')
    check_text(re.sub(r'\S*[/\\]\S*','',mapfile.read_text()),'link map symbols')
    # Map membership is checked independently of token/symbol bans.
    actual={str(p.resolve()).replace('\\','/').lower() for p in objects}
    for m in re.finditer(r'^LOAD (.+)$',mapfile.read_text(),re.M):
        name=m[1].strip();p=Path(name)
        if p.suffix=='.o' and local(p) is not None and str(p.resolve()).replace('\\','/').lower() not in actual:
            raise ValueError('unlisted link object: '+name)
    # Enumerate every linked archive/member, including ordinary CRT imports.
    # Project archives are never implicitly admitted through -L or GCC specs.
    archives=[]
    roots=[GCC.parent.parent.resolve(),(SDL/'lib').resolve()]
    for name,member in re.findall(r'^([^\s]+\.a)\(([^)]+)\)',mapfile.read_text(),re.M):
        path=Path(name).resolve()
        if not any(path.is_relative_to(root) for root in roots):raise ValueError('unlisted archive: '+name)
        audit_symbols(member,'archive member '+name);archives.append(dict(archive=str(path),member=member))
    if backend=='sdl':
        shutil.copyfile(SDL/'bin/SDL3.dll',out/'SDL3.dll')
        shutil.copyfile(OPL/'LICENSE',out/'Nuked-OPL3-LICENSE.txt')
        shutil.copyfile(SDL_ROOT/'SDL3-3.4.16/LICENSE.txt',out/'SDL-LICENSE.txt')
        for name in ['opl3.c','opl3.h']:shutil.copyfile(OPL/name,out/name)
    for dll in ['libwinpthread-1.dll']:
        if (GCC.parent/dll).exists():shutil.copyfile(GCC.parent/dll,out/dll)
    receipt=dict(result='PASS',backend=backend,manifest=sha(ROOT/'metadata/native-manifest.json'),
       compiler=sha(GCC),objects={p.name:sha(p) for p in objects},includes=closures,archive_members=archives,
       inputs=inputs,map_sha256=sha(mapfile),executable_sha256=sha(exe),verification=False)
    save(out/'nativebuild.json',receipt);return exe
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--backend',choices=['test','sdl'],default='test');p.add_argument('--out',type=Path);p.add_argument('--negative-control',action='store_true');a=p.parse_args()
    try:print(build(a.backend,a.out,a.negative_control))
    except (ValueError,RuntimeError) as e:print(str(e),file=sys.stderr);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
