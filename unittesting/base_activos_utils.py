import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from unittesting.utils import getPathDirectory,getCodeSquadTribe,isNullOrEmpty

def getBaseActivos():
    file = "base_activos.xlsx"

    print("Leo base de datos de activos de team members: " + file)

    file = getPathDirectory("input\\base_activos\\" + file)

    xlsBase = pd.read_excel(file,usecols=["matricula","squad","flag_activo","especialidad", "squad_code","cod_app","fecha_actualizado"],sheet_name=0)
    xlsBase = xlsBase[(xlsBase['flag_activo'].isin(['ACTIVO COE','NUEVO']))]

    return xlsBase

def getMatriculaWithoutZero(codeTeamMember:str):
    if(isNullOrEmpty(codeTeamMember)): return ""

    codeTeamMember = str(codeTeamMember).upper().strip()

    firstZero = codeTeamMember[0:1]

    if(firstZero=="0"): codeTeamMember=codeTeamMember[1:len(codeTeamMember)]

    return codeTeamMember

def getValueBaseActivosByTeamMember(codeTeamMember:str,baseActivos:pd.DataFrame,property:str,originalValue:str):
    codeTeamMember = codeTeamMember.upper().strip()

    teamMember = baseActivos[(baseActivos['matricula']==codeTeamMember)]

    if(len(teamMember)==0): return originalValue

    value = teamMember.iloc[0][property]

    if(not str(value)): return originalValue

    if((property=="especialidad") & (("IOS" in originalValue) | ("ANDROID" in originalValue))):
        return originalValue
    
    return value