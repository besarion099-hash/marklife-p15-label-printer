# Richtet den Marklife P15 als Windows-Drucker am Bluetooth-COM-Port ein
# (zum Drucken aus Word & Co.; der Etikettendrucker selbst braucht ihn nicht).
#
# Der Treiber des Herstellers (YinXiaoQian, signiert) ist fuer USB geschrieben
# (USBPRINT\_P15_82D7); sein Installer legt deshalb keinen Drucker an. Hier
# wird das Paket in den Treiberspeicher gelegt (vom Installer des Herstellers
# oder per pnputil aus -Inf, beides mit Administratorrechten), dann Port und
# Drucker von Hand angelegt.
#
# Aufruf durch kern\einrichtung.py; das Ergebnis steht in -Protokoll
# ("OK" oder "FEHLER: ...").

param(
    [string]$Inf = '',
    [Parameter(Mandatory)][string]$Port,
    [Parameter(Mandatory)][string]$Protokoll,
    [string]$Name = 'Marklife P15'
)
$ErrorActionPreference = 'Stop'
try {
    if (-not (Get-PrinterDriver -Name 'P15' -ErrorAction SilentlyContinue)) {
        # Add-PrinterDriver nimmt nur INF-Dateien aus dem Treiberspeicher. Dort liegt
        # das Paket schon, wenn der Installer des Herstellers lief; sonst per pnputil.
        $muster = "$env:WINDIR\System32\DriverStore\FileRepository\yxqpor.inf_*\yxqpor.inf"
        $gespeichert = Get-ChildItem $muster -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if (-not $gespeichert) {
            if (-not $Inf -or -not (Test-Path $Inf)) { throw "Treiberpaket fehlt: $Inf" }
            $ausgabe = & pnputil.exe /add-driver $Inf 2>&1
            $gespeichert = Get-ChildItem $muster -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if (-not $gespeichert) { throw "pnputil hat das Treiberpaket nicht aufgenommen: $ausgabe" }
        }
        Add-PrinterDriver -Name 'P15' -InfPath $gespeichert.FullName
    }
    $anschluss = "$($Port.TrimEnd(':')):"
    if (-not (Get-PrinterPort -Name $anschluss -ErrorAction SilentlyContinue)) {
        Add-PrinterPort -Name $anschluss
    }
    if (Get-Printer -Name $Name -ErrorAction SilentlyContinue) {
        Set-Printer -Name $Name -PortName $anschluss
    } else {
        Add-Printer -Name $Name -DriverName 'P15' -PortName $anschluss
    }
    'OK' | Set-Content -Encoding UTF8 $Protokoll
} catch {
    "FEHLER: $($_.Exception.Message)" | Set-Content -Encoding UTF8 $Protokoll
    exit 1
}
