#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
douche.py - Un mini-film en caractères ASCII : comment prendre une douche,
étape par étape, avec une barre de progression vers la propreté, puis un
petit questionnaire final.

Bibliothèque standard uniquement : aucun paquet externe à installer.

Usage :
    python douche.py                  # lecture automatique
    python douche.py --pas-a-pas      # Entrée pour passer à l'étape suivante
    python douche.py --vitesse 2      # deux fois plus rapide (0.5 = deux fois plus lent)
    python douche.py --sans-quiz      # n'affiche pas le questionnaire final
"""

import argparse
import math
import os
import random
import shutil
import sys
import textwrap
import time
from dataclasses import dataclass

# --------------------------------------------------------------------------
# Réglages de l'affichage
# --------------------------------------------------------------------------
LARGEUR = 50            # largeur de la scène (en caractères)
HAUTEUR = 29            # hauteur de la scène (en lignes)
X_JET = 20              # colonne du pommeau de douche
X_DOUCHE = 20           # centre du personnage sous le jet
X_COTE = 41             # centre du personnage à côté du jet
Y_SOL = 28              # ligne du sol
Y_TETE = 6              # ligne du haut de la tête
X_AIDE = 32             # position de la personne qui frotte le dos
DELAI_IMAGE = 0.12      # secondes entre deux images (à vitesse 1)
LARGEUR_BARRE = 30      # largeur de la barre de progression
LARGEUR_TEXTE = 56      # largeur de la zone de texte sous l'animation
LIGNES_TEXTE = 3        # nombre de lignes réservées à la description
LIGNES_ECRAN = HAUTEUR + 8

VISAGES = {
    "normal": ("o   o", "\\_/"),
    "yeux_fermes": ("-   -", "\\_/"),
    "content": ("^   ^", "\\_/"),
    "perplexe": ("o   o", "-.-"),
}
MIROIR = {"/": "\\", "\\": "/", "(": ")", ")": "(", "{": "}", "}": "{"}


# --------------------------------------------------------------------------
# Description des étapes
# --------------------------------------------------------------------------
@dataclass
class Etape:
    titre: str
    texte: str
    propre: tuple                      # (% de propreté au début, à la fin)
    eau: bool = False                  # l'eau coule-t-elle ?
    place: str = "douche"              # "douche" (sous le jet) ou "cote"
    mousse_tete: tuple = (0.0, 0.0)    # niveau de mousse 0..1 (début, fin)
    mousse_corps: tuple = (0.0, 0.0)
    mousse_jambes: tuple = (0.0, 0.0)
    savon: str = ""                    # "", "corps", "jambes" ou "glisse"
    bras: str = "bas"                  # "bas", "tete", "corps", "jambes", "rincer", "deo_parfum"
    visage: str = "normal"
    serviette: int = 0                 # 0 aucune, 1 corps entier, 2 à la taille
    habits: tuple = (0.0, 0.0)         # 1 = habillé, 0 = déshabillé
    produit: str = ""                  # "deo_parfum"
    etiquette: str = ""
    frames: int = 36                   # durée de l'étape (en images)


ETAPES = [
    Etape(
        "Préparer la salle de bain",
        "Placez une serviette propre, des vêtements de rechange et vos produits "
        "(savon, shampoing, déodorant) à portée de main.",
        (0, 0), habits=(1, 1), frames=32,
    ),
    Etape(
        "Se déshabiller",
        "Retirez vos vêtements et posez-les au sec, loin des éclaboussures.",
        (0, 0), habits=(1, 0), frames=34,
    ),
    Etape(
        "Régler l'eau",
        "Ouvrez le robinet et réglez une eau tiède, autour de 37-38 °C. "
        "Vérifiez la température avant d'entrer sous le jet.",
        (0, 0), eau=True, place="cote", etiquette="38°C", frames=36,
    ),
    Etape(
        "Se mouiller",
        "Placez-vous sous le jet et mouillez tout le corps, des cheveux "
        "jusqu'aux pieds.",
        (0, 10), eau=True, bras="corps", visage="yeux_fermes", frames=40,
    ),
    Etape(
        "Shampoing",
        "Coupez l'eau (facultatif). Faites mousser une noix de shampoing sur le "
        "cuir chevelu, avec les deux mains, en massant doucement.",
        (10, 30), mousse_tete=(0.0, 1.0), bras="tete", visage="yeux_fermes",
        frames=48,
    ),
    Etape(
        "Rincer les cheveux",
        "Rouvrez l'eau et rincez abondamment, jusqu'à ce que l'eau coule "
        "claire et sans mousse.",
        (30, 45), eau=True, mousse_tete=(1.0, 0.0), bras="tete",
        visage="yeux_fermes", frames=40,
    ),
    Etape(
        "Le savon, mode d'emploi",
        "Le savon : un bloc glissant qui rêve de s'évader. Si vous ne savez pas "
        "l'utiliser, demandez à quelqu'un de vous montrer (ou de vous frotter le dos).",
        (45, 45), savon="glisse", visage="perplexe", frames=84,
    ),
    Etape(
        "Savonner le haut du corps",
        "Appliquez gel douche ou savon : bras, épaules, torse, ventre et dos. "
        "Faites mousser sans frotter trop fort.",
        (45, 70), mousse_corps=(0.0, 1.0), savon="corps", bras="corps", frames=56,
    ),
    Etape(
        "Jambes, pieds et plis",
        "Continuez par les jambes et les pieds (entre les orteils), puis les "
        "zones de plis avec un produit doux.",
        (70, 85), mousse_corps=(1.0, 1.0), mousse_jambes=(0.0, 1.0),
        savon="jambes", bras="jambes", frames=48,
    ),
    Etape(
        "Rincer tout le corps",
        "Rincez de haut en bas jusqu'à la disparition complète de la mousse.",
        (85, 96), eau=True, mousse_corps=(1.0, 0.0), mousse_jambes=(1.0, 0.0),
        bras="rincer", visage="yeux_fermes", frames=40,
    ),
    Etape(
        "Se sécher",
        "Fermez le robinet, essorez vos cheveux puis séchez-vous avec la "
        "serviette en tamponnant, de la tête aux pieds.",
        (96, 98), serviette=1, bras="corps", visage="content", frames=40,
    ),
    Etape(
        "Déodorant et parfum",
        "Une fois sec, appliquez votre déodorant, puis un petit coup de "
        "parfum (un seul pschit suffit).",
        (98, 100), serviette=2, bras="deo_parfum", visage="content",
        produit="deo_parfum", frames=56,
    ),
    Etape(
        "Se rhabiller",
        "Enfilez vos vêtements propres. Le linge sale va dans le panier.",
        (100, 100), visage="content", habits=(0, 1), frames=40,
    ),
]


# --------------------------------------------------------------------------
# Questionnaire final
# --------------------------------------------------------------------------
QUESTIONS = [
    ("Avant d'entrer sous le jet, que faut-il faire ?",
     ["Vérifier la température de l'eau", "Mettre du parfum", "Se rhabiller"], 0,
     "On règle l'eau avant d'entrer pour ne pas se brûler ni geler."),
    ("Quelle température d'eau est conseillée ?",
     ["Environ 37-38 °C", "Bouillante", "Glacée"], 0,
     "Une eau tiède est agréable et ménage la peau."),
    ("Après le shampoing, que fait-on ?",
     ["On rince abondamment les cheveux", "On met le déodorant",
      "On sort de la douche en mousse"], 0,
     "Le shampoing se rince jusqu'à ce que l'eau soit claire."),
    ("Comment utilise-t-on un savon ?",
     ["On le mouille, on se frotte avec, on rince",
      "On le croque, c'est bon pour les dents",
      "On le pose sur la tête et on attend"], 0,
     "Si vous avez hésité : demandez à quelqu'un de vous le montrer !"),
    ("Jusqu'à quand rince-t-on le corps ?",
     ["Jusqu'à disparition complète de la mousse", "Jusqu'à ce que l'eau soit froide",
      "Dix secondes, au hasard"], 0,
     "Il ne doit plus rester de mousse sur la peau."),
    ("Quand met-on déodorant et parfum ?",
     ["Après s'être séché, avant de se rhabiller", "Avant d'entrer sous la douche",
      "Sous le jet, pour gagner du temps"], 0,
     "Sur une peau propre et sèche, ils tiennent mieux."),
]


def questionnaire():
    """Pose les questions dans le terminal et affiche le score."""
    sys.stdout.write("\033[2J\033[H")
    print("=== PETIT QUESTIONNAIRE ===\n")
    print("Avez-vous bien compris comment prendre une douche ?")
    print("Répondez avec le numéro de votre choix.")
    score = 0
    total = len(QUESTIONS)
    for n, (question, choix, bonne, explication) in enumerate(QUESTIONS, 1):
        ordre = list(range(len(choix)))
        random.shuffle(ordre)
        print(f"\nQuestion {n}/{total} : {question}")
        for pos, idx in enumerate(ordre, 1):
            print(f"  {pos}. {choix[idx]}")
        while True:
            reponse = input(f"Votre réponse (1-{len(choix)}) : ").strip()
            if reponse.isdigit() and 1 <= int(reponse) <= len(choix):
                break
            print("Entrez simplement un numéro de la liste.")
        if ordre[int(reponse) - 1] == bonne:
            score += 1
            print("  Bonne réponse ! " + explication)
        else:
            print("  Pas tout à fait. Bonne réponse : " + choix[bonne] + ". " + explication)
    print(f"\nScore final : {score}/{total}")
    if score == total:
        print("Parfait ! Vous êtes un as de la douche.")
    elif score >= total - 2:
        print("Très bien. Quelques détails à revoir, mais l'essentiel y est.")
    else:
        print("Relancez l'animation avec --pas-a-pas pour revoir les étapes.")


# --------------------------------------------------------------------------
# Outils de dessin
# --------------------------------------------------------------------------
def arrondi(v):
    return int(math.floor(v + 0.5))


def valeur(plage, t):
    return plage[0] + (plage[1] - plage[0]) * t


def niveau(plage, t):
    """Convertit une plage (début, fin) et l'avancement t (0..1) en niveau 0/1/2."""
    v = valeur(plage, t)
    if v < 0.05:
        return 0
    return 1 if v < 0.5 else 2


def poser(grille, x, y, texte, opaque=False):
    """Écrit `texte` dans la grille ; les espaces sont transparents sauf si opaque."""
    if not 0 <= y < HAUTEUR:
        return
    for i, c in enumerate(texte):
        if 0 <= x + i < LARGEUR and (opaque or c != " "):
            grille[y][x + i] = c


def poser_sprite(grille, x, y, ligne):
    """Pose une ligne du personnage : opaque entre ses deux bords, transparent autour."""
    debut = len(ligne) - len(ligne.lstrip())
    fin = len(ligne.rstrip())
    poser(grille, x + debut, y, ligne[debut:fin], opaque=True)


def mousse(n, niv, graine):
    """Chaîne de mousse de longueur n (niv 1 = légère, 2 = dense)."""
    if niv == 0:
        return " " * n
    motif = "oO*oO" if niv == 2 else "o  . "
    return "".join(motif[(i * 7 + graine * 13) % len(motif)] for i in range(n))


# --------------------------------------------------------------------------
# Le personnage (tronc et jambes), puis les bras
# --------------------------------------------------------------------------
def construire_personne(visage, nt, nc, nj, habille, serv, f, haut="=", bas="#"):
    """Retourne les 22 lignes (13 caractères) du personnage, sans les bras."""
    graine = f // 3
    yeux, bouche = VISAGES[visage]

    if nt == 2:
        sommet = "  (" + mousse(7, 2, graine) + ")  "
    elif nt == 1:
        sommet = "   " + mousse(7, 1, graine) + "   "
    else:
        sommet = "   .-----.   "
    lignes = [
        sommet,
        "  /       \\  ",
        f" |  {yeux}  | ",
        " |    ^    | ",
        f"  \\  {bouche}  /  ",
        "   '-----'   ",
        "     | |     ",
    ]

    def interieur(i):
        if serv == 1:
            return "#######"
        if habille:
            return haut * 7
        if nc:
            return mousse(7, nc, graine + i)
        return " " * 7

    lignes.append("  .#######.  " if serv == 1 else "  .-'---'-.  ")
    for i in range(1, 7):
        lignes.append("  |" + interieur(i) + "|  ")

    if serv or habille:
        hanches = "#######"
    elif nj:
        hanches = mousse(7, nj, graine + 9)
    else:
        hanches = "_______"
    lignes.append("  |" + hanches + "|  ")

    for k in range(6):
        if serv == 2 and k < 3:
            lignes.append("  |#######|  ")
            continue
        if habille:
            c1 = c2 = bas
        elif nj:
            m = mousse(2, nj, graine + k)
            c1, c2 = m[0], m[1]
        else:
            c1 = c2 = " "
        lignes.append(f"  |{c1}|   |{c2}|  ")
    if habille:
        lignes.append(f" _|{bas}|   |{bas}|_ ")
    elif nj:
        m = mousse(2, nj, graine + 7)
        lignes.append(f" _|{m[0]}|   |{m[1]}|_ ")
    else:
        lignes.append(" _| |   | |_ ")
    return lignes


def segment(a, b):
    """Caractères à placer entre deux articulations (extrémités exclues)."""
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    n = max(abs(dx), abs(dy))
    if dy == 0:
        c = "_"
    else:
        rapport = abs(dx) / abs(dy)
        if rapport < 0.5:
            c = "|"
        elif rapport > 2:
            c = "_"
        else:
            c = "\\" if dx * dy > 0 else "/"
    return [(arrondi(x1 + dx * i / n), arrondi(y1 + dy * i / n), c) for i in range(1, n)]


def articulations(pose, f, sw=0):
    """Épaule, coude, main, caractère de la main et du coude du bras GAUCHE.

    Les x sont relatifs au bord gauche du personnage, les y à son sommet de tête.
    """
    if pose == "tete":                                  # mains sur la tête qui frottent
        hs = (0, 1, 2, 1)[(f // 2) % 4]
        main = (1 if hs == 0 else 0, 1 + hs)
        coude = (-3 - (hs % 2), 5 + hs // 2)
        return (1, 7), coude, main, ("(" if (f // 2) % 2 == 0 else "{"), "o"
    if pose == "corps":                                 # main qui balaie le torse
        hx = 4 + arrondi(2 * math.sin(f / 1.5))
        hy = 9 + (0, 1, 2, 1)[(f // 3) % 4]
        return (1, 7), (-2, 11), (hx, hy), "o", "o"
    if pose == "jambes":                                # main qui descend le long de la jambe
        hs = (0, 1, 2, 3, 2, 1)[(f // 2) % 6]
        return (1, 7), (-3, 11), (-1, 15 + hs), "o", "o"
    if pose == "deo":                                   # bras plié, bombe au creux du bras
        return (1, 7), (-1, 10), (-3, 8 + (0, 0, 1, 1)[(f // 3) % 4]), "o", "o"
    if pose == "parfum":                                # bras plié, flacon à hauteur d'épaule
        return (1, 7), (-1, 10), (-2, 7), "o", "o"
    if pose == "dos":                                   # bras de l'aide qui frotte le dos
        return (1, 7), (-2, 10), (-4, 8 + (0, 1, 2, 1)[(f // 2) % 4]), "o", "o"
    return (1, 7), (-sw, 10), (1, 13), "'", None        # "bas" : bras le long du corps


def dessiner_bras(g, x0, y0, pose, cote, f, sw=0):
    """Dessine un bras ; retourne la position (x, y) de sa main."""
    epaule, coude, main, car_main, car_coude = articulations(pose, f, sw)
    cellules = [(epaule[0], epaule[1], "_")]
    cellules += segment(epaule, coude) + segment(coude, main)
    cellules.append((coude[0], coude[1], car_coude or "|"))
    cellules.append((main[0], main[1], car_main))
    for x, y, c in cellules:
        if cote == "d":
            x, c = 12 - x, MIROIR.get(c, c)
        poser(g, x0 + x, y0 + y, c)
    return (main[0] if cote == "g" else 12 - main[0]), main[1]


def poses_des_bras(e, t, f):
    """Retourne (pose gauche, pose droite, côté actif) pour l'image courante."""
    pose = e.bras
    if pose == "rincer":
        pose = "corps" if t < 0.55 else "jambes"
    if pose == "tete":
        return "tete", "tete", None
    if pose in ("corps", "jambes"):
        periode = 16 if pose == "corps" else 24
        if (f // periode) % 2 == 0:
            return pose, "bas", "g"
        return "bas", pose, "d"
    if pose == "deo_parfum":
        return ("deo", "bas", "g") if t < 0.5 else ("bas", "parfum", "d")
    return "bas", "bas", None


# --------------------------------------------------------------------------
# Dessin de la scène
# --------------------------------------------------------------------------
def dessiner_scene(e, t, f):
    """Retourne la liste des lignes de la scène pour l'étape e, avancement t, image f."""
    g = [[" "] * LARGEUR for _ in range(HAUTEUR)]
    px = X_DOUCHE if e.place == "douche" else X_COTE
    x0 = px - 6
    alt = (f // 3) % 2 == 0
    graine = f // 3
    nt = niveau(e.mousse_tete, t)
    nc = niveau(e.mousse_corps, t)
    nj = niveau(e.mousse_jambes, t)
    habille = valeur(e.habits, t) >= 0.5

    # Sol, tuyau et pommeau de douche
    poser(g, 0, Y_SOL, "=" * LARGEUR)
    poser(g, 0, 0, "=" * X_JET + "+")
    poser(g, X_JET, 1, "|")
    poser(g, X_JET - 8, 2, ".-" + "'" * 13 + "-.")
    poser(g, X_JET - 8, 3, "'-" + (".:" * 7)[:13] + "-'")

    # Eau qui coule (chaque colonne tombe à sa propre vitesse)
    if e.eau:
        for x in range(X_JET - 7, X_JET + 8):
            for y in range(4, Y_SOL - 1):
                p = (y - f * (1 + x % 2) + 3 * x) % 5
                if p == 0:
                    g[y][x] = "|"
                elif p == 3:
                    g[y][x] = "."
        for x in range(X_JET - 8, X_JET + 9):        # éclaboussures au sol
            g[Y_SOL - 1][x] = ".,' ."[(f + x) % 5]

    # Bulles flottantes autour de la personne
    if (nt or nc or nj) and not e.eau:
        hasard = random.Random(f)
        for _ in range(10):
            bx = hasard.randint(x0 - 6, x0 + 19)
            by = hasard.randint(5, Y_SOL - 3)
            c = hasard.choice("oO.")
            if 0 <= bx < LARGEUR and g[by][bx] == " ":
                g[by][bx] = c

    # Mousse au-dessus de la tête
    if nt:
        poser(g, x0 + 2, Y_TETE - 1, mousse(9, nt, graine + 1))
        if nt == 2:
            poser(g, x0 + 3, Y_TETE - 2, mousse(7, 2, graine + 2))

    # Le personnage
    visage = e.visage
    if e.savon == "glisse":
        visage = "perplexe" if t < 0.30 else "content"
    for k, ligne in enumerate(construire_personne(visage, nt, nc, nj, habille, e.serviette, f)):
        poser_sprite(g, x0, Y_TETE + k, ligne)

    # Panneau de censure
    if not habille and e.serviette == 0:
        poser(g, x0 + 1, Y_TETE + 15, "[CENSORED]", True)

    # Les bras, toujours en mouvement
    pose_g, pose_d, actif = poses_des_bras(e, t, f)
    sw_g = (f // 6) % 2
    sw_d = ((f + 3) // 6) % 2
    main_g = dessiner_bras(g, x0, Y_TETE, pose_g, "g", f, sw_g)
    main_d = dessiner_bras(g, x0, Y_TETE, pose_d, "d", f, sw_d)

    # Savon tenu dans la main active
    if e.savon in ("corps", "jambes") and actif:
        hx, hy = main_g if actif == "g" else main_d
        poser(g, x0 + hx - 1, Y_TETE + hy, "[:]", True)

    # Étape du savon : il rebondit, puis quelqu'un vient frotter le dos et repart
    if e.savon == "glisse":
        if t < 0.30:
            y = 26 - int(abs(math.sin(f / 4)) * 9)
            x = x0 + 14 + int(8 * math.sin(f / 8))
            poser(g, x, y, "[:::]", True)
            poser(g, x0 + 1, Y_TETE - 2 + (0 if alt else 1), "?")
            poser(g, x0 + 11, Y_TETE - 1 - (0 if alt else 1), "?")
        ax = None
        if 0.30 <= t < 0.45:
            ax = arrondi(54 + (X_AIDE - 54) * (t - 0.30) / 0.15)
        elif 0.45 <= t < 0.75:
            ax = X_AIDE
        elif 0.75 <= t < 0.90:
            ax = arrondi(X_AIDE + (54 - X_AIDE) * (t - 0.75) / 0.15)
        if ax is not None:
            frotte = 0.45 <= t < 0.75
            saut = -1 if (not frotte and (f // 2) % 2 == 0) else 0
            for k, ligne in enumerate(construire_personne(
                    "content", 0, 0, 0, True, 0, f, haut="+")):
                poser_sprite(g, ax, Y_TETE + k + saut, ligne)
            dessiner_bras(g, ax, Y_TETE + saut, "dos" if frotte else "bas", "g", f,
                          (f // 2) % 2)
            dessiner_bras(g, ax, Y_TETE + saut, "bas", "d", f, ((f // 2) + 1) % 2)
            if frotte:
                hx, hy = articulations("dos", f)[2]
                poser(g, ax + hx - 1, Y_TETE + hy, "[:]", True)
                poser(g, ax + hx - 1, Y_TETE + hy - 1, "o" if alt else ".")
                paroles = ("Plus haut !", "Plus bas !", "Parfait, merci !")
                poser(g, x0 - 1, Y_TETE - 2, paroles[min(2, int((t - 0.45) / 0.30 * 3))])
            elif t < 0.45:
                poser(g, min(ax + 1, LARGEUR - 8), Y_TETE - 2, "Coucou !")
            else:
                poser(g, min(ax - 1, LARGEUR - 14), Y_TETE - 2, "Bonne douche !")

    # Habillage / déshabillage
    if e.habits[0] != e.habits[1] and 0.45 <= t < 0.65:
        poser(g, x0 + 14, Y_TETE + 8, "hop !")

    # Déodorant puis parfum
    if e.produit == "deo_parfum":
        if t < 0.5:
            hx, hy = main_g
            poser(g, x0 + hx - 1, Y_TETE + hy, "[D]", True)
            poser(g, x0 + hx + 2, Y_TETE + hy, ".:." if alt else ":.:")
            poser(g, x0 - 10, Y_TETE + 4, "PSHHT !")
        else:
            hx, hy = main_d
            poser(g, x0 + hx + 1, Y_TETE + hy, "[P]", True)
            poser(g, x0 + 8, Y_TETE + 6, ".*:." if alt else "*.:*")
            poser(g, x0 + 15, Y_TETE + 3, "pschit !")

    # Étincelles quand on est propre
    if e.visage == "content":
        etoile = "*" if alt else "+"
        for dx, dy in ((-9, 8), (17, 9), (-8, 18), (18, 17), (-6, 4), (16, 5)):
            poser(g, px + dx, dy, etoile)

    # Thermomètre
    if e.etiquette:
        poser(g, 30, 2, f"[ {e.etiquette} ]")

    return ["".join(ligne) for ligne in g]


def barre(pct):
    plein = round(LARGEUR_BARRE * pct / 100)
    return "[" + "#" * plein + "-" * (LARGEUR_BARRE - plein) + "]"


def composer_ecran(e, numero, total, t, f, aide):
    """Assemble l'écran complet : scène + étape + barre de progression."""
    pct = valeur(e.propre, t)
    marge = " " * ((LARGEUR_TEXTE - LARGEUR) // 2)

    lignes = ["=== COMMENT PRENDRE UNE DOUCHE ===".center(LARGEUR_TEXTE)]
    lignes += [marge + ligne for ligne in dessiner_scene(e, t, f)]
    lignes.append("-" * LARGEUR_TEXTE)
    lignes.append(f"Étape {numero}/{total} : {e.titre}")

    texte = textwrap.wrap(e.texte, LARGEUR_TEXTE)[:LIGNES_TEXTE]
    texte += [""] * (LIGNES_TEXTE - len(texte))
    lignes += texte

    lignes.append(f"Propreté {barre(pct)} {pct:3.0f} %")
    lignes.append(aide)
    return lignes


# --------------------------------------------------------------------------
# Terminal
# --------------------------------------------------------------------------
def afficher(lignes):
    """Redessine l'écran sur place (curseur en haut à gauche, sans clignotement)."""
    sys.stdout.write("\033[H" + "\n".join(l + "\033[K" for l in lignes) + "\033[J")
    sys.stdout.flush()


def preparer_terminal():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if os.name == "nt":
        os.system("")          # active les séquences ANSI dans la console Windows


def verifier_taille():
    taille = shutil.get_terminal_size((80, 40))
    if taille.columns < LARGEUR_TEXTE or taille.lines < LIGNES_ECRAN + 1:
        print(
            f"Agrandissez la fenêtre : il faut au moins {LARGEUR_TEXTE} colonnes "
            f"x {LIGNES_ECRAN + 1} lignes (actuellement {taille.columns} x {taille.lines})."
        )
        print("Astuce : passez en plein écran ou réduisez la taille de la police (Ctrl et -).")
        if sys.stdin.isatty():
            input("Puis appuyez sur Entrée pour lancer l'animation...")


def lire_arguments():
    p = argparse.ArgumentParser(description="Animation ASCII : prendre une douche.")
    p.add_argument("--vitesse", type=float, default=1.0,
                   help="multiplicateur de vitesse (défaut : 1.0)")
    p.add_argument("--pas-a-pas", action="store_true",
                   help="attend la touche Entrée entre chaque étape")
    p.add_argument("--sans-quiz", action="store_true",
                   help="n'affiche pas le questionnaire final")
    args = p.parse_args()
    if args.vitesse <= 0:
        p.error("--vitesse doit être strictement positif")
    return args


# --------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------
def main():
    args = lire_arguments()
    preparer_terminal()
    verifier_taille()

    total = len(ETAPES)
    f = 0
    try:
        sys.stdout.write("\033[2J\033[?25l")        # efface l'écran, cache le curseur
        for i, e in enumerate(ETAPES, 1):
            for k in range(e.frames):
                t = k / max(1, e.frames - 1)
                afficher(composer_ecran(e, i, total, t, f, "(Ctrl+C pour quitter)"))
                time.sleep(DELAI_IMAGE / args.vitesse)
                f += 1
            if args.pas_a_pas and i < total:
                afficher(composer_ecran(
                    e, i, total, 1.0, f,
                    "Appuyez sur Entrée pour passer à l'étape suivante..."))
                input()

        time.sleep(1.5 / args.vitesse)
        sys.stdout.write("\033[2J\033[H\033[?25h")
        print("Vous êtes tout propre ! Récapitulatif :\n")
        for i, e in enumerate(ETAPES, 1):
            print(f"  {i:2d}. {e.titre}")

        if not args.sans_quiz:
            input("\nAppuyez sur Entrée pour passer au petit questionnaire...")
            questionnaire()
        else:
            print("\nAstuce : relancez avec --pas-a-pas pour avancer à votre rythme.")
    except (KeyboardInterrupt, EOFError):
        sys.stdout.write("\033[2J\033[H")
        print("Programme interrompu. À bientôt !")
    finally:
        sys.stdout.write("\033[?25h")               # réaffiche le curseur
        sys.stdout.flush()


if __name__ == "__main__":
    main()
