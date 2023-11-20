import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from decimal import Decimal

from cloud_development.app.repository.CosmosDbRepository import CosmosDbRepository

from cloud_development.app.domain.CosmosDb import CosmosDb
from cloud_development.app.domain.CosmosDbMetric import CosmosDbMetric
import cloud_development.app.common.Constants as Constants

from cloud_development.app.common.Utils import Utils

class CosmosDbService():

    __metricsAzureMonitor:any  
    __cosmosDbRepository:CosmosDbRepository

    def __init__(self,metricsAzureMonitor:any):
        self.__metricsAzureMonitor = metricsAzureMonitor
        self.__cosmosDbRepository = CosmosDbRepository()

    def __getMetric(self,nameMetric:str)->pd.DataFrame:
        metricAzure = [metric for metric in self.__metricsAzureMonitor if metric["metric"]==nameMetric][0]

        return metricAzure

    def listAllCosmosDatabases(self)->pd.DataFrame:
        return self.__cosmosDbRepository.getAllCosmosDatabases()
    
    def calculateMetrics(self,database:CosmosDb)->CosmosDbMetric:
        metric:CosmosDbMetric = CosmosDbMetric(database)

        metricAzureMonitor:any

        azureMonitor:pd.DataFrame = self.__cosmosDbRepository.getAzureMonitor(database)

        metricAzureMonitor = self.__getMetric("NormalizedRUConsumption")
        metric.maximumRusConsumption = self.__getTopConsumptionQueries(azureMonitor,metricAzureMonitor["limitValue"])
        metric.maximumRusConsumptionPoints = Utils.getMetricPointsAzureMonitor(metric.maximumRusConsumption,metricAzureMonitor["ranges"])     

        return metric


    def __getTopConsumptionQueries(self,azureMonitor:pd.DataFrame,maxRusPercentage:Decimal)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_RU_CONSUMPTION]))]

        azureMonitor = azureMonitor[(azureMonitor['value'] > maxRusPercentage)]

        value = len(azureMonitor.index)

        return value                