# Story 3.5a: start med dobbeltklikk med uv, uten Docker (gruppens svar
# 23.10 kl. 16:16 og 16:37). Startes av «Start demoen.cmd» og «Start den
# ekte versjonen.cmd» i rota. Fila er UTF-8 med BOM, fordi Windows
# PowerShell 5.1 ellers leser æ, ø og å feil.
#
# Webserveren startes med waitress bare på 127.0.0.1:8000, aldri med debug,
# og aldri med src/app.py som skript (den har debug=True). Nøkkelen vises
# aldri og skrives bare til .env.
#
# OSE_START_SVAR_JA=1 svarer ja på spørsmålet om uv og venter ikke på Enter
# (CI). OSE_START_UTEN_NETTLESER=1 åpner ingen nettleser (CI).

param(
    [ValidateSet('demo', 'ekte')]
    [string]$Versjon = 'demo'
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$Adresse = 'http://127.0.0.1:8000'
$SvarJa = $env:OSE_START_SVAR_JA -eq '1'

function Vent-PaaEnter {
    if (-not $SvarJa) { [void](Read-Host 'Trykk Enter for å lukke vinduet') }
}

function Stopp([string]$Melding) {
    Write-Host ''
    Write-Host "Noe gikk galt: $Melding"
    Write-Host 'Se «Står du fast?» i README-en, eller docs/hjelp.md. Du kan starte på nytt med et nytt dobbeltklikk.'
    Vent-PaaEnter
    exit 1
}

function Svarer([string]$Url) {
    try {
        $svar = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
        return $svar.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Til mappa skriptet ligger i, uansett hvor det ble startet fra.
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

if ($Versjon -eq 'demo') {
    Write-Host 'OSE Signal: demoen, med oppdiktede selskaper og kurser.'
} else {
    Write-Host 'OSE Signal: den ekte versjonen, med kurser fra EODHD.'
}
Write-Host 'Stopp appen ved å lukke dette vinduet, eller med Ctrl+C.'
Write-Host ''

# uv: på PATH, i .local\bin i brukermappa, eller installert etter et ja.
$uvMappe = Join-Path $env:USERPROFILE '.local\bin'
if (-not (Get-Command uv -ErrorAction SilentlyContinue) -and (Test-Path (Join-Path $uvMappe 'uv.exe'))) {
    $env:Path = "$uvMappe;$env:Path"
}
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host 'Appen trenger uv, som installerer Python og pakkene appen bruker.'
    Write-Host 'uv er ikke installert. Den offisielle installasjonen fra astral.sh legger den i brukermappa di.'
    if ($SvarJa) {
        $svar = 'j'
    } else {
        $svar = Read-Host 'Installere uv nå? Skriv j og trykk Enter for ja'
    }
    if ($svar -notmatch '^\s*(j|ja|y|yes)\s*$') {
        Stopp 'uv er ikke installert. Installer uv slik «Tester» i README-en sier, og start på nytt.'
    }
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$uvMappe;$env:Path"
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Stopp 'uv ble ikke funnet etter installasjonen. Lukk vinduet og start på nytt.'
    }
}

if (Svarer $Adresse) {
    Stopp "noe svarer allerede på $Adresse. Stopp det først, for eksempel demoen i Docker med docker compose --profile demo down."
}

Write-Host 'Installerer pakkene (uv sync). Første gang tar det noen minutter.'
uv sync
if ($LASTEXITCODE -ne 0) { Stopp "uv sync gikk ut med kode $LASTEXITCODE. Sjekk at maskinen er koblet til nettet." }

if ($Versjon -eq 'demo') {
    Write-Host 'Lager demobasen.'
    uv run python src/demo.py
    if ($LASTEXITCODE -ne 0) { Stopp "demobasen kunne ikke lages (kode $LASTEXITCODE)." }
    $env:OSE_DEMO = '1'
} else {
    Remove-Item Env:OSE_DEMO -ErrorAction SilentlyContinue
    if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }
    $linjer = @(Get-Content -LiteralPath '.env' -Encoding UTF8)
    $harNoekkel = @($linjer | Where-Object { $_ -match '^EODHD_API_KEY=\S' }).Count -gt 0
    if (-not $harNoekkel) {
        Write-Host 'Første gang trenger den ekte versjonen en nøkkel fra EODHD. Registreringssiden åpnes nå.'
        Write-Host 'Lag en gratis konto, kopier nøkkelen (API key), og lim den inn her.'
        if ($env:OSE_START_UTEN_NETTLESER -ne '1') { Start-Process 'https://eodhd.com/register' }
        $sikker = Read-Host 'Lim inn nøkkelen og trykk Enter (den vises ikke)' -AsSecureString
        $peker = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sikker)
        try {
            $noekkel = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($peker).Trim()
        } finally {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($peker)
        }
        if (-not $noekkel) { Stopp 'ingen nøkkel ble limt inn.' }
        $nye = @($linjer | Where-Object { $_ -notmatch '^EODHD_API_KEY=' }) + "EODHD_API_KEY=$noekkel"
        [IO.File]::WriteAllText((Join-Path (Get-Location) '.env'), (($nye -join "`r`n") + "`r`n"), (New-Object System.Text.UTF8Encoding($false)))
        Remove-Variable noekkel, nye
        Write-Host 'Nøkkelen er lagret i .env.'
    }
    Write-Host 'Henter kurser. Er alt hentet, brukes ingen kall.'
    uv run python src/fetch_prices.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Hentingen gikk ut med kode $LASTEXITCODE. Appen starter likevel, med det som er hentet før."
    }
}

Write-Host "Starter appen på $Adresse."
$env:PYTHONPATH = 'src'
$server = Start-Process -FilePath 'uv' -ArgumentList 'run', 'waitress-serve', '--listen=127.0.0.1:8000', 'app:app' -NoNewWindow -PassThru
$klar = $false
for ($i = 0; $i -lt 120; $i++) {
    if ($server.HasExited) { break }
    if (Svarer $Adresse) { $klar = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $klar) { Stopp 'appen svarte ikke på 127.0.0.1:8000.' }

Write-Host ''
Write-Host "Appen kjører på $Adresse."
Write-Host 'Lukk dette vinduet, eller trykk Ctrl+C, for å stoppe den.'
if ($env:OSE_START_UTEN_NETTLESER -ne '1') { Start-Process $Adresse }
$server.WaitForExit()
