# Story 3.7, tillegg 4 (svaret 11.11 kl. 22:07, rettelsen fra rådet 12.11):
# et spørsmål i startvinduet venter høyst 30 sekunder. Uten svar gir
# Les-Med-Frist $null, og den som spør, gjør det samme som uten spørsmål,
# uten å huske noe. OSE_START_SVAR_FRIST setter sekundene i testene.
#
# Gjennomgangen (BH3, ECH1): taster trykket før spørsmålet, for eksempel
# Enter mens uv sync går, tømmes først, så de ikke blir svaret. (ECH6): kan
# ikke vinduet lese tastene, brukes Read-Host, som før 3.7. (VG1, VG2):
# tastene leses gjennom to skriptblokker, så testene kan gi falske taster.

function Svar-Frist {
    $s = 0
    if ($env:OSE_START_SVAR_FRIST -and [int]::TryParse($env:OSE_START_SVAR_FRIST, [ref]$s) -and $s -gt 0) { return $s }
    return 30
}

function Les-Taster([int]$Sekunder, [scriptblock]$HarTast, [scriptblock]$LesTast, [switch]$Skjult) {
    # Teksten til Enter, eller $null når fristen går ut. Taster som venter
    # før spørsmålet, er alt tømt av den som kaller.
    $slutt = (Get-Date).AddSeconds($Sekunder)
    $tekst = ''
    while ((Get-Date) -lt $slutt) {
        if (-not (& $HarTast)) { Start-Sleep -Milliseconds 100; continue }
        $tast = & $LesTast
        if ($tast.Key -eq 'Enter') { Write-Host ''; return $tekst }
        if ($tast.Key -eq 'Backspace') {
            if ($tekst.Length -gt 0) { $tekst = $tekst.Substring(0, $tekst.Length - 1); Write-Host "`b `b" -NoNewline }
            continue
        }
        if ($tast.KeyChar -and -not [char]::IsControl($tast.KeyChar)) {
            $tekst += $tast.KeyChar
            if ($Skjult) { Write-Host '*' -NoNewline } else { Write-Host $tast.KeyChar -NoNewline }
        }
    }
    Write-Host ''
    return $null
}

function Les-Med-Frist([string]$Sporsmaal, [int]$Sekunder = 0, [switch]$Skjult) {
    if ($Sekunder -le 0) { $Sekunder = Svar-Frist }
    if ([Console]::IsInputRedirected) {
        # Testene: svaret kommer på standard inn, gjennom én leser for hele
        # skriptet (gjennomgangen, BH6, ECH11). Uten en linje innen fristen,
        # eller når den er lukket, er det ikke svart.
        Write-Host "${Sporsmaal}: " -NoNewline
        if (-not $script:FristLeser) { $script:FristLeser = New-Object System.IO.StreamReader([Console]::OpenStandardInput()) }
        if (-not $script:FristLinje) { $script:FristLinje = $script:FristLeser.ReadLineAsync() }
        if (-not $script:FristLinje.Wait([TimeSpan]::FromSeconds($Sekunder))) { Write-Host ''; return $null }
        $linje = $script:FristLinje.Result
        $script:FristLinje = $null
        Write-Host ''
        return $linje
    }
    try {
        while ([Console]::KeyAvailable) { [void][Console]::ReadKey($true) }
    } catch {
        # Ingen konsoll å lese tastene fra (ECH6): som før 3.7, uten frist.
        if ($Skjult) {
            $sikker = Read-Host $Sporsmaal -AsSecureString
            $peker = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sikker)
            try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($peker) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($peker) }
        }
        return (Read-Host $Sporsmaal)
    }
    Write-Host "${Sporsmaal}: " -NoNewline
    return (Les-Taster $Sekunder { [Console]::KeyAvailable } { [Console]::ReadKey($true) } -Skjult:$Skjult)
}
