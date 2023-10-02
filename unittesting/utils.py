import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import math

from datetime import datetime

from os import listdir,path

PATH_DIR = path.dirname(path.abspath(__file__)) + "\\"

def getPathDirectory(newDir) -> str:
    pathDirectory = PATH_DIR + newDir

    return pathDirectory

def getFilesDirectory(directory):
    files = [x for x in listdir(getPathDirectory(directory))]

    return files

def getCodeSquadTribe(squadTribe:str):
    if(isNullOrEmpty(squadTribe)): return None

    arrSquad=squadTribe.split("[")   

    if(len(arrSquad)<2): 
        arrSquad=squadTribe.split("(")   

        if(len(arrSquad)<2): return None

    if ")" in str(arrSquad[1]): 
        squadCode=arrSquad[1].split(")")[0].strip()
    else:
        squadCode=arrSquad[1].split("]")[0].strip()

    return squadCode

def isNullOrEmpty(value)->bool:
    if(value==None): return True

    if(len(str(value).strip())==0): return True

    return False

def isNotNumber(value)->bool:
    if(value==None): return True

    if(math.isnan(value)): return True

    return False

def getBeforePeriodProcess(periodActually:str)->str:
    yearActually = int(periodActually[0:4])
    monthActually = int(periodActually[4:6])    

    yearBefore = yearActually
    monthBefore = monthActually

    if monthActually == 1:
        monthBefore = 12
        yearBefore -= 1
    else:
        monthBefore -= 1

    periodBefore = str(yearBefore) + str(monthBefore).zfill(2)

    return periodBefore


def setExportExcel(directory:str,xls:pd.DataFrame,sheet:str,columns):
    xls.to_excel(getPathDirectory(directory),sheet_name=sheet,columns=columns,index=False)

def setExportCsv(directory:str,data:pd.DataFrame,columns):
    data.to_csv(getPathDirectory(directory),columns=columns,encoding="utf-8",index=False)

def setAnalysisExecutionDate(period:str,dataFrame:pd.DataFrame):
    year = int(period[0:4])
    month = int(period[4:6])   

    #DATE ANALYSIS AND DATE EXECUTIONS
    dataFrame["analysis_date"] = datetime(year, month, 1,0,0,0).date()    
    dataFrame["execution_date"] = datetime.now().date()
