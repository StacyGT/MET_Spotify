Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Campagne de mesures : EDUROAM (Wi-Fi INSA) " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

python scripts/measure_route.py eduroam
python scripts/run_cdn_campaign.py eduroam 30
python scripts/run_campaign.py eduroam 30

Write-Host "`n[OK] Mesures Eduroam terminees avec succes !" -ForegroundColor Green