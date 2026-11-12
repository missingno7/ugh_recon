"""Fresh TASM/OMF comparison against the independently locked expanded image.

This is an object-contribution certificate, not a natural-link or packed-file proof.
Objects have zero origins; contributions are placed at the observed (nonparagraph)
image starts. All OMF offsets and segment bases are resolved, never masked.
The maintained single-segment sources certify bytes and relocation sites/targets;
relocation stream order is diagnostic here and proved by tools/verify.py.
"""
import argparse, json, re, shutil, struct, sys
from common import ROOT, BUILD, MZ, sha256
from dos import dos
from omf import parse, records

MAP=ROOT/'metadata/asm-map.json'
EXTENTS={'GAME':(0x13b,8,0x529c),'SOUND':(0x664,0xc,0x2143),'TIMER':(0xa32,6,0x341)}

def validate_map(doc):
    if doc['encoding_exceptions']:raise ValueError('this gate accepts no instruction-byte exceptions')
    if len(doc['modules'])!=3 or {m['name'] for m in doc['modules']}!=set(EXTENTS):
        raise ValueError('all three contributions are required')
    for mod in doc['modules']:
        if tuple(mod[k] for k in ('frame','start','end'))!=EXTENTS[mod['name']]:
            raise ValueError('observed contribution extent changed')
        p=mod['start']
        for sp in mod['spans']:
            if sp['start']!=p or sp['end']<=p or sp['kind'] not in ('code','data','padding'):
                raise ValueError(f"{mod['name']}: gap, overlap or UNKNOWN in {sp}")
            p=sp['end']
        if p!=mod['end']:raise ValueError('incomplete classification')
        if mod.get('pieces'):
            p=mod['start']
            for piece in mod['pieces']:
                if piece['start']!=p or piece['end']<=p:raise ValueError('fragment gap/overlap')
                p=piece['end']
            if p!=mod['end']:raise ValueError('fragment extent changed')

def grouped_source_audit(source,listing,mod):
    """Audit generated proof listing offsets against the independent code/data map."""
    pieces={p['segment']:p for p in mod['pieces']};rows={n:[] for n in pieces};current=None
    if any(re.match(r'\s*(incbin|org)\b',s.split(';',1)[0],re.I) for s in source.read_text().splitlines()):
        raise ValueError('forbidden source directive')
    for line in listing.read_text().splitlines():
        # Pinned TASM's source column begins at 37; unindented SEGMENT names
        # would be truncated by the legacy instruction-only column 40.
        statement=line.expandtabs(8)[37:].split(';',1)[0].strip()
        start=re.match(r'(\w+)\s+segment\b',statement,re.I)
        end=re.match(r'(\w+)\s+ends\b',statement,re.I)
        if start:current=start[1].upper();continue
        if end:current=None;continue
        match=re.match(r'\s*(?:1\s+)?(\d+)\s+([0-9A-F]{4})\s',line)
        if current not in pieces or not match:continue
        if statement and not statement.endswith(':') and ' equ ' not in statement.lower():
            rows[current].append((int(match[2],16),int(match[1]),statement))
    data={p for span in mod['spans'] if span['kind']=='data' for p in range(span['start'],span['end'])}
    audited=set()
    for name,items in rows.items():
        piece=pieces[name];size=piece['end']-piece['start']
        for off,num,statement in items:
            if re.search(r'\b(incbin|org)\b',statement,re.I):raise ValueError('forbidden source directive')
            if re.search(r'\b(db|dw|dd|dq|dt)\b',statement,re.I):
                end=next((p for p,_,_ in items if p>off),size)
                if end<=off or not all(piece['start']+p in data for p in range(off,end)):
                    raise ValueError(f'{mod["name"]}: instruction bytes as data in {name} at listing line {num}')
                audited.update(range(piece['start']+off,piece['start']+end))
    if audited!=data:raise ValueError(f'listing data coverage {len(audited)}/{len(data)} differs; missing {sorted(data-audited)[:12]}')

def source_audit(source, listing, mod, size):
    """Reject byte/word directives anywhere outside classified data, using actual LST addresses."""
    if mod.get('pieces'):return grouped_source_audit(source,listing,mod)
    src=source.read_text().splitlines();rows=[]
    if any(re.match(r'\s*(incbin|org)\b',s.split(';',1)[0],re.I) for s in src):
        raise ValueError('forbidden source directive')
    for line in listing.read_text().splitlines():
        match=re.match(r'\s*(?:1\s+)?(\d+)\s+([0-9A-F]{4})\s',line)
        if not match:continue
        num,off=match.groups();num=int(num);off=int(off,16)
        if off>size:continue
        # PROC expansions advance TASM's listing counter; it is not a source line index.
        statement=line.expandtabs(8)[40:].split(';',1)[0].strip()
        if statement and not statement.endswith(':') and ' equ ' not in statement.lower():rows.append((off,num,statement))
    data={p for s in mod['spans'] if s['kind']=='data' for p in range(s['start'],s['end'])}
    for off,num,statement in rows:
        if re.search(r'\b(incbin|org)\b',statement,re.I):raise ValueError(f'forbidden source directive at line {num}')
        if re.search(r'\b(db|dw|dd|dq|dt)\b',statement,re.I):
            end=next((a for a,_,_ in rows if a>off),size)
            if not all(p+mod['start'] in data for p in range(off,end)):
                raise ValueError(f"{mod['name']}: instruction bytes as data at source line {num}")

def grouped_materialize(obj,mod):
    """Resolve ordinary OMF segment/group and relative fixups without masking bytes.

    Piece placement is an independent object certificate. The natural build uses
    LAYOUT.ASM, never this metadata, to obtain the placement from TLINK.
    """
    pieces={p['segment']:p for p in mod['pieces']}
    if {s['name'] for s in obj.segments}!=set(pieces):raise ValueError('unexpected owned fragments')
    if len(obj.groups)!=1 or obj.groups[0]['name']!=mod['group']:raise ValueError('unexpected code group')
    group_names=[obj.segments[i-1]['name'] for kind,i in obj.groups[0]['items'] if kind=='segment']
    # TASM 3.0 writes GRPDEF members in reverse of the source GROUP declaration.
    if group_names!=[p['segment'] for p in reversed(mod['pieces'])]:raise ValueError('code group member order changed')
    starts={};raw=bytearray(mod['end']-mod['start']);covered=bytearray(len(raw))
    for s in obj.segments:
        p=pieces[s['name']];starts[s['index']]=mod['frame']*16+p['start']
        if s['size']!=p['end']-p['start']:raise ValueError('fragment size changed: '+s['name'])
        if s['attr']>>5!={'byte':1,'word':2}[p['alignment']]:raise ValueError('fragment alignment changed')
        if (s['attr']>>2)&7!=2 or s['class_name']!='CODE':raise ValueError('fragment combine/class changed')
    ownbase=mod['frame']*16+mod['start'];groupbase=mod['frame']*16
    for d in obj.data:
        at=starts[d['segment']]-ownbase+d['offset'];end=at+len(d['data'])
        if at<0 or end>len(raw) or any(covered[at:end]):raise ValueError('overlapping/out-of-range object data')
        raw[at:end]=d['data'];covered[at:end]=b'\1'*(end-at)
    if not all(covered):raise ValueError('uninitialized bytes in owned fragments')
    def target(method,datum):
        if method==0:
            base=starts[datum];return base,base//16*16
        if method==1:
            if datum!=1:raise ValueError('unknown target group')
            return groupbase,groupbase
        if method==2:
            name=obj.externals[datum-1]['name']
            match=re.fullmatch('EXT_([0-9A-F]{4})',name)
            function=re.fullmatch('_FN_(?:([0-9A-F]{4})_)?([0-9A-F]{4})',name)
            if match:
                fr=int(match[1],16);off=mod.get('external_starts',{}).get(f'{fr:04X}',0)
            elif function:fr=int(function[1],16) if function[1] else 0x878;off=int(function[2],16)
            else:raise ValueError('unbound external '+name)
            return fr*16+off,fr*16
        raise ValueError('unsupported target method')
    sites=[];details=[]
    for f in obj.fixups:
        address,default_frame=target(f.target_method,f.target_datum)
        if f.frame_method==5:frame=default_frame
        elif f.frame_method==0:frame=starts[f.frame_datum]//16*16
        elif f.frame_method==1:
            if f.frame_datum!=1:raise ValueError('unknown frame group')
            frame=groupbase
        else:raise ValueError('unsupported frame method')
        site=starts[f.segment]+f.offset;at=site-ownbase;disp=f.displacement or 0
        if not f.self_relative:
            if f.location not in (0,1):raise ValueError('unsupported relative fixup')
            width=1 if f.location==0 else 2
            add=int.from_bytes(raw[at:at+width],'little')
            # Pinned TLINK subtracts two for LOC0 as well as LOC1; source cross-
            # segment SHORT references carry +1. groupbranch.py proves this.
            value=(address+disp+add-(site+2))&((1<<(width*8))-1)
            raw[at:at+width]=value.to_bytes(width,'little')
        else:
            def addword(p,value):struct.pack_into('<H',raw,p,(struct.unpack_from('<H',raw,p)[0]+value)&65535)
            if f.location==1:addword(at,address-frame+disp)
            elif f.location==2:addword(at,frame//16+disp);sites.append(site)
            elif f.location==3:
                addword(at,address-frame+disp);addword(at+2,frame//16);sites.append(site+2)
            else:raise ValueError('unsupported segment-relative fixup')
        details.append({'segment':obj.segments[f.segment-1]['name'],'offset':at,'location':f.location,
                        'target_linear':address,'frame_linear':frame,'displacement':disp,
                        'segment_relative':f.self_relative})
    return bytes(raw),sites,details,obj

def materialize(blob, mod):
    # The maintained ASM contribution certificate deliberately remains LEDATA-only.
    # Data-only modules may use LIDATA through the natural linker build.
    if any(t in (0xa2,0xa3) for t,_ in records(blob)):raise ValueError('LIDATA is not certified by this gate; use explicit data initializers')
    obj=parse(blob)
    if mod.get('pieces'):return grouped_materialize(obj,mod)
    if len(obj.segments)!=1:raise ValueError('expected one owned segment')
    alignment={'byte':1,'word':2}[mod.get('alignment','word')]
    if obj.segments[0]['attr']>>5!=alignment:raise ValueError('segment alignment changed')
    n=obj.segments[0]['size'];raw=bytearray(n);covered=bytearray(n)
    for d in obj.data:
        if d['segment']!=1:raise ValueError('unexpected LEDATA segment')
        a=d['offset'];b=a+len(d['data'])
        if b>n or any(covered[a:b]):raise ValueError('overlapping or out-of-range OMF data')
        raw[a:b]=d['data'];covered[a:b]=b'\1'*(b-a)
    if not all(covered):raise ValueError('uninitialized bytes in owned contribution')
    relocs=[];details=[]
    ownbase=mod['frame']*16+mod['start']
    for f in obj.fixups:
        if f.segment!=1 or not f.self_relative:raise ValueError(f'unsupported OMF fixup {f}')
        if f.target_method==0:
            if f.target_datum!=1:raise ValueError(f'unknown segment {f}')
            target_frame,target_offset=mod['frame'],mod['start']
        elif f.target_method==2:
            name=obj.externals[f.target_datum-1]['name']
            match=re.fullmatch('EXT_([0-9A-F]{4})',name)
            function=re.fullmatch('_FN_(?:([0-9A-F]{4})_)?([0-9A-F]{4})',name)
            if match:
                target_frame=int(match[1],16)
                target_offset=mod.get('external_starts',{}).get(f'{target_frame:04X}',0)
            elif function:
                target_frame=int(function[1],16) if function[1] else 0x878
                target_offset=int(function[2],16)
            else:raise ValueError(f'unbound external {name}')
        else:raise ValueError(f'unsupported fixup target {f}')
        target=target_frame*16+target_offset
        if f.frame_method!=5:raise ValueError(f'unsupported fixup frame {f}')
        p=f.offset;disp=f.displacement or 0
        def addword(at,value):
            struct.pack_into('<H',raw,at,(struct.unpack_from('<H',raw,at)[0]+value)&0xffff)
        if f.location==1:addword(p,target_offset+disp)
        elif f.location==2:
            addword(p,target_frame+disp);relocs.append(ownbase+p)
        elif f.location==3:
            addword(p,target_offset+disp);addword(p+2,target_frame);relocs.append(ownbase+p+2)
        else:raise ValueError(f'unsupported fixup location {f}')
        details.append({'offset':p,'location':f.location,'target_linear':target,'displacement':disp})
    return bytes(raw),relocs,details,obj

def compare(mod, oracle, blob, out):
    data,sites,details,obj=materialize(blob,mod)
    a=mod['frame']*16+mod['start'];b=mod['frame']*16+mod['end']
    want=oracle.image[a:b]
    expected_order=[s for s in oracle.sites if a<=s<b]
    expected=sorted(expected_order)
    fixok=sorted(sites)==expected and len(sites)==len(set(sites))
    mismatch=[p for p in range(min(len(want),len(data))) if want[p]!=data[p]]
    count=sum(want[p]==data[p] for p in range(min(len(want),len(data))))
    # Clean sources certify contribution bytes/targets/sites. Order is a diagnostic;
    # only the derived whole-program proof variant promises the original stream.
    okay=len(want)==len(data) and not mismatch and fixok
    result={'module':mod['name'],'start_linear':a,'end_linear':b,'expected_bytes':len(want),
            'object_bytes':len(data),'bytes_equal_at_position':count,'mismatch_count':len(mismatch),
            'relocations_expected':expected,'relocations_emitted':sites,'relocations_equal':fixok,
            'relocation_order_equal':sites==expected_order,
            'omf_fixups':details,'first_mismatches':[{'offset':p+mod['start'],'want':want[p],'got':data[p]} for p in mismatch[:40]],
            'strict_object_contribution_match':okay}
    (out/(mod['name']+'.resolved.bin')).write_bytes(data)
    (out/(mod['name']+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--module',choices=['GAME','SOUND','TIMER']);args=ap.parse_args()
    doc=json.loads(MAP.read_text());oracle=MZ((BUILD/'oracle/UGH_X.EXE').read_bytes())
    lock=json.loads((ROOT/'metadata/oracle.json').read_text())
    if sha256(oracle.data)!=doc['oracle_sha256']:raise ValueError('map oracle binding changed')
    if oracle.identity()!=lock['expanded']:raise ValueError('expanded oracle is not locked')
    validate_map(doc)
    if {p.stem.upper() for p in (ROOT/'src/asm').glob('*.ASM')}!=set(EXTENTS):
        raise ValueError('unmapped or missing assembly source')
    out=BUILD/'asm';out.mkdir(parents=True,exist_ok=True);okay=True
    for mod in doc['modules']:
        if args.module and mod['name']!=args.module:continue
        name=mod['name'];src=ROOT/'src/asm'/(name+'.ASM')
        if any(s['kind']=='UNKNOWN' for s in mod['spans']):raise ValueError(f'{name}: UNKNOWN debt')
        shutil.copyfile(src,out/src.name)
        obj=out/(name+'.OBJ');obj.unlink(missing_ok=True)
        try:log=dos('TASM',['/kh8192',f'{name}.ASM,{name}.OBJ,{name}.LST'],out)
        except RuntimeError as e:
            (out/(name+'.log')).write_text(str(e));print(str(e));okay=False;continue
        (out/(name+'.log')).write_text(log)
        r=compare(mod,oracle,obj.read_bytes(),out)
        source_audit(src,out/(name+'.LST'),mod,r['object_bytes'])
        okay &= r['strict_object_contribution_match']
        exceptions=[x for x in doc['encoding_exceptions'] if x['module']==name]
        databytes=sum(s['end']-s['start'] for s in mod['spans'] if s['kind']=='data')
        print(f"{name}: {r['bytes_equal_at_position']}/{r['expected_bytes']} bytes; "
              f"{len(r['relocations_emitted'])}/{len(r['relocations_expected'])} relocation fixups "
              f"({'equal' if r['relocations_equal'] else 'DIFFER'}, order {'equal' if r['relocation_order_equal'] else 'DIFFER'}); "
              f"{len(r['omf_fixups'])} total OMF fixups resolved; "
              f"{len(exceptions)} encoding exceptions; {databytes} data bytes; "
              f"{'EXACT contribution' if r['strict_object_contribution_match'] else 'FAIL'}")
        if r['object_bytes']!=r['expected_bytes']:print('  object length',r['object_bytes'],'expected',r['expected_bytes'])
        if r['first_mismatches']:print('  first differences',r['first_mismatches'][:4])
    return 0 if okay else 1

if __name__=='__main__':sys.exit(main())
