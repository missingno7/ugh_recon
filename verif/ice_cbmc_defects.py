"""Repeat the pilot's five actual-C mutants with CBMC (no model mutations)."""
import json
from pathlib import Path
import ice_cbmc
ROOT=ice_cbmc.ROOT;OUT=ice_cbmc.OUT
REPLACEMENTS={
    'rare_length':('return bases[kind]+take_bits(reader,widths[kind]);','return bases[kind]+take_bits(reader,widths[kind])+(kind==4);','length'),
    'refill_carry':('((byte << 1) | bit)','(byte << 1)','reader'),
    'cursor_wrap':('return (index + 65535u) & 65535u;','return index ? index-1 : 0;','reader'),
    'signed_literal_boundary':('minus_one > 32768','minus_one >= 32768','literal'),
    'offset_bit_order':('return take_bits(reader,wide ? 9 : 6)+(wide ? 65 : 1);','unsigned v=take_bits(reader,wide ? 9 : 6); if(wide) v=((v & 1u)<<8) | (v>>1); return v+(wide ? 65 : 1);','offset')}

def main():
    original=(ROOT/'native/ice.c').read_text();OUT.mkdir(parents=True,exist_ok=True);rows={}
    for name,(old,new,mode) in REPLACEMENTS.items():
        assert original.count(old)==1
        path=OUT/f'mutant_{name}.c';path.write_text(original.replace(old,new))
        primitive=ice_cbmc.run(8,1,17,60,path,'mutant_'+name,'sat',mode)
        whole=ice_cbmc.run(16,2,17,90,path,'mutant_'+name,'sat','whole')
        rows[name]=dict(primitive=primitive,whole=whole)
    (OUT/'defects.json').write_text(json.dumps(rows,indent=2)+'\n')
    print({k:(v['primitive']['result'],v['whole']['result']) for k,v in rows.items()})
    # FAIL means a counterexample, not a harness/frontend/unwind failure. The
    # individual logs must be checked for the failed observation/assertion.
    return int(any(r['primitive']['result']!='FAIL' for r in rows.values()))
if __name__=='__main__':raise SystemExit(main())
