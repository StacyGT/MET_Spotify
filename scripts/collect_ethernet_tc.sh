#!/bin/bash

# ==============================================================================
# Campagne de Métrologie Réseau - Ethernet TC (INSA Lyon)
# Capture haute précision des métriques avec curl
# ==============================================================================

OUTPUT_DIR="data/raw"
mkdir -p "$OUTPUT_DIR"

CDN_FILE="$OUTPUT_DIR/cdn_measures_ethernet_tc.csv"

echo "======================================================================"
echo "  [1/2] Lancement de la Campagne CDN (30 mesures haute précision)"
echo "======================================================================"
echo "Fichier cible : $CDN_FILE"
echo ""

# En-tête CSV standard
echo "timestamp,dns_lookup,tcp_connect,tls_handshake,ttfb,total_time,download_size_bytes,download_speed_bps" > "$CDN_FILE"

for i in {1..30}; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  
  # Requête curl vers l'endpoint Spotify avec désactivation du cache DNS si nécessaire
  # Utilisation d'un format explicite sans espaces parasites
  METRICS=$(curl -s -L -o /dev/null -w "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{size_download},%{speed_download}" "https://open.spotify.com")
  
  echo "\"$TIMESTAMP\",$METRICS" >> "$CDN_FILE"
  
  TOTAL_S=$(echo "$METRICS" | cut -d',' -f5)
  echo "  --> Mesure CDN [$i/30] - Total: ${TOTAL_S} s"
  sleep 1
done

RAW_FILE="$OUTPUT_DIR/raw_measures_ethernet_tc.csv"

echo ""
echo "======================================================================"
echo "  [2/2] Lancement de la Campagne RTT (50 mesures)"
echo "======================================================================"
echo "Fichier cible : $RAW_FILE"
echo ""

echo "timestamp,rtt_dns,rtt_tcp,rtt_tls,ttfb,total_time,status_code" > "$RAW_FILE"

for i in {1..50}; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  
  METRICS=$(curl -s -L -o /dev/null -w "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{http_code}" "https://open.spotify.com")
  
  echo "\"$TIMESTAMP\",$METRICS" >> "$RAW_FILE"
  
  TOTAL_S=$(echo "$METRICS" | cut -d',' -f5)
  echo "  --> Mesure RTT [$i/50] - Total: ${TOTAL_S} s"
  sleep 1
done

echo ""
echo "======================================================================"
echo "  Terminé ! Vérifiez avec : head -n 5 $CDN_FILE"
echo "======================================================================"