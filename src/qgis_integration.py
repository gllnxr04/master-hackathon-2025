"""
Modul für die QGIS-Integration und Visualisierung.
"""
import subprocess
import tempfile

# QGIS-Pfad für macOS (LTR Version)
import sys
import platform


# QGIS-Pfad automatisch erkennen
def get_qgis_path():
    """Ermittelt QGIS-Pfad je nach Betriebssystem."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return "/Applications/QGIS-LTR.app"
    elif system == "Windows":
        return "C:/Program Files/QGIS 3.x"
    elif system == "Linux":
        return "/usr/bin/qgis"
    else:
        raise OSError(f"Betriebssystem {system} nicht unterstützt")


QGIS_PATH = get_qgis_path()


def create_qgis_script(geojson_files):
    """
    Erstellt ein QGIS-Python-Skript zum Laden der Layer.

    Args:
        geojson_files (list): Liste mit GeoJSON-Datei-Infos

    Returns:
        str: QGIS-Python-Skript als String
    """
    script = """from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsProject
from qgis.utils import iface

# 1. OpenStreetMap laden
osm_url = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0"
osm_layer = QgsRasterLayer(osm_url, "OpenStreetMap", "wms")

if osm_layer.isValid():
    QgsProject.instance().addMapLayer(osm_layer)
    print("✓ OpenStreetMap geladen")
else:
    print("✗ OpenStreetMap-Fehler")

# 2. Layer-Daten
layer_list = [
"""

    # Layer-Infos ins Skript schreiben
    for file_info in geojson_files:
        safe_path = file_info['path'].replace('\\', '\\\\')
        script += f'    {{"path": "{safe_path}", "year": {file_info["year"]}, "count": {file_info["count"]}}},\n'

    script += """]

# 3. Alle Layer laden
for item in layer_list:
    layer_name = "Unfaelle " + str(item["year"]) + " (" + str(item["count"]) + ")"
    vector_layer = QgsVectorLayer(item["path"], layer_name, "ogr")

    if vector_layer.isValid():
        QgsProject.instance().addMapLayer(vector_layer)
        print("✓ Layer geladen: " + layer_name)
    else:
        print("✗ Layer-Fehler: " + layer_name)

# 4. Auf Leipzig zoomen
if len(layer_list) > 0:
    first_layer = QgsVectorLayer(layer_list[0]["path"], "temp", "ogr")
    if first_layer.isValid():
        iface.setActiveLayer(first_layer)
        iface.zoomToActiveLayer()
        print("✓ Gezoomt auf Leipzig")

print("\\n✓ Alle Layer geladen!")
"""

    return script


def visualize_in_qgis(geojson_files):
    """
    Öffnet QGIS mit allen GeoJSON-Layern und OpenStreetMap-Basiskarte.

    Args:
        geojson_files (list): Liste mit GeoJSON-Datei-Infos
    """
    # QGIS-Skript erstellen
    qgis_script = create_qgis_script(geojson_files)

    # Temporäres Skript speichern
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(qgis_script)
        temp_script_path = f.name

    # QGIS starten
    '''
    🚨| Bei Nutzung von Betriebssystem "Windows" hier abändern zu:
    "    try:
        subprocess.run([
            QGIS_PATH,
            "--code", temp_script_path
        ], check = TRUE)
        print(f"✓ QGIS geöffnet mit {len(geojson_files)} Layern")
    except Exception as e:
        print(f"✗ Fehler beim Öffnen von QGIS: {e}")
    "
    '''
    try:
        subprocess.run([
            f"{QGIS_PATH}/Contents/MacOS/QGIS",
            "--code", temp_script_path
        ])
        print(f"✓ QGIS geöffnet mit {len(geojson_files)} Layern")
    except Exception as e:
        print(f"✗ Fehler beim Öffnen von QGIS: {e}")
