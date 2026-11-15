"""Compiled identity/graph properties, independent of game callback execution.

The plain image supplies expected transport words and live scalar operands.
The generated graph is checked against that input, never used as its oracle.
All child commands use the world gate's bounded process runner.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(root, out, bounded, save):
    root, out = Path(root), Path(out) / 'object-identities'
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(root / 'tools'))
    from cbuild import GCC
    import cgen
    bounded([sys.executable, root / 'tools/object_identities.py', '--check'], 'identity-generation')
    mz, _ = cgen.read_symbols()
    manifest = json.loads((root / 'metadata/object-identities.json').read_text())
    world = json.loads((root / 'metadata/resource-world.json').read_text())
    fixture = out / 'resources.bin'
    fixture.write_bytes(b''.join(mz.image[r['image_start']:r['image_start']+r['size']] for r in world['regions']))
    resources = []
    for row in manifest['resources']:
        for position in row['positions']:
            resources.append(' {'+row['kind']+',{'+str(row['view'])+'},'+str(position)+','+str(row['word']+position)+'},')
    callbacks = []
    for row in manifest['callbacks']:
        callbacks.append(' {OBJECT_LEGACY_'+row['family'].upper()+','+str(row['word'])+','+str(row['role'])+'},')
    expected = ['static const ExpectedResource expected_resources[]={', *resources, '};',
                'static const ExpectedCallback expected_callbacks[]={', *callbacks, '};',
                'static const uint16_t expected_links[]={',
                ','.join(str(row['word']) for row in manifest['links']), '};']
    source = out / 'properties.c'
    source.write_text('''#include "object_identities_bridge.h"
#include "resource_world_bridge.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* A negative control must exit deterministically, without the Windows CRT
 * assertion dialog waiting for interactive input. */
#undef assert
#define assert(condition) do { if(!(condition)){fprintf(stderr,"Assertion failed at line %u\\n",(unsigned)__LINE__);exit(3);} } while(0)
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
typedef struct ExpectedResource {ObjectResourceKind kind;ResourceWorldToken view;uint16_t position,word;} ExpectedResource;
typedef struct ExpectedCallback {ObjectLegacyCallbackFamily family;uint16_t word,role;} ExpectedCallback;
''' + '\n'.join(expected) + r'''
static unsigned callback_role(ObjectCallbackIdentity value){
 if(value.kind==OBJECT_CALLBACK_ACTOR)return value.actor;
 if(value.kind==OBJECT_CALLBACK_ENEMY)return value.enemy;
 if(value.kind==OBJECT_CALLBACK_ITEM)return value.item;
 assert(value.kind==OBJECT_CALLBACK_DEMO_EFFECT);return value.effect.index;
}
int main(int argc,char **argv){
 assert(argc==2);FILE *input=fopen(argv[1],"rb");assert(input);
 for(unsigned i=0;i<RESOURCE_WORLD_REGIONS;i++){
  const ResourceAllocation *allocation=resource_world_allocation(i);
  assert(fread(resource_world_bootstrap(i),1,allocation->size,input)==allocation->size);
 }
 assert(fgetc(input)==EOF);fclose(input);
 unsigned resource_count=sizeof expected_resources/sizeof *expected_resources;
 for(unsigned i=0;i<resource_count;i++){
  const ExpectedResource *expected=expected_resources+i;ObjectResourceIdentity got,back;uint16_t word;
  assert(object_resource_identity(expected->kind,expected->view,expected->position,&got)==OBJECT_IDENTITY_OK);
  assert(object_resource_from_legacy(expected->kind,expected->word,&back)==OBJECT_IDENTITY_OK);
  assert(got.kind==back.kind && got.view.index==back.view.index && got.position==back.position);
  assert(object_resource_to_legacy(got,&word)==OBJECT_IDENTITY_OK && word==expected->word);
  assert(object_resource_identity(OBJECT_RESOURCE_UNSUPPORTED,expected->view,expected->position,&back)==OBJECT_IDENTITY_UNSUPPORTED);
  ResourceWorldView view;assert(resource_world_view(expected->view,&view));
  if((unsigned)expected->position+1<view.size){
   uint8_t low,high;uint16_t live;
   resource_world_read(RESOURCE_BORROW_ACTORS,expected->view,expected->position,&low);
   resource_world_read(RESOURCE_BORROW_ACTORS,expected->view,expected->position+1,&high);
   assert(object_resource_read(got,0,&live)==OBJECT_IDENTITY_OK && live==(uint16_t)(low+256u*high));
   resource_world_store(RESOURCE_BORROW_ACTORS,expected->view,expected->position,(uint8_t)(low^255u));
   assert(object_resource_read(got,0,&live)==OBJECT_IDENTITY_OK && live==(uint16_t)((low^255u)+256u*high));
   resource_world_store(RESOURCE_BORROW_ACTORS,expected->view,expected->position,low);
  }
  assert(object_resource_read(got,(uint16_t)view.size,&word)==OBJECT_IDENTITY_UNSUPPORTED);
 }
 for(unsigned family=OBJECT_ACTOR_DESCRIPTOR;family<=OBJECT_DROP_LIST;family++)for(unsigned word=0;word<65536;word++){
  int expected=0;ObjectResourceIdentity got;
  for(unsigned i=0;i<resource_count;i++)if(expected_resources[i].kind==(ObjectResourceKind)family && expected_resources[i].word==word){expected=1;break;}
  assert((object_resource_from_legacy((ObjectResourceKind)family,(uint16_t)word,&got)==OBJECT_IDENTITY_OK)==expected);
 }
 for(unsigned family=OBJECT_LEGACY_ACTOR;family<=OBJECT_LEGACY_EFFECT;family++)for(unsigned word=0;word<65536;word++){
  const ExpectedCallback *expected=0;ObjectCallbackIdentity got;uint16_t back;
  for(unsigned i=0;i<sizeof expected_callbacks/sizeof *expected_callbacks;i++)if(expected_callbacks[i].family==(ObjectLegacyCallbackFamily)family && expected_callbacks[i].word==word){expected=expected_callbacks+i;break;}
  assert((object_callback_from_legacy((ObjectLegacyCallbackFamily)family,(uint16_t)word,&got)==OBJECT_IDENTITY_OK)==!!expected);
  if(expected){assert(callback_role(got)==expected->role);assert(object_callback_to_legacy(got,&back)==OBJECT_IDENTITY_OK && back==word);}
  else assert(got.kind==OBJECT_CALLBACK_UNSUPPORTED);
 }
 for(unsigned value=0;value<65536;value++){
  ObjectCallbackIdentity request={OBJECT_CALLBACK_ACTOR,(ActorCallback)value,H_ZERO,ITEM_CALLBACK_UNSUPPORTED,{RESOURCE_DEMO_EFFECT,0}},checked;
  assert((object_callback_identity(request,&checked)==OBJECT_IDENTITY_OK)==(value>0 && value<ACTOR_CALLBACK_COUNT));
  request.kind=OBJECT_CALLBACK_ENEMY;request.enemy=(HazardEntry)value;
  assert((object_callback_identity(request,&checked)==OBJECT_IDENTITY_OK)==(value<=H_TREE_EMPTY));
  request.kind=OBJECT_CALLBACK_ITEM;request.item=(ItemCallbackRole)value;
  assert((object_callback_identity(request,&checked)==OBJECT_IDENTITY_OK)==(value>0 && value<=ITEM_CALLBACK_COLLECT));
  request.kind=OBJECT_CALLBACK_DEMO_EFFECT;request.effect.index=(uint16_t)value;
  assert((object_callback_identity(request,&checked)==OBJECT_IDENTITY_OK)==(value<3));
 }
 assert(object_graph_link_count()==sizeof expected_links/sizeof *expected_links);
 unsigned mutated=0;
 for(size_t i=0;i<object_graph_link_count();i++){
  ObjectGraphLink link,live,lookup;uint8_t low,high;uint16_t word=expected_links[i];
  assert(object_graph_link_at(i,&link)==OBJECT_IDENTITY_OK);
  assert(object_graph_link(link.source,link.member,&lookup)==OBJECT_IDENTITY_OK);
  assert(lookup.kind==link.kind);
  resource_world_read(RESOURCE_BORROW_ACTORS,link.source,link.member,&low);
  resource_world_read(RESOURCE_BORROW_ACTORS,link.source,link.member+1,&high);
  assert(word==(uint16_t)(low+256u*high));
  assert(object_live_link(link.source,link.member,&live)==OBJECT_IDENTITY_OK);
  if(link.kind==OBJECT_LINK_RESOURCE){uint16_t back;assert(object_resource_to_legacy(live.resource,&back)==OBJECT_IDENTITY_OK && back==word);}
  if(link.kind==OBJECT_LINK_CALLBACK && link.callback.kind!=OBJECT_CALLBACK_EMPTY){
   uint16_t back;assert(object_callback_to_legacy(live.callback,&back)==OBJECT_IDENTITY_OK && back==word);
   /* Invalid half-word splices never acquire a callable role, and no failed
    * interpretation overwrites the retained provider operand. */
   resource_world_store(RESOURCE_BORROW_ACTORS,link.source,link.member,0xff);
   resource_world_store(RESOURCE_BORROW_ACTORS,link.source,link.member+1,0xff);
   assert(object_live_link(link.source,link.member,&live)==OBJECT_IDENTITY_UNSUPPORTED);
   resource_world_read(RESOURCE_BORROW_ACTORS,link.source,link.member,&low);assert(low==255);
   resource_world_store(RESOURCE_BORROW_ACTORS,link.source,link.member,(uint8_t)word);
   resource_world_store(RESOURCE_BORROW_ACTORS,link.source,link.member+1,(uint8_t)(word>>8));
   assert(object_live_link(link.source,link.member,&live)==OBJECT_IDENTITY_OK);mutated++;
  }
 }
 ObjectGraphLink bad;
 assert(object_graph_link_at(object_graph_link_count(),&bad)==OBJECT_IDENTITY_UNSUPPORTED);
 assert(object_graph_link((ResourceWorldToken){65535},0,&bad)==OBJECT_IDENTITY_UNSUPPORTED);
 printf("{\"resources\":%u,\"links\":%u,\"live_mutations\":%u,\"resource_words\":458752,\"callback_words\":262144}\n",resource_count,(unsigned)object_graph_link_count(),mutated);
}
''', encoding='utf-8', newline='\n')
    exe = out / 'properties.exe'
    bounded([GCC, '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I', root/'c', '-I', root/'native/bridge',
             source, root/'native/resource_world.c', root/'native/bridge/resource_world_bridge.c', root/'native/object_identities.c', root/'native/bridge/object_identities_bridge.c', root/'native/resource_catalog.c', '-o', exe], 'identity-compile')
    result = bounded([exe, fixture], 'identity-run')
    receipt = dict(result='PASS', counts=json.loads(result['stdout']),
                   scope='Generated typed graph, registered resource positions, all raw-word families, callback roles, live mutations, Unsupported and bounded live scalar reads. No callback execution claim.')
    save(out / 'receipt.json', receipt)
    return receipt


def defects(root, out, bounded):
    """Mutate actual C, keeping the positive plain-image fixture unchanged."""
    import re
    from cbuild import GCC
    root, out = Path(root), Path(out)
    folder = out / 'object-identities'
    harness, fixture = folder/'properties.c', folder/'resources.bin'
    assert harness.is_file() and fixture.is_file(), 'positive borrower properties must run first'
    mutations = [
        ('admitted-script-interior', 'native/object_identities.c',
         'entry->position!=position || ', ''),
        ('stale-live-callback', 'native/bridge/object_identities_bridge.c',
         'uint16_t word=(uint16_t)(low+256u*high);*link=schema;',
         'uint16_t word=(uint16_t)(low+256u*high);*link=schema;return OBJECT_IDENTITY_OK;'),
        ('unregistered-callback-role', 'native/bridge/object_identities_bridge.c',
         ' return OBJECT_IDENTITY_UNSUPPORTED;\n}\nObjectIdentityStatus object_callback_to_legacy',
         ' return OBJECT_IDENTITY_OK;\n}\nObjectIdentityStatus object_callback_to_legacy'),
    ]
    rows = []
    for name, relative, old, new in mutations:
        path = root/relative; text = path.read_text(); assert text.count(old)==1, name
        text = text.replace(old, new)
        text = re.sub(r'#include "([^"]+)"', lambda m: '#include "'+(path.parent/m[1]).resolve().as_posix()+'"', text)
        candidate = folder/(name+'.c'); candidate.write_text(text, encoding='utf-8', newline='\n')
        sources = [candidate if relative==n else root/n for n in ['native/resource_world.c','native/bridge/resource_world_bridge.c','native/object_identities.c','native/bridge/object_identities_bridge.c','native/resource_catalog.c']]
        exe = folder/(name+'.exe')
        bounded([GCC, '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I', root/'c', '-I', root/'native/bridge',
                 harness, *sources, '-o', exe], 'identity-defect-'+name+'-compile')
        result = bounded([exe, fixture], 'identity-defect-'+name, ok=(3,))
        assert 'Assertion failed' in result['stderr'] or 'Assertion failed' in result['stdout'], result
        rows.append(dict(defect=name, result='DETECTED', exit=result['returncode'],
                         case='Actual C identity/graph properties; unchanged plain-image fixture'))
    return rows


if __name__ == '__main__':
    sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'verif')]
    from job_pool import run as child, save
    out = ROOT/'build/workers/cut-5x/identities'
    def bounded(command, tag): return child(command, ROOT, out, tag)
    print(json.dumps(run(ROOT, out, bounded, save), sort_keys=True))
