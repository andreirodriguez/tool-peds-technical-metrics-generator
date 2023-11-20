import pandas as pd
import os
PD = pd

############### INPUT PATHS ##################################
PATH_MATURITY_LEVEL_FILE = 'input'+ os.sep +'maturity_level_by_squad' + os.sep
PATH_BASE_ACTIVOS        = 'input'+ os.sep +'base_activos' + os.sep
PATH_PRS_FILE            = 'input'+ os.sep +'pull_request' + os.sep
PATH_FORTIFY_BASE_PATH   = 'input'+ os.sep +'fortify' + os.sep
PATH_QUIZ_FILES          = 'input'+ os.sep +'quiz' + os.sep
NODE_SONAR_REPORT_FILE   = 'input'+ os.sep +'sonar' + os.sep

############### OUTPUT PATH ##################################

OUTPUT_BASE_FILE         = "cs-prs-detail.csv"
OUTPUT_DETAIL_FILE       = "output" + os.sep + "{}-" + OUTPUT_BASE_FILE
OUTPUT_BY_SQUAD_FILE     = "output" + os.sep + "{}-cs-maturity-level-by-squad.csv"
OUTPUT_BY_SQUAD_FILE_BACKEND= "output" + os.sep + "{}-cs-maturity-level-by-squad-BACKEND.csv"
OUTPUT_BY_SQUAD_FILE_ANDROID= "output" + os.sep + "{}-cs-maturity-level-by-squad-FRONTEND ANDROID.csv"
OUTPUT_BY_SQUAD_FILE_IOS= "output" + os.sep + "{}-cs-maturity-level-by-squad-FRONTEND IOS.csv"
OUTPUT_BY_SQUAD_FILE_WEB= "output" + os.sep + "{}-cs-maturity-level-by-squad-FRONTEND WEB.csv"
OUTPUT_FOLDER            = "output" + os.sep

############### OTHER FILES ##################################

EXTENSIONS_ADD_FUNTIONALITY = "config" + os.sep + "extensions.json"