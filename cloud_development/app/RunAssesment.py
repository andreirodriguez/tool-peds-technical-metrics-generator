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

from cloud_development.app.service.MetricModelAppService import MetricModelAppService
from cloud_development.app.service.MaturityLevelService import MaturityLevelService
from cloud_development.app.service.MetricModelSquadService import MetricModelSquadService


from cloud_development.app.domain.AzureSql import AzureSql
from cloud_development.app.domain.AzureSqlMetric import AzureSqlMetric

from cloud_development.app.domain.RedisCache import RedisCache
from cloud_development.app.domain.RedisCacheMetric import RedisCacheMetric

from cloud_development.app.domain.CosmosDb import CosmosDb
from cloud_development.app.domain.CosmosDbMetric import CosmosDbMetric


class RunAssesment():
    __period:str
    __baseActivosService:BaseActivosService
    __assesmentService:AssesmentService
    __maturityLevelService:MaturityLevelService
    __metricModelSquadService:MetricModelSquadService

    def __init__(self,period:str):
        self.__period = period

        Utils.logInfo(f"INICIALIZO la ejecución del proceso modelo de métrica cloud development con el periodo {self.__period}")

        self.__baseActivosService = BaseActivosService()

        metricAssesmentRanges:any = Utils.getConfigurationFileJson("metricAssesmentRanges")
        self.__assesmentService = AssesmentService(metricAssesmentRanges)

        metricMaturityLevel:any = Utils.getConfigurationFileJson("metricMaturityLevel")
        self.__maturityLevelService = MaturityLevelService(metricMaturityLevel)
        self.__metricModelSquadService = MetricModelSquadService(self.__maturityLevelService)

    def run(self):
        Utils.logInfo(f"Leo la base de datos de activos con el periodo {self.__period}")

        baseActivos:pd.DataFrame = self.__baseActivosService.listBaseByPeriod(self.__period)

        Utils.logInfo(f"Cálculo las variables de los assesments del periodo {self.__period}")

        assesmentAzureSql:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_AZURE_SQL,Constants.ASSESMENT_METRICS_AZURE_SQL,baseActivos)

        assesmentCacheRedis:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_CACHE_REDIS,Constants.ASSESMENT_METRICS_CACHE_REDIS,baseActivos)

        assesmentCosmosDb:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_COSMOS_DB,Constants.ASSESMENT_METRICS_COSMOS_DB,baseActivos)

        Utils.logInfo(f"Cálculo el modelo de la métricas por squad y servicio cloud del periodo {self.__period}")

        metricsSquadSql = self.__metricModelSquadService.calculateMetricAssesmentAzureSqlBySquad(assesmentAzureSql,baseActivos)

        metricsSquadRedis = self.__metricModelSquadService.calculateMetricAssesmentRedisCacheBySquad(assesmentCacheRedis,baseActivos)

        metricsSquadCosmos = self.__metricModelSquadService.calculateMetricAssesmentCosmosDbBySquad(assesmentCosmosDb,baseActivos)

        Utils.logInfo(f"Cálculo el nivel de madurez de los squads priorizados del periodo {self.__period}")

        squads = self.__metricModelSquadService.calculateMaturityLevel(metricsSquadSql,metricsSquadRedis,metricsSquadCosmos)

        self.__maturityLevelService.exportExcelSummaryAssesment(self.__period,baseActivos,
                                                       squads,metricsSquadSql,metricsSquadRedis,metricsSquadCosmos,
                                                       assesmentAzureSql,assesmentCacheRedis,assesmentCosmosDb
                                                       )

        Utils.logInfo(f"FINALIZA la ejecución del proceso modelo de métrica cloud development con el periodo {self.__period}")