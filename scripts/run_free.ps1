Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Campagne de mesures : FREE MOBILE (4G/5G) " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

python scripts/measure_route.py free_mobile
python scripts/run_cdn_campaign.py free_mobile 30
python scripts/run_campaign.py free_mobile 30

Write-Host "`n[OK] Mesures Free Mobile terminees avec succes !" -ForegroundColor Green