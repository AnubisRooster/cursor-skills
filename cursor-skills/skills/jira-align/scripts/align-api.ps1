#Requires -Version 5.1
<#
.SYNOPSIS
  Thin helper for Jira Align REST API 2.0.

.DESCRIPTION
  Reads JIRA_ALIGN_URL and JIRA_ALIGN_API_TOKEN from the process or User env.
  Never hardcode tokens in this script.

.EXAMPLE
  .\align-api.ps1 -Method GET -Path Users -Query @{ '$top' = 5 }
.EXAMPLE
  .\align-api.ps1 -Method GET -Path Programs
.EXAMPLE
  .\align-api.ps1 -Method GET -Path 'Epics/123'
#>
[CmdletBinding()]
param(
  [ValidateSet('GET', 'POST', 'PUT', 'PATCH', 'DELETE')]
  [string] $Method = 'GET',

  [Parameter(Mandatory = $true)]
  [string] $Path,

  [hashtable] $Query,

  [object] $Body,

  [switch] $Raw
)

function Get-AlignEnv([string] $Name) {
  $v = [Environment]::GetEnvironmentVariable($Name, 'Process')
  if ([string]::IsNullOrWhiteSpace($v)) {
    $v = [Environment]::GetEnvironmentVariable($Name, 'User')
  }
  if ([string]::IsNullOrWhiteSpace($v)) {
    $v = [Environment]::GetEnvironmentVariable($Name, 'Machine')
  }
  return $v
}

$base = Get-AlignEnv 'JIRA_ALIGN_URL'
$token = Get-AlignEnv 'JIRA_ALIGN_API_TOKEN'

if ([string]::IsNullOrWhiteSpace($base)) {
  throw 'JIRA_ALIGN_URL is not set (User or process env).'
}
if ([string]::IsNullOrWhiteSpace($token)) {
  throw 'JIRA_ALIGN_API_TOKEN is not set (User or process env).'
}

$base = $base.TrimEnd('/')
$pathClean = $Path.TrimStart('/')
$uri = "$base/rest/align/api/2/$pathClean"

if ($Query -and $Query.Count -gt 0) {
  $pairs = foreach ($k in $Query.Keys) {
    $encKey = [uri]::EscapeDataString([string]$k)
    $encVal = [uri]::EscapeDataString([string]$Query[$k])
    "$encKey=$encVal"
  }
  $uri = $uri + '?' + ($pairs -join '&')
}

$headers = @{
  Authorization = "bearer $token"
  Accept        = 'application/json'
}

$irmParams = @{
  Method  = $Method
  Uri     = $uri
  Headers = $headers
}

if ($null -ne $Body) {
  $irmParams['ContentType'] = 'application/json'
  if ($Body -is [string]) {
    $irmParams['Body'] = $Body
  } else {
    $irmParams['Body'] = ($Body | ConvertTo-Json -Depth 20 -Compress)
  }
}

try {
  $resp = Invoke-RestMethod @irmParams
} catch {
  $status = $null
  if ($_.Exception.Response) {
    $status = [int]$_.Exception.Response.StatusCode
  }
  Write-Error "Align API $Method $uri failed (HTTP $status): $($_.Exception.Message)"
  throw
}

if ($Raw) {
  return $resp
}

$resp | ConvertTo-Json -Depth 20
