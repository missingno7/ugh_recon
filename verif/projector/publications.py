"""Producer-side publications added after the original seam checkpoint.

These hooks instrument generated copies only. They publish at the actual store,
never at a frame boundary, and do not repair or resynchronize the comparator.
"""


def instrument_publication(relative_path, text):
    if relative_path != 'native/bridge/ice_scratch_bridge.c':
        return text
    store = 'memcpy(ugh_mem+destination,output,sizeof output);'
    assert text.count(store) == 1, 'ICE scratch publication changed'
    return text.replace(store, store+'pr_publish(ugh_mem+destination,sizeof output);')
