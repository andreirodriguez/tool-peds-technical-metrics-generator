import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from concurrent.futures import ThreadPoolExecutor

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants

from cloud_development.app.service.BaseActivosService import BaseActivosService
from cloud_development.app.service.AssesmentService import AssesmentService
from cloud_development.app.service.SonarService import SonarService

from cloud_development.app.service.AzureSqlService import AzureSqlService
from cloud_development.app.service.RedisCacheService import RedisCacheService
from cloud_development.app.service.CosmosDbService import CosmosDbService


class RunProcess():
    __period:str
    __baseActivosService:BaseActivosService
    __assesmentService:AssesmentService
    __sonarService:SonarService
    __azureSqlService:AzureSqlService
    __redisCacheService:RedisCacheService
    __cosmosDbService:CosmosDbService

    def __init__(self,period:str):
        self.__period = period

        Utils.logInfo(f"INICIALIZO la ejecución del proceso modelo de métrica cloud development con el periodo {self.__period}")

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
        
        #baseActivos:pd.DataFrame = self.__baseActivosService.listBaseByPeriod(self.__period)

        #assesmentAzureSql:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_AZURE_SQL,Constants.ASSESMENT_METRICS_AZURE_SQL,baseActivos)

        #assesmentCacheRedis:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_CACHE_REDIS,Constants.ASSESMENT_METRICS_CACHE_REDIS,baseActivos)

        #assesmentCosmosDb:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_COSMOS_DB,Constants.ASSESMENT_METRICS_COSMOS_DB,baseActivos)

        #metricsSonar:pd.DataFrame = self.__sonarService.listMetricsSonar()

        #metricsSonarAzureSql:pd.DataFrame = self.__sonarService.listMetricsSonarByServiceCloud(Constants.SERVICE_CLOUD_AZURE_SQL,metricsSonar)

        #metricsSonarCacheRedis:pd.DataFrame = self.__sonarService.listMetricsSonarByServiceCloud(Constants.SERVICE_CLOUD_CACHE_REDIS,metricsSonar)

        #Utils.exportDataFrameToXlsx("cloud_development\\resources\\output\\metricsSonarCacheRedis.xlsx",metricsSonarCacheRedis)

        sqlDatabases = self.__azureSqlService.listAllSqlDatabases()

        self.__azureSqlService.calculateMetrics(sqlDatabases[0])

        redisDatabases = self.__redisCacheService.listAllRedisDatabases()

        self.__redisCacheService.calculateMetrics(redisDatabases[0])

        cosmosDatabases = self.__cosmosDbService.listAllCosmosDatabases()

        self.__cosmosDbService.calculateMetrics(cosmosDatabases[0])

        Utils.logInfo(f"FINALIZA la ejecución del proceso modelo de métrica cloud development con el periodo {self.__period}")
