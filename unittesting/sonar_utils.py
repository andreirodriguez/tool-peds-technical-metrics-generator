import pandas as pd
import unittesting.constants as constants
from pandas import DataFrame

import re

from unittesting.utils import getPathDirectory,getFilesDirectory

# Solo se toman en cuneta las versiones que no sean productivas
def is_production_version(version: str) -> str:
    version_split: list[str] = version.split('.')
    for version_index in version_split:
        if not version_index.isnumeric():
            return False

    return True

def get_sonar_data_frame(sonar_raw: DataFrame, metric: str, month, year) -> DataFrame:
    sonar_data_raw = sonar_raw[(sonar_raw["MONTH"] == month)
                      & (sonar_raw["YEAR"] == year)
                        & (sonar_raw["Metric"] == metric)
                      & (sonar_raw["Código Aplicación"].str.startswith("~") == False)
                      & (sonar_raw["Version"].str.endswith("-master") == False)
                      & (sonar_raw["Version"].str.contains("release/") == False)
                      & (sonar_raw["Version"].str.contains("-RC-") == False)
                      & (sonar_raw["Version"].str.startswith("MVPBCP-") == False)
                      & (sonar_raw["Version"].isin(
    ["t22055-UDV_M_WORKSHOP_ARQ_Q3_T22055", "T22055-UDV_M_WORKSHOP_ARQ_Q3_T22055",
     "-construccion", "2.2.13r-reverse-to-2.2.13", "T28819-WORKSHOP_T28819"]) == False)]

    return sonar_data_raw[(sonar_data_raw["Version"].apply(is_production_version) == False)] 

def get_name_repo(repo: str) -> str:
    app_and_repo = repo.removeprefix("https://bitbucket.lima.bcp.com.pe/scm/")
    name_repo = app_and_repo.split("/")[1]
    name_repo = name_repo.removesuffix(".git")

    return name_repo


def get_branch_of_version(version: str) -> str:
    version = version.replace('"', '')

    if re.match(r'^[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+(-SNAPSHOT-)', version):
        return re.sub(r'^[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+(-SNAPSHOT-)', '', version)
    elif re.match(r'^[0-9]+[.][0-9]+[.][0-9]+(-SNAPSHOT-)', version):
        return re.sub(r'^[0-9]+[.][0-9]+[.][0-9]+(-SNAPSHOT-)', '', version)
    elif re.match(r'^[0-9]+[.][0-9]+[.][0-9][a-zA-Z]+(-SNAPSHOT-)', version):
        return re.sub(r'^[0-9]+[.][0-9]+[.][0-9]+(-SNAPSHOT-)', '', version)
    elif re.match(r'^[0-9]+[.][0-9]+(-SNAPSHOT-)', version):
        return re.sub(r'^[0-9]+[.][0-9]+(-SNAPSHOT-)', '', version)
    elif re.match(r'^[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+(-)', version):
        return re.sub(r'^[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+(-)', '', version)
    elif re.match(r'^[0-9]+[.][0-9]+[.][0-9]+(-)', version):
        return re.sub(r'^[0-9]+[.][0-9]+[.][0-9]+(-)', '', version)
    elif re.match(r'^[0-9]+[.][0-9]+(-)', version):
        return re.sub(r'^[0-9]+[.][0-9]+(-)', '', version)
    elif re.match(r'^[A-Za-z0-9]*$', version):
        return re.sub(r'^[A-Za-z0-9]*$', '', version)
    else:
        return version
        #raise version

def get_float_value(value) -> float:
    if value is None: return None
    value = float(value)
    return round(value, 2)

def getPointZeroNone(point):  
    if(point==0): return None

    return point  

def getValueMetricSonar(pr,metric,sonarExecutions):  
    sonar = sonarExecutions[(sonarExecutions['repository']==pr["repo"]) & (sonarExecutions['branch']==pr['origin_branch']) & (sonarExecutions['metric']==metric)]

    if(pr["specialty"]==constants.SPECIALTY_FRONTEND_IOS):
        sonar = sonar[(sonar['type_information']==constants.TYPE_INFORMATION_SONAR_MANUAL)]

    if(len(sonar)==0): return None

    return sonar.iloc[0].value

def getFileSonarExecutions(file,year,month) -> DataFrame:
    print("Leo excel Sonar Executions: " + file)

    xlsSonar = pd.read_excel(getPathDirectory("input\\sonar\\" + file),sheet_name=0,header=2,usecols=[0,1,2,3,4,5,6],names=['application','project','url_repository','version','metric','value','date_analysis'])

    #Data complement
    xlsSonar["month"] = pd.to_datetime(xlsSonar["date_analysis"], dayfirst=True).dt.month
    xlsSonar["year"] = pd.to_datetime(xlsSonar["date_analysis"], dayfirst=True).dt.year
    xlsSonar['date_analysis'] = xlsSonar['date_analysis'].apply(lambda x: pd.to_datetime(x,format='%d/%m/%Y %H:%M:%S').to_datetime64())

    xlsSonar['metric'] = xlsSonar['metric'].apply(lambda x: str(x).lower())

    xlsSonar['application'] = xlsSonar['application'].apply(lambda x: str(x).upper())
    xlsSonar = xlsSonar[(xlsSonar['application'].str.len() > 0)]

    xlsSonar['url_repository'] = xlsSonar['url_repository'].apply(lambda x: str(x).lower())
    xlsSonar = xlsSonar[(xlsSonar['url_repository'].str.len() > 0)]
    xlsSonar = xlsSonar[(xlsSonar['url_repository']!="nan" )]

    #Filters
    xlsSonar = xlsSonar[(xlsSonar['metric']=='coverage') | (xlsSonar['metric']=='new_coverage')]
    xlsSonar = xlsSonar[(xlsSonar['application'].str.startswith("~")==False)]

    xlsSonar = xlsSonar[(xlsSonar["version"].str.endswith("-master") == False)]
    xlsSonar = xlsSonar[(xlsSonar["version"].str.contains("release/") == False)]
    xlsSonar = xlsSonar[(xlsSonar["version"].str.contains("-RC-") == False)]
    xlsSonar = xlsSonar[(xlsSonar["version"].str.startswith("MVPBCP-") == False)]
    xlsSonar = xlsSonar[(xlsSonar["version"].isin(["t22055-UDV_M_WORKSHOP_ARQ_Q3_T22055", "T22055-UDV_M_WORKSHOP_ARQ_Q3_T22055","-construccion", "2.2.13r-reverse-to-2.2.13", "T28819-WORKSHOP_T28819"]) == False)]
    xlsSonar = xlsSonar[(xlsSonar['version'].apply(is_production_version) == False)]

    xlsSonar["value"] = xlsSonar.apply(lambda row: get_float_value(row["value"]),axis=1)
    xlsSonar = xlsSonar[xlsSonar['value'].notna()]

    xlsSonar["type_information"] = getTypeSourceInformationSonar(file)

    return xlsSonar


def getTypeSourceInformationSonar(file:str)->str:
    for specialty in constants.SPECIALTYS_SCOPE_SEE:
        if(specialty in file) :
            return constants.TYPE_INFORMATION_SONAR_MANUAL
        
    return constants.TYPE_INFORMATION_SONAR_AUTO
    
def getSonarExecutionsConsolidated(year,month) -> DataFrame:
    print("Inicio a leer Excel Sonar Executions Consolidado")

    xlsConsolidated = pd.DataFrame({'application': [],'project': [],'url_repository': [],'version': [],'metric': [], 'value': [], 'date_analysis': [], 'month': [], 'year': [], 'type_information': []})

    files = getFilesDirectory("input\\sonar\\")

    for file in files:
        if (file.endswith(".xlsx")==False): continue

        xlsSonar = getFileSonarExecutions(file,year,month)

        xlsConsolidated = pd.concat([xlsConsolidated, xlsSonar], ignore_index=True)        

    xlsConsolidated["repository"] = xlsConsolidated.apply(lambda row: get_name_repo(row["url_repository"]),axis=1)
    xlsConsolidated["branch"] = xlsConsolidated.apply(lambda row: get_branch_of_version(row["version"]),axis=1)

    xlsConsolidated = xlsConsolidated.sort_values(['repository','version','metric','date_analysis'], ascending = [True,True, True, False])

    xlsConsolidated = xlsConsolidated.drop_duplicates(['repository','version','metric'],keep='first')

    print("Fin de leer Excel Sonar Executions Consolidado")

    return xlsConsolidated