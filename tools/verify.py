"""Fresh build, expanded diagnostics, then the packed-file acceptance gate.

Exit zero means pinned PKLITE produced exactly the locked original. Lesser
levels are diagnostics, never promoted to byte-exact program proof.
"""
import json, shutil, sys
from collections import Counter
from common import ROOT, BUILD, PACKED, MZ, sha256, load_json
from build import build, WORK
from dos import dos

def ranges(positions):
    out=[]
    for p in positions:
        if out and p==out[-1][1]:out[-1][1]=p+1
        else:out.append([p,p+1])
    return out

def compare(want, got):
    fields={k:{'want':v,'got':got.hdr[k]} for k,v in want.hdr.items() if v!=got.hdr[k]}
    ri=[{'index':i,'want':a,'got':b} for i,(a,b) in enumerate(zip(want.relocs,got.relocs)) if a!=b]
    for i in range(min(len(want.relocs),len(got.relocs)),max(len(want.relocs),len(got.relocs))):
        ri.append({'index':i,'want':want.relocs[i] if i<len(want.relocs) else None,'got':got.relocs[i] if i<len(got.relocs) else None})
    diffs=[i for i,(a,b) in enumerate(zip(want.image,got.image)) if a!=b]
    diffs+=list(range(min(len(want.image),len(got.image)),max(len(want.image),len(got.image))))
    regions=load_json('regions.json')['regions'];per=[]
    for i,r in enumerate(regions):
        start=int(r['frame'],16)*16
        end=int(regions[i+1]['frame'],16)*16 if i+1<len(regions) else max(len(want.image),len(got.image))
        ds=[p for p in diffs if start<=p<end]
        per.append({'name':r['name'],'frame':r['frame'],'class':r['class'],'differing_bytes':len(ds),
                    'ranges':ranges(ds),'first_differences':[{'image':p,'want':want.image[p] if p<len(want.image) else None,'got':got.image[p] if p<len(got.image) else None} for p in ds[:8]]})
    return {'header_fields':fields,'header_gap_equal':want.header_gap==got.header_gap,
            'header_padding_equal':want.header_pad==got.header_pad,'tail_equal':want.tail==got.tail,
            'relocations_in_order_equal':want.relocs==got.relocs,
            'relocation_set_equal':set(want.sites)==set(got.sites),
            'relocation_tuple_set_equal':set(want.relocs)==set(got.relocs),
            'relocation_multiset_equal':Counter(want.sites)==Counter(got.sites),
            'relocation_differences':ri,
            'missing_relocation_sites':sorted((Counter(want.sites)-Counter(got.sites)).elements()),
            'extra_relocation_sites':sorted((Counter(got.sites)-Counter(want.sites)).elements()),
            'image_size':{'want':len(want.image),'got':len(got.image)},
            'image_equal':want.image==got.image,'image_differing_bytes':len(diffs),
            'image_difference_ranges':ranges(diffs),'regions':per,
            'expanded_file_equal':want.data==got.data}

def byte_classes():
    """Disjoint load-image accounting; RAW is debt even with a known owner."""
    doc=load_json('asm-map.json')
    asm={kind:sum(s['end']-s['start'] for m in doc['modules'] for s in m['spans'] if s['kind']==kind)
         for kind in ('code','data','padding')}
    classes={'ASM_code':asm['code'],'C_code':7030,
             'runtime_library_code':0x13b8,'runtime_library_data':145+(0x7e2e-0x7b7c)-1,
             'compiler_switch_tables':44,'C_initialized_data':4,
             'RAW_assembly_owned_data':asm['data'],
             'RAW_far_banks_and_game_DGROUP':64768+(0x5c09-0x1a38)*16+(0x7b7c-0x92),
             'assembler_and_linker_padding':asm['padding']+1+15+12+1+1,'UNKNOWN_file_bytes':0}
    return {'classes':classes,'load_image_total':sum(classes.values()),
            'RAW_data_debt':classes['RAW_assembly_owned_data']+classes['RAW_far_banks_and_game_DGROUP'],
            'RAW_virtual_reservation_debt':128,
            'note':'Instruction extents use asm-map, superseding the old paragraph census. '
                   'All copied opaque data is RAW debt, including data with an assembly owner. '
                   'The trailing reserve reproduces allocation only; its historical owner/use are unknown.'}

def main():
    lock=load_json('oracle.json'); original=PACKED.read_bytes()
    oracle=(BUILD/'oracle/UGH_X.EXE').read_bytes()
    if sha256(original)!=lock['packed']['file_sha256'] or sha256(oracle)!=lock['expanded']['file_sha256']:
        raise ValueError('oracle hash mismatch; run python tools/oracle.py')
    exe=build();got=MZ(exe.read_bytes());want=MZ(oracle)
    r=compare(want,got)
    packed=WORK/'PACKED.EXE';shutil.copyfile(exe,packed)
    (WORK/'PKLITE.log').write_text(dos('PKLITE',[packed.name],WORK))
    r['packed_equal']=packed.read_bytes()==original
    r['packed_sha256']=sha256(packed.read_bytes())
    candidate=packed.read_bytes()
    packed_diffs=[i for i,(a,b) in enumerate(zip(original,candidate)) if a!=b]
    packed_diffs+=list(range(min(len(original),len(candidate)),max(len(original),len(candidate))))
    r['packed_size']={'want':len(original),'got':len(candidate)}
    r['packed_differing_bytes']=len(packed_diffs)
    r['packed_difference_ranges']=ranges(packed_diffs)
    r['byte_accounting']=byte_classes()
    if r['byte_accounting']['load_image_total']!=len(want.image):raise ValueError('byte accounting incomplete')
    def contribution(a,b):
        return (got.image[a:b]==want.image[a:b] and
                Counter(s for s in got.sites if a<=s<b)==Counter(s for s in want.sites if a<=s<b))
    r['contribution_matches']={m['name']:contribution(m['frame']*16+m['start'],m['frame']*16+m['end'])
                               for m in load_json('asm-map.json')['modules']}
    r['contribution_matches']['C_TU']=contribution(0x8783,0xa325) and contribution(0x1a370,0x1a374)
    r['contribution_matches']['runtime']=all(contribution(a,b) for a,b in
         [(0,0x13b8),(0x5c090,0x5c121),(0x63c0c,0x63ebe)])
    r['proof_level']=('FULL_PACKED_FILE' if r['packed_equal'] else
                      'EXPANDED_FILE_DIAGNOSTIC' if r['expanded_file_equal'] else
                      'IMAGE_AND_RELOCATION_SET_DIAGNOSTIC' if r['image_equal'] and r['relocation_multiset_equal'] else
                      'NATURAL_LINK_DIAGNOSTIC')
    print('proof level:',r['proof_level'])
    print('header field differences:',r['header_fields'])
    print('header gap/padding equal:',r['header_gap_equal'],r['header_padding_equal'])
    print('relocations: ordered',r['relocations_in_order_equal'],'set',r['relocation_set_equal'],
          'multiset',r['relocation_multiset_equal'],'different positions',len(r['relocation_differences']))
    if r['relocation_differences']:print('  first positions:',r['relocation_differences'][:8])
    print('image:',len(got.image),'bytes;',r['image_differing_bytes'],'different bytes')
    for region in r['regions']:
        if region['differing_bytes']:print(' ',region['frame'],region['name'],region['differing_bytes'],region['first_differences'][:4])
    print('expanded file equal:',r['expanded_file_equal'],'packed file equal:',r['packed_equal'])
    print('packed:',r['packed_size'],'different bytes:',len(packed_diffs),
          'first difference:',f'{packed_diffs[0]:06X}' if packed_diffs else 'none')
    print('byte classes:',r['byte_accounting']['classes'])
    print('exact contributions (bytes + relocation multiset):',r['contribution_matches'])
    print('RAW data debt:',r['byte_accounting']['RAW_data_debt'],'file bytes; virtual reserve:',
          r['byte_accounting']['RAW_virtual_reservation_debt'],'bytes (owner/use unknown)')
    (WORK/'verify.json').write_text(json.dumps(r,indent=2)+'\n')
    return 0 if r['packed_equal'] else 1

if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,RuntimeError,OSError) as e:
        WORK.mkdir(parents=True,exist_ok=True)
        (WORK/'verify.json').write_text(json.dumps({'proof_level':'BUILD_OR_VALIDATION_FAILURE','error':str(e)},indent=2)+'\n')
        print('proof level: BUILD_OR_VALIDATION_FAILURE\n'+str(e));sys.exit(2)
