#!/bin/bash

# Configuration du dossier et des fichiers
OUTPUT_DIR="data/raw"
mkdir -p "$OUTPUT_DIR"

CDN_FILE="$OUTPUT_DIR/cdn_measures_ethernet_tc.csv"
RAW_FILE="$OUTPUT_DIR/raw_measures_ethernet_tc.csv"

# Configuration du proxy INSA (décommenter si nécessaire)
export http_proxy="http://proxy.insa-lyon.fr:3128"
export https_proxy="http://proxy.insa-lyon.fr:3128"

# En-têtes CSV
echo "timestamp,dns_lookup,tcp_connect,tls_handshake,ttfb,total_time,download_size_bytes,download_speed_bps" > "$CDN_FILE"
echo "timestamp,rtt_dns,rtt_tcp,rtt_tls,ttfb,total_time,status_code" > "$RAW_FILE"

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TARGET_URL="https://open.spotify.com"

echo "======================================================================"
echo "  Lancement de la collecte Ethernet TC (avec Proxy INSA)"
echo "======================================================================"

for i in {1..30}; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  
  # Execution curl avec proxy et capture des métriques
  METRICS_CDN=$(curl -s -k -L -A "$UA" -o /dev/null -w "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{size_download},%{speed_download}" "$TARGET_URL")
  METRICS_RAW=$(curl -s -k -L -A "$UA" -o /dev/null -w "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{http_code}" "$TARGET_URL")
  
  echo "\"$TIMESTAMP\",$METRICS_CDN" >> "$CDN_FILE"
  echo "\"$TIMESTAMP\",$METRICS_RAW" >> "$RAW_FILE"
  
  TOTAL_S=$(echo "$METRICS_CDN" | cut -d',' -f5)
  SIZE_B=$(echo "$METRICS_CDN" | cut -d',' -f6)
  
  echo "[$i/30] Temps total : ${TOTAL_S} s | Taille : ${SIZE_B} octets"
  sleep 1
done

echo ""
echo "Terminé ! Aperçu du fichier $CDN_FILE :"
head -n 5 "$CDN_FILE"