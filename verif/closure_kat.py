"""Small negative controls for the closure checker, in an isolated scratch tree."""
import importlib.util,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));import closure

def main():
    scratch=ROOT/'build/workers/pilot-ice/closure-kat'
    (scratch/'metadata/closure').mkdir(parents=True,exist_ok=True)
    for source in (ROOT/'native').rglob('*'):
        if source.is_file():
            dest=scratch/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    shutil.copyfile(ROOT/'metadata/closure/ice.json',scratch/'metadata/closure/ice.json')
    closure.ROOT=scratch
    assert not closure.validate()[1]
    source=scratch/'native/ice.c';original=source.read_text();rows=[]
    for name,changed in [
        ('machine_identifier',original+'\nRegs *forbidden_state;\n'),
        ('original_code_literal',original+'\nunsigned forbidden_code = 0x4CAD;\n'),
        ('undeclared_call',original.replace('*result=(IceResult)', 'unlisted_function(); *result=(IceResult)')),
        ('undeclared_include','#include <stdio.h>\n'+original)]:
        source.write_text(changed);errors=closure.validate()[1];assert errors,name
        rows.append(dict(case=name,detected=True,errors=errors));source.write_text(original)
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
