/* Narrow services; only the pilot subset is implemented. See docs/architecture.md. */
#ifndef UGH_PLATFORM_H
#define UGH_PLATFORM_H
#include "ugh.h"
enum { LOG_OUT=1, LOG_IN=2, LOG_DOS=3 };
typedef struct IoEvent { uint32_t kind, port, size, value; } IoEvent;
/* Test device state, never game state. Plain unchained VGA write mode 0 only. */
typedef struct Devices {
    uint8_t plane[4][65536], latch[4];
    uint8_t seq_index, map_mask, gc_index, read_map;
    uint32_t count, error;
    IoEvent log[270000];
} Devices;
extern Devices ugh_devices;
EXPORT void platform_out(uint16_t port, unsigned size, uint32_t value);
EXPORT uint32_t platform_in(uint16_t port, unsigned size);
EXPORT int platform_interrupt(uint8_t number, Regs *r);
/* Reserved contracts: IRQ delivery at explicit service points, DOS vector/file calls,
 * keyboard/joystick scripts, OPL register writes and DSP/DMA transfers. Unsupported
 * requests fail; these declarations are not implementations or coverage claims. */
typedef enum ServicePoint { SERVICE_RETRACE, SERVICE_TIMER_WAIT, SERVICE_IO } ServicePoint;
int platform_service_point(ServicePoint point, Regs *r);
#endif
