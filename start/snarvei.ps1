# Story 3.6 (del C, gruppens svar 10.11 kl. 14:07, og tillegget om demoen
# kl. 15:57): snarveien «OSE Signal» på skrivebordet i Windows, med ikonet.
# start.ps1 kaller Snarvei-Og-Nettleser når appen svarer. Første gang spør vinduet
# om snarveien skal lages. Et nei huskes i data\, og finnes snarveien,
# spørres det ikke igjen. Starter den en annen kopi, spør vinduet én gang
# om den skal starte denne i stedet (svaret 11.11 kl. 13:47). Snarveien starter versjonen som dobbeltklikket
# gjør: «Start den ekte versjonen.cmd» eller «Start demoen.cmd».
#
# OSE_SKRIVEBORD er skrivebordet (testene gir en midlertidig mappe),
# OSE_START_SVAR_SNARVEI svarer på spørsmålet (j eller n, testene), og
# OSE_START_SVAR_JA=1 (CI) gir verken spørsmål eller snarvei.

# Story 3.7, tillegg 4: spørsmålet venter høyst 30 sekunder (frist.ps1).
. (Join-Path $PSScriptRoot 'frist.ps1')

function Snarvei-Navn([string]$Versjon) {
    if ($Versjon -eq 'demo') { return 'OSE Signal (demo)' }
    return 'OSE Signal'
}

function Tilby-Snarvei([string]$Versjon, [string]$Rot) {
    if ($env:OS -ne 'Windows_NT') { return }
    if ($env:OSE_START_SVAR_JA -eq '1' -and -not $env:OSE_START_SVAR_SNARVEI) { return }
    $navn = Snarvei-Navn $Versjon
    $skrivebord = $env:OSE_SKRIVEBORD
    if (-not $skrivebord) { $skrivebord = [Environment]::GetFolderPath('Desktop') }
    if (-not $skrivebord -or -not (Test-Path -LiteralPath $skrivebord)) { return }
    $lnk = Join-Path $skrivebord "$navn.lnk"
    $fil = if ($Versjon -eq 'demo') { 'Start demoen.cmd' } else { 'Start den ekte versjonen.cmd' }
    $her = Join-Path $Rot $fil
    # Finnes snarveien og starter den denne kopien, spørres det ikke. Peker
    # den på en mappe som er slettet, er den død, og da tilbys den på nytt
    # (gjennomgangen, BH2). Peker den på en annen kopi som finnes, sier
    # vinduet hvilken mappe det er, og spør om den skal starte denne kopien
    # i stedet (gruppens svar 11.11 kl. 13:47, spørsmål 8).
    $annen = $null
    if (Test-Path -LiteralPath $lnk) {
        $maal = $null
        try { $maal = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk).TargetPath } catch { }
        if (-not $maal) { return }
        $lik = $false
        try { $lik = [IO.Path]::GetFullPath($maal) -ieq [IO.Path]::GetFullPath($her) } catch { }
        if ($lik) { return }
        if (Test-Path -LiteralPath $maal) {
            # Bare en snarvei til samme startfil i en annen mappe er en annen
            # kopi. En snarvei brukeren har laget til noe annet, står
            # (gjennomgangen, ECH3).
            if ((Split-Path -Leaf $maal) -ne $fil) { return }
            $annen = Split-Path -Parent $maal
        }
    }
    # Et nei huskes i data-mappa til denne kopien, så hver kopi spør bare én
    # gang. Et nei til å la snarveien starte denne kopien har sin egen fil,
    # så en snarvei som senere blir død, tilbys på nytt (gjennomgangen, ECH1).
    if ($annen) { $huske = Join-Path $Rot "data\snarvei-nei-flytt-$Versjon" }
    else { $huske = Join-Path $Rot "data\snarvei-nei-$Versjon" }
    if (Test-Path -LiteralPath $huske) { return }
    if ($annen) {
        Write-Host "Snarveien «$navn» på skrivebordet starter kopien i $annen."
        $spoersmaal = "Skal den starte denne kopien ($Rot) i stedet? Skriv j og trykk Enter for ja, eller bare Enter for nei"
    } else {
        $spoersmaal = "Lage snarveien «$navn» på skrivebordet? Skriv j og trykk Enter for ja, eller bare Enter for nei"
    }
    # Story 3.7 (svaret 11.11 kl. 22:07): nettleseren åpnes etter svaret, så
    # spørsmålet ikke står i vinduet bak den. Linja står rett før spørsmålet.
    if ($env:OSE_START_UTEN_NETTLESER -ne '1') { Write-Host 'Nettleseren åpner appen når du har svart.' }
    if ($env:OSE_START_SVAR_SNARVEI) {
        # Testene: spørsmålet skrives, så teksten kan prøves (gjennomgangen, VG1).
        Write-Host $spoersmaal
        $svar = $env:OSE_START_SVAR_SNARVEI
    } else {
        $svar = Les-Med-Frist $spoersmaal
    }
    # Tillegg 4: uten svar innen fristen lages ingen snarvei, og ingenting
    # huskes, så spørsmålet kommer igjen neste gang.
    if ($null -eq $svar) {
        Write-Host "Ingen svar på $(Svar-Frist) sekunder, så ingen endring av snarveien nå. Spørsmålet kommer igjen neste gang."
        return
    }
    if ($svar -notmatch '^\s*(j|ja|y|yes)\s*$') {
        $foer = if ($annen) { 'Snarveien er som før.' } else { 'Ingen snarvei.' }
        try {
            New-Item -ItemType Directory -Force -Path (Join-Path $Rot 'data') -ErrorAction Stop | Out-Null
            Set-Content -LiteralPath $huske -Value 'Svaret var nei. Slett fila for å bli spurt igjen.' -Encoding UTF8 -ErrorAction Stop
            Write-Host "$foer Vinduet spør ikke igjen."
        } catch {
            Write-Host "$foer Svaret kunne ikke huskes, så vinduet spør igjen neste gang."
        }
        return
    }
    try {
        $skall = New-Object -ComObject WScript.Shell
        $snarvei = $skall.CreateShortcut($lnk)
        $snarvei.TargetPath = $her
        $snarvei.Arguments = ''
        $snarvei.WorkingDirectory = $Rot
        $snarvei.IconLocation = (Join-Path $Rot 'src\static\ikon.ico') + ',0'
        $snarvei.Description = $navn
        $snarvei.Save()
        if ($annen) { Write-Host "Snarveien «$navn» starter nå denne kopien." }
        else { Write-Host "Snarveien «$navn» ligger på skrivebordet." }
    } catch {
        Write-Host "Snarveien kunne ikke lages: $($_.Exception.Message) Appen kjører som før."
    }
}

# Story 3.7 (svaret 11.11 kl. 22:07): når appen svarer, spør vinduet om
# snarveien først, og nettleseren åpnes etter svaret, også etter et nei og
# når vinduet ikke spør. Har appen stoppet, spørres det ikke, og har den
# stoppet mens vinduet spurte, åpnes ingen nettleser; beskjeden kommer fra
# start.ps1 som før. $Kjoerer sier om appen kjører, og $Aapne åpner
# nettleseren, så testene kan prøve rekkefølgen med en falsk nettleser.
function Snarvei-Og-Nettleser([string]$Versjon, [string]$Rot, [scriptblock]$Kjoerer, [scriptblock]$Aapne) {
    if (-not (& $Kjoerer)) { return }
    # Gjennomgangen (ECH6, VG8): en feil i spørsmålet stopper ikke appen, og
    # nettleseren åpnes likevel.
    try { Tilby-Snarvei $Versjon $Rot } catch { Write-Host "Snarveien kunne ikke tilbys: $($_.Exception.Message) Appen kjører som før." }
    if (-not (& $Kjoerer)) { return }
    if ($env:OSE_START_UTEN_NETTLESER -ne '1') { & $Aapne }
}
