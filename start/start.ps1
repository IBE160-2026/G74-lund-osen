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
$server = $null

function Vent-PaaEnter {
    if (-not $SvarJa) { [void](Read-Host 'Trykk Enter for å lukke vinduet') }
}

function Stopp-Serveren {
    # Gjennomgangen (BH3, ECH2): uv, python og waitress i samme tre.
    if ($script:server -and -not $script:server.HasExited) {
        try { & taskkill.exe /T /F /PID $script:server.Id | Out-Null } catch { }
    }
}

function Stopp([string]$Melding) {
    Stopp-Serveren
    Write-Host ''
    Write-Host "Noe gikk galt: $Melding"
    Write-Host 'Se «Står du fast?» i README-en, eller docs/hjelp.md. Du kan starte på nytt med et nytt dobbeltklikk.'
    Vent-PaaEnter
    exit 1
}

# Gjennomgangen (BH4, VG2): også en feil skriptet ikke har ventet, gir
# beskjeden på norsk, og vinduet står til Enter.
trap { Stopp "$($_.Exception.Message)" }

function Opptatt {
    # Svarer noe på porten, uansett hva (gjennomgangen, BH16 og ECH7).
    $klient = New-Object System.Net.Sockets.TcpClient
    try {
        $klient.Connect('127.0.0.1', 8000)
        return $true
    } catch {
        return $false
    } finally {
        $klient.Close()
    }
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
Write-Host 'Vinduet må være åpent mens appen kjører. Stopp appen ved å lukke vinduet, eller med Ctrl+C.'
Write-Host ''

# Gruppens svar 23.10 kl. 23:31 (b): i en mappe med .git, en klon, stopper
# den ekte versjonen før uv, .env og hentingen, også på main, så et
# dobbeltklikk i en klon aldri henter med gruppens nøkkel. En ZIP-fil har
# ingen .git. Erstatter vernet «bare fra main» (VG1 og ECH9).
if ($Versjon -eq 'ekte' -and (Test-Path -LiteralPath '.git')) {
    Stopp 'mappa har .git (en klon av repoet eller et eget git-repo), og der starter ikke den ekte versjonen. Last ned en egen kopi med «Download ZIP» på GitHub, pakk den ut, og bruk din egen nøkkel fra EODHD. Demoen kan startes herfra.'
}

# uv: på PATH, i .local\bin i brukermappa, eller installert etter et ja.
$uvMappe = Join-Path $env:USERPROFILE '.local\bin'
if (-not (Get-Command uv -ErrorAction SilentlyContinue) -and (Test-Path -LiteralPath (Join-Path $uvMappe 'uv.exe'))) {
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
    if ($LASTEXITCODE -ne 0) { Stopp "installasjonen av uv feilet (kode $LASTEXITCODE)." }
    $env:Path = "$uvMappe;$env:Path"
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Stopp 'uv ble ikke funnet etter installasjonen. Lukk vinduet og start på nytt.'
    }
}

if (Opptatt) {
    Stopp "noe svarer allerede på $Adresse. Stopp det først: lukk det andre vinduet, eller stopp Docker med docker compose --profile demo down."
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
    if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
    $linjer = @(Get-Content -LiteralPath '.env' -Encoding UTF8)
    $harNoekkel = @($linjer | Where-Object { $_ -match '^EODHD_API_KEY=\S' }).Count -gt 0
    if (-not $harNoekkel) {
        Write-Host 'Første gang trenger den ekte versjonen en nøkkel fra EODHD. Registreringssiden åpnes nå.'
        # Forprøven 24.10 (funn 1–3): hvor nøkkelen står, og hvordan den limes inn.
        Write-Host 'Lag en gratis konto. Nøkkelen står som «API token» under «Dashboard» hos EODHD, med kopiknappen til høyre.'
        Write-Host 'Lim den inn her med Ctrl+V eller et høyreklikk. Den vises som stjerner.'
        if ($env:OSE_START_UTEN_NETTLESER -ne '1') { Start-Process 'https://eodhd.com/register' }
        $sikker = Read-Host 'Lim inn nøkkelen og trykk Enter' -AsSecureString
        $peker = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sikker)
        try {
            # Uten mellomrom og linjeskift, som i start.sh (gjennomgangen, BH7).
            $noekkel = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($peker) -replace '\s', ''
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
        Write-Host "Hentingen gikk ut med kode $LASTEXITCODE. Grunnen står i linjene over. Appen starter likevel, med det som er hentet før."
        Write-Host 'Er nøkkelen feil, sletter du det som står etter EODHD_API_KEY= i .env, så spør vinduet etter den på nytt neste gang.'
    }
}

Write-Host "Starter appen på $Adresse."
$env:PYTHONPATH = 'src'
$server = Start-Process -FilePath 'uv' -ArgumentList 'run', 'waitress-serve', '--listen=127.0.0.1:8000', 'app:app' -NoNewWindow -PassThru
# Uten Handle gir Windows PowerShell 5.1 ingen ExitCode etterpå.
$null = $server.Handle
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
# Gjennomgangen (BH2, VG2): stopper appen av seg selv, står beskjeden.
if ($server.ExitCode -ne 0) { Stopp "appen stoppet med kode $($server.ExitCode). Grunnen står i linjene over." }
