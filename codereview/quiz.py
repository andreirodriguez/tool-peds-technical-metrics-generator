import pandas as pd

import codereview.maturity_points as util
from codereview.tm_data_base import getValueBaseActivosByTeamMember
from codereview.util import extract_squad_tribe_id
from codereview.cr_constants import ARRAY_VARIABLES_QUIZ, QUIZ_FILE
from codereview.pull_request_data_utils import current_date_formated, first_day_custom_date

def get_data_quiz(base, period) -> pd.DataFrame:
    print("Getting result of quiz")

    usecols=[0,1,2]
    names=["team_member_code","fullname","email"]

    count = 4
    for metric in ARRAY_VARIABLES_QUIZ:
        usecols.append(count)
        names.append(metric)
        count += 1

    quiz_result = pd.read_excel(QUIZ_FILE, header=0, usecols = usecols, names = names)

    quiz_result["team_member_code"] = quiz_result.apply(lambda quiz: str(quiz["team_member_code"]).upper(), axis=1)

    base = base.sort_values(['team_member_code','squad','fecha_actualizado'], ascending = [True,True,False])
    base: pd.DataFrame = base.drop_duplicates(subset=["team_member_code","squad_code"], keep="first")

    quiz_result = pd.merge(quiz_result, base[['team_member_code', 'squad','specialty','squad_code']], on="team_member_code", how="left")

    quiz_result["analysis_date"] = first_day_custom_date(period[4:6], period[0:4])
    quiz_result["execution_date"] = current_date_formated()

    return quiz_result


def get_note_per_variable(quiz_result) -> pd.DataFrame:
    print("Getting point per variable for the quiz")

    for metric in ARRAY_VARIABLES_QUIZ:
        quiz_result[metric + "_points"] = quiz_result.apply(lambda q: util.get_quiz_points(q[metric]), axis=1)

    return quiz_result