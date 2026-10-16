/* First words of the resident block (0x8000F000): the magic and the version, checked by the
   start-up stub; then tick_store, the jump target of the race overlay's lap clock store. */
#include "game.h"
    .set noreorder
    .set noat
    .section .text.start, "ax"
    .globl _start
_start:
    .word PAYLOAD_MAGIC
    .word PAYLOAD_VERSION

/* In place of `sw $v0, ($a2) / jr $ra` at the end of the race overlay's clock tick ($v0: the new
   clock, $a2: its address): the store is skipped while FREEZE TIMER is on in a licence test,
   once the clock has left 0. Only temporaries are used (the function returns right after). */
    .globl tick_store
tick_store:
    lui     $t0, %hi(STATE)
    lbu     $t1, %lo(STATE + 4)($t0)          /* struct g: freeze */
    lui     $t2, %hi(RACE_MODE)
    beqz    $t1, 1f
    lbu     $t2, %lo(RACE_MODE)($t2)
    li      $t1, MODE_LICENCE
    bne     $t2, $t1, 1f
    nop
    lw      $t1, 0($a2)
    nop
    bnez    $t1, 2f
    nop
1:  sw      $v0, 0($a2)
2:  jr      $ra
    nop
