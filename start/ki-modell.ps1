# Story 3.7 (tillegg 2 og 3, gruppens svar 12.11 kl. 16:41 og 16:46):
# første gang den ekte versjonen startes, etter nøkkelen og før første
# henting, tilbyr vinduet å hente Gemma, en gratis språkmodell som kjører på
# maskinen, eller å bruke egen API-nøkkel til Gemini, Anthropic eller
# OpenAI. Bare start.ps1 for den ekte versjonen kaller Tilby-KI; demoen
# spør aldri. Spørsmålene står i spec-3-7-snarveien-spoer-foer-nettleseren.md.
#
# Det spørres bare når tjenesten er lokal (miljøet først, så den siste
# linja i .env, som hentingen leser dem), ingen data\ki-nei-ekte finnes, og
# Ollama ikke svarer med modellen kveldsjobben bruker, heller ikke etter at
# en Ollama som er installert, er startet. Et nei huskes i data\, som for
# snarveien. En feil huskes ikke, og appen starter som før.
#
# Testene og CI: OSE_START_SVAR_KI (1, 2 eller 3), OSE_START_SVAR_KI_TJENESTE
# (g, a eller o), OSE_START_SVAR_KI_NOEKKEL (bare falske nøkler i testene),
# OSE_START_OLLAMA_URL og OSE_START_OLLAMA_VENT. OSE_START_SVAR_JA=1 (CI) gir
# verken spørsmål, installasjon eller endring i .env, med mindre testene også
# gir OSE_START_SVAR_KI, som for snarveien. Nøkkelen skrives aldri ut.

# Tillegg 4 (spørsmål 22): spørsmålene venter høyst 30 sekunder.
. (Join-Path $PSScriptRoot 'frist.ps1')

$KiModell = 'gemma4:e4b'
$KiStandardUrl = 'http://127.0.0.1:11434'
$KiWingetPakke = 'Ollama.Ollama'
$KiNedlasting = 'https://ollama.com/download'
$KiLokal = '«Den lokale modellen for KI-teksten»'
$KiEgen = '«Egen nøkkel til Gemini, Anthropic eller OpenAI»'
# Tjenestene med egen nøkkel, som i src/ki_tekst.py (MED_NOEKKEL).
$KiTjenester = [ordered]@{
    g = @{ Navn = 'Gemini'; Verdi = 'gemini'; Noekkel = 'OSE_KI_GEMINI_NOKKEL' }
    a = @{ Navn = 'Anthropic (Claude)'; Verdi = 'anthropic'; Noekkel = 'OSE_KI_ANTHROPIC_NOKKEL' }
    o = @{ Navn = 'OpenAI (ChatGPT)'; Verdi = 'openai'; Noekkel = 'OSE_KI_OPENAI_NOKKEL' }
}

function Ki-Verdi([string[]]$Linjer, [string]$Navn) {
    # Som python-dotenv: den siste linja gjelder, «export » foran og en
    # kommentar etter « #» tas bort (gjennomgangen, ECH2, BH10).
    $verdi = $null
    foreach ($l in $Linjer) {
        if ($l -match ('^\s*(export\s+)?' + [regex]::Escape($Navn) + '\s*=(.*)$')) {
            $v = $Matches[2]
            if ($v -notmatch '^\s*["'']') { $v = ($v -replace '\s+#.*$', '') }
            $verdi = $v.Trim().Trim('"', "'")
        }
    }
    return $verdi
}

function Ki-OllamaUrl([string[]]$Linjer) {
    # Adressen hentingen bruker: miljøet, så .env, så standarden (ECH3).
    if ($env:OSE_START_OLLAMA_URL) { return $env:OSE_START_OLLAMA_URL.TrimEnd('/') }
    if ($env:OSE_KI_OLLAMA_URL) { return $env:OSE_KI_OLLAMA_URL.Trim().TrimEnd('/') }
    $v = Ki-Verdi $Linjer 'OSE_KI_OLLAMA_URL'
    if ($v) { return $v.TrimEnd('/') }
    return $KiStandardUrl
}

function Ki-OllamaSvarer {
    # $null: svarer ikke. Ellers navnene på modellene Ollama har.
    try {
        $svar = Invoke-RestMethod -Uri ($script:KiUrl + '/api/tags') -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    } catch {
        return $null
    }
    $navn = @()
    foreach ($m in @($svar.models)) {
        foreach ($felt in 'name', 'model') {
            $v = "$($m.$felt)"
            if ($v) { $navn += $(if ($v.Contains(':')) { $v } else { "${v}:latest" }) }
        }
    }
    return , $navn
}

function Ki-HarModellen {
    $modeller = Ki-OllamaSvarer
    return ($null -ne $modeller -and $modeller -contains $KiModell)
}

function Ki-SkrivEnv([string]$Sti, [Collections.Specialized.OrderedDictionary]$Verdier) {
    # Bytter ut linjene for nøklene i $Verdier der de står, og legger dem til
    # nederst når de mangler. Flere like linjer blir én. Ingenting annet endres.
    $linjer = @()
    if (Test-Path -LiteralPath $Sti) { $linjer = @(Get-Content -LiteralPath $Sti -Encoding UTF8) }
    $sett = @{}
    $nye = foreach ($l in $linjer) {
        $treff = $null
        foreach ($n in $Verdier.Keys) { if ($l -match ('^\s*(export\s+)?' + [regex]::Escape($n) + '\s*=')) { $treff = $n } }
        if (-not $treff) { $l; continue }
        if ($sett[$treff]) { continue }
        $sett[$treff] = $true
        "$treff=$($Verdier[$treff])"
    }
    $nye = @($nye)
    foreach ($n in $Verdier.Keys) { if (-not $sett[$n]) { $nye += "$n=$($Verdier[$n])" } }
    [IO.File]::WriteAllText($Sti, (($nye -join "`r`n") + "`r`n"), (New-Object System.Text.UTF8Encoding($false)))
}

function Ki-Senere([string]$Hva, [string]$Del = $KiLokal) {
    Write-Host "$Hva Appen starter som før, uten KI-tekst. Vinduet spør igjen neste gang, og hvordan det gjøres for hånd, står under $Del i docs/installasjon.md."
}

function Ki-FinnOllama {
    $c = Get-Command ollama -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    # Der installasjonen legger den for brukeren, og for hele maskinen (ECH8).
    $mapper = @((Join-Path $env:LOCALAPPDATA 'Programs\Ollama'))
    if ($env:ProgramFiles) { $mapper += (Join-Path $env:ProgramFiles 'Ollama') }
    foreach ($mappe in $mapper) {
        foreach ($fil in 'ollama.exe', 'ollama.cmd') {
            $sti = Join-Path $mappe $fil
            if (Test-Path -LiteralPath $sti) { $env:Path = "$mappe;$env:Path"; return $sti }
        }
    }
    return $null
}

function Ki-StartOllama([string]$Ollama, [int]$Sekunder) {
    # Starter en Ollama som er installert, men ikke svarer, og venter høyst
    # $Sekunder, målt med klokka (ECH9). Gir om den svarer.
    if ($null -ne (Ki-OllamaSvarer)) { return $true }
    Write-Host 'Starter Ollama.'
    try { Start-Process -FilePath $Ollama -ArgumentList 'serve' -WindowStyle Hidden -ErrorAction Stop | Out-Null } catch { }
    $slutt = (Get-Date).AddSeconds($Sekunder)
    while ((Get-Date) -lt $slutt) {
        if ($null -ne (Ki-OllamaSvarer)) { return $true }
        Start-Sleep -Seconds 1
    }
    return ($null -ne (Ki-OllamaSvarer))
}

function Ki-Vent([int]$Standard) {
    $s = 0
    if ($env:OSE_START_OLLAMA_VENT -and [int]::TryParse($env:OSE_START_OLLAMA_VENT, [ref]$s)) { return $s }
    return $Standard
}

function Ki-HentGemma {
    $ollama = Ki-FinnOllama
    if (-not $ollama) {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Host "Installerer Ollama med winget ($KiWingetPakke)."
            & winget install --id $KiWingetPakke --exact --source winget --accept-package-agreements --accept-source-agreements
            $kode = $LASTEXITCODE
            $ollama = Ki-FinnOllama
            # winget gir en annen kode enn 0 også når pakken finnes fra før
            # (ECH8, BH7). Da brukes den.
            if ($kode -ne 0 -and -not $ollama) { Ki-Senere "Ollama kunne ikke installeres med winget (kode $kode). Sjekk at maskinen er koblet til nettet."; return }
        } else {
            Write-Host "winget finnes ikke på denne maskinen. Siden der Ollama lastes ned, åpnes nå: $KiNedlasting"
            if ($env:OSE_START_UTEN_NETTLESER -ne '1') { Start-Process $KiNedlasting }
            # Gjennomgangen (BH2): også denne ventingen har en frist, så appen starter.
            if (-not $env:OSE_START_SVAR_KI) { [void](Les-Med-Frist 'Installer Ollama, og trykk Enter her når den er installert (vinduet venter i høyst 10 minutter)' 600) }
        }
        if (-not $ollama) { $ollama = Ki-FinnOllama }
        if (-not $ollama) { Ki-Senere 'Ollama ble ikke funnet etter installasjonen.'; return }
    }
    $vent = Ki-Vent 30
    if (-not (Ki-StartOllama $ollama $vent)) { Ki-Senere "Ollama svarte ikke etter $vent sekunder."; return }
    Write-Host "Henter $KiModell. Framdriften står under."
    & $ollama pull $KiModell
    if ($LASTEXITCODE -ne 0) { Ki-Senere "Gemma ble ikke hentet (kode $LASTEXITCODE). Sjekk at maskinen er koblet til nettet."; return }
    Write-Host 'Gemma er hentet. Hentingen lager KI-teksten med den, og ingenting sendes ut.'
}

function Ki-EgenNoekkel([string]$Rot) {
    $sporsmaal = 'Hvilken tjeneste? Skriv g for Gemini, a for Anthropic (Claude) eller o for OpenAI (ChatGPT), og trykk Enter'
    if ($env:OSE_START_SVAR_KI) {
        Write-Host $sporsmaal
        $valg = "$env:OSE_START_SVAR_KI_TJENESTE"
    } else {
        $valg = Les-Med-Frist $sporsmaal
    }
    $valg = "$valg".Trim().ToLower()
    if (-not $KiTjenester.Contains($valg)) { Write-Host '.env er ikke endret, fordi svaret ikke var g, a eller o. Vinduet spør igjen neste gang.'; return }
    $t = $KiTjenester[$valg]
    Write-Host "Nøkkelen fra $($t.Navn) limes inn med Ctrl+V eller et høyreklikk. Den vises som stjerner."
    if ($env:OSE_START_SVAR_KI) {
        $noekkel = "$env:OSE_START_SVAR_KI_NOEKKEL" -replace '\s', ''
    } else {
        $noekkel = "$(Les-Med-Frist 'Lim inn nøkkelen og trykk Enter' 120 -Skjult)" -replace '\s', ''
    }
    if (-not $noekkel) { Write-Host 'Ingen nøkkel ble limt inn, så .env er ikke endret. Vinduet spør igjen neste gang.'; return }
    $verdier = [ordered]@{ OSE_KI_TJENESTE = $t.Verdi }
    $verdier[$t.Noekkel] = $noekkel
    try {
        Ki-SkrivEnv (Join-Path $Rot '.env') $verdier
    } catch {
        Remove-Variable noekkel, verdier
        Ki-Senere '.env kunne ikke skrives.' $KiEgen
        return
    }
    Remove-Variable noekkel, verdier
    Write-Host "Valget er lagret i .env: KI-teksten lages av $($t.Navn) med nøkkelen din. Det endres i .env, se $KiEgen i docs/installasjon.md."
}

function Tilby-KI([string]$Rot) {
    if ($env:OS -ne 'Windows_NT') { return }
    if ($env:OSE_START_SVAR_JA -eq '1' -and -not $env:OSE_START_SVAR_KI) { return }
    try {
        $huske = Join-Path $Rot 'data\ki-nei-ekte'
        if (Test-Path -LiteralPath $huske) { return }
        $env_ = Join-Path $Rot '.env'
        $linjer = @()
        if (Test-Path -LiteralPath $env_) { $linjer = @(Get-Content -LiteralPath $env_ -Encoding UTF8) }
        # Miljøet går foran .env, som i hentingen (ki_innstillinger, ECH3).
        $tjeneste = if ($null -ne $env:OSE_KI_TJENESTE) { $env:OSE_KI_TJENESTE } else { Ki-Verdi $linjer 'OSE_KI_TJENESTE' }
        if ($null -ne $tjeneste -and $tjeneste.Trim().ToLower() -ne 'lokal') { return }
        $script:KiUrl = Ki-OllamaUrl $linjer
        if (Ki-HarModellen) { return }
        # Er Ollama installert, men stoppet, startes den før det spørres (ECH7).
        $ollama = Ki-FinnOllama
        if ($ollama -and (Ki-StartOllama $ollama (Ki-Vent 10)) -and (Ki-HarModellen)) { return }
        Write-Host ''
        Write-Host 'KI-teksten på aksjesidene skrives av en språkmodell. Appen virker også uten.'
        Write-Host '  1  Hent Gemma, en gratis språkmodell som kjører på denne maskinen. Ollama installeres,'
        Write-Host '     og Gemma hentes nå (noen GB og noen minutter). Ingenting sendes ut.'
        Write-Host '  2  Bruk din egen API-nøkkel til Gemini, Anthropic (Claude) eller OpenAI (ChatGPT).'
        Write-Host '     En API-nøkkel er ikke det samme som et abonnement på ChatGPT eller Claude.'
        Write-Host '     Tallene teksten bygger på, sendes da til tjenesten, og det kan koste der.'
        Write-Host '     Gemini har en gratis nøkkel.'
        Write-Host '  3  Ikke nå. Vinduet spør ikke igjen.'
        $sporsmaal = 'Skriv 1, 2 eller 3 og trykk Enter (bare Enter er 3)'
        if ($env:OSE_START_SVAR_KI) {
            Write-Host $sporsmaal
            $svar = $env:OSE_START_SVAR_KI
        } else {
            $svar = Les-Med-Frist $sporsmaal
        }
        # Tillegg 4, spørsmål 22: uten svar innen fristen er det «ikke nå»
        # bare denne gangen, så appen alltid starter.
        if ($null -eq $svar) {
            Write-Host "Ingen svar på $(Svar-Frist) sekunder, så ingen KI-tekst nå. Spørsmålet kommer igjen neste gang."
            return
        }
        switch ("$svar".Trim()) {
            '1' { Ki-HentGemma; return }
            '2' { Ki-EgenNoekkel $Rot; return }
            '3' { }
            '' { }
            default {
                # Gjennomgangen (ECH13): et annet svar, for eksempel j, huskes ikke.
                Write-Host 'Svaret var ikke 1, 2 eller 3, så ingen KI-tekst nå. Spørsmålet kommer igjen neste gang.'
                return
            }
        }
        try {
            New-Item -ItemType Directory -Force -Path (Join-Path $Rot 'data') -ErrorAction Stop | Out-Null
            Set-Content -LiteralPath $huske -Value 'Svaret var ikke nå. Slett fila for å bli spurt igjen.' -Encoding UTF8 -ErrorAction Stop
            Write-Host "Ingen KI-tekst nå. Vinduet spør ikke igjen. Hvordan den slås på senere, står under $KiLokal i docs/installasjon.md."
        } catch {
            Write-Host 'Ingen KI-tekst nå. Svaret kunne ikke huskes, så vinduet spør igjen neste gang.'
        }
    } catch {
        # Feiler noe her, starter appen som før (NFR-04).
        Ki-Senere "KI-valget stoppet: $($_.Exception.Message)"
    }
}
