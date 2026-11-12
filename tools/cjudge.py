"""Compile period C with pinned BCC; compare full function extents and resolved OMF fixups.

JUDGE options, DATA frame and BIND symbol frame:offset belong in a source header.
@frame:offset immediately precedes each definition. inventory.json lists ALL debt.
This is bound-object/function proof, not a natural-link or packed-file certificate.
"""
import argparse, json, re, shlex, struct, sys
from pathlib import Path
from types import SimpleNamespace
import omf
from common import ROOT, BUILD, MZ, sha256, load_json
from dos import dos
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

def read_object(data):
    """Adapt the shared reader; reject unhandled records and invalid checksums."""
    p=0
    allowed={0x80,0x88,0x96,0x98,0x9a,0x90,0x8c,0xa0,0x9c,0x8a,0x94}
    while p<len(data):
        if p+3>len(data):raise ValueError('truncated OMF header')
        n=struct.unpack_from('<H',data,p+1)[0];end=p+3+n
        if not n or end>len(data) or sum(data[p:end])&255:raise ValueError('invalid OMF extent/checksum')
        if data[p] not in allowed:raise ValueError(f'unsupported OMF record {data[p]:02X}')
        p=end
    module=omf.parse(data)
    # C++ -P is a profile probe. Names carry no code-byte evidence; reject overload ambiguity.
    def symbol(name):
        match=re.match(r'@([^@]+)\$',name)
        return '_'+match[1] if match else name
    public_names=[symbol(x['name']) for x in module.publics]
    if len(public_names)!=len(set(public_names)):raise ValueError('ambiguous decorated publics')
    segments=[None]+[dict(name=x['name'],class_name=x['class_name'],size=x['size'],
                         data=bytearray(x['size']),written=set()) for x in module.segments]
    for item in module.data:
        dest=segments[item['segment']];at=item['offset'];raw=item['data']
        if at+len(raw)>dest['size']:raise ValueError('LEDATA outside SEGDEF')
        dest['data'][at:at+len(raw)]=raw;dest['written'].update(range(at,at+len(raw)))
    fixups=[SimpleNamespace(seg=f.segment,at=f.offset,kind=f.location,
                            # Shared reader currently names the LOCAT M bit self_relative;
                            # M=1 actually denotes segment-relative, per Intel OMF.
                            relative=not f.self_relative,frame=(f.frame_method,f.frame_datum),
                            target=(f.target_method,f.target_datum),displacement=f.displacement or 0)
            for f in module.fixups]
    return SimpleNamespace(segments=segments,fixups=fixups,
                           publics={symbol(x['name']):(x['segment'],x['offset']) for x in module.publics},
                           externs=['']+[symbol(x['name']) for x in module.externals],module=module)


def word(data,at=0):return struct.unpack_from('<H',data,at)[0]


def address(s):
    a,b=s.split(':'); return int(a,16),int(b,16)


def disasm(data, start):
    c=Cs(CS_ARCH_X86,CS_MODE_16)
    return '\n'.join(f'    {i.address:04X} {i.bytes.hex():24} {i.mnemonic.replace("cwde","cbw").replace("cdq","cwd")} {i.op_str}'
                     for i in c.disasm(bytes(data),start))


def compile_source(path, options=None, dest=None):
    source=path.read_text()
    match=re.search(r'JUDGE:\s*([^\r\n]+)',source)
    if not match: raise ValueError(f'{path}: missing JUDGE header')
    flags=shlex.split(match[1]) if options is None else options
    if any(not x.startswith('-') or x in ('-e','-n','-o') for x in flags):
        raise ValueError('JUDGE only accepts compiler option arguments')
    out=dest or BUILD/'c'/path.stem
    out.mkdir(parents=True,exist_ok=True)
    for p in (*out.glob('UNIT.*'), *out.glob('*.diff.txt')):p.unlink()
    (out/'UNIT.C').write_bytes(source.replace('\r\n','\n').replace('\n','\r\n').encode('ascii'))
    log=dos('BCC',['-c',*flags,'-n.','UNIT.C'],out)
    (out/'compile.txt').write_text(log)
    return read_object((out/'UNIT.OBJ').read_bytes()),source,out


def compare(path, inventory, mz, options=None, dest=None, verbose=True):
    obj,source,out=compile_source(path,options,dest)
    bindings={('_'+name):address(at) for name,at in re.findall(r'BIND:\s*(\w+)\s+([0-9A-Fa-f]+:[0-9A-Fa-f]+)',source)}
    data_match=re.search(r'DATA:\s*([0-9A-Fa-f]+)',source)
    data_frame=int(data_match[1],16) if data_match else None
    if data_frame is not None and sum(s is not None and s['class_name']=='FAR_DATA' for s in obj.segments)!=1:
        raise ValueError('DATA binding requires exactly one FAR_DATA segment')
    markers={}
    for a,b,name in re.findall(r'/\*\s*@([0-9A-Fa-f]+):([0-9A-Fa-f]+)\s*\*/\s*[^;{}]*?\b(\w+)\s*\([^;{}]*\)\s*\{',source):
        markers['_'+name]=(int(a,16),int(b,16))
    bindings.update({name:address(at) for name,at in re.findall(r'OMF:\s*(\S+)\s+([0-9A-Fa-f]+:[0-9A-Fa-f]+)',source)})
    bindings.update(markers)
    results={}
    # Code segments can only have one uniform placement when their public anchors agree.
    segment_bases={}
    for name,(seg,off) in obj.publics.items():
        if name in bindings:
            frame,target=bindings[name]
            segment_bases.setdefault(seg,set()).add((frame,target-off))
    def target(t, displacement=0):
        method,datum=t
        if method==0:
            seg=obj.segments[datum]
            if seg['class_name']=='FAR_DATA' and data_frame is not None:return data_frame,displacement
            # A full TU has one physical placement. Never independently move internal
            # functions/tables to repair code-shape or neighbour-size differences.
            bases=segment_bases.get(datum,set())
            if len(bases)==1:
                frame,offset=next(iter(bases));return frame,offset+displacement
            raise ValueError(f'unbound code target {seg["name"]}+{displacement:04x}')
        if method==2:
            name=obj.externs[datum]
            if name not in bindings:raise ValueError(f'unbound external {name}')
            frame,off=bindings[name];return frame,off+displacement
        raise ValueError(f'unsupported target {t}')
    if not markers:raise ValueError('no function markers')
    for name,(segment,offset) in obj.publics.items():
        if obj.segments[segment]['class_name']=='CODE' and name not in markers:
            raise ValueError(f'code public {name} has no oracle marker')
    if len(set(markers.values()))!=len(markers):raise ValueError('duplicate oracle markers')
    for seg in range(1,len(obj.segments)):
        if obj.segments[seg]['class_name']=='CODE':
            starts=[offset for name,(segment,offset) in obj.publics.items() if segment==seg and name in markers]
            if not starts or min(starts)!=0:raise ValueError('unclassified code prefix/segment')
    for name,where in markers.items():
        key=where[1]; entry=next((f for f in inventory['functions'] if address(f['address'])==where),None)
        if entry is None:raise ValueError(f'{name}: absent from inventory')
        seg,off=obj.publics[name]; s=obj.segments[seg]
        following=[p for g,p in obj.publics.values() if g==seg and p>off]
        end=min(following,default=s['size'])
        if not set(range(off,end))<=s['written']:raise ValueError(f'{name}: unwritten object bytes')
        actual=bytearray(s['data'][off:end]); original=mz.image[where[0]*16+key:where[0]*16+key+entry['length']]
        relocs=[]; issue=None
        try:
            for fx in obj.fixups:
                if fx.seg!=seg or not off<=fx.at<end:continue
                p=fx.at-off
                raw=word(actual,p)
                frame,add=target(fx.target,fx.displacement+(raw if fx.kind in (1,3) else 0))
                if fx.frame!=(5,None):raise ValueError(f'unsupported fixup frame {fx.frame}')
                if fx.relative:raise ValueError('self-relative fixup requires full segment placement')
                if fx.kind==2:
                    struct.pack_into('<H',actual,p,(raw+frame)&65535);relocs.append(p)
                elif fx.kind==1:
                    struct.pack_into('<H',actual,p,add&65535)
                elif fx.kind==3:
                    # TLINK's default same-code-segment far-call relaxation preserves five bytes.
                    # Earlier definitions already use the compiler's four-byte push cs/call near.
                    internal=(fx.target[0]==0 and fx.target[1]==seg) or (frame==where[0] and fx.target[0]==2 and obj.externs[fx.target[1]] in bindings)
                    if internal and p>0 and actual[p-1]==0x9a:
                        actual[p-1:p+4]=bytes([0x90,0x0e,0xe8])+struct.pack('<H',(add-(key+p+4))&65535)
                    else:
                        struct.pack_into('<H',actual,p,add&65535)
                        struct.pack_into('<H',actual,p+2,(word(actual,p+2)+frame)&65535);relocs.append(p+2)
                else:raise ValueError(f'unsupported fixup kind {fx.kind}')
            wanted=[r-(where[0]*16+key) for r in mz.sites if where[0]*16+key<=r<where[0]*16+key+len(original)]
            if sorted(relocs)!=sorted(wanted):issue=f'relocation sites {sorted(relocs)} != {sorted(wanted)}'
        except ValueError as e:issue=str(e)
        mismatch=next((i for i,(a,b) in enumerate(zip(actual,original)) if a!=b),None)
        exact=issue is None and actual==original
        results[key]={'exact':exact,'length':len(actual),'expected':len(original),'issue':issue,'first_difference':mismatch}
        if verbose:
            print(f'{entry["address"]} {name[1:]}: '+('exact' if exact else f'DIFF +{mismatch if mismatch is not None else min(len(actual),len(original)):04X}, lengths {len(actual)}/{len(original)}'+(f'; {issue}' if issue else '')))
            if not exact:
                # Full disassemblies are small enough to preserve in build artifacts; console shows first difference context.
                diag='ORIGINAL\n'+disasm(original,key)+'\nCANDIDATE (resolved)\n'+disasm(actual,key)+'\n'
                (out/f'{name[1:]}.diff.txt').write_text(diag)
                pos=mismatch or 0
                for title,data in [('original',original),('candidate',actual)]:
                    print('  '+title)
                    instructions=list(Cs(CS_ARCH_X86,CS_MODE_16).disasm(bytes(data),key))
                    ix=next((j for j,i in enumerate(instructions) if i.address+i.size>key+pos),len(instructions)-1)
                    for i in instructions[max(0,ix-2):ix+4]:print(f'    {i.address:04X} {i.bytes.hex():24} {i.mnemonic.replace("cwde","cbw").replace("cdq","cwd")} {i.op_str}')
    order_exact=True
    for seg,bases in segment_bases.items():
        if obj.segments[seg]['class_name']!='CODE':continue
        if len(bases)!=1:
            order_exact=False
            continue
        frame,offset=next(iter(bases));origin=frame*16+offset
        sites=[]
        for fx in obj.fixups:
            if fx.seg!=seg:continue
            if fx.kind==2:sites.append(origin+fx.at)
            elif fx.kind==3:
                raw=word(obj.segments[seg]['data'],fx.at)
                tf,_=target(fx.target,fx.displacement+raw)
                internal=(fx.target==(0,seg)) or (tf==frame and fx.target[0]==2)
                is_call=fx.at>0 and obj.segments[seg]['data'][fx.at-1]==0x9a
                if not (internal and is_call):sites.append(origin+fx.at+2)
        wanted=[r for r in mz.sites if origin<=r<origin+obj.segments[seg]['size']]
        order_exact &= sites==wanted
        if verbose:
            print(f'TU placement: {frame:04X}:{offset:04X}; ordered relocations: {len(sites)}/{len(wanted)} '+('exact' if sites==wanted else 'DIFF'))
    for result in results.values():result['ordered_relocations_exact']=order_exact
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('files',nargs='*',type=Path)
    args=p.parse_args(); inventory=json.loads((ROOT/'src/c/inventory.json').read_text())
    oracle=(BUILD/'oracle/UGH_X.EXE').read_bytes()
    if sha256(oracle)!=load_json('oracle.json')['expanded']['file_sha256']:
        sys.exit('oracle hash mismatch; run python tools/oracle.py')
    mz=MZ(oracle)
    files=args.files or sorted((ROOT/'src/c').rglob('*.c')); all_results={}; errors=False
    for path in files:
        try:
            for at,result in compare(path,inventory,mz).items():
                if at in all_results:raise ValueError(f'duplicate function at {at:04X}')
                all_results[at]=result
        except Exception as e:print(f'ERROR {path}: {e}');errors=True
    for f in inventory['functions']:
        if address(f['address'])[1] not in all_results:print(f'{f["address"]} {f["name"]}: UNMATCHED (source not reconstructed)')
    for span in inventory.get('non_functions',[]):
        print(f'{span["class"]} 0878:{span["start"]}..{span["end"]} (exclusive): {span["note"]}')
    exact=[r for r in all_results.values() if r['exact']]
    total=sum(f['length'] for f in inventory['functions'])
    print(f'{len(exact)}/{len(inventory["functions"])} exact C functions, {sum(x["expected"] for x in exact)}/{total} bytes including switch tables; function proof only')
    success=not errors and len(exact)==len(inventory['functions']) and all(r['ordered_relocations_exact'] for r in all_results.values())
    (BUILD/'c/judge.json').write_text(json.dumps({'success':success,'functions':all_results,'exact_functions':len(exact),'exact_bytes':sum(x['expected'] for x in exact),'total_functions':len(inventory['functions']),'total_bytes':total},indent=2))
    return 0 if success else 1

if __name__=='__main__':sys.exit(main())
