# ---------------------------------------------------------------------------
# setup_infra_leadership_sync_task.ps1
# Registers "LATC Infra Leadership Sync" in Windows Task Scheduler.
# Run once from PowerShell (same account that runs the Friday weekly report).
#
# Prerequisites:
#   1. pip install cursor-sdk
#   2. CURSOR_API_KEY set as a persistent user environment variable
# ---------------------------------------------------------------------------

$ErrorActionPreference = "Stop"

# ---------- Configuration --------------------------------------------------
$ScriptPath   = Join-Path $PSScriptRoot "infra_leadership_sync.py"
$TaskName     = "LATC Infra Leadership Sync"
$TaskDesc     = "Weekly Infra leadership sync notes: scrape Jira, publish dated Confluence page under Infrastructure Leadership Sync."
$PythonExe    = "C:\Users\mfink\AppData\Local\Programs\Python\Python312\python.exe"
$FirstRun     = "2026-09-02T15:00:00"
# ---------------------------------------------------------------------------

$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not (Test-Path $PythonExe)) {
    if ($pyCmd -and $pyCmd.Source) {
        $PythonExe = $pyCmd.Source
    } else {
        Write-Error "Python not found. Install Python 3.12 or update `$PythonExe in this script."
        exit 1
    }
}

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Script not found: $ScriptPath"
    exit 1
}

$sdkCheck = & $PythonExe -c "import cursor_sdk; print('ok')" 2>&1
if ($sdkCheck -ne "ok") {
    Write-Warning "cursor-sdk does not appear to be installed. Run: pip install cursor-sdk"
}

if (-not $env:CURSOR_API_KEY) {
    Write-Warning "CURSOR_API_KEY is not set in the current environment."
    Write-Warning "Add it as a persistent user environment variable:"
    Write-Warning '  [System.Environment]::SetEnvironmentVariable("CURSOR_API_KEY","cursor_...","User")'
}

$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument ('"{0}"' -f $ScriptPath) `
    -WorkingDirectory $PSScriptRoot

$Trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Wednesday `
    -At (Get-Date $FirstRun)

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Limited

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Host "Removing existing task '$TaskName' ..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName    $TaskName `
    -Description $TaskDesc `
    -Action      $Action `
    -Trigger     $Trigger `
    -Settings    $Settings `
    -Principal   $Principal | Out-Null

Write-Host ""
Write-Host "[OK] Scheduled task '$TaskName' registered successfully." -ForegroundColor Green
Write-Host "  Runs: Every Wednesday at 3:00 PM (local Eastern time)"
Write-Host "  First run: $FirstRun"
Write-Host "  Python: $PythonExe"
Write-Host "  Script: $ScriptPath"
Write-Host ""
Write-Host "To run it now for testing:"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "To view status after a run:"
Write-Host "  Get-ScheduledTaskInfo -TaskName '$TaskName'"
Write-Host "  Get-Content '$PSScriptRoot\logs\infra_leadership_sync.log' -Tail 40"
