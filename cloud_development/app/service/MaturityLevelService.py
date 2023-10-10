import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from decimal import Decimal
import math

from cloud_development.app.repository.SquadPrioritizedRepository import SquadPrioritizedRepository

import cloud_development.app.common.Constants as Constants
from cloud_development.app.common.Utils import Utils

from cloud_development.app.domain.AzureSqlMetric import AzureSqlMetric
from cloud_development.app.domain.RedisCacheMetric import RedisCacheMetric
from cloud_development.app.domain.CosmosDbMetric import CosmosDbMetric

class MaturityLevelService():

    __metricsModel:any  

    def __init__(self,metricsModel:any):
        self.__metricsModel = metricsModel

    def calculateMaturityLevelBySquad(self,serviceCloud:str,squads:pd.DataFrame)->pd.DataFrame:
        model:any = Utils.findObjectJson(self.__metricsModel,"serviceCloud",serviceCloud)

        self.__calculateMetricsSquads(model,squads)

        return squads
    
    def __calculateMetricsSquads(self,model:any,squads:pd.DataFrame):
        for category in model["categories"]:
            for metric in category["metrics"]:
                squads[metric["metric"]] = squads.apply(lambda record: self.__getMetricPoints(record,metric["variables"]),axis=1)

        for category in model["categories"]:
            squads[category["category"]] = squads.apply(lambda record: self.__getCategoryPoints(record,category["metrics"]),axis=1)


    def __getMetricPoints(self,squad:any,variables:any)->Decimal:
        if(not squad["hasAzure"]): return None

        metricPoints:Decimal = 0.00
        points:Decimal = 0.00
        for variable in variables: 
            points = squad[variable["variable"]]

            if(points==None): points = Constants.METRIC_SONAR_POINTS_MINIMUM

            metricPoints += points * (variable["percentage"] / 100)

        return round(metricPoints,2)
    
    def __getCategoryPoints(self,squad:any,metrics:any)->Decimal:
        if(not squad["hasAzure"]): return None

        categoryPoints:Decimal = 0.00
        points:Decimal = 0.00
        for metric in metrics: 
            points = squad[metric["metric"]]

            if(points==None): points = Constants.METRIC_SONAR_POINTS_MINIMUM

            categoryPoints += points * (metric["percentage"] / 100)

        return round(categoryPoints,2)

