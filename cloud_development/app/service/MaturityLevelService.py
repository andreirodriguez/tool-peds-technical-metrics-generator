import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from decimal import Decimal
import math

from cloud_development.app.repository.SquadPrioritizedRepository import SquadPrioritizedRepository

import cloud_development.app.common.Constants as Constants
from cloud_development.app.common.Utils import Utils

from cloud_development.app.domain.AzureSqlMetric import AzureSqlMetric
from cloud_development.app.domain.RedisCacheMetric import RedisCacheMetric
from cloud_development.app.domain.CosmosDbMetric import CosmosDbMetric

class MaturityLevelService():

    __metricsModel:any  

    def __init__(self,metricsModel:any):
        self.__metricsModel = metricsModel

    def calculateMaturityLevelBySquad(self,serviceCloud:str,squads:pd.DataFrame)->pd.DataFrame:
        model:any = Utils.findObjectJson(self.__metricsModel,"serviceCloud",serviceCloud)

        self.__calculateMetricsSquads(model,squads)

        return squads

    def calculateMaturityLevelAssesmentBySquad(self,serviceCloud:str,squads:pd.DataFrame)->pd.DataFrame:

        model:any = Utils.findObjectJson(self.__metricsModel,"serviceCloud",serviceCloud)

        squads["applyPractice"] = squads.apply(lambda record: self.__getApplyAssesmentPractice(record,model),axis=1)

        self.__calculateMetricsAssesmentSquads(model,squads)

        return squads    
    
    def __getApplyAssesmentPractice(self,squad:any,model:any)->Decimal:
        metricPoints:Decimal = 0.00
        points:Decimal = 0.00

        for category in model["categories"]:
            for metric in category["metrics"]:        
                for variable in metric["variables"]: 
                    if(not variable["type"]=="assesment"): continue

                    points = squad[variable["variable"]]

                    if(math.isnan(points)): return False

        return True
    
    def calculateMaturityLevel(self,squads:pd.DataFrame,squadsAzureSql:pd.DataFrame,squadsCacheRedis:pd.DataFrame,squadsCosmosDb:pd.DataFrame)->pd.DataFrame:
        squads["maturityLevelAzureSql"] = squads.apply(lambda record: self.__getMaturityLevelBySquadAndServiceCloud(record["squadCode"],squadsAzureSql),axis=1)
        squads["maturityLevelRedisCache"] = squads.apply(lambda record: self.__getMaturityLevelBySquadAndServiceCloud(record["squadCode"],squadsCacheRedis),axis=1)
        squads["maturityLevelCosmosDb"] = squads.apply(lambda record: self.__getMaturityLevelBySquadAndServiceCloud(record["squadCode"],squadsCosmosDb),axis=1)

        squads["maturityLevel"] = squads.apply(lambda record: self.__getMaturityLevelSquad(record),axis=1)

        return squads    

    def __getMaturityLevelBySquadAndServiceCloud(self,squadCode:str,serviceCloudData:pd.DataFrame):
        squad = serviceCloudData[(serviceCloudData['squadCode'] == squadCode)]

        if(len(squad.index)==0): return None

        maturityLevel = squad.iloc[0]["maturityLevel"]

        if(math.isnan(maturityLevel)): return None

        return maturityLevel

    def __getMaturityLevelSquad(self,squad:any):
        percentageAzureSql:Decimal = Utils.findObjectJson(self.__metricsModel,"serviceCloud",Constants.SERVICE_CLOUD_AZURE_SQL)["percentage"]/100
        percentageRedisCache:Decimal = Utils.findObjectJson(self.__metricsModel,"serviceCloud",Constants.SERVICE_CLOUD_CACHE_REDIS)["percentage"]/100
        percentageCosmosDb:Decimal = Utils.findObjectJson(self.__metricsModel,"serviceCloud",Constants.SERVICE_CLOUD_COSMOS_DB)["percentage"]/100

        maturityLevelAzureSql:Decimal = squad["maturityLevelAzureSql"]
        if(math.isnan(maturityLevelAzureSql)): maturityLevelAzureSql = None

        maturityLevelRedisCache:Decimal = squad["maturityLevelRedisCache"]
        if(math.isnan(maturityLevelRedisCache)): maturityLevelRedisCache = None

        maturityLevelCosmosDb:Decimal = squad["maturityLevelCosmosDb"]
        if(math.isnan(maturityLevelCosmosDb)): maturityLevelCosmosDb = None

        if(maturityLevelAzureSql==None and maturityLevelRedisCache==None and maturityLevelCosmosDb==None): return None

        if(maturityLevelAzureSql!=None and maturityLevelRedisCache!=None and maturityLevelCosmosDb!=None):
            return round((maturityLevelAzureSql * percentageAzureSql) +
                         (maturityLevelRedisCache * percentageRedisCache) +
                         (maturityLevelCosmosDb * percentageCosmosDb),2)
        
        if(maturityLevelAzureSql==None and maturityLevelRedisCache!=None and maturityLevelCosmosDb!=None):
            return round((maturityLevelRedisCache * (percentageRedisCache + percentageAzureSql / 2)) +
                         (maturityLevelCosmosDb * (percentageCosmosDb + percentageAzureSql / 2)),2)
        
        if(maturityLevelAzureSql!=None and maturityLevelRedisCache==None and maturityLevelCosmosDb!=None):
            return round((maturityLevelAzureSql * (percentageAzureSql + percentageRedisCache / 2)) +
                         (maturityLevelCosmosDb * (percentageCosmosDb + percentageRedisCache / 2)),2)        
        
        if(maturityLevelAzureSql!=None and maturityLevelRedisCache!=None and maturityLevelCosmosDb==None):
            return round((maturityLevelAzureSql * (percentageAzureSql + percentageCosmosDb / 2)) +
                         (maturityLevelRedisCache * (percentageRedisCache + percentageCosmosDb / 2)),2)                

        if(maturityLevelAzureSql!=None): return maturityLevelAzureSql

        if(maturityLevelRedisCache!=None): return maturityLevelRedisCache

        if(maturityLevelCosmosDb!=None): return maturityLevelCosmosDb

        return None

    def __calculateMetricsSquads(self,model:any,squads:pd.DataFrame):
        for category in model["categories"]:
            for metric in category["metrics"]:
                squads[metric["metric"]] = squads.apply(lambda record: self.__getMetricPoints(record,metric["variables"]),axis=1)

        for category in model["categories"]:
            squads[category["category"]] = squads.apply(lambda record: self.__getCategoryPoints(record,category["metrics"]),axis=1)

        squads["maturityLevel"] = squads.apply(lambda record: self.__getMaturityLevelServiceCloud(record,model["categories"]),axis=1)

    def __calculateMetricsAssesmentSquads(self,model:any,squads:pd.DataFrame):
        for category in model["categories"]:
            for metric in category["metrics"]:
                squads[metric["metric"]] = squads.apply(lambda record: self.__getMetricAssesmentPoints(record,metric["variables"]),axis=1)

        for category in model["categories"]:
            squads[category["category"]] = squads.apply(lambda record: self.__getCategoryPoints(record,category["metrics"]),axis=1)

        squads["maturityLevel"] = squads.apply(lambda record: self.__getMaturityLevelServiceCloud(record,model["categories"]),axis=1)        

    def __getMetricPoints(self,squad:any,variables:any)->Decimal:
        if(not squad["applyPractice"]): return None

        metricPoints:Decimal = 0.00
        points:Decimal = 0.00
        for variable in variables: 
            points = squad[variable["variable"]]

            if(math.isnan(points)): points = Constants.METRIC_SONAR_POINTS_MINIMUM

            metricPoints += points * (variable["percentage"] / 100)

        return round(metricPoints,2)
    
    def __getMetricAssesmentPoints(self,squad:any,variables:any)->Decimal:
        if(not squad["applyPractice"]): return None

        metricPoints:Decimal = 0.00
        points:Decimal = 0.00

        for variable in variables: 
            if(not variable["type"]=="assesment"): continue

            points = squad[variable["variable"]]

            if(math.isnan(points)): points = Constants.METRIC_SONAR_POINTS_MINIMUM

            metricPoints = points

        return round(metricPoints,2)    
    
    def __getCategoryPoints(self,squad:any,metrics:any)->Decimal:
        if(not squad["applyPractice"]): return None

        categoryPoints:Decimal = 0.00
        points:Decimal = 0.00
        for metric in metrics: 
            points = squad[metric["metric"]]

            if(math.isnan(points)): points = Constants.METRIC_SONAR_POINTS_MINIMUM

            categoryPoints += points * (metric["percentage"] / 100)

        return round(categoryPoints,2)

    def __getMaturityLevelServiceCloud(self,squad:any,categories:any)->Decimal:
        if(not squad["applyPractice"]): return None

        maturityLevel:Decimal = 0.00
        points:Decimal = 0.00
        for category in categories: 
            points = squad[category["category"]]

            if(math.isnan(points)): points = Constants.METRIC_SONAR_POINTS_MINIMUM

            maturityLevel += points * (category["percentage"] / 100)

        return round(maturityLevel,2)

    def exportExcelSummary(self,period,baseActivos:pd.DataFrame,
                              squadsMaturityLevel:pd.DataFrame,squadsAzureSql:pd.DataFrame,squadsRedisCache:pd.DataFrame,squadsCosmosDb:pd.DataFrame,
                              metricsAppAzureSql:pd.DataFrame,metricsAppRedisCache:pd.DataFrame,metricsAppCosmosDb:pd.DataFrame,
                              metricsAzureSql:pd.DataFrame,metricsAzureRedis:pd.DataFrame,metricsAzureCosmos:pd.DataFrame,
                              metricsSonarAzureSql:pd.DataFrame,metricsSonarRedisCache:pd.DataFrame,
                              assesmentAzureSql:pd.DataFrame,assesmentRedisCache:pd.DataFrame,assesmentCosmosDb:pd.DataFrame
                              ):
        file = Utils.getPathDirectory(Constants.PATH_OUTPUT_FILE_SUMMARY.format(period=period))

        with pd.ExcelWriter(file) as writer:
            squadsMaturityLevel.to_excel(writer,sheet_name=Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_GENERAL,columns=self.__getColumnsSquadsGeneral(), index=False)
            squadsAzureSql.to_excel(writer,sheet_name=Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_SQL,columns=self.__getColumnsSquadsServiceCloud(Constants.SERVICE_CLOUD_AZURE_SQL), index=False)
            squadsRedisCache.to_excel(writer,sheet_name=Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_REDIS,columns=self.__getColumnsSquadsServiceCloud(Constants.SERVICE_CLOUD_CACHE_REDIS), index=False)
            squadsCosmosDb.to_excel(writer,sheet_name=Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_COSMOS,columns=self.__getColumnsSquadsServiceCloud(Constants.SERVICE_CLOUD_COSMOS_DB), index=False)
            metricsAppAzureSql.to_excel(writer,sheet_name="APP " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_SQL,columns=self.__getColumnsMetricsAppByServiceCloud(Constants.SERVICE_CLOUD_AZURE_SQL), index=False)
            metricsAppRedisCache.to_excel(writer,sheet_name="APP " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_REDIS,columns=self.__getColumnsMetricsAppByServiceCloud(Constants.SERVICE_CLOUD_CACHE_REDIS), index=False)
            metricsAppCosmosDb.to_excel(writer,sheet_name="APP " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_COSMOS,columns=self.__getColumnsMetricsAppByServiceCloud(Constants.SERVICE_CLOUD_COSMOS_DB), index=False)            
            metricsAzureSql.to_excel(writer,sheet_name="AZURE " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_SQL,columns=self.__getColumnsMetricsAzureByServiceCloud(Constants.SERVICE_CLOUD_AZURE_SQL), index=False)
            metricsAzureRedis.to_excel(writer,sheet_name="AZURE " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_REDIS,columns=self.__getColumnsMetricsAzureByServiceCloud(Constants.SERVICE_CLOUD_CACHE_REDIS), index=False)
            metricsAzureCosmos.to_excel(writer,sheet_name="AZURE " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_COSMOS,columns=self.__getColumnsMetricsAzureByServiceCloud(Constants.SERVICE_CLOUD_COSMOS_DB), index=False)                        
            metricsSonarAzureSql.to_excel(writer,sheet_name="SONAR " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_SQL,columns=self.__getColumnsMetricsSonarByServiceCloud(Constants.SERVICE_CLOUD_AZURE_SQL), index=False)
            metricsSonarRedisCache.to_excel(writer,sheet_name="SONAR " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_REDIS,columns=self.__getColumnsMetricsSonarByServiceCloud(Constants.SERVICE_CLOUD_CACHE_REDIS), index=False)            
            assesmentAzureSql.to_excel(writer,sheet_name="ASSESMENT " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_SQL,columns=self.__getColumnsMetricsAssesmentByServiceCloud(Constants.SERVICE_CLOUD_AZURE_SQL), index=False)
            assesmentRedisCache.to_excel(writer,sheet_name="ASSESMENT " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_REDIS,columns=self.__getColumnsMetricsAssesmentByServiceCloud(Constants.SERVICE_CLOUD_CACHE_REDIS), index=False)
            assesmentCosmosDb.to_excel(writer,sheet_name="ASSESMENT " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_COSMOS,columns=self.__getColumnsMetricsAssesmentByServiceCloud(Constants.SERVICE_CLOUD_COSMOS_DB), index=False)
            baseActivos.to_excel(writer,sheet_name="BASE ACTIVOS", index=False)

    def exportExcelSummaryAssesment(self,period,baseActivos:pd.DataFrame,
                              squadsMaturityLevel:pd.DataFrame,squadsAzureSql:pd.DataFrame,squadsRedisCache:pd.DataFrame,squadsCosmosDb:pd.DataFrame,
                              assesmentAzureSql:pd.DataFrame,assesmentRedisCache:pd.DataFrame,assesmentCosmosDb:pd.DataFrame
                              ):
        file = Utils.getPathDirectory(Constants.PATH_OUTPUT_FILE_ASSESMENT_SUMMARY.format(period=period))

        with pd.ExcelWriter(file) as writer:
            squadsMaturityLevel.to_excel(writer,sheet_name=Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_GENERAL,columns=self.__getColumnsSquadsGeneral(), index=False)
            squadsAzureSql.to_excel(writer,sheet_name=Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_SQL,columns=self.__getColumnsAssesmentSquadsServiceCloud(Constants.SERVICE_CLOUD_AZURE_SQL), index=False)
            squadsRedisCache.to_excel(writer,sheet_name=Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_REDIS,columns=self.__getColumnsAssesmentSquadsServiceCloud(Constants.SERVICE_CLOUD_CACHE_REDIS), index=False)
            squadsCosmosDb.to_excel(writer,sheet_name=Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_COSMOS,columns=self.__getColumnsAssesmentSquadsServiceCloud(Constants.SERVICE_CLOUD_COSMOS_DB), index=False)
            assesmentAzureSql.to_excel(writer,sheet_name="ASSESMENT " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_SQL,columns=self.__getColumnsMetricsAssesmentByServiceCloud(Constants.SERVICE_CLOUD_AZURE_SQL), index=False)
            assesmentRedisCache.to_excel(writer,sheet_name="ASSESMENT " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_REDIS,columns=self.__getColumnsMetricsAssesmentByServiceCloud(Constants.SERVICE_CLOUD_CACHE_REDIS), index=False)
            assesmentCosmosDb.to_excel(writer,sheet_name="ASSESMENT " + Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_COSMOS,columns=self.__getColumnsMetricsAssesmentByServiceCloud(Constants.SERVICE_CLOUD_COSMOS_DB), index=False)
            baseActivos.to_excel(writer,sheet_name="BASE ACTIVOS", index=False)

    def __getColumnsSquadsGeneral(self)->list[str]:
        columns:list[str] = ["tribeCode","tribe","squadCode","squad","group","cmt","maturityLevel",
                             "maturityLevelAzureSql","maturityLevelRedisCache","maturityLevelCosmosDb"]
        
        return columns
    
    def __getColumnsSquadsServiceCloud(self,serviceCloud:str)->list[str]:
        model:any = Utils.findObjectJson(self.__metricsModel,"serviceCloud",serviceCloud)        

        columns:list[str] = ["tribeCode","tribe","squadCode","squad","group","cmt","applyPractice","maturityLevel"]
        
        for category in model["categories"]:
            columns.append(category["category"])
            for metric in category["metrics"]:
                columns.append(metric["metric"])
                for variable in metric["variables"]:
                    columns.append(variable["variable"])

        columns.append("app")

        return columns

    def __getColumnsAssesmentSquadsServiceCloud(self,serviceCloud:str)->list[str]:
        model:any = Utils.findObjectJson(self.__metricsModel,"serviceCloud",serviceCloud)        

        columns:list[str] = ["tribeCode","tribe","squadCode","squad","group","cmt","applyPractice","maturityLevel"]
        
        for category in model["categories"]:
            columns.append(category["category"])
            for metric in category["metrics"]:
                columns.append(metric["metric"])
                for variable in metric["variables"]:
                    if(not variable["type"]=="assesment"): continue

                    columns.append(variable["variable"])

        columns.append("app")

        return columns

    def __getColumnsMetricsAppByServiceCloud(self,serviceCloud:str)->list[str]:
        columns:list[str] = ["app"]

        if(serviceCloud==Constants.SERVICE_CLOUD_AZURE_SQL):
            columns += Constants.AZURE_MONITOR_AZURE_SQL_METRICS
            columns.append(Constants.METRIC_SONAR_CONNECTION_POOL)
        elif(serviceCloud==Constants.SERVICE_CLOUD_CACHE_REDIS):
            columns += Constants.AZURE_MONITOR_AZURE_REDIS_METRICS
            columns.append(Constants.METRIC_SONAR_CONNECTION_POOL)            
        elif(serviceCloud==Constants.SERVICE_CLOUD_COSMOS_DB):
            columns += Constants.AZURE_MONITOR_AZURE_COSMOS_METRICS
        
        return columns    
    
    def __getColumnsMetricsAzureByServiceCloud(self,serviceCloud:str)->list[str]:
        columns:list[str] = ["id","subscriptionId","resourceGroup","app","name"]

        if(serviceCloud==Constants.SERVICE_CLOUD_AZURE_SQL):
            columns += self.__getColumnsVariableWithPoints(Constants.AZURE_MONITOR_AZURE_SQL_METRICS)          
        elif(serviceCloud==Constants.SERVICE_CLOUD_CACHE_REDIS):
            columns += self.__getColumnsVariableWithPoints(Constants.AZURE_MONITOR_AZURE_REDIS_METRICS)
        elif(serviceCloud==Constants.SERVICE_CLOUD_COSMOS_DB):
            columns += self.__getColumnsVariableWithPoints(Constants.AZURE_MONITOR_AZURE_COSMOS_METRICS)
        
        return columns

    def __getColumnsMetricsSonarByServiceCloud(self,serviceCloud:str)->list[str]:
        columns:list[str] = ["app","repository"]

        if(serviceCloud==Constants.SERVICE_CLOUD_AZURE_SQL):
            columns += self.__getColumnsVariableWithPoints([Constants.METRIC_SONAR_CONNECTION_POOL])          
        elif(serviceCloud==Constants.SERVICE_CLOUD_CACHE_REDIS):
            columns += self.__getColumnsVariableWithPoints([Constants.METRIC_SONAR_CONNECTION_POOL])          
        
        return columns

    def __getColumnsMetricsAssesmentByServiceCloud(self,serviceCloud:str)->list[str]:
        columns:list[str] = ["employeeCode","employeeNameForm","employeeEmailForm","employeeSpecialtyForm","name","fatherLastName","motherLastName","email","squad","squadCode","specialty"]

        if(serviceCloud==Constants.SERVICE_CLOUD_AZURE_SQL):
            columns += self.__getColumnsVariableWithPoints(Constants.ASSESMENT_METRICS_AZURE_SQL)          
        elif(serviceCloud==Constants.SERVICE_CLOUD_CACHE_REDIS):
            columns += self.__getColumnsVariableWithPoints(Constants.ASSESMENT_METRICS_CACHE_REDIS)
        elif(serviceCloud==Constants.SERVICE_CLOUD_COSMOS_DB):
            columns += self.__getColumnsVariableWithPoints(Constants.ASSESMENT_METRICS_COSMOS_DB)
        
        return columns        

    def __getColumnsVariableWithPoints(self,columnsMetric:list[str])->list[str]:
        columns:list[str] = []

        for metric in columnsMetric:
            columns.append(metric)
            columns.append(metric + "Points")

        return columns