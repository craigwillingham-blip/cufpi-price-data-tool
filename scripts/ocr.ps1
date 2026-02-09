param(
  [Parameter(Mandatory=$true)][string]$InputPath,
  [string]$OutputPath = "ocr-output"
)

if (-not (Get-Command tesseract -ErrorAction SilentlyContinue)) {
  Write-Error "Tesseract not found. Install and add to PATH."
  exit 1
}

$tgt = [System.IO.Path]::ChangeExtension($OutputPath, $null)

Write-Host "Running OCR on $InputPath"
& tesseract $InputPath $tgt

Write-Host "OCR output: $tgt.txt"
