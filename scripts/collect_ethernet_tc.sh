#!/bin/bash

OUTPUT_DIR="data/raw"
mkdir -p "$OUTPUT_DIR"

CDN_FILE="$OUTPUT_DIR/cdn_measures_ethernet_tc.csv"
RAW_FILE="$OUTPUT_DIR/raw_measures_ethernet_tc.csv"

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TARGET_URL="https://open.spotify.com"

echo "======================================================"
echo "  [1/2] Campagne CDN Ethernet TC (30 mesures)"
echo "======================================================"

# En-tête CSV exact
echo "timestamp,dns_lookup,tcp_connect,tls_handshake,ttfb,total_time,download_size_bytes,download_speed_bps" > "$CDN_FILE"

for i in {1..30}; do
  TS=$(date +"%Y-%m-%d %H:%M:%S")
  
  # 1. Écrire le timestamp avec guillemets au début de la ligne (sans saut de ligne)
  printf '"%s",' "$TS" >> "$CDN_FILE"
  
  # 2. curl écrit directement les 7 métriques suivies d'un saut de ligne dans le CSV
  curl -s -k -L -A "$UA" -o /dev/null -w "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{size_download},%{speed_download}\n" "$TARGET_URL" >> "$CDN_FILE"
  
  echo "  --> Mesure CDN [$i/30] enregistrée"
  sleep 1
done

echo ""
echo "======================================================"
echo "  [2/2] Campagne RTT Ethernet TC (50 mesures)"
echo "======================================================"

# En-tête RTT
echo "timestamp,rtt_dns,rtt_tcp,rtt_tls,ttfb,total_time,status_code" > "$RAW_FILE"

for i in {1..50}; do
  TS=$(date +"%Y-%m-%d %H:%M:%S")
  
  printf '"%s",' "$TS" >> "$RAW_FILE"
  curl -s -k -L -A "$UA" -o /dev/null -w "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{http_code}\n" "$TARGET_URL" >> "$RAW_FILE"
  
  echo "  --> Mesure RTT [$i/50] enregistrée"
  sleep 1
done

echo ""
echo "======================================================"
echo "  Collecte terminée ! Aperçu des 3 premières lignes :"
echo "======================================================"
head -n 3 "$CDN_FILE"