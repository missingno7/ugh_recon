"""Producer-side publications added after the original seam checkpoint.

These hooks instrument generated copies only. They publish at the actual store,
never at a frame boundary, and do not repair or resynchronize the comparator.
"""


def instrument_publication(relative_path, text):
    if relative_path in ('native/bridge/palette_world_bridge.c','native/bridge/input_world_bridge.c','native/bridge/video_pages_bridge.c','native/bridge/pixel_world_bridge.c','native/bridge/presentation_world_bridge.c','native/bridge/run_world_bridge.c','native/bridge/random_world_bridge.c','native/bridge/player_world_bridge.c','native/bridge/resource_catalog_bridge.c','native/bridge/platform_world_bridge.c'):
        return text # Writes are owner writes, or delegate to the existing audio/unmoved publisher.
    if relative_path == 'native/bridge/audio_world_bridge.c':
        store='ugh_mem[address]=source[i];'
        assert text.count(store)==1
        text=text.replace(store,store+'pr_pointer_write(ugh_mem+address,source[i]);')
        store='window[index]=value;';assert text.count(store)==1
        return text.replace(store,store+'pr_pointer_write(window+index,value);')
    if relative_path != 'native/bridge/ice_scratch_bridge.c':
        return text
    if 'audio_workspace_publish(' in text:
        # Its producer hook is at the actual unmoved byte store. Owned lanes
        # go directly to native state and never enter the RAM/write journal.
        assert 'memcpy(ugh_mem+destination,output,sizeof output);' not in text
        return text
    store = 'memcpy(ugh_mem+destination,output,sizeof output);'
    assert text.count(store) == 1, 'ICE scratch publication changed'
    return text.replace(store, store+'pr_publish(ugh_mem+destination,sizeof output);')
