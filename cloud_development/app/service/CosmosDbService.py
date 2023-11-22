import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from decimal import Decimal
import concurrent.futures

import math

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

    def __listAllCosmosDatabases(self)->pd.DataFrame:
        return self.__cosmosDbRepository.getAllCosmosDatabases()
    
    def extractMetricsAzure(self,maximumThreads:int):
        databases = self.__listAllCosmosDatabases()

        Utils.logInfo(f"Inicio a calcular información de las métricas de {str(len(databases))} base de datos Cosmos Db")

        metrics:list[CosmosDbMetric] = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=maximumThreads) as executor:
            metrics += executor.map(self.__extractMetricsAzureByDatabase, databases)

        metrics = list(filter(lambda record: not record == None, metrics))

        Utils.logInfo(f"Fin a calcular información de las métricas de {str(len(databases))} base de datos Cosmos Db")

        return metrics


    def __extractMetricsAzureByDatabase(self,database:CosmosDb)->CosmosDbMetric:
        Utils.logInfo(f"Cálculo métricas del recurso Cosmos Db: {database.id}")

        try:
            metric:CosmosDbMetric = self.__calculateMetrics(database)

            return metric
        except Exception as ex:
            Utils.logError(f"Error en el cálculo de metricas del recurso Cosmos Db {database.id}",ex)

            return None    
    
    def __calculateMetrics(self,database:CosmosDb)->CosmosDbMetric:
        metric:CosmosDbMetric = CosmosDbMetric(database)

        metricAzureMonitor:any

        azureMonitor:pd.DataFrame = self.__cosmosDbRepository.getAzureMonitor(database)

        metricAzureMonitor = self.__getMetric("NormalizedRUConsumption")
        metric.provisionedThroughput = self.__getTotalProvisionedThroughput(azureMonitor)
        metric.autoscaleMaxThroughput = self.__getTotalAutoscaleMaxThroughput(azureMonitor)
        metric.totalRequestUnits = self.__getTotalRequestUnits(azureMonitor)
        metric.maximumRusConsumption = self.__getRusConsumption(azureMonitor,metricAzureMonitor["limitValue"])
        metric.maximumRusConsumptionPoints = Utils.getMetricPointsAzureMonitor(metric.maximumRusConsumption,metricAzureMonitor["ranges"])     

        return metric
    
    def __getTotalRequestUnits(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_TOTAL_REQUEST_UNITS]))]

        value = azureMonitor["value"].sum()

        if(math.isnan(value)): return 0.0

        return round(value,2)

    def __getTotalProvisionedThroughput(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_PROVISIONEDTHROUGHPUT]))]

        value = azureMonitor["value"].min()

        if(math.isnan(value)): return None

        return round(value,2)

    def __getTotalAutoscaleMaxThroughput(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_AUTOSCALEMAXTHROUGHPUT]))]

        value = azureMonitor["value"].max()

        if(math.isnan(value)): return None

        return round(value,2)


    def __getRusConsumption(self,azureMonitor:pd.DataFrame,maxRusPercentage:Decimal)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_RU_CONSUMPTION]))]

        azureMonitor = azureMonitor[(azureMonitor['value'] > maxRusPercentage)]

        value = len(azureMonitor.index)

        return value       

