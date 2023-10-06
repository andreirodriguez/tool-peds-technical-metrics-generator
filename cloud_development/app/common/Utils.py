import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import json
import datetime
import logging as log
import traceback
import os
from decimal import Decimal

from cloud_development.app.common.Log import getLog,getLogDateFormat,getLogFormat
from os import listdir,getcwd,mkdir

log.basicConfig(filename=getLog(), 
                level=log.INFO,
                format=getLogFormat(),
                datefmt=getLogDateFormat())

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
    def getFilesDirectory(directory:str) -> str:
        files = [x for x in listdir(Utils.getPathDirectory(directory))]

        return files          
    
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
                    return round(
                            range["points"] + 
                                ((((range["maximum"] - value) * 100) / (range["minimum"] - range["maximum"])) / 100)
                            ,2)