import pandas as pd
from codereview.util import extract_squad_tribe_id
from codereview.cr_constants import PRIORITIZED_FILE, SPECIALITIES, SPECIALTY_GENERAL
def get_prioritized_squads(specialty:str):

    squad_result = pd.read_excel(PRIORITIZED_FILE,usecols=[0,1,2,3],names=["tribe","squad","group","cmt"],
                              sheet_name = specialty)

    squad_result["squad_code"] = squad_result.apply(lambda squad: extract_squad_tribe_id(squad["squad"]), axis=1)
    squad_result["tribe_code"] = squad_result.apply(lambda squad: extract_squad_tribe_id(squad["tribe"]), axis=1)

    squad_result = squad_result[squad_result["squad_code"] != ""]

    return squad_result

def get_squads_with_specialty_prioritized():
    prioritized_squads_all = pd.DataFrame()
    for specialty in SPECIALITIES:
        if specialty != SPECIALTY_GENERAL:
            prioritized_squads = get_prioritized_squads(specialty)
            prioritized_squads["squad_specialty"] = prioritized_squads.apply(lambda x: x["squad_code"] + specialty, axis=1)
            prioritized_squads_all = pd.concat([prioritized_squads_all, prioritized_squads], ignore_index=True)

    return set(prioritized_squads_all["squad_specialty"].values)