import abc
import pandas as pd

class RepoInterface(metaclass=abc.ABCMeta):    
    
    @abc.abstractmethod
    def table()->pd.DataFrame:
        pass

    @abc.abstractmethod
    def set_table(self, data: pd.DataFrame)->None:
        pass