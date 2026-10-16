# Gran Turismo 2 — notes de recherche (menu de triche en surimpression)

But : comme [GranTurismo1-OverlayCheat](https://github.com/soaresden/GranTurismo1-OverlayCheat),
SELECT maintenu → un menu par-dessus le jeu : FREEZE TIMER (chrono des permis) et MONEY
(crédits en direct).

Relevés sur **GT2 Plus beta 7, disque combiné Europe (SCES-12380)**, PCSX-Redux + BIOS
SCPH-5502, outils `tools/emu` (repris du projet GT1).

## Mémoire

| Adresse | Rôle | Vérifié |
|---|---|---|
| 0x801D1598 | crédits (u32) en mode GT | écrit 99 999 999 → affiché 99.999.999 sur la carte |
| 0x80046F44 | chrono du tour en cours (u32), 3 000 unités par seconde (+60 par image à 50 Hz) | mis à 0 en permis B-1 → l'affichage repart de 0:00 |

Pour comparer, les codes GameShark de la version US 1.2 placent les crédits à 0x801D1568
(+0x30 sur GT2 Plus PAL).

## Programme

- `SCES_123.80` (PS-X EXE, chargé à 0x80010000, point d'entrée 0x8005D640) : la partie
  **résidente** va de 0x8005D640 à 0x800A9000 ; ce qui est avant est remplacé par un overlay.
- `GT2.OVL` : 6 overlays gzippés (table de 6 × (u32 offset, u32 taille) en tête ; noms de
  GT2OVLTool : overlay0, global, arcade, overlay3, gt, overlay5). **overlay0 = la course**,
  chargé à 0x80010000 (0x4D640 octets, jusqu'au point d'entrée du résident). Le chrono
  0x80046F44 est dans ses données.
- Les overlays de GT2 Plus et du jeu d'origine ont presque la même taille : les adresses
  devront être vérifiées (ou cherchées par motif) pour chaque version.

## Points d'accroche (trouvés avec les points d'arrêt de PCSX-Redux, `--interp --debugger`)

| Adresse | Rôle |
|---|---|
| 0x801F0CC8 | port 1 tel que libpad le reçoit (état, type, boutons, 0 = appuyé), écrit en 0x80089C80 |
| 0x8007F9C0 | mise à jour de la manette du jeu (lit 0x801F0CC8 en 0x8007FCF4), installée comme callback en 0x8007F97C / 0x8007F980 |
| 0x800802E0 | dessin d'une table d'ordre (DMA 2 en 0x80082BFC), appelé en 0x8007FF90 et 0x80080D04 |
| 0x8003D154 (overlay de course) | ajoute 0x3C (ou 0x78 à 25 images/s) au chrono, l'écrit en 0x8003D1C4 |
| 0x801D5896 | mode de course, 3 en permis (lu par la fonction du chrono) |

`SCES_123.80` ne diffère que de 12 octets entre le jeu d'origine et GT2 Plus beta 7, et aucune
de ces adresses n'en fait partie ; la fonction du chrono est à la même adresse dans les deux
overlays de course. Le patch est vérifié sur le disque combiné d'origine et sur GT2 Plus combiné.

Mémoire basse : zéros de 0x8000E500 à 0x80010000 dans tous les modes ; le bloc résident va à
0x8000F000, son état à 0x8000FF80.
