"""
Modul für das Einlesen und Filtern von Unfalldaten.
"""
import csv
import pandas as pd
import geopandas as gpd
import os


def read_csv_auto(path):
    """
    Liest CSV-Datei mit automatischer Trennzeichen-Erkennung.
    Fallback auf Semikolon falls Sniffer fehlschlägt.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            sample = f.read(2048)
            f.seek(0)

            # Versuche automatische Erkennung
            try:
                dialect = csv.Sniffer().sniff(sample)
                delimiter = dialect.delimiter
            except csv.Error:
                # Fallback: Prüfe ob Semikolon oder Komma häufiger vorkommt
                semicolon_count = sample.count(';')
                comma_count = sample.count(',')
                delimiter = ';' if semicolon_count > comma_count else ','
                print(f"    → Automatische Erkennung fehlgeschlagen, verwende '{delimiter}'")

            f.seek(0)
            return pd.read_csv(f, delimiter=delimiter, dtype=str, low_memory=False)

    except Exception as e:
        print(f"    ✗ Fehler beim Einlesen: {e}")
        # Letzter Fallback: Versuche mit Semikolon
        return pd.read_csv(path, delimiter=';', dtype=str, low_memory=False, encoding='utf-8')


def load_bezirke(bezirke_path):
    """
    Lädt die Leipziger Bezirksgrenzen (nur einmal).

    Args:
        bezirke_path (str): Pfad zur GeoJSON-Datei der Bezirke

    Returns:
        gpd.GeoDataFrame: Bezirksgrenzen
    """
    return gpd.read_file(bezirke_path)


def clean_coordinates(df):
    """
    Korrigiert Dezimaltrennzeichen in Koordinaten.

    Args:
        df (pd.DataFrame): DataFrame mit Koordinaten

    Returns:
        pd.DataFrame: Bereinigter DataFrame
    """
    df["XGCSWGS84"] = df["XGCSWGS84"].str.replace(",", ".").astype(float)
    df["YGCSWGS84"] = df["YGCSWGS84"].str.replace(",", ".").astype(float)
    return df


def create_geodataframe(df):
    """
    Erstellt GeoDataFrame aus Koordinaten.

    Args:
        df (pd.DataFrame): DataFrame mit XGCSWGS84 und YGCSWGS84 Spalten

    Returns:
        gpd.GeoDataFrame: GeoDataFrame mit Punktgeometrien
    """
    return gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["XGCSWGS84"], df["YGCSWGS84"]),
        crs="EPSG:4326"
    )


def filter_by_boundaries(gdf_points, gdf_boundaries):
    """
    Filtert Punkte nach Bezirksgrenzen (Spatial Join).

    Args:
        gdf_points (gpd.GeoDataFrame): Unfall-Punkte
        gdf_boundaries (gpd.GeoDataFrame): Bezirksgrenzen

    Returns:
        gpd.GeoDataFrame: Gefilterte Punkte innerhalb der Grenzen
    """
    # CRS matchen
    gdf_points_matched = gdf_points.to_crs(gdf_boundaries.crs)

    # Spatial Join: nur Punkte innerhalb der Bezirksgrenzen
    return gpd.sjoin(
        gdf_points_matched,
        gdf_boundaries,
        how="inner",
        predicate="within"
    )


def process_year(year, data_dir, gdf_leipzig):
    """
    Verarbeitet ein einzelnes Jahr: CSV einlesen, filtern.

    Args:
        year (int): Jahr
        data_dir (str): Pfad zum Datenverzeichnis
        gdf_leipzig (gpd.GeoDataFrame): Leipziger Bezirksgrenzen

    Returns:
        dict: Verarbeitete Daten {'year', 'gdf_filtered', 'count'} oder None
    """
    csv_path = f"{data_dir}/Unfallorte{year}_LinRef.csv"

    # Prüfen ob Datei existiert
    if not os.path.exists(csv_path):
        print(f"  ⊘ Jahr {year}: Datei nicht gefunden")
        return None

    # CSV einlesen und verarbeiten
    df = read_csv_auto(csv_path)
    df = clean_coordinates(df)
    gdf_points = create_geodataframe(df)
    gdf_filtered = filter_by_boundaries(gdf_points, gdf_leipzig)

    return {
        'year': year,
        'gdf_filtered': gdf_filtered,
        'count': len(gdf_filtered)
    }
