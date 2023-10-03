import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.repository.SonarRepository import SonarRepository

class SonarService():
    
    __sonarRepository:SonarRepository

    def __init__(self):
        self.__sonarRepository = SonarRepository()

    def listSonarCodeSmells(self)->pd.DataFrame:
        return self.__sonarRepository.getSonarCodeSmells()