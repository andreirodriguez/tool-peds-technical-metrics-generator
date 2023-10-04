import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from concurrent.futures import ThreadPoolExecutor

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants

from cloud_development.app.service.BaseActivosService import BaseActivosService
from cloud_development.app.service.AssesmentService import AssesmentService
from cloud_development.app.service.SonarService import SonarService

class RunProcess():
    __period:str
    __baseActivosService:BaseActivosService
    __assesmentService:AssesmentService
    __sonarService:SonarService

    def __init__(self,period:str):
        self.__period = period

        Utils.logInfo(f"INICIALIZO la ejecución del proceso modelo de métrica cloud development con el periodo {self.__period}")

        self.__baseActivosService = BaseActivosService()

        metricAssesmentRanges:any = Utils.getConfigurationFileJson("metricAssesmentRanges")
        self.__assesmentService = AssesmentService(metricAssesmentRanges)


        metricSonarCodeSmells:any = Utils.getConfigurationFileJson("metricSonarCodeSmells")
        self.__sonarService = SonarService(metricSonarCodeSmells)

    def run(self):
        #baseActivos:pd.DataFrame = self.__baseActivosService.listBaseByPeriod(self.__period)

        #assesmentAzureSql:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_AZURE_SQL,Constants.ASSESMENT_METRICS_AZURE_SQL,baseActivos)

        #assesmentCacheRedis:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_CACHE_REDIS,Constants.ASSESMENT_METRICS_CACHE_REDIS,baseActivos)

        #assesmentCosmosDb:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.PATH_INPUT_ASSESMENT_COSMOS_DB,Constants.ASSESMENT_METRICS_COSMOS_DB,baseActivos)

        metricsSonar:pd.DataFrame = self.__sonarService.listMetricsSonar()

        metricsSonarAzureSql:pd.DataFrame = self.__sonarService.listMetricsSonarByServiceCloud(Constants.SERVICE_CLOUD_AZURE_SQL,metricsSonar)

        metricsSonarCacheRedis:pd.DataFrame = self.__sonarService.listMetricsSonarByServiceCloud(Constants.SERVICE_CLOUD_CACHE_REDIS,metricsSonar)

        Utils.exportDataFrameToXlsx("cloud_development\\resources\\output\\data.xlsx",metricsSonarCacheRedis)

        Utils.logInfo(f"FINALIZA la ejecución del proceso modelo de métrica cloud development con el periodo {self.__period}")
