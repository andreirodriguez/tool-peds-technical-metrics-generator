import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants

from cloud_development.app.service.MaturityLevelService import MaturityLevelService
from cloud_development.app.service.MetricModelSquadService import MetricModelSquadService

from cloud_development.app.service.BaseActivosService import BaseActivosService
from cloud_development.app.service.AzureSqlService import AzureSqlService
from cloud_development.app.service.RedisCacheService import RedisCacheService
from cloud_development.app.service.CosmosDbService import CosmosDbService

from cloud_development.app.domain.AzureSql import AzureSql
from cloud_development.app.domain.AzureSqlMetric import AzureSqlMetric

from cloud_development.app.domain.RedisCache import RedisCache
from cloud_development.app.domain.RedisCacheMetric import RedisCacheMetric

from cloud_development.app.domain.CosmosDb import CosmosDb
from cloud_development.app.domain.CosmosDbMetric import CosmosDbMetric


class RunScopePractice():
    __period:str
    __baseActivosService:BaseActivosService
    __azureSqlService:AzureSqlService
    __redisCacheService:RedisCacheService
    __cosmosDbService:CosmosDbService
    __maturityLevelService:MaturityLevelService
    __metricModelSquadService:MetricModelSquadService    

    def __init__(self,period:str):
        self.__period = period

        self.__baseActivosService = BaseActivosService()

        metricAzureMonitorSql:any = Utils.getConfigurationFileJson("metricAzureMonitorSql")
        self.__azureSqlService = AzureSqlService(metricAzureMonitorSql)

        metricAzureMonitorRedis:any = Utils.getConfigurationFileJson("metricAzureMonitorRedis")
        self.__redisCacheService = RedisCacheService(metricAzureMonitorRedis)

        metricAzureMonitorCosmos:any = Utils.getConfigurationFileJson("metricAzureMonitorCosmos")
        self.__cosmosDbService = CosmosDbService(metricAzureMonitorCosmos)

        metricMaturityLevel:any = Utils.getConfigurationFileJson("metricMaturityLevel")
        self.__maturityLevelService = MaturityLevelService(metricMaturityLevel)
        self.__metricModelSquadService = MetricModelSquadService(self.__maturityLevelService)        

    def run(self):
        Utils.logInfo(f"Leo la base de datos de activos con el periodo {self.__period}")

        baseActivos:pd.DataFrame = self.__baseActivosService.listBaseByPeriod(self.__period)

        Utils.logInfo(f"Obtengo la información de los recursos cloud de la practica")

        azureSqls:pd.DataFrame = self.__azureSqlService.listSummarySqlDatabases()

        cacheRedis:pd.DataFrame = self.__redisCacheService.listSummaryRedisDatabases()

        cosmosDbs:pd.DataFrame = self.__cosmosDbService.listSummaryCosmosDatabases()

        Utils.logInfo(f"Exporto el archivo de squads priorizados de la práctica")

        self.__metricModelSquadService.exportExcelSquadsPriorizados(baseActivos,azureSqls,cacheRedis,cosmosDbs)

        Utils.logInfo(f"FINALIZA la ejecución del proceso para obtener los squads del alcance de la practica con el periodo {self.__period}")