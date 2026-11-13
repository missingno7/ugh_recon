"""Local CBMC resource envelope; shared tooling is read-only."""
import ctypes as C,subprocess,time
from pathlib import Path
import closure_support as support
from windows_job import WindowsJob,ExtendedLimits

MEMORY_BYTES=8_000_000_000
LAST_PEAK=0
def limited_solver(command,folder,timeout):
    global LAST_PEAK
    assert 0<timeout<=600
    start=time.perf_counter()
    with WindowsJob() as job,(Path(folder)/'cbmc.log').open('w') as log:
        limits=ExtendedLimits();limits.basic.flags=0x2000|0x200;limits.job_memory=MEMORY_BYTES
        if not job.kernel.SetInformationJobObject(job.handle,9,C.byref(limits),C.sizeof(limits)):
            raise C.WinError(C.get_last_error())
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,creationflags=0x4)
        job.assign(process)
        native=C.WinDLL('ntdll');native.NtResumeProcess.argtypes=[C.c_void_p];native.NtResumeProcess.restype=C.c_long
        status=native.NtResumeProcess(C.c_void_p(int(process._handle)))
        if status:job.terminate();process.wait();raise RuntimeError(f'NtResumeProcess:{status}')
        try:code=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:job.terminate();process.wait();code=None
        actual=ExtendedLimits();job.kernel.QueryInformationJobObject.argtypes=[C.c_void_p,C.c_int,C.c_void_p,C.c_ulong,C.c_void_p]
        if not job.kernel.QueryInformationJobObject(job.handle,9,C.byref(actual),C.sizeof(actual),None):raise C.WinError(C.get_last_error())
        LAST_PEAK=int(actual.peak_job_memory)
    return code,time.perf_counter()-start,(Path(folder)/'cbmc.log').read_text()

def cbmc(harness,folder,inputs,**options):
    assert 0<options.get('timeout',120)<=600
    previous=support.run_solver;support.run_solver=limited_solver
    try:result=support.cbmc(harness,folder,[*inputs,Path(__file__)],**options)
    finally:support.run_solver=previous
    result['resource_limits']=dict(job_memory_bytes=MEMORY_BYTES,peak_job_memory_bytes=LAST_PEAK,seconds=options.get('timeout',120),scope='CBMC and all descendant solver processes together; suspended launch before job assignment')
    support.save(Path(folder)/'result.json',result);return result
