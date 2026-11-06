#!/bin/bash

# Création du dossier cible
OUTPUT_DIR="data/raw"
mkdir -p "$OUTPUT_DIR"

CDN_FILE="$OUTPUT_DIR/cdn_measures_ethernet_tc.csv"
RAW_FILE="$OUTPUT_DIR/raw_measures_ethernet_tc.csv"

# User-Agent pour éviter les blocages CDN
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TARGET_URL="https://open.spotify.com"

# Chaînes de formatage isolées (les simples guillemets empêchent Bash d'effacer les %)
FMT_CDN='%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{size_download},%{speed_download}'
FMT_RAW='%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{http_code}'

echo "======================================================================"
echo "  [1/2] Campagne CDN Ethernet TC (30 mesures)"
echo "======================================================================"

# En-tête CSV (noms de colonnes exactement identiques aux fichiers Python)
echo "timestamp,dns_lookup,tcp_connect,tls_handshake,ttfb,total_time,download_size_bytes,download_speed_bps" > "$CDN_FILE"

for i in {1..30}; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  
  # Exécution de curl avec formatage sécurisé
  METRICS=$(curl -s -k -L -A "$UA" -w "$FMT_CDN" -o /dev/null "$TARGET_URL")
  
  # Écriture dans le fichier CSV
  echo "\"$TIMESTAMP\",$METRICS" >> "$CDN_FILE"
  
  # Extraction du temps total et de la taille pour affichage dans le terminal
  TOTAL_S=$(echo "$METRICS" | cut -d',' -f5)
  SIZE_B=$(echo "$METRICS" | cut -d',' -f6)
  
  echo "  --> [$i/30] Temps total: ${TOTAL_S} s | Taille: ${SIZE_B} octets"
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
  echo "  --> [$i/50] Temps total: ${TOTAL_S} s"
  sleep 1
done

echo ""
echo "======================================================================"
echo "  Vérification de la première ligne de données dans $CDN_FILE :"
echo "======================================================================"
head -n 2 "$CDN_FILE"