$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  Write-Host "Python not found on PATH. Install Python 3.9+ and retry."
  exit 1
}

$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
  Write-Host "cloudflared not found. Install from https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
  exit 1
}

Start-Process -NoNewWindow -FilePath "python" -ArgumentList "app.py --serve --host 0.0.0.0 --port 5000"
Start-Sleep -Seconds 2
cloudflared tunnel --url http://localhost:5000
