from repo.RepoInterface import RepoInterface
from utils.constants import NODE_SONAR_REPORT_FILE, PD
from utils.singleton import singleton
import re
from utils.PathManage import PathManage

@singleton
class SonarRepo(RepoInterface):
    def __init__(self):
        dfs = []
        files = PathManage.getAllFilesPath(NODE_SONAR_REPORT_FILE)

        for file in files:
            dfs.append(PD.read_excel(file['full_path'], usecols=['Código Aplicación', 'Proyecto Sonar', 'Repositorio', 'Metric', 'Version', 'Value', 'Fecha Analisis'], sheet_name=0, header=2))
            
        self.df = PD.concat(dfs)     
        
        self.df['repo']             = self.df.apply(lambda row: str(row['Repositorio']).rsplit('/', 1)[-1].replace('.git', ''), axis=1)
        self.df['branch_name']      = self.df.apply(lambda row: self.setBranchName(row), axis=1)        
        self.df['branch_repo_key']  = self.df.apply(lambda row: row['repo'] + row['branch_name'], axis=1)
        self.df['Fecha Analisis']   = self.df['Fecha Analisis'].astype('datetime64[ns]')
        self.df['Fecha Analisis']   = PD.to_datetime(self.df['Fecha Analisis'].dt.strftime('%d/%m/%Y %H:%M:%S'))
        self.df                     = self.df.sort_values(by='Fecha Analisis', ascending=True)
        
    
    def table(self)->PD.DataFrame:
        df = self.df        
        return df
    
    def setBranchName(self, row)->str:
        branch = re.sub(r"""^.+SNAPSHOT-""", "", row['Version'])
        branch = re.sub(r"""^(\d+(\.|-))+""", "", branch)
        return branch       