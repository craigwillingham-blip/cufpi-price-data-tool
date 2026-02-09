param(
  [string]$ConfigPath = "..\config\sources.json",
  [string]$OutDir = "..\data\circulars"
)

if (-not (Test-Path $OutDir)) {
  New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
}

$cfg = Get-Content $ConfigPath | ConvertFrom-Json

foreach ($source in $cfg.sources) {
  if (-not $source.enabled) { continue }

  $fileName = "$($source.store)_" + (Get-Date -Format "yyyyMMdd") + ".bin"
  $dest = Join-Path $OutDir $fileName

  Write-Host "Downloading $($source.url) -> $dest"
  Invoke-WebRequest -Uri $source.url -OutFile $dest

  # Detect file type (simple magic bytes)
  $bytes = Get-Content $dest -Encoding Byte -TotalCount 4
  $sig = [System.BitConverter]::ToString($bytes)

  if ($sig -match "25-50-44-46") {
    Write-Host "Detected PDF"
  } elseif ($sig -match "FF-D8-FF" -or $sig -match "89-50-4E-47") {
    Write-Host "Detected image"
  } else {
    Write-Host "Unknown type, treating as HTML"
  }

  # Placeholder: call OCR or parser
  Write-Host "Queued for parsing"
}
