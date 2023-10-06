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
    
    def getColumnsTableByDatabase(self,tenantId:str,database:AzureSql)->list[AzureSql]:
        file:str = Constants.PATH_INPUT_METRIC_AZURE_SQL_TABLE_COLUMNS.format(tenantId=tenantId,subscriptionId=database.subscriptionId,resourceGroup=database.resourceGroup,sqlServer=database.sqlServer,sqlDatabase=database.name)
        file = Utils.getPathDirectory(file)

        usecols:list[str]=["id","subscriptionId","resourceGroup","sqlServer","sqlDatabase",
                           "table","name","type"]

        data:pd.DataFrame = pd.read_csv(file,usecols=usecols,encoding="utf-8")
        data = data.astype(object).where(pd.notnull(data),None)

        return data 
    
    def getTopQuerysByDatabase(self,tenantId:str,database:AzureSql)->list[AzureSql]:
        file:str = Constants.PATH_INPUT_METRIC_AZURE_SQL_TOP_QUERIES.format(tenantId=tenantId,subscriptionId=database.subscriptionId,resourceGroup=database.resourceGroup,sqlServer=database.sqlServer,sqlDatabase=database.name)
        file = Utils.getPathDirectory(file)

        usecols:list[str]=["id","subscriptionId","resourceGroup","sqlServer","sqlDatabase",
                           "executionCount","intervalStartTime",
                           "unitCpu","valueCpu","unitMemory","valueMemory"]

        data:pd.DataFrame = pd.read_csv(file,usecols=usecols,encoding="utf-8")
        data = data.astype(object).where(pd.notnull(data),None)

        return data     
    
    def getAdvisorsRecommended(self,tenantId:str,database:AzureSql)->list[AzureSql]:
        file:str = Constants.PATH_INPUT_METRIC_AZURE_SQL_ADVISOR_RECOMMENDEDS.format(tenantId=tenantId,subscriptionId=database.subscriptionId,resourceGroup=database.resourceGroup,sqlServer=database.sqlServer,sqlDatabase=database.name)
        file = Utils.getPathDirectory(file)

        usecols:list[str]=["id","subscriptionId","resourceGroup","sqlServer","sqlDatabase",
                           "advisor","name","reason",
                           "state","score"]

        data:pd.DataFrame = pd.read_csv(file,usecols=usecols,encoding="utf-8")
        data = data.astype(object).where(pd.notnull(data),None)

        return data
    
    def getAzureMonitor(self,tenantId:str,database:AzureSql)->list[AzureSql]:
        file:str = Constants.PATH_INPUT_METRIC_AZURE_SQL_MONITOR_METRICS.format(tenantId=tenantId,subscriptionId=database.subscriptionId,resourceGroup=database.resourceGroup,sqlServer=database.sqlServer,sqlDatabase=database.name)
        file = Utils.getPathDirectory(file)

        usecols:list[str]=["metric","subscriptionId","resourceGroup","resourceName",
                           "aggregation","interval","unit","intervalTimeStamp","value"]

        data:pd.DataFrame = pd.read_csv(file,usecols=usecols,encoding="utf-8")
        data = data.astype(object).where(pd.notnull(data),None)

        return data    