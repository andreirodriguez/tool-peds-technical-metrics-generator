import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants

class SonarRepository():

    def __getFileSonar(self,path:str)->pd.DataFrame:
        file:str = Utils.getPathDirectory(path)

        usecols:list[int]=[0,1,2,3,4,5,6]
        namescols:list[str]=["app","project","urlRepository","codeSmell","component","creationDate","updateDate"]

        data:pd.DataFrame = pd.read_excel(file,usecols=usecols,names=namescols)
        data = data.astype(object).where(pd.notnull(data),None)

        data['creationDate'] = data['creationDate'].apply(lambda value: pd.to_datetime(value,format=Constants.FORMAT_DATETIME_SONAR).to_datetime64())
        data['updateDate'] = data['updateDate'].apply(lambda value: pd.to_datetime(value,format=Constants.FORMAT_DATETIME_SONAR).to_datetime64())

        data['repository'] = data['urlRepository'].apply(lambda value: self.__getRepository(value))

        return data
    
    def getSonarCodeSmells(self)->pd.DataFrame:
        data = pd.DataFrame({})
        path:str = Constants.PATH_INPUT_SONAR
        files = Utils.getFilesDirectory(Constants.PATH_INPUT_SONAR)

        for file in files:
            if (not file.endswith(".xlsx")): continue

            data = pd.concat([data, self.__getFileSonar(path + file)], ignore_index=True)        

        data = data.sort_values(["app","repository"], ascending = [True, True])

        return data

    def __getRepository(self,url: str) -> str:
        repository:str = url.strip().lower().removeprefix(Constants.URL_BASE_BITBUCKET_REPO)
        repository = repository.split("/")[1]
        repository = repository.removesuffix(".git")

        return repository
