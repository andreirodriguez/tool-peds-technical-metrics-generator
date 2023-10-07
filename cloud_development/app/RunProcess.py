import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import concurrent.futures

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants

from cloud_development.app.service.BaseActivosService import BaseActivosService
from cloud_development.app.service.AssesmentService import AssesmentService
from cloud_development.app.service.SonarService import SonarService

from cloud_development.app.service.AzureSqlService import AzureSqlService
from cloud_development.app.service.RedisCacheService import RedisCacheService
from cloud_development.app.service.CosmosDbService import CosmosDbService

from cloud_development.app.domain.AzureSql import AzureSql
from cloud_development.app.domain.AzureSqlMetric import AzureSqlMetric

from cloud_development.app.domain.RedisCache import RedisCache
from cloud_development.app.domain.RedisCacheMetric import RedisCacheMetric

from cloud_development.app.domain.CosmosDb import CosmosDb
from cloud_development.app.domain.CosmosDbMetric import CosmosDbMetric


class RunProcess():
    __period:str
    __environment:any
    __baseActivosService:BaseActivosService
    __assesmentService:AssesmentService
    __sonarService:SonarService
    __azureSqlService:AzureSqlService
    __redisCacheService:RedisCacheService
    __cosmosDbService:CosmosDbService

    def __init__(self,period:str):
        self.__period = period

        Utils.logInfo(f"INICIALIZO la ejecución del proceso modelo de métrica cloud development con el periodo {self.__period}")

        self.__environment = Utils.getConfigurationFileJson("environment")
        self.__baseActivosService = BaseActivosService()

        metricAssesmentRanges:any = Utils.getConfigurationFileJson("metricAssesmentRanges")
        self.__assesmentService = AssesmentService(metricAssesmentRanges)

        metricSonarCodeSmells:any = Utils.getConfigurationFileJson("metricSonarCodeSmells")
        self.__sonarService = SonarService(metricSonarCodeSmells)

        metricAzureMonitorSql:any = Utils.getConfigurationFileJson("metricAzureMonitorSql")
        self.__azureSqlService = AzureSqlService(metricAzureMonitorSql)

        metricAzureMonitorRedis:any = Utils.getConfigurationFileJson("metricAzureMonitorRedis")
        self.__redisCacheService = RedisCacheService(metricAzureMonitorRedis)

        metricAzureMonitorCosmos:any = Utils.getConfigurationFileJson("metricAzureMonitorCosmos")
        self.__cosmosDbService = CosmosDbService(metricAzureMonitorCosmos)

    def run(self):
        Utils.logInfo(f"Leo la base de datos de activos con el periodo {self.__period}")

        baseActivos:pd.DataFrame = self.__baseActivosService.listBaseByPeriod(self.__period)

        Utils.logInfo(f"Cálculo las variables de los assesments del periodo {self.__period}")

        assesmentAzureSql:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_AZURE_SQL,Constants.ASSESMENT_METRICS_AZURE_SQL,baseActivos)

        assesmentCacheRedis:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_CACHE_REDIS,Constants.ASSESMENT_METRICS_CACHE_REDIS,baseActivos)

        assesmentCosmosDb:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_COSMOS_DB,Constants.ASSESMENT_METRICS_COSMOS_DB,baseActivos)

        Utils.logInfo(f"Leo las metricas de sonar con el periodo {self.__period}")

        metricsSonar:pd.DataFrame = self.__sonarService.listMetricsSonar()

        Utils.logInfo(f"Cálculo las variables de sonar de una totalidad de {str(len(metricsSonar.index))} métricas del periodo {self.__period}")

        metricsSonarAzureSql:pd.DataFrame = self.__sonarService.listMetricsSonarByServiceCloud(Constants.SERVICE_CLOUD_AZURE_SQL,metricsSonar)

        metricsSonarCacheRedis:pd.DataFrame = self.__sonarService.listMetricsSonarByServiceCloud(Constants.SERVICE_CLOUD_CACHE_REDIS,metricsSonar)

        Utils.logInfo(f"Cálculo las variables de azure monitor del periodo {self.__period}")

        sqlDatabases = self.__azureSqlService.listAllSqlDatabases()

        metricsSql = self.__extractMetricsAzureSql(sqlDatabases)

        redisDatabases = self.__redisCacheService.listAllRedisDatabases()

        metricsRedis = self.__extractMetricsRedisCache(redisDatabases)

        cosmosDatabases = self.__cosmosDbService.listAllCosmosDatabases()

        metricsCosmos = self.__extractMetricsCosmosDb(cosmosDatabases)

        Utils.logInfo(f"FINALIZA la ejecución del proceso modelo de métrica cloud development con el periodo {self.__period}")

    def __extractMetricsAzureSql(self,databases:list[AzureSql]):
        Utils.logInfo(f"Inicio a calcular información de las métricas de {str(len(databases))} base de datos Azure SQL")

        metrics:list[AzureSqlMetric] = []
        threads:int = self.__environment["threads"][Constants.SERVICE_CLOUD_AZURE_SQL]

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            metrics += executor.map(self.__extractMetricsAzureSqlByDatabase, databases)

        Utils.logInfo(f"Fin a calcular información de las métricas de {str(len(databases))} base de datos Azure Sql")

        return metrics


    def __extractMetricsAzureSqlByDatabase(self,database:AzureSql)->AzureSqlMetric:
        Utils.logInfo(f"Cálculo métricas del recurso Azure Sql: {database.id}")

        try:
            metric:AzureSqlMetric = self.__azureSqlService.calculateMetrics(self.__environment["tenantId"],database)

            return metric
        except Exception as ex:
            Utils.logError(f"Error en el cálculo de metricas del recurso Azure Sql {database.id}",ex)

            return None    
        
    def __extractMetricsRedisCache(self,databases:list[RedisCache]):
        Utils.logInfo(f"Inicio a calcular información de las métricas de {str(len(databases))} base de datos Redis Cache")

        metrics:list[RedisCacheMetric] = []
        threads:int = self.__environment["threads"][Constants.SERVICE_CLOUD_CACHE_REDIS]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            metrics += executor.map(self.__extractMetricsRedisCacheByDatabase, databases)

        Utils.logInfo(f"Fin a calcular información de las métricas de {str(len(databases))} base de datos Redis Cache")

        return metrics


    def __extractMetricsRedisCacheByDatabase(self,database:RedisCache)->RedisCacheMetric:
        Utils.logInfo(f"Cálculo métricas del recurso Redis Cache: {database.id}")

        try:
            metric:RedisCacheMetric = self.__redisCacheService.calculateMetrics(self.__environment["tenantId"],database)

            return metric
        except Exception as ex:
            Utils.logError(f"Error en el cálculo de metricas del recurso Redis Cache {database.id}",ex)

            return None

    def __extractMetricsCosmosDb(self,databases:list[CosmosDb]):
        Utils.logInfo(f"Inicio a calcular información de las métricas de {str(len(databases))} base de datos Cosmos Db")

        metrics:list[CosmosDbMetric] = []
        threads:int = self.__environment["threads"][Constants.SERVICE_CLOUD_COSMOS_DB]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            metrics += executor.map(self.__extractMetricsCosmosDbByDatabase, databases)

        Utils.logInfo(f"Fin a calcular información de las métricas de {str(len(databases))} base de datos Cosmos Db")

        return metrics


    def __extractMetricsCosmosDbByDatabase(self,database:CosmosDb)->CosmosDbMetric:
        Utils.logInfo(f"Cálculo métricas del recurso Cosmos Db: {database.id}")

        try:
            metric:CosmosDbMetric = self.__cosmosDbService.calculateMetrics(self.__environment["tenantId"],database)

            return metric
        except Exception as ex:
            Utils.logError(f"Error en el cálculo de metricas del recurso Cosmos Db {database.id}",ex)

            return None           