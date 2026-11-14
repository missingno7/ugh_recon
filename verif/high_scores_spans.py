"""Actual maintained front-end spans shared by compiled and symbolic evidence."""
from closure_support import ROOT,function
def sources():return [(ROOT/'c'/n).read_text() for n in ['menu.c','menu_helpers.c','game_services.c']]
def format_span():
    body=function(sources()[0],'c_InsertHighScoreAndClearScore');return body[body.index('        set_al(r,add_byte'):body.index('        r->si=increment_word')]
def high_editor_span(native=False):
    text=(ROOT/'native/bridge/high_scores_bridge.c').read_text() if native else sources()[0];body=function(text,'edit_score_name')
    part=body[body.index('        uint8_t ch='):body.index('        return UGH_OK;')]
    return part.replace('continue;','return 1;').replace('goto reset;','return 2;')+'return 0;'
