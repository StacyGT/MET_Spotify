
import pandas as pd
from pathlib import Path

# Trouver le fichier de mesures
dossier_projet = Path(__file__).resolve().parent.parent
fichier = dossier_projet / "data" / "raw" / "mesures_ping.csv"

donnees = pd.read_csv(fichier)

# Garder uniquement les paquets ayant un RTT mesuré
rtt = donnees["rtt_ms"].dropna()

print("Nombre de paquets envoyés :", len(donnees))
print("Nombre de réponses reçues :", len(rtt))
print("Taux de perte :",
      round(100 * (len(donnees) - len(rtt)) / len(donnees), 2), "%")

print("\nStatistiques du RTT (ms)")
print("Minimum :", rtt.min())
print("Médiane :", rtt.median())
print("Moyenne :", round(rtt.mean(), 2))
print("Maximum :", rtt.max())
print("90e percentile :", rtt.quantile(0.90))


import matplotlib.pyplot as plt

# Numéros des paquets pour lesquels un RTT a été mesuré
numero_paquet = donnees.loc[rtt.index, "numero_paquet"]

plt.figure(figsize=(10, 5))

plt.plot(numero_paquet, rtt, marker="o", label="RTT mesuré")
plt.axhline(
    rtt.median(),
    linestyle="--",
    label=f"Médiane : {rtt.median():.1f} ms"
)

plt.xlabel("Numéro du paquet")
plt.ylabel("RTT (ms)")
plt.title("Évolution du RTT vers 1.1.1.1")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Enregistrer le graphique dans le dossier results/figures
dossier_figures = dossier_projet / "results" / "figures"
dossier_figures.mkdir(parents=True, exist_ok=True)

plt.savefig(dossier_figures / "rtt_ping.png", dpi=150)
plt.show()
