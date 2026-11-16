"""Legacy compiler-flag adapter for player-world case operators.

The stale-after-stone mutation now targets the live physics projection directly
in player_world_cases.py, so no source rewrite is needed here.
"""
def source(text):
 return text

def install(adapter):adapter.SOURCE_ADAPTERS['player_world_cases']=source
