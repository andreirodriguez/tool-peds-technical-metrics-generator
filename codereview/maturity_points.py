import math
import pandas as pd
import codereview.util as util

from typing import List
from codereview.cr_constants import ARRAY_VARIABLES_QUIZ, ARRAY_VARIABLES_PR,\
     LEGACY_NAME, HANDLING_COMMITS_WEIGHT,PR_CREATION_WEIGHT,\
    PR_REVIEW_WEIGHT, PR_COMMENTS_WEIGHT, METRICS_WEIGHT, COMPLEXITY_WEIGHT, OPEN_PR_PENALTY_WEIGTH,\
    SPECIALITIES_SCOPE, SPECIALTY_GENERAL
from codereview.pull_request_data_utils import current_date_formated, first_day_custom_date
from codereview.util import isNotNumber

max_point = 5
min_point = 1

def get_commit_points(commit_value: float):
    ranges = {1:{"min": 8},
              2:{"min": 6, "max": 8},
              3:{"min": 5, "max": 5},
              4:{"min": 3, "max": 5},
              5:{"min": 0, "max": 3}}

    return get_points_majorequal_minor(ranges, commit_value)

def get_files_average_points(files: List[int], application_type):
    accumulated_file_points = 0

    if len(files) == 0:
        return 5

    for file in files:
        accumulated_file_points = accumulated_file_points + get_file_commit_point(file, application_type)

    return round(accumulated_file_points / len(files), 2)

def get_file_commit_point(file_value: float, application_type):  
    if application_type == LEGACY_NAME:
        ranges = {1:{"min": 60},
              2:{"min": 50, "max": 60},
              3:{"min": 40, "max": 50},
              4:{"min": 35, "max": 40},
              5:{"min": 0, "max": 35}}
    else:
        ranges = {1:{"min": 40},
                2:{"min": 30, "max": 40},
                3:{"min": 20, "max": 30},
                4:{"min": 15, "max": 20},
                5:{"min": 0, "max": 15}}

    return get_points_majorequal_minor(ranges,file_value)

def get_lines_average_points(files: List[int], lines: List[int], application_type):
    accumulated_lines_points = 0

    if len(files) == 0:
        return 5

    for index, file in enumerate(files):
        accumulated_lines_points = accumulated_lines_points + get_line_commit_point(lines[index], application_type)

    return round(accumulated_lines_points / len(files), 2)

def get_line_commit_point(file_value: float, application_type):  
    if application_type == LEGACY_NAME:
        ranges = {1:{"min": 400},
              2:{"min": 300, "max": 400},
              3:{"min": 200, "max": 300},
              4:{"min": 150, "max": 200},
              5:{"min": 0, "max": 150}}
    else:
        ranges = {1:{"min": 350},
              2:{"min": 250, "max": 350},
              3:{"min": 150, "max": 250},
              4:{"min": 100, "max": 150},
              5:{"min": 0, "max": 100}}

    return get_points_majorequal_minor(ranges,file_value)

def get_reviewer_point(reviewer_value: int):  

    ranges = {2:{"reviewer": 0},
              3:{"reviewer": 1},
              4:{"reviewer": 2},
              5:{"reviewer": 3}}

    for point, values in ranges.items():
        if reviewer_value == values['reviewer']:
            return point
        elif point == max_point and values['reviewer'] <= reviewer_value:
            return point
    return 0

def get_pr_declined_amount(squad_code, pr_declined, specialty, squad_maturity_level_array = None):
    if(specialty == SPECIALTY_GENERAL):
        specialties = getSpecialitysBySquadsPrioritized(squad_code,squad_maturity_level_array, True)
        pr_declined = pr_declined[(pr_declined["squad_code"] == squad_code) & (pr_declined['specialty'].isin(specialties))]
    else:
        pr_declined = pr_declined[(pr_declined['squad_code'] == squad_code) & (pr_declined['specialty'] == specialty)]

    declined_prs_count = pr_declined.shape[0]

    return declined_prs_count

def get_declined_pr_points(declined_prs_count):  
    ranges = {1:{"pr_decline": 3},
              2:{"pr_decline": 2},
              3:{"pr_decline": 1},
              5:{"pr_decline": 0}}

    for point, values in ranges.items():
        if point != min_point and values['pr_decline'] <= declined_prs_count:
            return point
        
        elif declined_prs_count == values['pr_decline']:
            return point
        
    return 0

def get_opened_prs_amount(pr_opened, squad_code, specialty, squad_maturity_level_array = None):
    if(specialty == SPECIALTY_GENERAL):
        specialties = getSpecialitysBySquadsPrioritized(squad_code,squad_maturity_level_array, True)
        pr_opened = pr_opened[(pr_opened["squad_code"] == squad_code) & (pr_opened['specialty'].isin(specialties))]
    else:
        pr_opened = pr_opened[(pr_opened['squad_code'] == squad_code) & (pr_opened['specialty'] == specialty)]

    opened_prs_count = pr_opened.shape[0]

    return opened_prs_count

def get_opened_prs_points(opened_prs_count):
    if opened_prs_count > 0:
        return OPEN_PR_PENALTY_WEIGTH

    return 0

def get_time_points(current_time: float, complexity_points: float):

    if 3 < complexity_points <= 5:
        if current_time > 32:
            return 1

        if 20 < current_time <= 32:
            return 2

        if 8 < current_time <= 20:
            return 3

        if 4 < current_time <= 8:
            return 4

        if current_time <= 4:
            return 5
    elif 0 <= complexity_points <= 3:
        if (current_time > 32) or (current_time <= 0.5):
            return 1

        if (20 < current_time <= 32) or (0.5 < current_time <= 1):
            return 2

        if 8 < current_time <= 20:
            return 3

        if 4 < current_time <= 8:
            return 4

        if current_time <= 4:
            return 5

    return 0

def get_line_pr_points(line_value: float, application_type):  
    
    if application_type == LEGACY_NAME:
        ranges = {1:{"min": 1200},
              2:{"min": 700, "max": 1200},
              3:{"min": 500, "max": 700},
              4:{"min": 100, "max": 500},
              5:{"min": 0, "max": 100}}
    else:
        ranges = {1:{"min": 1200},
                2:{"min": 500, "max": 1200},
                3:{"min": 300, "max": 500},
                4:{"min": 50, "max": 300},
                5:{"min": 0, "max": 50}}

    return get_points_major_minorequal(ranges, line_value)

def get_tasks_and_comments_points(complexity_points: float, comments: int, solved_tasks: int):
    solved_tasks_and_comments = solved_tasks + comments

    if 0 <= complexity_points < 3:
        if solved_tasks == 0 and comments == 0:
            return 1
        if solved_tasks_and_comments == 1:
            return 2
        if 1 < solved_tasks_and_comments <= 5:
            return 3
        if 5 < solved_tasks_and_comments <= 10:
            if solved_tasks > 5:
                return 5
            return 4
        return 5

    if 3 <= complexity_points < 4:
        if solved_tasks == 0 and comments == 0:
            return 2
        if 1 <= solved_tasks_and_comments < 3:
            return 3

        if solved_tasks >= 3:
            return 5

        if solved_tasks_and_comments >= 3:
            return 4
        
    if 4 <= complexity_points < 5:
        if solved_tasks == 0 and comments == 0:
            return 3

        if solved_tasks >= 2:
            return 5

        if solved_tasks_and_comments >= 1:
            return 4
    else:
        if solved_tasks_and_comments == 0:
            return 4

        if solved_tasks_and_comments >= 1:
            return 5

    return 0

def get_complexity_points(files_points: float, lines_points: float,
                                commits_points: int, lines_in_pr_points: int):
    return (
            files_points * COMPLEXITY_WEIGHT["files_weight"]
            + lines_points * COMPLEXITY_WEIGHT["lines_weight"]
            + commits_points * COMPLEXITY_WEIGHT["commits_weight"]
            + lines_in_pr_points * COMPLEXITY_WEIGHT["lines_in_pr_weight"]
    )

def get_points_majorequal_minor(ranges: dict[int, dict[str]], value:float):
    if value is None or math.isnan(value): 
        return None

    for point, values in ranges.items():
        if point == min_point:
            if values['min'] <= value:
                return point
            continue

        elif point == max_point:
            if values['min'] <= value < values['max']:
                return point
            continue
        
        elif(values['min'] <= value < values['max']):
            return point

    return 0

def get_points_major_minorequal(ranges: dict[int, dict[str]], value:float):
    
    if value is None or math.isnan(value): 
        return None

    for point, values in ranges.items():
        if point == min_point:
            if values['min'] < value:
                return point
            continue

        if point == max_point:
            if values['min'] <= value <= values['max']:
                return point
            continue
        
        elif(values['min'] < value <= values['max']):
            return point

    return 0

def get_quiz_points(quiz_value: float):  
    ranges = {1:{"min": 0, "max": 20},
              2:{"min": 20, "max": 50},
              3:{"min": 50, "max": 65},
              4:{"min": 65, "max": 80},
              5:{"min": 80, "max": 100}}

    return get_quiz_points_majorequal_minor(ranges, quiz_value)

def get_quiz_points_majorequal_minor(ranges: dict[int, dict[str]], quiz_value:float):
    if quiz_value is None or math.isnan(quiz_value): 
        return None

    for point, values in ranges.items():
        if point != max_point and values['min'] <= quiz_value < values['max']:
            point_to_return = point + (quiz_value - values['min']) * (100/(values['max'] - values['min'])/100)
            return round(point_to_return, 2) 
        
        elif(values['min'] <= quiz_value <= values['max']):
            return point
        
    return math.nan

def get_maturity_by_squad(pr_with_variable_note, quiz_with_variable_point, specialty, squads_prioritized, period):
    print("--------------------------------------------Getting metric by squad for " + specialty)
    # previous_note = get_previous_note(period, specialty)
    squads_prioritized["analysis_date"] = first_day_custom_date(period[4:6], period[0:4])
    squads_prioritized["execution_date"] = current_date_formated()

    for metric in ARRAY_VARIABLES_QUIZ:
        variable = metric + "_points"
        squads_prioritized[variable] = squads_prioritized.apply(lambda squad: get_mean_by_squad_and_specialty(
            squad["squad_code"], specialty, quiz_with_variable_point, variable), axis=1)

    for metric in ARRAY_VARIABLES_PR:
        variable = metric + "_points"
        squads_prioritized[variable] = squads_prioritized.apply(lambda squad: get_mean_by_squad_and_specialty(
            squad["squad_code"], specialty, pr_with_variable_note, variable), axis=1)

        # get previous note if it doesn't has
        # squads_prioritized["execution_date"] = squads_prioritized.apply(lambda squad: get_execution_date(
        #     squad["squad_code"], specialty, previous_note, squad["execution_date"]) if math.isnan(squad[variable]) else squad["execution_date"], axis=1)
        
        # squads_prioritized[variable] = squads_prioritized.apply(lambda squad: get_mean_by_squad_and_specialty(
        #     squad["squad_code"], specialty, previous_note, variable) if math.isnan(squad[variable]) else squad[variable], axis=1)

    squads_prioritized = get_note_per_metric(squads_prioritized, specialty, period)
    squads_without_note = squads_prioritized[squads_prioritized["maturity_level"].isna()].copy()

    print("----------------------Squads que no tendran nivel de madurez")
    print(squads_without_note["squad"].values)

    return squads_prioritized

def get_maturity_by_squad_general(squads_prioritized, squad_maturity_level_array, period, pr_with_variable_note, quiz_with_variable_point):

    squads_prioritized["analysis_date"] = first_day_custom_date(period[4:6], period[0:4])
    squads_prioritized["execution_date"] = current_date_formated()

    for metric in ARRAY_VARIABLES_QUIZ:
        variable = metric + "_points"
        squads_prioritized[variable] = squads_prioritized.apply(lambda squad: get_mean_by_squad_general(
            squad["squad_code"], quiz_with_variable_point, variable, squad_maturity_level_array), axis=1)

    for metric in ARRAY_VARIABLES_PR:
        variable = metric + "_points"
        squads_prioritized[variable] = squads_prioritized.apply(lambda squad: get_mean_by_squad_general(
            squad["squad_code"], pr_with_variable_note, variable, squad_maturity_level_array), axis=1)
    
    squads_prioritized = get_note_per_metric(squads_prioritized, SPECIALTY_GENERAL, period, squad_maturity_level_array)
    squads_without_note = squads_prioritized[squads_prioritized["maturity_level"].isna()].copy()

    print("----------------------Squads que no tendran nivel de madurez")
    print(squads_without_note["squad"].values)

    return squads_prioritized

def get_mean_by_squad_and_specialty(squad_code:str, specialty:str, data:pd.DataFrame, property:str)->float:
    
    dataBySquad = data[(data['squad_code'] == squad_code) & (data['specialty'] == specialty)]

    value = dataBySquad[property].mean()

    if(math.isnan(value)): 
        return math.nan

    return round(value, 2)

def get_mean_by_squad_general(squad_code:str, data:pd.DataFrame, property:str, squad_maturity_level_array):
    
    specialties = getSpecialitysBySquadsPrioritized(squad_code, squad_maturity_level_array, True)
    dataBySquad = data[(data['squad_code'] == squad_code) & (data['specialty'].isin(specialties))]

    value = dataBySquad[property].mean()

    if(math.isnan(value)): 
        return math.nan

    return round(value, 2)

def getSpecialitysBySquadsPrioritized(squadCode:str,squadsPrioritized,withMaturityLevel:bool)->float:
    specialities = []

    countSquad:int = 0
    for specialty in SPECIALITIES_SCOPE:
        squads = squadsPrioritized[countSquad]
        squads = squads[(squads['squad_code']==squadCode)]
        countSquad += 1
        if(len(squads)==0): continue

        #SI ESA ESPECIALIDAD NO TIENE NIVEL DE MADUREZ
        if(withMaturityLevel):
            if(isNotNumber(squads.iloc[0]["maturity_level"])): continue

        specialities.append(specialty)    

    return specialities

def get_note_per_metric(squads_prioritized, specialty, period, squad_maturity_level_array = None ):
    pr_declined = util.import_csv("DECLINED", period)
    pr_opened = util.import_csv("OPEN", period)

    squads_prioritized["pr_declined_amount"] = squads_prioritized.apply(lambda squad: get_pr_declined_amount(
        squad["squad_code"], pr_declined, specialty, squad_maturity_level_array), axis=1)

    squads_prioritized["declined_amount_points"] = squads_prioritized.apply(lambda squad: get_declined_pr_points(
        squad["pr_declined_amount"]), axis=1)

    squads_prioritized["handling_commits_metric"] = squads_prioritized.apply(lambda squad: get_handling_commits_points(
        squad["standard_commit_points"], squad["atomic_commit_points"], 
        squad["commits_points"], squad["files_points"], squad["lines_points"]), axis=1)
    
    squads_prioritized["pr_creation_metric"] = squads_prioritized.apply(lambda squad: get_pr_creation_points(
        squad["reviewers_points"], squad["creation_pr_points"], squad["declined_amount_points"]), axis=1)
    
    squads_prioritized["pr_review_metric"] = squads_prioritized.apply(lambda squad: get_pr_review_points(
        squad["lines_in_pr_points"], squad["time_points"], squad["decline_pr_points"]), axis=1)
    
    squads_prioritized["pr_comments_metric"] = squads_prioritized.apply(lambda squad: get_pr_comments_points(
        squad["comment_pr_points"], squad["tasks_and_comments_points"]), axis=1)
    
    squads_prioritized["pr_open_amount"] = squads_prioritized.apply(lambda squad: get_opened_prs_amount(
        pr_opened, squad["squad_code"], specialty, squad_maturity_level_array), axis=1)

    squads_prioritized["opened_prs_penalty"] = squads_prioritized.apply(lambda squad: get_opened_prs_points(
        squad["pr_open_amount"]), axis=1)
    
    squads_prioritized["maturity_level"]= squads_prioritized.apply(lambda squad: get_maturity_level(
        squad["handling_commits_metric"], squad["pr_creation_metric"], squad["pr_review_metric"],
        squad["pr_comments_metric"], squad["approve_pr_points"], squad["opened_prs_penalty"]), axis=1)
    
    return squads_prioritized

def get_handling_commits_points(standard_commit_points: float, atomic_commit_points: float, 
                                commits_points: float, files_points: float, lines_points: float):
    
    if math.isnan(standard_commit_points) and math.isnan(atomic_commit_points):
        survey_weight = HANDLING_COMMITS_WEIGHT["standard_commit_weight"] + HANDLING_COMMITS_WEIGHT["atomic_commit_weight"]

        result = commits_points * (HANDLING_COMMITS_WEIGHT["commits_weight"] + (survey_weight/3)) + \
             files_points * (HANDLING_COMMITS_WEIGHT["files_weight"] + (survey_weight/3)) +  \
             lines_points * (HANDLING_COMMITS_WEIGHT["lines_weight"] + (survey_weight/3))
    else:
        result = standard_commit_points * HANDLING_COMMITS_WEIGHT["standard_commit_weight"] + \
                atomic_commit_points * HANDLING_COMMITS_WEIGHT["atomic_commit_weight"] +  \
                commits_points * HANDLING_COMMITS_WEIGHT["commits_weight"] + \
                files_points * HANDLING_COMMITS_WEIGHT["files_weight"] +  \
                lines_points * HANDLING_COMMITS_WEIGHT["lines_weight"]
        
    return round(result, 2)

def get_pr_creation_points(reviewers_points: float, creation_pr_points: float, pr_declined_points):
    if math.isnan(creation_pr_points):
        result = reviewers_points * (PR_CREATION_WEIGHT["reviewers_weight"] + (PR_CREATION_WEIGHT["creation_pr_weight"]/2)) + \
                pr_declined_points * (PR_CREATION_WEIGHT["pr_declined_weight"] + (PR_CREATION_WEIGHT["creation_pr_weight"]/2) )
    else:
        result = reviewers_points * PR_CREATION_WEIGHT["reviewers_weight"] + \
                creation_pr_points * PR_CREATION_WEIGHT["creation_pr_weight"] + \
                pr_declined_points * PR_CREATION_WEIGHT["pr_declined_weight"]
        
    return round(result, 2)
           
def get_pr_review_points(lines_in_pr_points: float, time_points: float, decline_pr_points: float):
    if math.isnan(decline_pr_points):
        result = lines_in_pr_points * (PR_REVIEW_WEIGHT["lines_in_pr_weight"] + (PR_REVIEW_WEIGHT["decline_pr_weight"]/2)) + \
                time_points * (PR_REVIEW_WEIGHT["time_weight"] + (PR_REVIEW_WEIGHT["decline_pr_weight"]/2))
    else:
        result = lines_in_pr_points * PR_REVIEW_WEIGHT["lines_in_pr_weight"] + \
                time_points * PR_REVIEW_WEIGHT["time_weight"] +  \
                decline_pr_points * PR_REVIEW_WEIGHT["decline_pr_weight"]
    return round(result, 2)


def get_pr_comments_points(comment_pr_points: float, tasks_and_comments_points: float):
    if math.isnan(comment_pr_points):
        result = tasks_and_comments_points
    else:
        result = comment_pr_points * PR_COMMENTS_WEIGHT["comment_pr_weight"] + \
                tasks_and_comments_points * PR_COMMENTS_WEIGHT["tasks_and_comments_weight"]
        
    return round(result, 2)


def get_maturity_level(handling_commits_points: float, pr_creation_points: float, pr_review_points: float,
                       pr_comments_points: float, approve_pr_points: float, opened_prs_penalty: float):
    if math.isnan(approve_pr_points):
        result = handling_commits_points * METRICS_WEIGHT["handling_commits_weight"] + \
                pr_creation_points * METRICS_WEIGHT["pr_creation_weight"] + \
                pr_review_points * (METRICS_WEIGHT["pr_review_weight"] + METRICS_WEIGHT["approve_pr_weight"]) + \
                pr_comments_points * METRICS_WEIGHT["pr_comments_weight"] - \
                opened_prs_penalty
    else:
        result = handling_commits_points * METRICS_WEIGHT["handling_commits_weight"] + \
                pr_creation_points * METRICS_WEIGHT["pr_creation_weight"] + \
                pr_review_points * METRICS_WEIGHT["pr_review_weight"] + \
                pr_comments_points * METRICS_WEIGHT["pr_comments_weight"] + \
                approve_pr_points * METRICS_WEIGHT["approve_pr_weight"] - \
                opened_prs_penalty
    return round(result, 2)
