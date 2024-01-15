import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import math

import cloud_development.app.common.Constants as Constants
from cloud_development.app.common.Utils import Utils

from cloud_development.app.service.SonarService import SonarService

from cloud_development.app.domain.AzureSqlMetric import AzureSqlMetric
from cloud_development.app.domain.RedisCacheMetric import RedisCacheMetric
from cloud_development.app.domain.CosmosDbMetric import CosmosDbMetric

class MetricModelAppService():
    __sonarService:SonarService  

    def __init__(self,sonarService:any):
        self.__sonarService = sonarService

    def calculateMetricAzureSqlByApp(self,metricsAzure:list[AzureSqlMetric],metricsSonar:pd.DataFrame)->pd.DataFrame:
        metrics:pd.DataFrame = self.__getMetricsAzureByApp(metricsAzure,Constants.AZURE_MONITOR_AZURE_SQL_METRICS)

        metrics = self.__getMetricsSonarByApp(metrics,metricsSonar,[Constants.METRIC_SONAR_CONNECTION_POOL])

        return metrics
    
    def calculateMetricAzureRedisByApp(self,metricsAzure:list[RedisCacheMetric],metricsSonar:pd.DataFrame)->pd.DataFrame:
        metrics:pd.DataFrame = self.__getMetricsAzureByApp(metricsAzure,Constants.AZURE_MONITOR_AZURE_REDIS_METRICS)

        metrics = self.__getMetricsSonarByApp(metrics,metricsSonar,[Constants.METRIC_SONAR_CONNECTION_POOL])

        return metrics    
    
    def calculateMetricAzureCosmosByApp(self,metricsAzure:list[CosmosDbMetric])->pd.DataFrame:
        metrics:pd.DataFrame = self.__getMetricsAzureByApp(metricsAzure,Constants.AZURE_MONITOR_AZURE_COSMOS_METRICS)

        return metrics        
    
    def __getMetricsAzureByApp(self,metricsAzureObjects:any,listMetrics:list[str])->pd.DataFrame:
        metricsAzure:pd.DataFrame = Utils.getDataFrameToDictionaryList(metricsAzureObjects)

        metrics:pd.DataFrame = metricsAzure[["app"]].copy()
        metrics = metrics.sort_values(['app'], ascending = [True])
        metrics = metrics.drop_duplicates(['app'],keep='first')        

        for metric in listMetrics:
            metrics[metric] = metrics.apply(lambda record: self.__getMetricAzureMeanByApp(record["app"],metric,metricsAzure),axis=1)

        return metrics

    def __getMetricsSonarByApp(self,metrics:pd.DataFrame,metricsSonarObjects:any,listMetrics:list[str])->pd.DataFrame:
        exclusions:pd.DataFrame = self.__sonarService.getSonarExclusions()

        for metric in listMetrics:
            metrics[metric] = metrics.apply(lambda record: self.__getMetricSonarMeanByApp(record["app"],metric,metricsSonarObjects,exclusions),axis=1)

        return metrics

    def __getMetricAzureMeanByApp(self,app:str,metric:str,metrics:pd.DataFrame)->float:
        metric = metric + "Points"

        metrics = metrics[(metrics['app']==app)]

        value = metrics[metric].mean()

        return round(value,2)

    def __getMetricSonarMeanByApp(self,app:str,metric:str,metrics:pd.DataFrame,exclusions:pd.DataFrame)->float:
        inclusionApp = len(exclusions[(exclusions['app']==app)].index)

        if(inclusionApp==0): return None

        metric = metric + "Points"

        metrics = metrics[(metrics['app']==app)]

        value = metrics[metric].mean() 

        if(math.isnan(value)): return Constants.METRIC_SONAR_POINTS_MAXIMUM

        return round(value,2)


        


