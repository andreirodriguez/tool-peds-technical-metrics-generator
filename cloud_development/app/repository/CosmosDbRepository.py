import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants
from cloud_development.app.domain.CosmosDb import CosmosDb
class CosmosDbRepository():

    def __getCosmosDatabasesByDirectoryResourceGroup(self,directory:str)->pd.DataFrame:
        file:str = Utils.getPathDirectory(directory)

        usecols:list[str]=["id","subscriptionId","resourceGroup","location","name","type","kind",
                           "state","documentEndpoint","enabledApiTypes","databaseAccountOfferType","minimalTlsVersion"]

        data:pd.DataFrame = pd.read_csv(file,usecols=usecols,encoding="utf-8")
        data = data.astype(object).where(pd.notnull(data),None)

        return data
    
    def getAllCosmosDatabases(self)->list[CosmosDb]:
        data = pd.DataFrame({})
        path:str = Constants.PATH_INPUT_AZURE_MONITOR
        files = Utils.getAllFilesSubDirectory(path,Constants.AZURE_MONITOR_FILE_COSMOS_DB)

        for file in files:
            data = pd.concat([data, self.__getCosmosDatabasesByDirectoryResourceGroup(file)], ignore_index=True)

        data = data.sort_values(["subscriptionId","resourceGroup","name"], ascending = [True, True,True])

        dataBases:list[CosmosDb] = [CosmosDb(**record) for record in data.to_dict(orient='records')]

        return dataBases