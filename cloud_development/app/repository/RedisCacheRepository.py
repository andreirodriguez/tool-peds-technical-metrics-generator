import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants
from cloud_development.app.domain.RedisCache import RedisCache
class RedisCacheRepository():
    
    def getAllRedisDatabases(self)->list[RedisCache]:
        data = Utils.getAllResourcesAzureType(Constants.PATH_INPUT_AZURE_MONITOR,Constants.AZURE_MONITOR_FILE_REDIS_CACHE,Constants.AZURE_MONITOR_AZURE_REDIS_COLUMNS)

        data = data.sort_values(["subscriptionId","resourceGroup","name","processDate"], ascending = [True, True,True,False])
        data = data.drop_duplicates(['subscriptionId','resourceGroup','name'],keep='first')

        data = data[Constants.AZURE_MONITOR_AZURE_REDIS_COLUMNS].copy()
        dataBases:list[RedisCache] = [RedisCache(**record) for record in data.to_dict(orient='records')]

        return dataBases
    
    def getAzureMonitor(self,database:RedisCache)->pd.DataFrame:
        file:str = Constants.PATH_INPUT_METRIC_REDIS_CACHE_MONITOR_METRICS.format(tenantId=Constants.PARAMETER_INPUT_AZURE_TENANTID,subscriptionId=database.subscriptionId,resourceGroup=database.resourceGroup,redisCache=database.name)

        usecols:list[str]=["metric","subscriptionId","resourceGroup","resourceName",
                           "aggregation","interval","unit","intervalTimeStamp","value"]

        data = Utils.getDataAzureMonitor(file,usecols)

        return data        