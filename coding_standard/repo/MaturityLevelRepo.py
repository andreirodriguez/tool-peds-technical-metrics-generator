from repo.RepoInterface import RepoInterface
from utils.constants import PATH_MATURITY_LEVEL_FILE, PD
from utils.singleton import singleton
from utils.PathManage import PathManage

@singleton
class MaturityLevelRepo(RepoInterface):
    def __init__(self):
        self.df = PD.read_csv(PathManage.getFirstFilePath(PATH_MATURITY_LEVEL_FILE), 
                            usecols=['squad_code', 'squad', 'tribe_code', 'tribe','group', 'cmt'], on_bad_lines='skip'
                        )
    
    def table(self)->PD.DataFrame:
        return self.df

    def set_table(self, data: PD.DataFrame)->None:
        self.df = data