#include "items.h"
#include <stdio.h>
/* Free flight is identical until first landing. Ignoring all platforms can
 * only postpone that first landing/retirement; landed lifetime is then 560. */
int main(void) {
    unsigned maximum=0;unsigned long long states=0;
    for(int y=-544;y<=6256;y++) for(int velocity=-135;velocity<=-14;velocity++) {
        FallingItem item={0};item.sprite=285;item.position.y32=(uint16_t)y;
        item.vertical_step=(uint16_t)velocity;
        unsigned updates=0;
        while(item.sprite!=65535u && updates<140) { item_advance(&item,0,0);updates++; }
        if(item.sprite!=65535u) return 23;
        if(updates>maximum) maximum=updates;
        states++;
    }
    printf("{\"states\":%llu,\"max_flight_updates\":%u,\"max_total_updates\":%u}\n",states,maximum,maximum+560);
    return maximum+560<700?0:24;
}
