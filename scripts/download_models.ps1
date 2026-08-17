$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ModelDirectory = Join-Path $ProjectRoot "models\mfr"
$BaseUrl = "https://huggingface.co/breezedeus/pix2text-mfr/resolve/main"

New-Item -ItemType Directory -Force -Path $ModelDirectory | Out-Null

$Files = @(
    "encoder_model.onnx",
    "decoder_model.onnx",
    "tokenizer.json"
)

foreach ($File in $Files) {
    $Destination = Join-Path $ModelDirectory $File
    if (Test-Path -LiteralPath $Destination) {
        Write-Host "Already present: $File"
        continue
    }
    Write-Host "Downloading: $File"
    Invoke-WebRequest -Uri "$BaseUrl/$File?download=true" -OutFile $Destination
}

Write-Host "Models ready: $ModelDirectory"
