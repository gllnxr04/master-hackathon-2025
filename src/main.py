import sys
import subprocess
import os
from visualization import visualize_in_qgis
from heatmap_qgis_integration import visualize_in_qgis_heatmap
from UnfaelleJahresvergleich import lade_unfaelle
from UnfaelleJahresvergleich import plot_unfalltrend
from UnfaelleStadtbezirkeNachJahreszeiten import user_input_choice
from UnfaelleStadtbezirkeNachJahreszeiten import user_input_choice_2
"""f
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

def input_user():
    print("\nWelche Auswertung möchtest du starten?")
    print("  [1] Darstellung in QGIS")
    print("  [2] Visualisierung als Plot (Jahresvergleich)")
    print("  [3] Weitere Analyse (Stadtbezirke nach Jahreszeiten)")
    print("  [q] Beenden")

    return input("Bitte Auswahl eingeben (1/2/3/q): ").strip().lower()

def input_user_for_1():
    print("\nWelche Auswertung möchtest du in QGIS haben?")
    print("  [1] Darstellung in QGIS als Punkte")
    print("  [2] Darstellung in QGIS als Heatmap")

    return input("Bitte Auswahl eingeben (1/2): ").strip().lower()

def setup_directories(data_dir: str) -> None:
    """Erstellt benötigte Output-Verzeichnisse falls nicht vorhanden."""
    dirs = [
        f"{data_dir}/processed/csv",
        f"{data_dir}/processed/geojson",
        f"{data_dir}/temp"
    ]
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
    print("✓ Verzeichnisstruktur geprüft/erstellt\n")

def outputs_already_exist(processed_dir:str, years) -> bool:
    """
    Prüft, ob für alle Jahre bereits CSV- und GeoJSON-Dateien existieren
    UND eine kombinierte CSV vorhanden ist.
    Wenn ja, kann die Verarbeitung übersprungen werden.
    """
    csv_dir = os.path.join(processed_dir, "csv")
    geo_dir = os.path.join(processed_dir, "geojson")

    # Wenn es die Ordner gar nicht gibt: sicher neu rechnen
    if not (os.path.isdir(csv_dir) and os.path.isdir(geo_dir)):
        return False

    for year in years:
        csv_file = os.path.join(csv_dir, f"Unfallorte{year}_Leipzig.csv")
        geo_file = os.path.join(geo_dir, f"Unfallorte{year}_Leipzig.geojson")
        if not (os.path.isfile(csv_file) and os.path.isfile(geo_file)):
            return False

    # Optional: kombinierte CSV prüfen
    combined_csv = os.path.join(csv_dir, "Unfallorte_Leipzig_2016-2024_GESAMT.csv")
    if not os.path.isfile(combined_csv):
        return False

    return True

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


    # # NEU: Prüfen, ob bereits alles vorliegt
    # if outputs_already_exist(processed_dir, years):
    #     print("✔ Verarbeitete Daten bereits vorhanden – überspringe Verarbeitung.\n")
    #     # Wenn du später hier nur noch Visualisierung starten willst, kannst du das tun:
    #     # qgis.visualize_in_qgis( ... )
    #     return

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

    # Schritt 4: Input User
    print("=" * 60)
    print("WILLKOMMEN! DEINE EINGABE IST NUN ERFORDERLICH")
    print("=" * 60)
    input = input_user()

    # Schritt 5 Input prüfen
    if input == "1":
        print("Success 1")
        input_for_1 = input_user_for_1()
        if input_for_1 == "1":
            visualize_in_qgis(created_files["geojson_files"])
        elif input_for_1 == "2":
            visualize_in_qgis_heatmap(created_files["geojson_files"])

    elif input == "2":
        print("Success 2")
        plot_unfalltrend(lade_unfaelle()) #WAS BENÖTIGT DIE FUNKTION???
    elif input == "3":
        print("Success 3")
        user_input_choice()
        user_input_choice_2()

    else:
        print("\n\nFehlerhafte Eingabe. Bitte gib eine der Zahlen an, die Dir vorgeschlagen werden und drücke dann auf Enter.")

    # # Schritt X: QGIS-Visualisierung
    # print(f"\n[4/4] Öffne QGIS...")
    # qgis.visualize_in_qgis(created_files['geojson_files'])
    #
    # print("\n" + "=" * 60)
    # print("✓ WORKFLOW ABGESCHLOSSEN")
    # print("=" * 60)


if __name__ == "__main__":
    main()