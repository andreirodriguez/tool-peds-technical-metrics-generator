import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.repository.CosmosDbRepository import CosmosDbRepository

class CosmosDbService():
    
    __cosmosDbRepository:CosmosDbRepository

    def __init__(self):
        self.__cosmosDbRepository = CosmosDbRepository()

    def listAllCosmosDatabases(self)->pd.DataFrame:
        return self.__cosmosDbRepository.getAllCosmosDatabases()