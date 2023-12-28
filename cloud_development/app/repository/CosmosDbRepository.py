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
    
    @staticmethod
    def getAllResourcesAzureType(basePathAzure:str,fileResource:str,resourceColumns:list[str])->pd.DataFrame:
        data = pd.DataFrame({})
        files = Utils.getAllFilesSubDirectory(basePathAzure,fileResource)

        for file in files:
            data = pd.concat([data, Utils.getFileResourcesAzureType(file,resourceColumns)], ignore_index=True)        

        return data

    @staticmethod
    def getFileResourcesAzureType(directory:str,resourceColumns:list[str])->pd.DataFrame:
        file:str = Utils.getPathDirectory(directory)

        usecols:list[str]=resourceColumns.copy()
        usecols.append("processDate")

        data:pd.DataFrame = pd.read_csv(file,usecols=usecols,encoding="utf-8")
        data = data.astype(object).where(pd.notnull(data),None)

        data['processDate'] = data['processDate'].apply(lambda value: pd.to_datetime(value,format=Constants.FORMAT_DATETIME_PROCESS_AZURE_MONITOR).to_datetime64())

        return data       
    

    @staticmethod
    def getAzureCosts(period:str)->pd.DataFrame:
        data = pd.DataFrame({})
        path:str = Constants.PATH_INPUT_AZURE_COSTS_COSMOS_DB
        files = Utils.getFilesDirectory(path)

        for file in files:
            if (not file.endswith(".xlsx")): continue

            data = pd.concat([data, pd.read_excel(Utils.getPathDirectory(path + file),
                                                  usecols=["UsageDate","ResourceName","ResourceGroupName","CostUSD","SubscriptionName","Meter"],
                                                  sheet_name="Data")], ignore_index=True)        

        data = data.rename(columns= {"UsageDate": "usageDate", 
                    "ResourceName": "name",
                    "ResourceGroupName": "resourceGroup",
                    "CostUSD": "azureCost",
                    "SubscriptionName": "subscriptionName",
                    "Meter": "meter"
                    })

        data['usageDate'] = data['usageDate'].apply(lambda value: pd.to_datetime(value,format=Constants.FORMAT_DATETIME_AZURE_COST).to_datetime64())

        data['subscriptionId'] = data['subscriptionName'].apply(lambda value: Utils.getAzureSubscriptionId(value))

        data = data[(data['usageDate'].dt.strftime('%Y%m')==period)]

        return data