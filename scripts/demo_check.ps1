$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
function Check([string]$Name, [scriptblock]$Action) {
    try { & $Action; Write-Host ("[OK] {0}" -f $Name) -ForegroundColor Green }
    catch { Write-Host ("[FAIL] {0}: {1}" -f $Name, $_.Exception.Message) -ForegroundColor Red; $script:failed = $true }
}
Check "Docker Desktop" { $v = docker version --format "{{.Server.Version}}" 2>$null; if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($v)) { throw "Docker chưa chạy" } }
Check "API health" { $r = Invoke-WebRequest http://127.0.0.1:8088/health -UseBasicParsing; if ($r.StatusCode -ne 200) { throw "HTTP $($r.StatusCode)" } }
Check "hệ thống phục vụ (B0, hoặc B0 + LBR)" { $r = Invoke-RestMethod http://127.0.0.1:8088/api/v1/models/status; if ($r.data.served_run -notmatch "sed_served_B0" -or (-not $r.data.official -and -not $r.data.lbr_run)) { throw ($r | ConvertTo-Json -Compress) } }
Check "parser" { $r = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/api/v1/retrieval/parse -ContentType application/json -Body '{"question":"Bản ghi nào có tiếng chim?","language":"vi"}'; if (-not $r.success) { throw "parser thất bại" } }
Check "corpus upload" { $r = Invoke-RestMethod "http://127.0.0.1:8088/api/v1/recordings?corpus=upload&limit=1"; if ([int]$r.meta.total -lt 15) { throw ("chỉ có {0} recording" -f $r.meta.total) } }
Check "Qwen model local" { $m = Join-Path $Root "artifacts/llm/Qwen_Qwen3.5-9B-Q4_K_M.gguf"; if (-not (Test-Path $m)) { throw "thiếu $m" } }
Check "BGE-M3 cache local" { $m = Join-Path $Root "artifacts/hf/models--BAAI--bge-m3"; if (-not (Test-Path $m)) { throw "thiếu $m" } }
Check "run B0 phục vụ local" { if (-not (Test-Path (Join-Path $Root "ml/runs/sed_served_B0_20261107T175659Z"))) { throw "thiếu run B0" } }
Check "run LBR V3 local" { if (-not (Test-Path (Join-Path $Root "ml/runs/sed_lbr_B0v3_20261110T042337Z/lbr_model.pkl"))) { throw "thiếu run LBR V3" } }
if ($failed) { Write-Host "Kiểm tra thất bại; chạy lại trước demo." -ForegroundColor Red; exit 1 }
Write-Host "Tất cả kiểm tra pass. Chạy script này khoảng 10 phút trước buổi demo; không tự khởi động service."
