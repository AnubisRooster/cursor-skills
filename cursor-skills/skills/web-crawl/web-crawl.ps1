#!/usr/bin/env pwsh
# web-crawl.ps1 - Crawl an external website, follow same-host links, flag bug-related pages.
# Usage: .\web-crawl.ps1 -Url https://example.com -MaxPages 20 -MaxDepth 3 -BugKeywords "bug,issue,task"
# Output: web-crawl-results.csv in the current directory

param(
    [Parameter(Mandatory=$true)][string]$Url,
    [int]$MaxPages = 50,
    [int]$MaxDepth = 3,
    [string]$BugKeywords = "bug,issue,task,fix,todo,changelog"
)

$ErrorActionPreference = "Stop"
$keywordArray = $BugKeywords.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ }
$csvPath = Join-Path (Get-Location) "web-crawl-results.csv"

# Ensure trailing slash on base for host extraction
$baseUri = [Uri]$Url
$baseHost = $baseUri.Host

$rows = New-Object System.Collections.Generic.List[object]
$visited = @{}
$queue = New-Object System.Collections.Generic.Queue[object]
$queue.Enqueue(@{ url = $Url; depth = 0; source = "" })
$visited[$Url] = $true
$pageCount = 0

function Normalize-Absolute([string]$href, [string]$baseUrl) {
    if ($href -match '^(https?:)?//') {
        if ($href -match '^//') { return "https:$href" }
        return $href
    }
    try {
        return (New-Object Uri([Uri]$baseUrl, $href)).AbsoluteUri
    } catch { return $null }
}

function Get-Title([string]$html) {
    $m = [regex]::Match($html, '(?is)<title[^>]*>(.*?)</title>')
    if ($m.Success) { return ($m.Groups[1].Value -replace '\s+', ' ').Trim() }
    $m = [regex]::Match($html, '(?is)<h1[^>]*>(.*?)</h1>')
    if ($m.Success) { return ($m.Groups[1].Value -replace '<[^>]+>', '' -replace '\s+', ' ').Trim() }
    return "Untitled"
}

function Get-Links([string]$html, [string]$baseUrl) {
    $links = @()
    foreach ($m in [regex]::Matches($html, '(?is)<a\b[^>]*\bhref\s*=\s*["'']([^"'']+)["'']')) {
        $abs = Normalize-Absolute $m.Groups[1].Value $baseUrl
        if ($abs) { $links += $abs }
    }
    return $links | Select-Object -Unique
}

function Has-BugKeywords([string]$text) {
    $lower = $text.ToLowerInvariant()
    foreach ($kw in $keywordArray) {
        if ($lower.Contains($kw.ToLowerInvariant())) { return $true }
    }
    return $false
}

while ($queue.Count -gt 0 -and $pageCount -lt $MaxPages) {
    $item = $queue.Dequeue()
    $pageUrl = $item.url
    $depth = $item.depth
    if ($depth -gt $MaxDepth) { continue }

    try {
        $resp = Invoke-WebRequest -Uri $pageUrl -UseBasicParsing -TimeoutSec 30 `
            -Headers @{ "User-Agent" = "Mozilla/5.0 (compatible; web-crawl/1.0)" }
        $html = $resp.Content
    } catch {
        $rows.Add([pscustomobject]@{
            depth = $depth; url = $pageUrl; title = "ERROR: $($_.Exception.Message)"
            bug_indicator = "NO"; source = $item.source
        })
        continue
    }

    $pageCount++
    $title = Get-Title $html
    $bug = Has-BugKeywords "$title $pageUrl"
    $rows.Add([pscustomobject]@{
        depth = $depth; url = $pageUrl; title = $title
        bug_indicator = $(if ($bug) { "YES" } else { "NO" }); source = $item.source
    })

    if ($depth -lt $MaxDepth) {
        foreach ($link in (Get-Links $html $pageUrl)) {
            try {
                $u = [Uri]$link
                if ($u.Host -ne $baseHost) { continue }   # same-host only
                if ($u.Scheme -notmatch '^https?$') { continue }
                $clean = $u.AbsoluteUri
                if ($visited.ContainsKey($clean)) { continue }
                if ($clean -match '(\.(png|jpe?g|gif|svg|webp|css|js|ico|pdf|zip|xml))($|\?)') { continue }
                $visited[$clean] = $true
                $queue.Enqueue(@{ url = $clean; depth = $depth + 1; source = $pageUrl })
            } catch { }
        }
    }
}

# Write CSV
"depth,url,title,bug-indicator,source" | Out-File -FilePath $csvPath -Encoding utf8
foreach ($r in $rows) {
    $esc = { param($s) '"' + ($s -replace '"', '""') + '"' }
    $line = "$($r.depth),$(& $esc $r.url),$(& $esc $r.title),$($r.bug_indicator),$(& $esc $r.source)"
    $line | Out-File -FilePath $csvPath -Append -Encoding utf8
}

$bugCount = ($rows | Where-Object { $_.bug_indicator -eq "YES" }).Count
Write-Output "Crawled $pageCount pages. Found $bugCount bug-flagged pages. Results: $csvPath"
