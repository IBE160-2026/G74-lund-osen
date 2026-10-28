# Story 2.3d: hentingen som jobb i Oppgaveplanlegging (gruppens svar 26.10
# kl. 22:58 og 27.10 kl. 20:58). Jobben fra legg-inn-kveldshentingen.ps1
# starter denne fila i jobbens egen arbeidskopi av main, aldri i hovedkopien.
# Fila er UTF-8 med BOM, fordi Windows PowerShell 5.1 ellers leser æ, ø og å
# feil.
#
# Rekkefølgen er stegene 2-7 i hentingsinstruksjonene i dagsfilene:
# 1. Arbeidskopien flyttes til commiten origin/main hadde ved midnatt, så det
#    som flettes en dag, ikke går samme kveld (svar 3 under story 2.3).
# 2. data/ og .env må være lenker til hovedkopien, så basen og nøkkelen er de
#    samme, og nøkkelen ikke kopieres.
# 3. Docker Desktop og Ollama startes, med én felles tidsgrense. Svarer de
#    ikke innen den, hentes det uten KI-tekst (NFR-04).
# 4. uv run python src/fetch_prices.py, uten flagg, med OSE_KI_TJENESTE=lokal
#    og OSE_KI_OLLAMA_URL satt bare for kjøringen. Så målingen av omsetning,
#    uv run python src/fetch_prices.py --maal-omsetning (story 2.13).
# 5. Det skriptet selv startet, stoppes, også når noe feiler. Skriptet
#    avslutter med koden fra hentingen.
#
# Alt går til data/logg/kveldshenting-<dato>.log i hovedkopien. Nøkkelen og
# miljøet skrives aldri ut: .env leses bare som avtrykk (sha256).
#
# -BareUtsjekk stopper etter steg 1 og 2, med kode 0 (testene og prøven).

param(
    [Parameter(Mandatory = $true)]
    [string]$Hovedkopi,
    [int]$Tidsgrense = 180,
    [switch]$BareUtsjekk,
    [switch]$EtterUtsjekk
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
$env:PYTHONIOENCODING = 'utf-8'
# Gjennomgangen (BH3): jobben går uten vindu, så git skal aldri spørre.
$env:GIT_TERMINAL_PROMPT = '0'
$env:GCM_INTERACTIVE = 'never'

# Den samme som MODELL i src/ki_lokal.py (testen sjekker det).
$Modell = 'gemma4:e4b'
$OllamaUrl = 'http://127.0.0.1:11434'

function Full-Sti([string]$Sti) {
    $Sti = $Sti -replace '^\\\\\?\\', ''
    return [System.IO.Path]::GetFullPath($Sti).TrimEnd('\', '/')
}

$Arbeidskopi = Full-Sti (Split-Path -Parent $PSScriptRoot)
$Hovedkopi = Full-Sti $Hovedkopi
$LoggMappe = Join-Path $Hovedkopi 'data\logg'
$Logg = Join-Path $LoggMappe ('kveldshenting-{0:yyyy-MM-dd}.log' -f (Get-Date))

function Logg([string]$Tekst) {
    $linje = '{0:HH:mm:ss} {1}' -f (Get-Date), $Tekst
    Write-Host $linje
    try { Add-Content -LiteralPath $script:Logg -Value $linje -Encoding UTF8 } catch { }
}

function Stopp([string]$Melding) {
    Logg "STOPP: $Melding"
    exit 1
}

# Et program med en tidsgrense. Gir koden (-1 ved tidsgrensen) og utskriften.
function Kjoer-Med-Grense([string]$Fil, [string[]]$Argumenter, [int]$Sekunder) {
    $info = New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName = $Fil
    $info.Arguments = ($Argumenter | ForEach-Object { if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ } }) -join ' '
    $info.WorkingDirectory = $Arbeidskopi
    $info.UseShellExecute = $false
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.CreateNoWindow = $true
    try { $p = [System.Diagnostics.Process]::Start($info) } catch { return @{ Kode = -1; Ut = '' } }
    $ut = $p.StandardOutput.ReadToEndAsync()
    $feil = $p.StandardError.ReadToEndAsync()
    if (-not $p.WaitForExit([Math]::Max(1, $Sekunder) * 1000)) {
        try { & taskkill.exe /T /F /PID $p.Id | Out-Null } catch { }
        return @{ Kode = -1; Ut = '' }
    }
    # Gjennomgangen (ECH10): et barnebarn kan holde utskriften åpen.
    if (-not $ut.Wait(5000) -or -not $feil.Wait(5000)) { return @{ Kode = $p.ExitCode; Ut = '' } }
    return @{ Kode = $p.ExitCode; Ut = $ut.Result + $feil.Result }
}

try { New-Item -ItemType Directory -Force -Path $LoggMappe | Out-Null } catch { }
Logg "Kveldshentingen starter i $Arbeidskopi."

$GitExe = Get-Command git -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $GitExe) { Stopp 'Fant ikke git.' }

# Bare det git skriver til stdout. Advarsler på stderr blandes ikke inn i
# stier og commiter (gjennomgangen, BH13).
function Kjoer-Git {
    $ErrorActionPreference = 'Continue'
    $ut = & $GitExe.Source @args 2>$null | ForEach-Object { "$_" }
    $script:GitKode = $LASTEXITCODE
    return $ut
}

try {
    # Steg 1: aldri fra hovedkopien, og bare fra en arbeidskopi av samme repo.
    if ($Arbeidskopi -eq $Hovedkopi) {
        Stopp 'Skriptet kjører fra hovedkopien. Jobben kjører bare fra sin egen arbeidskopi av main.'
    }
    if (-not (Test-Path -LiteralPath (Join-Path $Hovedkopi '.git') -PathType Container)) {
        Stopp "Hovedkopien $Hovedkopi har ingen .git-mappe."
    }
    $felles = Kjoer-Git -C $Arbeidskopi rev-parse --path-format=absolute --git-common-dir
    if ($GitKode -ne 0 -or (Full-Sti "$felles") -ne (Full-Sti (Join-Path $Hovedkopi '.git'))) {
        Stopp 'Arbeidskopien er ikke en arbeidskopi av hovedkopien (git worktree).'
    }
    $endret = Kjoer-Git -C $Arbeidskopi status --porcelain --untracked-files=no
    if ($GitKode -ne 0 -or $endret) {
        Stopp 'Arbeidskopien har endringer. Den skal bare brukes av jobben.'
    }

    $hentet = Kjoer-Med-Grense $GitExe.Source @('-C', $Arbeidskopi, 'fetch', '--quiet', 'origin', 'main') 120
    if ($hentet.Kode -ne 0) { Logg 'git fetch feilet. Bruker origin/main slik den var sist hentet.' }

    # Gjennomgangen (BH14): forskyvningen for denne datoen, også dagen tiden
    # skifter.
    $midnatt = ([DateTimeOffset]::new((Get-Date).Date)).ToString('yyyy-MM-ddTHH:mm:sszzz')
    $commit = "$(Kjoer-Git -C $Arbeidskopi rev-list -1 --first-parent --before=$midnatt origin/main)".Trim()
    if ($GitKode -ne 0 -or $commit -notmatch '^[0-9a-f]{40}$') {
        Stopp "Fant ingen commit på origin/main fra før $midnatt."
    }
    # Gjennomgangen (ECH1): commiten fra midnatt kan være eldre enn jobben,
    # dagen 2.3d flettes. Da ville utsjekken ta bort skriptet som kjører.
    $null = Kjoer-Git -C $Arbeidskopi cat-file -e "${commit}:start/kveldshenting.ps1"
    if ($GitKode -ne 0) {
        Stopp "Commiten fra midnatt, $commit, har ikke start/kveldshenting.ps1 ennå. Jobben går fra neste kveld."
    }

    $foer = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash
    $null = Kjoer-Git -C $Arbeidskopi checkout --quiet --detach $commit
    if ($GitKode -ne 0) { Stopp "git checkout av $commit feilet." }
    $head = "$(Kjoer-Git -C $Arbeidskopi rev-parse HEAD)".Trim()
    $null = Kjoer-Git -C $Arbeidskopi symbolic-ref -q HEAD
    if ($head -ne $commit -or $GitKode -eq 0) {
        Stopp "Arbeidskopien står ikke løsrevet på $commit."
    }
    Logg "Arbeidskopien står på $commit, siste commit på origin/main før $midnatt."

    # Skriptet selv kan være endret av utsjekken. Da kjøres den nye versjonen,
    # én gang, så det som går i kveld, er det som var på main ved midnatt.
    if (-not $EtterUtsjekk -and (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash -ne $foer) {
        Logg 'Skriptet ble endret av utsjekken. Kjører den nye versjonen.'
        $argumenter = @('-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath,
            '-Hovedkopi', $Hovedkopi, '-Tidsgrense', $Tidsgrense, '-EtterUtsjekk')
        if ($BareUtsjekk) { $argumenter += '-BareUtsjekk' }
        & (Join-Path $PSHOME 'powershell.exe') @argumenter
        exit $LASTEXITCODE
    }

    # Steg 2: data/ og .env deles med hovedkopien, som lenker.
    $data = Get-Item -LiteralPath (Join-Path $Arbeidskopi 'data') -Force -ErrorAction SilentlyContinue
    if (-not $data -or $data.LinkType -notin @('Junction', 'SymbolicLink') -or
        (Full-Sti "$(@($data.Target)[0])") -ne (Full-Sti (Join-Path $Hovedkopi 'data'))) {
        Stopp 'data i arbeidskopien er ikke en lenke til data i hovedkopien.'
    }
    $envHoved = Join-Path $Hovedkopi '.env'
    $envJobb = Get-Item -LiteralPath (Join-Path $Arbeidskopi '.env') -Force -ErrorAction SilentlyContinue
    if (-not $envJobb -or -not (Test-Path -LiteralPath $envHoved -PathType Leaf)) {
        Stopp '.env mangler i arbeidskopien eller i hovedkopien.'
    }
    $lenket = if ($envJobb.LinkType -eq 'SymbolicLink') {
        (Full-Sti "$(@($envJobb.Target)[0])") -eq (Full-Sti $envHoved)
    } else {
        $envJobb.LinkType -eq 'HardLink' -and
        (Get-FileHash -LiteralPath $envJobb.FullName).Hash -eq (Get-FileHash -LiteralPath $envHoved).Hash
    }
    if (-not $lenket) {
        Stopp '.env i arbeidskopien er ikke en lenke til .env i hovedkopien. Lag lenken på nytt, ikke en kopi.'
    }
    Logg 'data og .env er lenker til hovedkopien.'

    if ($BareUtsjekk) {
        Logg 'Bare utsjekken: ingen henting.'
        exit 0
    }
} catch {
    Stopp "Uventet feil: $($_.Exception.Message)"
}

# Steg 3: Docker Desktop og Ollama, med én felles frist for begge
# (gjennomgangen, BH2): kjøringen kl. 23:45 når hentingen før kl. 23:50.
function Vent-Paa([scriptblock]$Svarer) {
    while ($true) {
        if (& $Svarer) { return $true }
        if ((Get-Date) -ge $script:frist) { return $false }
        Start-Sleep -Seconds 5
    }
}

function Igjen { [int][Math]::Max(1, ($script:frist - (Get-Date)).TotalSeconds) }

$startetDocker = $false
$startetOllama = $false
$kiKlar = $false
$kode = 1
$frist = (Get-Date).AddSeconds($Tidsgrense)
try {
    $docker = Get-Command docker -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    $dockerSvarer = { $docker -and (Kjoer-Med-Grense $docker.Source @('info') ([Math]::Min(30, (Igjen)))).Kode -eq 0 }

    if (-not $docker) {
        Logg 'Fant ikke docker.'
    } elseif (-not (& $dockerSvarer)) {
        if (-not (Get-Process -Name 'Docker Desktop' -ErrorAction SilentlyContinue)) {
            $desktop = Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'
            if (Test-Path -LiteralPath $desktop -PathType Leaf) {
                Logg 'Starter Docker Desktop.'
                Start-Process -FilePath $desktop
                $startetDocker = $true
            } else {
                Logg 'Fant ikke Docker Desktop.'
            }
        }
    }
    if ($docker -and (Vent-Paa $dockerSvarer)) {
        $kjoerer = Kjoer-Med-Grense $docker.Source @('compose', '--profile', 'ki', 'ps', '--status', 'running', '--services') (Igjen)
        if ($kjoerer.Kode -eq 0 -and ($kjoerer.Ut -split "`r?`n") -contains 'ollama') {
            Logg 'Ollama kjørte fra før.'
        } else {
            Logg 'Starter Ollama.'
            # Gjennomgangen (ECH7, BH8): regnes som startet av skriptet også
            # når up går over fristen, så den stoppes etterpå.
            $startetOllama = $true
            $null = Kjoer-Med-Grense $docker.Source @('compose', '--profile', 'ki', 'up', '-d', 'ollama') (Igjen)
        }
        $kiKlar = Vent-Paa {
            $liste = Kjoer-Med-Grense $docker.Source @('compose', 'exec', '-T', 'ollama', 'ollama', 'list') ([Math]::Min(30, (Igjen)))
            $liste.Kode -eq 0 -and $liste.Ut.Contains($Modell)
        }
    } elseif ($docker) {
        Logg "Docker svarte ikke innen $Tidsgrense s."
    }

    if ($kiKlar) {
        Logg "Ollama svarer med $Modell."
        $env:OSE_KI_TJENESTE = 'lokal'
        $env:OSE_KI_OLLAMA_URL = $OllamaUrl
    } else {
        Logg 'Docker eller Ollama svarte ikke. Henter uten KI-tekst (NFR-04).'
        $env:OSE_KI_TJENESTE = 'av'
    }

    # Steg 4: hentingen, uten flagg.
    $uv = Get-Command uv -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    $uvSti = if ($uv) { $uv.Source } else { Join-Path $env:USERPROFILE '.local\bin\uv.exe' }
    if (Test-Path -LiteralPath $uvSti -PathType Leaf) {
        Logg 'uv run python src/fetch_prices.py'
        Set-Location -LiteralPath $Arbeidskopi
        $ErrorActionPreference = 'Continue'
        & $uvSti run python src/fetch_prices.py 2>&1 | ForEach-Object { Logg "$_" }
        $kode = $LASTEXITCODE
        Logg "Hentingen avsluttet med kode $kode."
        # Story 2.13 (avgjørelsen 28.10 kl. 22:17): målingen etter hentingen i
        # hver kjøring. Den venter selv til hentingen har kursene, og koden
        # fra den endrer ikke koden jobben avslutter med.
        Logg 'uv run python src/fetch_prices.py --maal-omsetning'
        & $uvSti run python src/fetch_prices.py --maal-omsetning 2>&1 | ForEach-Object { Logg "$_" }
        Logg "Målingen avsluttet med kode $LASTEXITCODE."
        $ErrorActionPreference = 'Stop'
    } else {
        Logg 'Fant ikke uv. Ingen henting.'
    }
} catch {
    Logg "FEIL: $($_.Exception.Message)"
    $kode = 1
} finally {
    # Steg 5: bare det skriptet selv startet, stoppes, også etter en feil
    # (gjennomgangen, ECH4).
    if ($startetOllama) {
        Logg 'Stopper Ollama.'
        $null = Kjoer-Med-Grense $docker.Source @('compose', '--profile', 'ki', 'stop', 'ollama') 120
    }
    if ($startetDocker) {
        Logg 'Stopper Docker Desktop.'
        if ((Kjoer-Med-Grense $docker.Source @('desktop', 'stop') 120).Kode -ne 0) {
            Logg 'docker desktop stop feilet. Docker Desktop kjører videre.'
        }
    }
    if (-not $startetOllama -and -not $startetDocker) { Logg 'Skriptet startet verken Docker Desktop eller Ollama.' }
}

exit $kode
