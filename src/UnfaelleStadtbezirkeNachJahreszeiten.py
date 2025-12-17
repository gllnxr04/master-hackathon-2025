import geopandas as gpd
import pandas as pd
from pathlib import Path

# Jetzt können wir auf unseren erzeugten geojson-Dateien aufbauen
# Frage 1: Wie sieht die prozentuale Verteilung der Unfälle in den jeweiligen Stadtbezirken gestaffelt nach Jahreszeiten aus?
# Frage 2: Wie sieht die prozentuale Verteilung der Unfälle in den jeweiligen Stadtbezirken gestaffelt nach Jahreszeiten und Verkehrsmitteln aus?

# ------------------------------------------
# geojson-Dateien laden und zusammenfassen
# -------------------------------------------

# Wo liegen die Dateien? → einen Ordner über "src"
data_dir = Path("../data/processed/geojson")
geojson_files = sorted(data_dir.glob("Unfallorte*.geojson")) # * als Platzhalter, um alle Jahre von 2016-2024 zu erfassen

# Leere Liste anlegen
alle_unfaelle_geojson = []

# Sortierte geojson_files einlesen
for file in geojson_files:
    gdf = gpd.read_file(file)
    # Sicherstellen, dass alle benötigten Spalten existieren ("IstSonstig" gibt es nicht in allen Dateien)
    for spalte in ["IstPKW", "IstRad", "IstFuss", "IstKrad", "IstSonstig"]:
        if spalte not in gdf.columns: # bedeutet z. B. für "IstSonstig" wird 0 eingesetzt, wenn nicht vorhanden in der Datei
            gdf[spalte] = 0

# Benötigte Spalten auswählen
    gdf = gdf[[ "Name", "UMONAT", "UJAHR", "IstPKW", "IstRad", "IstFuss", "IstKrad", "IstSonstig"]]

# Liste befüllen
    alle_unfaelle_geojson.append(gdf)

# Alle Jahre zusammenführen
unfaelle = pd.concat(alle_unfaelle_geojson, ignore_index=True)

# ----------------------------------
# Monate den Jahreszeiten zuordnen
# ----------------------------------

"""Grundannahme: Frühling = März, April, Mai / Sommer = Juni, Juli, August /
Herbst = September, Oktober, November / Winter = Dezember, Januar, Februar"""

def monat_zu_jahreszeit(monat:int) -> str:
    """Ordnet die Monate der jeweiligen Jahreszeit zu."""
    if monat in [3, 4, 5]:
        return "Frühling"
    elif monat in [6, 7, 8]:
        return "Sommer"
    elif monat in [9, 10, 11]:
        return "Herbst"
    else:
        return "Winter"

# Neue Spalte für Jahreszeiten erzeugen
unfaelle["Jahreszeit"] = unfaelle["UMONAT"].astype(int).apply(monat_zu_jahreszeit)

# ------------------------------------------
# Jetzt können wir nach Stadtbezirk auswerten
# ------------------------------------------

def unfaelle_nach_jahreszeit(stadtbezirk: str):
    """Zählt Unfälle pro Jahreszeit für einen Stadtbezirk und berechnet die
    prozentuale Unfallverteilung auf Basis der zurückliegenden Jahre."""

    # DataFrame 'unfaelle' nach dem eingegebenen Stadtbezirk filtern, also z. B. "Nord"
    gefiltert = unfaelle[unfaelle["Name"] == stadtbezirk]

    if gefiltert.empty:
        print(f"Keine Daten für den Stadtbezirk '{stadtbezirk}' gefunden.")
        return None

    # Anzahl der Unfälle pro Jahreszeit zählen
    # DataFrame, das vorher nach dem Stadtbezirk gefiltert wurde, wird jetzt mit .groupby in Gruppen nach Jahreszeit aufgeteilt
    # .size zählt, wie viele Zeilen (also Unfälle) in jeder "Jahreszeit-Gruppe" passiert sind
    # .reindex stellt sicher, dass die Serie immer in der festgelegten Reihenfolge der Jahreszeiten ausgegeben wird; fill_value = 0 (falls eine Jahreszeit nicht vorkommt)
    jahreszeit_counts = (
        gefiltert
        .groupby("Jahreszeit")
        .size()
        .reindex(["Frühling", "Sommer", "Herbst", "Winter"], fill_value=0)
    )

    # jahreszeit_counts enthält für jede Jahreszeit die Anzahl der Unfälle im gewählten Stadtbezirk
    # 'gesamt' erfasst nun die Summe dieser Unfälle
    # Für den Fall, dass es im Stadtbezirk über alle Jahreszeiten hinweg keine Unfälle gab, wird das festgelegte Statement ausgegeben
    gesamt = jahreszeit_counts.sum()
    if gesamt == 0:
        print(f"Keine Unfälle für '{stadtbezirk}' gefunden.")
        return None

    # Relative Verteilung der Unfälle auf die Jahreszeiten
    prozentuale_unfallverteilung = jahreszeit_counts / gesamt * 100
    return prozentuale_unfallverteilung

# Eingabe Stadtbezirk
stadtbezirk_input = str(input("Gib hier den Stadtbezirk ein, für den du die prozentuale Verteilung der Unfälle nach Jahreszeit wissen möchtest.\n"
                          "Diese beruht auf der Basis der Unfalldaten der Jahre 2016-2024.\n"
                          "Du hast die Wahl zwischen Nord, Nordwest, Nordost, Ost, Südost, Süd, Südwest, West, Alt-West und Mitte: "))

# Ausgabe der prozentualen Verteilung der Unfälle nach Jahreszeit in einem bestimmten Stadtbezirk
prozentuale_unfallverteilung = unfaelle_nach_jahreszeit(stadtbezirk_input)

if prozentuale_unfallverteilung is not None:
    print(f"\nDie prozentuale Verteilung der Unfälle im Stadtbezirk '{stadtbezirk_input}': ")
    for saison, prozent in prozentuale_unfallverteilung.items():
        print(f"{saison}: {prozent: .2f}%")
    print()

# ----------------------------------
# Unfallverteilung nach Jahreszeit und Fortbewegungsmittel
# ----------------------------------

def unfaelle_nach_jahreszeit_und_verkehrsmittel(stadtbezirk: str):
    """Berechnet die prozentuale Verteilung der Unfälle nach Fortbewegungsmittel
    und Jahreszeit für einen bestimmten Stadtbezirk"""

    # DataFrame 'unfaelle' nach dem eingegebenen Stadtbezirk filtern, also z. B. "Nord"
    gefiltert = unfaelle[unfaelle["Name"] == stadtbezirk]

    # überprüfen, ob nach dem Filtern keine Zeilen übrig bleiben (also keine Daten vorhanden sind)
    # sind tatsächlich keine Daten vorhanden, wird die Funktion beendet
    if gefiltert.empty:
        print(f"Keine Daten für den Stadtbezirk '{stadtbezirk}' gefunden.")
        return None

    # Dictionary der Verkehrsmittel erzeugen und sinnvolle Bezeichnungen vergeben
    verkehrsmittel = {
    "PKW": "IstPKW",
    "Rad": "IstRad",
    "Fußgänger": "IstFuss",
    "Kraftrad": "IstKrad",
    "Sonstige": "IstSonstig",
    }

    # Leeres Dictionary anlegen, in dem später die Ergebnisse pro Jahreszeit gespeichert werden
    ergebnis = {}

    # Schleife durchläuft alle vier Jahreszeiten nacheinander
    for jahreszeit in ["Frühling", "Sommer", "Herbst", "Winter"]:
        daten_js = gefiltert[gefiltert["Jahreszeit"] == jahreszeit]

        # Bedingung: wenn es für eine Jahreszeit keine Einträge gibt, wird diese übersprungen
        if daten_js.empty:
            continue

        # Dictionary anlegen, das für die jeweilige Jahreszeit die Anzahl der Unfälle pro Verkehrsmittel enthält
        counts = {
            name: daten_js[spalte].astype(int).sum()
            for name, spalte in verkehrsmittel.items()
        }

        # Summe der Unfälle in jeweiliger Jahreszeit berechnen (über alle Verkehrsmittel)
        # Falls keine Unfälle gezählt wurden, wird die jeweilige Jahreszeit übersprungen
        gesamt = sum(counts.values())
        if gesamt == 0:
            continue

        # für jedes Verkehrsmittel den prozentualen Anteil an der Gesamtzahl der Unfälle innerhalb der jeweiligen Jahreszeit ermitteln
        # counts.items liefert hierfür eine Liste von Key-Value-Paaren aus dem Dictionary 'counts'
        # in der Schleife wird jedes dieser Paare einzeln durchlaufen
        # d. h. key = k wird immer beibehalten, value = v, aber durch den prozentualen Anteil ersetzt
        ergebnis[jahreszeit] = {
            k: v / gesamt * 100 for k, v in counts.items()
        }

    # Ergebnis wird als Dictionary zurückgegeben, das pro Jahreszeit die Prozentwerte je Verkehrsmittel enthält
    return ergebnis

# --------------------------
# Input 2 und Funktion aufrufen
# --------------------------

stadtbezirk_input2 = str(input("Gib den Stadtbezirk ein, für den du die prozentuale Verteilung "
                               "der Unfälle nach Fortbewegungsmittel und Jahreszeit erfahren möchtest.\n"
                               "Du hast die Wahl zwischen Nord, Nordwest, Nordost, Ost, Südost, Süd, Südwest, West, Alt-West und Mitte: "))

verteilung = unfaelle_nach_jahreszeit_und_verkehrsmittel(stadtbezirk_input2)

# prüfen, ob überhaupt Daten für den Stadtbezirk gefunden wurden
# wenn ja, wird Unfallverteilung nach Jahreszeit und Fortbewegungsmittel ausgegeben
if verteilung:
    print(f"Unfallverteilung nach Fortbewegungsmittel in '{stadtbezirk_input2}':\n")

    for jahreszeit, werte in verteilung.items():
        print(f"{jahreszeit}:")
        for verkehrsmittel, prozent in werte.items():
            print(f" {verkehrsmittel}: {prozent:.2f} %") # .2f formatiert auf zwei Deimalstellen
        print()