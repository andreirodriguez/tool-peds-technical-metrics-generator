import pandas as pd
import re

OUTPUT_DIFFERENCES_FILE = "util/files/Diferencias.xlsx"
PRIORITIZED_FILE = "util/files/squads_priorizados.xlsx"
SIGA_FILE = "util/files/siga.xlsx"
NEW_PRIORITIZED_FILE = "util/files/squads_priorizados_new.xlsx"

def extract_squad_tribe_id(large_name):
    large_name = str(large_name)
    match_expr = re.search('\[(.+?)\]', large_name)

    if match_expr == None:
        match_expr = re.search('\((.+?)\)', large_name)
    
    if match_expr:
        return match_expr.group(1)
    else:
        return ''
    
def take_previous_value(squad, column, previous_value):
    squad.fillna("", inplace=True)
    if squad[column] == "":
        squad[column] = squad[previous_value]
    return squad[column]
    
prioritized_general = pd.read_excel(PRIORITIZED_FILE, sheet_name = "GENERAL")
prioritized_java = pd.read_excel(PRIORITIZED_FILE, sheet_name = "BACKEND JAVA")
prioritized_web = pd.read_excel(PRIORITIZED_FILE, sheet_name = "FRONTEND WEB")
prioritized_android = pd.read_excel(PRIORITIZED_FILE, sheet_name = "FRONTEND ANDROID")
prioritized_ios = pd.read_excel(PRIORITIZED_FILE, sheet_name = "FRONTEND IOS")

siga = pd.read_excel(SIGA_FILE, sheet_name = "ARBOL", dtype={"HIJO": str, "PADRE": str})

prioritized_general =prioritized_general[prioritized_general["Squad"] == "lupe"]

prioritized_general["code_squad"] = prioritized_general.apply(lambda pr: extract_squad_tribe_id(pr["Squad"]), axis=1)
prioritized_general["code_tribe_cmt"] = prioritized_general.apply(lambda pr: extract_squad_tribe_id(pr["Tribu"]), axis=1)
siga = siga.rename(columns={'HIJO': 'code_squad'})
siga = siga.rename(columns={'PADRE': 'code_tribe_siga'})
siga = siga.rename(columns={'DESCRIPCION_HIJO': 'squad'})
siga = siga.rename(columns={'DESCRIPCION_PADRE': 'tribe'})
siga["squad_code_siga"] = siga.apply(lambda pr: pr["squad"] + " [" + pr["code_squad"] + "]", axis=1)
siga["tribu_code_siga"] = siga.apply(lambda pr: pr["tribe"] + " [" + pr["code_tribe_siga"] + "]", axis=1)

# Get general resume information about squads
new_prioritized_general = pd.merge(prioritized_general, siga[['squad_code_siga', 'code_squad', 'tribu_code_siga','code_tribe_siga','squad','tribe']], on="code_squad", how="left")
new_prioritized_general["is_squad_equal"] = new_prioritized_general.apply(lambda pr: pr["Squad"] == pr["squad_code_siga"], axis=1)
new_prioritized_general["is_tribe_equal"] = new_prioritized_general.apply(lambda pr: pr["Tribu"] == pr["tribu_code_siga"], axis=1)
new_prioritized_general["is_cod_tribe_equal"] = new_prioritized_general.apply(lambda pr: pr["code_tribe_cmt"] == pr["code_tribe_siga"], axis=1)

new_prioritized_general.to_excel(OUTPUT_DIFFERENCES_FILE,index=False, 
                                 columns= ['Tribu','Squad',	'Grupo', 'CMT',	'code_squad', 'code_tribe_cmt', 'squad_code_siga', 'tribu_code_siga', 'code_tribe_siga', 'is_squad_equal', 'is_tribe_equal', 'is_cod_tribe_equal'])

# Make file that is use in technical metrics generations
prioritized_java["code_squad"] = prioritized_java.apply(lambda squad: extract_squad_tribe_id(squad["Squad"]), axis=1)
prioritized_web["code_squad"] = prioritized_web.apply(lambda squad: extract_squad_tribe_id(squad["Squad"]), axis=1)
prioritized_android["code_squad"] = prioritized_android.apply(lambda squad: extract_squad_tribe_id(squad["Squad"]), axis=1)
prioritized_ios["code_squad"] = prioritized_ios.apply(lambda squad: extract_squad_tribe_id(squad["Squad"]), axis=1)

new_prioritized_java = pd.merge(prioritized_java, siga[['squad_code_siga', 'code_squad', 'tribu_code_siga']], on="code_squad", how="left")
new_prioritized_web = pd.merge(prioritized_web, siga[['squad_code_siga', 'code_squad', 'tribu_code_siga']], on="code_squad", how="left")
new_prioritized_android = pd.merge(prioritized_android, siga[['squad_code_siga', 'code_squad', 'tribu_code_siga']], on="code_squad", how="left")
new_prioritized_ios = pd.merge(prioritized_ios, siga[['squad_code_siga', 'code_squad', 'tribu_code_siga']], on="code_squad", how="left")

new_prioritized_general["squad_code_siga"] = new_prioritized_general.apply(lambda squad: take_previous_value(squad,"squad_code_siga","Squad"), axis=1)
new_prioritized_general["tribu_code_siga"] = new_prioritized_general.apply(lambda squad: take_previous_value(squad,"tribu_code_siga","Tribu"), axis=1)

new_prioritized_java["squad_code_siga"] = new_prioritized_java.apply(lambda squad: take_previous_value(squad,"squad_code_siga","Squad"), axis=1)
new_prioritized_java["tribu_code_siga"] = new_prioritized_java.apply(lambda squad: take_previous_value(squad,"tribu_code_siga","Tribu"), axis=1)

new_prioritized_web["squad_code_siga"] = new_prioritized_web.apply(lambda squad: take_previous_value(squad,"squad_code_siga","Squad"), axis=1)
new_prioritized_web["tribu_code_siga"] = new_prioritized_web.apply(lambda squad: take_previous_value(squad,"tribu_code_siga","Tribu"), axis=1)

new_prioritized_android["squad_code_siga"] = new_prioritized_android.apply(lambda squad: take_previous_value(squad,"squad_code_siga","Squad"), axis=1)
new_prioritized_android["tribu_code_siga"] = new_prioritized_android.apply(lambda squad: take_previous_value(squad,"tribu_code_siga","Tribu"), axis=1)

new_prioritized_ios["squad_code_siga"] = new_prioritized_ios.apply(lambda squad: take_previous_value(squad,"squad_code_siga","Squad"), axis=1)
new_prioritized_ios["tribu_code_siga"] = new_prioritized_ios.apply(lambda squad: take_previous_value(squad,"tribu_code_siga","Tribu"), axis=1)

with pd.ExcelWriter(NEW_PRIORITIZED_FILE) as writer:
    new_prioritized_general.to_excel(writer, sheet_name="GENERAL", index=False,columns=["tribu_code_siga","squad_code_siga","Grupo","CMT"],header=["Tribu","Squad","Grupo","CMT"])
    new_prioritized_java.to_excel(writer, sheet_name="BACKEND JAVA", index=False,columns=["tribu_code_siga","squad_code_siga","Grupo","CMT"],header=["Tribu","Squad","Grupo","CMT"])
    new_prioritized_web.to_excel(writer, sheet_name="FRONTEND WEB", index=False,columns=["tribu_code_siga","squad_code_siga","Grupo","CMT"],header=["Tribu","Squad","Grupo","CMT"])
    new_prioritized_android.to_excel(writer, sheet_name="FRONTEND IOS", index=False,columns=["tribu_code_siga","squad_code_siga","Grupo","CMT"],header=["Tribu","Squad","Grupo","CMT"])
    new_prioritized_ios.to_excel(writer, sheet_name="FRONTEND ANDROID", index=False,columns=["tribu_code_siga","squad_code_siga","Grupo","CMT"],header=["Tribu","Squad","Grupo","CMT"])
 
# Make file for data analytics
# squads_for_dashboard = pd.read_excel("util/files/tribe_squad_old.xlsx", dtype={"tribe_code": str, "squad_code": str})
# squads_for_dashboard = squads_for_dashboard[squads_for_dashboard["status"] == 0 | squads_for_dashboard["squad_code"].str.upper().str.endswith('X')]
# new_prioritized_general = new_prioritized_general.rename(columns={'code_tribe_siga': 'tribe_code'})
# new_prioritized_general = new_prioritized_general.rename(columns={'code_squad': 'squad_code'})
# new_prioritized_general["status"] = 1

# file_for_dashboard = pd.concat([squads_for_dashboard, new_prioritized_general], ignore_index=True)

# file_for_dashboard.to_excel("util/files/tribe_squad_new.xlsx",index=False,columns=['tribe_code','tribe','squad_code','squad','status'])
