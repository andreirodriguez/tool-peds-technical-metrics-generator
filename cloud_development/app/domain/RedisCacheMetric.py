from dataclasses import dataclass
from decimal import Decimal
from cloud_development.app.domain.RedisCache import RedisCache
from cloud_development.app.common.Utils import Utils

@dataclass
class RedisCacheMetric:
    id:str
    subscriptionId:str
    resourceGroup: str
    app:str
    name: str

    cacheMissRate:int
    cacheMissRatePoints:Decimal

    maximumMemoryConsumption:int
    maximumMemoryConsumptionPoints:Decimal

    maximumProcessorConsumption:int
    maximumProcessorConsumptionPoints:Decimal

    def __init__(self,redisCache:RedisCache):
        self.id = redisCache.id
        self.subscriptionId = redisCache.subscriptionId
        self.resourceGroup = redisCache.resourceGroup
        self.app = Utils.getAppCodeByResourceGroupName(redisCache.resourceGroup)
        self.name = redisCache.name    

