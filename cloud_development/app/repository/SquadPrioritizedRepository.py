import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants

class SquadPrioritizedRepository():

    def getSquadsByServiceCloud(self,serviceCloud:str)->pd.DataFrame:
        file:str = Utils.getPathDirectory(Constants.PATH_INPUT_SQUADS_PRIORIZADOS)

        usecols:list[str]=[0,1,2,3]
        usenames:list[str]=["tribe","squad","group","cmt"]
        data:pd.DataFrame = pd.read_excel(file,usecols=usecols,names=usenames,sheet_name=serviceCloud)
        data = data.astype(object).where(pd.notnull(data),None)

        data = data.sort_values(["tribe","squad"], ascending = [True, True])

        data["tribeCode"] = data.apply(lambda record: Utils.getCodeSquadTribe(record["tribe"]),axis=1)
        data["squadCode"] = data.apply(lambda record: Utils.getCodeSquadTribe(record["squad"]),axis=1)

        return data
