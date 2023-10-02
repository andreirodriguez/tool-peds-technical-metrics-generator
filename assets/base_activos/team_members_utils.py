import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import assets.base_activos.utils as utils
import assets.base_activos.constants as constants

def getValidationTeamMembers(base:pd.DataFrame,team_members_prs:pd.DataFrame)->pd.DataFrame:

    print("Realizo las validaciones de los team members en la base de activos")

    base["is_observed_squad_code"] = base.apply(lambda record: getObservedSquadCode(record["squad_code"]),axis=1)    
    base["is_observed_specialty"] = base.apply(lambda record: getObservedSpecialty(record["especialidad"]),axis=1)
    base["is_observed_pullrequest"] = False

    team_members_prs = team_members_prs[~team_members_prs['matricula'].isin([base["matricula"].unique()])]
    team_members_prs["is_observed_pullrequest"] = True

    base = pd.concat([base, team_members_prs], ignore_index=True)        

    base["observed_comments"] = base.apply(lambda record: getObservedComments(record),axis=1)

    base = base.sort_values(['matricula'], ascending = [True])

    base = base[(base['observed_comments']!="")]

    return base

def getObservedSpecialty(specialty:str)->bool:
    return utils.isNullOrEmpty(specialty)

def getObservedSquadCode(squad_code:str)->bool:
    return utils.isNullOrEmpty(squad_code)

def getObservedComments(squad)->str:
    comment:str = ""

    if(squad["is_observed_squad_code"]):
        comment = " No tiene código de squad."

    if(squad["is_observed_specialty"]):
        comment = " No tiene especialidad."        

    if(squad["is_observed_pullrequest"]):
        comment = " No existe en la base de activos."          

    return comment.strip()

def setExcelReport(team_members:pd.DataFrame):
    file = utils.getPathDirectory("output\\team_members_observed.xlsx")
    columns = ["matricula","nombre","apellido_paterno","apellido_materno","correo","tribu_code","tribu","squad_code","squad","rol","rol_insourcing","especialidad","nombre_cal","matricula_cl","nombre_cl","tipo_contratacion","empresa","flag_activo","fecha_actualizado","observed_comments"]

    print("Exporto archivo de validaciones de base de activos: " + file)

    team_members.to_excel(file,sheet_name="Data",columns=columns,index=False)