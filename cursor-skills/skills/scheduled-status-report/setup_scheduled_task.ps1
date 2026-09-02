# ---------------------------------------------------------------------------
# setup_scheduled_task.ps1
# Registers "LATC Weekly Status Report" in Windows Task Scheduler.
# Run once from an elevated (Administrator) PowerShell prompt.
#
# Prerequisites:
#   1. pip install cursor-sdk
#   2. CURSOR_API_KEY set as a persistent system/user environment variable
#      (or edit $env block below to pass it directly)
# ---------------------------------------------------------------------------

$ErrorActionPreference = "Stop"

# ---------- Configuration --------------------------------------------------
$ScriptPath   = "$PSScriptRoot\weekly_status_report.py"
$TaskName     = "LATC Weekly Status Report"
$TaskDesc     = "Generates weekly LATC pillar status reports (Ops/Eval/Models) and publishes to Confluence. Runs Monday 9:00 AM Eastern."
$FirstRun     = "2026-09-07 09:00"  # Next Monday 9:00 AM Eastern
                                    # Recurs every Monday at 9:00 AM thereafter.

$PythonCmd    = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Error "Python not found on PATH. Install Python and ensure it is in PATH."
    exit 1
}
$PythonExe    = $PythonCmd.Source
# ---------------------------------------------------------------------------

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Script not found: $ScriptPath"
    exit 1
}

# Verify cursor-sdk is installed
$sdkCheck = & python -c "import cursor_sdk; print('ok')" 2>&1
if ($sdkCheck -ne "ok") {
    Write-Warning "cursor-sdk does not appear to be installed. Run: pip install cursor-sdk"
}

# Verify CURSOR_API_KEY is available
if (-not $env:CURSOR_API_KEY) {
    Write-Warning "CURSOR_API_KEY is not set in the current environment."
    Write-Warning "Add it as a persistent user environment variable:"
    Write-Warning '  [System.Environment]::SetEnvironmentVariable("CURSOR_API_KEY","cursor_...","User")'
}

# Build the scheduled task
$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory (Split-Path $ScriptPath)

$Trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday `
    -At (Get-Date $FirstRun)

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit  (New-TimeSpan -Hours 1) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Limited

# Remove existing task with same name if present
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Host "Removing existing task '$TaskName' ..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$Task = Register-ScheduledTask `
    -TaskName   $TaskName `
    -Description $TaskDesc `
    -Action     $Action `
    -Trigger    $Trigger `
    -Settings   $Settings `
    -Principal  $Principal

Write-Host ""
Write-Host "[OK] Scheduled task '$TaskName' registered successfully." -ForegroundColor Green
Write-Host "  Runs: Every Monday at 9:00 AM (local Eastern time)"
Write-Host "  First run: $FirstRun (local Eastern time)"
Write-Host ""
Write-Host "To run it now for testing:"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "To view logs after a run:"
Write-Host "  Get-ScheduledTaskInfo -TaskName '$TaskName'"
