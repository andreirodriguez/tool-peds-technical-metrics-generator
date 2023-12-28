from dataclasses import dataclass
from decimal import Decimal
from cloud_development.app.domain.CosmosDb import CosmosDb
from cloud_development.app.common.Utils import Utils

@dataclass
class CosmosDbMetric:
    id:str
    subscriptionId:str
    resourceGroup: str
    app:str
    name: str

    provisionedMinThroughput:Decimal
    autoscaleMaxThroughput:Decimal
    provisionedMaxThroughput:Decimal
    azureCosts:Decimal

    averageHalfRequestUnits:Decimal
    maximumRequestUnits:Decimal
    averageSpikesRequestUnits:Decimal
    totalRequestUnits:Decimal

    percentageRusConsumption:Decimal
    maximumRusConsumption:int
    maximumRusConsumptionPoints:Decimal

    def __init__(self,cosmosDb:CosmosDb):
        self.id = cosmosDb.id
        self.subscriptionId = cosmosDb.subscriptionId
        self.resourceGroup = cosmosDb.resourceGroup
        self.app = Utils.getAppCodeByResourceGroupName(cosmosDb.resourceGroup)
        self.name = cosmosDb.name    

