import pandas as pd
from typing import List
from unittesting.utils import getPathDirectory,getCodeSquadTribe

PATH = "input/ut/squads-priorizados.xlsx"

def get_prioritized_squads():
    result = pd.read_excel(PATH, index_col=0)
    return result["squad"].astype(str).values.tolist()

def getPrioritizedSquads(speciality:str):
    file = "squads_priorizados.xlsx"

    print("Leo lista de squads priorizados de la especialidad: " + speciality)

    file = getPathDirectory("input\\squads_priorizados\\" + file)

    xlsSquads = pd.read_excel(file,usecols=[0,1,2,3],names=["tribe","squad","grupo","cmt"],sheet_name=speciality)

    xlsSquads["squad_code"] = xlsSquads.apply(lambda squad: getCodeSquadTribe(squad["squad"]),axis=1)
    xlsSquads["tribe_code"] = xlsSquads.apply(lambda squad: getCodeSquadTribe(squad["tribe"]),axis=1)

    return xlsSquads

def getValueBySquad(squadCode:str,squads:pd.DataFrame,property:str,originalValue:str):
    squad = squads[(squads['squad_code']==squadCode)]

    if(len(squad)==0): return originalValue

    value = squad.iloc[0][property]

    return value
    


