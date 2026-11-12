"""Fresh TASM/OMF comparison against the independently locked expanded image.

This is an object-contribution certificate, not a natural-link or packed-file proof.
Objects have zero origins; contributions are placed at the observed (nonparagraph)
image starts. All OMF offsets and segment bases are resolved, never masked.
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

def source_audit(source, listing, mod, size):
    """Reject byte/word directives anywhere outside classified data, using actual LST addresses."""
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

def materialize(blob, mod):
    # No current source needs LIDATA. Avoid silently relying on the shared reader's
    # unverified nested/repeated-data path (see docs/asm.md).
    if any(t in (0xa2,0xa3) for t,_ in records(blob)):raise ValueError('LIDATA is not certified by this gate; use explicit data initializers')
    obj=parse(blob)
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
            target=ownbase
        elif f.target_method==2:
            name=obj.externals[f.target_datum-1]['name']
            match=re.fullmatch('EXT_([0-9A-F]{4})',name)
            if not match:raise ValueError(f'unbound external {name}')
            fr=int(match[1],16)
            target=fr*16+mod.get('external_starts',{}).get(f'{fr:04X}',0)
        else:raise ValueError(f'unsupported fixup target {f}')
        if f.frame_method!=5:raise ValueError(f'unsupported fixup frame {f}')
        p=f.offset;disp=f.displacement or 0
        def addword(at,value):
            struct.pack_into('<H',raw,at,(struct.unpack_from('<H',raw,at)[0]+value)&0xffff)
        if f.location==1:addword(p,(target&15)+disp)
        elif f.location==2:
            addword(p,(target>>4)+disp);relocs.append(ownbase+p)
        elif f.location==3:
            addword(p,(target&15)+disp);addword(p+2,target>>4);relocs.append(ownbase+p+2)
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
              f"({'equal' if r['relocations_equal'] else 'DIFFER'}); "
              f"{len(r['omf_fixups'])} total OMF fixups resolved; "
              f"{len(exceptions)} encoding exceptions; {databytes} data bytes; "
              f"{'EXACT contribution' if r['strict_object_contribution_match'] else 'FAIL'}")
        if r['object_bytes']!=r['expected_bytes']:print('  object length',r['object_bytes'],'expected',r['expected_bytes'])
        if r['first_mismatches']:print('  first differences',r['first_mismatches'][:4])
    return 0 if okay else 1

if __name__=='__main__':sys.exit(main())
