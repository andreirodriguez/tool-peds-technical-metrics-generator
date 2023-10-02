from typing import List
import glob
import pandas as pd
import codereview.commit_util as util
from codereview.cr_constants import COMMIT_FILE, COMMIT_TYPE_GUIDELINES

def get_commit():
    print("Getting data from commits")

    commit_files = glob.glob(COMMIT_FILE)
    commit_files.sort()
    commit_xls_files: List[pd.DataFrame] = []

    for commit in commit_files:
        commit_xls_files.append(
            pd.read_excel(commit, header=2, usecols=[0,1,2,3,4,5,6,10,12],
                        names=['app','repo','prid','commit_id','number_files',
                                'add_lines','delete_lines','commit_message','log_date']))

    commits_raw = pd.concat(commit_xls_files).drop_duplicates(
        subset=["repo", "prid", "commit_id"], keep="last")

    commits_raw = commits_raw[(commits_raw["number_files"] > 0)]

    commits_raw["repo_with_pr_id"] = commits_raw.apply(
        lambda row: row["repo"] + " - " + str(row["prid"]), axis=1)

    commits_raw["modified_lines"] = commits_raw.apply(
        lambda row: row["add_lines"] + row["delete_lines"], axis=1)

    commits_raw["type"] = commits_raw.apply(
        lambda row: util.get_type_of_commit(
            row["commit_message"], row["number_files"]), axis=1)
    
    return commits_raw

def get_pr_with_commit_detail(pull_request_df, commit_df):
    print("Join commit information to pr data")

    #Get PRs and Commits Merged
    pr_merged = pull_request_df[pull_request_df["status"] == "MERGED"]
    prs_repo_set = set(pr_merged["repo_with_pr_id"].values)
    commit_df = commit_df[commit_df["repo_with_pr_id"].isin(prs_repo_set)]

    #Get commit's amount per PR
    commit_counts = commit_df.groupby('repo_with_pr_id')['commit_id'].nunique().reset_index() \
                            .rename(columns={'commit_id':'commit_amount'})
    pr_merged = pd.merge(pr_merged, commit_counts, on='repo_with_pr_id', how='left')

    #Get commit's type that are in the guidelines
    commit_types_guidelines = set(COMMIT_TYPE_GUIDELINES)
    commit_df_guidelines = commit_df[commit_df["type"].isin(commit_types_guidelines)]
    #Get a list of files and lines that are in the guidelines
    files_guidelines = commit_df_guidelines.groupby(['repo_with_pr_id'])['number_files'].agg(list).reset_index()
    lines_guidelines = commit_df_guidelines.groupby(['repo_with_pr_id'])['modified_lines'].agg(list).reset_index()
    #Get a list of files and lines per type in general
    files = commit_df.groupby(['repo_with_pr_id','type'])['number_files'].agg(list).reset_index()
    lines = commit_df.groupby(['repo_with_pr_id','type'])['modified_lines'].agg(list).reset_index()
    types = commit_df['type'].unique()

    for elem in types:
        files_by_commit_type_key = "files_by_" + elem + "_commits"
        lines_by_commit_type_key = "lines_by_" + elem + "_commits"

        pr_merged[files_by_commit_type_key] = pr_merged.apply(
            lambda pr: util.get_files_lines_per_type(pr['repo_with_pr_id'], files, elem, 'number_files'),axis=1)
        pr_merged[lines_by_commit_type_key] = pr_merged.apply(
            lambda pr: util.get_files_lines_per_type(pr['repo_with_pr_id'], lines, elem, 'modified_lines'),axis=1)

    pr_merged["files_in_included_commits"] = pr_merged.apply(
        lambda pr: util.get_all_files_lines(pr['repo_with_pr_id'], files_guidelines, 'number_files'),axis=1)
    pr_merged["lines_in_included_commits"] = pr_merged.apply(
        lambda pr: util.get_all_files_lines(pr['repo_with_pr_id'], lines_guidelines, 'modified_lines'),axis=1)

    return pr_merged


