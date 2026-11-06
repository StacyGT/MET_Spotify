#!/bin/bash

OUTPUT_DIR="data/raw"
mkdir -p "$OUTPUT_DIR"

CDN_FILE="$OUTPUT_DIR/cdn_measures_ethernet_tc.csv"

echo "======================================================================"
echo "  Campagne CDN Ethernet TC - Capture Haute Précision"
echo "======================================================================"

# En-tête CSV
echo "timestamp,dns_lookup,tcp_connect,tls_handshake,ttfb,total_time,download_size_bytes,download_speed_bps" > "$CDN_FILE"

# Format de sortie curl sécurisé
CURL_FORMAT='%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{size_download},%{speed_download}'

for i in {1..30}; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  
  # Execution avec option -k (ignore d'éventuels certificats proxy de salle) et -L (redirections)
  METRICS=$(curl -s -k -L -o /dev/null -w "$CURL_FORMAT" "https://open.spotify.com")
  
  echo "\"$TIMESTAMP\",$METRICS" >> "$CDN_FILE"
  
  TOTAL_S=$(echo "$METRICS" | cut -d',' -f5)
  echo "[$i/30] Temps total mesuré : ${TOTAL_S} s"
  sleep 1
done

RAW_FILE="$OUTPUT_DIR/raw_measures_ethernet_tc.csv"
echo "timestamp,rtt_dns,rtt_tcp,rtt_tls,ttfb,total_time,status_code" > "$RAW_FILE"
CURL_FORMAT_RAW='%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{http_code}'

for i in {1..50}; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  METRICS=$(curl -s -k -L -o /dev/null -w "$CURL_FORMAT_RAW" "https://open.spotify.com")
  echo "\"$TIMESTAMP\",$METRICS" >> "$RAW_FILE"
  sleep 1
done

echo "Terminé ! Vérification des 3 premières lignes :"
head -n 4 "$CDN_FILE"