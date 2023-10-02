import sys

import unittesting.constants as constants
from unittesting.base_activos_utils import getBaseActivos
from unittesting.quiztest_utils import getQuizTest,getQuizTestByTeamMember,getQuizTestByTeamMemberWithMaturityLevel
from unittesting.sonar_utils import getSonarExecutionsConsolidated
from unittesting.pullrequest_utils import getPrsCodeReview,getPrsSonarExecutions,getPrsSonarExecutionsWithMaturityLevel
from unittesting.maturity_models import getSquadsSpecialtyWithMaturityLevel,getSquadsGeneralWithMaturityLevel,setExportCsvSquadsWithMaturityLevel,setExportCsvPullRequestSonarExecutions,setExportCsvQuizTests,setExportExcelSummary,getReportSquadsWithoutExecutionsSonar,getReportSquadsMaturityLevelByGroup,getReportSquadsApprovedByGroup

def execute(period):
    year = int(period[0:4])
    month = int(period[4:6])

    print("INICIO proceso calculo nivel de madurez unit testing periodo: " + period)

    sonarExecutions = getSonarExecutionsConsolidated(year,month)

    prsCodeReview =  getPrsCodeReview(year,month)

    prsSonarExecutions = getPrsSonarExecutions(prsCodeReview,sonarExecutions)

    prsSonarExecutions = getPrsSonarExecutionsWithMaturityLevel(period,prsSonarExecutions)
    setExportCsvPullRequestSonarExecutions(period,prsSonarExecutions)

    baseActivos = getBaseActivos()

    quizTest = getQuizTest()

    quizTest = getQuizTestByTeamMember(quizTest,baseActivos)

    quizTest = getQuizTestByTeamMemberWithMaturityLevel(period,quizTest)
    setExportCsvQuizTests(period,quizTest)

    squadsWithMaturityLevel = []
    squads = None
    #SQUADS POR ESPECIALIDAD
    for specialty in constants.SPECIALTYS_SCOPE_SEE:
        squads = getSquadsSpecialtyWithMaturityLevel(period,specialty,prsSonarExecutions,quizTest)
        setExportCsvSquadsWithMaturityLevel(period,squads,specialty)
        squadsWithMaturityLevel.append(squads)

    #SQUADS LISTA GENERAL
    squads = getSquadsGeneralWithMaturityLevel(period,squadsWithMaturityLevel,prsSonarExecutions,quizTest)
    setExportCsvSquadsWithMaturityLevel(period,squads,constants.SPECIALTY_GENERAL)

    reportSquadsWithoutExecutionsSonar = getReportSquadsWithoutExecutionsSonar(squadsWithMaturityLevel)
    
    reportSquadsMaturityLevelByGroup = getReportSquadsMaturityLevelByGroup(squads,squadsWithMaturityLevel)

    reportSquadsApprovedByGroup = getReportSquadsApprovedByGroup(squads,squadsWithMaturityLevel)

    setExportExcelSummary(period,baseActivos,sonarExecutions,quizTest,prsSonarExecutions,reportSquadsMaturityLevelByGroup,reportSquadsApprovedByGroup,reportSquadsWithoutExecutionsSonar,squads,squadsWithMaturityLevel)

    print("FIN proceso calculo nivel de madurez unit testing periodo: " + period)

period:str = sys.argv[1]

execute(period)