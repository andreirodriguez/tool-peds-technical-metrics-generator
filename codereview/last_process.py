import pandas as pd
from codereview.cr_constants import PATH_LAST_PROCESS, FILE_LAST_PROCESS_THIRD_MODEL, SPECIALITIES
from codereview.util import get_previous_period
 
def get_previous_note(period, specialty):
    previous_period = get_previous_period(period)

    if specialty == "GENERAL":
        file = PATH_LAST_PROCESS + previous_period + FILE_LAST_PROCESS_THIRD_MODEL + ".csv" 
    else: file = PATH_LAST_PROCESS + previous_period + FILE_LAST_PROCESS_THIRD_MODEL + "-" + specialty + ".csv" 
    previous = pd.read_csv(file,encoding="utf-8", dtype=str)
    previous["specialty"] = specialty

    return previous


def get_execution_date(squad_code, specialty, previous_note, analysis_date):
    previous_note = previous_note[(previous_note["squad_code"] == squad_code) & 
                                  (previous_note["specialty"] == specialty)]

    return analysis_date if previous_note.empty else previous_note.iloc[0]["execution_date"]