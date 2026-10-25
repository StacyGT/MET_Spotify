import os
import sys

# Cible de l'étude de métrologie
TARGET_HOST = "open.spotify.com"
TARGET_URL = f"https://{TARGET_HOST}"

# Arborescence des dossiers
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
ROUTES_DIR = os.path.join(DATA_RAW_DIR, "routes")
CSV_RAW_PATH = os.path.join(DATA_RAW_DIR, "raw_measures.csv")

# Paramètres de la campagne
DEFAULT_PROBE_COUNT = 30     # Nombre de mesures HTTPS par session
INTERVAL_BETWEEN_PROBES = 5 # Pause en secondes entre deux requêtes curl

# Gestion cross-platform du dev/null pour cURL
NULL_DEVICE = "NUL" if sys.platform.startswith("win") else "/dev/null"