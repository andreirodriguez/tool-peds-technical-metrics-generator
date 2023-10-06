import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from decimal import Decimal

import cloud_development.app.common.Constants as Constants

from cloud_development.app.repository.SonarRepository import SonarRepository

class SonarService():
    
    __sonarRepository:SonarRepository
    __metricsSonar:any
    __metrics:pd.DataFrame = pd.DataFrame({"app": [],"repository":[],"serviceCloud":[],"metric":[],"value":[],"points":[]})

    def __init__(self,metricsSonar:any):
        self.__metricsSonar = metricsSonar

        self.__sonarRepository = SonarRepository()

    def __listSonarCodeSmells(self)->pd.DataFrame:
        return self.__sonarRepository.getSonarCodeSmells()
    
    def listMetricsSonarByServiceCloud(self,serviceCloud:str,metricsSonar:pd.DataFrame)->pd.DataFrame:
        metricsSonar = metricsSonar[(metricsSonar['serviceCloud']==serviceCloud)]

        metrics:pd.DataFrame = metricsSonar[["app","repository"]].copy()
        metrics = metrics.sort_values(['app','repository'], ascending = [True,True])
        metrics = metrics.drop_duplicates(['app','repository'],keep='first')        

        for metricSonar in self.__metricsSonar:
            if(not self.__metricApplyServiceCloud(serviceCloud,metricSonar)): continue

            metrics[metricSonar["metric"]] = metrics.apply(lambda record: self.__getPropertyMetricSonar(record["app"],record["repository"],metricsSonar,"value"),axis=1)
            metrics[metricSonar["metric"] + "Points"] = metrics.apply(lambda record: self.__getPropertyMetricSonar(record["app"],record["repository"],metricsSonar,"points"),axis=1)

        return metrics

    def __getPropertyMetricSonar(self,app:str,repo:str,metricsSonar:pd.DataFrame,property:str)->any:
        metricsSonar = metricsSonar[(metricsSonar['app']==app) & (metricsSonar['repository']==repo)]

        if(len(metricsSonar.index) == 0): return None

        return metricsSonar.iloc[0][property]

    def listMetricsSonar(self)->pd.DataFrame:
        codeSmellsSonar:pd.DataFrame = self.__listSonarCodeSmells()

        metrics = self.__metrics.copy()

        metrics = pd.concat([metrics, self.__listMetricsConnectionPool(codeSmellsSonar)], ignore_index=True)

        return metrics

    def __getMetric(self,nameMetric:str)->pd.DataFrame:
        metricSonar = [metric for metric in self.__metricsSonar if metric["metric"]==nameMetric][0]

        return metricSonar
    
    def __metricApplyServiceCloud(self,serviceCloud:str,metricSonar:any)->bool:
        count = len([metric for metric in metricSonar["services"] if metric["service"]==serviceCloud])

        return (count>0)

    def __listMetricsConnectionPool(self,codeSmellsSonar:pd.DataFrame)->pd.DataFrame:
        configuration = self.__getMetric(Constants.METRIC_SONAR_CONNECTION_POOL)

        codeSmellTypes:list[str] = []
        for service in configuration["services"]:
            codeSmellTypes += service["codeSmells"]

        codeSmells:pd.DataFrame = codeSmellsSonar[(codeSmellsSonar['codeSmell'].isin(codeSmellTypes))]

        apps:any = codeSmells["app"].unique()
        repos:any

        codeSmellsApp:pd.DataFrame
        codeSmellsRepo:pd.DataFrame

        metrics:pd.DataFrame = self.__metrics.copy()
        row:any = []
        value:int
        points:Decimal
        for app in apps:
            codeSmellsApp = codeSmells[(codeSmells['app']==app)]
            repos = codeSmellsApp["repository"].unique()

            for repo in repos:
                codeSmellsRepo = codeSmellsApp[(codeSmellsApp['repository']==repo)]

                for service in configuration["services"]:
                    value = self.__getValueCodeSmellConnectionPool(app,repo,service,codeSmellsRepo)

                    points = self.__getPointsCodeSmellConnectionPool(value,service["rangesMetric"])

                    row = [app, repo, service["service"], configuration["metric"],value,points]
                    metrics.loc[len(metrics.index)] = row                    

        return metrics
    
    def __getValueCodeSmellConnectionPool(self,app:str,repo:str,serviceCloud:any,codeSmells:pd.DataFrame)->Decimal:
        codeSmells = codeSmells[(codeSmells['codeSmell'].isin(serviceCloud["codeSmells"]))]
    
        value:int
        maxValue:int=0

        components = codeSmells["component"].unique()

        for component in components:
            value = len(codeSmells[(codeSmells['component'] == component)].index)

            if(value>maxValue): maxValue = value

        return maxValue
    
    def __getPointsCodeSmellConnectionPool(self,value:int,rangesMetric:any)->Decimal:
        length:int = len(rangesMetric)

        for range in rangesMetric:
            if(value <= range["maximum"]):
                return range["points"]




