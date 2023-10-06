import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.repository.RedisCacheRepository import RedisCacheRepository

class RedisCacheService():
    
    __redisCacheRepository:RedisCacheRepository

    def __init__(self):
        self.__redisCacheRepository = RedisCacheRepository()

    def listAllRedisDatabases(self)->pd.DataFrame:
        return self.__redisCacheRepository.getAllRedisDatabases()