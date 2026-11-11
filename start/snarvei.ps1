# Story 3.6 (del C, gruppens svar 10.11 kl. 14:07, og tillegget om demoen
# kl. 15:57): snarveien «OSE Signal» på skrivebordet i Windows, med ikonet.
# start.ps1 kaller Tilby-Snarvei når appen svarer. Første gang spør vinduet
# om snarveien skal lages. Et nei huskes i data\, og finnes snarveien,
# spørres det ikke igjen. Starter den en annen kopi, spør vinduet én gang
# om den skal starte denne i stedet (svaret 11.11 kl. 13:47). Snarveien starter versjonen som dobbeltklikket
# gjør: «Start den ekte versjonen.cmd» eller «Start demoen.cmd».
#
# OSE_SKRIVEBORD er skrivebordet (testene gir en midlertidig mappe),
# OSE_START_SVAR_SNARVEI svarer på spørsmålet (j eller n, testene), og
# OSE_START_SVAR_JA=1 (CI) gir verken spørsmål eller snarvei.

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
        if (Test-Path -LiteralPath $maal) { $annen = Split-Path -Parent $maal }
    }
    # Et nei, til å lage snarveien eller til å la den starte denne kopien,
    # huskes i data-mappa til denne kopien, så hver kopi spør bare én gang.
    $huske = Join-Path $Rot "data\snarvei-nei-$Versjon"
    if (Test-Path -LiteralPath $huske) { return }
    if ($annen) {
        Write-Host "Snarveien «$navn» på skrivebordet starter kopien i $annen."
        $spoersmaal = "Skal den starte denne kopien ($Rot) i stedet? Skriv j og trykk Enter for ja, eller bare Enter for nei"
    } else {
        $spoersmaal = "Lage snarveien «$navn» på skrivebordet? Skriv j og trykk Enter for ja, eller bare Enter for nei"
    }
    if ($env:OSE_START_SVAR_SNARVEI) {
        $svar = $env:OSE_START_SVAR_SNARVEI
    } else {
        $svar = Read-Host $spoersmaal
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
