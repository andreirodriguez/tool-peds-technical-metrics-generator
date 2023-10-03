import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants

class AssesmentRepository():

    def __getFileAssesment(self,path:str,metrics:list[str])->pd.DataFrame:
        file:str = Utils.getPathDirectory(path)

        usecols:list[int]=[0,1,2,3]
        namescols:list[str]=["employeeCode","employeeNameForm","employeeEmailForm","employeeSpecialtyForm"]
        count = 4
        for metric in metrics:
            usecols.append(count)
            namescols.append(metric)

            count += 1        

        data:pd.DataFrame = pd.read_excel(file,usecols=usecols,names=namescols)
        data = data.astype(object).where(pd.notnull(data),None)

        return data
    
    def getAssesmentServiceCloud(self,path:str,metrics:list[str])->pd.DataFrame:
        data = pd.DataFrame({})
        files = Utils.getFilesDirectory(path)

        for file in files:
            if (not file.endswith(".xlsx")): continue

            data = pd.concat([data, self.__getFileAssesment(path + file,metrics)], ignore_index=True)        

        return data

        
