Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Campagne de mesures : ETHERNET TC (Cable)  " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

python scripts/measure_route.py ethernet_tc
python scripts/run_cdn_campaign.py ethernet_tc 30
python scripts/run_campaign.py ethernet_tc 30

Write-Host "`n[OK] Mesures Ethernet TC terminees avec succes !" -ForegroundColor Green
