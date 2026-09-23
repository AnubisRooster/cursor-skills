# ---------------------------------------------------------------------------
# run_digest_via_herdr.ps1
# Run the LATC Confluence Daily Digest inside a Herdr pane when the server is
# available; otherwise fall back to direct python so Task Scheduler still
# publishes. Herdr is preferred for observability, not required for success.
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

function Ensure-HerdrServer {
    $stat = & $Herdr status 2>$null | Out-String
    if ($stat -match "status:\s+running") {
        return $true
    }
    Log "herdr server not running - starting"
    Start-Process -FilePath $Herdr -ArgumentList "server" -WindowStyle Hidden
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 2
        $stat = & $Herdr status 2>$null | Out-String
        if ($stat -match "status:\s+running") {
            Log "herdr server is running"
            return $true
        }
    }
    Log "WARN: herdr server did not come up after 30s"
    return $false
}

function Invoke-DirectDigest {
    param([string]$Reason)
    Log "FALLBACK: running digest via direct python ($Reason)"
    if ($Simulate) {
        Log "Digest DONE: status=PUBLISHED (simulated direct) run_id=herdr-fallback url=https://none"
        return 0
    }
    Push-Location $DigestDir
    try {
        & $Python $DigestPy 2>&1 | Tee-Object -FilePath $runLog -Append
        $code = $LASTEXITCODE
    } finally {
        Pop-Location
    }
    Log "direct python exit=$code"
    return $code
}

# 1. Prefer Herdr when the headless server is healthy.
$herdrOk = Test-Path $Herdr
if (-not $herdrOk) {
    exit (Invoke-DirectDigest "herdr.exe missing")
}

if (-not (Ensure-HerdrServer)) {
    exit (Invoke-DirectDigest "herdr server unavailable")
}

# 2. Dedicated workspace + fresh pane per run.
$stamp2 = Get-Date -Format "yyyyMMdd-Hmm"
$createdRaw = & $Herdr workspace create --cwd $DigestDir --label "digest-$stamp2" --no-focus 2>&1 | Out-String
$created = $null
try { $created = $createdRaw | ConvertFrom-Json } catch { $created = $null }
if (-not $created -or -not $created.result) {
    Log "ERROR: could not create herdr workspace: $createdRaw"
    exit (Invoke-DirectDigest "workspace create failed")
}
$paneId = $created.result.root_pane.pane_id
Log "workspace=$($created.result.workspace.id) pane=$paneId"

# 3. Run the digest inside the pane.
if ($Simulate) {
    & $Herdr pane run $paneId "echo 'Digest DONE: status=PUBLISHED (simulated) run_id=herdr-pilot url=https://none'"
} else {
    & $Herdr pane run $paneId "`"$Python`" `"$DigestPy`""
}
Log "digest dispatched to pane $paneId"

# 4. Wait for a completion sentinel.
$wait = & $Herdr pane wait-output $paneId --regex $Sentinel --timeout $TimeoutMs 2>$null | ConvertFrom-Json
if ($wait.result -and $wait.result.matched_line) {
    Log "sentinel matched: $($wait.result.matched_line)"
} else {
    Log "WARN: no sentinel within ${TimeoutMs}ms - leaving pane open; trying direct fallback"
    exit (Invoke-DirectDigest "pane wait timed out")
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
