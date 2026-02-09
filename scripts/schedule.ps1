param(
  [string]$TaskName = "CUFPI_Circular_Ingest",
  [string]$ScriptPath = "C:\Users\craig\Downloads\CUFPI Price Data Tool\scripts\ingest-circulars.ps1"
)

$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File `"$ScriptPath`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 6am
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Force

Write-Host "Scheduled task created: $TaskName"
