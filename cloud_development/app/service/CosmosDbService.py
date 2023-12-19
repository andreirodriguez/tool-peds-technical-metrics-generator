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

        self.__setProvisionedThroughput(azureMonitor,metric)
        metric.autoscaleMaxThroughput = self.__getTotalAutoscaleMaxThroughput(azureMonitor)

        metric.averageHalfRequestUnits = self.__getAverageHalfRequestUnits(azureMonitor)
        metric.averageSpikesRequestUnits = self.__getAverageSpikesRequestUnits(azureMonitor,metric.averageHalfRequestUnits)
        metric.maximumRequestUnits = self.__getMaximumRequestUnits(azureMonitor)
        metric.totalRequestUnits = self.__getTotalRequestUnits(azureMonitor)

        self.__setRusConsumption(azureMonitor,metric,metricAzureMonitor["limitValue"])
        metric.maximumRusConsumptionPoints = Utils.getMetricPointsAzureMonitor(metric.maximumRusConsumption,metricAzureMonitor["ranges"])     

        return metric

    def __getAverageHalfRequestUnits(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_TOTAL_REQUEST_UNITS]))]
        azureMonitor = azureMonitor[(azureMonitor['aggregation']=="maximum")]

        value = azureMonitor["value"].quantile(Constants.AZURE_MONITOR_AZURE_COSMOS_RU_PERCENTILE)

        if(math.isnan(value)): return None

        return round(value,2)
    
    def __getAverageSpikesRequestUnits(self,azureMonitor:pd.DataFrame,averageHalf:float)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_TOTAL_REQUEST_UNITS]))]
        azureMonitor = azureMonitor[(azureMonitor['aggregation']=="maximum")]
        azureMonitor = azureMonitor[(azureMonitor['value']>averageHalf)]

        value = azureMonitor["value"].mean()

        if(math.isnan(value)): return None

        return round(value,2)    

    def __getTotalRequestUnits(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_TOTAL_REQUEST_UNITS]))]
        azureMonitor = azureMonitor[(azureMonitor['aggregation']=="total")]

        value = azureMonitor["value"].sum()

        if(math.isnan(value)): return 0.0

        return round(value,2)

    def __getMaximumRequestUnits(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_TOTAL_REQUEST_UNITS]))]
        azureMonitor = azureMonitor[(azureMonitor['aggregation']=="maximum")]

        value = azureMonitor["value"].max()

        if(math.isnan(value)): return 0.0

        return round(value,2)


    def __setProvisionedThroughput(self,azureMonitor:pd.DataFrame,metric:CosmosDbMetric):
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_PROVISIONEDTHROUGHPUT]))]

        metric.provisionedMinThroughput = round(azureMonitor["value"].min(),2)
        metric.provisionedMaxThroughput = round(azureMonitor["value"].max(),2)

    def __getTotalAutoscaleMaxThroughput(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_AUTOSCALEMAXTHROUGHPUT]))]

        value = azureMonitor["value"].max()

        if(math.isnan(value)): return None

        return round(value,2)


    def __setRusConsumption(self,azureMonitor:pd.DataFrame,metric:CosmosDbMetric,maxRusPercentage:Decimal):
        azureRus = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_TOTAL_REQUEST_UNITS]))]
        azureRus = azureRus[(azureRus['aggregation']=="maximum")]
        azureRus["intervalTimeStampProvisioned"] = azureRus.apply(lambda record: Utils.getIntervalHour(record["intervalTimeStamp"]),axis=1)

        azureProvisioned = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_PROVISIONEDTHROUGHPUT]))]
        azureProvisioned = azureProvisioned[['intervalTimeStamp', 'value']].copy()
        azureProvisioned = azureProvisioned.rename(columns={"intervalTimeStamp": "intervalTimeStampProvisioned", "value": "provisionedThroughput"})

        azureRus = pd.merge(azureRus, azureProvisioned, on="intervalTimeStampProvisioned", how="left")

        azureRus["percentageConsumptionProvisioned"] = azureRus.apply(lambda record: round((record["value"] * 100) / record["provisionedThroughput"],2),axis=1)

        metric.percentageRusConsumption = round(azureRus["percentageConsumptionProvisioned"].mean(),2)
        metric.maximumRusConsumption = len(azureRus[(azureRus['percentageConsumptionProvisioned'] > maxRusPercentage)].index)



