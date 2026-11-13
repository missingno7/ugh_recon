/* Complete Cartesian domain of the actual production reduction expression.
 * Separate translation units, no LTO: every pair calls the compiled expression.
 * The independent reference uses wide integer division and bucket counts. */
#include <stdint.h>
#include <stdio.h>
#include "random.h"
uint16_t tested_reduce(RandomState *,uint16_t);
static uint32_t buckets[65536];
int main(void) {
    uint64_t cases=0;
    for(uint32_t bound=0;bound<65536;bound++) {
        for(uint32_t i=0;i<bound;i++) buckets[i]=0;
        for(uint32_t word=0;word<65536;word++) {
            RandomState state={{(uint16_t)word,0,0,0}};
            uint16_t value=tested_reduce(&state,(uint16_t)bound);
            uint16_t reference=(uint16_t)(((uint64_t)word*bound)/65536u);
            if(value!=reference || (bound ? value>=bound : value!=0)) return 23;
            if(bound) buckets[value]++;
            cases++;
        }
        for(uint32_t value=0;value<bound;value++) {
            uint32_t lower=(value*65536u+bound-1)/bound;
            uint32_t upper=((value+1)*65536u+bound-1)/bound;
            if(buckets[value]!=upper-lower) return 23;
        }
    }
    printf("{\"word_bound_pairs\":%llu,\"bound_domain\":65536,\"word_domain\":65536,\"all_bucket_cardinalities_checked\":true}\n",
           (unsigned long long)cases);
    return 0;
}
