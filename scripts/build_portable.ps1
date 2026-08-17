$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$ModelSource = Join-Path $ProjectRoot "models\mfr"
$Distribution = Join-Path $ProjectRoot "dist\mathlatex"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Development environment not found. Create .venv and install dev dependencies first."
}

& $Python -m PyInstaller --noconfirm --clean --windowed --onedir `
    --name mathlatex `
    --paths (Join-Path $ProjectRoot "src") `
    (Join-Path $ProjectRoot "run_mathlatex.py")

New-Item -ItemType Directory -Force -Path (Join-Path $Distribution "models\mfr") | Out-Null
Copy-Item -LiteralPath (Join-Path $ModelSource "encoder_model.onnx") -Destination (Join-Path $Distribution "models\mfr") -Force
Copy-Item -LiteralPath (Join-Path $ModelSource "decoder_model.onnx") -Destination (Join-Path $Distribution "models\mfr") -Force
Copy-Item -LiteralPath (Join-Path $ModelSource "tokenizer.json") -Destination (Join-Path $Distribution "models\mfr") -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "LICENSE") -Destination $Distribution -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "THIRD_PARTY_NOTICES.md") -Destination $Distribution -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "README.md") -Destination $Distribution -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "licenses") -Destination $Distribution -Recurse -Force

Write-Host "Portable build created: $Distribution"
