$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
function Check([string]$Name, [scriptblock]$Action) {
    try { & $Action; Write-Host ("[OK] {0}" -f $Name) -ForegroundColor Green }
    catch { Write-Host ("[FAIL] {0}: {1}" -f $Name, $_.Exception.Message) -ForegroundColor Red; $script:failed = $true }
}
Check "Docker Desktop" { $v = docker version --format "{{.Server.Version}}" 2>$null; if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($v)) { throw "Docker chưa chạy" } }
Check "API health" { $r = Invoke-WebRequest http://127.0.0.1:8088/health -UseBasicParsing; if ($r.StatusCode -ne 200) { throw "HTTP $($r.StatusCode)" } }
Check "f2 official" { $r = Invoke-RestMethod http://127.0.0.1:8088/api/v1/models/status; if (-not $r.data.official -or $r.data.served_run -notmatch "sed_ensemble_t2b") { throw ($r | ConvertTo-Json -Compress) } }
Check "parser" { $r = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/api/v1/retrieval/parse -ContentType application/json -Body '{"question":"Bản ghi nào có tiếng chim?","language":"vi"}'; if (-not $r.success) { throw "parser thất bại" } }
Check "corpus upload" { $r = Invoke-RestMethod "http://127.0.0.1:8088/api/v1/recordings?corpus=upload&limit=1"; if ([int]$r.meta.total -lt 15) { throw ("chỉ có {0} recording" -f $r.meta.total) } }
Check "Qwen model local" { $m = Join-Path $Root "artifacts/llm/Qwen_Qwen3.5-9B-Q4_K_M.gguf"; if (-not (Test-Path $m)) { throw "thiếu $m" } }
Check "BGE-M3 cache local" { $m = Join-Path $Root "artifacts/hf/models--BAAI--bge-m3"; if (-not (Test-Path $m)) { throw "thiếu $m" } }
Check "f2 run local" { if (-not (Test-Path (Join-Path $Root "ml/runs/sed_ensemble_t2b_20260927T200914Z"))) { throw "thiếu run f2" } }
if ($failed) { Write-Host "Kiểm tra thất bại; chạy lại trước demo." -ForegroundColor Red; exit 1 }
Write-Host "Tất cả kiểm tra pass. Chạy script này khoảng 10 phút trước buổi demo; không tự khởi động service."
