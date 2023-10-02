import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import assets.base_activos.utils as utils
import assets.base_activos.constants as constants

def getSquadsPriorizados(specialty:str)->pd.DataFrame:
    file = "squads_priorizados.xlsx"

    print("Leo los squads priorizados de: " + specialty)

    file = utils.getPathDirectory("input\\squads_priorizados\\" + file)

    squads = pd.read_excel(file,usecols=["Tribu","Squad","Grupo","CMT"],sheet_name=specialty)
    squads = squads.astype(object).where(pd.notnull(squads),None)

    squads = squads.rename(columns= {"Tribu": "tribu", 
                    "Squad": "squad",
                    "Grupo": "grupo",
                    "CMT": "cmt",
                    })
    
    squads['tribu'] = squads['tribu'].apply(lambda value: utils.getStringUpperStrip(value))
    squads['squad'] = squads['squad'].apply(lambda value: utils.getStringUpperStrip(value))

    squads["squad_code"] = squads.apply(lambda pr: utils.getCodeSquadTribe(pr["squad"]),axis=1)
    squads["tribu_code"] = squads.apply(lambda pr: utils.getCodeSquadTribe(pr["tribu"]),axis=1)

    return squads

def getValidationSquads(base:pd.DataFrame)->any:
    squadsArray = []

    for specialty in constants.SPECIALTYS_SCOPE:
        squadsArray.append(getValidationSquadsBySpecialty(specialty,base))

    return squadsArray

def getValidationSquadsBySpecialty(specialty:str,base:pd.DataFrame)->pd.DataFrame:
    squads:pd.DataFrame = getSquadsPriorizados(specialty)

    specialtys = []

    if(specialty==constants.SPECIALTY_GENERAL):
        specialtys = constants.SPECIALTYS_SCOPE_SEE.copy()
    else:
        specialtys.append(specialty)

    squads["is_observed_quantity_teammembers"] = squads.apply(lambda record: getObservedQuantityTeamMembers(record["squad_code"],specialtys,base),axis=1)
    squads["observed_comments"] = squads.apply(lambda record: getObservedComments(record),axis=1)

    squads = squads[(squads['observed_comments']!="")]

    return squads

def getObservedQuantityTeamMembers(squadCode:str,specialtys,base:pd.DataFrame)->bool:
    baseSquad = base[(base['squad_code']==squadCode)]

    baseSquad = baseSquad[(baseSquad['flag_activo'].isin(["ACTIVO COE",'NUEVO']))]
    baseSquad = baseSquad[(baseSquad['especialidad'].isin(specialtys))]

    quantityTeamMembers:int = len(baseSquad.index)

    return (quantityTeamMembers == 0)

def getObservedComments(squad)->str:
    comment:str = ""

    if(squad["is_observed_quantity_teammembers"]):
        comment = " No tiene team members en esta especialidad."

    return comment.strip()

def setExcelSummary(squadsArray:any):
    file = utils.getPathDirectory("output\\squads_observed.xlsx")
    columns = ["tribu_code","tribu","squad_code","squad","grupo","cmt","observed_comments"]
    
    print("Exporto archivo de validaciones de squads priorizados: " + file)

    with pd.ExcelWriter(file) as writer:
        countSquad:int = 0
        for specialty in constants.SPECIALTYS_SCOPE:
            squadsArray[countSquad].to_excel(writer,sheet_name=specialty,columns=columns, index=False)
            countSquad += 1


