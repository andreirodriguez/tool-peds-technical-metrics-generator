import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.repository.AzureSqlRepository import AzureSqlRepository

class AzureSqlService():
    
    __azureSqlRepository:AzureSqlRepository

    def __init__(self):
        self.__azureSqlRepository = AzureSqlRepository()

    def listAllSqlDatabases(self)->pd.DataFrame:
        return self.__azureSqlRepository.getAllSqlDatabases()