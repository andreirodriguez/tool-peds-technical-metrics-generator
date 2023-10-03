import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from decimal import Decimal

from cloud_development.app.repository.AssesmentRepository import AssesmentRepository


class AssesmentService():
    
    __assesmentRepository:AssesmentRepository
    __metricRanges:any

    def __init__(self,metricRanges):
        self.__metricRanges = metricRanges

        self.__assesmentRepository = AssesmentRepository()
        

    def listAssesmentByServiceCloud(self,path:str,metrics:list[str],baseActivos:pd.DataFrame)->pd.DataFrame:
        assesments:pd.DataFrame = self.__assesmentRepository.getAssesmentServiceCloud(path,metrics)

        for metric in metrics:
            assesments[metric + "Points"] =  assesments.apply(lambda record: self.__getMetricRangePoints(record[metric]),axis=1)

        teamMembers = baseActivos.sort_values(['employeeCode','squadCode'], ascending = [True,False])
        teamMembers = teamMembers.drop_duplicates(subset=["employeeCode","squadCode"], keep="first")

        assesments = pd.merge(assesments, teamMembers[['employeeCode','name','fatherLastName','motherLastName','email','squad', 'squadCode','specialty',]], on="employeeCode", how="left")

        return assesments
    
    def __getMetricRangePoints(self,approvalPercentage:Decimal)->Decimal:
        point:Decimal = 0.00
        length:int = len(self.__metricRanges)

        for range in self.__metricRanges:
            if(range["id"]<length):
                if(range["minimum"] <= approvalPercentage < range["maximum"]):
                    point = range["points"]
                    point += (approvalPercentage - range["minimum"]) * (100/(range["minimum"] - range["maximum"])/100)
                    point = round(point, 2) 

                    break
            else:
                if(range["minimum"] <= approvalPercentage <= range["maximum"]):
                    point = range["points"]

        return point


