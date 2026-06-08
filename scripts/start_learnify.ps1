$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$logs = Join-Path $root "logs"
$outLog = Join-Path $logs "server.out.log"
$errLog = Join-Path $logs "server.err.log"

New-Item -ItemType Directory -Force $logs | Out-Null

$existing = netstat -ano | Select-String ":5173.*LISTENING"
if ($existing) {
  Write-Output "Learnify is already running at http://127.0.0.1:5173"
  exit 0
}

Start-Process `
  -FilePath python `
  -ArgumentList "-u", "server.py" `
  -WorkingDirectory $root `
  -WindowStyle Hidden `
  -RedirectStandardOutput $outLog `
  -RedirectStandardError $errLog

Start-Sleep -Seconds 2

try {
  $response = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 5
  Write-Output "Learnify started: http://127.0.0.1:5173 ($($response.StatusCode))"
} catch {
  Write-Output "Learnify did not start. Check logs:"
  Write-Output $outLog
  Write-Output $errLog
  throw
}

