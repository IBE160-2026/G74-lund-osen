# Story 2.3d: legger inn jobben «OSE Signal kveldshenting» i Oppgaveplanlegging
# (gruppens svar 26.10 kl. 22:58 og 27.10 kl. 20:58). Kjøres fra hovedkopien,
# med stien til jobbens egen arbeidskopi av main. Jobben starter
# start\kveldshenting.ps1 i arbeidskopien. Fila er UTF-8 med BOM, fordi Windows
# PowerShell 5.1 ellers leser æ, ø og å feil.
#
# Hver dag kl. 22:15, ikke bare på hverdager (svar 2 under story 2.3), og igjen
# hver halvtime til 23:45: 22:15, 22:45, 23:15 og 23:45. Varigheten er 1 time
# og 35 minutter, så 23:45 er med og 00:15 ikke. Ingen ny kjøring starter mens
# en går (ECH3 i gjennomgangen av 2.3b), og tapte kjøringer tas ikke igjen
# (beslutningen 29.09 under FR-401). Jobben kjører bare når brukeren er logget
# inn, fordi Docker Desktop startes som et vanlig program.
#
# -FoersteDato er første dag jobben går, som åååå-mm-dd. Uten den: i dag.
# Ta jobben bort med start\ta-bort-kveldshentingen.ps1.

param(
    [Parameter(Mandatory = $true)]
    [string]$Arbeidskopi,
    [string]$FoersteDato = (Get-Date).ToString('yyyy-MM-dd')
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$Navn = 'OSE Signal kveldshenting'
$Hovedkopi = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot)).TrimEnd('\')
$Arbeidskopi = [System.IO.Path]::GetFullPath($Arbeidskopi).TrimEnd('\')
$Skript = Join-Path $Arbeidskopi 'start\kveldshenting.ps1'

if ($Arbeidskopi -eq $Hovedkopi) {
    Write-Host 'Arbeidskopien kan ikke være hovedkopien. Jobben kjører fra sin egen arbeidskopi av main.'
    exit 1
}
if (-not (Test-Path -LiteralPath $Skript -PathType Leaf)) {
    Write-Host "Fant ikke $Skript."
    exit 1
}
$dato = [datetime]::MinValue
if (-not [datetime]::TryParseExact($FoersteDato, 'yyyy-MM-dd', $null, 'None', [ref]$dato)) {
    Write-Host "FoersteDato må skrives som åååå-mm-dd, for eksempel 2026-10-29. Fikk «$FoersteDato»."
    exit 1
}

$handling = New-ScheduledTaskAction -Execute 'powershell.exe' -WorkingDirectory $Arbeidskopi -Argument (
    "-NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Skript`" -Hovedkopi `"$Hovedkopi`"")
$utloeser = New-ScheduledTaskTrigger -Daily -At $dato.Date.AddHours(22).AddMinutes(15)
$utloeser.Repetition = (New-ScheduledTaskTrigger -Once -At $dato.Date.AddHours(22).AddMinutes(15) `
        -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Hours 1 -Minutes 35)).Repetition
$innstillinger = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$innstillinger.StartWhenAvailable = $false
$bruker = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $Navn -Action $handling -Trigger $utloeser -Settings $innstillinger -Principal $bruker `
    -Description 'OSE Signal: hentingen hver kveld (story 2.3d). Loggen er i data\logg i hovedkopien.' -Force | Out-Null
Write-Host "Jobben «$Navn» er lagt inn: hver dag kl. 22:15, 22:45, 23:15 og 23:45 fra $FoersteDato."
Write-Host "Den kjører $Skript. Loggen er i $(Join-Path $Hovedkopi 'data\logg')."
