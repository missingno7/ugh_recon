/* All input bit patterns and all register/flag environments; actual C pair.
 * The byte-access shim represents the one owned ordinary-RAM word exactly. */
void __CPROVER_assume(_Bool);
void __CPROVER_assert(_Bool,const char *);
static uint8_t scratch[2];
uint8_t ugh_read(uint32_t address) {
    __CPROVER_assert(address>=D(CoordinateScaleScratch) && address<=D(CoordinateScaleScratch)+1,"scale reads owned word");
    return scratch[address-D(CoordinateScaleScratch)];
}
void ugh_write(uint32_t address,uint8_t value) {
    __CPROVER_assert(address>=D(CoordinateScaleScratch) && address<=D(CoordinateScaleScratch)+1,"scale writes owned word");
    scratch[address-D(CoordinateScaleScratch)]=value;
}
int main(void) {
    Regs old;old.ds=0;Regs modern=old;
    unsigned speed;__CPROVER_assume(speed<=1);
    CoordinateScale result=speed ? scale_level_speed(old.ax) : scale_level_y(old.ax);
    int a=speed ? l1_ScaleLevelSpeedToThreeHalves(&old) : l1_ScaleLevelYToThreeQuarters(&old);
    uint16_t stored=rd16(0,D(CoordinateScaleScratch));
    int b=speed ? c_ScaleLevelSpeedToThreeHalves(&modern) : c_ScaleLevelYToThreeQuarters(&modern);
    __CPROVER_assert(a==b && a==UGH_OK,"scale status");
    __CPROVER_assert(old.ax==result.value && stored==result.removed_fraction,"scale native values");
    __CPROVER_assert(stored==rd16(0,D(CoordinateScaleScratch)),"scale retained scratch");
    __CPROVER_assert(old.ax==modern.ax && old.bx==modern.bx && old.cx==modern.cx && old.dx==modern.dx && old.si==modern.si && old.di==modern.di && old.bp==modern.bp && old.sp==modern.sp && old.ss==modern.ss && old.cs==modern.cs && old.ds==modern.ds && old.es==modern.es && old.ip==modern.ip && old.flags==modern.flags,"scale complete register and flag shell");
    return 0;
}
