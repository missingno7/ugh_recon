#include "ugh.h"
#include "../coordinate_scale.h"

EXPORT int c_ScaleLevelYToThreeQuarters(Regs *r) {
    CoordinateScale result=scale_level_y(r->ax);
    wr16(r->ds,D(CoordinateScaleScratch),result.removed_fraction);
    /* Retain arithmetic diagnostics; no flag-elimination hypothesis needed. */
    r->ax=sub16(r,r->ax,result.removed_fraction,0);
    return UGH_OK;
}
EXPORT int c_ScaleLevelSpeedToThreeHalves(Regs *r) {
    CoordinateScale result=scale_level_speed(r->ax);
    wr16(r->ds,D(CoordinateScaleScratch),result.removed_fraction);
    r->ax=add16(r,r->ax,result.removed_fraction,0);
    return UGH_OK;
}
