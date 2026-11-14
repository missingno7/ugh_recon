"""Named readers/writers, callers, IRQ boundaries, shipped palette and Amiga meaning."""
import sys,json,hashlib
from pathlib import Path
from closure_support import ROOT,receipt,save
from video_dos_build import OUT,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest
contacts_reference.OUT=OUT/'reference'

def main():
    plain=contacts_reference.prepare_reference(local=True);model=json.loads((ROOT/'metadata/program-model.json').read_text());rows=[];m=difftest.Machine()
    for name in NAMES:
        full='GAME:'+name;address=model['routines'][full]['address']
        callers=sorted({owner for site in model['sites'].values() if not site.get('indirect') and [address,'call'] in site.get('edges',[]) for owner in site.get('owners',[])})
        indirect=[k for k,v in model['indirect_sites'].items() if address in v.get('targets',[])]
        rows.append(dict(name=full,address=address,static_callers=callers,indirect_sites=indirect))
    fields=['DrawPagePointer','BackgroundPagePointer','DisplayedVgaPagePointer','FixedVgaPagePointer','PlayfieldHeight','VgaPlaneCopyByteCount','BasePalettePointer','FadedPalettePointer']
    owners={field:model['variables'][field] for field in fields}
    palette=m.read(m.rw('DGROUP:PaletteSourcePointer',2),m.rw('DGROUP:PaletteSourcePointer'),768)
    amiga=None;path=ROOT/'build/amiga/files/t'
    if path.exists():
        from amiga import Hunk
        import capstone
        raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()=='6826d1f7438e856367d2f78a6b546189517d1255e0f0ca526949d14e214355e7';code=bytes(Hunk(raw).hunks[0]['data'])
        decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
        amiga=dict(hash=hashlib.sha256(raw).hexdigest(),range='h0:03A40..03A62',instructions=[dict(offset=f'{i.address:05x}',mnemonic=i.mnemonic,operands=i.op_str) for i in decoder.disasm(code[0x3a40:0x3a64],0x3a40)],meaning='Exchange of two record longwords followed by beam-position polling (DFF006/DFF005); beam wait meaning only, without asserting a field mapping for the exchanged pair. Different hardware/algorithm; no DOS retrace, palette or byte equivalence.')
    save(OUT/'inventory.json',receipt([sys.executable,'verif/video_dos_inventory.py'],[Path(__file__),ROOT/'metadata/program-model.json',ROOT/'src/asm/GAME.ASM',ROOT/'src/data/DGDATA.ASM',ROOT/'c/video.c',ROOT/'c/dos_input.c',ROOT/'c/game_services.c',ROOT/'host/video.c',plain,*([path,ROOT/'tools/amiga.py'] if amiga else [])],result='PASS',routines=rows,page_ownership=owners,palette_source=dict(size=len(palette),maximum=max(palette),first_half_maximum=max(palette[:384]),sha256=hashlib.sha256(palette).hexdigest()),amiga=amiga,limitations='Complete named source references, with source/model sites retained for review; model complete=false is retained. Malformed arbitrary far-pointer writes can alias these cells, which are always reborrowed. IRQ24 is installed by the DOS vector service, not a static call edge.'))
    print('PASS20 entry caller/indirect audits;8 ownership fields; palette max',max(palette),'Amiga inspected',bool(amiga))
if __name__=='__main__':main()
