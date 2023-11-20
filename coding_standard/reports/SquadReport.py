import pandas as pd
from typing import List
from config.PropertyInterface import PropertyInterface
from repo.Storage import Storage
from models.SquadModel import SquadModel
from reports.ReportInterface import ReportInterface
from utils.GlobalTypes import Especialty

class SquadReport(ReportInterface):

    def __init__(self, output_path:str, storage: Storage, specialty: Especialty, report_fields: List[PropertyInterface])->None:
        self.__storage = storage
        self.__specialty: Especialty = specialty
        self.__output_path = output_path
        self.__maturity_repo = storage.maturity_level()
        self.__baseactivos_quiz_repo = storage.activos_and_quiz()
        self.__report_fields = report_fields

    def toDataframe(self)->pd.DataFrame:
        self.__pr_detail = self.__storage.pr_detail()
        all_squads  = self.__maturity_repo.table()
        squads_df   = all_squads
        df_detail       = self.__pr_detail.table()
        df_activos_quiz = self.__baseactivos_quiz_repo.table()

        if self.__specialty != Especialty.ALL:
            df_detail = df_detail[df_detail['specialty'] == self.__specialty.value]
            if len(df_detail) == 0: return pd.DataFrame([])
        
        squads_collect = df_detail.drop_duplicates(subset="squad_code")
        
        dataFrameCollect = []
        squad: pd.DataFrame
        counter = 0
        for index, squad in squads_collect.iterrows():
            counter+=1
            print(f"PROCESANDO SQUAD:: {squad['squad']} REG::{counter} DE {len(squads_collect)} Especialidad:: {self.__specialty.value}")
            df_squad = squads_df[squads_df['squad_code'] == squad['squad_code']]

            if len(df_squad): squad_m: SquadModel = SquadModel(df_squad.iloc[0], self.__report_fields, df_detail, df_activos_quiz)
            dataFrameCollect.append(squad_m.toDataFrame())
        
        print('################# PROCESS DONE! ############################')
        return pd.concat(dataFrameCollect)
        

    def to_csv(self, df: pd.DataFrame)->None:
        df.to_csv(self.__output_path, index=False)