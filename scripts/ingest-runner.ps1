param(
  [Parameter(Mandatory=$true)][string]$StoreId,
  [Parameter(Mandatory=$true)][string]$SourceUrl,
  [Parameter(Mandatory=$true)][string]$InputPath,
  [string]$ApiBase = "http://127.0.0.1:8000"
)

if (-not (Test-Path $InputPath)) {
  Write-Error "InputPath not found: $InputPath"
  exit 1
}

$text = ""
$ext = [System.IO.Path]::GetExtension($InputPath).ToLower()

if ($ext -in ".txt", ".text") {
  $text = Get-Content $InputPath -Raw
} else {
  if (-not (Get-Command tesseract -ErrorAction SilentlyContinue)) {
    Write-Error "Tesseract not found in PATH."
    exit 1
  }
  $outBase = [System.IO.Path]::ChangeExtension($InputPath, $null)
  & tesseract $InputPath $outBase | Out-Null
  $outTxt = $outBase + ".txt"
  $text = Get-Content $outTxt -Raw
}

$payload = @{
  store_id = [int]$StoreId
  source_url = $SourceUrl
  text = $text
}

$json = $payload | ConvertTo-Json -Depth 4
Invoke-RestMethod -Method Post -Uri "$ApiBase/ingestion/circulars/run" -Body $json -ContentType "application/json"
