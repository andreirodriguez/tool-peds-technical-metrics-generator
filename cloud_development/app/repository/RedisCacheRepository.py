import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants
from cloud_development.app.domain.RedisCache import RedisCache
class RedisCacheRepository():

    def __getRedisDatabasesByDirectoryResourceGroup(self,directory:str)->pd.DataFrame:
        file:str = Utils.getPathDirectory(directory)

        usecols:list[str]=["id","subscriptionId","resourceGroup","location","name","type",
                           "state","version","hostName"]

        data:pd.DataFrame = pd.read_csv(file,usecols=usecols,encoding="utf-8")
        data = data.astype(object).where(pd.notnull(data),None)

        return data
    
    def getAllRedisDatabases(self)->list[RedisCache]:
        data = pd.DataFrame({})
        path:str = Constants.PATH_INPUT_AZURE_MONITOR
        files = Utils.getAllFilesSubDirectory(path,Constants.AZURE_MONITOR_FILE_REDIS_CACHE)

        for file in files:
            data = pd.concat([data, self.__getRedisDatabasesByDirectoryResourceGroup(file)], ignore_index=True)        

        data = data.sort_values(["subscriptionId","resourceGroup","name"], ascending = [True, True,True])

        dataBases:list[RedisCache] = [RedisCache(**record) for record in data.to_dict(orient='records')]

        return dataBases