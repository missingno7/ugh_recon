"""Run a pinned DOS tool under the MS-DOS Player with a bounded environment."""
import os, subprocess
from common import TOOLS, load_json, sha256

RUNNER = TOOLS / 'nmlgcdos' / 'msdos.exe'


def tool_path(name):
    """Path of a tool named in metadata/toolchain-lock.json, hash checked."""
    entry = load_json('toolchain-lock.json')['tools'][name]
    path = TOOLS / entry['path']
    if sha256(path.read_bytes()) != entry['sha256']:
        raise RuntimeError(f'{name}: {path} does not match the locked hash')
    return path


def dos(name, args, cwd, timeout=300, env_extra=None):
    """Run tool `name` in `cwd`; return its console text. Raises on a non-zero exit."""
    env = {k: v for k, v in os.environ.items()
           if k.upper() in ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'COMSPEC')}
    env.update(env_extra or {})
    p = subprocess.run([str(RUNNER), str(tool_path(name)), *args], cwd=cwd, env=env,
                       capture_output=True, timeout=timeout)
    text = (p.stdout + p.stderr).decode('cp437', errors='replace').replace('\r', '')
    if p.returncode:
        raise RuntimeError(f'{name} exit {p.returncode}\n{text}')
    return text
