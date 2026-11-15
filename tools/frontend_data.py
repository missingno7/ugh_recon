"""Build-time front-end data pointer translation, never linked into the game."""
import struct
import cgen

def generate(rows,symbols):
    mz,_=cgen.read_symbols()
    def view(start,size):
        choices=[r for r in rows if r['image_start']<=start and start+size<=r['image_start']+r['size']]
        if not choices:raise ValueError('front-end data view outside admitted object')
        r=min(choices,key=lambda r:r['size'])
        return '{UINT64_C(%d),%d,%d}'%(r['id'],start-r['image_start'],size)
    lines=['typedef struct GameFrontDataView {GSResourceId resource;size_t offset,size;} GameFrontDataView;',
           'static const GameFrontDataView game_front_banks[]={']
    for name in ['SpritePixels0To216Pointer','SpritePixels217To297Pointer','SpritePixels298To546Pointer','SpritePixels547AndUpPointer']:
        offset,frame=struct.unpack_from('<HH',mz.image,symbols['GAME:'+name]['linear'])
        r=next(r for r in rows if r['name'].startswith('world.allocation.') and r['image_start']==frame*16+offset)
        lines.append(view(r['image_start'],r['size'])+',')
    lines+=['};','static const GameFrontDataView game_front_labels[]={']
    for name,count in [('DifficultyLabelPointers',3),('PlayerCountLabelPointers',2),('ControlModeLabelPointers',3)]:
        for i in range(count):
            off=struct.unpack_from('<H',mz.image,symbols['DGROUP:'+name]['linear']+2*i)[0]
            start=cgen.FRAMES['DGROUP']*16+off
            end=mz.image.index(b'\0',start)+1
            lines.append(view(start,end-start)+',')
    return lines+['};']
