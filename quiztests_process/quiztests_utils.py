import pandas as pd
import json
import numpy as np

from quiztests_process.utils import getPathDirectory,getCodeSquadTribe,isNullOrEmpty
from quiztests_process.base_activos_utils import getValueBaseActivosByTeamMember
import quiztests_process.constants as constants

def getQuizTests(configuration):
    print("Leo archivo de cuestionario: " + configuration["archivo"])

    countInitial:int = 7
    columns = ["id","hora_inicio","hora_fin","email","nombre","squad_form","matricula"]
    if(configuration["especialidad"]=="GENERAL"): 
        countInitial += 1
        columns.append("especialidad")

    columns.append("recibi_capacitaciones")

    segmentos = configuration["segmentos"]
    countRespuesta:int = None
    for segmento in segmentos:
        countRespuesta = 1
        for respuesta in segmento["respuestas"]:
            columns.append(segmento["segmento"] + "_respuesta_" + str(countRespuesta))
            countRespuesta += 1

    useCols = []
    countColumn = 0
    for column in columns:
        useCols.append(countColumn)
        countColumn += 1

    file = getPathDirectory("input\\quiz_tests\\" + configuration["archivo"])

    quiz = pd.read_excel(file,usecols=useCols,names=columns,sheet_name=0)

    quiz["matricula"] = quiz.apply(lambda pr: str(pr["matricula"]).upper().strip(),axis=1)
    quiz["hora_inicio"] = quiz.apply(lambda pr: pd.to_datetime(pr["hora_inicio"],format="%Y-%m-%d %H:%M:%S").to_datetime64(),axis=1)
    quiz["hora_fin"] = quiz.apply(lambda pr: pd.to_datetime(pr["hora_fin"],format="%Y-%m-%d %H:%M:%S").to_datetime64(),axis=1)
    quiz["squad_form"] = quiz.apply(lambda pr: str(pr["squad_form"]).upper().strip(),axis=1)
    quiz["squad_code_form"] = quiz.apply(lambda pr: getCodeSquadTribe(pr["squad_form"]),axis=1)

    if(configuration["especialidad"]=="GENERAL"): 
        quiz["especialidad"] = quiz.apply(lambda pr: str(pr["especialidad"]).upper().strip(),axis=1)
    else:
        quiz["especialidad"] = str(configuration["especialidad"]).upper().strip()

    quiz = quiz.astype(object).where(pd.notnull(quiz),None)

    return quiz

def getQuizTestsWithApprovalRate(configuration,quizTests:pd.DataFrame):
    print("Calculo el porcentaje de aprobación del archivo de cuestionario: " + configuration["archivo"])

    segmentos = configuration["segmentos"]
    countRespuesta:int = None
    for segmento in segmentos:
        countRespuesta = 1
        for respuesta in segmento["respuestas"]:
            quizTests[segmento["segmento"] + "_respuesta_correcta_" + str(countRespuesta)] = quizTests.apply(lambda quiz: getIfCorrectAnswer(quiz,segmento,countRespuesta,respuesta),axis=1)
            countRespuesta += 1

    for segmento in segmentos:
        quizTests[segmento["segmento"] + "_points"] = quizTests.apply(lambda quiz: getApprovalRateBySegment(quiz,segmento),axis=1)

    totalAnswers = getTotalAnswers(segmentos)

    quizTests["state"] = quizTests.apply(lambda quiz: getStateQuizTest(quiz,segmentos,totalAnswers),axis=1)

    return quizTests

def getQuizTestsForModel(quizTests:pd.DataFrame)->pd.DataFrame:
    print("Obtengo el reporte final de cuestionarios para el modelo")

    xlsReport = quizTests[(quizTests['state']==constants.STATE_FINALIZADO)]

    xlsReport = xlsReport.sort_values(['matricula','hora_fin'], ascending = [True, False])
    xlsReport = xlsReport.drop_duplicates(['matricula'],keep='first')

    return xlsReport

def getIfCorrectAnswer(rowTest,segmento,indexRespuesta,respuesta_correcta):
    col_respuesta = segmento["segmento"] + "_respuesta_" + str(indexRespuesta)

    respuesta = rowTest[col_respuesta]

    isCorrect = None

    if(isNullOrEmpty(respuesta)): return isCorrect

    isCorrect = "SI" if respuesta.strip() == respuesta_correcta.strip() else "NO"

    return isCorrect

def getApprovalRateBySegment(rowTest,segmento):
    col_respuesta_correcta = segmento["segmento"] + "_respuesta_correcta_"

    respuesta_correcta = None
    countRespuesta = 0
    countRespuestaCorrecta = 0
    for respuesta in segmento["respuestas"]:
        countRespuesta += 1

        respuesta_correcta = rowTest[col_respuesta_correcta + str(countRespuesta)]

        if(respuesta_correcta=="SI"): countRespuestaCorrecta += 1 

    approvalRate:float = 0

    if(countRespuestaCorrecta==0): return approvalRate

    approvalRate = round((countRespuestaCorrecta * 100) / countRespuesta,2)

    return approvalRate

def getTotalAnswers(segmentos)->int:
    totalAnswers:int = 0

    for segmento in segmentos:
        totalAnswers += len(segmento["respuestas"]) 

    return totalAnswers        

def getStateQuizTest(rowTest,segmentos,totalRespuestas):
    countRespuestasRegistradas:int = 0

    for segmento in segmentos:
        countRespuesta = 1
        col_respuesta = segmento["segmento"] + "_respuesta_"

        for respuesta in segmento["respuestas"]:
            respuesta_registrada = rowTest[col_respuesta + str(countRespuesta)]

            countRespuesta += 1

            if(isNullOrEmpty(respuesta_registrada)): continue

            countRespuestasRegistradas += 1

    state:str = "PENDIENTE"

    if(countRespuestasRegistradas==0): return state

    if(countRespuestasRegistradas==totalRespuestas): state = "FINALIZADO"
    else: state = "EN PROCESO"

    return state
    
def getReportDifferencesBaseActivos(quizTests:pd.DataFrame)->pd.DataFrame:
    print("Leo los team members que tienen diferencias entre el squad que indicaron en el formulario y el squad de la bd activos")

    xlsReport = quizTests[quizTests['squad_code']!=quizTests['squad_code_form']]
    xlsReport = xlsReport.sort_values(['matricula','hora_fin'], ascending = [True, False])
    xlsReport = xlsReport.drop_duplicates(['matricula'],keep='first')

    return xlsReport

def setExcelReportQuizTestsModel(configuration,quizTests:pd.DataFrame):
    file = configuration["archivo"]

    print("Exportando a Excel Reporte de Quiz Tests para el modelo" + file)

    file = getPathDirectory("output\\" + file)

    columns = ["matricula","nombre","email","especialidad"]

    segmentos = configuration["segmentos"]
    for segmento in segmentos:
        columns.append(segmento["segmento"] + "_points")

    quizTests.to_excel(file,columns=columns,sheet_name="Tests",index=False)

def setExcelReportSummary(configuration,quizTests:pd.DataFrame,reportSquadsWithoutScore,reportTeamMembersWithoutScore,bdActivosPriorizada,bdActivos,quizResume):
    file = "summary-" + configuration["archivo"]

    print("Exportando a Excel Reporte de Resumen: " + file)

    file = getPathDirectory("output\\" + file)

    columnsReportTeamMembersWithoutScore = ["matricula","nombre","apellido_paterno","apellido_materno","correo","tribu","squad_code","squad","especialidad","nombre_cal","nombre_cl"]
    columnsBdActivosPriorizada = ["matricula","nombre","apellido_paterno","apellido_materno","correo","tribu","squad_code","squad","especialidad","nombre_cal","nombre_cl"]
    columnsBdActivos = ["matricula","nombre","apellido_paterno","apellido_materno","correo","tribu","squad_code","squad","especialidad","nombre_cal","nombre_cl"]
    columnsQuizTests = getColumnsQuizTests(configuration)
    columns_resume = ["specialty","totalPriorizado","totalCompletado","squadSinNota","ratio"]

    with pd.ExcelWriter(file) as writer:
        quizTests.to_excel(writer,sheet_name="CUESTIONARIOS",columns=columnsQuizTests, index=False)
        reportSquadsWithoutScore.to_excel(writer,sheet_name="SQUADS SIN NOTA", index=False)
        reportTeamMembersWithoutScore.to_excel(writer,sheet_name="TEAM MEMBERS SIN NOTA",columns=columnsReportTeamMembersWithoutScore, index=False)
        bdActivosPriorizada.to_excel(writer,sheet_name="BD ACTIVOS PRIORIZADA",columns=columnsBdActivosPriorizada, index=False)
        bdActivos.to_excel(writer,sheet_name="BD ACTIVOS",columns=columnsBdActivos, index=False) 
        quizResume.to_excel(writer,sheet_name="RESUMEN",columns=columns_resume, index=False) 

def getReportQuizResume(configuration,bdActivosPriorizada,reportTeamMembersWithoutScore,reportSquadsWithoutScore):
    resume_array = []
    columns_resume = ["specialty","totalPriorizado","totalCompletado","squadSinNota","ratio"]
    
    if(configuration["especialidad"]==constants.SPECIALTY_GENERAL): 
        especialidades = constants.SPECIALTYS_SCOPE.copy()

        for specialty in especialidades:
            resume_array.append(getResume(bdActivosPriorizada, specialty, reportSquadsWithoutScore, reportTeamMembersWithoutScore))

    else: 
        resume_array.append(getResume(bdActivosPriorizada, configuration["especialidad"], reportSquadsWithoutScore, reportTeamMembersWithoutScore))

    quizResume = pd.DataFrame(resume_array, columns = columns_resume)
    return quizResume

def getColumnsQuizTests(configuration):
    columnsQuizTests = ["matricula","nombre","email","especialidad","hora_inicio","hora_fin","recibi_capacitaciones","state"]

    segmentos = configuration["segmentos"]

    for segmento in segmentos:
        countRespuesta = 1
        col_segmento = segmento["segmento"] + "_points"
        col_respuesta = segmento["segmento"] + "_respuesta_"
        col_respuesta_correcta = segmento["segmento"] + "_respuesta_correcta_"

        columnsQuizTests.append(col_segmento)

        for respuesta in segmento["respuestas"]:
            columnsQuizTests.append(col_respuesta + str(countRespuesta))
            columnsQuizTests.append(col_respuesta_correcta + str(countRespuesta))

            countRespuesta += 1    

    return columnsQuizTests

def getResume(bdActivosPriorizada, specialty, reportSquadsWithoutScore, reportTeamMembersWithoutScore):
    totalPriorizado = len(bdActivosPriorizada[bdActivosPriorizada["especialidad"] == specialty])
    totalCompletado = totalPriorizado - len(reportTeamMembersWithoutScore[reportTeamMembersWithoutScore["especialidad"] == specialty])
    squadSinNota = len(reportSquadsWithoutScore[reportSquadsWithoutScore[specialty] == "NO"])
    ratio = (totalCompletado / totalPriorizado) * 100
    return [specialty,totalPriorizado,totalCompletado,squadSinNota,ratio]
