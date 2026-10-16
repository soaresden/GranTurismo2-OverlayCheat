/*
 * Start-up stub of the patched SCES_123.80: the executable's entry point (header +0x10) points
 * here instead of the game's (GAME_ENTRY). The stub sits in zeros of the overlay area (which the
 * game fills with its overlays later), with the resident block right after it:
 *
 *   copy the block to RESIDENT (low RAM) and clear its copy here (the area was zeros),
 *   FlushCache, cheat_boot() (redirects the game's calls), FlushCache again,
 *   then jump to the game.
 *
 * $sp, $gp and $ra as the BIOS set them are left as they were for the game.
 */
#include "game.h"
    .set noreorder
    .set noat

    .macro flush
    li      $a0, 1                  /* EnterCriticalSection */
    syscall
    li      $t2, 0xA0               /* A0:44 FlushCache */
    jalr    $t2
    li      $t1, 0x44
    li      $a0, 2                  /* ExitCriticalSection */
    syscall
    .endm

    .text
    .globl _start
_start:
    move    $s7, $ra                /* kept for the game (s7: not used by what is called here) */
    lui     $t0, %hi(block)
    addiu   $t0, $t0, %lo(block)
    lui     $t1, %hi(RESIDENT)
    addiu   $t1, $t1, %lo(RESIDENT)
    li      $t2, BLOCK_WORDS
1:  lw      $t3, 0($t0)
    sw      $zero, 0($t0)
    addiu   $t0, $t0, 4
    addiu   $t2, $t2, -1
    sw      $t3, 0($t1)
    bnez    $t2, 1b
    addiu   $t1, $t1, 4
    flush
    jal     CHEAT_BOOT
    nop
    flush
    move    $ra, $s7
    lui     $t0, %hi(GAME_ENTRY)
    addiu   $t0, $t0, %lo(GAME_ENTRY)
    jr      $t0
    move    $s7, $zero
    .balign 4
block:
