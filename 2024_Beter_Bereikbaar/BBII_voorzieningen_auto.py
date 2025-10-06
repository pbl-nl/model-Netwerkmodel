# Load different Python libraries
import os
import sys
import pandas as pd
import numpy as np
from time import gmtime, strftime
from os import listdir
import copy

# Get ArcGIS paths to load ArcPy
with open(r".\support\py64paths_CPE.txt") as f:
    gispaths = f.readlines()
    gispaths = [x.strip() for x in gispaths] 

for path in gispaths:
    if path not in sys.path:
        sys.path.append(path)  

## inhoud py64paths_CPE.txt:
# c:\program files (x86)\arcgis\desktop10.6\arcpy
# C:\Python27\ArcGISx6410.6
# C:\Windows\SYSTEM32\python27.zip
# C:\Python27\ArcGISx6410.6\DLLs
# C:\Python27\ArcGISx6410.6\lib
# C:\Python27\ArcGISx6410.6\lib\plat-win
# C:\Python27\ArcGISx6410.6\lib\lib-tk
# C:\Python27\ArcGISx6410.6\lib\site-packages
# C:\Program Files (x86)\ArcGIS\Desktop10.6\bin64
# C:\Program Files (x86)\ArcGIS\Desktop10.6\ArcPy
# C:\Program Files (x86)\ArcGIS\Desktop10.6\ArcToolBox\Scripts

# Import ArcPy
try:
    import arcpy
    from arcpy import env
    print("Arcpy ingeladen")
except:
    print("Arcpy kan niet ingeladen worden. Ga na of Python de benodigde paden weet te vinden.")

# ---------------------------------------------
# Instellingen
# ---------------------------------------------

# Aanmaken 2 dictionaries: instellingen en uitleg
settings_dict = {}
settings_dict_uitleg = {}

# Input directory (locatie met originele csv-bestanden die door GeoDMS zijn gemaakt)
# geodms_output_dir = os.path.join(r'd:\geodms_output\Output')
geodms_output_dir = os.path.join(r'c:\RN\z')
settings_dict["geodms_output_dir"] = geodms_output_dir
settings_dict_uitleg["geodms_output_dir"] = "Locatie met originele csv-bestanden die door GeoDMS zijn aangemaakt"

# Output directory (locatie waar de resultaten uit dit script worden opgeslagen)
# geodms_bewerkt_dir = os.path.join(r'c:\RN\z_output')
geodms_bewerkt_dir = os.path.join(r'c:RN\_Result_python_temp')
settings_dict["geodms_bewerkt_dir"] = geodms_bewerkt_dir
settings_dict_uitleg["geodms_bewerkt_dir"] = "Output directory (locatie waar de resultaten uit dit script worden opgeslagen)"

# Locatie polygonenbestand waaraan data wordt gekoppeld (kolommen zijn gereduceerd tot buurtcode)
polygons = os.path.join(r""d:\Brondata\RegioIndelingen\CBS_WijkBuurt\2022\buurt_2022_zonder_cbs_cijfers.shp")
settings_dict["polygons"] = polygons
settings_dict_uitleg["polygons"] = "Locatie polygonenbestand waaraan later in dit script data wordt gekoppeld (kolommen met cbs-cijfers zijn hieruit verwijderd)"

# Locatie polygonenbestand waaraan data wordt gekoppeld (dit is het totale bestand met alle kolommen)
polygons_cijfers = os.path.join(r"d:\Brondata\RegioIndelingen\CBS_WijkBuurt\2022\buurt_2022_v1.shp")
settings_dict["polygons"] = polygons_cijfers
settings_dict_uitleg["polygons_cijfers"] = "Locatie polygonenbestand waaraan later in dit script data wordt gekoppeld (kolommen met cbs-cijfers zijn hieruit verwijderd)"

# type car network
type_carnetwork = "OSM2022_tomtom" #tomtom zonder jaar invullen (staat verderop bij datum), indien geprojecteerd op osm jaar osm invullen

# ======================================
# Analyse datum date (datum in bestandsnaam) 
date = "2022_12"
settings_dict["date"] = date
settings_dict_uitleg["date"] = "Analysis date (datum in bestandsnaam) "
# ======================================

# ======================================
# Type run
type_run = "car"
settings_dict["type_run"] = type_run
settings_dict_uitleg["type_run"] = "Type run"
# ======================================

# ======================================
# vul in TT of B
traveltime_banen = 'TT'
# ======================================

# Vaststellen public of private transport
public_private = ""
if type_run in ["car", "bike", "pedestrian"]:
    public_private = "Private transport"
else:
    public_private = "Public transport"

settings_dict["public_private"] = public_private
settings_dict_uitleg["public_private"] = "Betreft het een run met public of private transport"

# ======================================
# Stel tijdblok in bij Private Transport of "" bij OV
tijdblok = "tuesday" #MonTue #WedThuFri #SatSun
if tijdblok != "":
    tijdblok_private = "_" + tijdblok
else:
    tijdblok_private = ""
# ======================================

# # Instelling extra minuten voor car ivm lopen naar auto en parkeertijd
# extraminuten_car = 5 #5
    
# Naam run
indicator = "VO2022_"
koppel_identificatie = "VO_ID"
if type_carnetwork <> "":
    carnetwork = "_" + type_carnetwork
else:
    carnetwork = ""
    
run = indicator + traveltime_banen + "_" + type_run + carnetwork + "_" + date + tijdblok_private # vul hier de naam van de directory met excelbestanden in (niveau hoger dan geodms_output_dir en geodms_bewerkt_dir)
settings_dict["run"] = run
settings_dict_uitleg["run"] = "Naam van de run"

# # ======================================
# # Calculation type --> waarde is alleen van invloed bij private transport (bij public transport mag alles er dus staan)
# calculation_type =  "freeflow"  #"freeflow" "MorningRush" "NoonRush" "LateEveningRush" "ActualBike"
# settings_dict["calculation_type"] = calculation_type
# settings_dict_uitleg["calculation_type"] = "Calculation type"
# ======================================

# 1h of 2h gemiddelden
gem_hour = ""
# selectie
subset = "" #"_W10"  #"_" + "cat_1_2_4"
# walking time biking time variant
walkbike = ""
# zonder of met wachttijd
wachttijd = ""

# Vaststellen specifieke in- en output directory
workspace_input = os.path.join(geodms_output_dir, run+"_"+wachttijd+"_"+walkbike+"_"+gem_hour+subset)
workspace_output = os.path.join(geodms_bewerkt_dir, run+"_"+wachttijd+"_"+walkbike+"_"+gem_hour+subset)

settings_dict["workspace_input"] = workspace_input
settings_dict_uitleg["workspace_input"] = "Input directory"
settings_dict["workspace_output"] = workspace_output
settings_dict_uitleg["workspace_output"] = "Output directory"

# Lege lijstjes aanmaken en vullen met volledige naam van de in de input directory's voorkomende runs
variant_list = []
variant_list_cbp = []

for subfolder in os.listdir(geodms_output_dir):
    if date in subfolder:
        if ("car" in subfolder or "bike" in subfolder or "pedestrian" in subfolder):
            variant_list_cbp.append(subfolder)
        else:
            variant_list.append(subfolder)

variant_list_plus = variant_list + variant_list_cbp

settings_dict["variant_list"] = variant_list
settings_dict_uitleg["variant_list"] = "PM"
settings_dict["variant_list_cbp"] = variant_list_cbp
settings_dict_uitleg["variant_list_cbp"] = "PM"
settings_dict["variant_list_plus"] = variant_list_plus
settings_dict_uitleg["variant_list_plus"] = "PM"

print("De volgende '{}'-gegevens worden (gegeven de instellingen) in deze notebook verwerkt:\n{}\n".format(public_private, workspace_input))

print("De volgende varianten van '{}' met alanysis_date '{}'staan in de input directory:".format(public_private, date))
for i in variant_list_plus:
    print(i)

# inlezen kolom met geodms-id's en buurtcodes van destinations (tbv car berekening)
geodms_ids_file = os.path.join(geodms_output_dir, "sub_BJ_HAVO_VWO_2022.csv")

print("-" * 120)
for item in settings_dict:
    try:
        print(settings_dict_uitleg[item])
    except:
        print("")
    print("{}:\n{}".format(item, settings_dict[item]))
    print("-" * 120)

size = len(indicator)
# Slice string to remove last character from string
mod_string = indicator[:size - 3]

# Vertrekreistijd car bepalen voor verschillende stedelijkheidscategorieen (wordt later opgeteld bij de parkeerzoektijd)
vertrekreistijd_car = 1

if type_run == "car":
    size = len(indicator)
    # Slice string to remove last character from string
    mod_string = indicator[:size - 3]
    if "ZH" in run:
        print("Correctie betreft ziekenhuizen.")
        correctie_vertrekreistijd_parkeerzoektijd = {0: 2+vertrekreistijd_car, 1: 4+vertrekreistijd_car, 2: 2+vertrekreistijd_car, 3: 2+vertrekreistijd_car, 4: 2+vertrekreistijd_car, 5: 2+vertrekreistijd_car}
    else:
        print("Correctie betreft andere type destinations dan ziekenhuizen.")
        correctie_vertrekreistijd_parkeerzoektijd = {0: 1+vertrekreistijd_car, 1: 2+vertrekreistijd_car, 2: 1+vertrekreistijd_car, 3: 1+vertrekreistijd_car, 4: 1+vertrekreistijd_car, 5: 1+vertrekreistijd_car}
        
    print("\nCorrectie aantal minuten per verstedelijkingscategorie:\nVertrekreistijd / parkeerzoektijd: {}".format(correctie_vertrekreistijd_parkeerzoektijd))

    # inlezen kolom met geodms-id's en buurtcodes van destinations
    settings_dict["geodms_ids"] = geodms_ids_file
    settings_dict_uitleg["run"] = "kolom met geodms-id's en buurtcodes van destinations"
    geodms_ids = pd.read_csv(geodms_ids_file, sep = ';')
    geodms_ids = geodms_ids[[koppel_identificatie, 'buurtcode']]
    geodms_ids = geodms_ids.replace("'", "", regex=True)
    print("\n{}".format(geodms_ids_file))


    # Inlezen tabel met buurtcodes uit polygonenbestand met gegevens (aantal inwoners). Pandastabel: region_code_cijfers.
    # Import dbf table from polygons
    import_table_cijfers = polygons_cijfers.replace(".shp", ".dbf")
    settings_dict["import_table_cijfers"] = import_table_cijfers
    settings_dict_uitleg["import_table_cijfers"] = "Locatie waar vandaan de ruimtelijke indeling (met gegevens) van de sources is ingelezen"

    arr_cijfers = arcpy.da.TableToNumPyArray(import_table_cijfers, ("BU_CODE", "AANT_INW", "STED"))

    region_code_cijfers = pd.DataFrame(arr_cijfers)

    region_code_cijfers.rename(columns={'BU_CODE': 'OrgName'}, inplace=True)

    region_code_cijfers = region_code_cijfers.sort_values("AANT_INW", ascending=True)
    region_code_cijfers["AANT_INW"] = region_code_cijfers["AANT_INW"].apply(lambda x : x if x > 0 else 0)
    region_code_cijfers["STED"] = region_code_cijfers["STED"].apply(lambda x : x if x > 0 else 0)

    # kolom Correctie aanmaken met minuten tbv correctie voor car
    region_code_cijfers['Correctie'] = region_code_cijfers['STED']
    region_code_cijfers['Correctie'] = region_code_cijfers['Correctie'].replace(correctie_vertrekreistijd_parkeerzoektijd)

    print(len(arr_cijfers))

    geodms_ids = pd.merge(geodms_ids, region_code_cijfers, left_on="buurtcode", right_on="OrgName", how='left')
    geodms_ids = geodms_ids[[koppel_identificatie, 'Correctie']]

# # Blok RENAMEN

# # Script om te lange inputbestanden te renamen
# # Doet niets indien tempdirectory leeg is of indien bestanden al gerenamed zijn

# tempdir = r"C:\RN"
# settings_dict["tempdir"] = r"C:\RN"
# settings_dict_uitleg["tempdir"] = "Tijdelijke locatie op disk waar bestandsnamen in lengte worden gerealiseerd"

# for folder in os.listdir(tempdir):
#     full_folder = os.path.join(tempdir, folder)
#     for filename_old in os.listdir(full_folder):
#         full_filename_old = os.path.join(full_folder, filename_old)
#         full_filename_new = full_filename_old.replace("Traveltime", "TT").replace("Departure", "Dep").replace("centroiden", "centr").replace("Buurt", "Brt").replace("00s", "").replace("Long", "Lng").replace("DEST", "DST").replace("with", "w").replace("Dep_At", "Dep").replace("TT_Lng_", "TTLng").replace("W_OV_W_w_WW", "WOVWwWW").replace("O2SWtime-", "").replace("voortgezet_onderwijs", "vo")
#         os.rename(full_filename_old, full_filename_new)
#         print("renamed {} --> {}".format(full_filename_old, full_filename_new))

# In dit deel wordt een directorty in Def aangemaakt, waarin alle output wordt opgeslagen.

if os.path.exists(workspace_output):
    print("Directory {} bestaat al en is niet aangemaakt.".format(workspace_output))
else:
    print("Directory {} bestond nog niet en is aangemaakt.".format(workspace_output))
    os.makedirs(workspace_output)
    
# Inlezen tabel met buurtcodes uit polygonenbestand. Pandastabel: region_code.
# Import dbf table from polygons
import_table = polygons.replace(".shp", ".dbf")
settings_dict["import_table"] = import_table
settings_dict_uitleg["import_table"] = "Locatie waar vandaan de ruimtelijke indeling van de sources is ingelezen"

arr = arcpy.da.TableToNumPyArray(import_table, ("BU_CODE"))
region_code = pd.DataFrame(arr)
region_code.rename(columns={'BU_CODE': 'OrgName'}, inplace=True)
region_code = region_code.sort_values("OrgName", ascending=True) 
print(len(arr))

# Create ArcGIS file-geodatabase to store ArcGIS-data
fgdb_name = "Data.gdb"
settings_dict["fgdb_name"] = fgdb_name
settings_dict_uitleg["fgdb_name"] = "Locatie file geodatabase waarin resultaten worden opgeslagen"

fgdb_folder = os.path.join(geodms_bewerkt_dir, run+"_"+wachttijd+"_"+walkbike+"_"+gem_hour+subset)
settings_dict["fgdb_folder"] = fgdb_folder
settings_dict_uitleg["fgdb_folder"] = "Output directory waarin reaultaten worden opgeslagen, waaronder de fgdb"

fgdb_out = os.path.join(fgdb_folder, fgdb_name)
settings_dict["fgdb_out"] = fgdb_out
settings_dict_uitleg["fgdb_out"] = "Padnaam fgdb"

print("Output folder: {}".format(fgdb_folder))
# # Execute CreateFileGDB_management
try:
    arcpy.CreateFileGDB_management(fgdb_folder, fgdb_name)
    print("File-geodatabase aangemaakt")
except:
    print("Something went wrong creating the new File-geodatabase {}".format(fgdb_name))

### 1. Aanmaken tabellen met GeoDMS output, voorzien van ontbrekende buurtcodes
# Ruwe GeoDMS output voorzien van ontbrekende buurtcodes
# Inlezen tabel met buurtcodes uit polygonenbestand. Pandastabel: region_code.

y_in = os.path.join(geodms_output_dir, run+"_"+wachttijd+"_"+walkbike+"_"+gem_hour+subset)
y_out = os.path.join(geodms_bewerkt_dir, run+"_"+wachttijd+"_"+walkbike+"_"+gem_hour+subset)

print(y_in)
print(y_out)
settings_dict["y_in"] = y_in
settings_dict_uitleg["y_in"] = "PM"
settings_dict["y_out"] = y_out
settings_dict_uitleg["y_out"] = "PM"

input_files_dir = os.listdir(y_in)
settings_dict["input_files_dir"] = input_files_dir
settings_dict_uitleg["input_files_dir"] = "PM"

# Opschonen input_files_dir
for filename in input_files_dir:
    if ".xml" in filename:
        input_files_dir.remove(filename)
for filename in input_files_dir:
    if ".zip" in filename:
        input_files_dir.remove(filename)
for filename in input_files_dir:
    if ".dms" in filename:
        input_files_dir.remove(filename)

y_in_file = os.path.join(y_in, input_files_dir[0])
settings_dict["y_in_file"] = y_in_file
settings_dict_uitleg["y_in_file"] = "PM"

y_out_file = os.path.join(y_out, input_files_dir[0]).replace(".csv", "_allbrt.csv")
settings_dict["y_out_file"] = y_out_file
settings_dict_uitleg["y_out_file"] = "PM"

varianten_car = ['MaxSpeed', 'MorningRush', 'NoonRush', 'LateEveningRush']

if public_private == "Private transport":
    if type_run in y_out_file:
        y_out_file_export_to_map = y_out_file
        settings_dict["y_out_file_export_to_map"] = y_out_file_export_to_map
        settings_dict_uitleg["y_out_file_export_to_map"] = "PM"

    print("Inlezen originele GeoDMS csv: {}".format(y_in_file))
    orgfile_private = pd.read_csv(y_in_file, sep = ';')
    orgfile_private = orgfile_private.rename(columns={'Org': 'OrgName', 'Dst': 'DestName'})
    
    if type_run == "car":
        # correctie toepassen op reisijden car voor alle tijdstippen met het aantal minuten in variabele extraminuten_car
        orgfile_private = pd.merge(orgfile_private, geodms_ids, left_on='DestName', right_on=koppel_identificatie, how='inner') #outer is vervangen door inner omdat er records werden toegevoegd zonder OrgName

        print("Reistijden voor alle tijdstippen corrigeren met aantal minuten, afhankelijk van stedelijkheidsklasse waar destination is gevestigd {}".format(correctie_vertrekreistijd_parkeerzoektijd))
        for col_car in orgfile_private.columns.tolist():
            if col_car in varianten_car:
                print("Corrigeren {}".format(col_car))
                orgfile_private[col_car] = orgfile_private[col_car] + orgfile_private["Correctie"]        
        del orgfile_private[koppel_identificatie]
        del orgfile_private["Correctie"]

# Voor pedestrian en bike geldt dat Org en Dest andersom worden berekend, kolomnamen moeten daarom hernoemd worden
# Berekening in GeoDMS gaat daardoor sneller, het maakt niet uit of je voor pedestrian org-dest berekent of dest-org
# Er is namelijk geen sprake van eenrichtingsverkeer

    # enkel kolommen renamen bij berekening van TT (bij traveltime, en niet bij banen)
#     if traveltime_banen == "TT":
#         if settings_dict["type_run"] == "pedestrian" or settings_dict["type_run"] == "bike":
#             orgfile_private = orgfile_private.rename(columns={'OrgName': 'TempName'})
#             orgfile_private = orgfile_private.rename(columns={'DestName': 'OrgName'})
#             orgfile_private = orgfile_private.rename(columns={'TempName': 'DestName'})
#             orgfile_private = orgfile_private.rename(columns={'Freeflow': 'freeflow'})
    print("Ingelezen '{}' bestand bevat {} records.".format(public_private, len(orgfile_private.index)))
    data = pd.merge(region_code, orgfile_private, on='OrgName', how='outer')
    data = data.replace(np.nan, -99999).sort_values(by=['OrgName'])
#     print("GeoDMS csv aangevuld met buurten: {}".format(y_out_file))
    print("Bestand na aanvullen ontbrekende buurten bevat {} records.".format(len(data.index)))

    if os.path.exists(y_out_file):
        print("Csv is al eerder opgeslagen. Dateframe is niet opnieuw geexporteerd.")
        next
    else:
        data.to_csv (y_out_file, index = None, header=True, sep=";", decimal=",")
        print("Export ruwe output naar csv voltooid.")
        print("*"*120)

    print(y_out_file_export_to_map)
    print(len(data))

print("{}".format(len(data['OrgName'].unique().tolist())))

columns = []
columns_dict = {}

for i in data.columns:
    if i == "OrgName" or i == "DestName" or i == "Traveltime_m_At_07h00m00s" or i == "Key" or i == "Traveltime_m_At_07h10m00s" or i == "Traveltime_m_At_07h20m00s" or i == "Traveltime_m_At_07h30m00s" or i == "Traveltime_m_At_07h40m00s" or i == "Traveltime_m_At_07h50m00s" or i == "Traveltime_m_At_08h00m00s" or i == "Traveltime_m_At_08h10m00s" or i == "Traveltime_m_At_08h20m00s" or i == "Traveltime_m_At_08h30m00s" or i == "Traveltime_m_At_08h40m00s" or i == "Traveltime_m_At_08h50m00s" or i == "Traveltime_m_At_12h00m00s" or i == "Traveltime_m_At_12h10m00s" or i == "Traveltime_m_At_12h20m00s" or i == "Traveltime_m_At_12h30m00s" or i == "Traveltime_m_At_12h40m00s" or i == "Traveltime_m_At_12h50m00s" or i == "Traveltime_m_At_13h00m00s" or i == "Traveltime_m_At_13h10m00s" or i == "Traveltime_m_At_13h20m00s" or i == "Traveltime_m_At_13h30m00s" or i == "Traveltime_m_At_13h40m00s" or i == "Traveltime_m_At_13h50m00s" or i == "Traveltime_m_At_21h00m00s" or i == "Traveltime_m_At_21h10m00s" or i == "Traveltime_m_At_21h20m00s" or i == "Traveltime_m_At_21h30m00s" or i == "Traveltime_m_At_21h40m00s" or i == "Traveltime_m_At_21h50m00s" or i == "Traveltime_m_At_22h00m00s" or i == "Traveltime_m_At_22h10m00s" or i == "Traveltime_m_At_22h20m00s" or i == "Traveltime_m_At_22h30m00s" or i == "Traveltime_m_At_22h40m00s" or i == "Traveltime_m_At_22h50m00s" or i == "Traveltime_m_At_07h05m00s" or i == "Traveltime_m_At_07h15m00s" or i == "Traveltime_m_At_07h25m00s" or i == "Traveltime_m_At_07h35m00s" or i == "Traveltime_m_At_07h45m00s" or i == "Traveltime_m_At_07h55m00s" or i == "Traveltime_m_At_08h05m00s" or i == "Traveltime_m_At_08h15m00s" or i == "Traveltime_m_At_08h25m00s" or i == "Traveltime_m_At_08h35m00s" or i == "Traveltime_m_At_08h45m00s" or i == "Traveltime_m_At_08h55m00s" or i == "Traveltime_m_At_12h05m00s" or i == "Traveltime_m_At_12h15m00s" or i == "Traveltime_m_At_12h25m00s" or i == "Traveltime_m_At_12h35m00s" or i == "Traveltime_m_At_12h45m00s" or i == "Traveltime_m_At_12h55m00s" or i == "Traveltime_m_At_13h05m00s" or i == "Traveltime_m_At_13h15m00s" or i == "Traveltime_m_At_13h25m00s" or i == "Traveltime_m_At_13h35m00s" or i == "Traveltime_m_At_13h45m00s" or i == "Traveltime_m_At_13h55m00s" or i == "Traveltime_m_At_21h05m00s" or i == "Traveltime_m_At_21h15m00s" or i == "Traveltime_m_At_21h25m00s" or i == "Traveltime_m_At_21h35m00s" or i == "Traveltime_m_At_21h45m00s" or i == "Traveltime_m_At_21h55m00s" or i == "Traveltime_m_At_22h05m00s" or i == "Traveltime_m_At_22h15m00s" or i == "Traveltime_m_At_22h25m00s" or i == "Traveltime_m_At_22h35m00s" or i == "Traveltime_m_At_22h45m00s" or i == "Traveltime_m_At_22h55m00s" or i == "count_1x_07" or i == "count_1x_08" or i == "count_1x_12" or i == "count_1x_13" or i == "count_1x_21" or i == "count_1x_22" or i == "max_1x_pu_0708" or i == "max_1x_pu_1213" or i == "max_1x_pu_2122" or i == "ModeUsed_At_07h00m00s" or i == "ModeUsed_At_07h10m00s" or i == "ModeUsed_At_07h20m00s" or i == "ModeUsed_At_07h30m00s" or i == "ModeUsed_At_07h40m00s" or i == "ModeUsed_At_07h50m00s" or i == "ModeUsed_At_08h00m00s" or i == "ModeUsed_At_08h10m00s" or i == "ModeUsed_At_08h20m00s" or i == "ModeUsed_At_08h30m00s" or i == "ModeUsed_At_08h40m00s" or i == "ModeUsed_At_08h50m00s" or i == "ModeUsed_At_12h00m00s" or i == "ModeUsed_At_12h10m00s" or i == "ModeUsed_At_12h20m00s" or i == "ModeUsed_At_12h30m00s" or i == "ModeUsed_At_12h40m00s" or i == "ModeUsed_At_12h50m00s" or i == "ModeUsed_At_13h00m00s" or i == "ModeUsed_At_13h10m00s" or i == "ModeUsed_At_13h20m00s" or i == "ModeUsed_At_13h30m00s" or i == "ModeUsed_At_13h40m00s" or i == "ModeUsed_At_13h50m00s" or i == "ModeUsed_At_21h00m00s" or i == "ModeUsed_At_21h10m00s" or i == "ModeUsed_At_21h20m00s" or i == "ModeUsed_At_21h30m00s" or i == "ModeUsed_At_21h40m00s" or i == "ModeUsed_At_21h50m00s" or i == "ModeUsed_At_22h00m00s" or i == "ModeUsed_At_22h10m00s" or i == "ModeUsed_At_22h20m00s" or i == "ModeUsed_At_22h30m00s" or i == "ModeUsed_At_22h40m00s" or i == "ModeUsed_At_22h50m00s" or i == "ModeUsed_At_07h05m00s" or i == "Key" or i == "ModeUsed_At_07h15m00s" or i == "ModeUsed_At_07h25m00s" or i == "ModeUsed_At_07h35m00s" or i == "ModeUsed_At_07h45m00s" or i == "ModeUsed_At_07h55m00s" or i == "ModeUsed_At_08h05m00s" or i == "ModeUsed_At_08h15m00s" or i == "ModeUsed_At_08h25m00s" or i == "ModeUsed_At_08h35m00s" or i == "ModeUsed_At_08h45m00s" or i == "ModeUsed_At_08h55m00s" or i == "ModeUsed_At_12h05m00s" or i == "ModeUsed_At_12h15m00s" or i == "ModeUsed_At_12h25m00s" or i == "ModeUsed_At_12h35m00s" or i == "ModeUsed_At_12h45m00s" or i == "ModeUsed_At_12h55m00s" or i == "ModeUsed_At_13h05m00s" or i == "ModeUsed_At_13h15m00s" or i == "ModeUsed_At_13h25m00s" or i == "ModeUsed_At_13h35m00s" or i == "ModeUsed_At_13h45m00s" or i == "ModeUsed_At_13h55m00s" or i == "ModeUsed_At_21h05m00s" or i == "ModeUsed_At_21h15m00s" or i == "ModeUsed_At_21h25m00s" or i == "ModeUsed_At_21h35m00s" or i == "ModeUsed_At_21h45m00s" or i == "ModeUsed_At_21h55m00s" or i == "ModeUsed_At_22h05m00s" or i == "ModeUsed_At_22h15m00s" or i == "ModeUsed_At_22h25m00s" or i == "ModeUsed_At_22h35m00s" or i == "ModeUsed_At_22h45m00s" or i == "ModeUsed_At_22h55m00s":
        next
    else:
        columns.append(i)

columns_dict["Freeflow"] = "FF"
columns_dict["ActualBike"] = "AB"
columns_dict["MaxSpeed"] = "MS"
columns_dict["MorningRush"] = "MR"
columns_dict["NoonRush"] = "NR"
columns_dict["Freeflow"] = "FF"
columns_dict["Freeflow_ebike"] = "FFEB"
columns_dict["LateEveningRush"] = "LER"
columns_dict["Median_TT_0708h"] = "0708h"
columns_dict["Median_TT_1213h"] = "1213h"
columns_dict["Median_TT_2122h"] = "2122h"


### Tabel maken met aantal bestemmingen (alleen draaien bij TT)
columns = []
columns_dict = {}

for i in data.columns:
    if i == "OrgName" or i == "DestName" or i == "Traveltime_m_At_07h00m00s" or i == "Key" or i == "Traveltime_m_At_07h10m00s" or i == "Traveltime_m_At_07h20m00s" or i == "Traveltime_m_At_07h30m00s" or i == "Traveltime_m_At_07h40m00s" or i == "Traveltime_m_At_07h50m00s" or i == "Traveltime_m_At_08h00m00s" or i == "Traveltime_m_At_08h10m00s" or i == "Traveltime_m_At_08h20m00s" or i == "Traveltime_m_At_08h30m00s" or i == "Traveltime_m_At_08h40m00s" or i == "Traveltime_m_At_08h50m00s" or i == "Traveltime_m_At_15h00m00s" or i == "Traveltime_m_At_15h10m00s" or i == "Traveltime_m_At_15h20m00s" or i == "Traveltime_m_At_15h30m00s" or i == "Traveltime_m_At_15h40m00s" or i == "Traveltime_m_At_15h50m00s" or i == "Traveltime_m_At_16h00m00s" or i == "Traveltime_m_At_16h10m00s" or i == "Traveltime_m_At_16h20m00s" or i == "Traveltime_m_At_16h30m00s" or i == "Traveltime_m_At_16h40m00s" or i == "Traveltime_m_At_16h50m00s" or i == "Traveltime_m_At_21h00m00s" or i == "Traveltime_m_At_21h10m00s" or i == "Traveltime_m_At_21h20m00s" or i == "Traveltime_m_At_21h30m00s" or i == "Traveltime_m_At_21h40m00s" or i == "Traveltime_m_At_21h50m00s" or i == "Traveltime_m_At_22h00m00s" or i == "Traveltime_m_At_22h10m00s" or i == "Traveltime_m_At_22h20m00s" or i == "Traveltime_m_At_22h30m00s" or i == "Traveltime_m_At_22h40m00s" or i == "Traveltime_m_At_22h50m00s" or i == "Traveltime_m_At_07h05m00s" or i == "Traveltime_m_At_07h15m00s" or i == "Traveltime_m_At_07h25m00s" or i == "Traveltime_m_At_07h35m00s" or i == "Traveltime_m_At_07h45m00s" or i == "Traveltime_m_At_07h55m00s" or i == "Traveltime_m_At_08h05m00s" or i == "Traveltime_m_At_08h15m00s" or i == "Traveltime_m_At_08h25m00s" or i == "Traveltime_m_At_08h35m00s" or i == "Traveltime_m_At_08h45m00s" or i == "Traveltime_m_At_08h55m00s" or i == "Traveltime_m_At_15h05m00s" or i == "Traveltime_m_At_15h15m00s" or i == "Traveltime_m_At_15h25m00s" or i == "Traveltime_m_At_15h35m00s" or i == "Traveltime_m_At_15h45m00s" or i == "Traveltime_m_At_15h55m00s" or i == "Traveltime_m_At_16h05m00s" or i == "Traveltime_m_At_16h15m00s" or i == "Traveltime_m_At_16h25m00s" or i == "Traveltime_m_At_16h35m00s" or i == "Traveltime_m_At_16h45m00s" or i == "Traveltime_m_At_16h55m00s" or i == "Traveltime_m_At_21h05m00s" or i == "Traveltime_m_At_21h15m00s" or i == "Traveltime_m_At_21h25m00s" or i == "Traveltime_m_At_21h35m00s" or i == "Traveltime_m_At_21h45m00s" or i == "Traveltime_m_At_21h55m00s" or i == "Traveltime_m_At_22h05m00s" or i == "Traveltime_m_At_22h15m00s" or i == "Traveltime_m_At_22h25m00s" or i == "Traveltime_m_At_22h35m00s" or i == "Traveltime_m_At_22h45m00s" or i == "Traveltime_m_At_22h55m00s" or i == "count_1x_07" or i == "count_1x_08" or i == "count_1x_15" or i == "count_1x_16" or i == "count_1x_21" or i == "count_1x_22" or i == "max_1x_pu_0708" or i == "max_1x_pu_1516" or i == "max_1x_pu_2122" or i == "ModeUsed_At_07h00m00s" or i == "ModeUsed_At_07h10m00s" or i == "ModeUsed_At_07h20m00s" or i == "ModeUsed_At_07h30m00s" or i == "ModeUsed_At_07h40m00s" or i == "ModeUsed_At_07h50m00s" or i == "ModeUsed_At_08h00m00s" or i == "ModeUsed_At_08h10m00s" or i == "ModeUsed_At_08h20m00s" or i == "ModeUsed_At_08h30m00s" or i == "ModeUsed_At_08h40m00s" or i == "ModeUsed_At_08h50m00s" or i == "ModeUsed_At_15h00m00s" or i == "ModeUsed_At_15h10m00s" or i == "ModeUsed_At_15h20m00s" or i == "ModeUsed_At_15h30m00s" or i == "ModeUsed_At_15h40m00s" or i == "ModeUsed_At_15h50m00s" or i == "ModeUsed_At_16h00m00s" or i == "ModeUsed_At_16h10m00s" or i == "ModeUsed_At_16h20m00s" or i == "ModeUsed_At_16h30m00s" or i == "ModeUsed_At_16h40m00s" or i == "ModeUsed_At_16h50m00s" or i == "ModeUsed_At_21h00m00s" or i == "ModeUsed_At_21h10m00s" or i == "ModeUsed_At_21h20m00s" or i == "ModeUsed_At_21h30m00s" or i == "ModeUsed_At_21h40m00s" or i == "ModeUsed_At_21h50m00s" or i == "ModeUsed_At_22h00m00s" or i == "ModeUsed_At_22h10m00s" or i == "ModeUsed_At_22h20m00s" or i == "ModeUsed_At_22h30m00s" or i == "ModeUsed_At_22h40m00s" or i == "ModeUsed_At_22h50m00s" or i == "ModeUsed_At_07h05m00s" or i == "Key" or i == "ModeUsed_At_07h15m00s" or i == "ModeUsed_At_07h25m00s" or i == "ModeUsed_At_07h35m00s" or i == "ModeUsed_At_07h45m00s" or i == "ModeUsed_At_07h55m00s" or i == "ModeUsed_At_08h05m00s" or i == "ModeUsed_At_08h15m00s" or i == "ModeUsed_At_08h25m00s" or i == "ModeUsed_At_08h35m00s" or i == "ModeUsed_At_08h45m00s" or i == "ModeUsed_At_08h55m00s" or i == "ModeUsed_At_15h05m00s" or i == "ModeUsed_At_15h15m00s" or i == "ModeUsed_At_15h25m00s" or i == "ModeUsed_At_15h35m00s" or i == "ModeUsed_At_15h45m00s" or i == "ModeUsed_At_15h55m00s" or i == "ModeUsed_At_16h05m00s" or i == "ModeUsed_At_16h15m00s" or i == "ModeUsed_At_16h25m00s" or i == "ModeUsed_At_16h35m00s" or i == "ModeUsed_At_16h45m00s" or i == "ModeUsed_At_16h55m00s" or i == "ModeUsed_At_21h05m00s" or i == "ModeUsed_At_21h15m00s" or i == "ModeUsed_At_21h25m00s" or i == "ModeUsed_At_21h35m00s" or i == "ModeUsed_At_21h45m00s" or i == "ModeUsed_At_21h55m00s" or i == "ModeUsed_At_22h05m00s" or i == "ModeUsed_At_22h15m00s" or i == "ModeUsed_At_22h25m00s" or i == "ModeUsed_At_22h35m00s" or i == "ModeUsed_At_22h45m00s" or i == "ModeUsed_At_22h55m00s":
        next
    else:
        columns.append(i)

# Vaststellen tijdstippen
categories = [15, 30, 45, 60]

for column in columns:
    csv_out_file = os.path.join(y_out, input_files_dir[0]).replace("-", "_").replace(".csv", "_" + column + "_" + "cnt.csv").replace("Median_TT", "med").replace("_07h_", "7").replace("_15h_", "15").replace("_23h_", "23").replace("Dep_07h00m_", "")
    fgdb_table_out_file = os.path.join(fgdb_out, "table_").replace("table_", "table_" + run+"_"+wachttijd+"_"+walkbike+"_"+gem_hour+subset + "_" + column + "_med_cnt")
    fgdb_table_out_filename = fgdb_table_out_file.split("\\")[-1]
    fgdb_polygon_out_file = os.path.join(fgdb_out, "polygons_").replace("polygons_", "polygons_" + run+"_"+wachttijd+"_"+walkbike+"_"+gem_hour+subset + "_" + column + "_med_cnt")

    print(column)

    df2 = data.copy(deep=True)

    print(len(df2))
    
    # in onderstaande actie wordt -99999 uit de kolommen gefilterd
    if column == "Median_TT_0708h":
        df2 = df2.loc[df2.max_1x_pu_0708 <> 1]
        print("Selecteren {} records uit {}".format(len(df2), column))
    if column == "Median_TT_1516h":
        df2 = df2.loc[df2.max_1x_pu_1516 <> 1]
        print("Selecteren {} records uit {}".format(len(df2), column))
    if column == "Median_TT_2122h":
        df2 = df2.loc[df2.max_1x_pu_2122 <> 1]
        print("Selecteren {} records uit {}".format(len(df2), column))

#     for item in ["count_1x_07", "count_1x_08", "count_1x_15", "count_1x_16", "count_1x_21", "count_1x_22"]:
#         if item in df2.columns:
#             df2[item].replace({0:0, 2:0, 3:0, 4:0, 5:0, 6:0}, inplace=True)
                                                    
    column_list = []
    
    for col in df2.columns:
#         print(col)
        if "Traveltime" in col:
            del df2[col]
        elif "Key" in col:
            del df2[col]
        else:
            next
    for minute in categories:
        column_cat = "Score_lt" + str(minute) + "min"
        column_list.append(column_cat)
        print('Toevoegen kolom {}'.format(column_cat))
        df2[column_cat] = 1
        df2[column_cat].where(df2[column] < minute, 0, inplace=True)
        df2[column_cat] = np.where(df2[column] < 0, 0, df2[column_cat])

    group_data = df2.groupby(["OrgName"])[column_list].sum().reset_index()
    group_data = pd.merge(region_code, group_data, on='OrgName', how='left')
    group_data = group_data.fillna(0)
    print(len(group_data))
    for i in column_list:
        print("Maximum {}: {}".format(i, group_data[i].max()))

    # hier de tabel exporteren naar de fgdb
    arcpy.env.overwriteOutput = True
    
    # exporteren csv
    print("{} :  Start exporteren csv.".format(strftime("%d-%m-%Y %H:%M:%S")))
    if os.path.exists(csv_out_file):
        print("Csv is al eerder opgeslagen. Dateframe is niet opnieuw geexporteerd.")
    else:
        group_data.to_csv (csv_out_file, index = None, header=True, sep=";", decimal=",")
        print("{} :  Exporteren voltooid".format(strftime("%d-%m-%Y %H:%M:%S")))

    # conversie zojuist opgeslagen csv naar fgdb-table
    arcpy.env.overwriteOutput = True

    try:
        arcpy.TableToTable_conversion(csv_out_file, fgdb_out, fgdb_table_out_filename)
#         arcpy.CopyFeatures_management(feature_layer_joined, featureclass_name)
        print("{} :  Export tabel naar fgdb voltooid.".format(strftime("%d-%m-%Y %H:%M:%S")))

    except:
        print("{} :  Exporteren tabel naar fgdb niet voltooid.".format(strftime("%d-%m-%Y %H:%M:%S")))
    
    # exporteren fgdb-polygons
    try:
        feature_layer = arcpy.MakeFeatureLayer_management(polygons, "polygons")
        feature_layer_joined = arcpy.AddJoin_management(feature_layer, "BU_CODE", fgdb_table_out_file, "OrgName")
        arcpy.CopyFeatures_management(feature_layer_joined, fgdb_polygon_out_file)
#         arcpy.CopyFeatures_management(polygons, fgdb_polygon_out_file)
        print("{} :  Export polygons naar fgdb voltooid.".format(strftime("%d-%m-%Y %H:%M:%S")))

    except:
        print("{} :  Exporteren polygons naar fgdb niet voltooid.".format(strftime("%d-%m-%Y %H:%M:%S")))
    
    ### printen van aantal inwoners per categorie
    # 1) Inwonersbestand inlezen (minimaal kolommen: buurtcode, aantal_inw)
    inw_2022 = pd.read_csv(r"c:\RN\brt2023.txt", sep=";")

    # 2) Mergen op buurtcode -> in jouw group_data heet dit 'OrgName'
    group_data_inw = group_data.merge(inw_2022, left_on="OrgName", right_on="buurtcode", how="left")

    # 3) Zorg dat de scorekolommen numeriek zijn (veiligheidshalve) en vervang NaN door 0
    score_kolommen = ["Score_lt15min", "Score_lt30min", "Score_lt45min", "Score_lt60min"]
    for c in score_kolommen:
        group_data_inw[c] = pd.to_numeric(group_data_inw[c], errors="coerce").fillna(0)

    # 4) Zorg dat aantal_inw numeriek is (en NaN -> 0)
    group_data_inw["aantal_inw"] = pd.to_numeric(group_data_inw["aantal_inw"], errors="coerce").fillna(0).astype(np.int64)

    # 5) Labels per drempel
    kolommen = {
        "Score_lt15min": "binnen 15 minuten",
        "Score_lt30min": "binnen 30 minuten",
        "Score_lt45min": "binnen 45 minuten",
        "Score_lt60min": "binnen 60 minuten"
    }

    # 6) Categorisatiefunctie: 0, 1, 2, 3, 3+ voorzieningen
    def categorize(n):
        try:
            n_int = int(n)
        except:
            n_int = 0
        if n_int == 0:
            return "0 voorzieningen"
        elif n_int == 1:
            return "1 voorziening"
        elif n_int == 2:
            return "2 voorzieningen"
        elif n_int >= 3:
            return "3 of meer voorzieningen"
        else:
            return "overig"

    cat_order = ["0 voorzieningen", "1 voorziening", "2 voorzieningen", "3 of meer voorzieningen"]

    # 8) Loop door drempels en print resultaten
    #    We verzamelen ook alles in 'totaal_dict' om op het eind één tabel te kunnen tonen.
    totaal_dict = {}

    for col, label in kolommen.iteritems():
        group_data_inw["voorzieningen"] = group_data_inw[col]
        group_data_inw["categorie"] = group_data_inw["voorzieningen"].apply(categorize)

        result = group_data_inw.groupby("categorie")["aantal_inw"].sum().reindex(cat_order, fill_value=0)

        # Bewaar voor eindtabel
        totaal_dict[label] = result

    # 9) (Optioneel) Eindtabel met alle drempels naast elkaar
    #    Handig als je alles in één oogopslag wilt vergelijken.
    try:
        eindtabel = pd.DataFrame(totaal_dict)
        # Zorg dat de rijen in vaste volgorde staan
        eindtabel = eindtabel.reindex(cat_order)
        print "\nOverzichtstabel (rijen = categorieën, kolommen = tijdsdrempels):"
        print eindtabel
        print("="*80)
    except Exception as e:
        # Als er iets misgaat met het bouwen van de eindtabel, print dan de fout maar ga verder.
        print "\nKon geen overzichtstabel maken vanwege fout: {}".format(e)    

print("Klaar!")


# Vaststellen tijdstippen
categories = [15, 30, 45, 60]

for column in columns:
    csv_out_file = os.path.join(y_out, input_files_dir[0]).replace("-", "_").replace(".csv", "_" + column + "_" + "cnt.csv").replace("Median_TT", "med").replace("_07h_", "7").replace("_15h_", "15").replace("_23h_", "23").replace("Dep_07h00m_", "")
    fgdb_table_out_file = os.path.join(fgdb_out, "table_").replace("table_", "table_" + run+"_"+wachttijd+"_"+walkbike+"_"+gem_hour+subset + "_" + column + "_med_cnt")
    fgdb_table_out_filename = fgdb_table_out_file.split("\\")[-1]
    fgdb_polygon_out_file = os.path.join(fgdb_out, "polygons_").replace("polygons_", "polygons_" + run+"_"+wachttijd+"_"+walkbike+"_"+gem_hour+subset + "_" + column + "_med_cnt")

    print(column)

    df2 = data.copy(deep=True)

    print(len(df2))
    
    # in onderstaande actie wordt -99999 uit de kolommen gefilterd
    if column == "Median_TT_0708h":
        df2 = df2.loc[df2.max_1x_pu_0708 <> 1]
        print("Selecteren {} records uit {}".format(len(df2), column))
    if column == "Median_TT_1516h":
        df2 = df2.loc[df2.max_1x_pu_1516 <> 1]
        print("Selecteren {} records uit {}".format(len(df2), column))
    if column == "Median_TT_2122h":
        df2 = df2.loc[df2.max_1x_pu_2122 <> 1]
        print("Selecteren {} records uit {}".format(len(df2), column))

    column_list = []
    
    for col in df2.columns:
#         print(col)
        if "Traveltime" in col:
            del df2[col]
        elif "Key" in col:
            del df2[col]
        else:
            next
    for minute in categories:
        column_cat = "Score_lt" + str(minute) + "min"
        column_list.append(column_cat)
        print('Toevoegen kolom {}'.format(column_cat))
        df2[column_cat] = 1
        df2[column_cat].where(df2[column] < minute, 0, inplace=True)
        df2[column_cat] = np.where(df2[column] < 0, 0, df2[column_cat])

    group_data = df2.groupby(["OrgName"])[column_list].sum().reset_index()
    group_data = pd.merge(region_code, group_data, on='OrgName', how='left')
    group_data = group_data.fillna(0)
    print(len(group_data))
    for i in column_list:
        print("Maximum {}: {}".format(i, group_data[i].max()))

    # hier de tabel exporteren naar de fgdb
    arcpy.env.overwriteOutput = True
    
    # exporteren csv
    print("{} :  Start exporteren csv.".format(strftime("%d-%m-%Y %H:%M:%S")))
    if os.path.exists(csv_out_file):
        print("Csv is al eerder opgeslagen. Dateframe is niet opnieuw geexporteerd.")
    else:
        group_data.to_csv (csv_out_file, index = None, header=True, sep=";", decimal=",")
        print("{} :  Exporteren voltooid".format(strftime("%d-%m-%Y %H:%M:%S")))

    # conversie zojuist opgeslagen csv naar fgdb-table
    arcpy.env.overwriteOutput = True

    try:
        arcpy.TableToTable_conversion(csv_out_file, fgdb_out, fgdb_table_out_filename)
#         arcpy.CopyFeatures_management(feature_layer_joined, featureclass_name)
        print("{} :  Export tabel naar fgdb voltooid.".format(strftime("%d-%m-%Y %H:%M:%S")))

    except:
        print("{} :  Exporteren tabel naar fgdb niet voltooid.".format(strftime("%d-%m-%Y %H:%M:%S")))
    
    # exporteren fgdb-polygons
    try:
        feature_layer = arcpy.MakeFeatureLayer_management(polygons, "polygons")
        feature_layer_joined = arcpy.AddJoin_management(feature_layer, "BU_CODE", fgdb_table_out_file, "OrgName")
        arcpy.CopyFeatures_management(feature_layer_joined, fgdb_polygon_out_file)
#         arcpy.CopyFeatures_management(polygons, fgdb_polygon_out_file)
        print("{} :  Export polygons naar fgdb voltooid.".format(strftime("%d-%m-%Y %H:%M:%S")))

    except:
        print("{} :  Exporteren polygons naar fgdb niet voltooid.".format(strftime("%d-%m-%Y %H:%M:%S")))
    
    ### printen van aantal inwoners per categorie
    # 1) Inwonersbestand inlezen (minimaal kolommen: buurtcode, aantal_inw)
    inw_2022 = pd.read_csv(r"c:\RN\brt2022.txt", sep=";")

    # 2) Mergen op buurtcode -> in jouw group_data heet dit 'OrgName'
    group_data_inw = group_data.merge(inw_2022, left_on="OrgName", right_on="buurtcode", how="left")

    # 3) Zorg dat de scorekolommen numeriek zijn (veiligheidshalve) en vervang NaN door 0
    score_kolommen = ["Score_lt15min", "Score_lt30min", "Score_lt45min", "Score_lt60min"]
    for c in score_kolommen:
        group_data_inw[c] = pd.to_numeric(group_data_inw[c], errors="coerce").fillna(0)

    # 4) Zorg dat aantal_inw numeriek is (en NaN -> 0)
    group_data_inw["aantal_inw"] = pd.to_numeric(group_data_inw["aantal_inw"], errors="coerce").fillna(0).astype(np.int64)

    # 5) Labels per drempel
    kolommen = {
        "Score_lt15min": "binnen 15 minuten",
        "Score_lt30min": "binnen 30 minuten",
        "Score_lt45min": "binnen 45 minuten",
        "Score_lt60min": "binnen 60 minuten"
    }

    # 6) Categorisatiefunctie: 0, 1, 2, 3, 3+ voorzieningen
    def categorize(n):
        try:
            n_int = int(n)
        except:
            n_int = 0
        if n_int == 0:
            return "0 voorzieningen"
        elif n_int == 1:
            return "1 voorziening"
        elif n_int == 2:
            return "2 voorzieningen"
        elif n_int >= 3:
            return "3 of meer voorzieningen"
        else:
            return "overig"

    cat_order = ["0 voorzieningen", "1 voorziening", "2 voorzieningen", "3 of meer voorzieningen"]

    # 8) Loop door drempels en print resultaten
    #    We verzamelen ook alles in 'totaal_dict' om op het eind één tabel te kunnen tonen.
    totaal_dict = {}

    for col, label in kolommen.iteritems():
        group_data_inw["voorzieningen"] = group_data_inw[col]
        group_data_inw["categorie"] = group_data_inw["voorzieningen"].apply(categorize)

        result = group_data_inw.groupby("categorie")["aantal_inw"].sum().reindex(cat_order, fill_value=0)

        # Bewaar voor eindtabel
        totaal_dict[label] = result

    # 9) (Optioneel) Eindtabel met alle drempels naast elkaar
    #    Handig als je alles in één oogopslag wilt vergelijken.
    try:
        eindtabel = pd.DataFrame(totaal_dict)
        # Zorg dat de rijen in vaste volgorde staan
        eindtabel = eindtabel.reindex(cat_order)
        print "\nOverzichtstabel (rijen = categorieën, kolommen = tijdsdrempels):"
        print eindtabel
        print("="*80)
    except Exception as e:
        # Als er iets misgaat met het bouwen van de eindtabel, print dan de fout maar ga verder.
        print "\nKon geen overzichtstabel maken vanwege fout: {}".format(e)    

print("Klaar!")