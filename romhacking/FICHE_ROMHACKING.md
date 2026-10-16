# Fiche romhacking.net — Gran Turismo 2 Overlay Cheat

Textes à copier dans le formulaire « Submit a hack ». Le site est en anglais ; la version
française de la description est en bas, si tu veux la mettre dans le readme ou ailleurs. La
fiche de GT1 est dans le dépôt GranTurismo1-OverlayCheat (`romhacking/FICHE_ROMHACKING.md`) :
deux envois séparés, un par jeu.

## Fichiers à envoyer

- **Patch** : `GT2-OverlayCheat-v1.0.zip` (https://raw.githubusercontent.com/soaresden/GranTurismo2-OverlayCheat/main/romhacking/GT2-OverlayCheat-v1.0.zip) (PPF + xdelta + README.txt + LISEZMOI.txt)
- **Captures** (PNG, résolution d'origine du jeu), dans cet ordre ; romhacking.net les prend
  par URL, les adresses directes sur GitHub sont sous chaque ligne :
  1. `screenshots/0_menu_language_screen.png` — le menu sur l'écran des langues (368 × 480)
     https://raw.githubusercontent.com/soaresden/GranTurismo2-OverlayCheat/main/romhacking/screenshots/0_menu_language_screen.png
  2. `screenshots/1_menu_city_map.png` — le menu sur la carte du mode GT (512 × 504)
     https://raw.githubusercontent.com/soaresden/GranTurismo2-OverlayCheat/main/romhacking/screenshots/1_menu_city_map.png
  3. `screenshots/2_menu_licence_test.png` — le menu pendant le permis B-1 (320 × 256)
     https://raw.githubusercontent.com/soaresden/GranTurismo2-OverlayCheat/main/romhacking/screenshots/2_menu_licence_test.png
  4. `screenshots/3_licence_timer_frozen.png` — le chrono figé en permis (320 × 256)
     https://raw.githubusercontent.com/soaresden/GranTurismo2-OverlayCheat/main/romhacking/screenshots/3_licence_timer_frozen.png

## Champs du formulaire

| Champ | Valeur |
|---|---|
| Title | Gran Turismo 2 Overlay Cheat Menu |
| Hack of | Gran Turismo 2 |
| Platform | PlayStation |
| Category | Cheat *(sinon : Improvement)* |
| Status | Fully Playable |
| Version | 1.0 |
| Release date | 2026-10-16 |
| Language | English *(le menu ; le jeu reste dans sa langue)* |
| Author | soaresden |
| Website | https://github.com/soaresden/GranTurismo2-OverlayCheat |
| Region / version | PAL (Europe), Simulation disc (Disc 2, SCES-12380, "Gran Turismo Mode") |
| Patch format | PPF 3.0 and xdelta3 |

**ROM / ISO information** (champ « Source ROM ») :

```
Gran Turismo 2 (Europe) (En,Fr,De,Es,It) (Disc 2) (Gran Turismo Mode).bin
Single track, 2352 bytes per sector, 710,226,384 bytes
CRC32: 64439308
SHA-1: c63a53bcf5ac6e49547a0c95b05174deff172021
```

**Short description** (une ligne) :

> Hold SELECT (or L1+R1+L2+R2) for an overlay menu: freeze the licence test timer and change your credits live.

**Description** :

```
An overlay cheat menu for Gran Turismo 2 (PAL). Hold SELECT, or press L1 + R1 + L2 + R2 together,
and a small menu appears over the game, anywhere: menus, dealers, races and licence tests.

- FREEZE TIMER: stops the clock of the licence tests. Turned on before the start, the clock stops
  at 0:00.040; stop in the target zone and the gold is yours.
- MONEY: change your credits live, with an adjustable step (R1 / L1), Triangle for the maximum
  (99,999,999) and Square for zero.

While the menu is open the game does not receive the pad; a short tap of SELECT is still given to
the game. The L1 + R1 + L2 + R2 combo keeps the menu open (START closes it): use it in RetroArch,
where SELECT is often the hotkey button.

The patch only changes SCES_123.80 and GT2.OVL (no game data is touched) and works on the
original Simulation disc. For the combined disc (GT2-Combined-Disc) and pez2k's GT2 Plus, use the
Python tool of the project (patch_disc.py), which takes a .chd, .cue or .bin.

Tested in PCSX-Redux (Sony BIOS and OpenBIOS) and in RetroArch / RALibretro with the Beetle PSX
core. Sources and technical notes on GitHub.
```

## Description en français

```
Un menu de triche en surimpression pour Gran Turismo 2 (PAL). Maintenez SELECT, ou appuyez
L1 + R1 + L2 + R2 ensemble, et un petit menu apparaît par-dessus le jeu, partout : menus,
concessionnaires, courses et permis.

- FREEZE TIMER : arrête le chronomètre des permis. Activé avant le départ, le chrono s'arrête à
  0:00.040 ; arrêtez-vous dans la zone et l'or est à vous.
- MONEY : changez vos crédits en direct, avec un pas réglable (R1 / L1), Triangle pour le maximum
  (99 999 999) et Carré pour zéro.

Tant que le menu est ouvert, le jeu ne reçoit plus la manette ; un appui bref sur SELECT reste
transmis au jeu. La combinaison L1 + R1 + L2 + R2 garde le menu ouvert (START le referme) : à
utiliser dans RetroArch, où SELECT est souvent la touche « hotkey ».

Le patch ne modifie que SCES_123.80 et GT2.OVL et marche sur le disque Simulation d'origine. Pour
le disque combiné (GT2-Combined-Disc) et GT2 Plus de pez2k, utilisez l'outil Python du projet
(patch_disc.py), qui prend un .chd, .cue ou .bin.

Essayé dans PCSX-Redux (BIOS Sony et OpenBIOS) et dans RetroArch / RALibretro avec le cœur
Beetle PSX. Sources et notes techniques sur GitHub.
```

## À vérifier avant d'envoyer

- Le CRC32 / SHA-1 de **ton** image du disque 2 doit être celui ci-dessus. Je n'ai pas pu le
  comparer à la fiche Redump (le site ne répondait pas) : si ta copie a d'autres valeurs, dis-le
  moi et je refais les patchs depuis la bonne image.
- Romhacking.net demande souvent que la première capture soit l'écran titre du jeu ; ici, la
  première montre le menu sur l'écran des langues, qui est le premier écran du jeu.
