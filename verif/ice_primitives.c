/* Compile with L1 memory.c and platform.c. Both maintained implementations are
 * included unchanged so static helpers can be exercised directly. L1's token
 * decode statements are extracted verbatim by ice_evidence.py into l1_tokens.inc.
 */
#include "ugh.h"
#include <stdio.h>
#include <string.h>
#include "../c/ice.c"
#ifndef ICE_IMPLEMENTATION
#define ICE_IMPLEMENTATION "../native/ice.c"
#endif
#include ICE_IMPLEMENTATION
#include "l1_tokens.inc"

static uint8_t encoded[32];
static unsigned length_bits;
static void append(unsigned value,unsigned width) {
    for (unsigned i=width; i>0; --i) {
        unsigned at=length_bits++;
        if ((value >> (i-1)) & 1) encoded[31-at/8] |= (uint8_t)(128u >> (at%8));
    }
}
static void setup(Ice *old,BitReader *modern) {
    for (unsigned i=0;i<32;++i) wr8(0x5000,(uint16_t)i,encoded[i]);
    *old=(Ice){0x5000,0x7000,31,1000,128,0};
    *modern=(BitReader){encoded,32,31,128,ICE_OK};
}
static int one_length(unsigned kind,unsigned value) {
    static const unsigned widths[]={0,0,1,2,10};
    memset(encoded,0,sizeof encoded); length_bits=0;
    append((1u<<kind)-1,kind); if(kind<4)append(0,1);
    append(value,widths[kind]);
    Ice old; BitReader modern; setup(&old,&modern);
    unsigned a=l1_length(&old), b=match_length(&modern);
    return a!=b || old.bits!=modern.pending || old.si!=modern.cursor;
}
static int one_offset(unsigned length,unsigned kind,unsigned value) {
    memset(encoded,0,sizeof encoded);length_bits=0;
    if(length==2) { append(kind,1);append(value,kind?9:6); }
    else if(kind==0) {append(0,1);append(value,8);}
    else {append(kind==1?2:3,2);append(value,kind==1?5:12);}
    Ice old;BitReader modern;setup(&old,&modern);
    unsigned dx=l1_offset(&old,(uint16_t)(length-2));
    unsigned a=(length+dx)&65535u,b=match_distance(&modern,length);
    return a!=b || old.bits!=modern.pending || old.si!=modern.cursor;
}
int main(int argc,char **argv) {
    if(argc!=2)return 10;
    FILE *snapshot=fopen(argv[1],"rb");
    if(!snapshot || fread(ugh_mem,1,UGH_MEM_SIZE,snapshot)!=UGH_MEM_SIZE)return 11;
    fclose(snapshot);
    unsigned transitions=0,lengths=0,offsets=0,literals=0;
    for(unsigned p=0;p<256;++p)for(unsigned b=0;b<256;++b) {
        for(unsigned edge=0;edge<3;++edge) {
            uint16_t at=edge==0?0:edge==1?1:65535;
            wr8(0x5000,at,(uint8_t)b);
            uint8_t input[65536];input[at]=(uint8_t)b;
            Ice old={0x5000,0x7000,at,0,(uint8_t)p,0};
            BitReader modern={input,sizeof input,at,(uint8_t)p,ICE_OK};
            if(next_bit(&old)!=take_bit(&modern) || old.bits!=modern.pending || old.si!=modern.cursor) return 1;
            ++transitions;
        }
    }
    for(unsigned k=0;k<5;++k) {
        static const unsigned width[]={0,0,1,2,10};
        for(unsigned v=0;v<(1u<<width[k]);++v) {if(one_length(k,v))return 2;++lengths;}
    }
    for(unsigned n=2;n<=1033;++n) {
        for(unsigned k=0;k<(n==2?2u:3u);++k) {
            unsigned width=n==2?(k?9:6):(k==0?8:k==1?5:12);
            for(unsigned v=0;v<(1u<<width);++v) {if(one_offset(n,k,v))return 3;++offsets;}
        }
    }
    for(unsigned k=0;k<5;++k) {
        static const unsigned width[]={2,2,3,8,15};
        for(unsigned v=0;v<(1u<<width[k]);++v) {
            memset(encoded,0,sizeof encoded);length_bits=0;append(1,1);
            for(unsigned j=0;j<k;++j)append((1u<<width[j])-1,width[j]);
            append(v,width[k]);
            Ice old;BitReader modern;setup(&old,&modern);
            unsigned a=l1_literal(&old),b=literal_length(&modern);
            if(a!=b || old.bits!=modern.pending || old.si!=modern.cursor) return 4;
            ++literals;
        }
    }
    printf("{\"bit_transitions\":%u,\"match_lengths\":%u,\"offsets\":%u,\"literals\":%u}\n",transitions,lengths,offsets,literals);
    return 0;
}
