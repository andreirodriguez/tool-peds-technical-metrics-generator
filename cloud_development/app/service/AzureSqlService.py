import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from decimal import Decimal
import concurrent.futures

from cloud_development.app.repository.AzureSqlRepository import AzureSqlRepository
from cloud_development.app.domain.AzureSql import AzureSql
from cloud_development.app.domain.AzureSqlMetric import AzureSqlMetric
import cloud_development.app.common.Constants as Constants

from cloud_development.app.common.Utils import Utils

class AzureSqlService():

    __metricsAzureMonitor:any    
    __azureSqlRepository:AzureSqlRepository

    def __init__(self,metricsAzureMonitor:any):
        self.__metricsAzureMonitor = metricsAzureMonitor
        self.__azureSqlRepository = AzureSqlRepository()

    def __getMetric(self,nameMetric:str)->pd.DataFrame:
        metricAzure = [metric for metric in self.__metricsAzureMonitor if metric["metric"]==nameMetric][0]

        return metricAzure

    def __listAllSqlDatabases(self)->pd.DataFrame:
        return self.__azureSqlRepository.getAllSqlDatabases()
    
    def extractMetricsAzure(self,maximumThreads:int):
        databases = self.__listAllSqlDatabases()

        Utils.logInfo(f"Inicio a calcular información de las métricas de {str(len(databases))} base de datos Azure SQL")

        metrics:list[AzureSqlMetric] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=maximumThreads) as executor:
            metrics += executor.map(self.__extractMetricsAzureByDatabase, databases)

        metrics = list(filter(lambda record: not record == None, metrics))

        Utils.logInfo(f"Fin a calcular información de las métricas de {str(len(databases))} base de datos Azure Sql")

        return metrics


    def __extractMetricsAzureByDatabase(self,database:AzureSql)->AzureSqlMetric:
        Utils.logInfo(f"Cálculo métricas del recurso Azure Sql: {database.id}")

        try:
            metric:AzureSqlMetric = self.__calculateMetrics(database)

            return metric
        except Exception as ex:
            Utils.logError(f"Error en el cálculo de metricas del recurso Azure Sql {database.id}",ex)

            return None
    
    def __calculateMetrics(self,database:AzureSql)->AzureSqlMetric:
        metric:AzureSqlMetric = AzureSqlMetric(database)

        metricAzureMonitor:any

        metricAzureMonitor = self.__getMetric("tablesDenormalized")
        self.__getTables(database,metric,metricAzureMonitor["limitValue"])
        metric.tablesDenormalizedPoints = Utils.getMetricPointsAzureMonitor(metric.tablesDenormalized,metricAzureMonitor["ranges"]) 

        metricAzureMonitor = self.__getMetric("topConsumptionQueries")
        metric.topConsumptionQueries = self.__getTopConsumptionQueries(database,metricAzureMonitor["limitValue"])
        metric.topConsumptionQueriesPoints = Utils.getMetricPointsAzureMonitor(metric.topConsumptionQueries,metricAzureMonitor["ranges"]) 

        metricAzureMonitor = self.__getMetric("advisorsRecommended")
        metric.advisorsRecommended = self.__getAdvisorsRecommended(database)
        metric.advisorsRecommendedPoints = Utils.getMetricPointsAzureMonitor(metric.advisorsRecommended,metricAzureMonitor["ranges"]) 

        azureMonitor:pd.DataFrame = self.__azureSqlRepository.getAzureMonitor(database)

        metricAzureMonitor = self.__getMetric("deadlock")
        metric.deadlock = self.__getDeadlocks(azureMonitor)
        metric.deadlockPoints = Utils.getMetricPointsAzureMonitor(metric.deadlock,metricAzureMonitor["ranges"]) 

        metricAzureMonitor = self.__getMetric("connection_failed")
        metric.connectionFailed = self.__getConnectionFailed(azureMonitor)
        metric.connectionFailedPoints = Utils.getMetricPointsAzureMonitor(metric.deadlock,metricAzureMonitor["ranges"]) 

        return metric

    def __getTables(self,database:AzureSql,metric:AzureSqlMetric,limitColumns:int):
        columns:pd.DataFrame = self.__azureSqlRepository.getColumnsTableByDatabase(database)

        tables = columns.groupby(['table']).size().reset_index(name='count')

        metric.tablesQuantity = len(tables.index)

        tablesDenormalized = tables[(tables['count'] > limitColumns)]

        metric.tablesDenormalized = len(tablesDenormalized.index)
    
    def __getTopConsumptionQueries(self,database:AzureSql,maxCpuPercentage:Decimal)->Decimal:
        topQueries:pd.DataFrame = self.__azureSqlRepository.getTopQuerysByDatabase(database)

        if(len(topQueries.index)==0): return 0

        topQueries = topQueries[(topQueries['valueCpu'] > maxCpuPercentage)]

        value = len(topQueries.index)

        return value    
    
    def __getAdvisorsRecommended(self,database:AzureSql)->Decimal:
        advisors:pd.DataFrame = self.__azureSqlRepository.getAdvisorsRecommended(database)

        if(len(advisors.index)==0): return 0

        advisors = advisors[(advisors['state'].isin(Constants.AZURE_MONITOR_AZURE_SQL_ADVISORS_RECOMMENDED_STATES))]

        value:Decimal = advisors["score"].sum()

        return value    
    
    def __getDeadlocks(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitor = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_SQL_METRIC_DEADLOCK]))]

        value:Decimal = azureMonitor["value"].sum()

        return value  

    def __getConnectionFailed(self,azureMonitor:pd.DataFrame)->Decimal:
        azureMonitorSuccess = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_SQL_METRIC_CONNECTION_SUCCESSFUL]))]

        successful:Decimal = azureMonitorSuccess["value"].sum()

        azureMonitorFailed = azureMonitor[(azureMonitor['metric'].isin([Constants.AZURE_MONITOR_AZURE_SQL_METRIC_CONNECTION_FAILED]))]

        failed:Decimal = azureMonitorFailed["value"].sum()  

        value:Decimal = 0.00

        if(failed==value): return value

        value = (failed * 100) / successful

        return round(value,2)



