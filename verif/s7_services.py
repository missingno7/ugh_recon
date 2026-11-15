"""Step 7.2: independent deterministic services, actual host streams and defects.

Only generated copies of verification sources are instrumented. All children are
serial, limited to 600s and 8 GiB in a Windows job. The backend object is compiled
alone, with only standard C headers and port/services.h in its include closure.
"""
from __future__ import annotations
import argparse
import ctypes as C
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/workers/s7-services'
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'verif')]
from cbuild import GCC
from windows_job import WindowsJob, ExtendedLimits

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n')

def bounded(command, name, *, success=True):
    command = list(map(str, command))
    env = dict(os.environ, PATH=str(GCC.parent)+os.pathsep+os.environ.get('PATH',''),
               SDL_AUDIO_DRIVER='dummy', SDL_VIDEO_DRIVER='dummy')
    start = time.perf_counter()
    with WindowsJob() as job:
        limits = ExtendedLimits()
        limits.basic.flags = 0x2000 | 0x100 | 0x200
        limits.process_memory = limits.job_memory = 8*1024**3
        if not job.kernel.SetInformationJobObject(job.handle,9,C.byref(limits),C.sizeof(limits)):
            raise C.WinError(C.get_last_error())
        p = subprocess.Popen(command, cwd=ROOT, env=env, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        job.assign(p)
        try:
            stdout, stderr = p.communicate(timeout=600)
        except subprocess.TimeoutExpired:
            job.terminate(); stdout, stderr = p.communicate()
            save(OUT/'children'/(name+'.json'),dict(command=command,result='TIMEOUT',stdout=stdout,stderr=stderr))
            raise
    row = dict(command=command,returncode=p.returncode,stdout=stdout,stderr=stderr,
               seconds=time.perf_counter()-start,timeout_seconds=600,memory_limit_bytes=8*1024**3)
    save(OUT/'children'/(name+'.json'),row)
    if success and p.returncode:
        raise RuntimeError(name+': '+stderr[-9000:]+stdout[-1000:])
    print(name, 'PASS' if not p.returncode else 'REJECTED', round(row['seconds'],2), 's', flush=True)
    return row

def instrument(relative, text):
    if relative not in ('c/memory.c','c/platform.c'):
        return text
    if relative=='c/memory.c':
        text=text.replace('uint8_t ugh_read(uint32_t a) {','uint8_t s7_model_read(uint32_t a) {')
        text=text.replace('void ugh_write(uint32_t a, uint8_t v) {','void s7_model_write(uint32_t a, uint8_t v) {')
    if relative=='c/platform.c':
        text=text.replace('void platform_out(uint16_t port,unsigned size,uint32_t value) {','void s7_model_out(uint16_t port,unsigned size,uint32_t value) {')
        text=text.replace('uint32_t platform_in(uint16_t port,unsigned size) {','uint32_t s7_model_in(uint16_t port,unsigned size) {')
        text=text.replace('int platform_interrupt(uint8_t n,Regs *r) {','int s7_model_interrupt(uint8_t n,Regs *r) {')
        text=text.replace('int platform_frame_boundary(Regs *r) {','int platform_frame_boundary(Regs *r) { s7_check();')
        text=text.replace('log_event(LOG_IRQ,(uint16_t)e->irq,0,e->clocks);',
                          'log_event(LOG_IRQ,(uint16_t)e->irq,0,e->clocks); s7_irq(e->irq,e->clocks,!!(r->flags&IF));')
        # Named opportunities only; no game callback in the backend.
        text=text.replace('Devices *d=&ugh_devices; (void)point;',
                          'Devices *d=&ugh_devices; s7_cut(point==SERVICE_RETRACE?GS_RETRACE_ACTIVE:point==SERVICE_TIMER_WAIT?GS_TIMER_OPPORTUNITY:GS_INPUT_OPPORTUNITY);')
        text=text.replace('wr16(0x40,0x1a,tail);return tail;',
                          'wr16(0x40,0x1a,tail);s7_flush(tail);return tail;')
    return '#include "s7_shadow.h"\n'+text

def compile_backend(source, output, name):
    pin=json.loads((ROOT/'tests/port/toolchain.json').read_text())['gcc']
    assert sha(GCC)==pin['sha256'],'pinned compiler changed'
    bounded([GCC,'-c','-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'port/test',
             '-MMD','-MF',output.with_suffix('.d'),source,'-o',output],name)
    deps=output.with_suffix('.d').read_text()
    assert not re.search(r'(?i)(?:[/\\]c[/\\]|native|s7_shadow|SDL|opl3)',deps),deps
    return dict(source=str(source),object_sha256=sha(output),dependencies=deps)

def build_edges(source=None, name='edges'):
    folder=OUT/name;folder.mkdir(parents=True,exist_ok=True)
    oracle=[]
    for n in ['platform','memory']:
        dest=folder/(n+'.c');dest.write_text(instrument('c/'+n+'.c',(ROOT/'c'/(n+'.c')).read_text()))
        oracle.append(dest)
    obj=folder/'backend.o'
    backend=compile_backend(source or ROOT/'port/test/backend.c',obj,name+'-backend')
    command=[GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',
             '-I',ROOT/'port','-I',ROOT/'c','-I',ROOT/'native','-I',ROOT/'tests/port',
             '-o',folder/'edges.exe',ROOT/'tests/port/s7_edges.c',ROOT/'tests/port/s7_shadow.c',
             *oracle,ROOT/'native/input.c',obj]
    bounded(command,name+'-compile')
    save(folder/'build.json',dict(backend=backend,command=list(map(str,command)),
         oracle_sources={str(p):sha(p) for p in oracle},compiler_sha256=sha(GCC)))
    return folder/'edges.exe'

def edge_tests():
    exe=build_edges()
    for name in ['video','input','files','clock']:
        bounded([exe,name],'edges-'+name)
    bounded([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'port',
             ROOT/'tests/port/s7_standalone.c',OUT/'edges/backend.o','-o',OUT/'standalone.exe'], 'standalone-link')
    bounded([OUT/'standalone.exe'],'standalone-run')
    save(OUT/'edges.json',dict(result='PASS',groups=['video','input','files','clock']))

def host_build_worker():
    import hostbuild
    if not (ROOT/'build/link/plain/UGH.EXE').exists():
        import build
        build.build_variant('plain')
    original=hostbuild.composition_source
    def composed(relative,text,units):
        return instrument(relative,original(relative,text,units))
    hostbuild.composition_source=composed
    # Hostbuild has no post-composition hook for host/*.c. Adapt its in-memory
    # function to stage those copies in this worker directory. No maintained
    # host, bridge, tool or generated c/ file is written.
    def host_sources(out):
        paths=[]
        for p in sorted((ROOT/'host').glob('*.c')):
            text=p.read_text()
            if p.name=='main.c':
                old='load_data(data); ugh_devices_reset(); scenario_fixture();'
                assert old in text
                text=text.replace(old,old+' s7_begin();')
                text=text.replace('SDL_Quit();','s7_finish(); SDL_Quit();')
            dest=out/'sources'/('host_'+p.name)
            dest.write_text('#include "s7_shadow.h"\n'+text);paths.append(dest)
        paths.append(ROOT/'tests/port/s7_shadow.c')
        obj=out/'backend.o';compile_backend(ROOT/'port/test/backend.c',obj,'host-backend')
        paths.append(obj)
        return paths
    hostbuild.host_sources=host_sources
    raw=inspect.getsource(hostbuild.build)
    raw=raw.replace("sources += sorted((ROOT/'host').glob('*.c'))",'sources += host_sources(out)')
    raw=raw.replace("'-I', str(ROOT/'c'),", "'-I', str(ROOT/'tests/port'), '-I', str(ROOT/'port'), '-I', str(ROOT/'native'), '-I', str(ROOT/'c'),")
    raw=raw.replace("'-Wall', '-Wextra', '-Werror',", "'-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation',")
    exec(compile(raw,'<s7 instrumented host build>','exec'),hostbuild.__dict__)
    hostbuild.build(out=OUT/'host',generate=False)

def host_streams():
    bounded([sys.executable,__file__,'--host-build-worker'],'host-build')
    paths=sorted((ROOT/'tests/scenarios').glob('*.txt'));assert len(paths)==20
    rows=[]
    for path in paths+[None]:
        name=path.stem if path else 'smoke'
        frames=next(int(s.split()[1]) for s in path.read_text().splitlines() if s.startswith('frames ')) if path else 256
        command=[OUT/'host/ugh.exe','--headless',str(frames),'--timeout','120']
        command+=['--script',path] if path else ['--smoke','256']
        row=bounded(command,'stream-'+name)
        counts=re.search(r'S7 STREAM (.*)',row['stderr']);assert counts,'no service witness: '+name
        counts={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',counts[1])};assert counts['requests']>0 and counts['boundaries']>0
        actual=[json.loads(s) for s in row['stdout'].splitlines()]
        if path:
            expected=json.loads((ROOT/'build/whole'/(name+'.ref.json')).read_text())['frames']
            assert actual==expected,'instrumented host changed reference: '+name
        else:
            assert len(actual)==256
        rows.append(dict(scenario=name,counts=counts,boundaries=len(actual),reference_equal=True,
                         request_source='actual composed host; synchronous dual consumption at platform and aperture cuts',
                         command_receipt='children/stream-'+name+'.json'))
    save(OUT/'streams.json',dict(result='PASS',scenarios=rows,
        comparison='Every reply and ordered effect for supported requests; complete planes/latches/controls/DAC/OPL/PIT/PIC/clocks/files/handles/video/exit at boundaries. Fixture scripts/cursors independently consumed. Pending capability probes and external vectors explicitly excluded.'))

def negative_tests():
    text=(ROOT/'port/test/backend.c').read_text()
    controls=[
        ('latch-refresh','video','b->latches[p]=b->planes[p][cell]','b->latches[p]=b->planes[p][cell^1u]'),
        ('inherited-mode','video','mode=b->gc[5]&3','mode=0'),
        ('water-store','video','store(ctx,cell,0x40)','store(ctx,cell,0)'),
        ('live-copy','video','GSStatus s=read_cell(ctx,src,GS_SOURCE_READ,v);',
         '''GSTestBackend *b=ctx;static uint8_t snapshot[4][65536];static int ready;
    if(!ready){memcpy(snapshot,b->planes,sizeof snapshot);ready=1;}
    uint8_t live[4];for(unsigned p=0;p<4;p++){live[p]=b->planes[p][src];b->planes[p][src]=snapshot[p][src];}
    GSStatus s=read_cell(ctx,src,GS_SOURCE_READ,v);
    for(unsigned p=0;p<4;p++)b->planes[p][src]=live[p];
    '''),
        ('partial-dac','video','b->dac_component=0;b->dac_index++','b->dac_component=1;b->dac_index++'),
        ('scan-break','input','*v=(uint8_t)n;effect(b,GST_SCAN','*v=(uint8_t)n&127;effect(b,GST_SCAN'),
        ('zero-limit','input','r->remaining=limit;','r->remaining=limit?limit:1;'),
        ('short-read-tail','files','if(n)memcpy(data,b->scores+pos,n);','if(count)memset(data,0,count);\n    if(n)memcpy(data,b->scores+pos,n);'),
        ('pit-phase','clock','b->pit_phase^=1;','b->pit_phase=0;'),
        ('opl-order','clock','b->opl[b->opl_index]=v','b->opl[(uint8_t)(b->opl_index+1)]=v'),
        ('event-timeline','clock','b->timer_tick++;','b->timer_tick+=2;'),
        ('seed-reply','clock','*r=b->seed;effect(b,GST_SEED','*r=b->seed;r->seconds^=1;effect(b,GST_SEED'),
        ('pending-success','clock','static GSStatus unsupported(void *ctx){(void)ctx;return GS_UNSUPPORTED;}','static GSStatus unsupported(void *ctx){(void)ctx;return GS_OK;}'),
    ]
    rows=[]
    for name,group,old,new in controls:
        assert text.count(old)==1,(name,text.count(old))
        folder=OUT/('defect-'+name);folder.mkdir(exist_ok=True)
        source=folder/'backend.c';source.write_text(text.replace(old,new))
        exe=build_edges(source,'defect-'+name)
        row=bounded([exe,group],'detect-'+name,success=False)
        assert row['returncode'] in [86,87] and ('MISMATCH' in row['stderr'] or 'EDGE FAIL' in row['stderr']),name
        rows.append(dict(defect=name,group=group,result='DETECTED',diagnostic=row['stderr'].splitlines()[-1],mutation=dict(old=old,new=new)))
    save(OUT/'negative.json',dict(result='PASS',controls=rows))

def finish():
    rows={name:json.loads((OUT/(name+'.json')).read_text()) for name in ['edges','streams','negative']}
    assert all(v['result']=='PASS' for v in rows.values())
    inputs=[ROOT/'port/services.h',*sorted((ROOT/'port/test').glob('*')),*sorted((ROOT/'tests/port').glob('s7_*')),Path(__file__)]
    save(OUT/'receipt.json',dict(result='PASS',scope='Step 7.2 deterministic backend; no native binding or byte-match promotion',
         evidence={name:sha(OUT/(name+'.json')) for name in rows},inputs={p.relative_to(ROOT).as_posix():sha(p) for p in inputs},
         model_inputs={p.relative_to(ROOT).as_posix():sha(p) for p in [ROOT/'c/platform.c',ROOT/'c/memory.c',ROOT/'native/input.c',*sorted((ROOT/'verif').glob('*_platform_model.inc'))]},
         scenarios=len(rows['streams']['scenarios']),detected_defects=len(rows['negative']['controls']),
         admission_inventory=json.loads((OUT/'admission.json').read_text()),
         groundwork=json.loads((OUT/'groundwork/unit.json').read_text())))

def admission_worker():
    import admission
    manifest=json.loads((ROOT/'metadata/admission.json').read_text())
    row=dict(manifest_sha256=sha(ROOT/'metadata/admission.json'),
             scope='Read-only D5 inventory check; no manifest/certificate relock')
    try:
        row.update(result='PASS',counts=admission.check(manifest))
    except ValueError as error:
        wanted=admission.assemble(manifest)
        row.update(result='BASELINE_DRIFT',diagnostic=str(error),manifest_counts=manifest['counts'],
                   current_inventory_counts=wanted['counts'],
                   changed_certificate_inputs=[k for k in wanted['certificate_inputs'] if wanted['certificate_inputs'][k]!=manifest['certificate_inputs'].get(k)])
        print('D5 inventory drift (unchanged source/manifest): '+str(error),flush=True)
    save(OUT/'admission.json',row)

def groundwork_worker():
    import port_services
    port_services.OUT=OUT/'groundwork'
    port_services.build()
    port_services.unit()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['all','edges','streams','negative','host-build-worker','admission-worker','groundwork-worker','finish']:
        p.add_argument('--'+name,action='store_true')
    a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if a.host_build_worker:host_build_worker();return
    if a.admission_worker:admission_worker();return
    if a.groundwork_worker:groundwork_worker();return
    if a.all:bounded([sys.executable,__file__,'--admission-worker'],'admission')
    if a.all:bounded([sys.executable,__file__,'--groundwork-worker'],'groundwork')
    if a.all or a.edges:edge_tests()
    if a.all or a.streams:host_streams()
    if a.all or a.negative:negative_tests()
    if a.all or a.finish:finish()
if __name__=='__main__':main()
