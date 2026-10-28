# Story 2.3d: tar bort jobben «OSE Signal kveldshenting» fra
# Oppgaveplanlegging. Arbeidskopien, data og loggen står. Fila er UTF-8 med
# BOM, fordi Windows PowerShell 5.1 ellers leser æ, ø og å feil.

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$Navn = 'OSE Signal kveldshenting'

if (Get-ScheduledTask -TaskName $Navn -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $Navn -Confirm:$false
    Write-Host "Jobben «$Navn» er tatt bort."
} else {
    Write-Host "Jobben «$Navn» finnes ikke."
}
