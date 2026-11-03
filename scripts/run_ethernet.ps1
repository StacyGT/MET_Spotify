Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Campagne de mesures : ETHERNET TC (Câble)  " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

python scripts/measure_route.py ethernet_tc
python scripts/run_cdn_campaign.py ethernet_tc 30
python scripts/run_campaign.py ethernet_tc 30

Write-Host "`n[✔] Mesures Ethernet TC terminées avec succès !" -ForegroundColor Green
