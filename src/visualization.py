import tempfile
from pathlib import (Path)
import geopandas as gpd
import os
import platform
import subprocess
from typing import List, Dict

def get_qgis_path() -> str:
    """
        Ermittelt den QGIS-Startpfad je nach Betriebssystem.

        Rückgabe:
            Pfad zur QGIS-Executable bzw. App.
            - macOS:  /Applications/QGIS-LTR.app
            - Windows: C:/Program Files/QGIS 3.x/bin/qgis.exe (ggf. anpassen)
            - Linux:  /usr/bin/qgis
        """
    system = platform.system()

    if system == "Darwin":  # macOS
        return "/Applications/QGIS-LTR.app"
    elif system == "Windows":
        # Pfad ggf. an deine Installation anpassen
        return r"C:\Program Files\QGIS 3.x\bin\qgis.exe"
    elif system == "Linux":
        return "/usr/bin/qgis"
    else:
        raise OSError(f"Betriebssystem {system} nicht unterstützt")

QGIS_PATH = get_qgis_path()

def create_qgis_script(geojson_files: List[Dict]) -> str:
    """
     Baut ein QGIS-Python-Skript als String, das:
      - OpenStreetMap als Basiskarte lädt
      - alle Unfall-Layer (GeoJSON) lädt
      - auf den ersten Layer (Leipzig) zoomt

    Erwartete Struktur eines Eintrags in geojson_files:
        {
            "path": "/pfad/zu/Unfallorte2016_Leipzig.geojson",
            "year": 2016,
            "count": 1234
        }
    """
    # Kopf des Skripts: Imports + OSM-Basiskarte
    script = """from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsProject
from qgis.utils import iface

# 1. OpenStreetMap-Basiskarte laden
osm_url = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0"
osm_layer = QgsRasterLayer(osm_url, "OpenStreetMap", "wms")

if osm_layer.isValid():
    QgsProject.instance().addMapLayer(osm_layer)
    print("✓ OpenStreetMap geladen")
else:
    print("✗ OpenStreetMap-Fehler")

# 2. Layer-Liste (GeoJSON-Dateien)
layer_list = [
"""

    # Layer-Infos in die Python-Liste layer_list schreiben
    for file_info in geojson_files:
        # Pfad für Python-String escapen (insbesondere für Windows-Pfade)
        safe_path = file_info["path"].replace("\\", "\\\\")
        year = file_info.get("year", "None")
        count = file_info.get("count", "None")

        script += f'    {{"path": "{safe_path}", "year": {year}, "count": {count}}},\n'

    script += """]

# 3. Alle GeoJSON-Layer laden
for item in layer_list:
    layer_name = f"Unfälle {item['year']} ({item['count']})"
    vector_layer = QgsVectorLayer(item["path"], layer_name, "ogr")

    if vector_layer.isValid():
        QgsProject.instance().addMapLayer(vector_layer)
        print("✓ Layer geladen:", layer_name)
    else:
        print("✗ Layer-Fehler:", layer_name)

# 4. Auf Leipzig zoomen (erster Layer)
if len(layer_list) > 0:
    first_layer = QgsVectorLayer(layer_list[0]["path"], "temp", "ogr")
    if first_layer.isValid():
        iface.setActiveLayer(first_layer)
        iface.zoomToActiveLayer()
        print("✓ Gezoomt auf Leipzig")

print("\\n✓ Alle Layer geladen!")
"""

    return script


def _build_qgis_command(temp_script_path: str) -> List[str]:
    """
    Baut den passenden subprocess-Befehl für das aktuelle Betriebssystem,
    um QGIS mit einem Python-Skript zu starten.
    """
    system = platform.system()

    if system == "Darwin":  # macOS .app-Struktur
        qgis_executable = os.path.join(QGIS_PATH, "Contents", "MacOS", "QGIS")
        return [qgis_executable, "--code", temp_script_path]

    elif system == "Windows":
        # QGIS_PATH sollte hier bereits der Pfad zur qgis.exe sein
        return [QGIS_PATH, "--code", temp_script_path]

    elif system == "Linux":
        # QGIS_PATH ist typischerweise /usr/bin/qgis
        return [QGIS_PATH, "--code", temp_script_path]

    else:
        raise OSError(f"Betriebssystem {system} nicht unterstützt")


def visualize_in_qgis(geojson_files: List[Dict]) -> None:
    """
    Öffnet QGIS mit:
      - OpenStreetMap-Basiskarte
      - allen übergebenen GeoJSON-Layern

    Parameter:
        geojson_files: Liste von Dicts mit mindestens:
            - "path": Pfad zur GeoJSON-Datei
            - "year": Jahr (int)
            - "count": Anzahl Unfälle (int)
    """
    if not geojson_files:
        print("✗ Keine GeoJSON-Dateien übergeben – breche ab.")
        return

    # QGIS-Python-Skript erzeugen
    qgis_script = create_qgis_script(geojson_files)

    # Temporäre Skript-Datei schreiben
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(qgis_script)
        temp_script_path = tmp.name

    # QGIS-Startbefehl bauen und ausführen
    cmd = _build_qgis_command(temp_script_path)

    try:
        subprocess.run(cmd, check=False)
        print(f"✓ QGIS geöffnet mit {len(geojson_files)} Layern")
    except Exception as e:
        print(f"✗ Fehler beim Öffnen von QGIS: {e}")