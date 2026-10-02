$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
docker compose --profile app down
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$pidFile = Join-Path $env:TEMP "environmental-audio-rag-demo-llama.pid"
if (Test-Path $pidFile) {
    $processId = [int](Get-Content $pidFile -Raw).Trim()
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($null -ne $process) { Stop-Process -Id $processId -Force }
    Remove-Item $pidFile -Force
}
Write-Host "Đã dừng app demo; volume DB không bị xoá."
