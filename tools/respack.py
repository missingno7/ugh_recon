"""D3 build-time data extractor. Never reads assets or loads an executable at runtime.

Curated data-layout objects and explicit assembly data declarations are the only
byte sources. Original coordinates exist only in the build manifest, not the pack.
All unclassified data remains opaque_mutable; zero workspace is a reservation.
"""
import argparse,hashlib,json,re,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import cgen
MAGIC=b'UGHRES1\0';VERSION=1;HEADER=128;ENTRY=64
CLASSES={'immutable':1,'mutable':2,'opaque_mutable':3,'scratch':4}
def digest(data):return hashlib.sha256(data).digest()
def resource_id(family,index):return (family<<32)|index
def named_id(name):return resource_id(4,zlib.crc32(name.encode('utf-8')))
def classification_policy():
    cert=json.loads((ROOT/'metadata/closure/resource_catalog.json').read_text())
    if cert['component']!='resource_catalog' or cert['memory']['new_mutable']!=2648 or cert['memory']['new_provider_readonly']!=60:
        raise ValueError('resource_catalog classification changed; provider review required')
    vocabulary=re.sub(r'\s+','',(ROOT/'native/resource_catalog.h').read_text())
    if 'RESOURCE_SPRITE_RECORD=1,RESOURCE_CODEC_TABLE,RESOURCE_DEMO_EFFECT' not in vocabulary or 'RESOURCE_SPRITE_RECORDS=662,RESOURCE_CODEC_BYTES=60' not in vocabulary:
        raise ValueError('resource_catalog token vocabulary changed; schema review required')
    # Dependent relocks are concurrent work. They do not alter data classification.
    return dict(component=cert['component'],mutable=2648,readonly=60,assumptions=cert['assumptions'],retained=cert['retained'])

def inventory(image,symbols):
    layout=json.loads((ROOT/'metadata/data-layout.json').read_text())
    model=json.loads((ROOT/'metadata/program-model.json').read_text())
    rows=[];excluded=[];seen={}
    codec=symbols['GAME:IceDecoderTables']['linear']
    data_frames={int(r['frame'],16) for r in json.loads((ROOT/'metadata/regions.json').read_text())['regions'] if r['class']=='DATA'}
    def add(name,start,end,classification='opaque_mutable',identity=None,basis='unsettled provider constness'):
        if not 0<=start<=end<=len(image):raise ValueError('data span outside rebuilt image: '+name)
        identity=named_id(name) if identity is None else identity
        if identity in seen:raise ValueError('resource ID collision: '+name+' / '+seen[identity])
        seen[identity]=name
        rows.append(dict(id=identity,name=name,image_start=start,size=end-start,classification=classification,basis=basis))
    for module in layout['modules']:
        if module['frame'] not in data_frames:raise ValueError('data-layout module outside curated DATA frames')
        if module['name']=='ZERO':
            a=module['frame']*16+module['start'];b=module['frame']*16+module['end']
            if any(image[a:b]):raise ValueError('nonzero workspace reservation requires provider review')
            excluded.append(dict(name='workspace reservation',image_start=a,size=b-a,reason='scratch, not resource payload; full-window aliases remain step7 work'))
            continue
        labels={}
        for label in module['labels']:
            if not label['name'].startswith('ext_'):labels.setdefault(label['offset'],label['name'])
        cursor=module['start']
        for ordinal,obj in enumerate(module['objects']):
            if obj['start']!=cursor or obj['end']<=cursor:raise ValueError('data-layout partition is not exact')
            cursor=obj['end'];a=module['frame']*16+obj['start'];b=module['frame']*16+obj['end']
            name='data.'+module['name']+'.'+labels.get(obj['start'],'object_'+str(ordinal))
            classification='mutable' if module['name']=='B5B63' and obj['end']<=662*4 else 'opaque_mutable'
            add(name,a,b,classification,basis='resource_catalog whole directory records mutable' if classification=='mutable' else 'curated data object; no global constness inferred')
        if cursor!=module['end']:raise ValueError('data-layout trailing gap')
    group=next(m for m in layout['modules'] if m['name']=='DGDATA');base=group['frame']*16
    excluded.extend([dict(name='runtime startup data',image_start=base,size=group['start'],reason='library state/alignment, not game resource'),
        dict(name='runtime library initialization',image_start=base+group['end'],size=len(image)-base-group['end'],reason='library runtime/init table, not game resource')])
    # Separately classified C startup flags and paragraph padding are data too.
    add('data.CDATA.initial_flags',0x1a370,0x1a374,'mutable',basis='known native audio initial flags; initialization template only')
    add('data.CDATA.padding',0x1a374,0x1a380)
    # Inline tables/state in assembly-origin modules: declarations only, never
    # instruction ranges. Missing coordinates fail extraction rather than guess.
    for module in ['GAME','SOUND','TIMER']:
        cursor=None;label='';block=0;parts=[]
        for line in (ROOT/('src/asm/'+module+'.ASM')).read_text().splitlines():
            m=re.match(r'^(\w+):',line)
            if m:label=m[1];cursor=symbols.get(module+':'+label,{}).get('offset');block=0
            data=re.match(r'^\s*(?:\w+\s+)?(db|dw|dd)\s+(.+)',line,re.I)
            mark=re.search(r'; data ([0-9A-F]+)\.\.([0-9A-F]+)',line)
            if mark:
                if not data:raise ValueError('data annotation on an instruction')
                a,b=map(lambda x:int(x,16),mark.groups());cursor=b
            elif data:
                if cursor is None or data[1].lower()!='dw' or ',' in data[2]:raise ValueError('unlocated declaration: '+line)
                a,b=cursor,cursor+2;cursor=b
            else:
                if re.search(r'; @[0-9A-F]+',line):cursor=None
                continue
            base=cgen.FRAMES[module]*16
            # Join only consecutive declarations with the same registered anchor.
            if parts and parts[-1][0]==label and parts[-1][2]==base+a:parts[-1][2]=base+b
            else:parts.append([label,base+a,base+b])
        used={}
        for label,a,b in parts:
            n=used.get(label,0);used[label]=n+1
            name='inline.'+module+'.'+label+('.part'+str(n) if n else '')
            classification='immutable' if a==codec and b-a==60 else 'opaque_mutable'
            add(name,a,b,classification,basis='resource_catalog explicit60-byte codec block' if classification=='immutable' else 'explicit data declaration; mutable/unsettled')
    # IDs use the exact catalog kind/index namespaces; views share payload bytes.
    for i in range(662):add('catalog.sprite.'+str(i),0x5b630+i*4,0x5b634+i*4,'mutable',resource_id(1,i),'resource_catalog sprite record token')
    for i,(offset,size) in enumerate(zip([0,40,45,50,54],[60,5,5,3,6])):
        add('catalog.codec.'+str(i),codec+offset,codec+offset+size,'immutable',resource_id(2,i),'resource_catalog biased table view; first logical index -1 for subviews')
    for i in range(3):add('catalog.demo_effect.'+str(i),0,0,'immutable',resource_id(3,i),'semantic token; no executable or data payload')
    # The may-model names data references, but does not give sound allocation
    # bounds for every variable. Register model aliases only with an existing
    # exact declared-object start; never guess a scalar/array extent from uses.
    roots=list(rows);bindings=[]
    for name,variable in sorted(model['variables'].items()):
        addresses={value['linear'] for key,value in symbols.items() if key.split(':',1)[1]==name}
        candidates=[r for r in roots if r['size'] and r['image_start'] in addresses and not r['name'].startswith('catalog.')]
        starts={r['image_start'] for r in candidates}
        if len(starts)==1:
            base=max(candidates,key=lambda r:r['size'])
            add('model.'+name,base['image_start'],base['image_start']+base['size'],base['classification'],basis='model data reference; exact declared-object view '+base['name'])
            bindings.append(dict(name=name,resource='model.'+name,declared_view=base['name'],readers=variable['readers'],writers=variable['writers']))
        else:bindings.append(dict(name=name,resource=None,reason='no unique exact declared data-object start; no extent guessed. Base data is retained; scratch/runtime exclusions are explicit. Biased anchors are not allocations'))
    rows.sort(key=lambda row:row['id'])
    instruction_starts=set()
    for module in ['GAME','SOUND','TIMER']:
        for value in re.findall(r'; @([0-9A-F]{4})\b',(ROOT/('src/asm/'+module+'.ASM')).read_text()):instruction_starts.add(cgen.FRAMES[module]*16+int(value,16))
    for row in rows:
        if any(row['image_start']<=pc<row['image_start']+row['size'] for pc in instruction_starts):raise ValueError('instruction starts inside data selection: '+row['name'])
    # An immutable alias must never be reachable through a mutable resource view.
    for a in rows:
        if a['classification']!='immutable' or not a['size']:continue
        for b in rows:
            if b['classification']!='immutable' and max(a['image_start'],b['image_start'])<min(a['image_start']+a['size'],b['image_start']+b['size']):
                raise ValueError('immutable/mutable alias requires review: '+a['name']+' / '+b['name'])
    return rows,excluded,model,bindings

def extract(output,manifest_path=None,header_path=None):
    mz,symbols=cgen.read_symbols()
    if (ROOT/'build/link/plain/UGH.EXE').resolve()!=cgen.PLAIN.joinpath('UGH.EXE').resolve():raise ValueError('plain provider drift')
    rows,excluded,model,bindings=inventory(mz.image,symbols)
    spans=[]
    for row in sorted(rows,key=lambda r:r['image_start']):
        a,b=row['image_start'],row['image_start']+row['size']
        if a==b:continue
        if spans and a<=spans[-1][1]:spans[-1][1]=max(spans[-1][1],b)
        else:spans.append([a,b])
    payload=bytearray();mapping=[]
    for a,b in spans:mapping.append((a,b,len(payload)));payload+=mz.image[a:b]
    toc=bytearray()
    for row in rows:
        a,n=row['image_start'],row['size'];offset=0 if not n else next(p+a-lo for lo,hi,p in mapping if lo<=a and a+n<=hi)
        sha=digest(mz.image[a:a+n]);row.update(payload_offset=offset,sha256=sha.hex())
        toc+=struct.pack('<QIIQQ32s',row['id'],CLASSES[row['classification']],0,offset,n,sha)
    length=HEADER+len(toc)+len(payload)
    head=struct.pack('<8sIIIIQQQ32s32s16s',MAGIC,VERSION,ENTRY,len(rows),0,HEADER,HEADER+len(toc),length,digest(toc),digest(payload),bytes(16))
    assert len(head)==HEADER
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(head+toc+payload)
    manifest=dict(schema=1,format='UGHRES1',source='rebuilt plain load-image data declarations only',image_sha256=hashlib.sha256(mz.image).hexdigest(),pack_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),resources=rows,model_bindings=bindings,excluded=excluded,payload_bytes=len(payload),code_bytes=0,runtime_image=False,
        classification='resource_catalog: whole sprite records mutable, explicit codec block immutable; other spans opaque_mutable, including initializer templates',
        classification_policy=classification_policy(),model_inputs=model['inputs'],inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'metadata/data-layout.json',ROOT/'metadata/program-model.json',ROOT/'metadata/regions.json',ROOT/'native/resource_catalog.h',*[ROOT/('src/asm/'+m+'.ASM') for m in ['GAME','SOUND','TIMER']]]})
    target=Path(manifest_path) if manifest_path else output.with_suffix('.manifest.json');target.write_text(json.dumps(manifest,indent=2)+'\n')
    if header_path:
        text='/* Build-time admission manifest. No image coordinates. */\n#include "resources.h"\n'
        names=set()
        for r in rows:
            name='GS_RESOURCE_ID_'+re.sub('[^A-Za-z0-9_]','_',r['name']).upper()
            if name in names:raise ValueError('resource macro collision: '+name)
            names.add(name);text+='#define '+name+' UINT64_C('+str(r['id'])+')\n'
        text+='static const GSRequiredResource port_required_resources[]={\n'
        for r in rows:text+='{UINT64_C('+str(r['id'])+'),'+str(CLASSES[r['classification']])+','+str(r['size'])+','+str(r['payload_offset'])+',{'+','.join('0x'+r['sha256'][i:i+2] for i in range(0,64,2))+'}},\n'
        text+='};\n#define PORT_REQUIRED_COUNT (sizeof port_required_resources/sizeof *port_required_resources)\n';Path(header_path).write_text(text)
    verify(output,target)
    return manifest

def verify(path,manifest_path):
    data=Path(path).read_bytes();manifest=json.loads(Path(manifest_path).read_text());mz,_=cgen.read_symbols()
    if manifest['classification_policy']!=classification_policy():raise ValueError('stale resource classification policy')
    for name,expected in manifest['inputs'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:raise ValueError('stale extraction input: '+name)
    if len(data)<HEADER:raise ValueError('short header')
    magic,version,width,count,reserved,tstart,pstart,total,thash,phash,pad=struct.unpack_from('<8sIIIIQQQ32s32s16s',data)
    if (magic,version,width,reserved,tstart,total,pad)!=(MAGIC,1,64,0,128,len(data),bytes(16)) or pstart!=128+64*count:raise ValueError('invalid pack header')
    if digest(data[tstart:pstart])!=thash or digest(data[pstart:])!=phash:raise ValueError('pack hash mismatch')
    if hashlib.sha256(data).hexdigest()!=manifest['pack_sha256'] or len(data)-pstart!=manifest['payload_bytes']:raise ValueError('canonical pack differs from manifest')
    if count!=len(manifest['resources']):raise ValueError('required ID count mismatch')
    for i,r in enumerate(manifest['resources']):
        identity,kind,flags,offset,size,sha=struct.unpack_from('<QIIQQ32s',data,tstart+i*64)
        if (identity,kind,flags,offset,size)!=(r['id'],CLASSES[r['classification']],0,r['payload_offset'],r['size']):raise ValueError('ID/class/size/alias mismatch')
        actual=data[pstart+offset:pstart+offset+size]
        if len(actual)!=size or digest(actual)!=sha or sha.hex()!=r['sha256']:raise ValueError('resource hash mismatch')
        expected=mz.image[r['image_start']:r['image_start']+size]
        if actual!=expected:raise ValueError('resource roundtrip differs: '+r['name'])
    return dict(result='PASS',resources=count,compared_bytes=sum(r['size'] for r in manifest['resources']),payload_bytes=len(data)-pstart)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/port/ugh.res');p.add_argument('--manifest',type=Path);p.add_argument('--header',type=Path);p.add_argument('--verify',action='store_true');a=p.parse_args()
    if a.verify:result=verify(a.output,a.manifest or a.output.with_suffix('.manifest.json'))
    else:
        m=extract(a.output,a.manifest,a.header);result=dict(result='PASS',resources=len(m['resources']),payload_bytes=m['payload_bytes'],pack_sha256=m['pack_sha256'])
    print(json.dumps(result))
if __name__=='__main__':main()
