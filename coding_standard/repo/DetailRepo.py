import os
from repo.RepoInterface import RepoInterface
from utils.constants import OUTPUT_BASE_FILE, OUTPUT_FOLDER, PD
from utils.singleton import singleton

@singleton
class DetailRepo(RepoInterface):
    def __init__(self):
        files = os.listdir(OUTPUT_FOLDER)        
        match_file = ""
        for file in files:        
            if OUTPUT_BASE_FILE in file: 
                match_file = file                
                break        
        
        df = PD.read_csv(OUTPUT_FOLDER + match_file, encoding = 'utf8')
        self.df = df

    def table(self)->PD.DataFrame:
        return self.df
    
    def set_table(self, data: PD.DataFrame)->None:
        self.df = data