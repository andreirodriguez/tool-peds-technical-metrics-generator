import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from quiztests_process.utils import getPathDirectory,getCodeSquadTribe,isNullOrEmpty
import quiztests_process.constants as constants

def getBaseActivos():
    file = "base_activos.xlsx"

    print("Leo base de datos de activos de team members: " + file)

    file = getPathDirectory("input\\base_activos\\" + file)

    base = pd.read_excel(file,usecols=["matricula","tribu","squad","squad_code","especialidad","flag_activo","correo","apellido_paterno","apellido_materno","nombre","nombre_cal","nombre_cl"],sheet_name=0)

    base = base.rename(columns={
        "matricula":"matricula",
        "tribu":"tribu",
        "squad":"squad",
        "squad_code":"squad_code",
        "especialidad":"especialidad",
        "flag_activo":"flag_activo",
        "correo":"correo",
        "apellido_paterno":"apellido_paterno",
        "apellido_materno":"apellido_materno",
        "nombre":"nombre",
        "nombre_cal":"nombre_cal",
        "nombre_cl":"nombre_cl"
    })

    base = base.astype(object).where(pd.notnull(base),None)

    base = base.sort_values(["matricula","squad_code"], ascending = [True, False])
    base = base.drop_duplicates(["matricula","squad_code"],keep='first')

    return base

def getMatriculaWithoutZero(codeTeamMember:str):
    if(isNullOrEmpty(codeTeamMember)): return ""

    codeTeamMember = codeTeamMember.upper().strip()

    firstZero = codeTeamMember[0:1]

    if(firstZero=="0"): codeTeamMember=codeTeamMember[1:len(codeTeamMember)]

    return codeTeamMember

def getValueBaseActivosByTeamMember(codeTeamMember:str,baseActivos:pd.DataFrame,property:str):
    teamMember = baseActivos[(baseActivos['matricula']==codeTeamMember)]

    if(len(teamMember)==0): return None

    value = teamMember.iloc[0][property]

    if(not str(value)): return None
    
    return value

def getSquadPriorizados(especialidad:str):
    file = "squads_priorizados.xlsx"
    
    print("Leo los squads priorizados del archivo: " + file)

    file = getPathDirectory("input\\squads_priorizados\\" + file)

    squads:pd.DataFrame = pd.read_excel(file,usecols=[1],names=["squad"],sheet_name=especialidad)

    squads["squad_code"] = squads.apply(lambda pr: getCodeSquadTribe(pr["squad"]),axis=1)

    return squads

def getBaseActivosPriorizada(especialidad,baseActivos:pd.DataFrame)->pd.DataFrame:
    squads = getSquadPriorizados(especialidad)
    
    especialidades = []

    if(especialidad==constants.SPECIALTY_GENERAL): 
        especialidades = constants.SPECIALTYS_SCOPE.copy()
    else: 
        especialidades.append(especialidad)

    base = baseActivos[(baseActivos['squad_code'].isin(squads["squad_code"].unique()))]

    base = base[(base['especialidad'].isin(especialidades))]

    return base

def getReportTeamMembersWithoutScore(especialidad,baseActivosPriorizada:pd.DataFrame,quizTests:pd.DataFrame)->pd.DataFrame:
    print("Leo los team members que no registraron cuestionario de la base de activos priorizada")

    quizTestsFinalizado = quizTests[(quizTests['state']==constants.STATE_FINALIZADO)]

    matriculas = quizTestsFinalizado["matricula"].unique()

    xlsReport = baseActivosPriorizada[~baseActivosPriorizada['matricula'].isin(matriculas)]

    if(not especialidad==constants.SPECIALTY_GENERAL):
        especialidades = []

        especialidades.append(especialidad)

        xlsReport = xlsReport[(xlsReport['especialidad'].isin(especialidades))]

    return xlsReport

def getReportSquadsWithoutScore(especialidad,quizTests:pd.DataFrame,baseActivosPriorizada:pd.DataFrame)->pd.DataFrame:
    print("Leo los squads a los cuales les falta score por especialidades")

    squads = getSquadPriorizados(especialidad)
    especialidades = []

    baseActivos = baseActivosPriorizada.filter(['matricula','tribu','squad','squad_code'], axis=1)
    quizTestTM = quizTests.merge(baseActivos, on='matricula')    

    if(especialidad==constants.SPECIALTY_GENERAL):
        especialidades = constants.SPECIALTYS_SCOPE.copy()
    else:
        especialidades.append(especialidad)

    for especialidad in especialidades:
        squadsEspecialidad = getSquadPriorizados(especialidad)

        squads[especialidad] = "SI"

        squads[especialidad] = squads.apply(lambda pr: getSpecialtysWithoutScore(pr["squad_code"],especialidad,squadsEspecialidad,quizTestTM),axis=1)

    return squads

def getSpecialtysWithoutScore(squadCode:str,especialidad:str,squadsEspecialidad:pd.DataFrame,quizTests:pd.DataFrame)->str:
    countTeamMembers = 0

    squadCount = squadsEspecialidad[squadsEspecialidad["squad_code"]==squadCode]

    if(len(squadCount)==0): return "SI"

    teamMembers = quizTests[(quizTests['squad_code']==squadCode) & (quizTests['especialidad']==especialidad)]

    countTeamMembers = len(teamMembers)

    if(countTeamMembers==0): return "NO"

    return "SI"


