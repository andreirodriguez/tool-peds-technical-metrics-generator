import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from decimal import Decimal

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

    def listAllSqlDatabases(self)->pd.DataFrame:
        return self.__azureSqlRepository.getAllSqlDatabases()
    
    def calculateMetrics(self,tenantId:str,database:AzureSql)->AzureSqlMetric:
        metric:AzureSqlMetric = AzureSqlMetric(database)

        metricAzureMonitor:any

        metricAzureMonitor = self.__getMetric("tablesDenormalized")
        metric.tablesDenormalized = self.__getTablesDenormalized(tenantId,database,metricAzureMonitor["limitValue"])
        metric.tablesDenormalizedPoints = Utils.getMetricPointsAzureMonitor(metric.tablesDenormalized,metricAzureMonitor["ranges"]) 
        
        metricAzureMonitor = self.__getMetric("topConsumptionQueries")
        metric.topConsumptionQueries = self.__getTopConsumptionQueries(tenantId,database,metricAzureMonitor["limitValue"])
        metric.topConsumptionQueriesPoints = Utils.getMetricPointsAzureMonitor(metric.topConsumptionQueries,metricAzureMonitor["ranges"]) 

        metricAzureMonitor = self.__getMetric("advisorsRecommended")
        metric.advisorsRecommended = self.__getAdvisorsRecommended(tenantId,database)
        metric.advisorsRecommendedPoints = Utils.getMetricPointsAzureMonitor(metric.advisorsRecommended,metricAzureMonitor["ranges"]) 

        azureMonitor:pd.DataFrame = self.__azureSqlRepository.getAzureMonitor(tenantId,database)

        metricAzureMonitor = self.__getMetric("deadlock")
        metric.deadlock = self.__getDeadlocks(azureMonitor)
        metric.deadlockPoints = Utils.getMetricPointsAzureMonitor(metric.deadlock,metricAzureMonitor["ranges"]) 

        metricAzureMonitor = self.__getMetric("connection_failed")
        metric.connectionFailed = self.__getConnectionFailed(azureMonitor)
        metric.connectionFailedPoints = Utils.getMetricPointsAzureMonitor(metric.deadlock,metricAzureMonitor["ranges"]) 

        return metric
    
    def __getTablesDenormalized(self,tenantId:str,database:AzureSql,limitColumns:int)->Decimal:
        columns:pd.DataFrame = self.__azureSqlRepository.getColumnsTableByDatabase(tenantId,database)

        tables = columns.groupby(['table']).size().reset_index(name='count')

        tables = tables[(tables['count'] > limitColumns)]

        value = len(tables.index)

        return value
    
    def __getTopConsumptionQueries(self,tenantId:str,database:AzureSql,maxCpuPercentage:Decimal)->Decimal:
        topQueries:pd.DataFrame = self.__azureSqlRepository.getTopQuerysByDatabase(tenantId,database)

        topQueries = topQueries[(topQueries['valueCpu'] > maxCpuPercentage)]

        value = len(topQueries.index)

        return value    
    
    def __getAdvisorsRecommended(self,tenantId:str,database:AzureSql)->Decimal:
        advisors:pd.DataFrame = self.__azureSqlRepository.getAdvisorsRecommended(tenantId,database)

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



