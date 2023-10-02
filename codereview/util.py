import csv
import pandas as pd
import re
import codereview.util as util
import math

from codereview.cr_constants import EXCLUSIONS_FILE, COLUMN_NAME_REPO_EXCLUDED,\
      OUTPUT_PATH, PR_STATUS_PATH, PR_STATUS_FILE, SPECIALITIES, SPECIALTY_GENERAL, YES, NO
from codereview.headers_columns_util import column_pr_with_commits_info, column_quiz_note_per_variable, \
    column_maturity_level_by_squad, columns_summary, column_status, columns_summary_propened, xls_report_columns

def get_technology_type(repository, app, specialty_file, column:str):
    specialty_file = specialty_file[(specialty_file["repository_name"] == repository) & (specialty_file["project"] == app)]
    return "" if specialty_file.empty else specialty_file.iloc[0][column]

def get_specialty(repository, app, team_member_code, specialty_file, base):

    specialty_file = specialty_file[(specialty_file["repository_name"] == repository) & (specialty_file["project"] == app)]
    specialty_file.fillna("", inplace=True)

    specialty_from_master = "" if specialty_file.empty else specialty_file.iloc[0]["specialty"]

    if len(specialty_from_master) == 0:
        team_member = base[(base['team_member_code'] == team_member_code)]
        team_member.fillna("", inplace=True)

        specialty_from_base = "" if team_member.empty else team_member.iloc[0]["specialty"]

        return specialty_from_base
    else: 
        return specialty_from_master
    
def get_squad_tribe_from_base(author_with_prefix, base, column):
    team_member = base[(base['author_with_prefix'] == author_with_prefix)]
    team_member.fillna("", inplace=True)

    value = "" if team_member.empty else team_member.iloc[0][column]

    return value

def extract_squad_tribe_id(large_name):
    large_name = str(large_name)
    match_expr = re.search('\[(.+?)\]', large_name)

    if match_expr == None:
        match_expr = re.search('\((.+?)\)', large_name)
    
    if match_expr:
        return match_expr.group(1)
    else:
        return ''
    

def import_csv(status, period):
    data_result = pd.read_csv(PR_STATUS_PATH + period + PR_STATUS_FILE, dtype={"squad_code": str})

    data_result = data_result[data_result["status"] == status]    
    return data_result


def extract_repo_name(repository_string):
    match = re.search(r'\/repos\/([^\/]+)', repository_string)
    if match:
        repository = match.group(1)
        return repository
    else:
        return repository_string
    
def get_repo_branch_excluded(type_of_exclusion: str):
    file = EXCLUSIONS_FILE

    ignored_result = pd.read_excel(file, usecols=[type_of_exclusion], sheet_name = type_of_exclusion)

    if type_of_exclusion == COLUMN_NAME_REPO_EXCLUDED:
        ignored_result[type_of_exclusion] = ignored_result.apply(lambda x:extract_repo_name(x[type_of_exclusion]), axis=1)

    ignored_result = ignored_result.drop_duplicates(subset=[type_of_exclusion], keep="last")

    return ignored_result

def get_list_variables_from_exclusion_file(type_of_variable: str):
    file = EXCLUSIONS_FILE

    list_variables = pd.read_excel(file, usecols=['Tipo', 'Variable', 'Valor'], sheet_name = 'Variables')
    list_variables = list_variables[list_variables['Tipo'] == type_of_variable]

    return list_variables

def export_final_csv(file_name, headers, df, columns):
    df = df[columns]

    df.to_csv(OUTPUT_PATH + file_name, quoting = csv.QUOTE_ALL, index=False, header= headers, encoding="utf-8")

def get_previous_period(period):
    year = period[0:4]
    month = period[4:6]

    year = int(year)
    month = int(month)

    month, year = (12, year-1) if month == 1 else (month-1, year)
    previous_period = str(year) + str(month).zfill(2)

    return previous_period

def get_team_member_id_without_zero(codeTeamMember:str):
    codeTeamMember = codeTeamMember.upper().strip()
    firstZero = codeTeamMember[0:1]
    if(firstZero == "0"): codeTeamMember = codeTeamMember[1:len(codeTeamMember)]
    return codeTeamMember


def set_export_excel_summary(period, team_member_data_base, pr_with_variable_note, 
                             quiz_with_variable_point, squad_maturity_level_array, pr_with_variable_note_filter):
    print("Make a summary report.")
    file = OUTPUT_PATH + period + "-cr-maturity-level-by-squad-summary.xlsx"
    resume_array = []

    new_pr_with_variable_note_filter = pr_with_variable_note_filter.copy()
    new_pr_with_variable_note_filter['identifier'] = new_pr_with_variable_note_filter['app'].str.cat(new_pr_with_variable_note_filter['repo']).str.cat(new_pr_with_variable_note_filter['prid'].astype(str))
    scope = new_pr_with_variable_note_filter['identifier'].to_numpy().tolist()

    new_pr_with_variable_note = pr_with_variable_note.copy()
    new_pr_with_variable_note['identifier'] = new_pr_with_variable_note['app'].str.cat(new_pr_with_variable_note['repo']).str.cat(new_pr_with_variable_note['prid'].astype(str))

    new_pr_with_variable_note['scope'] = new_pr_with_variable_note.apply(lambda pr: YES if pr['identifier'] in scope else NO, axis = 1)
    with pd.ExcelWriter(file) as writer:
        countSquad:int = 0
        for specialty in SPECIALITIES:
            squad_maturity_level_array[countSquad].to_excel(writer, sheet_name=specialty, columns=column_maturity_level_by_squad, index=False)
            resume_array.append(get_summary(squad_maturity_level_array[countSquad], specialty))
            countSquad += 1

        pr_declined = util.import_csv("DECLINED", period)
        pr_opened = util.import_csv("OPEN", period)
        pr_with_status = pd.concat([pr_declined, pr_opened])
        summary_open_pr_df = get_summary_pr(pr_opened)
        resume_df = pd.DataFrame(resume_array, columns = columns_summary)
        summmary_amounts = get_data_per_group(squad_maturity_level_array)

        new_columns = column_pr_with_commits_info.copy()
        new_columns.append("scope")

        new_pr_with_variable_note.to_excel(writer, sheet_name="PULL REQUESTS", columns=new_columns, index=False)
        pr_with_status.to_excel(writer, sheet_name="PR ABIERTO DECLINADO", columns=column_status, index=False)
        quiz_with_variable_point.to_excel(writer, sheet_name="QUIZ TESTS", columns=column_quiz_note_per_variable, index=False)
        team_member_data_base.to_excel(writer, sheet_name="BASE ACTIVOS", index=False)
        resume_df.to_excel(writer, sheet_name="RESUMEN", index=False)
        summary_open_pr_df.to_excel(writer, sheet_name="PR ABIERTOS RESUMEN", index=False)
        summmary_amounts.to_excel(writer, sheet_name="CANTIDADES", index=False)

def get_summary(squad_maturity_level, specialty):
    group_1_2 = round(squad_maturity_level[(squad_maturity_level['group']==1) | (squad_maturity_level['group']==2)]["maturity_level"].mean(),2)
    group_3 = round(squad_maturity_level[(squad_maturity_level['group']==3)]["maturity_level"].mean(),2)
    all = round(squad_maturity_level["maturity_level"].mean(),2)

    return [specialty, group_1_2, group_3, all]

def get_summary_pr(pr_opened):
    summary_open_pr = []
    for specialty in SPECIALITIES:
        if specialty != SPECIALTY_GENERAL:
            amount = pr_opened[pr_opened['specialty'] == specialty].shape[0]
            summary_open_pr.append([specialty, amount])

    summary_open_pr_df = pd.DataFrame(summary_open_pr, columns = columns_summary_propened)
    return summary_open_pr_df

def get_data_per_group(squads_with_maturity_level)->pd.DataFrame:
    xls_report = []
    squads:pd.DataFrame = None
    squadsByGroup:pd.DataFrame = None
    nmApproved:float = 0.0
    count = 0
    for specialty in SPECIALITIES:
        squads = squads_with_maturity_level[count]
        nmApproved = 4
        if(specialty == "FRONTEND IOS" or specialty == "FRONTEND ANDROID"): nmApproved = 3
        squadsByGroup = squads[(squads['group'].isin([1,2]))]
        group_1_2_approved = squadsByGroup[squadsByGroup['maturity_level'] >= nmApproved].shape[0]
        group_1_2_disapprove = squadsByGroup[squadsByGroup['maturity_level'] < nmApproved].shape[0]
        group_1_2_without_maturity_level = squadsByGroup[squadsByGroup['maturity_level'].isnull()].shape[0]
        group_1_2_total = squadsByGroup.shape[0]
        nmApproved = 3.5
        squadsByGroup = squads[(squads['group'].isin([3]))]
        group_3_approved = squadsByGroup[squadsByGroup['maturity_level'] >= nmApproved].shape[0]
        group_3_disapprove = squadsByGroup[squadsByGroup['maturity_level'] < nmApproved].shape[0]
        group_3_without_maturity_level = squadsByGroup[squadsByGroup['maturity_level'].isnull()].shape[0]
        group_3_total = squadsByGroup.shape[0]
        without_maturity = group_1_2_without_maturity_level + group_3_without_maturity_level
        all_squads = len(squads)
        xls_report.append([specialty, group_1_2_approved, group_1_2_disapprove, group_1_2_without_maturity_level, group_1_2_total, group_3_approved, 
                         group_3_disapprove, group_3_without_maturity_level, group_3_total, without_maturity, all_squads])
        xls_report_df = pd.DataFrame(xls_report, columns = xls_report_columns)
        count += 1

    return xls_report_df

def isNotNumber(value)->bool:
    if(value==None): return True

    if(math.isnan(value)): return True

    return False