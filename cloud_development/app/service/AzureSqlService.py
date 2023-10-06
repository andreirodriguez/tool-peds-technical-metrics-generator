import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from decimal import Decimal

from cloud_development.app.repository.AzureSqlRepository import AzureSqlRepository
from cloud_development.app.domain.AzureSql import AzureSql
from cloud_development.app.domain.AzureSqlMetric import AzureSqlMetric

from cloud_development.app.common.Utils import Utils

class AzureSqlService():

    __metricsAzureMonitor:any    
    __azureSqlRepository:AzureSqlRepository


    def __init__(self,metricsAzureMonitor:any):
        self.__metricsAzureMonitor = metricsAzureMonitor
        self.__azureSqlRepository = AzureSqlRepository()

    def listAllSqlDatabases(self)->pd.DataFrame:
        return self.__azureSqlRepository.getAllSqlDatabases()
    
    def calculateMetrics(self,database:AzureSql)->AzureSqlMetric:
        metric:AzureSqlMetric = AzureSqlMetric(database)

        metricAzureMonitor:any

        metricAzureMonitor = self.__getMetric("tablesDenormalized")
        metric.tablesDenormalized = self.__getTablesDenormalized(database,metricAzureMonitor["limitValue"])
        metric.tablesDenormalizedPoints = Utils.getMetricPointsAzureMonitor(metric.tablesDenormalized,metricAzureMonitor["ranges"]) 
        
        return metric
    
    def __getTablesDenormalized(self,database:AzureSql,limitColumns:int)->Decimal:
        columns:pd.DataFrame = self.__azureSqlRepository.getColumnsTableByDatabase(self.__metricsAzureMonitor["tenantId"],database)

        tables = columns.groupby(['table']).size().reset_index(name='count')

        tables = tables[(tables['count'] > limitColumns)]

        value = len(tables.index)

        return value

    def __getMetric(self,nameMetric:str)->pd.DataFrame:
        metricAzure = [metric for metric in self.__metricsAzureMonitor["metrics"] if metric["metric"]==nameMetric][0]

        return metricAzure


