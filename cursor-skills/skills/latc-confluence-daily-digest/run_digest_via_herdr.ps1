# ---------------------------------------------------------------------------
# run_digest_via_herdr.ps1
# Pilot: run the LATC Confluence Daily Digest inside a Herdr pane so the run
# survives disconnects and is observable (working/blocked/done) in the Herdr
# UI. The scheduled task calls this instead of invoking python directly.
#
# - -Simulate : skips the real digest; echoes the completion sentinel to
#               validate the Herdr plumbing end-to-end.
# ---------------------------------------------------------------------------

param([switch]$Simulate)

$ErrorActionPreference = "Continue"
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [Environment]::GetEnvironmentVariable("Path", "User")

$Herdr      = "C:\Users\mfink\AppData\Local\Programs\Herdr\bin\herdr.exe"
$Python     = "C:\Users\mfink\AppData\Local\Programs\Python\Python312\python.exe"
$DigestDir  = "C:\Users\mfink\.claude\skills\latc-confluence-daily-digest"
$DigestPy   = Join-Path $DigestDir "latc_confluence_daily_digest.py"
$LogDir     = "C:\Users\mfink\.herdr-pilot"
$Sentinel   = "published SUCCESSFULLY|Digest DONE|Digest FAILED|completed with ERRORS"
$TimeoutMs  = 2700000   # 45 min cap (digest has internal retries)

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$runLog = Join-Path $LogDir "digest-$stamp.log"

function Log([string]$msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg"
    $line | Out-File -FilePath $runLog -Append -Encoding utf8
    Write-Output $line
}

# 1. Ensure the headless server is up (survives after this wrapper exits).
$stat = & $Herdr status 2>$null | Out-String
if ($stat -notmatch "running") {
    Log "herdr server not running - starting"
    Start-Process -FilePath $Herdr -ArgumentList "server" -WindowStyle Hidden
    Start-Sleep -Seconds 8
}

# 2. Dedicated workspace + fresh pane per run (kept for later inspection on failure).
$stamp2 = Get-Date -Format "yyyyMMdd-Hmm"
$created = & $Herdr workspace create --cwd $DigestDir --label "digest-$stamp2" --no-focus 2>$null | ConvertFrom-Json
if (-not $created -or -not $created.result) {
    Log "ERROR: could not create herdr workspace: $created"
    exit 1
}
$paneId = $created.result.root_pane.pane_id
Log "workspace=$($created.result.workspace.id) pane=$paneId"

# 3. Run the digest inside the pane (survives lid close / session drop).
if ($Simulate) {
    & $Herdr pane run $paneId "echo 'Digest DONE: status=PUBLISHED (simulated) run_id=herdr-pilot url=https://none'"
} else {
    & $Herdr pane run $paneId "`"$Python`" `"$DigestPy`""
}
Log "digest dispatched to pane $paneId"

# 4. Wait for a completion sentinel (short/robust tokens survive pane wrap).
$wait = & $Herdr pane wait-output $paneId --regex $Sentinel --timeout $TimeoutMs 2>$null | ConvertFrom-Json
if ($wait.result -and $wait.result.matched_line) {
    Log "sentinel matched: $($wait.result.matched_line)"
} else {
    Log "WARN: no sentinel within ${TimeoutMs}ms - pane left open for inspection"
    exit 1
}

# 5. Capture the run tail into the log file.
Start-Sleep -Seconds 3
$tail = & $Herdr pane read $paneId --lines 40 2>$null | Out-String
$tail | Out-File -FilePath $runLog -Append -Encoding utf8

# 6. Close the pane on success to keep the herd tidy (failure panes stay open).
$ok = ($wait.result.matched_line -match "SUCCESSFULLY|Digest DONE") -and ($wait.result.matched_line -notmatch "FAILED|ERRORS")
if ($ok -and -not $Simulate) {
    & $Herdr pane close $paneId 2>$null | Out-Null
    Log "pane closed"
}
Log "run finished ok=$ok"
exit $(if ($ok) { 0 } else { 1 })
