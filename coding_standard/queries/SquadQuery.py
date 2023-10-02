import pandas as pd

class SquadQuery:
    def __init__(self, df_squad: pd.DataFrame, df_detail: pd.DataFrame, df_baseactivos_quiz_repo: pd.DataFrame)->None:        
        df_detail = df_detail[df_detail['squad_code'] == df_squad['squad_code']]        
        self.__detail_tbl = df_detail
        
        df_bq = df_baseactivos_quiz_repo
        df_bq = df_bq[df_bq['squad_code'] == df_squad['squad_code']]
        self.__baseactivos_quiz = df_bq


    def metricFirstValue(self, metric:str):
        if len(self.__detail_tbl[metric]): return self.__detail_tbl[metric].iloc[0]
        return 0

    def sumMetric(self, metric: str)->float:
        df = self.__detail_tbl     
        if len(df[metric]): return round(df[metric].sum(), 2)
        return 0          
    
    def avgMetric(self, metric: str)->float:
        df = self.__detail_tbl
        if len(df[metric]): return round(df[metric].mean(), 2)
        return 0
    
    def uniqueRepoSumMetric(self, metric: str)->float:
        df = self.__detail_tbl        
        df = df.dropna(subset=[metric])
        df = df.drop_duplicates(subset = "repo")        
        if len(df[metric]): return round(df[metric].sum(), 2)
        return 0 
    
    def uniqueRepoAverageMetric(self, metric: str)->float:
        df = self.__detail_tbl        
        df = df.dropna(subset=[metric])
        df = df.drop_duplicates(subset = "repo")        
        if len(df[metric]): return round(df[metric].mean(), 2)
        return 0
    
    def uniqueRepoCountMetric(self, metric: str, exclude_zero_values: bool = True)->int:
        df = self.__detail_tbl        
        df = df.dropna(subset=[metric])
        if exclude_zero_values: df = df[df[metric] > 0]
        df = df.drop_duplicates(subset = "repo")
        return len(df[metric])

    def quizAverageMetric(self, metric: str)->float:
        df = self.__baseactivos_quiz
        if len(df[metric]): return round(df[metric].mean(), 2)
        return 0
    
    def countAllRegisters(self)->int:        
        return self.__detail_tbl['app'].count()
    
    def registersWithSonarExecution(self)->int:
        df = self.__detail_tbl
        df.dropna(subset='sonar_project_name')
        return df['sonar_project_name'].count()
        