# ========================================
# Met dit script wordt het aantal banen gekoppeld aan de od-matrix voor car
# En wordt het gewogen gemiddelde van aantal banen per buurt voor Nederland berekend (weging naar aantal inwoners per buurt)
# ========================================

# Load different Python libraries
import os
import pandas as pd
from time import gmtime, strftime
from os import listdir
import time

# Output directory (locatie waar de resultaten uit dit script worden opgeslagen)
geodms_bewerkt_dir = os.path.join(r'd:\Output')
out_filename = 'CAR_OSM2022_tomtom_2022_12.csv'

# Input directory (locatie met originele csv-bestanden die door GeoDMS zijn gemaakt) [3: REISTIJDEN]
geodms_output_dir = os.path.join(r'd:\Input\CAR_OSM2022_tomtom_2022_12')

# Vaststellen specifieke in- en output directory
workspace_input = os.path.join(geodms_output_dir)
workspace_output = os.path.join(geodms_bewerkt_dir)

# padnamen extra bestanden
locatie_lisa__csv = r'd:\Output\LISA2022.csv'
populatie = r'd:\Output\Inwoners2022.csv'

# Inlezen bestanden
print("="*40)
print("{}  : Inlezen pc6 lisa bestand banen totaal".format(strftime("%d-%m-%Y %H:%M:%S")))
lisa_bestand = pd.read_csv(locatie_lisa__csv,sep=",",decimal=",")
print("{}  : Inlezen voltooid".format(strftime("%d-%m-%Y %H:%M:%S")))
print(lisa_bestand.columns)
print("="*40)
print("{}  : Inlezen populatie per buurt".format(strftime("%d-%m-%Y %H:%M:%S")))
df_populatie = pd.read_csv(populatie, sep=";") #pd.read_excel(populatie)
print(df_populatie.columns)
print("{}  : Inlezen voltooid".format(strftime("%d-%m-%Y %H:%M:%S")))
print("="*40)

## Verwerken van de gegevens

# Inlezen bestanden
print("="*40)
print("{}  : Inlezen car traveltime per verbinding".format(strftime("%d-%m-%Y %H:%M:%S")))

directory = geodms_output_dir

csv_bestanden = [bestand for bestand in os.listdir(directory) if bestand.endswith('.csv')]

for csv_bestand in csv_bestanden:
    csv_bestand = os.path.join(directory, csv_bestand)
    if "Achterhoek_DEST" in csv_bestand:
        print("{}  : Inlezen {}".format(strftime("%d-%m-%Y %H:%M:%S"), csv_bestand))
        df_cartraveltime = pd.read_csv(csv_bestand, sep = ';')
    else:
        print("{}  : Inlezen {}".format(strftime("%d-%m-%Y %H:%M:%S"), csv_bestand))
        df_cartraveltime_tmp = pd.read_csv(csv_bestand, sep = ';')
        print("{}  : Toevoegen aan dataframe.".format(strftime("%d-%m-%Y %H:%M:%S")))
        df_cartraveltime = pd.concat([df_cartraveltime, df_cartraveltime_tmp], ignore_index=True)

print(df_cartraveltime.columns)
print("{}  : Inlezen voltooid".format(strftime("%d-%m-%Y %H:%M:%S")))

# unieke key aanmaken
df_cartraveltime['Key'] = df_cartraveltime['Org'] + "_" + df_cartraveltime['Dst'].astype(str)

# # in verband met het kunnen berekenen van de decay, moet de reistijd groter zijn dan 0; daarom 0 gewijzigd in 1 minuut reistijd
# print("{} :  Wijzigen reistijden 0 minuten (reistijd naar zelfde buurt ) naar 1 minuut ivm het correct kunnen berekenen van de decay.".format(strftime("%d-%m-%Y %H:%M:%S")))
# df_cartraveltime = df_cartraveltime.replace(0.0, 1)
# print("{} :  Klaar.".format(strftime("%d-%m-%Y %H:%M:%S")))

# instellen precisie op 2 decimalen

def set_decimal_precision(df):
    for column in df.select_dtypes(include=['float64', 'float32']).columns:
        df[column] = df[column].round(2)
    return df

df = df_cartraveltime
df = set_decimal_precision(df)

# Mergen banen aan od-matrix
print("{} :  Mergen banen aan od-matrix.".format(strftime("%d-%m-%Y %H:%M:%S")))
df_lisa = pd.merge(df, lisa_bestand, left_on='Dst', right_on='bu2022', how='left')
print("{} :  Klaar.".format(strftime("%d-%m-%Y %H:%M:%S")))

# gebruik alleen de verbindingen binnen x minuten
df_lisa_x_min = df_lisa[df_lisa["MorningRush"] < 45]

# Berekenen totaal banen per herkomstbuurt
banen_per_buurt = df_lisa_x_min.groupby("Org", as_index=False)["wpft_2022"].sum()

# koppelen inwoners
banen_per_buurt = pd.merge(banen_per_buurt, df_populatie, left_on='Org', right_on='OrgName', how='left')

# berekenen gewogen gemiddelde aantal banen per buurt voor Nederland (weging naar aantal inwoners per buurt)
gewogen_gem = (banen_per_buurt["wpft_2022"] * banen_per_buurt["totaal_2022"]).sum() / banen_per_buurt["totaal_2022"].sum()
print("Gewogen gemiddelde van het aantal banen per buurt in Nederland: {}".format(gewogen_gem))

print("{}  : Exporteren eindbestand".format(strftime("%d-%m-%Y %H:%M:%S")))
out_file = os.path.join(geodms_bewerkt_dir, out_filename)
df_lisa.to_csv(out_file, index=False)
print("{}  : Export voltooid".format(strftime("%d-%m-%Y %H:%M:%S")))

