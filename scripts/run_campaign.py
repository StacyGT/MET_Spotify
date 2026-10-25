import time
import sys
import os

# Importation de la configuration et des modules de mesure
from config import (
    TARGET_HOST, TARGET_URL, CSV_RAW_PATH, 
    DEFAULT_PROBE_COUNT, INTERVAL_BETWEEN_PROBES, ROUTES_DIR
)
from measure_dns_http import run_single_probe
from measure_route import run_traceroute

def execute_campaign(network_label, probe_count=DEFAULT_PROBE_COUNT):
    """
    Exécute une campagne complète sur le réseau spécifié :
    1. Cartographie de route (L3/L4)
    2. Série de N mesures de performance HTTPS (L7)
    """
    print("=" * 65)
    print(f" Lancement de la campagne MET | Cible : {TARGET_HOST}")
    print(f" Réseau d'accès : {network_label.upper()}")
    print(f" Nombre de requêtes HTTPS : {probe_count}")
    print("=" * 65)

    # 1. Cartographie initiale
    print("\n[Étape 1/2] Exécution de la cartographie réseau (Traceroute)...")
    try:
        run_traceroute(network_label)
    except Exception as e:
        print(f"[!] Avertissement : Échec du traceroute ({e})")

    # 2. Campagne de mesures applicatives
    print(f"\n[Étape 2/2] Collecte de {probe_count} sondes HTTPS...")
    successful_probes = 0

    for i in range(1, probe_count + 1):
        print(f"-> Sondage {i}/{probe_count} ... ", end="", flush=True)
        success = run_single_probe(network_label=network_label)
        
        if success:
            successful_probes += 1
        
        if i < probe_count:
            time.sleep(INTERVAL_BETWEEN_PROBES)

    print("\n" + "=" * 65)
    print(f" Campagne terminée : {successful_probes}/{probe_count} mesures réussies.")
    print(f" Données enregistrées dans : {CSV_RAW_PATH}")
    print("=" * 65)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n[!] Usage : python scripts/run_campaign.py <nom_du_reseau> [nombre_de_sondes]")
        print("Exemples :")
        print("  python scripts/run_campaign.py quantic")
        print("  python scripts/run_campaign.py free_mobile 50")
        print("  python scripts/run_campaign.py eduroam 30\n")
        sys.exit(1)

    net_env = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PROBE_COUNT
    
    execute_campaign(network_label=net_env, probe_count=count)