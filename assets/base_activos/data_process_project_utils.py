import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import assets.base_activos.utils as utils
import assets.base_activos.constants as constants

def getProjectsScope()->pd.DataFrame:
    file = "data-process-project.xlsx"

    print("Leo las aplicaciones del ALCANCE ACELERA: " + file)

    file = utils.getPathDirectory("input\\data_process_project\\" + file)

    projects = pd.read_excel(file,usecols=["project"],sheet_name=0)
    projects = projects.astype(object).where(pd.notnull(projects),None)

    projects['project'] = projects['project'].apply(lambda value: utils.getStringUpperStrip(value))

    return projects