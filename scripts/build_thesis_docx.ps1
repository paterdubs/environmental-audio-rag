param(
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$thesisDir = Join-Path $repoRoot "docs\thesis"
$referenceDoc = Join-Path $repoRoot "report\Mau bao cao KLTN_DS.docx"
$bibliography = Join-Path $thesisDir "bibliography.bib"
$citationStyle = Join-Path $thesisDir "ieee.csl"
$figureFilter = Join-Path $thesisDir "number_thesis_figures.lua"
$metadataFile = Join-Path $thesisDir "preview_metadata.yaml"

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $thesisDir "build\khoaluan.docx"
}
elseif (-not [System.IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath = Join-Path $repoRoot $OutputPath
}

$pandocCandidates = @(
    "C:\Program Files\Pandoc\pandoc.exe",
    (Join-Path $env:LOCALAPPDATA "Pandoc\pandoc.exe")
)
$pandocPath = $null
$pandocCommand = Get-Command pandoc -ErrorAction SilentlyContinue
if ($null -ne $pandocCommand) {
    $pandocPath = $pandocCommand.Source
}
else {
    foreach ($candidate in $pandocCandidates) {
        if (Test-Path -LiteralPath $candidate) {
            $pandocPath = $candidate
            break
        }
    }
}

if ([string]::IsNullOrWhiteSpace($pandocPath)) {
    throw "Pandoc was not found. Install JohnMacFarlane.Pandoc before building the thesis."
}

$requiredFiles = @($referenceDoc, $bibliography, $citationStyle, $figureFilter, $metadataFile)
foreach ($requiredFile in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $requiredFile)) {
        throw "Required file is missing: $requiredFile"
    }
}

$chapters = @()
foreach ($number in 1..7) {
    $chapter = Join-Path $thesisDir ("ch{0}.md" -f $number)
    if (Test-Path -LiteralPath $chapter) {
        $chapters += $chapter
    }
}
if ($chapters.Count -eq 0) {
    throw "No thesis chapters were found in docs/thesis."
}

$outputDirectory = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$pandocArguments = @(
    "--from=markdown+tex_math_dollars",
    "--to=docx",
    "--standalone",
    "--toc",
    "--toc-depth=3",
    "--citeproc",
    "--bibliography=$bibliography",
    "--csl=$citationStyle",
    "--reference-doc=$referenceDoc",
    "--lua-filter=$figureFilter",
    "--resource-path=$thesisDir",
    "--metadata-file=$metadataFile",
    "--output=$OutputPath"
)
$pandocArguments += $chapters

Write-Host ("Building {0} thesis chapters with Pandoc..." -f $chapters.Count)
& $pandocPath @pandocArguments
$rc = $LASTEXITCODE
if ($rc -ne 0) {
    throw "Pandoc failed with exit code $rc."
}

Write-Host "Created: $OutputPath"
