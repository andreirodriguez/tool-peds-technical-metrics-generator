import math
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from datetime import datetime 

import unittesting.constants as constants
from unittesting.sonar_utils import getPointZeroNone
from unittesting.prioritized_squads import getPrioritizedSquads
from unittesting.maturity_points import setMaturityLevel
from unittesting.utils import setExportCsv,getPathDirectory,getBeforePeriodProcess,getCodeSquadTribe,setAnalysisExecutionDate,isNotNumber

def get_ut_metric_technical(coverage,coverage_point,new_coverage,new_coverage_point):
    if coverage is None or math.isnan(coverage): return None

    if new_coverage is None or math.isnan(new_coverage): return coverage_point

    if coverage < 40.0:
        return round(coverage_point * 0.0 + new_coverage_point * 1, 2)
    else:
        return round(coverage_point * 0.5 + new_coverage_point * 0.5, 2)

def get_ut_maturity_model_from_technical(metric_technical, survey_points): 
    if metric_technical is None or math.isnan(metric_technical): return getPointZeroNone(survey_points)

    if survey_points is None or math.isnan(survey_points): return getPointZeroNone(metric_technical)

    nm = round(metric_technical * 0.6 + survey_points * 0.4, 2)

    return getPointZeroNone(nm)

def calculate_values_for_excetpions(row):
    row["technical_metric"] = float(row['coverage_points']) if math.isnan(row["technical_metric"]) else row["technical_metric"]
    
    if math.isnan(float(row["coverage"])):
        if float(row['coverage_points']) > 1:
            row["technical_metric"] = row['coverage_points']
        else:
            if float(row["maturity_level"]) > 0:
                row["coverage_points"] = None
                row["technical_metric"] = None
                row["maturity_level"] = row["survey_points"]
                return row

            row["coverage_points"] = 1
            row["technical_metric"] = 1

    row["maturity_level"] = float(row['coverage_points']) * 0.6 + float(row['survey_points']) * 0.4 if math.isnan(float(row["coverage"])) else row["maturity_level"]

    return row

def getSquadsGeneralWithMaturityLevel(period:str,squadsPrioritized,prsSonarExecutions:pd.DataFrame,quizTest:pd.DataFrame)->pd.DataFrame:
    squads = getPrioritizedSquads(constants.SPECIALTY_GENERAL) 

    #POINTS DE VARIABLES DE METRICAS DEL PERIODO ACTUAL
    squads["coverage_points"] =  squads.apply(lambda squad: getMeanBySquadGeneral(squad["squad_code"],squadsPrioritized,prsSonarExecutions,"coverage_points"),axis=1)

    for metric in constants.ARRAY_QUIZ_METRICS:
        variable = metric + "_points"

        squads[variable] =  squads.apply(lambda squad: getMeanBySquadGeneral(squad["squad_code"],squadsPrioritized,quizTest,variable),axis=1)

    setAnalysisExecutionDate(period,squads)

    #setValuesLastProcess(period,squads,constants.SPECIALTY_GENERAL)

    squads["ratio_prs_executions_sonar"] =  squads.apply(lambda squad: getRatioPrsExecutionSonar(squad["squad_code"],prsSonarExecutions,constants.SPECIALTY_GENERAL,squadsPrioritized),axis=1)
    squads["penalty_prs_executions_sonar"] =  squads.apply(lambda squad: getPenaltyRatioPrsExecutionSonar(squad["ratio_prs_executions_sonar"]),axis=1)

    #CALCULO EL NIVEL DE MADUREZ
    setMaturityLevel(squads)

    print("Nivel de madurez calculado para lista de squads priorizados en la lista GENERAL ")

    return squads

def getSquadsSpecialtyWithMaturityLevel(period:str,speciality:str,prsSonarExecutions:pd.DataFrame,quizTest:pd.DataFrame)->pd.DataFrame:
    squads = getPrioritizedSquads(speciality) 

    #POINTS DE VARIABLES DE METRICAS DEL PERIODO ACTUAL
    squads["coverage_points"] =  squads.apply(lambda squad: getMeanBySquadAndSpeciality(squad["squad_code"],speciality,prsSonarExecutions,"coverage_points"),axis=1)

    for metric in constants.ARRAY_QUIZ_METRICS:
        variable = metric + "_points"

        squads[variable] =  squads.apply(lambda squad: getMeanBySquadAndSpeciality(squad["squad_code"],speciality,quizTest,variable),axis=1)

    setAnalysisExecutionDate(period,squads)

    #setValuesLastProcess(period,squads,speciality)

    squads["ratio_prs_executions_sonar"] =  squads.apply(lambda squad: getRatioPrsExecutionSonar(squad["squad_code"],prsSonarExecutions,speciality,[]),axis=1)
    squads["penalty_prs_executions_sonar"] =  squads.apply(lambda squad: getPenaltyRatioPrsExecutionSonar(squad["ratio_prs_executions_sonar"]),axis=1)

    #CALCULO EL NIVEL DE MADUREZ
    setMaturityLevel(squads)

    print("Nivel de madurez calculado para lista de squads priorizados de la especialidad: " + speciality)

    return squads

def setValuesLastProcess(period:str,squads:pd.DataFrame,speciality:str):
    lastProcess = getImportCsvSquadsWithMaturityLevelLastProcess(period,speciality)
    squads["analysis_date"] = squads.apply(lambda squad: getAnalysisDateLastProcess(period,squad,lastProcess),axis=1)

    #POINTS DE VARIABLES DE METRICAS DEL PERIODO ANTERIOR
    metrics = []
    #metrics = constants.ARRAY_QUIZ_METRICS.copy()
    metrics.append("coverage")

    for metric in metrics:
        variable = metric + "_points"

        squads[variable] =  squads.apply(lambda squad: getValueLastProcess(squad["squad_code"],lastProcess,variable,squad[variable]),axis=1)

def getValueLastProcess(squadCode:str,lastProcess:pd.DataFrame,variable:str,originalValue:float)->float:
    if(not isNotNumber(originalValue)): return originalValue

    squadLastProcess = lastProcess[(lastProcess['squad_code']==squadCode)]

    if(len(squadLastProcess)==0): return originalValue

    lastValue = squadLastProcess.iloc[0][variable]

    if(isNotNumber(lastValue)): return originalValue

    return lastValue

def getAnalysisDateLastProcess(period,squad,lastProcess:pd.DataFrame)->pd.DataFrame:
    year = int(period[0:4])
    month = int(period[4:6])

    analysisDate = datetime(year, month, 1,0,0,0).date()

    valueActually = None
    valueLast = None

    squadLastProcess = lastProcess[(lastProcess['squad_code']==squad.squad_code)]

    if(len(squadLastProcess)==0): return analysisDate

    metrics = []
    #metrics = constants.ARRAY_QUIZ_METRICS.copy()
    metrics.append("coverage")

    for metric in metrics:
        variable = metric + "_points"

        valueActually = squad[variable]

        if(not isNotNumber(valueActually)): continue

        valueLast = squadLastProcess.iloc[0][variable]

        if(isNotNumber(valueLast)): continue

        analysisDate = pd.to_datetime(squadLastProcess.iloc[0]["analysis_date"],format="%d/%m/%Y").date()

        return analysisDate
    
    return analysisDate

def getMeanBySquadGeneral(squadCode:str,squadsPrioritized,metrics:pd.DataFrame,property:str)->float:
    specialitys = getSpecialitysBySquadsPrioritized(squadCode,squadsPrioritized,True)

    return getMeanBySquadAndSpecialitys(squadCode,specialitys,metrics,property)

def getMeanBySquadAndSpeciality(squadCode:str,speciality:str,metrics:pd.DataFrame,property:str)->float:
    specialitys = []

    specialitys.append(speciality)

    return getMeanBySquadAndSpecialitys(squadCode,specialitys,metrics,property)

def getRatioPrsExecutionSonar(squadCode:str,prsExecutionsSonar:pd.DataFrame,specialty:str,squadsPrioritized)->float:
    specialtys = []
    if(specialty==constants.SPECIALTY_GENERAL):
        specialtys = getSpecialitysBySquadsPrioritized(squadCode,squadsPrioritized,False)
    else:
        specialtys.append(specialty)

    executionsSonar = prsExecutionsSonar[(prsExecutionsSonar['squad_code']==squadCode) & (prsExecutionsSonar['specialty'].isin(specialtys))]

    countPrs = len(executionsSonar)

    if(countPrs==0): return None

    executionsSonar = executionsSonar[~executionsSonar["overall_coverage"].isnull()]

    countExecutionsSonar = len(executionsSonar)

    ratio = round((countExecutionsSonar * 100) / countPrs,2)

    return ratio

def getPenaltyRatioPrsExecutionSonar(ratioPrsExecutionsSonar:float)->float:
    if(math.isnan(ratioPrsExecutionsSonar)): return None

    penalty:float = 0.0

    if(ratioPrsExecutionsSonar<constants.RANGE_PENALTY_PERCENTAGE_RATIO_EXECUTION_SONAR): 
        penalty = constants.PENALTY_PERCENTAGE_RATIO_EXECUTION_SONAR
    
    return penalty

def getMeanBySquadAndSpecialitys(squadCode:str,specialitys,metrics:pd.DataFrame,property:str)->float:
    metricsBySquad = metrics[(metrics['squad_code']==squadCode) & (metrics['specialty'].isin(specialitys))]

    value = metricsBySquad[property].mean()

    if(math.isnan(value)): return None  

    return round(value,2)

def getSpecialitysBySquadsPrioritized(squadCode:str,squadsPrioritized,withMaturityLevel:bool)->float:
    specialitysCalculate = []
    specialtysPrioritized = []

    countSquad:int = 0
    for specialty in constants.SPECIALTYS_SCOPE_SEE:
        squads = squadsPrioritized[countSquad]

        squads = squads[(squads['squad_code']==squadCode)]

        countSquad += 1

        #SI NO ESTA PRIORIZADO PARA LA ESPECIALIDAD
        if(len(squads)==0): continue

        specialtysPrioritized.append(specialty)

        #SI ESA ESPECIALIDAD NO TIENE NIVEL DE MADUREZ
        if(withMaturityLevel):
            if(isNotNumber(squads.iloc[0]["maturity_level"])): continue

        specialitysCalculate.append(specialty)    

    #SI NO TIENE ALGUNA ESPECIALIDAD PRIORIZADA SE CALCULAN TODAS LAS DEL SCOPE
    if(len(specialtysPrioritized)==0): specialitysCalculate = constants.SPECIALTYS_SCOPE.copy()

    return specialitysCalculate


def getImportCsvSquadsWithMaturityLevelLastProcess(period:str,specialty:str)->pd.DataFrame:
    periodBefore = getBeforePeriodProcess(period)
    file = "input\\last_process\\" + periodBefore + "-ut-maturity-level-by-squad"

    if(specialty!=constants.SPECIALTY_GENERAL): file = file + "-" + specialty

    file = file + ".csv"

    print("Leo notas del proceso anterior: " + file)

    columns=['squad','analysis_date']

    #for metric in constants.ARRAY_QUIZ_METRICS: columns.append(metric + "_points")

    columns.append("coverage_points")

    file = getPathDirectory(file)

    csvMaturityLevel = pd.read_csv(file,usecols=columns,encoding="utf-8")

    csvMaturityLevel["squad_code"] = csvMaturityLevel.apply(lambda pr: getCodeSquadTribe(pr["squad"]),axis=1)

    return csvMaturityLevel

def getReportSquadsWithoutExecutionsSonar(squadsPrioritized)->pd.DataFrame:
    print("Genero reporte de Squads sin ejecuciones de sonar ")

    xlsReport = pd.DataFrame({'specialty': [],'squads_without_executions_sonar': []})

    squads = None
    count = 0
    countSonar = 0
    for specialty in constants.SPECIALTYS_SCOPE_SEE:
        squads = squadsPrioritized[count]
        countExecutionsSonar = squads[(squads['ratio_prs_executions_sonar']==0.0)]
        
        countSonar = len(countExecutionsSonar.index)

        newRow = pd.Series({'specialty': specialty,'squads_without_executions_sonar': countSonar})
        xlsReport = pd.concat([xlsReport, newRow.to_frame().T], ignore_index=True)

        count += 1

    return xlsReport

def getReportSquadsMaturityLevelByGroup(squadsGeneral,squadsPrioritized)->pd.DataFrame:
    print("Genero reporte de niveles de madurez por grupos y especialidad ")

    xlsReport = pd.DataFrame({'specialty': [],'grupo_1_2': [],'grupo_3': [],'otros': []})

    squadsArray = squadsPrioritized.copy()
    squadsArray.append(squadsGeneral)
    
    specialtys = constants.SPECIALTYS_SCOPE_SEE.copy()
    specialtys.append(constants.SPECIALTY_GENERAL)

    squads = None
    count = 0
    for specialty in specialtys:
        squads = squadsArray[count]

        squadsByGroup = squads[(squads['grupo']==1) | (squads['grupo']==2)]
        mean_group_1_2 = round(squadsByGroup["maturity_level"].mean(),2)

        squadsByGroup = squads[(squads['grupo']==3)] 
        mean_group_3 = round(squadsByGroup["maturity_level"].mean(),2)

        squadsByGroup = squads[(squads['grupo'].isnull())]
        mean_others = round(squadsByGroup["maturity_level"].mean(),2)

        mean_all = round(squads["maturity_level"].mean(),2)

        newRow = pd.Series({'specialty': specialty,'grupo_1_2': mean_group_1_2,'grupo_3': mean_group_3,'otros': mean_others, 'todos': mean_all})
        xlsReport = pd.concat([xlsReport, newRow.to_frame().T], ignore_index=True)

        count += 1

    return xlsReport

def getReportSquadsApprovedByGroup(squadsGeneral,squadsPrioritized)->pd.DataFrame:
    print("Genero reporte de niveles de madurez por grupos y especialidad ")

    xlsReport = pd.DataFrame({'specialty': [],'grupo_1_2_approved': [],'grupo_1_2_disapprove': [],'grupo_1_2_without_maturity_level': [],'grupo_1_2_total': [],'grupo_3_approved': [],'grupo_3_disapprove': [],'grupo_3_without_maturity_level': [],'grupo_3_total': []})

    squadsArray = squadsPrioritized.copy()
    squadsArray.append(squadsGeneral)
    
    specialtys = constants.SPECIALTYS_SCOPE_SEE.copy()
    specialtys.append(constants.SPECIALTY_GENERAL)

    squads:pd.DataFrame = None
    squadsByGroup:pd.DataFrame = None
    nmApproved:float = 0.0
    count = 0
    for specialty in specialtys:
        squads = squadsArray[count]

        nmApproved = 4

        if(specialty in "IOS" or specialty in "ANDROID"): nmApproved = 3

        squadsByGroup = squads[(squads['grupo'].isin([1,2]))]

        grupo_1_2_approved = len(squadsByGroup[(squadsByGroup['maturity_level'] >= nmApproved)].index)
        grupo_1_2_disapprove = len(squadsByGroup[(squadsByGroup['maturity_level'] < nmApproved)].index)
        grupo_1_2_without_maturity_level = len(squadsByGroup[(squadsByGroup['maturity_level'].isnull())].index)
        grupo_1_2_total = len(squadsByGroup.index)

        nmApproved = 3.5

        squadsByGroup = squads[(squads['grupo'].isin([3]))]

        grupo_3_approved = len(squadsByGroup[(squadsByGroup['maturity_level'] >= nmApproved)].index)
        grupo_3_disapprove = len(squadsByGroup[(squadsByGroup['maturity_level'] < nmApproved)].index)
        grupo_3_without_maturity_level = len(squadsByGroup[(squadsByGroup['maturity_level'].isnull())].index)
        grupo_3_total = len(squadsByGroup.index)        

        newRow = pd.Series({'specialty': specialty,'grupo_1_2_approved': grupo_1_2_approved,'grupo_1_2_disapprove': grupo_1_2_disapprove,'grupo_1_2_without_maturity_level': grupo_1_2_without_maturity_level,'grupo_1_2_total': grupo_1_2_total,'grupo_3_approved': grupo_3_approved,'grupo_3_disapprove': grupo_3_disapprove,'grupo_3_without_maturity_level': grupo_3_without_maturity_level,'grupo_3_total': grupo_3_total})
        xlsReport = pd.concat([xlsReport, newRow.to_frame().T], ignore_index=True)

        count += 1

    return xlsReport

def setExportCsvSquadsWithMaturityLevel(period,squads,specialty):
    columns = getColumnsExportSquadsWithMaturityLevel()

    squadsWithMaturityLevel = squads[~squads["coverage_points"].isnull()]

    file = "output\\" + period + "-ut-maturity-level-by-squad"

    if(specialty!=constants.SPECIALTY_GENERAL): file = file + "-" + specialty

    file = file + ".csv"

    setExportCsv(file,squadsWithMaturityLevel,columns)

    print("Exportando a Csv Squads con nivel de madurez de la especialidad  " + specialty + " : " + file)

def setExportCsvPullRequestSonarExecutions(period,pullRequests):
    columns = getColumnsExportPullRequest()

    file = "output\\" + period + "-prs-with-sonar-executions.csv"

    setExportCsv(file,pullRequests,columns)

    print("Exportando a Csv Pull Requests con ejecuciones de sonar : " + file)    

def setExportCsvQuizTests(period,quizTests):
    columns = getColumnsExportQuizTests()

    file = "output\\" + period + "-quiz-tests-team-members.csv"

    setExportCsv(file,quizTests,columns)

    print("Exportando a Csv Quiz Tests  : " + file)        

def getColumnsExportSquadsWithMaturityLevel()->list[str]:
    columns = ["squad_code","squad","tribe_code","tribe","grupo","cmt"]
    
    for metric in constants.ARRAY_QUIZ_METRICS:
        columns.append(metric + "_points")

    for metric in ["coverage_points","patrones_principios_metric","asserts_restricciones_metric","mocks_stubs_metric","naming_convention_metric","coverage_metric","ratio_prs_executions_sonar","penalty_prs_executions_sonar","maturity_level","analysis_date","execution_date"]:
        columns.append(metric)    
    
    return columns

def getColumnsExportPullRequest()->list[str]:
    columns = ['app','repo','prid','squad_code','squad','tribe','technology','specialty','application_type','author','author_name','origin_branch','close_date','overall_coverage','new_coverage','overall_coverage_points','new_coverage_points','coverage_points','analysis_date','execution_date']
        
    return columns    

def getColumnsExportQuizTests()->list[str]:
    columns = ["matricula","nombre","email",'squad_code',"squad","especialidad"]

    for metric in constants.ARRAY_QUIZ_METRICS:
        columns.append(metric)

    for metric in constants.ARRAY_QUIZ_METRICS:
        columns.append(metric + "_points")
    
    columns.append('analysis_date')
    columns.append('execution_date')

    return columns    

def setExportExcelSummary(period,baseActivos,sonarExecutions,quizTest,prsSonarExecutions,reportSquadsMaturityLevelByGroup,reportSquadsApprovedByGroup,reportSquadsWithoutExecutionsSonar,squadsGeneral,squadsWithMaturityLevel):
    file = getPathDirectory("output\\" + period + "-ut-maturity-level-by-squad-summary.xlsx")

    with pd.ExcelWriter(file) as writer:
        squadsGeneral.to_excel(writer,sheet_name=constants.SPECIALTY_GENERAL,columns=getColumnsExportSquadsWithMaturityLevel(), index=False)

        countSquad:int = 0
        for specialty in constants.SPECIALTYS_SCOPE_SEE:
            squadsWithMaturityLevel[countSquad].to_excel(writer,sheet_name=specialty,columns=getColumnsExportSquadsWithMaturityLevel(), index=False)
            countSquad += 1

        reportSquadsMaturityLevelByGroup.to_excel(writer,sheet_name="REPORT MATURITY LEVEL", index=False)
        reportSquadsApprovedByGroup.to_excel(writer,sheet_name="REPORT SQUADS APPROVED", index=False)
        reportSquadsWithoutExecutionsSonar.to_excel(writer,sheet_name="SQUADS SIN PRACTICA", index=False)
        prsSonarExecutions.to_excel(writer,sheet_name="PULL REQUESTS",columns=getColumnsExportPullRequest(), index=False)
        sonarExecutions.to_excel(writer,sheet_name="SONAR EXECUTIONS",columns=['application','project','url_repository','repository','version','branch','metric','value','date_analysis','type_information'], index=False)
        quizTest.to_excel(writer,sheet_name="QUIZ TESTS",columns=getColumnsExportQuizTests(), index=False)
        baseActivos.to_excel(writer,sheet_name="BASE ACTIVOS", index=False)

    print("Exportando Resumen de Nivel de Madurez  : " + file)