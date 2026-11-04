import os
import sys
import socket
import subprocess
import pandas as pd
from datetime import datetime

# Importer configuration globale
from config import TARGET_HOST, TARGET_URL, CSV_RAW_PATH, NULL_DEVICE,TARGET_URL_CDN, CSV_CDN_PATH


def get_dns_info(host):
    """
    Résout le nom de domaine pour capturer l'IP Anycast
    du CDN (Fastly) assignée en ce moment.
    """
    try:
        ip_address = socket.gethostbyname(host)
        return ip_address
    except Exception as e:
        return f"ERROR: {e}"


def measure_curl_breakdown(url):
    """
    Utilise cURL pour décomposer de manière précise la connexion HTTPS:
    - dns_time_s        : Temps de résolution DNS
    - tcp_connect_s     : Temps d'établissement du Handshake TCP (RTT pur)
    - tls_handshake_s   : Temps de négociation de la couche de chiffrement TLS
    - ttfb_s            : Time To First Byte (Temps d'accès au premier octet)
    - download_time_s   : Temps de téléchargement pur du contenu
    - total_time_s      : Temps total accumulé
    """
    # Chaine de format de cURL
    format_str = (
        "%{time_namelookup};"
        "%{time_connect};"
        "%{time_appconnect};"
        "%{time_starttransfer};"
        "%{time_total};"
        "%{size_download};"
        "%{http_code}"
    )

    cmd = [
        "curl",
        "-s",
        "-o",
        NULL_DEVICE,
        "-w",
        format_str,
        url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        parts = result.stdout.strip().split(";")

        if len(parts) == 7:
            dns_time = float(parts[0])
            tcp_time = float(parts[1]) - dns_time
            tls_time = (
                float(parts[2]) - float(parts[1]) if float(parts[2]) > 0 else 0
            )
            ttfb = float(parts[3])
            total_time = float(parts[4])
            download_size = int(parts[5])
            http_code = int(parts[6])

            return {
                "dns_time_s": dns_time,
                "tcp_connect_s": tcp_time,
                "tls_handshake_s": tls_time,
                "ttfb_s": ttfb,
                "download_time_s": max(0.0, total_time - ttfb),
                "total_time_s": total_time,
                "download_size_bytes": download_size,
                "http_code": http_code,
            }
    except Exception as e:
        print(f"[!] Erreur exécutant cURL: {e}")
        return None


def run_single_probe(network_label="default_network"):
    """
    Exécute un unique sonde, formate la ligne de données et la concatène
    au fichier CSV de données brutes (`data/raw/raw_measures.csv`).
    """
    timestamp = datetime.now().isoformat()
    target_ip = get_dns_info(TARGET_HOST)
    metrics = measure_curl_breakdown(TARGET_URL)

    if metrics:
        row = {
            "timestamp": timestamp,
            "network": network_label,
            "target_host": TARGET_HOST,
            "resolved_ip": target_ip,
            **metrics,
        }

        # S'assurer que le répertoire data/raw/ existe
        os.makedirs(os.path.dirname(CSV_RAW_PATH), exist_ok=True)

        df = pd.DataFrame([row])
        file_exists = os.path.isfile(CSV_RAW_PATH)

        # Écrire dans le CSV (création de l'en-tête uniquement si le fichier n'existe pas)
        df.to_csv(CSV_RAW_PATH, mode="a", header=not file_exists, index=False)

        print(
            f"OK | IP: {target_ip} | TTFB: {metrics['ttfb_s']*1000:.1f}ms | "
            f"Descarga: {metrics['download_time_s']*1000:.1f}ms | "
            f"Total: {metrics['total_time_s']*1000:.1f}ms"
        )
        return True
    else:
        print("ÉCHEC (Sonde désactivée ou erreur de réseau)")
        return False


if __name__ == "__main__":
    # Permet de exécuter le script de manière individuelle pour des tests rapides
    net_env = sys.argv[1] if len(sys.argv) > 1 else "test_network"
    print(f"[*] Lancement d'une sonde individuelle sur le réseau: '{net_env}'...")
    run_single_probe(network_label=net_env)


#CDN Media Probe

    from config import TARGET_URL_CDN, CSV_CDN_PATH

def run_single_probe_cdn(network_label="quantic"):
    timestamp = datetime.now().isoformat()
    
    curl_format = "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_starttransfer},%{time_total},%{size_download},%{http_code}\n"
    null_output = "NUL" if os.name == 'nt' else "/dev/null"
    curl_bin = "curl.exe" if os.name == 'nt' else "curl"
    
    cmd = [
        curl_bin, "-L", "-o", null_output,
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "-s", "-w", curl_format,
        TARGET_URL_CDN
    ]

    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
        dns, tcp_conn, tls_conn, ttfb, total_time, size_bytes, http_code = map(float, output.split(','))

        dns_time = dns
        tcp_connect = max(0.0, tcp_conn - dns) if tcp_conn > 0 else 0.0
        tls_handshake = max(0.0, tls_conn - tcp_conn) if tls_conn > 0 else 0.0
        download_time = max(0.0, total_time - ttfb)
        
        # Débit utile (Throughput) en Mbit/s
        throughput_mbps = (size_bytes * 8.0 / total_time / 1e6) if total_time > 0 else 0.0

        row_data = {
            "timestamp": timestamp,
            "network": network_label,
            "target_url": TARGET_URL_CDN,
            "dns_time_s": dns_time,
            "tcp_connect_s": tcp_connect,
            "tls_handshake_s": tls_handshake,
            "ttfb_s": ttfb,
            "download_time_s": download_time,
            "total_time_s": total_time,
            "download_size_bytes": size_bytes,
            "throughput_mbps": throughput_mbps
        }

        file_exists = os.path.exists(CSV_CDN_PATH)
        df_row = pd.DataFrame([row_data])
        df_row.to_csv(CSV_CDN_PATH, mode='a', header=not file_exists, index=False)

        print(f"OK [HTTP {int(http_code)}] (TTFB: {ttfb*1000:.1f} ms | Taille: {int(size_bytes)} B | Débit: {throughput_mbps:.2f} Mbps)")
        return True

    except Exception as e:
        print(f"ÉCHEC ({e})")
        return False