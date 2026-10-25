import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Ajout du chemin parent pour importer la configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.config import CSV_RAW_PATH, BASE_DIR
except ImportError:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSV_RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "raw_measures.csv")

# Palette de couleurs optimisée pour la publication scientifique
NET_COLORS = {
    "quantic": "#1f77b4",       # Bleu
    "eduroam": "#ff7f0e",       # Orange
    "free_mobile": "#2ca02c",   # Vert
    "ethernet_tc": "#d62728"    # Rouge
}

FIGURES_DIR = os.path.join(BASE_DIR, "results", "figures")


def setup_matplotlib_style():
    """Configure le style graphique global pour un rendu papier/rapport (publication ready)."""
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 10,
        'axes.labelsize': 10,
        'axes.titlesize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'figure.titlesize': 12,
        'figure.dpi': 300
    })


def load_data():
    """Charge et valide le fichier CSV de mesures brutes."""
    if not os.path.exists(CSV_RAW_PATH):
        print(f"[!] Erreur : Le fichier '{CSV_RAW_PATH}' n'existe pas encore.")
        return None

    df = pd.read_csv(CSV_RAW_PATH)
    if df.empty:
        print("[!] Erreur : Le fichier CSV est vide.")
        return None

    # Conversion des colonnes de temps (s -> ms) pour la lisibilité
    time_cols = ['dns_time_s', 'tcp_connect_s', 'tls_handshake_s', 'ttfb_s', 'download_time_s', 'total_time_s']
    for col in time_cols:
        if col in df.columns:
            df[col.replace('_s', '_ms')] = df[col] * 1000.0

    return df


def plot_ecdf_ttfb(df):
    """Génère la fonction de répartition cumulative empirique (ECDF) du TTFB par réseau."""
    fig, ax = plt.subplots(figsize=(6, 3.5))

    networks = df['network'].unique()
    for net in networks:
        sub_df = df[df['network'] == net]
        ttfb_ms = sub_df['ttfb_ms'].dropna().values
        
        if len(ttfb_ms) == 0:
            continue

        sorted_data = np.sort(ttfb_ms)
        y = np.arange(1, len(sorted_data) + 1) / len(sorted_data)

        color = NET_COLORS.get(net, None)
        ax.plot(
            sorted_data, y, 
            marker='.', linestyle='none', 
            label=f"{net} (n={len(sorted_data)})", 
            color=color, alpha=0.7
        )

    ax.set_xlabel("Time To First Byte - TTFB (ms)", fontweight='bold')
    ax.set_ylabel("ECDF (Probabilité cumulative)", fontweight='bold')
    ax.set_title("Distribution cumulative du temps d'accès (TTFB)", fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='lower right', frameon=True)

    plt.tight_layout()
    out_path = os.path.join(FIGURES_DIR, "ecdf_ttfb_spotify.pdf")
    plt.savefig(out_path, format="pdf")
    plt.close()
    print(f"[+] ECDF générée : {out_path}")


def plot_boxplot_performance(df):
    """Génère des Boxplots comparatifs (TCP Handshake vs TTFB vs Temps Total) par réseau."""
    fig, ax = plt.subplots(figsize=(6.5, 3.8))

    networks = df['network'].unique()
    data_to_plot = []
    labels = []

    for net in networks:
        sub_df = df[df['network'] == net]
        ttfb_vals = sub_df['ttfb_ms'].dropna().values
        if len(ttfb_vals) > 0:
            data_to_plot.append(ttfb_vals)
            labels.append(net)

    if not data_to_plot:
        return

    bplot = ax.boxplot(
        data_to_plot, 
        patch_artist=True, 
        tick_labels=labels,
        flierprops=dict(marker='o', markersize=3, alpha=0.5)
    )

    # Coloration des boxplots selon la charte des réseaux
    for patch, label in zip(bplot['boxes'], labels):
        patch.set_facecolor(NET_COLORS.get(label, '#1f77b4'))
        patch.set_alpha(0.6)

    ax.set_ylabel("Temps de réponse (ms)", fontweight='bold')
    ax.set_title("Variabilité de la latence d'accès (TTFB) selon le réseau", fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')

    plt.tight_layout()
    out_path = os.path.join(FIGURES_DIR, "boxplot_ttfb_per_network.pdf")
    plt.savefig(out_path, format="pdf")
    plt.close()
    print(f"[+] Boxplot généré : {out_path}")


def plot_latency_breakdown(df):
    """Génère un graphique montrant la décomposition moyenne des phases de connexion (DNS, TCP, TLS, TTFB)."""
    metrics = ['dns_time_ms', 'tcp_connect_ms', 'tls_handshake_ms', 'download_time_ms']
    labels_map = {
        'dns_time_ms': 'Résolution DNS',
        'tcp_connect_ms': 'Handshake TCP (RTT)',
        'tls_handshake_ms': 'Handshake TLS',
        'download_time_ms': 'Téléchargement'
    }

    avg_df = df.groupby('network')[metrics].mean()
    if avg_df.empty:
        return

    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    
    avg_df.rename(columns=labels_map).plot(
        kind='bar', 
        stacked=True, 
        ax=ax, 
        colormap='tab10', 
        alpha=0.85, 
        edgecolor='black', 
        linewidth=0.5
    )

    ax.set_ylabel("Temps moyen (ms)", fontweight='bold')
    ax.set_xlabel("Réseau d'accès", fontweight='bold')
    ax.set_title("Décomposition des phases de connexion applicative", fontweight='bold')
    ax.legend(title="Phases", bbox_to_anchor=(1.02, 1), loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    plt.xticks(rotation=0)

    plt.tight_layout()
    out_path = os.path.join(FIGURES_DIR, "breakdown_phases_per_network.pdf")
    plt.savefig(out_path, format="pdf")
    plt.close()
    print(f"[+] Graphique de décomposition généré : {out_path}")


def main():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    setup_matplotlib_style()

    df = load_data()
    if df is None:
        return

    print(f"[*] Analyse de {len(df)} mesures brutes enregistrées...")
    plot_ecdf_ttfb(df)
    plot_boxplot_performance(df)
    plot_latency_breakdown(df)
    print("[✔] Toutes les figures ont été générées au format PDF dans 'results/figures/'.")


if __name__ == "__main__":
    main()