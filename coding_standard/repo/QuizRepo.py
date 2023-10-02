from repo.RepoInterface import RepoInterface
from utils.constants import PATH_QUIZ_FILES, PD
from utils.singleton import singleton
from utils.PathManage import PathManage

@singleton
class QuizRepo(RepoInterface):
    def __init__(self):        
        dfs = []

        files = PathManage.getAllFilesPath(PATH_QUIZ_FILES)

        for file in files:
            dfs.append(PD.read_excel(file['full_path']))

        self.df = PD.concat(dfs)        
    
    def table(self)->PD.DataFrame:                
        return self.df