#!/bin/bash

# ==============================================================================
# Campagne de Métrologie Réseau - Ethernet TC (INSA Lyon)
# Génération automatique des CSV pour la Campagne CDN et la Campagne Continue
# ==============================================================================

OUTPUT_DIR="data/raw"
mkdir -p "$OUTPUT_DIR"

# ------------------------------------------------------------------------------
# 1. CAMPAGNE CDN (30 mesures rapides pour fig4_cross_network_breakdown)
# ------------------------------------------------------------------------------
CDN_FILE="$OUTPUT_DIR/cdn_measures_ethernet_tc.csv"

echo "======================================================================"
echo "  [1/2] Lancement de la Campagne CDN (30 mesures)"
echo "======================================================================"
echo "Fichier cible : $CDN_FILE"
echo ""

# En-tête exact attendu par generate_figures.py
echo "timestamp,dns_lookup,tcp_connect,tls_handshake,ttfb,total_time,download_size_bytes,download_speed_bps" > "$CDN_FILE"

for i in {1..30}; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  
  # Capture des 7 métriques brutes via curl
  METRICS=$(curl -s -o /dev/null -w "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{size_download},%{speed_download}" "https://open.spotify.com")
  
  # Ajout au fichier CSV
  echo "\"$TIMESTAMP\",$METRICS" >> "$CDN_FILE"
  
  TOTAL_S=$(echo "$METRICS" | cut -d',' -f5)
  echo "  --> Mesure CDN [$i/30] enregistrée (Temps total: ${TOTAL_S} s)"
  sleep 1
done

echo ""
echo "--> Campagne CDN terminée avec succès !"
echo ""

# ------------------------------------------------------------------------------
# 2. CAMPAGNE RTT / CONTINU (50 mesures rapides pour la comparaison générale)
# ------------------------------------------------------------------------------
RAW_FILE="$OUTPUT_DIR/raw_measures_ethernet_tc.csv"

echo "======================================================================"
echo "  [2/2] Lancement de la Campagne RTT (50 mesures)"
echo "======================================================================"
echo "Fichier cible : $RAW_FILE"
echo ""

# En-tête exact pour la campagne globale
echo "timestamp,rtt_dns,rtt_tcp,rtt_tls,ttfb,total_time,status_code" > "$RAW_FILE"

for i in {1..50}; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  
  # Capture avec le code HTTP de statut
  METRICS=$(curl -s -o /dev/null -w "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{http_code}" "https://open.spotify.com")
  
  echo "\"$TIMESTAMP\",$METRICS" >> "$RAW_FILE"
  
  TOTAL_S=$(echo "$METRICS" | cut -d',' -f5)
  echo "  --> Mesure RTT [$i/50] enregistrée (Temps total: ${TOTAL_S} s)"
  sleep 1
done

echo ""
echo "======================================================================"
echo "  Toutes les campagnes sont terminées avec succès !"
echo "======================================================================"