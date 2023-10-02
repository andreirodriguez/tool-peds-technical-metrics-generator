import pandas as pd

def get_team_member_id_without_zero(codeTeamMember:str):
    codeTeamMember = codeTeamMember.upper().strip()
    firstZero = codeTeamMember[0:1]
    if(firstZero == "0"): codeTeamMember = codeTeamMember[1:len(codeTeamMember)]
    return codeTeamMember


def getTwoBaseActivos():
    print("Getting from two data base of team members")
    FIRST_BASE = "util/files/base0.xlsx"
    SECOND_BASE = "util/files/base1.xlsx"
    OUTPUT = "util/files/base.xlsx"

    base_result_first = pd.read_excel(FIRST_BASE, sheet_name=0)
    base_result_first["team_member_code"] = base_result_first.apply(lambda teamMember: get_team_member_id_without_zero(str(teamMember["Matrícula"])), axis=1)

    base_result_first: pd.DataFrame = base_result_first.drop_duplicates(subset=["team_member_code"], keep="last")

    base_result_second = pd.read_excel(SECOND_BASE, sheet_name=0)
    base_result_second["team_member_code"] = base_result_second.apply(lambda teamMember: get_team_member_id_without_zero(str(teamMember["Matrícula"])), axis=1)

    base_result_second: pd.DataFrame = base_result_second.drop_duplicates(subset=["team_member_code"], keep="last")

    merged = pd.concat([base_result_second, base_result_first])
    base_merged: pd.DataFrame = merged.drop_duplicates(subset=["team_member_code"], keep="last")

    base_merged.to_excel(OUTPUT, index=False)
