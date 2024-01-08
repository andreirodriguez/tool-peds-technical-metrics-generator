import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from decimal import Decimal
import concurrent.futures

from cloud_development.app.repository.RedisCacheRepository import RedisCacheRepository

from cloud_development.app.domain.RedisCache import RedisCache
from cloud_development.app.domain.RedisCacheMetric import RedisCacheMetric
import cloud_development.app.common.Constants as Constants

from cloud_development.app.common.Utils import Utils

class RedisCacheService():
    
    __metricsAzureMonitor:any  
    __redisCacheRepository:RedisCacheRepository


    def __init__(self,metricsAzureMonitor:any):
        self.__metricsAzureMonitor = metricsAzureMonitor
        self.__redisCacheRepository = RedisCacheRepository()

    def __getMetric(self,nameMetric:str)->pd.DataFrame:
        metricAzure = [metric for metric in self.__metricsAzureMonitor if metric["metric"]==nameMetric][0]

        return metricAzure

    def __listAllRedisDatabases(self)->pd.DataFrame:
        return self.__redisCacheRepository.getAllRedisDatabases()

    def listSummaryRedisDatabases(self)->pd.DataFrame:
        return self.__redisCacheRepository.getSummaryRedisDatabases()

    def extractMetricsAzure(self,maximumThreads:int):
        databases = self.__listAllRedisDatabases()

        Utils.logInfo(f"Inicio a calcular información de las métricas de {str(len(databases))} base de datos Redis Cache")

        metrics:list[RedisCacheMetric] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=maximumThreads) as executor:
            metrics += executor.map(self.__extractMetricsAzureByDatabase, databases)

        metrics = list(filter(lambda record: not record == None, metrics))

        Utils.logInfo(f"Fin a calcular información de las métricas de {str(len(databases))} base de datos Redis Cache")

        return metrics


    def __extractMetricsAzureByDatabase(self,database:RedisCache)->RedisCacheMetric:
        Utils.logInfo(f"Cálculo métricas del recurso Redis Cache: {database.id}")

        try:
            metric:RedisCacheMetric = self.__calculateMetrics(database)

            return metric
        except Exception as ex:
            Utils.logError(f"Error en el cálculo de metricas del recurso Redis Cache {database.id}",ex)

            return None

    def __calculateMetrics(self,database:RedisCache)->RedisCacheMetric:
        metric:RedisCacheMetric = RedisCacheMetric(database)

        metricAzureMonitor:any

        azureMonitor:pd.DataFrame = self.__redisCacheRepository.getAzureMonitor(database)

        metricAzureMonitor = self.__getMetric("cachemissrate")
        self.__getCacheMissRate(azureMonitor,metric)
        metric.cacheMissRatePoints = Utils.getMetricPointsAzureMonitor(metric.cacheMissRate,metricAzureMonitor["ranges"])     

        metricAzureMonitor = self.__getMetric("percentProcessorTime")
        self.__setMaximumProcessorConsumption(azureMonitor,metricAzureMonitor["limitValue"],metric)
        metric.maximumProcessorConsumptionPoints = Utils.getMetricPointsAzureMonitor(metric.maximumProcessorConsumption,metricAzureMonitor["ranges"])             

        metricAzureMonitor = self.__getMetric("percentProcessorTime")
        self.__setMaximumMemoryConsumption(azureMonitor,metricAzureMonitor["limitValue"],metric)
        metric.maximumMemoryConsumptionPoints = Utils.getMetricPointsAzureMonitor(metric.maximumMemoryConsumption,metricAzureMonitor["ranges"])                     

        return metric    
    
    def __getCacheMissRate(self,azureMonitor:pd.DataFrame,metric:RedisCacheMetric):
        azureMonitorSuccess = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_REDIS_METRIC_CACHE_HITS]))]

        metric.cacheSearchHits = azureMonitorSuccess["value"].sum()

        azureMonitorFailed = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_REDIS_METRIC_CACHE_MISSES]))]

        metric.cacheSearchFailed = azureMonitorFailed["value"].sum()

        metric.cacheSearchTotal = metric.cacheSearchHits + metric.cacheSearchFailed

        value:Decimal = 0.00        

        metric.cacheMissRate = value
        if(metric.cacheSearchTotal>value): 
            metric.cacheMissRate = round(((metric.cacheSearchFailed * 100) / metric.cacheSearchTotal),2)
    
    def __setMaximumProcessorConsumption(self,azureMonitor:pd.DataFrame,maxProcessorPercentage:Decimal,metric:RedisCacheMetric):
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_REDIS_METRIC_PERCENT_PROCESSOR]))]

        metric.halfAverageProcessorValue = azureMonitor["value"].quantile(Constants.AZURE_MONITOR_AZURE_REDIS_CPU_PERCENTILE)
        metric.maximumProcessorValue = azureMonitor["value"].max()

        azureMonitor = azureMonitor[(azureMonitor['value'] > maxProcessorPercentage)]
        metric.maximumProcessorConsumption = len(azureMonitor.index)
    
    def __setMaximumMemoryConsumption(self,azureMonitor:pd.DataFrame,maxMemoryPercentage:Decimal,metric:RedisCacheMetric):
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_REDIS_METRIC_MEMORY_PERCENTAGE]))]

        metric.halfAverageMemoryValue = azureMonitor["value"].quantile(Constants.AZURE_MONITOR_AZURE_REDIS_MEMORY_PERCENTILE)
        metric.maximumMemoryValue = azureMonitor["value"].max()

        azureMonitor = azureMonitor[(azureMonitor['value'] > maxMemoryPercentage)]
        metric.maximumMemoryConsumption = len(azureMonitor.index)