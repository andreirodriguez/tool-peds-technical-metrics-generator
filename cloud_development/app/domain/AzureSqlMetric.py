from dataclasses import dataclass
from decimal import Decimal
from cloud_development.app.domain.AzureSql import AzureSql
from cloud_development.app.common.Utils import Utils
@dataclass
class AzureSqlMetric:
    id:str
    subscriptionId:str
    resourceGroup: str
    app:str
    sqlServer: str
    name: str

    tablesDenormalized:int
    tablesDenormalizedPoints:Decimal

    def __init__(self,azureSql:AzureSql):
        self.id = azureSql.id
        self.subscriptionId = azureSql.subscriptionId
        self.resourceGroup = azureSql.resourceGroup
        self.app = Utils.getAppCodeByResourceGroupName(azureSql.resourceGroup)
        self.sqlServer = azureSql.sqlServer
        self.name = azureSql.name    

