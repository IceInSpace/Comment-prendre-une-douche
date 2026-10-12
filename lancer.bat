@echo off
rem Lanceur Windows : cree l'environnement virtuel (une seule fois) puis lance l'animation.
chcp 65001 >nul
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo Python est introuvable. Installez-le depuis https://www.python.org/downloads/
    echo ^(cochez "Add python.exe to PATH" pendant l'installation^).
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creation de l'environnement virtuel ^(.venv^)...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo Echec de la creation de l'environnement virtuel.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"
python -m pip install -r requirements.txt -q --disable-pip-version-check
python douche.py %*
pause
