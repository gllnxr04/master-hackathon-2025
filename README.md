Hellooo Team 🤩,

hier ist unser Unfalldaten-Analyse-Projekt für den Hackathon. Der Code filtert automatisch alle Unfälle in Leipzig (2016-2024) und visualisiert sie in QGIS.

# Unfalldaten-Analyse für die Stadt Leipzig in den Jahren 2016 bis 2024

## 📋 Voraussetzungen

- Python 3.9+
- QGIS LTR (für Visualisierung)

## Was macht der Code?

Der Workflow läuft in 4 Schritten ab (siehe `main.py`):

### 1. Datenverarbeitung (`data_processing.py`)
- Lädt die Leipziger Bezirksgrenzen (GeoJSON)
- Liest alle CSV-Dateien der Jahre 2016-2024 ein
- Korrigiert Dezimaltrennzeichen in Koordinaten
- Filtert nur Unfälle, die **INNERHALB** von Leipzig liegen (Spatial Join)

### 2. Export (`export_handlers.py`)
- Speichert gefilterte Daten als CSV (pro Jahr)
- Speichert gefilterte Daten als GeoJSON (pro Jahr)
- Erstellt eine Gesamtdatei mit **ALLEN** Jahren und durchgehender `UNFALL_ID`

### 3. QGIS-Visualisierung (`qgis_integration.py`)
- Öffnet automatisch QGIS
- Lädt OpenStreetMap als Basiskarte (unterste Ebene)
- Lädt alle Unfall-Layer darüber (ein Layer pro Jahr)
- Zoomt automatisch auf Leipzig

### 4. Orchestrierung (`main.py`)
- Steuert den gesamten Ablauf
- Installiert automatisch fehlende Pakete
- Erstellt benötigte Ordnerstruktur

---

## Vor dem ersten Start

### 1. Virtual Environment erstellen

Terminal öffnen, zum Projektordner navigieren:

**macOS/Linux:**
python3 -m venv .venv source .venv/bin/activate

**Windows:**
python -m venv .venv .venv\Scripts\activate

### 2. QGIS-Pfad prüfen

Öffne: `src/qgis_integration.py`  
Zeile 6: `QGIS_PATH` anpassen falls QGIS woanders installiert ist

**Standardpfade:**
- macOS: `/Applications/QGIS-LTR.app`
- Windows: `C:/Program Files/QGIS 3.x`
- Linux: `/usr/bin/qgis`

### 3. Daten prüfen

Stelle sicher, dass in `data/raw/` folgende Dateien liegen:
- `Stadtbezirke_Leipzig_UTM33N.json`
- `Unfallorte2016_LinRef.csv` bis `Unfallorte2024_LinRef.csv`

---

## Ausführung
In der `main.py`-Datei entweder "Play" drücken, 
oder im Terminal folgenden Befehl eingeben:

cd src python main.py

Das war's! Der Code läuft automatisch durch und öffnet am Ende QGIS.

---

## Output

Nach dem Durchlauf findet ihr:

### `data/processed/csv/`
- `Unfallorte2016_Leipzig.csv` (nur Leipzig-Unfälle)
- `Unfallorte2017_Leipzig.csv`
- ... (bis 2024)
- `Unfallorte_Leipzig_2016-2024_GESAMT.csv` (ALLE Jahre kombiniert mit `UNFALL_ID`)

### `data/processed/geojson/`
- `Unfallorte2016_Leipzig.geojson`
- ... (für QGIS-Visualisierung)

---

## Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'pandas'`
**Lösung:** Virtual Environment aktivieren + `pip install -r requirements.txt`

### Problem: QGIS öffnet nicht
**Lösung:** `QGIS_PATH` in `src/qgis_integration.py` anpassen

### Problem: "Datei nicht gefunden"
**Lösung:** Prüfe ob alle CSV-Dateien in `data/raw/` liegen

---

Bei Fragen: einfach melden!

Viel Erfolg! 🚀