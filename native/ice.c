#include "ice.h"

typedef struct BitReader {
    const uint8_t *data;
    size_t size, cursor;
    uint8_t pending;
    IceStatus error;
} BitReader;

/* Retained DOS semantics: decrementing zero wraps inside the same 64 KiB
 * byte window. This is deliberately independent of host pointer arithmetic. */
static size_t previous(size_t index) { return (index + 65535u) & 65535u; }

static uint8_t take_byte(BitReader *reader) {
    if (reader->cursor >= reader->size) { reader->error=ICE_RANGE; return 0; }
    uint8_t value=reader->data[reader->cursor];
    reader->cursor=previous(reader->cursor);
    return value;
}

/* The low sentinel bit marks exhaustion. A refill rotates the next byte
 * through the outgoing carry; zero pending is also defined for corrupt input. */
static unsigned take_bit(BitReader *reader) {
    unsigned bit=reader->pending >> 7;
    reader->pending=(uint8_t)(reader->pending << 1);
    if (!reader->pending) {
        uint8_t byte=take_byte(reader);
        reader->pending=(uint8_t)((byte << 1) | bit);
        bit=byte >> 7;
    }
    return bit;
}

static unsigned take_bits(BitReader *reader, unsigned width) {
    unsigned value=0;
    for (unsigned i=0; i<width; ++i) value=(value << 1) | take_bit(reader);
    return value;
}

static unsigned literal_length(BitReader *reader) {
    static const unsigned widths[]={2,2,3,8,15};
    static const unsigned bases[]={2,5,8,15,270};
    if (!take_bit(reader)) return 1;
    for (unsigned i=0; i<5; ++i) {
        unsigned code=take_bits(reader,widths[i]);
        if (code != (1u << widths[i])-1 || i==4) {
            /* Retained DOS DEC/JNS: DX>32768 copies once; DX==32768 becomes
             * 32767 on the first decrement and copies 32769 bytes. The last
             * literal class can reach both cases, including corrupt streams. */
            unsigned minus_one=(code+bases[i]-1) & 65535u;
            return minus_one > 32768 ? 1 : minus_one+1;
        }
    }
    return 1; /* all five classes are exhaustive */
}

static unsigned match_length(BitReader *reader) {
    static const unsigned widths[]={0,0,1,2,10};
    static const unsigned bases[]={2,3,4,6,10};
    unsigned kind=0;
    while (kind<4 && take_bit(reader)) ++kind;
    return bases[kind]+take_bits(reader,widths[kind]);
}

static unsigned match_distance(BitReader *reader, unsigned length) {
    if (length==2) {
        unsigned wide=take_bit(reader);
        return take_bits(reader,wide ? 9 : 6)+(wide ? 65 : 1);
    }
    if (!take_bit(reader)) return length+31+take_bits(reader,8);
    if (take_bit(reader)) return length+287+take_bits(reader,12);
    unsigned code=take_bits(reader,5);
    return code ? length+code-1 : 1;
}

IceStatus ice_decode(const uint8_t *source, size_t source_size,
                     uint8_t *output, size_t output_size, IceResult *result) {
    *result=(IceResult){0,0,0,0};
    if (source_size<2) return ICE_TRUNCATED;
    result->source_cursor=2;
    if (source[0]!='I' || source[1]!='C') return ICE_BAD_MAGIC;
    if (source_size<4) return ICE_TRUNCATED;
    result->source_cursor=4;
    if (source[2]!='E' || source[3]!='!') return ICE_BAD_MAGIC;
    if (source_size<12) return ICE_TRUNCATED;
    size_t packed=(unsigned)source[6]*256u+source[7];
    size_t unpacked=(unsigned)source[10]*256u+source[11];
    BitReader reader={source,source_size,previous(packed),0,ICE_OK};
    size_t cursor=previous(unpacked);
    reader.pending=take_byte(&reader);
    IceStatus status=reader.error;
    for (unsigned token=0; status==ICE_OK; ++token) {
        if (token==2000000u) { status=ICE_LIMIT; break; }
        result->tokens=token+1;
        if (take_bit(&reader)) {
            unsigned length=literal_length(&reader);
            for (unsigned i=0; i<length; ++i) {
                uint8_t byte=take_byte(&reader);
                if (reader.error) { status=reader.error; break; }
                if (cursor>=output_size) { status=ICE_RANGE; break; }
                output[cursor]=byte; cursor=previous(cursor); ++result->bytes_written;
            }
        }
        if (status) break;
        if (reader.error) { status=reader.error; break; }
        if (cursor==65535u) break;
        unsigned length=match_length(&reader);
        unsigned distance=match_distance(&reader,length);
        if (reader.error) { status=reader.error; break; }
        size_t from=(cursor+distance) & 65535u;
        /* Copy backward one byte at a time: distance one is an intentional
         * overlapping run, so memcpy/memmove would change the result. */
        for (unsigned i=0; i<length; ++i) {
            if (cursor>=output_size || from>=output_size) { status=ICE_RANGE; break; }
            output[cursor]=output[from];
            cursor=previous(cursor); from=previous(from); ++result->bytes_written;
        }
    }
    result->source_cursor=reader.cursor;
    result->destination_cursor=cursor;
    return status;
}
