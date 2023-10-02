import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import numpy as np

import json

from os import listdir,path

PATH_DIR = path.dirname(path.abspath(__file__)) + "\\"

def getConfigurationFileJson(configurationFile):
    print("Leo el archivo de configuracion: " + configurationFile)

    configurationFile = getPathDirectory("input\\configuration\\" + configurationFile + ".json")
    configuration = None

    with open(configurationFile) as data:
        configuration = json.load(data)       

    return configuration

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

def setExportExcel(directory:str,xls:pd.DataFrame,sheet:str,columns):
    if(columns==None):
        xls.to_excel(getPathDirectory(directory),sheet_name=sheet,index=False)
    else:
        xls.to_excel(getPathDirectory(directory),sheet_name=sheet,columns=columns,index=False)

def setExportCsv(directory:str,data:pd.DataFrame,columns):
    data.to_csv(getPathDirectory(directory),columns=columns,encoding="utf-8",index=False)

def isNullOrEmpty(value)->bool:
    if(value==None): return True

    if(len(str(value).strip())==0): return True

    return False

def getStringUpperStrip(text:str):
    if(isNullOrEmpty(text)): return None

    text = text.upper().strip()

    return text

def getStringLowerStrip(text:str):
    if(isNullOrEmpty(text)): return None

    text = text.upper().strip()

    return text