import pandas as pd
from typing import List
from config.PropertyInterface import PropertyInterface
from reports.ReportInterface import ReportInterface
from models.PullRequestModel import PullRequestModel
from repo.Storage import Storage
from utils.MaturityCalc import MaturityCalc
from utils.TimestampsCalc import TimestampsCalc

class PullRequestReport(ReportInterface):

    def __init__(self, output_path, storage: Storage, timestamps: TimestampsCalc, report_fields: List[PropertyInterface])->None:
        self.__output_path      = output_path
        self.__timestamps       = timestamps
        self.__maturity_calc    = MaturityCalc()
        self.__sonar            = storage.sonar().table()
        self.__fortify          = storage.fortify().table()
        self.__maturity_level   = storage.maturity_level().table() 
        self.__pull_request     = storage.pull_request()
        self.__report_fields    = report_fields

    def toDataframe(self)->pd.DataFrame:        
        dataFrameCollect = []       

        period = f"{self.__timestamps.get_year}-{self.__timestamps.get_month}-{self.__timestamps.get_day} 23:59:59"
        self.__fortify = self.__fortify.loc[self.__fortify['custom_analysis_date'] <= period]
        self.__sonar = self.__sonar.loc[self.__sonar['Fecha Analisis'] <= period]        

        counter = 0
        squad: pd.DataFrame
        for index, squad in self.__maturity_level.iterrows():
            counter += 1
            print(f'REPORTE POR PR:  Squad:: {str(squad["squad"])} - REG {counter} DE {len(self.__maturity_level)} ###################')
            
            df_prs_by_squad = self.__pull_request.bySquadCode(squad['squad_code'])
            if len(df_prs_by_squad) == 0: continue
            prs = self.__get_pull_requests(df_prs_by_squad)
            if len(prs): dataFrameCollect.append(prs)

        print('################# PROCESS DONE! ############################')
        return pd.concat(dataFrameCollect)

    def __get_pull_requests(self, df_prs_by_squad: pd.DataFrame)->pd.DataFrame:
        prCollection    = []        
        for key, pr in df_prs_by_squad.iterrows():                 
            print('PR_ID: ' + str(pr['prid']) + ' REPO: ' + pr['repo'])

            pull = PullRequestModel(
                    self.__maturity_calc,
                    self.__timestamps,
                    df_prs_by_squad,
                    self.__report_fields,
                    sonar_tbl = self.__sonar,
                    fortify_df = self.__fortify,
                    df_pr = pr
                )
            pull.toDataFrame()
            prCollection.append(pull.toDataFrame())

        return pd.concat(prCollection)

    def to_csv(self, df: pd.DataFrame)->None:
        df.to_csv(self.__output_path, index=False)