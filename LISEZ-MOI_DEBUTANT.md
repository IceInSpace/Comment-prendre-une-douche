# Guide d'installation et de lancement — débutants

Ce guide vous explique, pas à pas, comment installer ce qu'il faut et lancer
le programme. Aucune connaissance en programmation n'est nécessaire.
Comptez environ 10 minutes.

---

## Contenu du dossier

| Fichier | À quoi il sert |
|---|---|
| `douche.py` | Le programme à lancer |
| `lancer.bat` | Lanceur pour **Windows** (double-clic) |
| `lancer.sh` | Lanceur pour **macOS / Linux** |
| `requirements.txt` | Liste des paquets à installer (ici : aucun) |
| `README_AVANCE.md` | Version pour utilisateurs expérimentés |

---

## À savoir : l'« environnement virtuel »

Un **environnement virtuel** est un dossier à part (`.venv`) qui contient sa
propre copie de Python. Le programme tourne **dedans** : votre Python et vos
bibliothèques déjà installés ne sont jamais modifiés. Les lanceurs fournis le
créent tout seuls, une seule fois.

Pour tout effacer un jour : supprimez simplement le dossier `.venv`.

---

## Étape 1 — Installer Python (si besoin)

Version requise : **Python 3.8 ou plus récent**.

### Windows
1. Allez sur <https://www.python.org/downloads/> et téléchargez la dernière version.
2. Lancez l'installateur.
3. ⚠️ **Cochez la case « Add python.exe to PATH »** en bas de la fenêtre, puis cliquez sur *Install Now*.

### macOS
1. Téléchargez l'installateur sur <https://www.python.org/downloads/> et suivez les étapes.
2. (Avec Homebrew : `brew install python`.)

### Linux (Ubuntu / Debian)
Dans un terminal :
```bash
sudo apt update
sudo apt install python3 python3-venv
```
(Le paquet `python3-venv` est indispensable pour créer l'environnement.)

---

## Étape 2 — Récupérer le dossier

Placez le dossier `douche_animee` où vous voulez (Bureau, Documents…).
Si vous l'avez reçu en `.zip`, faites un clic droit → **Extraire tout**
(Windows) ou double-cliquez dessus (macOS) **avant** de continuer.

---

## Étape 3 — Préparer la fenêtre

Le programme demande une fenêtre assez grande : au moins **56 colonnes × 38 lignes**.
Passez la fenêtre en **plein écran**, ou réduisez la taille de la police
(touches `Ctrl` et `-`).

---

## Étape 4 — Lancer

### Windows
Double-cliquez sur **`lancer.bat`**.
La première fois, patientez quelques secondes : l'environnement se crée, puis le programme démarre.

### macOS / Linux
1. Ouvrez l'application **Terminal**.
2. Allez dans le dossier (exemple s'il est sur le Bureau) :
   ```bash
   cd ~/Desktop/douche_animee
   ```
   Astuce : tapez `cd ` puis glissez le dossier dans la fenêtre du Terminal.
3. Rendez le lanceur exécutable (une seule fois), puis lancez-le :
   ```bash
   chmod +x lancer.sh
   ./lancer.sh
   ```

---

## Options de lancement

Ajoutez-les à la suite de la commande, dans un terminal ouvert dans le dossier :

| Option | Effet |
|---|---|
| `--pas-a-pas` | Avancer avec la touche Entrée |
| `--vitesse 2` | Deux fois plus rapide (`0.5` = deux fois plus lent) |
| `--sans-quiz` | Ne pas afficher le questionnaire de fin |

Exemples :
- Windows : `lancer.bat --pas-a-pas`
- macOS / Linux : `./lancer.sh --vitesse 2`

Pour **quitter** à tout moment : touches `Ctrl` + `C`.

---

## Si ça ne marche pas

| Problème | Solution |
|---|---|
| *« Python est introuvable »* | Python n'est pas installé, ou la case **Add to PATH** n'a pas été cochée (Windows). Réinstallez-le en la cochant. |
| Windows ouvre le Microsoft Store quand on tape `python` | Désactivez les « alias d'exécution d'application » pour Python (Paramètres → Applications → Paramètres avancés), ou installez Python depuis python.org. |
| *« Permission denied »* sur `lancer.sh` | Tapez `chmod +x lancer.sh` puis relancez. |
| Sous Ubuntu/Debian : *« ensurepip is not available »* | Installez le paquet manquant : `sudo apt install python3-venv`. |
| Accents ou caractères déformés | Utilisez *Windows Terminal* (gratuit sur le Microsoft Store) ou le Terminal macOS/Linux. Avec `lancer.bat`, l'encodage est déjà réglé. |
| Le dessin saute ou se superpose | La fenêtre est trop petite : voir l'étape 3. |
| Le dossier est resté dans un `.zip` | Extrayez-le d'abord (étape 2). |
