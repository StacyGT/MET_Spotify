#!/bin/bash

# ==============================================================================
# Campagne de Métrologie Réseau - Ethernet TC (INSA Lyon)
# Version robuste (échappement strict des % de curl)
# ==============================================================================

OUTPUT_DIR="data/raw"
mkdir -p "$OUTPUT_DIR"

CDN_FILE="$OUTPUT_DIR/cdn_measures_ethernet_tc.csv"
RAW_FILE="$OUTPUT_DIR/raw_measures_ethernet_tc.csv"

# User-Agent Chrome pour éviter les rejets anti-bot CDN
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TARGET_URL="https://open.spotify.com"

# Modèle de format curl avec échappement % pour Bash/printf
FMT_CDN='%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{size_download},%{speed_download}\n'
FMT_RAW='%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{http_code}\n'

echo "======================================================================"
echo "  [1/2] Campagne CDN Ethernet TC (30 mesures)"
echo "======================================================================"
echo "timestamp,dns_lookup,tcp_connect,tls_handshake,ttfb,total_time,download_size_bytes,download_speed_bps" > "$CDN_FILE"

for i in {1..30}; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  
  METRICS=$(curl -s -k -L -A "$UA" -w "$FMT_CDN" -o /dev/null "$TARGET_URL")
  
  echo "\"$TIMESTAMP\",$METRICS" >> "$CDN_FILE"
  
  TOTAL_S=$(echo "$METRICS" | cut -d',' -f5)
  SIZE_B=$(echo "$METRICS" | cut -d',' -f6)
  echo "  --> [$i/30] CDN enregistré | Total: ${TOTAL_S}s | Taille: ${SIZE_B} octets"
  sleep 1
done

echo ""
echo "======================================================================"
echo "  [2/2] Campagne RTT Ethernet TC (50 mesures)"
echo "======================================================================"
echo "timestamp,rtt_dns,rtt_tcp,rtt_tls,ttfb,total_time,status_code" > "$RAW_FILE"

for i in {1..50}; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  
  METRICS=$(curl -s -k -L -A "$UA" -w "$FMT_RAW" -o /dev/null "$TARGET_URL")
  
  echo "\"$TIMESTAMP\",$METRICS" >> "$RAW_FILE"
  
  TOTAL_S=$(echo "$METRICS" | cut -d',' -f5)
  echo "  --> [$i/50] RTT enregistré | Total: ${TOTAL_S}s"
  sleep 1
done

echo ""
echo "======================================================================"
echo "  Campagne terminée avec succès !"
echo "======================================================================"
echo "Vérification des premières lignes de $CDN_FILE :"
head -n 4 "$CDN_FILE"