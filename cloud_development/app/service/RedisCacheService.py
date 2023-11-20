import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from decimal import Decimal

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

    def listAllRedisDatabases(self)->pd.DataFrame:
        return self.__redisCacheRepository.getAllRedisDatabases()
    
    def calculateMetrics(self,tenantId:str,database:RedisCache)->RedisCacheMetric:
        metric:RedisCacheMetric = RedisCacheMetric(database)

        metricAzureMonitor:any

        azureMonitor:pd.DataFrame = self.__redisCacheRepository.getAzureMonitor(tenantId,database)

        metricAzureMonitor = self.__getMetric("cachemissrate")
        metric.cacheMissRate = self.__getCacheMissRate(azureMonitor)
        metric.cacheMissRatePoints = Utils.getMetricPointsAzureMonitor(metric.cacheMissRate,metricAzureMonitor["ranges"])     

        metricAzureMonitor = self.__getMetric("percentProcessorTime")
        metric.maximumProcessorConsumption = self.__getMaximumProcessorConsumption(azureMonitor,metricAzureMonitor["limitValue"])
        metric.maximumProcessorConsumptionPoints = Utils.getMetricPointsAzureMonitor(metric.maximumProcessorConsumption,metricAzureMonitor["ranges"])             

        metricAzureMonitor = self.__getMetric("percentProcessorTime")
        metric.maximumMemoryConsumption = self.__getMaximumMemoryConsumption(azureMonitor,metricAzureMonitor["limitValue"])
        metric.maximumMemoryConsumptionPoints = Utils.getMetricPointsAzureMonitor(metric.maximumMemoryConsumption,metricAzureMonitor["ranges"])                     

        return metric    
    
    def __getCacheMissRate(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitorSuccess = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_REDIS_METRIC_CACHE_HITS]))]

        successful:Decimal = azureMonitorSuccess["value"].sum()

        value:Decimal = 0.00

        if(successful==value): return value

        azureMonitorFailed = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_REDIS_METRIC_CACHE_MISSES]))]

        failed:Decimal = azureMonitorFailed["value"].sum()  

        if(failed==value): return value

        value = (failed * 100) / successful

        return round(value,2)
    
    def __getMaximumProcessorConsumption(self,azureMonitor:pd.DataFrame,maxProcessorPercentage:Decimal)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_REDIS_METRIC_PERCENT_PROCESSOR]))]

        azureMonitor = azureMonitor[(azureMonitor['value'] > maxProcessorPercentage)]

        value = len(azureMonitor.index)

        return value           
    
    def __getMaximumMemoryConsumption(self,azureMonitor:pd.DataFrame,maxMemoryPercentage:Decimal)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_REDIS_METRIC_MEMORY_PERCENTAGE]))]

        azureMonitor = azureMonitor[(azureMonitor['value'] > maxMemoryPercentage)]

        value = len(azureMonitor.index)

        return value               