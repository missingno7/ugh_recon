"""Standalone-readiness measurement; generated copies only, no migration.

Source-body hooks include direct calls, static helpers and c/ugh.h inlines.
Bookkeeping never enters RAM/Devices or the digest/log. Every spawned child is
serial, owned by an 8-GiB Windows Job and bounded to 600 seconds. --all rebuilds
the native host and a literal smoke comparator under this worker's directory.
"""
import argparse
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/workers/close-adlx-19'
sys.path.insert(0, str(ROOT/'tools'))
from windows_job import WindowsJob, ExtendedLimits


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bounded(command, tag, env=None, cwd=ROOT):
    started = time.perf_counter()
    with WindowsJob() as job:
        limit = ExtendedLimits()
        limit.basic.flags = 0x2000 | 0x100 | 0x200
        limit.process_memory = limit.job_memory = 8*1024**3
        if not job.kernel.SetInformationJobObject(job.handle, 9, C.byref(limit), C.sizeof(limit)):
            raise C.WinError(C.get_last_error())
        p = subprocess.Popen(list(map(str, command)), cwd=cwd, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        job.assign(p)
        try:
            stdout, stderr = p.communicate(timeout=600)
        except subprocess.TimeoutExpired:
            job.terminate()
            stdout, stderr = p.communicate()
            save(OUT/'negative'/f'{tag}.json', dict(command=list(map(str,command)),
                 result='TIMEOUT', stdout=stdout, stderr=stderr))
            raise RuntimeError(tag+' timed out')
    result = dict(command=list(map(str,command)), returncode=p.returncode,
                  seconds=time.perf_counter()-started, stdout=stdout, stderr=stderr,
                  memory_limit_bytes=8*1024**3, timeout_seconds=600)
    save(OUT/'children'/f'{tag}.json', result)
    if p.returncode:
        save(OUT/'negative'/f'{tag}-{time.time_ns()}.json', result)
        raise RuntimeError(tag+' failed: '+stderr[-5000:])
    return result


def masked(text):
    return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                  lambda m: ''.join('\n' if c=='\n' else ' ' for c in m[0]), text, flags=re.S)


def bodies(text):
    """Top-level real definitions, not macro/prototype or nested control braces."""
    clean = masked(text)
    depth = 0
    start = None
    result = []
    for i,ch in enumerate(clean):
        if ch=='{':
            if depth==0:
                k=i-1
                while k>=0 and clean[k].isspace():k-=1
                if k>=0 and clean[k]==')':
                    end=k; n=1;k-=1
                    while k>=0 and n:
                        n += (clean[k]==')')-(clean[k]=='('); k-=1
                    before=clean[:k+1]
                    match=re.search(r'([A-Za-z_]\w*)\s*$', before)
                    if match:
                        name=match[1]
                        line=clean[clean.rfind('\n',0,match.start())+1:i]
                        if name not in ['if','for','while','switch'] and not line.lstrip().startswith('#'):
                            start=(match.start(),i,name)
            depth+=1
        elif ch=='}':
            depth-=1
            if depth==0 and start:
                a,b,name=start; result.append((a,b,i,name));start=None
    assert depth==0
    return result


HEADER = r'''
#ifndef STANDALONE_CENSUS_H
#define STANDALONE_CENSUS_H
struct Regs;
void sc_enter(unsigned);void sc_leave(unsigned);void sc_macro_leave(void);void sc_start(void);
void sc_machine(unsigned,unsigned,unsigned,unsigned,struct Regs *);
int sc_fallback(unsigned,int (*)(struct Regs *),struct Regs *);
#endif
'''

OBSERVER = r'''
#include "platform.h"
#include "census.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>
extern unsigned host_frame;
#include "metadata.inc"
typedef unsigned long long U64;
typedef struct Count {U64 count;unsigned first,last;} Count;
typedef struct Edge {unsigned kind,caller,bridge,site,a,b,c;Count n;uint16_t regs[14];} Edge;
#define CAP 131072
#define HCAP 2097152
typedef struct FrameCount {unsigned kind,id,frame;U64 count;} FrameCount;
static FrameCount history[HCAP];static unsigned history_buckets[HCAP*2],nhistory;
static Count counts[SC_FUNCTIONS],fallbacks[SC_SITES];
static Edge edges[CAP];static unsigned buckets[CAP*2],nedges;
static unsigned stack[4096],depth,enabled;static DWORD game_thread;
static void fail(const char *what){fprintf(stderr,"census: %s\n",what);fflush(stderr);ExitProcess(86);}
static void add(Count *c){if(!c->count)c->first=host_frame;c->count++;c->last=host_frame;}
static void frame_add(unsigned kind,unsigned id){
 unsigned h=(kind*769u+id*12289u+host_frame*31u)&(HCAP*2-1);
 while(history_buckets[h]){FrameCount *p=&history[history_buckets[h]-1];if(p->kind==kind && p->id==id && p->frame==host_frame){p->count++;return;}h=(h+1)&(HCAP*2-1);}
 if(nhistory==HCAP){fail("frame-history capacity");}FrameCount *p=&history[nhistory];history_buckets[h]=++nhistory;
 p->kind=kind;p->id=id;p->frame=host_frame;p->count=1;
}
static unsigned parent(void){return depth>1?stack[depth-2]:0;}
static unsigned bridge(void){for(unsigned i=depth;i;i--)if(sc_kinds[stack[i-1]]==2)return stack[i-1];return 0;}
static void edge(unsigned kind,unsigned site,unsigned a,unsigned b,unsigned c,Regs *r){
 unsigned caller=kind==7 && depth?stack[depth-1]:parent(),owner=bridge();
 unsigned h=(kind*12289u+caller*769u+owner*97u+site*53u+a*31u+b*17u+c)&(CAP*2-1);
 while(buckets[h]){Edge *e=&edges[buckets[h]-1];if(e->kind==kind && e->caller==caller && e->bridge==owner && e->site==site && e->a==a && e->b==b && e->c==c){add(&e->n);frame_add(2,buckets[h]-1);return;}h=(h+1)&(CAP*2-1);}
 if(nedges==CAP){fail("edge capacity");}Edge *e=&edges[nedges];buckets[h]=++nedges;
 e->kind=kind;e->caller=caller;e->bridge=owner;e->site=site;e->a=a;e->b=b;e->c=c;add(&e->n);
 frame_add(2,nedges-1);
 if(r)memcpy(e->regs,r,sizeof e->regs);
}
void sc_enter(unsigned id){
 if(!enabled || GetCurrentThreadId()!=game_thread)return;
 if(id>=SC_FUNCTIONS || depth>=4096)fail("entry bound");
 stack[depth++]=id;add(&counts[id]);
 if(sc_kinds[id]==1)frame_add(0,id);
 if(sc_entries[id])edge(5,0,id,0,0,NULL);
}
void sc_leave(unsigned id){
 if(!enabled || GetCurrentThreadId()!=game_thread)return;
 if(!depth || stack[depth-1]!=id){fprintf(stderr,"expected=%u depth=%u top=%u frame=%u\n",id,depth,depth?stack[depth-1]:0,host_frame);fail("unbalanced source hook");}depth--;
}
void sc_macro_leave(void){if(enabled && GetCurrentThreadId()==game_thread){if(!depth)fail("macro underflow");sc_leave(stack[depth-1]);}}
void sc_machine(unsigned kind,unsigned a,unsigned b,unsigned c,Regs *r){
 if(!enabled)return;
 if(kind==1 && sc_far[parent()]){kind=6;unsigned at=(unsigned)r->ss*16u+r->sp;c=ugh_mem[at]+256u*ugh_mem[at+1];}
 edge(kind,0,a,b,c,r);
}
int sc_fallback(unsigned site,int (*fn)(Regs *),Regs *r){
 if(site>=SC_SITES){fail("fallback bound");}add(&fallbacks[site]);
 frame_add(1,site);
 edge(7,site,0,0,0,r);return fn(r);
}
static void count(FILE *f,Count c){fprintf(f,"[%llu,%u,%u]",c.count,c.first,c.last);}
static void dump(void){
 const char *p=getenv("SC_OUTPUT");if(!p)return;FILE *f=fopen(p,"wb");if(!f)fail("dump open");
 fprintf(f,"{\"frame\":%u,\"body\":[",host_frame);unsigned n=0;
 for(unsigned i=1;i<SC_FUNCTIONS;i++)if(counts[i].count){fprintf(f,"%s[%u,",n++?",":"",i);count(f,counts[i]);fputc(']',f);}
 fprintf(f,"],\"fallbacks\":[");n=0;for(unsigned i=0;i<SC_SITES;i++)if(fallbacks[i].count){fprintf(f,"%s[%u,",n++?",":"",i);count(f,fallbacks[i]);fputc(']',f);}
 fprintf(f,"],\"edges\":[");for(unsigned i=0;i<nedges;i++){Edge *e=&edges[i];fprintf(f,"%s[%u,%u,%u,%u,%u,%u,%u,",i?",":"",e->kind,e->caller,e->bridge,e->site,e->a,e->b,e->c);count(f,e->n);fprintf(f,",[");for(unsigned j=0;j<14;j++)fprintf(f,"%s%u",j?",":"",e->regs[j]);fprintf(f,"]]");}
 fprintf(f,"],\"per_frame\":[");for(unsigned i=0;i<nhistory;i++){FrameCount *p=&history[i];fprintf(f,"%s[%u,%u,%u,%llu]",i?",":"",p->kind,p->id,p->frame,p->count);}
 fprintf(f,"],\"depth_at_dump\":%u}\n",depth);fclose(f);
}
static int control_reply(Regs *r){return r->ax==0x5678?0:1;}
void sc_start(void){
 game_thread=GetCurrentThreadId();enabled=1;if(atexit(dump))fail("atexit");
 if(getenv("SC_CONTROL")){
  Regs r={0};r.ax=0x5678;host_frame=7;sc_enter(1);sc_machine(0,0x1234,0x2345,0x3456,&r);
  if(sc_fallback(0,control_reply,&r)){fail("control reply");}sc_leave(1);
  if(depth || counts[1].count!=1 || fallbacks[0].count!=1 || counts[1].first!=7)fail("control counters");
  exit(0);
 }
}
'''


def replace_returns(body, ident):
    clean=masked(body); edits=[]
    for m in re.finditer(r'\breturn\b',clean):
        semi=clean.index(';',m.end());expr=body[m.end():semi].strip()
        if expr=='0':
            value='{sc_leave('+str(ident)+');return 0;}'
        elif expr:
            value='{__auto_type sc_result=('+expr+');sc_leave('+str(ident)+');return sc_result;}'
        else:value='{sc_leave('+str(ident)+');return;}'
        edits.append((m.start(),semi+1,value))
    for a,b,value in reversed(edits):body=body[:a]+value+body[b:]
    return '\nsc_enter('+str(ident)+');\n'+body+'\nsc_leave('+str(ident)+');\n'


def instrument(text, source, functions, sites):
    edits=[]
    for a,b,e,name in bodies(text):
        # Per-byte typed view leaves have no control-flow edge or fallback.
        # Keep every c/ body and every entry/transfer hook; avoid multiplying
        # their cost by three hooks per ordinary memory byte.
        if source=='native/bridge/timing_world_bridge.c' and name in {
            'timing_shared_read','timing_shared_write','timing_is_owned',
            'get','put','require','word_token','token_word','audio_borrowed_byte','binding_width'}:
            assert not re.search(r'\b(?:l1_\w+|ugh_dispatch\w*|ugh_call_near\w*)\s*\(',text[b+1:e])
            continue
        if source=='native/bridge/audio_world_bridge.c' and name=='audio_borrowed_store':
            assert not re.search(r'\b(?:l1_\w+|ugh_dispatch\w*|ugh_call_near\w*)\s*\(',text[b+1:e])
            continue
        ident=len(functions);body=text[b+1:e]
        line=text.count('\n',0,a)+1
        far=bool(re.search(r'\bugh_dispatch\s*\(',body) and re.search(r'(?:push\w*\s*\([^;]*r->cs|wr16\s*\([^;]*r->cs)',body))
        functions.append(dict(id=ident,name=name,path=source,line=line,
                              kind='bridge' if source.startswith('native/bridge/') else 'c',
                              entry=bool(re.match(r'(?:c_|l1_)',name)),far_frame_helper=far))
        # Explicit fallback-call sites, including conditional expressions; declarations
        # never occur in extracted bodies. Keep the entire enclosing guard prefix.
        for match in reversed(list(re.finditer(r'\b(l1_\w+)\s*\(\s*r\s*\)',body))):
            site=len(sites);at=b+1+match.start()
            sites.append(dict(id=site,path=source,line=text.count('\n',0,at)+1,
                              caller=name,callee=match[1],
                              guard_prefix=body[:match.start()].strip(),
                              context='\n'.join(text[:at].splitlines()[-8:])))
            body=body[:match.start()]+f'sc_fallback({site},{match[1]},r)'+body[match.end():]
        call=None
        if name=='ugh_dispatch':call='sc_machine(1,segment,offset,0,r);'
        elif name=='ugh_call_near':call='sc_machine(0,r->cs,target,return_ip,r);'
        elif name=='ugh_dispatch_interrupt':call='sc_machine(2,segment,offset,0,r);'
        elif name=='platform_interrupt':call='sc_machine(3,n,r->ax,0,r);'
        elif name=='ugh_call_near_ret_hook':call='sc_machine(4,GAME_SEG,target,return_ip,r);'
        body=replace_returns(body,ident)
        if call:body=body.replace('sc_enter('+str(ident)+');','sc_enter('+str(ident)+');'+call,1)
        edits.append((b+1,e,body))
    for a,b,body in reversed(edits):text=text[:a]+body+text[b:]
    # Error-propagating macros return from their caller, not from a separately
    # instrumentable function. An ordinary generated-copy return needs a pop too.
    def macro_hook(m):
        line=m[0]
        def ret(q):
            expr=q[1].strip()
            if not expr:return '{sc_macro_leave();return;}'
            return '{__auto_type sc_macro_result=('+expr+');sc_macro_leave();return sc_macro_result;}'
        return re.sub(r'\breturn\b\s*([^;]*);',ret,line)
    text=re.sub(r'^[ \t]*#define(?:[^\n]*\\\n)*[^\n]*',macro_hook,text,flags=re.M)
    return text


def unit_list():
    import hostbuild
    return hostbuild.selected_units()


def original_owned(cert):
    original=cert.get('original',{})
    if isinstance(original,list):return [r['identity'] for r in original]
    return [r if isinstance(r,str) else r['identity'] for r in original.get('owned',[])]


def generate(literal=False):
    import hostbuild,cgen
    folder=OUT/('literal' if literal else 'instrumented');folder.mkdir(parents=True,exist_ok=True)
    units=[] if literal else unit_list()
    exports={n for u in units for n in u['exports']}
    functions=[dict(id=0,name='<host/native>',path='',kind='external',entry=False,far_frame_helper=False)]
    sites=[];sources=[];inputs=[Path(__file__),ROOT/'verif/windows_job.py',ROOT/'tools/hostbuild.py',ROOT/'tools/cgen.py',ROOT/'metadata/program-model.json',*sorted((ROOT/'metadata/closure').glob('*.json'))]
    for top in ['c','native','host']:
        for p in sorted((ROOT/top).rglob('*')):
            if p.suffix not in ['.c','.h','.inc']:continue
            rel=p.relative_to(ROOT).as_posix();text=p.read_text();inputs.append(p)
            if top=='c' and p.suffix=='.c':
                for name in sorted(exports):text=re.sub(r'\b'+re.escape(name)+r'\b','l1_'+name[2:],text)
            text=hostbuild.composition_source(rel,text,units)
            if not literal and ((top=='c' and p.name!='dispatch_table.inc') or rel.startswith('native/bridge/')):
                text=instrument(text,rel,functions,sites)
            if not literal and rel=='host/main.c':
                needle='int main(int argc,char **argv) {';assert needle in text;text=text.replace(needle,needle+'\nsc_start();',1)
            target=folder/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
    sources += sorted((folder/'c').glob('*.c'))+sorted((folder/'host').glob('*.c'))
    sources += [folder/u['native'].relative_to(ROOT) for u in units]
    sources += [folder/u['bridge'].relative_to(ROOT) for u in units]
    for site in sites:
        path=ROOT/site['path'];text=path.read_text();name=site['caller']
        site['upstream_call_contexts']=[dict(line=i+1,text='\n'.join(text.splitlines()[max(0,i-3):i+2]))
            for i,line in enumerate(text.splitlines()) if re.search(r'\b'+re.escape(name)+r'\s*\(',line)
            and not re.search(r'\b(?:int|void)\s+'+re.escape(name)+r'\s*\(',line)]
    (folder/'fallbacks.h').write_text(('' if literal else '#include "census.h"\n')+'#include "ugh.h"\n'+''.join(f'int l1_{n[2:]}(Regs *);\n' for n in sorted(exports)))
    (folder/'units.c').write_text('#include "host.h"\nconst char *host_native_units[]={'+','.join(json.dumps(u['component']) for u in units)+'};\nconst unsigned host_native_unit_count='+str(len(units))+';\nconst char *host_variant='+json.dumps('literal' if literal else 'native-bridged')+';\n')
    sources.append(folder/'units.c')
    # Read-only symbol validation; never call cgen.generate or a maintained build.
    mz,symbols=cgen.read_symbols()
    lines=['#include "host.h"','const HostSymbol host_symbols[]={']
    lines += ['{'+json.dumps(n)+f',{cgen.LOAD+r["frame"]},{r["offset"]}'+'},' for n,r in sorted(symbols.items())]
    lines += ['};','const unsigned host_symbol_count=sizeof(host_symbols)/sizeof(host_symbols[0]);',f'const char host_data_hash[]="{hashlib.sha256(mz.data).hexdigest()}";']
    (folder/'symbols.c').write_text('\n'.join(lines)+'\n');sources.append(folder/'symbols.c')
    shutil.copy2(ROOT/'build/link/plain/UGH.EXE',folder/'ugh-data.exe')
    if not literal:
        (folder/'census.h').write_text(HEADER)
        kinds=[2 if f['kind']=='bridge' else 1 if f['kind']=='c' else 0 for f in functions]
        meta=f'#define SC_FUNCTIONS {len(functions)}\n#define SC_SITES {max(1,len(sites))}\n'
        for name,values in [('sc_kinds',kinds),('sc_far',[int(f['far_frame_helper']) for f in functions]),('sc_entries',[int(f['entry']) for f in functions])]:
            meta+='static const unsigned char '+name+'[]={'+','.join(map(str,values))+'};\n'
        (folder/'metadata.inc').write_text(meta);(folder/'census.c').write_text(OBSERVER);sources.append(folder/'census.c')
    command=[hostbuild.GCC,'-O2','-g','-std=c11','-Wall','-Wextra','-Werror','-fwrapv',
             *hostbuild.composition_options(units,folder),
             '-include',folder/'fallbacks.h','-I',folder/'c','-I',folder/'host',
             '-I',hostbuild.SDL/'include','-I',hostbuild.OPL]
    if not literal:command+=['-include',folder/'census.h','-I',folder]
    command+=['-o',folder/'ugh.exe',*sources,hostbuild.OPL/'opl3.c','-L',hostbuild.SDL/'lib','-lSDL3','-lbcrypt']
    env=dict(os.environ,PATH=str(hostbuild.GCC.parent)+os.pathsep+os.environ.get('PATH',''))
    result=bounded(command,'build-literal' if literal else 'build-native',env)
    for dll in [hostbuild.SDL/'bin/SDL3.dll',hostbuild.GCC.parent/'libwinpthread-1.dll']:
        if dll.exists():shutil.copy2(dll,folder/dll.name)
    result.pop('stdout');result.pop('stderr')
    result.update(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  variant='literal' if literal else 'native-bridged',executable_sha256=sha(folder/'ugh.exe'),
                  functions=functions,sites=sites,units=[dict(component=u['component'],exports=u['exports']) for u in units],
                  inputs={str(p.relative_to(ROOT)):sha(p) for p in inputs},compiler_sha256=sha(hostbuild.GCC))
    save(folder/'build.json',result)
    print('Built',result['variant'],len(functions)-1,'instrumented bodies',len(sites),'fallback sites',flush=True)


def run_one(name):
    folder=OUT/'instrumented';exe=folder/'ugh.exe';build=json.loads((folder/'build.json').read_text())
    assert sha(exe)==build['executable_sha256']
    for n,h in build['inputs'].items():assert sha(ROOT/n)==h,'input changed: '+n
    smoke=name=='smoke';path=ROOT/'tests/scenarios'/f'{name}.txt'
    if smoke:frames=256
    else:frames=next(int(x.split()[1]) for x in path.read_text().splitlines() if x.startswith('frames '))
    command=[exe,'--headless',str(frames),'--timeout','590']
    command+=['--smoke','256'] if smoke else ['--script',path]
    rawpath=OUT/'runs'/f'{name}-raw.json';rawpath.parent.mkdir(exist_ok=True)
    env=dict(os.environ,SC_OUTPUT=str(rawpath))
    child=bounded(command,'run-'+name,env)
    got=[json.loads(x) for x in child['stdout'].splitlines()]
    refpath=ROOT/'build/whole'/('attract.ref.json' if smoke else name+'.ref.json')
    ref=json.loads(refpath.read_text())['frames']
    assert got[:len(ref)]==ref,(name,'reference differs')
    if smoke:
        literal=bounded([OUT/'literal/ugh.exe','--headless','256','--smoke','256','--timeout','590'],'smoke-literal')
        expected=[json.loads(x) for x in literal['stdout'].splitlines()]
        assert got==expected and len(got)==256,'full literal smoke differs'
    else:assert len(got)==len(ref),(name,'length differs')
    raw=json.loads(rawpath.read_text());raw.update(scenario=name,matched_reference=True,
        boundaries=len(got),reference=str(refpath.relative_to(ROOT)),reference_sha256=sha(refpath),
        reference_boundaries=len(ref),smoke_full_literal=smoke,seconds=child['seconds'],
        build_sha256=sha(folder/'build.json'),frame_convention='host_frame at entry: completed boundaries, zero before first flip')
    save(OUT/'runs'/f'{name}.json',raw)
    print('PASS',name,len(got),'boundaries',round(child['seconds'],3),'seconds',flush=True)


def static_inventory():
    model=json.loads((ROOT/'metadata/program-model.json').read_text())
    certs={p.stem:json.loads(p.read_text()) for p in (ROOT/'metadata/closure').glob('*.json')}
    routine_owner={r:n for n,d in certs.items() for r in original_owned(d)}
    components={r:n for n,d in model['components'].items() for r in d['routines']}
    result=[]
    def expanded(p,seen):
        if p in seen:return ''
        seen.add(p);text=p.read_text()
        for inc in re.findall(r'#include "([^"]+)"',text):
            child=(p.parent/inc).resolve()
            if child.is_relative_to((ROOT/'native/bridge').resolve()) and child.exists():text+='\n'+expanded(child,seen)
        return text
    owners={}
    for symbol,v in model['variables'].items():
        writers=sorted({routine_owner.get(r,components.get(r,'unattributed')) for r in v.get('writers',[])})
        readers=sorted({routine_owner.get(r,components.get(r,'unattributed')) for r in v.get('readers',[])})
        owners[symbol]=dict(candidate_writers=writers,reader_units=readers,shared=len(set(writers+readers))>1,
                            completeness=v.get('complete'),writers=v.get('writers',[]),readers=v.get('readers',[]))
    for u in unit_list():
        p=u['bridge'];seen=set();text=expanded(p,seen);clean=masked(text)
        owned=set(original_owned(certs[u['component']]))
        refs={m[1] for m in re.finditer(r'\b[DGST]\(\s*(\w+)\s*\)',clean)}
        symbols={}
        for n,v in model['variables'].items():
            read=sorted(set(v.get('readers',[]))&owned);write=sorted(set(v.get('writers',[]))&owned)
            if n in refs or read or write:symbols[n]=dict(model_readers=read,model_writers=write,
                source_token=n in refs,source_accesses=[dict(line=i+1,text=line.strip()) for i,line in enumerate(text.splitlines()) if re.search(r'\b'+re.escape(n)+r'\b',line)],**owners[n])
        # Keep named data/resource bindings outside the incomplete program-model
        # variable set, and immediate read/write directions where syntactically
        # known. Never turn an indexed/far alias into a guessed named field.
        named={}
        for tag,n in re.findall(r'\b([DGST])\(\s*(\w+)\s*\)',clean):
            if len(n)<2 or {'G':'GAME','S':'SOUND','T':'TIMER','D':'DGROUP'}[tag]+':'+n in model['routines']:continue
            named.setdefault(n,dict(tags=[],reads=[],writes=[],classification='data' if tag=='D' or n in model['variables'] else 'unclassified binding'))['tags'].append(tag)
        for m in re.finditer(r'\b(rd(?:8|16|32)(?:_linear)?|wr(?:8|16|32)|R|W|RI|WI|RX|INPUT_READ|INPUT_WRITE)\s*\(',clean):
            at=m.end();depth=1;end=at
            while depth:
                depth+=(clean[end]=='(')-(clean[end]==')');end+=1
            args=[];start=at;depth=0
            for i in range(at,end-1):
                depth+=(clean[i]=='(')-(clean[i]==')')
                if clean[i]==',' and not depth:args.append(clean[start:i]);start=i+1
            args.append(clean[start:end-1]);call=m[1]
            base=','.join(args[:2]) if call.startswith(('rd','wr')) else args[0]
            found=re.findall(r'\b[DGST]\(\s*(\w+)\s*\)',base)
            if call in ['R','W','RI','WI','RX','INPUT_READ','INPUT_WRITE'] and re.fullmatch(r'\s*\w+\s*',base):found.append(base.strip())
            direction='writes' if call.startswith('wr') or call in ['W','WI','INPUT_WRITE'] else 'reads'
            for n in found:
                if n not in named:named[n]=dict(tags=[],reads=[],writes=[],classification='data')
                named[n][direction].append(dict(expanded_line=clean.count('\n',0,m.start())+1,expression=text[m.start():end]))
        for v in named.values():v['tags']=sorted(set(v['tags']))
        ramcalls=[]
        for i,line in enumerate(text.splitlines()):
            if re.search(r'\b(?:rd(?:8|16|32)(?:_linear)?|wr(?:8|16|32)|memcpy|memset|ugh_mem)\b',line):
                ramcalls.append(dict(expanded_line=i+1,text=line.strip()))
        (OUT/'static-source').mkdir(exist_ok=True)
        (OUT/'static-source'/f'{u["component"]}.txt').write_text(text,encoding='utf-8')
        result.append(dict(component=u['component'],bridge=p.relative_to(ROOT).as_posix(),
            included_bridge_headers=sorted(x.relative_to(ROOT).as_posix() for x in seen if x!=p),
            ram_symbols=symbols,named_source_bindings=named,raw_access_expressions=ramcalls,
            regs_fields=sorted(set(re.findall(r'\b\w+->(ax|bx|cx|dx|si|di|bp|sp|cs|ds|es|ss|ip|flags)\b',clean))),
            ports_and_interrupts=[dict(line=i+1,text=l.strip()) for i,l in enumerate(text.splitlines()) if re.search(r'\b(?:platform_(?:in|out|interrupt|service_point(?:_at)?)|ugh_dispatch_interrupt)\s*\(',l)],
            dispatcher_calls=[dict(line=i+1,text=l.strip()) for i,l in enumerate(text.splitlines()) if re.search(r'\b(?:ugh_(?:dispatch|call_near|resolve|call_near_ret_hook)|\w*far\w*call\w*)\s*\(',l)]))
    save(OUT/'static.json',dict(bridges=result,variables=owners,
        scope='Lexical maintained bridge/include access expressions plus program-model per-original read/write sets. Model completeness=false stays false; arbitrary numeric/far/indexed aliases are explicitly retained as raw access expressions, not assigned invented symbol ownership. Expanded line numbers refer to the concatenated inventory, source tokens are verbatim.'))
    lines=['# Bridge machine-facility inventory','',
        'Named read/write directions below come from the original per-entry program model. Source-token-only names do not imply a read or write; raw accesses through dynamic bindings are listed separately in static.json and static-source/<unit>.txt. Completeness=false remains false. All included bridge helpers are considered. No independent owner is inferred for aliases.','']
    for row in result:
        lines+=['## '+row['component'],'','Bridge: `'+row['bridge']+'`.','',
            'Regs: '+', '.join(row['regs_fields'])+'.','',
            'Named reads: '+', '.join('`'+n+'`' for n,v in row['ram_symbols'].items() if v['model_readers'])+'.','',
            'Named writes: '+', '.join('`'+n+'`' for n,v in row['ram_symbols'].items() if v['model_writers'])+'.','',
            'Other source bindings (direction in access expressions): '+', '.join('`'+n+'`' for n,v in row['ram_symbols'].items() if v['source_token'] and not(v['model_readers'] or v['model_writers']))+'.','',
            'Additional named bindings outside the model: '+', '.join('`'+n+'` ('+('/'.join(x for x in ['read' if v['reads'] else '', 'write' if v['writes'] else ''] if x) or v['classification'])+')' for n,v in sorted(row['named_source_bindings'].items()) if n not in row['ram_symbols'])+'.','',
            'Ports / vectors / service delivery:','']
        lines+=['- `'+x['text'].replace('`','')+'`' for x in row['ports_and_interrupts']]
        lines+=['','Dispatcher / far-call source:','']
        lines+=['- `'+x['text'].replace('`','')+'`' for x in row['dispatcher_calls']]
        lines+=['',f'Raw RAM accessor lines: {len(row["raw_access_expressions"])}; verbatim source in `static-source/{row["component"]}.txt`.','']
    (OUT/'BRIDGES.md').write_text('\n'.join(lines),encoding='utf-8')
    lines=['# Candidate shared state ownership','',
           'Candidate writers are certificate owners of the original writers; readers retain borrowed views. Multiple writers mean composition must bind the same cell, not choose one copy. Program-model unknown aliases and incompleteness remain open. The consolidation plan is in REPORT.md.','',
           '| Symbol | Writer units | Reader units | Shared | Model complete |','|---|---|---|---|---|']
    for n,v in owners.items():lines.append('| '+n+' | '+', '.join(v['candidate_writers'])+' | '+', '.join(v['reader_units'])+' | '+str(v['shared'])+' | '+str(v['completeness'])+' |')
    (OUT/'OWNERS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Static inventory:',len(result),'bridges,',len(owners),'named variables',flush=True)


def summarize():
    build=json.loads((OUT/'instrumented/build.json').read_text());f=build['functions'];sites=build['sites']
    runs=[json.loads(p.read_text()) for p in sorted((OUT/'runs').glob('*.json')) if not p.stem.endswith('-raw')]
    assert len(runs)==21 and all(r['matched_reference'] for r in runs)
    # Map the maintained dispatch table to actual selected native adapter identities.
    exports={n:u['component'] for u in build['units'] for n in u['exports']}
    dispatch={}
    header=(ROOT/'c/ugh_sym.h').read_text()
    load=int(re.search(r'#define UGH_LOAD (0x[0-9a-fA-F]+)',header)[1],0)
    sym={m[1]:eval(re.sub(r'(?<=[0-9a-fA-F])[uUlL]+\b','',m[2]),{'__builtins__':{}},{'UGH_LOAD':load})
         for m in re.finditer(r'^#define\s+(UGH_[SO]_\w+)\s+([^\n]+)',header,re.M)}
    for seg,off,name in re.findall(r'\{(UGH_S_\w+),(UGH_O_\w+),(c_\w+)\}',(ROOT/'c/dispatch_table.inc').read_text()):
        dispatch[f'{sym[seg]:04X}:{sym[off]:04X}']=dict(name=name,kind='native' if name in exports else 'L1',owner=exports.get(name))
    detailed=[];totals={};fallbacks={}
    for r in runs:
        history={}
        for kind,ident,frame,count in r['per_frame']:history.setdefault((kind,ident),[]).append([frame,count])
        body=[]
        for ident,n in r['body']:
            row=dict(**f[ident],count=n[0],first_frame=n[1],last_frame=n[2],scenario=r['scenario']);body.append(row)
            if f[ident]['kind']=='c':
                row['per_frame']=sorted(history[(0,ident)])
                assert sum(x[1] for x in row['per_frame'])==n[0]
            t=totals.setdefault(str(ident),dict(**f[ident],count=0,examples=[]));t['count']+=n[0];t['examples'].append(dict(scenario=r['scenario'],frame=n[1],count=n[0]))
        fb=[]
        for ident,n in r['fallbacks']:
            row=dict(**sites[ident],count=n[0],first_frame=n[1],last_frame=n[2],scenario=r['scenario'],per_frame=sorted(history[(1,ident)]));fb.append(row)
            assert sum(x[1] for x in row['per_frame'])==n[0]
            fallbacks.setdefault(str(ident),[]).append(dict(scenario=r['scenario'],frame=n[1],count=n[0]))
        edges=[]
        for edge_id,(kind,caller,bridge,site,a,b,c,n,regs) in enumerate(r['edges']):
            target=dispatch.get(f'{a:04X}:{b:04X}',dict(name=f'{a:04X}:{b:04X}',kind='external/unknown'))
            if kind==5:target=dict(name=f[a]['name'],kind='L1' if f[a]['kind']=='c' else 'native',owner=f[a]['path'])
            if kind==7:target=dict(name=sites[site]['callee'],kind='L1',owner=sites[site]['path'])
            if kind==3:target=dict(name=f'INT {a:02X} AX={b:04X}',kind='platform-service')
            if kind==2 and (a,b)==(0xf000,0x100):target=dict(name='fixture BIOS INT08 chain',kind='platform-service')
            edges.append(dict(kind=['near','dispatch','interrupt-delivery','DOS/BIOS-interrupt','broken-far-hook','ABI-entry','far-dispatch','fallback'][kind],
                caller=f[caller],bridge=f[bridge],site=sites[site] if kind==7 else None,target=target,
                segment=a,offset=b,return_ip=c,count=n[0],first_frame=n[1],last_frame=n[2],first_regs=regs,
                per_frame=sorted(history[(2,edge_id)])))
            assert sum(x[1] for x in edges[-1]['per_frame'])==n[0]
        item=dict(scenario=r['scenario'],boundaries=r['boundaries'],bodies=body,fallbacks=fb,machine_edges=edges)
        save(OUT/'detail'/f'{r["scenario"]}.json',item);detailed.append(dict(scenario=r['scenario'],boundaries=r['boundaries'],
            l1_body_calls=sum(x['count'] for x in body if x['kind']=='c' and x['entry']),
            fallback_calls=sum(x['count'] for x in fb),machine_edge_calls=sum(x['count'] for x in edges if x['kind']!='ABI-entry')))
    unreplaced=sorted(set(v['name'] for v in dispatch.values() if v['kind']=='L1'))
    save(OUT/'census.json',dict(revision=build['revision'],result='PASS',scenarios=detailed,
         functions=list(totals.values()),fallback_sites=[dict(**s,taken=str(s['id']) in fallbacks,
             observations=fallbacks.get(str(s['id']),[])) for s in sites],unreplaced=unreplaced,
         frame_convention='Completed host boundaries at function/edge entry; first/last are zero-based.',
         limits='21 serial native runs; smoke prefix against existing attract reference, all256 against generated unmodified literal host; no universal never-taken theorem.'))
    lines=['# Dynamic census','',
           'Frames are zero-based completed host boundaries before entry; post-run service teardown may appear at frame N. Every c/ body, explicit l1 call site and machine-edge group has an exact [frame,count] histogram in detail/<scenario>.json. Layered near/dispatch/far/ABI events are counted separately, not presented as unique logical calls.','',
           '| Scenario | Boundaries | L1 entry calls | Explicit l1 calls | Machine-edge layer calls |','|---|---:|---:|---:|---:|']
    for r in detailed:lines.append('| '+r['scenario']+' | '+' | '.join(str(r[k]) for k in ['boundaries','l1_body_calls','fallback_calls','machine_edge_calls'])+' |')
    lines+=['','## Executed L1 entry bodies','','| Entry | Calls | Scenario: first frame (count) |','|---|---:|---|']
    for row in totals.values():
        if row['kind']=='c' and row['entry']:
            lines.append('| '+row['name']+' | '+str(row['count'])+' | '+', '.join(x['scenario']+':'+str(x['frame'])+' ('+str(x['count'])+')' for x in row['examples'])+' |')
    lines+=['','## Explicit l1 sites','','Bridge admission fallbacks are distinguished from unconditional calls introduced by symbol replacement in generated legacy c/ wrappers. Zero observations permit a fail-closed proposal for the tested/admitted path, not a universal reachability theorem.','',
            '| Site | Call | Class | Observations | Guard / enclosing source |','|---|---|---|---|']
    for site in sites:
        obs=fallbacks.get(str(site['id']),[])
        lines.append('| '+str(site['id'])+' '+site['path']+':'+str(site['line'])+' | '+site['callee']+' | '+('bridge admission' if site['path'].startswith('native/') else 'generated legacy call')+' | '+(', '.join(x['scenario']+':'+str(x['frame'])+' x'+str(x['count']) for x in obs) or '0, not taken')+' | '+site['caller']+'; full guard_prefix and upstream_call_contexts in census.json |')
    (OUT/'DYNAMIC.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Summary PASS:',len(unreplaced),'unreplaced entries;',sum(x['fallback_calls'] for x in detailed),'explicit fallback calls',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build',action='store_true');p.add_argument('--literal',action='store_true')
    p.add_argument('--one');p.add_argument('--static',action='store_true');p.add_argument('--summarize',action='store_true');p.add_argument('--all',action='store_true');p.add_argument('--control',action='store_true')
    a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if a.build:generate(a.literal)
    if a.static:static_inventory()
    if a.one:run_one(a.one)
    if a.control:
        path=OUT/'observer-control.json'
        bounded([OUT/'instrumented/ugh.exe'],'observer-control',dict(os.environ,SC_CONTROL='1',SC_OUTPUT=str(path)))
        r=json.loads(path.read_text());assert r['fallbacks']==[[0,[1,7,7]]] and r['body']==[[1,[1,7,7]]] and r['depth_at_dump']==0
        print('PASS isolated observer control',flush=True)
    if a.summarize:summarize()
    if a.all:
        # Build itself is a bounded child, and each compiler grandchild has its own Job.
        for args in [['--build'],['--build','--literal'],['--control'],['--static']]:
            bounded([sys.executable,__file__,*args],'driver-'+args[-1].strip('-'))
        for path in sorted((ROOT/'tests/scenarios').glob('*.txt')):
            bounded([sys.executable,__file__,'--one',path.stem],'driver-'+path.stem)
        bounded([sys.executable,__file__,'--one','smoke'],'driver-smoke')
        summarize()


if __name__=='__main__':main()
