param(
    [string]$Path = "report\Bao_cao_KLTN_giua_ky_environmental_audio_rag.docx",
    [switch]$NoPdf
)

# Cập nhật mọi Word field (mục lục, danh mục hình/bảng, STYLEREF/SEQ của caption, REF, PAGE)
# bằng chính Microsoft Word qua COM, lưu lại DOCX và xuất PDF xem trước.
# Không thay đổi nội dung chữ; chỉ tính lại kết quả field và số trang.

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not [System.IO.Path]::IsPathRooted($Path)) { $Path = Join-Path $repoRoot $Path }
$Path = (Resolve-Path -LiteralPath $Path).Path
$pdfPath = [System.IO.Path]::ChangeExtension($Path, ".pdf")

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0  # wdAlertsNone
try {
    $doc = $word.Documents.Open($Path, $false, $false, $false)
    # Hai lượt: lượt đầu đánh số caption/trang, lượt sau để REF và mục lục thấy số cuối cùng.
    foreach ($pass in 1..2) {
        foreach ($story in $doc.StoryRanges) {
            $range = $story
            while ($null -ne $range) {
                [void]$range.Fields.Update()
                $range = $range.NextStoryRange
            }
        }
        foreach ($toc in $doc.TablesOfContents) { [void]$toc.Update() }
        foreach ($tof in $doc.TablesOfFigures) { [void]$tof.Update() }
    }
    $doc.Save()
    $pages = $doc.ComputeStatistics(2)  # wdStatisticPages
    if (-not $NoPdf) {
        $doc.ExportAsFixedFormat($pdfPath, 17)  # wdExportFormatPDF
    }
    $doc.Close($false)
    Write-Host "Fields updated: $Path ($pages pages)"
    if (-not $NoPdf) { Write-Host "PDF: $pdfPath" }
}
finally {
    $word.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
}
