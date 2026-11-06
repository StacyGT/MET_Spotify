#!/bin/bash

OUTPUT_DIR="data/raw"
mkdir -p "$OUTPUT_DIR"

TRACE_FILE="$OUTPUT_DIR/traceroute_ethernet_tc.txt"
PROXY_INSA="http://proxy.insa-lyon.fr:3128"

echo "======================================================"
echo "  Capture du chemin réseau (Traceroute Ethernet TC)"
echo "======================================================"
echo "Timestamp: $(date +"%Y-%m-%d %H:%M:%S")" > "$TRACE_FILE"
echo "Target: open.spotify.com" >> "$TRACE_FILE"
echo "------------------------------------------------------" >> "$TRACE_FILE"

# 1. Tentative avec traceroute standard (ICMP/UDP)
if command -v traceroute &> /dev/null; then
    echo "[+] Exécution de traceroute..."
    traceroute -m 20 open.spotify.com >> "$TRACE_FILE" 2>&1
elif command -v tracepath &> /dev/null; then
    echo "[+] Exécution de tracepath..."
    tracepath -n open.spotify.com >> "$TRACE_FILE" 2>&1
else
    echo "[-] Ni traceroute ni tracepath ne sont disponibles." >> "$TRACE_FILE"
fi

echo "" >> "$TRACE_FILE"
echo "======================================================" >> "$TRACE_FILE"

echo "Terminé ! Aperçu de la route capturée :"
cat "$TRACE_FILE"