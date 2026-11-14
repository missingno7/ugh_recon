#include "high_scores.h"
FrontBlink front_blink(uint16_t position,uint16_t capacity,uint8_t counter)
{FrontBlink blink={(uint8_t)(counter-1u),0,(uint8_t)(position<capacity)};blink.character=blink.counter&16u ? '?' : ' ';return blink;}
FrontEditCommand front_edit_command(uint16_t position,uint16_t capacity,uint8_t character,int spaces)
{
    FrontEditCommand command={FRONT_EDIT_IGNORE,position,{0,0},character,0,0,0,0};
    if(character==8) {
        if(!position) return command;
        command.kind=FRONT_EDIT_ERASE;
        if(position<capacity) command.erase[command.erase_count++]=position;
        command.position=(uint16_t)(position-1u);command.erase[command.erase_count++]=command.position;
        return command;
    }
    int accepted=(character>='A' && character<='Z') || (character>='0' && character<='9') || (spaces && character==' ');
    if(character>='a' && character<='z') {character=(uint8_t)(character-32u);accepted=1;}
    if(accepted) {
        command.accepted=1;
        if(position>=capacity) return command;
        command.kind=FRONT_EDIT_STORE;command.character=character;command.position=(uint16_t)(position+1u);return command;
    }
    if(character==13) {command.kind=FRONT_EDIT_FINISH;command.clear_current=(uint8_t)(position<capacity);command.empty=(uint8_t)(position==0);}
    return command;
}
FrontRectangle front_entry_rectangle(int score_name) {FrontRectangle rectangle={0,(uint16_t)(score_name ? 160 : 176),320,16};return rectangle;}
uint16_t front_next_byte_position(uint16_t position,int reverse) {return (uint16_t)(position+(reverse ? -1 : 1));}

uint16_t high_row_offset(uint8_t row,uint8_t stride,int digits) {return (uint16_t)((uint16_t)row*stride+(digits ? 14u : 0u));}
void high_compare_step(HighQualification *test,uint8_t candidate,uint8_t stored)
{
    /* Unsigned byte lexicographic order; ties qualify and precede old ties. */
    if(candidate!=stored || test->position==5) {test->done=1;test->qualifies=(uint8_t)(candidate>=stored);}
    else test->position++;
}
HighFormatDigit high_format_digit(uint8_t digit,uint8_t significant)
{
    uint8_t character=(uint8_t)(digit+48u);
    if(character!=48) significant=(uint8_t)(significant-1u);
    HighFormatDigit result={(uint8_t)(!significant && character==48 ? 32 : character),significant};return result;
}
HighCopy high_copy_begin(uint16_t source) {HighCopy copy={source,(uint16_t)(source+21u),20};return copy;}
void high_copy_advance(HighCopy *copy) {copy->source++;copy->destination++;copy->remaining--;}
HighDescending high_complement_begin(void) {HighDescending cursor={106,107};return cursor;}
HighDescending high_digits_begin(void) {HighDescending cursor={5,6};return cursor;}
HighDescending high_name_begin(void) {HighDescending cursor={11,12};return cursor;}
void high_descending_advance(HighDescending *cursor) {cursor->position--;cursor->remaining--;}
uint8_t high_complement_byte(uint8_t byte) {return (uint8_t)(byte^255u);}
void high_insertion_compare(HighInsertion *insertion,int qualifies)
{
    if(qualifies) {insertion->done=1;insertion->accepted=1;insertion->shift=3;}
    else if(++insertion->row==5) insertion->done=1;
}
int high_shift_advance(HighInsertion *insertion)
{
    /* Even insertion at row4 performs the row3->row4 copy once. */
    insertion->shift--;return (int16_t)insertion->shift>=(int16_t)insertion->row;
}
uint16_t high_file_size(void) {return 107;}
HighFileAction high_file_next(HighFileFlow *flow,int failed)
{
    if(flow->saving) switch(flow->phase++) {
    case 0:return HIGH_FILE_COMPLEMENT;
    case 1:return HIGH_FILE_CREATE;
    case 2:if(!failed) return HIGH_FILE_WRITE;flow->phase=4;return HIGH_FILE_COMPLEMENT;
    case 3:return HIGH_FILE_COMPLEMENT;
    default:return HIGH_FILE_DONE;
    }
    switch(flow->phase++) {
    case 0:return HIGH_FILE_OPEN;
    case 1:return failed ? HIGH_FILE_DONE : HIGH_FILE_READ;
    case 2:return failed ? HIGH_FILE_DONE : HIGH_FILE_CLOSE;
    case 3:return failed ? HIGH_FILE_DONE : HIGH_FILE_COMPLEMENT;
    default:return HIGH_FILE_DONE;
    }
}
int16_t high_show_result(uint8_t scan) {return (scan&127u)==16 ? -1 : 1;}
uint16_t high_default_name_word(unsigned index)
{static const uint8_t name[]="INCOGNITUS";return (uint16_t)(name[2u*index]+256u*name[2u*index+1u]);}
