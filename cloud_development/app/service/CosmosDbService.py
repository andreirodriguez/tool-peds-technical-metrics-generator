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
    __azureCosts:pd.DataFrame

    def __init__(self,metricsAzureMonitor:any):
        self.__metricsAzureMonitor = metricsAzureMonitor
        self.__cosmosDbRepository = CosmosDbRepository()

    def __getMetric(self,nameMetric:str)->pd.DataFrame:
        metricAzure = [metric for metric in self.__metricsAzureMonitor if metric["metric"]==nameMetric][0]

        return metricAzure

    def __listAllCosmosDatabases(self)->pd.DataFrame:
        return self.__cosmosDbRepository.getAllCosmosDatabases()

    def listSummaryCosmosDatabases(self)->pd.DataFrame:
        return self.__cosmosDbRepository.getSummaryCosmosDatabases()

    def extractMetricsAzure(self,period:str,maximumThreads:int):
        databases = self.__listAllCosmosDatabases()
        self.__azureCosts = self.__cosmosDbRepository.getAzureCosts(period)

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
        metric.azureCosts = self.__getAzureCost(metric)

        metric.averageHalfRequestUnits = self.__getAverageHalfRequestUnits(azureMonitor)
        metric.maximumRequestUnits = self.__getMaximumRequestUnits(azureMonitor)
        metric.totalRequestUnits = self.__getTotalRequestUnits(azureMonitor)

        self.__setRusConsumption(azureMonitor,metric,metricAzureMonitor["limitValue"])
        metric.maximumRusConsumptionPoints = Utils.getMetricPointsAzureMonitor(metric.maximumRusConsumption,metricAzureMonitor["ranges"])

        self.__setRusConsumptionProposed(azureMonitor,metric,metricAzureMonitor["limitValue"])

        return metric

    def __getAverageHalfRequestUnits(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_TOTAL_REQUEST_UNITS]))]
        azureMonitor = azureMonitor[(azureMonitor['aggregation']=="maximum")]

        value = azureMonitor["value"].quantile(Constants.AZURE_MONITOR_AZURE_COSMOS_RU_PERCENTILE)

        if(math.isnan(value)): return None

        return round(value,2)
     

    def __getTotalRequestUnits(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_TOTAL_REQUEST_UNITS]))]
        azureMonitor = azureMonitor[(azureMonitor['aggregation']=="total")]

        value = azureMonitor["value"].sum()

        if(math.isnan(value)): return 0.0

        return round(value,2)


    def __getAzureCost(self,metric:CosmosDbMetric)->Decimal:
        costs = self.__azureCosts[(self.__azureCosts['subscriptionId']==metric.subscriptionId)]
        costs = costs[(costs['resourceGroup']==metric.resourceGroup.lower())]
        costs = costs[(costs['name']==metric.name.lower())]

        value = costs["azureCost"].sum()

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
        azureRus:pd.DataFrame = self.__getRusMaximumSpikes(azureMonitor,metric.provisionedMinThroughput,maxRusPercentage)

        metric.averageSpikesRequestUnits = round(azureRus["value"].mean(),2)
        metric.maximumRusConsumption = len(azureRus.index)


    def __setRusConsumptionProposed(self,azureMonitor:pd.DataFrame,metric:CosmosDbMetric,maxRusPercentage:Decimal):
        metric.provisionedMinThroughputProposed = self.__getThroughputIncrement(metric.averageHalfRequestUnits)

        azureRus:pd.DataFrame
        spikesAcceptable:int = round((Constants.AZURE_MONITOR_AZURE_COSMOS_QUANTITY_RUNNING * (Constants.AZURE_MONITOR_AZURE_COSMOS_PERCENTAGE_SPIKES_ACCEPTABLE / 100)),0)
        spikesRus:int = spikesAcceptable
        while(spikesRus>=spikesAcceptable):
            azureRus = self.__getRusMaximumSpikes(azureMonitor,metric.provisionedMinThroughputProposed,maxRusPercentage)

            spikesRus = len(azureRus.index)

            if(spikesRus>=spikesAcceptable): 
                metric.provisionedMinThroughputProposed += Constants.AZURE_MONITOR_AZURE_COSMOS_RU_INCREMENT
            else:
                metric.spikesThroughputProposed = spikesRus

        metric.autoscaleMaxThroughputProposed = round((metric.maximumRequestUnits * (1 + (Constants.AZURE_MONITOR_AZURE_COSMOS_PERCENTAGE_AUTOSCALE_PROPOSED / 100))),2)
        metric.autoscaleMaxThroughputProposed = self.__getThroughputIncrement(metric.autoscaleMaxThroughputProposed) + Constants.AZURE_MONITOR_AZURE_COSMOS_RU_INCREMENT
        autoscaleMinThroughput:Decimal = Constants.AZURE_MONITOR_AZURE_COSMOS_RU_INCREMENT * 10

        if(metric.autoscaleMaxThroughputProposed < autoscaleMinThroughput): metric.autoscaleMaxThroughputProposed = autoscaleMinThroughput

        if(metric.provisionedMinThroughputProposed==Constants.AZURE_MONITOR_AZURE_COSMOS_RU_INCREMENT and metric.autoscaleMaxThroughputProposed>autoscaleMinThroughput):
            metric.provisionedMinThroughputProposed = metric.autoscaleMaxThroughputProposed * (Constants.AZURE_MONITOR_AZURE_COSMOS_PERCENTAGE_PROVISIONEDTHROUGHPUT / 100)
        else:
            provisionedMinThroughput:Decimal = metric.provisionedMinThroughputProposed * (Constants.AZURE_MONITOR_AZURE_COSMOS_PERCENTAGE_PROVISIONEDTHROUGHPUT / 100)

            if(metric.provisionedMinThroughputProposed < provisionedMinThroughput): metric.provisionedMinThroughputProposed = provisionedMinThroughput

        metric.percentageUtilizationProposed = round(((metric.provisionedMinThroughputProposed * 100) / metric.autoscaleMaxThroughputProposed),2)

    def __getThroughputIncrement(self,provisionedThroughput)->Decimal:
        proposedThroughput:Decimal = Constants.AZURE_MONITOR_AZURE_COSMOS_RU_INCREMENT

        while(proposedThroughput<provisionedThroughput):
            proposedThroughput += Constants.AZURE_MONITOR_AZURE_COSMOS_RU_INCREMENT

        return proposedThroughput


    def __getRusMaximumSpikes(self,azureMonitor:pd.DataFrame,provisionedThroughput:Decimal,maxRusPercentage:Decimal):
        azureRus = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_COSMOS_METRIC_TOTAL_REQUEST_UNITS]))]
        azureRus = azureRus[(azureRus['aggregation']=="maximum")]

        azureRus["percentageConsumptionProvisioned"] = azureRus.apply(lambda record: self.__calculatePercentageConsumptionProvisioned(record["value"],provisionedThroughput),axis=1)

        azureRus = azureRus[(azureRus['percentageConsumptionProvisioned'] > maxRusPercentage)]

        return azureRus

    def __calculatePercentageConsumptionProvisioned(self,consumptionRus:Decimal,provisionedThroughput:Decimal)->Decimal:
        percentageRusConsumption:Decimal = 0.0

        if(provisionedThroughput==0.0): return percentageRusConsumption

        provisionedThroughput = round((consumptionRus * 100) / provisionedThroughput,2)

        return provisionedThroughput
    

    def getContainersCosmosDatabases(self)->pd.DataFrame:
        data = self.__cosmosDbRepository.getContainersCosmosDatabases()

        data["provisionedMinThroughput"] = data.apply(lambda record: self.__getProvisionedMinThroughputContainer(record["provisionedTroughputDatabase"],record["provisionedTroughputContainer"],record["troughputMode"]),axis=1)
        data["azureCostActually"] = data.apply(lambda record: self.__getCostProvisionedThroughputContainer(record["provisionedMinThroughput"],record["troughputMode"]),axis=1)

        data["provisionedProposedThroughput"] = data.apply(lambda record: self.__getProvisionedThroughputProposed(record["provisionedMinThroughput"],record["troughputMode"]),axis=1)
        data["azureCostProposed"] = data.apply(lambda record: self.__getCostProvisionedThroughputContainer(record["provisionedProposedThroughput"],record["troughputMode"]),axis=1)        

        return data       
    
    def __getProvisionedMinThroughputContainer(self,provisionedTroughputDatabase:Decimal,provisionedThroughput:Decimal,troughputMode:str)->Decimal:
        if(not Utils.isNumber(provisionedThroughput)): return provisionedTroughputDatabase

        if(troughputMode==Constants.AZURE_MONITOR_COSMOS_DB_TROUGHPUT_MODE_AUTOSCALE):
            provisionedThroughput = provisionedThroughput * (Constants.AZURE_MONITOR_AZURE_COSMOS_PERCENTAGE_PROVISIONEDTHROUGHPUT / 100)

        return provisionedThroughput
    
    def __getCostProvisionedThroughputContainer(self,provisionedThroughput:Decimal,troughputMode:str)->Decimal:
        if(not Utils.isNumber(provisionedThroughput)): return None

        azureCost:Decimal 
        if(troughputMode==Constants.AZURE_MONITOR_COSMOS_DB_TROUGHPUT_MODE_AUTOSCALE):
            azureCost = (Constants.AZURE_MONITOR_AZURE_COSMOS_COST_RU_AUTOSCALE * provisionedThroughput) * Constants.HOURS_FOR_DAYS * Constants.DAYS_FOR_MONTH_AZURE
        else:
            azureCost = (((Constants.AZURE_MONITOR_AZURE_COSMOS_COST_RU_MANUAL * provisionedThroughput) / 10) * 15) * Constants.HOURS_FOR_DAYS * Constants.DAYS_FOR_MONTH_AZURE


        return round(azureCost,2)
    
    def __getProvisionedThroughputProposed(self,provisionedThroughput:Decimal,troughputMode:str)->Decimal:
        if(not Utils.isNumber(provisionedThroughput)): return None

        if(provisionedThroughput>Constants.AZURE_MONITOR_AZURE_COSMOS_PROVISIONEDTHROUGHPUT_PROPOSED): provisionedThroughput = Constants.AZURE_MONITOR_AZURE_COSMOS_PROVISIONEDTHROUGHPUT_PROPOSED

        return round(provisionedThroughput,2)    
