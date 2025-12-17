import sys
import subprocess
import os

"""
Hauptskript: Filtert Unfalldaten für Leipzig und erstellt Visualisierungen!
"""

def install_required_packages():
    """
    Installiert automatisch benötigte Python-Pakete, falls nicht vorhanden.
    """
    required_packages = ['pandas', 'geopandas']
    """
    Der print-Block dient nur der besseren Darstellung im Terminal!
    """
    print("=" * 60)
    print("PRÜFE BENÖTIGTE PAKETE")
    print("=" * 60)

    for package in required_packages:
        """
        Wenn die Pakete vorhanden und bereits installiert sind wird lediglich 
        "{Paketname} bereits installiert" ausgegeben, andernfalls installiert 
        PyCharm automatisch das fehlende Paket.
        """
        try:
            __import__(package)
            print(f"✓ {package} bereits installiert")
        except ImportError:
            print(f"⊘ {package} nicht gefunden - installiere...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} erfolgreich installiert")

    print()


# Pakete installieren BEVOR andere Dateien importiert werden.
install_required_packages()

"""
Hier werden jetzt die vorher definierten Module importiert. 
Sie werden abgekürzt "as XX", bei der weiteren Nutzung 
immer nur die Kürzel nutzen, etwa "dp.XXXXX"!
"""
import data_processing as dp
import export_handlers as exp
import qgis_integration as qgis


def setup_directories(data_dir):
    """Erstellt benötigte Output-Verzeichnisse falls nicht vorhanden."""
    dirs = [
        f"{data_dir}/processed/csv",
        f"{data_dir}/processed/geojson",
        f"{data_dir}/temp"
    ]

    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

    print("✓ Verzeichnisstruktur geprüft/erstellt\n")


# Hier folgte jetzt die Hauptfunktion, die den gesamten Workflow koordinieren soll.
def main():
    """Hauptfunktion: Koordiniert den gesamten Workflow."""

    # Konfiguration
    years = range(2016, 2025)
    data_dir = "../data"
    raw_dir = f"{data_dir}/raw"
    processed_dir = f"{data_dir}/processed"
    bezirke_file = f"{raw_dir}/Stadtbezirke_Leipzig_UTM33N.json"

    print("=" * 60)
    print("UNFALLDATEN-ANALYSE LEIPZIG")
    print("=" * 60)

    # Verzeichnisse erstellen
    setup_directories(data_dir)

    # Schritt 1: Bezirksgrenzen einmalig laden
    print("[1/4] Lade Leipziger Bezirksgrenzen...")
    gdf_leipzig = dp.load_bezirke(bezirke_file)
    print(f"✓ Bezirke geladen (CRS: {gdf_leipzig.crs})\n")

    # Schritt 2: Alle Jahre verarbeiten
    print("[2/4] Verarbeite Unfalldaten...")
    all_results = []

    for year in years:
        result = dp.process_year(year, raw_dir, gdf_leipzig)  # raw_dir!
        if result:
            all_results.append(result)
            print(f"  ✓ Jahr {year}: {result['count']} Unfälle in Leipzig")

    # Schritt 3: Daten exportieren
    print(f"\n[3/4] Exportiere Daten...")
    created_files = exp.export_all(all_results, processed_dir)  # processed_dir!
    print(f"✓ {len(created_files['csv_files'])} CSV-Dateien erstellt")
    print(f"✓ {len(created_files['geojson_files'])} GeoJSON-Dateien erstellt")
    print(f"✓ Gesamtdatei: {os.path.basename(created_files['combined_csv'])}")

    # Schritt 4: QGIS-Visualisierung
    print(f"\n[4/4] Öffne QGIS...")
    qgis.visualize_in_qgis(created_files['geojson_files'])

    print("\n" + "=" * 60)
    print("✓ WORKFLOW ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    main()
