param(
  [string]$InputJson,
  [string]$ApiBase = "http://127.0.0.1:8000"
)

if (-not $InputJson) {
  Write-Error "Provide -InputJson path"
  exit 1
}

$body = Get-Content $InputJson -Raw

Invoke-RestMethod -Method Post -Uri "$ApiBase/ingestion/circulars/run" -Body $body -ContentType "application/json"
