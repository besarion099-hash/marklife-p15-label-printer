@echo off
chcp 65001 >nul
title Etikettendrucker

set "HIER=%~dp0"

rem Bewusst python.exe statt pythonw.exe: Smart App Control blockiert
rem pythonw.exe, und weil pythonw kein Konsolenfenster hat, sieht man davon
rem nichts. Die App blendet ihr Konsolenfenster selbst aus.

set "PY=%HIER%venv\Scripts\python.exe"
if not exist "%PY%" (
    echo Die Python-Umgebung fehlt. Bitte zuerst install.bat ausfuehren.
    pause
    exit /b 1
)

start "Etikettendrucker" /min "%PY%" "%HIER%gui\app.py"
