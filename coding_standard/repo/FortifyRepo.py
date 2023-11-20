from repo.RepoInterface import RepoInterface
from utils.TimestampsCalc import TimestampsCalc
from utils.constants import PATH_FORTIFY_BASE_PATH, PD
from utils.singleton import singleton
from utils.PathManage import PathManage
import warnings

@singleton
class FortifyRepo(RepoInterface):
    def __init__(self)->None:        
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            self.df = PD.read_excel(PathManage.getFirstFilePath(PATH_FORTIFY_BASE_PATH), 
                usecols=[
                        'Versión', 'Rama Repositorio', 'Aplicación', 'Ultimo análisis',
                        'Valor Crítico', 'Valor Alto', 'Valor Medio', 'Valor Bajo',
                        'Only Not an Issue Critical', 'Only Not an Issue High', 'Only Not an Issue Medium', 'Only Not an Issue Low'
                    ]
                ,sheet_name=0, header=3)
        self.df = self.df.dropna(subset=['Ultimo análisis'])
        self.df['branch_repo_key']= self.df.apply(lambda row: str(row['Versión']) + str(row['Rama Repositorio']), axis=1)
        self.df['format_date'] = self.df['Ultimo análisis'].astype('datetime64[ns]')
        self.df['format_date'] = PD.to_datetime(self.df['format_date'], format="%Y-%m-%d")
        self.df['short_last_analysis_date']  = self.df['format_date'].dt.strftime('%Y-%m-%d %H:%M')
        self.df['custom_analysis_date']  = self.df.apply(lambda row: TimestampsCalc.set_dataframe_date(row['Ultimo análisis'], '-'), axis=1)
    
    def table(self)->PD.DataFrame:
        self.df = self.df.sort_values(by='custom_analysis_date', ascending=True)
        return self.df
    
    def set_table(self, data: PD.DataFrame)->None:
        self.df = data