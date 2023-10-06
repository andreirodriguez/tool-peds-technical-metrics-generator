from dataclasses import dataclass
from decimal import Decimal
from cloud_development.app.domain.CosmosDb import CosmosDb
from cloud_development.app.common.Utils import Utils

@dataclass
class AzureSqlMetric:
    id:str
    subscriptionId:str
    resourceGroup: str
    app:str
    name: str

    tablesDenormalized:int
    tablesDenormalizedPoints:Decimal

    topConsumptionQueries:int
    topConsumptionQueriesPoints:Decimal    

    advisorsRecommended:int
    advisorsRecommendedPoints:Decimal

    deadlock:int
    deadlockPoints:Decimal      

    connectionFailed :Decimal
    connectionFailedPoints :Decimal

    def __init__(self,cosmosDb:CosmosDb):
        self.id = cosmosDb.id
        self.subscriptionId = cosmosDb.subscriptionId
        self.resourceGroup = cosmosDb.resourceGroup
        self.app = Utils.getAppCodeByResourceGroupName(cosmosDb.resourceGroup)
        self.name = cosmosDb.name    

