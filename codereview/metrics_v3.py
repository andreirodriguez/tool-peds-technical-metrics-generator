import sys
from codereview.maturity_points import get_maturity_by_squad, get_maturity_by_squad_general
from codereview.pull_request import get_data_pr_commit, get_note_per_variable
from codereview.tm_data_base import getBaseActivos
from codereview.cr_constants import SPECIALITIES_SCOPE, SPECIALTY_GENERAL
from codereview.headers_columns_util import header_maturity_level_by_squad, header_pr_with_commits_raw, \
    header_pr_with_commits_info, header_quiz_note_per_variable, column_pr_with_commits_raw, \
    column_pr_with_commits_info, column_quiz_note_per_variable, column_maturity_level_by_squad
from codereview.prioritized_squads import get_prioritized_squads, get_squads_with_specialty_prioritized
from codereview.util import export_final_csv, set_export_excel_summary, get_summary
import codereview.quiz as quiz

period = sys.argv[1]

def execute_metrics():
    
    tm_data_base = getBaseActivos()

    pr_with_commit_detail = get_data_pr_commit(tm_data_base, period) #prs-with-commit-info-raw
    pr_with_variable_note = get_note_per_variable(pr_with_commit_detail) #prs-with-commit-info

    quiz_result = quiz.get_data_quiz(tm_data_base, period)
    quiz_with_variable_point = quiz.get_note_per_variable(quiz_result)

    prioritized_squads_all_set = get_squads_with_specialty_prioritized()
    pr_with_variable_note_filter = pr_with_variable_note[(pr_with_variable_note["squad_code"] + pr_with_variable_note["specialty"])
                                                  .isin(prioritized_squads_all_set)]
    pr_with_commit_detail_filter = pr_with_commit_detail[(pr_with_commit_detail["squad_code"] + pr_with_commit_detail["specialty"])
                                                  .isin(prioritized_squads_all_set)]
    quiz_with_variable_point_filter = quiz_with_variable_point[(quiz_with_variable_point["squad_code"] + quiz_with_variable_point["specialty"])
                                                        .isin(prioritized_squads_all_set)]

    squad_maturity_level_array = []
    
    for specialty in SPECIALITIES_SCOPE:
        squads_prioritized = get_prioritized_squads(specialty)
        
        squad_maturity_level = get_maturity_by_squad(pr_with_variable_note_filter, quiz_with_variable_point_filter, specialty, squads_prioritized, period)
        squad_maturity_level_array.append(squad_maturity_level)
        squad_maturity_level = squad_maturity_level.dropna(subset=["maturity_level"])
        file = period + "-cr-maturity-level-by-squad-" + specialty + ".csv"
        export_final_csv(file, header_maturity_level_by_squad, squad_maturity_level, column_maturity_level_by_squad)
        
    squads_prioritized = get_prioritized_squads(SPECIALTY_GENERAL)
    squads_prioritized_set = set(squads_prioritized["squad_code"].values)

    squad_maturity_level = get_maturity_by_squad_general(squads_prioritized,squad_maturity_level_array, period, pr_with_variable_note_filter, quiz_with_variable_point_filter)
    squad_maturity_level_array.append(squad_maturity_level)
    squad_maturity_level = squad_maturity_level.dropna(subset=["maturity_level"])
    file = period + "-cr-maturity-level-by-squad.csv"
    export_final_csv(file, header_maturity_level_by_squad, squad_maturity_level, column_maturity_level_by_squad)

    pr_with_commit_detail_csv = pr_with_commit_detail_filter[pr_with_commit_detail_filter["squad_code"].isin(squads_prioritized_set)]
    export_final_csv(period + "-prs-with-commit-info-raw.csv", header_pr_with_commits_raw, pr_with_commit_detail_csv,
                    column_pr_with_commits_raw)
    quiz_with_variable_point_csv = quiz_with_variable_point_filter[quiz_with_variable_point_filter["squad_code"].isin(squads_prioritized_set)]
    export_final_csv(period + "-quiz-test-team-members.csv", header_quiz_note_per_variable, quiz_with_variable_point_csv,
                    column_quiz_note_per_variable)
        
    set_export_excel_summary(period, tm_data_base, pr_with_variable_note, quiz_with_variable_point, squad_maturity_level_array, pr_with_variable_note_filter)
    export_final_csv(period + "-prs-with-commit-info.csv", header_pr_with_commits_info, pr_with_variable_note, column_pr_with_commits_info)

execute_metrics()