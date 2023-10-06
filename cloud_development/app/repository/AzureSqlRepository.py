import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants
from cloud_development.app.domain.AzureSql import AzureSql
class AzureSqlRepository():

    def __getSqlDatabasesByDirectoryResourceGroup(self,directory:str)->pd.DataFrame:
        file:str = Utils.getPathDirectory(directory)

        usecols:list[str]=["id","subscriptionId","resourceGroup","sqlServer",
                           "kind","name"]

        data:pd.DataFrame = pd.read_csv(file,usecols=usecols,encoding="utf-8")
        data = data.astype(object).where(pd.notnull(data),None)

        return data
    
    def getAllSqlDatabases(self)->list[AzureSql]:
        data = pd.DataFrame({})
        path:str = Constants.PATH_INPUT_AZURE_MONITOR
        files = Utils.getAllFilesSubDirectory(path,Constants.AZURE_MONITOR_FILE_AZURE_SQL)

        for file in files:
            data = pd.concat([data, self.__getSqlDatabasesByDirectoryResourceGroup(file)], ignore_index=True)        

        data = data.sort_values(["subscriptionId","resourceGroup","sqlServer","name"], ascending = [True, True,True,True])

        dataBases:list[AzureSql] = [AzureSql(**record) for record in data.to_dict(orient='records')]

        return dataBases