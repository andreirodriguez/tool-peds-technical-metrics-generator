import glob
import pandas as pd
import json
from typing import List

import codereview.maturity_points as maturity_util
import codereview.util as util
import codereview.pull_request_data_utils as pr_util
from codereview.commit_v3 import get_commit, get_pr_with_commit_detail
from codereview.prioritized_squads import get_squads_with_specialty_prioritized
from codereview.cr_constants import PR_FILE, PR_STATUS, COLUMN_NAME_REPO_EXCLUDED, \
    COLUMN_NAME_BRANCH_EXCLUDED, CSV_SPECIALTY_FILE, PR_STATUS_PATH, PR_STATUS_FILE, SPECIALITIES, \
    TYPE_REGS_EXCLUSION, EXTENSIONS_FOR_SPECIALTIES_UT, OUTPUT_PATH, YES, NO
from codereview.headers_columns_util import header_status
from codereview.tm_data_base import get_squad_of_team_member

def get_data_pr():
    print("Getting all prs with exclusions")

    pr_files = glob.glob(PR_FILE)
    pr_files.sort() 
    pr_xls_files: List[pd.DataFrame] = []

    for pr in pr_files:
        pr_xls_files.append(
            pd.read_excel(pr, header = 2,
                          usecols = [0,1,2,3,4,5,6,7,8,9,10,11,13,16,17,18,19,20,21],
                          names = ['app','repo','title','prid','origin_branch','target_branch',
                                 'status','modified_files','add_lines','delete_lines',
                                 'create_date','close_date','author','reviewers','solved_task',
                                 'opened_task','comments','generation_date','modified_extensions']))

    prs_raw: pd.DataFrame = pd.concat(pr_xls_files).drop_duplicates(subset=["repo", "prid"], keep="last")

    return prs_raw

def exclude_repo_branch(prs_raw_initial):

    ignored_repos = util.get_repo_branch_excluded(COLUMN_NAME_REPO_EXCLUDED)
    bad_origin_branch = util.get_repo_branch_excluded(COLUMN_NAME_BRANCH_EXCLUDED)

    prs_with_exclude = prs_raw_initial[(~prs_raw_initial["repo"].isin(ignored_repos.Repositorio.values)) & 
                    (~prs_raw_initial["origin_branch"].isin(bad_origin_branch.Branch.values))]
    prs_with_exclude = prs_with_exclude[prs_with_exclude["origin_branch"] != "develop"]
    prs_with_exclude = exclude_repo_branch_with_regex(prs_with_exclude)
    prs_with_exclude["modified_lines_in_pr"] = prs_with_exclude.apply(lambda row: row["add_lines"] + row["delete_lines"], axis=1)
    prs_with_exclude = prs_with_exclude[prs_with_exclude["modified_lines_in_pr"] != 0]
    
    return prs_with_exclude

def exclude_repo_branch_with_regex(prs_with_exclude):
    print("Exclude prs matching with regular expresion")

    list_variables = util.get_list_variables_from_exclusion_file(TYPE_REGS_EXCLUSION)
    for index, row in list_variables.iterrows():
      column = row[1]
      value = row[2]
      prs_with_exclude = prs_with_exclude[~prs_with_exclude[column].str.match(value)]

    return prs_with_exclude

def get_pull_request(base, period):
    print("Add important information to prs data")

    prs_raw_initial = get_data_pr()
    prs_raw_initial = get_modify_functionality(prs_raw_initial, period)
    prs_raw = exclude_repo_branch(prs_raw_initial)
    
    specialty_file = pd.read_csv(CSV_SPECIALTY_FILE)

    prs_raw["team_member_code"] = prs_raw["author"].apply(pr_util.get_author_id_from_author_full_name)

    prs_raw["repo_with_pr_id"] = prs_raw.apply(lambda row: row["repo"] + " - " + str(row["prid"]), axis=1)
    
    prs_raw['status'] = prs_raw['status'].apply(lambda x: str(x).upper())
    
    prs_raw["creation_date_in_timestamp"] = prs_raw["create_date"].apply(pr_util.date_to_timestamp)

    prs_raw["days_between_dates"] = prs_raw.apply(
        lambda row: pr_util.get_days_between_dates( row["create_date"], row["close_date"]), axis=1)

    prs_raw["real_time_in_hours"] = prs_raw.apply(
        lambda row: pr_util.get_diff_of_dates_in_hours(row["create_date"], row["close_date"]), axis=1)

    prs_raw["real_time_in_minutes"] = prs_raw.apply(
        lambda row: pr_util.get_diff_of_dates_in_minutes(row["create_date"], row["close_date"]), axis=1)

    prs_raw["time_in_hours_without_out_of_office_hours"] = prs_raw.apply(
        lambda row: pr_util.get_diff_of_dates_in_hours_without_out_of_office_hours(
            row["create_date"], row["close_date"], row["real_time_in_hours"]), axis=1,)
    
    prs_raw["technology"] = prs_raw.apply(lambda pr: util.get_technology_type(pr["repo"], pr["app"], specialty_file, "technology"), axis=1)
    prs_raw["application_type"] = prs_raw.apply(lambda pr: util.get_technology_type(pr["repo"], pr["app"], specialty_file, "application_type"), axis=1)
    prs_raw["specialty"] = prs_raw.apply(lambda pr: util.get_specialty(pr["repo"], pr["app"], pr["team_member_code"], specialty_file, base), axis=1)

    prs_raw["fullname"] = prs_raw.apply(lambda pr: get_squad_of_team_member(pr["team_member_code"], pr["app"], base, "fullname"), axis=1)
    prs_raw["squad"] = prs_raw.apply(lambda pr: get_squad_of_team_member(pr["team_member_code"], pr["app"], base, "squad"), axis=1)
    prs_raw["tribe"] = prs_raw.apply(lambda pr: get_squad_of_team_member(pr["team_member_code"], pr["app"], base, "tribe"), axis=1)
    prs_raw["squad_code"] = prs_raw.apply(lambda pr: get_squad_of_team_member(pr["team_member_code"], pr["app"], base, "squad_code"), axis=1)
    prs_raw["tribe_code"] = prs_raw.apply(lambda pr: get_squad_of_team_member(pr["team_member_code"], pr["app"], base, "tribe_code"), axis=1)

    return prs_raw

def get_data_pr_commit(base, period):
    pull_request_df = get_pull_request(base, period)
    commit_df = get_commit()

    commits_repo_set = set(commit_df["repo_with_pr_id"].values)
    prs_repo_set = set(pull_request_df["repo_with_pr_id"].values)

    valid_repo_set = commits_repo_set.intersection(prs_repo_set)

    commit_df = commit_df[commit_df["repo_with_pr_id"].isin(valid_repo_set)]
    pull_request_df = pull_request_df[pull_request_df["repo_with_pr_id"].isin(valid_repo_set)]

    export_pr_by_status(pull_request_df, period)
    
    pr_with_commit_detail = get_pr_with_commit_detail(pull_request_df, commit_df)

    return pr_with_commit_detail


def get_note_per_variable(pr_with_commit_detail):
    pr_with_commit_detail['commits_points'] = pr_with_commit_detail.apply(
        lambda pr: maturity_util.get_commit_points(pr["commit_amount"]), axis=1)
    
    pr_with_commit_detail['files_points'] = pr_with_commit_detail.apply(
        lambda pr: maturity_util.get_files_average_points (pr["files_in_included_commits"], pr["application_type"]), axis=1)

    pr_with_commit_detail['lines_points'] = pr_with_commit_detail.apply(
        lambda pr: maturity_util.get_lines_average_points(pr["files_in_included_commits"],
                                                  pr["lines_in_included_commits"], pr["application_type"]), axis=1)
    
    pr_with_commit_detail['reviewers_points'] = pr_with_commit_detail.apply( 
        lambda pr: maturity_util.get_reviewer_point(pr["reviewers"]), axis=1)
    
    pr_with_commit_detail['lines_in_pr_points'] = pr_with_commit_detail.apply(
        lambda pr: maturity_util.get_line_pr_points(pr["modified_lines_in_pr"], pr["application_type"]), axis=1)
    
    pr_with_commit_detail['complexity'] = pr_with_commit_detail.apply(
        lambda pr: maturity_util.get_complexity_points( pr['files_points'], pr['lines_points'], 
                                                     pr['commits_points'], pr['lines_in_pr_points']), axis=1)
    
    pr_with_commit_detail['time_points'] = pr_with_commit_detail.apply(
        lambda pr: maturity_util.get_time_points(pr["real_time_in_hours"], pr["complexity"]), axis=1)
    
    pr_with_commit_detail['tasks_and_comments_points'] = pr_with_commit_detail.apply(
        lambda pr: maturity_util.get_tasks_and_comments_points(pr["complexity"], pr["comments"], 
                                                                     pr["solved_task"]), axis=1)
    
    return pr_with_commit_detail


def export_pr_by_status(pull_request_df, period):
    pull_request_df = pull_request_df[pull_request_df["specialty"].isin(SPECIALITIES)]

    prioritized_squads_all_set = get_squads_with_specialty_prioritized()
    pull_request_df = pull_request_df[(pull_request_df["squad_code"] + pull_request_df["specialty"])
                                                  .isin(prioritized_squads_all_set)]

    pr_with_status = pd.DataFrame()

    for key, elem in PR_STATUS.items():
        if elem["validate"]:
            MAX_GENERATED_DATE = str(pull_request_df["generation_date"].max())

            max_generated_date_less_7_days = (
                    pr_util.date_to_timestamp(MAX_GENERATED_DATE) - 60 * 60 * 24 * 7
            )

            filtered_prs = pull_request_df[
                (pull_request_df["status"] == key) & 
                (pull_request_df["generation_date"] == MAX_GENERATED_DATE) & 
                (pull_request_df["creation_date_in_timestamp"] < max_generated_date_less_7_days)]
        else:
            filtered_prs = pull_request_df[pull_request_df["status"] == key]
            
        filtered_prs = filtered_prs[elem["column"]]

        pr_with_status = pd.concat([pr_with_status, filtered_prs], ignore_index=True)  

    pr_with_status.to_csv(PR_STATUS_PATH + period + PR_STATUS_FILE, index=False, header= header_status)


def get_modify_functionality(pr_info, period):
    pr_info['mod_functionality_for_UT'] = pr_info.apply(lambda pr: is_functionality(pr["modified_extensions"]), axis=1)
    pr_info.to_csv(OUTPUT_PATH + period + '-prs-with-identifier-functionality.csv', index=False, encoding="utf-8")
    return pr_info

def is_functionality(files_modifies):
    files = json.loads(files_modifies)
    for key in files:
        if key in EXTENSIONS_FOR_SPECIALTIES_UT:
            return YES
        else:
            continue
    return NO