# Gran Turismo 2 (PS1) — menu de triche en surimpression

🇬🇧 [English version](README.en.md)

Un patch pour **Gran Turismo 2** (PlayStation, version européenne, disque Simulation
**SCES-12380**) : en maintenant **SELECT**, un petit menu apparaît par-dessus le jeu, avec deux
options :

1. **FREEZE TIMER** — arrête le chronomètre des **permis** (licences) ;
2. **MONEY** — change les crédits **en direct** (pas réglable, maximum, zéro).

Il marche sur le disque Simulation d'origine, sur le **disque combiné**
([GT2-Combined-Disc](https://github.com/CookiePLMonster/GT2-Combined-Disc)) et sur **GT2 Plus**
(beta 7) de pez2k. Il ne touche que `SCES_123.80` et `GT2.OVL`, sans aucune donnée du jeu dans
ce dépôt. Il s'applique donc aussi à un disque déjà modifié ailleurs, par exemple le mod
[MX-5 RF](https://github.com/soaresden/MazdaMx5-nd-rf-ingames) du même auteur.

![Le menu sur la carte du mode GT](docs/menu_carte.png)
![Le menu pendant un permis, FREEZE TIMER activé](docs/menu_permis.png)

## Commandes (manette 1)

Deux façons d'ouvrir le menu `GT2 CHEAT`, en haut de l'écran :

- **SELECT maintenu** : le menu apparaît après un court instant et disparaît quand on relâche ;
- **L1 + R1 + L2 + R2 appuyés ensemble** : le menu s'ouvre et **reste ouvert** ; **START**
  (ou les quatre gâchettes à nouveau) le referme. C'est la façon à utiliser dans **Batocera /
  RetroArch**, où SELECT est la touche « hotkey » : tant qu'elle est maintenue, le jeu ne reçoit
  plus rien, et SELECT + une touche déclenche les raccourcis de l'émulateur.

Tant que le menu est ouvert, le jeu ne reçoit plus la manette.

| Touche | Ligne FREEZE TIMER | Ligne MONEY |
|---|---|---|
| ↑ / ↓ | change de ligne | change de ligne |
| ← / → | ON / OFF | − / + le pas (maintenu : répétition) |
| ✕ / ○ | ON / OFF | |
| R1 / L1 | | pas × 10 / ÷ 10 (de 1 à 10 000 000) |
| △ | | 99 999 999 (le maximum) |
| □ | | 0 |

- **FREEZE TIMER ON** : dans un permis, le chronomètre s'arrête là où il est. S'il était déjà
  ON au départ, il s'arrête à **0:00.040**, juste après le départ, car un permis dont le chrono
  reste à 0 ne se termine jamais. Le choix est gardé jusqu'à l'extinction de la console.
- **MONEY** : les crédits changent tout de suite (carte de la ville, concessionnaires…).
- Un appui **bref** sur SELECT, sans autre touche, est rendu au jeu quand on le relâche.

Essayé dans PCSX-Redux avec le BIOS PAL SCPH-5502 :
- sur GT2 Plus combiné : menu sur l'écran des langues, sur la carte de la ville et en permis ;
  crédits mis à jour à l'écran (99.999.999) ; en permis B-1, chrono figé jusqu'à la fin de
  l'épreuve, activé au départ comme en pleine course ;
- sur le disque combiné d'origine : menu sur la carte de la ville, crédits lus à la même adresse.

Essayé aussi dans **RALibretro avec le cœur Beetle PSX** (mednafen), sur GT2 Plus combiné avec la
MX-5 RF : le menu s'ouvre avec SELECT et avec L1 + R1 + L2 + R2. Sous Beetle, libpad ne relit pas
la manette à chaque trame ; la triche ignore les lectures déjà traitées.

## Appliquer le patch

**Disque Simulation d'origine** : un patch PPF ou xdelta, dans la
[release](https://github.com/soaresden/GranTurismo2-OverlayCheat/releases/latest) (dossier
`patch/`), à appliquer au `.bin` (une piste, 2352 octets par secteur ; CRC32 64439308, SHA-1
`c63a53bcf5ac6e49547a0c95b05174deff172021`).

**Tous les disques**, combiné et GT2 Plus compris, avec le script (Python 3, rien à installer) :

```bash
python patch_disc.py "Gran Turismo 2.chd"            # -> "Gran Turismo 2 [Cheat].bin" + .cue
python patch_disc.py "Gran Turismo 2.cue" "GT2 cheat.bin"
```

L'entrée peut être un `.chd`, un `.cue` ou un `.bin` du disque Simulation, d'un disque combiné ou
de GT2 Plus. Chaque mot modifié est vérifié avant : sur un autre jeu ou une autre version,
rien n'est écrit.

## Comment ça marche

`SCES_123.80` n'est pas compressé. De 0x80010000 au point d'entrée 0x8005D640, c'est la zone des
overlays (`GT2.OVL`, chargés plus tard) ; la suite est le code résident, toujours en mémoire.

- Le **chargeur** (`src/stub.S`) est logé dans des zéros de la zone des overlays, le point
  d'entrée de l'exécutable pointe sur lui. Il :
  1. copie le **bloc résident** (`src/start.S` + `src/cheat.c`, ≈ 2,4 Ko) à 0x8000F000, en
     mémoire basse libre, et efface sa copie ;
  2. appelle `cheat_boot`, qui modifie trois endroits du code résident après avoir vérifié
     qu'ils sont bien ceux attendus ;
  3. vide le cache d'instructions et saute au jeu.
- Les trois endroits du code résident, valables dans tous les overlays (menus, courses,
  permis) :

| Adresse | Origine | Patch |
|---|---|---|
| 0x8007F97C / 0x8007F980 | adresse du callback de la manette (0x8007F9C0, une fois par trame) | `pad_hook` : lit le port 1, gère le menu, masque la manette au jeu, puis appelle le callback du jeu |
| 0x8007FF90, 0x80080D04 | `jal 0x800802E0`, le dessin de la table d'ordre d'une image | `draw_hook` : une fois l'image dessinée (fin du DMA), dessine le menu par-dessus |

- Dans l'**overlay de course** (entrée 0 de `GT2.OVL`, chargée à 0x80010000), la fonction
  0x8003D154 ajoute au chrono du tour (0x80046F44, 3 000 par seconde) puis l'écrit en
  0x8003D1C4. Le patch remplace cette écriture par un saut vers `tick_store`, qui la saute en
  permis (0x801D5896 = 3) si FREEZE TIMER est actif et que le chrono a quitté 0. L'overlay est
  recompressé, et `GT2.OVL` reste dans ses secteurs.
- Crédits : 0x801D1598 (u32), la même adresse sur le jeu d'origine et sur GT2 Plus.

Dessin : primitives TILE envoyées directement au GPU (GP0), police 5×7 du projet (`src/font.py`),
taille doublée en 512 de large ou en 480 lignes, puis le mode de dessin du jeu est remis.

Les relevés (adresses, méthode) sont dans [NOTES.md](NOTES.md).

## Limites connues

- Manette 1 seulement (avec un multitap : sa prise A).
- Pendant que le menu est ouvert, le jeu ne voit plus la manette (en course, la voiture continue
  sans commandes).
- FREEZE TIMER n'agit que dans les permis, pas en course.
- Le chrono affiché peut bouger de quelques millièmes (le jeu lisse son affichage entre deux
  images) ; le temps compté reste celui du moment où il a été figé.

## Construire depuis les sources

- `src/cheat.c`, `src/start.S`, `src/stub.S`, `src/payload.ld`, `src/font.py` : le code ;
- `gt2cheat/game.py` : toutes les adresses du jeu ; `gt2cheat/patcher.py` : le patch ;
- `python build.py [--list]` : compile avec GCC MIPS (`mipsel-none-elf-*` de PSn00bSDK, ou
  `mips-linux-gnu-*`) et écrit `gt2cheat/payload.py` ;
- `tools/emu` : pilotage de PCSX-Redux pour les essais, repris du projet GT1 ; `tools/ra.py` :
  désassemblage et recherche de références (capstone).

## Licence

GPL-3.0-or-later. Gran Turismo est une marque de Sony Interactive Entertainment ; projet de fan,
sans lien avec Sony ni Polyphony Digital.
