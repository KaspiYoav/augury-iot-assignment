"""Central configuration: all constants and domain rules live here."""

# ---------- Hardware types ----------
NODE_TYPES = ("AHN2", "CASSIA", "MOXA")
EP_TYPES = ("EP1", "EP2", "CANARY_A")

# ---------- API hosts (per Node hardware type) ----------
API_HOSTS = {
    "AHN2": "buildroot_api.azure",
    "CASSIA": "buildroot_api.azure",
    "MOXA": "moxa_api.azure",
}

# ---------- EP battery thresholds in mA (do not DFU below these) ----------
BATTERY_THRESHOLDS_MA = {
    "EP1": 2500,
    "EP2": 2500,
    "CANARY_A": 3600,
}

# ---------- OTA poll / retry model ----------
OTA_MAX_RETRIES = 3
OTA_RETRY_INTERVAL_SEC = 1.0

# ---------- Naming formats ----------
OTA_CHANNEL_PREFIX = "OTA_"
ARTIFACT_EXTENSION = ".swu"

# ---------- HTTP-like return codes ----------
HTTP_OK = 200
HTTP_BAD_REQUEST = 400