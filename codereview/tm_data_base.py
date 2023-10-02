import pandas as pd
from codereview.cr_constants import BASE_FILE
from codereview.util import get_team_member_id_without_zero, extract_squad_tribe_id

def getBaseActivos():
    print("Getting data base of team members")

    base_result = pd.read_excel(BASE_FILE, 
                                usecols=["matricula","squad","tribu","especialidad", "apellido_paterno", "apellido_materno","nombre","squad","tribu_code","squad_code","cod_app","fecha_actualizado"],
                                sheet_name=0)
    
    new_column_names = {"matricula": "team_member_code", "tribu": "tribe", "tribu_code":"tribe_code", "especialidad": "specialty",
                         "apellido_paterno" : "paternal_surname", "apellido_materno" : "maternal_surname", "nombre": "name"}
    base_result = base_result.rename(columns=new_column_names)
    base_result.fillna("", inplace=True)
    base_result["fullname"] = base_result.apply(
        lambda teamMember: teamMember["name"].upper() + " " +  teamMember["paternal_surname"].upper() + " " + teamMember["maternal_surname"].upper() , axis=1)

    return base_result

def getValueBaseActivosByTeamMember(teamMemberCode:str, baseActivos:pd.DataFrame, property:str, originalValue:str):

    teamMember = baseActivos[(baseActivos['team_member_code'] == teamMemberCode)]

    if(len(teamMember) == 0): return originalValue

    value = teamMember.iloc[0][property]

    if(not str(value)): return originalValue

    if((property=="specialty") & (("IOS" in originalValue) | ("ANDROID" in originalValue))):
        return originalValue
    
    return value

def get_squad_of_team_member(team_member_code, app, base, column_name):
    base_tm = base[base["team_member_code"] == team_member_code]
    base_tm_app = base[(base["team_member_code"] == team_member_code) & (base["cod_app"] == app)]
    if len(base_tm_app) == 1:
        value = base_tm_app.iloc[0][column_name]
    elif len(base_tm) == 0:
        value = ""
    else:
        base_tm = base_tm.sort_values(['team_member_code','squad','fecha_actualizado'], ascending = [True,True,False])
        value = base_tm.iloc[0][column_name]
    return value