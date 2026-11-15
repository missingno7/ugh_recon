"""Build-time ADLX pack identities; no executable coordinates in native code."""
def generate(rows,symbols):
    # Shipped resource frames are data allocations, with ID-based runtime views.
    # Discover the authoritative complete ADLX census from DATA declarations.
    import cgen
    mz,_=cgen.read_symbols()
    objects=[r for r in rows if r['name'].startswith('data.') and mz.image[r['image_start']:r['image_start']+4]==b'ADLX']
    objects.sort(key=lambda r:r['image_start'])
    if len(objects)!=11:raise ValueError('expected eleven admitted ADLX allocations')
    score=next(i for i,r in enumerate(objects) if r['name']=='data.B3279.AdlxHeader_3279')
    game_over=next(i for i,r in enumerate(objects) if r['name']=='data.B326B.AdlxHeader_326B')
    menu=next(i for i,r in enumerate(objects) if r['name']=='data.B3637.AdlxHeader_3637')
    intro=next(i for i,r in enumerate(objects) if r['name']=='data.B3629.AdlxHeader_3629')
    lines=['/* Generated data IDs and offsets within admitted data objects. */',
           'typedef struct GameAudioResourceSpec {GSResourceId id,allocation;size_t offset,size;} GameAudioResourceSpec;',
           'static const GameAudioResourceSpec game_audio_specs[]={']
    for r in objects:
        start=r['image_start'];size=int.from_bytes(mz.image[start+4:start+8],'big')+8
        owner=next(a for a in rows if a['name'].startswith('world.allocation.') and a['image_start']<=start and start+size<=a['image_start']+a['size'])
        lines.append('{UINT64_C(%d),UINT64_C(%d),%d,%d},'%(r['id'],owner['id'],start-owner['image_start'],size))
    return lines+['};','#define GAME_AUDIO_GAME_OVER %d'%game_over,'#define GAME_AUDIO_MENU %d'%menu,'#define GAME_AUDIO_SCORE %d'%score,'#define GAME_AUDIO_INTRO %d'%intro]
