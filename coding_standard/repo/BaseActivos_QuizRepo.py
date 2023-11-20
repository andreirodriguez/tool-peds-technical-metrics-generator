from repo.BaseActivosRepo import BaseActivosRepo
from repo.QuizRepo import QuizRepo
from repo.RepoInterface import RepoInterface
from utils.constants import PD
from utils.singleton import singleton
from utils.DataFrameMerger import DataFrameMerger
from utils.MetricCalculate import MetricCalculate

@singleton
class BaseActivosQuizRepo(RepoInterface):
    def __init__(self):
        merged = DataFrameMerger(QuizRepo(), BaseActivosRepo(), 'matricula', 'matricula')        
        self.df = merged.table()

    def table(self)->PD.DataFrame:        
        self.df['estandares_lineamientos_int_points'] = self.df.apply(lambda row: MetricCalculate.quizPoints(row['estandares_lineamientos_points']), axis=1)
        self.df['patrones_principios_int_points'] = self.df.apply(lambda row: MetricCalculate.quizPoints(row['patrones_principios_points']), axis=1)
        return self.df
    
    def set_table(self, data: PD.DataFrame)->None:
        self.df = data