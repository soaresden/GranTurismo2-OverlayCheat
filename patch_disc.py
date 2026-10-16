"""Gran Turismo 2 (PAL, Simulation disc SCES-12380, combined disc or GT2 Plus): add the overlay
cheat menu to your disc image.

    python patch_disc.py "Gran Turismo 2.chd"                    -> "Gran Turismo 2 [Cheat].bin/.cue"
    python patch_disc.py "Gran Turismo 2.cue" "GT2 cheat.bin"

The input can be the stock disc or a disc already modded in other files (the MX-5 mod, for
instance): only SCES_123.80 and GT2.OVL change, in their place on the disc, and the words changed
are checked first. Python 3 only, nothing to install.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt2cheat import patcher  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('src', help='.chd, .cue or .bin of Gran Turismo 2 PAL (SCES-12380)')
    ap.add_argument('dst', nargs='?', help='output .bin (a .cue is written next to it)')
    a = ap.parse_args()
    try:
        dst = a.dst or os.path.splitext(a.src)[0] + ' [Cheat].bin'
        if not dst.lower().endswith('.bin'):
            dst += '.bin'
        patcher.patch_disc(a.src, dst, lambda i, n: print('\r%3d %%' % (100 * i // n), end='', flush=True))
        print('\rwritten %s (+ .cue)' % dst)
    except (patcher.PatchError, ValueError, OSError) as e:
        sys.exit('error: %s' % e)


if __name__ == '__main__':
    main()
