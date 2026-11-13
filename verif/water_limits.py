"""Water passenger solver owner: <=600 seconds and <=8 GiB job-private peak.

The job-private limit is conservative: CBMC and any child SMT solver together
must fit, hence no individual process can exceed the per-run cap unnoticed.
Only this worker's job is sampled or terminated. Shared historically locked
closure_support/windows_job implementations remain unchanged.
"""
import ctypes as C,json,subprocess,time,os,shutil
from datetime import datetime,timezone
from pathlib import Path
import closure_support as support
from windows_job import WindowsJob,ExtendedLimits

Z3=Path('C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe')
SMT=['--smt2','--z3','--external-smt2-solver',str(Z3)]

class SolverPermit:
    """Two abandoned-safe Windows mutex slots, shared by this worker's CLIs."""
    def __enter__(self):
        self.kernel=C.WinDLL('kernel32',use_last_error=True)
        self.kernel.CreateMutexW.argtypes=[C.c_void_p,C.c_int,C.c_wchar_p];self.kernel.CreateMutexW.restype=C.c_void_p
        self.kernel.WaitForMultipleObjects.argtypes=[C.c_uint32,C.POINTER(C.c_void_p),C.c_int,C.c_uint32]
        self.kernel.ReleaseMutex.argtypes=[C.c_void_p];self.kernel.CloseHandle.argtypes=[C.c_void_p]
        self.handles=(C.c_void_p*2)(*[self.kernel.CreateMutexW(None,0,'Local\\ugh_recon.close_stones_5.cbmc.'+str(i)) for i in range(2)])
        if not all(self.handles):raise C.WinError(C.get_last_error())
        while True:
            result=self.kernel.WaitForMultipleObjects(2,self.handles,0,50)
            if result in (0,1,128,129):self.index=result%128;return self
            if result!=258:raise C.WinError(C.get_last_error())
    def __exit__(self,*args):
        self.kernel.ReleaseMutex(self.handles[self.index])
        for handle in self.handles:self.kernel.CloseHandle(handle)

def cbmc(harness,folder,inputs,*,memory_mib=8192,timeout=120,**kwargs):
    if not 0<memory_mib<=8192 or not 0<timeout<=600:raise ValueError('worker resource cap')
    stats=dict(memory_limit_bytes=memory_mib*1024*1024,peak_private_bytes=0,termination_reason=None)
    tracked=[*inputs,Path(__file__),Z3,Path(harness),Path(support.__file__)]
    initial_inputs=support.hashes(tracked)
    def owned(command,directory,seconds):
        start=time.perf_counter();directory=Path(directory)
        with WindowsJob() as job,(directory/'cbmc.log').open('w') as log:
            limits=ExtendedLimits();limits.basic.flags=0x2000|0x100|0x200
            limits.process_memory=limits.job_memory=8192*1024*1024
            if not job.kernel.SetInformationJobObject(job.handle,9,C.byref(limits),C.sizeof(limits)):raise C.WinError(C.get_last_error())
            stats['hard_private_limit_bytes']=limits.job_memory
            job.kernel.QueryInformationJobObject.argtypes=[C.c_void_p,C.c_int,C.c_void_p,C.c_uint32,C.c_void_p]
            def sample():
                limits=ExtendedLimits()
                if not job.kernel.QueryInformationJobObject(job.handle,9,C.byref(limits),C.sizeof(limits),None):raise C.WinError(C.get_last_error())
                stats['peak_private_bytes']=max(stats['peak_private_bytes'],limits.peak_job_memory)
            process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);job.assign(process)
            while True:
                try:code=process.wait(timeout=0.05)
                except subprocess.TimeoutExpired:code=None
                sample()
                if stats['peak_private_bytes']>stats['memory_limit_bytes']:
                    stats['termination_reason']='MEMORY_CAP'
                    if process.poll() is None:job.terminate();process.wait()
                    code=1;break
                if code is not None:break
                if time.perf_counter()-start>=seconds:
                    stats['termination_reason']='TIMEOUT';job.terminate();process.wait();code=None;break
        return code,time.perf_counter()-start,(directory/'cbmc.log').read_text()
    def run(command,directory,seconds):
        queued=time.perf_counter()
        with SolverPermit() as permit:
            stats.update(permit_slot=permit.index,queued_seconds=time.perf_counter()-queued,started_utc=datetime.now(timezone.utc).isoformat())
            answer=owned(command,directory,seconds)
            stats['finished_utc']=datetime.now(timezone.utc).isoformat()
            return answer
    prior=support.run_solver
    try:
        support.run_solver=run
        result=support.cbmc(harness,folder,[*inputs,Path(__file__),Z3],timeout=timeout,**kwargs)
    finally:support.run_solver=prior
    result.update(stats)
    current_inputs=support.hashes(tracked)
    if current_inputs!=initial_inputs:
        result['result']='INPUT_CHANGED';result['changed_inputs']=[n for n in initial_inputs if initial_inputs[n]!=current_inputs[n]]
    if result['result']=='ERROR' and any(s in (Path(folder)/'cbmc.log').read_text().lower() for s in ['bad_alloc','out of memory','memory limit']):
        result['result']='MEMORY_CAP';result['termination_reason']='MEMORY_CAP'
    if stats['termination_reason']:result['result']=stats['termination_reason']
    result['smt_solver_sha256']=support.digest(Z3)
    support.save(Path(folder)/'result.json',result)
    if result['result']!='PASS':
        from water_build import OUT
        archive=OUT/'negative'/(str(time.time_ns())+'-'+str(os.getpid())+'-'+result['result']);archive.mkdir(parents=True)
        for name in ['harness.c','pair.inc','harness.i','cbmc.log']:
            source=Path(folder)/name
            if source.is_file():shutil.copyfile(source,archive/name)
        support.save(archive/'result.json',dict(result,source_output_folder=str(Path(folder).relative_to(OUT))))
    return result

if __name__=='__main__':
    from water_build import OUT
    folder=OUT/'cap-control';folder.mkdir(parents=True,exist_ok=True);source=folder/'harness.c'
    source.write_text('int main(void) { unsigned x; __CPROVER_assert(x+1!=x,"cap-control"); return 0;}\n')
    result=cbmc(source,folder,[source],unwind=1,timeout=30,memory_mib=1)
    print(json.dumps({k:result[k] for k in ['result','peak_private_bytes','seconds']}));assert result['result']=='MEMORY_CAP'
