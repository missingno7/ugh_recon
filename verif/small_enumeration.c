/* Included after the mechanically extracted L1 and production native pair. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#undef assert
#define assert(condition) do { if(!(condition)) { fprintf(stderr,"check failed: %s:%d\n",__FILE__,__LINE__); exit(23); } } while(0)
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t address) { return ugh_mem[address]; }
void ugh_write(uint32_t address,uint8_t value) { ugh_mem[address]=value; }

static void scales(void) {
    for (unsigned speed=0;speed<2;++speed) for (unsigned value=0;value<65536;++value) {
        CoordinateScale result=speed ? scale_level_speed((uint16_t)value) : scale_level_y((uint16_t)value);
        for (unsigned preserved=0;preserved<2;++preserved) {
            Regs before={0},after;
            before.ax=(uint16_t)value;before.ds=0x1000;before.flags=preserved ? 65535 : 0;
            before.bx=123;before.cx=234;before.dx=345;before.si=456;before.di=567;
            before.bp=678;before.ss=789;before.sp=890;before.cs=901;before.ip=12;
            after=before;
            int old=speed ? l1_ScaleLevelSpeedToThreeHalves(&before) : l1_ScaleLevelYToThreeQuarters(&before);
            assert(old==UGH_OK);assert(before.ax==result.value);
            assert(rd16(0x1000,D(CoordinateScaleScratch))==result.removed_fraction);
            int modern=speed ? c_ScaleLevelSpeedToThreeHalves(&after) : c_ScaleLevelYToThreeQuarters(&after);
            assert(modern==old);assert(!memcmp(&before,&after,sizeof before));
            assert(rd16(0x1000,D(CoordinateScaleScratch))==result.removed_fraction);
        }
    }
}
static void reset_divisors(void) {
    wr8(0,D(DecimalTenDivisor),10);wr8(0,D(DecimalHundredDivisor),100);
    wr16(0,D(DecimalThousandDivisor),1000);wr16(0,D(DecimalTenThousandDivisor),10000);
}
static void decimals(void) {
    for (unsigned digits=2;digits<=6;digits+=2) {
        unsigned bound=digits==2 ? 256 : digits==4 ? 65536 : 1000000;
        for (unsigned value=0;value<bound;++value) {
            /* Canonical immutable divisors and disjoint output. Every input in
             * each stated value domain, not a sample of six-digit values. */
            reset_divisors();
            Regs before={0},after;
            before.ax=(uint16_t)value;before.dx=(uint16_t)(value>>16);
            before.si=0x500;before.cx=0x9abc;before.bx=0x1234;before.flags=0xed7;
            after=before;
            int old=digits==2 ? l1_EncodeTwoDecimalDigits(&before) : digits==4 ? l1_EncodeFourDecimalDigits(&before) : l1_EncodeSixDecimalDigits(&before);
            uint8_t expected[7];memcpy(expected,ugh_mem+0x500,digits+1);
            memset(ugh_mem+0x500,0x5a,digits+1);
            int modern=digits==2 ? c_EncodeTwoDecimalDigits(&after) : digits==4 ? c_EncodeFourDecimalDigits(&after) : c_EncodeSixDecimalDigits(&after);
            assert(modern==old);assert(!memcmp(&before,&after,sizeof before));
            assert(!memcmp(expected,ugh_mem+0x500,digits+1));
            unsigned remainder=value;
            for (int i=(int)digits-1;i>=0;--i) {
                /* Leading element deliberately keeps the whole quotient. */
                unsigned digit=i==0 ? remainder : remainder%10;
                assert(expected[i]==(uint8_t)digit);remainder/=10;
            }
            assert(expected[digits]==255);
        }
    }
    /* A second complete arithmetic domain: all byte values times all ten
     * divisors, including the L1 rejected-zero path. Output disjoint at 0500. */
    for (unsigned divisor=0;divisor<256;++divisor) for (unsigned value=0;value<256;++value) {
        wr8(0,D(DecimalTenDivisor),(uint8_t)divisor);
        memset(ugh_mem+0x500,0x5a,3);
        Regs before={0},after;before.ax=(uint16_t)(0xab00u+value);
        before.dx=0x4321;before.si=0x500;before.flags=0xed7;after=before;
        int old=l1_EncodeTwoDecimalDigits(&before);
        uint8_t expected[3];memcpy(expected,ugh_mem+0x500,3);
        memset(ugh_mem+0x500,0x5a,3);
        int modern=c_EncodeTwoDecimalDigits(&after);
        assert(old==modern);assert(!memcmp(&before,&after,sizeof before));
        assert(!memcmp(expected,ugh_mem+0x500,3));
        assert(old==(divisor ? UGH_OK : UGH_UNSUPPORTED));
        if(divisor)assert(expected[0]==value/divisor && expected[1]==value%divisor && expected[2]==255);
    }
}
static void copies(void) {
    uint8_t expected[65568];unsigned cases=0;
    for (unsigned backwards=0;backwards<2;++backwards)
      for (unsigned displacement=0;displacement<3;++displacement)
       for (unsigned start=0;start<4;++start)
        for (unsigned n=0;n<7;++n) {
            unsigned counts[]={0,1,2,12,20,256,65535};
            unsigned positions[]={0,1,65520,65535};
            for(unsigned i=0;i<sizeof expected;++i) ugh_mem[i]=(uint8_t)(i*29+7);
            wr16(0x2000,4,(uint16_t)counts[n]);wr16(0x2000,6,0xfeed);
            wr16(0x2000,8,(uint16_t)positions[start]);wr16(0x2000,10,0);
            wr16(0x2000,12,(uint16_t)(positions[start]+1));
            wr16(0x2000,14,(uint16_t)displacement);
            Regs before={0},after;before.ss=0x2000;before.cx=123;before.flags=backwards?0xed7:0xad7;
            after=before;
            assert(l1_CopyFarBytes(&before)==UGH_OK);
            memcpy(expected,ugh_mem,sizeof expected);
            for(unsigned i=0;i<sizeof expected;++i) ugh_mem[i]=(uint8_t)(i*29+7);
            assert(c_CopyFarBytes(&after)==UGH_OK);
            assert(!memcmp(expected,ugh_mem,sizeof expected));assert(!memcmp(&before,&after,sizeof before));
            ++cases;
        }
    assert(cases==168);
}
int main(void) {
    scales();decimals();copies();
    puts("{\"scale_value_domains\":131072,\"scale_bridge_cases\":262144,\"decimal_two\":256,\"decimal_two_all_ten_divisors\":65536,\"decimal_four\":65536,\"decimal_six_usual_domain\":1000000,\"copy_differential_cases\":168}");
    return 0;
}
