#!/bin/bash

OUTPUT_DIR="data/raw"
mkdir -p "$OUTPUT_DIR"

TRACE_FILE="$OUTPUT_DIR/traceroute_ethernet_tc.txt"

echo "======================================================"
echo "  Capture de la route (Tracepath Ethernet TC)"
echo "======================================================"
echo "Timestamp: $(date +"%Y-%m-%d %H:%M:%S")" > "$TRACE_FILE"
echo "Target: proxy.insa-lyon.fr" >> "$TRACE_FILE"
echo "------------------------------------------------------" >> "$TRACE_FILE"

# tracepath ne nécessite aucun privilège root
tracepath proxy.insa-lyon.fr >> "$TRACE_FILE" 2>&1

echo "Terminé ! Aperçu du fichier généré :"
cat "$TRACE_FILE"