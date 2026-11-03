import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuration des chemins
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.config import CSV_RAW_PATH, BASE_DIR
except ImportError:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSV_RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "raw_measures.csv")

FIGURES_DIR = os.path.join(BASE_DIR, "results", "figures")

NET_COLORS = {
    "quantic": "#1f77b4",       # Bleu
    "eduroam": "#ff7f0e",       # Orange
    "free_mobile": "#2ca02c",   # Vert
    "ethernet_tc": "#d62728"    # Rouge
}


def setup_matplotlib_style():
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 10,
        'axes.labelsize': 10,
        'axes.titlesize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'figure.dpi': 300
    })


def save_figure(fig, filename_base):
    os.makedirs(FIGURES_DIR, exist_ok=True)
    fig.savefig(os.path.join(FIGURES_DIR, f"{filename_base}.png"), format="png", dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(FIGURES_DIR, f"{filename_base}.pdf"), format="pdf", bbox_inches='tight')
    print(f"[+] Figure sauvegardée : {filename_base} (.png, .pdf)")


def load_data():
    if not os.path.exists(CSV_RAW_PATH):
        print(f"[!] Erreur : Fichier '{CSV_RAW_PATH}' introuvable.")
        return None

    df = pd.read_csv(CSV_RAW_PATH)
    if df.empty:
        return None

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['dayofweek'] = df['timestamp'].dt.dayofweek  # 0=Lundi, 5=Samedi, 6=Dimanche

    time_cols = ['dns_time_s', 'tcp_connect_s', 'tls_handshake_s', 'ttfb_s', 'download_time_s', 'total_time_s']
    for col in time_cols:
        if col in df.columns:
            df[col.replace('_s', '_ms')] = df[col] * 1000.0

    return df


def plot_quantic_hourly_profile(df):
    """FIGURE 2 : Profil horaire de la latence TTFB sur le réseau Quantic (7 jours)."""
    quantic_df = df[df['network'] == 'quantic']
    if quantic_df.empty:
        return

    hourly_stats = quantic_df.groupby('hour')['ttfb_ms'].agg(
        p25=lambda x: np.percentile(x.dropna(), 25),
        median='median',
        p75=lambda x: np.percentile(x.dropna(), 75)
    ).reset_index()

    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    ax.plot(hourly_stats['hour'], hourly_stats['median'], color=NET_COLORS['quantic'], linewidth=2, label='Médiane TTFB')
    ax.fill_between(
        hourly_stats['hour'], hourly_stats['p25'], hourly_stats['p75'], 
        color=NET_COLORS['quantic'], alpha=0.2, label='Écart interquartile (P25-P75)'
    )

    ax.set_xlabel("Heure de la journée (00h - 23h)", fontweight='bold')
    ax.set_ylabel("TTFB (ms)", fontweight='bold')
    ax.set_title("Variabilité horaire du temps d'accès sur Quantic (7 jours)", fontweight='bold')
    ax.set_xticks(range(0, 24, 2))
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper left')

    plt.tight_layout()
    save_figure(fig, "fig2_quantic_hourly_profile")
    plt.close()


def plot_quantic_weekday_vs_weekend(df):
    """FIGURE 3 : Stabilité et outliers Quantic (Semaine vs Week-end) avec échelle Log."""
    quantic_df = df[df['network'] == 'quantic'].copy()
    if quantic_df.empty:
        return

    quantic_df['period'] = quantic_df['dayofweek'].apply(
        lambda x: 'Week-end' if x >= 5 else 'Semaine (Lundi-Vendredi)'
    )

    fig, ax = plt.subplots(figsize=(6, 3.8))
    
    periods = ['Semaine (Lundi-Vendredi)', 'Week-end']
    data = [quantic_df[quantic_df['period'] == p]['ttfb_ms'].dropna().values for p in periods]

    bplot = ax.boxplot(
        data, 
        patch_artist=True, 
        tick_labels=periods,
        flierprops=dict(marker='o', markersize=3, alpha=0.3, markerfacecolor='red', markeredgecolor='none')
    )

    for patch in bplot['boxes']:
        patch.set_facecolor(NET_COLORS['quantic'])
        patch.set_alpha(0.6)

    # 1. Utilisation de l'échelle logarithmique pour révéler les boîtes écrasées
    ax.set_yscale('log')
    
    # 2. Formater l'axe Y pour afficher des millisecondes lisibles
    from matplotlib.ticker import FormatStrFormatter
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

    ax.set_ylabel("TTFB (ms) - Échelle Logarithmique", fontweight='bold')
    ax.set_title("Dispersion du TTFB : Semaine vs Week-end (Quantic)", fontweight='bold')
    ax.grid(True, which="both", linestyle='--', alpha=0.5, axis='y')

    plt.tight_layout()
    save_figure(fig, "fig3_quantic_weekday_vs_weekend")
    plt.close()


def plot_cross_network_breakdown(df):
    """FIGURE 4 : Décomposition comparative des phases applicatives (Toutes réseaux)."""
    metrics = ['dns_time_ms', 'tcp_connect_ms', 'tls_handshake_ms', 'download_time_ms']
    labels_map = {
        'dns_time_ms': 'Résolution DNS',
        'tcp_connect_ms': 'Handshake TCP (RTT)',
        'tls_handshake_ms': 'Handshake TLS',
        'download_time_ms': 'Téléchargement HTTP'
    }

    avg_df = df.groupby('network')[metrics].median()
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

    ax.set_ylabel("Temps médian (ms)", fontweight='bold')
    ax.set_xlabel("Réseau d'accès", fontweight='bold')
    ax.set_title("Ordre de grandeur comparatif des phases applicatives", fontweight='bold')
    ax.legend(title="Phases", bbox_to_anchor=(1.02, 1), loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    plt.xticks(rotation=0)

    plt.tight_layout()
    save_figure(fig, "fig4_cross_network_breakdown")
    plt.close()

# =====================================================================
# AGREGAR AL FINAL DE TU generate_figures.py ACTUAL
# =====================================================================

CSV_CDN_PATH = os.path.join(BASE_DIR, "data", "raw", "cdn_measures.csv")

def plot_cdn_throughput_comparison():
    """Génère la comparaison du débit utile (Mbps) à partir de cdn_measures.csv."""
    if not os.path.exists(CSV_CDN_PATH):
        print("[-] Fichier 'cdn_measures.csv' non trouvé (pas encore de mesures CDN).")
        return

    df_cdn = pd.read_csv(CSV_CDN_PATH)
    if df_cdn.empty or 'throughput_mbps' not in df_cdn.columns:
        return

    fig, ax = plt.subplots(figsize=(6, 3.5))
    
    # Médiane du débit utile par réseau
    median_tp = df_cdn.groupby('network')['throughput_mbps'].median()

    median_tp.plot(
        kind='bar', 
        ax=ax, 
        color=[NET_COLORS.get(net, '#1f77b4') for net in median_tp.index],
        edgecolor='black', 
        alpha=0.85
    )

    # Ligne de référence : Seuil Spotify Hi-Fi (320 kbps = 0.32 Mbps)
    ax.axhline(y=0.32, color='r', linestyle='--', label='Seuil Spotify 320 kbps')
    
    ax.set_ylabel("Débit utile médian (Mbit/s)", fontweight='bold')
    ax.set_xlabel("Réseau d'accès", fontweight='bold')
    ax.set_title("Capacité de livraison du flux audio (CDN Spotify)", fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    plt.xticks(rotation=0)

    plt.tight_layout()
    save_figure(fig, "fig4_throughput_per_network")
    plt.close()
    
def main():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    setup_matplotlib_style()

    df = load_data()
    if df is None:
        return

    print(f"[*] Traitement de {len(df)} mesures brutes...")
    plot_quantic_hourly_profile(df)
    plot_quantic_weekday_vs_weekend(df)
    plot_cross_network_breakdown(df)
    print("[✔] Figures générées avec succès dans 'results/figures/'.")
    plot_cdn_throughput_comparison()

if __name__ == "__main__":
    main()