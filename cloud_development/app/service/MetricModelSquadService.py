import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from decimal import Decimal
import math

from cloud_development.app.repository.SquadPrioritizedRepository import SquadPrioritizedRepository

import cloud_development.app.common.Constants as Constants
from cloud_development.app.common.Utils import Utils

from cloud_development.app.service.MaturityLevelService import MaturityLevelService

from cloud_development.app.domain.AzureSqlMetric import AzureSqlMetric
from cloud_development.app.domain.RedisCacheMetric import RedisCacheMetric
from cloud_development.app.domain.CosmosDbMetric import CosmosDbMetric

class MetricModelSquadService():

    __maturityLevelService:MaturityLevelService  
    __squadPrioritizedRepository:SquadPrioritizedRepository

    def __init__(self,maturityLevelService:MaturityLevelService):
        self.__maturityLevelService = maturityLevelService
        self.__squadPrioritizedRepository = SquadPrioritizedRepository()

    def calculateMetricAzureSqlBySquad(self,metricsApp:pd.DataFrame,metricsAssesment:pd.DataFrame,baseActivos:pd.DataFrame)->pd.DataFrame:
        squads:pd.DataFrame = self.__squadPrioritizedRepository.getSquadsByServiceCloud(Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_SQL)

        squads = self.__getPointsMetricBySquad(squads,baseActivos,
                                      Constants.AZURE_MONITOR_AZURE_SQL_METRICS,metricsApp,
                                      [Constants.METRIC_SONAR_CONNECTION_POOL],metricsApp,
                                      Constants.ASSESMENT_METRICS_AZURE_SQL,metricsAssesment
                                      )
        
        self.__maturityLevelService.calculateMaturityLevelBySquad(Constants.SERVICE_CLOUD_AZURE_SQL,squads)

        return squads
    
    def calculateMetricCacheRedisBySquad(self,metricsApp:pd.DataFrame,metricsAssesment:pd.DataFrame,baseActivos:pd.DataFrame)->pd.DataFrame:
        squads:pd.DataFrame = self.__squadPrioritizedRepository.getSquadsByServiceCloud(Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_REDIS)

        squads = self.__getPointsMetricBySquad(squads,baseActivos,
                                      Constants.AZURE_MONITOR_AZURE_REDIS_METRICS,metricsApp,
                                      [Constants.METRIC_SONAR_CONNECTION_POOL],metricsApp,
                                      Constants.ASSESMENT_METRICS_CACHE_REDIS,metricsAssesment
                                      )
        
        self.__maturityLevelService.calculateMaturityLevelBySquad(Constants.SERVICE_CLOUD_CACHE_REDIS,squads)

        return squads    
    
    def calculateMetricCosmosDbBySquad(self,metricsApp:pd.DataFrame,metricsAssesment:pd.DataFrame,baseActivos:pd.DataFrame)->pd.DataFrame:
        squads:pd.DataFrame = self.__squadPrioritizedRepository.getSquadsByServiceCloud(Constants.PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_COSMOS)

        squads = self.__getPointsMetricBySquad(squads,baseActivos,
                                      Constants.AZURE_MONITOR_AZURE_COSMOS_METRICS,metricsApp,
                                      [],metricsApp,
                                      Constants.ASSESMENT_METRICS_COSMOS_DB,metricsAssesment
                                      )

        self.__maturityLevelService.calculateMaturityLevelBySquad(Constants.SERVICE_CLOUD_COSMOS_DB,squads)

        return squads        
    
    def __getPointsMetricBySquad(self,squads:pd.DataFrame,baseActivos:pd.DataFrame,
                                 metricsListAzure:list[str],metricsDataAzure:pd.DataFrame,
                                 metricsListSonar:list[str],metricsDataSonar:pd.DataFrame,
                                 metricsListAssesment:list[str],metricsDataAssesment:pd.DataFrame)->pd.DataFrame:        
        squads["app"] = squads.apply(lambda record: self.__getAppsBySquad(record["squadCode"],baseActivos),axis=1)
        squads["hasAzure"] = squads.apply(lambda record: self.__hazAzure(record["app"],metricsDataAzure),axis=1)

        for metric in metricsListAzure:
            squads[metric] = squads.apply(lambda record: self.__getPointsMetricsAzureBySquad(record["app"],metricsDataAzure,metric),axis=1)

        for metric in metricsListSonar:
            squads[metric] = squads.apply(lambda record: self.__getPointsMetricsSonarBySquad(record["app"],metricsDataSonar,metric),axis=1)

        for metric in metricsListAssesment:
            squads[metric] = squads.apply(lambda record: self.__getPointsMetricsAssesmentBySquad(record["squadCode"],metricsDataAssesment,metric),axis=1)

        return squads
    
    def __getAppsBySquad(self,squadCode:str,baseActivos:pd.DataFrame)->str:
        appBySquad:pd.DataFrame = baseActivos[(baseActivos['squadCode']==squadCode)]
        appBySquad = appBySquad[["app","squadCode"]].copy()
        appBySquad = appBySquad.sort_values(['app','squadCode'], ascending = [True,True])
        appBySquad = appBySquad.drop_duplicates(['app','squadCode'],keep ='first')  

        if(len(appBySquad.index)==0): return None

        apps:str = ""
        for index,row in appBySquad.iterrows():
            apps = "," + row.app + apps

        apps = apps[1:len(apps)]

        return apps    

    def __hazAzure(self,apps:str,metricsAzure:pd.DataFrame)->Decimal:        
        metricsAzure:pd.DataFrame = metricsAzure[(metricsAzure['app'].isin(apps.split(",")))]

        if(len(metricsAzure.index)==0): return False

        return True

    def __getPointsMetricsAzureBySquad(self,apps:str,metricsData:pd.DataFrame,metric:str)->Decimal:        
        metricsBySquad:pd.DataFrame = metricsData[(metricsData['app'].isin(apps.split(",")))]

        if(len(metricsBySquad.index)==0): return None

        points:Decimal = metricsBySquad[metric].mean()

        if(math.isnan(points)): return None

        return points    
    
    def __getPointsMetricsSonarBySquad(self,apps:str,metricsData:pd.DataFrame,metric:str)->Decimal:        
        metricsBySquad:pd.DataFrame = metricsData[(metricsData['app'].isin(apps.split(",")))]

        if(len(metricsBySquad.index)==0): return None

        points:Decimal = metricsBySquad[metric].mean()

        if(math.isnan(points)): return None

        return points
    
    def __getPointsMetricsAssesmentBySquad(self,squadCode:str,metricsData:pd.DataFrame,metric:str)->Decimal:        
        metricsBySquad:pd.DataFrame = metricsData[(metricsData['squadCode']==squadCode)]

        if(len(metricsData.index)==0): return None

        points:Decimal = metricsBySquad[metric + "Points"].mean()

        if(math.isnan(points)): return None

        return round(points,2)    
    

    
    