import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import assets.base_activos.utils as utils
import assets.base_activos.constants as constants


def getFilePullRequests(file) -> pd.DataFrame:
    print("Leo excel Pull Requests: " + file)

    base = pd.read_excel(utils.getPathDirectory("input\\pull_requests\\" + file),sheet_name=0,header=2,usecols=[0,10,13],names=['project','fecha_actualizado','author'])

    base['project'] = base['project'].apply(lambda value: utils.getStringUpperStrip(value))
    base['fecha_actualizado'] = base['fecha_actualizado'].apply(lambda x: pd.to_datetime(x,format='%d/%m/%Y %H:%M:%S').date())

    return base

def getPullRequestsConsolidated() -> pd.DataFrame:
    print("Inicio a leer Excel PullRequests Consolidado")

    consolidated = pd.DataFrame({})

    files = utils.getFilesDirectory("input\\pull_requests\\")

    for file in files:
        if (file.endswith(".xlsx")==False): continue

        xls = getFilePullRequests(file)

        consolidated = pd.concat([consolidated, xls], ignore_index=True)        

    consolidated = consolidated.astype(object).where(pd.notnull(consolidated),None)

    print("Fin de leer Excel Pull Requests Consolidado")

    return consolidated

def getTeamMembersPullRequests(projects:pd.DataFrame) -> pd.DataFrame:
    consolidated = getPullRequestsConsolidated()

    consolidated = consolidated[consolidated['project'].isin(projects["project"].unique())]

    consolidated["matricula"] = consolidated.apply(lambda record: getMatricula(record["author"]),axis=1)
    consolidated["nombre"] = consolidated.apply(lambda record: getNames(record["author"]),axis=1)

    consolidated = consolidated.sort_values(['matricula','fecha_actualizado'], ascending = [True,False])
    consolidated = consolidated.drop_duplicates(['matricula'],keep='first')

    return consolidated

def getMatricula(author:str):
    if(utils.isNullOrEmpty(author)): return None

    authorArray = author.split("(")

    if(len(authorArray)<2): return None

    authorArray = authorArray[1].split(")")

    return authorArray[0].upper().strip()

def getNames(author:str):
    if(utils.isNullOrEmpty(author)): return None

    authorArray = author.split("(")

    if(len(authorArray)<2): return None

    return authorArray[0].upper().strip()