/* The driver includes the actual L1 wrapper/decoder prefix and actual bridge
 * prefix, stopping both at the recognized-stream seam, with no hand model. */
#include "../c/ugh.h"
void __CPROVER_assert(int, const char *);
void __CPROVER_assume(int);
uint16_t nondet_word(void);
Regs nondet_regs(void);
static uint16_t words[2],source_segment,start;
static unsigned reads;

uint8_t ugh_read(uint32_t address) {
    unsigned word=reads/2,byte=reads%2;
    __CPROVER_assert(reads<4,"only signature bytes read");
    __CPROVER_assert(address==(uint32_t)source_segment*16u+
                    (uint16_t)(start+word*2u)+byte,"contiguous word/effective-offset wrap");
    ++reads;
    return (uint8_t)(words[word]>>(byte*8u));
}

#include "scan_bodies.inc"

int main(void) {
    Regs original=nondet_regs(),reference=original,native=original;
    words[0]=nondet_word();words[1]=nondet_word();
    /* The unchanged codec API admits recognized application headers at zero.
     * Every offset and both arbitrary signature words remain free otherwise. */
    __CPROVER_assume(words[0]!=0x4349 || words[1]!=0x2145 || original.si==0);
    source_segment=original.ds;start=original.si;
    int expected=reference_scratch(&reference);unsigned reference_reads=reads;
    reads=0;
    int actual=c_UnpackIceToScratch(&native);
    __CPROVER_assert(actual==expected,"equal return/seam");
    __CPROVER_assert(reads==reference_reads,"same reads, in the same order");
#define SAME(field) __CPROVER_assert(native.field==reference.field,"register frame/publication: " #field)
    SAME(ax);SAME(bx);SAME(cx);SAME(dx);SAME(si);SAME(di);SAME(bp);SAME(sp);
    SAME(cs);SAME(ds);SAME(es);SAME(ss);SAME(ip);SAME(flags);
}
