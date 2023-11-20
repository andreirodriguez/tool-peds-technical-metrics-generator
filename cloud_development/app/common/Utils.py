import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import json
import datetime
import logging as log
import traceback
import os
from decimal import Decimal

import cloud_development.app.common.Constants as Constants

from cloud_development.app.common.Log import getLog,getLogDateFormat,getLogFormat
from os import listdir,getcwd,mkdir

log.basicConfig(filename=getLog(), 
                level=log.INFO,
                format=getLogFormat(),
                datefmt=getLogDateFormat(),
                filemode="w")

class Utils:
    @staticmethod
    def getPathDirectory(newDir) -> str:
        path_dir:str = getcwd() + "\\" 

        pathDirectory = path_dir + newDir

        return pathDirectory

    @staticmethod
    def getDataFrameToDictionaryList(listObject:list[object])->pd.DataFrame:
        csv:pd.DataFrame = pd.DataFrame([o.__dict__ for o in listObject ])

        return csv

    @staticmethod
    def setCreateDirectory(directory:str):
        if(os.path.exists(directory)): return

        mkdir(directory)

    @staticmethod
    def existsDirectory(directory:str)->bool:
        if(os.path.exists(directory)): return True

        return False

    @staticmethod
    def setCreateMkdir(directory:str):
        arrDirectory = directory.split("\\")

        fileName = arrDirectory[len(arrDirectory)-1]

        directory = directory.replace(fileName,"")

        if(os.path.exists(directory)): return

        mkdir(directory)

    @staticmethod
    def setListObjectExportCsv(directory:str,listObject:list[object]):
        data:pd.DataFrame = Utils.getDataFrameToDictionaryList(listObject)

        data.to_csv(Utils.getPathDirectory(directory),encoding="utf-8",index=False)

    @staticmethod
    def exportDataFrameToXlsx(directory:str,data:pd.DataFrame):
        data.to_excel(Utils.getPathDirectory(directory),index=False)        

    @staticmethod
    def getConfigurationFileJson(configurationFile):
        configurationFile = Utils.getPathDirectory("cloud_development\\resources\\configuration\\" + configurationFile + ".json")
        configuration = None

        with open(configurationFile) as data:
            configuration = json.load(data)       

        return configuration
    
    @staticmethod
    def convertRestUtcToDatetime(dateUtc:str):
        date = datetime.datetime.strptime(dateUtc,'%Y-%m-%dT%H:%M:%S.%fZ')

        return date
            
    
    @staticmethod
    def convertRestUtcMsToDatetime(dateUtc:str):
        date = datetime.datetime.strptime(dateUtc,'%Y-%m-%dT%H:%M:%SZ')

        return date

    @staticmethod
    def convertStringToDatetime(date:str,format:str)->datetime.datetime:
        date = datetime.datetime.strptime(date,format)

        return date    

    @staticmethod
    def convertXmlUtcToDatetime(dateUtc:str):
        date = datetime.datetime.strptime(dateUtc,'%Y-%m-%dT%H:%M:%S')

        return date    

    @staticmethod
    def convertDateTimeToStringInterval(date:datetime.datetime)->str:
        text:str = date.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

        return text        
    
    @staticmethod
    def convertTimeStampToDatetimeUTC5(time:float)->datetime.datetime:
        date:datetime.datetime = datetime.datetime.fromtimestamp(time)

        return date
    
    @staticmethod
    def convertArgTextToDatetime(dateArg:str)->datetime.datetime:
        date = datetime.datetime.strptime(dateArg,'%d/%m/%Y')

        return date   

    @staticmethod
    def convertArgFullTextToDatetime(dateArg:str)->datetime.datetime:
        date = datetime.datetime.strptime(dateArg,'%d/%m/%Y %H:%M:%S')

        return date         
    
    @staticmethod
    def logInfo(info:str) -> str:
        log.info(info)

        time:str = Utils.convertDateTimeToStringInterval(datetime.datetime.now())

        print(time + ": " + info)

    @staticmethod
    def logWarning(warning:str,ex:Exception) -> str:
        warning = f"{warning}. Message Warning: {str(ex)}"

        log.warning(warning)

        time:str = Utils.convertDateTimeToStringInterval(datetime.datetime.now())

        print(time + ": " + warning)

    @staticmethod
    def logError(error:str,ex:Exception) -> str:
        tbError:str = ''.join(traceback.format_tb(ex.__traceback__))
        error = f"{error}. Message Error: {str(ex)} -> {tbError}"

        log.error(error)

        time:str = Utils.convertDateTimeToStringInterval(datetime.datetime.now())

        print(time + ": " + error)

    @staticmethod
    def getEnvironmentByResourceGroupName(resourceGroupName:str) -> str:
        lenght:int = len(resourceGroupName) - 1
        character:str = resourceGroupName[lenght]

        if(not character.isnumeric()): return "F"

        while lenght >= 0:
            character = resourceGroupName[lenght]

            if(character.isnumeric()): 
                lenght-=1
            else:
                return character.upper()

    @staticmethod
    def getFilesDirectory(directory:str) -> list:
        files = [x for x in listdir(Utils.getPathDirectory(directory))]

        return files   

    @staticmethod
    def getFoldersDirectory(directory:str) -> list:
        directory = Utils.getPathDirectory(directory)
        folders:list[str] = []

        for folder in os.listdir(directory):
            if os.path.isdir(os.path.join(directory, folder)):
                folders.append(folder)

        return folders

    
    @staticmethod
    def getAllFilesSubDirectory(directory:str,pattern:str) -> list[str]:
        paths:list[str] = []

        for path, subdirs, files in os.walk(directory):
            for name in files:
                if name==pattern:
                    paths.append(os.path.join(path, name))   

        return paths
    

    @staticmethod
    def getAppCodeByResourceGroupName(resourceGroupName:str) -> str:
        lenght:int = len(resourceGroupName) - 1
        character:str = resourceGroupName[lenght]

        if(not character.isnumeric()): return None

        while lenght >= 0:
            character = resourceGroupName[lenght]

            if(character.isnumeric()): 
                lenght-=1
            else:
                return resourceGroupName[(lenght-4):lenght].upper()    
            
        return None
    
    @staticmethod
    def getMetricPointsAzureMonitor(value:Decimal,ranges:any) -> Decimal:
        length:int = len(ranges)

        for range in ranges:
            if(range["id"]==1):
                if(range["maximum"] <= value):
                    return range["points"]   
            elif(range["id"]==length):
                if(value < range["minimum"]):
                    return range["points"]                                 
            else:
                if(range["maximum"] <= value < range["minimum"]):
                    points:Decimal = (range["minimum"] - range["maximum"])
                    points = ((range["maximum"] - value) * 100) / points
                    points = points / 100
                    points += range["points"]
                    points = round(points,2)

                    return points
                
    @staticmethod
    def getCodeSquadTribe(squadTribe:str)->str:
        if(Utils.isNullOrEmpty(squadTribe)): return None

        arrSquad=squadTribe.split("[")   

        if(len(arrSquad)<2): 
            arrSquad=squadTribe.split("(")   

            if(len(arrSquad)<2): return None

        if ")" in str(arrSquad[1]): 
            squadCode=arrSquad[1].split(")")[0].strip()
        else:
            squadCode=arrSquad[1].split("]")[0].strip()    

        return squadCode


    @staticmethod
    def isNullOrEmpty(value)->bool:
        if(value==None): return True

        if(len(str(value).strip())==0): return True

        return False            
    
    @staticmethod
    def findObjectJson(listJson:any,property:str,value:str)->pd.DataFrame:
        listJson = [record for record in listJson if record[property]==value]

        if(len(listJson)==0): return None

        return listJson[0]
    
    @staticmethod
    def getAllResourcesAzureType(basePathAzure:str,fileResource:str,resourceColumns:list[str])->pd.DataFrame:
        data = pd.DataFrame({})
        files = Utils.getAllFilesSubDirectory(basePathAzure,fileResource)

        for file in files:
            data = pd.concat([data, Utils.getFileResourcesAzureType(file,resourceColumns)], ignore_index=True)        

        return data

    @staticmethod
    def getFileResourcesAzureType(directory:str,resourceColumns:list[str])->pd.DataFrame:
        file:str = Utils.getPathDirectory(directory)

        usecols:list[str]=resourceColumns.copy()
        usecols.append("processDate")

        data:pd.DataFrame = pd.read_csv(file,usecols=usecols,encoding="utf-8")
        data = data.astype(object).where(pd.notnull(data),None)

        data['processDate'] = data['processDate'].apply(lambda value: pd.to_datetime(value,format=Constants.FORMAT_DATETIME_PROCESS_AZURE_MONITOR).to_datetime64())

        return data            
    
    @staticmethod
    def getDataAzureMonitor(pathAzureData:str,columnsAzureData:list[str])->pd.DataFrame:
        data = pd.DataFrame(columns=columnsAzureData)
        folders = Utils.getFoldersDirectory(Constants.PATH_INPUT_AZURE_MONITOR)

        for folder in folders:
            file = pathAzureData.replace(Constants.PARAMETER_INPUT_AZURE_TENANTID,folder)

            if(not Utils.existsDirectory(file)): continue

            dataAzure = pd.read_csv(Utils.getPathDirectory(file),usecols=columnsAzureData,encoding="utf-8")
            dataAzure = dataAzure.astype(object).where(pd.notnull(dataAzure),None)

            data = pd.concat([data, dataAzure], ignore_index=True)        

        return data    