from repo.RepoInterface import RepoInterface
from utils.constants import PATH_PRS_FILE, PD
from utils.singleton import singleton
from utils.PathManage import PathManage

@singleton
class PullRequestRepo(RepoInterface):   
    def __init__(self)->None:
        df = PD.read_csv(PathManage.getFirstFilePath(PATH_PRS_FILE), on_bad_lines='skip', usecols=[
            'app', 'squad', 'squad_code', 'repo', 'prid', 'tribe','tribe_code', 'author', 'author_name', 'specialty',
            'technology', 'origin_branch', 'close_date'
        ])        

        df = df.astype({'close_date': 'datetime64[ns]'})
        df = df.dropna(subset=['squad_code'])        

        df['close_date']           = PD.to_datetime(df['close_date'], format="%Y-%m-%d")        
        df['branch_repo_key']      = df.apply(lambda row: row['repo'] + row['origin_branch'], axis=1)
        df                         = df[df.squad_code.apply(lambda row: row.isnumeric())]
        df                         = df.astype({'squad_code': int})
        df['short_close_date']     = df['close_date'].dt.strftime("%Y-%m-%d")
        self.__pull_request         = df

    def table(self)->PD.DataFrame:
        return self.__pull_request
        
    def bySquadCode(self, squad_code:int)->PD.DataFrame:
        df = self.__pull_request
        df = df[(df['squad_code'] == squad_code)]
        return df