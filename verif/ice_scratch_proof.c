#include "ice_scratch.h"
void __CPROVER_assert(int, const char *);
void __CPROVER_assume(int);
#define assert(condition) __CPROVER_assert((condition), #condition)

unsigned nondet_unsigned(void);
size_t nondet_size(void);
uint8_t nondet_byte(void);
static IceStatus reply;
static IceResult published;
static const IceScratchView *expected;
static unsigned calls;
static uint8_t written;

/* Equality seam: these are arbitrary codec outputs, not a model of decoding.
 * The accepted ice certificate supplies the codec's separate properties. */
IceStatus ice_decode(const uint8_t *source, size_t source_size,
                     uint8_t *output, size_t output_size, IceResult *result) {
    assert(source==expected->source && source_size==expected->source_size);
    assert(output==expected->workspace && output_size==expected->workspace_size);
    ++calls;
    output[0]=written;
    *result=published;
    return reply;
}

#include "../native/ice_scratch.c"

int main(void) {
    uint8_t source[2]={nondet_byte(),nondet_byte()};
    uint8_t workspace[2]={nondet_byte(),nondet_byte()};
    uint8_t source0=source[0],source1=source[1],other=workspace[1];
    IceScratchView view={source,nondet_size(),workspace,nondet_size()};
    size_t source_size=view.source_size,workspace_size=view.workspace_size;
    IceScratchResult result;
    published.source_cursor=nondet_size();
    published.destination_cursor=nondet_size();
    published.bytes_written=nondet_size(); published.tokens=nondet_unsigned();
    unsigned code=nondet_unsigned(); __CPROVER_assume(code<=ICE_LIMIT);
    reply=(IceStatus)code; written=nondet_byte(); expected=&view;
    IceStatus status=ice_unpack_scratch(&view,&result);
    assert(calls==1 && status==reply);
    assert(result.decoder.source_cursor==published.source_cursor);
    assert(result.decoder.destination_cursor==published.destination_cursor);
    assert(result.decoder.bytes_written==published.bytes_written);
    assert(result.decoder.tokens==published.tokens);
    assert(result.source_cursor==(reply==ICE_OK || reply==ICE_BAD_MAGIC ?
           (uint16_t)published.source_cursor : 10));
    assert(result.workspace_cursor==(reply==ICE_OK ?
           (uint16_t)published.destination_cursor : 0));
    assert(workspace[0]==written && workspace[1]==other);
    assert(source[0]==source0 && source[1]==source1);
    assert(view.source==source && view.workspace==workspace);
    assert(view.source_size==source_size && view.workspace_size==workspace_size);
}
