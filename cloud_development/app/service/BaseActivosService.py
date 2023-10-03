import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.repository.BaseActivosRepository import BaseActivosRepository

class BaseActivosService():
    
    __baseActivosRepository:BaseActivosRepository

    def __init__(self):
        self.__baseActivosRepository = BaseActivosRepository()

    def listBaseByPeriod(self,period:str)->pd.DataFrame:
        return self.__baseActivosRepository.getBaseByPeriod(period)