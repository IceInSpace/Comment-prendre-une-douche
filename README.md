# Comment prendre une douche

Une animation en caractères ASCII, à lancer dans un terminal, qui montre étape par étape comment prendre une douche, avec une barre de progression vers la propreté et un petit questionnaire final.

Python 3.8 ou plus récent. Aucune dépendance externe : le lanceur crée un environnement virtuel (`.venv`) et n'altère pas votre installation Python.

## Lancer

**Windows** : double-cliquez sur `lancer.bat`.

**macOS / Linux** :

```bash
chmod +x lancer.sh
./lancer.sh
```

Il faut une fenêtre de terminal d'au moins 56 colonnes × 38 lignes.

## Options

| Option | Effet |
|---|---|
| `--pas-a-pas` | Avancer avec la touche Entrée |
| `--vitesse 2` | Deux fois plus rapide (`0.5` = deux fois plus lent) |
| `--sans-quiz` | Ne pas afficher le questionnaire de fin |

Exemple : `./lancer.sh --pas-a-pas`. `Ctrl+C` pour quitter.

## Guides d'installation

- [LISEZ-MOI_DEBUTANT.md](LISEZ-MOI_DEBUTANT.md) : pas à pas complet, pour les débutants.
- [README_AVANCE.md](README_AVANCE.md) : installation et lancement pour les utilisateurs expérimentés.
