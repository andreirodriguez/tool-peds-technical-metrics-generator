from codereview.headers_columns_util import column_status

EXCLUSIONS_FILE = "codereview/input/exclusiones/branch_repo_exclude.xlsx"
CSV_SPECIALTY_FILE = "specialty_extraction_repository/output/specialty-file.csv"
QUIZ_FILE = "codereview/input/quiz/survey.xlsx"
BASE_FILE = "codereview/input/base/base.xlsx"
PRIORITIZED_FILE = "codereview/input/priorizados/squads_priorizados.xlsx"
PR_FILE = "codereview/input/prs/*.xlsx"
COMMIT_FILE = "codereview/input/commits/*.xlsx"
OUTPUT_PATH = "codereview/output/"

ARRAY_VARIABLES_PR = ["commits","files","lines","reviewers","lines_in_pr","time","tasks_and_comments"]
ARRAY_VARIABLES_QUIZ = ["standard_commit","atomic_commit","creation_pr","decline_pr","comment_pr","approve_pr"]

EXTENSIONS_FOR_SPECIALTIES_UT = ["java","js","ts","tsx","kt","swift"]

COMMIT_TYPE_GUIDELINES = ["feat", "fix", "perf", "refactor", "test", "ci", "other"]

PR_STATUS = {"MERGED": { "column": column_status, "validate": False},
             "OPEN": {"column": column_status, "validate": True}, 
             "DECLINED": {"column": column_status, "validate": False}}

PR_STATUS_PATH = "codereview/output/"
PR_STATUS_FILE = "-prs_with-status.csv"

COLUMN_NAME_REPO_EXCLUDED = "Repositorio"
COLUMN_NAME_BRANCH_EXCLUDED = "Branch"
TYPE_REGS_EXCLUSION = "ExpresionRegular"

LEGACY_NAME = "LEGACY"

PATH_LAST_PROCESS = "codereview/input/last_process/"
FILE_LAST_PROCESS_THIRD_MODEL = "-cr-maturity-level-by-squad"

SPECIALITIES = ["BACKEND JAVA", "FRONTEND WEB", "FRONTEND IOS", "FRONTEND ANDROID", "GENERAL"]
SPECIALITIES_SCOPE = ["BACKEND JAVA", "FRONTEND WEB", "FRONTEND IOS", "FRONTEND ANDROID"]
SPECIALTY_GENERAL:str = "GENERAL"

YES = "Y"
NO = "N"

COMPLEXITY_WEIGHT = {"files_weight": 0.25,
                     "lines_weight": 0.25,
                     "commits_weight": 0.2,
                     "lines_in_pr_weight": 0.3}

HANDLING_COMMITS_WEIGHT = {"standard_commit_weight": 0.1, 
                           "atomic_commit_weight": 0.1, 
                           "commits_weight": 0.3 , 
                           "files_weight": 0.25, 
                           "lines_weight": 0.25
                           }

PR_CREATION_WEIGHT = {"creation_pr_weight": 0.1, 
                      "reviewers_weight": 0.6, 
                      "pr_declined_weight": 0.3
                      }

PR_REVIEW_WEIGHT = {"time_weight": 0.7, 
                    "lines_in_pr_weight": 0.2, 
                    "decline_pr_weight": 0.1
                    }

PR_COMMENTS_WEIGHT = {"comment_pr_weight": 0.5, 
                      "tasks_and_comments_weight": 0.5
                      }

OPEN_PR_PENALTY_WEIGTH = 0.5

METRICS_WEIGHT = {"handling_commits_weight": 0.25,
                  "pr_creation_weight": 0.15,
                  "pr_review_weight": 0.35,
                  "pr_comments_weight": 0.2,
                  "approve_pr_weight": 0.05
                  }