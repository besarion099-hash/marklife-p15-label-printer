@echo off
chcp 65001 >nul
title Etikettendrucker - Einrichtung
echo Richtet die Python-Umgebung ein (einmalig). Kann einige Minuten dauern.
echo.

set "HIER=%~dp0"

if exist "%HIER%venv\Scripts\python.exe" goto pakete

rem Das "python" im PATH ist auf diesem Rechner nur der Store-Platzhalter.
rem Deshalb die von uv verwaltete Python 3.11 nehmen, wie beim Multilayer-Tool.
set "BASIS="
for /f "delims=" %%P in ('uv python find 3.11 2^>nul') do set "BASIS=%%P"
if not defined BASIS (
    echo uv oder Python 3.11 fehlt. Einmalig ausfuehren: uv python install 3.11
    pause
    exit /b 1
)
echo Erstelle venv ...
"%BASIS%" -m venv "%HIER%venv"

:pakete
"%HIER%venv\Scripts\python.exe" -m pip install --upgrade pip
"%HIER%venv\Scripts\python.exe" -m pip install -r "%HIER%requirements.txt"

"%HIER%venv\Scripts\python.exe" "%HIER%aufkleber_holen.py"
powershell -NoProfile -ExecutionPolicy Bypass -File "%HIER%startmenue.ps1"

echo.
echo Fertig. Starte das Programm ueber das Startmenue oder den Desktop ("Etikettendrucker")
echo oder mit "Etikettendrucker.bat".
echo.
pause
