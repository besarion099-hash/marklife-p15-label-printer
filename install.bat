@echo off
chcp 65001 >nul
title Etikettendrucker / Label Printer - Einrichtung / Setup
echo Richtet die Python-Umgebung ein (einmalig). Kann einige Minuten dauern.
echo Sets up the Python environment (once). This can take a few minutes.
echo.

set "HIER=%~dp0"
set "PY=%HIER%venv\Scripts\python.exe"

echo Sprache / Language:   1 = Deutsch    2 = English
choice /c 12 /n /m "Bitte waehlen / Please choose [1,2]: "
if errorlevel 2 (set "SPRACHE=en") else (set "SPRACHE=de")
echo.

if exist "%PY%" goto pakete

rem Das "python" im PATH ist auf diesem Rechner nur der Store-Platzhalter.
rem Deshalb die von uv verwaltete Python 3.11 nehmen, wie beim Multilayer-Tool.
set "BASIS="
for /f "delims=" %%P in ('uv python find 3.11 2^>nul') do set "BASIS=%%P"
if not defined BASIS (
    echo uv oder Python 3.11 fehlt. Einmalig ausfuehren: uv python install 3.11
    echo uv or Python 3.11 is missing. Run once: uv python install 3.11
    pause
    exit /b 1
)
echo Erstelle venv / creating venv ...
"%BASIS%" -m venv "%HIER%venv"

:pakete
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r "%HIER%requirements.txt"

"%PY%" "%HIER%aufkleber_holen.py"
"%PY%" -c "import sys; sys.path.insert(0, r'%HIER%.'); from kern import einstellungen; einstellungen.sprache_setzen('%SPRACHE%')"
powershell -NoProfile -ExecutionPolicy Bypass -File "%HIER%startmenue.ps1"

echo.
if "%SPRACHE%"=="en" (
    echo Done. Start the program from the Start menu or desktop shortcut "Etikettendrucker"
    echo or with "Etikettendrucker.bat".
) else (
    echo Fertig. Starte das Programm ueber das Startmenue oder den Desktop ^("Etikettendrucker"^)
    echo oder mit "Etikettendrucker.bat".
)
echo.
pause
