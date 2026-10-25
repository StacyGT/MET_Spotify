
import csv
import re
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

# 1. Paramètres de la mesure
destination = "1.1.1.1"
nombre_paquets = 30
lieu = "Domicile"
acces = "Wi-Fi"

# 2. Informations communes à cette session
id_session = str(uuid.uuid4())[:8]
date_session = datetime.now().isoformat(timespec="seconds")

# 3. Chemin du fichier CSV
dossier_projet = Path(__file__).resolve().parent.parent
dossier_donnees = dossier_projet / "data" / "raw"
dossier_donnees.mkdir(parents=True, exist_ok=True)

fichier_csv = dossier_donnees / "mesures_ping.csv"

colonnes = [
    "id_session",
    "date_session",
    "lieu",
    "acces",
    "destination",
    "numero_paquet",
    "rtt_ms",
    "ttl",
    "recu",
]

# 4. Exécuter le ping
commande = ["ping", "-n", str(nombre_paquets), destination]

resultat = subprocess.run(
    commande,
    capture_output=True,
    errors="replace",
    timeout=90
)

sortie = resultat.stdout

# 5. Lire les réponses et les enregistrer
nouveau_fichier = (
    not fichier_csv.exists() or fichier_csv.stat().st_size == 0
)

recus = 0
temps = []
numero = 0

with open(fichier_csv, "a", newline="", encoding="utf-8") as fichier:
    writer = csv.DictWriter(fichier, fieldnames=colonnes)

    if nouveau_fichier:
        writer.writeheader()

    for ligne in sortie.splitlines():
        if "TTL=" in ligne.upper():
            numero += 1
            recus += 1

            correspondance = re.search(
                r"temps[=<]\s*(\d+)\s*ms",
                ligne,
                re.IGNORECASE
            )
            ttl_match = re.search(
                r"TTL=(\d+)",
                ligne,
                re.IGNORECASE
            )

            rtt = int(correspondance.group(1)) if correspondance else None
            ttl = int(ttl_match.group(1)) if ttl_match else None

            if rtt is not None:
                temps.append(rtt)

            writer.writerow({
                "id_session": id_session,
                "date_session": date_session,
                "lieu": lieu,
                "acces": acces,
                "destination": destination,
                "numero_paquet": numero,
                "rtt_ms": rtt,
                "ttl": ttl,
                "recu": True,
            })

    # Ajouter une ligne pour chaque paquet sans réponse
    while numero < nombre_paquets:
        numero += 1

        writer.writerow({
            "id_session": id_session,
            "date_session": date_session,
            "lieu": lieu,
            "acces": acces,
            "destination": destination,
            "numero_paquet": numero,
            "rtt_ms": None,
            "ttl": None,
            "recu": False,
        })

# 6. Afficher le bilan de la session
print("Identifiant de session :", id_session)
print("Date :", date_session)
print("Lieu :", lieu)
print("Accès :", acces)
print("Paquets envoyés :", nombre_paquets)
print("Réponses reçues :", recus)
print("Perte de paquets :", round(
    100 * (nombre_paquets - recus) / nombre_paquets, 2
), "%")

if temps:
    print("RTT minimum :", min(temps), "ms")
    print("RTT médian :", sorted(temps)[len(temps) // 2], "ms")
    print("RTT moyen :", round(sum(temps) / len(temps), 2), "ms")
    print("RTT maximum :", max(temps), "ms")

print("Résultats enregistrés dans :", fichier_csv)
