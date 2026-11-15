"""Isolated bounded children and deterministic parallel stage receipts.

Timing/raw commands are diagnostics; semantic receipts exclude scheduling and
wall time. Children are created suspended, assigned to their own8-GiB Windows
Job, then resumed. Closing the Job kills its entire tree on every exit path.
"""
import ctypes as C,json,os,subprocess,time,concurrent.futures
from pathlib import Path
from windows_job import WindowsJob,ExtendedLimits
MEMORY=8*1024**3

def save(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf-8')

def run(command,cwd,output,tag,env=None,timeout=600,allowed=(0,)):
 if timeout>600:raise ValueError('child wall bound exceeds600s')
 command=list(map(str,command));cwd=Path(cwd);output=Path(output);start=time.perf_counter()
 with WindowsJob() as job:
  limits=ExtendedLimits();limits.basic.flags=0x2000|0x100|0x200;limits.process_memory=limits.job_memory=MEMORY
  if not job.kernel.SetInformationJobObject(job.handle,9,C.byref(limits),C.sizeof(limits)):raise C.WinError(C.get_last_error())
  process=subprocess.Popen(command,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,creationflags=4)
  job.assign(process);resume=C.WinDLL('ntdll').NtResumeProcess;resume.argtypes=[C.c_void_p];resume.restype=C.c_long
  if resume(int(process._handle))!=0:job.terminate();process.wait();raise RuntimeError('cannot resume '+tag)
  timed_out=False
  try:stdout,stderr=process.communicate(timeout=timeout)
  except subprocess.TimeoutExpired:
   timed_out=True;job.terminate();stdout,stderr=process.communicate()
 row=dict(command=command,cwd=str(cwd),stdout=stdout,stderr=stderr,returncode=process.returncode,timed_out=timed_out,seconds=time.perf_counter()-start,timeout_seconds=timeout,memory_limit_bytes=MEMORY)
 save(output/'diagnostics'/(tag+'.json'),row)
 if timed_out or process.returncode not in allowed:raise RuntimeError(tag+': '+stdout[-3000:]+stderr[-5000:])
 return row

def pool(tasks,jobs=3):
 if jobs<1 or jobs>6:raise ValueError('pool must have1..6 jobs (8GiB each)')
 results={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
  futures={executor.submit(fn):name for name,fn in tasks}
  try:
   for future in concurrent.futures.as_completed(futures):results[futures[future]]=future.result()
  except BaseException:
   for future in futures:future.cancel()
   raise
 return {name:results[name] for name,fn in tasks}
