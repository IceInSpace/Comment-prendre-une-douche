#!/usr/bin/env bash
# Lanceur macOS / Linux : crée l'environnement virtuel (une seule fois) puis lance l'animation.
set -e
cd "$(dirname "$0")"

PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
    echo "Python est introuvable. Installez-le puis relancez ce script (voir LISEZ-MOI_DEBUTANT.md)."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Création de l'environnement virtuel (.venv)..."
    "$PY" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -r requirements.txt -q --disable-pip-version-check
python douche.py "$@"
