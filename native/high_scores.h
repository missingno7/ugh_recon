#ifndef NATIVE_HIGH_SCORES_H
#define NATIVE_HIGH_SCORES_H
#include <stdint.h>
#include "front_end.h"
typedef struct HighScoreRow {uint8_t name[14],digits[6],separator;} HighScoreRow;
typedef struct HighScoreTable {HighScoreRow rows[5];uint8_t terminators[2];} HighScoreTable;
uint16_t high_row_offset(uint8_t row,uint8_t stride,int digits);
typedef struct HighQualification {uint8_t position,done,qualifies;} HighQualification;
void high_compare_step(HighQualification *test,uint8_t candidate,uint8_t stored);
typedef struct HighFormatDigit {uint8_t character,significant;} HighFormatDigit;
HighFormatDigit high_format_digit(uint8_t digit,uint8_t significant);
typedef struct HighCopy {uint16_t source,destination,remaining;} HighCopy;
HighCopy high_copy_begin(uint16_t source);
void high_copy_advance(HighCopy *copy);
typedef struct HighDescending {uint16_t position,remaining;} HighDescending;
HighDescending high_complement_begin(void);
HighDescending high_digits_begin(void);
HighDescending high_name_begin(void);
void high_descending_advance(HighDescending *cursor);
uint8_t high_complement_byte(uint8_t byte);
typedef struct HighInsertion {uint16_t row,shift;uint8_t done,accepted;} HighInsertion;
void high_insertion_compare(HighInsertion *insertion,int qualifies);
int high_shift_advance(HighInsertion *insertion);
uint16_t high_file_size(void);
typedef enum HighFileAction {HIGH_FILE_DONE,HIGH_FILE_COMPLEMENT,HIGH_FILE_CREATE,HIGH_FILE_OPEN,HIGH_FILE_READ,HIGH_FILE_WRITE,HIGH_FILE_CLOSE} HighFileAction;
typedef struct HighFileFlow {uint8_t saving,phase;} HighFileFlow;
HighFileAction high_file_next(HighFileFlow *flow,int failed);
int16_t high_show_result(uint8_t scan);
uint16_t high_default_name_word(unsigned index);
#endif
