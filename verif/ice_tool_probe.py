"""Record tool availability and failed acquisition without changing C:/tools."""
import hashlib,importlib.util,json,os,shutil,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/pilot-ice'

def main():
    OUT.mkdir(parents=True,exist_ok=True);rows=[]
    commands=[
        [sys.executable,'-c',"import z3; print(z3.get_version_string())"],
        [sys.executable,'-m','pip','--isolated','download','--no-deps','--retries','0','--timeout','3',
         '--dest',str(OUT/'tool-download'),'--index-url','https://pypi.org/simple','z3-solver'],
        ['wsl.exe','--list','--quiet']]
    for cmd in commands:
        start=time.perf_counter()
        try:
            p=subprocess.run(cmd,capture_output=True,timeout=20)
            def decode(b):return b.decode('utf-16-le' if b'\x00' in b else 'utf-8',errors='replace')
            rows.append(dict(command=cmd,returncode=p.returncode,stdout=decode(p.stdout),stderr=decode(p.stderr),seconds=time.perf_counter()-start))
        except Exception as e:rows.append(dict(command=cmd,error=str(e),seconds=time.perf_counter()-start))
    url='https://api.github.com/repos/diffblue/cbmc/releases/latest'
    try:
        response=urllib.request.urlopen(url,timeout=3)
        acquisition=dict(url=url,result='reachable',body=response.read(1024).decode())
    except Exception as e:acquisition=dict(url=url,result='failed',error=str(e))
    result=dict(commands=rows,cbmc=dict(path=shutil.which('cbmc'),acquisition=acquisition,
                source_url='https://github.com/diffblue/cbmc/releases'),
                klee=dict(path=shutil.which('klee'),result='not attempted in WSL: enumeration denied; building LLVM/KLEE is not cheap',
                          source_url='https://klee-se.org/getting-started/'),
                chosen='Ghidra bundled libz3.dll via Python ctypes, see smt.json',
                constraint='C:/tools is read-only under the active filesystem policy; all extracted tools and downloads target the worker directory')
    (OUT/'tool-probe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
