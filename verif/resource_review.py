"""Provider review: static extents/aliases plus generated-copy actual write census.
No maintained tools or data are modified. Serial600s/8-GiB children.
"""
import argparse,bisect,hashlib,io,json,os,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-stones-24'
REVIEW_REVISION='d980140eed281584326bb97568b2cd37ff8a7e65'
sys.path.insert(0,str(ROOT/'tools'))
import player_composition as player
for module in [player]+player.modules:module.OUT=OUT
bounded=player.bounded;save=player.save;sha=player.sha

def inventory():
 import cgen,dataprobe,difftest
 mz,symbols=cgen.read_symbols();m=difftest.Machine();plan=(ROOT/'docs/standalone-cuts.md').read_text(encoding='utf-8');names=re.findall('`(.*?)`',plan.split('### 5R:')[1].split('**Owner/bindings:**')[0]);assert len(names)==43
 model=json.loads((ROOT/'metadata/program-model.json').read_text());rows=[]
 for name in names:
  candidates=[key for key in symbols if key.endswith(':'+name)];key=next((k for k in candidates if k.startswith(('GAME:','SOUND:','DGROUP:','ZERO:'))),candidates[0])
  segment,offset=m.address(key);size=4 if 'Pointer' in name or name in ['KeyboardHandlerVector'] else 1
  if name in ['PlayerAnimationCycleStarts','PlayerAnimationCycleEnds','PlayerImpactLimits']:size=4 if name!='PlayerImpactLimits' else 6
  if name in ['IceDecodeWorkspace','ext_0A67']:size=65536
  rows.append(dict(name=name,symbol=key,address=segment*16+offset,size=size,model=model['variables'][name],classification='scratch workspace' if name in ['IceDecodeWorkspace','ext_0A67'] else 'mutable/unsettled',reason='No constness inferred from an absent model writer; generic/indirect aliases need review'))
 data=[]
 for a,b,kind,description,confidence,reader in dataprobe.object_table(mz):
  if kind in ['padding','C state']:continue
  data.append(dict(name=kind+': '+description,address=cgen.LOAD*16+a,size=b-a,classification='scratch workspace' if kind=='scratch' else 'mutable/unsettled',reader=reader,reason='Provider retained image region; indirect/generic writes not excluded merely by finite observations'))
 dataprobe.OUT=OUT/'provider-data'
 for item in dataprobe.dgroup(mz).values():
  if item['kind']=='keyboard sequence':continue
  data.append(dict(name=item['kind'],address=m.seg('DGROUP:PlayerCount')*16+item['start'],size=item['end']-item['start'],classification='mutable/unsettled',reader=item['reader'],reason='Decoded exact descriptor/list/animation/script extent. Static generic/foreign aliases not excluded; finite no-write observations do not prove constness.'))
 _,levels=dataprobe.levels(mz)
 for pointer in sorted({r['record'] for r in levels}):data.append(dict(name='original level record '+pointer,address=m.seg('DGROUP:PlayerCount')*16+int(pointer,16),size=26,classification='mutable/unsettled',reason='Distinct from the live record; shipped loader reads it, but a global alias exclusion is not proved here.'))
 seg,off=m.address('GAME:IceDecoderTables')
 codec=[dict(name='IceDecoderTables',address=seg*16+off,size=60,bytes=m.read(seg,off,60).hex(),classification='immutable under accepted codec contract',reason='Explicit60-byte data span in GAME.ASM, ending before FadePaletteIn. Actual native ice.c const arithmetic; accepted ICE admission excludes writes overlapping live code/tables. Registered table stores fail closed.')]
 for n,bias,size in [('IceMatchLengthBitCountsMinusOne',1,5),('IceMatchLengthBiases',1,5),('IceMatchOffsetBitCountsMinusOne',1,3),('IceMatchOffsetBiases',2,6)]:
  seg,anchor=m.address('GAME:'+n);off=anchor-bias;codec.append(dict(name=n,address=seg*16+off,size=size,anchor_bias=bias,bytes=m.read(seg,off,size).hex(),classification='immutable under accepted codec contract',reason='Biased view inside IceDecoderTables; includes negative unary-class indices. Not an independent allocation.'))
 for r in rows:
  match=next((c for c in codec if c['name']==r['name']),None)
  if match:r.update({k:v for k,v in match.items() if k not in ['name','bytes']})
 # All encoded directory fields remain mutable: even offsets may be affected by
 # admitted generic data-window aliases, despite only width214 having a normal writer.
 seg=m.rw('GAME:SpriteDirectoryPointer',2);off=m.rw('GAME:SpriteDirectoryPointer');reveal=m.rw('GAME:DemoRevealWidthPointer')
 directory=dict(name='Sprite directory',address=seg*16+off,size=662*4,classification='mutable with known and generic writers',reason='SetDemoRevealSpriteWidth writes the low dimension byte; full RAM copy/decimal/codec views can address other fields. Entire records retained, not only one observed byte.',reveal_ordinal=(reveal-off)//4,reveal_lane=(reveal-off)%4)
 assert directory['reveal_ordinal']==214 and directory['reveal_lane']==2
 static=[]
 pattern=re.compile(r'\b(?:wr8|wr16|wr32|player_write8|player_write16|player_write32|run_write8|run_write16|rng_write8|rng_write16|audio_workspace_publish|memcpy|memmove|memset)\s*\(|\bugh_mem\s*\[')
 raw=subprocess.check_output(['git','archive','--format=tar',REVIEW_REVISION],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
  for item in archive.getmembers():
   if not item.isfile() or item.name.split('/')[0] not in ['c','native'] or Path(item.name).suffix not in ['.c','.h']:continue
   text=archive.extractfile(item).read().decode('utf-8');lines=[dict(line=i+1,text=line.strip()) for i,line in enumerate(text.splitlines()) if pattern.search(line)]
   if lines:static.append(dict(file=item.name,writes=lines))
 save(OUT/'provider-inventory.json',dict(result='PASS',revision=REVIEW_REVISION,named=rows,regions=data,codec_tables=codec,directory=directory,static_writes=static,source_inputs={f:sha(ROOT/f) for f in ['docs/standalone-cuts.md','docs/standalone-ledger.md','metadata/program-model.json','tools/dataprobe.py','native/ice.c','native/bridge/ice_bridge.c','native/bridge/ice_scratch_bridge.c']}))
 return rows+data+codec+[directory]

CENSUS=r'''#include "platform.h"
#include "host.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned count[UGH_MEM_SIZE],actual[UGH_MEM_SIZE],first[UGH_MEM_SIZE],last[UGH_MEM_SIZE];
static unsigned char watched[UGH_MEM_SIZE],last_value[UGH_MEM_SIZE];static int started;
static void dump(void){const char*p=getenv("RESOURCE_REVIEW_OUTPUT");if(!p)return;FILE*f=fopen(p,"w");if(!f)exit(91);fputs("[",f);unsigned emitted=0;
 for(unsigned i=0;i<UGH_MEM_SIZE;i++){if(count[i])fprintf(f,"%s[%u,%u,%u,%u,%u,%u]",emitted++?",":"",i,count[i],actual[i],first[i],last[i],last_value[i]);}fputs("]",f);fclose(f);}
void resource_review_write(uint32_t a,uint8_t v,int is_actual){
 if(!started){started=1;FILE*f=fopen("watch.bin","rb");if(!f || fread(watched,1,sizeof watched,f)!=sizeof watched)exit(91);fclose(f);atexit(dump);}
 if(a>=UGH_MEM_SIZE || !watched[a])return;
 if(!count[a]){first[a]=host_frame;}count[a]++;actual[a]+=(unsigned)!!is_actual;last[a]=host_frame;last_value[a]=v;
}
'''

def observe():
 import wholegame,cgen
 regions=inventory();folder=OUT/'review-baseline';revision=REVIEW_REVISION;raw=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
  for member in archive.getmembers():
   if member.isfile():p=folder/member.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.extractfile(member).read())
 shutil.copytree(ROOT/'build/link',folder/'build/link',dirs_exist_ok=True)
 # Watch all ordinary RAM, not just named starts: biased anchors and unnamed
 # tables/padding must not disappear from the write evidence. VGA is a service.
 mask=bytearray(b'\x01'*0x110000);mask[0xa0000:0xb0000]=b'\x00'*0x10000
 (folder/'watch.bin').write_bytes(mask);(folder/'host/resource_review.c').write_text(CENSUS)
 p=folder/'c/memory.c';s=p.read_text();needle='void ugh_write(uint32_t a, uint8_t v) {';assert s.count(needle)==1;s='extern void resource_review_write(uint32_t,unsigned char,int);\n'+s.replace(needle,needle+'resource_review_write(a,v,1);',1);p.write_text(s)
 p=folder/'native/bridge/audio_world_bridge.c';s=p.read_text();s='extern void resource_review_write(uint32_t,unsigned char,int);\n'+s;s=s.replace('uint32_t address=base+i;','uint32_t address=base+i;resource_review_write(address,source[i],written>((extent-1u-i)&65535u));',1);s=s.replace('window[index]=value;','window[index]=value;\n if((size_t)window>=(size_t)ugh_mem && (size_t)window-(size_t)ugh_mem+index<UGH_MEM_SIZE)resource_review_write((uint32_t)((size_t)window-(size_t)ugh_mem+index),value,1);');p.write_text(s)
 bounded([sys.executable,'tools/build.py'],'review-asm-build',folder)
 bounded([sys.executable,'tools/hostbuild.py'],'review-build',folder)
 capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True);print(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
 paths=[('whole',p) for p in sorted((ROOT/'tests/scenarios').glob('*.txt'))]
 for group in ['levels','levels-audio','levels-deep']:paths += [(group,p) for p in sorted((ROOT/'tests'/group).glob('*.txt'))]
 rows=[]
 for group,script in paths:
  spec=wholegame.scenario(script);ref=json.loads((ROOT/'build'/group/(script.stem+'.ref.json')).read_text());output=OUT/'resource-writes'/(group+'-'+script.stem+'.json');output.parent.mkdir(exist_ok=True);os.environ['RESOURCE_REVIEW_OUTPUT']=str(output)
  try:r=bounded([sys.executable,capture,folder/'build/host/ugh.exe','--headless',str(spec['frames']),'--script',script,'--timeout','590'],'review-'+group+'-'+script.stem,folder)
  finally:os.environ.pop('RESOURCE_REVIEW_OUTPUT',None)
  result=json.loads(r['stdout']);assert result['returncode']==0,result['stderr'];records=[json.loads(line) for line in result['stdout'].splitlines()];assert records==ref['frames'],(group,script.stem,'independent ASM frame mismatch')
  events=json.loads(output.read_text());rows.append(dict(group=group,scenario=script.stem,frames=len(records),write_addresses=len(events),receipt=output.relative_to(OUT).as_posix(),reference_key=ref['key']))
 save(OUT/'provider-writes.json',dict(result='PASS',revision=revision,runs=rows,scope='20 maintained scenarios and81+7+8 level groups; exact reference frames. Every unmoved physical byte store and completed codec-window publication instrumented; actual decoder-written bytes distinguished from unchanged seeded-tail republication. Already-native owners are documented by their source writers, not inferred immutable from zero physical-RAM writes.'))
 classify()

def classify():
 inv=json.loads((OUT/'provider-inventory.json').read_text());runs=json.loads((OUT/'provider-writes.json').read_text());regions=inv['named']+inv['regions']+inv['codec_tables']+[inv['directory']]
 for region in regions:region['observed_writes']=[]
 for run in runs['runs']:
  events=json.loads((OUT/run['receipt']).read_text());addresses=[e[0] for e in events]
  for region in regions:
   a=region['address'];b=a+region['size'];lo=bisect.bisect_left(addresses,a);hi=bisect.bisect_left(addresses,b);hits=events[lo:hi]
   if hits:region['observed_writes'].append(dict(scenario=run['group']+'/'+run['scenario'],addresses=len(hits),publications=sum(h[1] for h in hits),actual=sum(h[2] for h in hits),first_frame=min(h[3] for h in hits)))
 for region in inv['codec_tables']:assert not region['observed_writes'],region
 save(OUT/'provider-review.json',dict(result='PASS',named=inv['named'],regions=inv['regions'],codec_tables=inv['codec_tables'],directory=inv['directory'],scope='Conservative provider classification. Only the accepted immutable-codec-table contract supports immutable registration in this landing; unresolved generic/foreign aliases keep every deferred candidate mutable. Read-only returned views alone are not evidence of global constness.',proposed_cut='Resource catalog:662 live mutable directory records,60 immutable codec-table bytes with biased subviews, stable sprite-record/codec-table/demo-effect tokens. Codec workspace and other identities remain separate continuations, with full-window ICE behavior untouched.'))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--observe',action='store_true');p.add_argument('--classify',action='store_true');p.add_argument('--inventory',action='store_true');p.add_argument('--internal',action='store_true');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if a.inventory:inventory()
 if a.observe:
  if a.internal:observe()
  else:bounded([sys.executable,__file__,'--observe','--internal'],'provider-review-child')
 if a.classify:classify()
