import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def lade_unfaelle():
    # Wo liegen Dateien? (→ eine Ebene über src)
    BASE_DIR = Path(__file__).resolve().parent.parent
    # Datenordner
    DATA_DIR = BASE_DIR / "data"

    # Zeitraum definieren (Achtung: Angabe bis 2025 nötig, weil 2025 ausgeschlossen wird!)
    years = range(2016, 2025)

    # Liste für Data Frames
    dfs = []

    for year in years:
        filepath = DATA_DIR / f"Unfallorte{year}_LinRef.csv"

    # Separator wählen
        sep = ";" if year != 2024 else ","

        df_year = pd.read_csv(filepath, sep=sep, low_memory=False)
        dfs.append(df_year)

    # Alle Jahre zu einem Data Frame zusammenführen (.concat() hängt alle Tabellen untereinander)
    df_all = pd.concat(dfs, ignore_index=True)
    return df_all
    # → df_all enthält jetzt alle Unfälle von 2016-2024!

def plot_unfalltrend(df_all):
    # Jetzt können wir die Unfälle pro Jahr zählen
    # → jede Zeile = ein Unfall
    # → value_counts() zählt pro Jahr
    # → sort_index() sortiert chronologisch
    unfaelle_pro_jahr = df_all["UJAHR"].value_counts().sort_index()

    #Unfalltrend plotten mit .plot(): Liniendiagramm der Unfallentwicklung pro Jahr
    unfaelle_pro_jahr.plot(
        kind="line",
        marker="o",
        title="Unfallentwicklung in Leipzig (2016-2024)",
        xlabel="Jahr",
        ylabel="Anzahl der Unfälle",
        grid=True
    )

    plt.show()

# Beide Funktionen aufrufen: Daten laden und Plot erzeugen
df_all = lade_unfaelle()
plot_unfalltrend(df_all)