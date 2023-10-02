import sys

import quiztests_process.utils as utils
import quiztests_process.base_activos_utils as base_activos_utils
import quiztests_process.quiztests_utils as quiztests_utils

def execute_by_specialty(configurationFile):
    print("INICIO proceso calculo del cuestionario: " + configurationFile)

    configuration = utils.getConfigurationFileJson(configurationFile)

    base_activos = base_activos_utils.getBaseActivos()

    quiz_tests = quiztests_utils.getQuizTests(configuration)

    quiz_tests = quiztests_utils.getQuizTestsWithApprovalRate(configuration,quiz_tests)

    quiz_tests_model = quiztests_utils.getQuizTestsForModel(quiz_tests)

    base_activos_priorizada = base_activos_utils.getBaseActivosPriorizada(configuration["especialidad"],base_activos)    

    report_tm_without_score = base_activos_utils.getReportTeamMembersWithoutScore(configuration["especialidad"],base_activos_priorizada,quiz_tests)

    report_squads_without_score = base_activos_utils.getReportSquadsWithoutScore(configuration["especialidad"],quiz_tests_model,base_activos_priorizada)

    quiztests_utils.setExcelReportQuizTestsModel(configuration,quiz_tests_model)
    
    quizResume = quiztests_utils.getReportQuizResume(configuration,base_activos_priorizada,report_tm_without_score,report_squads_without_score)

    quiztests_utils.setExcelReportSummary(configuration,quiz_tests,report_squads_without_score,report_tm_without_score,base_activos_priorizada,base_activos,quizResume)

    print("FIN proceso calculo del cuestionario:  " + configurationFile)

def execute(configurationFile):
    if configurationFile == "all":
        files = utils.getFilesDirectory("input\\configuration")

        for file in files:
            if(not ".json" in file): continue

            file = file.replace(".json","")

            execute_by_specialty(file)
    else:
        execute_by_specialty(configurationFile)

configurationFile:str = sys.argv[1]

execute(configurationFile)
