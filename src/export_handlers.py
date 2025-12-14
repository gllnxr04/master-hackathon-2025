import os  # ← Das fehlt!
import pandas as pd


def export_single_csv(gdf, year, output_dir):
    """Exportiert gefilterte Daten als CSV für ein Jahr."""
    df_for_csv = gdf.drop(columns=['geometry'])
    csv_path = f"{output_dir}/csv/Unfallorte{year}_Leipzig.csv"
    df_for_csv.to_csv(csv_path, index=False, encoding='utf-8')
    return csv_path

def export_single_geojson(gdf, year, output_dir):
    """Exportiert gefilterte Daten als GeoJSON für ein Jahr."""
    geojson_path = f"{output_dir}/geojson/Unfallorte{year}_Leipzig.geojson"
    gdf.to_file(geojson_path, driver="GeoJSON")

    return {
        'path': os.path.abspath(geojson_path),
        'year': year,
        'count': len(gdf)
    }

def export_combined_csv(all_results, output_dir):
    """Kombiniert alle Jahre in eine Gesamt-CSV mit durchgehender ID."""
    all_dfs = [result['gdf_filtered'].drop(columns=['geometry'])
               for result in all_results]

    df_combined = pd.concat(all_dfs, ignore_index=True)
    df_combined.insert(0, 'UNFALL_ID', range(1, len(df_combined) + 1))

    combined_path = f"{output_dir}/csv/Unfallorte_Leipzig_2016-2024_GESAMT.csv"
    df_combined.to_csv(combined_path, index=False, encoding='utf-8')

    return combined_path


def export_all(all_results, output_dir):
    """Exportiert alle Daten: einzelne CSVs, GeoJSONs und Gesamtdatei."""
    csv_files = []
    geojson_files = []

    # Einzelne Jahre exportieren
    for result in all_results:
        # CSV
        csv_path = export_single_csv(
            result['gdf_filtered'],
            result['year'],
            output_dir
        )
        csv_files.append(csv_path)

        # GeoJSON
        geojson_info = export_single_geojson(
            result['gdf_filtered'],
            result['year'],
            output_dir
        )
        geojson_files.append(geojson_info)

    # Gesamtdatei
    combined_csv = export_combined_csv(all_results, output_dir)

    return {
        'csv_files': csv_files,
        'geojson_files': geojson_files,
        'combined_csv': combined_csv
    }
