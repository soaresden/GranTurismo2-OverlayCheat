Gran Turismo 2 (PS1, PAL) - Overlay Cheat Menu v1.0
====================================================
by soaresden - https://github.com/soaresden/GranTurismo2-OverlayCheat

Hold SELECT (or press L1 + R1 + L2 + R2 together) and a small menu appears over the game:

  FREEZE TIMER   stops the clock of the licence tests
  MONEY          changes the credits live (adjustable step, maximum, zero)

Controls (pad 1)
----------------
Two ways to open the "GT2 CHEAT" menu:
  - hold SELECT: the menu appears after a short moment, and goes away on release;
  - press L1 + R1 + L2 + R2 together: the menu opens and stays open; START (or the four
    shoulder buttons again) closes it. Use this one in RetroArch / Batocera, where SELECT is
    often the hotkey button.
While the menu is open, the game does not receive the pad.

  Up / Down                     choose the line
  FREEZE TIMER line:
    Left / Right / Cross / Circle   ON / OFF
  MONEY line:
    Right / Left                + / - the step (held: repeats)
    R1 / L1                     step x10 / step /10 (from 1 to 10,000,000)
    Triangle                    99,999,999 (the maximum)
    Square                      0

- FREEZE TIMER ON: in a licence test the clock stops where it is. If it was already ON at the
  start, it stops at 0:00.040, right after the start (a licence test whose clock stays at 0 never
  ends). Stop in the target zone and the gold is yours. The choice is kept until power off.
  It only acts in licence tests, not in races.
- A short press of SELECT (no other button) is given back to the game on release.

Patching
--------
Patch the Simulation disc (Disc 2, SCES-12380, "Gran Turismo Mode") with one of:
  Gran Turismo 2 (Europe) (Disc 2) [Overlay Cheat].ppf     (PPF 3.0, changed bytes only)
  Gran Turismo 2 (Europe) (Disc 2) [Overlay Cheat].xdelta  (xdelta3)

Source image: a single-track .bin, 2352 bytes per sector:
  Gran Turismo 2 (Europe) (En,Fr,De,Es,It) (Disc 2) (Gran Turismo Mode).bin
  Size   710,226,384 bytes
  CRC32  64439308
  SHA-1  c63a53bcf5ac6e49547a0c95b05174deff172021
Patched image:
  CRC32  41B7DCB9
  SHA-1  9fe8e1acf3819398fc4849efc26bbf0f4601cd93

The PPF only touches the sectors of SCES_123.80, GT2.OVL and one directory sector.

Combined disc (GT2-Combined-Disc) and GT2 Plus: their layout differs, use the Python tool of the
project instead (patch_disc.py, Python 3, nothing to install), which takes a .chd, .cue or .bin
and checks every word before changing it:
  python patch_disc.py "Gran Turismo 2.chd"

Tested
------
- PCSX-Redux (BIOS SCPH-5502 and OpenBIOS): menu on the language screen, the city map and in
  licence tests; credits updated on screen; licence B-1 with the clock frozen until the end.
- RALibretro / RetroArch, Beetle PSX core (mednafen): menu with SELECT and with the shoulder
  buttons.
On the original combined disc and on GT2 Plus beta 7 combined.

How it works
------------
SCES_123.80 is not compressed: a start-up stub, placed in zeros of the overlay area, copies the
resident code to free low RAM (0x8000F000) and redirects the pad update callback and the two
calls that draw a frame (the menu is drawn over the frame with GPU primitives). In the race
overlay of GT2.OVL, the store of the lap clock jumps to a routine that skips it in licence tests
while FREEZE TIMER is on. Sources, addresses and notes: see the GitHub project.

Gran Turismo is a trademark of Sony Interactive Entertainment. Fan project, not affiliated with
Sony or Polyphony Digital. License: GPL-3.0-or-later.
