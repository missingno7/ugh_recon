"""Own a Windows process tree so timed-out external solvers cannot survive it."""
import ctypes as C
from ctypes import wintypes as W

class BasicLimits(C.Structure):
    _fields_=[('process_time',C.c_int64),('job_time',C.c_int64),('flags',W.DWORD),
              ('min_working_set',C.c_size_t),('max_working_set',C.c_size_t),
              ('active_processes',W.DWORD),('affinity',C.c_size_t),
              ('priority',W.DWORD),('scheduling',W.DWORD)]
class IoCounters(C.Structure):
    _fields_=[(name,C.c_uint64) for name in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
class ExtendedLimits(C.Structure):
    _fields_=[('basic',BasicLimits),('io',IoCounters),('process_memory',C.c_size_t),
              ('job_memory',C.c_size_t),('peak_process_memory',C.c_size_t),('peak_job_memory',C.c_size_t)]

class WindowsJob:
    def __enter__(self):
        self.kernel=C.WinDLL('kernel32',use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes=[C.c_void_p,W.LPCWSTR];self.kernel.CreateJobObjectW.restype=W.HANDLE
        self.kernel.SetInformationJobObject.argtypes=[W.HANDLE,C.c_int,C.c_void_p,W.DWORD]
        self.kernel.AssignProcessToJobObject.argtypes=[W.HANDLE,W.HANDLE]
        self.kernel.TerminateJobObject.argtypes=[W.HANDLE,W.UINT]
        self.kernel.CloseHandle.argtypes=[W.HANDLE]
        self.handle=self.kernel.CreateJobObjectW(None,None)
        if not self.handle:raise C.WinError(C.get_last_error())
        limits=ExtendedLimits();limits.basic.flags=0x2000 # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(self.handle,9,C.byref(limits),C.sizeof(limits)):
            self.kernel.CloseHandle(self.handle);raise C.WinError(C.get_last_error())
        return self
    def assign(self,process):
        if not self.kernel.AssignProcessToJobObject(self.handle,W.HANDLE(int(process._handle))):
            process.kill();process.wait();raise C.WinError(C.get_last_error())
    def terminate(self):
        if not self.kernel.TerminateJobObject(self.handle,1):raise C.WinError(C.get_last_error())
    def __exit__(self,*args):self.kernel.CloseHandle(self.handle)
