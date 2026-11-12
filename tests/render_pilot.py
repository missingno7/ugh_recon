"""Actual sprite-bank bytes and edge fixtures through the planar upload loop."""
from difftest import Case
from emu import DATA_SEG


def make(count,start,reverse=False):
    def setup(m):
        m.ww('GAME:VgaPlaneCopyByteCount',count)
        m.ww('GAME:DrawPagePointer',start)
        m.ww('GAME:DrawPagePointer',0xA000,2)
        # Source is real, column-major indexed sprite bytes from our own build.
        m.ww('DGROUP:DecodedImagePointer',0)
        m.ww('DGROUP:DecodedImagePointer',m.seg('B1E1F:ext_1E1F'),2)
        m.device.planes[:]=bytes((i*17+0x5A)&255 for i in range(4*65536))
    return Case(f'planar upload count={count}, DI={start:04X}, DF={reverse}',
                'GAME:UploadChunkyImageToVgaPlanes',setup=setup,regs=dict(DS=DATA_SEG),
                flags=0x602 if reverse else 0x202,
                out_regs=('AX','BX','CX','DX','SI','DI','BP','CF','PF','ZF','SF','OF','DF'))


CASES=[make(1,0),make(32,0xFFF0),make(32,15,True),make(16000,0),make(0,0)]
