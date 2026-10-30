$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$outputPath = Join-Path (Split-Path -Parent $projectRoot) "P7_RAG_Document_QA_submission.zip"
$excludedDirectories = @(
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "docs",
    "chroma_db",
    "htmlcov"
)
$excludedFiles = @(".env", "secrets.toml")

$packageFiles = foreach ($file in Get-ChildItem -LiteralPath $projectRoot -Recurse -File -Force) {
    $relativePath = $file.FullName.Substring($projectRoot.Length).TrimStart("\", "/")
    $pathParts = $relativePath -split "[\\/]"
    if ($pathParts | Where-Object { $excludedDirectories -contains $_ }) {
        continue
    }
    if ($excludedFiles -contains $file.Name -or $file.Extension -in @(".pyc", ".db")) {
        continue
    }
    $file
}

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
if (Test-Path -LiteralPath $outputPath) {
    Remove-Item -LiteralPath $outputPath -Force
}

$archive = [System.IO.Compression.ZipFile]::Open(
    $outputPath,
    [System.IO.Compression.ZipArchiveMode]::Create
)
try {
    foreach ($file in $packageFiles) {
        $relativePath = $file.FullName.Substring($projectRoot.Length).TrimStart("\", "/")
        $entryName = "P7_RAG_Document_QA/" + $relativePath.Replace("\", "/")
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $archive,
            $file.FullName,
            $entryName,
            [System.IO.Compression.CompressionLevel]::Optimal
        ) | Out-Null
    }
}
finally {
    $archive.Dispose()
}

Write-Output "Created submission archive: $outputPath"
