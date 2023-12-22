import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants
from cloud_development.app.domain.CosmosDb import CosmosDb
class CosmosDbRepository():
    
    def getAllCosmosDatabases(self)->list[CosmosDb]:
        data = Utils.getAllResourcesAzureType(Constants.PATH_INPUT_AZURE_MONITOR,Constants.AZURE_MONITOR_FILE_COSMOS_DB,Constants.AZURE_MONITOR_AZURE_COSMOS_COLUMNS)

        data = data.sort_values(["subscriptionId","resourceGroup","name","processDate"], ascending = [True, True,True,False])
        data = data.drop_duplicates(['subscriptionId','resourceGroup','name'],keep='first')

        data = data[Constants.AZURE_MONITOR_AZURE_COSMOS_COLUMNS].copy()
        dataBases:list[CosmosDb] = [CosmosDb(**record) for record in data.to_dict(orient='records')]

        return dataBases
    
    def getSummaryCosmosDatabases(self)->pd.DataFrame:
        data = Utils.getAllResourcesAzureType(Constants.PATH_INPUT_AZURE_MONITOR,Constants.AZURE_MONITOR_FILE_SUMMARY_COSMOS_DB,Constants.AZURE_MONITOR_AZURE_COSMOS_COLUMNS)

        data = data[Constants.AZURE_MONITOR_AZURE_COSMOS_COLUMNS].copy()

        data["app"] = data.apply(lambda record: Utils.getAppCodeByResourceGroupName(record["resourceGroup"]),axis=1)

        return data    
    
    def getAzureMonitor(self,database:CosmosDb)->pd.DataFrame:
        file:str = Constants.PATH_INPUT_METRIC_COSMOS_DB_MONITOR_METRICS.format(tenantId=Constants.PARAMETER_INPUT_AZURE_TENANTID,subscriptionId=database.subscriptionId,resourceGroup=database.resourceGroup,cosmosDb=database.name)

        usecols:list[str]=["metric","subscriptionId","resourceGroup","resourceName",
                           "aggregation","interval","unit","intervalTimeStamp","value"]

        data = Utils.getDataAzureMonitor(file,usecols)

        return data        