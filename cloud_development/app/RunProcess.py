import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from concurrent.futures import ThreadPoolExecutor

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants

from cloud_development.app.service.BaseActivosService import BaseActivosService
from cloud_development.app.service.AssesmentService import AssesmentService

class RunProcess():
    __period:str
    __baseActivosService:BaseActivosService
    __assesmentService:AssesmentService

    def __init__(self,period:str):
        Utils.logInfo(f"INICIALIZO la ejecución del proceso modelo de métrica cloud development con el periodo {period}")

        self.__period = period
        self.__baseActivosService = BaseActivosService()

        metricAssesmentRanges:any = Utils.getConfigurationFileJson("metricAssesmentRanges")
        self.__assesmentService = AssesmentService(metricAssesmentRanges)

    def run(self):
        baseActivos:pd.DataFrame = self.__baseActivosService.listBaseByPeriod(self.__period)

        assesmentAzureSql:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.ASSESMENT_PATH_AZURE_SQL,Constants.ASSESMENT_METRICS_AZURE_SQL,baseActivos)

        assesmentCacheRedis:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.ASSESMENT_PATH_CACHE_REDIS,Constants.ASSESMENT_METRICS_CACHE_REDIS,baseActivos)

        assesmentCosmosDb:pd.DataFrame = self.__assesmentService.listAssesmentByServiceCloud(Constants.ASSESMENT_PATH_COSMOS_DB,Constants.ASSESMENT_METRICS_COSMOS_DB,baseActivos)

        Utils.exportDataFrameToXlsx("cloud_development\\resources\\output\\data.xlsx",assesmentCosmosDb)
