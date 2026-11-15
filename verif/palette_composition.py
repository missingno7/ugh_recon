"""Compatibility name; common execution lives in verif/world_gate.py."""
import sys
from world_cases import legacy_palette as _cases
if __name__=='__main__':
 from world_gate import main
 main(default_world='palette_world')
else:
 sys.modules[__name__]=_cases
