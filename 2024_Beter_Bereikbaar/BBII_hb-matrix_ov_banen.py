# ========================================
# Met dit script wordt het aantal banen gekoppeld aan de od-matrix voor OV
# Vervolgens wordt de mediaan reistijd berekend voor ochtend, middag, avond per od-verbinding
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
out_filename = 'W_OV_W_with_WW_2022_di.csv'

# Input directory (locatie met originele csv-bestanden die door GeoDMS zijn gemaakt)
geodms_output_dir = os.path.join(r'd:\Input\W_OV_W_with_WW_2022_di')

# Vaststellen specifieke in- en output directory
workspace_input = os.path.join(geodms_output_dir)
workspace_output = os.path.join(geodms_bewerkt_dir)

# list van uren; o.a. gebruikt bij berekenen mediaan voor de verschillende uren
hours = ["07h", "12h", "21h"]

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

print("="*50)
print("{} :  Inlezen REISTIJDEN en berekenen MEDIAAN per verbinding".format(strftime("%d-%m-%Y %H:%M:%S")))
print("="*50)
print("\n")

y_in = geodms_output_dir
y_out = geodms_bewerkt_dir

# lijst maken van geodms csv-files; sluit zip- en xml-bestanden uit
input_files_dir = os.listdir(y_in)

for item in input_files_dir:
    if ".xml" in item:
        input_files_dir.remove(item)
    if ".zip" in item:
        input_files_dir.remove(item)
    if ".dms" in item:
        input_files_dir.remove(item)
for item in input_files_dir:
    if ".zip" in item:
        input_files_dir.remove(item)
    if ".xml" in item:
        input_files_dir.remove(item)
    if ".dms" in item:
        input_files_dir.remove(item)
        
input_files_dir_regio = input_files_dir
y_in_file = os.path.join(y_in, input_files_dir_regio[0])
y_out_file = os.path.join(y_out, input_files_dir[0]).replace(".csv", "_allbrt.csv")
n = 0

# inlezen van GeoDMS bestanden voor OV en samenstellen bestand reistijden
columns = []
for filename in input_files_dir_regio:
#         print(filename)
    if "07h00m" in filename:
        n += 1
        y_in_file = os.path.join(y_in, filename)
        print("="*40)
        print(n)
        y_out_file = os.path.join(y_out, filename).replace(".csv", "_allbrt.csv").replace("Dep_At_07h00m", "AllDep")
        print("{} :  GeoDMS csv inlezen: \n{}".format(strftime("%d-%m-%Y %H:%M:%S"), y_in_file))
        data = pd.read_csv(y_in_file, sep = ';')#, nrows=10000)
        data['Key'] = data['OrgName'] + "_" + data['DestName'].astype(str)
        print("Aantal records ingelezen databestand :  {}".format(len(data)))
        column = data.columns[2]
        columns.append(column)
    else:
        n += 1
        y_in_file = os.path.join(y_in, filename)
        print("="*40)
        print(n)
        print("{} :  GeoDMS csv inlezen: \n{}".format(strftime("%d-%m-%Y %H:%M:%S"), y_in_file))
        data_append = pd.read_csv(y_in_file, sep = ';')#, nrows=10000)
        data_append['Key'] = data_append['OrgName'] + "_" + data_append['DestName'].astype(str)
        print(len(data_append))
        print("{} :  Data mergen ".format(strftime("%d-%m-%Y %H:%M:%S")))
        data = pd.merge(data, data_append, on='Key', how='outer')
        print("Aantal records na mergen ingelezen databestand :  {}".format(len(data)))
        data['OrgName_x'].fillna(data['OrgName_y'], inplace=True)
        data['DestName_x'].fillna(data['DestName_y'], inplace=True)
        data.rename(columns={'OrgName_x': 'OrgName'}, inplace=True)
        data.rename(columns={'DestName_x': 'DestName'}, inplace=True)
        del data['OrgName_y']
        del data['DestName_y']
        column = data_append.columns[2]
        columns.append(column)

# Berekenen mediaan per verbinding
print("")
print("="*40)
print("{} :  Mediaan berekenen voor de verschillende dagmomenten".format(strftime("%d-%m-%Y %H:%M:%S")))
print("="*40)

for hour in hours:
    print(hour)
    columns_median = []
    # verzamel alle kolomnamen met de specifieke reistijd
    for i in columns:
        if "{}".format(hour) in i:
            columns_median.append(i)
    # Bereken de mediaan voor elke rij, met inachtneming van de geselecteerde kolommen
    row_medians = data[columns_median].median(axis=1)

    # Voeg de berekende medianen toe als een nieuwe kolom aan het DataFrame
    data['Median_TT_{}'.format(hour)] = row_medians

    columns.append('Median_TT_{}'.format(hour))

print("\n")
print("="*40)
print("{} :  Klaar".format(strftime("%d-%m-%Y %H:%M:%S")))
print("="*40)

# # in verband met het kunnen berekenen van de decay, moet de reistijd groter zijn dan 0; daarom 0 gewijzigd in 1 minuut reistijd = binnen eigen buurt
# print("{} :  Wijzigen reistijden 0 minuten (reistijd naar zelfde buurt ) naar 1 minuut ivm het correct kunnen berekenen van de decay.".format(strftime("%d-%m-%Y %H:%M:%S")))
# data = data.replace(0.0, 1)
# print("{} :  Klaar.".format(strftime("%d-%m-%Y %H:%M:%S")))

# verwijderen kolommen OD-matrix waar "Traveltime" of "ModeUsed" in kolomnaam staat
for name in data.columns:
    if "Traveltime" in name:
        print("delete kolom {}".format(name))
        del data[name]
count_columns = 0 

#verwijderen kolommen OD-matrix
for name in data.columns:
    if "ModeUsed" in name:
        print("delete kolom {}".format(name))
        del data[name]
count_columns = 0 

print("{} :  Alle kolommen met 'Traveltime' of 'ModeUsed' in kolomnaam zijn verwijderd.".format(strftime("%d-%m-%Y %H:%M:%S")))

# De functie set_decimal_precision rondt in een DataFrame alle kolommen van het type float32 en float64 af op twee decimalen en geeft het aangepaste DataFrame terug.
def set_decimal_precision(df):
    for column in df.select_dtypes(include=['float64', 'float32']).columns:
        df[column] = df[column].round(2)
    return df

df = data

# print("Voor het instellen van precisie:")
# print(df)

df = set_decimal_precision(df)

print("\nNa het instellen van precisie:")
print(df)

# Mergen banen aan od-matrix
print("{} :  Mergen banen aan od-matrix.".format(strftime("%d-%m-%Y %H:%M:%S")))
df_lisa = pd.merge(df, lisa_bestand, left_on='DestName', right_on='bu2022', how='left')
print("{} :  Klaar.".format(strftime("%d-%m-%Y %H:%M:%S")))

# gebruik alleen de verbindingen binnen x minuten
df_lisa_x_min_morning = df_lisa[df_lisa["Median_TT_07h"] < 45]
df_lisa_x_min_noon = df_lisa[df_lisa["Median_TT_12h"] < 45]
df_lisa_x_min_evening = df_lisa[df_lisa["Median_TT_21h"] < 45]

# Berekenen totaal banen per herkomstbuurt
banen_per_buurt_morning = df_lisa_x_min_morning.groupby("OrgName", as_index=False)["wpft_2022"].sum()
banen_per_buurt_noon = df_lisa_x_min_noon.groupby("OrgName", as_index=False)["wpft_2022"].sum()
banen_per_buurt_evening = df_lisa_x_min_evening.groupby("OrgName", as_index=False)["wpft_2022"].sum()

# koppelen inwoners
banen_per_buurt_morning = pd.merge(banen_per_buurt_morning, df_populatie, left_on='OrgName', right_on='OrgName', how='left')
banen_per_buurt_noon = pd.merge(banen_per_buurt_noon, df_populatie, left_on='OrgName', right_on='OrgName', how='left')
banen_per_buurt_evening = pd.merge(banen_per_buurt_evening, df_populatie, left_on='OrgName', right_on='OrgName', how='left')

# berekenen gewogen gemiddelde aantal banen per buurt voor Nederland (weging naar aantal inwoners per buurt)
gewogen_gem_morning = (banen_per_buurt_morning["wpft_2022"] * banen_per_buurt_morning["totaal_2022"]).sum() / banen_per_buurt_morning["totaal_2022"].sum()
gewogen_gem_noon = (banen_per_buurt_noon["wpft_2022"] * banen_per_buurt_noon["totaal_2022"]).sum() / banen_per_buurt_noon["totaal_2022"].sum()
gewogen_gem_evening = (banen_per_buurt_evening["wpft_2022"] * banen_per_buurt_evening["totaal_2022"]).sum() / banen_per_buurt_evening["totaal_2022"].sum()

print("Gewogen gemiddelde van het aantal banen per buurt in Nederland - ochtend: {}".format(gewogen_gem_morning))
print("Gewogen gemiddelde van het aantal banen per buurt in Nederland: - middag {}".format(gewogen_gem_noon))
print("Gewogen gemiddelde van het aantal banen per buurt in Nederland: - avond {}".format(gewogen_gem_evening))

print("{}  : Exporteren eindbestand".format(strftime("%d-%m-%Y %H:%M:%S")))
out_file = os.path.join(geodms_bewerkt_dir, out_filename)
df_lisa.to_csv(out_file, index=False)
print("{}  : Export voltooid".format(strftime("%d-%m-%Y %H:%M:%S")))

