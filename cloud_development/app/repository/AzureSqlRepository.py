import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants
from cloud_development.app.domain.AzureSql import AzureSql
class AzureSqlRepository():
    
    def getAllSqlDatabases(self)->list[AzureSql]:
        data = Utils.getAllResourcesAzureType(Constants.PATH_INPUT_AZURE_MONITOR,Constants.AZURE_MONITOR_FILE_AZURE_SQL,Constants.AZURE_MONITOR_AZURE_SQL_COLUMNS)

        data = data.sort_values(["subscriptionId","resourceGroup","sqlServer","name","processDate"], ascending = [True, True,True,True,False])
        data = data.drop_duplicates(['subscriptionId','resourceGroup','sqlServer','name'],keep='first')

        data = data[Constants.AZURE_MONITOR_AZURE_SQL_COLUMNS].copy()
        dataBases:list[AzureSql] = [AzureSql(**record) for record in data.to_dict(orient='records')]

        return dataBases
    
    def getColumnsTableByDatabase(self,database:AzureSql)->pd.DataFrame:
        file:str = Constants.PATH_INPUT_METRIC_AZURE_SQL_TABLE_COLUMNS.format(tenantId=Constants.PARAMETER_INPUT_AZURE_TENANTID,subscriptionId=database.subscriptionId,resourceGroup=database.resourceGroup,sqlServer=database.sqlServer,sqlDatabase=database.name)

        usecols:list[str]=["id","subscriptionId","resourceGroup","sqlServer","sqlDatabase",
                           "table","name","type"]

        data = Utils.getDataAzureMonitor(file,usecols)

        return data
    
    def getTopQuerysByDatabase(self,database:AzureSql)->pd.DataFrame:
        file:str = Constants.PATH_INPUT_METRIC_AZURE_SQL_TOP_QUERIES.format(tenantId=Constants.PARAMETER_INPUT_AZURE_TENANTID,subscriptionId=database.subscriptionId,resourceGroup=database.resourceGroup,sqlServer=database.sqlServer,sqlDatabase=database.name)

        usecols:list[str]=["id","subscriptionId","resourceGroup","sqlServer","sqlDatabase",
                           "executionCount","intervalStartTime",
                           "unitCpu","valueCpu","unitMemory","valueMemory"]

        data = Utils.getDataAzureMonitor(file,usecols)

        return data     
    
    def getAdvisorsRecommended(self,database:AzureSql)->pd.DataFrame:
        file:str = Constants.PATH_INPUT_METRIC_AZURE_SQL_ADVISOR_RECOMMENDEDS.format(tenantId=Constants.PARAMETER_INPUT_AZURE_TENANTID,subscriptionId=database.subscriptionId,resourceGroup=database.resourceGroup,sqlServer=database.sqlServer,sqlDatabase=database.name)

        usecols:list[str]=["id","subscriptionId","resourceGroup","sqlServer","sqlDatabase",
                           "advisor","name","reason",
                           "state","score"]

        data = Utils.getDataAzureMonitor(file,usecols)

        return data
    
    def getAzureMonitor(self,database:AzureSql)->pd.DataFrame:
        file:str = Constants.PATH_INPUT_METRIC_AZURE_SQL_MONITOR_METRICS.format(tenantId=Constants.PARAMETER_INPUT_AZURE_TENANTID,subscriptionId=database.subscriptionId,resourceGroup=database.resourceGroup,sqlServer=database.sqlServer,sqlDatabase=database.name)

        usecols:list[str]=["metric","subscriptionId","resourceGroup","resourceName",
                           "aggregation","interval","unit","intervalTimeStamp","value"]

        data = Utils.getDataAzureMonitor(file,usecols)

        return data    