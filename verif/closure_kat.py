"""Small negative controls for the closure checker, in an isolated scratch tree."""
import importlib.util,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));import closure

def main():
    scratch=ROOT/'build/native/closure-kat'
    (scratch/'metadata/closure').mkdir(parents=True,exist_ok=True)
    for source in (ROOT/'native').rglob('*'):
        if source.is_file():
            dest=scratch/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    for cert in (ROOT/'metadata/closure').glob('*.json'):
        shutil.copyfile(cert,scratch/'metadata/closure'/cert.name)
        for name in json.loads(cert.read_text()).get('verification_inputs',{}):
            dest=scratch/name;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/name,dest)
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
    source=scratch/'native/far_copy.c'
    if source.exists():
        original=source.read_text();source.write_bytes(original.replace('\r\n','\n').replace('\n','\r\n').encode())
        assert not closure.validate()[1]
        rows.append(dict(case='checkout_crlf',accepted=True));source.write_text(original)
        source.write_text(original+'\n/* benign source change */\n')
        errors=closure.validate()[1];assert any('stale verification input native/far_copy.c' in e for e in errors)
        rows.append(dict(case='stale_verification_input',detected=True,errors=errors));source.write_text(original)
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
