"""Compatibility name; common execution lives in verif/world_gate.py."""
import sys
from world_cases import legacy_platform as _cases
if __name__=='__main__':
 from world_gate import main
 main(default_world='platform_world')
else:
 sys.modules[__name__]=_cases
