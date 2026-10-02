param(
    [switch]$ResetHistory,
    [int]$HistoryCount = 20
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$VenvPython = Join-Path $Root ".venv/Scripts/python.exe"
$PidFile = Join-Path $env:TEMP "environmental-audio-rag-demo-llama.pid"
$LogFile = Join-Path $env:TEMP "environmental-audio-rag-demo-llama.log"
$ErrorLogFile = Join-Path $env:TEMP "environmental-audio-rag-demo-llama.error.log"

function Fail-Step([string]$Step, [string]$Message) {
    Write-Error ("[{0}] {1}" -f $Step, $Message)
    exit 1
}

function Wait-Http([string]$Uri, [string]$Step, [int]$TimeoutSeconds = 300) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) { return }
        } catch { }
        Start-Sleep -Seconds 2
    }
    Fail-Step $Step ("không sẵn sàng sau {0} giây: {1}" -f $TimeoutSeconds, $Uri)
}

$dockerServer = docker version --format "{{.Server.Version}}" 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($dockerServer)) {
    Fail-Step "Docker" "Docker Desktop chưa chạy."
}
$config = Get-Content (Join-Path $Root "ml/configs/caption_llm.yaml") -Raw
$modelMatch = [regex]::Match($config, "(?m)^\s*local_path:\s*(\S+)")
if (-not $modelMatch.Success) { Fail-Step "llama.cpp" "Không đọc được model path từ caption_llm.yaml." }
$model = Join-Path $Root $modelMatch.Groups[1].Value
if (-not (Test-Path $model -PathType Leaf)) { Fail-Step "llama.cpp" ("Thiếu model: {0}" -f $model) }

$llamaReady = Test-NetConnection -ComputerName 127.0.0.1 -Port 8081 -InformationLevel Quiet
if (-not $llamaReady) {
    $server = Get-ChildItem (Join-Path $Root "artifacts/llm") -Filter "llama-server.exe" -Recurse -File | Select-Object -First 1
    if ($null -eq $server) { Fail-Step "llama.cpp" "Không tìm thấy llama-server.exe trong artifacts/llm." }
    Write-Host "[llama.cpp] khởi động Qwen3.5-9B trên cổng 8081..."
    $arguments = "-m `"$model`" -ngl 99 -c 4096 -np 1 --jinja --port 8081"
    $process = Start-Process -FilePath $server.FullName -ArgumentList $arguments -WorkingDirectory $Root `
        -RedirectStandardOutput $LogFile -RedirectStandardError $ErrorLogFile -WindowStyle Hidden -PassThru
    Set-Content -Path $PidFile -Value $process.Id -Encoding ASCII
    Wait-Http "http://127.0.0.1:8081/health" "llama.cpp" 180
} else { Write-Host "[llama.cpp] đã có server trên cổng 8081." }

Write-Host "[Compose] khởi động db, inference, api và frontend..."
docker compose --profile app up -d --build
if ($LASTEXITCODE -ne 0) { Fail-Step "Compose" "docker compose up thất bại." }
Wait-Http "http://127.0.0.1:8088/health" "api" 300
$status = Invoke-RestMethod "http://127.0.0.1:8088/api/v1/models/status"
if (-not $status.success -or -not $status.data.official -or $status.data.served_run -notmatch "sed_ensemble_t2b") {
    Fail-Step "models/status" "API không báo f2 official=true."
}
$parse = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8088/api/v1/retrieval/parse" `
    -ContentType "application/json" -Body '{"question":"Bản ghi nào có tiếng chim?","language":"vi"}'
if (-not $parse.success) { Fail-Step "retrieval/parse" "Parser không xử lý được câu mẫu." }
$history = Invoke-RestMethod "http://127.0.0.1:8088/api/v1/recordings?corpus=upload&limit=1"
if ($ResetHistory -or [int]$history.meta.total -eq 0) {
    $seedArgs = @("scripts/seed_demo_history.py", "--base-url", "http://127.0.0.1:8088",
                  "--count", [string]$HistoryCount)
    if ($ResetHistory) { $seedArgs += "--reset" }
    Write-Host "[History] nạp $HistoryCount recording TRAIN..."
    & $VenvPython $seedArgs
    if ($LASTEXITCODE -ne 0) { Fail-Step "seed" "Nạp dữ liệu lịch sử thất bại." }
} else { Write-Host ("[History] đã có {0} recording upload; giữ nguyên." -f $history.meta.total) }
Start-Process "http://127.0.0.1:8088"
Write-Host "Demo sẵn sàng: http://127.0.0.1:8088"
