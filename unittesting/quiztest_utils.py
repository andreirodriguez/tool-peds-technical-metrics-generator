import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import unittesting.constants as constants
from unittesting.utils import getPathDirectory,getCodeSquadTribe,setAnalysisExecutionDate,getFilesDirectory
from unittesting.base_activos_utils import getValueBaseActivosByTeamMember
from unittesting.maturity_points import get_quiz_test_points


def getQuizTestSpecialty(file,usecols,namecols)->pd.DataFrame:
    file = getPathDirectory("input\\quiz_tests\\" + file)

    xlsQuiz = pd.read_excel(file,usecols=usecols,names=namecols)

    return xlsQuiz

def getQuizTest()->pd.DataFrame:
    directory = "input\\quiz_tests\\"

    print("Leo los cuestionarios de los team members de la carpeta: " + directory)

    usecols=[0,1,2,3]
    names=["matricula","nombre","email","specialty"]

    count = 4
    for metric in constants.ARRAY_QUIZ_METRICS:
        usecols.append(count)
        names.append(metric)

        count += 1

    files = getFilesDirectory(directory)

    xlsConsolidated = pd.DataFrame({'matricula': [],'nombre': [],'email': [],'specialty': []})

    for file in files:
        if (file.endswith(".xlsx")==False): continue

        xlsQuiz = getQuizTestSpecialty(file,usecols,names)

        xlsConsolidated = pd.concat([xlsConsolidated, xlsQuiz], ignore_index=True)        

    xlsConsolidated["matricula"] = xlsConsolidated.apply(lambda q: str(q["matricula"]).upper(),axis=1)
    xlsConsolidated["specialty"] = xlsConsolidated.apply(lambda q: str(q["specialty"]).upper(),axis=1)

    return xlsConsolidated

def getQuizTestByTeamMember(quizTests:pd.DataFrame,baseActivos:pd.DataFrame)->pd.DataFrame:
    print("Leo cuestionarios de team members y les asocio squad y especialidad según la base de activos ")

    baseActivos = baseActivos.sort_values(['matricula','squad_code','fecha_actualizado'], ascending = [True,True,False])
    baseActivos: pd.DataFrame = baseActivos.drop_duplicates(subset=["matricula","squad_code"], keep="first")

    quizTests = pd.merge(quizTests, baseActivos[['matricula', 'squad', 'squad_code','especialidad']], on="matricula", how="left")
    
    return quizTests

def getQuizTestByTeamMemberWithMaturityLevel(period:str,quizTests:pd.DataFrame)->pd.DataFrame:
    print("Leo cuestionarios de team members y les calculo su puntaje de nivel de madurez ")

    for metric in constants.ARRAY_QUIZ_METRICS:
        quizTests[metric + "_points"] = quizTests.apply(lambda q: get_quiz_test_points(q[metric]),axis=1)

    setAnalysisExecutionDate(period,quizTests)

    return quizTests
