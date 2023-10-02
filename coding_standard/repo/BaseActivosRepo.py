from repo.RepoInterface import RepoInterface
from utils.constants import PATH_BASE_ACTIVOS, PD
from utils.singleton import singleton
from utils.PathManage import PathManage

@singleton
class BaseActivosRepo(RepoInterface):
    def __init__(self):        
        file = PathManage.getFirstFilePath(PATH_BASE_ACTIVOS)        
        self.df = PD.read_excel(file)
        self.df = self.df.dropna(subset=['squad_code'])        
        self.df = self.df[self.df.squad_code.apply(lambda row: row.isnumeric())]
        self.df = self.df.astype({'squad_code': int})
    
    def table(self)->PD.DataFrame:
        df = self.df        
        return df