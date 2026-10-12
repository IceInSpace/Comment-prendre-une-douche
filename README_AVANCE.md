# Installation et lancement — utilisateurs expérimentés

Python ≥ 3.8, bibliothèque standard uniquement : aucune dépendance tierce.
Le seul prérequis système sous Debian/Ubuntu est `python3-venv`.

## Démarrage rapide

```bash
python3 -m venv .venv
source .venv/bin/activate                      # voir tableau ci-dessous
python -m pip install -r requirements.txt      # sans effet : aucune dépendance
python douche.py [options]
deactivate
```

Les lanceurs `lancer.sh` (macOS/Linux) et `lancer.bat` (Windows) automatisent
exactement ces commandes : création du venv si absent, activation, installation
de `requirements.txt`, exécution, et transmission des arguments (`"$@"` / `%*`).

## Activation du venv selon le shell

| Shell | Commande |
|---|---|
| bash / zsh | `source .venv/bin/activate` |
| fish | `source .venv/bin/activate.fish` |
| csh / tcsh | `source .venv/bin/activate.csh` |
| PowerShell | `.venv\Scripts\Activate.ps1` |
| cmd.exe | `.venv\Scripts\activate.bat` |

- PowerShell peut refuser le script : `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- L'activation est facultative : `.venv/bin/python douche.py` (ou
  `.venv\Scripts\python.exe douche.py` sous Windows) suffit.

## Alternatives

- **uv** : `uv venv && uv run douche.py`
- **conda** : `conda create -n douche python=3.12 && conda activate douche && python douche.py`
- `python -m venv --upgrade-deps .venv` met pip et setuptools à jour à la création.

## Options de la ligne de commande

| Option | Défaut | Effet |
|---|---|---|
| `--vitesse X` | `1.0` | Multiplicateur de vitesse (`X > 0`) |
| `--pas-a-pas` | désactivé | Attend la touche Entrée entre deux étapes |
| `--sans-quiz` | désactivé | Ignore le questionnaire de fin |

Code de retour 0 en fonctionnement normal ; `Ctrl+C` et la fin de flux (EOF) sont
interceptés proprement et le curseur du terminal est restauré.

## Terminal requis

- Taille minimale : **56 colonnes × 38 lignes** (vérifiée au démarrage, avec
  avertissement si la fenêtre est trop petite).
- Terminal compatible séquences ANSI : tout terminal Unix récent, Windows
  Terminal, ou la console de Windows 10 et plus.
- Encodage UTF-8 : forcé par `lancer.bat` (`chcp 65001`) ; ailleurs, vérifiez
  `locale` / `$LANG`.
- Sortie redirigée vers un fichier ou un pipe : fonctionne, mais le flux contient
  alors les séquences d'échappement ANSI brutes.

## Vérifier l'installation

```bash
# Le venv est bien actif (doit afficher True)
python -c "import sys; print(sys.prefix != sys.base_prefix)"

# Exécution accélérée, sans questionnaire, code de retour attendu : 0
python douche.py --vitesse 200 --sans-quiz > /dev/null; echo $?
```

## Dépannage

| Symptôme | Cause probable / solution |
|---|---|
| `ensurepip is not available` (Debian/Ubuntu) | `sudo apt install python3-venv` |
| `Errno 38 … lib64` à la création du venv | Système de fichiers sans liens symboliques (dossier partagé, certains montages). Créez le venv ailleurs : `python3 -m venv ~/.venvs/douche`, puis lancez `~/.venvs/douche/bin/python douche.py`. |
| `Permission denied` sur `lancer.sh` | `chmod +x lancer.sh`, ou `bash lancer.sh`. Sur un dossier monté en `noexec`, utilisez `bash lancer.sh`. |
| Séquences `^[[H` affichées à l'écran | Terminal sans support ANSI : utiliser Windows Terminal. |
| Image qui défile au lieu de se rafraîchir | Fenêtre trop petite : agrandir la fenêtre ou réduire la police. |
| `python` ouvre le Microsoft Store (Windows) | Désactiver l'alias d'exécution Python (Paramètres → Applications → Paramètres avancés) ou installer Python depuis python.org. |
| `py` / `python` introuvable | Python absent du `PATH` : réinstaller en cochant « Add python.exe to PATH ». |

## Désinstallation

Supprimer le dossier `.venv` (et `__pycache__`). Rien n'est écrit en dehors du
dossier du projet ; le Python système n'est jamais modifié. Si vous versionnez le
projet, ajoutez `.venv/` et `__pycache__/` à votre `.gitignore`.
