# Legt im Startmenue den Eintrag "Etikettendrucker" an.
#
# Er startet die Basis-Python aus venv\pyvenv.cfg (Eintrag "home") direkt,
# nicht venv\Scripts\python.exe: Der venv-Starter ist unter Windows nur ein
# Weiterleiter mit einem zweiten Prozess. gui\app.py bindet die Pakete der
# venv selbst ein (venv_einbinden).

$hier = Split-Path -Parent $MyInvocation.MyCommand.Path
$cfg = Join-Path $hier 'venv\pyvenv.cfg'
# "executable" ist der echte Pfad (uv: cpython-3.11.15-...), "home" oft nur eine
# Verknuepfung darauf (cpython-3.11-...). Der echte Pfad zuerst, damit der Prozess
# unter genau einem Namen laeuft.
$zeilen = Get-Content $cfg
$basis = $null
foreach ($schluessel in 'executable', 'home') {
    $zeile = $zeilen | Where-Object { $_ -match "^$schluessel\s*=" } | Select-Object -First 1
    if (-not $zeile) { continue }
    $wert = ($zeile -replace "^$schluessel\s*=\s*", '').Trim()
    if ($schluessel -eq 'home') { $wert = Join-Path $wert 'python.exe' }
    if (Test-Path $wert) { $basis = $wert; break }
}
if (-not $basis) { Write-Host 'Keine Basis-Python in venv\pyvenv.cfg - erst install.bat ausfuehren.'; exit 1 }

$ziel = Join-Path ([Environment]::GetFolderPath('Programs')) 'Etikettendrucker.lnk'
$verknuepfung = (New-Object -ComObject WScript.Shell).CreateShortcut($ziel)
$verknuepfung.TargetPath = $basis
$verknuepfung.Arguments = '"' + (Join-Path $hier 'gui\app.py') + '"'
$verknuepfung.WorkingDirectory = $hier
$verknuepfung.WindowStyle = 7          # minimiert; die App blendet die Konsole selbst aus
$verknuepfung.Description = 'Etiketten gestalten und auf dem Marklife P15 drucken'
$verknuepfung.Save()
Write-Host "Startmenue-Eintrag angelegt: $ziel"
