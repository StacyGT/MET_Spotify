#!/bin/bash

OUTPUT_DIR="data/raw"
mkdir -p "$OUTPUT_DIR"

TRACE_FILE="$OUTPUT_DIR/traceroute_ethernet_tc.txt"

echo "======================================================"
echo "  Capture du chemin réseau (Ethernet TC - INSA)"
echo "======================================================"
echo "Timestamp: $(date +"%Y-%m-%d %H:%M:%S")" > "$TRACE_FILE"
echo "Cible: proxy.insa-lyon.fr / open.spotify.com" >> "$TRACE_FILE"
echo "------------------------------------------------------" >> "$TRACE_FILE"

# 1. Tentative TCP Traceroute (Port 3128 / 80)
if command -v tcptraceroute &> /dev/null; then
    echo "[+] Exécution de tcptraceroute vers le proxy INSA..."
    tcptraceroute proxy.insa-lyon.fr 3128 >> "$TRACE_FILE" 2>&1
# 2. Tentative traceroute en mode TCP (SYN)
elif traceroute -T -p 80 open.spotify.com &> /dev/null; then
    echo "[+] Exécution de traceroute TCP..."
    traceroute -T -p 80 open.spotify.com >> "$TRACE_FILE" 2>&1
# 3. Fallback sur tracepath
elif command -v tracepath &> /dev/null; then
    echo "[+] Exécution de tracepath..."
    tracepath proxy.insa-lyon.fr >> "$TRACE_FILE" 2>&1
else
    echo "[!] Mode classique ICMP fallback..."
    traceroute -m 15 proxy.insa-lyon.fr >> "$TRACE_FILE" 2>&1
fi

echo ""
echo "Terminé ! Aperçu du fichier généré :"
cat "$TRACE_FILE"