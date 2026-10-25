import sys
import os
import subprocess
from datetime import datetime

# Import de la configuration centralisée
try:
    from config import TARGET_HOST, ROUTES_DIR
except ImportError:
    TARGET_HOST = "open.spotify.com"
    ROUTES_DIR = "data/raw/routes"

def run_traceroute(network_label):
    os.makedirs(ROUTES_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(ROUTES_DIR, f"route_{network_label}_{timestamp}.txt")
    
    # Choix de la commande selon le système d'exploitation
    if sys.platform.startswith("win"):
        # -d évite la résolution inverse DNS trop lente par saut
        cmd = ["tracert", "-d", TARGET_HOST]
    else:
        # Sur Linux, traceroute TCP port 443 pour traverser les pare-feux
        cmd = ["traceroute", "-n", "-T", "-p", "443", TARGET_HOST]
        
    print(f"[*] Lancement de la cartographie sur {network_label} vers {TARGET_HOST}...")
    
    with open(out_file, "w", encoding="utf-8") as f:
        # Redirection propre de la sortie d'erreur vers STDOUT ou la console
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True, check=True)
        
    print(f"[+] Cartographie enregistrée dans : {out_file}")

if __name__ == "__main__":
    net = sys.argv[1] if len(sys.argv) > 1 else "unknown_net"
    run_traceroute(net)