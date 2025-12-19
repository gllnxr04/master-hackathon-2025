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
        return "/Applications/QGIS-LTR.app/Contents/MacOS/QGIS-LTR"
    elif system == "Windows":
        return "C:/Program Files/QGIS 3.x"
    elif system == "Linux":
        return "/usr/bin/qgis"
    else:
        raise OSError(f"Betriebssystem {system} nicht unterstützt")


QGIS_PATH = get_qgis_path()


def create_qgis_script(geojson_files):
    """
    Erstellt ein QGIS-Python-Skript mit Heatmap-Darstellung.
    """
    script_heatmap = """from qgis.core import (QgsRasterLayer, QgsVectorLayer, QgsProject, 
                          QgsHeatmapRenderer, QgsGradientColorRamp, QgsUnitTypes)
from qgis.utils import iface
from PyQt5.QtGui import QColor

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

    for file_info in geojson_files:
        safe_path = file_info['path'].replace('\\', '\\\\')
        script_heatmap += f'    {{"path": "{safe_path}", "year": {file_info["year"]}, "count": {file_info["count"]}}},\n'

    script_heatmap += """]

# 3. Alle Layer als Heatmap laden
for item in layer_list:
    layer_name = "Heatmap Unfaelle " + str(item["year"])
    vector_layer = QgsVectorLayer(item["path"], layer_name, "ogr")

    if vector_layer.isValid():
        # Heatmap-Renderer erstellen
        heatmap_renderer = QgsHeatmapRenderer()
        
        # Radius setzen
        heatmap_renderer.setRadius(50)
        heatmap_renderer.setRadiusUnit(QgsUnitTypes.RenderPixels)
        
        # Farbverlauf: Transparent → Rot
        color_ramp = QgsGradientColorRamp()
        color_ramp.setColor1(QColor(255, 0, 0, 0))      # Rot transparent
        color_ramp.setColor2(QColor(255, 0, 0, 255))    # Rot opak
        heatmap_renderer.setColorRamp(color_ramp)
        
        # Maximumwert automatisch
        heatmap_renderer.setMaximumValue(0)
        
        # Render-Qualität
        heatmap_renderer.setRenderQuality(1)
        
        vector_layer.setRenderer(heatmap_renderer)
        QgsProject.instance().addMapLayer(vector_layer)
        print("✓ Heatmap geladen: " + layer_name)
    else:
        print("✗ Layer-Fehler: " + layer_name)


# 4. Auf Leipzig zoomen
if len(layer_list) > 0:
    first_layer = QgsVectorLayer(layer_list[0]["path"], "temp", "ogr")
    if first_layer.isValid():
        iface.setActiveLayer(first_layer)
        iface.zoomToActiveLayer()
        print("✓ Gezoomt auf Leipzig")

print("\\n✓ Alle Heatmap-Layer geladen!")
"""
    return script_heatmap


def visualize_in_qgis_heatmap(geojson_files):
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
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", "-a", "QGIS-LTR", "--args", "--code", temp_script_path])
        else:
            subprocess.run([QGIS_PATH, "--code", temp_script_path])
        print(f"✓ QGIS geöffnet mit {len(geojson_files)} Layern")
    except Exception as e:
        print(f"✗ Fehler beim Öffnen von QGIS: {e}")
