"""Small shared closure harness toolkit; no component algorithms live here.

Builds real C together, extracts maintained functions, runs the CBMC shim recipe,
and records commands, source/tool hashes and wall times. Receipts are evidence
records, not cache keys or automatic status promotions.
"""
import hashlib,json,os,re,subprocess,time
from pathlib import Path
from windows_job import WindowsJob

ROOT=Path(__file__).resolve().parents[1]
GCC=Path('C:/msys64/mingw64/bin/gcc.exe')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def hashes(paths):
    return {p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p):digest(p)
            for p in sorted({Path(p).resolve() for p in paths})}

def receipt(command,inputs,**result):
    return dict(command=list(map(str,command)),inputs=hashes([*inputs,Path(__file__)]),**result)

def save(path,result):
    Path(path).write_text(json.dumps(result,indent=2)+'\n')
    return result

def checked_compile(command):
    """Also used by the ICE pilot, preserving its exact compiler options."""
    env=dict(os.environ,PATH=str(GCC.parent)+os.pathsep+os.environ.get('PATH',''))
    p=subprocess.run(command,capture_output=True,text=True,env=env)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    return p

def compile_c(sources,output,includes=(),options=()):
    command=[str(GCC),'-O2','-std=c11','-Wall','-Wextra','-Werror','-fwrapv',
             *map(str,options),*[f'-I{p}' for p in includes],'-o',str(output),*map(str,sources)]
    checked_compile(command)
    return receipt(command,sources,compiler_sha256=digest(GCC))

def function(source,name):
    """Copy one actual function verbatim, failing if its spelling disappears.

    Braces in comments/strings are masked before finding the closing brace.
    No algorithm rewrite, loop bound, or manual model is introduced.
    """
    masked=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',
                  lambda m:' '*len(m[0]),source,flags=re.S)
    match=re.search(r'^[^\n;{}]*\b'+re.escape(name)+r'\s*\([^;{}]*\)\s*\{',masked,re.M)
    if not match: raise ValueError('function not found: '+name)
    depth=1; end=match.end()
    while depth:
        if masked[end]=='{':depth+=1
        elif masked[end]=='}':depth-=1
        end+=1
    return source[match.start():end]+'\n'

def run_solver(command,folder,timeout):
    """Shared by the pilot and new harnesses; preserves caller command options."""
    folder=Path(folder);start=time.perf_counter()
    with WindowsJob() as job,(folder/'cbmc.log').open('w') as log:
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);job.assign(process)
        try:code=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:job.terminate();process.wait();code=None
    return code,time.perf_counter()-start,(folder/'cbmc.log').read_text()

def cbmc(harness,folder,inputs,unwind=24,timeout=120,defines=(),extra=()):
    """Run actual C using the pinned tool and minimal system-header shim.

    Bounds/pointer/overflow and unwinding assertions stay enabled. A timeout
    kills the complete owned process tree. Callers inspect result explicitly.
    """
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'metadata/verif-tools.json').read_text())
    tool=Path(manifest['cbmc']['exe'])
    if digest(tool)!=manifest['cbmc']['exe_sha256']:raise RuntimeError('CBMC hash drift')
    preprocessed=folder/'harness.i'
    preprocess=[str(GCC),'-E','-P','-nostdinc','-U_WIN32',f'-I{ROOT/"c"}',
                f'-I{ROOT/"verif/cbmc_shim"}',f'-I{ROOT/"native"}',*defines,str(harness),'-o',str(preprocessed)]
    checked_compile(preprocess)
    command=[str(tool),str(preprocessed),'--unwind',str(unwind),'--unwinding-assertions',
             '--bounds-check','--pointer-check','--signed-overflow-check',
             '--slice-formula','--trace',*extra]
    code,elapsed,log=run_solver(command,folder,timeout)
    result=receipt(command,[*inputs,harness,ROOT/'metadata/verif-tools.json',
                           ROOT/'verif/windows_job.py',*sorted((ROOT/'verif/cbmc_shim').glob('*.h'))],
        preprocess=preprocess,compiler_sha256=digest(GCC),tools=manifest,
        preprocessed_sha256=digest(preprocessed),unwind=unwind,seconds=elapsed,
        result='TIMEOUT' if code is None else 'PASS' if code==0 and 'VERIFICATION SUCCESSFUL' in log else 'FAIL' if code==10 else 'ERROR',
        returncode=code,failures=re.findall(r'^\[([^]]+)\] (.*): FAILURE$',log,re.M),
        solver_times=re.findall(r'Runtime (?:Solver|decision procedure): ([^\n]+)',log))
    save(folder/'result.json',result)
    return result
