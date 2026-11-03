import sys
import time
from measure_dns_http import run_single_probe_cdn

if __name__ == "__main__":
    net = sys.argv[1] if len(sys.argv) > 1 else "quantic"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    print(f"[*] Campagne CDN sur '{net}' ({count} sondes)...")
    for i in range(1, count + 1):
        print(f"-> Sondage CDN {i}/{count} ... ", end="", flush=True)
        run_single_probe_cdn(network_label=net)
        time.sleep(1)